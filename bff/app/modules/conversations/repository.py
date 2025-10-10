"""Repository protocol for conversation persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Iterable, List, Optional, Tuple
from uuid import UUID

from app.modules.conversations.models import (
    ConversationModel,
    ConversationParticipantModel,
    ConversationUserSettingModel,
)


class ConversationRepositoryProtocol(ABC):
    """Abstract persistence operations for conversations."""

    # Listing ----------------------------------------------------------------
    @abstractmethod
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
        """Return conversations a user participates in plus personal settings."""

    # Single aggregate -------------------------------------------------------
    @abstractmethod
    async def get(self, conversation_id: UUID) -> Optional[ConversationModel]:
        """Fetch a conversation by ID without membership checks."""

    @abstractmethod
    async def get_for_user(
        self, conversation_id: UUID, user_id: UUID
    ) -> Optional[Tuple[ConversationModel, Optional[ConversationUserSettingModel]]]:
        """Fetch a conversation ensuring the user is an active participant."""

    @abstractmethod
    async def create(self, conversation: ConversationModel) -> ConversationModel: ...

    @abstractmethod
    async def save(self, conversation: ConversationModel) -> ConversationModel: ...

    @abstractmethod
    async def delete(self, conversation: ConversationModel) -> None: ...

    # User settings ----------------------------------------------------------
    @abstractmethod
    async def get_user_settings(
        self, conversation_id: UUID, user_id: UUID
    ) -> Optional[ConversationUserSettingModel]:
        """Return per-user settings."""

    @abstractmethod
    async def upsert_user_settings(
        self, settings: ConversationUserSettingModel
    ) -> ConversationUserSettingModel:
        """Persist user settings, inserting if needed."""

    # Participants -----------------------------------------------------------
    @abstractmethod
    async def list_participants(
        self, conversation_id: UUID
    ) -> List[ConversationParticipantModel]:
        """Return active participants."""

    @abstractmethod
    async def add_participant(
        self, participant: ConversationParticipantModel
    ) -> ConversationParticipantModel: ...

    @abstractmethod
    async def remove_participant(
        self, conversation_id: UUID, participant_id: UUID, participant_type: str
    ) -> bool: ...

    @abstractmethod
    async def is_user_participant(
        self, conversation_id: UUID, user_id: UUID
    ) -> bool: ...

    # Stats ------------------------------------------------------------------
    @abstractmethod
    async def update_last_message(
        self,
        conversation_id: UUID,
        *,
        message_id: Optional[UUID],
        message_at: Optional[datetime],
    ) -> Optional[ConversationModel]:
        """Update last message metadata and return refreshed model."""

    @abstractmethod
    async def adjust_counts(
        self,
        conversation_id: UUID,
        *,
        message_delta: int = 0,
        participant_delta: int = 0,
    ) -> Optional[ConversationModel]:
        """Adjust aggregate counters atomically."""

    @abstractmethod
    async def increment_export(self, conversation_id: UUID) -> None: ...

    @abstractmethod
    async def mark_read(
        self,
        conversation_id: UUID,
        user_id: UUID,
        *,
        message_id: Optional[UUID],
        read_at: datetime,
    ) -> None: ...


ConversationRepository = ConversationRepositoryProtocol

__all__ = ["ConversationRepositoryProtocol", "ConversationRepository"]
