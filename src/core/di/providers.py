"""
Dependency Providers
====================

Provider implementations for different dependency creation strategies.

Example:
    # Singleton provider
    provider = SingletonProvider(lambda: ExpensiveService())
    instance = provider.get()  # Same instance every time

    # Factory provider
    provider = FactoryProvider(lambda ctx: UserService(ctx.user_id))
    instance = provider.get(context)
"""

from __future__ import annotations

import logging
import threading
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Generic, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class Provider(ABC, Generic[T]):
    """
    Abstract base class for dependency providers.

    A provider knows how to create instances of a dependency.
    """

    @abstractmethod
    def get(self, *args, **kwargs) -> T:
        """Get an instance from this provider."""
        pass

    @abstractmethod
    def dispose(self) -> None:
        """Dispose of any held resources."""
        pass


class SingletonProvider(Provider[T]):
    """
    Provider that creates a single instance.

    Thread-safe lazy initialization.
    """

    def __init__(self, factory: Callable[[], T]):
        self._factory = factory
        self._instance: T | None = None
        self._lock = threading.Lock()

    def get(self, *args, **kwargs) -> T:
        if self._instance is None:
            with self._lock:
                if self._instance is None:
                    self._instance = self._factory()
                    logger.debug(f"Created singleton: {type(self._instance)}")
        return self._instance

    def dispose(self) -> None:
        with self._lock:
            if self._instance is not None:
                if hasattr(self._instance, "dispose"):
                    self._instance.dispose()
                elif hasattr(self._instance, "close"):
                    self._instance.close()
                self._instance = None


class TransientProvider(Provider[T]):
    """
    Provider that creates a new instance each time.
    """

    def __init__(self, factory: Callable[..., T]):
        self._factory = factory

    def get(self, *args, **kwargs) -> T:
        instance = self._factory(*args, **kwargs)
        logger.debug(f"Created transient: {type(instance)}")
        return instance

    def dispose(self) -> None:
        pass  # Nothing to dispose


class FactoryProvider(Provider[T]):
    """
    Provider that uses a factory function with context.

    The factory receives any arguments passed to get().
    """

    def __init__(self, factory: Callable[..., T]):
        self._factory = factory

    def get(self, *args, **kwargs) -> T:
        return self._factory(*args, **kwargs)

    def dispose(self) -> None:
        pass


class ValueProvider(Provider[T]):
    """
    Provider that returns a pre-existing value.
    """

    def __init__(self, value: T):
        self._value = value

    def get(self, *args, **kwargs) -> T:
        return self._value

    def dispose(self) -> None:
        if hasattr(self._value, "dispose"):
            self._value.dispose()
        elif hasattr(self._value, "close"):
            self._value.close()


class LazyProvider(Provider[T]):
    """
    Provider with lazy initialization.

    Delays creation until first access.
    """

    def __init__(self, factory: Callable[[], T]):
        self._factory = factory
        self._instance: T | None = None
        self._initialized = False
        self._lock = threading.Lock()

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    def get(self, *args, **kwargs) -> T:
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    self._instance = self._factory()
                    self._initialized = True
        return self._instance  # type: ignore

    def dispose(self) -> None:
        with self._lock:
            if self._initialized and self._instance is not None:
                if hasattr(self._instance, "dispose"):
                    self._instance.dispose()
                elif hasattr(self._instance, "close"):
                    self._instance.close()
                self._instance = None
                self._initialized = False


class PooledProvider(Provider[T]):
    """
    Provider that maintains a pool of instances.

    Useful for expensive-to-create objects like database connections.
    """

    def __init__(
        self,
        factory: Callable[[], T],
        pool_size: int = 10,
    ):
        self._factory = factory
        self._pool_size = pool_size
        self._pool: list[T] = []
        self._in_use: set[int] = set()
        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)

    def get(self, *args, timeout: float | None = None, **kwargs) -> T:
        with self._condition:
            # Try to get from pool
            while True:
                for i, instance in enumerate(self._pool):
                    if i not in self._in_use:
                        self._in_use.add(i)
                        return instance

                # Create new if pool not full
                if len(self._pool) < self._pool_size:
                    instance = self._factory()
                    idx = len(self._pool)
                    self._pool.append(instance)
                    self._in_use.add(idx)
                    return instance

                # Wait for return
                if not self._condition.wait(timeout=timeout):
                    raise TimeoutError("Could not acquire pooled instance")

    def release(self, instance: T) -> None:
        """Return an instance to the pool."""
        with self._condition:
            try:
                idx = self._pool.index(instance)
                self._in_use.discard(idx)
                self._condition.notify()
            except ValueError:
                pass  # Not from this pool

    def dispose(self) -> None:
        with self._lock:
            for instance in self._pool:
                if hasattr(instance, "dispose"):
                    instance.dispose()
                elif hasattr(instance, "close"):
                    instance.close()
            self._pool.clear()
            self._in_use.clear()
