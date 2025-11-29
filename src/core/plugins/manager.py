"""
Plugin Manager
==============

Manages the full lifecycle of plugins including discovery, loading,
configuration, dependency resolution, and graceful shutdown.

This is the main entry point for working with plugins at runtime.

Design Patterns:
    - Facade Pattern: Simplified interface to plugin subsystem
    - Mediator Pattern: Coordinates plugin interactions
    - Lifecycle Management: Startup/shutdown orchestration

Academic Reference:
    - Gamma et al., "Design Patterns" (Facade, p. 185)
    - Fowler, "Patterns of Enterprise Application Architecture" (Service Layer, p. 133)

Example:
    # Initialize manager
    manager = PluginManager()
    
    # Discover plugins from directories
    manager.discover("plugins/")
    
    # Start all enabled plugins
    manager.start_all()
    
    # Access a specific plugin
    weather = manager.get("weather")
    result = weather.search_content("Paris")
    
    # Graceful shutdown
    manager.stop_all()
"""

import threading
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Type, Union
import logging
import signal

from pydantic import BaseModel

from src.core.plugins.base import (
    BasePlugin,
    PluginCapability,
    PluginContext,
    PluginMetadata,
    PluginState,
)
from src.core.plugins.registry import (
    PluginRegistry,
    PluginNotFoundError,
    PluginRegistrationError,
)
from src.core.plugins.events import (
    Event,
    EventBus,
    PluginErrorEvent,
    PluginLoadedEvent,
    PluginStartedEvent,
    PluginStoppedEvent,
)

logger = logging.getLogger(__name__)


class PluginManagerConfig(BaseModel):
    """Configuration for the plugin manager."""
    
    # Discovery
    plugin_dirs: List[str] = ["plugins"]
    auto_discover: bool = True
    
    # Startup
    auto_start: bool = True
    start_timeout: float = 30.0
    parallel_start: bool = True
    
    # Shutdown
    stop_timeout: float = 10.0
    graceful_shutdown: bool = True
    
    # Health
    health_check_interval: float = 30.0
    auto_restart_failed: bool = False
    max_restart_attempts: int = 3
    
    # Configuration
    plugin_configs: Dict[str, Dict[str, Any]] = {}


class PluginManager:
    """
    Central manager for all plugins.
    
    Responsibilities:
    - Plugin discovery and loading
    - Lifecycle management (start/stop)
    - Dependency resolution
    - Configuration management
    - Health monitoring
    - Event coordination
    
    Thread Safety:
    All operations are thread-safe through careful locking.
    
    Example:
        manager = PluginManager(
            PluginManagerConfig(
                plugin_dirs=["plugins/", "extra/"],
                auto_start=True,
            )
        )
        manager.initialize()
        
        # Later...
        manager.shutdown()
    """
    
    def __init__(
        self,
        config: Optional[PluginManagerConfig] = None,
        context: Optional[PluginContext] = None,
    ):
        """
        Initialize the plugin manager.
        
        Args:
            config: Manager configuration
            context: Shared plugin context
        """
        self.config = config or PluginManagerConfig()
        self._context = context or PluginContext()
        
        # Link context to manager
        self._context.plugin_registry = PluginRegistry
        self._context.event_bus = EventBus
        
        # State tracking
        self._started_plugins: Set[str] = set()
        self._failed_plugins: Dict[str, Exception] = {}
        self._restart_counts: Dict[str, int] = defaultdict(int)
        
        # Threading
        self._lock = threading.RLock()
        self._shutdown_event = threading.Event()
        self._health_thread: Optional[threading.Thread] = None
        
        # Callbacks
        self._on_plugin_started: List[Callable[[str], None]] = []
        self._on_plugin_stopped: List[Callable[[str], None]] = []
        self._on_plugin_failed: List[Callable[[str, Exception], None]] = []
        
        logger.info("PluginManager initialized")
    
    # ==================== Lifecycle ====================
    
    def initialize(self) -> None:
        """
        Initialize the plugin manager.
        
        This will:
        1. Discover plugins if auto_discover is enabled
        2. Start plugins if auto_start is enabled
        3. Start health monitoring
        """
        logger.info("Initializing PluginManager...")
        
        if self.config.auto_discover:
            self.discover_all()
        
        if self.config.auto_start:
            self.start_all()
        
        # Start health monitoring
        if self.config.health_check_interval > 0:
            self._start_health_monitor()
        
        # Register signal handlers for graceful shutdown
        if self.config.graceful_shutdown:
            self._register_signal_handlers()
        
        logger.info("PluginManager initialization complete")
    
    def shutdown(self, timeout: Optional[float] = None) -> None:
        """
        Shutdown the plugin manager.
        
        Stops all plugins gracefully with timeout.
        
        Args:
            timeout: Maximum time to wait for shutdown
        """
        timeout = timeout or self.config.stop_timeout
        logger.info(f"Shutting down PluginManager (timeout={timeout}s)...")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Stop health monitor
        if self._health_thread and self._health_thread.is_alive():
            self._health_thread.join(timeout=5.0)
        
        # Stop all plugins
        self.stop_all(timeout=timeout)
        
        logger.info("PluginManager shutdown complete")
    
    # ==================== Discovery ====================
    
    def discover(self, path: Union[str, Path]) -> List[str]:
        """
        Discover plugins from a directory.
        
        Args:
            path: Directory to search
            
        Returns:
            List of discovered plugin names
        """
        path = Path(path)
        logger.info(f"Discovering plugins in {path}")
        
        discovered = PluginRegistry.discover(path)
        
        for name in discovered:
            EventBus.publish(PluginLoadedEvent(
                source="PluginManager",
                plugin_name=name,
                plugin_version=PluginRegistry.get_metadata(name).version,
            ))
        
        return discovered
    
    def discover_all(self) -> List[str]:
        """Discover plugins from all configured directories."""
        all_discovered = []
        
        for dir_path in self.config.plugin_dirs:
            path = Path(dir_path)
            if path.exists():
                all_discovered.extend(self.discover(path))
            else:
                logger.warning(f"Plugin directory not found: {path}")
        
        logger.info(f"Total plugins discovered: {len(all_discovered)}")
        return all_discovered
    
    # ==================== Plugin Access ====================
    
    def get(self, name: str) -> BasePlugin:
        """
        Get a plugin instance.
        
        Args:
            name: Plugin name
            
        Returns:
            Plugin instance
            
        Raises:
            PluginNotFoundError: If plugin not found
        """
        return PluginRegistry.get_instance(name, self._context)
    
    def get_by_capability(
        self,
        capability: PluginCapability,
    ) -> List[BasePlugin]:
        """Get all plugins with a specific capability."""
        names = PluginRegistry.get_by_capability(capability)
        return [self.get(name) for name in names if name in self._started_plugins]
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all plugins with their status."""
        result = []
        
        for name in PluginRegistry.list_plugins():
            try:
                plugin = PluginRegistry.get_instance(name, singleton=False)
                metadata = PluginRegistry.get_metadata(name)
                
                result.append({
                    "name": name,
                    "version": metadata.version,
                    "state": plugin.state.name if plugin else "UNKNOWN",
                    "started": name in self._started_plugins,
                    "failed": name in self._failed_plugins,
                    "enabled": metadata.enabled,
                    "capabilities": [c.name for c in metadata.capabilities],
                })
            except Exception as e:
                result.append({
                    "name": name,
                    "error": str(e),
                })
        
        return result
    
    # ==================== Start/Stop ====================
    
    def start(self, name: str, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Start a single plugin.
        
        Args:
            name: Plugin name
            config: Plugin configuration
        """
        with self._lock:
            if name in self._started_plugins:
                logger.debug(f"Plugin {name} already started")
                return
            
            try:
                logger.info(f"Starting plugin: {name}")
                
                # Get or create instance
                plugin = PluginRegistry.get_instance(name, self._context)
                
                # Get config from manager config or parameter
                plugin_config = config or self.config.plugin_configs.get(name, {})
                
                # Configure and start
                plugin.configure(plugin_config)
                plugin.start()
                
                self._started_plugins.add(name)
                self._failed_plugins.pop(name, None)
                
                # Publish event
                EventBus.publish(PluginStartedEvent(
                    source="PluginManager",
                    plugin_name=name,
                ))
                
                # Callbacks
                for callback in self._on_plugin_started:
                    try:
                        callback(name)
                    except Exception:
                        pass
                
                logger.info(f"Plugin {name} started successfully")
                
            except Exception as e:
                logger.error(f"Failed to start plugin {name}: {e}")
                self._failed_plugins[name] = e
                
                EventBus.publish(PluginErrorEvent(
                    source="PluginManager",
                    plugin_name=name,
                    error_type=type(e).__name__,
                    error_message=str(e),
                ))
                
                for callback in self._on_plugin_failed:
                    try:
                        callback(name, e)
                    except Exception:
                        pass
                
                raise
    
    def stop(self, name: str) -> None:
        """
        Stop a single plugin.
        
        Args:
            name: Plugin name
        """
        with self._lock:
            if name not in self._started_plugins:
                logger.debug(f"Plugin {name} not started")
                return
            
            try:
                logger.info(f"Stopping plugin: {name}")
                
                plugin = PluginRegistry.get_instance(name, singleton=True)
                uptime = plugin.uptime
                
                plugin.stop()
                
                self._started_plugins.discard(name)
                
                # Publish event
                EventBus.publish(PluginStoppedEvent(
                    source="PluginManager",
                    plugin_name=name,
                    uptime_seconds=uptime,
                ))
                
                # Callbacks
                for callback in self._on_plugin_stopped:
                    try:
                        callback(name)
                    except Exception:
                        pass
                
                logger.info(f"Plugin {name} stopped")
                
            except Exception as e:
                logger.error(f"Error stopping plugin {name}: {e}")
                raise
    
    def start_all(self) -> Dict[str, bool]:
        """
        Start all enabled plugins in dependency order.
        
        Returns:
            Dict mapping plugin name to success status
        """
        logger.info("Starting all enabled plugins...")
        
        results = {}
        enabled_plugins = PluginRegistry.get_enabled()
        
        # Resolve dependencies for all plugins
        start_order = []
        for name in enabled_plugins:
            try:
                deps = PluginRegistry.resolve_dependencies(name)
                for dep in deps:
                    if dep not in start_order:
                        start_order.append(dep)
            except Exception as e:
                logger.error(f"Dependency resolution failed for {name}: {e}")
                results[name] = False
        
        # Start in order
        for name in start_order:
            if name not in enabled_plugins:
                continue
            
            try:
                self.start(name)
                results[name] = True
            except Exception:
                results[name] = False
        
        success_count = sum(1 for v in results.values() if v)
        logger.info(
            f"Started {success_count}/{len(results)} plugins successfully"
        )
        
        return results
    
    def stop_all(self, timeout: Optional[float] = None) -> None:
        """
        Stop all running plugins.
        
        Stops in reverse dependency order.
        
        Args:
            timeout: Maximum time to wait
        """
        logger.info("Stopping all plugins...")
        
        # Stop in reverse order
        to_stop = list(self._started_plugins)
        to_stop.reverse()
        
        for name in to_stop:
            try:
                self.stop(name)
            except Exception as e:
                logger.error(f"Error stopping {name}: {e}")
        
        logger.info("All plugins stopped")
    
    def restart(self, name: str) -> None:
        """Restart a plugin."""
        self.stop(name)
        self.start(name)
    
    # ==================== Health Monitoring ====================
    
    def health_check(self, name: str) -> bool:
        """Check if a plugin is healthy."""
        if name not in self._started_plugins:
            return False
        
        try:
            plugin = PluginRegistry.get_instance(name, singleton=True)
            return plugin.health_check()
        except Exception:
            return False
    
    def health_check_all(self) -> Dict[str, bool]:
        """Check health of all started plugins."""
        return {name: self.health_check(name) for name in self._started_plugins}
    
    def _start_health_monitor(self) -> None:
        """Start background health monitoring thread."""
        def monitor():
            while not self._shutdown_event.is_set():
                try:
                    health = self.health_check_all()
                    
                    for name, is_healthy in health.items():
                        if not is_healthy:
                            logger.warning(f"Plugin {name} health check failed")
                            
                            if self.config.auto_restart_failed:
                                self._try_restart(name)
                    
                except Exception as e:
                    logger.error(f"Health monitor error: {e}")
                
                # Wait for next check
                self._shutdown_event.wait(self.config.health_check_interval)
        
        self._health_thread = threading.Thread(
            target=monitor,
            name="PluginHealthMonitor",
            daemon=True,
        )
        self._health_thread.start()
    
    def _try_restart(self, name: str) -> bool:
        """Attempt to restart a failed plugin."""
        with self._lock:
            if self._restart_counts[name] >= self.config.max_restart_attempts:
                logger.error(
                    f"Plugin {name} exceeded max restart attempts "
                    f"({self.config.max_restart_attempts})"
                )
                return False
            
            try:
                logger.info(f"Attempting to restart plugin {name}...")
                self._restart_counts[name] += 1
                self.restart(name)
                return True
            except Exception as e:
                logger.error(f"Failed to restart {name}: {e}")
                return False
    
    # ==================== Callbacks ====================
    
    def on_plugin_started(self, callback: Callable[[str], None]) -> None:
        """Register callback for plugin start events."""
        self._on_plugin_started.append(callback)
    
    def on_plugin_stopped(self, callback: Callable[[str], None]) -> None:
        """Register callback for plugin stop events."""
        self._on_plugin_stopped.append(callback)
    
    def on_plugin_failed(
        self,
        callback: Callable[[str, Exception], None],
    ) -> None:
        """Register callback for plugin failure events."""
        self._on_plugin_failed.append(callback)
    
    # ==================== Signal Handling ====================
    
    def _register_signal_handlers(self) -> None:
        """Register signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown...")
            self.shutdown()
        
        try:
            signal.signal(signal.SIGTERM, signal_handler)
            signal.signal(signal.SIGINT, signal_handler)
        except Exception as e:
            # May fail in non-main thread
            logger.debug(f"Could not register signal handlers: {e}")
    
    # ==================== Statistics ====================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get plugin manager statistics."""
        return {
            "total_plugins": PluginRegistry.count(),
            "started_plugins": len(self._started_plugins),
            "failed_plugins": len(self._failed_plugins),
            "plugin_dirs": self.config.plugin_dirs,
            "health": self.health_check_all(),
        }
    
    # ==================== Context Manager ====================
    
    def __enter__(self) -> "PluginManager":
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.shutdown()


# ============== Convenience Function ==============

_manager: Optional[PluginManager] = None


def get_plugin_manager() -> PluginManager:
    """Get the global plugin manager instance."""
    global _manager
    if _manager is None:
        _manager = PluginManager()
    return _manager


def init_plugins(config: Optional[PluginManagerConfig] = None) -> PluginManager:
    """Initialize the global plugin manager."""
    global _manager
    _manager = PluginManager(config)
    _manager.initialize()
    return _manager

