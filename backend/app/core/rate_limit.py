"""
Rate Limiting Middleware
Token bucket algorithm for request rate limiting with Redis backend.
"""
import time
from typing import Optional, Dict, Tuple
from collections import defaultdict
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from .config import get_settings
from .auth import token_manager

settings = get_settings()


class RateLimiter:
    """
    Token bucket rate limiter with in-memory fallback.
    Uses Redis if available, otherwise falls back to in-memory storage.
    """

    def __init__(self):
        self.requests_per_window = settings.rate_limit_requests
        self.window_seconds = settings.rate_limit_window_seconds
        self.burst = settings.rate_limit_burst
        self._memory_store: Dict[str, Tuple[float, int]] = {}  # key -> (last_refill, tokens)
        self._redis_client = None
        self._init_redis()

    def _init_redis(self):
        """Initialize Redis connection if available."""
        try:
            import redis
            self._redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            self._redis_client.ping()
        except Exception:
            self._redis_client = None

    def _get_redis_key(self, identifier: str) -> str:
        return f"ratelimit:{identifier}"

    def _refill_tokens(self, last_refill: float, tokens: int) -> Tuple[float, int]:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - last_refill
        new_tokens = min(self.burst, tokens + int(elapsed * self.requests_per_window / self.window_seconds))
        return now, new_tokens

    async def check_rate_limit(self, identifier: str, cost: int = 1) -> Tuple[bool, Dict[str, int]]:
        """
        Check if request is within rate limit.

        Returns:
            Tuple of (allowed, headers_dict)
        """
        if not settings.rate_limit_enabled:
            return True, {}

        key = self._get_redis_key(identifier)
        now = time.time()

        if self._redis_client:
            return await self._check_redis(key, cost, now)
        else:
            return self._check_memory(key, cost, now)

    async def _check_redis(self, key: str, cost: int, now: float) -> Tuple[bool, Dict[str, int]]:
        """Check rate limit using Redis."""
        try:
            pipe = self._redis_client.pipeline()

            # Get current state
            pipe.hmget(key, "tokens", "last_refill")
            results = pipe.execute()

            tokens_str, last_refill_str = results[0]
            tokens = float(tokens_str) if tokens_str else self.burst
            last_refill = float(last_refill_str) if last_refill_str else now

            # Refill
            last_refill, tokens = self._refill_tokens(last_refill, tokens)

            allowed = tokens >= cost
            if allowed:
                tokens -= cost

            # Save state
            pipe.hmset(key, {"tokens": tokens, "last_refill": last_refill})
            pipe.expire(key, self.window_seconds * 2)
            pipe.execute()

            remaining = int(tokens)
            reset = int(last_refill + self.window_seconds)

            headers = {
                "X-RateLimit-Limit": str(self.requests_per_window),
                "X-RateLimit-Remaining": str(max(0, remaining)),
                "X-RateLimit-Reset": str(reset),
            }

            return allowed, headers

        except Exception:
            # Fallback to memory on Redis error
            return self._check_memory(key, cost, now)

    def _check_memory(self, key: str, cost: int, now: float) -> Tuple[bool, Dict[str, int]]:
        """Check rate limit using in-memory store."""
        tokens, last_refill = self._memory_store.get(key, (self.burst, now))
        last_refill, tokens = self._refill_tokens(last_refill, tokens)

        allowed = tokens >= cost
        if allowed:
            tokens -= cost

        self._memory_store[key] = (last_refill, tokens)

        # Cleanup old entries periodically
        if len(self._memory_store) > 10000:
            self._cleanup_memory(now)

        remaining = int(tokens)
        reset = int(last_refill + self.window_seconds)

        headers = {
            "X-RateLimit-Limit": str(self.requests_per_window),
            "X-RateLimit-Remaining": str(max(0, remaining)),
            "X-RateLimit-Reset": str(reset),
        }

        return allowed, headers

    def _cleanup_memory(self, now: float):
        """Remove expired entries from memory store."""
        cutoff = now - self.window_seconds * 2
        self._memory_store = {
            k: v for k, v in self._memory_store.items()
            if v[0] > cutoff
        }


# Global rate limiter instance
rate_limiter = RateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for rate limiting."""

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/metrics"]:
            return await call_next(request)

        # Get identifier (IP + user if authenticated)
        client_ip = request.client.host if request.client else "unknown"
        user_id = getattr(request.state, "user_id", None)
        identifier = f"{user_id}:{client_ip}" if user_id else client_ip

        # Check rate limit
        allowed, headers = await rate_limiter.check_rate_limit(identifier)

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers=headers,
            )

        response = await call_next(request)

        # Add rate limit headers to response
        for key, value in headers.items():
            response.headers[key] = value

        return response


def get_client_identifier(request: Request) -> str:
    """Extract client identifier for rate limiting."""
    client_ip = request.client.host if request.client else "unknown"
    # Check for forwarded headers (when behind proxy)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
    return client_ip