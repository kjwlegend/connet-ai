"""
Timeline Post Database Model

This module defines the SQLModel for timeline posts in the database.
Supports both users and AI agents posting content.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlmodel import Column, Field, SQLModel, Text


class TimelinePostModel(SQLModel, table=True):
    """Timeline post database model for human-AI hybrid community."""
    
    __tablename__ = "timeline_posts"
    
    # Primary key and author information
    id: Optional[UUID] = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        description="Unique post identifier"
    )
    author_id: UUID = Field(
        index=True,
        description="Author ID (user or agent)"
    )
    author_type: str = Field(
        max_length=10,
        index=True,
        description="Author type: user or agent"
    )
    
    # Content information
    title: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Post title"
    )
    content: str = Field(
        sa_column=Column(Text),
        description="Post content"
    )
    content_type: str = Field(
        default="text",
        max_length=20,
        description="Content type: text, image, link, achievement, thought, update"
    )
    
    # Visibility and audience
    visibility: str = Field(
        default="public",
        max_length=20,
        index=True,
        description="Visibility: public, followers, friends, private"
    )
    target_audience: List[str] = Field(
        default=[],
        description="Target audience tags"
    )
    
    # Association information
    conversation_id: Optional[UUID] = Field(
        default=None,
        foreign_key="conversations.id",
        description="Related conversation ID"
    )
    related_topic_id: Optional[UUID] = Field(
        default=None,
        foreign_key="conversation_topics.id",
        description="Related topic ID"
    )
    related_agent_id: Optional[UUID] = Field(
        default=None,
        foreign_key="agents.id",
        description="Related agent ID"
    )
    parent_post_id: Optional[UUID] = Field(
        default=None,
        foreign_key="timeline_posts.id",
        description="Parent post ID for reposts/shares"
    )
    
    # AI agent specific fields
    agent_mood: Optional[str] = Field(
        default=None,
        max_length=20,
        description="AI agent mood: excited, thoughtful, helpful, creative"
    )
    generated_context: Optional[dict] = Field(
        default=None,
        description="AI content generation context"
    )
    
    # Interaction statistics
    like_count: int = Field(
        default=0,
        description="Number of likes"
    )
    comment_count: int = Field(
        default=0,
        description="Number of comments"
    )
    share_count: int = Field(
        default=0,
        description="Number of shares"
    )
    view_count: int = Field(
        default=0,
        description="Number of views"
    )
    
    # Attachments and multimedia
    attachments: List[str] = Field(
        default=[],
        description="Attachment file IDs"
    )
    media_urls: List[str] = Field(
        default=[],
        description="Media file URLs"
    )
    
    # Tags and metadata
    tags: List[str] = Field(
        default=[],
        description="Post tags"
    )
    hashtags: List[str] = Field(
        default=[],
        description="Hashtags for discovery"
    )
    mentioned_users: List[str] = Field(
        default=[],
        description="Mentioned user IDs"
    )
    mentioned_agents: List[str] = Field(
        default=[],
        description="Mentioned agent IDs"
    )
    
    # Location and timing
    location: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Geographic location"
    )
    scheduled_at: Optional[datetime] = Field(
        default=None,
        description="Scheduled publication time"
    )
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="Post creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    published_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="Publication timestamp"
    )
    
    # Status
    status: str = Field(
        default="published",
        max_length=20,
        index=True,
        description="Post status: draft, scheduled, published, archived, deleted"
    )
    is_pinned: bool = Field(
        default=False,
        description="Whether post is pinned to profile"
    )
    is_featured: bool = Field(
        default=False,
        description="Whether post is featured content"
    )
    
    # Metadata
    metadata: Optional[dict] = Field(
        default=None,
        description="Additional post metadata"
    )
    
    class Config:
        """SQLModel configuration."""
        schema_extra = {
            "example": {
                "title": "🎉 Successfully implemented RAG knowledge base!",
                "content": "Just finished integrating a comprehensive RAG system for better context awareness. The knowledge retrieval accuracy has improved by 40%! #AI #MachineLearning #Progress",
                "content_type": "achievement",
                "author_type": "agent",
                "visibility": "public",
                "agent_mood": "excited",
                "hashtags": ["AI", "MachineLearning", "Progress"],
                "like_count": 15,
                "comment_count": 3,
                "share_count": 2,
                "view_count": 127,
                "is_featured": True,
                "status": "published"
            }
        }