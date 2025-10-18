"""User Service business logic for the users module."""

from typing import List, Optional, Tuple

from app.core.cache import CacheManager, CacheExpiration, CacheKeys
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import User, UserUpdateRequest
from app.utils.logging import get_logger


class UserService:
    """Coordinates user-related application logic."""

    def __init__(
        self,
        user_repository: UserRepository,
        cache_manager: CacheManager,
    ) -> None:
        self.user_repository = user_repository
        self.cache_manager = cache_manager
        self.logger = get_logger("UserService")

    async def _cache_get(self, key: str) -> Optional[User]:
        if not self.cache_manager:
            return None
        try:
            return await self.cache_manager.get(key)
        except Exception as exc:  # pragma: no cover - defensive
            self.logger.warning("Cache get failed", extra={"key": key, "error": str(exc)})
            return None

    async def _cache_set(self, key: str, value: User, expire: int) -> None:
        if not self.cache_manager:
            return
        try:
            await self.cache_manager.set(key, value, expire=expire)
        except Exception as exc:  # pragma: no cover - defensive
            self.logger.warning("Cache set failed", extra={"key": key, "error": str(exc)})

    async def _cache_delete(self, key: str) -> None:
        if not self.cache_manager:
            return
        try:
            await self.cache_manager.delete(key)
        except Exception as exc:  # pragma: no cover - defensive
            self.logger.warning("Cache delete failed", extra={"key": key, "error": str(exc)})

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        cache_key = CacheKeys.USER_BY_ID.format(user_id=user_id)

        cached_user = await self._cache_get(cache_key)
        if cached_user:
            self.logger.debug("User cache hit", extra={"user_id": user_id})
            return cached_user

        user = await self.user_repository.get_by_id(user_id)
        if user:
            await self._cache_set(cache_key, user, CacheExpiration.USER_PROFILE)
        return user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        return await self.user_repository.get_by_email(email)

    async def list_users(
        self,
        offset: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
    ) -> Tuple[List[User], int]:
        if search:
            return await self.user_repository.search_users(
                query=search,
                offset=offset,
                limit=limit,
            )

        users = await self.user_repository.get_all(offset=offset, limit=limit)
        total = await self.user_repository.count()
        return users, total

    async def update_user(
        self,
        user_id: str,
        update_request: UserUpdateRequest,
    ) -> Optional[User]:
        updates: dict = {}
        if update_request.full_name is not None:
            updates["full_name"] = update_request.full_name
        if update_request.username is not None:
            updates["username"] = update_request.username

        if not updates:
            return await self.get_user_by_id(user_id)

        user = await self.user_repository.update(user_id, updates)
        if user:
            await self._cache_delete(CacheKeys.USER_BY_ID.format(user_id=user_id))
        return user

    async def delete_user(self, user_id: str) -> bool:
        success = await self.user_repository.delete(user_id)
        if success:
            await self._cache_delete(CacheKeys.USER_BY_ID.format(user_id=user_id))
        return success

    async def activate_user(self, user_id: str) -> bool:
        success = await self.user_repository.activate_user(user_id)
        if success:
            await self._cache_delete(CacheKeys.USER_BY_ID.format(user_id=user_id))
        return success

    async def deactivate_user(self, user_id: str) -> bool:
        success = await self.user_repository.deactivate_user(user_id)
        if success:
            await self._cache_delete(CacheKeys.USER_BY_ID.format(user_id=user_id))
        return success

    async def get_user_profile(self, user_id: str) -> Optional[User]:
        return await self.get_user_by_id(user_id)
