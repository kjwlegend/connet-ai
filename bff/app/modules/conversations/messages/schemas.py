"""Pydantic schemas for conversation messages."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    content: str = Field(..., description="Message body")
    message_type: str = Field(default="text")


class MessageCreate(MessageBase):
    conversation_id: UUID
    reply_to_id: Optional[UUID] = None
    thread_id: Optional[UUID] = None
    mentions: List[str] = Field(default_factory=list)
    attachments: List[str] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None


class MessageResponse(MessageBase):
    id: UUID
    sender_id: UUID
    sender_type: str
    sender_name: Optional[str] = None
    sender_avatar_url: Optional[str] = None
    conversation_id: UUID

    edited: bool = False
    edited_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    attachments: List[str] = Field(default_factory=list)
    mentions: List[str] = Field(default_factory=list)
    reactions: List[Dict[str, Any]] = Field(default_factory=list)

    ai_model: Optional[str] = None
    ai_context: Optional[Dict[str, Any]] = None

    status: str = "sent"
    is_system_message: bool = False
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


__all__ = ["MessageCreate", "MessageResponse"]
