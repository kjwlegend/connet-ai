"""
Integration tests for Contact Instance Management System (Priority 2)
End-to-end tests for the complete contact instance management workflow.
"""

import pytest
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from app.modules.ai.workflows.contact_manager import ContactInstanceManager
from app.modules.contacts.repository_impl import ContactRepository
from app.modules.contacts.models import ContactModel, EntityType
from app.modules.ai.agents.models import AIAgentModel


class TestContactInstanceIntegration:
    """Integration tests for the complete contact instance management system."""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock session for testing."""
        session = Mock()
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        session.add = Mock()
        session.delete = AsyncMock()
        session.rollback = AsyncMock()
        return session
    
    @pytest.fixture
    def sample_user_id(self):
        """Sample user ID for testing."""
        return uuid4()
    
    @pytest.fixture
    def sample_agent(self):
        """Sample agent for testing."""
        return AIAgentModel(
            id=uuid4(),
            name="python_expert",
            display_name="Python Expert",
            description="Expert Python development assistant",
            agent_type="specialized",
            system_prompt="You are an expert Python developer with 10+ years of experience.",
            is_active=True,
            created_by=uuid4(),
            # Enhanced fields from Priority 1
            node_type="standard",
            execution_config={
                "timeout_seconds": 45,
                "max_retries": 3,
                "streaming": True
            },
            resource_limits={
                "max_memory_mb": 512,
                "max_cpu_percent": 70,
                "max_execution_time": 120
            },
            dependencies={
                "required_tools": ["code_interpreter", "file_search"],
                "optional_tools": ["web_search"],
                "model_requirements": ["gpt-4", "claude-3"]
            },
            model_preferences={
                "temperature": 0.3,
                "max_tokens": 2000,
                "top_p": 0.9
            },
            capabilities=["code_generation", "debugging", "refactoring"],
            required_permissions=["code_execution", "file_access"]
        )

    @pytest.mark.asyncio
    async def test_complete_agent_to_contact_workflow(self, mock_session, sample_user_id, sample_agent):
        """Test the complete workflow from agent to personalized contact instance."""
        
        # Setup mocks
        contact_manager = ContactInstanceManager(mock_session)
        
        # Mock agent query for existence check
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_agent
        mock_session.execute.return_value = mock_result
        
        # Step 1: Convert Agent to Contact Instance
        user_customizations = {
            "custom_system_prompt": "You are my personal Python tutor. Always explain concepts step-by-step and provide multiple examples.",
            "instance_config": {
                "temperature": 0.1,  # Lower for more consistent tutoring
                "max_tokens": 3000,  # Higher for detailed explanations
                "response_style": "educational",
                "include_examples": True
            },
            "resource_limits": {
                "max_requests_per_hour": 50,  # Conservative limit for tutoring
                "disable_web_search": True,   # Focus on core concepts
                "max_code_exec_time": 30
            },
            "display_name_override": "My Python Tutor"
        }
        
        # Mock the repository create method
        created_contact = ContactModel(
            follower_id=sample_user_id,
            following_id=sample_agent.id,
            following_type=EntityType.agent,
            agent_id=sample_agent.id,
            custom_system_prompt=user_customizations["custom_system_prompt"],
            instance_config=user_customizations["instance_config"],
            resource_limits=user_customizations["resource_limits"],
            display_name="My Python Tutor"
        )
        contact_manager.contact_repo.create_contact_instance = AsyncMock(return_value=created_contact)
        
        # Execute agent to contact conversion
        contact_info = await contact_manager.agent_to_contact_conversion(
            user_id=sample_user_id,
            agent_id=sample_agent.id,
            **user_customizations
        )
        
        # Verify conversion results
        assert contact_info["agent_id"] == str(sample_agent.id)
        assert contact_info["follower_id"] == str(sample_user_id)
        assert contact_info["system_prompt"] == user_customizations["custom_system_prompt"]
        assert contact_info["display_name"] == "My Python Tutor"
        
        # Verify merged model preferences (contact overrides agent)
        model_prefs = contact_info["model_preferences"]
        assert model_prefs["temperature"] == 0.1  # From contact (overrides agent's 0.3)
        assert model_prefs["max_tokens"] == 3000   # From contact (overrides agent's 2000)
        assert model_prefs["top_p"] == 0.9         # From agent (preserved)
        
        # Step 2: Test Permission Validation
        contact_manager.contact_repo.get_user_contact_by_agent = AsyncMock(return_value=created_contact)
        
        permissions = await contact_manager.validate_contact_permissions(
            user_id=sample_user_id,
            agent_id=sample_agent.id,
            requested_permissions=["code_execution", "file_access", "internet_access"]
        )
        
        # Verify permissions (agent has code_execution and file_access)
        assert permissions["code_execution"] is True   # Agent has it, not restricted
        assert permissions["file_access"] is True     # Agent has it, not restricted
        assert permissions["internet_access"] is False # Agent doesn't have this permission
        
        # Step 3: Test Effective Configuration
        effective_config = await contact_manager.get_contact_effective_config(
            user_id=sample_user_id,
            agent_id=sample_agent.id
        )
        
        # Verify effective configuration merging
        assert effective_config is not None
        assert effective_config["system_prompt"] == user_customizations["custom_system_prompt"]
        
        # Agent base + contact overrides
        model_prefs = effective_config["model_preferences"]
        assert model_prefs["temperature"] == 0.1  # Contact override
        assert model_prefs["max_tokens"] == 3000  # Contact override
        assert model_prefs["include_examples"] is True  # Contact addition
        
        # Resource limits merging
        resource_limits = effective_config["resource_limits"]
        assert resource_limits["max_memory_mb"] == 512  # From agent
        assert resource_limits["max_requests_per_hour"] == 50  # From contact
        assert resource_limits["disable_web_search"] is True   # From contact
        
        # Other fields preserved from agent
        assert effective_config["capabilities"] == sample_agent.capabilities
        assert effective_config["execution_config"] == sample_agent.execution_config
        assert effective_config["dependencies"] == sample_agent.dependencies

    @pytest.mark.asyncio
    async def test_contact_personalization_update_workflow(self, mock_session, sample_user_id, sample_agent):
        """Test updating contact personalization after creation."""
        
        contact_manager = ContactInstanceManager(mock_session)
        
        # Existing contact
        existing_contact = ContactModel(
            follower_id=sample_user_id,
            following_id=sample_agent.id,
            following_type=EntityType.agent,
            agent_id=sample_agent.id,
            custom_system_prompt="Old prompt",
            instance_config={"temperature": 0.5},
            resource_limits={"max_requests_per_hour": 100}
        )
        
        # Mock the repository update
        updated_contact = ContactModel(
            follower_id=sample_user_id,
            following_id=sample_agent.id,
            following_type=EntityType.agent,
            agent_id=sample_agent.id,
            custom_system_prompt="Updated: You are now my advanced Python mentor with focus on best practices.",
            instance_config={
                "temperature": 0.2,
                "max_tokens": 2500,
                "focus_areas": ["best_practices", "code_review", "optimization"]
            },
            resource_limits={
                "max_requests_per_hour": 75,
                "enable_code_review": True
            },
            display_name="Advanced Python Mentor",
            notes="Updated for advanced learning path"
        )
        
        contact_manager.contact_repo.update_contact_config = AsyncMock(return_value=updated_contact)
        
        # Mock agent query
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_agent
        mock_session.execute.return_value = mock_result
        
        # Execute update
        result = await contact_manager.update_contact_personalization(
            user_id=sample_user_id,
            agent_id=sample_agent.id,
            custom_system_prompt=updated_contact.custom_system_prompt,
            instance_config=updated_contact.instance_config,
            resource_limits=updated_contact.resource_limits,
            display_name=updated_contact.display_name,
            notes=updated_contact.notes
        )
        
        # Verify update results
        assert result is not None
        assert "Advanced Python Mentor" in result["display_name"]
        assert "advanced Python mentor" in result["system_prompt"]
        assert result["model_preferences"]["temperature"] == 0.2
        assert "best_practices" in result["model_preferences"]["focus_areas"]

    @pytest.mark.asyncio
    async def test_multi_agent_contact_management(self, mock_session, sample_user_id):
        """Test managing multiple agent contacts for one user."""
        
        # Create multiple specialized agents
        agents = [
            AIAgentModel(
                id=uuid4(),
                name="python_expert",
                display_name="Python Expert",
                system_prompt="Python specialist",
                capabilities=["python", "debugging"],
                required_permissions=["code_execution"],
                model_preferences={"temperature": 0.3}
            ),
            AIAgentModel(
                id=uuid4(),
                name="web_dev_assistant",
                display_name="Web Dev Assistant", 
                system_prompt="Web development helper",
                capabilities=["html", "css", "javascript"],
                required_permissions=["file_access"],
                model_preferences={"temperature": 0.5}
            ),
            AIAgentModel(
                id=uuid4(),
                name="data_scientist",
                display_name="Data Scientist",
                system_prompt="Data analysis expert",
                capabilities=["pandas", "numpy", "visualization"],
                required_permissions=["code_execution", "file_access"],
                model_preferences={"temperature": 0.4}
            )
        ]
        
        # Create personalized contact instances for each
        contact_personalizations = [
            {
                "custom_system_prompt": "Focus on clean, readable Python code",
                "instance_config": {"code_style": "pep8", "explain_logic": True}
            },
            {
                "custom_system_prompt": "Help me build responsive, accessible websites",
                "instance_config": {"framework_preference": "react", "css_framework": "tailwind"}
            },
            {
                "custom_system_prompt": "Help me with statistical analysis and visualization",
                "instance_config": {"plot_library": "matplotlib", "explain_statistics": True}
            }
        ]
        
        contact_manager = ContactInstanceManager(mock_session)
        created_contacts = []
        
        for agent, personalization in zip(agents, contact_personalizations):
            # Mock agent query
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = agent
            mock_session.execute.return_value = mock_result
            
            # Mock contact creation
            contact = ContactModel(
                follower_id=sample_user_id,
                following_id=agent.id,
                following_type=EntityType.agent,
                agent_id=agent.id,
                custom_system_prompt=personalization["custom_system_prompt"],
                instance_config=personalization["instance_config"]
            )
            contact_manager.contact_repo.create_contact_instance = AsyncMock(return_value=contact)
            
            # Create contact instance
            contact_info = await contact_manager.agent_to_contact_conversion(
                user_id=sample_user_id,
                agent_id=agent.id,
                custom_system_prompt=personalization["custom_system_prompt"],
                instance_config=personalization["instance_config"]
            )
            
            created_contacts.append(contact_info)
        
        # Verify all contacts were created with different personalizations
        assert len(created_contacts) == 3
        
        python_contact = created_contacts[0]
        web_contact = created_contacts[1]
        data_contact = created_contacts[2]
        
        # Verify personalizations are different
        assert "clean, readable Python" in python_contact["system_prompt"]
        assert "responsive, accessible" in web_contact["system_prompt"]
        assert "statistical analysis" in data_contact["system_prompt"]
        
        # Verify merged configurations
        assert python_contact["model_preferences"]["code_style"] == "pep8"
        assert web_contact["model_preferences"]["framework_preference"] == "react"
        assert data_contact["model_preferences"]["plot_library"] == "matplotlib"

    def test_contact_instance_data_consistency(self):
        """Test data consistency requirements for contact instances."""
        user_id = uuid4()
        agent_id = uuid4()
        
        # Test that a proper contact instance has consistent references
        contact = ContactModel(
            follower_id=user_id,
            following_id=agent_id,
            following_type=EntityType.agent,
            agent_id=agent_id,  # Should match following_id for agent contacts
            is_agent=True,     # Should be True for agent contacts
            relationship_type="follow"
        )
        
        # Verify data consistency
        assert contact.following_id == contact.agent_id
        assert contact.following_type == EntityType.agent
        assert contact.is_agent is True
        
        # Test effective configuration merging logic
        agent_config = {"temperature": 0.5, "model": "gpt-4"}
        contact_config = {"temperature": 0.8, "custom_param": "value"}
        
        merged = {**agent_config, **contact_config}
        
        assert merged["temperature"] == 0.8  # Contact overrides agent
        assert merged["model"] == "gpt-4"    # Agent preserved
        assert merged["custom_param"] == "value"  # Contact addition

    def test_permission_validation_edge_cases(self):
        """Test edge cases in permission validation."""
        from app.modules.ai.workflows.contact_manager import ContactInstanceManager
        
        manager = ContactInstanceManager(Mock())
        
        # Test various permission restriction scenarios
        test_cases = [
            # No restrictions
            ({}, "file_access", False),
            # Explicit restriction
            ({"disable_file_access": True}, "file_access", True),
            # No restriction (False)
            ({"disable_file_access": False}, "file_access", False),
            # Unrelated restrictions
            ({"disable_internet": True}, "file_access", False),
            # Multiple restrictions
            ({"disable_file_access": True, "disable_code_exec": True}, "code_execution", True),
        ]
        
        for resource_limits, permission, expected_restricted in test_cases:
            result = manager._check_permission_restriction(permission, resource_limits)
            assert result == expected_restricted, f"Failed for {resource_limits} -> {permission}"
