"""
Real LLM Integration Tests

Tests actual LLM calls with the OneAPI service to verify end-to-end functionality.
"""

import pytest
import asyncio
import os
from datetime import datetime
from uuid import uuid4
from unittest.mock import patch

from app.services.langgraph.workflow_engine import WorkflowEngine
from app.services.langgraph.conversation_service import ConversationService
from app.services.langgraph.contact_manager import ContactInstanceManager
from app.infrastructure.database.models import UserModel, AIAgentModel, ContactModel
from app.infrastructure.database.models.contact_model import EntityType
from app.config.settings import get_settings


@pytest.mark.integration
class TestRealLLMIntegration:
    """Test real LLM integration with actual API calls"""
    
    @pytest.fixture
    def skip_if_no_api_key(self):
        """Skip tests if OpenAI API key not available"""
        settings = get_settings()
        if not settings.openai_api_key:
            pytest.skip("OpenAI API key not configured - skipping real LLM tests")
    
    @pytest.mark.asyncio
    async def test_direct_openai_call(self, skip_if_no_api_key):
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
            max_tokens=100
        )
        
        # Test simple call
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Keep responses brief."},
            {"role": "user", "content": "Say hello and confirm you can respond."}
        ]
        
        response = await llm.ainvoke(messages)
        
        # Verify response
        assert response is not None
        assert response.content is not None
        assert len(response.content) > 0
        assert "hello" in response.content.lower()
        
        # Verify token usage if available
        if hasattr(response, 'response_metadata') and 'token_usage' in response.response_metadata:
            token_usage = response.response_metadata['token_usage']
            assert token_usage['total_tokens'] > 0
            print(f"[SUCCESS] Token usage: {token_usage}")
        
        print(f"[SUCCESS] LLM Response: {response.content[:100]}...")
    
    @pytest.mark.asyncio
    async def test_workflow_engine_with_real_llm(self, test_session, skip_if_no_api_key):
        """Test workflow engine with real LLM calls"""
        
        # Create test data
        user = UserModel(
            id=uuid4(),
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            created_at=datetime.utcnow()
        )
        
        agent = AIAgentModel(
            id=uuid4(),
            name="test_assistant",
            display_name="Test Assistant",
            description="A helpful test assistant",
            system_prompt="You are a helpful test assistant. Keep responses brief and friendly.",
            agent_type="system",
            model_preferences={
                "temperature": 0.7,
                "max_tokens": 150
            },
            created_by=user.id,
            created_at=datetime.utcnow()
        )
        
        contact = ContactModel(
            follower_id=user.id,
            following_id=agent.id,
            following_type=EntityType.agent,
            relationship_type="follow",
            is_agent=True,
            created_at=datetime.utcnow()
        )
        
        # Add to session
        test_session.add_all([user, agent, contact])
        await test_session.commit()
        
        # Create conversation service
        conversation_service = ConversationService(test_session)
        
        # Create conversation
        conversation = await conversation_service.create_conversation(
            user_id=user.id,
            title="Real LLM Test",
            initial_agent_ids=[agent.id]
        )
        
        # Send message with real LLM processing
        result = await conversation_service.send_message(
            conversation_id=conversation["conversation_id"],
            user_id=user.id,
            content="Hello! Please introduce yourself briefly."
        )
        
        # Verify workflow executed successfully
        assert result["success"] is True
        assert result["workflow_result"] is not None
        assert len(result["ai_responses"]) > 0
        
        # Verify workflow details
        workflow_result = result["workflow_result"]
        assert workflow_result["workflow_type"] == "single_contact"
        assert workflow_result["success"] is True
        assert workflow_result["final_response"] is not None
        assert len(workflow_result["final_response"]) > 0
        
        # Verify contact response details
        contact_responses = workflow_result["contact_responses"]
        assert len(contact_responses) == 1
        
        contact_response = list(contact_responses.values())[0]
        assert contact_response["status"] == "success"
        assert contact_response["response"] is not None
        assert contact_response["tokens_used"] is not None
        assert contact_response["tokens_used"] > 0
        
        print(f"[SUCCESS] Workflow Response: {workflow_result['final_response'][:100]}...")
        print(f"[SUCCESS] Tokens Used: {contact_response['tokens_used']}")
        
        # Verify messages were stored
        messages = await conversation_service.get_conversation_messages(
            conversation["conversation_id"]
        )
        
        assert len(messages) == 2  # User message + AI response
        assert messages[0]["sender_type"] == "user"
        assert messages[0]["content"] == "Hello! Please introduce yourself briefly."
        assert messages[1]["sender_type"] == "agent" 
        assert messages[1]["content"] == contact_response["response"]
        assert messages[1]["tokens_used"] == contact_response["tokens_used"]
    
    @pytest.mark.asyncio  
    async def test_mention_routing_with_real_llm(self, test_session, skip_if_no_api_key):
        """Test @mention routing with multiple agents and real LLM calls"""
        
        # Create test user
        user = UserModel(
            id=uuid4(),
            username="testuser", 
            email="test@example.com",
            full_name="Test User",
            created_at=datetime.utcnow()
        )
        
        # Create multiple agents
        coder_agent = AIAgentModel(
            id=uuid4(),
            name="coder",
            display_name="Code Assistant",
            description="A helpful coding assistant",
            system_prompt="You are a coding assistant. Keep responses brief and technical.",
            agent_type="system",
            model_preferences={"temperature": 0.3, "max_tokens": 100},
            created_by=user.id,
            created_at=datetime.utcnow()
        )
        
        writer_agent = AIAgentModel(
            id=uuid4(),
            name="writer", 
            display_name="Writing Assistant",
            description="A helpful writing assistant",
            system_prompt="You are a writing assistant. Keep responses brief and creative.",
            agent_type="system", 
            model_preferences={"temperature": 0.8, "max_tokens": 100},
            created_by=user.id,
            created_at=datetime.utcnow()
        )
        
        # Create contacts
        coder_contact = ContactModel(
            follower_id=user.id,
            following_id=coder_agent.id,
            following_type=EntityType.agent,
            relationship_type="follow",
            is_agent=True,
            created_at=datetime.utcnow()
        )
        
        writer_contact = ContactModel(
            follower_id=user.id,
            following_id=writer_agent.id, 
            following_type=EntityType.agent,
            relationship_type="follow",
            is_agent=True,
            created_at=datetime.utcnow()
        )
        
        # Add to session
        test_session.add_all([user, coder_agent, writer_agent, coder_contact, writer_contact])
        await test_session.commit()
        
        # Create conversation service
        conversation_service = ConversationService(test_session)
        
        # Create group conversation
        conversation = await conversation_service.create_conversation(
            user_id=user.id,
            title="Multi-Agent Test",
            initial_agent_ids=[coder_agent.id, writer_agent.id]
        )
        
        # Send message with mentions
        result = await conversation_service.send_message(
            conversation_id=conversation["conversation_id"],
            user_id=user.id,
            content="Hey @coder and @writer, can you both briefly introduce yourselves?"
        )
        
        # Verify results
        assert result["success"] is True
        workflow_result = result["workflow_result"]
        assert workflow_result["workflow_type"] == "mention_routing"
        
        # Should have responses from both mentioned agents
        contact_responses = workflow_result["contact_responses"]
        assert len(contact_responses) == 2
        
        # Verify both agents responded
        successful_responses = [
            r for r in contact_responses.values() 
            if r["status"] == "success"
        ]
        assert len(successful_responses) == 2
        
        # Verify token usage
        total_tokens = sum(r["tokens_used"] or 0 for r in successful_responses)
        assert total_tokens > 0
        
        print(f"[SUCCESS] Multi-agent responses received")
        print(f"[SUCCESS] Total tokens used: {total_tokens}")
        
        for i, response in enumerate(successful_responses, 1):
            print(f"[SUCCESS] Agent {i}: {response['response'][:50]}...")
    
    @pytest.mark.asyncio
    async def test_error_handling_with_invalid_model(self, test_session, skip_if_no_api_key):
        """Test error handling with invalid model configuration"""
        
        # Create test data with invalid model
        user = UserModel(
            id=uuid4(),
            username="testuser",
            email="test@example.com", 
            full_name="Test User",
            created_at=datetime.utcnow()
        )
        
        agent = AIAgentModel(
            id=uuid4(),
            name="broken_agent",
            display_name="Broken Agent",
            description="Agent with invalid model config",
            system_prompt="You are a test assistant.",
            agent_type="system",
            model_preferences={
                "default_model": "invalid-model-name-that-does-not-exist",
                "temperature": 0.7
            },
            created_by=user.id,
            created_at=datetime.utcnow()
        )
        
        contact = ContactModel(
            follower_id=user.id,
            following_id=agent.id,
            following_type=EntityType.agent,
            relationship_type="follow",
            is_agent=True,
            created_at=datetime.utcnow()
        )
        
        test_session.add_all([user, agent, contact])
        await test_session.commit()
        
        # Test error handling
        conversation_service = ConversationService(test_session)
        
        conversation = await conversation_service.create_conversation(
            user_id=user.id,
            title="Error Test",
            initial_agent_ids=[agent.id]
        )
        
        # This should handle the error gracefully
        result = await conversation_service.send_message(
            conversation_id=conversation["conversation_id"],
            user_id=user.id,
            content="Hello, this should fail gracefully."
        )
        
        # The workflow should indicate failure but not crash
        assert result["success"] is False
        assert result["error"] is not None
        
        print(f"[SUCCESS] Error handled gracefully: {result['error'][:100]}")


@pytest.mark.integration 
class TestPerformanceAndMonitoring:
    """Test performance monitoring and metrics collection"""
    
    @pytest.mark.asyncio
    async def test_workflow_performance_tracking(self, test_session, skip_if_no_api_key):
        """Test that workflow performance metrics are collected"""
        
        # This would test the monitoring services we need to implement
        # For now, just verify the structure exists
        
        from app.services.langgraph.workflow_engine import WorkflowEngine
        
        engine = WorkflowEngine(test_session)
        
        # Verify engine has monitoring capabilities
        assert hasattr(engine, 'default_config')
        assert engine.default_config['enable_tracing'] is not None
        
        print("[SUCCESS] Performance tracking structure verified")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])