"""
Conversation API Schemas
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


# Base schemas
class ConversationBase(BaseModel):
    title: str = Field(..., max_length=200, description="Conversation title")
    conversation_type: str = Field(default="chat", description="Conversation type: chat, task, project")
    is_group: bool = Field(default=False, description="Whether this is a group conversation")


# Request schemas
class ConversationCreate(ConversationBase):
    """Schema for creating a conversation."""
    participants: List[Dict[str, Any]] = Field(
        default=[],
        description="Initial participants: [{'id': UUID, 'type': 'user|agent'}]"
    )
    initial_message: Optional[str] = Field(None, description="Initial message content")
    settings: Optional[Dict[str, Any]] = Field(None, description="Conversation settings")


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation."""
    title: Optional[str] = Field(None, max_length=200, description="New conversation title")
    settings: Optional[Dict[str, Any]] = Field(None, description="Updated settings")
    summary: Optional[str] = Field(None, description="Conversation summary")


class ConversationPinRequest(BaseModel):
    """Schema for pinning/unpinning conversations."""
    is_pinned: bool = Field(..., description="Whether to pin or unpin")
    pin_order: int = Field(default=0, description="Order for pinned conversations")


# Response schemas
class ConversationParticipantResponse(BaseModel):
    """Schema for conversation participant information."""
    participant_id: UUID
    participant_type: str  # user or agent
    role: str = "member"  # owner, admin, member
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = True
    joined_at: datetime
    last_read_at: Optional[datetime] = None


class ConversationResponse(ConversationBase):
    """Schema for conversation response."""
    id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime] = None
    last_message_preview: Optional[str] = None
    
    # User-specific settings
    is_pinned: bool = False
    pin_order: int = 0
    is_archived: bool = False
    unread_count: int = 0
    notifications_enabled: bool = True
    custom_title: Optional[str] = None
    
    # Participants
    participants: List[ConversationParticipantResponse] = []
    participant_count: int = 0
    
    # Statistics
    message_count: int = 0
    export_count: int = 0
    last_exported_at: Optional[datetime] = None
    
    # Metadata
    summary: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    status: str = "active"

    class Config:
        from_attributes = True


class ConversationExportResponse(BaseModel):
    """Schema for conversation export response."""
    conversation_id: UUID
    export_format: str
    content: str
    filename: str
    download_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Message schemas
class MessageBase(BaseModel):
    content: str = Field(..., description="Message content")
    message_type: str = Field(default="text", description="Message type: text, image, file, system")


class MessageCreate(MessageBase):
    """Schema for creating a message."""
    conversation_id: UUID
    mentions: List[Dict[str, Any]] = Field(
        default=[],
        description="Mentioned users/agents: [{'id': UUID, 'type': 'user|agent', 'name': str}]"
    )
    attachments: List[str] = Field(default=[], description="Attachment file IDs")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Message metadata")


class MessageResponse(MessageBase):
    """Schema for message response."""
    id: UUID
    sender_id: UUID
    sender_type: str  # user or agent
    sender_name: str
    sender_avatar_url: Optional[str] = None
    conversation_id: UUID
    
    # Content
    content: str
    message_type: str
    edited: bool = False
    edited_at: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    # Attachments and media
    attachments: List[Dict[str, Any]] = []
    
    # AI-specific fields
    ai_model: Optional[str] = None
    ai_context: Optional[Dict[str, Any]] = None
    
    # Interaction
    mentions: List[Dict[str, Any]] = []
    reactions: List[Dict[str, Any]] = []
    
    # Status
    status: str = "sent"  # sent, delivered, read, failed
    is_system_message: bool = False
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True