"""Decorators for caching function results."""

import asyncio
import functools
import hashlib
import json
import pickle
from typing import Any, Callable, Optional

from app.core.cache.cache_keys import CacheExpiration
from app.core.cache.cache_manager import get_cache_manager
from app.utils.logging import get_logger

logger = get_logger(__name__)


def generate_cache_key(func_name: str, args: tuple, kwargs: dict) -> str:
    key_data = {
        "func": func_name,
        "args": args,
        "kwargs": sorted(kwargs.items()),
    }
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    key_hash = hashlib.md5(key_str.encode()).hexdigest()
    return f"func:{func_name}:{key_hash}"


def cache_result(
    expire: int = CacheExpiration.MEDIUM,
    key_prefix: Optional[str] = None,
    key_generator: Optional[Callable] = None,
    serialize_with_pickle: bool = False,
):
    """Decorator to cache function results."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            cache_manager = get_cache_manager()

            try:
                if key_generator:
                    cache_key = key_generator(*args, **kwargs)
                else:
                    cache_key = generate_cache_key(func.__name__, args, kwargs)

                if key_prefix:
                    cache_key = f"{key_prefix}:{cache_key}"

                cached_result = await cache_manager.get(cache_key)
                if cached_result is not None:
                    if serialize_with_pickle and isinstance(cached_result, bytes):
                        result = pickle.loads(cached_result)
                    else:
                        result = cached_result

                    logger.debug("Cache hit for %s: %s", func.__name__, cache_key)
                    return result

                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)

                cached_data = (
                    pickle.dumps(result)
                    if serialize_with_pickle
                    else result
                )

                await cache_manager.set(cache_key, cached_data, expire=expire)
                logger.debug("Cached result for %s: %s", func.__name__, cache_key)
                return result

            except Exception as exc:
                logger.warning("Cache operation failed for %s: %s", func.__name__, exc)
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                return func(*args, **kwargs)

        return wrapper

    return decorator


def cache_user_data(expire: int = CacheExpiration.USER_PROFILE):
    def key_generator(user_id: str, *args, **kwargs):
        return (
            f"user_data:{user_id}:"
            f"{hashlib.md5(str(args + tuple(kwargs.items())).encode()).hexdigest()}"
        )

    return cache_result(
        expire=expire,
        key_generator=key_generator,
        serialize_with_pickle=True,
    )


def cache_conversation_data(expire: int = CacheExpiration.CONVERSATION):
    def key_generator(conversation_id: str, *args, **kwargs):
        return (
            f"conv_data:{conversation_id}:"
            f"{hashlib.md5(str(args + tuple(kwargs.items())).encode()).hexdigest()}"
        )

    return cache_result(
        expire=expire,
        key_generator=key_generator,
        serialize_with_pickle=True,
    )


def cache_search_results(expire: int = CacheExpiration.SEARCH_RESULTS):
    def key_generator(query: str, *args, **kwargs):
        query_hash = hashlib.md5(query.encode()).hexdigest()
        return (
            f"search:{query_hash}:"
            f"{hashlib.md5(str(args + tuple(kwargs.items())).encode()).hexdigest()}"
        )

    return cache_result(
        expire=expire,
        key_generator=key_generator,
        serialize_with_pickle=True,
    )


def invalidate_cache(key_pattern: str):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            cache_manager = get_cache_manager()

            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            try:
                await cache_manager.delete_pattern(key_pattern)
                logger.debug("Invalidated cache pattern: %s", key_pattern)
            except Exception as exc:
                logger.warning("Cache invalidation failed: %s", exc)

            return result

        return wrapper

    return decorator


def invalidate_user_cache(user_id_arg: str = "user_id"):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            try:
                user_id = kwargs.get(user_id_arg)
                if not user_id and args:
                    user_id = args[0]

                if user_id:
                    cache_manager = get_cache_manager()
                    patterns = [
                        f"user:{user_id}:*",
                        f"user_data:{user_id}:*",
                        f"user:sessions:{user_id}",
                    ]
                    for pattern in patterns:
                        await cache_manager.delete_pattern(pattern)
                    logger.debug("Invalidated user cache for: %s", user_id)

            except Exception as exc:
                logger.warning("User cache invalidation failed: %s", exc)

            return result

        return wrapper

    return decorator


__all__ = [
    "cache_result",
    "cache_user_data",
    "cache_conversation_data",
    "cache_search_results",
    "invalidate_cache",
    "invalidate_user_cache",
    "generate_cache_key",
]
