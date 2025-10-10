"""SQLModel definitions for the conversations domain."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel
from sqlalchemy import Column, JSON


class ConversationModel(SQLModel, table=True):
    """Conversation metadata and aggregate state."""

    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    title: str = Field(max_length=200, description="Conversation title")
    conversation_type: str = Field(
        default="chat",
        max_length=20,
        description="Conversation type: chat | task | project",
        index=True,
    )
    status: str = Field(
        default="active",
        max_length=20,
        description="Conversation status",
        index=True,
    )
    is_group: bool = Field(default=False, description="Whether this is a group conversation")

    created_by: UUID = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    last_message_at: Optional[datetime] = Field(default=None, index=True)
    last_message_id: Optional[UUID] = Field(default=None)

    is_pinned: bool = Field(default=False, description="Global pin (admin feature)")
    summary: Optional[str] = Field(default=None, description="AI-generated summary")

    export_count: int = Field(default=0)
    last_exported_at: Optional[datetime] = Field(default=None)

    settings: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    conversation_metadata: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    message_count: int = Field(default=0)
    participant_count: int = Field(default=0)
    topic_count: int = Field(default=0)


class ConversationParticipantModel(SQLModel, table=True):
    """Per-participant membership state for a conversation."""

    __tablename__ = "conversation_participants"

    conversation_id: UUID = Field(foreign_key="conversations.id", primary_key=True)
    participant_id: UUID = Field(primary_key=True)
    participant_type: str = Field(primary_key=True, max_length=10)

    role: str = Field(default="member", max_length=20)
    joined_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    invited_by: Optional[UUID] = Field(default=None, foreign_key="users.id")

    is_active: bool = Field(default=True)
    last_read_at: Optional[datetime] = Field(default=None)
    last_read_message_id: Optional[UUID] = Field(default=None)

    notification_enabled: bool = Field(default=True)
    settings: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    workflow_priority: Optional[int] = Field(default=0)
    conversation_permissions: Optional[dict] = Field(default=None, sa_column=Column(JSON))


class ConversationUserSettingModel(SQLModel, table=True):
    """User-personal settings for a conversation."""

    __tablename__ = "conversation_user_settings"

    conversation_id: UUID = Field(foreign_key="conversations.id", primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", primary_key=True)

    is_pinned: bool = Field(default=False)
    pinned_at: Optional[datetime] = Field(default=None)
    pin_order: int = Field(default=0)

    notifications_enabled: bool = Field(default=True)
    notification_level: str = Field(default="all", max_length=20)
    muted_until: Optional[datetime] = Field(default=None)

    last_read_at: Optional[datetime] = Field(default=None)
    last_read_message_id: Optional[UUID] = Field(default=None)
    unread_count: int = Field(default=0)

    is_archived: bool = Field(default=False)
    archived_at: Optional[datetime] = Field(default=None)

    custom_title: Optional[str] = Field(default=None, max_length=200)
    settings: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ConversationMemoryModel(SQLModel, table=True):
    """Long-term memory snippets for conversations."""

    __tablename__ = "conversation_memories"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    owner_id: Optional[UUID] = Field(default=None, description="User or agent owner")
    owner_type: Optional[str] = Field(default=None, max_length=10)

    memory_type: str = Field(default="summary", max_length=30)
    content: dict = Field(sa_column=Column(JSON))

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    expires_at: Optional[datetime] = Field(default=None)
    metadata: Optional[dict] = Field(default=None, sa_column=Column(JSON))


__all__ = [
    "ConversationModel",
    "ConversationParticipantModel",
    "ConversationUserSettingModel",
    "ConversationMemoryModel",
]
