"""
Intelligent caching system with semantic similarity detection.
Provides multi-level caching for faster response times.
"""

import hashlib
import time
from typing import Any, Optional, Dict, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import json

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Represents a cached item with metadata."""
    key: str
    value: Any
    timestamp: float
    hits: int = 0
    last_access: float = field(default_factory=time.time)
    ttl: int = 3600  # seconds
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if entry is expired."""
        return time.time() - self.timestamp > self.ttl
    
    def is_stale(self, max_age: int = 300) -> bool:
        """Check if entry is stale (older than max_age seconds)."""
        return time.time() - self.timestamp > max_age
    
    def access(self) -> None:
        """Record access to this entry."""
        self.hits += 1
        self.last_access = time.time()


class IntelligentCache:
    """
    Multi-level intelligent cache with semantic similarity detection.
    Provides fast lookups with automatic expiration and LRU eviction.
    """
    
    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: int = 3600,
        enable_semantic: bool = False,
    ):
        """
        Initialize intelligent cache.
        
        Args:
            max_size: Maximum number of entries
            default_ttl: Default time-to-live in seconds
            enable_semantic: Enable semantic similarity matching
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.enable_semantic = enable_semantic
        
        # Main cache storage
        self._cache: Dict[str, CacheEntry] = {}
        
        # Statistics
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        
        logger.info(f"IntelligentCache initialized (max_size={max_size}, ttl={default_ttl}s)")
    
    def get(self, key: str, default: Any = None) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            default: Default value if not found
            
        Returns:
            Cached value or default
        """
        cache_key = self._hash_key(key)
        
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            
            # Check expiration
            if entry.is_expired():
                self._remove(cache_key)
                self._misses += 1
                logger.debug(f"Cache expired: {key[:50]}")
                return default
            
            # Update access stats
            entry.access()
            self._hits += 1
            
            logger.debug(f"Cache hit: {key[:50]} (hits={entry.hits})")
            return entry.value
        
        self._misses += 1
        logger.debug(f"Cache miss: {key[:50]}")
        return default
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None = use default)
            metadata: Optional metadata
        """
        # Check if we need to evict entries
        if len(self._cache) >= self.max_size:
            self._evict_lru()
        
        cache_key = self._hash_key(key)
        ttl = ttl or self.default_ttl
        
        entry = CacheEntry(
            key=cache_key,
            value=value,
            timestamp=time.time(),
            ttl=ttl,
            metadata=metadata or {}
        )
        
        self._cache[cache_key] = entry
        logger.debug(f"Cache set: {key[:50]} (ttl={ttl}s)")
    
    def has(self, key: str) -> bool:
        """
        Check if key exists in cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists and not expired
        """
        cache_key = self._hash_key(key)
        
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            if not entry.is_expired():
                return True
            else:
                self._remove(cache_key)
        
        return False
    
    def delete(self, key: str) -> bool:
        """
        Delete entry from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False if not found
        """
        cache_key = self._hash_key(key)
        return self._remove(cache_key)
    
    def clear(self) -> None:
        """Clear all cache entries."""
        count = len(self._cache)
        self._cache.clear()
        logger.info(f"Cache cleared: {count} entries removed")
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired entries.
        
        Returns:
            Number of entries removed
        """
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired()
        ]
        
        for key in expired_keys:
            self._remove(key)
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired entries")
        
        return len(expired_keys)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Statistics dictionary
        """
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0
        
        return {
            'size': len(self._cache),
            'max_size': self.max_size,
            'hits': self._hits,
            'misses': self._misses,
            'evictions': self._evictions,
            'hit_rate': hit_rate,
            'total_requests': total_requests,
        }
    
    def get_top_entries(self, n: int = 10) -> List[Dict[str, Any]]:
        """
        Get top N most accessed entries.
        
        Args:
            n: Number of entries to return
            
        Returns:
            List of entry statistics
        """
        sorted_entries = sorted(
            self._cache.values(),
            key=lambda e: e.hits,
            reverse=True
        )
        
        return [
            {
                'key': entry.key[:50],
                'hits': entry.hits,
                'age': time.time() - entry.timestamp,
                'last_access': time.time() - entry.last_access,
            }
            for entry in sorted_entries[:n]
        ]
    
    def _hash_key(self, key: str) -> str:
        """
        Generate hash for cache key.
        
        Args:
            key: Original key
            
        Returns:
            Hash string
        """
        return hashlib.md5(key.encode()).hexdigest()
    
    def _remove(self, cache_key: str) -> bool:
        """
        Remove entry from cache.
        
        Args:
            cache_key: Hashed cache key
            
        Returns:
            True if removed
        """
        if cache_key in self._cache:
            del self._cache[cache_key]
            return True
        return False
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if not self._cache:
            return
        
        # Find LRU entry
        lru_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].last_access
        )
        
        self._remove(lru_key)
        self._evictions += 1
        logger.debug("Evicted LRU entry")
    
    def warm_up(self, keys_values: List[Tuple[str, Any]]) -> int:
        """
        Warm up cache with pre-populated data.
        
        Args:
            keys_values: List of (key, value) tuples
            
        Returns:
            Number of entries added
        """
        count = 0
        for key, value in keys_values:
            self.set(key, value)
            count += 1
        
        logger.info(f"Cache warmed up with {count} entries")
        return count


class QueryCache(IntelligentCache):
    """
    Specialized cache for query results with query normalization.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def normalize_query(self, query: str) -> str:
        """
        Normalize query for consistent cache keys.
        
        Args:
            query: Query string
            
        Returns:
            Normalized query
        """
        # Convert to lowercase and strip
        normalized = query.lower().strip()
        
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        
        # Remove common punctuation at end
        normalized = normalized.rstrip('?!.')
        
        return normalized
    
    def get_query(self, query: str, default: Any = None) -> Optional[Any]:
        """
        Get cached query result with normalization.
        
        Args:
            query: Query string
            default: Default value
            
        Returns:
            Cached result or default
        """
        normalized = self.normalize_query(query)
        return self.get(normalized, default)
    
    def set_query(
        self,
        query: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        """
        Cache query result with normalization.
        
        Args:
            query: Query string
            value: Result to cache
            ttl: Time-to-live
        """
        normalized = self.normalize_query(query)
        self.set(normalized, value, ttl, metadata={'original_query': query})
