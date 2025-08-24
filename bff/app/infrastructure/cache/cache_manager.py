"""
Cache Manager

This module provides a high-level interface for cache operations.
Handles Redis connections, key management, and common cache operations.
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
        """Initialize cache manager with Redis client."""
        self._redis_client = redis_client
        self.settings = get_settings()
    
    async def _get_client(self) -> redis.Redis:
        """Get Redis client instance."""
        if self._redis_client is None:
            # Parse Redis URL or use individual components
            if self.settings.redis_url:
                url_parts = urlparse(self.settings.redis_url)
                host = url_parts.hostname or "localhost"
                port = url_parts.port or 6379
                db = int(url_parts.path.strip("/")) if url_parts.path and url_parts.path != "/" else 0
                password = url_parts.password or self.settings.redis_password
            else:
                host = getattr(self.settings, 'redis_host', 'localhost')
                port = getattr(self.settings, 'redis_port', 6379)
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
        """
        Get value from cache.
        
        Args:
            key: Cache key
            default: Default value if key not found
            
        Returns:
            Cached value or default
        """
        try:
            client = await self._get_client()
            value = await client.get(key)
            
            if value is None:
                return default
            
            # Try to deserialize JSON first, then pickle
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                try:
                    return pickle.loads(value.encode('latin-1') if isinstance(value, str) else value)
                except (pickle.PickleError, TypeError):
                    return value
                    
        except Exception as e:
            logger.warning(f"Cache get failed for key {key}: {e}")
            return default
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        expire: Optional[int] = None,
        nx: bool = False,
        xx: bool = False
    ) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            expire: Expiration time in seconds
            nx: Set only if key doesn't exist
            xx: Set only if key exists
            
        Returns:
            True if successful, False otherwise
        """
        try:
            client = await self._get_client()
            
            # Serialize value
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value, ensure_ascii=False, default=str)
            elif isinstance(value, (int, float, str, bool)) or value is None:
                serialized_value = json.dumps(value)
            else:
                # Use pickle for complex objects
                serialized_value = pickle.dumps(value).decode('latin-1')
            
            result = await client.set(
                key, 
                serialized_value, 
                ex=expire, 
                nx=nx, 
                xx=xx
            )
            
            return bool(result)
            
        except Exception as e:
            logger.error(f"Cache set failed for key {key}: {e}")
            return False
    
    async def delete(self, *keys: str) -> int:
        """
        Delete one or more keys from cache.
        
        Args:
            keys: Cache keys to delete
            
        Returns:
            Number of keys deleted
        """
        try:
            if not keys:
                return 0
                
            client = await self._get_client()
            return await client.delete(*keys)
            
        except Exception as e:
            logger.error(f"Cache delete failed for keys {keys}: {e}")
            return 0
    
    async def exists(self, *keys: str) -> int:
        """
        Check if keys exist in cache.
        
        Args:
            keys: Cache keys to check
            
        Returns:
            Number of keys that exist
        """
        try:
            if not keys:
                return 0
                
            client = await self._get_client()
            return await client.exists(*keys)
            
        except Exception as e:
            logger.warning(f"Cache exists check failed for keys {keys}: {e}")
            return 0
    
    async def expire(self, key: str, seconds: int) -> bool:
        """
        Set expiration time for a key.
        
        Args:
            key: Cache key
            seconds: Expiration time in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            client = await self._get_client()
            return await client.expire(key, seconds)
            
        except Exception as e:
            logger.error(f"Cache expire failed for key {key}: {e}")
            return False
    
    async def ttl(self, key: str) -> int:
        """
        Get time to live for a key.
        
        Args:
            key: Cache key
            
        Returns:
            TTL in seconds (-1 if no expire, -2 if key doesn't exist)
        """
        try:
            client = await self._get_client()
            return await client.ttl(key)
            
        except Exception as e:
            logger.warning(f"Cache TTL check failed for key {key}: {e}")
            return -2
    
    async def keys(self, pattern: str = "*") -> List[str]:
        """
        Get keys matching pattern.
        
        Args:
            pattern: Key pattern (supports wildcards)
            
        Returns:
            List of matching keys
        """
        try:
            client = await self._get_client()
            return await client.keys(pattern)
            
        except Exception as e:
            logger.warning(f"Cache keys search failed for pattern {pattern}: {e}")
            return []
    
    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern.
        
        Args:
            pattern: Key pattern to match
            
        Returns:
            Number of keys deleted
        """
        try:
            matching_keys = await self.keys(pattern)
            if matching_keys:
                return await self.delete(*matching_keys)
            return 0
            
        except Exception as e:
            logger.error(f"Cache pattern delete failed for pattern {pattern}: {e}")
            return 0
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """
        Increment numeric value in cache.
        
        Args:
            key: Cache key
            amount: Amount to increment by
            
        Returns:
            New value after increment
        """
        try:
            client = await self._get_client()
            return await client.incrby(key, amount)
            
        except Exception as e:
            logger.error(f"Cache increment failed for key {key}: {e}")
            raise
    
    async def decrement(self, key: str, amount: int = 1) -> int:
        """
        Decrement numeric value in cache.
        
        Args:
            key: Cache key
            amount: Amount to decrement by
            
        Returns:
            New value after decrement
        """
        try:
            client = await self._get_client()
            return await client.decrby(key, amount)
            
        except Exception as e:
            logger.error(f"Cache decrement failed for key {key}: {e}")
            raise
    
    async def hash_get(self, key: str, field: str, default: Any = None) -> Any:
        """
        Get field value from hash.
        
        Args:
            key: Hash key
            field: Field name
            default: Default value if field not found
            
        Returns:
            Field value or default
        """
        try:
            client = await self._get_client()
            value = await client.hget(key, field)
            
            if value is None:
                return default
            
            # Try to deserialize JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
                
        except Exception as e:
            logger.warning(f"Cache hash get failed for {key}.{field}: {e}")
            return default
    
    async def hash_set(self, key: str, field: str, value: Any) -> bool:
        """
        Set field value in hash.
        
        Args:
            key: Hash key
            field: Field name
            value: Field value
            
        Returns:
            True if successful, False otherwise
        """
        try:
            client = await self._get_client()
            
            # Serialize value
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value, ensure_ascii=False, default=str)
            else:
                serialized_value = json.dumps(value) if value is not None else ""
            
            result = await client.hset(key, field, serialized_value)
            return bool(result)
            
        except Exception as e:
            logger.error(f"Cache hash set failed for {key}.{field}: {e}")
            return False
    
    async def hash_get_all(self, key: str) -> Dict[str, Any]:
        """
        Get all fields from hash.
        
        Args:
            key: Hash key
            
        Returns:
            Dictionary of field-value pairs
        """
        try:
            client = await self._get_client()
            hash_data = await client.hgetall(key)
            
            # Deserialize values
            result = {}
            for field, value in hash_data.items():
                try:
                    result[field] = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    result[field] = value
            
            return result
            
        except Exception as e:
            logger.warning(f"Cache hash get all failed for key {key}: {e}")
            return {}
    
    async def hash_delete(self, key: str, *fields: str) -> int:
        """
        Delete fields from hash.
        
        Args:
            key: Hash key
            fields: Field names to delete
            
        Returns:
            Number of fields deleted
        """
        try:
            if not fields:
                return 0
                
            client = await self._get_client()
            return await client.hdel(key, *fields)
            
        except Exception as e:
            logger.error(f"Cache hash delete failed for {key}: {e}")
            return 0
    
    async def list_push(self, key: str, *values: Any, left: bool = True) -> int:
        """
        Push values to list.
        
        Args:
            key: List key
            values: Values to push
            left: Push to left (True) or right (False)
            
        Returns:
            New length of list
        """
        try:
            if not values:
                return 0
                
            client = await self._get_client()
            
            # Serialize values
            serialized_values = []
            for value in values:
                if isinstance(value, (dict, list)):
                    serialized_values.append(json.dumps(value, ensure_ascii=False, default=str))
                else:
                    serialized_values.append(json.dumps(value))
            
            if left:
                return await client.lpush(key, *serialized_values)
            else:
                return await client.rpush(key, *serialized_values)
                
        except Exception as e:
            logger.error(f"Cache list push failed for key {key}: {e}")
            return 0
    
    async def list_pop(self, key: str, left: bool = True, default: Any = None) -> Any:
        """
        Pop value from list.
        
        Args:
            key: List key
            left: Pop from left (True) or right (False)
            default: Default value if list is empty
            
        Returns:
            Popped value or default
        """
        try:
            client = await self._get_client()
            
            if left:
                value = await client.lpop(key)
            else:
                value = await client.rpop(key)
            
            if value is None:
                return default
            
            # Deserialize value
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
                
        except Exception as e:
            logger.warning(f"Cache list pop failed for key {key}: {e}")
            return default
    
    async def list_range(self, key: str, start: int = 0, stop: int = -1) -> List[Any]:
        """
        Get range of values from list.
        
        Args:
            key: List key
            start: Start index
            stop: Stop index
            
        Returns:
            List of values
        """
        try:
            client = await self._get_client()
            values = await client.lrange(key, start, stop)
            
            # Deserialize values
            result = []
            for value in values:
                try:
                    result.append(json.loads(value))
                except (json.JSONDecodeError, TypeError):
                    result.append(value)
            
            return result
            
        except Exception as e:
            logger.warning(f"Cache list range failed for key {key}: {e}")
            return []
    
    async def list_length(self, key: str) -> int:
        """
        Get length of list.
        
        Args:
            key: List key
            
        Returns:
            Length of list
        """
        try:
            client = await self._get_client()
            return await client.llen(key)
            
        except Exception as e:
            logger.warning(f"Cache list length check failed for key {key}: {e}")
            return 0
    
    async def set_add(self, key: str, *values: Any) -> int:
        """
        Add values to set.
        
        Args:
            key: Set key
            values: Values to add
            
        Returns:
            Number of values added
        """
        try:
            if not values:
                return 0
                
            client = await self._get_client()
            
            # Serialize values
            serialized_values = []
            for value in values:
                if isinstance(value, (dict, list)):
                    serialized_values.append(json.dumps(value, ensure_ascii=False, default=str))
                else:
                    serialized_values.append(json.dumps(value))
            
            return await client.sadd(key, *serialized_values)
            
        except Exception as e:
            logger.error(f"Cache set add failed for key {key}: {e}")
            return 0
    
    async def set_remove(self, key: str, *values: Any) -> int:
        """
        Remove values from set.
        
        Args:
            key: Set key
            values: Values to remove
            
        Returns:
            Number of values removed
        """
        try:
            if not values:
                return 0
                
            client = await self._get_client()
            
            # Serialize values
            serialized_values = []
            for value in values:
                if isinstance(value, (dict, list)):
                    serialized_values.append(json.dumps(value, ensure_ascii=False, default=str))
                else:
                    serialized_values.append(json.dumps(value))
            
            return await client.srem(key, *serialized_values)
            
        except Exception as e:
            logger.error(f"Cache set remove failed for key {key}: {e}")
            return 0
    
    async def set_members(self, key: str) -> List[Any]:
        """
        Get all members of set.
        
        Args:
            key: Set key
            
        Returns:
            List of set members
        """
        try:
            client = await self._get_client()
            values = await client.smembers(key)
            
            # Deserialize values
            result = []
            for value in values:
                try:
                    result.append(json.loads(value))
                except (json.JSONDecodeError, TypeError):
                    result.append(value)
            
            return result
            
        except Exception as e:
            logger.warning(f"Cache set members failed for key {key}: {e}")
            return []
    
    async def set_is_member(self, key: str, value: Any) -> bool:
        """
        Check if value is member of set.
        
        Args:
            key: Set key
            value: Value to check
            
        Returns:
            True if value is member, False otherwise
        """
        try:
            client = await self._get_client()
            
            # Serialize value
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value, ensure_ascii=False, default=str)
            else:
                serialized_value = json.dumps(value)
            
            return await client.sismember(key, serialized_value)
            
        except Exception as e:
            logger.warning(f"Cache set member check failed for {key}: {e}")
            return False
    
    async def flush_all(self) -> bool:
        """
        Flush all keys from current database.
        
        Warning: This will delete ALL data in the current Redis database.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            client = await self._get_client()
            await client.flushdb()
            return True
            
        except Exception as e:
            logger.error(f"Cache flush all failed: {e}")
            return False
    
    async def ping(self) -> bool:
        """
        Ping Redis server to check connection.
        
        Returns:
            True if connection is healthy, False otherwise
        """
        try:
            client = await self._get_client()
            await client.ping()
            return True
            
        except Exception as e:
            logger.warning(f"Cache ping failed: {e}")
            return False
    
    async def info(self) -> Dict[str, Any]:
        """
        Get Redis server information.
        
        Returns:
            Dictionary containing server info
        """
        try:
            client = await self._get_client()
            return await client.info()
            
        except Exception as e:
            logger.warning(f"Cache info failed: {e}")
            return {}
    
    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis_client:
            await self._redis_client.close()
            self._redis_client = None


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


async def close_cache_manager() -> None:
    """Close global cache manager."""
    global _cache_manager
    if _cache_manager:
        await _cache_manager.close()
        _cache_manager = None