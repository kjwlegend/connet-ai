"""
Tests for Enhanced WorkflowEngine (Priority 3)
Tests the enhanced collaboration modes and advanced workflow functionality.
"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4
from datetime import datetime

from app.modules.ai.workflows.workflow_engine import WorkflowEngine
from app.modules.ai.workflows.state_models import (
    ConversationState, 
    ContactInfo, 
    ContactResponse,
    WorkflowType,
    MessageState,
    WorkflowConfig
)


class TestWorkflowEngineEnhanced:
    """Test enhanced WorkflowEngine functionality."""
    
    @pytest.fixture
    def mock_session(self):
        """Create mock session for testing."""
        session = Mock()
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        return session
    
    @pytest.fixture
    def workflow_engine(self, mock_session):
        """Create WorkflowEngine with mocked dependencies."""
        with patch('app.modules.ai.workflows.workflow_engine.get_settings') as mock_settings:
            mock_settings.return_value = Mock(
                openai_api_key="test-key",
                openai_base_url="https://api.openai.com/v1",
                openai_default_model="gpt-4",
                langsmith_tracing=False
            )
            with patch('app.modules.ai.workflows.workflow_engine.ChatOpenAI'):
                engine = WorkflowEngine(mock_session)
                # Mock the contact manager
                engine.contact_manager = Mock()
                engine.contact_manager.get_conversation_participants = AsyncMock()
                return engine
    
    @pytest.fixture
    def sample_contacts(self):
        """Create sample contacts for testing."""
        return [
            {
                "contact_id": str(uuid4()),
                "agent_id": str(uuid4()),
                "display_name": "Python Expert",
                "agent_name": "python_expert",
                "system_prompt": "You are a Python expert",
                "capabilities": ["python", "debugging", "optimization"],
                "model_preferences": {"temperature": 0.3, "max_tokens": 2000},
                "resource_limits": {"max_requests_per_hour": 100},
                "custom_config": {"response_style": "detailed"},
                "required_permissions": ["code_execution"]
            },
            {
                "contact_id": str(uuid4()),
                "agent_id": str(uuid4()),
                "display_name": "Web Developer",
                "agent_name": "web_dev",
                "system_prompt": "You are a web development expert",
                "capabilities": ["javascript", "react", "css"],
                "model_preferences": {"temperature": 0.5, "max_tokens": 1500},
                "resource_limits": {"max_requests_per_hour": 80},
                "custom_config": {"response_style": "concise"},
                "required_permissions": ["file_access"]
            },
            {
                "contact_id": str(uuid4()),
                "agent_id": str(uuid4()),
                "display_name": "Data Scientist",
                "agent_name": "data_scientist",
                "system_prompt": "You are a data science expert",
                "capabilities": ["python", "statistics", "visualization"],
                "model_preferences": {"temperature": 0.4, "max_tokens": 2500},
                "resource_limits": {"max_requests_per_hour": 60},
                "custom_config": {"response_style": "educational"},
                "required_permissions": ["code_execution", "file_access"]
            }
        ]

    def test_determine_collaboration_mode_debate(self, workflow_engine, sample_contacts):
        """Test debate mode detection."""
        state = {
            "active_contacts": sample_contacts,
            "current_message": "Compare Python vs JavaScript for web development"
        }
        
        mode = workflow_engine._determine_collaboration_mode(state)
        assert mode == "debate_mode"

    def test_determine_collaboration_mode_expert_panel(self, workflow_engine, sample_contacts):
        """Test expert panel mode detection."""
        state = {
            "active_contacts": sample_contacts,
            "current_message": "I need expert opinions on the best approach for data visualization"
        }
        
        mode = workflow_engine._determine_collaboration_mode(state)
        assert mode == "expert_panel"

    def test_determine_collaboration_mode_parallel_processing(self, workflow_engine, sample_contacts):
        """Test parallel processing mode detection."""
        # Set contacts to prefer parallel processing
        for contact in sample_contacts:
            contact["custom_config"]["parallel_processing"] = True
        
        state = {
            "active_contacts": sample_contacts[:2],  # Only 2 contacts
            "current_message": "Help me optimize this code"
        }
        
        mode = workflow_engine._determine_collaboration_mode(state)
        assert mode == "parallel_processing"

    def test_determine_collaboration_mode_default(self, workflow_engine, sample_contacts):
        """Test default collaboration mode."""
        state = {
            "active_contacts": sample_contacts[:2],
            "current_message": "General question about programming"
        }
        
        mode = workflow_engine._determine_collaboration_mode(state)
        assert mode == "default_parallel"

    @pytest.mark.asyncio
    async def test_create_contact_node_personalization(self, workflow_engine):
        """Test contact node creation with personalization."""
        contact = {
            "contact_id": str(uuid4()),
            "agent_id": str(uuid4()),
            "display_name": "Test Agent",
            "system_prompt": "Custom system prompt",
            "model_preferences": {
                "model": "gpt-3.5-turbo",
                "temperature": 0.8,
                "max_tokens": 1000,
                "top_p": 0.9
            },
            "resource_limits": {
                "max_response_time": 20,
                "max_response_length": 2000,
                "disable_llm_calls": False
            },
            "custom_config": {
                "response_style": "concise",
                "include_examples": True
            }
        }
        
        # Mock ChatOpenAI
        with patch('app.modules.ai.workflows.workflow_engine.ChatOpenAI') as mock_llm_class:
            mock_llm = Mock()
            mock_response = Mock()
            mock_response.content = "Test response"
            mock_response.response_metadata = {"token_usage": {"total_tokens": 50}}
            mock_llm.ainvoke = AsyncMock(return_value=mock_response)
            mock_llm_class.return_value = mock_llm
            
            # Create contact node processor
            processor = workflow_engine._create_contact_node(contact)
            
            # Create test state
            state = {
                "conversation_id": str(uuid4()),
                "current_message": "Test message",
                "contact_responses": {},
                "execution_path": [],
                "metadata": {},
                "conversation_memory": None
            }
            
            # Execute processor
            result = await processor(state)
            
            # Verify LLM was configured with contact preferences
            mock_llm_class.assert_called_once()
            call_args = mock_llm_class.call_args[1]
            assert call_args["model"] == "gpt-3.5-turbo"
            assert call_args["temperature"] == 0.8
            assert call_args["max_tokens"] == 1000
            assert call_args["top_p"] == 0.9
            
            # Verify response was added to state
            assert contact["contact_id"] in result["contact_responses"]
            response = result["contact_responses"][contact["contact_id"]]
            assert response["status"] == "success"
            # Response may be modified by filtering
            assert "Test response" in response["response"]

    @pytest.mark.asyncio
    async def test_contact_node_timeout_handling(self, workflow_engine):
        """Test contact node timeout handling."""
        contact = {
            "contact_id": str(uuid4()),
            "agent_id": str(uuid4()),
            "display_name": "Test Agent",
            "system_prompt": "Test prompt",
            "resource_limits": {"max_response_time": 1}  # Very short timeout
        }
        
        with patch('app.modules.ai.workflows.workflow_engine.ChatOpenAI') as mock_llm_class:
            mock_llm = Mock()
            # Simulate timeout
            mock_llm.ainvoke = AsyncMock(side_effect=asyncio.TimeoutError())
            mock_llm_class.return_value = mock_llm
            
            processor = workflow_engine._create_contact_node(contact)
            
            state = {
                "conversation_id": str(uuid4()),
                "current_message": "Test message",
                "contact_responses": {},
                "execution_path": [],
                "metadata": {}
            }
            
            result = await processor(state)
            
            # Verify timeout was handled
            response = result["contact_responses"][contact["contact_id"]]
            assert response["status"] == "timeout"
            assert "timeout" in response["error"]

    @pytest.mark.asyncio
    async def test_contact_node_resource_limits(self, workflow_engine):
        """Test contact node resource limits enforcement."""
        contact = {
            "contact_id": str(uuid4()),
            "agent_id": str(uuid4()),
            "display_name": "Test Agent",
            "system_prompt": "Test prompt",
            "resource_limits": {"disable_llm_calls": True}
        }
        
        processor = workflow_engine._create_contact_node(contact)
        
        state = {
            "conversation_id": str(uuid4()),
            "current_message": "Test message",
            "contact_responses": {},
            "execution_path": [],
            "metadata": {}
        }
        
        result = await processor(state)
        
        # Verify LLM calls were disabled
        response = result["contact_responses"][contact["contact_id"]]
        assert response["status"] == "failed"
        assert "LLM calls disabled" in response["error"]

    def test_apply_response_filtering_concise(self, workflow_engine):
        """Test response filtering for concise style."""
        contact = {
            "custom_config": {"response_style": "concise"}
        }
        
        long_response = "First sentence. Second sentence. Third sentence. Fourth sentence. Fifth sentence."
        filtered = workflow_engine._apply_response_filtering(long_response, contact)
        
        # Should be truncated to first 3 sentences
        assert filtered == "First sentence. Second sentence. Third sentence."

    def test_apply_response_filtering_examples(self, workflow_engine):
        """Test response filtering with examples."""
        contact = {
            "custom_config": {"include_examples": True}
        }
        
        response = "This is a response without examples"
        filtered = workflow_engine._apply_response_filtering(response, contact)
        
        # Should add example text if "example" not already in response
        if "example" not in response.lower():
            assert "For example" in filtered
            assert len(filtered) > len(response)
        else:
            assert filtered == response

    @pytest.mark.asyncio
    async def test_synthesize_parallel_responses(self, workflow_engine):
        """Test parallel response synthesis."""
        with patch('app.modules.ai.workflows.workflow_engine.ChatOpenAI') as mock_llm_class:
            mock_llm = Mock()
            mock_response = Mock()
            mock_response.content = "Synthesized response combining all inputs"
            mock_response.response_metadata = {"token_usage": {"total_tokens": 100}}
            mock_llm.ainvoke = AsyncMock(return_value=mock_response)
            mock_llm_class.return_value = mock_llm
            
            state = {
                "current_message": "How to optimize code?",
                "contact_responses": {
                    "contact1": {
                        "contact_name": "Expert 1",
                        "response": "Use efficient algorithms",
                        "status": "success"
                    },
                    "contact2": {
                        "contact_name": "Expert 2", 
                        "response": "Profile your code first",
                        "status": "success"
                    }
                },
                "execution_path": [],
                "metadata": {}
            }
            
            result = await workflow_engine._synthesize_parallel_responses(state)
            
            # Verify synthesis was performed
            assert "synthesized" in result["contact_responses"]
            synthesized = result["contact_responses"]["synthesized"]
            assert synthesized["status"] == "success"
            assert synthesized["contact_name"] == "Response Synthesizer"

    @pytest.mark.asyncio
    async def test_debate_summarization(self, workflow_engine):
        """Test debate summarization functionality."""
        with patch('app.modules.ai.workflows.workflow_engine.ChatOpenAI') as mock_llm_class:
            mock_llm = Mock()
            mock_response = Mock()
            mock_response.content = "Comprehensive debate summary with key points"
            mock_response.response_metadata = {"token_usage": {"total_tokens": 150}}
            mock_llm.ainvoke = AsyncMock(return_value=mock_response)
            mock_llm_class.return_value = mock_llm
            
            state = {
                "current_message": "Python vs JavaScript debate",
                "contact_responses": {
                    "position_0_contact1": {
                        "response": "Python is better for data science",
                        "status": "success"
                    },
                    "position_1_contact2": {
                        "response": "JavaScript is more versatile",
                        "status": "success"
                    },
                    "rebuttal_contact1": {
                        "response": "Python has better libraries",
                        "status": "success"
                    }
                },
                "execution_path": [],
                "metadata": {}
            }
            
            result = await workflow_engine._summarize_debate(state)
            
            # Verify debate summary was created
            assert "debate_summary" in result["contact_responses"]
            summary = result["contact_responses"]["debate_summary"]
            assert summary["status"] == "success"
            assert summary["contact_name"] == "Debate Moderator"

    @pytest.mark.asyncio
    async def test_expert_consensus_building(self, workflow_engine):
        """Test expert consensus building functionality."""
        with patch('app.modules.ai.workflows.workflow_engine.ChatOpenAI') as mock_llm_class:
            mock_llm = Mock()
            mock_response = Mock()
            mock_response.content = "Expert consensus recommendation"
            mock_response.response_metadata = {"token_usage": {"total_tokens": 120}}
            mock_llm.ainvoke = AsyncMock(return_value=mock_response)
            mock_llm_class.return_value = mock_llm
            
            state = {
                "current_message": "Best practices for machine learning",
                "contact_responses": {
                    "expert_contact1": {
                        "contact_name": "ML Expert 1",
                        "response": "Use cross-validation",
                        "status": "success"
                    },
                    "expert_contact2": {
                        "contact_name": "ML Expert 2",
                        "response": "Feature engineering is crucial",
                        "status": "success"
                    }
                },
                "execution_path": [],
                "metadata": {}
            }
            
            result = await workflow_engine._build_expert_consensus(state)
            
            # Verify expert consensus was built
            assert "expert_consensus" in result["contact_responses"]
            consensus = result["contact_responses"]["expert_consensus"]
            assert consensus["status"] == "success"
            assert consensus["contact_name"] == "Expert Panel Consensus"

    def test_format_collaborative_response(self, workflow_engine):
        """Test collaborative response formatting."""
        responses = [
            {
                "contact_name": "Expert 1",
                "response": "First expert opinion"
            },
            {
                "contact_name": "Expert 2",
                "response": "Second expert opinion"
            }
        ]
        
        formatted = workflow_engine._format_collaborative_response(responses)
        
        expected = "**Expert 1**: First expert opinion\n\n**Expert 2**: Second expert opinion"
        assert formatted == expected

    @pytest.mark.asyncio
    async def test_workflow_execution_metadata(self, workflow_engine, sample_contacts):
        """Test that workflow execution includes proper metadata."""
        conversation_id = uuid4()
        user_id = uuid4()
        message = "Test collaborative message"
        
        # Mock contact manager
        workflow_engine.contact_manager.get_conversation_participants.return_value = sample_contacts
        
        # Mock mention parser
        workflow_engine.mention_parser = Mock()
        workflow_engine.mention_parser.build_routing_context.return_value = {
            "mentions_found": [],
            "mentioned_contacts": [],
            "routing_strategy": "parallel_discussion",
            "has_mentions": False
        }
        
        # Build initial state
        with patch('app.modules.ai.workflows.workflow_engine.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value.isoformat.return_value = "2024-01-01T00:00:00"
            
            state = await workflow_engine._build_initial_state(
                conversation_id, user_id, message, None, uuid4()
            )
        
        # Verify state structure
        assert state["conversation_id"] == str(conversation_id)
        assert state["user_id"] == str(user_id)
        assert state["current_message"] == message
        assert state["active_contacts"] == sample_contacts
        assert state["workflow_type"] == WorkflowType.PARALLEL_DISCUSSION.value
        assert state["routing_strategy"] == "parallel_discussion"
        assert "metadata" in state
        assert len(state["message_history"]) == 1


class TestWorkflowEngineConfiguration:
    """Test workflow engine configuration and settings."""
    
    def test_default_workflow_config(self):
        """Test default workflow configuration."""
        with patch('app.modules.ai.workflows.workflow_engine.get_settings') as mock_settings:
            mock_settings.return_value = Mock(
                openai_api_key="test-key",
                langsmith_tracing=True,
                langsmith_api_key="test-langsmith-key",
                langsmith_endpoint="https://api.smith.langchain.com",
                langsmith_project="test-project"
            )
            with patch('app.modules.ai.workflows.workflow_engine.ChatOpenAI'):
                with patch('os.environ'):
                    engine = WorkflowEngine(Mock())
                    
                    config = engine.default_config
                    assert config["max_parallel_contacts"] == 5
                    assert config["timeout_seconds"] == 30
                    assert config["enable_tracing"] is True
                    assert config["enable_memory"] is True
                    assert config["fallback_on_error"] is True

    def test_workflow_type_determination(self):
        """Test workflow type determination logic."""
        with patch('app.modules.ai.workflows.workflow_engine.get_settings') as mock_settings:
            mock_settings.return_value = Mock(openai_api_key="test-key", langsmith_tracing=False)
            with patch('app.modules.ai.workflows.workflow_engine.ChatOpenAI'):
                engine = WorkflowEngine(Mock())
                
                # Test mention routing
                routing_context = {"has_mentions": True}
                contacts = [{"contact_id": "1"}]
                workflow_type = engine._determine_workflow_type(routing_context, contacts)
                assert workflow_type == WorkflowType.MENTION_ROUTING.value
                
                # Test single contact
                routing_context = {"has_mentions": False}
                contacts = [{"contact_id": "1"}]
                workflow_type = engine._determine_workflow_type(routing_context, contacts)
                assert workflow_type == WorkflowType.SINGLE_CONTACT.value
                
                # Test parallel discussion
                contacts = [{"contact_id": "1"}, {"contact_id": "2"}]
                workflow_type = engine._determine_workflow_type(routing_context, contacts)
                assert workflow_type == WorkflowType.PARALLEL_DISCUSSION.value
                
                # Test sequential processing
                contacts = [{"contact_id": str(i)} for i in range(5)]
                workflow_type = engine._determine_workflow_type(routing_context, contacts)
                assert workflow_type == WorkflowType.SEQUENTIAL_PROCESSING.value