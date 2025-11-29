"""
Retry Pattern with Exponential Backoff
======================================

Automatically retry failed operations with configurable backoff.

Features:
- Exponential backoff with jitter
- Configurable retry conditions
- Exception filtering
- Retry hooks for logging/metrics

Academic Reference:
    - AWS Architecture Blog, "Exponential Backoff and Jitter"
    - Google Cloud, "Implementing retry with exponential backoff"

Example:
    @retry(max_attempts=3, backoff_factor=2, max_delay=30)
    def flaky_api_call():
        return requests.get("https://flaky-api.example.com")
"""

from __future__ import annotations

import logging
import random
import time
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from typing import (
    Any,
    TypeVar,
)

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


class RetryError(Exception):
    """Raised when all retry attempts are exhausted."""

    def __init__(
        self,
        message: str,
        attempts: int,
        last_exception: Exception,
    ):
        super().__init__(message)
        self.attempts = attempts
        self.last_exception = last_exception


@dataclass
class RetryPolicy:
    """
    Configuration for retry behavior.

    Attributes:
        max_attempts: Maximum number of attempts (including first)
        backoff_factor: Multiplier for exponential backoff
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        jitter: Add randomness to delay (0 = no jitter, 1 = full jitter)
        retryable_exceptions: Exception types to retry (None = retry all)
        non_retryable_exceptions: Exception types to NOT retry
        retry_on_result: Function to check if result should be retried
        on_retry: Callback for each retry attempt
    """

    max_attempts: int = 3
    backoff_factor: float = 2.0
    initial_delay: float = 1.0
    max_delay: float = 60.0
    jitter: float = 0.1
    retryable_exceptions: set[type[Exception]] | None = None
    non_retryable_exceptions: set[type[Exception]] | None = None
    retry_on_result: Callable[[Any], bool] | None = None
    on_retry: Callable[[int, Exception, float], None] | None = None

    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for a given attempt number.

        Uses exponential backoff with optional jitter:
        delay = min(initial_delay * (backoff_factor ^ attempt), max_delay)

        With jitter (decorrelated jitter algorithm):
        delay = random(0, delay * (1 + jitter))
        """
        # Exponential backoff
        delay = self.initial_delay * (self.backoff_factor**attempt)

        # Cap at max delay
        delay = min(delay, self.max_delay)

        # Add jitter
        if self.jitter > 0:
            jitter_range = delay * self.jitter
            delay = delay + random.uniform(-jitter_range, jitter_range)
            delay = max(0, delay)  # Ensure non-negative

        return delay

    def should_retry(self, exception: Exception) -> bool:
        """Check if an exception should trigger a retry."""
        exc_type = type(exception)

        # Check non-retryable first
        if self.non_retryable_exceptions and exc_type in self.non_retryable_exceptions:
            return False

        # Check retryable
        if self.retryable_exceptions:
            return exc_type in self.retryable_exceptions

        # Default: retry all exceptions
        return True


def with_retry(
    func: Callable[..., Any],
    policy: RetryPolicy,
    *args,
    **kwargs,
) -> Any:
    """
    Execute a function with retry logic.

    Args:
        func: Function to execute
        policy: Retry policy configuration
        *args, **kwargs: Arguments to pass to function

    Returns:
        Function result

    Raises:
        RetryError: If all attempts fail
    """
    last_exception: Exception | None = None

    for attempt in range(policy.max_attempts):
        try:
            result = func(*args, **kwargs)

            # Check if result should be retried
            if policy.retry_on_result and policy.retry_on_result(result):
                if attempt < policy.max_attempts - 1:
                    delay = policy.calculate_delay(attempt)
                    logger.debug(
                        f"Retrying due to result, attempt {attempt + 1}/{policy.max_attempts}, "
                        f"waiting {delay:.2f}s"
                    )
                    time.sleep(delay)
                    continue

            return result

        except Exception as e:
            last_exception = e

            # Check if should retry this exception
            if not policy.should_retry(e):
                raise

            # Check if we have attempts left
            if attempt < policy.max_attempts - 1:
                delay = policy.calculate_delay(attempt)

                logger.warning(
                    f"Attempt {attempt + 1}/{policy.max_attempts} failed: {e}, "
                    f"retrying in {delay:.2f}s"
                )

                # Call retry hook
                if policy.on_retry:
                    try:
                        policy.on_retry(attempt + 1, e, delay)
                    except Exception:
                        pass

                time.sleep(delay)
            else:
                logger.error(
                    f"All {policy.max_attempts} attempts failed, last error: {e}"
                )

    # All attempts exhausted
    raise RetryError(
        f"All {policy.max_attempts} attempts failed",
        policy.max_attempts,
        last_exception or Exception("Unknown error"),
    )


def retry(
    max_attempts: int = 3,
    backoff_factor: float = 2.0,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    jitter: float = 0.1,
    retryable_exceptions: set[type[Exception]] | None = None,
    non_retryable_exceptions: set[type[Exception]] | None = None,
    retry_on_result: Callable[[Any], bool] | None = None,
    on_retry: Callable[[int, Exception, float], None] | None = None,
) -> Callable[[F], F]:
    """
    Decorator to add retry logic to a function.

    Args:
        max_attempts: Maximum retry attempts
        backoff_factor: Multiplier for exponential backoff
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay cap
        jitter: Randomness factor (0-1)
        retryable_exceptions: Only retry these exceptions
        non_retryable_exceptions: Never retry these exceptions
        retry_on_result: Retry if this function returns True for result
        on_retry: Callback for each retry

    Example:
        @retry(max_attempts=3, backoff_factor=2)
        def flaky_function():
            return call_unreliable_api()

        # With exception filtering
        @retry(
            max_attempts=5,
            retryable_exceptions={TimeoutError, ConnectionError},
            non_retryable_exceptions={AuthenticationError},
        )
        def api_call():
            return requests.get(url)
    """
    policy = RetryPolicy(
        max_attempts=max_attempts,
        backoff_factor=backoff_factor,
        initial_delay=initial_delay,
        max_delay=max_delay,
        jitter=jitter,
        retryable_exceptions=retryable_exceptions,
        non_retryable_exceptions=non_retryable_exceptions,
        retry_on_result=retry_on_result,
        on_retry=on_retry,
    )

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return with_retry(func, policy, *args, **kwargs)

        # Attach policy for inspection
        wrapper.retry_policy = policy  # type: ignore

        return wrapper  # type: ignore

    return decorator


# ============== Common Retry Policies ==============

AGGRESSIVE_RETRY = RetryPolicy(
    max_attempts=5,
    backoff_factor=1.5,
    initial_delay=0.5,
    max_delay=10.0,
    jitter=0.2,
)

CONSERVATIVE_RETRY = RetryPolicy(
    max_attempts=3,
    backoff_factor=3.0,
    initial_delay=2.0,
    max_delay=60.0,
    jitter=0.1,
)

NO_RETRY = RetryPolicy(max_attempts=1)
