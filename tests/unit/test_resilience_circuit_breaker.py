"""
Unit tests for Circuit Breaker pattern.

Test Coverage:
- State transitions (CLOSED -> OPEN -> HALF_OPEN -> CLOSED)
- Failure threshold triggering
- Reset timeout behavior
- Success threshold for recovery
- Excluded exceptions
- Decorator and context manager usage
- Statistics tracking
"""
import time

import pytest

from src.core.resilience.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpen,
    CircuitBreakerStats,
    CircuitState,
    circuit_breaker,
)


class TestCircuitState:
    """Tests for CircuitState enum."""

    def test_all_states_exist(self):
        """Test all circuit states are defined."""
        assert CircuitState.CLOSED
        assert CircuitState.OPEN
        assert CircuitState.HALF_OPEN

    def test_state_count(self):
        """Test we have exactly 3 states."""
        assert len(list(CircuitState)) == 3


class TestCircuitBreakerStats:
    """Tests for CircuitBreakerStats."""

    def test_initial_stats(self):
        """Test initial statistics values."""
        stats = CircuitBreakerStats()
        assert stats.total_calls == 0
        assert stats.successful_calls == 0
        assert stats.failed_calls == 0
        assert stats.rejected_calls == 0
        assert stats.state_changes == []
        assert stats.last_failure is None
        assert stats.last_success is None

    def test_success_rate_empty(self):
        """Test success rate with no calls."""
        stats = CircuitBreakerStats()
        assert stats.success_rate == 1.0  # Default to 100%

    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        stats = CircuitBreakerStats(
            total_calls=10,
            successful_calls=8,
            failed_calls=2
        )
        assert stats.success_rate == 0.8

    def test_failure_rate_empty(self):
        """Test failure rate with no calls."""
        stats = CircuitBreakerStats()
        assert stats.failure_rate == 0.0

    def test_failure_rate_calculation(self):
        """Test failure rate calculation."""
        stats = CircuitBreakerStats(
            total_calls=10,
            successful_calls=7,
            failed_calls=3
        )
        assert stats.failure_rate == 0.3


class TestCircuitBreaker:
    """Tests for CircuitBreaker class."""

    @pytest.fixture
    def breaker(self):
        """Create a circuit breaker with test configuration."""
        # Clear registry before each test
        CircuitBreaker._registry.clear()
        return CircuitBreaker(
            name="test_breaker",
            failure_threshold=3,
            success_threshold=2,
            reset_timeout=0.1  # Short timeout for tests
        )

    def test_initial_state_closed(self, breaker):
        """Test circuit starts in CLOSED state."""
        assert breaker.state == CircuitState.CLOSED
        assert breaker.is_closed
        assert not breaker.is_open

    def test_allow_request_when_closed(self, breaker):
        """Test requests are allowed when closed."""
        assert breaker.allow_request() is True

    def test_record_success(self, breaker):
        """Test recording successful calls."""
        breaker.record_success()
        assert breaker.stats.successful_calls == 1
        assert breaker.stats.total_calls == 1
        assert breaker.stats.last_success is not None

    def test_record_failure(self, breaker):
        """Test recording failed calls."""
        breaker.record_failure()
        assert breaker.stats.failed_calls == 1
        assert breaker.stats.total_calls == 1
        assert breaker.stats.last_failure is not None

    def test_transition_to_open_on_threshold(self, breaker):
        """Test circuit opens after reaching failure threshold."""
        for _ in range(3):  # failure_threshold = 3
            breaker.record_failure()

        assert breaker.state == CircuitState.OPEN
        assert breaker.is_open

    def test_request_blocked_when_open(self, breaker):
        """Test requests are blocked when open."""
        # Trip the breaker
        for _ in range(3):
            breaker.record_failure()

        assert breaker.allow_request() is False

    def test_transition_to_half_open_after_timeout(self, breaker):
        """Test circuit goes to HALF_OPEN after reset timeout."""
        # Trip the breaker
        for _ in range(3):
            breaker.record_failure()

        assert breaker.state == CircuitState.OPEN

        # Wait for reset timeout
        time.sleep(0.15)

        # Access state to trigger transition
        assert breaker.state == CircuitState.HALF_OPEN

    def test_transition_to_closed_from_half_open(self, breaker):
        """Test circuit closes after success threshold in HALF_OPEN."""
        # Trip and wait for HALF_OPEN
        for _ in range(3):
            breaker.record_failure()
        time.sleep(0.15)
        assert breaker.state == CircuitState.HALF_OPEN

        # Record successes
        breaker.record_success()
        breaker.record_success()

        assert breaker.state == CircuitState.CLOSED

    def test_transition_back_to_open_from_half_open(self, breaker):
        """Test circuit goes back to OPEN on failure in HALF_OPEN."""
        # Trip and wait for HALF_OPEN
        for _ in range(3):
            breaker.record_failure()
        time.sleep(0.15)
        assert breaker.state == CircuitState.HALF_OPEN

        # Record failure
        breaker.record_failure()

        assert breaker.state == CircuitState.OPEN

    def test_success_resets_failure_count(self, breaker):
        """Test success in CLOSED state resets failure count."""
        breaker.record_failure()
        breaker.record_failure()
        assert breaker._failure_count == 2

        breaker.record_success()
        assert breaker._failure_count == 0

    def test_manual_reset(self, breaker):
        """Test manual reset to CLOSED."""
        for _ in range(3):
            breaker.record_failure()
        assert breaker.state == CircuitState.OPEN

        breaker.reset()
        assert breaker.state == CircuitState.CLOSED

    def test_manual_trip(self, breaker):
        """Test manual trip to OPEN."""
        assert breaker.state == CircuitState.CLOSED
        breaker.trip()
        assert breaker.state == CircuitState.OPEN

    def test_excluded_exceptions(self):
        """Test excluded exceptions don't count as failures."""
        CircuitBreaker._registry.clear()
        breaker = CircuitBreaker(
            name="excluded_test",
            failure_threshold=3,
            excluded_exceptions={ValueError}
        )

        for _ in range(5):
            breaker.record_failure(ValueError("excluded"))

        # Should still be closed - ValueErrors are excluded
        assert breaker.state == CircuitState.CLOSED

    def test_non_excluded_exceptions(self):
        """Test non-excluded exceptions count as failures."""
        CircuitBreaker._registry.clear()
        breaker = CircuitBreaker(
            name="non_excluded_test",
            failure_threshold=3,
            excluded_exceptions={ValueError}
        )

        for _ in range(3):
            breaker.record_failure(RuntimeError("counted"))

        assert breaker.state == CircuitState.OPEN


class TestCircuitBreakerContextManager:
    """Tests for circuit breaker context manager."""

    @pytest.fixture
    def breaker(self):
        """Create a circuit breaker for context manager tests."""
        CircuitBreaker._registry.clear()
        return CircuitBreaker(
            name="context_test",
            failure_threshold=3,
            reset_timeout=0.1
        )

    def test_context_manager_success(self, breaker):
        """Test context manager records success."""
        with breaker:
            pass  # No exception

        assert breaker.stats.successful_calls == 1

    def test_context_manager_failure(self, breaker):
        """Test context manager records failure on exception."""
        try:
            with breaker:
                raise RuntimeError("test error")
        except RuntimeError:
            pass

        assert breaker.stats.failed_calls == 1

    def test_context_manager_rejects_when_open(self, breaker):
        """Test context manager raises when circuit is open."""
        for _ in range(3):
            breaker.record_failure()

        with pytest.raises(CircuitBreakerOpen) as exc_info:
            with breaker:
                pass

        assert exc_info.value.circuit_name == "context_test"
        assert breaker.stats.rejected_calls == 1


class TestCircuitBreakerDecorator:
    """Tests for circuit_breaker decorator."""

    def test_decorator_wraps_function(self):
        """Test decorator wraps function correctly."""
        CircuitBreaker._registry.clear()

        @circuit_breaker(name="decorated_func", failure_threshold=3)
        def test_func():
            return "success"

        result = test_func()
        assert result == "success"
        assert hasattr(test_func, "circuit_breaker")

    def test_decorator_counts_success(self):
        """Test decorator counts successful calls."""
        CircuitBreaker._registry.clear()

        @circuit_breaker(name="success_counter", failure_threshold=3)
        def always_succeeds():
            return "ok"

        always_succeeds()
        always_succeeds()

        cb = CircuitBreaker.get("success_counter")
        assert cb.stats.successful_calls == 2

    def test_decorator_counts_failure(self):
        """Test decorator counts failed calls."""
        CircuitBreaker._registry.clear()

        @circuit_breaker(name="failure_counter", failure_threshold=5)
        def always_fails():
            raise ValueError("error")

        for _ in range(3):
            try:
                always_fails()
            except ValueError:
                pass

        cb = CircuitBreaker.get("failure_counter")
        assert cb.stats.failed_calls == 3

    def test_decorator_opens_circuit(self):
        """Test decorator opens circuit after threshold."""
        CircuitBreaker._registry.clear()

        @circuit_breaker(name="opener", failure_threshold=2, reset_timeout=0.1)
        def failing_func():
            raise RuntimeError("fail")

        for _ in range(2):
            try:
                failing_func()
            except RuntimeError:
                pass

        cb = CircuitBreaker.get("opener")
        assert cb.state == CircuitState.OPEN

        with pytest.raises(CircuitBreakerOpen):
            failing_func()


class TestCircuitBreakerRegistry:
    """Tests for circuit breaker registry."""

    def test_get_registered_breaker(self):
        """Test getting registered circuit breaker."""
        CircuitBreaker._registry.clear()
        breaker = CircuitBreaker(name="registry_test")

        retrieved = CircuitBreaker.get("registry_test")
        assert retrieved is breaker

    def test_get_nonexistent_breaker(self):
        """Test getting non-existent circuit breaker."""
        CircuitBreaker._registry.clear()
        assert CircuitBreaker.get("nonexistent") is None

    def test_get_all_breakers(self):
        """Test getting all registered circuit breakers."""
        CircuitBreaker._registry.clear()
        CircuitBreaker(name="breaker1")
        CircuitBreaker(name="breaker2")
        CircuitBreaker(name="breaker3")

        all_breakers = CircuitBreaker.get_all()
        assert len(all_breakers) == 3
        assert "breaker1" in all_breakers
        assert "breaker2" in all_breakers
        assert "breaker3" in all_breakers

    def test_reset_all_breakers(self):
        """Test resetting all circuit breakers."""
        CircuitBreaker._registry.clear()
        b1 = CircuitBreaker(name="reset1", failure_threshold=1)
        b2 = CircuitBreaker(name="reset2", failure_threshold=1)

        b1.record_failure()
        b2.record_failure()

        assert b1.state == CircuitState.OPEN
        assert b2.state == CircuitState.OPEN

        CircuitBreaker.reset_all()

        assert b1.state == CircuitState.CLOSED
        assert b2.state == CircuitState.CLOSED


class TestCircuitBreakerGetStats:
    """Tests for get_stats method."""

    def test_get_stats(self):
        """Test getting circuit breaker statistics."""
        CircuitBreaker._registry.clear()
        breaker = CircuitBreaker(
            name="stats_test",
            failure_threshold=5,
            reset_timeout=30.0
        )

        breaker.record_success()
        breaker.record_success()
        breaker.record_failure()

        stats = breaker.get_stats()

        assert stats["name"] == "stats_test"
        assert stats["state"] == "CLOSED"
        assert stats["total_calls"] == 3
        assert stats["successful_calls"] == 2
        assert stats["failed_calls"] == 1
        assert stats["failure_threshold"] == 5
        assert stats["reset_timeout"] == 30.0


class TestCircuitBreakerCallback:
    """Tests for state change callback."""

    def test_state_change_callback(self):
        """Test callback is invoked on state change."""
        CircuitBreaker._registry.clear()
        callback_called = []

        def on_change(old_state, new_state):
            callback_called.append((old_state, new_state))

        breaker = CircuitBreaker(
            name="callback_test",
            failure_threshold=2,
            on_state_change=on_change
        )

        breaker.record_failure()
        breaker.record_failure()

        assert len(callback_called) == 1
        assert callback_called[0] == (CircuitState.CLOSED, CircuitState.OPEN)

    def test_callback_exception_handled(self):
        """Test callback exceptions are handled gracefully."""
        CircuitBreaker._registry.clear()

        def bad_callback(old_state, new_state):
            raise RuntimeError("Callback error")

        breaker = CircuitBreaker(
            name="bad_callback_test",
            failure_threshold=1,
            on_state_change=bad_callback
        )

        # Should not raise even though callback fails
        breaker.record_failure()
        assert breaker.state == CircuitState.OPEN

