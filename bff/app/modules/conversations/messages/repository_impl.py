"""SQLAlchemy implementation of the message repository."""

from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.conversations.messages.models import MessageModel
from app.modules.conversations.messages.repository import MessageRepositoryProtocol


class MessageRepository(MessageRepositoryProtocol):
    """SQLModel powered message repository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_for_conversation(
        self,
        conversation_id: UUID,
        *,
        skip: int,
        limit: int,
        before_id: Optional[UUID],
        after_id: Optional[UUID],
    ) -> List[MessageModel]:
        stmt = select(MessageModel).where(MessageModel.conversation_id == conversation_id)

        if before_id:
            sub_stmt = select(MessageModel.created_at).where(
                MessageModel.id == before_id
            )
            result = await self.session.execute(sub_stmt)
            before_ts = result.scalar_one_or_none()
            if before_ts:
                stmt = stmt.where(MessageModel.created_at < before_ts)

        if after_id:
            sub_stmt = select(MessageModel.created_at).where(MessageModel.id == after_id)
            result = await self.session.execute(sub_stmt)
            after_ts = result.scalar_one_or_none()
            if after_ts:
                stmt = stmt.where(MessageModel.created_at > after_ts)

        stmt = stmt.order_by(desc(MessageModel.created_at)).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        messages = list(result.scalars().all())
        # ensure chronological order ascending for client readability
        messages.sort(key=lambda m: m.created_at)
        return messages

    async def list_all(self, conversation_id: UUID) -> List[MessageModel]:
        stmt = (
            select(MessageModel)
            .where(MessageModel.conversation_id == conversation_id)
            .order_by(asc(MessageModel.created_at))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get(self, message_id: UUID) -> Optional[MessageModel]:
        return await self.session.get(MessageModel, message_id)

    async def create(self, message: MessageModel) -> MessageModel:
        self.session.add(message)
        await self.session.flush()
        await self.session.refresh(message)
        return message


__all__ = ["MessageRepository"]
