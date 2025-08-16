"""
User Service

This module provides user-related business logic.
"""

from typing import List, Optional, Tuple

from app.core.interfaces.repositories.user_repository import UserRepository
from app.infrastructure.cache.cache_manager import CacheManager
from app.infrastructure.cache.cache_keys import CacheKeys, CacheExpiration
from app.schemas.user import User, UserUpdateRequest
from app.services.base import BaseRepositoryService
from app.utils.logging import get_logger

logger = get_logger(__name__)


class UserService(BaseRepositoryService):
    """User service for business logic."""
    
    def __init__(
        self,
        user_repository: UserRepository,
        cache_manager: CacheManager,
    ):
        super().__init__(user_repository, cache_manager, logger_name="UserService")
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        try:
            # Try cache first
            cache_key = f"user:{user_id}"
            cached_user = await self.cache_manager.get(cache_key)
            
            if cached_user:
                logger.debug(f"User {user_id} found in cache")
                return cached_user
            
            # Get from repository
            user = await self.user_repository.get_by_id(user_id)
            
            if user:
                # Cache for 30 minutes
                await self.cache_manager.set(cache_key, user, ttl=1800)
                logger.debug(f"User {user_id} cached")
            
            return user
            
        except Exception as e:
            logger.error(f"Failed to get user {user_id}: {e}")
            raise
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            return await self.user_repository.get_by_email(email)
        except Exception as e:
            logger.error(f"Failed to get user by email {email}: {e}")
            raise
    
    async def list_users(
        self,
        offset: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
    ) -> Tuple[List[User], int]:
        """List users with pagination."""
        try:
            if search:
                users, total = await self.user_repository.search_users(
                    query=search,
                    offset=offset,
                    limit=limit,
                )
            else:
                users = await self.user_repository.get_all(
                    offset=offset,
                    limit=limit,
                )
                total = await self.user_repository.count()
            
            return users, total
            
        except Exception as e:
            logger.error(f"Failed to list users: {e}")
            raise
    
    async def update_user(
        self,
        user_id: str,
        update_request: UserUpdateRequest,
    ) -> Optional[User]:
        """Update user information."""
        try:
            # Build update dict
            updates = {}
            if update_request.full_name is not None:
                updates["full_name"] = update_request.full_name
            if update_request.username is not None:
                updates["username"] = update_request.username
            
            if not updates:
                # No updates to make
                return await self.get_user_by_id(user_id)
            
            # Update in repository
            user = await self.user_repository.update(user_id, updates)
            
            if user:
                # Invalidate cache
                cache_key = f"user:{user_id}"
                await self.cache_manager.delete(cache_key)
                logger.info(f"User {user_id} updated successfully")
            
            return user
            
        except Exception as e:
            logger.error(f"Failed to update user {user_id}: {e}")
            raise
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        try:
            success = await self.user_repository.delete(user_id)
            
            if success:
                # Invalidate cache
                cache_key = f"user:{user_id}"
                await self.cache_manager.delete(cache_key)
                logger.info(f"User {user_id} deleted successfully")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete user {user_id}: {e}")
            raise
    
    async def activate_user(self, user_id: str) -> bool:
        """Activate a user account."""
        try:
            success = await self.user_repository.activate_user(user_id)
            
            if success:
                # Invalidate cache
                cache_key = f"user:{user_id}"
                await self.cache_manager.delete(cache_key)
                logger.info(f"User {user_id} activated successfully")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to activate user {user_id}: {e}")
            raise
    
    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user account."""
        try:
            success = await self.user_repository.deactivate_user(user_id)
            
            if success:
                # Invalidate cache
                cache_key = f"user:{user_id}"
                await self.cache_manager.delete(cache_key)
                logger.info(f"User {user_id} deactivated successfully")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to deactivate user {user_id}: {e}")
            raise
    
    async def get_user_profile(self, user_id: str) -> Optional[User]:
        """Get user profile (public information)."""
        # For now, same as get_user_by_id
        # In the future, this might filter sensitive information
        return await self.get_user_by_id(user_id)


# Factory function for dependency injection
async def get_user_service() -> UserService:
    """Get user service instance."""
    from app.api.dependencies import get_user_repository, get_cache_manager
    
    user_repository = await get_user_repository()
    cache_manager = await get_cache_manager()
    
    return UserService(
        user_repository=user_repository,
        cache_manager=cache_manager
    )