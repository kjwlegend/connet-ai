"""
Conversation Database Model

This module defines the SQLModel for conversations in the database.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class ConversationModel(SQLModel, table=True):
    """Conversation database model."""
    
    __tablename__ = "conversations"
    
    # Primary key and basic information
    id: Optional[UUID] = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        description="Unique conversation identifier"
    )
    title: str = Field(
        max_length=200,
        description="Conversation title"
    )
    conversation_type: str = Field(
        default="chat",
        max_length=20,
        index=True,
        description="Conversation type: chat, task, project"
    )
    
    # Conversation status
    status: str = Field(
        default="active",
        max_length=20,
        index=True,
        description="Conversation status: active, archived, deleted"
    )
    is_group: bool = Field(
        default=False,
        description="Whether this is a group conversation"
    )
    
    # Creation information
    created_by: UUID = Field(
        foreign_key="users.id",
        index=True,
        description="Creator user ID"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="Conversation creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    
    # Last activity
    last_message_at: Optional[datetime] = Field(
        default=None,
        index=True,
        description="Last message timestamp"
    )
    last_message_id: Optional[UUID] = Field(
        default=None,
        description="ID of the last message"
    )
    
    # Pin status (user-specific pinning handled via many-to-many relationship)
    is_pinned: bool = Field(
        default=False,
        description="Whether conversation is globally pinned (admin feature)"
    )
    
    # Conversation summary/memory for AI context
    summary: Optional[str] = Field(
        default=None,
        description="AI-generated conversation summary for context"
    )
    
    # Export metadata
    export_count: int = Field(
        default=0,
        description="Number of times conversation was exported"
    )
    last_exported_at: Optional[datetime] = Field(
        default=None,
        description="Last export timestamp"
    )
    
    # Settings
    settings: Optional[dict] = Field(
        default=None,
        description="Conversation settings and preferences"
    )
    metadata: Optional[dict] = Field(
        default=None,
        description="Additional conversation metadata"
    )
    
    # Statistics
    message_count: int = Field(
        default=0,
        description="Total number of messages"
    )
    participant_count: int = Field(
        default=0,
        description="Number of participants"
    )
    topic_count: int = Field(
        default=0,
        description="Number of topics/subtopics"
    )
    
    class Config:
        """SQLModel configuration."""
        schema_extra = {
            "example": {
                "title": "Project Planning Discussion",
                "conversation_type": "project",
                "is_group": True,
                "status": "active",
                "settings": {
                    "auto_archive_days": 30,
                    "allow_agent_mentions": True,
                    "notification_level": "important"
                },
                "message_count": 87,
                "participant_count": 5,
                "topic_count": 3
            }
        }