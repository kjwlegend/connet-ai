"""SQLAlchemy implementation of the timeline repository protocol."""

from __future__ import annotations

from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.timeline.models import (
    TimelineCommentModel,
    TimelineLikeModel,
    TimelinePostModel,
)
from app.modules.timeline.repository import TimelineRepositoryProtocol


class TimelineRepository(TimelineRepositoryProtocol):
    """Persistence layer for timeline posts, comments, and reactions."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # Posts -----------------------------------------------------------------
    async def list_posts(
        self,
        *,
        user_id: UUID,
        category: Optional[str],
        author_type: Optional[str],
        skip: int,
        limit: int,
    ) -> Tuple[List[TimelinePostModel], int]:
        filters = []
        if category and category != "all":
            filters.append(TimelinePostModel.category == category)
        if author_type and author_type not in {"all", ""}:
            filters.append(TimelinePostModel.author_type == author_type)

        stmt = (
            select(TimelinePostModel)
            .where(*filters)
            .order_by(desc(TimelinePostModel.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        posts = result.scalars().all()

        count_stmt = select(func.count()).select_from(TimelinePostModel).where(*filters)
        total_result = await self.session.execute(count_stmt)
        total = int(total_result.scalar_one())

        return posts, total

    async def get_post(self, post_id: UUID) -> Optional[TimelinePostModel]:
        return await self.session.get(TimelinePostModel, post_id)

    async def create_post(self, post: TimelinePostModel) -> TimelinePostModel:
        self.session.add(post)
        await self.session.flush()
        await self.session.refresh(post)
        return post

    async def save_post(self, post: TimelinePostModel) -> TimelinePostModel:
        await self.session.flush()
        await self.session.refresh(post)
        return post

    async def delete_post(self, post: TimelinePostModel) -> None:
        await self.session.delete(post)
        await self.session.flush()

    async def update_post_metrics(
        self,
        post_id: UUID,
        *,
        like_delta: int = 0,
        comment_delta: int = 0,
        share_delta: int = 0,
        view_delta: int = 0,
    ) -> TimelinePostModel:
        post = await self.get_post(post_id)
        if not post:
            raise ValueError(f"Timeline post {post_id} not found")

        post.like_count = max(0, post.like_count + like_delta)
        post.comment_count = max(0, post.comment_count + comment_delta)
        post.share_count = max(0, post.share_count + share_delta)
        post.view_count = max(0, post.view_count + view_delta)

        await self.session.flush()
        await self.session.refresh(post)
        return post

    # Comments --------------------------------------------------------------
    async def list_comments(
        self,
        post_id: UUID,
        *,
        skip: int,
        limit: int,
    ) -> Tuple[List[TimelineCommentModel], int]:
        stmt = (
            select(TimelineCommentModel)
            .where(TimelineCommentModel.post_id == post_id)
            .order_by(TimelineCommentModel.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        comments = result.scalars().all()

        count_stmt = (
            select(func.count())
            .select_from(TimelineCommentModel)
            .where(TimelineCommentModel.post_id == post_id)
        )
        count_result = await self.session.execute(count_stmt)
        total = int(count_result.scalar_one())
        return comments, total

    async def get_comment(self, comment_id: UUID) -> Optional[TimelineCommentModel]:
        return await self.session.get(TimelineCommentModel, comment_id)

    async def create_comment(self, comment: TimelineCommentModel) -> TimelineCommentModel:
        self.session.add(comment)
        await self.session.flush()
        await self.session.refresh(comment)
        return comment

    async def delete_comment(self, comment: TimelineCommentModel) -> None:
        await self.session.delete(comment)
        await self.session.flush()

    # Likes -----------------------------------------------------------------
    async def get_like(
        self,
        *,
        user_id: UUID,
        target_id: UUID,
        target_type: str,
    ) -> Optional[TimelineLikeModel]:
        stmt = select(TimelineLikeModel).where(
            and_(
                TimelineLikeModel.user_id == user_id,
                TimelineLikeModel.target_id == target_id,
                TimelineLikeModel.target_type == target_type,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_like(self, like: TimelineLikeModel) -> TimelineLikeModel:
        self.session.add(like)
        await self.session.flush()
        await self.session.refresh(like)
        return like

    async def delete_like(self, like: TimelineLikeModel) -> None:
        await self.session.delete(like)
        await self.session.flush()

    # Aggregations ----------------------------------------------------------
    async def count_posts_by_author(self, author_id: UUID) -> int:
        stmt = select(func.count()).select_from(TimelinePostModel).where(
            TimelinePostModel.author_id == author_id
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def count_comments_by_author(self, author_id: UUID) -> int:
        stmt = select(func.count()).select_from(TimelineCommentModel).where(
            TimelineCommentModel.author_id == author_id
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def count_likes_by_user(self, user_id: UUID) -> int:
        stmt = select(func.count()).select_from(TimelineLikeModel).where(
            TimelineLikeModel.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def count_pinned_posts(self, author_id: UUID) -> int:
        stmt = select(func.count()).select_from(TimelinePostModel).where(
            and_(
                TimelinePostModel.author_id == author_id,
                TimelinePostModel.is_pinned.is_(True),
            )
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one())


__all__ = ["TimelineRepository"]
