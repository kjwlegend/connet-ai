"""Repository protocol for messages."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.modules.conversations.messages.models import MessageModel


class MessageRepositoryProtocol(ABC):
    """Abstract persistence operations for messages."""

    @abstractmethod
    async def list_for_conversation(
        self,
        conversation_id: UUID,
        *,
        skip: int,
        limit: int,
        before_id: Optional[UUID],
        after_id: Optional[UUID],
    ) -> List[MessageModel]:
        """Return messages within a conversation honoring pagination cursors."""

    @abstractmethod
    async def list_all(self, conversation_id: UUID) -> List[MessageModel]: ...

    @abstractmethod
    async def get(self, message_id: UUID) -> Optional[MessageModel]: ...

    @abstractmethod
    async def create(self, message: MessageModel) -> MessageModel: ...


MessageRepository = MessageRepositoryProtocol

__all__ = ["MessageRepositoryProtocol", "MessageRepository"]
