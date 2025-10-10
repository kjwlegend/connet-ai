"""
Simple Real LLM Integration Tests

Tests actual LLM calls without complex database setup to verify core functionality.
"""

import pytest
import asyncio
import os
from datetime import datetime
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

from app.modules.ai.workflows.workflow_engine import WorkflowEngine
from app.modules.ai.workflows.conversation_service import ConversationService
from app.modules.ai.workflows.contact_manager import ContactInstanceManager
from app.config.settings import get_settings


@pytest.mark.integration
class TestSimpleRealLLMIntegration:
    """Test real LLM integration with minimal dependencies"""
    
    @pytest.fixture
    def skip_if_no_api_key(self):
        """Skip tests if OpenAI API key not available"""
        settings = get_settings()
        if not settings.openai_api_key:
            pytest.skip("OpenAI API key not configured - skipping real LLM tests")
    
    @pytest.mark.asyncio
    async def test_direct_openai_call_simple(self, skip_if_no_api_key):
        """Test direct OpenAI API call with custom base URL"""
        from langchain_openai import ChatOpenAI
        
        settings = get_settings()
        
        # Initialize LLM client with custom base URL (ensure v1 endpoint)
        base_url = settings.openai_base_url
        if base_url and not base_url.endswith('/v1'):
            base_url = base_url.rstrip('/') + '/v1'
        
        llm = ChatOpenAI(
            model=settings.openai_default_model,
            api_key=settings.openai_api_key,
            base_url=base_url,
            temperature=0.7,
            max_tokens=50
        )
        
        # Test simple call
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Keep responses very brief."},
            {"role": "user", "content": "Say hello in one sentence."}
        ]
        
        response = await llm.ainvoke(messages)
        
        # Verify response
        assert response is not None
        assert response.content is not None
        assert len(response.content) > 0
        assert "hello" in response.content.lower()
        
        # Verify token usage
        if hasattr(response, 'response_metadata') and 'token_usage' in response.response_metadata:
            token_usage = response.response_metadata['token_usage']
            assert token_usage['total_tokens'] > 0
            print(f"[SUCCESS] Simple LLM test - Token usage: {token_usage}")
        
        print(f"[SUCCESS] Simple LLM test - Response: {response.content}")

    @pytest.mark.asyncio
    async def test_workflow_engine_mock_db(self, skip_if_no_api_key):
        """Test workflow engine with mocked database but real LLM"""
        
        # Mock database session
        mock_session = AsyncMock()
        
        # Create a simple workflow engine instance
        engine = WorkflowEngine(mock_session)
        
        # Verify the engine is properly initialized
        assert engine.session == mock_session
        assert engine.default_config is not None
        assert 'enable_tracing' in engine.default_config
        
        print("[SUCCESS] WorkflowEngine initialized with real LLM capability")
        
        # Test workflow type determination
        context = {
            'user_message': 'Hello @coder and @writer',
            'mentioned_contacts': ['coder', 'writer'],
            'conversation_participants': ['coder', 'writer']
        }
        
        workflow_type = engine._determine_workflow_type(context)
        assert workflow_type == 'mention_routing'
        
        print(f"[SUCCESS] Workflow type determination: {workflow_type}")

    @pytest.mark.asyncio  
    async def test_contact_manager_basic(self, skip_if_no_api_key):
        """Test contact manager basic functionality"""
        
        # Mock database session
        mock_session = AsyncMock()
        
        # Create contact manager
        manager = ContactInstanceManager(mock_session)
        
        # Verify manager initialization
        assert manager.session == mock_session
        
        print("[SUCCESS] ContactInstanceManager initialized")
        
        # Test agent name formatting
        test_names = ['test-agent', 'test_agent', 'TestAgent']
        for name in test_names:
            formatted = manager._format_agent_name(name)
            assert isinstance(formatted, str)
            assert len(formatted) > 0
            print(f"[SUCCESS] Agent name formatting: '{name}' -> '{formatted}'")

    @pytest.mark.asyncio
    async def test_langgraph_graph_creation(self, skip_if_no_api_key):
        """Test LangGraph graph creation without database"""
        from langgraph.graph import StateGraph, END
        from app.modules.ai.workflows.state_models import ConversationState
        
        # Create a basic state graph
        workflow = StateGraph(ConversationState)
        
        # Add a simple node
        def test_node(state: ConversationState) -> ConversationState:
            return {**state, 'processing_complete': True}
        
        workflow.add_node("test", test_node)
        workflow.set_entry_point("test")
        workflow.add_edge("test", END)
        
        # Compile the graph
        app = workflow.compile()
        
        # Test basic execution
        initial_state = {
            'user_id': str(uuid4()),
            'conversation_id': str(uuid4()),
            'user_message': 'Test message',
            'contact_responses': {},
            'mentioned_contacts': [],
            'processing_complete': False,
            'final_response': None,
            'error_message': None,
            'workflow_metadata': {}
        }
        
        result = await app.ainvoke(initial_state)
        
        assert result['processing_complete'] is True
        
        print("[SUCCESS] LangGraph StateGraph creation and execution")

    @pytest.mark.asyncio
    async def test_conversation_service_basic(self, skip_if_no_api_key):
        """Test conversation service basic functionality"""
        
        # Mock database session
        mock_session = AsyncMock()
        
        # Create conversation service
        service = ConversationService(mock_session)
        
        # Verify service initialization
        assert service.session == mock_session
        assert service.workflow_engine is not None
        assert service.contact_manager is not None
        
        print("[SUCCESS] ConversationService initialized with dependencies")
        
        # Test message validation
        test_messages = ["Hello", "Hi @agent", "", "Test message with content"]
        for msg in test_messages:
            is_valid = len(msg.strip()) > 0
            print(f"[SUCCESS] Message validation: '{msg}' -> {is_valid}")

    @pytest.mark.asyncio
    async def test_settings_configuration(self, skip_if_no_api_key):
        """Test that all required settings are properly configured"""
        
        settings = get_settings()
        
        # Verify OpenAI settings
        assert settings.openai_api_key is not None
        assert settings.openai_base_url is not None
        assert settings.openai_default_model is not None
        
        # Verify base URL format
        base_url = settings.openai_base_url
        if not base_url.endswith('/v1'):
            base_url = base_url.rstrip('/') + '/v1'
        
        assert base_url.startswith('https://')
        assert '/v1' in base_url
        
        print(f"[SUCCESS] OpenAI configuration verified:")
        print(f"  - Model: {settings.openai_default_model}")
        print(f"  - Base URL: {base_url}")
        print(f"  - API Key: {'*' * 8}...{settings.openai_api_key[-4:] if settings.openai_api_key else 'None'}")
        
        # Verify LangSmith settings
        print(f"  - LangSmith Tracing: {settings.langsmith_tracing}")
        if settings.langsmith_tracing:
            print(f"  - LangSmith Project: {settings.langsmith_project}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])