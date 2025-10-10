"""
Contact API Schemas
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


# Base schemas
class ContactBase(BaseModel):
    display_name: Optional[str] = Field(
        None, max_length=100, description="Custom display name"
    )
    notes: Optional[str] = Field(None, description="Personal notes about contact")
    tags: List[str] = Field(default=[], description="Custom tags for organization")


# Request schemas
class ContactCreate(ContactBase):
    """Schema for adding a contact."""

    following_id: UUID = Field(..., description="ID of user or agent to follow")
    following_type: str = Field(
        ..., pattern="^(user|agent)$", description="Type of contact"
    )
    relationship_type: Optional[str] = Field(
        "follow", description="Type of relationship"
    )
    is_favorite: Optional[bool] = Field(False, description="Mark as favorite")
    notification_level: Optional[str] = Field(
        "normal", description="Notification level"
    )
    shared_via: Optional[str] = Field(None, description="How contact was shared")


class ContactUpdate(BaseModel):
    """Schema for updating contact information."""

    display_name: Optional[str] = Field(
        None, max_length=100, description="Custom display name"
    )
    notes: Optional[str] = Field(None, description="Personal notes")
    tags: Optional[List[str]] = Field(None, description="Updated tags")
    notification_level: Optional[str] = Field(None, description="Notification level")
    is_muted: Optional[bool] = Field(None, description="Mute status")


# Response schemas
class ContactResponse(ContactBase):
    """Schema for contact response."""

    follower_id: UUID
    following_id: UUID
    following_type: str  # user or agent
    relationship_type: str = "follow"

    # Status
    online_status: str = "unknown"  # online, offline, away, busy, unknown
    last_seen_at: Optional[datetime] = None
    is_favorite: bool = False
    is_muted: bool = False
    is_blocked: bool = False
    is_agent: bool = False
    is_pinned: bool = False

    # Settings
    notification_level: str = "normal"  # none, important, normal, all

    # Metadata
    created_at: datetime
    updated_at: datetime
    last_interaction_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ContactSearchResponse(BaseModel):
    """Schema for contact search results."""

    id: UUID
    type: str  # user or agent
    name: str
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    is_followed: bool = False

    class Config:
        from_attributes = True


# Contact Knowledge Base Management
class ContactKnowledgeResponse(BaseModel):
    """Schema for contact knowledge base response."""

    id: UUID
    knowledge_base_id: UUID
    knowledge_base_name: Optional[str] = None
    alias: Optional[str] = None
    added_at: datetime

    class Config:
        from_attributes = True


# Contact Tool Management
class ContactToolResponse(BaseModel):
    """Schema for contact tool response."""

    id: UUID
    tool_id: UUID
    tool_name: Optional[str] = None
    enabled: bool = True
    tool_config: Optional[Dict[str, Any]] = None
    added_at: datetime

    class Config:
        from_attributes = True


class QRCodeResponse(BaseModel):
    """Schema for QR code generation response."""

    qr_code_data: str
    qr_code_image_url: str
    expires_at: datetime
    user_info: Dict[str, Any]

    class Config:
        from_attributes = True


class ConversationStartResponse(BaseModel):
    """Schema for conversation start response."""

    conversation_id: UUID
    is_new_conversation: bool
    message: str

    class Config:
        from_attributes = True
