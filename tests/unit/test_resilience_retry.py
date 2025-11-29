"""
Unit tests for Retry pattern with exponential backoff.

Test Coverage:
- RetryPolicy configuration
- Delay calculation with exponential backoff
- Jitter application
- Exception filtering (retryable/non-retryable)
- Result-based retry conditions
- Retry hooks
- Decorator usage
"""

import pytest

from src.core.resilience.retry import (
    AGGRESSIVE_RETRY,
    CONSERVATIVE_RETRY,
    NO_RETRY,
    RetryError,
    RetryPolicy,
    retry,
    with_retry,
)


class TestRetryPolicy:
    """Tests for RetryPolicy configuration."""

    def test_default_policy(self):
        """Test default policy values."""
        policy = RetryPolicy()
        assert policy.max_attempts == 3
        assert policy.backoff_factor == 2.0
        assert policy.initial_delay == 1.0
        assert policy.max_delay == 60.0
        assert policy.jitter == 0.1
        assert policy.retryable_exceptions is None
        assert policy.non_retryable_exceptions is None

    def test_custom_policy(self):
        """Test custom policy configuration."""
        policy = RetryPolicy(
            max_attempts=5,
            backoff_factor=3.0,
            initial_delay=0.5,
            max_delay=30.0,
            jitter=0.2,
        )
        assert policy.max_attempts == 5
        assert policy.backoff_factor == 3.0
        assert policy.initial_delay == 0.5

    def test_calculate_delay_exponential(self):
        """Test exponential backoff delay calculation."""
        policy = RetryPolicy(
            initial_delay=1.0,
            backoff_factor=2.0,
            max_delay=60.0,
            jitter=0,  # No jitter for predictable test
        )

        assert policy.calculate_delay(0) == 1.0  # 1 * 2^0
        assert policy.calculate_delay(1) == 2.0  # 1 * 2^1
        assert policy.calculate_delay(2) == 4.0  # 1 * 2^2
        assert policy.calculate_delay(3) == 8.0  # 1 * 2^3

    def test_calculate_delay_max_cap(self):
        """Test delay is capped at max_delay."""
        policy = RetryPolicy(
            initial_delay=1.0, backoff_factor=10.0, max_delay=50.0, jitter=0
        )

        # 1 * 10^3 = 1000, but capped at 50
        assert policy.calculate_delay(3) == 50.0

    def test_calculate_delay_with_jitter(self):
        """Test jitter adds randomness to delay."""
        policy = RetryPolicy(
            initial_delay=10.0,
            backoff_factor=1.0,  # No exponential increase
            max_delay=60.0,
            jitter=0.5,  # ±50%
        )

        delays = [policy.calculate_delay(0) for _ in range(100)]

        # All delays should be within jitter range
        for delay in delays:
            assert 5.0 <= delay <= 15.0  # 10 ± 50%

        # Should have some variation
        assert len(set(delays)) > 1

    def test_should_retry_all_exceptions(self):
        """Test retrying all exceptions when no filter set."""
        policy = RetryPolicy()

        assert policy.should_retry(ValueError("test")) is True
        assert policy.should_retry(RuntimeError("test")) is True
        assert policy.should_retry(Exception("test")) is True

    def test_should_retry_retryable_only(self):
        """Test only retrying specified exceptions."""
        policy = RetryPolicy(retryable_exceptions={ValueError, TimeoutError})

        assert policy.should_retry(ValueError("test")) is True
        assert policy.should_retry(TimeoutError("test")) is True
        assert policy.should_retry(RuntimeError("test")) is False

    def test_should_retry_non_retryable(self):
        """Test not retrying specified exceptions."""
        policy = RetryPolicy(non_retryable_exceptions={KeyboardInterrupt, SystemExit})

        assert policy.should_retry(ValueError("test")) is True
        assert policy.should_retry(KeyboardInterrupt()) is False
        assert policy.should_retry(SystemExit()) is False


class TestWithRetry:
    """Tests for with_retry function."""

    def test_success_on_first_attempt(self):
        """Test function succeeds on first attempt."""
        call_count = 0

        def succeeds():
            nonlocal call_count
            call_count += 1
            return "success"

        policy = RetryPolicy(max_attempts=3, initial_delay=0.01)
        result = with_retry(succeeds, policy)

        assert result == "success"
        assert call_count == 1

    def test_success_after_retries(self):
        """Test function succeeds after retries."""
        call_count = 0

        def fails_twice():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("fail")
            return "success"

        policy = RetryPolicy(max_attempts=5, initial_delay=0.01)
        result = with_retry(fails_twice, policy)

        assert result == "success"
        assert call_count == 3

    def test_exhaust_all_attempts(self):
        """Test raising RetryError after exhausting attempts."""
        call_count = 0

        def always_fails():
            nonlocal call_count
            call_count += 1
            raise ValueError("always fail")

        policy = RetryPolicy(max_attempts=3, initial_delay=0.01)

        with pytest.raises(RetryError) as exc_info:
            with_retry(always_fails, policy)

        assert exc_info.value.attempts == 3
        assert isinstance(exc_info.value.last_exception, ValueError)
        assert call_count == 3

    def test_non_retryable_exception_immediate(self):
        """Test non-retryable exception is raised immediately."""
        call_count = 0

        def fails_non_retryable():
            nonlocal call_count
            call_count += 1
            raise KeyboardInterrupt()

        policy = RetryPolicy(
            max_attempts=5,
            non_retryable_exceptions={KeyboardInterrupt},
            initial_delay=0.01,
        )

        with pytest.raises(KeyboardInterrupt):
            with_retry(fails_non_retryable, policy)

        assert call_count == 1  # Only one attempt

    def test_retry_on_result(self):
        """Test retrying based on result value."""
        call_count = 0

        def returns_none_twice():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return None
            return "success"

        policy = RetryPolicy(
            max_attempts=5, initial_delay=0.01, retry_on_result=lambda r: r is None
        )

        result = with_retry(returns_none_twice, policy)

        assert result == "success"
        assert call_count == 3

    def test_on_retry_callback(self):
        """Test retry callback is called."""
        callback_calls = []

        def on_retry(attempt, exception, delay):
            callback_calls.append((attempt, str(exception), delay))

        call_count = 0

        def fails_twice():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("fail")
            return "success"

        policy = RetryPolicy(max_attempts=5, initial_delay=0.01, on_retry=on_retry)

        with_retry(fails_twice, policy)

        assert len(callback_calls) == 2
        assert callback_calls[0][0] == 1  # First retry
        assert callback_calls[1][0] == 2  # Second retry


class TestRetryDecorator:
    """Tests for retry decorator."""

    def test_decorator_success(self):
        """Test decorator with successful function."""

        @retry(max_attempts=3, initial_delay=0.01)
        def always_succeeds():
            return "success"

        assert always_succeeds() == "success"

    def test_decorator_with_retries(self):
        """Test decorator retries failed function."""
        call_count = 0

        @retry(max_attempts=5, initial_delay=0.01)
        def fails_twice():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("fail")
            return "success"

        result = fails_twice()
        assert result == "success"
        assert call_count == 3

    def test_decorator_attaches_policy(self):
        """Test decorator attaches policy to function."""

        @retry(max_attempts=5, backoff_factor=3.0)
        def test_func():
            return "ok"

        assert hasattr(test_func, "retry_policy")
        assert test_func.retry_policy.max_attempts == 5
        assert test_func.retry_policy.backoff_factor == 3.0

    def test_decorator_exception_filtering(self):
        """Test decorator with exception filtering."""
        call_count = 0

        @retry(
            max_attempts=5,
            initial_delay=0.01,
            retryable_exceptions={ValueError},
            non_retryable_exceptions={TypeError},
        )
        def selective_fail(error_type):
            nonlocal call_count
            call_count += 1
            raise error_type("fail")

        # ValueError should be retried
        call_count = 0
        with pytest.raises(RetryError):
            selective_fail(ValueError)
        assert call_count == 5  # All attempts used

        # TypeError should not be retried
        call_count = 0
        with pytest.raises(TypeError):
            selective_fail(TypeError)
        assert call_count == 1  # Only one attempt


class TestPresetPolicies:
    """Tests for preset retry policies."""

    def test_aggressive_retry(self):
        """Test AGGRESSIVE_RETRY preset."""
        assert AGGRESSIVE_RETRY.max_attempts == 5
        assert AGGRESSIVE_RETRY.backoff_factor == 1.5
        assert AGGRESSIVE_RETRY.initial_delay == 0.5
        assert AGGRESSIVE_RETRY.max_delay == 10.0

    def test_conservative_retry(self):
        """Test CONSERVATIVE_RETRY preset."""
        assert CONSERVATIVE_RETRY.max_attempts == 3
        assert CONSERVATIVE_RETRY.backoff_factor == 3.0
        assert CONSERVATIVE_RETRY.initial_delay == 2.0
        assert CONSERVATIVE_RETRY.max_delay == 60.0

    def test_no_retry(self):
        """Test NO_RETRY preset."""
        assert NO_RETRY.max_attempts == 1


class TestRetryEdgeCases:
    """Edge case tests for retry pattern."""

    def test_single_attempt_policy(self):
        """Test policy with only one attempt."""
        call_count = 0

        def fails_once():
            nonlocal call_count
            call_count += 1
            raise ValueError("fail")

        policy = RetryPolicy(max_attempts=1)

        with pytest.raises(RetryError):
            with_retry(fails_once, policy)

        assert call_count == 1

    def test_zero_jitter(self):
        """Test delay calculation with zero jitter."""
        policy = RetryPolicy(initial_delay=5.0, jitter=0)

        delays = [policy.calculate_delay(0) for _ in range(10)]
        assert all(d == 5.0 for d in delays)

    def test_very_high_backoff(self):
        """Test delay capped with very high backoff."""
        policy = RetryPolicy(
            initial_delay=1.0, backoff_factor=100.0, max_delay=60.0, jitter=0
        )

        # Should be capped at max_delay
        assert policy.calculate_delay(5) == 60.0

    def test_callback_exception_handled(self):
        """Test retry callback exceptions are handled."""

        def bad_callback(attempt, exception, delay):
            raise RuntimeError("Callback error")

        call_count = 0

        def fails_once():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("fail")
            return "success"

        policy = RetryPolicy(max_attempts=3, initial_delay=0.01, on_retry=bad_callback)

        # Should succeed despite callback error
        result = with_retry(fails_once, policy)
        assert result == "success"
