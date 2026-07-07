# Niskala - Performance Optimization Utilities
# Version: 1.0.0

import time
import functools
import logging
from typing import Dict, Optional, Any
from collections import OrderedDict
import threading


class LRUCache:
    """Thread-safe LRU cache for data caching"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 300):
        """Initialize cache
        
        Args:
            max_size: Maximum number of cached items
            ttl: Time-to-live in seconds
        """
        self.max_size = max_size
        self.ttl = ttl
        self._cache: OrderedDict = OrderedDict()
        self._timestamps: Dict[str, float] = {}
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None
            
            # Check TTL
            if self._is_expired(key):
                self._remove(key)
                self._misses += 1
                return None
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            self._hits += 1
            
            return self._cache[key]
    
    def put(self, key: str, value: Any):
        """Put item in cache
        
        Args:
            key: Cache key
            value: Value to cache
        """
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            else:
                if len(self._cache) >= self.max_size:
                    # Remove oldest
                    oldest = next(iter(self._cache))
                    self._remove(oldest)
            
            self._cache[key] = value
            self._timestamps[key] = time.time()
    
    def remove(self, key: str):
        """Remove item from cache"""
        with self._lock:
            self._remove(key)
    
    def clear(self):
        """Clear all cached items"""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()
    
    def _remove(self, key: str):
        """Internal remove (must hold lock)"""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)
    
    def _is_expired(self, key: str) -> bool:
        """Check if item is expired"""
        if key not in self._timestamps:
            return True
        return (time.time() - self._timestamps[key]) > self.ttl
    
    @property
    def size(self) -> int:
        """Current cache size"""
        return len(self._cache)
    
    @property
    def hit_rate(self) -> float:
        """Cache hit rate"""
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0
    
    def stats(self) -> Dict:
        """Get cache statistics"""
        return {
            'size': self.size,
            'max_size': self.max_size,
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': self.hit_rate,
            'ttl': self.ttl
        }


class DataCache:
    """Specialized cache for market data"""
    
    def __init__(self):
        self._quote_cache = LRUCache(max_size=500, ttl=5)      # 5s for quotes
        self._history_cache = LRUCache(max_size=100, ttl=300)   # 5m for history
        self._fundamental_cache = LRUCache(max_size=200, ttl=3600)  # 1h for fundamentals
        self._news_cache = LRUCache(max_size=100, ttl=60)       # 1m for news
    
    def get_quote(self, symbol: str) -> Optional[Dict]:
        """Get cached quote"""
        return self._quote_cache.get(f"quote:{symbol}")
    
    def put_quote(self, symbol: str, data: Dict):
        """Cache quote"""
        self._quote_cache.put(f"quote:{symbol}", data)
    
    def get_history(self, symbol: str, period: str) -> Optional[Any]:
        """Get cached history"""
        return self._history_cache.get(f"history:{symbol}:{period}")
    
    def put_history(self, symbol: str, period: str, data: Any):
        """Cache history"""
        self._history_cache.put(f"history:{symbol}:{period}", data)
    
    def get_fundamental(self, symbol: str) -> Optional[Dict]:
        """Get cached fundamental data"""
        return self._fundamental_cache.get(f"fund:{symbol}")
    
    def put_fundamental(self, symbol: str, data: Dict):
        """Cache fundamental data"""
        self._fundamental_cache.put(f"fund:{symbol}", data)
    
    def get_news(self, source: str) -> Optional[list]:
        """Get cached news"""
        return self._news_cache.get(f"news:{source}")
    
    def put_news(self, source: str, data: list):
        """Cache news"""
        self._news_cache.put(f"news:{source}", data)
    
    def clear_all(self):
        """Clear all caches"""
        self._quote_cache.clear()
        self._history_cache.clear()
        self._fundamental_cache.clear()
        self._news_cache.clear()
    
    def stats(self) -> Dict:
        """Get all cache statistics"""
        return {
            'quote': self._quote_cache.stats(),
            'history': self._history_cache.stats(),
            'fundamental': self._fundamental_cache.stats(),
            'news': self._news_cache.stats()
        }


def cached(cache: LRUCache, key_func=None):
    """Decorator for caching function results
    
    Args:
        cache: LRUCache instance
        key_func: Function to generate cache key from args
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = f"{func.__name__}:{args}:{kwargs}"
            
            # Check cache
            result = cache.get(key)
            if result is not None:
                return result
            
            # Compute and cache
            result = func(*args, **kwargs)
            cache.put(key, result)
            
            return result
        return wrapper
    return decorator


class RateLimiter:
    """Rate limiter for API calls"""
    
    def __init__(self, max_calls: int, period: float):
        """Initialize rate limiter
        
        Args:
            max_calls: Maximum calls in period
            period: Time period in seconds
        """
        self.max_calls = max_calls
        self.period = period
        self._calls: list = []
        self._lock = threading.Lock()
    
    def acquire(self) -> bool:
        """Try to acquire a rate limit slot
        
        Returns:
            True if acquired, False if rate limited
        """
        with self._lock:
            now = time.time()
            
            # Remove old calls
            self._calls = [t for t in self._calls if now - t < self.period]
            
            if len(self._calls) < self.max_calls:
                self._calls.append(now)
                return True
            
            return False
    
    def wait(self):
        """Wait until a slot is available"""
        while not self.acquire():
            time.sleep(0.1)
    
    @property
    def remaining(self) -> int:
        """Remaining calls in current period"""
        with self._lock:
            now = time.time()
            self._calls = [t for t in self._calls if now - t < self.period]
            return self.max_calls - len(self._calls)


class BatchProcessor:
    """Process items in batches for efficiency"""
    
    def __init__(self, batch_size: int = 50, flush_interval: float = 1.0):
        """Initialize batch processor
        
        Args:
            batch_size: Items per batch
            flush_interval: Max time between flushes
        """
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self._buffer: list = []
        self._last_flush = time.time()
        self._lock = threading.Lock()
        self._processor: Optional[callable] = None
    
    def set_processor(self, processor: callable):
        """Set batch processor function"""
        self._processor = processor
    
    def add(self, item: Any):
        """Add item to batch buffer"""
        with self._lock:
            self._buffer.append(item)
            
            # Check if should flush
            if (len(self._buffer) >= self.batch_size or
                time.time() - self._last_flush >= self.flush_interval):
                self._flush()
    
    def _flush(self):
        """Flush buffer to processor"""
        if not self._buffer or not self._processor:
            return
        
        batch = self._buffer.copy()
        self._buffer.clear()
        self._last_flush = time.time()
        
        try:
            self._processor(batch)
        except Exception as e:
            logging.error(f"Batch processor error: {e}")


# Global instances
data_cache = DataCache()

# Rate limiters for external APIs
yfinance_limiter = RateLimiter(max_calls=100, period=60)  # 100/min
news_limiter = RateLimiter(max_calls=30, period=60)       # 30/min


# Test
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Test LRU Cache
    print("=== LRU Cache Test ===")
    cache = LRUCache(max_size=5, ttl=2)
    
    cache.put('a', 1)
    cache.put('b', 2)
    cache.put('c', 3)
    
    print(f"Get 'a': {cache.get('a')}")
    print(f"Get 'b': {cache.get('b')}")
    print(f"Size: {cache.size}")
    print(f"Hit rate: {cache.hit_rate:.2%}")
    
    # Test Data Cache
    print("\n=== Data Cache Test ===")
    dc = DataCache()
    
    dc.put_quote('BBCA', {'price': 9100, 'change': 0.5})
    dc.put_quote('BBRI', {'price': 4850, 'change': 1.2})
    
    print(f"Get BBCA: {dc.get_quote('BBCA')}")
    print(f"Get BBRI: {dc.get_quote('BBRI')}")
    print(f"Stats: {dc.stats()}")
    
    # Test Rate Limiter
    print("\n=== Rate Limiter Test ===")
    limiter = RateLimiter(max_calls=3, period=1.0)
    
    for i in range(5):
        acquired = limiter.acquire()
        print(f"Call {i+1}: {'OK' if acquired else 'RATE LIMITED'}")
    
    print(f"Remaining: {limiter.remaining}")
