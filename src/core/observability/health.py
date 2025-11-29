"""
Health Check System
===================

Comprehensive health checking for services and dependencies.

Features:
- Component health checks
- Dependency health (databases, APIs)
- Liveness and readiness probes
- Health aggregation

Example:
    @health_check("database", critical=True)
    def check_database():
        return db.ping()

    # Get overall health
    status = get_health_status()
    if not status.is_healthy:
        alert_ops_team()
"""

from __future__ import annotations

import logging
import threading
import time
import traceback
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"  # Some non-critical checks failing
    UNHEALTHY = "unhealthy"  # Critical checks failing
    UNKNOWN = "unknown"  # Not yet checked


@dataclass
class HealthCheckResult:
    """Result of a single health check."""
    name: str
    status: HealthStatus
    message: str | None = None
    duration_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    details: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


@dataclass
class HealthCheck:
    """
    A registered health check.

    Attributes:
        name: Check identifier
        check_fn: Function that performs the check
        critical: If True, failure makes system unhealthy
        timeout: Check timeout in seconds
        interval: Minimum seconds between checks
        description: Human-readable description
    """
    name: str
    check_fn: Callable[[], bool]
    critical: bool = True
    timeout: float = 5.0
    interval: float = 30.0
    description: str = ""

    # State
    last_result: HealthCheckResult | None = None
    last_check_time: float = 0.0
    consecutive_failures: int = 0


class HealthRegistry:
    """
    Central registry for health checks.

    Provides:
    - Health check registration
    - Parallel check execution
    - Result caching
    - Status aggregation
    """

    _checks: dict[str, HealthCheck] = {}
    _lock = threading.RLock()

    @classmethod
    def register(
        cls,
        name: str,
        check_fn: Callable[[], bool],
        *,
        critical: bool = True,
        timeout: float = 5.0,
        interval: float = 30.0,
        description: str = "",
    ) -> HealthCheck:
        """Register a health check."""
        check = HealthCheck(
            name=name,
            check_fn=check_fn,
            critical=critical,
            timeout=timeout,
            interval=interval,
            description=description,
        )

        with cls._lock:
            cls._checks[name] = check

        logger.debug(f"Registered health check: {name}")
        return check

    @classmethod
    def unregister(cls, name: str) -> None:
        """Remove a health check."""
        with cls._lock:
            cls._checks.pop(name, None)

    @classmethod
    def run_check(
        cls,
        name: str,
        force: bool = False,
    ) -> HealthCheckResult:
        """
        Run a specific health check.

        Args:
            name: Check name
            force: Run even if within interval

        Returns:
            Health check result
        """
        with cls._lock:
            check = cls._checks.get(name)
            if not check:
                return HealthCheckResult(
                    name=name,
                    status=HealthStatus.UNKNOWN,
                    message="Check not found",
                )

        # Check if we should skip (within interval)
        now = time.time()
        if not force and check.last_result:
            if now - check.last_check_time < check.interval:
                return check.last_result

        # Run the check
        start_time = time.time()
        try:
            result = check.check_fn()
            duration_ms = (time.time() - start_time) * 1000

            if result:
                status = HealthStatus.HEALTHY
                message = "OK"
                check.consecutive_failures = 0
            else:
                status = HealthStatus.UNHEALTHY
                message = "Check returned False"
                check.consecutive_failures += 1

            health_result = HealthCheckResult(
                name=name,
                status=status,
                message=message,
                duration_ms=duration_ms,
                details={
                    "critical": check.critical,
                    "consecutive_failures": check.consecutive_failures,
                },
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            check.consecutive_failures += 1

            health_result = HealthCheckResult(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=str(e),
                duration_ms=duration_ms,
                error=traceback.format_exc(),
                details={
                    "critical": check.critical,
                    "consecutive_failures": check.consecutive_failures,
                },
            )

        # Update check state
        check.last_result = health_result
        check.last_check_time = now

        return health_result

    @classmethod
    def run_all_checks(
        cls,
        force: bool = False,
    ) -> dict[str, HealthCheckResult]:
        """Run all registered health checks."""
        results = {}

        with cls._lock:
            check_names = list(cls._checks.keys())

        for name in check_names:
            results[name] = cls.run_check(name, force=force)

        return results

    @classmethod
    def get_aggregate_status(cls) -> AggregateHealth:
        """Get aggregated health status."""
        results = cls.run_all_checks()
        return AggregateHealth.from_results(results)

    @classmethod
    def list_checks(cls) -> list[dict[str, Any]]:
        """List all registered checks."""
        with cls._lock:
            return [
                {
                    "name": check.name,
                    "critical": check.critical,
                    "description": check.description,
                    "last_status": check.last_result.status.value if check.last_result else "unknown",
                }
                for check in cls._checks.values()
            ]

    @classmethod
    def clear(cls) -> None:
        """Clear all checks (for testing)."""
        with cls._lock:
            cls._checks.clear()


@dataclass
class AggregateHealth:
    """Aggregated health status across all checks."""
    status: HealthStatus
    checks: dict[str, HealthCheckResult]
    healthy_count: int = 0
    unhealthy_count: int = 0
    degraded_count: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def is_healthy(self) -> bool:
        return self.status == HealthStatus.HEALTHY

    @property
    def is_degraded(self) -> bool:
        return self.status == HealthStatus.DEGRADED

    @property
    def is_unhealthy(self) -> bool:
        return self.status == HealthStatus.UNHEALTHY

    @classmethod
    def from_results(
        cls,
        results: dict[str, HealthCheckResult],
    ) -> AggregateHealth:
        """Create aggregate from individual results."""
        healthy = 0
        unhealthy = 0
        degraded = 0
        has_critical_failure = False

        for _name, result in results.items():
            if result.status == HealthStatus.HEALTHY:
                healthy += 1
            elif result.status == HealthStatus.UNHEALTHY:
                unhealthy += 1
                # Check if critical
                if result.details.get("critical", True):
                    has_critical_failure = True
            elif result.status == HealthStatus.DEGRADED:
                degraded += 1

        # Determine overall status
        if has_critical_failure:
            status = HealthStatus.UNHEALTHY
        elif unhealthy > 0 or degraded > 0:
            status = HealthStatus.DEGRADED
        elif healthy > 0:
            status = HealthStatus.HEALTHY
        else:
            status = HealthStatus.UNKNOWN

        return cls(
            status=status,
            checks=results,
            healthy_count=healthy,
            unhealthy_count=unhealthy,
            degraded_count=degraded,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "summary": {
                "healthy": self.healthy_count,
                "unhealthy": self.unhealthy_count,
                "degraded": self.degraded_count,
            },
            "checks": {
                name: {
                    "status": result.status.value,
                    "message": result.message,
                    "duration_ms": result.duration_ms,
                }
                for name, result in self.checks.items()
            },
        }


# ============== Decorator ==============

def health_check(
    name: str,
    *,
    critical: bool = True,
    timeout: float = 5.0,
    interval: float = 30.0,
    description: str = "",
) -> Callable:
    """
    Decorator to register a function as a health check.

    The function should return True if healthy, False otherwise.
    Any exception is treated as unhealthy.

    Example:
        @health_check("redis", critical=True)
        def check_redis():
            return redis.ping()

        @health_check("external_api", critical=False)
        def check_api():
            response = requests.get(api_url, timeout=3)
            return response.status_code == 200
    """
    def decorator(func: Callable[[], bool]) -> Callable[[], bool]:
        HealthRegistry.register(
            name=name,
            check_fn=func,
            critical=critical,
            timeout=timeout,
            interval=interval,
            description=description or func.__doc__ or "",
        )
        return func

    return decorator


def get_health_status() -> AggregateHealth:
    """Get the current health status of all checks."""
    return HealthRegistry.get_aggregate_status()


# ============== Standard Health Checks ==============

def create_liveness_probe() -> Callable[[], bool]:
    """
    Create a liveness probe check.

    A liveness probe checks if the application is running.
    If it fails, the container should be restarted.
    """
    def check() -> bool:
        # Basic check - can we execute Python?
        return True

    return check


def create_readiness_probe(
    checks: list[str] | None = None,
) -> Callable[[], bool]:
    """
    Create a readiness probe check.

    A readiness probe checks if the application is ready to serve traffic.
    If it fails, the pod should be removed from load balancer.

    Args:
        checks: List of health check names that must pass
    """
    def check() -> bool:
        results = HealthRegistry.run_all_checks()

        if checks:
            # Only check specified checks
            for name in checks:
                if name in results and results[name].status != HealthStatus.HEALTHY:
                    return False
            return True
        else:
            # All critical checks must pass
            for name, result in results.items():
                if result.details.get("critical") and result.status != HealthStatus.HEALTHY:
                    return False
            return True

    return check

