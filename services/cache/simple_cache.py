"""
Simple In-Memory Cache
Fallback cache when Redis is not available
"""
from datetime import datetime, timedelta
from typing import Any, Optional
import threading

class SimpleCache:
    """Thread-safe in-memory cache for when Redis is unavailable"""

    def __init__(self):
        self._cache = {}
        self._timeouts = {}
        self._lock = threading.Lock()

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        with self._lock:
            # Check if key exists and hasn't expired
            if key in self._cache:
                if key in self._timeouts:
                    if datetime.now() > self._timeouts[key]:
                        # Expired, remove it
                        del self._cache[key]
                        del self._timeouts[key]
                        return default
                return self._cache[key]
            return default

    def set(self, key: str, value: Any, timeout: int = 300) -> bool:
        """Set value in cache with timeout in seconds"""
        with self._lock:
            try:
                self._cache[key] = value
                if timeout:
                    self._timeouts[key] = datetime.now() + timedelta(seconds=timeout)
                return True
            except Exception:
                return False

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        with self._lock:
            try:
                if key in self._cache:
                    del self._cache[key]
                if key in self._timeouts:
                    del self._timeouts[key]
                return True
            except Exception:
                return False

    def clear(self):
        """Clear all cached data"""
        with self._lock:
            self._cache.clear()
            self._timeouts.clear()

    def cleanup_expired(self):
        """Remove all expired entries"""
        with self._lock:
            now = datetime.now()
            expired_keys = [
                key for key, expiry in self._timeouts.items()
                if now > expiry
            ]
            for key in expired_keys:
                if key in self._cache:
                    del self._cache[key]
                del self._timeouts[key]

# Global cache instance
_cache_instance = None

def get_cache():
    """Get cache instance (tries Redis first, falls back to SimpleCache)"""
    global _cache_instance

    if _cache_instance is None:
        try:
            # Try to use Redis cache
            from services.cache.redis_cache import RedisCache
            from config.settings import CacheConfig
            config = CacheConfig()
            if config.enabled:
                _cache_instance = RedisCache(config)
                print("Using Redis cache")
            else:
                raise Exception("Redis not enabled")
        except Exception as e:
            # Fall back to simple in-memory cache
            print(f"Redis unavailable ({str(e)}), using in-memory cache")
            _cache_instance = SimpleCache()

    return _cache_instance

# Singleton instance for easy import
cache = get_cache()

# Helper functions for compatibility
def cache_user_session(user_id: int, user_data: dict, timeout: int = 3600):
    """Cache user session data"""
    key = f"session:{user_id}"
    return cache.set(key, user_data, timeout)

def get_cached_session(user_id: int):
    """Get cached user session"""
    key = f"session:{user_id}"
    return cache.get(key)

def clear_user_session(user_id: int):
    """Clear user session from cache"""
    key = f"session:{user_id}"
    return cache.delete(key)
