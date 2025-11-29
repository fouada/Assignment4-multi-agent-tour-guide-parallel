"""
Collector - Aggregates results from the judge and produces the final tour guide output.
Maintains order and provides the final playlist.
"""

import threading
from collections.abc import Callable
from datetime import datetime
from typing import Any

from src.models.decision import JudgeDecision
from src.models.output import TourGuideOutput
from src.models.route import Route
from src.utils.logger import get_logger, set_log_context

logger = get_logger(__name__)


def log_collector_update(point_id: str, content: str):
    """Log collector update."""
    set_log_context(point_id=point_id, agent_type="collector")
    logger.info(f"📥 Collected: {content}")


class ResultCollector:
    """
    Collects and organizes results from the judge agents.
    Maintains proper ordering and generates the final tour guide output.
    """

    def __init__(self, route: Route):
        """
        Initialize the collector.

        Args:
            route: The route being processed
        """
        self.route = route
        self.decisions: dict[str, JudgeDecision] = {}
        self._lock = threading.Lock()
        self._completion_event = threading.Event()
        self.started_at = datetime.now()

        set_log_context(agent_type="collector")
        logger.info(
            f"Collector initialized for route: {route.source} → {route.destination}"
        )

    def add_decision(self, decision: JudgeDecision):
        """
        Add a judge decision to the collection.

        Args:
            decision: The judge's decision for a point
        """
        with self._lock:
            self.decisions[decision.point_id] = decision

            # Find the point index for logging
            next((p for p in self.route.points if p.id == decision.point_id), None)

            log_collector_update(
                decision.point_id,
                f"{decision.selected_content.content_type.value}: {decision.selected_content.title[:30]}...",
            )

            # Check if all points are collected
            if len(self.decisions) >= len(self.route.points):
                self._completion_event.set()
                logger.info("📦 All results collected!")

    def get_decision(self, point_id: str) -> JudgeDecision | None:
        """Get the decision for a specific point."""
        with self._lock:
            return self.decisions.get(point_id)

    def is_complete(self) -> bool:
        """Check if all points have been collected."""
        with self._lock:
            return len(self.decisions) >= len(self.route.points)

    def wait_for_completion(self, timeout: float | None = None) -> bool:
        """
        Wait for all results to be collected.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            True if completed, False if timeout
        """
        return self._completion_event.wait(timeout=timeout)

    def get_progress(self) -> dict:
        """Get collection progress."""
        with self._lock:
            collected = len(self.decisions)
            total = len(self.route.points)

            return {
                "collected": collected,
                "total": total,
                "percentage": (collected / total * 100) if total > 0 else 0,
                "remaining": total - collected,
            }

    def get_ordered_decisions(self) -> list[JudgeDecision]:
        """Get decisions in route order."""
        with self._lock:
            ordered = []
            for point in self.route.points:
                if point.id in self.decisions:
                    ordered.append(self.decisions[point.id])
            return ordered

    def generate_output(self) -> TourGuideOutput:
        """
        Generate the final tour guide output.

        Returns:
            Complete TourGuideOutput with all decisions
        """
        set_log_context(agent_type="collector")

        duration = (datetime.now() - self.started_at).total_seconds()
        ordered_decisions = self.get_ordered_decisions()

        # Calculate statistics
        content_type_counts: dict[str, int] = {}
        total_score: float = 0

        for decision in ordered_decisions:
            content_type = decision.selected_content.content_type.value
            content_type_counts[content_type] = (
                content_type_counts.get(content_type, 0) + 1
            )
            total_score += decision.selected_content.relevance_score

        avg_score = total_score / len(ordered_decisions) if ordered_decisions else 0

        output = TourGuideOutput(
            route=self.route,
            decisions=ordered_decisions,
            processing_stats={
                "total_points": len(self.route.points),
                "processed_points": len(ordered_decisions),
                "processing_time_seconds": duration,
                "content_type_distribution": content_type_counts,
                "average_relevance_score": round(avg_score, 2),
            },
        )

        logger.info(
            f"📊 Tour guide generated: {len(ordered_decisions)} points in {duration:.2f}s"
        )

        return output

    def print_summary(self):
        """Print a summary of collected results."""
        set_log_context(agent_type="collector")

        progress = self.get_progress()
        print("\n" + "=" * 60)
        print("📊 COLLECTION SUMMARY")
        print("=" * 60)
        print(f"Route: {self.route.source} → {self.route.destination}")
        print(
            f"Progress: {progress['collected']}/{progress['total']} ({progress['percentage']:.1f}%)"
        )
        print("-" * 60)

        for point in self.route.points:
            decision = self.decisions.get(point.id)
            if decision:
                content = decision.selected_content
                emoji = {"video": "🎬", "music": "🎵", "text": "📖"}.get(
                    content.content_type.value, "📄"
                )

                print(f"\n📍 {point.index + 1}. {point.location_name or point.address}")
                print(
                    f"   {emoji} {content.content_type.value.upper()}: {content.title}"
                )
                print(f"   ⭐ Score: {content.relevance_score:.1f}/10")
            else:
                print(f"\n📍 {point.index + 1}. {point.location_name or point.address}")
                print("   ⏳ Pending...")

        print("\n" + "=" * 60)


class StreamingCollector(ResultCollector):
    """
    Extended collector that supports streaming output.
    Provides results as they arrive rather than waiting for completion.
    """

    def __init__(
        self, route: Route, on_decision: Callable[[JudgeDecision], Any] | None = None
    ):
        """
        Initialize streaming collector.

        Args:
            route: The route being processed
            on_decision: Callback for each new decision
        """
        super().__init__(route)
        self.on_decision = on_decision
        self._decision_order: list[str] = []

    def add_decision(self, decision: JudgeDecision):
        """Add decision and notify callback."""
        super().add_decision(decision)

        with self._lock:
            self._decision_order.append(decision.point_id)

        # Notify callback
        if self.on_decision:
            try:
                self.on_decision(decision)
            except Exception as e:
                logger.error(f"Decision callback error: {e}")

    def get_latest_decisions(self, count: int = 5) -> list[JudgeDecision]:
        """Get the most recently received decisions."""
        with self._lock:
            recent_ids = self._decision_order[-count:]
            return [self.decisions[pid] for pid in recent_ids if pid in self.decisions]

    def stream_results(self):
        """Generator that yields decisions as they arrive."""
        yielded = set()

        while not self.is_complete():
            with self._lock:
                for point_id in self._decision_order:
                    if point_id not in yielded:
                        yielded.add(point_id)
                        yield self.decisions[point_id]

            # Small sleep to prevent busy waiting
            import time

            time.sleep(0.1)

        # Yield any remaining
        with self._lock:
            for point_id in self._decision_order:
                if point_id not in yielded:
                    yielded.add(point_id)
                    yield self.decisions[point_id]
