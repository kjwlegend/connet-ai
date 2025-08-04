"""
User Management Endpoints

This module contains user management endpoints.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import (
    get_current_user,
    get_pagination_params,
    get_user_service,
    require_permission,
)
from app.schemas.responses import PaginatedResponse
from app.schemas.user import User, UserResponse, UserUpdateRequest
from app.services.user_service import UserService
from app.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/", response_model=PaginatedResponse[UserResponse])
async def list_users(
    pagination: dict = Depends(get_pagination_params),
    search: str = Query(None, description="Search users by name or email"),
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_permission("user", "list")),
) -> PaginatedResponse[UserResponse]:
    """List users with pagination and search."""
    try:
        users, total = await user_service.list_users(
            offset=pagination["offset"],
            limit=pagination["limit"],
            search=search,
        )
        
        user_responses = [UserResponse.from_user(user) for user in users]
        
        return PaginatedResponse(
            items=user_responses,
            total=total,
            page=pagination["page"],
            size=pagination["size"],
            pages=(total + pagination["size"] - 1) // pagination["size"],
        )
        
    except Exception as e:
        logger.error(f"Failed to list users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list users"
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_permission("user", "read")),
) -> UserResponse:
    """Get user by ID."""
    try:
        user = await user_service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse.from_user(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user"
        )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    request: UserUpdateRequest,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Update user information."""
    try:
        # Check if user is updating their own profile or has admin permission
        if current_user.id != user_id:
            # Check if current user has permission to update other users
            # This would be handled by a permission dependency in production
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own profile"
            )
        
        user = await user_service.update_user(user_id, request)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"User updated successfully: {user_id}")
        return UserResponse.from_user(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_permission("user", "delete")),
) -> dict:
    """Delete a user."""
    try:
        # Prevent users from deleting themselves
        if current_user.id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot delete your own account"
            )
        
        success = await user_service.delete_user(user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"User deleted successfully: {user_id}")
        return {"message": "User deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )


@router.get("/{user_id}/profile", response_model=UserResponse)
async def get_user_profile(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Get user profile (public information)."""
    try:
        user = await user_service.get_user_profile(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse.from_user(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user profile {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile"
        )


@router.post("/{user_id}/activate")
async def activate_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_permission("user", "activate")),
) -> dict:
    """Activate a user account."""
    try:
        success = await user_service.activate_user(user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"User activated successfully: {user_id}")
        return {"message": "User activated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to activate user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to activate user"
        )


@router.post("/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_permission("user", "deactivate")),
) -> dict:
    """Deactivate a user account."""
    try:
        # Prevent users from deactivating themselves
        if current_user.id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot deactivate your own account"
            )
        
        success = await user_service.deactivate_user(user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"User deactivated successfully: {user_id}")
        return {"message": "User deactivated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to deactivate user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate user"
        )