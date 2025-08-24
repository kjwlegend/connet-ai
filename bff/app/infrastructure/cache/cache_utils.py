"""
Cache Utilities

This module provides utility functions for common caching operations.
"""

import asyncio
import hashlib
from typing import Any, Dict, List, Optional, Union, Callable

from app.infrastructure.cache.cache_manager import get_cache_manager
from app.infrastructure.cache.cache_keys import CacheKeys, CacheExpiration
from app.utils.logging import get_logger

logger = get_logger(__name__)


class CacheUtils:
    """Utility class for common cache operations."""
    
    @staticmethod
    def generate_hash_key(*args, **kwargs) -> str:
        """Generate a hash key from arguments."""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    @staticmethod
    async def get_or_set(
        key: str,
        factory_func: Callable,
        expire: int = CacheExpiration.MEDIUM,
        *args,
        **kwargs
    ) -> Any:
        """
        Get value from cache or execute factory function and cache result.
        
        Args:
            key: Cache key
            factory_func: Function to execute if cache miss
            expire: Cache expiration time
            args: Arguments for factory function
            kwargs: Keyword arguments for factory function
            
        Returns:
            Cached or newly computed value
        """
        cache_manager = get_cache_manager()
        
        try:
            # Try to get from cache first
            cached_value = await cache_manager.get(key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {key}")
                return cached_value
            
            # Execute factory function
            if asyncio.iscoroutinefunction(factory_func):
                value = await factory_func(*args, **kwargs)
            else:
                value = factory_func(*args, **kwargs)
            
            # Cache the result
            await cache_manager.set(key, value, expire=expire)
            logger.debug(f"Cache set: {key}")
            
            return value
            
        except Exception as e:
            logger.warning(f"Cache operation failed for key {key}: {e}")
            # Fallback to direct execution
            if asyncio.iscoroutinefunction(factory_func):
                return await factory_func(*args, **kwargs)
            else:
                return factory_func(*args, **kwargs)
    
    @staticmethod
    async def invalidate_user_related_cache(user_id: str) -> None:
        """
        Invalidate all user-related cache entries.
        
        Args:
            user_id: User ID to invalidate cache for
        """
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
            except Exception as e:
                logger.warning(f"Failed to invalidate cache pattern {pattern}: {e}")
    
    @staticmethod
    async def invalidate_conversation_cache(conversation_id: str) -> None:
        """
        Invalidate conversation-related cache entries.
        
        Args:
            conversation_id: Conversation ID to invalidate cache for
        """
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
            except Exception as e:
                logger.warning(f"Failed to invalidate cache pattern {pattern}: {e}")
    
    @staticmethod
    async def cache_user_profile(user_id: str, profile_data: Dict[str, Any]) -> bool:
        """
        Cache user profile data.
        
        Args:
            user_id: User ID
            profile_data: Profile data to cache
            
        Returns:
            True if successful, False otherwise
        """
        cache_manager = get_cache_manager()
        key = CacheKeys.user_by_id(user_id)
        
        return await cache_manager.set(
            key, 
            profile_data, 
            expire=CacheExpiration.USER_PROFILE
        )
    
    @staticmethod
    async def get_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile from cache.
        
        Args:
            user_id: User ID
            
        Returns:
            User profile data or None
        """
        cache_manager = get_cache_manager()
        key = CacheKeys.user_by_id(user_id)
        
        return await cache_manager.get(key)
    
    @staticmethod
    async def cache_conversation_data(
        conversation_id: str, 
        conversation_data: Dict[str, Any]
    ) -> bool:
        """
        Cache conversation data.
        
        Args:
            conversation_id: Conversation ID
            conversation_data: Conversation data to cache
            
        Returns:
            True if successful, False otherwise
        """
        cache_manager = get_cache_manager()
        key = CacheKeys.conversation_by_id(conversation_id)
        
        return await cache_manager.set(
            key, 
            conversation_data, 
            expire=CacheExpiration.CONVERSATION
        )
    
    @staticmethod
    async def get_conversation_data(conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get conversation data from cache.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Conversation data or None
        """
        cache_manager = get_cache_manager()
        key = CacheKeys.conversation_by_id(conversation_id)
        
        return await cache_manager.get(key)
    
    @staticmethod
    async def cache_search_results(
        query: str, 
        results: List[Dict[str, Any]], 
        page: Optional[int] = None
    ) -> bool:
        """
        Cache search results.
        
        Args:
            query: Search query
            results: Search results to cache
            page: Page number (optional)
            
        Returns:
            True if successful, False otherwise
        """
        cache_manager = get_cache_manager()
        query_hash = hashlib.md5(query.encode()).hexdigest()
        key = CacheKeys.search_results(query_hash, page)
        
        return await cache_manager.set(
            key, 
            results, 
            expire=CacheExpiration.SEARCH_RESULTS
        )
    
    @staticmethod
    async def get_search_results(
        query: str, 
        page: Optional[int] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get search results from cache.
        
        Args:
            query: Search query
            page: Page number (optional)
            
        Returns:
            Search results or None
        """
        cache_manager = get_cache_manager()
        query_hash = hashlib.md5(query.encode()).hexdigest()
        key = CacheKeys.search_results(query_hash, page)
        
        return await cache_manager.get(key)
    
    @staticmethod
    async def set_rate_limit(
        key: str, 
        limit: int, 
        window_seconds: int = 60
    ) -> bool:
        """
        Set rate limit counter.
        
        Args:
            key: Rate limit key
            limit: Maximum number of requests
            window_seconds: Time window in seconds
            
        Returns:
            True if within limit, False if exceeded
        """
        cache_manager = get_cache_manager()
        
        try:
            # Get current count
            current = await cache_manager.get(key, 0)
            
            if current >= limit:
                return False
            
            # Increment counter
            await cache_manager.increment(key)
            
            # Set expiration on first increment
            if current == 0:
                await cache_manager.expire(key, window_seconds)
            
            return True
            
        except Exception as e:
            logger.error(f"Rate limit check failed for key {key}: {e}")
            return False
    
    @staticmethod
    async def check_rate_limit(key: str) -> int:
        """
        Check current rate limit count.
        
        Args:
            key: Rate limit key
            
        Returns:
            Current count
        """
        cache_manager = get_cache_manager()
        return await cache_manager.get(key, 0)
    
    @staticmethod
    async def cache_session_data(
        user_id: str, 
        session_data: Dict[str, Any]
    ) -> bool:
        """
        Cache user session data.
        
        Args:
            user_id: User ID
            session_data: Session data to cache
            
        Returns:
            True if successful, False otherwise
        """
        cache_manager = get_cache_manager()
        key = CacheKeys.user_sessions(user_id)
        
        return await cache_manager.set(
            key, 
            session_data, 
            expire=CacheExpiration.USER_SESSION
        )
    
    @staticmethod
    async def get_session_data(user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user session data from cache.
        
        Args:
            user_id: User ID
            
        Returns:
            Session data or None
        """
        cache_manager = get_cache_manager()
        key = CacheKeys.user_sessions(user_id)
        
        return await cache_manager.get(key)
    
    @staticmethod
    async def invalidate_session(user_id: str) -> bool:
        """
        Invalidate user session.
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful, False otherwise
        """
        cache_manager = get_cache_manager()
        key = CacheKeys.user_sessions(user_id)
        
        return await cache_manager.delete(key) > 0
    
    @staticmethod
    async def cache_jwt_blacklist(token_id: str, expire: int) -> bool:
        """
        Add JWT token to blacklist.
        
        Args:
            token_id: JWT token ID
            expire: Expiration time in seconds
            
        Returns:
            True if successful, False otherwise
        """
        cache_manager = get_cache_manager()
        key = CacheKeys.jwt_blacklist(token_id)
        
        return await cache_manager.set(key, True, expire=expire)
    
    @staticmethod
    async def is_jwt_blacklisted(token_id: str) -> bool:
        """
        Check if JWT token is blacklisted.
        
        Args:
            token_id: JWT token ID
            
        Returns:
            True if blacklisted, False otherwise
        """
        cache_manager = get_cache_manager()
        key = CacheKeys.jwt_blacklist(token_id)
        
        return await cache_manager.exists(key) > 0
    
    @staticmethod
    async def batch_get(keys: List[str]) -> Dict[str, Any]:
        """
        Get multiple values from cache.
        
        Args:
            keys: List of cache keys
            
        Returns:
            Dictionary of key-value pairs
        """
        cache_manager = get_cache_manager()
        result = {}
        
        # Redis doesn't have async mget, so we'll use asyncio.gather
        async def get_single(key: str):
            return key, await cache_manager.get(key)
        
        try:
            tasks = [get_single(key) for key in keys]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result_item in results:
                if isinstance(result_item, Exception):
                    logger.warning(f"Batch get failed for a key: {result_item}")
                    continue
                
                key, value = result_item
                if value is not None:
                    result[key] = value
            
            return result
            
        except Exception as e:
            logger.error(f"Batch get operation failed: {e}")
            return {}
    
    @staticmethod
    async def batch_set(data: Dict[str, Any], expire: Optional[int] = None) -> int:
        """
        Set multiple values in cache.
        
        Args:
            data: Dictionary of key-value pairs
            expire: Expiration time in seconds
            
        Returns:
            Number of successful sets
        """
        cache_manager = get_cache_manager()
        
        async def set_single(key: str, value: Any):
            return await cache_manager.set(key, value, expire=expire)
        
        try:
            tasks = [set_single(key, value) for key, value in data.items()]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            success_count = 0
            for result in results:
                if isinstance(result, Exception):
                    logger.warning(f"Batch set failed for a key: {result}")
                elif result:
                    success_count += 1
            
            return success_count
            
        except Exception as e:
            logger.error(f"Batch set operation failed: {e}")
            return 0