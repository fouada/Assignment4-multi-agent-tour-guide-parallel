"""
Dependency Injection Container
==============================

Production-grade DI container for managing dependencies and their lifecycles.

Features:
- Constructor injection
- Property injection
- Singleton, transient, and scoped lifetimes
- Factory registration
- Interface to implementation mapping
- Lazy resolution
- Circular dependency detection

Design Patterns:
    - Dependency Injection (Fowler)
    - Service Locator (anti-pattern, but useful for transition)
    - Factory Pattern

Academic Reference:
    - Fowler, "Inversion of Control Containers and the Dependency Injection pattern"
    - Mark Seemann, "Dependency Injection in .NET"

Example:
    # Register dependencies
    container = Container()
    container.register(IUserRepository, SqlUserRepository, Lifetime.SINGLETON)
    container.register(UserService, lifetime=Lifetime.TRANSIENT)

    # Resolve dependencies
    service = container.resolve(UserService)

    # Or use decorator
    @inject
    def handler(service: UserService):
        return service.get_all()
"""

from src.core.di.container import (
    Container,
    Lifetime,
    get_container,
    inject,
    injectable,
    set_container,
)
from src.core.di.providers import (
    FactoryProvider,
    Provider,
    SingletonProvider,
    TransientProvider,
    ValueProvider,
)
from src.core.di.scope import (
    Scope,
    ScopeContext,
    scoped,
)

__all__ = [
    # Container
    "Container",
    "Lifetime",
    "inject",
    "injectable",
    "get_container",
    "set_container",
    # Scope
    "Scope",
    "ScopeContext",
    "scoped",
    # Providers
    "Provider",
    "SingletonProvider",
    "TransientProvider",
    "FactoryProvider",
    "ValueProvider",
]
