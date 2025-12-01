"""
MIT-Level Interactive Research Dashboard
========================================

Publication-quality, interactive visualization dashboard for
Multi-Agent Tour Guide System analysis and monitoring.

Features:
- Real-time system monitoring
- Interactive sensitivity analysis
- Pareto frontier exploration
- Statistical comparison tools
- Monte Carlo simulation controls
- Agent performance analytics

Author: Multi-Agent Tour Guide Research Team
Version: 1.0.0
Date: November 2025

Usage:
    # From command line
    python run_dashboard.py

    # Or programmatically
    from src.dashboard import run_dashboard
    run_dashboard()
"""

__version__ = "1.0.0"


# Lazy imports to avoid import errors when dependencies not installed
def __getattr__(name):
    """Lazy import of dashboard components."""
    if name in ("create_app", "run_dashboard"):
        from .app import create_app, run_dashboard

        return {"create_app": create_app, "run_dashboard": run_dashboard}[name]

    elif name == "DashboardDataManager":
        from .data_manager import DashboardDataManager

        return DashboardDataManager

    elif name in (
        "AgentPerformancePanel",
        "MonteCarloPanel",
        "ParetoFrontierPanel",
        "SensitivityPanel",
        "StatisticalComparisonPanel",
        "SystemMonitorPanel",
    ):
        from . import components

        return getattr(components, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "create_app",
    "run_dashboard",
    "DashboardDataManager",
    "SystemMonitorPanel",
    "SensitivityPanel",
    "ParetoFrontierPanel",
    "StatisticalComparisonPanel",
    "MonteCarloPanel",
    "AgentPerformancePanel",
]
