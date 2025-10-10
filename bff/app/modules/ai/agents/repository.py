"""Agent repository protocol definition."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from app.modules.agents.models import AIAgentModel, AIAgentVersionModel


class AgentRepositoryProtocol(ABC):
    """Interface for agent repository implementations."""

    @abstractmethod
    async def create_agent(self, agent_data: Dict[str, Any], user_id: UUID) -> AIAgentModel: ...

    @abstractmethod
    async def update_agent(
        self, agent_id: UUID, update_data: Dict[str, Any], user_id: Optional[UUID] = None
    ) -> Optional[AIAgentModel]: ...

    @abstractmethod
    async def delete_agent(self, agent_id: UUID, user_id: Optional[UUID] = None) -> bool: ...

    @abstractmethod
    async def get_agent_by_id(
        self, agent_id: UUID, user_id: Optional[UUID] = None
    ) -> Optional[AIAgentModel]: ...

    @abstractmethod
    async def get_agent_by_name(
        self, name: str, user_id: Optional[UUID] = None
    ) -> Optional[AIAgentModel]: ...

    @abstractmethod
    async def get_agent_by_display_name(self, display_name: str) -> Optional[AIAgentModel]: ...

    @abstractmethod
    async def list_agents(
        self,
        user_id: Optional[UUID] = None,
        agent_type: Optional[str] = None,
        status: Optional[str] = None,
        category: Optional[str] = None,
        only_active: bool = True,
        only_public: bool = False,
        offset: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> Tuple[List[AIAgentModel], int]: ...

    @abstractmethod
    async def list_public_agents(
        self,
        agent_type: Optional[str] = None,
        status: Optional[str] = None,
        category: Optional[str] = None,
        offset: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> Tuple[List[AIAgentModel], int]: ...

    # Version operations
    @abstractmethod
    async def create_version(
        self,
        agent_id: UUID,
        version_data: Dict[str, Any],
        created_by: UUID,
    ) -> AIAgentVersionModel: ...

    @abstractmethod
    async def list_versions(self, agent_id: UUID) -> List[AIAgentVersionModel]: ...

    @abstractmethod
    async def get_version(
        self, agent_id: UUID, version_number: str
    ) -> Optional[AIAgentVersionModel]: ...


# Backwards compatibility alias
AgentRepository = AgentRepositoryProtocol

__all__ = ["AgentRepositoryProtocol", "AgentRepository"]
