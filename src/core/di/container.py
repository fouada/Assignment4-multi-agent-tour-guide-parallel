"""
Dependency Injection Container
==============================

Central container for dependency registration and resolution.

Example:
    container = Container()

    # Register implementations
    container.register(ILogger, FileLogger, Lifetime.SINGLETON)
    container.register(ICache, RedisCache, Lifetime.SINGLETON)
    container.register(UserService)  # Auto-wired

    # Resolve
    service = container.resolve(UserService)
"""

from __future__ import annotations

import inspect
import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from functools import wraps
from typing import (
    Any,
    TypeVar,
    get_type_hints,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")


class Lifetime(Enum):
    """Dependency lifetime."""

    SINGLETON = auto()  # One instance for container lifetime
    TRANSIENT = auto()  # New instance each resolution
    SCOPED = auto()  # One instance per scope


class CircularDependencyError(Exception):
    """Raised when circular dependency detected."""

    pass


class DependencyNotFoundError(Exception):
    """Raised when dependency cannot be resolved."""

    pass


@dataclass
class Registration:
    """A registered dependency."""

    service_type: type
    implementation: type | Callable | Any
    lifetime: Lifetime
    factory: Callable[..., Any] | None = None
    instance: Any | None = None  # For singletons
    tags: set[str] = field(default_factory=set)


class Container:
    """
    Dependency Injection Container.

    Manages dependency registration and resolution with support for
    different lifetimes and automatic constructor injection.

    Example:
        container = Container()

        # Register with interface -> implementation
        container.register(IUserRepo, SqlUserRepo, Lifetime.SINGLETON)

        # Register concrete type
        container.register(UserService)

        # Register factory
        container.register_factory(Config, lambda: load_config())

        # Register instance
        container.register_instance(Logger, my_logger)

        # Resolve
        service = container.resolve(UserService)
    """

    def __init__(self, parent: Container | None = None):
        """
        Initialize container.

        Args:
            parent: Parent container for hierarchical resolution
        """
        self._registrations: dict[type, Registration] = {}
        self._parent = parent
        self._lock = threading.RLock()
        self._resolving: set[type] = set()  # For circular dependency detection

    def register(
        self,
        service_type: type[T],
        implementation: type[T] | None = None,
        lifetime: Lifetime = Lifetime.TRANSIENT,
        *,
        tags: set[str] | None = None,
    ) -> Container:
        """
        Register a service type with its implementation.

        Args:
            service_type: The service type (interface or class)
            implementation: The implementation class (defaults to service_type)
            lifetime: The instance lifetime
            tags: Optional tags for filtering

        Returns:
            Self for chaining
        """
        impl = implementation or service_type

        with self._lock:
            self._registrations[service_type] = Registration(
                service_type=service_type,
                implementation=impl,
                lifetime=lifetime,
                tags=tags or set(),
            )

        logger.debug(
            f"Registered {service_type.__name__} -> {impl.__name__} ({lifetime.name})"
        )
        return self

    def register_factory(
        self,
        service_type: type[T],
        factory: Callable[..., T],
        lifetime: Lifetime = Lifetime.TRANSIENT,
    ) -> Container:
        """
        Register a factory function for creating instances.

        Args:
            service_type: The service type
            factory: Factory function
            lifetime: Instance lifetime
        """
        with self._lock:
            self._registrations[service_type] = Registration(
                service_type=service_type,
                implementation=factory,
                lifetime=lifetime,
                factory=factory,
            )

        logger.debug(f"Registered factory for {service_type.__name__}")
        return self

    def register_instance(
        self,
        service_type: type[T],
        instance: T,
    ) -> Container:
        """
        Register an existing instance (singleton).

        Args:
            service_type: The service type
            instance: The instance to use
        """
        with self._lock:
            self._registrations[service_type] = Registration(
                service_type=service_type,
                implementation=type(instance),
                lifetime=Lifetime.SINGLETON,
                instance=instance,
            )

        logger.debug(f"Registered instance for {service_type.__name__}")
        return self

    def resolve(self, service_type: type[T]) -> T:
        """
        Resolve a service by type.

        Automatically injects dependencies via constructor.

        Args:
            service_type: The service type to resolve

        Returns:
            Instance of the service

        Raises:
            DependencyNotFoundError: If service not registered
            CircularDependencyError: If circular dependency detected
        """
        return self._resolve(service_type, set())

    def _resolve(
        self,
        service_type: type[T],
        resolving_stack: set[type],
    ) -> T:
        """Internal resolution with circular dependency detection."""
        # Check for circular dependency
        if service_type in resolving_stack:
            chain = " -> ".join(t.__name__ for t in resolving_stack)
            raise CircularDependencyError(
                f"Circular dependency detected: {chain} -> {service_type.__name__}"
            )

        with self._lock:
            registration = self._registrations.get(service_type)

            # Check parent container
            if not registration and self._parent:
                return self._parent.resolve(service_type)

            if not registration:
                raise DependencyNotFoundError(
                    f"No registration found for {service_type.__name__}"
                )

            # Return existing singleton
            if registration.lifetime == Lifetime.SINGLETON and registration.instance:
                return registration.instance  # type: ignore[no-any-return]

            # Track resolution stack
            resolving_stack = resolving_stack | {service_type}

            # Create instance
            instance = self._create_instance(registration, resolving_stack)

            # Store singleton
            if registration.lifetime == Lifetime.SINGLETON:
                registration.instance = instance

            return instance  # type: ignore[no-any-return]

    def _create_instance(
        self,
        registration: Registration,
        resolving_stack: set[type],
    ) -> Any:
        """Create an instance with dependency injection."""
        impl = registration.implementation

        # Use factory if provided
        if registration.factory:
            # Resolve factory dependencies
            sig = inspect.signature(registration.factory)
            kwargs = self._resolve_parameters(sig, resolving_stack)
            return registration.factory(**kwargs)

        # Get constructor parameters
        if inspect.isclass(impl):
            try:
                sig = inspect.signature(impl.__init__)
                kwargs = self._resolve_parameters(sig, resolving_stack)
                return impl(**kwargs)
            except ValueError:
                # No signature (e.g., built-in types)
                return impl()

        # It's a callable or value
        return impl

    def _resolve_parameters(
        self,
        sig: inspect.Signature,
        resolving_stack: set[type],
    ) -> dict[str, Any]:
        """Resolve constructor parameters."""
        kwargs = {}

        for name, param in sig.parameters.items():
            if name == "self":
                continue

            # Get type annotation
            if param.annotation != inspect.Parameter.empty:
                param_type = param.annotation

                # Skip primitives and optionals with defaults
                if param_type in (str, int, float, bool):
                    if param.default != inspect.Parameter.empty:
                        continue

                # Try to resolve
                try:
                    if param_type in self._registrations:
                        kwargs[name] = self._resolve(param_type, resolving_stack)
                    elif param.default == inspect.Parameter.empty:
                        # Required parameter without registration
                        logger.warning(f"Cannot resolve parameter {name}: {param_type}")
                except DependencyNotFoundError:
                    if param.default == inspect.Parameter.empty:
                        raise

        return kwargs

    def resolve_all(self, service_type: type[T]) -> list[T]:
        """Resolve all registrations that implement a type."""
        results: list[T] = []

        with self._lock:
            for reg_type, registration in self._registrations.items():
                impl = registration.implementation
                if isinstance(impl, type) and issubclass(impl, service_type):
                    results.append(self.resolve(reg_type))

        return results

    def resolve_by_tag(self, tag: str) -> list[Any]:
        """Resolve all services with a specific tag."""
        results: list[Any] = []

        with self._lock:
            for service_type, registration in self._registrations.items():
                if tag in registration.tags:
                    results.append(self.resolve(service_type))

        return results

    def is_registered(self, service_type: type) -> bool:
        """Check if a type is registered."""
        with self._lock:
            if service_type in self._registrations:
                return True
            if self._parent:
                return self._parent.is_registered(service_type)
            return False

    def create_child(self) -> Container:
        """Create a child container."""
        return Container(parent=self)

    def get_registrations(self) -> dict[str, dict[str, Any]]:
        """Get all registrations for debugging."""
        with self._lock:
            return {
                t.__name__: {
                    "implementation": r.implementation.__name__
                    if isinstance(r.implementation, type)
                    else str(r.implementation),
                    "lifetime": r.lifetime.name,
                    "has_instance": r.instance is not None,
                    "tags": list(r.tags),
                }
                for t, r in self._registrations.items()
            }

    def clear(self) -> None:
        """Clear all registrations."""
        with self._lock:
            self._registrations.clear()


# ============== Global Container ==============

_container: Container | None = None
_container_lock = threading.Lock()


def get_container() -> Container:
    """Get the global container, creating if needed."""
    global _container
    with _container_lock:
        if _container is None:
            _container = Container()
        return _container


def set_container(container: Container) -> None:
    """Set the global container."""
    global _container
    with _container_lock:
        _container = container


# ============== Decorators ==============


def injectable(
    lifetime: Lifetime = Lifetime.TRANSIENT,
    tags: set[str] | None = None,
) -> Callable[[type[T]], type[T]]:
    """
    Decorator to mark a class as injectable.

    Automatically registers the class with the global container.

    Example:
        @injectable(lifetime=Lifetime.SINGLETON)
        class UserService:
            def __init__(self, repo: UserRepository):
                self.repo = repo
    """

    def decorator(cls: type[T]) -> type[T]:
        container = get_container()
        container.register(cls, lifetime=lifetime, tags=tags)
        return cls

    return decorator


def inject(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to inject dependencies into a function.

    Resolves parameters from the container based on type hints.

    Example:
        @inject
        def handler(service: UserService, repo: UserRepository):
            return service.process(repo.get_all())
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        container = get_container()
        sig = inspect.signature(func)
        hints = get_type_hints(func)

        # Resolve missing parameters
        for name, _param in sig.parameters.items():
            if name in kwargs or name in ("self", "cls"):
                continue

            if name in hints:
                param_type = hints[name]
                if container.is_registered(param_type):
                    kwargs[name] = container.resolve(param_type)

        return func(*args, **kwargs)

    return wrapper
