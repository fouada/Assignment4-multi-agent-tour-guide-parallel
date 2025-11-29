"""
Core Framework
==============

MIT-level production infrastructure for the Multi-Agent Tour Guide System.

This module provides enterprise-grade building blocks:

1. **Plugin Architecture** (`src.core.plugins`)
   - Plugin lifecycle management
   - Discovery and registration
   - Event-driven communication
   - Hook system for extensibility

2. **Resilience Patterns** (`src.core.resilience`)
   - Circuit Breaker
   - Retry with backoff
   - Timeout management
   - Bulkhead isolation
   - Rate limiting
   - Fallback strategies

3. **Observability** (`src.core.observability`)
   - Metrics (Counter, Gauge, Histogram)
   - Distributed tracing
   - Health checks
   - Structured logging

4. **Dependency Injection** (`src.core.di`)
   - IoC container
   - Lifetime management
   - Scoped dependencies
   - Auto-wiring

Academic References:
    - Martin, "Clean Architecture" (Pearson, 2017)
    - Gamma et al., "Design Patterns" (Addison-Wesley, 1994)
    - Nygard, "Release It!" (Pragmatic Bookshelf, 2018)
    - Fowler, "Patterns of Enterprise Application Architecture" (Addison-Wesley, 2002)

Example Usage:
    from src.core.plugins import PluginManager, PluginRegistry
    from src.core.resilience import circuit_breaker, retry
    from src.core.observability import Counter, trace, health_check
    from src.core.di import Container, inject

    # Register plugin
    @PluginRegistry.register("my_plugin")
    class MyPlugin(BasePlugin):
        ...

    # Use resilience patterns
    @circuit_breaker(failure_threshold=5)
    @retry(max_attempts=3)
    def call_api():
        ...

    # Add metrics
    requests = Counter("requests_total", labels=["method"])
    requests.inc(method="GET")

    # Dependency injection
    container = Container()
    container.register(IService, ConcreteService)
    service = container.resolve(IService)
"""

# Import submodules for easier access
from src.core import di, observability, plugins, resilience

__all__ = [
    "plugins",
    "resilience",
    "observability",
    "di",
]
