"""
Contact API Schemas
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


# Base schemas
class ContactBase(BaseModel):
    display_name: Optional[str] = Field(None, max_length=100, description="Custom display name")
    notes: Optional[str] = Field(None, description="Personal notes about contact")
    tags: List[str] = Field(default=[], description="Custom tags for organization")


# Request schemas
class ContactCreate(ContactBase):
    """Schema for adding a contact."""
    following_id: UUID = Field(..., description="ID of user or agent to follow")
    following_type: str = Field(..., regex="^(user|agent)$", description="Type of contact")
    shared_via: Optional[str] = Field(None, description="How contact was shared")


class ContactUpdate(BaseModel):
    """Schema for updating contact information."""
    display_name: Optional[str] = Field(None, max_length=100, description="Custom display name")
    notes: Optional[str] = Field(None, description="Personal notes")
    tags: Optional[List[str]] = Field(None, description="Updated tags")
    notification_level: Optional[str] = Field(None, description="Notification level")
    is_muted: Optional[bool] = Field(None, description="Mute status")


# Response schemas
class ContactResponse(ContactBase):
    """Schema for contact response."""
    following_id: UUID
    following_type: str  # user or agent
    relationship_type: str = "follow"
    
    # Contact information
    name: str  # actual name from user/agent
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    
    # Status
    online_status: str = "unknown"  # online, offline, away, busy, unknown
    last_seen_at: Optional[datetime] = None
    is_favorite: bool = False
    is_muted: bool = False
    is_blocked: bool = False
    
    # Settings
    notification_level: str = "normal"  # none, important, normal, all
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    last_interaction_at: Optional[datetime] = None
    
    # Contact sharing
    qr_code_shared: bool = False
    shared_via: Optional[str] = None
    
    # AI agent specific fields (if applicable)
    agent_capabilities: Optional[List[str]] = None
    agent_specialties: Optional[List[str]] = None
    agent_availability: Optional[str] = None

    class Config:
        from_attributes = True


class ContactSearchResponse(BaseModel):
    """Schema for contact search results."""
    id: UUID
    type: str  # user or agent
    name: str
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    
    # Status
    online_status: str = "unknown"
    is_already_contact: bool = False
    
    # AI agent specific
    agent_capabilities: Optional[List[str]] = None
    agent_rating: Optional[float] = None
    
    # Match information
    match_score: Optional[float] = None
    match_reason: Optional[str] = None

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