"""
Conversation Participant Database Model

This module defines the SQLModel for conversation participants in the database.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Field, SQLModel
from sqlalchemy import Column, JSON


class ConversationParticipantModel(SQLModel, table=True):
    """Conversation participant database model."""
    
    __tablename__ = "conversation_participants"
    
    # Composite primary key
    conversation_id: UUID = Field(
        foreign_key="conversations.id",
        primary_key=True,
        description="Conversation ID"
    )
    participant_id: UUID = Field(
        primary_key=True,
        description="Participant ID (user or agent)"
    )
    participant_type: str = Field(
        primary_key=True,
        max_length=10,
        description="Participant type: user or agent"
    )
    
    # Participation information
    role: str = Field(
        default="member",
        max_length=20,
        description="Participant role: owner, admin, member"
    )
    joined_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="Join timestamp"
    )
    invited_by: Optional[UUID] = Field(
        default=None,
        foreign_key="users.id",
        description="User who invited this participant"
    )
    
    # Status
    is_active: bool = Field(
        default=True,
        description="Whether participant is active in conversation"
    )
    last_read_at: Optional[datetime] = Field(
        default=None,
        description="Last read timestamp"
    )
    last_read_message_id: Optional[UUID] = Field(
        default=None,
        description="ID of last read message"
    )
    
    # Settings
    notification_enabled: bool = Field(
        default=True,
        description="Whether notifications are enabled"
    )
    settings: Optional[dict] = Field(default=None,
        description="Participant-specific settings"
    ,

        sa_column=Column(JSON)

    )
    
    model_config = {

    
        "json_schema_extra": {
            "example": {
                "conversation_id": "12345678-1234-5678-9012-123456789012",
                "participant_id": "87654321-4321-8765-2109-876543210987",
                "participant_type": "user",
                "role": "admin",
                "is_active": True,
                "notification_enabled": True,
                "settings": {
                    "mute_until": None,
                    "auto_read": False,
                    "priority_notifications": True
                }

    
    }
            }
        }