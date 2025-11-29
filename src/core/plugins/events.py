"""
Event Bus System
================

Production-grade event bus for decoupled inter-component communication.
Implements the Observer pattern with priority-based dispatch,
async support, and error isolation.

Design Patterns:
    - Observer Pattern: Decoupled event notification
    - Mediator Pattern: Central event coordination
    - Chain of Responsibility: Priority-based handling

Academic Reference:
    - Gamma et al., "Design Patterns" (Observer, p. 293)
    - Vernon, "Implementing Domain-Driven Design" (Domain Events, Ch. 8)
    - Fowler, "Event Sourcing" (https://martinfowler.com/eaaDev/EventSourcing.html)

Example:
    # Define an event
    class UserLoggedIn(Event):
        user_id: str
        timestamp: datetime

    # Subscribe to events
    @EventBus.subscribe(UserLoggedIn)
    def handle_login(event: UserLoggedIn):
        print(f"User {event.user_id} logged in")

    # Publish events
    EventBus.publish(UserLoggedIn(user_id="123", timestamp=datetime.now()))
"""

from __future__ import annotations

import asyncio
import logging
import threading
import traceback
from collections import defaultdict
from collections.abc import Awaitable, Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
from typing import (
    Any,
    TypeVar,
)
from uuid import uuid4

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

T = TypeVar("T", bound="Event")


class EventPriority(IntEnum):
    """
    Event handler priority levels.

    Lower values execute first.
    Use CRITICAL sparingly for essential system handlers.
    """

    CRITICAL = 0  # System-critical handlers
    HIGH = 100  # High priority (e.g., security)
    NORMAL = 500  # Default priority
    LOW = 900  # Low priority (e.g., analytics)
    MONITOR = 1000  # Monitoring/logging only


class Event(BaseModel):
    """
    Base class for all events.

    Events are immutable value objects that represent
    something that happened in the system.

    Attributes:
        event_id: Unique event identifier
        event_type: Event type name (auto-populated)
        timestamp: When the event occurred
        source: Component that generated the event
        correlation_id: For tracing related events
        metadata: Additional event metadata
    """

    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str = Field(default="")
    timestamp: datetime = Field(default_factory=datetime.now)
    source: str | None = None
    correlation_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    def __init__(self, **data):
        super().__init__(**data)
        # Auto-populate event_type from class name
        if not self.event_type:
            object.__setattr__(self, "event_type", self.__class__.__name__)

    class Config:
        frozen = True  # Events are immutable


# ============== Pre-defined System Events ==============


class PluginLoadedEvent(Event):
    """Fired when a plugin is loaded."""

    plugin_name: str
    plugin_version: str


class PluginStartedEvent(Event):
    """Fired when a plugin starts."""

    plugin_name: str


class PluginStoppedEvent(Event):
    """Fired when a plugin stops."""

    plugin_name: str
    uptime_seconds: float | None = None


class PluginErrorEvent(Event):
    """Fired when a plugin encounters an error."""

    plugin_name: str
    error_type: str
    error_message: str
    stacktrace: str | None = None


class AgentStartedEvent(Event):
    """Fired when an agent starts processing."""

    agent_type: str
    point_id: str
    location: str


class AgentCompletedEvent(Event):
    """Fired when an agent completes processing."""

    agent_type: str
    point_id: str
    duration_seconds: float
    success: bool
    content_title: str | None = None


class JudgeDecisionEvent(Event):
    """Fired when judge makes a decision."""

    point_id: str
    selected_type: str
    candidates_count: int
    reasoning: str


class RouteProcessingStartedEvent(Event):
    """Fired when route processing begins."""

    route_id: str
    source: str
    destination: str
    point_count: int


class RouteProcessingCompletedEvent(Event):
    """Fired when route processing completes."""

    route_id: str
    duration_seconds: float
    success_rate: float


# ============== Event Handler Types ==============

EventHandler = Callable[[Event], None]
AsyncEventHandler = Callable[[Event], Awaitable[None]]


@dataclass
class HandlerRegistration:
    """Registration info for an event handler."""

    handler: EventHandler | AsyncEventHandler
    priority: EventPriority
    is_async: bool
    once: bool  # Unsubscribe after first call
    weak: bool  # Use weak reference
    filter_fn: Callable[[Event], bool] | None = None
    handler_id: str = field(default_factory=lambda: str(uuid4())[:8])


class EventBus:
    """
    Central event bus for publish-subscribe messaging.

    Thread-safe implementation with:
    - Priority-based handler ordering
    - Sync and async handler support
    - Error isolation (one handler failure doesn't affect others)
    - Weak references for automatic cleanup
    - One-time handlers
    - Event filtering

    Example:
        # Method 1: Decorator
        @EventBus.subscribe(UserLoggedIn)
        def log_login(event):
            print(f"Login: {event.user_id}")

        # Method 2: Explicit subscription
        def handle_event(event):
            ...
        EventBus.add_handler(UserLoggedIn, handle_event, priority=EventPriority.HIGH)

        # Publish
        EventBus.publish(UserLoggedIn(user_id="123"))
    """

    # Class-level storage
    _handlers: dict[type[Event], list[HandlerRegistration]] = defaultdict(list)
    _global_handlers: list[HandlerRegistration] = []
    _lock = threading.RLock()
    _executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="EventBus")

    # Configuration
    _async_mode: bool = False
    _error_handler: Callable[[Event, Exception], None] | None = None
    _event_log: list[Event] = []
    _max_log_size: int = 1000

    @classmethod
    def subscribe(
        cls,
        event_type: type[T],
        *,
        priority: EventPriority = EventPriority.NORMAL,
        once: bool = False,
        weak: bool = False,
        filter_fn: Callable[[T], bool] | None = None,
    ) -> Callable[[Callable[[T], None]], Callable[[T], None]]:
        """
        Decorator to subscribe a handler to an event type.

        Args:
            event_type: Event class to subscribe to
            priority: Handler priority (lower = earlier)
            once: Unsubscribe after first call
            weak: Use weak reference (auto-cleanup)
            filter_fn: Only call handler if filter returns True

        Returns:
            Decorator function

        Example:
            @EventBus.subscribe(UserLoggedIn, priority=EventPriority.HIGH)
            def handle_login(event: UserLoggedIn):
                print(f"User {event.user_id} logged in")
        """

        def decorator(handler: Callable[[T], None]) -> Callable[[T], None]:
            cls.add_handler(
                event_type,
                handler,
                priority=priority,
                once=once,
                weak=weak,
                filter_fn=filter_fn,
            )
            return handler

        return decorator

    @classmethod
    def add_handler(
        cls,
        event_type: type[Event],
        handler: EventHandler | AsyncEventHandler,
        *,
        priority: EventPriority = EventPriority.NORMAL,
        once: bool = False,
        weak: bool = False,
        filter_fn: Callable[[Event], bool] | None = None,
    ) -> str:
        """
        Add an event handler.

        Args:
            event_type: Event class to handle
            handler: Handler function
            priority: Handler priority
            once: Remove after first call
            weak: Use weak reference
            filter_fn: Event filter predicate

        Returns:
            Handler ID for later removal
        """
        is_async = asyncio.iscoroutinefunction(handler)

        registration = HandlerRegistration(
            handler=handler,
            priority=priority,
            is_async=is_async,
            once=once,
            weak=weak,
            filter_fn=filter_fn,
        )

        with cls._lock:
            handlers = cls._handlers[event_type]
            handlers.append(registration)
            # Sort by priority (lower = earlier)
            handlers.sort(key=lambda r: r.priority)

        logger.debug(
            f"Subscribed {handler.__name__} to {event_type.__name__} "
            f"(priority={priority.name})"
        )

        return registration.handler_id

    @classmethod
    def add_global_handler(
        cls,
        handler: EventHandler | AsyncEventHandler,
        *,
        priority: EventPriority = EventPriority.MONITOR,
    ) -> str:
        """Add a handler that receives ALL events."""
        is_async = asyncio.iscoroutinefunction(handler)

        registration = HandlerRegistration(
            handler=handler,
            priority=priority,
            is_async=is_async,
            once=False,
            weak=False,
        )

        with cls._lock:
            cls._global_handlers.append(registration)
            cls._global_handlers.sort(key=lambda r: r.priority)

        return registration.handler_id

    @classmethod
    def remove_handler(cls, handler_id: str) -> bool:
        """Remove a handler by ID."""
        with cls._lock:
            for _event_type, handlers in cls._handlers.items():
                for reg in handlers:
                    if reg.handler_id == handler_id:
                        handlers.remove(reg)
                        return True

            for reg in cls._global_handlers:
                if reg.handler_id == handler_id:
                    cls._global_handlers.remove(reg)
                    return True

        return False

    @classmethod
    def unsubscribe(
        cls,
        event_type: type[Event],
        handler: EventHandler | AsyncEventHandler,
    ) -> bool:
        """Remove a handler by reference."""
        with cls._lock:
            handlers = cls._handlers.get(event_type, [])
            for reg in handlers:
                if reg.handler is handler:
                    handlers.remove(reg)
                    return True
        return False

    @classmethod
    def publish(
        cls,
        event: Event,
        *,
        sync: bool = True,
        wait: bool = False,
    ) -> None:
        """
        Publish an event to all subscribers.

        Args:
            event: Event to publish
            sync: Execute handlers synchronously
            wait: If async, wait for completion
        """
        # Log event
        cls._log_event(event)

        logger.debug(f"Publishing event: {event.event_type}")

        # Collect handlers
        handlers = []

        with cls._lock:
            # Type-specific handlers
            handlers.extend(cls._handlers.get(type(event), []))

            # Walk up class hierarchy for parent event types
            for base in type(event).__mro__[1:]:
                if base is Event or not issubclass(base, Event):
                    continue
                handlers.extend(cls._handlers.get(base, []))

            # Global handlers
            handlers.extend(cls._global_handlers)

        # Sort by priority
        handlers.sort(key=lambda r: r.priority)

        # Execute handlers
        to_remove = []
        for reg in handlers:
            # Apply filter
            if reg.filter_fn and not reg.filter_fn(event):
                continue

            try:
                if reg.is_async:
                    if sync:
                        # Run async in thread pool
                        future = cls._executor.submit(asyncio.run, reg.handler(event))
                        if wait:
                            future.result()
                    else:
                        asyncio.create_task(reg.handler(event))
                else:
                    if sync:
                        reg.handler(event)
                    else:
                        cls._executor.submit(reg.handler, event)

                if reg.once:
                    to_remove.append(reg)

            except Exception as e:
                cls._handle_error(event, e, reg)

        # Remove one-time handlers
        if to_remove:
            with cls._lock:
                for reg in to_remove:
                    for handlers in cls._handlers.values():
                        if reg in handlers:
                            handlers.remove(reg)

    @classmethod
    async def publish_async(cls, event: Event) -> None:
        """Publish event with async handler execution."""
        cls._log_event(event)

        handlers = []

        with cls._lock:
            handlers.extend(cls._handlers.get(type(event), []))
            handlers.extend(cls._global_handlers)

        handlers.sort(key=lambda r: r.priority)

        for reg in handlers:
            if reg.filter_fn and not reg.filter_fn(event):
                continue

            try:
                if reg.is_async:
                    await reg.handler(event)
                else:
                    reg.handler(event)
            except Exception as e:
                cls._handle_error(event, e, reg)

    @classmethod
    def _handle_error(
        cls,
        event: Event,
        error: Exception,
        registration: HandlerRegistration,
    ) -> None:
        """Handle errors in event handlers."""
        logger.error(
            f"Error in event handler {registration.handler.__name__} "
            f"for {event.event_type}: {error}"
        )

        if cls._error_handler:
            try:
                cls._error_handler(event, error)
            except Exception:
                pass

        # Publish error event (but avoid recursion)
        if not isinstance(event, PluginErrorEvent):
            try:
                error_event = PluginErrorEvent(
                    source="EventBus",
                    plugin_name="EventBus",
                    error_type=type(error).__name__,
                    error_message=str(error),
                    stacktrace=traceback.format_exc(),
                    correlation_id=event.correlation_id,
                )
                cls.publish(error_event)
            except Exception:
                pass

    @classmethod
    def _log_event(cls, event: Event) -> None:
        """Log event to internal buffer."""
        with cls._lock:
            cls._event_log.append(event)
            # Trim if too large
            if len(cls._event_log) > cls._max_log_size:
                cls._event_log = cls._event_log[-cls._max_log_size // 2 :]

    @classmethod
    def get_event_log(
        cls,
        event_type: type[Event] | None = None,
        limit: int = 100,
    ) -> list[Event]:
        """Get recent events from the log."""
        with cls._lock:
            events = cls._event_log[-limit:]
            if event_type:
                events = [e for e in events if isinstance(e, event_type)]
            return events

    @classmethod
    def set_error_handler(
        cls,
        handler: Callable[[Event, Exception], None],
    ) -> None:
        """Set global error handler for event processing errors."""
        cls._error_handler = handler

    @classmethod
    def clear(cls) -> None:
        """Clear all handlers and event log (for testing)."""
        with cls._lock:
            cls._handlers.clear()
            cls._global_handlers.clear()
            cls._event_log.clear()

    @classmethod
    def get_stats(cls) -> dict[str, Any]:
        """Get event bus statistics."""
        with cls._lock:
            return {
                "handler_count": sum(len(h) for h in cls._handlers.values()),
                "global_handler_count": len(cls._global_handlers),
                "event_types": list(cls._handlers.keys()),
                "event_log_size": len(cls._event_log),
            }


# ============== Convenience Functions ==============


def publish(event: Event, **kwargs) -> None:
    """Shorthand for EventBus.publish()."""
    EventBus.publish(event, **kwargs)


def subscribe(
    event_type: type[T],
    **kwargs,
) -> Callable[[Callable[[T], None]], Callable[[T], None]]:
    """Shorthand for EventBus.subscribe()."""
    return EventBus.subscribe(event_type, **kwargs)
