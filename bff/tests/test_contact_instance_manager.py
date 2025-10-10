"""
Tests for Contact Instance Manager (Priority 2)
Tests the enhanced contact instance management functionality.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4
from datetime import datetime

from app.modules.ai.workflows.contact_manager import ContactInstanceManager
from app.modules.contacts.models import ContactModel, EntityType
from app.modules.agents.models import AIAgentModel


class TestContactInstanceManager:
    """Test ContactInstanceManager enhanced functionality."""
    
    @pytest.fixture
    def mock_session(self):
        """Create mock session for testing."""
        session = Mock()
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        session.flush = AsyncMock()
        session.add = Mock()
        session.delete = AsyncMock()
        session.rollback = AsyncMock()
        return session
    
    @pytest.fixture
    def contact_manager(self, mock_session):
        """Create ContactInstanceManager with mock session."""
        return ContactInstanceManager(mock_session)
    
    @pytest.fixture
    def sample_agent(self):
        """Create sample agent for testing."""
        return AIAgentModel(
            id=uuid4(),
            name="test_agent",
            display_name="Test Agent",
            description="A test agent",
            agent_type="custom",
            system_prompt="You are a helpful test agent",
            is_active=True,
            created_by=uuid4(),
            node_type="standard",
            execution_config={"timeout": 30},
            resource_limits={"max_memory": 256},
            dependencies={"required_tools": ["search"]}
        )
    
    @pytest.fixture
    def sample_contact(self, sample_agent):
        """Create sample contact for testing."""
        user_id = uuid4()
        return ContactModel(
            follower_id=user_id,
            following_id=sample_agent.id,
            following_type=EntityType.agent,
            agent_id=sample_agent.id,
            relationship_type="follow",
            is_agent=True,
            custom_system_prompt="Be very concise and technical",
            instance_config={"temperature": 0.7, "max_tokens": 1000},
            resource_limits={"max_requests_per_hour": 50}
        )

    @pytest.mark.asyncio
    async def test_agent_to_contact_conversion_success(
        self, 
        contact_manager, 
        mock_session,
        sample_agent
    ):
        """Test successful agent to contact conversion."""
        user_id = uuid4()
        
        # Mock agent query
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_agent
        mock_session.execute.return_value = mock_result
        
        # Mock contact repo methods
        contact_manager.contact_repo.get_user_contact_by_agent = AsyncMock(return_value=None)
        contact_manager.contact_repo.create_contact_instance = AsyncMock()
        
        # Create sample contact that would be returned
        created_contact = ContactModel(
            follower_id=user_id,
            following_id=sample_agent.id,
            following_type=EntityType.agent,
            agent_id=sample_agent.id,
            custom_system_prompt="Custom prompt",
            instance_config={"temperature": 0.8}
        )
        contact_manager.contact_repo.create_contact_instance.return_value = created_contact
        
        # Execute conversion
        result = await contact_manager.agent_to_contact_conversion(
            user_id=user_id,
            agent_id=sample_agent.id,
            custom_system_prompt="Custom prompt",
            instance_config={"temperature": 0.8}
        )
        
        # Verify repository was called correctly
        contact_manager.contact_repo.create_contact_instance.assert_called_once_with(
            user_id=user_id,
            agent_id=sample_agent.id,
            custom_system_prompt="Custom prompt",
            instance_config={"temperature": 0.8},
            resource_limits=None
        )
        
        # Verify result structure
        assert result["agent_id"] == str(sample_agent.id)
        assert result["follower_id"] == str(user_id)
        assert result["system_prompt"] == "Custom prompt"

    @pytest.mark.asyncio
    async def test_agent_to_contact_conversion_agent_not_found(
        self, 
        contact_manager, 
        mock_session
    ):
        """Test agent to contact conversion when agent doesn't exist."""
        user_id = uuid4()
        agent_id = uuid4()
        
        # Mock agent query returning None
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        # Expect ValueError
        with pytest.raises(ValueError, match="Agent .* not found or inactive"):
            await contact_manager.agent_to_contact_conversion(
                user_id=user_id,
                agent_id=agent_id
            )

    @pytest.mark.asyncio
    async def test_update_contact_personalization(
        self, 
        contact_manager, 
        sample_contact, 
        sample_agent
    ):
        """Test updating contact personalization."""
        user_id = sample_contact.follower_id
        agent_id = sample_agent.id
        
        # Mock repository update
        updated_contact = ContactModel(
            follower_id=user_id,
            following_id=agent_id,
            following_type=EntityType.agent,
            agent_id=agent_id,
            custom_system_prompt="Updated prompt",
            instance_config={"temperature": 0.9},
            display_name="Updated Display"
        )
        contact_manager.contact_repo.update_contact_config = AsyncMock(return_value=updated_contact)
        
        # Mock agent query
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_agent
        contact_manager.session.execute.return_value = mock_result
        
        # Execute update
        result = await contact_manager.update_contact_personalization(
            user_id=user_id,
            agent_id=agent_id,
            custom_system_prompt="Updated prompt",
            instance_config={"temperature": 0.9},
            display_name="Updated Display"
        )
        
        # Verify repository was called
        contact_manager.contact_repo.update_contact_config.assert_called_once()
        
        # Verify result
        assert result is not None
        assert result["system_prompt"] == "Updated prompt"

    @pytest.mark.asyncio
    async def test_validate_contact_permissions(
        self, 
        contact_manager, 
        sample_contact, 
        sample_agent
    ):
        """Test contact permission validation."""
        user_id = sample_contact.follower_id
        agent_id = sample_agent.id
        
        # Setup agent with permissions
        sample_agent.required_permissions = ["search", "file_access", "code_execution"]
        
        # Setup contact with restrictions
        sample_contact.resource_limits = {
            "disable_file_access": True,
            "disable_code_exec": False
        }
        
        # Mock repository and queries
        contact_manager.contact_repo.get_user_contact_by_agent = AsyncMock(return_value=sample_contact)
        
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_agent
        contact_manager.session.execute.return_value = mock_result
        
        # Test permission validation
        permissions = await contact_manager.validate_contact_permissions(
            user_id=user_id,
            agent_id=agent_id,
            requested_permissions=["search", "file_access", "code_execution", "invalid_permission"]
        )
        
        # Verify results
        assert permissions["search"] is True  # Agent has it, no restriction
        assert permissions["file_access"] is False  # Agent has it, but restricted by contact
        assert permissions["code_execution"] is True  # Agent has it, not restricted
        assert permissions["invalid_permission"] is False  # Agent doesn't have it

    @pytest.mark.asyncio
    async def test_get_contact_effective_config(
        self, 
        contact_manager, 
        sample_contact, 
        sample_agent
    ):
        """Test getting effective configuration for contact."""
        user_id = sample_contact.follower_id
        agent_id = sample_agent.id
        
        # Setup mock data
        sample_agent.model_preferences = {"temperature": 0.5, "max_tokens": 2000}
        sample_agent.resource_limits = {"max_memory": 512}
        
        sample_contact.instance_config = {"temperature": 0.8, "custom_param": "value"}
        sample_contact.resource_limits = {"max_requests_per_hour": 100}
        
        # Mock repository and queries
        contact_manager.contact_repo.get_user_contact_by_agent = AsyncMock(return_value=sample_contact)
        
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_agent
        contact_manager.session.execute.return_value = mock_result
        
        # Get effective config
        config = await contact_manager.get_contact_effective_config(
            user_id=user_id,
            agent_id=agent_id
        )
        
        # Verify merged configuration
        assert config is not None
        assert config["system_prompt"] == sample_contact.custom_system_prompt
        
        # Verify model preferences are merged (contact overrides agent)
        assert config["model_preferences"]["temperature"] == 0.8  # From contact
        assert config["model_preferences"]["max_tokens"] == 2000  # From agent
        assert config["model_preferences"]["custom_param"] == "value"  # From contact
        
        # Verify resource limits are merged
        assert config["resource_limits"]["max_memory"] == 512  # From agent
        assert config["resource_limits"]["max_requests_per_hour"] == 100  # From contact
        
        # Verify other fields
        assert config["execution_config"] == sample_agent.execution_config
        assert config["dependencies"] == sample_agent.dependencies

    @pytest.mark.asyncio
    async def test_get_contact_effective_config_contact_not_found(
        self, 
        contact_manager
    ):
        """Test getting effective config when contact doesn't exist."""
        user_id = uuid4()
        agent_id = uuid4()
        
        # Mock repository returning None
        contact_manager.contact_repo.get_user_contact_by_agent = AsyncMock(return_value=None)
        
        # Get config
        config = await contact_manager.get_contact_effective_config(
            user_id=user_id,
            agent_id=agent_id
        )
        
        # Should return None
        assert config is None

    def test_check_permission_restriction(self, contact_manager):
        """Test permission restriction logic."""
        # Test various restrictions
        restrictions = {
            "disable_file_access": True,
            "disable_internet": False,
            "disable_code_exec": True
        }
        
        assert contact_manager._check_permission_restriction("file_access", restrictions) is True
        assert contact_manager._check_permission_restriction("internet_access", restrictions) is False
        assert contact_manager._check_permission_restriction("code_execution", restrictions) is True
        assert contact_manager._check_permission_restriction("unknown_permission", restrictions) is False


class TestContactInstanceIntegration:
    """Integration tests for Contact Instance Management."""
    
    def test_contact_personalization_workflow(self):
        """Test the complete workflow of agent to contact conversion and personalization."""
        # This would be an integration test that:
        # 1. Creates an agent
        # 2. Converts it to a contact instance  
        # 3. Updates personalization settings
        # 4. Validates the effective configuration
        # 5. Tests permission validation
        
        # For now, this serves as documentation of the expected workflow
        assert True  # Placeholder
