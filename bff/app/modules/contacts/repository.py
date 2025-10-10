"""Contact repository protocol definition."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from app.modules.contacts.models import ContactModel, ContactKnowledgeLink, ContactToolLink


class ContactRepositoryProtocol(ABC):
    """Interface that contact repository implementations must satisfy."""

    @abstractmethod
    async def get_by_follower_id(self, follower_id: UUID) -> List[ContactModel]: ...

    @abstractmethod
    async def get_by_following_id(self, following_id: UUID) -> Optional[ContactModel]: ...

    @abstractmethod
    async def create_contact(self, contact: ContactModel) -> ContactModel: ...

    @abstractmethod
    async def update_contact(self, contact: ContactModel) -> Optional[ContactModel]: ...

    @abstractmethod
    async def delete_contact(self, follower_id: UUID, following_id: UUID, following_type: str) -> bool: ...

    @abstractmethod
    async def exists(self, follower_id: UUID, following_id: UUID, following_type: str) -> bool: ...

    @abstractmethod
    async def search_contacts(self, query: str, offset: int = 0, limit: int = 20) -> Tuple[List[ContactModel], int]: ...

    # Knowledge base operations
    @abstractmethod
    async def add_knowledge_to_contact(
        self,
        follower_id: UUID,
        following_id: UUID,
        following_type: str,
        knowledge_base_id: UUID,
        alias: Optional[str] = None,
    ) -> ContactKnowledgeLink: ...

    @abstractmethod
    async def remove_knowledge_from_contact(
        self,
        follower_id: UUID,
        following_id: UUID,
        following_type: str,
        knowledge_base_id: UUID,
    ) -> bool: ...

    @abstractmethod
    async def get_contact_knowledge_bases(
        self,
        follower_id: UUID,
        following_id: UUID,
        following_type: str,
    ) -> List[ContactKnowledgeLink]: ...

    # Tool operations
    @abstractmethod
    async def add_tool_to_contact(
        self,
        follower_id: UUID,
        following_id: UUID,
        following_type: str,
        tool_id: UUID,
        enabled: bool = True,
        tool_config: Optional[Dict[str, Any]] = None,
    ) -> ContactToolLink: ...

    @abstractmethod
    async def remove_tool_from_contact(
        self,
        follower_id: UUID,
        following_id: UUID,
        following_type: str,
        tool_id: UUID,
    ) -> bool: ...

    @abstractmethod
    async def get_contact_tools(
        self,
        follower_id: UUID,
        following_id: UUID,
        following_type: str,
    ) -> List[ContactToolLink]: ...

    @abstractmethod
    async def update_tool_config(
        self,
        follower_id: UUID,
        following_id: UUID,
        following_type: str,
        tool_id: UUID,
        enabled: Optional[bool] = None,
        tool_config: Optional[Dict[str, Any]] = None,
    ) -> Optional[ContactToolLink]: ...


# Backwards compatibility alias
ContactRepository = ContactRepositoryProtocol

__all__ = ["ContactRepositoryProtocol", "ContactRepository"]
