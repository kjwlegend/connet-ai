"""
Cache Manager

High-level interface for Redis cache operations.
"""

import json
import pickle
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

import redis.asyncio as redis

from app.config.settings import get_settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


class CacheManager:
    """High-level cache manager for Redis operations."""

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self._redis_client = redis_client
        self.settings = get_settings()

    async def _get_client(self) -> redis.Redis:
        if self._redis_client is None:
            if self.settings.redis_url:
                url_parts = urlparse(self.settings.redis_url)
                host = url_parts.hostname or "localhost"
                port = url_parts.port or 6379
                db = (
                    int(url_parts.path.strip("/"))
                    if url_parts.path and url_parts.path != "/"
                    else 0
                )
                password = url_parts.password or self.settings.redis_password
            else:
                host = getattr(self.settings, "redis_host", "localhost")
                port = getattr(self.settings, "redis_port", 6379)
                db = self.settings.redis_db
                password = self.settings.redis_password

            self._redis_client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                retry_on_error=[redis.ConnectionError, redis.TimeoutError],
                health_check_interval=30,
            )

        return self._redis_client

    async def get(self, key: str, default: Any = None) -> Any:
        try:
            client = await self._get_client()
            value = await client.get(key)

            if value is None:
                return default

            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                try:
                    return pickle.loads(
                        value.encode("latin-1") if isinstance(value, str) else value
                    )
                except (pickle.PickleError, TypeError):
                    return value

        except Exception as exc:
            logger.warning("Cache get failed for key %s: %s", key, exc)
            return default

    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None,
        nx: bool = False,
        xx: bool = False,
    ) -> bool:
        try:
            client = await self._get_client()

            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(
                    value, ensure_ascii=False, default=str
                )
            elif isinstance(value, (int, float, str, bool)) or value is None:
                serialized_value = json.dumps(value)
            else:
                serialized_value = pickle.dumps(value).decode("latin-1")

            result = await client.set(
                key,
                serialized_value,
                ex=expire,
                nx=nx,
                xx=xx,
            )

            return bool(result)

        except Exception as exc:
            logger.error("Cache set failed for key %s: %s", key, exc)
            return False

    async def delete(self, *keys: str) -> int:
        try:
            if not keys:
                return 0

            client = await self._get_client()
            return await client.delete(*keys)

        except Exception as exc:
            logger.error("Cache delete failed for keys %s: %s", keys, exc)
            return 0

    async def exists(self, *keys: str) -> int:
        try:
            if not keys:
                return 0

            client = await self._get_client()
            return await client.exists(*keys)

        except Exception as exc:
            logger.warning("Cache exists check failed for keys %s: %s", keys, exc)
            return 0

    async def expire(self, key: str, seconds: int) -> bool:
        try:
            client = await self._get_client()
            return await client.expire(key, seconds)
        except Exception as exc:
            logger.error("Cache expire failed for key %s: %s", key, exc)
            return False

    async def ttl(self, key: str) -> int:
        try:
            client = await self._get_client()
            return await client.ttl(key)
        except Exception as exc:
            logger.error("Cache TTL failed for key %s: %s", key, exc)
            return -2

    async def keys(self, pattern: str = "*") -> List[str]:
        try:
            client = await self._get_client()
            return await client.keys(pattern)
        except Exception as exc:
            logger.warning("Cache keys failed for pattern %s: %s", pattern, exc)
            return []

    async def delete_pattern(self, pattern: str) -> int:
        try:
            client = await self._get_client()
            cursor = "0"
            total_deleted = 0

            while cursor != 0:
                cursor, keys = await client.scan(cursor=cursor, match=pattern, count=1000)
                if keys:
                    total_deleted += await client.delete(*keys)

            return total_deleted
        except Exception as exc:
            logger.error("Cache pattern delete failed for %s: %s", pattern, exc)
            return 0


_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


__all__ = ["CacheManager", "get_cache_manager"]
