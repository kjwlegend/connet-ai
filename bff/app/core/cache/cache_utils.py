"""Utility helpers for cache operations."""

import asyncio
import hashlib
from typing import Any, Callable, Dict, List, Optional

from app.core.cache.cache_keys import CacheExpiration, CacheKeys
from app.core.cache.cache_manager import get_cache_manager
from app.utils.logging import get_logger

logger = get_logger(__name__)


class CacheUtils:
    """Utility class for common cache workflows."""

    @staticmethod
    def generate_hash_key(*args, **kwargs) -> str:
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()

    @staticmethod
    async def get_or_set(
        key: str,
        factory_func: Callable,
        expire: int = CacheExpiration.MEDIUM,
        *args,
        **kwargs,
    ) -> Any:
        cache_manager = get_cache_manager()

        try:
            cached_value = await cache_manager.get(key)
            if cached_value is not None:
                logger.debug("Cache hit: %s", key)
                return cached_value

            if asyncio.iscoroutinefunction(factory_func):
                value = await factory_func(*args, **kwargs)
            else:
                value = factory_func(*args, **kwargs)

            await cache_manager.set(key, value, expire=expire)
            logger.debug("Cache set: %s", key)
            return value

        except Exception as exc:
            logger.warning("Cache operation failed for key %s: %s", key, exc)
            if asyncio.iscoroutinefunction(factory_func):
                return await factory_func(*args, **kwargs)
            return factory_func(*args, **kwargs)

    @staticmethod
    async def invalidate_user_related_cache(user_id: str) -> None:
        cache_manager = get_cache_manager()

        patterns = [
            f"user:{user_id}:*",
            f"user_data:{user_id}:*",
            CacheKeys.user_by_id(user_id),
            CacheKeys.user_sessions(user_id),
            CacheKeys.user_contacts(user_id),
            CacheKeys.user_timeline(user_id),
        ]

        for pattern in patterns:
            try:
                if "*" in pattern:
                    await cache_manager.delete_pattern(pattern)
                else:
                    await cache_manager.delete(pattern)
            except Exception as exc:
                logger.warning(
                    "Failed to invalidate cache pattern %s: %s", pattern, exc
                )

    @staticmethod
    async def invalidate_conversation_cache(conversation_id: str) -> None:
        cache_manager = get_cache_manager()

        patterns = [
            f"conv_data:{conversation_id}:*",
            CacheKeys.conversation_by_id(conversation_id),
            CacheKeys.conversation_participants(conversation_id),
            CacheKeys.conversation_messages(conversation_id),
            CacheKeys.conversation_topics(conversation_id),
        ]

        for pattern in patterns:
            try:
                if "*" in pattern:
                    await cache_manager.delete_pattern(pattern)
                else:
                    await cache_manager.delete(pattern)
            except Exception as exc:
                logger.warning(
                    "Failed to invalidate cache pattern %s: %s", pattern, exc
                )

    @staticmethod
    async def cache_user_profile(user_id: str, profile_data: Dict[str, Any]) -> bool:
        cache_manager = get_cache_manager()
        key = CacheKeys.user_by_id(user_id)
        return await cache_manager.set(
            key,
            profile_data,
            expire=CacheExpiration.USER_PROFILE,
        )

    @staticmethod
    async def get_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
        cache_manager = get_cache_manager()
        key = CacheKeys.user_by_id(user_id)
        return await cache_manager.get(key)

    @staticmethod
    async def cache_conversation_data(
        conversation_id: str,
        conversation_data: Dict[str, Any],
    ) -> bool:
        cache_manager = get_cache_manager()
        key = CacheKeys.conversation_by_id(conversation_id)
        return await cache_manager.set(
            key,
            conversation_data,
            expire=CacheExpiration.CONVERSATION,
        )

    @staticmethod
    async def get_conversation_data(conversation_id: str) -> Optional[Dict[str, Any]]:
        cache_manager = get_cache_manager()
        key = CacheKeys.conversation_by_id(conversation_id)
        return await cache_manager.get(key)


__all__ = ["CacheUtils"]
