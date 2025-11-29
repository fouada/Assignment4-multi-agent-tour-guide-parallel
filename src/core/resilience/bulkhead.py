"""
Bulkhead Pattern
================

Isolates components to prevent cascading failures.
Limits concurrent access to protected resources.

Named after ship bulkheads that prevent flooding from spreading.

Implementation:
- Semaphore-based concurrency limiting
- Thread pool isolation
- Queue-based overflow handling

Academic Reference:
    - Nygard, "Release It!" (Bulkheads, p. 104)
    - Netflix Hystrix, "Thread Pool Isolation"

Example:
    # Limit concurrent API calls
    @bulkhead(max_concurrent=10, max_queued=100)
    def call_external_api():
        return requests.get(api_url)
"""

from __future__ import annotations

import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Dict, Optional, TypeVar
import logging

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


class BulkheadFull(Exception):
    """Raised when bulkhead capacity is exceeded."""
    
    def __init__(self, message: str, bulkhead_name: str):
        super().__init__(message)
        self.bulkhead_name = bulkhead_name


@dataclass
class BulkheadStats:
    """Statistics for a bulkhead."""
    total_calls: int = 0
    successful_calls: int = 0
    rejected_calls: int = 0
    current_concurrent: int = 0
    current_queued: int = 0
    max_concurrent_reached: int = 0
    
    @property
    def acceptance_rate(self) -> float:
        if self.total_calls == 0:
            return 1.0
        return self.successful_calls / self.total_calls


class Bulkhead:
    """
    Bulkhead implementation using semaphores.
    
    Parameters:
        name: Identifier for this bulkhead
        max_concurrent: Maximum concurrent executions
        max_queued: Maximum queued requests (0 = no queue)
        timeout: Wait timeout for queued requests
        
    Example:
        bulkhead = Bulkhead(
            name="api_calls",
            max_concurrent=10,
            max_queued=50,
            timeout=30.0,
        )
        
        with bulkhead:
            result = call_api()
    """
    
    _registry: Dict[str, "Bulkhead"] = {}
    _lock = threading.Lock()
    
    def __init__(
        self,
        name: str = "default",
        max_concurrent: int = 10,
        max_queued: int = 0,
        timeout: Optional[float] = None,
    ):
        self.name = name
        self.max_concurrent = max_concurrent
        self.max_queued = max_queued
        self.timeout = timeout
        
        self._semaphore = threading.Semaphore(max_concurrent)
        self._queue_semaphore = threading.Semaphore(max_queued) if max_queued > 0 else None
        self._stats_lock = threading.Lock()
        self._current_concurrent = 0
        self._current_queued = 0
        
        self.stats = BulkheadStats()
        
        # Register
        with Bulkhead._lock:
            Bulkhead._registry[name] = self
    
    def acquire(self, timeout: Optional[float] = None) -> bool:
        """
        Acquire a permit from the bulkhead.
        
        Returns True if permit acquired, False if rejected.
        """
        timeout = timeout or self.timeout
        
        with self._stats_lock:
            self.stats.total_calls += 1
        
        # Try to acquire immediately
        acquired = self._semaphore.acquire(blocking=False)
        
        if acquired:
            with self._stats_lock:
                self._current_concurrent += 1
                self.stats.max_concurrent_reached = max(
                    self.stats.max_concurrent_reached,
                    self._current_concurrent,
                )
            return True
        
        # No queue or queue full
        if not self._queue_semaphore or not self._queue_semaphore.acquire(blocking=False):
            with self._stats_lock:
                self.stats.rejected_calls += 1
            return False
        
        # We're in the queue
        with self._stats_lock:
            self._current_queued += 1
        
        try:
            # Wait for permit with timeout
            acquired = self._semaphore.acquire(timeout=timeout)
            
            if acquired:
                with self._stats_lock:
                    self._current_concurrent += 1
                    self._current_queued -= 1
                return True
            else:
                with self._stats_lock:
                    self._current_queued -= 1
                    self.stats.rejected_calls += 1
                return False
        finally:
            self._queue_semaphore.release()
    
    def release(self) -> None:
        """Release a permit back to the bulkhead."""
        with self._stats_lock:
            self._current_concurrent -= 1
            self.stats.successful_calls += 1
        self._semaphore.release()
    
    def __enter__(self) -> "Bulkhead":
        if not self.acquire():
            raise BulkheadFull(
                f"Bulkhead '{self.name}' is full",
                self.name,
            )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.release()
    
    @property
    def available_permits(self) -> int:
        """Number of available permits."""
        return self.max_concurrent - self._current_concurrent
    
    @property
    def queued_count(self) -> int:
        """Number of queued requests."""
        return self._current_queued
    
    def get_stats(self) -> Dict[str, Any]:
        """Get bulkhead statistics."""
        return {
            "name": self.name,
            "max_concurrent": self.max_concurrent,
            "max_queued": self.max_queued,
            "current_concurrent": self._current_concurrent,
            "current_queued": self._current_queued,
            "available_permits": self.available_permits,
            **{
                "total_calls": self.stats.total_calls,
                "successful_calls": self.stats.successful_calls,
                "rejected_calls": self.stats.rejected_calls,
                "acceptance_rate": self.stats.acceptance_rate,
                "max_concurrent_reached": self.stats.max_concurrent_reached,
            },
        }
    
    @classmethod
    def get(cls, name: str) -> Optional["Bulkhead"]:
        """Get a bulkhead by name."""
        return cls._registry.get(name)


class ThreadPoolBulkhead:
    """
    Bulkhead using a dedicated thread pool.
    
    Provides stronger isolation by using separate threads
    for each bulkhead, preventing slow operations from
    affecting the main thread pool.
    
    Example:
        bulkhead = ThreadPoolBulkhead(
            name="slow_api",
            max_workers=5,
        )
        
        result = bulkhead.execute(slow_api_call, arg1, arg2)
    """
    
    def __init__(
        self,
        name: str = "default",
        max_workers: int = 10,
        timeout: Optional[float] = None,
    ):
        self.name = name
        self.max_workers = max_workers
        self.timeout = timeout
        
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix=f"Bulkhead-{name}",
        )
        self._stats = BulkheadStats()
    
    def execute(
        self,
        func: Callable[..., Any],
        *args,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Any:
        """
        Execute a function in the bulkhead's thread pool.
        
        Args:
            func: Function to execute
            *args, **kwargs: Function arguments
            timeout: Override default timeout
            
        Returns:
            Function result
        """
        timeout = timeout or self.timeout
        
        self._stats.total_calls += 1
        
        future = self._executor.submit(func, *args, **kwargs)
        
        try:
            result = future.result(timeout=timeout)
            self._stats.successful_calls += 1
            return result
        except TimeoutError:
            self._stats.rejected_calls += 1
            raise
    
    def shutdown(self, wait: bool = True) -> None:
        """Shutdown the thread pool."""
        self._executor.shutdown(wait=wait)


def bulkhead(
    name: Optional[str] = None,
    max_concurrent: int = 10,
    max_queued: int = 0,
    timeout: Optional[float] = None,
) -> Callable[[F], F]:
    """
    Decorator to wrap a function with a bulkhead.
    
    Args:
        name: Bulkhead name (defaults to function name)
        max_concurrent: Maximum concurrent executions
        max_queued: Maximum queued requests
        timeout: Wait timeout for queued requests
        
    Example:
        @bulkhead(max_concurrent=5)
        def call_slow_api():
            return requests.get(slow_api_url)
    """
    def decorator(func: F) -> F:
        bh_name = name or func.__name__
        bh = Bulkhead(
            name=bh_name,
            max_concurrent=max_concurrent,
            max_queued=max_queued,
            timeout=timeout,
        )
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            with bh:
                return func(*args, **kwargs)
        
        wrapper.bulkhead = bh  # type: ignore
        return wrapper  # type: ignore
    
    return decorator

