"""
Contact Database Model

This module defines the SQLModel for contacts/following relationships in the database.
Supports users following other users or AI agents.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlmodel import Column, Field, SQLModel, Text


class ContactModel(SQLModel, table=True):
    """Contact/following relationship database model."""
    
    __tablename__ = "contacts"
    
    # Composite primary key
    follower_id: UUID = Field(
        foreign_key="users.id",
        primary_key=True,
        description="Follower user ID (only users can follow)"
    )
    following_id: UUID = Field(
        primary_key=True,
        description="Following ID (user or agent being followed)"
    )
    following_type: str = Field(
        primary_key=True,
        max_length=10,
        description="Following type: user or agent"
    )
    
    # Relationship type
    relationship_type: str = Field(
        default="follow",
        max_length=20,
        description="Relationship type: follow, friend, blocked, muted"
    )
    
    # Relationship information
    display_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Custom display name for this contact"
    )
    notes: Optional[str] = Field(
        default=None,
        sa_column=Column(Text),
        description="Personal notes about this contact"
    )
    tags: List[str] = Field(
        default=[],
        description="Custom tags for organization"
    )
    
    # Status
    is_favorite: bool = Field(
        default=False,
        description="Whether this is a favorite contact"
    )
    is_muted: bool = Field(
        default=False,
        description="Whether notifications are muted"
    )
    is_blocked: bool = Field(
        default=False,
        description="Whether this contact is blocked"
    )
    
    # Contact status tracking (for users and agents)
    online_status: str = Field(
        default="unknown",
        max_length=20,
        description="Online status: online, offline, away, busy, unknown"
    )
    last_seen_at: Optional[datetime] = Field(
        default=None,
        description="Last seen timestamp"
    )
    
    # QR code feature for easy contact addition
    qr_code_shared: bool = Field(
        default=False,
        description="Whether contact was added via QR code"
    )
    shared_via: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Method contact was shared: qr_code, invite_link, search, etc."
    )
    
    # Notification settings
    notification_level: str = Field(
        default="normal",
        max_length=20,
        description="Notification level: none, important, normal, all"
    )
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="Relationship creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    last_interaction_at: Optional[datetime] = Field(
        default=None,
        description="Last interaction timestamp"
    )
    
    class Config:
        """SQLModel configuration."""
        schema_extra = {
            "example": {
                "follower_id": "12345678-1234-5678-9012-123456789012",
                "following_id": "87654321-4321-8765-2109-876543210987",
                "following_type": "agent",
                "relationship_type": "follow",
                "display_name": "My Code Assistant",
                "notes": "Great for debugging Python issues",
                "tags": ["coding", "helpful", "technical"],
                "is_favorite": True,
                "is_muted": False,
                "notification_level": "all"
            }
        }