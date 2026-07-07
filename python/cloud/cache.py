# Niskala - Redis Cache Client
# Redis connection and caching utilities

import json
import pickle
from typing import Optional, Any, Dict, List
from datetime import timedelta
import logging

try:
    import redis.asyncio as aioredis
    HAS_REDIS_ASYNC = True
except ImportError:
    HAS_REDIS_ASYNC = False

try:
    import redis
    HAS_REDIS_SYNC = True
except ImportError:
    HAS_REDIS_SYNC = False

from .config import get_config

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis cache manager"""
    
    def __init__(self, url: Optional[str] = None):
        self.config = get_config()
        self.url = url or self.config.REDIS_URL
        self._client: Optional[Any] = None
        self._sync_client: Optional[Any] = None
        logger.info(f"RedisCache initialized: {self.url.split('@')[-1] if '@' in self.url else 'local'}")
    
    async def connect(self):
        """Connect to Redis"""
        if not HAS_REDIS_ASYNC:
            logger.warning("redis.asyncio not installed, using sync fallback")
            return
        
        try:
            self._client = aioredis.from_url(
                self.url,
                max_connections=20,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            # Test connection
            await self._client.ping()
            logger.info("Redis connected")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._client = None
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self._client:
            await self._client.close()
            logger.info("Redis disconnected")
    
    def _get_sync_client(self):
        """Get synchronous client (fallback)"""
        if not HAS_REDIS_SYNC:
            raise RuntimeError("redis not installed")
        
        if self._sync_client is None:
            self._sync_client = redis.from_url(self.url, decode_responses=True)
        
        return self._sync_client
    
    # String operations
    
    async def get(self, key: str) -> Optional[str]:
        """Get value by key"""
        if self._client:
            return await self._client.get(key)
        return self._get_sync_client().get(key)
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Set key-value pair"""
        if self._client:
            return await self._client.set(key, value, ex=ttl)
        return self._get_sync_client().set(key, value, ex=ttl)
    
    async def delete(self, key: str) -> bool:
        """Delete key"""
        if self._client:
            return await self._client.delete(key)
        return self._get_sync_client().delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if self._client:
            return await self._client.exists(key)
        return self._get_sync_client().exists(key)
    
    # JSON operations
    
    async def get_json(self, key: str) -> Optional[Any]:
        """Get JSON value"""
        value = await self.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def set_json(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set JSON value"""
        return await self.set(key, json.dumps(value), ttl)
    
    # Hash operations
    
    async def hget(self, name: str, key: str) -> Optional[str]:
        """Get hash field"""
        if self._client:
            return await self._client.hget(name, key)
        return self._get_sync_client().hget(name, key)
    
    async def hset(self, name: str, key: str, value: str) -> bool:
        """Set hash field"""
        if self._client:
            return await self._client.hset(name, key, value)
        return self._get_sync_client().hset(name, key, value)
    
    async def hgetall(self, name: str) -> Dict:
        """Get all hash fields"""
        if self._client:
            return await self._client.hgetall(name)
        return self._get_sync_client().hgetall(name)
    
    # List operations
    
    async def lpush(self, key: str, *values) -> int:
        """Push to list (left)"""
        if self._client:
            return await self._client.lpush(key, *values)
        return self._get_sync_client().lpush(key, *values)
    
    async def rpush(self, key: str, *values) -> int:
        """Push to list (right)"""
        if self._client:
            return await self._client.rpush(key, *values)
        return self._get_sync_client().rpush(key, *values)
    
    async def lrange(self, key: str, start: int, end: int) -> List:
        """Get list range"""
        if self._client:
            return await self._client.lrange(key, start, end)
        return self._get_sync_client().lrange(key, start, end)
    
    # Set operations
    
    async def sadd(self, key: str, *values) -> int:
        """Add to set"""
        if self._client:
            return await self._client.sadd(key, *values)
        return self._get_sync_client().sadd(key, *values)
    
    async def smembers(self, key: str) -> set:
        """Get set members"""
        if self._client:
            return await self._client.smembers(key)
        return self._get_sync_client().smembers(key)
    
    # Counter operations
    
    async def incr(self, key: str, amount: int = 1) -> int:
        """Increment counter"""
        if self._client:
            return await self._client.incr(key, amount)
        return self._get_sync_client().incr(key, amount)
    
    async def decr(self, key: str, amount: int = 1) -> int:
        """Decrement counter"""
        if self._client:
            return await self._client.decr(key, amount)
        return self._get_sync_client().decr(key, amount)
    
    # Pub/Sub
    
    async def publish(self, channel: str, message: str) -> int:
        """Publish message to channel"""
        if self._client:
            return await self._client.publish(channel, message)
        return self._get_sync_client().publish(channel, message)
    
    # Rate limiting
    
    async def check_rate_limit(self, key: str, limit: int, window: int) -> bool:
        """Check rate limit using sliding window
        
        Args:
            key: Rate limit key
            limit: Max requests per window
            window: Window in seconds
        
        Returns:
            True if allowed, False if rate limited
        """
        now = await self._client.time() if self._client else [0, 0]
        timestamp = now[0] + now[1] / 1_000_000
        
        pipe = self._client.pipeline() if self._client else None
        if pipe:
            pipe.zremrangebyscore(key, 0, timestamp - window)
            pipe.zadd(key, {str(timestamp): timestamp})
            pipe.zcard(key)
            pipe.expire(key, window)
            results = await pipe.execute()
            return results[2] <= limit
        else:
            # Sync fallback
            client = self._get_sync_client()
            pipe = client.pipeline()
            pipe.zremrangebyscore(key, 0, timestamp - window)
            pipe.zadd(key, {str(timestamp): timestamp})
            pipe.zcard(key)
            pipe.expire(key, window)
            results = pipe.execute()
            return results[2] <= limit
    
    # Cache helpers
    
    async def cache_get(self, key: str) -> Optional[Any]:
        """Get cached object"""
        data = await self.get(f"cache:{key}")
        if data:
            return pickle.loads(data.encode('latin-1'))
        return None
    
    async def cache_set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Cache object with TTL"""
        data = pickle.dumps(value).decode('latin-1')
        return await self.set(f"cache:{key}", data, ttl)
    
    async def cache_delete(self, key: str) -> bool:
        """Delete cached object"""
        return await self.delete(f"cache:{key}")
    
    async def flush_cache(self, pattern: str = "cache:*"):
        """Flush cache by pattern"""
        if self._client:
            keys = []
            async for key in self._client.scan_iter(match=pattern):
                keys.append(key)
            if keys:
                return await self._client.delete(*keys)
        return 0
    
    # Health check
    
    async def ping(self) -> bool:
        """Check Redis connection"""
        try:
            if self._client:
                return await self._client.ping()
            return self._get_sync_client().ping()
        except Exception:
            return False


# Singleton
_cache: Optional[RedisCache] = None


async def get_cache() -> RedisCache:
    """Get cache instance"""
    global _cache
    if _cache is None:
        _cache = RedisCache()
        await _cache.connect()
    return _cache


async def close_cache():
    """Close cache connection"""
    global _cache
    if _cache:
        await _cache.disconnect()
        _cache = None
