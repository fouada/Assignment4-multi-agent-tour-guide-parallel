"""
Timeout Pattern
===============

Ensures bounded execution time for operations.
Prevents hanging operations from consuming resources indefinitely.

Implementation:
- Uses threading for synchronous timeout
- Uses asyncio for async timeout
- Supports cancellation and cleanup

Example:
    @timeout(seconds=10)
    def slow_operation():
        # Must complete within 10 seconds
        return expensive_computation()
"""

from __future__ import annotations

import asyncio
import logging
import signal
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeout
from contextlib import contextmanager
from functools import wraps
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


class TimeoutError(Exception):
    """Raised when an operation times out."""

    def __init__(self, message: str, seconds: float):
        super().__init__(message)
        self.seconds = seconds


def with_timeout(
    func: Callable[..., Any],
    seconds: float,
    *args,
    **kwargs,
) -> Any:
    """
    Execute a function with a timeout.

    Uses a thread pool to execute the function and waits for the result
    with a timeout.

    Args:
        func: Function to execute
        seconds: Timeout in seconds
        *args, **kwargs: Arguments to pass to function

    Returns:
        Function result

    Raises:
        TimeoutError: If execution exceeds timeout
    """
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args, **kwargs)
        try:
            return future.result(timeout=seconds)
        except FuturesTimeout as err:
            raise TimeoutError(
                f"Operation timed out after {seconds} seconds",
                seconds,
            ) from err


def timeout(
    seconds: float,
    on_timeout: Callable[[], Any] | None = None,
) -> Callable[[F], F]:
    """
    Decorator to add timeout to a function.

    Args:
        seconds: Timeout in seconds
        on_timeout: Optional callback when timeout occurs

    Example:
        @timeout(seconds=10)
        def slow_api_call():
            return requests.get(slow_url)

        # With fallback
        @timeout(seconds=5, on_timeout=lambda: default_value)
        def get_data():
            return fetch_from_slow_service()
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return with_timeout(func, seconds, *args, **kwargs)
            except TimeoutError:
                if on_timeout:
                    return on_timeout()
                raise

        wrapper.timeout_seconds = seconds  # type: ignore
        return wrapper  # type: ignore

    return decorator


@contextmanager
def timeout_context(seconds: float):
    """
    Context manager for timeout using signals (Unix only).

    Note: Only works on main thread and Unix-like systems.
    For cross-platform timeout, use the timeout decorator instead.

    Example:
        with timeout_context(10):
            slow_operation()
    """
    def handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds} seconds", seconds)

    # Set signal handler
    old_handler = signal.signal(signal.SIGALRM, handler)
    signal.setitimer(signal.ITIMER_REAL, seconds)

    try:
        yield
    finally:
        # Reset signal
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old_handler)


# ============== Async Timeout ==============

async def async_with_timeout(
    coro,
    seconds: float,
) -> Any:
    """
    Execute an async coroutine with a timeout.

    Args:
        coro: Coroutine to execute
        seconds: Timeout in seconds

    Returns:
        Coroutine result

    Raises:
        TimeoutError: If execution exceeds timeout
    """
    try:
        return await asyncio.wait_for(coro, timeout=seconds)
    except asyncio.TimeoutError as err:
        raise TimeoutError(
            f"Async operation timed out after {seconds} seconds",
            seconds,
        ) from err


def async_timeout(seconds: float) -> Callable:
    """
    Decorator to add timeout to an async function.

    Example:
        @async_timeout(seconds=10)
        async def slow_async_call():
            return await aiohttp.get(slow_url)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await async_with_timeout(
                func(*args, **kwargs),
                seconds,
            )
        return wrapper
    return decorator

