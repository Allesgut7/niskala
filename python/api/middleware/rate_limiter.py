# Niskala - Rate Limiter Middleware
# Token bucket rate limiting

import time
from typing import Dict
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class TokenBucket:
    """Token bucket for rate limiting"""
    capacity: int
    tokens: int
    refill_rate: float  # tokens per second
    last_refill: float


class RateLimitMiddleware:
    """Rate limiting middleware"""
    
    def __init__(self, default_rate: int = 60, default_burst: int = 20):
        self.default_rate = default_rate
        self.default_burst = default_burst
        self.buckets: Dict[str, TokenBucket] = {}
        
        # Endpoint-specific rate limits
        self.rate_limits = {
            '/api/auth': {'rate': 10, 'burst': 5},
            '/api/trading/order': {'rate': 30, 'burst': 10},
            '/api/market': {'rate': 120, 'burst': 30},
            '/api/broker': {'rate': 30, 'burst': 10},
        }
    
    def check_rate_limit(self, client_id: str, endpoint: str = '') -> bool:
        """Check if request is allowed
        
        Args:
            client_id: Client identifier (IP or API key)
            endpoint: API endpoint
        
        Returns:
            True if request is allowed
        """
        now = time.time()
        
        # Get rate limit for endpoint
        limit_config = self.rate_limits.get(endpoint, {})
        rate = limit_config.get('rate', self.default_rate)
        burst = limit_config.get('burst', self.default_burst)
        
        if client_id not in self.buckets:
            self.buckets[client_id] = TokenBucket(
                capacity=burst,
                tokens=burst,
                refill_rate=rate / 60,  # Convert to per second
                last_refill=now,
            )
        
        bucket = self.buckets[client_id]
        
        # Refill tokens
        elapsed = now - bucket.last_refill
        bucket.tokens = min(
            bucket.capacity,
            bucket.tokens + elapsed * bucket.refill_rate
        )
        bucket.last_refill = now
        
        # Check if request allowed
        if bucket.tokens >= 1:
            bucket.tokens -= 1
            return True
        
        logger.warning(f"Rate limit exceeded for {client_id} on {endpoint}")
        return False
    
    def get_rate_limit_headers(self, client_id: str) -> Dict:
        """Get rate limit headers for response"""
        bucket = self.buckets.get(client_id)
        
        if not bucket:
            return {
                'X-RateLimit-Limit': str(self.default_burst),
                'X-RateLimit-Remaining': str(self.default_burst),
            }
        
        return {
            'X-RateLimit-Limit': str(bucket.capacity),
            'X-RateLimit-Remaining': str(int(bucket.tokens)),
        }
