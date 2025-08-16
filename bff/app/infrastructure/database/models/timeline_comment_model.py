"""
Timeline Comment Database Model

This module defines the SQLModel for timeline post comments in the database.
Supports nested comments and both user and agent participation.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlmodel import Column, Field, SQLModel, Text
from sqlalchemy import Column, JSON


class TimelineCommentModel(SQLModel, table=True):
    """Timeline comment database model."""
    
    __tablename__ = "timeline_comments"
    
    # Primary key and associations
    id: Optional[UUID] = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        description="Unique comment identifier"
    )
    post_id: UUID = Field(
        foreign_key="timeline_posts.id",
        index=True,
        description="Associated post ID"
    )
    parent_comment_id: Optional[UUID] = Field(
        default=None,
        foreign_key="timeline_comments.id",
        description="Parent comment ID for nested replies"
    )
    
    # Author information
    author_id: UUID = Field(
        index=True,
        description="Comment author ID (user or agent)"
    )
    author_type: str = Field(
        max_length=10,
        index=True,
        description="Author type: user or agent"
    )
    
    # Comment content
    content: str = Field(
        sa_column=Column(Text),
        description="Comment text content"
    )
    content_type: str = Field(
        default="text",
        max_length=20,
        description="Content type: text, image, sticker"
    )
    
    # Interaction statistics
    like_count: int = Field(
        default=0,
        description="Number of likes on this comment"
    )
    reply_count: int = Field(
        default=0,
        description="Number of replies to this comment"
    )
    
    # Mentions and tags
    mentioned_users: List[str] = Field(default=[],
        description="Mentioned user IDs in this comment"
    ,

        sa_column=Column(JSON)

    )
    mentioned_agents: List[str] = Field(default=[],
        description="Mentioned agent IDs in this comment"
    ,

        sa_column=Column(JSON)

    )
    
    # Attachments
    attachments: List[str] = Field(default=[],
        description="Attachment file IDs"
    ,

        sa_column=Column(JSON)

    )
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="Comment creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    
    # Status
    is_deleted: bool = Field(
        default=False,
        description="Whether comment has been deleted"
    )
    is_edited: bool = Field(
        default=False,
        description="Whether comment has been edited"
    )
    
    # Metadata
    comment_metadata: Optional[dict] = Field(default=None,
        description="Additional comment metadata"
    ,

        sa_column=Column(JSON)

    )
    
    model_config = {

    
        "json_schema_extra": {
            "example": {
                "content": "This is amazing! @code_assistant how did you implement the similarity search optimization?",
                "content_type": "text",
                "author_type": "user",
                "mentioned_agents": ["code_assistant"],
                "like_count": 3,
                "reply_count": 1,
                "is_deleted": False,
                "is_edited": False
            }

    
    }
        }