"""
Metrics Collection
==================

Prometheus-inspired metrics for monitoring application behavior.

Metric Types:
- Counter: Monotonically increasing value (e.g., total requests)
- Gauge: Value that can go up or down (e.g., active connections)
- Histogram: Distribution of values (e.g., response times)

Example:
    # Create metrics
    requests = Counter("http_requests", "Total HTTP requests", ["method", "path"])
    active_agents = Gauge("active_agents", "Currently active agents")
    response_time = Histogram("response_seconds", "Response time", buckets=[0.1, 0.5, 1, 5])
    
    # Use metrics
    requests.inc(method="GET", path="/api")
    active_agents.set(5)
    response_time.observe(0.234)
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar
import logging

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


@dataclass
class MetricValue:
    """A metric value with labels."""
    value: float = 0.0
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class Counter:
    """
    A monotonically increasing counter.
    
    Use for things like total requests, errors, etc.
    Value can only increase (or reset on restart).
    
    Example:
        counter = Counter("requests_total", "Total requests", ["method"])
        counter.inc(method="GET")
        counter.inc(5, method="POST")
    """
    
    def __init__(
        self,
        name: str,
        description: str = "",
        labels: Optional[List[str]] = None,
    ):
        self.name = name
        self.description = description
        self.label_names = labels or []
        self._values: Dict[Tuple, float] = defaultdict(float)
        self._lock = threading.Lock()
        
        MetricsRegistry.register(self)
    
    def inc(self, value: float = 1.0, **labels) -> None:
        """Increment the counter."""
        if value < 0:
            raise ValueError("Counter can only be incremented by positive values")
        
        key = self._labels_key(labels)
        with self._lock:
            self._values[key] += value
    
    def get(self, **labels) -> float:
        """Get current value for given labels."""
        key = self._labels_key(labels)
        with self._lock:
            return self._values[key]
    
    def _labels_key(self, labels: Dict[str, str]) -> Tuple:
        """Create a hashable key from labels."""
        return tuple(labels.get(name, "") for name in self.label_names)
    
    def collect(self) -> List[MetricValue]:
        """Collect all values for export."""
        with self._lock:
            return [
                MetricValue(
                    value=value,
                    labels=dict(zip(self.label_names, key)),
                )
                for key, value in self._values.items()
            ]


class Gauge:
    """
    A value that can go up or down.
    
    Use for things like active connections, queue depth, etc.
    
    Example:
        gauge = Gauge("active_connections", "Current active connections")
        gauge.set(10)
        gauge.inc()
        gauge.dec()
    """
    
    def __init__(
        self,
        name: str,
        description: str = "",
        labels: Optional[List[str]] = None,
    ):
        self.name = name
        self.description = description
        self.label_names = labels or []
        self._values: Dict[Tuple, float] = defaultdict(float)
        self._lock = threading.Lock()
        
        MetricsRegistry.register(self)
    
    def set(self, value: float, **labels) -> None:
        """Set the gauge to a value."""
        key = self._labels_key(labels)
        with self._lock:
            self._values[key] = value
    
    def inc(self, value: float = 1.0, **labels) -> None:
        """Increment the gauge."""
        key = self._labels_key(labels)
        with self._lock:
            self._values[key] += value
    
    def dec(self, value: float = 1.0, **labels) -> None:
        """Decrement the gauge."""
        key = self._labels_key(labels)
        with self._lock:
            self._values[key] -= value
    
    def get(self, **labels) -> float:
        """Get current value."""
        key = self._labels_key(labels)
        with self._lock:
            return self._values[key]
    
    def _labels_key(self, labels: Dict[str, str]) -> Tuple:
        return tuple(labels.get(name, "") for name in self.label_names)
    
    def collect(self) -> List[MetricValue]:
        with self._lock:
            return [
                MetricValue(
                    value=value,
                    labels=dict(zip(self.label_names, key)),
                )
                for key, value in self._values.items()
            ]


class Histogram:
    """
    Distribution of values across buckets.
    
    Use for things like response times, request sizes, etc.
    
    Example:
        histogram = Histogram(
            "response_seconds",
            "Response time in seconds",
            buckets=[0.01, 0.05, 0.1, 0.5, 1, 5, 10],
        )
        histogram.observe(0.234)
    """
    
    DEFAULT_BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10)
    
    def __init__(
        self,
        name: str,
        description: str = "",
        labels: Optional[List[str]] = None,
        buckets: Optional[Tuple[float, ...]] = None,
    ):
        self.name = name
        self.description = description
        self.label_names = labels or []
        self.buckets = buckets or self.DEFAULT_BUCKETS
        
        self._bucket_counts: Dict[Tuple, Dict[float, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        self._sum: Dict[Tuple, float] = defaultdict(float)
        self._count: Dict[Tuple, int] = defaultdict(int)
        self._lock = threading.Lock()
        
        MetricsRegistry.register(self)
    
    def observe(self, value: float, **labels) -> None:
        """Record an observation."""
        key = self._labels_key(labels)
        
        with self._lock:
            self._sum[key] += value
            self._count[key] += 1
            
            for bucket in self.buckets:
                if value <= bucket:
                    self._bucket_counts[key][bucket] += 1
    
    def get_percentile(self, p: float, **labels) -> Optional[float]:
        """Get approximate percentile value."""
        key = self._labels_key(labels)
        
        with self._lock:
            total = self._count[key]
            if total == 0:
                return None
            
            target = int(total * p)
            cumulative = 0
            
            for bucket in sorted(self.buckets):
                cumulative += self._bucket_counts[key][bucket]
                if cumulative >= target:
                    return bucket
            
            return self.buckets[-1]
    
    def _labels_key(self, labels: Dict[str, str]) -> Tuple:
        return tuple(labels.get(name, "") for name in self.label_names)
    
    def collect(self) -> Dict[str, Any]:
        """Collect histogram data."""
        with self._lock:
            return {
                "sum": dict(self._sum),
                "count": dict(self._count),
                "buckets": {
                    key: dict(buckets)
                    for key, buckets in self._bucket_counts.items()
                },
            }


class Timer:
    """
    Context manager for timing code blocks.
    
    Example:
        timer = Timer("operation_duration")
        with timer:
            do_something()
        
        # Or as decorator
        @timer
        def my_function():
            ...
    """
    
    def __init__(
        self,
        name: str,
        description: str = "",
        labels: Optional[List[str]] = None,
    ):
        self.histogram = Histogram(name, description, labels)
        self._start: Optional[float] = None
        self._labels: Dict[str, str] = {}
    
    def __enter__(self) -> "Timer":
        self._start = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._start:
            duration = time.time() - self._start
            self.histogram.observe(duration, **self._labels)
    
    def labels(self, **labels) -> "Timer":
        """Set labels for this timing."""
        self._labels = labels
        return self
    
    def __call__(self, func: F) -> F:
        """Use as decorator."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self.labels(function=func.__name__):
                return func(*args, **kwargs)
        return wrapper  # type: ignore


class MetricsRegistry:
    """
    Central registry for all metrics.
    
    Provides:
    - Metric registration and discovery
    - Bulk collection for export
    - Prometheus format export
    """
    
    _metrics: Dict[str, Any] = {}
    _lock = threading.Lock()
    
    @classmethod
    def register(cls, metric: Any) -> None:
        """Register a metric."""
        with cls._lock:
            cls._metrics[metric.name] = metric
    
    @classmethod
    def get(cls, name: str) -> Optional[Any]:
        """Get a metric by name."""
        return cls._metrics.get(name)
    
    @classmethod
    def list_metrics(cls) -> List[str]:
        """List all registered metric names."""
        return list(cls._metrics.keys())
    
    @classmethod
    def collect_all(cls) -> Dict[str, Any]:
        """Collect all metrics for export."""
        result = {}
        with cls._lock:
            for name, metric in cls._metrics.items():
                result[name] = {
                    "description": metric.description,
                    "type": type(metric).__name__,
                    "values": metric.collect(),
                }
        return result
    
    @classmethod
    def to_prometheus(cls) -> str:
        """Export metrics in Prometheus format."""
        lines = []
        
        with cls._lock:
            for name, metric in cls._metrics.items():
                # Add help and type
                lines.append(f"# HELP {name} {metric.description}")
                lines.append(f"# TYPE {name} {type(metric).__name__.lower()}")
                
                # Add values
                for value in metric.collect():
                    if value.labels:
                        label_str = ",".join(
                            f'{k}="{v}"' for k, v in value.labels.items()
                        )
                        lines.append(f"{name}{{{label_str}}} {value.value}")
                    else:
                        lines.append(f"{name} {value.value}")
        
        return "\n".join(lines)
    
    @classmethod
    def clear(cls) -> None:
        """Clear all metrics (for testing)."""
        with cls._lock:
            cls._metrics.clear()


# ============== Decorators ==============

def timed(
    name: Optional[str] = None,
    description: str = "Function execution time",
) -> Callable[[F], F]:
    """
    Decorator to time function execution.
    
    Example:
        @timed("my_function_duration")
        def my_function():
            ...
    """
    def decorator(func: F) -> F:
        metric_name = name or f"{func.__name__}_duration_seconds"
        timer = Timer(metric_name, description)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            with timer.labels(function=func.__name__):
                return func(*args, **kwargs)
        
        return wrapper  # type: ignore
    
    return decorator


def counted(
    name: Optional[str] = None,
    description: str = "Function call count",
    count_exceptions: bool = True,
) -> Callable[[F], F]:
    """
    Decorator to count function calls.
    
    Example:
        @counted("api_calls")
        def call_api():
            ...
    """
    def decorator(func: F) -> F:
        metric_name = name or f"{func.__name__}_total"
        counter = Counter(metric_name, description, labels=["function", "status"])
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                counter.inc(function=func.__name__, status="success")
                return result
            except Exception:
                if count_exceptions:
                    counter.inc(function=func.__name__, status="error")
                raise
        
        return wrapper  # type: ignore
    
    return decorator

