"""
Unit tests for utils/retry module.

Tests cover:
- RetryConfig dataclass
- RetryExhaustedError exception
- calculate_backoff_delay function
- retry_with_backoff decorator
- RetryExecutor class

MIT Level Testing - 85%+ Coverage Target
"""

import pytest
from unittest.mock import Mock, patch

from src.utils.retry import (
    RetryConfig,
    RetryExhaustedError,
    calculate_backoff_delay,
    retry_with_backoff,
    RetryExecutor,
)


class TestRetryConfig:
    """Tests for RetryConfig dataclass."""

    def test_default_values(self):
        """Test default configuration."""
        config = RetryConfig()
        assert config.max_retries == 3
        assert config.base_delay_seconds == 1.0
        assert config.max_delay_seconds == 30.0
        assert config.exponential_base == 2.0
        assert config.jitter is True
        assert config.retryable_exceptions == (Exception,)

    def test_custom_values(self):
        """Test custom configuration."""
        config = RetryConfig(
            max_retries=5,
            base_delay_seconds=2.0,
            max_delay_seconds=60.0,
            exponential_base=3.0,
            jitter=False,
            retryable_exceptions=(ValueError, TypeError),
        )
        assert config.max_retries == 5
        assert config.base_delay_seconds == 2.0
        assert config.max_delay_seconds == 60.0
        assert config.exponential_base == 3.0
        assert config.jitter is False
        assert config.retryable_exceptions == (ValueError, TypeError)


class TestRetryExhaustedError:
    """Tests for RetryExhaustedError exception."""

    def test_error_creation(self):
        """Test error creation with attributes."""
        error = RetryExhaustedError(
            agent_type="video",
            attempts=3,
            last_error="Connection timeout",
        )
        assert error.agent_type == "video"
        assert error.attempts == 3
        assert error.last_error == "Connection timeout"
        assert "video" in str(error)
        assert "3" in str(error)
        assert "Connection timeout" in str(error)

    def test_error_is_exception(self):
        """Test error can be raised and caught."""
        with pytest.raises(RetryExhaustedError) as exc_info:
            raise RetryExhaustedError("music", 5, "API error")
        assert exc_info.value.agent_type == "music"


class TestCalculateBackoffDelay:
    """Tests for calculate_backoff_delay function."""

    def test_first_attempt(self):
        """Test delay for first attempt (0-indexed)."""
        delay = calculate_backoff_delay(0, base_delay=1.0, jitter=False)
        assert delay == 1.0

    def test_second_attempt(self):
        """Test delay for second attempt."""
        delay = calculate_backoff_delay(1, base_delay=1.0, jitter=False)
        assert delay == 2.0

    def test_third_attempt(self):
        """Test delay for third attempt."""
        delay = calculate_backoff_delay(2, base_delay=1.0, jitter=False)
        assert delay == 4.0

    def test_exponential_growth(self):
        """Test exponential growth pattern."""
        delays = [calculate_backoff_delay(i, jitter=False) for i in range(5)]
        assert delays == [1.0, 2.0, 4.0, 8.0, 16.0]

    def test_max_delay_cap(self):
        """Test delay is capped at max_delay."""
        delay = calculate_backoff_delay(10, base_delay=1.0, max_delay=30.0, jitter=False)
        assert delay == 30.0

    def test_jitter_adds_variance(self):
        """Test jitter adds randomness."""
        delays = [calculate_backoff_delay(1, jitter=True) for _ in range(10)]
        # All delays should be between 2.0 and 2.5 (0-25% jitter)
        assert all(2.0 <= d <= 2.5 for d in delays)
        # Should have some variance
        assert len(set(delays)) > 1

    def test_custom_exponential_base(self):
        """Test custom exponential base."""
        delay = calculate_backoff_delay(2, base_delay=1.0, exponential_base=3.0, jitter=False)
        assert delay == 9.0  # 1 * 3^2 = 9


class TestRetryWithBackoff:
    """Tests for retry_with_backoff decorator."""

    def test_successful_first_attempt(self):
        """Test function succeeds on first attempt."""
        call_count = 0

        @retry_with_backoff(max_retries=3)
        def always_succeeds():
            nonlocal call_count
            call_count += 1
            return "success"

        result = always_succeeds()
        assert result == "success"
        assert call_count == 1

    @patch("src.utils.retry.time.sleep")
    def test_succeeds_after_retries(self, mock_sleep):
        """Test function succeeds after retries."""
        attempt = 0

        @retry_with_backoff(max_retries=3, base_delay=0.1)
        def fails_then_succeeds():
            nonlocal attempt
            attempt += 1
            if attempt < 3:
                raise ValueError("Temporary error")
            return "success"

        result = fails_then_succeeds()
        assert result == "success"
        assert attempt == 3
        assert mock_sleep.call_count == 2  # Two retries

    @patch("src.utils.retry.time.sleep")
    def test_exhausts_retries(self, mock_sleep):
        """Test raises after exhausting retries."""
        @retry_with_backoff(max_retries=2)
        def always_fails():
            raise RuntimeError("Persistent error")

        with pytest.raises(RuntimeError, match="Persistent error"):
            always_fails()
        assert mock_sleep.call_count == 2

    @patch("src.utils.retry.time.sleep")
    def test_only_retries_specified_exceptions(self, mock_sleep):
        """Test only retries specified exceptions."""
        @retry_with_backoff(max_retries=3, retryable_exceptions=(ValueError,))
        def raises_type_error():
            raise TypeError("Not retryable")

        with pytest.raises(TypeError):
            raises_type_error()
        mock_sleep.assert_not_called()

    @patch("src.utils.retry.time.sleep")
    def test_on_retry_callback(self, mock_sleep):
        """Test on_retry callback is called."""
        callback = Mock()
        attempt = 0

        @retry_with_backoff(max_retries=2, on_retry=callback)
        def fails_twice():
            nonlocal attempt
            attempt += 1
            if attempt <= 2:
                raise ValueError("Error")
            return "success"

        result = fails_twice()
        assert result == "success"
        assert callback.call_count == 2

    def test_preserves_function_metadata(self):
        """Test decorator preserves function metadata."""
        @retry_with_backoff()
        def my_function():
            """My docstring."""
            pass

        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "My docstring."


class TestRetryExecutor:
    """Tests for RetryExecutor class."""

    def test_initialization(self):
        """Test executor initialization."""
        executor = RetryExecutor(
            max_retries=5,
            base_delay=2.0,
            exponential_base=3.0,
            max_delay=60.0,
        )
        assert executor.max_retries == 5
        assert executor.base_delay == 2.0
        assert executor.exponential_base == 3.0
        assert executor.max_delay == 60.0

    def test_successful_execution(self):
        """Test successful execution."""
        executor = RetryExecutor(max_retries=3)
        result = executor.execute(lambda: "success", agent_type="test")
        assert result == "success"
        assert executor.attempts_made == 1

    @patch("src.utils.retry.time.sleep")
    def test_retries_on_failure(self, mock_sleep):
        """Test retries on failure."""
        executor = RetryExecutor(max_retries=2, base_delay=0.1)
        attempt = 0

        def fails_then_succeeds():
            nonlocal attempt
            attempt += 1
            if attempt < 2:
                raise ValueError("Temporary error")
            return "success"

        result = executor.execute(fails_then_succeeds, agent_type="test")
        assert result == "success"
        assert executor.attempts_made == 2
        assert mock_sleep.call_count == 1

    @patch("src.utils.retry.time.sleep")
    def test_raises_retry_exhausted_error(self, mock_sleep):
        """Test raises RetryExhaustedError when exhausted."""
        executor = RetryExecutor(max_retries=2, base_delay=0.1)

        with pytest.raises(RetryExhaustedError) as exc_info:
            executor.execute(
                lambda: (_ for _ in ()).throw(RuntimeError("Always fails")),
                agent_type="video",
                point_id="p1",
            )

        assert exc_info.value.agent_type == "video"
        assert exc_info.value.attempts == 3  # initial + 2 retries

    @patch("src.utils.retry.time.sleep")
    def test_tracks_total_wait_time(self, mock_sleep):
        """Test tracks total wait time."""
        executor = RetryExecutor(max_retries=2, base_delay=1.0)
        attempt = 0

        def fails_twice():
            nonlocal attempt
            attempt += 1
            if attempt <= 2:
                raise ValueError("Error")
            return "success"

        executor.execute(fails_twice, agent_type="test")
        assert executor.total_wait_time > 0

    def test_get_stats(self):
        """Test get_stats method."""
        executor = RetryExecutor(max_retries=1)
        executor.execute(lambda: "success", agent_type="test")

        stats = executor.get_stats()
        assert "attempts_made" in stats
        assert "total_wait_time_seconds" in stats
        assert stats["attempts_made"] == 1
        assert stats["total_wait_time_seconds"] == 0.0

    def test_resets_stats_on_new_execution(self):
        """Test stats reset on new execution."""
        executor = RetryExecutor(max_retries=1)
        executor.execute(lambda: "first", agent_type="test")
        executor.execute(lambda: "second", agent_type="test")

        stats = executor.get_stats()
        assert stats["attempts_made"] == 1  # From second execution

