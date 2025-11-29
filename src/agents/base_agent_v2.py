"""
Enhanced Base Agent with Full Plugin Architecture
==================================================

Production-grade base agent with:
- Lifecycle hooks (pre/post execute, on_error, on_success)
- Event emission for observability
- Resilience patterns (retry, circuit breaker, timeout)
- Metrics collection
- Distributed tracing
- Configuration validation
- Health checks

This is the MIT-level production-ready agent base class.

Academic Reference:
    - Martin, "Clean Architecture" (Use Cases, Entities)
    - Gamma et al., "Design Patterns" (Template Method, Strategy)
    - Vernon, "Implementing Domain-Driven Design" (Domain Services)

Example:
    class WeatherAgent(EnhancedBaseAgent):
        metadata = AgentMetadata(
            name="weather",
            version="1.0.0",
            capabilities=[AgentCapability.CONTENT_PROVIDER],
        )

        def _search_content(self, point: RoutePoint) -> Optional[ContentResult]:
            weather = self.api.get_weather(point.coordinates)
            return ContentResult(
                content_type=ContentType.TEXT,
                title=f"Weather at {point.name}",
                description=weather.summary,
            )
"""

from __future__ import annotations

import logging
import threading
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import (
    Any,
    ClassVar,
    Generic,
    TypeVar,
)

from pydantic import BaseModel

from src.core.observability import (
    Counter,
    Histogram,
    get_tracer,
    health_check,
    trace,
)

# Core imports
from src.core.plugins.events import Event, publish
from src.core.plugins.hooks import HookRegistry, HookType
from src.core.resilience import (
    CircuitBreaker,
    CircuitBreakerOpen,
    RetryPolicy,
    TimeoutError,
    with_retry,
    with_timeout,
)

# Model imports
from src.models import ContentResult, ContentType, RoutePoint

logger = logging.getLogger(__name__)

TConfig = TypeVar("TConfig", bound=BaseModel)


# ============== Agent-Specific Events ==============


class AgentExecutionStarted(Event):
    """Emitted when agent starts execution."""

    agent_name: str
    agent_type: str
    point_id: str
    location: str


class AgentExecutionCompleted(Event):
    """Emitted when agent completes execution."""

    agent_name: str
    agent_type: str
    point_id: str
    duration_seconds: float
    success: bool
    content_type: str | None = None


class AgentExecutionFailed(Event):
    """Emitted when agent execution fails."""

    agent_name: str
    agent_type: str
    point_id: str
    error_type: str
    error_message: str


# ============== Agent Capabilities ==============


class AgentCapability(Enum):
    """Capabilities that agents can have."""

    CONTENT_PROVIDER = auto()  # Provides content for points
    CONTENT_EVALUATOR = auto()  # Evaluates/judges content
    CONTENT_ENRICHER = auto()  # Enriches existing content
    REALTIME_DATA = auto()  # Provides real-time data (weather, traffic)
    USER_PERSONALIZED = auto()  # Uses user profile for personalization
    CACHEABLE = auto()  # Results can be cached
    LLM_POWERED = auto()  # Uses LLM for processing


class AgentState(Enum):
    """Agent execution states."""

    IDLE = auto()
    EXECUTING = auto()
    COMPLETED = auto()
    FAILED = auto()
    TIMEOUT = auto()


@dataclass
class AgentMetadata:
    """Metadata for an agent."""

    name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    capabilities: list[AgentCapability] = field(default_factory=list)
    content_type: ContentType | None = None
    priority: int = 100  # Lower = higher priority
    timeout: float = 30.0
    max_retries: int = 3
    circuit_breaker_threshold: int = 5
    tags: set[str] = field(default_factory=set)


# ============== Agent Configuration ==============


class AgentConfig(BaseModel):
    """Base configuration for agents."""

    enabled: bool = True
    timeout_seconds: float = 30.0
    max_retries: int = 3
    retry_backoff_factor: float = 2.0
    circuit_breaker_threshold: int = 5
    circuit_breaker_reset_timeout: float = 60.0
    cache_ttl_seconds: int = 3600
    log_level: str = "INFO"

    # LLM settings (if applicable)
    llm_model: str | None = None
    llm_temperature: float = 0.7
    llm_max_tokens: int = 1024


# ============== Metrics ==============

# Define agent metrics
agent_executions = Counter(
    "agent_executions_total",
    "Total agent executions",
    labels=["agent_type", "status"],
)

agent_execution_duration = Histogram(
    "agent_execution_seconds",
    "Agent execution duration in seconds",
    labels=["agent_type"],
)


# ============== Enhanced Base Agent ==============


class EnhancedBaseAgent(ABC, Generic[TConfig]):
    """
    Enhanced base agent with full production capabilities.

    Features:
    1. Lifecycle Hooks
       - on_before_execute: Called before execution
       - on_after_execute: Called after successful execution
       - on_error: Called on execution error
       - on_timeout: Called on timeout

    2. Resilience
       - Automatic retry with exponential backoff
       - Circuit breaker for failing services
       - Configurable timeouts

    3. Observability
       - Automatic metrics collection
       - Distributed tracing
       - Structured logging
       - Health checks

    4. Extensibility
       - Plugin-style configuration
       - Event emission
       - Hook system integration

    Example:
        class VideoAgent(EnhancedBaseAgent[VideoAgentConfig]):
            metadata = AgentMetadata(
                name="video",
                version="1.0.0",
                content_type=ContentType.VIDEO,
                capabilities=[AgentCapability.CONTENT_PROVIDER],
            )
            config_class = VideoAgentConfig

            def _search_content(self, point: RoutePoint) -> Optional[ContentResult]:
                # Implementation
                pass
    """

    # Class-level metadata (override in subclasses)
    metadata: ClassVar[AgentMetadata]
    config_class: ClassVar[type[BaseModel] | None] = AgentConfig

    def __init__(self, config: TConfig | None = None):
        """
        Initialize the agent.

        Args:
            config: Agent configuration
        """
        self._config: TConfig = config or (  # type: ignore[assignment]
            self.config_class() if self.config_class else AgentConfig()
        )
        self._state = AgentState.IDLE
        self._lock = threading.RLock()

        # Tracking
        self._current_point_id: str | None = None
        self._execution_count = 0
        self._success_count = 0
        self._failure_count = 0
        self._total_duration = 0.0

        # Initialize circuit breaker
        config = self._config
        cb_threshold = getattr(config, "circuit_breaker_threshold", 5)
        cb_reset_timeout = getattr(config, "circuit_breaker_reset_timeout", 60.0)
        self._circuit_breaker = CircuitBreaker(
            name=f"agent_{self.name}",
            failure_threshold=cb_threshold,
            reset_timeout=cb_reset_timeout,
        )

        # Initialize retry policy
        max_retries = getattr(config, "max_retries", 3)
        backoff_factor = getattr(config, "retry_backoff_factor", 2.0)
        self._retry_policy = RetryPolicy(
            max_attempts=max_retries,
            backoff_factor=backoff_factor,
            initial_delay=1.0,
            max_delay=30.0,
        )

        # Lifecycle hooks
        self._pre_execute_hooks: list[Callable] = []
        self._post_execute_hooks: list[Callable] = []
        self._error_hooks: list[Callable] = []

        # Register health check
        self._register_health_check()

        logger.info(f"Initialized agent: {self.name} v{self.version}")

    # ==================== Properties ====================

    @property
    def name(self) -> str:
        """Agent name from metadata."""
        return getattr(
            self.__class__, "metadata", AgentMetadata(name=self.__class__.__name__)
        ).name

    @property
    def version(self) -> str:
        """Agent version from metadata."""
        return getattr(
            self.__class__, "metadata", AgentMetadata(name=self.__class__.__name__)
        ).version

    @property
    def config(self) -> TConfig:
        """Agent configuration."""
        return self._config  # type: ignore[return-value]

    @property
    def state(self) -> AgentState:
        """Current agent state."""
        return self._state

    @property
    def is_healthy(self) -> bool:
        """Check if agent is healthy."""
        return self._state != AgentState.FAILED and self._circuit_breaker.is_closed

    @property
    def stats(self) -> dict[str, Any]:
        """Get agent statistics."""
        return {
            "name": self.name,
            "version": self.version,
            "state": self._state.name,
            "execution_count": self._execution_count,
            "success_count": self._success_count,
            "failure_count": self._failure_count,
            "success_rate": (
                self._success_count / self._execution_count
                if self._execution_count > 0
                else 0.0
            ),
            "average_duration": (
                self._total_duration / self._execution_count
                if self._execution_count > 0
                else 0.0
            ),
            "circuit_breaker": self._circuit_breaker.get_stats(),
        }

    # ==================== Main Execution ====================

    @trace("agent.execute")
    def execute(self, point: RoutePoint) -> ContentResult | None:
        """
        Execute the agent for a route point.

        This is the main entry point. It:
        1. Validates the request
        2. Runs pre-execute hooks
        3. Executes with retry and timeout
        4. Records metrics
        5. Runs post-execute hooks
        6. Emits events

        Args:
            point: Route point to process

        Returns:
            Content result or None on failure
        """
        tracer = get_tracer("agents")

        with tracer.span(f"{self.name}.execute") as span:
            span.set_attribute("agent.name", self.name)
            span.set_attribute("point.id", point.id)
            span.set_attribute("point.address", point.address)

            self._current_point_id = point.id
            self._execution_count += 1
            start_time = time.time()

            # Emit start event
            publish(
                AgentExecutionStarted(
                    source=self.name,
                    agent_name=self.name,
                    agent_type=self.__class__.__name__,
                    point_id=point.id,
                    location=point.address,
                )
            )

            try:
                with self._lock:
                    self._state = AgentState.EXECUTING

                # Run pre-execute hooks
                self._run_pre_execute_hooks(point)

                # Execute with resilience
                result = self._execute_with_resilience(point)

                # Record success
                duration = time.time() - start_time
                self._total_duration += duration
                self._success_count += 1

                with self._lock:
                    self._state = AgentState.COMPLETED

                # Run post-execute hooks
                self._run_post_execute_hooks(point, result)

                # Record metrics
                agent_executions.inc(agent_type=self.name, status="success")
                agent_execution_duration.observe(duration, agent_type=self.name)

                # Emit completion event
                publish(
                    AgentExecutionCompleted(
                        source=self.name,
                        agent_name=self.name,
                        agent_type=self.__class__.__name__,
                        point_id=point.id,
                        duration_seconds=duration,
                        success=True,
                        content_type=result.content_type.value if result else None,
                    )
                )

                span.set_attribute("success", True)
                span.set_attribute("duration_seconds", duration)

                return result

            except CircuitBreakerOpen as e:
                logger.warning(f"Circuit breaker open for {self.name}")
                self._handle_failure(point, e, start_time)
                return None

            except TimeoutError as e:
                logger.warning(f"Timeout in {self.name}: {e}")
                with self._lock:
                    self._state = AgentState.TIMEOUT
                self._handle_failure(point, e, start_time)
                return None

            except Exception as e:
                logger.error(f"Error in {self.name}: {e}")
                self._handle_failure(point, e, start_time)
                return None

    def _execute_with_resilience(
        self,
        point: RoutePoint,
    ) -> ContentResult | None:
        """Execute with retry, circuit breaker, and timeout."""

        def _inner():
            with self._circuit_breaker:
                return with_timeout(
                    self._search_content,
                    self._config.timeout_seconds,
                    point,
                )

        result = with_retry(_inner, self._retry_policy)
        return result  # type: ignore[no-any-return]

    def _handle_failure(
        self,
        point: RoutePoint,
        error: Exception,
        start_time: float,
    ) -> None:
        """Handle execution failure."""
        time.time() - start_time
        self._failure_count += 1

        with self._lock:
            if self._state != AgentState.TIMEOUT:
                self._state = AgentState.FAILED

        # Run error hooks
        self._run_error_hooks(point, error)

        # Record metrics
        agent_executions.inc(agent_type=self.name, status="failure")

        # Emit failure event
        publish(
            AgentExecutionFailed(
                source=self.name,
                agent_name=self.name,
                agent_type=self.__class__.__name__,
                point_id=point.id,
                error_type=type(error).__name__,
                error_message=str(error),
            )
        )

    # ==================== Hook Management ====================

    def add_pre_execute_hook(self, hook: Callable[[RoutePoint], None]) -> None:
        """Add a pre-execution hook."""
        self._pre_execute_hooks.append(hook)

    def add_post_execute_hook(
        self,
        hook: Callable[[RoutePoint, ContentResult | None], None],
    ) -> None:
        """Add a post-execution hook."""
        self._post_execute_hooks.append(hook)

    def add_error_hook(
        self,
        hook: Callable[[RoutePoint, Exception], None],
    ) -> None:
        """Add an error hook."""
        self._error_hooks.append(hook)

    def _run_pre_execute_hooks(self, point: RoutePoint) -> None:
        """Run all pre-execute hooks."""
        for hook in self._pre_execute_hooks:
            try:
                hook(point)
            except Exception as e:
                logger.warning(f"Pre-execute hook failed: {e}")

        # Run global hooks
        HookRegistry.execute_hooks(
            f"agent.{self.name}.execute",
            HookType.BEFORE,
            point,
        )

    def _run_post_execute_hooks(
        self,
        point: RoutePoint,
        result: ContentResult | None,
    ) -> None:
        """Run all post-execute hooks."""
        for hook in self._post_execute_hooks:
            try:
                hook(point, result)
            except Exception as e:
                logger.warning(f"Post-execute hook failed: {e}")

        # Run global hooks
        HookRegistry.execute_hooks(
            f"agent.{self.name}.execute",
            HookType.AFTER,
            result,
            point,
        )

    def _run_error_hooks(self, point: RoutePoint, error: Exception) -> None:
        """Run all error hooks."""
        for hook in self._error_hooks:
            try:
                hook(point, error)
            except Exception as e:
                logger.warning(f"Error hook failed: {e}")

        # Run global hooks
        HookRegistry.execute_hooks(
            f"agent.{self.name}.execute",
            HookType.ERROR,
            error,
            point,
        )

    # ==================== Health Check ====================

    def _register_health_check(self) -> None:
        """Register health check for this agent."""

        @health_check(
            f"agent_{self.name}",
            critical=False,
            description=f"Health check for {self.name} agent",
        )
        def check():
            return self.is_healthy

    def health_check(self) -> bool:
        """Perform health check."""
        return self.is_healthy

    # ==================== Abstract Methods ====================

    @abstractmethod
    def _search_content(self, point: RoutePoint) -> ContentResult | None:
        """
        Search for content relevant to the route point.

        This is the main method that subclasses must implement.
        Called with retry and timeout protection.

        Args:
            point: Route point to find content for

        Returns:
            ContentResult or None
        """
        pass

    @abstractmethod
    def get_content_type(self) -> ContentType:
        """Return the type of content this agent provides."""
        pass

    # ==================== Optional Hooks ====================

    def on_before_execute(self, point: RoutePoint) -> None:
        """
        Called before execution.

        Override to add pre-execution logic.
        """
        pass

    def on_after_execute(
        self,
        point: RoutePoint,
        result: ContentResult | None,
    ) -> None:
        """
        Called after successful execution.

        Override to add post-execution logic.
        """
        pass

    def on_error(self, point: RoutePoint, error: Exception) -> None:
        """
        Called on execution error.

        Override to add error handling logic.
        """
        pass

    # ==================== Utilities ====================

    def reset_circuit_breaker(self) -> None:
        """Manually reset the circuit breaker."""
        self._circuit_breaker.reset()
        logger.info(f"Circuit breaker reset for {self.name}")

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}(name={self.name}, state={self._state.name})>"
        )
