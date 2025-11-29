"""
Resilience Patterns
===================

Production-grade resilience patterns for fault-tolerant systems.
Implements patterns from the stability patterns literature.

Patterns Included:
- Circuit Breaker: Fail fast when service is unhealthy
- Retry with Backoff: Exponential retry with jitter
- Timeout: Bounded execution time
- Bulkhead: Resource isolation
- Fallback: Graceful degradation
- Rate Limiter: Request throttling

Academic Reference:
    - Nygard, "Release It!" (Stability Patterns)
    - Netflix, "Hystrix" (Circuit Breaker implementation)
    - Microsoft, "Cloud Design Patterns" (Retry, Circuit Breaker)

Example:
    # Using decorators
    @circuit_breaker(failure_threshold=5, reset_timeout=30)
    @retry(max_attempts=3, backoff_factor=2)
    @timeout(seconds=10)
    def call_external_api():
        return requests.get("https://api.example.com")
"""

from src.core.resilience.circuit_breaker import (
    CircuitBreaker,
    CircuitState,
    CircuitBreakerOpen,
    circuit_breaker,
)
from src.core.resilience.retry import (
    RetryPolicy,
    RetryError,
    retry,
    with_retry,
)
from src.core.resilience.timeout import (
    TimeoutError,
    timeout,
    with_timeout,
)
from src.core.resilience.bulkhead import (
    Bulkhead,
    BulkheadFull,
    bulkhead,
)
from src.core.resilience.fallback import (
    Fallback,
    fallback,
)
from src.core.resilience.rate_limiter import (
    RateLimiter,
    RateLimitExceeded,
    rate_limit,
    TokenBucket,
)

__all__ = [
    # Circuit Breaker
    "CircuitBreaker",
    "CircuitState",
    "CircuitBreakerOpen",
    "circuit_breaker",
    # Retry
    "RetryPolicy",
    "RetryError",
    "retry",
    "with_retry",
    # Timeout
    "TimeoutError",
    "timeout",
    "with_timeout",
    # Bulkhead
    "Bulkhead",
    "BulkheadFull",
    "bulkhead",
    # Fallback
    "Fallback",
    "fallback",
    # Rate Limiter
    "RateLimiter",
    "RateLimitExceeded",
    "rate_limit",
    "TokenBucket",
]

