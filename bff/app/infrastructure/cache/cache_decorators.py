"""
Cache Decorators

This module provides decorators for caching function results.
"""

import functools
import hashlib
import json
import pickle
from typing import Any, Callable, Optional, Union

from app.infrastructure.cache.cache_manager import get_cache_manager
from app.infrastructure.cache.cache_keys import CacheExpiration
from app.utils.logging import get_logger

logger = get_logger(__name__)


def generate_cache_key(func_name: str, args: tuple, kwargs: dict) -> str:
    """Generate a cache key from function name and arguments."""
    # Create a stable representation of arguments
    key_data = {
        "func": func_name,
        "args": args,
        "kwargs": sorted(kwargs.items())
    }
    
    # Convert to JSON string and hash
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    key_hash = hashlib.md5(key_str.encode()).hexdigest()
    
    return f"func:{func_name}:{key_hash}"


def cache_result(
    expire: int = CacheExpiration.MEDIUM,
    key_prefix: Optional[str] = None,
    key_generator: Optional[Callable] = None,
    serialize_with_pickle: bool = False
):
    """
    Decorator to cache function results.
    
    Args:
        expire: Cache expiration time in seconds
        key_prefix: Optional prefix for cache key
        key_generator: Custom function to generate cache key
        serialize_with_pickle: Use pickle for complex objects
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            cache_manager = get_cache_manager()
            
            try:
                # Generate cache key
                if key_generator:
                    cache_key = key_generator(*args, **kwargs)
                else:
                    cache_key = generate_cache_key(func.__name__, args, kwargs)
                
                if key_prefix:
                    cache_key = f"{key_prefix}:{cache_key}"
                
                # Try to get from cache
                cached_result = await cache_manager.get(cache_key)
                
                if cached_result is not None:
                    # Deserialize if needed
                    if serialize_with_pickle and isinstance(cached_result, bytes):
                        result = pickle.loads(cached_result)
                    else:
                        result = cached_result
                    
                    logger.debug(f"Cache hit for {func.__name__}: {cache_key}")
                    return result
                
                # Execute function
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # Cache the result
                if serialize_with_pickle:
                    cached_data = pickle.dumps(result)
                else:
                    cached_data = result
                
                await cache_manager.set(cache_key, cached_data, expire=expire)
                logger.debug(f"Cached result for {func.__name__}: {cache_key}")
                
                return result
                
            except Exception as e:
                logger.warning(f"Cache operation failed for {func.__name__}: {e}")
                # Fallback to executing function without cache
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
        
        return wrapper
    return decorator


def cache_user_data(expire: int = CacheExpiration.USER_PROFILE):
    """Decorator specifically for caching user-related data."""
    def key_generator(user_id: str, *args, **kwargs):
        return f"user_data:{user_id}:{hashlib.md5(str(args + tuple(kwargs.items())).encode()).hexdigest()}"
    
    return cache_result(
        expire=expire,
        key_generator=key_generator,
        serialize_with_pickle=True
    )


def cache_conversation_data(expire: int = CacheExpiration.CONVERSATION):
    """Decorator specifically for caching conversation-related data."""
    def key_generator(conversation_id: str, *args, **kwargs):
        return f"conv_data:{conversation_id}:{hashlib.md5(str(args + tuple(kwargs.items())).encode()).hexdigest()}"
    
    return cache_result(
        expire=expire,
        key_generator=key_generator,
        serialize_with_pickle=True
    )


def cache_search_results(expire: int = CacheExpiration.SEARCH_RESULTS):
    """Decorator specifically for caching search results."""
    def key_generator(query: str, *args, **kwargs):
        query_hash = hashlib.md5(query.encode()).hexdigest()
        return f"search:{query_hash}:{hashlib.md5(str(args + tuple(kwargs.items())).encode()).hexdigest()}"
    
    return cache_result(
        expire=expire,
        key_generator=key_generator,
        serialize_with_pickle=True
    )


def invalidate_cache(key_pattern: str):
    """
    Decorator to invalidate cache entries after function execution.
    
    Args:
        key_pattern: Pattern of cache keys to invalidate
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            cache_manager = get_cache_manager()
            
            # Execute function first
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            try:
                # Invalidate cache entries
                await cache_manager.delete_pattern(key_pattern)
                logger.debug(f"Invalidated cache pattern: {key_pattern}")
                
            except Exception as e:
                logger.warning(f"Cache invalidation failed: {e}")
            
            return result
        
        return wrapper
    return decorator


def invalidate_user_cache(user_id_arg: str = "user_id"):
    """Decorator to invalidate user-related cache after function execution."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Execute function first
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            try:
                # Get user_id from arguments
                user_id = kwargs.get(user_id_arg)
                if not user_id and args:
                    # Try to get from positional args (assuming first arg)
                    user_id = args[0] if len(args) > 0 else None
                
                if user_id:
                    cache_manager = get_cache_manager()
                    patterns = [
                        f"user:{user_id}:*",
                        f"user_data:{user_id}:*",
                        f"user:sessions:{user_id}",
                    ]
                    
                    for pattern in patterns:
                        await cache_manager.delete_pattern(pattern)
                    
                    logger.debug(f"Invalidated user cache for: {user_id}")
                
            except Exception as e:
                logger.warning(f"User cache invalidation failed: {e}")
            
            return result
        
        return wrapper
    return decorator


# Import asyncio at the end to avoid circular imports
import asyncio