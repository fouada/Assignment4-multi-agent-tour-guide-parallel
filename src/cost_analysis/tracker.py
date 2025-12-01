"""
Cost Tracking System
====================

Real-time and historical cost tracking for the Multi-Agent Tour Guide System.

Features:
- Thread-safe cost event recording
- Agent-level cost attribution
- Tour-level cost aggregation
- Historical trend analysis
- Budget alerting

Author: Multi-Agent Tour Guide Research Team
Version: 1.0.0
"""

from __future__ import annotations

import json
import logging
import threading
from collections import defaultdict
from collections.abc import Callable
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from src.cost_analysis.models import (
    APICostModel,
    ComputeCostModel,
    CostCategory,
    CostEvent,
    LLMCostModel,
    TourCostSummary,
)

logger = logging.getLogger(__name__)


class CostTracker:
    """
    Central cost tracking system.

    Thread-safe implementation for tracking costs across all system components.
    Supports real-time monitoring, alerting, and historical analysis.
    """

    def __init__(
        self,
        llm_model: LLMCostModel | None = None,
        api_model: APICostModel | None = None,
        compute_model: ComputeCostModel | None = None,
        budget_limit_usd: float = 100.0,
        alert_threshold: float = 0.8,  # Alert at 80% of budget
    ):
        """
        Initialize cost tracker.

        Args:
            llm_model: LLM cost calculation model
            api_model: API cost calculation model
            compute_model: Compute cost calculation model
            budget_limit_usd: Monthly budget limit in USD
            alert_threshold: Threshold for budget alerts (0-1)
        """
        self.llm_model = llm_model or LLMCostModel()
        self.api_model = api_model or APICostModel()
        self.compute_model = compute_model or ComputeCostModel()

        self.budget_limit_usd = budget_limit_usd
        self.alert_threshold = alert_threshold

        # Thread-safe data structures
        self._lock = threading.RLock()
        self._events: list[CostEvent] = []
        self._category_totals: dict[CostCategory, float] = defaultdict(float)
        self._agent_totals: dict[str, float] = defaultdict(float)
        self._tour_totals: dict[str, float] = defaultdict(float)

        # Alerting
        self._alert_callbacks: list[Callable[[str, float], None]] = []
        self._alert_sent = False

        # Persistence
        self._persistence_path: Path | None = None

    def record_llm_usage(
        self,
        input_tokens: int,
        output_tokens: int,
        agent_type: str | None = None,
        point_id: str | None = None,
        tour_id: str | None = None,
        model: str | None = None,
    ) -> CostEvent:
        """
        Record LLM API usage and calculate cost.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            agent_type: Type of agent making the call
            point_id: Route point identifier
            tour_id: Tour identifier
            model: Override model for cost calculation

        Returns:
            CostEvent with calculated cost
        """
        # Use override model if provided
        if model:
            original_model = self.llm_model.model
            self.llm_model.model = model
            cost = self.llm_model.calculate_cost(input_tokens, output_tokens)
            self.llm_model.model = original_model
        else:
            cost = self.llm_model.calculate_cost(input_tokens, output_tokens)

        # Create separate events for input and output
        input_event = CostEvent(
            timestamp=datetime.now(),
            category=CostCategory.LLM_INPUT_TOKENS,
            amount_usd=cost * (input_tokens / (input_tokens + output_tokens))
            if (input_tokens + output_tokens) > 0
            else 0,
            agent_type=agent_type,
            point_id=point_id,
            tour_id=tour_id,
            metadata={
                "tokens": input_tokens,
                "model": model or self.llm_model.model,
            },
        )

        output_event = CostEvent(
            timestamp=datetime.now(),
            category=CostCategory.LLM_OUTPUT_TOKENS,
            amount_usd=cost * (output_tokens / (input_tokens + output_tokens))
            if (input_tokens + output_tokens) > 0
            else 0,
            agent_type=agent_type,
            point_id=point_id,
            tour_id=tour_id,
            metadata={
                "tokens": output_tokens,
                "model": model or self.llm_model.model,
            },
        )

        with self._lock:
            self._events.extend([input_event, output_event])
            self._category_totals[CostCategory.LLM_INPUT_TOKENS] += (
                input_event.amount_usd
            )
            self._category_totals[CostCategory.LLM_OUTPUT_TOKENS] += (
                output_event.amount_usd
            )

            if agent_type:
                self._agent_totals[agent_type] += cost
            if tour_id:
                self._tour_totals[tour_id] += cost

        self._check_budget()

        logger.debug(
            f"LLM cost recorded: ${cost:.6f} "
            f"({input_tokens} input, {output_tokens} output tokens)"
        )

        # Return combined event for convenience
        return CostEvent(
            timestamp=datetime.now(),
            category=CostCategory.LLM_INPUT_TOKENS,  # Primary category
            amount_usd=cost,
            agent_type=agent_type,
            point_id=point_id,
            tour_id=tour_id,
            metadata={
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "model": model or self.llm_model.model,
            },
        )

    def record_api_call(
        self,
        api_type: str,
        calls: int = 1,
        agent_type: str | None = None,
        point_id: str | None = None,
        tour_id: str | None = None,
    ) -> CostEvent:
        """
        Record external API call and calculate cost.

        Args:
            api_type: Type of API (google_maps, youtube, web_search)
            calls: Number of API calls
            agent_type: Type of agent making the call
            point_id: Route point identifier
            tour_id: Tour identifier

        Returns:
            CostEvent with calculated cost
        """
        # Calculate cost based on API type
        if api_type == "google_maps":
            cost = self.api_model.calculate_google_maps_cost(directions_calls=calls)
            category = CostCategory.API_GOOGLE_MAPS
        elif api_type == "youtube":
            cost = self.api_model.calculate_youtube_cost(search_calls=calls)
            category = CostCategory.API_YOUTUBE
        elif api_type == "web_search":
            cost = self.api_model.calculate_web_search_cost(search_calls=calls)
            category = CostCategory.API_WEB_SEARCH
        elif api_type == "spotify":
            cost = 0.0  # Spotify is free (rate-limited)
            category = CostCategory.API_SPOTIFY
        else:
            cost = 0.0
            category = CostCategory.API_WEB_SEARCH

        event = CostEvent(
            timestamp=datetime.now(),
            category=category,
            amount_usd=cost,
            agent_type=agent_type,
            point_id=point_id,
            tour_id=tour_id,
            metadata={
                "api_type": api_type,
                "calls": calls,
            },
        )

        with self._lock:
            self._events.append(event)
            self._category_totals[category] += cost

            if agent_type:
                self._agent_totals[agent_type] += cost
            if tour_id:
                self._tour_totals[tour_id] += cost

        self._check_budget()

        logger.debug(f"API cost recorded: ${cost:.6f} ({api_type}, {calls} calls)")

        return event

    def record_compute_usage(
        self,
        cpu_seconds: float,
        memory_gb: float = 0.5,
        duration_seconds: float = 0,
        agent_type: str | None = None,
        tour_id: str | None = None,
    ) -> CostEvent:
        """
        Record compute resource usage and calculate cost.

        Args:
            cpu_seconds: CPU time in seconds
            memory_gb: Memory usage in GB
            duration_seconds: Wall clock duration
            agent_type: Type of agent
            tour_id: Tour identifier

        Returns:
            CostEvent with calculated cost
        """
        cost = self.compute_model.calculate_execution_cost(
            cpu_seconds, memory_gb, duration_seconds
        )

        event = CostEvent(
            timestamp=datetime.now(),
            category=CostCategory.COMPUTE_CPU,
            amount_usd=cost,
            agent_type=agent_type,
            tour_id=tour_id,
            metadata={
                "cpu_seconds": cpu_seconds,
                "memory_gb": memory_gb,
                "duration_seconds": duration_seconds,
            },
        )

        with self._lock:
            self._events.append(event)
            self._category_totals[CostCategory.COMPUTE_CPU] += cost

            if agent_type:
                self._agent_totals[agent_type] += cost
            if tour_id:
                self._tour_totals[tour_id] += cost

        return event

    def record_savings(
        self,
        savings_type: str,
        amount_usd: float,
        agent_type: str | None = None,
        tour_id: str | None = None,
    ) -> CostEvent:
        """
        Record cost savings (cache hits, circuit breaker).

        Args:
            savings_type: Type of savings (cache_hit, circuit_breaker)
            amount_usd: Amount saved in USD
            agent_type: Type of agent
            tour_id: Tour identifier

        Returns:
            CostEvent with savings
        """
        category = (
            CostCategory.CACHE_HIT_SAVINGS
            if savings_type == "cache_hit"
            else CostCategory.CIRCUIT_BREAKER_SAVINGS
        )

        # Savings are recorded as negative costs
        event = CostEvent(
            timestamp=datetime.now(),
            category=category,
            amount_usd=-amount_usd,  # Negative for savings
            agent_type=agent_type,
            tour_id=tour_id,
            metadata={"savings_type": savings_type},
        )

        with self._lock:
            self._events.append(event)
            self._category_totals[category] += -amount_usd

        logger.debug(f"Savings recorded: ${amount_usd:.6f} ({savings_type})")

        return event

    def record_retry_overhead(
        self,
        overhead_usd: float,
        agent_type: str | None = None,
        tour_id: str | None = None,
        retry_count: int = 1,
    ) -> CostEvent:
        """Record additional cost from retries."""
        event = CostEvent(
            timestamp=datetime.now(),
            category=CostCategory.RETRY_OVERHEAD,
            amount_usd=overhead_usd,
            agent_type=agent_type,
            tour_id=tour_id,
            metadata={"retry_count": retry_count},
        )

        with self._lock:
            self._events.append(event)
            self._category_totals[CostCategory.RETRY_OVERHEAD] += overhead_usd

            if agent_type:
                self._agent_totals[agent_type] += overhead_usd
            if tour_id:
                self._tour_totals[tour_id] += overhead_usd

        return event

    def get_total_cost(self) -> float:
        """Get total cost across all categories."""
        with self._lock:
            return sum(
                v
                for k, v in self._category_totals.items()
                if k
                not in {
                    CostCategory.CACHE_HIT_SAVINGS,
                    CostCategory.CIRCUIT_BREAKER_SAVINGS,
                }
            )

    def get_total_savings(self) -> float:
        """Get total savings."""
        with self._lock:
            return abs(
                sum(
                    v
                    for k, v in self._category_totals.items()
                    if k
                    in {
                        CostCategory.CACHE_HIT_SAVINGS,
                        CostCategory.CIRCUIT_BREAKER_SAVINGS,
                    }
                )
            )

    def get_effective_cost(self) -> float:
        """Get effective cost after savings."""
        return self.get_total_cost() - self.get_total_savings()

    def get_cost_breakdown(self) -> dict[str, float]:
        """Get cost breakdown by category."""
        with self._lock:
            return {k.value: v for k, v in self._category_totals.items()}

    def get_agent_costs(self) -> dict[str, float]:
        """Get cost breakdown by agent."""
        with self._lock:
            return dict(self._agent_totals)

    def get_tour_costs(self) -> dict[str, float]:
        """Get cost breakdown by tour."""
        with self._lock:
            return dict(self._tour_totals)

    def get_events_in_range(
        self,
        start: datetime,
        end: datetime,
    ) -> list[CostEvent]:
        """Get events within a time range."""
        with self._lock:
            return [e for e in self._events if start <= e.timestamp <= end]

    def get_hourly_costs(
        self,
        hours: int = 24,
    ) -> dict[str, float]:
        """Get hourly cost breakdown."""
        now = datetime.now()
        hourly_costs = {}

        for h in range(hours):
            hour_start = now - timedelta(hours=h + 1)
            hour_end = now - timedelta(hours=h)

            events = self.get_events_in_range(hour_start, hour_end)
            total = sum(e.amount_usd for e in events if e.amount_usd > 0)

            hour_label = hour_end.strftime("%H:%M")
            hourly_costs[hour_label] = total

        return hourly_costs

    def register_alert_callback(
        self,
        callback: Callable[[str, float], None],
    ) -> None:
        """Register callback for budget alerts."""
        self._alert_callbacks.append(callback)

    def _check_budget(self) -> None:
        """Check if budget threshold is exceeded."""
        total_cost = self.get_total_cost()
        threshold_amount = self.budget_limit_usd * self.alert_threshold

        if total_cost >= threshold_amount and not self._alert_sent:
            self._alert_sent = True
            message = (
                f"Budget alert: ${total_cost:.2f} spent "
                f"({total_cost / self.budget_limit_usd * 100:.1f}% of ${self.budget_limit_usd} limit)"
            )

            logger.warning(message)

            for callback in self._alert_callbacks:
                try:
                    callback(message, total_cost)
                except Exception as e:
                    logger.error(f"Alert callback error: {e}")

    def set_persistence_path(self, path: Path) -> None:
        """Set path for persisting cost data."""
        self._persistence_path = path
        path.parent.mkdir(parents=True, exist_ok=True)

    def persist(self) -> None:
        """Persist current state to disk."""
        if not self._persistence_path:
            return

        with self._lock:
            data = {
                "timestamp": datetime.now().isoformat(),
                "events": [e.to_dict() for e in self._events],
                "category_totals": {
                    k.value: v for k, v in self._category_totals.items()
                },
                "agent_totals": dict(self._agent_totals),
                "tour_totals": dict(self._tour_totals),
            }

        with open(self._persistence_path, "w") as f:
            json.dump(data, f, indent=2)

    def reset(self) -> None:
        """Reset all tracking data."""
        with self._lock:
            self._events.clear()
            self._category_totals.clear()
            self._agent_totals.clear()
            self._tour_totals.clear()
            self._alert_sent = False


class AgentCostTracker:
    """
    Cost tracker for a single agent.

    Provides detailed cost tracking at the agent level with
    automatic aggregation to the central tracker.
    """

    def __init__(
        self,
        agent_type: str,
        central_tracker: CostTracker,
    ):
        """
        Initialize agent cost tracker.

        Args:
            agent_type: Type of agent (video, music, text, judge)
            central_tracker: Central cost tracking system
        """
        self.agent_type = agent_type
        self.central_tracker = central_tracker

        # Agent-specific metrics
        self._call_count = 0
        self._total_tokens = 0
        self._total_api_calls = 0
        self._total_cost = 0.0
        self._lock = threading.Lock()

    def track_llm_call(
        self,
        input_tokens: int,
        output_tokens: int,
        point_id: str | None = None,
        tour_id: str | None = None,
    ) -> float:
        """Track LLM call for this agent."""
        event = self.central_tracker.record_llm_usage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            agent_type=self.agent_type,
            point_id=point_id,
            tour_id=tour_id,
        )

        with self._lock:
            self._call_count += 1
            self._total_tokens += input_tokens + output_tokens
            self._total_cost += event.amount_usd

        return event.amount_usd

    def track_api_call(
        self,
        api_type: str,
        calls: int = 1,
        point_id: str | None = None,
        tour_id: str | None = None,
    ) -> float:
        """Track API call for this agent."""
        event = self.central_tracker.record_api_call(
            api_type=api_type,
            calls=calls,
            agent_type=self.agent_type,
            point_id=point_id,
            tour_id=tour_id,
        )

        with self._lock:
            self._total_api_calls += calls
            self._total_cost += event.amount_usd

        return event.amount_usd

    def track_cache_hit(
        self,
        estimated_savings: float,
        tour_id: str | None = None,
    ) -> None:
        """Track cache hit savings."""
        self.central_tracker.record_savings(
            savings_type="cache_hit",
            amount_usd=estimated_savings,
            agent_type=self.agent_type,
            tour_id=tour_id,
        )

    def get_stats(self) -> dict[str, Any]:
        """Get agent cost statistics."""
        with self._lock:
            return {
                "agent_type": self.agent_type,
                "call_count": self._call_count,
                "total_tokens": self._total_tokens,
                "total_api_calls": self._total_api_calls,
                "total_cost": self._total_cost,
                "avg_cost_per_call": self._total_cost / self._call_count
                if self._call_count > 0
                else 0,
            }


class TourCostTracker:
    """
    Cost tracker for a single tour execution.

    Aggregates costs at the tour level and provides
    detailed per-point breakdown.
    """

    def __init__(
        self,
        tour_id: str,
        central_tracker: CostTracker,
    ):
        """
        Initialize tour cost tracker.

        Args:
            tour_id: Unique tour identifier
            central_tracker: Central cost tracking system
        """
        self.tour_id = tour_id
        self.central_tracker = central_tracker

        self.summary = TourCostSummary(
            tour_id=tour_id,
            start_time=datetime.now(),
        )

        self._point_costs: dict[str, float] = {}
        self._lock = threading.Lock()

    def start(self) -> None:
        """Mark tour start."""
        self.summary.start_time = datetime.now()

    def complete(self) -> TourCostSummary:
        """Mark tour complete and return summary."""
        self.summary.end_time = datetime.now()

        # Aggregate costs from central tracker
        events = self.central_tracker.get_events_in_range(
            self.summary.start_time,
            self.summary.end_time,
        )

        for event in events:
            if event.tour_id == self.tour_id:
                if event.category in {
                    CostCategory.LLM_INPUT_TOKENS,
                    CostCategory.LLM_OUTPUT_TOKENS,
                }:
                    self.summary.llm_costs += event.amount_usd
                    if "tokens" in event.metadata:
                        if event.category == CostCategory.LLM_INPUT_TOKENS:
                            self.summary.total_input_tokens += event.metadata["tokens"]
                        else:
                            self.summary.total_output_tokens += event.metadata["tokens"]
                elif event.category in {
                    CostCategory.API_GOOGLE_MAPS,
                    CostCategory.API_YOUTUBE,
                    CostCategory.API_WEB_SEARCH,
                }:
                    self.summary.api_costs += event.amount_usd
                    if event.category == CostCategory.API_GOOGLE_MAPS:
                        self.summary.google_maps_calls += event.metadata.get("calls", 0)
                    elif event.category == CostCategory.API_YOUTUBE:
                        self.summary.youtube_calls += event.metadata.get("calls", 0)
                    else:
                        self.summary.web_search_calls += event.metadata.get("calls", 0)
                elif event.category == CostCategory.COMPUTE_CPU:
                    self.summary.compute_costs += event.amount_usd
                elif event.category == CostCategory.CACHE_HIT_SAVINGS:
                    self.summary.cache_savings += abs(event.amount_usd)
                elif event.category == CostCategory.CIRCUIT_BREAKER_SAVINGS:
                    self.summary.circuit_breaker_savings += abs(event.amount_usd)
                elif event.category == CostCategory.RETRY_OVERHEAD:
                    self.summary.retry_overhead += event.amount_usd

                # Track per-agent costs
                if event.agent_type:
                    if event.agent_type not in self.summary.agent_costs:
                        self.summary.agent_costs[event.agent_type] = 0.0
                    self.summary.agent_costs[event.agent_type] += event.amount_usd

        return self.summary

    def set_num_points(self, num_points: int) -> None:
        """Set number of route points."""
        self.summary.num_points = num_points

    def record_point_cost(self, point_id: str, cost: float) -> None:
        """Record cost for a specific point."""
        with self._lock:
            self._point_costs[point_id] = cost

    def get_point_costs(self) -> dict[str, float]:
        """Get costs by point."""
        with self._lock:
            return dict(self._point_costs)


# Global cost tracker instance
_global_tracker: CostTracker | None = None


def get_cost_tracker() -> CostTracker:
    """Get or create global cost tracker instance."""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = CostTracker()
    return _global_tracker


def reset_cost_tracker() -> None:
    """Reset global cost tracker."""
    global _global_tracker
    _global_tracker = None
