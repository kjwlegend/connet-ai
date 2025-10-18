"""Redis client configuration and connection management."""

from urllib.parse import urlparse

import redis.asyncio as redis

from app.config.settings import get_settings
from app.utils.logging import get_logger

logger = get_logger(__name__)

_redis_client: redis.Redis | None = None


def get_redis_client() -> redis.Redis:
    """Return a shared Redis client."""
    global _redis_client
    if _redis_client is None:
        settings = get_settings()

        if settings.redis_url:
            url_parts = urlparse(settings.redis_url)
            host = url_parts.hostname or "localhost"
            port = url_parts.port or 6379
            db = (
                int(url_parts.path.strip("/"))
                if url_parts.path and url_parts.path != "/"
                else 0
            )
            password = url_parts.password or settings.redis_password
        else:
            host = getattr(settings, "redis_host", "localhost")
            port = getattr(settings, "redis_port", 6379)
            db = settings.redis_db
            password = settings.redis_password

        _redis_client = redis.Redis(
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

        logger.info("Redis client created for %s:%s/%s", host, port, db)

    return _redis_client


async def close_redis_client() -> None:
    """Close the Redis client."""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None
        logger.info("Redis connection closed")


__all__ = ["get_redis_client", "close_redis_client"]
