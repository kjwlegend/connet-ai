"""SQLAlchemy implementation for conversation topics."""

from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.conversations.topics.models import ConversationTopicModel
from app.modules.conversations.topics.repository import (
    ConversationTopicRepositoryProtocol,
)


class ConversationTopicRepository(ConversationTopicRepositoryProtocol):
    """Persistence operations for conversation topics."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_for_conversation(
        self, conversation_id: UUID
    ) -> List[ConversationTopicModel]:
        stmt = select(ConversationTopicModel).where(
            ConversationTopicModel.conversation_id == conversation_id
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get(self, topic_id: UUID) -> Optional[ConversationTopicModel]:
        return await self.session.get(ConversationTopicModel, topic_id)

    async def create(
        self, topic: ConversationTopicModel
    ) -> ConversationTopicModel:
        self.session.add(topic)
        await self.session.flush()
        await self.session.refresh(topic)
        return topic

    async def delete(self, topic: ConversationTopicModel) -> None:
        await self.session.delete(topic)
        await self.session.flush()


__all__ = ["ConversationTopicRepository"]
