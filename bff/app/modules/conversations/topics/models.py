"""SQLModel definitions for conversation topics."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, JSON
from sqlalchemy import Column as SAColumn
from sqlmodel import Field, SQLModel, Text


class ConversationTopicModel(SQLModel, table=True):
    """Represents hierarchical topics within a conversation."""

    __tablename__ = "conversation_topics"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    parent_topic_id: Optional[UUID] = Field(
        default=None, foreign_key="conversation_topics.id"
    )

    title: str = Field(max_length=200)
    description: Optional[str] = Field(
        default=None, sa_column=SAColumn(Text)
    )
    topic_type: str = Field(default="discussion", max_length=20)

    created_by: UUID = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    status: str = Field(default="active", max_length=20)
    tags: Optional[list[str]] = Field(default=None, sa_column=Column(JSON))
    metadata: Optional[dict] = Field(default=None, sa_column=Column(JSON))


__all__ = ["ConversationTopicModel"]
