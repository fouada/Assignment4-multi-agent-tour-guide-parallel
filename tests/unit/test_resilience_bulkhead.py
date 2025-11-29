"""
Unit tests for resilience/bulkhead module.

Tests cover:
- BulkheadFull exception
- BulkheadStats tracking
- Bulkhead class with semaphore-based limiting

MIT Level Testing - 85%+ Coverage Target
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from src.core.resilience.bulkhead import (
    Bulkhead,
    BulkheadFull,
    BulkheadStats,
)


class TestBulkheadFull:
    """Tests for BulkheadFull exception."""

    def test_exception_creation(self):
        """Test exception with bulkhead name."""
        exc = BulkheadFull("Capacity exceeded", "api_bulkhead")
        assert exc.bulkhead_name == "api_bulkhead"
        assert "Capacity exceeded" in str(exc)

    def test_can_be_raised_and_caught(self):
        """Test exception can be raised."""
        with pytest.raises(BulkheadFull) as exc_info:
            raise BulkheadFull("Full", "test")
        assert exc_info.value.bulkhead_name == "test"


class TestBulkheadStats:
    """Tests for BulkheadStats dataclass."""

    def test_default_values(self):
        """Test default stats."""
        stats = BulkheadStats()
        assert stats.total_calls == 0
        assert stats.successful_calls == 0
        assert stats.rejected_calls == 0
        assert stats.current_concurrent == 0
        assert stats.current_queued == 0
        assert stats.max_concurrent_reached == 0

    def test_acceptance_rate_no_calls(self):
        """Test acceptance rate with no calls."""
        stats = BulkheadStats()
        assert stats.acceptance_rate == 1.0

    def test_acceptance_rate_all_successful(self):
        """Test acceptance rate with all successful."""
        stats = BulkheadStats(total_calls=10, successful_calls=10)
        assert stats.acceptance_rate == 1.0

    def test_acceptance_rate_half_successful(self):
        """Test acceptance rate with half successful."""
        stats = BulkheadStats(total_calls=10, successful_calls=5)
        assert stats.acceptance_rate == 0.5

    def test_acceptance_rate_none_successful(self):
        """Test acceptance rate with none successful."""
        stats = BulkheadStats(total_calls=10, successful_calls=0)
        assert stats.acceptance_rate == 0.0


class TestBulkhead:
    """Tests for Bulkhead class."""

    def test_initialization(self):
        """Test bulkhead initialization."""
        bulkhead = Bulkhead(
            name="test_init",
            max_concurrent=5,
            max_queued=10,
            timeout=5.0,
        )
        assert bulkhead.name == "test_init"
        assert bulkhead.max_concurrent == 5
        assert bulkhead.max_queued == 10

    def test_acquire_successful(self):
        """Test successful acquire."""
        bulkhead = Bulkhead(name="test_acquire", max_concurrent=2)
        acquired = bulkhead.acquire()
        assert acquired is True
        bulkhead.release()

    def test_acquire_updates_stats(self):
        """Test acquire updates stats."""
        bulkhead = Bulkhead(name="test_stats", max_concurrent=2)
        bulkhead.acquire()

        stats = bulkhead.get_stats()
        assert stats["total_calls"] == 1
        bulkhead.release()

    def test_context_manager(self):
        """Test bulkhead as context manager."""
        bulkhead = Bulkhead(name="test_cm", max_concurrent=2)

        with bulkhead:
            stats = bulkhead.get_stats()
            assert stats["current_concurrent"] == 1

        stats = bulkhead.get_stats()
        assert stats["current_concurrent"] == 0

    def test_context_manager_with_exception(self):
        """Test context manager releases on exception."""
        bulkhead = Bulkhead(name="test_cm_exc", max_concurrent=2)

        try:
            with bulkhead:
                raise ValueError("Test error")
        except ValueError:
            pass

        stats = bulkhead.get_stats()
        assert stats["current_concurrent"] == 0

    def test_get_stats(self):
        """Test get_stats returns dict."""
        bulkhead = Bulkhead(name="test_getstats", max_concurrent=2)
        stats = bulkhead.get_stats()
        assert isinstance(stats, dict)
        assert "total_calls" in stats
        assert "current_concurrent" in stats

    def test_release(self):
        """Test release decrements concurrent."""
        bulkhead = Bulkhead(name="test_release", max_concurrent=2)
        bulkhead.acquire()
        stats = bulkhead.get_stats()
        assert stats["current_concurrent"] == 1

        bulkhead.release()
        stats = bulkhead.get_stats()
        assert stats["current_concurrent"] == 0

    def test_max_concurrent_tracking(self):
        """Test max concurrent is tracked."""
        bulkhead = Bulkhead(name="test_max", max_concurrent=5)

        bulkhead.acquire()
        bulkhead.acquire()
        bulkhead.acquire()

        stats = bulkhead.get_stats()
        assert stats["max_concurrent_reached"] == 3

        bulkhead.release()
        bulkhead.release()
        bulkhead.release()

    def test_concurrent_limit_respected(self):
        """Test concurrent limit is respected."""
        bulkhead = Bulkhead(name="test_limit", max_concurrent=2, max_queued=0)

        assert bulkhead.acquire() is True
        assert bulkhead.acquire() is True
        assert bulkhead.acquire() is False  # Should be rejected

        stats = bulkhead.get_stats()
        assert stats["rejected_calls"] == 1

        bulkhead.release()
        bulkhead.release()

    def test_queuing(self):
        """Test requests queue when semaphore full."""
        bulkhead = Bulkhead(name="test_queue", max_concurrent=1, max_queued=1)

        # Fill the semaphore
        assert bulkhead.acquire() is True

        # This should queue
        def try_acquire():
            return bulkhead.acquire(timeout=0.5)

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(try_acquire)
            time.sleep(0.1)  # Let it queue
            bulkhead.release()  # Release to let queue proceed
            result = future.result()
            assert result is True

        bulkhead.release()


class TestBulkheadRegistry:
    """Tests for bulkhead registry."""

    def test_get_by_name(self):
        """Test getting bulkhead by name."""
        bulkhead = Bulkhead(name="registered_bulkhead", max_concurrent=5)
        retrieved = Bulkhead.get("registered_bulkhead")
        assert retrieved is bulkhead

    def test_get_nonexistent(self):
        """Test getting nonexistent bulkhead."""
        result = Bulkhead.get("nonexistent_bulkhead")
        assert result is None


class TestBulkheadThreadSafety:
    """Tests for bulkhead thread safety."""

    def test_concurrent_acquire_release(self):
        """Test thread-safe concurrent access."""
        bulkhead = Bulkhead(name="test_threadsafe", max_concurrent=10)
        results = []
        lock = threading.Lock()

        def work(value):
            if bulkhead.acquire(timeout=2.0):
                try:
                    time.sleep(0.01)
                    with lock:
                        results.append(value)
                finally:
                    bulkhead.release()
            return value

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(work, i) for i in range(5)]
            for f in futures:
                f.result()

        assert len(results) == 5
        assert sorted(results) == list(range(5))
