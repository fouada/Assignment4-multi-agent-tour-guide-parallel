"""
Unit tests for Timeout pattern.

Test Coverage:
- Synchronous timeout with threading
- Timeout decorator
- Fallback on timeout
- Async timeout (when applicable)
- Edge cases
"""
import pytest
import time
import asyncio
from unittest.mock import MagicMock

from src.core.resilience.timeout import (
    TimeoutError,
    with_timeout,
    timeout,
    async_with_timeout,
    async_timeout
)


class TestTimeoutError:
    """Tests for TimeoutError exception."""

    def test_timeout_error_message(self):
        """Test timeout error message."""
        error = TimeoutError("Operation timed out", 10.0)
        assert str(error) == "Operation timed out"
        assert error.seconds == 10.0


class TestWithTimeout:
    """Tests for with_timeout function."""

    def test_fast_function_succeeds(self):
        """Test fast function completes before timeout."""
        def fast_func():
            return "fast"

        result = with_timeout(fast_func, seconds=1.0)
        assert result == "fast"

    def test_slow_function_times_out(self):
        """Test slow function is terminated on timeout."""
        def slow_func():
            time.sleep(5.0)
            return "slow"

        with pytest.raises(TimeoutError) as exc_info:
            with_timeout(slow_func, seconds=0.1)

        assert exc_info.value.seconds == 0.1

    def test_function_with_arguments(self):
        """Test function with args and kwargs."""
        def add(a, b, c=0):
            return a + b + c

        result = with_timeout(add, 1.0, 1, 2, c=3)
        assert result == 6

    def test_function_raising_exception(self):
        """Test function exception is propagated."""
        def raises():
            raise ValueError("test error")

        with pytest.raises(ValueError):
            with_timeout(raises, 1.0)


class TestTimeoutDecorator:
    """Tests for timeout decorator."""

    def test_decorator_fast_function(self):
        """Test decorator with fast function."""
        @timeout(seconds=1.0)
        def fast():
            return "quick"

        assert fast() == "quick"

    def test_decorator_slow_function(self):
        """Test decorator with slow function."""
        @timeout(seconds=0.1)
        def slow():
            time.sleep(5.0)
            return "slow"

        with pytest.raises(TimeoutError):
            slow()

    def test_decorator_attaches_timeout(self):
        """Test decorator attaches timeout value."""
        @timeout(seconds=5.0)
        def test_func():
            return "ok"

        assert hasattr(test_func, "timeout_seconds")
        assert test_func.timeout_seconds == 5.0

    def test_decorator_with_fallback(self):
        """Test decorator with on_timeout fallback."""
        @timeout(seconds=0.1, on_timeout=lambda: "fallback_value")
        def slow_with_fallback():
            time.sleep(5.0)
            return "slow"

        result = slow_with_fallback()
        assert result == "fallback_value"

    def test_decorator_no_fallback_raises(self):
        """Test decorator without fallback raises TimeoutError."""
        @timeout(seconds=0.1)
        def slow_no_fallback():
            time.sleep(5.0)
            return "slow"

        with pytest.raises(TimeoutError):
            slow_no_fallback()

    def test_decorator_preserves_docstring(self):
        """Test decorator preserves function metadata."""
        @timeout(seconds=1.0)
        def documented_func():
            """This is a documented function."""
            return "ok"

        assert documented_func.__doc__ == "This is a documented function."


class TestAsyncTimeout:
    """Tests for async timeout functions."""

    def test_async_with_timeout_sync(self):
        """Test async timeout can be run with asyncio.run."""
        import asyncio

        async def fast_async():
            await asyncio.sleep(0.01)
            return "fast"

        async def run_test():
            return await async_with_timeout(fast_async(), 1.0)

        result = asyncio.run(run_test())
        assert result == "fast"

    def test_async_slow_times_out_sync(self):
        """Test slow async function times out when run."""
        import asyncio

        async def slow_async():
            await asyncio.sleep(5.0)
            return "slow"

        async def run_test():
            return await async_with_timeout(slow_async(), 0.1)

        with pytest.raises(TimeoutError):
            asyncio.run(run_test())

    def test_async_decorator_sync(self):
        """Test async_timeout decorator when run."""
        import asyncio

        @async_timeout(seconds=1.0)
        async def fast_decorated():
            await asyncio.sleep(0.01)
            return "decorated"

        result = asyncio.run(fast_decorated())
        assert result == "decorated"

    def test_async_decorator_timeout_sync(self):
        """Test async_timeout decorator times out when run."""
        import asyncio

        @async_timeout(seconds=0.1)
        async def slow_decorated():
            await asyncio.sleep(5.0)
            return "slow"

        with pytest.raises(TimeoutError):
            asyncio.run(slow_decorated())


class TestTimeoutEdgeCases:
    """Edge case tests for timeout pattern."""

    def test_zero_timeout(self):
        """Test very small timeout value."""
        @timeout(seconds=0.001)
        def any_func():
            return "ok"

        # May or may not timeout - depends on system speed
        try:
            result = any_func()
            assert result == "ok"
        except TimeoutError:
            pass  # Also acceptable

    def test_timeout_with_cpu_bound(self):
        """Test timeout with CPU-bound operation."""
        @timeout(seconds=0.1)
        def cpu_bound():
            # This won't be interrupted immediately due to GIL
            # but timeout should eventually trigger
            total = 0
            for i in range(10_000_000):
                total += i
            return total

        # CPU bound tasks are tricky with threading timeout
        # May succeed or timeout depending on system
        try:
            cpu_bound()
        except TimeoutError:
            pass  # Expected in most cases

    def test_nested_timeouts(self):
        """Test nested timeout decorators."""
        @timeout(seconds=1.0)
        def outer():
            @timeout(seconds=0.5)
            def inner():
                time.sleep(0.8)
                return "inner"
            return inner()

        with pytest.raises(TimeoutError):
            outer()  # Inner timeout should trigger first

    def test_timeout_return_none(self):
        """Test function returning None doesn't cause issues."""
        @timeout(seconds=1.0)
        def returns_none():
            return None

        result = returns_none()
        assert result is None

    def test_timeout_return_exception(self):
        """Test function returning exception object (not raising)."""
        @timeout(seconds=1.0)
        def returns_exception():
            return ValueError("not raised")

        result = returns_exception()
        assert isinstance(result, ValueError)

