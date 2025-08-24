"""
Unit tests for extended data models.
Tests the new fields added to agents, contacts, participants, and memories.
"""

import pytest
from datetime import datetime
from uuid import uuid4

from app.infrastructure.database.models import (
    AIAgentModel,
    ContactModel,
    ConversationParticipantModel,
    ConversationMemoryModel
)


class TestAIAgentModelExtensions:
    """Test AIAgentModel extensions for LangGraph integration."""
    
    def test_agent_langraph_fields(self):
        """Test that new LangGraph fields are properly initialized."""
        agent = AIAgentModel(
            name="test_agent",
            display_name="Test Agent",
            description="A test agent",
            agent_type="custom",
            system_prompt="You are a test agent",
            created_by=uuid4(),
            
            # New fields
            node_type="workflow",
            execution_config={
                "timeout_seconds": 30,
                "max_retries": 3,
                "parallel_execution": True
            },
            resource_limits={
                "max_memory_mb": 512,
                "max_cpu_percent": 80,
                "max_execution_time": 60
            },
            dependencies={
                "required_tools": ["search", "calculator"],
                "optional_tools": ["image_generator"],
                "model_requirements": ["gpt-4", "claude-3"]
            }
        )
        
        assert agent.node_type == "workflow"
        assert agent.execution_config["timeout_seconds"] == 30
        assert agent.resource_limits["max_memory_mb"] == 512
        assert "search" in agent.dependencies["required_tools"]
    
    def test_agent_defaults(self):
        """Test that new fields have appropriate defaults."""
        agent = AIAgentModel(
            name="minimal_agent",
            display_name="Minimal Agent",
            agent_type="system",
            system_prompt="You are minimal",
            created_by=uuid4()
        )
        
        assert agent.node_type == "standard"
        assert agent.execution_config is None
        assert agent.resource_limits is None
        assert agent.dependencies is None


class TestContactModelExtensions:
    """Test ContactModel extensions for contact instance management."""
    
    def test_contact_instance_fields(self):
        """Test that new contact instance fields work correctly."""
        contact = ContactModel(
            follower_id=uuid4(),
            following_id=uuid4(),
            following_type="agent",
            
            # New fields
            agent_id=uuid4(),
            custom_system_prompt="You are my personal assistant. Be concise and technical.",
            instance_config={
                "temperature": 0.7,
                "max_tokens": 2000,
                "model_preference": "gpt-4",
                "response_style": "technical"
            },
            resource_limits={
                "max_requests_per_hour": 100,
                "max_tokens_per_request": 4000
            }
        )
        
        assert contact.agent_id is not None
        assert "personal assistant" in contact.custom_system_prompt
        assert contact.instance_config["temperature"] == 0.7
        assert contact.resource_limits["max_requests_per_hour"] == 100
    
    def test_contact_defaults(self):
        """Test that new fields have appropriate defaults."""
        contact = ContactModel(
            follower_id=uuid4(),
            following_id=uuid4(),
            following_type="user"
        )
        
        assert contact.agent_id is None
        assert contact.custom_system_prompt is None
        assert contact.instance_config is None
        assert contact.resource_limits is None


class TestConversationParticipantExtensions:
    """Test ConversationParticipantModel extensions for workflow management."""
    
    def test_participant_workflow_fields(self):
        """Test that new workflow fields work correctly."""
        participant = ConversationParticipantModel(
            conversation_id=uuid4(),
            participant_id=uuid4(),
            participant_type="agent",
            
            # New fields
            workflow_priority=10,
            conversation_permissions={
                "can_initiate_workflow": True,
                "can_modify_conversation": False,
                "can_access_memory": True,
                "allowed_tools": ["search", "calculation"]
            }
        )
        
        assert participant.workflow_priority == 10
        assert participant.conversation_permissions["can_initiate_workflow"] is True
        assert "search" in participant.conversation_permissions["allowed_tools"]
    
    def test_participant_defaults(self):
        """Test that new fields have appropriate defaults."""
        participant = ConversationParticipantModel(
            conversation_id=uuid4(),
            participant_id=uuid4(),
            participant_type="user"
        )
        
        assert participant.workflow_priority == 0
        assert participant.conversation_permissions is None


class TestConversationMemoryModel:
    """Test ConversationMemoryModel for memory storage."""
    
    def test_memory_creation(self):
        """Test that memory model can be created with all fields."""
        memory = ConversationMemoryModel(
            conversation_id=uuid4(),
            participant_id=uuid4(),
            participant_type="user",
            memory_type="short_term",
            memory_category="user_preference",
            content="User prefers detailed code examples with explanations",
            context={
                "topic": "programming_help",
                "trigger_message": "Can you show me how to use async/await?",
                "conversation_turn": 5
            },
            importance_score=0.8,
            confidence_score=0.9,
            emotional_valence=0.2,
            embedding_model="text-embedding-ada-002",
            memory_metadata={
                "source": "explicit_statement",
                "extraction_method": "pattern_matching"
            }
        )
        
        assert memory.memory_type == "short_term"
        assert memory.memory_category == "user_preference"
        assert "code examples" in memory.content
        assert memory.context["topic"] == "programming_help"
        assert memory.importance_score == 0.8
        assert memory.confidence_score == 0.9
        assert memory.emotional_valence == 0.2
        assert memory.embedding_model == "text-embedding-ada-002"
    
    def test_memory_defaults(self):
        """Test that memory fields have appropriate defaults."""
        memory = ConversationMemoryModel(
            conversation_id=uuid4(),
            memory_type="contextual",
            memory_category="fact",
            content="Basic fact"
        )
        
        assert memory.participant_id is None
        assert memory.participant_type is None
        assert memory.context is None
        assert memory.importance_score == 0.5
        assert memory.confidence_score == 1.0
        assert memory.emotional_valence == 0.0
        assert memory.access_count == 0
        assert memory.embedding_model is None
    
    def test_memory_timestamps(self):
        """Test that timestamps are properly set."""
        memory = ConversationMemoryModel(
            conversation_id=uuid4(),
            memory_type="long_term",
            memory_category="pattern",
            content="User pattern identified"
        )
        
        assert memory.created_at is not None
        assert memory.last_accessed_at is not None
        assert memory.expires_at is None  # Default no expiration


class TestModelIntegration:
    """Test integration between extended models."""
    
    def test_agent_to_contact_relationship(self):
        """Test that agent can be referenced in contact."""
        agent_id = uuid4()
        user_id = uuid4()
        
        # Create agent with LangGraph fields
        agent = AIAgentModel(
            name="coding_assistant",
            display_name="Coding Assistant",
            agent_type="specialized",
            system_prompt="I help with coding",
            created_by=user_id,
            node_type="tool",
            execution_config={"timeout": 45}
        )
        
        # Create contact that references the agent
        contact = ContactModel(
            follower_id=user_id,
            following_id=agent_id,
            following_type="agent",
            agent_id=agent_id,  # Direct reference
            custom_system_prompt="Focus on Python and be very detailed"
        )
        
        assert contact.following_type == "agent"
        assert contact.agent_id == agent_id
        assert contact.following_id == agent_id  # Should match
    
    def test_conversation_workflow_setup(self):
        """Test that conversation participants can be set up for workflow."""
        conversation_id = uuid4()
        agent_id = uuid4()
        user_id = uuid4()
        
        # User participant with lower priority
        user_participant = ConversationParticipantModel(
            conversation_id=conversation_id,
            participant_id=user_id,
            participant_type="user",
            workflow_priority=1,
            conversation_permissions={
                "can_initiate_workflow": True,
                "can_access_memory": True
            }
        )
        
        # Agent participant with higher priority
        agent_participant = ConversationParticipantModel(
            conversation_id=conversation_id,
            participant_id=agent_id,
            participant_type="agent",
            workflow_priority=10,
            conversation_permissions={
                "can_initiate_workflow": True,
                "can_modify_conversation": True,
                "allowed_tools": ["search", "code_exec"]
            }
        )
        
        assert user_participant.workflow_priority < agent_participant.workflow_priority
        assert agent_participant.conversation_permissions["can_modify_conversation"] is True
        assert "can_modify_conversation" not in user_participant.conversation_permissions
    
    def test_memory_context_integration(self):
        """Test that memory can store context from conversation."""
        conversation_id = uuid4()
        user_id = uuid4()
        
        # Memory storing user preference
        user_memory = ConversationMemoryModel(
            conversation_id=conversation_id,
            participant_id=user_id,
            participant_type="user",
            memory_type="medium_term",
            memory_category="user_preference",
            content="User prefers step-by-step explanations with code examples",
            context={
                "derived_from": "multiple_interactions",
                "confidence_source": "explicit_feedback",
                "applicable_domains": ["programming", "tutorials"]
            },
            importance_score=0.9
        )
        
        assert user_memory.conversation_id == conversation_id
        assert user_memory.context["derived_from"] == "multiple_interactions"
        assert user_memory.importance_score == 0.9