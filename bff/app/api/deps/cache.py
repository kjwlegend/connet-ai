"""Cache related dependencies."""

from app.infrastructure.cache.cache_manager import CacheManager, get_cache_manager

__all__ = ["CacheManager", "get_cache_manager"]
