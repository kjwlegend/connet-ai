"""Repository protocol for conversation topics."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.modules.conversations.topics.models import ConversationTopicModel


class ConversationTopicRepositoryProtocol(ABC):
    """Abstract persistence contract for conversation topics."""

    @abstractmethod
    async def list_for_conversation(
        self, conversation_id: UUID
    ) -> List[ConversationTopicModel]: ...

    @abstractmethod
    async def get(self, topic_id: UUID) -> Optional[ConversationTopicModel]: ...

    @abstractmethod
    async def create(
        self, topic: ConversationTopicModel
    ) -> ConversationTopicModel: ...

    @abstractmethod
    async def delete(self, topic: ConversationTopicModel) -> None: ...


ConversationTopicRepository = ConversationTopicRepositoryProtocol

__all__ = [
    "ConversationTopicRepositoryProtocol",
    "ConversationTopicRepository",
]
