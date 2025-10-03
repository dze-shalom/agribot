"""
Redis Cache Service
Location: agribot/services/cache/redis_cache.py

Provides caching functionality for API responses, knowledge base queries,
and other data that benefits from caching to improve performance.
"""

import redis
import json
import pickle
from typing import Any, Optional, Union
from datetime import timedelta
from config.settings import CacheConfig
from utils.exceptions import APIServiceError

class RedisCache:
    """Redis-based caching service for AgriBot"""
    
    def __init__(self, config: CacheConfig = None):
        self.config = config or CacheConfig()
        self._client = None
        
        if self.config.enabled:
            self._connect()
    
    def _connect(self):
        """Initialize Redis connection"""
        try:
            self._client = redis.from_url(
                self.config.url,
                decode_responses=False,  # We'll handle encoding ourselves
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            self._client.ping()
        except Exception as e:
            raise APIServiceError(
                "Redis", 
                f"Failed to connect to Redis cache: {str(e)}"
            )
    
    def _make_key(self, key: str) -> str:
        """Create prefixed cache key"""
        return f"{self.config.key_prefix}{key}"
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        if not self.config.enabled or not self._client:
            return default
        
        try:
            cache_key = self._make_key(key)
            value = self._client.get(cache_key)
            
            if value is None:
                return default
            
            # Try to deserialize as JSON first, then pickle
            try:
                return json.loads(value.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                return pickle.loads(value)
                
        except Exception as e:
            # Log error but don't fail - return default
            print(f"Cache get error for key {key}: {str(e)}")
            return default
    
    def set(self, key: str, value: Any, timeout: int = None) -> bool:
        """Set value in cache with optional timeout"""
        if not self.config.enabled or not self._client:
            return False
        
        try:
            cache_key = self._make_key(key)
            timeout = timeout or self.config.default_timeout
            
            # Try to serialize as JSON first, then pickle
            try:
                serialized_value = json.dumps(value, default=str)
            except TypeError:
                serialized_value = pickle.dumps(value)
            
            return self._client.setex(cache_key, timeout, serialized_value)
            
        except Exception as e:
            print(f"Cache set error for key {key}: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.config.enabled or not self._client:
            return False
        
        try:
            cache_key = self._make_key(key)
            return bool(self._client.delete(cache_key))
        except Exception as e:
            print(f"Cache delete error for key {key}: {str(e)}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.config.enabled or not self._client:
            return False
        
        try:
            cache_key = self._make_key(key)
            return bool(self._client.exists(cache_key))
        except Exception as e:
            print(f"Cache exists error for key {key}: {str(e)}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not self.config.enabled or not self._client:
            return 0
        
        try:
            cache_pattern = self._make_key(pattern)
            keys = self._client.keys(cache_pattern)
            if keys:
                return self._client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache clear pattern error for pattern {pattern}: {str(e)}")
            return 0
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        if not self.config.enabled or not self._client:
            return {"enabled": False}
        
        try:
            info = self._client.info()
            return {
                "enabled": True,
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "total_commands_processed": info.get("total_commands_processed", 0)
            }
        except Exception as e:
            return {"enabled": True, "error": str(e)}

# Cache decorators for common use cases
def cached(timeout: int = None, key_prefix: str = ""):
    """Decorator to cache function results"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache = RedisCache()
            
            # Create cache key from function name and arguments
            key_parts = [key_prefix, func.__name__]
            if args:
                key_parts.extend(str(arg) for arg in args)
            if kwargs:
                key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            
            cache_key = ":".join(key_parts)
            
            # Try to get from cache first
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result
        
        return wrapper
    return decorator
def cache_user_session(user_id: int, user_data: dict, timeout: int = 3600):
    """Cache user session data - add this to your existing class"""
    cache = RedisCache()
    key = f"session:{user_id}"
    return cache.set(key, user_data, timeout)

def get_cached_session(user_id: int) -> Optional[dict]:
    """Get cached user session - add this to your existing class"""
    cache = RedisCache()
    key = f"session:{user_id}"
    return cache.get(key)

def clear_user_session(user_id: int):
    """Clear user session from cache - add this to your existing class"""
    cache = RedisCache()
    key = f"session:{user_id}"
    return cache.delete(key)