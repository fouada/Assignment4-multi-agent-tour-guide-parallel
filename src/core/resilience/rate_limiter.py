"""
Rate Limiter
============

Controls the rate of operations to prevent overload.
Implements multiple rate limiting algorithms.

Algorithms:
- Token Bucket: Smooth rate limiting with bursts
- Sliding Window: Time-based rate limiting
- Fixed Window: Simple count-based limiting

Academic Reference:
    - Tanenbaum, "Computer Networks" (Token Bucket, Leaky Bucket)
    - Google Cloud, "Rate Limiting Strategies"

Example:
    @rate_limit(max_calls=100, period=60)  # 100 calls per minute
    def call_api():
        return requests.get(api_url)
"""

from __future__ import annotations

import threading
import time
from collections import deque
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Deque, Dict, Optional, TypeVar
import logging

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded."""
    
    def __init__(
        self,
        message: str,
        limiter_name: str,
        retry_after: Optional[float] = None,
    ):
        super().__init__(message)
        self.limiter_name = limiter_name
        self.retry_after = retry_after


@dataclass
class RateLimiterStats:
    """Statistics for a rate limiter."""
    total_requests: int = 0
    allowed_requests: int = 0
    rejected_requests: int = 0
    
    @property
    def rejection_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.rejected_requests / self.total_requests


class TokenBucket:
    """
    Token Bucket rate limiter.
    
    Tokens are added at a fixed rate up to a maximum.
    Each request consumes one token.
    Allows bursts up to bucket capacity.
    
    Parameters:
        rate: Tokens added per second
        capacity: Maximum tokens in bucket
        
    Example:
        bucket = TokenBucket(rate=10, capacity=50)  # 10/s, burst of 50
        if bucket.acquire():
            make_request()
    """
    
    def __init__(self, rate: float, capacity: float):
        self.rate = rate
        self.capacity = capacity
        self._tokens = capacity
        self._last_update = time.time()
        self._lock = threading.Lock()
    
    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self._last_update
        self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
        self._last_update = now
    
    def acquire(self, tokens: float = 1.0) -> bool:
        """
        Try to acquire tokens.
        
        Returns True if tokens acquired, False otherwise.
        """
        with self._lock:
            self._refill()
            
            if self._tokens >= tokens:
                self._tokens -= tokens
                return True
            return False
    
    def wait_and_acquire(
        self,
        tokens: float = 1.0,
        timeout: Optional[float] = None,
    ) -> bool:
        """
        Wait until tokens are available, then acquire.
        
        Returns True if acquired within timeout, False otherwise.
        """
        start_time = time.time()
        
        while True:
            if self.acquire(tokens):
                return True
            
            # Check timeout
            if timeout is not None:
                elapsed = time.time() - start_time
                if elapsed >= timeout:
                    return False
            
            # Wait for tokens to refill
            wait_time = tokens / self.rate
            if timeout is not None:
                wait_time = min(wait_time, timeout - (time.time() - start_time))
            
            time.sleep(max(0.01, wait_time))
    
    @property
    def available_tokens(self) -> float:
        """Number of available tokens."""
        with self._lock:
            self._refill()
            return self._tokens


class SlidingWindowLimiter:
    """
    Sliding Window rate limiter.
    
    Tracks requests within a sliding time window.
    More accurate than fixed window but uses more memory.
    
    Parameters:
        max_requests: Maximum requests in window
        window_seconds: Window size in seconds
        
    Example:
        limiter = SlidingWindowLimiter(max_requests=100, window_seconds=60)
        if limiter.allow():
            make_request()
    """
    
    def __init__(self, max_requests: int, window_seconds: float):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._timestamps: Deque[float] = deque()
        self._lock = threading.Lock()
    
    def _cleanup(self) -> None:
        """Remove expired timestamps."""
        cutoff = time.time() - self.window_seconds
        while self._timestamps and self._timestamps[0] < cutoff:
            self._timestamps.popleft()
    
    def allow(self) -> bool:
        """Check if request is allowed."""
        with self._lock:
            self._cleanup()
            
            if len(self._timestamps) < self.max_requests:
                self._timestamps.append(time.time())
                return True
            return False
    
    @property
    def current_count(self) -> int:
        """Current request count in window."""
        with self._lock:
            self._cleanup()
            return len(self._timestamps)
    
    @property
    def time_until_next(self) -> Optional[float]:
        """Time until next request would be allowed."""
        with self._lock:
            self._cleanup()
            
            if len(self._timestamps) < self.max_requests:
                return 0.0
            
            oldest = self._timestamps[0]
            return max(0, oldest + self.window_seconds - time.time())


class RateLimiter:
    """
    General-purpose rate limiter with multiple algorithms.
    
    Parameters:
        name: Identifier for this limiter
        max_calls: Maximum calls in period
        period: Time period in seconds
        algorithm: "token_bucket" or "sliding_window"
        burst_size: For token bucket, burst capacity (None = max_calls)
        
    Example:
        limiter = RateLimiter(
            name="api",
            max_calls=100,
            period=60,
        )
        
        with limiter:
            make_api_call()
    """
    
    _registry: Dict[str, "RateLimiter"] = {}
    
    def __init__(
        self,
        name: str = "default",
        max_calls: int = 100,
        period: float = 60.0,
        algorithm: str = "token_bucket",
        burst_size: Optional[int] = None,
        block: bool = True,
        block_timeout: Optional[float] = None,
    ):
        self.name = name
        self.max_calls = max_calls
        self.period = period
        self.algorithm = algorithm
        self.block = block
        self.block_timeout = block_timeout
        
        # Create underlying limiter
        if algorithm == "token_bucket":
            rate = max_calls / period
            capacity = burst_size if burst_size is not None else max_calls
            self._limiter = TokenBucket(rate=rate, capacity=capacity)
        else:  # sliding_window
            self._limiter = SlidingWindowLimiter(
                max_requests=max_calls,
                window_seconds=period,
            )
        
        self.stats = RateLimiterStats()
        
        RateLimiter._registry[name] = self
    
    def acquire(self) -> bool:
        """
        Acquire permission for a request.
        
        Returns True if allowed, False if rejected.
        """
        self.stats.total_requests += 1
        
        if isinstance(self._limiter, TokenBucket):
            if self.block:
                allowed = self._limiter.wait_and_acquire(timeout=self.block_timeout)
            else:
                allowed = self._limiter.acquire()
        else:
            allowed = self._limiter.allow()
        
        if allowed:
            self.stats.allowed_requests += 1
        else:
            self.stats.rejected_requests += 1
        
        return allowed
    
    def __enter__(self) -> "RateLimiter":
        if not self.acquire():
            retry_after = None
            if isinstance(self._limiter, SlidingWindowLimiter):
                retry_after = self._limiter.time_until_next
            
            raise RateLimitExceeded(
                f"Rate limit exceeded for '{self.name}'",
                self.name,
                retry_after,
            )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        pass
    
    @classmethod
    def get(cls, name: str) -> Optional["RateLimiter"]:
        """Get a rate limiter by name."""
        return cls._registry.get(name)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics."""
        return {
            "name": self.name,
            "max_calls": self.max_calls,
            "period": self.period,
            "algorithm": self.algorithm,
            "total_requests": self.stats.total_requests,
            "allowed_requests": self.stats.allowed_requests,
            "rejected_requests": self.stats.rejected_requests,
            "rejection_rate": self.stats.rejection_rate,
        }


def rate_limit(
    max_calls: int = 100,
    period: float = 60.0,
    name: Optional[str] = None,
    algorithm: str = "token_bucket",
    block: bool = True,
    block_timeout: Optional[float] = None,
) -> Callable[[F], F]:
    """
    Decorator to rate limit a function.
    
    Args:
        max_calls: Maximum calls in period
        period: Time period in seconds
        name: Limiter name (defaults to function name)
        algorithm: "token_bucket" or "sliding_window"
        block: Wait for rate limit vs. raise immediately
        block_timeout: Maximum wait time
        
    Example:
        @rate_limit(max_calls=10, period=1)  # 10 calls per second
        def call_api():
            return requests.get(api_url)
    """
    def decorator(func: F) -> F:
        limiter_name = name or func.__name__
        limiter = RateLimiter(
            name=limiter_name,
            max_calls=max_calls,
            period=period,
            algorithm=algorithm,
            block=block,
            block_timeout=block_timeout,
        )
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            with limiter:
                return func(*args, **kwargs)
        
        wrapper.rate_limiter = limiter  # type: ignore
        return wrapper  # type: ignore
    
    return decorator

