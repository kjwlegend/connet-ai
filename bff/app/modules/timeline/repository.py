"""Protocol definition for timeline repository implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from uuid import UUID

from app.modules.timeline.models import (
    TimelineCommentModel,
    TimelineLikeModel,
    TimelinePostModel,
)


class TimelineRepositoryProtocol(ABC):
    """Abstract interface for timeline persistence operations."""

    # Posts -----------------------------------------------------------------
    @abstractmethod
    async def list_posts(
        self,
        *,
        user_id: UUID,
        category: Optional[str],
        author_type: Optional[str],
        skip: int,
        limit: int,
    ) -> Tuple[List[TimelinePostModel], int]:
        """Return paginated posts for a user's feed along with total count."""

    @abstractmethod
    async def get_post(self, post_id: UUID) -> Optional[TimelinePostModel]:
        """Return a timeline post by identifier."""

    @abstractmethod
    async def create_post(self, post: TimelinePostModel) -> TimelinePostModel:
        """Persist a new timeline post."""

    @abstractmethod
    async def save_post(self, post: TimelinePostModel) -> TimelinePostModel:
        """Flush changes to an existing post and return the refreshed entity."""

    @abstractmethod
    async def delete_post(self, post: TimelinePostModel) -> None:
        """Remove a post permanently."""

    @abstractmethod
    async def update_post_metrics(
        self,
        post_id: UUID,
        *,
        like_delta: int = 0,
        comment_delta: int = 0,
        share_delta: int = 0,
        view_delta: int = 0,
    ) -> TimelinePostModel:
        """Adjust summary counters on a post and return the updated record."""

    # Comments --------------------------------------------------------------
    @abstractmethod
    async def list_comments(
        self,
        post_id: UUID,
        *,
        skip: int,
        limit: int,
    ) -> Tuple[List[TimelineCommentModel], int]:
        """Return paginated comments for a post along with total count."""

    @abstractmethod
    async def get_comment(self, comment_id: UUID) -> Optional[TimelineCommentModel]:
        """Return a comment by identifier."""

    @abstractmethod
    async def create_comment(self, comment: TimelineCommentModel) -> TimelineCommentModel:
        """Persist a new comment."""

    @abstractmethod
    async def delete_comment(self, comment: TimelineCommentModel) -> None:
        """Remove an existing comment."""

    # Likes -----------------------------------------------------------------
    @abstractmethod
    async def get_like(
        self,
        *,
        user_id: UUID,
        target_id: UUID,
        target_type: str,
    ) -> Optional[TimelineLikeModel]:
        """Return an existing reaction if present."""

    @abstractmethod
    async def create_like(self, like: TimelineLikeModel) -> TimelineLikeModel:
        """Persist a new reaction."""

    @abstractmethod
    async def delete_like(self, like: TimelineLikeModel) -> None:
        """Remove a reaction."""

    # Aggregations ----------------------------------------------------------
    @abstractmethod
    async def count_posts_by_author(self, author_id: UUID) -> int:
        """Return number of posts created by an author."""

    @abstractmethod
    async def count_comments_by_author(self, author_id: UUID) -> int:
        """Return number of comments created by an author."""

    @abstractmethod
    async def count_likes_by_user(self, user_id: UUID) -> int:
        """Return number of likes performed by a user."""

    @abstractmethod
    async def count_pinned_posts(self, author_id: UUID) -> int:
        """Return number of pinned posts for an author."""


# Backwards compatible alias ------------------------------------------------
TimelineRepository = TimelineRepositoryProtocol

__all__ = ["TimelineRepositoryProtocol", "TimelineRepository"]
