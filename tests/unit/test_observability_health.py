"""
Unit tests for Observability Health module.

Tests cover:
- HealthStatus enum
- HealthCheckResult dataclass
- HealthCheck dataclass
- HealthRegistry for managing checks
- health_check decorator
- AggregateHealth

MIT Level Testing - 85%+ Coverage Target
"""

from datetime import datetime
from unittest.mock import Mock

from src.core.observability.health import (
    AggregateHealth,
    HealthCheck,
    HealthCheckResult,
    HealthRegistry,
    HealthStatus,
    create_liveness_probe,
    create_readiness_probe,
    get_health_status,
    health_check,
)


class TestHealthStatus:
    """Tests for HealthStatus enum."""

    def test_status_values(self):
        """Test all status values exist."""
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.UNHEALTHY.value == "unhealthy"
        assert HealthStatus.UNKNOWN.value == "unknown"

    def test_status_uniqueness(self):
        """Test status values are unique."""
        values = [s.value for s in HealthStatus]
        assert len(values) == len(set(values))


class TestHealthCheckResult:
    """Tests for HealthCheckResult dataclass."""

    def test_minimal_result(self):
        """Test creating result with minimal fields."""
        result = HealthCheckResult(
            name="test",
            status=HealthStatus.HEALTHY,
        )
        assert result.name == "test"
        assert result.status == HealthStatus.HEALTHY
        assert result.message is None

    def test_full_result(self):
        """Test creating result with all fields."""
        result = HealthCheckResult(
            name="db_check",
            status=HealthStatus.UNHEALTHY,
            message="Connection refused",
            duration_ms=150.5,
            details={"host": "localhost"},
            error="ConnectionError",
        )
        assert result.name == "db_check"
        assert result.status == HealthStatus.UNHEALTHY
        assert result.message == "Connection refused"
        assert result.duration_ms == 150.5
        assert result.details["host"] == "localhost"
        assert result.error == "ConnectionError"

    def test_timestamp_auto_set(self):
        """Test timestamp is automatically set."""
        before = datetime.now()
        result = HealthCheckResult(name="test", status=HealthStatus.HEALTHY)
        after = datetime.now()
        assert before <= result.timestamp <= after


class TestHealthCheck:
    """Tests for HealthCheck dataclass."""

    def test_minimal_check(self):
        """Test creating check with minimal fields."""
        check_fn = Mock(return_value=True)
        check = HealthCheck(
            name="test_check",
            check_fn=check_fn,
        )
        assert check.name == "test_check"
        assert check.check_fn == check_fn
        assert check.critical is True  # Default

    def test_full_check(self):
        """Test creating check with all fields."""
        check_fn = Mock(return_value=True)
        check = HealthCheck(
            name="api_check",
            check_fn=check_fn,
            critical=False,
            timeout=10.0,
            interval=60.0,
            description="Check API health",
        )
        assert check.name == "api_check"
        assert check.critical is False
        assert check.timeout == 10.0
        assert check.interval == 60.0
        assert check.description == "Check API health"

    def test_defaults(self):
        """Test default values."""
        check = HealthCheck(name="test", check_fn=Mock())
        assert check.critical is True
        assert check.timeout == 5.0
        assert check.interval == 30.0
        assert check.description == ""
        assert check.last_result is None


class TestHealthRegistry:
    """Tests for HealthRegistry class methods."""

    def setup_method(self):
        """Clear registry before each test."""
        HealthRegistry.clear()

    def test_register_check(self):
        """Test registering a health check."""
        check_fn = Mock(return_value=True)
        HealthRegistry.register("test_check", check_fn)
        assert "test_check" in HealthRegistry._checks

    def test_register_with_options(self):
        """Test registering with options."""
        check_fn = Mock(return_value=True)
        HealthRegistry.register(
            "api_check",
            check_fn,
            critical=False,
            timeout=10.0,
            description="API health",
        )

        check = HealthRegistry._checks["api_check"]
        assert check.critical is False
        assert check.timeout == 10.0
        assert check.description == "API health"

    def test_run_check_success(self):
        """Test running a successful check."""
        check_fn = Mock(return_value=True)
        HealthRegistry.register("success_check", check_fn)

        result = HealthRegistry.run_check("success_check")
        assert result.status == HealthStatus.HEALTHY
        check_fn.assert_called_once()

    def test_run_check_failure(self):
        """Test running a failing check."""
        check_fn = Mock(return_value=False)
        HealthRegistry.register("fail_check", check_fn)

        result = HealthRegistry.run_check("fail_check")
        assert result.status == HealthStatus.UNHEALTHY

    def test_run_check_exception(self):
        """Test running check that raises exception."""
        check_fn = Mock(side_effect=Exception("Check error"))
        HealthRegistry.register("error_check", check_fn)

        result = HealthRegistry.run_check("error_check")
        assert result.status == HealthStatus.UNHEALTHY
        assert result.error is not None

    def test_run_all_checks(self):
        """Test running all checks."""
        HealthRegistry.register("check1", Mock(return_value=True))
        HealthRegistry.register("check2", Mock(return_value=True))

        results = HealthRegistry.run_all_checks()
        assert len(results) == 2
        assert all(r.status == HealthStatus.HEALTHY for r in results.values())

    def test_get_aggregate_status_healthy(self):
        """Test aggregate status when all healthy."""
        HealthRegistry.register("check1", Mock(return_value=True))
        HealthRegistry.register("check2", Mock(return_value=True))
        HealthRegistry.run_all_checks()

        status = HealthRegistry.get_aggregate_status()
        assert status.status == HealthStatus.HEALTHY

    def test_unregister(self):
        """Test unregistering a check."""
        HealthRegistry.register("to_remove", Mock())
        HealthRegistry.unregister("to_remove")
        assert "to_remove" not in HealthRegistry._checks

    def test_list_checks(self):
        """Test listing all checks."""
        HealthRegistry.register("check1", Mock())
        HealthRegistry.register("check2", Mock())

        checks = HealthRegistry.list_checks()
        names = [c["name"] for c in checks]
        assert "check1" in names
        assert "check2" in names

    def test_clear(self):
        """Test clearing all checks."""
        HealthRegistry.register("check1", Mock())
        HealthRegistry.clear()
        assert len(HealthRegistry._checks) == 0


class TestAggregateHealth:
    """Tests for AggregateHealth dataclass."""

    def test_is_healthy(self):
        """Test is_healthy property."""
        healthy = AggregateHealth(
            status=HealthStatus.HEALTHY,
            checks=[],
        )
        assert healthy.is_healthy is True

    def test_is_degraded(self):
        """Test is_degraded property."""
        degraded = AggregateHealth(
            status=HealthStatus.DEGRADED,
            checks=[],
        )
        assert degraded.is_degraded is True

    def test_is_unhealthy(self):
        """Test is_unhealthy property."""
        unhealthy = AggregateHealth(
            status=HealthStatus.UNHEALTHY,
            checks=[],
        )
        assert unhealthy.is_unhealthy is True

    def test_from_results_all_healthy(self):
        """Test from_results with all healthy."""
        results = {
            "c1": HealthCheckResult(name="c1", status=HealthStatus.HEALTHY),
            "c2": HealthCheckResult(name="c2", status=HealthStatus.HEALTHY),
        }
        aggregate = AggregateHealth.from_results(results)
        assert aggregate.status == HealthStatus.HEALTHY

    def test_to_dict(self):
        """Test to_dict method."""
        aggregate = AggregateHealth(
            status=HealthStatus.HEALTHY,
            checks={
                "c1": HealthCheckResult(name="c1", status=HealthStatus.HEALTHY),
            },
        )
        d = aggregate.to_dict()
        assert "status" in d
        assert "checks" in d


class TestHealthCheckDecorator:
    """Tests for health_check decorator."""

    def setup_method(self):
        """Clear registry before each test."""
        HealthRegistry.clear()

    def test_decorator_registers_check(self):
        """Test decorator registers the check."""

        @health_check("decorated_check")
        def my_check():
            return True

        assert "decorated_check" in HealthRegistry._checks

    def test_decorator_with_options(self):
        """Test decorator with options."""

        @health_check("custom_check", critical=False, timeout=15.0)
        def my_check():
            return True

        check = HealthRegistry._checks["custom_check"]
        assert check.critical is False
        assert check.timeout == 15.0

    def test_decorator_preserves_function(self):
        """Test decorated function still works."""

        @health_check("test")
        def my_check():
            """Check docstring."""
            return True

        result = my_check()
        assert result is True


class TestProbes:
    """Tests for liveness and readiness probes."""

    def setup_method(self):
        """Clear registry before each test."""
        HealthRegistry.clear()

    def test_liveness_probe(self):
        """Test liveness probe returns True."""
        probe = create_liveness_probe()
        assert probe() is True

    def test_readiness_probe_all_healthy(self):
        """Test readiness probe with healthy checks."""
        HealthRegistry.register("check1", Mock(return_value=True))
        probe = create_readiness_probe()
        assert probe() is True

    def test_readiness_probe_with_unhealthy(self):
        """Test readiness probe with unhealthy checks."""
        HealthRegistry.register("failing", Mock(return_value=False), critical=True)
        probe = create_readiness_probe()
        assert probe() is False


class TestGetHealthStatus:
    """Tests for get_health_status function."""

    def setup_method(self):
        """Clear registry before each test."""
        HealthRegistry.clear()

    def test_get_health_status(self):
        """Test get_health_status function."""
        HealthRegistry.register("check1", Mock(return_value=True))
        status = get_health_status()
        assert isinstance(status, AggregateHealth)
