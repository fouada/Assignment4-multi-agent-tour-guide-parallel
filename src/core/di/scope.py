"""
Scoped Dependencies
===================

Manages scoped lifetimes for request-scoped dependencies.

Example:
    # Create scope for a request
    with Scope("request") as scope:
        user_context = scope.resolve(UserContext)
        # ... handle request
    # Scope ends, dependencies disposed
"""

from __future__ import annotations

import contextvars
import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class ScopeContext:
    """Context for a scope."""

    name: str
    instances: dict[type, Any] = field(default_factory=dict)
    parent: ScopeContext | None = None

    def get(self, service_type: type[T]) -> T | None:
        """Get scoped instance."""
        if service_type in self.instances:
            return self.instances[service_type]
        if self.parent:
            return self.parent.get(service_type)
        return None

    def set(self, service_type: type[T], instance: T) -> None:
        """Set scoped instance."""
        self.instances[service_type] = instance

    def dispose(self) -> None:
        """Dispose of all scoped instances."""
        for instance in self.instances.values():
            if hasattr(instance, "dispose"):
                try:
                    instance.dispose()
                except Exception as e:
                    logger.warning(f"Error disposing {type(instance)}: {e}")
            elif hasattr(instance, "close"):
                try:
                    instance.close()
                except Exception as e:
                    logger.warning(f"Error closing {type(instance)}: {e}")

        self.instances.clear()


# Current scope context variable
_current_scope: contextvars.ContextVar[ScopeContext | None] = contextvars.ContextVar(
    "current_scope", default=None
)


class Scope:
    """
    Scope for managing scoped dependencies.

    Use as context manager to create a scope.

    Example:
        with Scope("request") as scope:
            # Resolve scoped dependencies
            db_session = scope.resolve(DbSession)
            # Use dependencies...
        # Scope ends, resources cleaned up
    """

    _active_scopes: dict[str, ScopeContext] = {}
    _lock = threading.Lock()

    def __init__(self, name: str = "default"):
        self.name = name
        self._context: ScopeContext | None = None
        self._token: contextvars.Token | None = None

    def __enter__(self) -> Scope:
        parent = _current_scope.get()
        self._context = ScopeContext(name=self.name, parent=parent)
        self._token = _current_scope.set(self._context)

        with Scope._lock:
            Scope._active_scopes[self.name] = self._context

        logger.debug(f"Entered scope: {self.name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._context:
            self._context.dispose()

        if self._token:
            _current_scope.reset(self._token)

        with Scope._lock:
            Scope._active_scopes.pop(self.name, None)

        logger.debug(f"Exited scope: {self.name}")

    def resolve(self, service_type: type[T]) -> T:
        """Resolve a scoped dependency."""
        if not self._context:
            raise RuntimeError("Scope not active")

        # Check if already resolved in this scope
        instance = self._context.get(service_type)
        if instance:
            return instance

        # Import here to avoid circular import
        from src.core.di.container import Lifetime, get_container

        container = get_container()
        instance = container.resolve(service_type)

        # Store in scope if scoped lifetime
        reg = container._registrations.get(service_type)
        if reg and reg.lifetime == Lifetime.SCOPED:
            self._context.set(service_type, instance)

        return instance

    @classmethod
    def current(cls) -> ScopeContext | None:
        """Get current scope context."""
        return _current_scope.get()

    @classmethod
    def get_active(cls, name: str) -> ScopeContext | None:
        """Get an active scope by name."""
        with cls._lock:
            return cls._active_scopes.get(name)


def scoped(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to run function in a new scope.

    Example:
        @scoped
        def handle_request():
            # All scoped dependencies are unique to this call
            session = resolve(DbSession)
            ...
    """
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        with Scope(f"scoped_{func.__name__}"):
            return func(*args, **kwargs)

    return wrapper
