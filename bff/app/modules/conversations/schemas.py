"""Pydantic schemas for conversations."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ConversationBase(BaseModel):
    title: str = Field(..., max_length=200)
    conversation_type: str = Field(default="chat")
    is_group: bool = Field(default=False)


class ConversationCreate(ConversationBase):
    participants: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Initial participants [{'id': UUID, 'type': 'user|agent'}]",
    )
    initial_message: Optional[str] = Field(default=None)
    settings: Optional[Dict[str, Any]] = None


class ConversationUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=200)
    settings: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None


class ConversationPinRequest(BaseModel):
    is_pinned: bool
    pin_order: int = Field(default=0)


class ConversationParticipantResponse(BaseModel):
    participant_id: UUID
    participant_type: str
    role: str = "member"
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = True
    joined_at: datetime
    last_read_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConversationResponse(ConversationBase):
    id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime] = None
    last_message_preview: Optional[str] = None

    is_pinned: bool = False
    pin_order: int = 0
    is_archived: bool = False
    unread_count: int = 0
    notifications_enabled: bool = True
    custom_title: Optional[str] = None

    participants: List[ConversationParticipantResponse] = Field(default_factory=list)
    participant_count: int = 0
    message_count: int = 0
    export_count: int = 0
    last_exported_at: Optional[datetime] = None

    summary: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    status: str = "active"

    class Config:
        from_attributes = True


class ConversationExportResponse(BaseModel):
    conversation_id: UUID
    export_format: str
    content: str
    filename: str
    created_at: datetime

    class Config:
        from_attributes = True


__all__ = [
    "ConversationBase",
    "ConversationCreate",
    "ConversationUpdate",
    "ConversationPinRequest",
    "ConversationParticipantResponse",
    "ConversationResponse",
    "ConversationExportResponse",
]
