"""
Retry mechanism with exponential backoff.

This module provides retry logic for agent API calls:
- Configurable number of retries (default: 3)
- Exponential backoff (1s, 2s, 4s)
- Jitter to avoid thundering herd
- Logging of retry attempts
"""

import functools
import random
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

from src.utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""

    max_retries: int = 3
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 30.0
    exponential_base: float = 2.0
    jitter: bool = True
    retryable_exceptions: tuple = (Exception,)


class RetryExhaustedError(Exception):
    """Raised when all retry attempts have failed."""

    def __init__(self, agent_type: str, attempts: int, last_error: str):
        self.agent_type = agent_type
        self.attempts = attempts
        self.last_error = last_error
        super().__init__(
            f"[{agent_type}] All {attempts} retry attempts failed. Last error: {last_error}"
        )


def calculate_backoff_delay(
    attempt: int,
    base_delay: float = 1.0,
    exponential_base: float = 2.0,
    max_delay: float = 30.0,
    jitter: bool = True,
) -> float:
    """
    Calculate delay for retry attempt using exponential backoff.

    Formula: delay = base_delay * (exponential_base ^ attempt) + jitter

    Args:
        attempt: Current attempt number (0-indexed)
        base_delay: Base delay in seconds
        exponential_base: Multiplier for exponential growth
        max_delay: Maximum delay cap
        jitter: Add random jitter to prevent thundering herd

    Returns:
        Delay in seconds

    Examples:
        attempt=0: 1s * 2^0 = 1s
        attempt=1: 1s * 2^1 = 2s
        attempt=2: 1s * 2^2 = 4s
        attempt=3: 1s * 2^3 = 8s (capped at max_delay if exceeded)
    """
    delay = base_delay * (exponential_base**attempt)
    delay = min(delay, max_delay)

    if jitter:
        # Add random jitter between 0-25% of delay
        jitter_amount = delay * random.uniform(0, 0.25)
        delay += jitter_amount

    return delay


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    exponential_base: float = 2.0,
    max_delay: float = 30.0,
    retryable_exceptions: tuple = (Exception,),
    on_retry: Callable[[int, Exception], None] | None = None,
):
    """
    Decorator for retrying functions with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay between retries in seconds
        exponential_base: Multiplier for exponential backoff
        max_delay: Maximum delay between retries
        retryable_exceptions: Tuple of exceptions that trigger retry
        on_retry: Callback function called on each retry (attempt, exception)

    Usage:
        @retry_with_backoff(max_retries=3, base_delay=1.0)
        def call_api():
            return requests.get(url)
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(max_retries + 1):  # +1 for initial attempt
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e

                    if attempt < max_retries:
                        delay = calculate_backoff_delay(
                            attempt, base_delay, exponential_base, max_delay
                        )

                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed: {e}. "
                            f"Retrying in {delay:.2f}s..."
                        )

                        if on_retry:
                            on_retry(attempt, e)

                        time.sleep(delay)
                    else:
                        logger.error(
                            f"All {max_retries + 1} attempts failed. Last error: {e}"
                        )

            raise last_exception

        return wrapper

    return decorator


class RetryExecutor:
    """
    Class-based retry executor for more control.

    Usage:
        executor = RetryExecutor(max_retries=3)
        result = executor.execute(lambda: api_call(), agent_type="video")
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        exponential_base: float = 2.0,
        max_delay: float = 30.0,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.exponential_base = exponential_base
        self.max_delay = max_delay
        self.attempts_made = 0
        self.total_wait_time = 0.0

    def execute(
        self,
        func: Callable[[], T],
        agent_type: str = "unknown",
        point_id: str = "-",
    ) -> T:
        """
        Execute function with retry logic.

        Args:
            func: Function to execute
            agent_type: Agent type for logging
            point_id: Point ID for logging

        Returns:
            Result of successful function execution

        Raises:
            RetryExhaustedError: If all retries fail
        """
        last_error = None
        self.attempts_made = 0
        self.total_wait_time = 0.0

        for attempt in range(self.max_retries + 1):
            self.attempts_made = attempt + 1

            try:
                logger.debug(
                    f"[{point_id}][{agent_type}] Attempt {attempt + 1}/{self.max_retries + 1}"
                )
                return func()

            except Exception as e:
                last_error = str(e)

                if attempt < self.max_retries:
                    delay = calculate_backoff_delay(
                        attempt, self.base_delay, self.exponential_base, self.max_delay
                    )
                    self.total_wait_time += delay

                    logger.warning(
                        f"[{point_id}][{agent_type}] Attempt {attempt + 1} failed: {e}. "
                        f"Waiting {delay:.2f}s before retry..."
                    )

                    time.sleep(delay)
                else:
                    logger.error(
                        f"[{point_id}][{agent_type}] All {self.max_retries + 1} attempts failed"
                    )

        raise RetryExhaustedError(agent_type, self.attempts_made, last_error)

    def get_stats(self) -> dict:
        """Get retry statistics."""
        return {
            "attempts_made": self.attempts_made,
            "total_wait_time_seconds": self.total_wait_time,
        }


# ============================================================================
# RETRY TIMING CALCULATION
# ============================================================================
"""
Timing Analysis for 3 Retries with Exponential Backoff:

  Attempt 1: Immediate
  Attempt 2: After 1s delay (1s total)
  Attempt 3: After 2s delay (3s total)
  Attempt 4: After 4s delay (7s total) - if max_retries=3

  With jitter (0-25%):
  - Attempt 2: 1.0s - 1.25s
  - Attempt 3: 2.0s - 2.5s
  - Attempt 4: 4.0s - 5.0s

  Total worst case with jitter: ~8.75s per agent

Combined with Queue Timeouts:
  - Agent retries: up to ~9s per agent (worst case)
  - Queue soft timeout: 15s (proceed with 2/3)
  - Queue hard timeout: 30s (proceed with 1/3)

Timeline Example:

  0s     Agent starts, Attempt 1
  0.5s   Attempt 1 fails
  0.5s   Wait 1s (backoff)
  1.5s   Attempt 2
  2s     Attempt 2 fails
  2s     Wait 2s (backoff)
  4s     Attempt 3
  4.5s   Attempt 3 fails
  4.5s   Wait 4s (backoff)
  8.5s   Attempt 4 (final)
  9s     Attempt 4 fails → Report failure to queue

Queue then decides:
  - If other 2 agents succeeded: Proceed with 2/3
  - If only 1 agent succeeded: Wait until 30s, then proceed with 1/3
"""
