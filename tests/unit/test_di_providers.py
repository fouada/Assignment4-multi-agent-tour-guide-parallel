"""
Unit tests for DI Providers module.

Tests cover:
- SingletonProvider: thread-safe lazy singleton
- TransientProvider: new instance each time
- FactoryProvider: factory with context
- ValueProvider: pre-created value
- LazyProvider: lazy initialization
- PooledProvider: pooled instances

MIT Level Testing - 85%+ Coverage Target
"""

import threading
from unittest.mock import Mock

import pytest

from src.core.di.providers import (
    SingletonProvider,
    TransientProvider,
    FactoryProvider,
    ValueProvider,
    LazyProvider,
    PooledProvider,
)


class TestSingletonProvider:
    """Tests for SingletonProvider."""

    def test_creates_single_instance(self):
        """Test singleton creates one instance."""
        factory = Mock(return_value="instance")
        provider = SingletonProvider(factory)

        result1 = provider.get()
        result2 = provider.get()

        assert result1 == result2
        factory.assert_called_once()

    def test_lazy_initialization(self):
        """Test instance not created until first get."""
        factory = Mock(return_value="instance")
        provider = SingletonProvider(factory)

        factory.assert_not_called()
        provider.get()
        factory.assert_called_once()

    def test_thread_safety(self):
        """Test thread-safe initialization."""
        call_count = 0
        lock = threading.Lock()

        def factory():
            nonlocal call_count
            with lock:
                call_count += 1
            return f"instance_{call_count}"

        provider = SingletonProvider(factory)
        results = []
        result_lock = threading.Lock()

        def get_instance():
            result = provider.get()
            with result_lock:
                results.append(result)

        threads = [threading.Thread(target=get_instance) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All threads should get same instance
        assert all(r == results[0] for r in results)
        assert call_count == 1

    def test_dispose_calls_dispose(self):
        """Test dispose calls instance.dispose()."""
        instance = Mock()
        provider = SingletonProvider(lambda: instance)
        provider.get()

        provider.dispose()
        instance.dispose.assert_called_once()

    def test_dispose_calls_close_if_no_dispose(self):
        """Test dispose calls close() if no dispose()."""
        instance = Mock(spec=["close"])
        provider = SingletonProvider(lambda: instance)
        provider.get()

        provider.dispose()
        instance.close.assert_called_once()

    def test_dispose_clears_instance(self):
        """Test dispose clears instance."""
        factory = Mock(return_value="instance")
        provider = SingletonProvider(factory)
        provider.get()
        provider.dispose()

        # Next get should create new instance
        provider.get()
        assert factory.call_count == 2


class TestTransientProvider:
    """Tests for TransientProvider."""

    def test_creates_new_instance_each_time(self):
        """Test new instance each get."""
        call_count = 0

        def factory():
            nonlocal call_count
            call_count += 1
            return f"instance_{call_count}"

        provider = TransientProvider(factory)

        result1 = provider.get()
        result2 = provider.get()

        assert result1 != result2
        assert call_count == 2

    def test_passes_args_to_factory(self):
        """Test args passed to factory."""
        factory = Mock(return_value="instance")
        provider = TransientProvider(factory)

        provider.get(1, 2, key="value")
        factory.assert_called_once_with(1, 2, key="value")

    def test_dispose_does_nothing(self):
        """Test dispose is noop."""
        provider = TransientProvider(lambda: "instance")
        provider.dispose()  # Should not raise


class TestFactoryProvider:
    """Tests for FactoryProvider."""

    def test_calls_factory_with_args(self):
        """Test factory called with arguments."""
        factory = Mock(return_value="result")
        provider = FactoryProvider(factory)

        result = provider.get("arg1", key="value")
        assert result == "result"
        factory.assert_called_once_with("arg1", key="value")

    def test_dispose_does_nothing(self):
        """Test dispose is noop."""
        provider = FactoryProvider(Mock())
        provider.dispose()  # Should not raise


class TestValueProvider:
    """Tests for ValueProvider."""

    def test_returns_same_value(self):
        """Test always returns same value."""
        provider = ValueProvider("my_value")

        result1 = provider.get()
        result2 = provider.get()

        assert result1 == "my_value"
        assert result1 == result2

    def test_dispose_does_nothing(self):
        """Test dispose is noop."""
        provider = ValueProvider("value")
        provider.dispose()  # Should not raise


class TestLazyProvider:
    """Tests for LazyProvider."""

    def test_lazy_initialization(self):
        """Test lazy creates instance on first access."""
        factory = Mock(return_value="lazy_instance")
        provider = LazyProvider(factory)

        factory.assert_not_called()
        result = provider.get()
        assert result == "lazy_instance"
        factory.assert_called_once()

    def test_returns_same_instance(self):
        """Test returns same instance after initialization."""
        call_count = 0

        def factory():
            nonlocal call_count
            call_count += 1
            return f"instance_{call_count}"

        provider = LazyProvider(factory)

        result1 = provider.get()
        result2 = provider.get()

        assert result1 == result2
        assert call_count == 1

    def test_dispose(self):
        """Test dispose clears instance."""
        factory = Mock(return_value="instance")
        provider = LazyProvider(factory)
        provider.get()
        provider.dispose()

        # Should create new instance after dispose
        provider.get()
        assert factory.call_count == 2


class TestPooledProvider:
    """Tests for PooledProvider."""

    def test_initialization(self):
        """Test pooled provider initialization."""
        factory = Mock(return_value="instance")
        provider = PooledProvider(factory, pool_size=5)
        assert provider._pool_size == 5

    def test_get_from_pool(self):
        """Test getting instance from pool."""
        factory = Mock(return_value="pooled_instance")
        provider = PooledProvider(factory, pool_size=2)

        result = provider.get()
        assert result == "pooled_instance"

    def test_dispose_clears_pool(self):
        """Test dispose clears pool."""
        factory = Mock(return_value="instance")
        provider = PooledProvider(factory, pool_size=2)
        provider.get()
        provider.dispose()  # Should not raise
