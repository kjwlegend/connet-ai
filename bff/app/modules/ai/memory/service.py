"""Business logic for AI memory management."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

from fastapi import HTTPException, status

from app.modules.ai.memory.models import AIMemoryModel, AIConversationSummaryModel
from app.modules.ai.memory.repository import (
    AIMemoryRepositoryProtocol,
    AIMemorySummaryRepositoryProtocol,
)
from app.modules.ai.memory.schemas import (
    ConversationSummaryResponse,
    MemoryCategory,
    MemoryCreate,
    MemoryResponse,
    MemoryType,
)


class AIMemoryService:
    """Coordinates AI memory and summary workflows."""

    def __init__(
        self,
        memory_repository: AIMemoryRepositoryProtocol,
        summary_repository: AIMemorySummaryRepositoryProtocol,
    ) -> None:
        self.memory_repo = memory_repository
        self.summary_repo = summary_repository

    async def create_memory(
        self, memory_data: MemoryCreate, user_id: UUID
    ) -> MemoryResponse:
        memory = await self.memory_repo.create_memory(memory_data, user_id)
        return MemoryResponse.model_validate(memory)

    async def store_short_term_memory(
        self,
        conversation_id: UUID,
        content: str,
        user_id: UUID,
        agent_id: Optional[UUID] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MemoryResponse:
        payload = MemoryCreate(
            conversation_id=conversation_id,
            agent_id=agent_id,
            memory_type=MemoryType.SHORT_TERM,
            memory_category=MemoryCategory.CONVERSATION,
            content=content,
            metadata=metadata or {},
            importance_score=0.5,
            confidence_score=1.0,
        )
        return await self.create_memory(payload, user_id)

    async def get_conversation_context(
        self, conversation_id: UUID, limit: int = 10
    ) -> List[MemoryResponse]:
        memories = await self.memory_repo.get_memories_by_conversation(
            conversation_id=conversation_id,
            memory_type=MemoryType.SHORT_TERM,
            limit=limit,
        )
        return [MemoryResponse.model_validate(memory) for memory in memories]

    async def get_user_memories(
        self,
        user_id: UUID,
        memory_type: Optional[MemoryType] = None,
        memory_category: Optional[MemoryCategory] = None,
        limit: int = 20,
    ) -> List[MemoryResponse]:
        memories = await self.memory_repo.get_memories_by_user(
            user_id=user_id,
            memory_type=memory_type,
            memory_category=memory_category,
            limit=limit,
        )
        return [MemoryResponse.model_validate(memory) for memory in memories]

    async def search_memories(
        self,
        user_id: UUID,
        query: str,
        memory_type: Optional[MemoryType] = None,
        conversation_id: Optional[UUID] = None,
        limit: int = 10,
    ) -> List[MemoryResponse]:
        memories = await self.memory_repo.search_memories(
            user_id=user_id,
            query=query,
            memory_type=memory_type,
            conversation_id=conversation_id,
            limit=limit,
        )
        await asyncio.gather(
            *[self.memory_repo.update_memory_access(memory.id) for memory in memories]
        )
        return [MemoryResponse.model_validate(memory) for memory in memories]

    async def compress_short_to_medium_term(
        self, conversation_id: UUID
    ) -> Optional[ConversationSummaryResponse]:
        short_term_memories = await self.memory_repo.get_memories_by_conversation(
            conversation_id=conversation_id,
            memory_type=MemoryType.SHORT_TERM,
        )
        if not short_term_memories:
            return None

        summary_data = await self._create_conversation_summary(
            conversation_id, short_term_memories
        )
        summary = await self.summary_repo.create_summary(summary_data)

        await self._create_medium_term_memories(summary, short_term_memories[0].user_id)
        await self._cleanup_short_term_memories(conversation_id, keep_recent=5)

        return ConversationSummaryResponse.model_validate(summary)

    async def get_conversation_summaries(
        self, conversation_id: UUID, limit: Optional[int] = None
    ) -> List[ConversationSummaryResponse]:
        summaries = await self.summary_repo.get_conversation_summaries(
            conversation_id, limit
        )
        return [ConversationSummaryResponse.model_validate(summary) for summary in summaries]

    async def search_conversation_summaries(
        self, query: str, conversation_id: Optional[UUID] = None, limit: int = 10
    ) -> List[ConversationSummaryResponse]:
        summaries = await self.summary_repo.search_summaries(
            query=query, conversation_id=conversation_id, limit=limit
        )
        return [ConversationSummaryResponse.model_validate(summary) for summary in summaries]

    async def get_contextual_memories(
        self,
        user_id: UUID,
        conversation_id: UUID,
        current_context: str,
        max_memories: int = 10,
    ) -> List[MemoryResponse]:
        memories: List[AIMemoryModel] = []

        recent_memories = await self.memory_repo.get_memories_by_conversation(
            conversation_id=conversation_id,
            memory_type=MemoryType.SHORT_TERM,
            limit=5,
        )
        memories.extend(recent_memories)

        if current_context:
            medium_memories = await self.memory_repo.search_memories(
                user_id=user_id,
                query=current_context,
                memory_type=MemoryType.MEDIUM_TERM,
                limit=3,
            )
            memories.extend(medium_memories)

        long_term_memories = await self.memory_repo.get_memories_by_user(
            user_id=user_id,
            memory_type=MemoryType.LONG_TERM,
            limit=2,
        )
        memories.extend(long_term_memories)

        ordered = sorted(
            memories,
            key=lambda mem: (
                -(mem.importance_score or 0),
                -(mem.confidence_score or 0),
                mem.created_at,
            ),
            reverse=True,
        )
        top_memories = ordered[:max_memories]
        await asyncio.gather(
            *[self.memory_repo.update_memory_access(memory.id) for memory in top_memories]
        )
        return [MemoryResponse.model_validate(memory) for memory in top_memories]

    async def cleanup_expired_memories(self) -> int:
        return await self.memory_repo.delete_expired_memories()

    async def get_memory_statistics(self, user_id: UUID) -> Dict[str, Any]:
        return await self.memory_repo.get_memory_statistics(user_id)

    async def summarize_memories_batch(
        self, conversation_id: UUID, user_id: UUID
    ) -> ConversationSummaryResponse:
        short_term_memories = await self.memory_repo.get_memories_by_conversation(
            conversation_id=conversation_id,
            memory_type=MemoryType.SHORT_TERM,
        )
        if not short_term_memories:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No short-term memories available",
            )

        summary_data = await self._create_conversation_summary(
            conversation_id, short_term_memories
        )
        summary = await self.summary_repo.create_summary(summary_data)
        await self._create_medium_term_memories(summary, user_id)
        return ConversationSummaryResponse.model_validate(summary)

    async def _create_conversation_summary(
        self, conversation_id: UUID, memories: List[AIMemoryModel]
    ) -> Dict[str, Any]:
        key_points = [memory.content for memory in memories]
        topics = list(
            {tag for memory in memories for tag in memory.metadata.get("topics", [])}
        )
        sentiment_scores = [memory.metadata.get("sentiment_score", 0.0) for memory in memories]
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0

        summary_text = "\n".join(key_points[:10])

        return {
            "id": uuid4(),
            "conversation_id": conversation_id,
            "summary_text": summary_text,
            "key_points": key_points,
            "entities": [memory.metadata.get("entities", []) for memory in memories],
            "topics": topics,
            "sentiment": self._map_sentiment(avg_sentiment),
            "time_range_start": memories[0].created_at,
            "time_range_end": memories[-1].created_at,
            "message_count": len(memories),
            "participant_count": self._estimate_participants(memories),
            "summary_quality_score": 1.0,
            "completeness_score": 1.0,
            "is_processed": False,
        }

    async def _create_medium_term_memories(
        self, summary: AIConversationSummaryModel, user_id: UUID
    ) -> None:
        medium_memory = MemoryCreate(
            conversation_id=summary.conversation_id,
            agent_id=summary.agent_id,
            memory_type=MemoryType.MEDIUM_TERM,
            memory_category=MemoryCategory.CONVERSATION,
            content=summary.summary_text,
            metadata={
                "summary_id": str(summary.id),
                "key_points": summary.key_points,
                "topics": summary.topics,
            },
            importance_score=0.7,
            confidence_score=0.9,
        )
        await self.memory_repo.create_memory(medium_memory, user_id)

    async def _cleanup_short_term_memories(
        self, conversation_id: UUID, keep_recent: int
    ) -> None:
        memories = await self.memory_repo.get_memories_by_conversation(
            conversation_id=conversation_id,
            memory_type=MemoryType.SHORT_TERM,
        )
        for memory in memories[keep_recent:]:
            memory.expires_at = datetime.utcnow() - timedelta(seconds=1)
        await self.memory_repo.delete_expired_memories()

    def _estimate_participants(self, memories: List[AIMemoryModel]) -> int:
        participants = {memory.user_id for memory in memories if memory.user_id}
        participants.update(
            memory.metadata.get("mentioned_users", []) for memory in memories
        )
        return len(participants)

    def _map_sentiment(self, score: float) -> str:
        if score > 0.2:
            return "positive"
        if score < -0.2:
            return "negative"
        return "neutral"


__all__ = ["AIMemoryService"]
