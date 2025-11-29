"""
Observability Framework
=======================

Production-grade observability for monitoring, tracing, and metrics.

Components:
- Metrics: Counters, gauges, histograms
- Tracing: Distributed tracing with span management
- Health Checks: Service health monitoring
- Structured Logging: Contextual logging

Academic Reference:
    - Google SRE Book, "Monitoring Distributed Systems"
    - OpenTelemetry Specification
    - Prometheus Best Practices

Example:
    # Metrics
    request_counter = Counter("http_requests_total", labels=["method", "path"])
    request_counter.inc(method="GET", path="/api/users")

    # Tracing
    with tracer.span("process_route") as span:
        span.set_attribute("route_id", route.id)
        result = process(route)

    # Health checks
    @health_check("database")
    def check_database():
        return db.ping()
"""

from src.core.observability.health import (
    HealthCheck,
    HealthRegistry,
    HealthStatus,
    get_health_status,
    health_check,
)
from src.core.observability.metrics import (
    Counter,
    Gauge,
    Histogram,
    MetricsRegistry,
    Timer,
    counted,
    timed,
)
from src.core.observability.tracing import (
    Span,
    SpanContext,
    Tracer,
    get_tracer,
    trace,
)

__all__ = [
    # Metrics
    "Counter",
    "Gauge",
    "Histogram",
    "Timer",
    "MetricsRegistry",
    "timed",
    "counted",
    # Tracing
    "Tracer",
    "Span",
    "SpanContext",
    "trace",
    "get_tracer",
    # Health
    "HealthCheck",
    "HealthStatus",
    "HealthRegistry",
    "health_check",
    "get_health_status",
]
