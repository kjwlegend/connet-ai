"""
Cache Infrastructure Package

This package provides caching functionality using Redis.
"""

from .cache_manager import CacheManager, get_cache_manager, close_cache_manager
from .redis_client import get_redis_client, close_redis_client
from .cache_keys import CacheKeys, CacheExpiration
from .cache_decorators import (
    cache_result,
    cache_user_data,
    cache_conversation_data,
    cache_search_results,
    invalidate_cache,
    invalidate_user_cache,
    generate_cache_key,
)
from .cache_utils import CacheUtils

__all__ = [
    # Cache Manager
    "CacheManager",
    "get_cache_manager",
    "close_cache_manager",
    
    # Redis Client
    "get_redis_client",
    "close_redis_client",
    
    # Cache Keys & Expiration
    "CacheKeys",
    "CacheExpiration",
    
    # Cache Utils
    "CacheUtils",
    
    # Decorators
    "cache_result",
    "cache_user_data",
    "cache_conversation_data",
    "cache_search_results",
    "invalidate_cache",
    "invalidate_user_cache",
    "generate_cache_key",
]