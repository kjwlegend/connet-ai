"""SQLAlchemy implementation of the conversation repository."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.conversations.models import (
    ConversationModel,
    ConversationParticipantModel,
    ConversationUserSettingModel,
)
from app.modules.conversations.repository import ConversationRepositoryProtocol


class ConversationRepository(ConversationRepositoryProtocol):
    """Conversation persistence powered by SQLModel/SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_for_user(
        self,
        *,
        user_id: UUID,
        include_archived: bool,
        pinned_only: bool,
        search: Optional[str],
        skip: int,
        limit: int,
    ) -> List[Tuple[ConversationModel, Optional[ConversationUserSettingModel]]]:
        stmt = (
            select(ConversationModel, ConversationUserSettingModel)
            .join(
                ConversationParticipantModel,
                and_(
                    ConversationParticipantModel.conversation_id
                    == ConversationModel.id,
                    ConversationParticipantModel.participant_id == user_id,
                    ConversationParticipantModel.participant_type == "user",
                    ConversationParticipantModel.is_active.is_(True),
                ),
            )
            .outerjoin(
                ConversationUserSettingModel,
                and_(
                    ConversationUserSettingModel.conversation_id
                    == ConversationModel.id,
                    ConversationUserSettingModel.user_id == user_id,
                ),
            )
        )

        if not include_archived:
            stmt = stmt.where(
                or_(
                    ConversationUserSettingModel.is_archived.is_(False),
                    ConversationUserSettingModel.is_archived.is_(None),
                )
            )

        if pinned_only:
            stmt = stmt.where(ConversationUserSettingModel.is_pinned.is_(True))

        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    ConversationModel.title.ilike(pattern),
                    ConversationUserSettingModel.custom_title.ilike(pattern),
                )
            )

        stmt = stmt.order_by(
            ConversationUserSettingModel.is_pinned.desc().nullslast(),
            ConversationUserSettingModel.pin_order.asc().nullslast(),
            ConversationModel.last_message_at.desc().nullslast(),
            ConversationModel.updated_at.desc(),
        )

        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.all()

    async def get(self, conversation_id: UUID) -> Optional[ConversationModel]:
        return await self.session.get(ConversationModel, conversation_id)

    async def get_for_user(
        self, conversation_id: UUID, user_id: UUID
    ) -> Optional[Tuple[ConversationModel, Optional[ConversationUserSettingModel]]]:
        stmt = (
            select(ConversationModel, ConversationUserSettingModel)
            .join(
                ConversationParticipantModel,
                and_(
                    ConversationParticipantModel.conversation_id == conversation_id,
                    ConversationParticipantModel.participant_id == user_id,
                    ConversationParticipantModel.participant_type == "user",
                    ConversationParticipantModel.is_active.is_(True),
                ),
            )
            .outerjoin(
                ConversationUserSettingModel,
                and_(
                    ConversationUserSettingModel.conversation_id
                    == ConversationModel.id,
                    ConversationUserSettingModel.user_id == user_id,
                ),
            )
            .where(ConversationModel.id == conversation_id)
        )
        result = await self.session.execute(stmt)
        return result.first()

    async def create(self, conversation: ConversationModel) -> ConversationModel:
        self.session.add(conversation)
        await self.session.flush()
        await self.session.refresh(conversation)
        return conversation

    async def save(self, conversation: ConversationModel) -> ConversationModel:
        await self.session.flush()
        await self.session.refresh(conversation)
        return conversation

    async def delete(self, conversation: ConversationModel) -> None:
        await self.session.delete(conversation)
        await self.session.flush()

    async def get_user_settings(
        self, conversation_id: UUID, user_id: UUID
    ) -> Optional[ConversationUserSettingModel]:
        stmt = select(ConversationUserSettingModel).where(
            and_(
                ConversationUserSettingModel.conversation_id == conversation_id,
                ConversationUserSettingModel.user_id == user_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert_user_settings(
        self, settings: ConversationUserSettingModel
    ) -> ConversationUserSettingModel:
        existing = await self.get_user_settings(settings.conversation_id, settings.user_id)
        if existing:
            for field, value in settings.model_dump(exclude={"conversation_id", "user_id"}).items():
                setattr(existing, field, value)
            existing.updated_at = datetime.utcnow()
            await self.session.flush()
            await self.session.refresh(existing)
            return existing

        self.session.add(settings)
        await self.session.flush()
        await self.session.refresh(settings)
        return settings

    async def list_participants(
        self, conversation_id: UUID
    ) -> List[ConversationParticipantModel]:
        stmt = select(ConversationParticipantModel).where(
            ConversationParticipantModel.conversation_id == conversation_id
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_participant(
        self, participant: ConversationParticipantModel
    ) -> ConversationParticipantModel:
        self.session.add(participant)
        await self.session.flush()
        await self.session.refresh(participant)
        return participant

    async def remove_participant(
        self, conversation_id: UUID, participant_id: UUID, participant_type: str
    ) -> bool:
        stmt = select(ConversationParticipantModel).where(
            and_(
                ConversationParticipantModel.conversation_id == conversation_id,
                ConversationParticipantModel.participant_id == participant_id,
                ConversationParticipantModel.participant_type == participant_type,
            )
        )
        result = await self.session.execute(stmt)
        participant = result.scalar_one_or_none()
        if not participant:
            return False
        await self.session.delete(participant)
        await self.session.flush()
        return True

    async def is_user_participant(
        self, conversation_id: UUID, user_id: UUID
    ) -> bool:
        stmt = select(func.count()).select_from(ConversationParticipantModel).where(
            and_(
                ConversationParticipantModel.conversation_id == conversation_id,
                ConversationParticipantModel.participant_id == user_id,
                ConversationParticipantModel.participant_type == "user",
                ConversationParticipantModel.is_active.is_(True),
            )
        )
        result = await self.session.execute(stmt)
        return bool(result.scalar_one())

    async def update_last_message(
        self,
        conversation_id: UUID,
        *,
        message_id: Optional[UUID],
        message_at: Optional[datetime],
    ) -> Optional[ConversationModel]:
        conversation = await self.get(conversation_id)
        if not conversation:
            return None
        conversation.last_message_id = message_id
        conversation.last_message_at = message_at
        conversation.updated_at = datetime.utcnow()
        await self.session.flush()
        await self.session.refresh(conversation)
        return conversation

    async def adjust_counts(
        self,
        conversation_id: UUID,
        *,
        message_delta: int = 0,
        participant_delta: int = 0,
    ) -> Optional[ConversationModel]:
        conversation = await self.get(conversation_id)
        if not conversation:
            return None
        conversation.message_count = max(0, conversation.message_count + message_delta)
        conversation.participant_count = max(
            0, conversation.participant_count + participant_delta
        )
        conversation.updated_at = datetime.utcnow()
        await self.session.flush()
        await self.session.refresh(conversation)
        return conversation

    async def increment_export(self, conversation_id: UUID) -> None:
        conversation = await self.get(conversation_id)
        if not conversation:
            return
        conversation.export_count += 1
        conversation.last_exported_at = datetime.utcnow()
        await self.session.flush()

    async def mark_read(
        self,
        conversation_id: UUID,
        user_id: UUID,
        *,
        message_id: Optional[UUID],
        read_at: datetime,
    ) -> None:
        settings = await self.get_user_settings(conversation_id, user_id)
        if not settings:
            settings = ConversationUserSettingModel(
                conversation_id=conversation_id,
                user_id=user_id,
            )
            self.session.add(settings)
            await self.session.flush()
            await self.session.refresh(settings)
        settings.last_read_message_id = message_id
        settings.last_read_at = read_at
        settings.unread_count = 0
        settings.updated_at = datetime.utcnow()
        await self.session.flush()


__all__ = ["ConversationRepository"]
