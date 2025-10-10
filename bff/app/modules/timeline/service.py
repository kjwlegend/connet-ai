"""Timeline service implementation."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List
from uuid import UUID

from fastapi import HTTPException, status

from app.modules.timeline.models import (
    TimelineCommentModel,
    TimelineLikeModel,
    TimelinePostModel,
)
from app.modules.timeline.repository import TimelineRepositoryProtocol
from app.modules.timeline.schemas import (
    TimelinePostCreate,
    TimelinePostResponse,
    TimelinePostUpdate,
    PostCommentCreate,
    PostCommentResponse,
    PostLikeResponse,
)


class TimelineService:
    """Business logic for timeline features."""

    def __init__(self, repository: TimelineRepositoryProtocol) -> None:
        self.repository = repository

    # Posts -----------------------------------------------------------------
    async def get_timeline_posts(
        self,
        user_id: UUID,
        category: str,
        skip: int,
        limit: int,
        author_type: str | None,
    ) -> List[TimelinePostResponse]:
        posts, _ = await self.repository.list_posts(
            user_id=user_id,
            category=category,
            author_type=author_type,
            skip=skip,
            limit=limit,
        )
        return [TimelinePostResponse.model_validate(post) for post in posts]

    async def create_post(
        self, user_id: UUID, post_data: TimelinePostCreate
    ) -> TimelinePostResponse:
        payload = post_data.model_dump()
        post = TimelinePostModel(
            author_id=user_id,
            author_type="user",
            **payload,
        )
        created = await self.repository.create_post(post)
        return TimelinePostResponse.model_validate(created)

    async def get_post(self, post_id: UUID, user_id: UUID) -> TimelinePostResponse:
        post = await self.repository.get_post(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Timeline post not found",
            )
        return TimelinePostResponse.model_validate(post)

    async def _require_owner(self, post: TimelinePostModel, user_id: UUID) -> None:
        if post.author_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to modify this post",
            )

    async def update_post(
        self, post_id: UUID, user_id: UUID, post_data: TimelinePostUpdate
    ) -> TimelinePostResponse:
        post = await self.repository.get_post(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Timeline post not found",
            )
        await self._require_owner(post, user_id)

        for field, value in post_data.model_dump(exclude_unset=True).items():
            setattr(post, field, value)
        post.updated_at = datetime.utcnow()

        updated = await self.repository.save_post(post)
        return TimelinePostResponse.model_validate(updated)

    async def delete_post(self, post_id: UUID, user_id: UUID) -> None:
        post = await self.repository.get_post(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Timeline post not found",
            )
        await self._require_owner(post, user_id)
        await self.repository.delete_post(post)

    async def toggle_like_post(self, post_id: UUID, user_id: UUID) -> PostLikeResponse:
        post = await self.repository.get_post(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Timeline post not found",
            )

        existing_like = await self.repository.get_like(
            user_id=user_id, target_id=post_id, target_type="post"
        )

        if existing_like:
            await self.repository.delete_like(existing_like)
            await self.repository.update_post_metrics(post_id, like_delta=-1)
            liked = False
        else:
            like = TimelineLikeModel(
                user_id=user_id,
                target_id=post_id,
                target_type="post",
            )
            await self.repository.create_like(like)
            await self.repository.update_post_metrics(post_id, like_delta=1)
            liked = True

        return PostLikeResponse(post_id=post_id, liked=liked)

    async def share_post(self, post_id: UUID, user_id: UUID) -> TimelinePostResponse:
        original = await self.repository.get_post(post_id)
        if not original:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Timeline post not found",
            )

        shared_post = TimelinePostModel(
            author_id=user_id,
            author_type="user",
            title=original.title,
            content=original.content,
            content_type=original.content_type,
            visibility=original.visibility,
            category=original.category,
            tags=list(original.tags or []),
            hashtags=list(original.hashtags or []),
            attachments=list(original.attachments or []),
            media_urls=list(original.media_urls or []),
            parent_post_id=original.id,
            related_agent_id=original.related_agent_id,
            related_topic_id=original.related_topic_id,
        )

        created = await self.repository.create_post(shared_post)
        await self.repository.update_post_metrics(post_id, share_delta=1)

        return TimelinePostResponse.model_validate(created)

    # Comments --------------------------------------------------------------
    async def get_post_comments(
        self, post_id: UUID, skip: int, limit: int
    ) -> List[PostCommentResponse]:
        post = await self.repository.get_post(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Timeline post not found",
            )

        comments, _ = await self.repository.list_comments(
            post_id, skip=skip, limit=limit
        )
        return [PostCommentResponse.model_validate(comment) for comment in comments]

    async def create_comment(
        self, post_id: UUID, user_id: UUID, comment_data: PostCommentCreate
    ) -> PostCommentResponse:
        post = await self.repository.get_post(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Timeline post not found",
            )

        comment = TimelineCommentModel(
            post_id=post_id,
            parent_comment_id=comment_data.parent_comment_id,
            author_id=user_id,
            author_type="user",
            content=comment_data.content,
        )

        created = await self.repository.create_comment(comment)
        await self.repository.update_post_metrics(post_id, comment_delta=1)

        return PostCommentResponse.model_validate(created)

    async def delete_comment(self, comment_id: UUID, user_id: UUID) -> None:
        comment = await self.repository.get_comment(comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found",
            )
        if comment.author_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this comment",
            )

        await self.repository.delete_comment(comment)
        await self.repository.update_post_metrics(comment.post_id, comment_delta=-1)

    # Stats -----------------------------------------------------------------
    async def get_user_timeline_stats(self, user_id: UUID) -> Dict[str, int]:
        posts = await self.repository.count_posts_by_author(user_id)
        comments = await self.repository.count_comments_by_author(user_id)
        likes = await self.repository.count_likes_by_user(user_id)
        pinned = await self.repository.count_pinned_posts(user_id)

        return {
            "total_posts": posts,
            "total_comments": comments,
            "total_likes": likes,
            "pinned_posts": pinned,
        }

    async def toggle_pin_post(self, post_id: UUID, user_id: UUID, is_pinned: bool) -> None:
        post = await self.repository.get_post(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Timeline post not found",
            )
        await self._require_owner(post, user_id)

        post.is_pinned = is_pinned
        post.updated_at = datetime.utcnow()
        await self.repository.save_post(post)


__all__ = ["TimelineService"]
