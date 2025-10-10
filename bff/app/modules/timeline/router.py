"""Timeline/Social API Endpoints."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user
from app.api.deps.services import get_timeline_service
from app.modules.timeline.schemas import (
    PostCommentCreate,
    PostCommentResponse,
    PostLikeResponse,
    TimelinePostCreate,
    TimelinePostResponse,
    TimelinePostUpdate,
)
from app.modules.timeline.service import TimelineService
from app.modules.users.schemas import User

router = APIRouter()


@router.get("/posts", response_model=List[TimelinePostResponse])
async def get_timeline_posts(
    category: str = Query(
        "friends_circle",
        pattern="^(friends_circle|public_square|my_circle|favorites|all)$",
    ),
    skip: int = Query(0, ge=0, description="Skip posts"),
    limit: int = Query(20, le=50, description="Limit posts"),
    author_type: Optional[str] = Query(
        None,
        pattern="^(user|agent|all)$",
        description="Filter by author type",
    ),
    current_user: User = Depends(get_current_user),
    timeline_service: TimelineService = Depends(get_timeline_service),
):
    """Get timeline posts by category."""
    return await timeline_service.get_timeline_posts(
        user_id=UUID(str(current_user.id)),
        category=category,
        skip=skip,
        limit=limit,
        author_type=author_type,
    )


@router.post("/posts", response_model=TimelinePostResponse)
async def create_post(
    post_data: TimelinePostCreate,
    current_user: User = Depends(get_current_user),
    timeline_service: TimelineService = Depends(get_timeline_service),
):
    """Create a new timeline post."""
    return await timeline_service.create_post(
        user_id=UUID(str(current_user.id)),
        post_data=post_data,
    )


@router.get("/posts/{post_id}", response_model=TimelinePostResponse)
async def get_post(
    post_id: UUID,
    current_user: User = Depends(get_current_user),
    timeline_service: TimelineService = Depends(get_timeline_service),
):
    """Get specific post details."""
    return await timeline_service.get_post(
        post_id=post_id,
        user_id=UUID(str(current_user.id)),
    )


@router.put("/posts/{post_id}", response_model=TimelinePostResponse)
async def update_post(
    post_id: UUID,
    post_data: TimelinePostUpdate,
    current_user: User = Depends(get_current_user),
    timeline_service: TimelineService = Depends(get_timeline_service),
):
    """Update a post (only by author)."""
    return await timeline_service.update_post(
        post_id=post_id,
        user_id=UUID(str(current_user.id)),
        post_data=post_data,
    )


@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: UUID,
    current_user: User = Depends(get_current_user),
    timeline_service: TimelineService = Depends(get_timeline_service),
):
    """Delete a post (only by author)."""
    await timeline_service.delete_post(
        post_id=post_id,
        user_id=UUID(str(current_user.id)),
    )
    return {"message": "Post deleted successfully"}


@router.post("/posts/{post_id}/like", response_model=PostLikeResponse)
async def like_post(
    post_id: UUID,
    current_user: User = Depends(get_current_user),
    timeline_service: TimelineService = Depends(get_timeline_service),
):
    """Like or unlike a post."""
    return await timeline_service.toggle_like_post(
        post_id=post_id,
        user_id=UUID(str(current_user.id)),
    )


@router.post("/posts/{post_id}/share", response_model=TimelinePostResponse)
async def share_post(
    post_id: UUID,
    current_user: User = Depends(get_current_user),
    timeline_service: TimelineService = Depends(get_timeline_service),
):
    """Share/repost a post."""
    return await timeline_service.share_post(
        post_id=post_id,
        user_id=UUID(str(current_user.id)),
    )


@router.get("/posts/{post_id}/comments", response_model=List[PostCommentResponse])
async def get_post_comments(
    post_id: UUID,
    skip: int = Query(0, ge=0, description="Skip comments"),
    limit: int = Query(20, le=50, description="Limit comments"),
    current_user: User = Depends(get_current_user),
    timeline_service: TimelineService = Depends(get_timeline_service),
):
    """Get comments for a post."""
    return await timeline_service.get_post_comments(
        post_id=post_id,
        skip=skip,
        limit=limit,
    )


@router.post("/posts/{post_id}/comments", response_model=PostCommentResponse)
async def create_comment(
    post_id: UUID,
    comment_data: PostCommentCreate,
    current_user: User = Depends(get_current_user),
    timeline_service: TimelineService = Depends(get_timeline_service),
):
    """Add a comment to a post."""
    return await timeline_service.create_comment(
        post_id=post_id,
        user_id=UUID(str(current_user.id)),
        comment_data=comment_data,
    )


@router.delete("/posts/{post_id}/comments/{comment_id}")
async def delete_comment(
    post_id: UUID,
    comment_id: UUID,
    current_user: User = Depends(get_current_user),
    timeline_service: TimelineService = Depends(get_timeline_service),
):
    """Delete a comment (only by author)."""
    await timeline_service.delete_comment(
        comment_id=comment_id,
        user_id=UUID(str(current_user.id)),
    )
    return {"message": "Comment deleted successfully"}


@router.get("/categories")
async def get_timeline_categories():
    """Get available timeline categories and their descriptions."""
    return {
        "categories": [
            {
                "key": "friends_circle",
                "name": "Friends Circle",
                "description": "Posts from friends and contacts you follow",
            },
            {
                "key": "public_square",
                "name": "Public Square",
                "description": "Public posts from users and agents you don't follow",
            },
            {
                "key": "my_circle",
                "name": "My Circle",
                "description": "Your own posts and activities",
            },
            {
                "key": "favorites",
                "name": "Favorites",
                "description": "Posts you've liked or favorited",
            },
        ]
    }


@router.get("/stats")
async def get_timeline_stats(
    current_user: User = Depends(get_current_user),
    timeline_service: TimelineService = Depends(get_timeline_service),
):
    """Get timeline statistics for the user."""
    return await timeline_service.get_user_timeline_stats(
        UUID(str(current_user.id))
    )


@router.post("/posts/{post_id}/pin")
async def pin_post(
    post_id: UUID,
    current_user: User = Depends(get_current_user),
    timeline_service: TimelineService = Depends(get_timeline_service),
):
    """Pin a post to profile (only own posts)."""
    await timeline_service.toggle_pin_post(
        post_id=post_id,
        user_id=UUID(str(current_user.id)),
        is_pinned=True,
    )
    return {"message": "Post pinned successfully"}


@router.delete("/posts/{post_id}/pin")
async def unpin_post(
    post_id: UUID,
    current_user: User = Depends(get_current_user),
    timeline_service: TimelineService = Depends(get_timeline_service),
):
    """Unpin a post from profile."""
    await timeline_service.toggle_pin_post(
        post_id=post_id,
        user_id=UUID(str(current_user.id)),
        is_pinned=False,
    )
    return {"message": "Post unpinned successfully"}
