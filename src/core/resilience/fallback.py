"""
Fallback Pattern
================

Provides graceful degradation when primary operations fail.
Returns alternative values or executes backup logic.

Features:
- Static fallback values
- Dynamic fallback functions
- Chained fallbacks
- Fallback caching

Example:
    @fallback(default_value=cached_data)
    def get_fresh_data():
        return api.fetch_latest()

    @fallback(fallback_fn=get_cached_version)
    def get_data():
        return api.fetch()
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from typing import Any, Generic, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])


@dataclass
class FallbackStats:
    """Statistics for fallback usage."""

    total_calls: int = 0
    primary_successes: int = 0
    fallback_activations: int = 0
    fallback_failures: int = 0


class Fallback(Generic[T]):
    """
    Fallback handler for graceful degradation.

    Provides multiple fallback strategies:
    1. Static value: Return a fixed default value
    2. Fallback function: Call an alternative function
    3. Chained fallbacks: Try multiple fallbacks in order

    Example:
        fallback = Fallback(
            default_value={"status": "unknown"},
            fallback_fn=get_cached_status,
        )

        result = fallback.execute(get_live_status)
    """

    def __init__(
        self,
        default_value: T | None = None,
        fallback_fn: Callable[..., T] | None = None,
        fallback_chain: list[Callable[..., T]] | None = None,
        exceptions: list[type[Exception]] | None = None,
        log_fallback: bool = True,
    ):
        """
        Initialize fallback handler.

        Args:
            default_value: Value to return on failure
            fallback_fn: Function to call on failure
            fallback_chain: List of fallback functions to try in order
            exceptions: Exception types to catch (None = all)
            log_fallback: Whether to log when fallback is used
        """
        self.default_value = default_value
        self.fallback_fn = fallback_fn
        self.fallback_chain = fallback_chain or []
        self.exceptions = tuple(exceptions) if exceptions else (Exception,)
        self.log_fallback = log_fallback

        self.stats = FallbackStats()

    def execute(
        self,
        primary_fn: Callable[..., T],
        *args,
        **kwargs,
    ) -> T:
        """
        Execute primary function with fallback support.

        Args:
            primary_fn: Primary function to execute
            *args, **kwargs: Function arguments

        Returns:
            Primary result or fallback value
        """
        self.stats.total_calls += 1

        # Try primary
        try:
            result = primary_fn(*args, **kwargs)
            self.stats.primary_successes += 1
            return result
        except self.exceptions as e:
            if self.log_fallback:
                logger.warning(
                    f"Primary function {primary_fn.__name__} failed: {e}, "
                    f"using fallback"
                )
            self.stats.fallback_activations += 1

        # Try fallback function
        if self.fallback_fn:
            try:
                return self.fallback_fn(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Fallback function failed: {e}")

        # Try fallback chain
        for fallback_fn in self.fallback_chain:
            try:
                return fallback_fn(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Chained fallback {fallback_fn.__name__} failed: {e}")

        # Return default value
        if self.default_value is not None:
            return self.default_value

        # All fallbacks failed
        self.stats.fallback_failures += 1
        raise RuntimeError("All fallbacks failed and no default value provided")


def fallback(
    default_value: Any | None = None,
    fallback_fn: Callable | None = None,
    fallback_chain: list[Callable] | None = None,
    exceptions: list[type[Exception]] | None = None,
    log_fallback: bool = True,
) -> Callable[[F], F]:
    """
    Decorator to add fallback support to a function.

    Args:
        default_value: Value to return on failure
        fallback_fn: Alternative function to call
        fallback_chain: List of fallbacks to try
        exceptions: Exception types to catch
        log_fallback: Log when fallback is used

    Example:
        @fallback(default_value="Unknown")
        def get_user_name(user_id):
            return api.get_user(user_id).name

        @fallback(fallback_fn=get_from_cache)
        def get_data():
            return fetch_live_data()
    """
    fb = Fallback(
        default_value=default_value,
        fallback_fn=fallback_fn,
        fallback_chain=fallback_chain,
        exceptions=exceptions,
        log_fallback=log_fallback,
    )

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return fb.execute(func, *args, **kwargs)

        wrapper.fallback_handler = fb  # type: ignore
        return wrapper  # type: ignore

    return decorator


# ============== Specialized Fallbacks ==============


def cache_fallback(
    cache_key_fn: Callable[..., str],
    cache_get_fn: Callable[[str], Any | None],
    cache_set_fn: Callable[[str, Any], None],
    ttl: int | None = None,
) -> Callable[[F], F]:
    """
    Decorator that falls back to cached value and caches successful results.

    Args:
        cache_key_fn: Function to generate cache key from args
        cache_get_fn: Function to get value from cache
        cache_set_fn: Function to set value in cache
        ttl: Cache TTL in seconds (if cache supports it)

    Example:
        @cache_fallback(
            cache_key_fn=lambda user_id: f"user:{user_id}",
            cache_get_fn=redis.get,
            cache_set_fn=redis.set,
        )
        def get_user(user_id):
            return api.get_user(user_id)
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = cache_key_fn(*args, **kwargs)

            try:
                # Try primary
                result = func(*args, **kwargs)

                # Cache successful result
                try:
                    cache_set_fn(cache_key, result)
                except Exception as e:
                    logger.warning(f"Failed to cache result: {e}")

                return result

            except Exception as e:
                logger.warning(f"Primary failed, trying cache: {e}")

                # Try cache
                cached = cache_get_fn(cache_key)
                if cached is not None:
                    return cached

                raise

        return wrapper  # type: ignore

    return decorator
