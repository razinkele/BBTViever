"""
Simple caching utilities for the application
"""
import time
import hashlib
import json
from functools import wraps
from typing import Any, Optional, Dict
import logging

logger = logging.getLogger(__name__)


class SimpleCache:
    """Simple in-memory cache implementation"""
    
    def __init__(self, ttl: int = 3600):
        """
        Initialize cache
        
        Args:
            ttl: Time to live in seconds (default 1 hour)
        """
        self.cache: Dict[str, tuple] = {}
        self.ttl = ttl
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                self.hits += 1
                logger.debug(f"Cache hit for key: {key}")
                return value
            else:
                # Expired, remove from cache
                del self.cache[key]
                logger.debug(f"Cache expired for key: {key}")
        
        self.misses += 1
        return None
    
    def set(self, key: str, value: Any) -> None:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
        """
        self.cache[key] = (value, time.time())
        logger.debug(f"Cached value for key: {key}")
        
        # Simple cleanup - remove expired entries periodically
        if len(self.cache) > 1000:  # Arbitrary threshold
            self.cleanup()
    
    def delete(self, key: str) -> bool:
        """
        Delete entry from cache
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False if not found
        """
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Deleted cache key: {key}")
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def cleanup(self) -> None:
        """Remove expired entries from cache"""
        current_time = time.time()
        expired_keys = [
            key for key, (value, timestamp) in self.cache.items()
            if current_time - timestamp >= self.ttl
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache stats
        """
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'size': len(self.cache),
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': f"{hit_rate:.2f}%",
            'ttl': self.ttl
        }


# Global cache instance
_cache_instance = None


def get_cache(ttl: int = 3600) -> SimpleCache:
    """
    Get global cache instance (singleton pattern)
    
    Args:
        ttl: Time to live in seconds
        
    Returns:
        Cache instance
    """
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = SimpleCache(ttl)
    return _cache_instance


def cached(ttl: int = 3600, key_prefix: str = None):
    """
    Decorator for caching function results
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Optional prefix for cache keys
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key_parts = [key_prefix or func.__name__]
            
            # Add args to key (skip 'self' for methods)
            if args:
                start_idx = 1 if 'self' in func.__code__.co_varnames else 0
                cache_key_parts.extend(str(arg) for arg in args[start_idx:])
            
            # Add kwargs to key
            if kwargs:
                cache_key_parts.append(json.dumps(kwargs, sort_keys=True))
            
            # Create hash of key parts for consistent key
            cache_key = hashlib.md5(
                '|'.join(cache_key_parts).encode()
            ).hexdigest()
            
            # Try to get from cache
            cache = get_cache(ttl)
            cached_value = cache.get(cache_key)
            
            if cached_value is not None:
                return cached_value
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            
            return result
        
        # Add method to clear cache for this function
        wrapper.clear_cache = lambda: get_cache().clear()
        
        return wrapper
    return decorator


def cache_key_for_request(request) -> str:
    """
    Generate cache key for Flask request
    
    Args:
        request: Flask request object
        
    Returns:
        Cache key string
    """
    key_parts = [
        request.path,
        request.method,
        str(sorted(request.args.items()))
    ]
    
    return hashlib.md5('|'.join(key_parts).encode()).hexdigest()


class CacheManager:
    """Manager for different cache backends"""
    
    @staticmethod
    def get_cache_backend(config: dict) -> Any:
        """
        Get appropriate cache backend based on configuration
        
        Args:
            config: Application configuration
            
        Returns:
            Cache backend instance
        """
        cache_type = config.get('CACHE_TYPE', 'simple')
        
        if cache_type == 'simple':
            return SimpleCache(config.get('CACHE_DEFAULT_TIMEOUT', 3600))
        
        elif cache_type == 'redis':
            # Redis cache implementation
            try:
                import redis
                redis_url = config.get('CACHE_REDIS_URL', 'redis://localhost:6379/0')
                return redis.from_url(redis_url)
            except ImportError:
                logger.warning("Redis not installed, falling back to simple cache")
                return SimpleCache(config.get('CACHE_DEFAULT_TIMEOUT', 3600))
        
        elif cache_type == 'null':
            # Null cache for testing
            return NullCache()
        
        else:
            logger.warning(f"Unknown cache type: {cache_type}, using simple cache")
            return SimpleCache(config.get('CACHE_DEFAULT_TIMEOUT', 3600))


class NullCache:
    """Null cache implementation for testing"""
    
    def get(self, key: str) -> None:
        return None
    
    def set(self, key: str, value: Any) -> None:
        pass
    
    def delete(self, key: str) -> bool:
        return False
    
    def clear(self) -> None:
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'size': 0,
            'hits': 0,
            'misses': 0,
            'hit_rate': '0.00%',
            'ttl': 0
        }
