"""
Conversation User Settings Database Model

This module defines the SQLModel for user-specific conversation settings
such as pinning conversations, notification preferences, etc.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Field, SQLModel
from sqlalchemy import Column, JSON


class ConversationUserSettingModel(SQLModel, table=True):
    """User-specific conversation settings database model."""
    
    __tablename__ = "conversation_user_settings"
    
    # Composite primary key
    conversation_id: UUID = Field(
        foreign_key="conversations.id",
        primary_key=True,
        description="Conversation ID"
    )
    user_id: UUID = Field(
        foreign_key="users.id", 
        primary_key=True,
        description="User ID"
    )
    
    # Pinning functionality
    is_pinned: bool = Field(
        default=False,
        description="Whether user has pinned this conversation"
    )
    pinned_at: Optional[datetime] = Field(
        default=None,
        description="When conversation was pinned"
    )
    pin_order: int = Field(
        default=0,
        description="Order of pinned conversations (for sorting)"
    )
    
    # Notification settings
    notifications_enabled: bool = Field(
        default=True,
        description="Whether notifications are enabled for this conversation"
    )
    notification_level: str = Field(
        default="all",
        max_length=20,
        description="Notification level: all, mentions, none"
    )
    muted_until: Optional[datetime] = Field(
        default=None,
        description="Mute conversation until this timestamp"
    )
    
    # Reading status
    last_read_at: Optional[datetime] = Field(
        default=None,
        description="Last read timestamp for this user"
    )
    last_read_message_id: Optional[UUID] = Field(
        default=None,
        description="ID of last read message for this user"
    )
    unread_count: int = Field(
        default=0,
        description="Number of unread messages"
    )
    
    # Archive status
    is_archived: bool = Field(
        default=False,
        description="Whether user has archived this conversation"
    )
    archived_at: Optional[datetime] = Field(
        default=None,
        description="When conversation was archived by user"
    )
    
    # Custom settings
    custom_title: Optional[str] = Field(
        default=None,
        max_length=200,
        description="User's custom title for the conversation"
    )
    settings: Optional[dict] = Field(default=None,
        description="Additional user-specific settings"
    ,

        sa_column=Column(JSON)

    )
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When settings were created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    
    model_config = {

    
        "json_schema_extra": {
            "example": {
                "conversation_id": "12345678-1234-5678-9012-123456789012",
                "user_id": "87654321-4321-8765-2109-876543210987",
                "is_pinned": True,
                "pin_order": 1,
                "notifications_enabled": True,
                "notification_level": "mentions",
                "unread_count": 3,
                "custom_title": "My Project Discussion",
                "settings": {
                    "show_typing_indicators": True,
                    "auto_mark_read": False,
                    "priority_keywords": ["urgent", "deadline"]
                }

    
    }
            }
        }