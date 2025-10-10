"""
Simple LangGraph Integration Tests

Tests basic functionality without complex database setup.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from uuid import uuid4

from app.modules.ai.workflows.mention_parser import MentionParser
from app.modules.ai.workflows.workflow_engine import WorkflowEngine
from app.modules.ai.workflows.state_models import ContactInfo, WorkflowType


class TestBasicLangGraphFunctionality:
    """Test basic LangGraph functionality without database dependencies"""
    
    def test_mention_parser_integration(self):
        """Test complete mention parsing workflow"""
        parser = MentionParser()
        
        # Test complex message with multiple mentions
        message = "Hey @coder and @writer, can you help @reviewer check this code?"
        
        mentions = parser.extract_mentions(message)
        assert mentions == ["coder", "writer", "reviewer"]
        
        # Test validation
        contacts = [
            ContactInfo(
                contact_id="1",
                agent_id="agent1", 
                follower_id="user1",
                agent_name="coder",
                display_name="Code Assistant",
                system_prompt="You help with coding",
                model_preferences={},
                is_active=True
            ),
            ContactInfo(
                contact_id="2",
                agent_id="agent2",
                follower_id="user1", 
                agent_name="writer",
                display_name="Writing Assistant",
                system_prompt="You help with writing",
                model_preferences={},
                is_active=True
            )
        ]
        
        validation = parser.validate_mentions(message, contacts)
        assert not validation["all_valid"]  # reviewer not available
        assert "coder" in validation["valid_mentions"]
        assert "writer" in validation["valid_mentions"] 
        assert "reviewer" in validation["invalid_mentions"]
    
    def test_workflow_type_determination(self):
        """Test workflow type selection logic"""
        # Mock a workflow engine (without database)
        with patch('app.modules.ai.workflows.workflow_engine.WorkflowEngine.__init__', 
                   return_value=None):
            engine = WorkflowEngine.__new__(WorkflowEngine)
            
            # Test single contact workflow
            routing_context = {"has_mentions": False}
            active_contacts = [Mock()]  # One contact
            
            workflow_type = engine._determine_workflow_type(routing_context, active_contacts)
            assert workflow_type == WorkflowType.SINGLE_CONTACT.value
            
            # Test mention routing
            routing_context = {"has_mentions": True}
            active_contacts = [Mock(), Mock()]  # Multiple contacts
            
            workflow_type = engine._determine_workflow_type(routing_context, active_contacts)
            assert workflow_type == WorkflowType.MENTION_ROUTING.value
            
            # Test parallel discussion
            routing_context = {"has_mentions": False}
            active_contacts = [Mock(), Mock(), Mock()]  # 3 contacts
            
            workflow_type = engine._determine_workflow_type(routing_context, active_contacts)
            assert workflow_type == WorkflowType.PARALLEL_DISCUSSION.value
    
    def test_state_models_structure(self):
        """Test that state models are properly structured"""
        from app.modules.ai.workflows.state_models import (
            ConversationState, ContactInfo, MessageState, ContactResponse
        )
        
        # Test ContactInfo structure
        contact = ContactInfo(
            contact_id="test-contact-1",
            agent_id="agent-1",
            follower_id="user-1", 
            agent_name="test_agent",
            display_name="Test Agent",
            system_prompt="You are a test agent",
            model_preferences={"temperature": 0.7},
            is_active=True
        )
        
        assert contact["agent_name"] == "test_agent"
        assert contact["is_active"] is True
        
        # Test MessageState structure
        message = MessageState(
            id="msg-1",
            content="Hello @test_agent",
            sender_id="user-1",
            sender_type="user",
            sender_name="Test User",
            timestamp=datetime.utcnow().isoformat(),
            message_type="text",
            mentions=["test_agent"]
        )
        
        assert message["content"] == "Hello @test_agent"
        assert message["mentions"] == ["test_agent"]
    
    def test_mention_routing_context(self):
        """Test mention routing context building"""
        parser = MentionParser()
        
        contacts = [
            ContactInfo(
                contact_id="1",
                agent_id="agent1",
                follower_id="user1",
                agent_name="assistant",
                display_name="AI Assistant", 
                system_prompt="You are helpful",
                model_preferences={},
                is_active=True
            )
        ]
        
        # Test message with mention
        message = "Hey @assistant, can you help me?"
        context = parser.build_routing_context(message, contacts)
        
        assert context["has_mentions"] is True
        assert context["routing_strategy"] == "mention_based"
        assert len(context["mentioned_contacts"]) == 1
        assert context["mentioned_contacts"][0]["agent_name"] == "assistant"
        
        # Test message without mention
        message = "Hello there!"
        context = parser.build_routing_context(message, contacts)
        
        assert context["has_mentions"] is False
        assert context["routing_strategy"] == "default"
        assert len(context["mentioned_contacts"]) == 0
    
    def test_workflow_configuration(self):
        """Test workflow configuration structure"""
        from app.modules.ai.workflows.state_models import WorkflowConfig
        
        config = WorkflowConfig(
            max_parallel_contacts=3,
            timeout_seconds=30,
            enable_tracing=True,
            enable_memory=False,
            fallback_on_error=True
        )
        
        assert config["max_parallel_contacts"] == 3
        assert config["enable_tracing"] is True
        assert config["enable_memory"] is False


class TestAPIEndpointStructure:
    """Test that API endpoints are properly structured"""
    
    def test_langgraph_endpoints_exist(self):
        """Test that LangGraph endpoints are defined"""
        from app.api.v1.endpoints.langgraph_chat import router
        
        # Check that router exists and has routes
        assert router is not None
        
        # Get list of routes 
        routes = [route for route in router.routes]
        route_paths = [route.path for route in routes if hasattr(route, 'path')]
        
        # Should have core endpoints
        expected_paths = [
            "/conversations",
            "/conversations/{conversation_id}/messages",
            "/conversations/{conversation_id}/agents",
            "/mentions/validate"
        ]
        
        for expected_path in expected_paths:
            assert any(expected_path in path for path in route_paths), f"Missing endpoint: {expected_path}"
    
    def test_router_integration(self):
        """Test that LangGraph router is integrated into main API"""
        from app.api.v1.router import api_router
        
        # Check that the router includes our LangGraph endpoints
        route_paths = []
        for route in api_router.routes:
            if hasattr(route, 'path'):
                route_paths.append(route.path)
            elif hasattr(route, 'path_regex'):
                # For sub-routers, check if they have the langgraph prefix
                path_str = str(route.path_regex.pattern)
                if 'langgraph' in path_str:
                    route_paths.append('/langgraph/*')
        
        assert any('langgraph' in path for path in route_paths), "LangGraph router not integrated"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])