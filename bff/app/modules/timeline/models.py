"""Timeline database models for posts, comments, and likes."""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from sqlmodel import Column, Field, SQLModel, Text
from sqlalchemy import Column as SAColumn
from sqlalchemy import JSON


class TimelinePostModel(SQLModel, table=True):
    """Timeline post database model for human-AI hybrid community."""

    __tablename__ = "timeline_posts"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        description="Unique post identifier",
    )
    author_id: UUID = Field(index=True, description="Author ID (user or agent)")
    author_type: str = Field(
        max_length=10, index=True, description="Author type: user or agent"
    )

    title: Optional[str] = Field(default=None, max_length=200, description="Post title")
    content: str = Field(sa_column=SAColumn(Text), description="Post content")
    content_type: str = Field(
        default="text",
        max_length=20,
        description="Content type: text, image, link, achievement, thought, update",
    )

    visibility: str = Field(
        default="public",
        max_length=20,
        index=True,
        description="Visibility: public, followers, friends, private",
    )
    target_audience: List[str] = Field(
        default_factory=list,
        description="Target audience tags",
        sa_column=SAColumn(JSON),
    )
    category: str = Field(
        default="public_square",
        max_length=20,
        index=True,
        description="Post category: friends_circle, public_square, my_circle, favorites",
    )

    conversation_id: Optional[UUID] = Field(
        default=None, foreign_key="conversations.id", description="Related conversation"
    )
    related_topic_id: Optional[UUID] = Field(
        default=None,
        foreign_key="conversation_topics.id",
        description="Related topic ID",
    )
    related_agent_id: Optional[UUID] = Field(
        default=None, foreign_key="agents.id", description="Related agent ID"
    )
    parent_post_id: Optional[UUID] = Field(
        default=None, foreign_key="timeline_posts.id", description="Parent post ID"
    )

    agent_mood: Optional[str] = Field(
        default=None,
        max_length=20,
        description="AI agent mood: excited, thoughtful, helpful, creative",
    )
    generated_context: Optional[Dict[str, str]] = Field(
        default=None,
        description="AI content generation context",
        sa_column=SAColumn(JSON),
    )

    like_count: int = Field(default=0, description="Number of likes")
    comment_count: int = Field(default=0, description="Number of comments")
    share_count: int = Field(default=0, description="Number of shares")
    view_count: int = Field(default=0, description="Number of views")

    attachments: List[str] = Field(
        default_factory=list,
        description="Attachment file IDs",
        sa_column=SAColumn(JSON),
    )
    media_urls: List[str] = Field(
        default_factory=list,
        description="Media file URLs",
        sa_column=SAColumn(JSON),
    )

    tags: List[str] = Field(
        default_factory=list, description="Post tags", sa_column=SAColumn(JSON)
    )
    hashtags: List[str] = Field(
        default_factory=list,
        description="Hashtags for discovery",
        sa_column=SAColumn(JSON),
    )
    mentioned_users: List[str] = Field(
        default_factory=list,
        description="Mentioned user IDs",
        sa_column=SAColumn(JSON),
    )
    mentioned_agents: List[str] = Field(
        default_factory=list,
        description="Mentioned agent IDs",
        sa_column=SAColumn(JSON),
    )

    location: Optional[str] = Field(
        default=None, max_length=200, description="Geographic location"
    )
    scheduled_at: Optional[datetime] = Field(
        default=None, description="Scheduled publication time"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow, index=True, description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )
    published_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="Publication timestamp",
    )

    status: str = Field(
        default="published",
        max_length=20,
        index=True,
        description="Post status: draft, scheduled, published, archived, deleted",
    )
    is_pinned: bool = Field(default=False, description="Whether post is pinned")
    is_featured: bool = Field(default=False, description="Whether post is featured")

    post_metadata: Optional[Dict[str, str]] = Field(
        default=None, description="Additional post metadata", sa_column=SAColumn(JSON)
    )


class TimelineCommentModel(SQLModel, table=True):
    """Timeline comment database model."""

    __tablename__ = "timeline_comments"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    post_id: UUID = Field(foreign_key="timeline_posts.id", index=True)
    parent_comment_id: Optional[UUID] = Field(
        default=None, foreign_key="timeline_comments.id"
    )

    author_id: UUID = Field(index=True)
    author_type: str = Field(max_length=10, index=True)

    content: str = Field(sa_column=SAColumn(Text))
    content_type: str = Field(default="text", max_length=20)

    like_count: int = Field(default=0)
    reply_count: int = Field(default=0)

    mentioned_users: List[str] = Field(
        default_factory=list,
        sa_column=SAColumn(JSON),
        description="Mentioned user IDs",
    )
    mentioned_agents: List[str] = Field(
        default_factory=list,
        sa_column=SAColumn(JSON),
        description="Mentioned agent IDs",
    )
    attachments: List[str] = Field(
        default_factory=list,
        sa_column=SAColumn(JSON),
        description="Attachment file IDs",
    )

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    is_deleted: bool = Field(default=False)
    is_edited: bool = Field(default=False)

    comment_metadata: Optional[Dict[str, str]] = Field(
        default=None, sa_column=SAColumn(JSON)
    )


class TimelineLikeModel(SQLModel, table=True):
    """Timeline like/reaction database model."""

    __tablename__ = "timeline_likes"

    user_id: UUID = Field(
        foreign_key="users.id",
        primary_key=True,
        description="User who liked (only users can like)",
    )
    target_id: UUID = Field(
        primary_key=True, description="Target ID (post or comment being liked)"
    )
    target_type: str = Field(
        primary_key=True, max_length=10, description="Target type: post or comment"
    )

    reaction_type: str = Field(
        default="like",
        max_length=20,
        description="Reaction type: like, love, laugh, wow, sad, angry",
    )

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    like_metadata: Optional[Dict[str, str]] = Field(
        default=None, sa_column=SAColumn(JSON)
    )


__all__ = [
    "TimelinePostModel",
    "TimelineCommentModel",
    "TimelineLikeModel",
]
