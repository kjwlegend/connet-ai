"""Business logic for conversation topics."""

from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import HTTPException, status

from app.modules.conversations.repository import ConversationRepositoryProtocol
from app.modules.conversations.topics.models import ConversationTopicModel
from app.modules.conversations.topics.repository import (
    ConversationTopicRepositoryProtocol,
)


class ConversationTopicService:
    """Coordinates topic CRUD inside conversations."""

    def __init__(
        self,
        topic_repository: ConversationTopicRepositoryProtocol,
        conversation_repository: ConversationRepositoryProtocol,
    ) -> None:
        self.topic_repository = topic_repository
        self.conversation_repository = conversation_repository

    async def list_topics(self, conversation_id: UUID, user_id: UUID) -> List[ConversationTopicModel]:
        await self._assert_membership(conversation_id, user_id)
        return await self.topic_repository.list_for_conversation(conversation_id)

    async def create_topic(
        self,
        conversation_id: UUID,
        user_id: UUID,
        title: str,
        description: str | None = None,
        parent_topic_id: UUID | None = None,
        topic_type: str = "discussion",
    ) -> ConversationTopicModel:
        await self._assert_membership(conversation_id, user_id)
        topic = ConversationTopicModel(
            conversation_id=conversation_id,
            parent_topic_id=parent_topic_id,
            title=title,
            description=description,
            topic_type=topic_type,
            created_by=user_id,
        )
        return await self.topic_repository.create(topic)

    async def delete_topic(self, topic_id: UUID, user_id: UUID) -> None:
        topic = await self.topic_repository.get(topic_id)
        if not topic:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")
        await self._assert_membership(topic.conversation_id, user_id)
        await self.topic_repository.delete(topic)

    async def _assert_membership(self, conversation_id: UUID, user_id: UUID) -> None:
        if not await self.conversation_repository.is_user_participant(conversation_id, user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


__all__ = ["ConversationTopicService"]
