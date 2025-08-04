"""
Message Database Model

This module defines the SQLModel for messages in the database.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlmodel import Column, Field, SQLModel, Text


class MessageModel(SQLModel, table=True):
    """Message database model."""
    
    __tablename__ = "messages"
    
    # Primary key and associations
    id: Optional[UUID] = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        description="Unique message identifier"
    )
    conversation_id: UUID = Field(
        foreign_key="conversations.id",
        index=True,
        description="Associated conversation ID"
    )
    
    # Sender information
    sender_id: UUID = Field(
        index=True,
        description="Sender ID (user or agent)"
    )
    sender_type: str = Field(
        max_length=10,
        index=True,
        description="Sender type: user or agent"
    )
    
    # Message content
    content: str = Field(
        sa_column=Column(Text),
        description="Message text content"
    )
    message_type: str = Field(
        default="text",
        max_length=20,
        description="Message type: text, image, file, system"
    )
    
    # Message metadata
    reply_to_id: Optional[UUID] = Field(
        default=None,
        foreign_key="messages.id",
        description="Reply to message ID"
    )
    thread_id: Optional[UUID] = Field(
        default=None,
        description="Message thread ID"
    )
    
    # AI related
    agent_mentions: List[str] = Field(
        default=[],
        description="Mentioned agent names"
    )
    ai_context: Optional[dict] = Field(
        default=None,
        description="AI processing context"
    )
    tokens_used: Optional[int] = Field(
        default=None,
        description="Number of tokens used for AI processing"
    )
    
    # Status and flags
    is_edited: bool = Field(
        default=False,
        description="Whether message has been edited"
    )
    is_deleted: bool = Field(
        default=False,
        description="Whether message has been deleted"
    )
    is_system: bool = Field(
        default=False,
        description="Whether this is a system message"
    )
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="Message creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    edited_at: Optional[datetime] = Field(
        default=None,
        description="Last edit timestamp"
    )
    
    # Attachments and multimedia
    attachments: List[str] = Field(
        default=[],
        description="Attachment file IDs"
    )
    
    # Metadata
    metadata: Optional[dict] = Field(
        default=None,
        description="Additional message metadata"
    )
    
    # Vector embedding (for semantic search)
    content_embedding: Optional[List[float]] = Field(
        default=None,
        description="Message content vector embedding"
    )
    
    class Config:
        """SQLModel configuration."""
        schema_extra = {
            "example": {
                "content": "Hey @code_assistant, can you help me debug this Python function?",
                "message_type": "text",
                "sender_type": "user",
                "agent_mentions": ["code_assistant"],
                "ai_context": {
                    "processing_status": "pending",
                    "mentioned_agents": ["code_assistant"]
                },
                "attachments": ["file_12345", "image_67890"],
                "is_edited": False,
                "is_deleted": False,
                "is_system": False
            }
        }