"""SQLModel definitions for conversation messages."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel, Text


class MessageModel(SQLModel, table=True):
    """Message persistence model."""

    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)

    sender_id: UUID = Field(index=True)
    sender_type: str = Field(max_length=10, index=True)

    content: str = Field(sa_column=Column(Text))
    message_type: str = Field(default="text", max_length=20)

    reply_to_id: Optional[UUID] = Field(default=None, foreign_key="messages.id")
    thread_id: Optional[UUID] = Field(default=None)

    agent_mentions: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    ai_context: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    tokens_used: Optional[int] = Field(default=None)

    is_edited: bool = Field(default=False)
    is_deleted: bool = Field(default=False)
    is_system: bool = Field(default=False)

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    edited_at: Optional[datetime] = Field(default=None)

    attachments: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    message_metadata: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    content_embedding: Optional[List[float]] = Field(default=None, sa_column=Column(JSON))


__all__ = ["MessageModel"]
