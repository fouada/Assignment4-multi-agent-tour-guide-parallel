"""
Hook System
===========

Aspect-Oriented Programming (AOP) style hooks for extending
behavior without modifying core code.

Design Patterns:
    - Decorator Pattern: Wrapping functions with hooks
    - Chain of Responsibility: Sequential hook execution
    - Interceptor Pattern: Pre/post processing

Academic Reference:
    - Kiczales et al., "Aspect-Oriented Programming" (ECOOP 1997)
    - Gamma et al., "Design Patterns" (Decorator, p. 175)

Example:
    # Define hookable function
    @hookable("agent.execute")
    def execute_agent(point):
        return agent.run(point)

    # Add pre-hook
    @before_hook("agent.execute")
    def log_start(point):
        logger.info(f"Starting agent for {point}")

    # Add post-hook
    @after_hook("agent.execute")
    def log_result(result, point):
        logger.info(f"Agent returned: {result}")

    # Add around hook (wraps entire execution)
    @around_hook("agent.execute")
    def with_timing(func, *args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"Took {time.time() - start}s")
        return result
"""

from __future__ import annotations

import logging
import threading
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import IntEnum
from functools import wraps
from typing import (
    Any,
    TypeVar,
)
from uuid import uuid4

logger = logging.getLogger(__name__)

T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])


class HookType(IntEnum):
    """Types of hooks that can be registered."""

    BEFORE = 1  # Runs before the function
    AFTER = 2  # Runs after the function (receives result)
    AROUND = 3  # Wraps the function (must call it)
    ERROR = 4  # Runs on exception
    FINALLY = 5  # Runs always (like try/finally)


class HookPriority(IntEnum):
    """Hook execution priority. Lower values execute first."""

    SYSTEM = 0  # System-level hooks (security, auth)
    HIGH = 100  # High priority (validation)
    NORMAL = 500  # Default priority
    LOW = 900  # Low priority (logging, metrics)


@dataclass
class Hook:
    """
    Represents a registered hook.

    Attributes:
        name: Hook point name (e.g., "agent.execute")
        hook_type: Type of hook (BEFORE, AFTER, etc.)
        handler: The hook function
        priority: Execution priority
        enabled: Whether hook is active
    """

    name: str
    hook_type: HookType
    handler: Callable
    priority: HookPriority = HookPriority.NORMAL
    enabled: bool = True
    hook_id: str = field(default_factory=lambda: str(uuid4())[:8])
    description: str = ""

    def __call__(self, *args, **kwargs) -> Any:
        """Execute the hook handler."""
        if self.enabled:
            return self.handler(*args, **kwargs)
        return None


class HookRegistry:
    """
    Central registry for all hooks in the system.

    Provides:
    - Hook registration via decorators or explicit calls
    - Priority-ordered execution
    - Thread-safe operations
    - Hook enable/disable

    Example:
        # Register hooks
        HookRegistry.register(
            "agent.execute",
            HookType.BEFORE,
            my_before_handler,
            priority=HookPriority.HIGH,
        )

        # Get and execute hooks
        for hook in HookRegistry.get_hooks("agent.execute", HookType.BEFORE):
            hook(*args, **kwargs)
    """

    # Class-level storage
    _hooks: dict[str, dict[HookType, list[Hook]]] = defaultdict(
        lambda: defaultdict(list)
    )
    _lock = threading.RLock()

    # Metrics
    _execution_counts: dict[str, int] = defaultdict(int)

    @classmethod
    def register(
        cls,
        name: str,
        hook_type: HookType,
        handler: Callable,
        *,
        priority: HookPriority = HookPriority.NORMAL,
        description: str = "",
    ) -> str:
        """
        Register a hook.

        Args:
            name: Hook point name (e.g., "agent.execute")
            hook_type: Type of hook
            handler: Hook function
            priority: Execution priority
            description: Human-readable description

        Returns:
            Hook ID for later removal
        """
        hook = Hook(
            name=name,
            hook_type=hook_type,
            handler=handler,
            priority=priority,
            description=description,
        )

        with cls._lock:
            hooks = cls._hooks[name][hook_type]
            hooks.append(hook)
            # Sort by priority
            hooks.sort(key=lambda h: h.priority)

        logger.debug(
            f"Registered {hook_type.name} hook for '{name}' (priority={priority.name})"
        )

        return hook.hook_id

    @classmethod
    def unregister(cls, hook_id: str) -> bool:
        """Remove a hook by ID."""
        with cls._lock:
            for _name, type_hooks in cls._hooks.items():
                for _hook_type, hooks in type_hooks.items():
                    for hook in hooks:
                        if hook.hook_id == hook_id:
                            hooks.remove(hook)
                            return True
        return False

    @classmethod
    def get_hooks(
        cls,
        name: str,
        hook_type: HookType | None = None,
    ) -> list[Hook]:
        """
        Get hooks for a hook point.

        Args:
            name: Hook point name
            hook_type: Filter by type (or get all if None)

        Returns:
            List of hooks sorted by priority
        """
        with cls._lock:
            if hook_type:
                return list(cls._hooks[name][hook_type])

            # Get all hooks for this point
            all_hooks = []
            for type_hooks in cls._hooks[name].values():
                all_hooks.extend(type_hooks)
            return sorted(all_hooks, key=lambda h: h.priority)

    @classmethod
    def execute_hooks(
        cls,
        name: str,
        hook_type: HookType,
        *args,
        **kwargs,
    ) -> list[Any]:
        """
        Execute all hooks of a given type for a hook point.

        Args:
            name: Hook point name
            hook_type: Type of hooks to execute
            *args, **kwargs: Arguments to pass to hooks

        Returns:
            List of hook return values
        """
        results = []
        hooks = cls.get_hooks(name, hook_type)

        for hook in hooks:
            if hook.enabled:
                try:
                    result = hook.handler(*args, **kwargs)
                    results.append(result)
                    cls._execution_counts[hook.hook_id] += 1
                except Exception as e:
                    logger.error(f"Hook {hook.hook_id} failed: {e}")
                    raise

        return results

    @classmethod
    def set_enabled(cls, hook_id: str, enabled: bool) -> bool:
        """Enable or disable a hook."""
        with cls._lock:
            for _name, type_hooks in cls._hooks.items():
                for hooks in type_hooks.values():
                    for hook in hooks:
                        if hook.hook_id == hook_id:
                            hook.enabled = enabled
                            return True
        return False

    @classmethod
    def list_hook_points(cls) -> list[str]:
        """List all registered hook points."""
        with cls._lock:
            return list(cls._hooks.keys())

    @classmethod
    def list_hooks(cls, name: str | None = None) -> list[dict[str, Any]]:
        """List all hooks, optionally filtered by hook point."""
        with cls._lock:
            result = []
            for hook_name, type_hooks in cls._hooks.items():
                if name and hook_name != name:
                    continue
                for _hook_type, hooks in type_hooks.items():
                    for hook in hooks:
                        result.append(
                            {
                                "id": hook.hook_id,
                                "name": hook.name,
                                "type": hook.hook_type.name,
                                "priority": hook.priority.name,
                                "enabled": hook.enabled,
                                "description": hook.description,
                                "handler": hook.handler.__name__,
                            }
                        )
            return result

    @classmethod
    def clear(cls) -> None:
        """Clear all hooks (for testing)."""
        with cls._lock:
            cls._hooks.clear()
            cls._execution_counts.clear()

    @classmethod
    def get_stats(cls) -> dict[str, Any]:
        """Get hook system statistics."""
        with cls._lock:
            total_hooks = sum(
                len(hooks)
                for type_hooks in cls._hooks.values()
                for hooks in type_hooks.values()
            )
            return {
                "hook_points": len(cls._hooks),
                "total_hooks": total_hooks,
                "execution_counts": dict(cls._execution_counts),
            }


# ============== Decorator-Based Hook Registration ==============


def hookable(name: str) -> Callable[[F], F]:
    """
    Decorator to make a function hookable.

    Wraps the function to execute registered hooks at appropriate points:
    - BEFORE hooks: Run before the function
    - AROUND hooks: Wrap the function (must call it)
    - AFTER hooks: Run after with the result
    - ERROR hooks: Run on exception
    - FINALLY hooks: Always run

    Args:
        name: Hook point name

    Returns:
        Decorator function

    Example:
        @hookable("agent.execute")
        def execute_agent(point):
            return agent.run(point)
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = None
            error = None

            try:
                # Execute BEFORE hooks
                HookRegistry.execute_hooks(name, HookType.BEFORE, *args, **kwargs)

                # Execute AROUND hooks or the function itself
                around_hooks = HookRegistry.get_hooks(name, HookType.AROUND)

                if around_hooks:
                    # Chain around hooks
                    def chain_around(index: int):
                        if index >= len(around_hooks):
                            return func(*args, **kwargs)

                        hook = around_hooks[index]
                        if hook.enabled:
                            return hook.handler(
                                lambda: chain_around(index + 1),
                                *args,
                                **kwargs,
                            )
                        return chain_around(index + 1)

                    result = chain_around(0)
                else:
                    result = func(*args, **kwargs)

                # Execute AFTER hooks
                after_results = HookRegistry.execute_hooks(
                    name, HookType.AFTER, result, *args, **kwargs
                )

                # Allow after hooks to modify result
                for after_result in after_results:
                    if after_result is not None:
                        result = after_result

                return result

            except Exception as e:
                error = e
                # Execute ERROR hooks
                try:
                    HookRegistry.execute_hooks(name, HookType.ERROR, e, *args, **kwargs)
                except Exception:
                    pass
                raise

            finally:
                # Execute FINALLY hooks
                try:
                    HookRegistry.execute_hooks(
                        name, HookType.FINALLY, result, error, *args, **kwargs
                    )
                except Exception:
                    pass

        return wrapper  # type: ignore

    return decorator


def before_hook(
    name: str,
    *,
    priority: HookPriority = HookPriority.NORMAL,
    description: str = "",
) -> Callable[[Callable], Callable]:
    """
    Decorator to register a BEFORE hook.

    The handler receives the same arguments as the hooked function.

    Example:
        @before_hook("agent.execute")
        def validate_point(point):
            if not point.is_valid():
                raise ValueError("Invalid point")
    """

    def decorator(handler: Callable) -> Callable:
        HookRegistry.register(
            name,
            HookType.BEFORE,
            handler,
            priority=priority,
            description=description or handler.__doc__ or "",
        )
        return handler

    return decorator


def after_hook(
    name: str,
    *,
    priority: HookPriority = HookPriority.NORMAL,
    description: str = "",
) -> Callable[[Callable], Callable]:
    """
    Decorator to register an AFTER hook.

    The handler receives (result, *original_args, **original_kwargs).
    Can return a modified result.

    Example:
        @after_hook("agent.execute")
        def log_result(result, point):
            logger.info(f"Agent returned: {result}")
            return result  # Can modify
    """

    def decorator(handler: Callable) -> Callable:
        HookRegistry.register(
            name,
            HookType.AFTER,
            handler,
            priority=priority,
            description=description or handler.__doc__ or "",
        )
        return handler

    return decorator


def around_hook(
    name: str,
    *,
    priority: HookPriority = HookPriority.NORMAL,
    description: str = "",
) -> Callable[[Callable], Callable]:
    """
    Decorator to register an AROUND hook.

    The handler receives (proceed_fn, *args, **kwargs) and MUST call proceed_fn()
    to continue execution.

    Example:
        @around_hook("agent.execute")
        def with_retry(proceed, *args, **kwargs):
            for attempt in range(3):
                try:
                    return proceed()
                except Exception:
                    if attempt == 2:
                        raise
    """

    def decorator(handler: Callable) -> Callable:
        HookRegistry.register(
            name,
            HookType.AROUND,
            handler,
            priority=priority,
            description=description or handler.__doc__ or "",
        )
        return handler

    return decorator


def error_hook(
    name: str,
    *,
    priority: HookPriority = HookPriority.NORMAL,
    description: str = "",
) -> Callable[[Callable], Callable]:
    """
    Decorator to register an ERROR hook.

    The handler receives (exception, *original_args, **original_kwargs).

    Example:
        @error_hook("agent.execute")
        def log_error(error, point):
            logger.error(f"Agent failed for {point}: {error}")
    """

    def decorator(handler: Callable) -> Callable:
        HookRegistry.register(
            name,
            HookType.ERROR,
            handler,
            priority=priority,
            description=description or handler.__doc__ or "",
        )
        return handler

    return decorator


def finally_hook(
    name: str,
    *,
    priority: HookPriority = HookPriority.NORMAL,
    description: str = "",
) -> Callable[[Callable], Callable]:
    """
    Decorator to register a FINALLY hook.

    The handler receives (result, error, *original_args, **original_kwargs).
    Always runs, even on error.

    Example:
        @finally_hook("agent.execute")
        def cleanup(result, error, point):
            logger.info(f"Agent finished, error={error is not None}")
    """

    def decorator(handler: Callable) -> Callable:
        HookRegistry.register(
            name,
            HookType.FINALLY,
            handler,
            priority=priority,
            description=description or handler.__doc__ or "",
        )
        return handler

    return decorator
