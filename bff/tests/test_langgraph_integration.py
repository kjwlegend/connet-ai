"""
Comprehensive tests for LangGraph integration

Tests the complete workflow from user message to AI response.
"""

import pytest
import asyncio
from datetime import datetime
from uuid import uuid4
from unittest.mock import Mock, patch

from sqlalchemy.ext.asyncio import AsyncSession
from app.services.langgraph.workflow_engine import WorkflowEngine
from app.services.langgraph.conversation_service import ConversationService
from app.services.langgraph.contact_manager import ContactInstanceManager
from app.services.langgraph.mention_parser import MentionParser
from app.services.langgraph.state_models import ContactInfo, ConversationState, WorkflowType
from app.infrastructure.database.models.user_model import UserModel
from app.infrastructure.database.models.agent_model import AIAgentModel
from app.infrastructure.database.models.contact_model import ContactModel, EntityType
from app.infrastructure.database.models.conversation_model import ConversationModel
from app.infrastructure.database.models.conversation_participant_model import ConversationParticipantModel


@pytest.fixture
async def test_user():
    """Create test user"""
    return UserModel(
        id=uuid4(),
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        created_at=datetime.utcnow()
    )


@pytest.fixture
async def test_agent():
    """Create test agent"""
    return AIAgentModel(
        id=uuid4(),
        name="test_assistant",
        display_name="Test Assistant",
        description="A helpful test assistant",
        system_prompt="You are a helpful test assistant.",
        agent_type="system",
        model_preferences={
            "default_model": "gpt-4o-mini",
            "temperature": 0.7
        },
        created_by=uuid4(),
        created_at=datetime.utcnow()
    )


@pytest.fixture
async def test_conversation(test_user):
    """Create test conversation"""
    return ConversationModel(
        id=uuid4(),
        title="Test Conversation",
        conversation_type="chat",
        created_by=test_user.id,
        is_group=False,
        status="active",
        created_at=datetime.utcnow()
    )


@pytest.fixture
async def test_contact(test_user, test_agent):
    """Create test contact relationship"""
    return ContactModel(
        follower_id=test_user.id,
        following_id=test_agent.id,
        following_type=EntityType.agent,
        relationship_type="follow",
        is_agent=True,
        created_at=datetime.utcnow()
    )


class TestMentionParser:
    """Test mention parser functionality"""
    
    def test_extract_mentions_single(self):
        """Test extracting single mention"""
        parser = MentionParser()
        message = "Hey @test_assistant, can you help me?"
        mentions = parser.extract_mentions(message)
        assert mentions == ["test_assistant"]
    
    def test_extract_mentions_multiple(self):
        """Test extracting multiple mentions"""
        parser = MentionParser()
        message = "Hey @assistant1 and @assistant2, can you both help?"
        mentions = parser.extract_mentions(message)
        assert mentions == ["assistant1", "assistant2"]
    
    def test_extract_mentions_duplicates(self):
        """Test extracting mentions with duplicates"""
        parser = MentionParser()
        message = "Hey @assistant1, and @assistant1 again!"
        mentions = parser.extract_mentions(message)
        assert mentions == ["assistant1"]  # Should deduplicate
    
    def test_has_mentions(self):
        """Test checking if message has mentions"""
        parser = MentionParser()
        assert parser.has_mentions("Hey @assistant")
        assert not parser.has_mentions("Hey there")
    
    def test_remove_mentions(self):
        """Test removing mentions from message"""
        parser = MentionParser()
        message = "Hey @assistant, can you help?"
        clean = parser.remove_mentions(message)
        assert clean == "Hey , can you help?"
    
    def test_find_mentioned_contacts(self):
        """Test finding mentioned contacts"""
        parser = MentionParser()
        
        contacts = [
            ContactInfo(
                contact_id="1",
                agent_id="agent1",
                follower_id="user1",
                agent_name="assistant1",
                display_name="Assistant 1",
                system_prompt="You are assistant 1",
                model_preferences={},
                is_active=True
            ),
            ContactInfo(
                contact_id="2",
                agent_id="agent2",
                follower_id="user1",
                agent_name="assistant2",
                display_name="Assistant 2",
                system_prompt="You are assistant 2",
                model_preferences={},
                is_active=True
            )
        ]
        
        message = "Hey @assistant1, can you help?"
        mentioned = parser.find_mentioned_contacts(message, contacts)
        assert len(mentioned) == 1
        assert mentioned[0]["agent_name"] == "assistant1"


class TestContactInstanceManager:
    """Test contact instance manager"""
    
    @pytest.mark.asyncio
    async def test_get_user_contact_by_agent(self, test_session, test_user, test_agent, test_contact):
        """Test getting user contact by agent"""
        # Add test data to session
        test_session.add_all([test_user, test_agent, test_contact])
        await test_session.commit()
        
        manager = ContactInstanceManager(test_session)
        contact_info = await manager.get_user_contact_by_agent(test_user.id, test_agent.id)
        
        assert contact_info is not None
        assert contact_info["agent_name"] == test_agent.name
        assert contact_info["display_name"] == test_agent.display_name
    
    @pytest.mark.asyncio
    async def test_create_contact_instance(self, test_session, test_user, test_agent):
        """Test creating a new contact instance"""
        # Add test data to session
        test_session.add_all([test_user, test_agent])
        await test_session.commit()
        
        manager = ContactInstanceManager(test_session)
        contact_info = await manager.create_contact_instance(
            test_user.id, 
            test_agent.id, 
            custom_display_name="My Assistant"
        )
        
        assert contact_info["agent_name"] == test_agent.name
        assert contact_info["display_name"] == "My Assistant"
    
    @pytest.mark.asyncio
    async def test_get_mentioned_contacts(self, test_session, test_user, test_agent, test_contact):
        """Test getting mentioned contacts"""
        # Add test data to session
        test_session.add_all([test_user, test_agent, test_contact])
        await test_session.commit()
        
        manager = ContactInstanceManager(test_session)
        mentioned = await manager.get_mentioned_contacts(
            test_user.id, 
            ["test_assistant"]
        )
        
        assert len(mentioned) == 1
        assert mentioned[0]["agent_name"] == "test_assistant"


class TestWorkflowEngine:
    """Test workflow engine functionality"""
    
    @pytest.mark.asyncio
    async def test_determine_workflow_type_single_contact(self, test_session):
        """Test workflow type determination for single contact"""
        engine = WorkflowEngine(test_session)
        
        routing_context = {"has_mentions": False}
        active_contacts = [Mock()]  # Single contact
        
        workflow_type = engine._determine_workflow_type(routing_context, active_contacts)
        assert workflow_type == WorkflowType.SINGLE_CONTACT.value
    
    @pytest.mark.asyncio
    async def test_determine_workflow_type_mentions(self, test_session):
        """Test workflow type determination for mentions"""
        engine = WorkflowEngine(test_session)
        
        routing_context = {"has_mentions": True}
        active_contacts = [Mock(), Mock()]  # Multiple contacts
        
        workflow_type = engine._determine_workflow_type(routing_context, active_contacts)
        assert workflow_type == WorkflowType.MENTION_ROUTING.value
    
    @pytest.mark.asyncio
    async def test_determine_workflow_type_parallel(self, test_session):
        """Test workflow type determination for parallel discussion"""
        engine = WorkflowEngine(test_session)
        
        routing_context = {"has_mentions": False}
        active_contacts = [Mock(), Mock(), Mock()]  # 3 contacts
        
        workflow_type = engine._determine_workflow_type(routing_context, active_contacts)
        assert workflow_type == WorkflowType.PARALLEL_DISCUSSION.value


class TestConversationService:
    """Test conversation service with LangGraph integration"""
    
    @pytest.mark.asyncio
    async def test_create_conversation(self, test_session, test_user, test_agent):
        """Test creating a conversation"""
        # Add test data to session
        test_session.add_all([test_user, test_agent])
        await test_session.commit()
        
        service = ConversationService(test_session)
        result = await service.create_conversation(
            user_id=test_user.id,
            title="Test Chat",
            initial_agent_ids=[test_agent.id]
        )
        
        assert result["title"] == "Test Chat"
        assert result["is_group"] == False  # 1 user + 1 agent = not group
        assert result["participant_count"] == 2
    
    @pytest.mark.asyncio
    async def test_add_agent_to_conversation(self, test_session, test_user, test_agent, test_conversation):
        """Test adding an agent to conversation"""
        # Add test data to session
        test_session.add_all([test_user, test_agent, test_conversation])
        await test_session.commit()
        
        service = ConversationService(test_session)
        success = await service.add_agent_to_conversation(
            test_conversation.id,
            test_agent.id,
            test_user.id
        )
        
        assert success is True
    
    @pytest.mark.asyncio
    @patch('app.services.langgraph.workflow_engine.WorkflowEngine.execute_conversation_workflow')
    async def test_send_message_with_workflow(self, mock_workflow, test_session, test_user, test_conversation):
        """Test sending message with workflow processing"""
        # Mock workflow response
        mock_workflow.return_value = {
            "execution_id": str(uuid4()),
            "workflow_type": "single_contact",
            "final_response": "Hello! How can I help you?",
            "contact_responses": {
                "contact_1": {
                    "contact_id": "contact_1",
                    "contact_name": "Test Assistant",
                    "agent_id": str(uuid4()),
                    "response": "Hello! How can I help you?",
                    "status": "success",
                    "tokens_used": 10
                }
            },
            "success": True
        }
        
        # Add test data to session
        test_session.add_all([test_user, test_conversation])
        await test_session.commit()
        
        service = ConversationService(test_session)
        result = await service.send_message(
            conversation_id=test_conversation.id,
            user_id=test_user.id,
            content="Hello there!"
        )
        
        assert result["success"] is True
        assert result["workflow_result"] is not None
        assert len(result["ai_responses"]) > 0
    
    @pytest.mark.asyncio
    async def test_get_conversation_participants(self, test_session, test_user, test_agent, test_conversation):
        """Test getting conversation participants"""
        # Add participants
        user_participant = ConversationParticipantModel(
            conversation_id=test_conversation.id,
            participant_id=test_user.id,
            participant_type="user",
            role="owner",
            is_active=True,
            joined_at=datetime.utcnow()
        )
        
        agent_participant = ConversationParticipantModel(
            conversation_id=test_conversation.id,
            participant_id=test_agent.id,
            participant_type="agent",
            role="member",
            is_active=True,
            joined_at=datetime.utcnow()
        )
        
        # Add test data to session
        test_session.add_all([test_user, test_agent, test_conversation, user_participant, agent_participant])
        await test_session.commit()
        
        service = ConversationService(test_session)
        participants = await service.get_conversation_participants(test_conversation.id)
        
        assert len(participants) == 2
        
        # Check user participant
        user_p = next(p for p in participants if p["type"] == "user")
        assert user_p["name"] == test_user.username
        assert user_p["role"] == "owner"
        
        # Check agent participant
        agent_p = next(p for p in participants if p["type"] == "agent")
        assert agent_p["name"] == test_agent.name
        assert agent_p["role"] == "member"


class TestEndToEndWorkflow:
    """End-to-end workflow tests"""
    
    @pytest.mark.asyncio
    @patch('app.services.langgraph.workflow_engine.ChatOpenAI')
    async def test_complete_1v1_conversation_flow(self, mock_llm_class, test_session, test_user, test_agent):
        """Test complete 1v1 conversation flow"""
        # Mock LLM response
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "Hello! I'm here to help you with any questions."
        mock_response.response_metadata = {"token_usage": {"total_tokens": 15}}
        mock_llm.ainvoke = Mock(return_value=mock_response)
        mock_llm_class.return_value = mock_llm
        
        # Add test data to session
        test_session.add_all([test_user, test_agent])
        await test_session.commit()
        
        # Create conversation with the agent
        service = ConversationService(test_session)
        conversation = await service.create_conversation(
            user_id=test_user.id,
            title="1v1 Test Chat",
            initial_agent_ids=[test_agent.id]
        )
        
        # Send message
        result = await service.send_message(
            conversation_id=conversation["conversation_id"],
            user_id=test_user.id,
            content="Hello, can you help me?"
        )
        
        assert result["success"] is True
        assert result["workflow_result"]["workflow_type"] == "single_contact"
        assert len(result["ai_responses"]) == 1
        
        # Verify messages were created
        messages = await service.get_conversation_messages(conversation["conversation_id"])
        assert len(messages) == 2  # User message + AI response
        assert messages[0]["sender_type"] == "user"
        assert messages[1]["sender_type"] == "agent"
    
    @pytest.mark.asyncio
    @patch('app.services.langgraph.workflow_engine.ChatOpenAI')
    async def test_mention_routing_workflow(self, mock_llm_class, test_session, test_user):
        """Test @mention routing workflow"""
        # Create multiple agents
        agent1 = AIAgentModel(
            id=uuid4(),
            name="coder",
            display_name="Code Assistant",
            system_prompt="You are a coding assistant.",
            agent_type="system",
            created_by=test_user.id,
            created_at=datetime.utcnow()
        )
        
        agent2 = AIAgentModel(
            id=uuid4(),
            name="writer",
            display_name="Writing Assistant", 
            system_prompt="You are a writing assistant.",
            agent_type="system",
            created_by=test_user.id,
            created_at=datetime.utcnow()
        )
        
        # Mock LLM responses
        mock_llm = Mock()
        responses = [
            Mock(content="I can help you with coding!", response_metadata={"token_usage": {"total_tokens": 10}}),
            Mock(content="I can help with writing!", response_metadata={"token_usage": {"total_tokens": 8}})
        ]
        mock_llm.ainvoke = Mock(side_effect=responses)
        mock_llm_class.return_value = mock_llm
        
        # Add test data to session
        test_session.add_all([test_user, agent1, agent2])
        await test_session.commit()
        
        # Create conversation with both agents
        service = ConversationService(test_session)
        conversation = await service.create_conversation(
            user_id=test_user.id,
            title="Multi-Agent Chat",
            initial_agent_ids=[agent1.id, agent2.id]
        )
        
        # Send message with mentions
        result = await service.send_message(
            conversation_id=conversation["conversation_id"],
            user_id=test_user.id,
            content="Hey @coder and @writer, can you both help me with a project?"
        )
        
        assert result["success"] is True
        assert result["workflow_result"]["workflow_type"] == "mention_routing"
        # Should have responses from both mentioned agents
        assert len(result["workflow_result"]["contact_responses"]) >= 2