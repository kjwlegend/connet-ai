"""Pydantic schemas for the timeline domain."""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TimelinePostBase(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    content: str = Field(..., min_length=1)
    content_type: str = Field("text")
    visibility: str = Field("public")
    category: str = Field("public_square")
    tags: List[str] = Field(default_factory=list)
    hashtags: List[str] = Field(default_factory=list)
    attachments: List[str] = Field(default_factory=list)
    media_urls: List[str] = Field(default_factory=list)
    target_audience: List[str] = Field(default_factory=list)


class TimelinePostCreate(TimelinePostBase):
    pass


class TimelinePostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    content_type: Optional[str] = None
    visibility: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    hashtags: Optional[List[str]] = None
    attachments: Optional[List[str]] = None
    media_urls: Optional[List[str]] = None


class TimelinePostResponse(TimelinePostBase):
    id: UUID
    author_id: UUID
    author_type: str
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    view_count: int = 0
    status: str = "published"
    is_pinned: bool = False
    is_featured: bool = False
    parent_post_id: Optional[UUID] = None
    related_agent_id: Optional[UUID] = None
    related_topic_id: Optional[UUID] = None
    conversation_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    published_at: datetime

    class Config:
        from_attributes = True


class PostCommentCreate(BaseModel):
    content: str = Field(..., min_length=1)
    parent_comment_id: Optional[UUID] = None


class PostCommentResponse(PostCommentCreate):
    id: UUID
    post_id: UUID
    author_id: UUID
    author_type: str
    like_count: int = 0
    reply_count: int = 0
    created_at: datetime
    updated_at: datetime
    is_deleted: bool = False
    is_edited: bool = False

    class Config:
        from_attributes = True


class PostLikeResponse(BaseModel):
    post_id: UUID
    liked: bool
    reaction_type: str = "like"


__all__ = [
    "TimelinePostCreate",
    "TimelinePostUpdate",
    "TimelinePostResponse",
    "PostCommentCreate",
    "PostCommentResponse",
    "PostLikeResponse",
]
