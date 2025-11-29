"""
Plugin Registry
===============

Central registry for plugin discovery, registration, and lookup.
Implements the Registry pattern with thread-safe operations.

Design Patterns:
    - Registry Pattern: Central storage for plugin types
    - Factory Pattern: Plugin instantiation
    - Singleton Pattern: Global registry instance

Academic Reference:
    - Fowler, "Patterns of Enterprise Application Architecture" (Registry, p. 480)
"""

import importlib
import importlib.util
import logging
import sys
import threading
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import (
    TypeVar,
)

import yaml  # type: ignore[import-untyped]

from src.core.plugins.base import (
    BasePlugin,
    PluginCapability,
    PluginContext,
    PluginMetadata,
)

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BasePlugin)


class PluginRegistrationError(Exception):
    """Raised when plugin registration fails."""

    pass


class PluginNotFoundError(Exception):
    """Raised when requested plugin is not found."""

    pass


class PluginRegistry:
    """
    Thread-safe registry for plugin types and instances.

    Supports:
    - Registration via decorator or explicit call
    - Plugin discovery from directories
    - Capability-based queries
    - Dependency resolution

    Example:
        # Decorator registration
        @PluginRegistry.register("weather")
        class WeatherPlugin(BasePlugin):
            ...

        # Explicit registration
        PluginRegistry.register_plugin("custom", CustomPlugin)

        # Query plugins
        content_plugins = PluginRegistry.get_by_capability(
            PluginCapability.CONTENT_PROVIDER
        )
    """

    # Class-level storage (thread-safe)
    _plugins: dict[str, type[BasePlugin]] = {}
    _metadata: dict[str, PluginMetadata] = {}
    _instances: dict[str, BasePlugin] = {}
    _lock = threading.RLock()

    # Discovery paths
    _search_paths: list[Path] = []
    _discovered: set[str] = set()

    @classmethod
    def register(
        cls,
        name: str,
        *,
        metadata: PluginMetadata | None = None,
        replace: bool = False,
    ) -> Callable[[type[T]], type[T]]:
        """
        Decorator to register a plugin class.

        Args:
            name: Unique plugin identifier
            metadata: Optional metadata override
            replace: Allow replacing existing plugin

        Returns:
            Decorator function

        Example:
            @PluginRegistry.register("weather")
            class WeatherPlugin(BasePlugin):
                metadata = PluginMetadata(
                    name="weather",
                    version="1.0.0"
                )
        """

        def decorator(plugin_class: type[T]) -> type[T]:
            cls.register_plugin(
                name,
                plugin_class,
                metadata=metadata,
                replace=replace,
            )
            return plugin_class

        return decorator

    @classmethod
    def register_plugin(
        cls,
        name: str,
        plugin_class: type[BasePlugin],
        *,
        metadata: PluginMetadata | None = None,
        replace: bool = False,
    ) -> None:
        """
        Register a plugin class with the registry.

        Args:
            name: Unique plugin identifier
            plugin_class: Plugin class to register
            metadata: Optional metadata override
            replace: Allow replacing existing plugin

        Raises:
            PluginRegistrationError: If registration fails
        """
        with cls._lock:
            # Check for existing registration
            if name in cls._plugins and not replace:
                raise PluginRegistrationError(
                    f"Plugin '{name}' is already registered. "
                    f"Use replace=True to override."
                )

            # Validate plugin class
            if not issubclass(plugin_class, BasePlugin):
                raise PluginRegistrationError(
                    f"Plugin class must inherit from BasePlugin: {plugin_class}"
                )

            # Get or create metadata
            if metadata:
                cls._metadata[name] = metadata
            elif hasattr(plugin_class, "metadata"):
                cls._metadata[name] = plugin_class.metadata
            else:
                # Auto-generate minimal metadata
                cls._metadata[name] = PluginMetadata(
                    name=name,
                    version="0.0.1",
                    description=plugin_class.__doc__ or "",
                )

            cls._plugins[name] = plugin_class
            logger.info(f"Registered plugin: {name} v{cls._metadata[name].version}")

    @classmethod
    def unregister(cls, name: str) -> None:
        """
        Unregister a plugin.

        Args:
            name: Plugin identifier
        """
        with cls._lock:
            if name in cls._plugins:
                # Stop instance if running
                if name in cls._instances:
                    instance = cls._instances[name]
                    if instance.is_running:
                        instance.stop()
                    del cls._instances[name]

                del cls._plugins[name]
                if name in cls._metadata:
                    del cls._metadata[name]

                logger.info(f"Unregistered plugin: {name}")

    @classmethod
    def get(cls, name: str) -> type[BasePlugin]:
        """
        Get a plugin class by name.

        Args:
            name: Plugin identifier

        Returns:
            Plugin class

        Raises:
            PluginNotFoundError: If plugin not found
        """
        with cls._lock:
            if name not in cls._plugins:
                raise PluginNotFoundError(f"Plugin not found: {name}")
            return cls._plugins[name]

    @classmethod
    def get_instance(
        cls,
        name: str,
        context: PluginContext | None = None,
        *,
        singleton: bool = True,
    ) -> BasePlugin:
        """
        Get or create a plugin instance.

        Args:
            name: Plugin identifier
            context: Runtime context
            singleton: Return same instance if already created

        Returns:
            Plugin instance
        """
        with cls._lock:
            if singleton and name in cls._instances:
                return cls._instances[name]

            plugin_class = cls.get(name)
            instance = plugin_class(context)

            if singleton:
                cls._instances[name] = instance

            return instance

    @classmethod
    def get_metadata(cls, name: str) -> PluginMetadata:
        """Get plugin metadata."""
        with cls._lock:
            if name not in cls._metadata:
                raise PluginNotFoundError(f"Plugin not found: {name}")
            return cls._metadata[name]

    @classmethod
    def list_plugins(cls) -> list[str]:
        """List all registered plugin names."""
        with cls._lock:
            return list(cls._plugins.keys())

    @classmethod
    def list_metadata(cls) -> dict[str, PluginMetadata]:
        """List all plugin metadata."""
        with cls._lock:
            return dict(cls._metadata)

    @classmethod
    def get_by_capability(
        cls,
        capability: PluginCapability,
    ) -> list[str]:
        """
        Find plugins by capability.

        Args:
            capability: Required capability

        Returns:
            List of plugin names with this capability
        """
        with cls._lock:
            return [
                name
                for name, meta in cls._metadata.items()
                if capability in meta.capabilities
            ]

    @classmethod
    def get_by_category(cls, category: str) -> list[str]:
        """Find plugins by category."""
        with cls._lock:
            return [
                name
                for name, meta in cls._metadata.items()
                if meta.category == category
            ]

    @classmethod
    def get_enabled(cls) -> list[str]:
        """Get list of enabled plugins."""
        with cls._lock:
            return [name for name, meta in cls._metadata.items() if meta.enabled]

    @classmethod
    def exists(cls, name: str) -> bool:
        """Check if a plugin is registered."""
        with cls._lock:
            return name in cls._plugins

    @classmethod
    def count(cls) -> int:
        """Get number of registered plugins."""
        with cls._lock:
            return len(cls._plugins)

    @classmethod
    def discover(
        cls,
        path: str | Path,
        *,
        recursive: bool = True,
        manifest_name: str = "plugin.yaml",
    ) -> list[str]:
        """
        Discover and register plugins from a directory.

        Plugin directories should contain:
        - plugin.yaml: Plugin manifest with metadata
        - plugin.py or __init__.py: Plugin implementation

        Args:
            path: Directory to search
            recursive: Search subdirectories
            manifest_name: Name of manifest file

        Returns:
            List of discovered plugin names
        """
        path = Path(path)
        if not path.exists():
            logger.warning(f"Plugin path does not exist: {path}")
            return []

        discovered = []

        # Find manifest files
        pattern = f"**/{manifest_name}" if recursive else manifest_name
        for manifest_path in path.glob(pattern):
            try:
                plugin_name = cls._load_plugin_from_manifest(manifest_path)
                if plugin_name:
                    discovered.append(plugin_name)
            except Exception as e:
                logger.error(f"Failed to load plugin from {manifest_path}: {e}")

        logger.info(f"Discovered {len(discovered)} plugins from {path}")
        return discovered

    @classmethod
    def _load_plugin_from_manifest(cls, manifest_path: Path) -> str | None:
        """Load a plugin from its manifest file."""
        plugin_dir = manifest_path.parent

        # Load manifest
        with open(manifest_path) as f:
            manifest = yaml.safe_load(f)

        name = manifest.get("name")
        if not name:
            raise PluginRegistrationError(
                f"Plugin manifest missing 'name': {manifest_path}"
            )

        # Check if already loaded
        if name in cls._discovered:
            return None

        # Load metadata
        metadata = PluginMetadata.from_yaml(manifest_path)

        # Find and load module
        module_name = manifest.get("module", "plugin")
        module_file = plugin_dir / f"{module_name}.py"

        if not module_file.exists():
            module_file = plugin_dir / "__init__.py"

        if not module_file.exists():
            raise PluginRegistrationError(f"Plugin module not found in {plugin_dir}")

        # Load module dynamically
        spec = importlib.util.spec_from_file_location(f"plugins.{name}", module_file)
        if not spec or not spec.loader:
            raise PluginRegistrationError(
                f"Could not load plugin module: {module_file}"
            )

        module = importlib.util.module_from_spec(spec)
        sys.modules[f"plugins.{name}"] = module
        spec.loader.exec_module(module)

        # Find plugin class
        class_name = manifest.get("class")
        if class_name:
            plugin_class = getattr(module, class_name)
        else:
            # Find first BasePlugin subclass
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, BasePlugin)
                    and attr is not BasePlugin
                ):
                    plugin_class = attr
                    break

        if not plugin_class:
            raise PluginRegistrationError(f"No plugin class found in {module_file}")

        # Register plugin
        cls.register_plugin(name, plugin_class, metadata=metadata)
        cls._discovered.add(name)

        return str(name)

    @classmethod
    def add_search_path(cls, path: str | Path) -> None:
        """Add a path to plugin search paths."""
        path = Path(path)
        if path not in cls._search_paths:
            cls._search_paths.append(path)

    @classmethod
    def discover_all(cls) -> list[str]:
        """Discover plugins from all search paths."""
        discovered = []
        for path in cls._search_paths:
            discovered.extend(cls.discover(path))
        return discovered

    @classmethod
    def clear(cls) -> None:
        """Clear all registrations (for testing)."""
        with cls._lock:
            # Stop all instances
            for instance in cls._instances.values():
                if instance.is_running:
                    try:
                        instance.stop()
                    except Exception:
                        pass

            cls._plugins.clear()
            cls._metadata.clear()
            cls._instances.clear()
            cls._discovered.clear()

    @classmethod
    def __iter__(cls) -> Iterator[str]:
        """Iterate over plugin names."""
        with cls._lock:
            return iter(list(cls._plugins.keys()))

    @classmethod
    def resolve_dependencies(cls, name: str) -> list[str]:
        """
        Resolve plugin dependencies in order.

        Returns a list of plugin names in the order they should be started.
        Uses topological sort for dependency resolution.

        Args:
            name: Plugin name to resolve

        Returns:
            Ordered list of plugin names (dependencies first)

        Raises:
            PluginRegistrationError: If circular dependency detected
        """
        with cls._lock:
            visited = set()
            order = []
            stack = set()

            def visit(plugin_name: str):
                if plugin_name in stack:
                    raise PluginRegistrationError(
                        f"Circular dependency detected: {plugin_name}"
                    )
                if plugin_name in visited:
                    return

                stack.add(plugin_name)

                if plugin_name in cls._metadata:
                    for dep in cls._metadata[plugin_name].depends_on:
                        if dep in cls._plugins:
                            visit(dep)

                stack.remove(plugin_name)
                visited.add(plugin_name)
                order.append(plugin_name)

            visit(name)
            return order
