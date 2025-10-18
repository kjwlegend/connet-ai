"""
Tests for Priority 4: Frontend-Backend API Deep Integration
Tests the real LangGraph integration and enhanced API endpoints.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4
from datetime import datetime

from app.modules.ai.chat.router import (
    chat_with_agent,
    stream_chat_with_agent,
)
from app.modules.ai.agents.router import (
    add_agent_to_contacts,
    check_agent_compatibility,
    get_marketplace_agents,
)
from app.modules.ai.agents.schemas import ChatMessage, ChatRequest
from app.modules.users.schemas import UserResponse


class TestAIChatIntegration:
    """Test AI chat API integration with real LangGraph workflow."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        session = Mock()
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        session.flush = AsyncMock()
        return session
    
    @pytest.fixture
    def mock_user(self):
        """Mock current user."""
        return UserResponse(
            id=str(uuid4()),
            email="test@example.com",
            username="testuser",
            display_name="Test User",
            full_name="Test User",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    @pytest.fixture
    def chat_request(self):
        """Sample chat request."""
        return ChatRequest(
            agent_id=uuid4(),
            conversation_id=uuid4(),
            messages=[
                ChatMessage(role="user", content="Hello, can you help me with Python programming?")
            ]
        )
    
    @pytest.fixture
    def mock_agent(self):
        """Mock AI agent response."""
        return Mock(
            id=uuid4(),
            display_name="Python Expert",
            model_preferences={"default_model": "gpt-4"},
            capabilities=["python", "programming"],
            required_permissions=["code_execution"]
        )

    @pytest.mark.asyncio
    async def test_chat_with_agent_integration(
        self, 
        chat_request, 
        mock_user, 
        mock_db_session, 
        mock_agent
    ):
        """Test chat endpoint with real LangGraph integration."""
        
        # Mock AI Agent Service
        with patch('app.modules.ai.chat.router.AIAgentService') as mock_agent_service:
            mock_service = Mock()
            mock_service.get_agent = AsyncMock(return_value=mock_agent)
            mock_service.update_usage_stats = AsyncMock()
            mock_agent_service.return_value = mock_service
            
            # Mock AI Memory Service
            with patch('app.modules.ai.chat.router.AIMemoryService') as mock_memory_service:
                mock_memory = Mock()
                mock_memory.get_contextual_memories = AsyncMock(return_value=[])
                mock_memory.store_short_term_memory = AsyncMock()
                mock_memory_service.return_value = mock_memory
                
                # Mock WorkflowEngine
                with patch('app.modules.ai.chat.router.WorkflowEngine') as mock_workflow:
                    mock_engine = Mock()
                    
                    # Mock workflow result
                    workflow_result = {
                        "execution_id": str(uuid4()),
                        "workflow_type": "single_contact",
                        "final_response": "Hello! I'd be happy to help you with Python programming. What specific topic would you like to learn about?",
                        "contact_responses": {
                            "contact-1": {
                                "status": "success",
                                "tokens_used": 150,
                                "contact_id": "contact-1"
                            }
                        },
                        "success": True,
                        "total_tokens": 150,
                        "metadata": {
                            "contact_execution_details": {
                                "contact-1": {
                                    "model_used": "gpt-4",
                                    "tokens_consumed": 150
                                }
                            }
                        }
                    }
                    
                    mock_engine.execute_conversation_workflow = AsyncMock(return_value=workflow_result)
                    mock_workflow.return_value = mock_engine
                    
                    # Execute the endpoint
                    response = await chat_with_agent(
                        request=chat_request,
                        current_user=mock_user,
                        db=mock_db_session
                    )
                    
                    # Verify the response
                    assert response.content == workflow_result["final_response"]
                    assert response.agent_id == chat_request.agent_id
                    assert response.model_used == "gpt-4"
                    assert response.token_usage["total_tokens"] == 150
                    assert response.confidence_score == 0.85  # Success case
                    
                    # Verify workflow was called correctly
                    mock_engine.execute_conversation_workflow.assert_called_once()
                    call_args = mock_engine.execute_conversation_workflow.call_args[1]
                    assert call_args["conversation_id"] == chat_request.conversation_id
                    assert call_args["user_id"] == mock_user.id
                    assert call_args["message"] == "Hello, can you help me with Python programming?"

    @pytest.mark.asyncio
    async def test_chat_with_agent_workflow_failure(
        self, 
        chat_request, 
        mock_user, 
        mock_db_session, 
        mock_agent
    ):
        """Test chat endpoint when workflow fails."""
        
        # Mock services with workflow failure
        with patch('app.modules.ai.chat.router.AIAgentService') as mock_agent_service:
            mock_service = Mock()
            mock_service.get_agent = AsyncMock(return_value=mock_agent)
            mock_service.update_usage_stats = AsyncMock()
            mock_agent_service.return_value = mock_service
            
            with patch('app.modules.ai.chat.router.AIMemoryService') as mock_memory_service:
                mock_memory = Mock()
                mock_memory.get_contextual_memories = AsyncMock(return_value=[])
                mock_memory.store_short_term_memory = AsyncMock()
                mock_memory_service.return_value = mock_memory
                
                with patch('app.modules.ai.chat.router.WorkflowEngine') as mock_workflow:
                    mock_engine = Mock()
                    
                    # Mock failed workflow result
                    workflow_result = {
                        "execution_id": str(uuid4()),
                        "workflow_type": "single_contact",
                        "final_response": "I apologize, but I'm unable to process your request at the moment.",
                        "contact_responses": {},
                        "success": False,
                        "total_tokens": 0,
                        "metadata": {}
                    }
                    
                    mock_engine.execute_conversation_workflow = AsyncMock(return_value=workflow_result)
                    mock_workflow.return_value = mock_engine
                    
                    # Execute the endpoint
                    response = await chat_with_agent(
                        request=chat_request,
                        current_user=mock_user,
                        db=mock_db_session
                    )
                    
                    # Verify failure handling
                    assert response.content == workflow_result["final_response"]
                    assert response.confidence_score == 0.5  # Failure case
                    assert response.token_usage["total_tokens"] == 0

    @pytest.mark.asyncio
    async def test_stream_chat_simulation(
        self, 
        chat_request, 
        mock_user, 
        mock_db_session, 
        mock_agent
    ):
        """Test streaming chat endpoint simulation."""
        
        # Mock services
        with patch('app.modules.ai.chat.router.AIAgentService') as mock_agent_service:
            mock_service = Mock()
            mock_service.get_agent = AsyncMock(return_value=mock_agent)
            mock_agent_service.return_value = mock_service
            
            with patch('app.modules.ai.chat.router.AIMemoryService') as mock_memory_service:
                mock_memory = Mock()
                mock_memory.get_contextual_memories = AsyncMock(return_value=[])
                mock_memory.store_short_term_memory = AsyncMock()
                mock_memory_service.return_value = mock_memory
                
                with patch('app.modules.ai.chat.router.WorkflowEngine') as mock_workflow:
                    mock_engine = Mock()
                    
                    workflow_result = {
                        "execution_id": str(uuid4()),
                        "workflow_type": "single_contact",
                        "final_response": "Hello there! How can I help?",
                        "contact_responses": {
                            "contact-1": {"status": "success", "tokens_used": 50}
                        },
                        "success": True,
                        "total_tokens": 50
                    }
                    
                    mock_engine.execute_conversation_workflow = AsyncMock(return_value=workflow_result)
                    mock_workflow.return_value = mock_engine
                    
                    # Execute streaming endpoint
                    response = await stream_chat_with_agent(
                        request=chat_request,
                        current_user=mock_user,
                        db=mock_db_session
                    )
                    
                    # Verify it returns a StreamingResponse
                    from fastapi.responses import StreamingResponse
                    assert isinstance(response, StreamingResponse)
                    assert response.media_type == "text/plain"
                    assert response.headers["Content-Type"] == "text/event-stream"


class TestAgentMarketplaceIntegration:
    """Test agent marketplace API integration."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return Mock()
    
    @pytest.fixture
    def mock_user(self):
        """Mock current user."""
        return UserResponse(
            id=str(uuid4()),
            email="test@example.com",
            username="testuser",
            display_name="Test User",
            full_name="Test User",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    @pytest.mark.asyncio
    async def test_add_agent_to_contacts(self, mock_user, mock_db_session):
        """Test adding agent to contacts endpoint."""
        
        agent_id = uuid4()
        customization_data = {
            "custom_system_prompt": "You are my personal coding assistant",
            "instance_config": {"temperature": 0.7, "max_tokens": 2000},
            "resource_limits": {"max_requests_per_hour": 50},
            "display_name": "My Coding Assistant"
        }
        
        # Mock ContactInstanceManager
        with patch('app.modules.ai.agents.router.ContactInstanceManager') as mock_contact_manager:
            mock_manager = Mock()
            
            # Mock successful conversion
            contact_info = {
                "agent_id": str(agent_id),
                "follower_id": str(mock_user.id),
                "contact_id": str(uuid4()),
                "display_name": "My Coding Assistant",
                "system_prompt": "You are my personal coding assistant",
                "model_preferences": {"temperature": 0.7, "max_tokens": 2000}
            }
            
            mock_manager.agent_to_contact_conversion = AsyncMock(return_value=contact_info)
            mock_contact_manager.return_value = mock_manager
            
            # Execute endpoint
            response = await add_agent_to_contacts(
                agent_id=agent_id,
                customization_data=customization_data,
                current_user=mock_user,
                db=mock_db_session
            )
            
            # Verify response
            assert response["message"] == "Agent successfully added to contacts"
            assert response["contact_info"] == contact_info
            
            # Verify manager was called correctly
            mock_manager.agent_to_contact_conversion.assert_called_once_with(
                user_id=mock_user.id,
                agent_id=agent_id,
                custom_system_prompt=customization_data["custom_system_prompt"],
                instance_config=customization_data["instance_config"],
                resource_limits=customization_data["resource_limits"],
                display_name_override=customization_data["display_name"]
            )

    @pytest.mark.asyncio
    async def test_check_agent_compatibility(self, mock_user, mock_db_session):
        """Test agent compatibility check endpoint."""
        
        agent_id = uuid4()
        
        # Mock agent
        mock_agent = Mock(
            id=agent_id,
            capabilities=["python", "web_development"],
            required_permissions=["code_execution", "file_access"]
        )
        
        # Mock services
        with patch('app.modules.ai.agents.router.AIAgentService') as mock_agent_service:
            mock_service = Mock()
            mock_service.get_agent = AsyncMock(return_value=mock_agent)
            mock_agent_service.return_value = mock_service
            
            with patch('app.modules.ai.agents.router.ContactInstanceManager') as mock_contact_manager:
                mock_manager = Mock()
                mock_manager.get_contact_effective_config = AsyncMock(return_value=None)  # Not already added
                mock_contact_manager.return_value = mock_manager
                
                # Execute endpoint
                response = await check_agent_compatibility(
                    agent_id=agent_id,
                    current_user=mock_user,
                    db=mock_db_session
                )
                
                # Verify response
                assert response["compatible"] is True
                assert response["already_added"] is False
                assert response["agent_capabilities"] == ["python", "web_development"]
                assert response["required_permissions"] == ["code_execution", "file_access"]
                assert "customization_options" in response
                assert response["customization_options"]["custom_system_prompt"] is True

    @pytest.mark.asyncio
    async def test_get_marketplace_agents(self, mock_user, mock_db_session):
        """Test marketplace agents endpoint."""
        
        # Mock marketplace response
        marketplace_response = {
            "agents": [
                {
                    "id": str(uuid4()),
                    "name": "python_expert",
                    "display_name": "Python Expert",
                    "description": "Expert Python programming assistant",
                    "category": "programming",
                    "featured": True
                },
                {
                    "id": str(uuid4()),
                    "name": "web_developer",
                    "display_name": "Web Developer",
                    "description": "Full-stack web development assistant",
                    "category": "web_development",
                    "featured": False
                }
            ],
            "total": 2,
            "limit": 20,
            "offset": 0
        }
        
        # Mock AIAgentService
        with patch('app.modules.ai.agents.router.AIAgentService') as mock_agent_service:
            mock_service = Mock()
            mock_service.get_marketplace_agents = AsyncMock(return_value=marketplace_response)
            mock_agent_service.return_value = mock_service
            
            # Execute endpoint
            response = await get_marketplace_agents(
                category="programming",
                search="python",
                featured=True,
                limit=20,
                offset=0,
                current_user=mock_user,
                db=mock_db_session
            )
            
            # Verify response
            assert response == marketplace_response
            
            # Verify service call
            mock_service.get_marketplace_agents.assert_called_once_with(
                category="programming",
                search="python",
                featured=True,
                limit=20,
                offset=0
            )


class TestAPIPerformanceAndErrorHandling:
    """Test API performance and error handling requirements."""
    
    @pytest.mark.asyncio
    async def test_chat_endpoint_error_handling(self):
        """Test chat endpoint error handling."""
        from fastapi import HTTPException
        
        chat_request = ChatRequest(
            agent_id=uuid4(),
            messages=[ChatMessage(role="user", content="Test message")]
        )
        
        mock_user = UserResponse(
            id=uuid4(),
            email="test@example.com",
            username="testuser",
            display_name="Test User",
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        # Test agent not found
        with patch('app.modules.ai.chat.router.AIAgentService') as mock_agent_service:
            mock_service = Mock()
            mock_service.get_agent = AsyncMock(return_value=None)  # Agent not found
            mock_agent_service.return_value = mock_service
            
            with pytest.raises(HTTPException) as exc_info:
                await chat_with_agent(
                    request=chat_request,
                    current_user=mock_user,
                    db=Mock()
                )
            
            assert exc_info.value.status_code == 404
            assert "Agent not found" in str(exc_info.value.detail)

    def test_api_response_structure(self):
        """Test API response structure consistency."""
        # This would be a integration test to verify response structure
        # For now, just verify that our response models are properly structured
        
        from app.modules.ai.agents.schemas import ChatResponse
        from datetime import datetime
        from uuid import uuid4
        
        # Test ChatResponse structure
        response = ChatResponse(
            conversation_id=uuid4(),
            message_id=uuid4(),
            agent_id=uuid4(),
            content="Test response",
            role="assistant",
            model_used="gpt-4",
            token_usage={"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
            generation_time=1.2,
            tools_used=[],
            context_sources=[],
            confidence_score=0.85,
            created_at=datetime.utcnow()
        )
        
        # Verify all required fields are present
        assert response.conversation_id is not None
        assert response.message_id is not None
        assert response.agent_id is not None
        assert response.content == "Test response"
        assert response.role == "assistant"
        assert response.model_used == "gpt-4"
        assert response.token_usage["total_tokens"] == 150
        assert response.generation_time == 1.2
        assert response.confidence_score == 0.85
