"""Repository protocols for AI memory storage."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.modules.ai.memory.models import AIMemoryModel, AIConversationSummaryModel
from app.schemas.ai import MemoryCategory, MemoryCreate, MemoryType


class AIMemoryRepositoryProtocol(ABC):
    """Abstract persistence interface for memories."""

    @abstractmethod
    async def create_memory(
        self, memory_data: MemoryCreate, user_id: UUID
    ) -> AIMemoryModel:
        ...

    @abstractmethod
    async def get_memories_by_conversation(
        self,
        conversation_id: UUID,
        memory_type: Optional[MemoryType] = None,
        limit: Optional[int] = None,
    ) -> List[AIMemoryModel]:
        ...

    @abstractmethod
    async def get_memories_by_user(
        self,
        user_id: UUID,
        memory_type: Optional[MemoryType] = None,
        memory_category: Optional[MemoryCategory] = None,
        limit: Optional[int] = None,
    ) -> List[AIMemoryModel]:
        ...

    @abstractmethod
    async def search_memories(
        self,
        user_id: UUID,
        query: str,
        memory_type: Optional[MemoryType] = None,
        conversation_id: Optional[UUID] = None,
        limit: int = 10,
    ) -> List[AIMemoryModel]:
        ...

    @abstractmethod
    async def update_memory_access(self, memory_id: UUID) -> None:
        ...

    @abstractmethod
    async def get_expired_memories(self, batch_size: int = 100) -> List[AIMemoryModel]:
        ...

    @abstractmethod
    async def delete_expired_memories(self) -> int:
        ...

    @abstractmethod
    async def get_memory_statistics(self, user_id: UUID) -> Dict[str, Any]:
        ...


class AIMemorySummaryRepositoryProtocol(ABC):
    """Abstract persistence interface for conversation summaries."""

    @abstractmethod
    async def create_summary(
        self, summary_data: Dict[str, Any]
    ) -> AIConversationSummaryModel:
        ...

    @abstractmethod
    async def get_conversation_summaries(
        self, conversation_id: UUID, limit: Optional[int] = None
    ) -> List[AIConversationSummaryModel]:
        ...

    @abstractmethod
    async def search_summaries(
        self,
        query: str,
        conversation_id: Optional[UUID] = None,
        limit: int = 10,
    ) -> List[AIConversationSummaryModel]:
        ...

    @abstractmethod
    async def update_summary_quality(
        self, summary_id: UUID, quality_score: float, completeness_score: float
    ) -> None:
        ...


__all__ = [
    "AIMemoryRepositoryProtocol",
    "AIMemorySummaryRepositoryProtocol",
]
