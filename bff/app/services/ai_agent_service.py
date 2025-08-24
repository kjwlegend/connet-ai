"""AI Agent service for managing AI agents and their lifecycle."""

import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from app.infrastructure.database.repositories.agent_repository_impl import (
    AgentRepository,
    AgentVersionRepository,
)
from app.schemas.ai import (
    AIAgentCreate,
    AIAgentUpdate,
    AIAgentResponse,
    AIAgentListResponse,
    PaginationParams,
    PersonalityProfile,
    ModelPreferences,
)
from app.services.base import BaseService


class AIAgentService(BaseService):
    """AI Agent service for managing agents"""

    def __init__(self, session):
        super().__init__(session)
        self.agent_repo = AgentRepository(session)
        self.version_repo = AgentVersionRepository(session)

    async def create_agent(
        self, agent_data: AIAgentCreate, user_id: UUID
    ) -> AIAgentResponse:
        """Create a new AI agent"""

        # Check if agent name already exists for user
        existing = await self.agent_repo.get_agent_by_name(agent_data.name, user_id)
        if existing:
            raise ValueError(f"Agent with name '{agent_data.name}' already exists")

        # Create agent
        agent = await self.agent_repo.create_agent(agent_data.model_dump(), user_id)

        # Create initial version
        await self._create_initial_version(agent, user_id)

        return AIAgentResponse.model_validate(agent)

    async def get_agent(
        self, agent_id: UUID, user_id: Optional[UUID] = None
    ) -> Optional[AIAgentResponse]:
        """Get agent by ID"""

        agent = await self.agent_repo.get_agent_by_id(agent_id, user_id)
        if not agent:
            return None

        return AIAgentResponse.model_validate(agent)

    async def update_agent(
        self, agent_id: UUID, agent_data: AIAgentUpdate, user_id: UUID
    ) -> Optional[AIAgentResponse]:
        """Update an existing agent"""

        # Get current agent
        current_agent = await self.agent_repo.get_agent_by_id(agent_id, user_id)
        if not current_agent:
            return None

        # Update agent
        updated_agent = await self.agent_repo.update_agent(
            agent_id, agent_data.model_dump(exclude_unset=True), user_id
        )
        if not updated_agent:
            return None

        # Create new version if significant changes
        if self._requires_new_version(agent_data):
            await self._create_version_from_update(
                updated_agent, current_agent, user_id
            )

        return AIAgentResponse.model_validate(updated_agent)

    async def list_agents(
        self,
        user_id: Optional[UUID] = None,
        agent_type: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        pagination: Optional[PaginationParams] = None,
    ) -> AIAgentListResponse:
        """List agents with filtering (deprecated - use get_public_agents or get_my_agents)"""

        # Convert pagination to offset/limit
        offset = 0
        limit = 100
        if pagination:
            offset = (pagination.page - 1) * pagination.size
            limit = pagination.size

        agents, total = await self.agent_repo.list_agents(
            user_id=user_id,
            agent_type=agent_type,
            status=status,
            search=search,
            offset=offset,
            limit=limit,
        )

        agent_responses = [AIAgentResponse.model_validate(agent) for agent in agents]

        if pagination:
            return AIAgentListResponse(
                agents=agent_responses,
                total=total,
                page=pagination.page,
                size=pagination.size,
            )

        return AIAgentListResponse(
            agents=agent_responses, total=total, page=1, size=len(agent_responses)
        )

    async def get_public_agents(
        self,
        agent_type: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        pagination: Optional[PaginationParams] = None,
    ) -> AIAgentListResponse:
        """Get all public agents"""

        # Convert pagination to offset/limit
        offset = 0
        limit = 100
        if pagination:
            offset = (pagination.page - 1) * pagination.size
            limit = pagination.size

        agents, total = await self.agent_repo.list_public_agents(
            agent_type=agent_type,
            status=status,
            search=search,
            offset=offset,
            limit=limit,
        )

        agent_responses = [AIAgentResponse.model_validate(agent) for agent in agents]

        if pagination:
            return AIAgentListResponse(
                agents=agent_responses,
                total=total,
                page=pagination.page,
                size=pagination.size,
            )

        return AIAgentListResponse(
            agents=agent_responses, total=total, page=1, size=len(agent_responses)
        )

    async def get_my_agents(
        self,
        user_id: UUID,
        agent_type: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        pagination: Optional[PaginationParams] = None,
    ) -> AIAgentListResponse:
        """Get agents created by the user"""

        # Convert pagination to offset/limit
        offset = 0
        limit = 100
        if pagination:
            offset = (pagination.page - 1) * pagination.size
            limit = pagination.size

        agents, total = await self.agent_repo.list_agents(
            user_id=user_id,
            agent_type=agent_type,
            status=status,
            search=search,
            offset=offset,
            limit=limit,
        )

        agent_responses = [AIAgentResponse.model_validate(agent) for agent in agents]

        if pagination:
            return AIAgentListResponse(
                agents=agent_responses,
                total=total,
                page=pagination.page,
                size=pagination.size,
            )

        return AIAgentListResponse(
            agents=agent_responses, total=total, page=1, size=len(agent_responses)
        )

    async def delete_agent(self, agent_id: UUID, user_id: UUID) -> bool:
        """Delete an agent"""

        return await self.agent_repo.delete_agent(agent_id, user_id)

    async def deploy_agent(self, agent_id: UUID, user_id: UUID) -> bool:
        """Deploy agent (placeholder for actual deployment logic)"""

        agent = await self.agent_repo.get_agent_by_id(agent_id, user_id)
        if not agent:
            return False

        # TODO: Implement actual deployment logic
        # For now, just mark as deployed
        await self.agent_repo.update_agent(
            agent_id, {"deployment_status": "deployed"}, user_id
        )

        return True

    async def get_agent_versions(
        self, agent_id: UUID, user_id: UUID
    ) -> List[Dict[str, Any]]:
        """Get version history for an agent"""

        # Verify ownership
        agent = await self.agent_repo.get_agent_by_id(agent_id, user_id)
        if not agent:
            return []

        versions = await self.version_repo.get_versions(agent_id)
        return [
            {
                "id": version.id,
                "version_number": version.version_number,
                "previous_version": version.previous_version,
                "changes": version.changes,
                "change_description": version.change_description,
                "created_at": version.created_at,
                "is_current": version.is_current,
            }
            for version in versions
        ]

    async def rollback_to_version(
        self, agent_id: UUID, version_number: str, user_id: UUID
    ) -> Optional[AIAgentResponse]:
        """Rollback agent to a specific version"""

        # Verify ownership
        agent = await self.agent_repo.get_agent_by_id(agent_id, user_id)
        if not agent:
            return None

        # Get target version
        target_version = await self.version_repo.get_version_by_number(
            agent_id, version_number
        )
        if not target_version:
            return None

        # Restore agent from snapshot
        agent_snapshot = target_version.agent_snapshot

        # Create update data from snapshot
        update_data = AIAgentUpdate(
            display_name=agent_snapshot.get("display_name"),
            description=agent_snapshot.get("description"),
            introduction=agent_snapshot.get("introduction"),
            avatar_url=agent_snapshot.get("avatar_url"),
            avatar_style=agent_snapshot.get("avatar_style"),
            conversation_style=agent_snapshot.get("conversation_style"),
            system_prompt=agent_snapshot.get("system_prompt"),
            personality_config=PersonalityProfile.model_validate(
                agent_snapshot.get("personality_config", {})
            ),
            model_preferences=ModelPreferences.model_validate(
                agent_snapshot.get("model_preferences", {})
            ),
            capabilities=agent_snapshot.get("capabilities", []),
            required_permissions=agent_snapshot.get("required_permissions", []),
            tags=agent_snapshot.get("tags", []),
            category=agent_snapshot.get("category"),
            is_public=agent_snapshot.get("is_public"),
            is_active=agent_snapshot.get("is_active"),
        )

        # Update agent
        updated_agent = await self.agent_repo.update_agent(
            agent_id, update_data.model_dump(exclude_unset=True), user_id
        )
        if not updated_agent:
            return None

        # Create rollback version
        await self._create_rollback_version(updated_agent, target_version, user_id)

        return AIAgentResponse.model_validate(updated_agent)

    async def update_usage_stats(
        self, agent_id: UUID, execution_time: float, success: bool
    ):
        """Update agent usage statistics"""

        await self.agent_repo.update_usage_stats(agent_id, execution_time, success)

    async def _create_initial_version(self, agent, user_id: UUID):
        """Create initial version for new agent"""

        version_data = {
            "version_number": "1.0.0",
            "previous_version": None,
            "agent_snapshot": self._create_agent_snapshot(agent),
            "changes": {
                "type": "initial_creation",
                "description": "Initial agent creation",
            },
            "change_description": "Initial version created",
        }

        await self.version_repo.create_version(agent.id, version_data, user_id)

    async def _create_version_from_update(
        self, updated_agent, original_agent, user_id: UUID
    ):
        """Create version from agent update"""

        current_version = await self.version_repo.get_current_version(updated_agent.id)
        new_version = self._increment_version(
            current_version.version_number if current_version else "1.0.0"
        )

        # Calculate changes
        changes = self._calculate_changes(original_agent, updated_agent)

        version_data = {
            "version_number": new_version,
            "previous_version": (
                current_version.version_number if current_version else None
            ),
            "agent_snapshot": self._create_agent_snapshot(updated_agent),
            "changes": changes,
            "change_description": self._generate_change_description(changes),
        }

        await self.version_repo.create_version(updated_agent.id, version_data, user_id)

    async def _create_rollback_version(self, agent, target_version, user_id: UUID):
        """Create version for rollback operation"""

        current_version = await self.version_repo.get_current_version(agent.id)
        new_version = self._increment_version(
            current_version.version_number if current_version else "1.0.0"
        )

        version_data = {
            "version_number": new_version,
            "previous_version": (
                current_version.version_number if current_version else None
            ),
            "agent_snapshot": self._create_agent_snapshot(agent),
            "changes": {
                "type": "rollback",
                "target_version": target_version.version_number,
                "description": f"Rolled back to version {target_version.version_number}",
            },
            "change_description": f"Rollback to version {target_version.version_number}",
        }

        await self.version_repo.create_version(agent.id, version_data, user_id)

    def _requires_new_version(self, agent_data: AIAgentUpdate) -> bool:
        """Check if update requires new version"""

        significant_fields = [
            "system_prompt",
            "personality_config",
            "model_preferences",
            "capabilities",
            "required_permissions",
        ]

        return any(
            getattr(agent_data, field, None) is not None for field in significant_fields
        )

    def _create_agent_snapshot(self, agent) -> Dict[str, Any]:
        """Create snapshot of agent state"""

        return {
            "name": agent.name,
            "display_name": agent.display_name,
            "description": agent.description,
            "introduction": agent.introduction,
            "agent_type": agent.agent_type,
            "version": agent.version,
            "avatar_url": agent.avatar_url,
            "avatar_style": agent.avatar_style,
            "conversation_style": agent.conversation_style,
            "system_prompt": agent.system_prompt,
            "personality_config": agent.personality_config,
            "model_preferences": agent.model_preferences,
            "capabilities": agent.capabilities,
            "required_permissions": agent.required_permissions,
            "tags": agent.tags,
            "category": agent.category,
            "is_public": agent.is_public,
            "is_active": agent.is_active,
        }

    def _increment_version(self, current_version: str) -> str:
        """Increment version number"""

        try:
            major, minor, patch = map(int, current_version.split("."))
            return f"{major}.{minor}.{patch + 1}"
        except ValueError:
            return "1.0.1"

    def _calculate_changes(self, original, updated) -> Dict[str, Any]:
        """Calculate changes between agent versions"""

        changes = {"type": "update", "fields_changed": []}

        fields_to_check = [
            "display_name",
            "description",
            "introduction",
            "avatar_url",
            "avatar_style",
            "conversation_style",
            "system_prompt",
            "personality_config",
            "model_preferences",
            "capabilities",
            "required_permissions",
            "tags",
            "category",
        ]

        for field in fields_to_check:
            original_value = getattr(original, field, None)
            updated_value = getattr(updated, field, None)

            if original_value != updated_value:
                changes["fields_changed"].append(
                    {
                        "field": field,
                        "old_value": original_value,
                        "new_value": updated_value,
                    }
                )

        return changes

    def _generate_change_description(self, changes: Dict[str, Any]) -> str:
        """Generate human-readable change description"""

        if changes["type"] == "update":
            changed_fields = [change["field"] for change in changes["fields_changed"]]
            if len(changed_fields) == 1:
                return f"Updated {changed_fields[0]}"
            elif len(changed_fields) <= 3:
                return f"Updated {', '.join(changed_fields)}"
            else:
                return f"Updated {len(changed_fields)} fields"

        return changes.get("description", "Agent updated")
