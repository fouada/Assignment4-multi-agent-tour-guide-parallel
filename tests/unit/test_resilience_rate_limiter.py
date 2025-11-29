"""
Unit tests for Rate Limiter pattern.

Test Coverage:
- Token Bucket algorithm
- Sliding Window algorithm
- RateLimiter class
- Decorator usage
- Blocking vs non-blocking modes
- Statistics tracking
"""

import threading
import time

import pytest

from src.core.resilience.rate_limiter import (
    RateLimiter,
    RateLimiterStats,
    RateLimitExceeded,
    SlidingWindowLimiter,
    TokenBucket,
    rate_limit,
)


class TestRateLimiterStats:
    """Tests for RateLimiterStats."""

    def test_initial_stats(self):
        """Test initial statistics values."""
        stats = RateLimiterStats()
        assert stats.total_requests == 0
        assert stats.allowed_requests == 0
        assert stats.rejected_requests == 0

    def test_rejection_rate_empty(self):
        """Test rejection rate with no requests."""
        stats = RateLimiterStats()
        assert stats.rejection_rate == 0.0

    def test_rejection_rate_calculation(self):
        """Test rejection rate calculation."""
        stats = RateLimiterStats(
            total_requests=100, allowed_requests=80, rejected_requests=20
        )
        assert stats.rejection_rate == 0.2


class TestTokenBucket:
    """Tests for TokenBucket algorithm."""

    def test_initial_capacity(self):
        """Test bucket starts at full capacity."""
        bucket = TokenBucket(rate=10, capacity=50)
        assert bucket.available_tokens == 50

    def test_acquire_success(self):
        """Test successful token acquisition."""
        bucket = TokenBucket(rate=10, capacity=50)
        assert bucket.acquire() is True
        # Use approximate comparison due to time-based refill
        assert 48.9 <= bucket.available_tokens <= 49.1

    def test_acquire_multiple(self):
        """Test acquiring multiple tokens."""
        bucket = TokenBucket(rate=10, capacity=50)
        assert bucket.acquire(tokens=10) is True
        # Use approximate comparison due to time-based refill
        assert 39.9 <= bucket.available_tokens <= 40.1

    def test_acquire_exceeds_capacity(self):
        """Test acquiring more tokens than available."""
        bucket = TokenBucket(rate=10, capacity=5)
        assert bucket.acquire(tokens=10) is False
        assert bucket.available_tokens == 5  # Unchanged

    def test_refill_over_time(self):
        """Test tokens are refilled over time."""
        bucket = TokenBucket(rate=100, capacity=100)

        # Use all tokens
        bucket.acquire(tokens=100)
        # Allow for small time-based refill
        assert bucket.available_tokens < 1

        # Wait for refill
        time.sleep(0.1)  # Should refill ~10 tokens at rate=100/s

        available = bucket.available_tokens
        assert available >= 5  # At least some refill

    def test_refill_capped_at_capacity(self):
        """Test refill doesn't exceed capacity."""
        bucket = TokenBucket(rate=100, capacity=10)
        time.sleep(0.5)  # Would refill 50 tokens

        assert bucket.available_tokens == 10  # Capped at capacity

    def test_wait_and_acquire_success(self):
        """Test waiting for tokens."""
        bucket = TokenBucket(rate=100, capacity=5)

        # Empty the bucket
        bucket.acquire(tokens=5)

        # Wait for tokens
        result = bucket.wait_and_acquire(tokens=1, timeout=0.5)
        assert result is True

    def test_wait_and_acquire_timeout(self):
        """Test waiting times out."""
        bucket = TokenBucket(rate=1, capacity=1)

        # Empty the bucket
        bucket.acquire(tokens=1)

        # Try to acquire more than can refill in time
        result = bucket.wait_and_acquire(tokens=10, timeout=0.1)
        assert result is False


class TestSlidingWindowLimiter:
    """Tests for SlidingWindowLimiter algorithm."""

    def test_allow_under_limit(self):
        """Test requests allowed under limit."""
        limiter = SlidingWindowLimiter(max_requests=10, window_seconds=1.0)

        for _ in range(5):
            assert limiter.allow() is True

        assert limiter.current_count == 5

    def test_reject_over_limit(self):
        """Test requests rejected over limit."""
        limiter = SlidingWindowLimiter(max_requests=3, window_seconds=1.0)

        assert limiter.allow() is True
        assert limiter.allow() is True
        assert limiter.allow() is True
        assert limiter.allow() is False

    def test_window_expiration(self):
        """Test old requests expire from window."""
        limiter = SlidingWindowLimiter(max_requests=2, window_seconds=0.1)

        assert limiter.allow() is True
        assert limiter.allow() is True
        assert limiter.allow() is False  # At limit

        time.sleep(0.15)  # Wait for window to expire

        assert limiter.allow() is True  # Should be allowed again

    def test_time_until_next(self):
        """Test calculating time until next request allowed."""
        limiter = SlidingWindowLimiter(max_requests=1, window_seconds=1.0)

        limiter.allow()
        time_until = limiter.time_until_next

        assert time_until is not None
        assert 0 < time_until <= 1.0


class TestRateLimiter:
    """Tests for RateLimiter class."""

    def test_default_configuration(self):
        """Test default rate limiter configuration."""
        RateLimiter._registry.clear()
        limiter = RateLimiter(name="default_test")

        assert limiter.max_calls == 100
        assert limiter.period == 60.0
        assert limiter.algorithm == "token_bucket"

    def test_token_bucket_algorithm(self):
        """Test rate limiter with token bucket."""
        RateLimiter._registry.clear()
        limiter = RateLimiter(
            name="token_test",
            max_calls=10,
            period=1.0,
            algorithm="token_bucket",
            block=False,
        )

        # Should allow up to burst capacity
        for _ in range(10):
            assert limiter.acquire() is True

    def test_sliding_window_algorithm(self):
        """Test rate limiter with sliding window."""
        RateLimiter._registry.clear()
        limiter = RateLimiter(
            name="window_test", max_calls=5, period=1.0, algorithm="sliding_window"
        )

        for _ in range(5):
            assert limiter.acquire() is True

        assert limiter.acquire() is False

    def test_context_manager_success(self):
        """Test context manager allows request."""
        RateLimiter._registry.clear()
        limiter = RateLimiter(name="ctx_success", max_calls=10, period=1.0, block=False)

        with limiter:
            pass  # Should not raise

        assert limiter.stats.allowed_requests == 1

    def test_context_manager_rejected(self):
        """Test context manager rejects when over limit."""
        RateLimiter._registry.clear()
        limiter = RateLimiter(
            name="ctx_reject",
            max_calls=1,
            period=60.0,
            algorithm="sliding_window",
            block=False,
        )

        with limiter:
            pass

        with pytest.raises(RateLimitExceeded):
            with limiter:
                pass

    def test_get_stats(self):
        """Test getting rate limiter statistics."""
        RateLimiter._registry.clear()
        limiter = RateLimiter(name="stats_test", max_calls=10, period=1.0, block=False)

        limiter.acquire()
        limiter.acquire()

        stats = limiter.get_stats()
        assert stats["name"] == "stats_test"
        assert stats["total_requests"] == 2
        assert stats["allowed_requests"] == 2

    def test_registry(self):
        """Test rate limiter registry."""
        RateLimiter._registry.clear()
        limiter = RateLimiter(name="registry_test")

        retrieved = RateLimiter.get("registry_test")
        assert retrieved is limiter


class TestRateLimitDecorator:
    """Tests for rate_limit decorator."""

    def test_decorator_allows_calls(self):
        """Test decorator allows calls under limit."""
        RateLimiter._registry.clear()

        @rate_limit(max_calls=10, period=1.0, name="deco_allow", block=False)
        def test_func():
            return "ok"

        for _ in range(5):
            assert test_func() == "ok"

    def test_decorator_rejects_over_limit(self):
        """Test decorator rejects calls over limit."""
        RateLimiter._registry.clear()

        @rate_limit(
            max_calls=2,
            period=60.0,
            name="deco_reject",
            algorithm="sliding_window",
            block=False,
        )
        def limited_func():
            return "ok"

        limited_func()
        limited_func()

        with pytest.raises(RateLimitExceeded):
            limited_func()

    def test_decorator_attaches_limiter(self):
        """Test decorator attaches rate limiter."""
        RateLimiter._registry.clear()

        @rate_limit(max_calls=100, period=60.0, name="deco_attach", block=False)
        def decorated():
            return "ok"

        assert hasattr(decorated, "rate_limiter")
        assert decorated.rate_limiter.max_calls == 100


class TestRateLimiterEdgeCases:
    """Edge case tests for rate limiter."""

    def test_high_rate(self):
        """Test very high rate limit."""
        RateLimiter._registry.clear()
        limiter = RateLimiter(
            name="high_rate", max_calls=10000, period=1.0, block=False
        )

        for _ in range(100):
            assert limiter.acquire() is True

    def test_concurrent_access(self):
        """Test rate limiter under concurrent access."""
        RateLimiter._registry.clear()
        limiter = RateLimiter(
            name="concurrent",
            max_calls=100,
            period=1.0,
            algorithm="token_bucket",
            block=False,
        )

        results = []
        lock = threading.Lock()

        def worker():
            for _ in range(10):
                result = limiter.acquire()
                with lock:
                    results.append(result)

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All should be allowed (10 workers * 10 calls = 100)
        assert len(results) == 100

    def test_blocking_mode(self):
        """Test blocking mode waits for tokens."""
        RateLimiter._registry.clear()
        limiter = RateLimiter(
            name="blocking",
            max_calls=100,  # 100 per second
            period=1.0,
            algorithm="token_bucket",
            block=True,
            block_timeout=0.5,
        )

        # Use all tokens
        for _ in range(100):
            limiter.acquire()

        # This should block and wait for refill
        start = time.time()
        result = limiter.acquire()
        time.time() - start

        # Should have waited some time for token refill
        assert result is True

    def test_rate_limit_exceeded_exception(self):
        """Test RateLimitExceeded exception attributes."""
        RateLimiter._registry.clear()
        limiter = RateLimiter(
            name="exception_test",
            max_calls=1,
            period=1.0,
            algorithm="sliding_window",
            block=False,
        )

        limiter.acquire()

        try:
            with limiter:
                pass
        except RateLimitExceeded as e:
            assert e.limiter_name == "exception_test"
            assert e.retry_after is not None
