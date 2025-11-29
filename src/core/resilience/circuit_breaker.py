"""
Circuit Breaker Pattern
=======================

Prevents cascading failures by failing fast when a service is unhealthy.

State Machine:
    CLOSED -> OPEN (after failure_threshold failures)
    OPEN -> HALF_OPEN (after reset_timeout)
    HALF_OPEN -> CLOSED (on success)
    HALF_OPEN -> OPEN (on failure)

Academic Reference:
    - Nygard, "Release It!" (Circuit Breaker, p. 97)
    - Netflix Hystrix documentation

Example:
    # Decorator
    @circuit_breaker(failure_threshold=5, reset_timeout=30)
    def call_api():
        return requests.get("https://api.example.com")

    # Context manager
    cb = CircuitBreaker(failure_threshold=5)
    with cb:
        result = call_api()
"""

from __future__ import annotations

import logging
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from functools import wraps
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = auto()  # Normal operation, requests allowed
    OPEN = auto()  # Failing fast, requests blocked
    HALF_OPEN = auto()  # Testing if service recovered


class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is open."""

    def __init__(self, message: str, circuit_name: str, opens_at: datetime):
        super().__init__(message)
        self.circuit_name = circuit_name
        self.opens_at = opens_at


@dataclass
class CircuitBreakerStats:
    """Statistics for a circuit breaker."""

    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rejected_calls: int = 0
    state_changes: list[dict[str, Any]] = field(default_factory=list)
    last_failure: datetime | None = None
    last_success: datetime | None = None

    @property
    def success_rate(self) -> float:
        if self.total_calls == 0:
            return 1.0
        return self.successful_calls / self.total_calls

    @property
    def failure_rate(self) -> float:
        if self.total_calls == 0:
            return 0.0
        return self.failed_calls / self.total_calls


class CircuitBreaker:
    """
    Circuit Breaker implementation with configurable thresholds.

    Parameters:
        name: Identifier for this circuit breaker
        failure_threshold: Number of failures to open circuit
        success_threshold: Successes in HALF_OPEN to close circuit
        reset_timeout: Seconds to wait before trying again (OPEN -> HALF_OPEN)
        excluded_exceptions: Exceptions that don't count as failures

    Example:
        cb = CircuitBreaker(
            name="external_api",
            failure_threshold=5,
            reset_timeout=30,
        )

        with cb:
            result = call_api()

        # Or manually:
        if cb.allow_request():
            try:
                result = call_api()
                cb.record_success()
            except Exception as e:
                cb.record_failure(e)
                raise
    """

    # Class-level registry for all circuit breakers
    _registry: dict[str, CircuitBreaker] = {}
    _lock = threading.Lock()

    def __init__(
        self,
        name: str = "default",
        failure_threshold: int = 5,
        success_threshold: int = 2,
        reset_timeout: float = 30.0,
        excluded_exceptions: set[type[Exception]] | None = None,
        on_state_change: Callable[[CircuitState, CircuitState], None] | None = None,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.reset_timeout = reset_timeout
        self.excluded_exceptions = excluded_exceptions or set()
        self.on_state_change = on_state_change

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: float | None = None
        self._instance_lock = threading.RLock()

        # Statistics
        self.stats = CircuitBreakerStats()

        # Register
        with CircuitBreaker._lock:
            CircuitBreaker._registry[name] = self

    @property
    def state(self) -> CircuitState:
        """Get current state, transitioning if necessary."""
        with self._instance_lock:
            if self._state == CircuitState.OPEN:
                if self._should_try_reset():
                    self._transition_to(CircuitState.HALF_OPEN)
            return self._state

    @property
    def is_closed(self) -> bool:
        return self.state == CircuitState.CLOSED

    @property
    def is_open(self) -> bool:
        return self.state == CircuitState.OPEN

    def allow_request(self) -> bool:
        """Check if a request should be allowed."""
        state = self.state

        if state == CircuitState.CLOSED:
            return True
        elif state == CircuitState.HALF_OPEN:
            return True  # Allow test requests
        else:  # OPEN
            return False

    def record_success(self) -> None:
        """Record a successful call."""
        with self._instance_lock:
            self.stats.total_calls += 1
            self.stats.successful_calls += 1
            self.stats.last_success = datetime.now()

            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.success_threshold:
                    self._transition_to(CircuitState.CLOSED)
            elif self._state == CircuitState.CLOSED:
                # Reset failure count on success
                self._failure_count = 0

    def record_failure(self, exception: Exception | None = None) -> None:
        """Record a failed call."""
        # Check if exception is excluded
        if exception and type(exception) in self.excluded_exceptions:
            logger.debug(f"Excluded exception: {type(exception).__name__}")
            return

        with self._instance_lock:
            self.stats.total_calls += 1
            self.stats.failed_calls += 1
            self.stats.last_failure = datetime.now()
            self._last_failure_time = time.time()

            if self._state == CircuitState.HALF_OPEN:
                # Failed during test, go back to OPEN
                self._transition_to(CircuitState.OPEN)
            elif self._state == CircuitState.CLOSED:
                self._failure_count += 1
                if self._failure_count >= self.failure_threshold:
                    self._transition_to(CircuitState.OPEN)

    def _should_try_reset(self) -> bool:
        """Check if enough time has passed to try resetting."""
        if self._last_failure_time is None:
            return True
        return time.time() - self._last_failure_time >= self.reset_timeout

    def _transition_to(self, new_state: CircuitState) -> None:
        """Transition to a new state."""
        old_state = self._state
        self._state = new_state

        # Reset counters on transition
        if new_state == CircuitState.CLOSED:
            self._failure_count = 0
            self._success_count = 0
        elif new_state == CircuitState.HALF_OPEN:
            self._success_count = 0

        # Log state change
        self.stats.state_changes.append(
            {
                "from": old_state.name,
                "to": new_state.name,
                "timestamp": datetime.now().isoformat(),
            }
        )

        logger.info(
            f"Circuit breaker '{self.name}' state change: "
            f"{old_state.name} -> {new_state.name}"
        )

        # Callback
        if self.on_state_change:
            try:
                self.on_state_change(old_state, new_state)
            except Exception as e:
                logger.error(f"State change callback error: {e}")

    def reset(self) -> None:
        """Manually reset the circuit breaker to CLOSED state."""
        with self._instance_lock:
            self._transition_to(CircuitState.CLOSED)

    def trip(self) -> None:
        """Manually trip the circuit breaker to OPEN state."""
        with self._instance_lock:
            self._last_failure_time = time.time()
            self._transition_to(CircuitState.OPEN)

    # ==================== Context Manager ====================

    def __enter__(self) -> CircuitBreaker:
        if not self.allow_request():
            self.stats.rejected_calls += 1
            raise CircuitBreakerOpen(
                f"Circuit breaker '{self.name}' is open",
                self.name,
                datetime.fromtimestamp(self._last_failure_time + self.reset_timeout)
                if self._last_failure_time
                else datetime.now(),
            )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is None:
            self.record_success()
        elif exc_type is not CircuitBreakerOpen:
            self.record_failure(exc_val)

    # ==================== Class Methods ====================

    @classmethod
    def get(cls, name: str) -> CircuitBreaker | None:
        """Get a circuit breaker by name."""
        return cls._registry.get(name)

    @classmethod
    def get_all(cls) -> dict[str, CircuitBreaker]:
        """Get all registered circuit breakers."""
        return dict(cls._registry)

    @classmethod
    def reset_all(cls) -> None:
        """Reset all circuit breakers."""
        for cb in cls._registry.values():
            cb.reset()

    def get_stats(self) -> dict[str, Any]:
        """Get circuit breaker statistics."""
        return {
            "name": self.name,
            "state": self.state.name,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "failure_threshold": self.failure_threshold,
            "reset_timeout": self.reset_timeout,
            **{
                "total_calls": self.stats.total_calls,
                "successful_calls": self.stats.successful_calls,
                "failed_calls": self.stats.failed_calls,
                "rejected_calls": self.stats.rejected_calls,
                "success_rate": self.stats.success_rate,
                "failure_rate": self.stats.failure_rate,
            },
        }


def circuit_breaker(
    name: str | None = None,
    failure_threshold: int = 5,
    success_threshold: int = 2,
    reset_timeout: float = 30.0,
    excluded_exceptions: set[type[Exception]] | None = None,
) -> Callable[[F], F]:
    """
    Decorator to wrap a function with a circuit breaker.

    Args:
        name: Circuit breaker name (defaults to function name)
        failure_threshold: Failures before opening circuit
        success_threshold: Successes in HALF_OPEN to close
        reset_timeout: Seconds before trying again
        excluded_exceptions: Exceptions that don't count as failures

    Example:
        @circuit_breaker(failure_threshold=5, reset_timeout=30)
        def call_external_api():
            return requests.get("https://api.example.com")
    """

    def decorator(func: F) -> F:
        cb_name = name or func.__name__
        cb = CircuitBreaker(
            name=cb_name,
            failure_threshold=failure_threshold,
            success_threshold=success_threshold,
            reset_timeout=reset_timeout,
            excluded_exceptions=excluded_exceptions,
        )

        @wraps(func)
        def wrapper(*args, **kwargs):
            with cb:
                return func(*args, **kwargs)

        # Attach circuit breaker reference
        wrapper.circuit_breaker = cb  # type: ignore

        return wrapper  # type: ignore

    return decorator
