"""
Base Plugin Class
=================

Abstract base class for all plugins with full lifecycle management,
configuration validation, and extensibility hooks.

This follows the Template Method pattern and provides extension points
for plugin authors to customize behavior without modifying core code.

Academic Reference:
    - Gamma et al., "Design Patterns" (Template Method, p. 325)
    - Martin, "Clean Architecture" (Plugin Architecture, Ch. 22)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Generic,
    List,
    Optional,
    Protocol,
    Set,
    Type,
    TypeVar,
    runtime_checkable,
)
import threading
import yaml
import json
import logging

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


class PluginState(Enum):
    """
    Plugin lifecycle states following the State pattern.
    
    State Machine:
        UNLOADED -> LOADED -> CONFIGURED -> STARTED -> STOPPED -> UNLOADED
                      ^                        |
                      |________________________|
    """
    UNLOADED = auto()      # Plugin not loaded
    LOADED = auto()        # Plugin class loaded but not configured
    CONFIGURED = auto()    # Configuration validated and applied
    STARTED = auto()       # Plugin is running and active
    STOPPED = auto()       # Plugin stopped gracefully
    FAILED = auto()        # Plugin failed during lifecycle
    SUSPENDED = auto()     # Temporarily suspended (for hot-reload)


class PluginCapability(Enum):
    """
    Capabilities that plugins can provide.
    Used for dependency resolution and feature flags.
    """
    # Agent capabilities
    CONTENT_PROVIDER = auto()      # Provides content for route points
    CONTENT_EVALUATOR = auto()     # Evaluates/judges content
    
    # Data capabilities
    API_INTEGRATION = auto()       # External API integration
    CACHE_PROVIDER = auto()        # Caching functionality
    STORAGE_PROVIDER = auto()      # Persistent storage
    
    # Enhancement capabilities
    PREPROCESSING = auto()         # Data preprocessing
    POSTPROCESSING = auto()        # Output formatting/enhancement
    ENRICHMENT = auto()            # Content enrichment
    
    # Infrastructure capabilities
    MONITORING = auto()            # Metrics and monitoring
    LOGGING = auto()               # Enhanced logging
    AUTHENTICATION = auto()        # Auth/authz
    
    # ML capabilities
    ML_MODEL = auto()              # Machine learning model
    EMBEDDING = auto()             # Vector embeddings
    RANKING = auto()               # Content ranking


class PluginMetadata(BaseModel):
    """
    Plugin metadata with validation.
    
    Loaded from plugin manifest (plugin.yaml) or defined in code.
    Follows semantic versioning and provides dependency declarations.
    """
    # Identity
    name: str = Field(..., min_length=1, max_length=100)
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+(-[\w.]+)?$")
    description: str = Field(default="", max_length=500)
    
    # Authorship
    author: str = Field(default="Unknown")
    author_email: Optional[str] = None
    license: str = Field(default="MIT")
    homepage: Optional[str] = None
    
    # Categorization
    category: str = Field(default="general")
    tags: List[str] = Field(default_factory=list)
    capabilities: List[PluginCapability] = Field(default_factory=list)
    
    # Dependencies
    depends_on: List[str] = Field(default_factory=list)  # Other plugin names
    conflicts_with: List[str] = Field(default_factory=list)
    python_requires: str = Field(default=">=3.10")
    
    # Runtime
    priority: int = Field(default=100, ge=0, le=1000)  # Lower = higher priority
    enabled: bool = Field(default=True)
    auto_start: bool = Field(default=True)
    
    # Configuration schema (JSON Schema)
    config_schema: Optional[Dict[str, Any]] = None
    
    @field_validator('version')
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate semantic versioning."""
        import re
        if not re.match(r"^\d+\.\d+\.\d+(-[\w.]+)?$", v):
            raise ValueError(f"Invalid version format: {v}")
        return v
    
    @classmethod
    def from_yaml(cls, path: Path) -> "PluginMetadata":
        """Load metadata from YAML manifest."""
        with open(path) as f:
            data = yaml.safe_load(f)
        
        # Convert capability strings to enums
        if "capabilities" in data:
            data["capabilities"] = [
                PluginCapability[cap.upper()] 
                for cap in data["capabilities"]
            ]
        
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export metadata as dictionary."""
        data = self.model_dump()
        data["capabilities"] = [cap.name for cap in self.capabilities]
        return data


@dataclass
class PluginContext:
    """
    Runtime context passed to plugins.
    
    Provides access to shared resources, configuration, and
    inter-plugin communication without tight coupling.
    
    This follows the Dependency Injection pattern.
    """
    # Shared resources
    config: Dict[str, Any] = field(default_factory=dict)
    shared_state: Dict[str, Any] = field(default_factory=dict)
    
    # Runtime info
    plugin_dir: Optional[Path] = None
    work_dir: Optional[Path] = None
    cache_dir: Optional[Path] = None
    
    # References to other components (set by PluginManager)
    event_bus: Optional[Any] = None
    plugin_registry: Optional[Any] = None
    service_locator: Optional[Any] = None
    
    # Thread safety
    _lock: threading.Lock = field(default_factory=threading.Lock)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Thread-safe config access."""
        with self._lock:
            return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Thread-safe config update."""
        with self._lock:
            self.config[key] = value


@runtime_checkable
class PluginProtocol(Protocol):
    """
    Protocol defining the plugin contract.
    
    This allows structural subtyping - any class implementing
    these methods can be treated as a plugin, even without
    explicit inheritance.
    """
    metadata: PluginMetadata
    state: PluginState
    
    def configure(self, config: Dict[str, Any]) -> None: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def health_check(self) -> bool: ...


TConfig = TypeVar("TConfig", bound=BaseModel)


class BasePlugin(ABC, Generic[TConfig]):
    """
    Abstract base class for all plugins.
    
    Provides:
    1. Lifecycle management (configure, start, stop, destroy)
    2. Configuration validation with Pydantic
    3. Health checking
    4. Hook integration points
    5. Thread-safe state management
    
    Plugin authors should:
    1. Define a config model (optional)
    2. Implement _on_start() and _on_stop()
    3. Optionally override other lifecycle methods
    
    Example:
        class MyConfig(BaseModel):
            api_key: str
            timeout: int = 30
        
        class MyPlugin(BasePlugin[MyConfig]):
            config_class = MyConfig
            
            def _on_start(self) -> None:
                # Initialize resources
                self.client = MyAPI(self.config.api_key)
            
            def _on_stop(self) -> None:
                # Cleanup
                self.client.close()
    """
    
    # Class-level metadata (override in subclasses or load from manifest)
    metadata: ClassVar[PluginMetadata]
    config_class: ClassVar[Optional[Type[BaseModel]]] = None
    
    def __init__(self, context: Optional[PluginContext] = None):
        """
        Initialize plugin with optional context.
        
        Args:
            context: Runtime context with shared resources
        """
        self._context = context or PluginContext()
        self._state = PluginState.LOADED
        self._config: Optional[TConfig] = None
        self._lock = threading.RLock()
        self._started_at: Optional[datetime] = None
        self._stopped_at: Optional[datetime] = None
        self._error: Optional[Exception] = None
        self._health_checks: List[Callable[[], bool]] = []
        
        # Extension points for hooks
        self._pre_start_hooks: List[Callable] = []
        self._post_start_hooks: List[Callable] = []
        self._pre_stop_hooks: List[Callable] = []
        self._post_stop_hooks: List[Callable] = []
        
        logger.debug(f"Plugin {self.name} instantiated")
    
    # ==================== Properties ====================
    
    @property
    def name(self) -> str:
        """Plugin name from metadata."""
        return getattr(self.__class__, 'metadata', 
                      PluginMetadata(name=self.__class__.__name__, version="0.0.1")).name
    
    @property
    def version(self) -> str:
        """Plugin version from metadata."""
        return getattr(self.__class__, 'metadata',
                      PluginMetadata(name=self.__class__.__name__, version="0.0.1")).version
    
    @property
    def state(self) -> PluginState:
        """Current plugin state (thread-safe)."""
        with self._lock:
            return self._state
    
    @property
    def config(self) -> Optional[TConfig]:
        """Validated configuration."""
        return self._config
    
    @property
    def context(self) -> PluginContext:
        """Plugin runtime context."""
        return self._context
    
    @property
    def is_running(self) -> bool:
        """Check if plugin is currently running."""
        return self.state == PluginState.STARTED
    
    @property
    def uptime(self) -> Optional[float]:
        """Seconds since plugin started, or None if not running."""
        if self._started_at and self.is_running:
            return (datetime.now() - self._started_at).total_seconds()
        return None
    
    # ==================== Lifecycle Methods ====================
    
    def configure(self, config: Dict[str, Any]) -> None:
        """
        Configure the plugin with validated settings.
        
        This is the first lifecycle method called after instantiation.
        Configuration is validated against the config_class schema.
        
        Args:
            config: Configuration dictionary
            
        Raises:
            ValidationError: If configuration is invalid
            StateError: If plugin is not in LOADED state
        """
        with self._lock:
            if self._state not in (PluginState.LOADED, PluginState.STOPPED):
                raise RuntimeError(
                    f"Cannot configure plugin in state {self._state.name}"
                )
            
            try:
                # Validate config if schema provided
                if self.config_class:
                    self._config = self.config_class(**config)
                else:
                    self._config = config  # type: ignore
                
                # Call hook for subclass customization
                self._on_configure(config)
                
                self._state = PluginState.CONFIGURED
                logger.info(f"Plugin {self.name} configured successfully")
                
            except Exception as e:
                self._state = PluginState.FAILED
                self._error = e
                logger.error(f"Plugin {self.name} configuration failed: {e}")
                raise
    
    def start(self) -> None:
        """
        Start the plugin.
        
        Executes pre-start hooks, calls _on_start(), then post-start hooks.
        Plugin must be in CONFIGURED state.
        
        Raises:
            StateError: If plugin is not in CONFIGURED state
            StartupError: If startup fails
        """
        with self._lock:
            if self._state not in (PluginState.CONFIGURED, PluginState.STOPPED):
                raise RuntimeError(
                    f"Cannot start plugin in state {self._state.name}"
                )
            
            try:
                # Execute pre-start hooks
                for hook in self._pre_start_hooks:
                    hook(self)
                
                # Call subclass implementation
                self._on_start()
                
                self._started_at = datetime.now()
                self._state = PluginState.STARTED
                
                # Execute post-start hooks
                for hook in self._post_start_hooks:
                    hook(self)
                
                logger.info(f"Plugin {self.name} v{self.version} started")
                
            except Exception as e:
                self._state = PluginState.FAILED
                self._error = e
                logger.error(f"Plugin {self.name} start failed: {e}")
                raise
    
    def stop(self) -> None:
        """
        Stop the plugin gracefully.
        
        Executes pre-stop hooks, calls _on_stop(), then post-stop hooks.
        Resources should be released in _on_stop().
        
        Raises:
            StateError: If plugin is not in STARTED state
        """
        with self._lock:
            if self._state != PluginState.STARTED:
                logger.warning(
                    f"Plugin {self.name} stop called in state {self._state.name}"
                )
                return
            
            try:
                # Execute pre-stop hooks
                for hook in self._pre_stop_hooks:
                    hook(self)
                
                # Call subclass implementation
                self._on_stop()
                
                self._stopped_at = datetime.now()
                self._state = PluginState.STOPPED
                
                # Execute post-stop hooks
                for hook in self._post_stop_hooks:
                    hook(self)
                
                logger.info(f"Plugin {self.name} stopped")
                
            except Exception as e:
                self._state = PluginState.FAILED
                self._error = e
                logger.error(f"Plugin {self.name} stop failed: {e}")
                raise
    
    def restart(self) -> None:
        """Restart the plugin (stop + start)."""
        self.stop()
        self.start()
    
    def destroy(self) -> None:
        """
        Destroy the plugin and release all resources.
        
        Called when plugin is being unloaded. After this,
        the plugin instance should not be used.
        """
        with self._lock:
            if self._state == PluginState.STARTED:
                self.stop()
            
            self._on_destroy()
            self._state = PluginState.UNLOADED
            logger.info(f"Plugin {self.name} destroyed")
    
    # ==================== Health & Status ====================
    
    def health_check(self) -> bool:
        """
        Check if plugin is healthy.
        
        Runs all registered health checks and the _check_health() hook.
        Returns True only if all checks pass.
        """
        if not self.is_running:
            return False
        
        try:
            # Run registered health checks
            for check in self._health_checks:
                if not check():
                    return False
            
            # Run subclass health check
            return self._check_health()
            
        except Exception as e:
            logger.warning(f"Plugin {self.name} health check failed: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get detailed plugin status."""
        return {
            "name": self.name,
            "version": self.version,
            "state": self.state.name,
            "is_running": self.is_running,
            "uptime": self.uptime,
            "started_at": self._started_at.isoformat() if self._started_at else None,
            "stopped_at": self._stopped_at.isoformat() if self._stopped_at else None,
            "healthy": self.health_check() if self.is_running else False,
            "error": str(self._error) if self._error else None,
        }
    
    # ==================== Hook Registration ====================
    
    def add_pre_start_hook(self, hook: Callable) -> None:
        """Register a hook to run before start()."""
        self._pre_start_hooks.append(hook)
    
    def add_post_start_hook(self, hook: Callable) -> None:
        """Register a hook to run after start()."""
        self._post_start_hooks.append(hook)
    
    def add_pre_stop_hook(self, hook: Callable) -> None:
        """Register a hook to run before stop()."""
        self._pre_stop_hooks.append(hook)
    
    def add_post_stop_hook(self, hook: Callable) -> None:
        """Register a hook to run after stop()."""
        self._post_stop_hooks.append(hook)
    
    def add_health_check(self, check: Callable[[], bool]) -> None:
        """Register a health check function."""
        self._health_checks.append(check)
    
    # ==================== Abstract Methods (Override in Subclasses) ====================
    
    @abstractmethod
    def _on_start(self) -> None:
        """
        Called when plugin starts.
        
        Initialize resources, connections, background tasks here.
        Override in subclasses.
        """
        pass
    
    @abstractmethod
    def _on_stop(self) -> None:
        """
        Called when plugin stops.
        
        Clean up resources, close connections, stop tasks here.
        Override in subclasses.
        """
        pass
    
    # ==================== Optional Hooks (Override if Needed) ====================
    
    def _on_configure(self, config: Dict[str, Any]) -> None:
        """
        Called during configuration.
        
        Perform additional configuration validation or setup here.
        Override in subclasses if needed.
        """
        pass
    
    def _on_destroy(self) -> None:
        """
        Called when plugin is destroyed.
        
        Final cleanup. Override in subclasses if needed.
        """
        pass
    
    def _check_health(self) -> bool:
        """
        Custom health check logic.
        
        Override to add plugin-specific health checks.
        Returns True if healthy.
        """
        return True
    
    # ==================== Utility Methods ====================
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name}, state={self.state.name})>"
    
    def __str__(self) -> str:
        return f"{self.name} v{self.version}"


class ContentProviderPlugin(BasePlugin):
    """
    Specialized base class for plugins that provide content.
    
    This is the primary extension point for adding new content types
    (weather, food, events, etc.) to the tour guide system.
    """
    
    @abstractmethod
    def search_content(self, location: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for content related to a location.
        
        Args:
            location: Location name or address
            context: Additional context (user profile, preferences, etc.)
            
        Returns:
            Content result with title, description, url, etc.
        """
        pass
    
    @abstractmethod
    def get_content_type(self) -> str:
        """Return the type of content this plugin provides."""
        pass


class ContentEvaluatorPlugin(BasePlugin):
    """
    Specialized base class for plugins that evaluate/rank content.
    
    Used to implement custom scoring algorithms or judge logic.
    """
    
    @abstractmethod
    def evaluate(
        self, 
        candidates: List[Dict[str, Any]], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate and rank content candidates.
        
        Args:
            candidates: List of content results to evaluate
            context: Evaluation context (user profile, location, etc.)
            
        Returns:
            Evaluation result with scores and selected content
        """
        pass

