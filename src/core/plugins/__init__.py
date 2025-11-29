"""
Plugin Architecture Core
========================

Production-level plugin system with:
- Automatic plugin discovery
- Lifecycle management (init, start, stop, destroy)
- Configuration validation
- Dependency resolution
- Hot-reloading support

MIT Level Architecture following the principles from:
- "Clean Architecture" by Robert C. Martin
- "Design Patterns: Elements of Reusable Object-Oriented Software" (GoF)
- "Building Microservices" by Sam Newman

Example Usage:
    # Register a plugin
    @PluginRegistry.register("weather")
    class WeatherPlugin(BasePlugin):
        ...

    # Load all plugins
    manager = PluginManager()
    manager.discover_plugins("plugins/")
    manager.start_all()
"""

from src.core.plugins.base import (
    BasePlugin,
    PluginCapability,
    PluginMetadata,
    PluginState,
)
from src.core.plugins.events import (
    Event,
    EventBus,
    EventHandler,
    EventPriority,
    publish,
    subscribe,
)
from src.core.plugins.hooks import (
    Hook,
    HookPriority,
    HookRegistry,
    HookType,
    after_hook,
    before_hook,
    hookable,
)
from src.core.plugins.manager import PluginManager
from src.core.plugins.registry import PluginRegistry

__all__ = [
    # Base
    "BasePlugin",
    "PluginMetadata",
    "PluginState",
    "PluginCapability",
    # Registry
    "PluginRegistry",
    # Manager
    "PluginManager",
    # Hooks
    "Hook",
    "HookType",
    "HookPriority",
    "HookRegistry",
    "hookable",
    "before_hook",
    "after_hook",
    # Events
    "Event",
    "EventBus",
    "EventPriority",
    "EventHandler",
    "publish",
    "subscribe",
]
