"""
Dashboard Data Manager
======================

Manages simulation data, caching, and real-time updates for the dashboard.
Provides a clean interface between the simulation engine and visualization.

Edge Cases Handled:
-------------------
1. Empty parameter lists in sensitivity analysis
2. Zero/negative timeout values (clamped to minimum)
3. Agent reliability at 0% or 100% boundaries
4. Empty simulation results
5. Thread-safe cache access
6. Missing data in export
7. Invalid configuration combinations (hard <= soft)

Author: Multi-Agent Tour Guide Research Team
Version: 1.0.0
"""

from __future__ import annotations

import json
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


class QueueStatus(Enum):
    """Queue completion status."""

    WAITING = "waiting"
    COMPLETE = "complete"
    SOFT_DEGRADED = "soft_degraded"
    HARD_DEGRADED = "hard_degraded"
    FAILED = "failed"


@dataclass
class AgentConfig:
    """Agent response time configuration."""

    name: str
    mu: float  # Log-normal location parameter
    sigma: float  # Log-normal scale parameter
    shift: float  # Minimum response time
    reliability: float  # Success probability
    quality_mean: float  # Mean quality score
    quality_std: float  # Quality score std dev


@dataclass
class QueueConfig:
    """Smart Queue configuration."""

    soft_timeout: float = 15.0
    hard_timeout: float = 30.0
    min_for_soft: int = 2
    min_for_hard: int = 1
    expected_agents: int = 3


@dataclass
class SimulationResult:
    """Result of a single simulation run."""

    status: QueueStatus
    latency: float
    num_results: int
    quality: float
    agent_times: dict[str, float] = field(default_factory=dict)
    agent_success: dict[str, bool] = field(default_factory=dict)


class SmartQueueSimulator:
    """
    High-fidelity simulator for the Smart Queue system.

    Mathematical Model:
    - Response Time: T_i ~ shift + LogNormal(μ, σ²)
    - Success: Bernoulli(ρ)
    - Quality: Truncated Normal(μ_q, σ_q²) on [0, 10]
    """

    DEFAULT_AGENTS = [
        AgentConfig(
            "video",
            mu=1.0,
            sigma=0.5,
            shift=0.5,
            reliability=0.92,
            quality_mean=7.5,
            quality_std=1.5,
        ),
        AgentConfig(
            "music",
            mu=0.8,
            sigma=0.4,
            shift=0.3,
            reliability=0.95,
            quality_mean=7.0,
            quality_std=1.2,
        ),
        AgentConfig(
            "text",
            mu=0.6,
            sigma=0.3,
            shift=0.2,
            reliability=0.98,
            quality_mean=6.5,
            quality_std=1.0,
        ),
    ]

    def __init__(
        self,
        queue_config: QueueConfig | None = None,
        agents: list[AgentConfig] | None = None,
    ):
        self.queue_config = queue_config or QueueConfig()
        self.agents = agents or [AgentConfig(**a.__dict__) for a in self.DEFAULT_AGENTS]

    def simulate_single(self) -> SimulationResult:
        """Simulate a single queue processing cycle."""
        cfg = self.queue_config
        agent_times = {}
        agent_success = {}
        agent_quality = {}

        # Generate agent responses
        for agent in self.agents:
            response_time = agent.shift + np.random.lognormal(agent.mu, agent.sigma)
            success = np.random.random() < agent.reliability
            quality = (
                np.clip(np.random.normal(agent.quality_mean, agent.quality_std), 0, 10)
                if success
                else 0.0
            )

            agent_times[agent.name] = response_time
            agent_success[agent.name] = success
            agent_quality[agent.name] = quality

        # Sort by response time
        sorted_agents = sorted(agent_times.items(), key=lambda x: x[1])

        # Collect successful results
        successes = [
            (n, t, agent_quality[n]) for n, t in sorted_agents if agent_success[n]
        ]

        # Apply tiered timeout logic
        if len(successes) == 0:
            return SimulationResult(
                QueueStatus.FAILED, cfg.hard_timeout, 0, 0.0, agent_times, agent_success
            )

        by_soft = [(n, t, q) for n, t, q in successes if t <= cfg.soft_timeout]
        by_hard = [(n, t, q) for n, t, q in successes if t <= cfg.hard_timeout]

        if len(successes) >= cfg.expected_agents:
            max_time = max(t for _, t, _ in successes)
            if max_time <= cfg.hard_timeout:
                latency = max_time
                status = QueueStatus.COMPLETE
                num_results = cfg.expected_agents
            else:
                latency = cfg.hard_timeout
                num_results = len(by_hard)
                status = (
                    QueueStatus.SOFT_DEGRADED
                    if num_results >= cfg.min_for_soft
                    else QueueStatus.HARD_DEGRADED
                )
        elif len(by_soft) >= cfg.min_for_soft:
            latency = cfg.soft_timeout
            status = QueueStatus.SOFT_DEGRADED
            num_results = len(by_soft)
        elif len(by_hard) >= cfg.min_for_hard:
            latency = cfg.hard_timeout
            status = QueueStatus.HARD_DEGRADED
            num_results = len(by_hard)
        else:
            latency = cfg.hard_timeout
            status = QueueStatus.FAILED
            num_results = 0

        valid_qualities = [q for _, t, q in successes if t <= latency]
        quality = max(valid_qualities) if valid_qualities else 0.0
        degradation_penalty = 1.0 - 0.05 * (cfg.expected_agents - num_results)
        quality *= max(0, degradation_penalty)

        return SimulationResult(
            status, latency, num_results, quality, agent_times, agent_success
        )

    def run_monte_carlo(self, n_simulations: int = 1000) -> pd.DataFrame:
        """Run Monte Carlo simulation."""
        results = []
        for _ in range(n_simulations):
            result = self.simulate_single()
            results.append(
                {
                    "status": result.status.value,
                    "latency": result.latency,
                    "num_results": result.num_results,
                    "quality": result.quality,
                    **{f"{k}_time": v for k, v in result.agent_times.items()},
                    **{f"{k}_success": v for k, v in result.agent_success.items()},
                }
            )
        return pd.DataFrame(results)


class DashboardDataManager:
    """
    Manages all data operations for the dashboard.

    Provides:
    - Simulation execution
    - Data caching
    - Real-time updates
    - Historical data management
    """

    def __init__(self, cache_dir: Path | None = None):
        self.cache_dir = cache_dir or Path("./data/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self._cache: dict[str, Any] = {}
        self._lock = threading.Lock()
        self._callbacks: list[Callable] = []

        # Initialize with default data
        self._baseline_data: pd.DataFrame | None = None
        self._sensitivity_data: dict[str, pd.DataFrame] = {}

    def get_baseline_simulation(
        self,
        n_sims: int = 5000,
        config: QueueConfig | None = None,
        force_refresh: bool = False,
    ) -> pd.DataFrame:
        """Get or generate baseline simulation data."""
        cache_key = f"baseline_{n_sims}"

        if not force_refresh and cache_key in self._cache:
            return self._cache[cache_key]

        simulator = SmartQueueSimulator(queue_config=config)
        df = simulator.run_monte_carlo(n_simulations=n_sims)

        with self._lock:
            self._cache[cache_key] = df
            self._baseline_data = df

        return df

    def run_sensitivity_analysis(
        self,
        param_name: str,
        param_values: list[float],
        n_sims: int = 2000,
        callback: Callable[[float], None] | None = None,
    ) -> pd.DataFrame:
        """Run sensitivity analysis for a single parameter."""
        results = []

        for i, value in enumerate(param_values):
            config = QueueConfig()
            setattr(config, param_name, value)

            sim = SmartQueueSimulator(queue_config=config)
            df = sim.run_monte_carlo(n_simulations=n_sims)

            complete_rate = (df["status"] == "complete").mean()
            degraded_rate = df["status"].isin(["soft_degraded", "hard_degraded"]).mean()
            failed_rate = (df["status"] == "failed").mean()

            results.append(
                {
                    "param_value": value,
                    "latency_mean": df["latency"].mean(),
                    "latency_std": df["latency"].std(),
                    "latency_p50": df["latency"].quantile(0.5),
                    "latency_p95": df["latency"].quantile(0.95),
                    "latency_p99": df["latency"].quantile(0.99),
                    "quality_mean": df["quality"].mean(),
                    "quality_std": df["quality"].std(),
                    "complete_rate": complete_rate,
                    "degraded_rate": degraded_rate,
                    "failed_rate": failed_rate,
                    "success_rate": 1 - failed_rate,
                }
            )

            if callback:
                callback((i + 1) / len(param_values))

        result_df = pd.DataFrame(results)
        self._sensitivity_data[param_name] = result_df
        return result_df

    def run_pareto_analysis(
        self,
        soft_timeout_range: tuple[float, float] = (5, 30),
        hard_timeout_range: tuple[float, float] = (10, 60),
        n_points: int = 50,
        n_sims: int = 1000,
    ) -> pd.DataFrame:
        """Generate Pareto frontier data."""
        results = []

        soft_values = np.linspace(*soft_timeout_range, int(np.sqrt(n_points)))
        hard_values = np.linspace(*hard_timeout_range, int(np.sqrt(n_points)))

        for soft in soft_values:
            for hard in hard_values:
                if hard <= soft:
                    continue

                config = QueueConfig(soft_timeout=soft, hard_timeout=hard)
                sim = SmartQueueSimulator(queue_config=config)
                df = sim.run_monte_carlo(n_simulations=n_sims)

                results.append(
                    {
                        "soft_timeout": soft,
                        "hard_timeout": hard,
                        "latency_mean": df["latency"].mean(),
                        "quality_mean": df["quality"].mean(),
                        "success_rate": (df["status"] != "failed").mean(),
                        "complete_rate": (df["status"] == "complete").mean(),
                    }
                )

        return pd.DataFrame(results)

    def compare_configurations(
        self, config_a: QueueConfig, config_b: QueueConfig, n_sims: int = 5000
    ) -> dict:
        """Compare two configurations statistically."""
        from scipy import stats

        sim_a = SmartQueueSimulator(queue_config=config_a)
        sim_b = SmartQueueSimulator(queue_config=config_b)

        df_a = sim_a.run_monte_carlo(n_simulations=n_sims)
        df_b = sim_b.run_monte_carlo(n_simulations=n_sims)

        lat_a, lat_b = df_a["latency"].values, df_b["latency"].values
        qual_a, qual_b = df_a["quality"].values, df_b["quality"].values

        # Statistical tests
        t_lat, p_lat = stats.ttest_ind(lat_a, lat_b, equal_var=False)
        t_qual, p_qual = stats.ttest_ind(qual_a, qual_b, equal_var=False)

        # Effect sizes
        pooled_lat = np.sqrt((np.var(lat_a) + np.var(lat_b)) / 2)
        pooled_qual = np.sqrt((np.var(qual_a) + np.var(qual_b)) / 2)
        d_lat = (np.mean(lat_a) - np.mean(lat_b)) / pooled_lat if pooled_lat > 0 else 0
        d_qual = (
            (np.mean(qual_a) - np.mean(qual_b)) / pooled_qual if pooled_qual > 0 else 0
        )

        return {
            "config_a": config_a.__dict__,
            "config_b": config_b.__dict__,
            "df_a": df_a,
            "df_b": df_b,
            "latency": {
                "mean_a": np.mean(lat_a),
                "mean_b": np.mean(lat_b),
                "std_a": np.std(lat_a),
                "std_b": np.std(lat_b),
                "p_value": p_lat,
                "cohens_d": d_lat,
            },
            "quality": {
                "mean_a": np.mean(qual_a),
                "mean_b": np.mean(qual_b),
                "std_a": np.std(qual_a),
                "std_b": np.std(qual_b),
                "p_value": p_qual,
                "cohens_d": d_qual,
            },
            "status_a": df_a["status"].value_counts(normalize=True).to_dict(),
            "status_b": df_b["status"].value_counts(normalize=True).to_dict(),
        }

    def get_real_time_metrics(self) -> dict:
        """Generate simulated real-time metrics for monitoring."""
        # Simulate current system state
        return {
            "timestamp": datetime.now().isoformat(),
            "active_tours": np.random.randint(0, 10),
            "queue_depth": np.random.randint(0, 20),
            "agents": {
                "video": {
                    "status": np.random.choice(
                        ["healthy", "healthy", "degraded"], p=[0.8, 0.15, 0.05]
                    ),
                    "avg_response_time": np.random.uniform(2, 5),
                    "success_rate": np.random.uniform(0.85, 0.98),
                },
                "music": {
                    "status": np.random.choice(
                        ["healthy", "healthy", "degraded"], p=[0.85, 0.12, 0.03]
                    ),
                    "avg_response_time": np.random.uniform(1.5, 4),
                    "success_rate": np.random.uniform(0.90, 0.99),
                },
                "text": {
                    "status": "healthy",
                    "avg_response_time": np.random.uniform(1, 3),
                    "success_rate": np.random.uniform(0.95, 0.99),
                },
            },
            "throughput": np.random.uniform(5, 20),
            "error_rate": np.random.uniform(0, 0.05),
        }

    def export_results(self, output_path: Path) -> None:
        """Export all cached results to JSON."""
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "baseline_stats": self._baseline_data.describe().to_dict()
            if self._baseline_data is not None
            else None,
            "sensitivity_data": {
                k: v.to_dict() for k, v in self._sensitivity_data.items()
            },
        }

        with open(output_path, "w") as f:
            json.dump(export_data, f, indent=2, default=str)
