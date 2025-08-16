"""
Conversation Topic Database Model

This module defines the SQLModel for conversation topics/subtopics in the database.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlmodel import Column, Field, SQLModel, Text
from sqlalchemy import Column, JSON


class ConversationTopicModel(SQLModel, table=True):
    """Conversation topic database model."""
    
    __tablename__ = "conversation_topics"
    
    # Primary key and associations
    id: Optional[UUID] = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        description="Unique topic identifier"
    )
    conversation_id: UUID = Field(
        foreign_key="conversations.id",
        index=True,
        description="Associated conversation ID"
    )
    parent_topic_id: Optional[UUID] = Field(
        default=None,
        foreign_key="conversation_topics.id",
        description="Parent topic ID for nested topics"
    )
    
    # Topic information
    title: str = Field(
        max_length=200,
        description="Topic title"
    )
    description: Optional[str] = Field(
        default=None,
        sa_column=Column(Text),
        description="Topic description"
    )
    topic_type: str = Field(
        default="discussion",
        max_length=20,
        description="Topic type: discussion, task, brainstorm, decision"
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
        description="Topic creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    
    # Topic status
    status: str = Field(
        default="active",
        max_length=20,
        index=True,
        description="Topic status: active, resolved, archived"
    )
    priority: str = Field(
        default="normal",
        max_length=20,
        description="Priority level: low, normal, high, urgent"
    )
    
    # Time management
    start_message_id: Optional[UUID] = Field(
        default=None,
        foreign_key="messages.id",
        description="Starting message ID for this topic"
    )
    due_date: Optional[datetime] = Field(
        default=None,
        description="Topic due date"
    )
    resolved_at: Optional[datetime] = Field(
        default=None,
        description="Topic resolution timestamp"
    )
    resolved_by: Optional[UUID] = Field(
        default=None,
        foreign_key="users.id",
        description="User who resolved the topic"
    )
    
    # Statistics
    message_count: int = Field(
        default=0,
        description="Number of messages related to this topic"
    )
    participant_count: int = Field(
        default=0,
        description="Number of participants in this topic"
    )
    
    # Tags and classification
    tags: List[str] = Field(default=[],
        description="Topic tags for organization"
    ,

        sa_column=Column(JSON)

    )
    
    # Metadata
    topic_metadata: Optional[dict] = Field(default=None,
        description="Additional topic metadata",
        sa_column=Column(JSON)
    )
    
    # AI-generated summary
    ai_summary: Optional[str] = Field(
        default=None,
        sa_column=Column(Text),
        description="AI-generated topic summary"
    )
    summary_updated_at: Optional[datetime] = Field(
        default=None,
        description="Last summary update timestamp"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Backend Architecture Decision",
                "description": "Discussing the choice between FastAPI vs Django for the backend implementation",
                "topic_type": "decision",
                "status": "active",
                "priority": "high",
                "due_date": "2025-01-15T00:00:00Z",
                "tags": ["architecture", "backend", "decision"],
                "message_count": 12,
                "participant_count": 4,
                "ai_summary": "The team is evaluating FastAPI vs Django for the backend. Key considerations include performance, development speed, and team expertise."
            }
        }
    }