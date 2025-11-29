"""
Distributed Tracing
===================

Trace execution across components with span management.

Features:
- Span creation and nesting
- Context propagation
- Timing and attributes
- Export to tracing backends

Example:
    tracer = get_tracer("tour-guide")
    
    with tracer.span("process_route") as span:
        span.set_attribute("route_id", route.id)
        span.set_attribute("point_count", len(route.points))
        
        for point in route.points:
            with tracer.span("process_point") as child:
                child.set_attribute("point_id", point.id)
                result = process(point)
"""

from __future__ import annotations

import contextvars
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


class SpanKind(Enum):
    """Kind of span."""
    INTERNAL = "internal"
    SERVER = "server"
    CLIENT = "client"
    PRODUCER = "producer"
    CONSUMER = "consumer"


class SpanStatus(Enum):
    """Span status."""
    UNSET = "unset"
    OK = "ok"
    ERROR = "error"


@dataclass
class SpanContext:
    """
    Immutable span context for propagation.
    
    Contains identifiers needed to correlate traces
    across service boundaries.
    """
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    trace_flags: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
        }
    
    @classmethod
    def create(cls, parent: Optional["SpanContext"] = None) -> "SpanContext":
        """Create a new span context."""
        return cls(
            trace_id=parent.trace_id if parent else str(uuid4()).replace("-", ""),
            span_id=str(uuid4()).replace("-", "")[:16],
            parent_span_id=parent.span_id if parent else None,
        )


@dataclass
class SpanEvent:
    """An event that occurred during a span."""
    name: str
    timestamp: datetime = field(default_factory=datetime.now)
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Span:
    """
    A span represents a unit of work.
    
    Spans can be nested to form a trace tree.
    Each span has timing, status, and attributes.
    """
    name: str
    context: SpanContext
    kind: SpanKind = SpanKind.INTERNAL
    status: SpanStatus = SpanStatus.UNSET
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    events: List[SpanEvent] = field(default_factory=list)
    
    # Internal
    _tracer: Optional["Tracer"] = field(default=None, repr=False)
    
    @property
    def duration_ms(self) -> Optional[float]:
        """Duration in milliseconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return None
    
    @property
    def is_recording(self) -> bool:
        """Check if span is still recording."""
        return self.end_time is None
    
    def set_attribute(self, key: str, value: Any) -> "Span":
        """Set a span attribute."""
        self.attributes[key] = value
        return self
    
    def set_attributes(self, attributes: Dict[str, Any]) -> "Span":
        """Set multiple attributes."""
        self.attributes.update(attributes)
        return self
    
    def add_event(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> "Span":
        """Add an event to the span."""
        event = SpanEvent(name=name, attributes=attributes or {})
        self.events.append(event)
        return self
    
    def set_status(self, status: SpanStatus, message: Optional[str] = None) -> "Span":
        """Set the span status."""
        self.status = status
        if message:
            self.attributes["status_message"] = message
        return self
    
    def record_exception(self, exception: Exception) -> "Span":
        """Record an exception."""
        self.set_status(SpanStatus.ERROR, str(exception))
        self.add_event(
            "exception",
            {
                "exception.type": type(exception).__name__,
                "exception.message": str(exception),
            },
        )
        return self
    
    def end(self) -> None:
        """End the span."""
        if self.is_recording:
            self.end_time = datetime.now()
            if self._tracer:
                self._tracer._on_span_end(self)
    
    def __enter__(self) -> "Span":
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_val:
            self.record_exception(exc_val)
        self.end()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for export."""
        return {
            "name": self.name,
            "context": self.context.to_dict(),
            "kind": self.kind.value,
            "status": self.status.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.duration_ms,
            "attributes": self.attributes,
            "events": [
                {
                    "name": e.name,
                    "timestamp": e.timestamp.isoformat(),
                    "attributes": e.attributes,
                }
                for e in self.events
            ],
        }


# Context variable for current span
_current_span: contextvars.ContextVar[Optional[Span]] = contextvars.ContextVar(
    "current_span", default=None
)


class Tracer:
    """
    Tracer for creating and managing spans.
    
    Example:
        tracer = Tracer("my-service")
        
        with tracer.span("operation") as span:
            span.set_attribute("key", "value")
            do_work()
    """
    
    _instances: Dict[str, "Tracer"] = {}
    _lock = threading.Lock()
    
    def __init__(
        self,
        name: str,
        version: str = "1.0.0",
        max_spans: int = 10000,
    ):
        self.name = name
        self.version = version
        self.max_spans = max_spans
        
        self._spans: List[Span] = []
        self._spans_lock = threading.Lock()
        
        with Tracer._lock:
            Tracer._instances[name] = self
    
    def span(
        self,
        name: str,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> Span:
        """
        Create a new span.
        
        The span is automatically linked to the current span as parent.
        Use as a context manager to ensure proper ending.
        
        Args:
            name: Span name
            kind: Span kind
            attributes: Initial attributes
            
        Returns:
            New span
        """
        # Get parent context
        parent = _current_span.get()
        parent_context = parent.context if parent else None
        
        # Create span
        context = SpanContext.create(parent_context)
        span = Span(
            name=name,
            context=context,
            kind=kind,
            attributes=attributes or {},
            _tracer=self,
        )
        
        # Set as current
        _current_span.set(span)
        
        logger.debug(f"Started span: {name} ({context.span_id})")
        return span
    
    def _on_span_end(self, span: Span) -> None:
        """Called when a span ends."""
        # Restore parent as current
        parent_id = span.context.parent_span_id
        if parent_id:
            # Find parent span
            with self._spans_lock:
                for s in reversed(self._spans):
                    if s.context.span_id == parent_id:
                        _current_span.set(s)
                        break
        else:
            _current_span.set(None)
        
        # Store span
        with self._spans_lock:
            self._spans.append(span)
            # Limit stored spans
            if len(self._spans) > self.max_spans:
                self._spans = self._spans[-self.max_spans // 2:]
        
        logger.debug(
            f"Ended span: {span.name} ({span.context.span_id}) - "
            f"{span.duration_ms:.2f}ms"
        )
    
    def get_current_span(self) -> Optional[Span]:
        """Get the current active span."""
        return _current_span.get()
    
    def get_spans(
        self,
        trace_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Span]:
        """Get recorded spans."""
        with self._spans_lock:
            spans = list(self._spans)
        
        if trace_id:
            spans = [s for s in spans if s.context.trace_id == trace_id]
        
        return spans[-limit:]
    
    def clear_spans(self) -> None:
        """Clear recorded spans."""
        with self._spans_lock:
            self._spans.clear()
    
    @classmethod
    def get(cls, name: str) -> Optional["Tracer"]:
        """Get a tracer by name."""
        return cls._instances.get(name)


# ============== Global Functions ==============

def get_tracer(name: str = "default") -> Tracer:
    """Get or create a tracer."""
    tracer = Tracer.get(name)
    if not tracer:
        tracer = Tracer(name)
    return tracer


def get_current_span() -> Optional[Span]:
    """Get the current active span."""
    return _current_span.get()


def trace(
    name: Optional[str] = None,
    kind: SpanKind = SpanKind.INTERNAL,
    tracer_name: str = "default",
) -> Callable[[F], F]:
    """
    Decorator to trace a function.
    
    Example:
        @trace("process_data")
        def process_data(data):
            ...
        
        @trace()  # Uses function name
        def my_function():
            ...
    """
    def decorator(func: F) -> F:
        span_name = name or func.__name__
        tracer = get_tracer(tracer_name)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            with tracer.span(span_name, kind=kind) as span:
                span.set_attribute("function", func.__name__)
                span.set_attribute("module", func.__module__)
                try:
                    result = func(*args, **kwargs)
                    span.set_status(SpanStatus.OK)
                    return result
                except Exception as e:
                    span.record_exception(e)
                    raise
        
        return wrapper  # type: ignore
    
    return decorator

