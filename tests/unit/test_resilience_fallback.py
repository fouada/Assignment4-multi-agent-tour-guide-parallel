"""
Unit tests for resilience/fallback module.

Tests cover:
- FallbackStats tracking
- Fallback class with various strategies
- fallback decorator
- cache_fallback decorator

MIT Level Testing - 85%+ Coverage Target
"""

from unittest.mock import Mock

import pytest

from src.core.resilience.fallback import (
    Fallback,
    FallbackStats,
    cache_fallback,
    fallback,
)


class TestFallbackStats:
    """Tests for FallbackStats dataclass."""

    def test_default_values(self):
        """Test default stats."""
        stats = FallbackStats()
        assert stats.total_calls == 0
        assert stats.primary_successes == 0
        assert stats.fallback_activations == 0
        assert stats.fallback_failures == 0

    def test_custom_values(self):
        """Test custom stats."""
        stats = FallbackStats(
            total_calls=10,
            primary_successes=8,
            fallback_activations=2,
            fallback_failures=0,
        )
        assert stats.total_calls == 10
        assert stats.primary_successes == 8


class TestFallbackClass:
    """Tests for Fallback class."""

    def test_initialization(self):
        """Test fallback initialization."""
        fb = Fallback(default_value="default")
        assert fb.default_value == "default"
        assert fb.fallback_fn is None
        assert fb.fallback_chain == []

    def test_primary_success(self):
        """Test primary function success."""
        fb = Fallback(default_value="fallback")

        def primary():
            return "primary_result"

        result = fb.execute(primary)
        assert result == "primary_result"
        assert fb.stats.primary_successes == 1

    def test_fallback_to_default(self):
        """Test fallback to default value."""
        fb = Fallback(default_value="fallback_value")

        def failing():
            raise ValueError("Failed")

        result = fb.execute(failing)
        assert result == "fallback_value"
        assert fb.stats.fallback_activations == 1

    def test_fallback_to_function(self):
        """Test fallback to function."""
        fallback_fn = Mock(return_value="fallback_result")
        fb = Fallback(fallback_fn=fallback_fn)

        def failing():
            raise ValueError("Failed")

        result = fb.execute(failing)
        assert result == "fallback_result"
        fallback_fn.assert_called_once()

    def test_fallback_chain(self):
        """Test fallback chain execution."""

        def fallback1():
            raise ValueError("Fallback1 failed")

        def fallback2():
            return "fallback2_result"

        fb = Fallback(fallback_chain=[fallback1, fallback2])

        def failing():
            raise ValueError("Primary failed")

        result = fb.execute(failing)
        assert result == "fallback2_result"

    def test_all_fallbacks_fail(self):
        """Test error when all fallbacks fail."""
        fb = Fallback()  # No default value

        def failing():
            raise ValueError("Failed")

        with pytest.raises(RuntimeError, match="All fallbacks failed"):
            fb.execute(failing)

    def test_exception_filtering(self):
        """Test only specified exceptions trigger fallback."""
        fb = Fallback(
            default_value="fallback",
            exceptions=[ValueError],
        )

        def raises_type_error():
            raise TypeError("Not caught")

        with pytest.raises(TypeError):
            fb.execute(raises_type_error)

    def test_stats_tracking(self):
        """Test stats are tracked correctly."""
        fb = Fallback(default_value="default")

        def success():
            return "ok"

        def failure():
            raise ValueError("Failed")

        fb.execute(success)
        fb.execute(success)
        fb.execute(failure)

        assert fb.stats.total_calls == 3
        assert fb.stats.primary_successes == 2
        assert fb.stats.fallback_activations == 1

    def test_passes_args_kwargs(self):
        """Test arguments are passed to primary and fallback."""
        fallback_fn = Mock(return_value="fallback")
        fb = Fallback(fallback_fn=fallback_fn)

        def failing(a, b, c=None):
            raise ValueError("Failed")

        fb.execute(failing, 1, 2, c=3)
        fallback_fn.assert_called_once_with(1, 2, c=3)

    def test_log_fallback_disabled(self):
        """Test logging can be disabled."""
        fb = Fallback(default_value="default", log_fallback=False)

        def failing():
            raise ValueError("Failed")

        result = fb.execute(failing)
        assert result == "default"

    def test_fallback_fn_fails_uses_chain(self):
        """Test if fallback_fn fails, tries chain."""

        def failing_fallback():
            raise ValueError("Fallback failed")

        def chain_fallback():
            return "chain_result"

        fb = Fallback(
            fallback_fn=failing_fallback,
            fallback_chain=[chain_fallback],
        )

        def primary():
            raise ValueError("Primary failed")

        result = fb.execute(primary)
        assert result == "chain_result"

    def test_fallback_fn_fails_uses_default(self):
        """Test if fallback_fn fails, uses default."""

        def failing_fallback():
            raise ValueError("Fallback failed")

        fb = Fallback(
            default_value="default_value",
            fallback_fn=failing_fallback,
        )

        def primary():
            raise ValueError("Primary failed")

        result = fb.execute(primary)
        assert result == "default_value"


class TestFallbackDecorator:
    """Tests for fallback decorator."""

    def test_decorator_success(self):
        """Test decorator with successful function."""

        @fallback(default_value="fallback")
        def my_func():
            return "success"

        assert my_func() == "success"

    def test_decorator_fallback(self):
        """Test decorator uses fallback on error."""

        @fallback(default_value="fallback_value")
        def failing_func():
            raise ValueError("Failed")

        assert failing_func() == "fallback_value"

    def test_decorator_with_fallback_fn(self):
        """Test decorator with fallback function."""

        def backup():
            return "backup_result"

        @fallback(fallback_fn=backup)
        def my_func():
            raise ValueError("Failed")

        assert my_func() == "backup_result"

    def test_decorator_preserves_metadata(self):
        """Test decorator preserves function metadata."""

        @fallback(default_value="default")
        def my_func():
            """My docstring."""
            return "result"

        assert my_func.__name__ == "my_func"
        assert my_func.__doc__ == "My docstring."

    def test_decorator_exposes_handler(self):
        """Test decorated function exposes fallback handler."""

        @fallback(default_value="default")
        def my_func():
            return "result"

        assert hasattr(my_func, "fallback_handler")
        assert isinstance(my_func.fallback_handler, Fallback)

    def test_decorator_with_chain(self):
        """Test decorator with fallback chain."""

        def fallback1():
            raise ValueError("Failed1")

        def fallback2():
            return "fallback2"

        @fallback(fallback_chain=[fallback1, fallback2])
        def my_func():
            raise ValueError("Primary failed")

        assert my_func() == "fallback2"


class TestCacheFallback:
    """Tests for cache_fallback decorator."""

    def test_primary_success_caches(self):
        """Test successful call caches result."""
        cache = {}
        cache_set = Mock(side_effect=lambda k, v: cache.__setitem__(k, v))
        cache_get = Mock(return_value=None)

        @cache_fallback(
            cache_key_fn=lambda x: f"key:{x}",
            cache_get_fn=cache_get,
            cache_set_fn=cache_set,
        )
        def my_func(x):
            return f"result_{x}"

        result = my_func(1)
        assert result == "result_1"
        cache_set.assert_called_once_with("key:1", "result_1")

    def test_primary_fails_uses_cache(self):
        """Test failed call uses cached value."""
        cache = {"key:1": "cached_value"}
        cache_get = Mock(side_effect=lambda k: cache.get(k))
        cache_set = Mock()

        call_count = 0

        @cache_fallback(
            cache_key_fn=lambda x: f"key:{x}",
            cache_get_fn=cache_get,
            cache_set_fn=cache_set,
        )
        def my_func(x):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise ValueError("Failed")
            return f"result_{x}"

        # First call succeeds
        result1 = my_func(1)
        assert result1 == "result_1"

        # Second call fails but uses cache
        result2 = my_func(1)
        assert result2 == "cached_value"

    def test_primary_fails_no_cache_raises(self):
        """Test raises when no cache available."""
        cache_get = Mock(return_value=None)
        cache_set = Mock()

        @cache_fallback(
            cache_key_fn=lambda x: f"key:{x}",
            cache_get_fn=cache_get,
            cache_set_fn=cache_set,
        )
        def failing_func(x):
            raise ValueError("Failed")

        with pytest.raises(ValueError):
            failing_func(1)

    def test_cache_set_failure_ignored(self):
        """Test cache set failure is ignored."""
        cache_get = Mock(return_value=None)
        cache_set = Mock(side_effect=Exception("Cache error"))

        @cache_fallback(
            cache_key_fn=lambda x: f"key:{x}",
            cache_get_fn=cache_get,
            cache_set_fn=cache_set,
        )
        def my_func(x):
            return f"result_{x}"

        # Should not raise
        result = my_func(1)
        assert result == "result_1"
