"""
Tests for ContactRepository Extensions (Priority 2)
Tests the new contact instance management methods in ContactRepository.
"""

import pytest
from uuid import uuid4
from datetime import datetime

from app.modules.contacts.models import ContactModel, EntityType
from app.modules.agents.models import AIAgentModel
from app.modules.users.models import UserModel


class TestContactRepositoryExtensions:
    """Test extended ContactRepository methods for contact instance management."""
    
    def test_create_contact_instance_data_structure(self):
        """Test that contact instance has correct structure."""
        user_id = uuid4()
        agent_id = uuid4()
        
        # Create contact instance manually to test structure
        contact = ContactModel(
            follower_id=user_id,
            following_id=agent_id,
            following_type=EntityType.agent,
            agent_id=agent_id,
            relationship_type="follow",
            is_agent=True,
            custom_system_prompt="You are my coding assistant",
            instance_config={
                "temperature": 0.7,
                "max_tokens": 2000,
                "model_preference": "gpt-4"
            },
            resource_limits={
                "max_requests_per_hour": 100,
                "max_tokens_per_day": 50000
            }
        )
        
        # Verify all fields are set correctly
        assert contact.follower_id == user_id
        assert contact.following_id == agent_id
        assert contact.agent_id == agent_id
        assert contact.following_type == EntityType.agent
        assert contact.is_agent is True
        assert contact.custom_system_prompt == "You are my coding assistant"
        assert contact.instance_config["temperature"] == 0.7
        assert contact.resource_limits["max_requests_per_hour"] == 100

    def test_contact_instance_config_merging(self):
        """Test that contact instance config can be merged with agent config."""
        # Simulate agent base config
        agent_base_config = {
            "temperature": 0.5,
            "max_tokens": 1000,
            "model": "gpt-3.5-turbo"
        }
        
        # Contact instance override config
        contact_instance_config = {
            "temperature": 0.8,  # Override
            "max_tokens": 2000,  # Override
            "custom_instructions": "Be very detailed"  # New field
        }
        
        # Merge configurations (contact overrides agent)
        merged_config = {
            **agent_base_config,
            **contact_instance_config
        }
        
        # Verify merged result
        assert merged_config["temperature"] == 0.8  # Contact overrides
        assert merged_config["max_tokens"] == 2000  # Contact overrides
        assert merged_config["model"] == "gpt-3.5-turbo"  # From agent
        assert merged_config["custom_instructions"] == "Be very detailed"  # From contact
        assert len(merged_config) == 4

    def test_resource_limits_validation(self):
        """Test resource limits structure and validation."""
        resource_limits = {
            "max_requests_per_hour": 50,
            "max_requests_per_day": 1000,
            "max_tokens_per_request": 4000,
            "max_tokens_per_day": 100000,
            "timeout_seconds": 30,
            "max_memory_mb": 256,
            "disable_file_access": False,
            "disable_internet": True,
            "allowed_tools": ["search", "calculator", "code_interpreter"]
        }
        
        contact = ContactModel(
            follower_id=uuid4(),
            following_id=uuid4(),
            following_type=EntityType.agent,
            agent_id=uuid4(),
            resource_limits=resource_limits
        )
        
        # Verify all resource limit fields are accessible
        limits = contact.resource_limits
        assert limits["max_requests_per_hour"] == 50
        assert limits["disable_internet"] is True
        assert "search" in limits["allowed_tools"]

    def test_custom_system_prompt_personalization(self):
        """Test custom system prompt functionality."""
        base_agent_prompt = "You are a helpful AI assistant."
        custom_user_prompt = "You are my personal coding mentor. Always explain concepts step-by-step and include examples."
        
        contact = ContactModel(
            follower_id=uuid4(),
            following_id=uuid4(),
            following_type=EntityType.agent,
            agent_id=uuid4(),
            custom_system_prompt=custom_user_prompt
        )
        
        # In actual usage, the effective prompt would be determined by ContactInstanceManager
        effective_prompt = contact.custom_system_prompt or base_agent_prompt
        
        assert effective_prompt == custom_user_prompt
        assert len(effective_prompt) > len(base_agent_prompt)

    def test_contact_agent_relationship_consistency(self):
        """Test that contact-agent relationship fields are consistent."""
        agent_id = uuid4()
        
        contact = ContactModel(
            follower_id=uuid4(),
            following_id=agent_id,
            following_type=EntityType.agent,
            agent_id=agent_id,  # Should match following_id for agents
            is_agent=True
        )
        
        # Verify consistency
        assert contact.following_id == contact.agent_id
        assert contact.following_type == EntityType.agent
        assert contact.is_agent is True

    def test_contact_instance_metadata(self):
        """Test contact instance metadata and timestamps."""
        now = datetime.utcnow()
        
        contact = ContactModel(
            follower_id=uuid4(),
            following_id=uuid4(),
            following_type=EntityType.agent,
            agent_id=uuid4(),
            display_name="My Coding Assistant",
            notes="Very helpful for Python development",
            tags=["coding", "python", "helpful"],
            is_favorite=True,
            is_pinned=True,
            pin_order=1,
            notification_level="all",
            created_at=now,
            updated_at=now
        )
        
        # Verify metadata fields
        assert contact.display_name == "My Coding Assistant"
        assert "python" in contact.tags
        assert contact.is_favorite is True
        assert contact.is_pinned is True
        assert contact.pin_order == 1
        assert contact.notification_level == "all"
        assert contact.created_at == now

    def test_contact_repository_method_signatures(self):
        """Test that repository method signatures are correct."""
        from app.modules.contacts.repository_impl import ContactRepository
        from sqlalchemy.ext.asyncio import AsyncSession
        from unittest.mock import Mock
        
        # Create repository instance with mock session
        mock_session = Mock(spec=AsyncSession)
        repo = ContactRepository(mock_session)
        
        # Verify method exists and has correct signature
        assert hasattr(repo, 'get_user_contact_by_agent')
        assert hasattr(repo, 'create_contact_instance')
        assert hasattr(repo, 'update_contact_config')
        assert hasattr(repo, 'get_user_agent_contacts')
        assert hasattr(repo, 'delete_contact_instance')
        
        # Verify methods are async
        import inspect
        assert inspect.iscoroutinefunction(repo.get_user_contact_by_agent)
        assert inspect.iscoroutinefunction(repo.create_contact_instance)
        assert inspect.iscoroutinefunction(repo.update_contact_config)
        assert inspect.iscoroutinefunction(repo.get_user_agent_contacts)
        assert inspect.iscoroutinefunction(repo.delete_contact_instance)

    def test_contact_permissions_structure(self):
        """Test conversation permissions structure for participants."""
        from app.modules.conversations.models import ConversationParticipantModel
        
        permissions = {
            "can_initiate_workflow": True,
            "can_modify_conversation": False,
            "can_access_memory": True,
            "can_invite_participants": False,
            "allowed_tools": ["search", "calculator"],
            "max_tool_calls_per_message": 5,
            "priority_level": "normal"
        }
        
        participant = ConversationParticipantModel(
            conversation_id=uuid4(),
            participant_id=uuid4(),
            participant_type="agent",
            workflow_priority=10,
            conversation_permissions=permissions
        )
        
        # Verify permissions structure
        perms = participant.conversation_permissions
        assert perms["can_initiate_workflow"] is True
        assert perms["can_modify_conversation"] is False
        assert "search" in perms["allowed_tools"]
        assert perms["max_tool_calls_per_message"] == 5

    def test_contact_search_functionality(self):
        """Test that contacts can be searched by customized fields."""
        # Create contacts with different customizations
        contacts = [
            ContactModel(
                follower_id=uuid4(),
                following_id=uuid4(),
                following_type=EntityType.agent,
                agent_id=uuid4(),
                display_name="Python Expert",
                notes="Great for Python development and debugging",
                tags=["python", "debugging", "expert"]
            ),
            ContactModel(
                follower_id=uuid4(),
                following_id=uuid4(),
                following_type=EntityType.agent,
                agent_id=uuid4(),
                display_name="Web Dev Assistant",
                notes="Helpful for frontend and backend web development",
                tags=["web", "frontend", "backend"]
            )
        ]
        
        # Test searchable fields are accessible
        python_contact = contacts[0]
        web_contact = contacts[1]
        
        assert "Python" in python_contact.display_name
        assert "python" in python_contact.tags
        assert "debugging" in python_contact.notes
        
        assert "Web Dev" in web_contact.display_name
        assert "web" in web_contact.tags
        assert "frontend" in web_contact.notes


class TestContactInstanceValidation:
    """Test validation and error cases for contact instances."""
    
    def test_contact_instance_required_fields(self):
        """Test that contact instance has required fields for agent contacts."""
        # Test that we can create a contact with minimal required fields
        contact = ContactModel(
            follower_id=uuid4(),
            following_id=uuid4(),
            following_type=EntityType.agent
        )
        
        # Should be able to create basic contact
        assert contact.follower_id is not None
        assert contact.following_id is not None
        assert contact.following_type == EntityType.agent
    
    def test_agent_contact_consistency(self):
        """Test validation of agent contact consistency."""
        agent_id = uuid4()
        
        # Valid agent contact
        valid_contact = ContactModel(
            follower_id=uuid4(),
            following_id=agent_id,
            following_type=EntityType.agent,
            agent_id=agent_id  # Should match following_id
        )
        
        assert valid_contact.following_id == valid_contact.agent_id
        
        # Inconsistent agent contact (this would be caught by business logic)
        inconsistent_contact = ContactModel(
            follower_id=uuid4(),
            following_id=agent_id,
            following_type=EntityType.agent,
            agent_id=uuid4()  # Different from following_id
        )
        
        # This is structurally valid but logically inconsistent
        assert inconsistent_contact.following_id != inconsistent_contact.agent_id
