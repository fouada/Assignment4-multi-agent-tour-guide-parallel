"""
Smart Agent Queue - Production Implementation

This queue implements the BEST design for a startup:
1. Wait for all 3 agents (ideal quality)
2. After soft timeout: proceed with 2/3 (graceful degradation)
3. After hard timeout: proceed with 1/3 (emergency fallback)

The queue NEVER blocks forever and ALWAYS produces output.
"""

import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from src.models.content import ContentResult, ContentType
from src.utils.logger import get_logger

logger = get_logger(__name__)


class QueueStatus(Enum):
    """Queue completion status"""

    WAITING = "waiting"
    COMPLETE = "complete"  # All agents responded
    SOFT_DEGRADED = "soft_degraded"  # 2/3 agents responded
    HARD_DEGRADED = "hard_degraded"  # 1/3 agents responded
    FAILED = "failed"  # No agents responded


@dataclass
class QueueMetrics:
    """Metrics for monitoring queue performance"""

    point_id: str
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime | None = None
    status: QueueStatus = QueueStatus.WAITING
    agents_expected: int = 3
    agents_received: int = 0
    agents_succeeded: list[str] = field(default_factory=list)
    agents_failed: list[str] = field(default_factory=list)
    wait_time_ms: int = 0

    def complete(self, status: QueueStatus):
        self.end_time = datetime.now()
        self.status = status
        self.wait_time_ms = int(
            (self.end_time - self.start_time).total_seconds() * 1000
        )


class SmartAgentQueue:
    """
    Intelligent queue that balances quality vs responsiveness.

    Strategy:
    - IDEAL: Wait for all 3 agents (best content quality)
    - SOFT TIMEOUT: After 15s, if 2/3 ready, proceed (good enough)
    - HARD TIMEOUT: After 30s, proceed with whatever we have (never block)

    This is the RECOMMENDED design for production because:
    1. Users get best quality when all agents respond quickly
    2. Users aren't stuck waiting forever if one agent is slow
    3. System always produces output (graceful degradation)
    4. Metrics help identify problematic agents
    """

    # Configuration (can be loaded from YAML in production)
    EXPECTED_AGENTS = 3
    SOFT_TIMEOUT_SECONDS = 15.0  # Proceed with 2/3 after this
    HARD_TIMEOUT_SECONDS = 30.0  # Proceed with anything after this
    MIN_REQUIRED_FOR_SOFT = 2  # Minimum for soft timeout
    MIN_REQUIRED_FOR_HARD = 1  # Minimum for hard timeout

    def __init__(self, point_id: str):
        self.point_id = point_id
        self._results: dict[str, ContentResult] = {}
        self._failures: dict[str, str] = {}  # agent_type -> error message
        self._start_time = time.time()
        self._condition = threading.Condition()
        self._metrics = QueueMetrics(point_id=point_id)

        logger.info(
            f"[{point_id}] Smart Queue initialized (expecting {self.EXPECTED_AGENTS} agents)"
        )

    def submit_success(self, agent_type: str, result: ContentResult):
        """
        Agent submits successful result.
        Called by agents after they find content.
        """
        with self._condition:
            self._results[agent_type] = result
            self._metrics.agents_succeeded.append(agent_type)
            self._metrics.agents_received += 1

            elapsed = time.time() - self._start_time
            count = len(self._results)

            logger.info(
                f"[{self.point_id}] ✅ {agent_type} submitted result "
                f"({count}/{self.EXPECTED_AGENTS}) [{elapsed:.1f}s elapsed]"
            )

            # Wake up anyone waiting for results
            self._condition.notify_all()

    def submit_failure(self, agent_type: str, error: str):
        """
        Agent reports failure after all retries exhausted.
        This counts toward the response count but not results.
        """
        with self._condition:
            self._failures[agent_type] = error
            self._metrics.agents_failed.append(agent_type)
            self._metrics.agents_received += 1

            elapsed = time.time() - self._start_time

            logger.warning(
                f"[{self.point_id}] ❌ {agent_type} failed: {error} [{elapsed:.1f}s elapsed]"
            )

            # Wake up anyone waiting (they might need to check timeouts)
            self._condition.notify_all()

    def wait_for_results(self) -> tuple[list[ContentResult], QueueMetrics]:
        """
        Wait for agent results with smart timeout strategy.

        Returns:
            Tuple of (results list, metrics)

        Strategy:
            1. Wait up to SOFT_TIMEOUT for all 3 agents
            2. If 2/3 ready at soft timeout, proceed (graceful degradation)
            3. Wait up to HARD_TIMEOUT if less than 2 ready
            4. At hard timeout, proceed with whatever we have (min 1)
            5. Raise error if 0 results at hard timeout
        """
        with self._condition:
            while True:
                elapsed = time.time() - self._start_time
                result_count = len(self._results)
                total_responses = len(self._results) + len(self._failures)

                # ===== CASE 1: All agents responded (ideal) =====
                if total_responses >= self.EXPECTED_AGENTS:
                    if result_count >= self.EXPECTED_AGENTS:
                        status = QueueStatus.COMPLETE
                        logger.info(
                            f"[{self.point_id}] 🎉 All {self.EXPECTED_AGENTS} agents succeeded!"
                        )
                    elif result_count >= self.MIN_REQUIRED_FOR_SOFT:
                        status = QueueStatus.SOFT_DEGRADED
                        logger.info(
                            f"[{self.point_id}] ⚠️ {result_count}/{self.EXPECTED_AGENTS} agents succeeded "
                            f"(some failed: {list(self._failures.keys())})"
                        )
                    elif result_count >= self.MIN_REQUIRED_FOR_HARD:
                        status = QueueStatus.HARD_DEGRADED
                        logger.warning(
                            f"[{self.point_id}] 🔶 Only {result_count}/{self.EXPECTED_AGENTS} agents succeeded"
                        )
                    else:
                        status = QueueStatus.FAILED
                        logger.error(f"[{self.point_id}] 💥 All agents failed!")
                        self._metrics.complete(status)
                        raise NoResultsError(
                            f"All agents failed for point {self.point_id}"
                        )

                    self._metrics.complete(status)
                    return list(self._results.values()), self._metrics

                # ===== CASE 2: Soft timeout reached =====
                if elapsed >= self.SOFT_TIMEOUT_SECONDS:
                    if result_count >= self.MIN_REQUIRED_FOR_SOFT:
                        missing = self._get_missing_agents()
                        logger.warning(
                            f"[{self.point_id}] ⏱️ Soft timeout ({self.SOFT_TIMEOUT_SECONDS}s): "
                            f"proceeding with {result_count}/{self.EXPECTED_AGENTS} "
                            f"(missing: {missing})"
                        )
                        self._metrics.complete(QueueStatus.SOFT_DEGRADED)
                        return list(self._results.values()), self._metrics

                # ===== CASE 3: Hard timeout reached =====
                if elapsed >= self.HARD_TIMEOUT_SECONDS:
                    if result_count >= self.MIN_REQUIRED_FOR_HARD:
                        missing = self._get_missing_agents()
                        logger.error(
                            f"[{self.point_id}] 🚨 Hard timeout ({self.HARD_TIMEOUT_SECONDS}s): "
                            f"proceeding with {result_count}/{self.EXPECTED_AGENTS} "
                            f"(missing: {missing})"
                        )
                        self._metrics.complete(QueueStatus.HARD_DEGRADED)
                        return list(self._results.values()), self._metrics
                    else:
                        self._metrics.complete(QueueStatus.FAILED)
                        raise NoResultsError(
                            f"No results after {self.HARD_TIMEOUT_SECONDS}s for point {self.point_id}"
                        )

                # ===== Calculate wait time =====
                if result_count >= self.MIN_REQUIRED_FOR_SOFT:
                    # We have 2, wait until soft timeout to give 3rd a chance
                    wait_time = max(0.1, self.SOFT_TIMEOUT_SECONDS - elapsed)
                else:
                    # We have <2, wait until hard timeout
                    wait_time = max(0.1, self.HARD_TIMEOUT_SECONDS - elapsed)

                logger.debug(
                    f"[{self.point_id}] Waiting up to {wait_time:.1f}s more "
                    f"(have {result_count}/{self.EXPECTED_AGENTS})"
                )

                self._condition.wait(timeout=wait_time)

    def _get_missing_agents(self) -> set[str]:
        """Get agents that haven't responded yet"""
        expected = {"video", "music", "text"}
        responded = set(self._results.keys()) | set(self._failures.keys())
        return expected - responded

    @property
    def metrics(self) -> QueueMetrics:
        """Get current metrics (even if waiting)"""
        return self._metrics


class NoResultsError(Exception):
    """Raised when no agents produce results"""

    pass


# ============================================================================
#                         QUEUE MANAGER (SINGLETON)
# ============================================================================


class QueueManager:
    """
    Manages all queues across route points.
    Provides global metrics and monitoring.
    """

    _instance: "QueueManager | None" = None
    _lock = threading.Lock()
    _queues: dict[str, SmartAgentQueue]
    _completed_metrics: list[QueueMetrics]

    def __new__(cls) -> "QueueManager":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._queues = {}
                cls._instance._completed_metrics = []
            return cls._instance

    def get_or_create_queue(self, point_id: str) -> SmartAgentQueue:
        """Get existing queue or create new one for point"""
        with self._lock:
            if point_id not in self._queues:
                self._queues[point_id] = SmartAgentQueue(point_id)
            return self._queues[point_id]

    def complete_queue(self, point_id: str, metrics: QueueMetrics):
        """Mark queue as completed and store metrics"""
        with self._lock:
            self._completed_metrics.append(metrics)
            if point_id in self._queues:
                del self._queues[point_id]

    def get_stats(self) -> dict[str, int | float]:
        """Get aggregate statistics for monitoring"""
        if not self._completed_metrics:
            return {"total": 0}

        total = len(self._completed_metrics)
        complete = sum(
            1 for m in self._completed_metrics if m.status == QueueStatus.COMPLETE
        )
        soft_degraded = sum(
            1 for m in self._completed_metrics if m.status == QueueStatus.SOFT_DEGRADED
        )
        hard_degraded = sum(
            1 for m in self._completed_metrics if m.status == QueueStatus.HARD_DEGRADED
        )
        failed = sum(
            1 for m in self._completed_metrics if m.status == QueueStatus.FAILED
        )
        avg_wait = sum(m.wait_time_ms for m in self._completed_metrics) / total

        return {
            "total": total,
            "complete": complete,
            "soft_degraded": soft_degraded,
            "hard_degraded": hard_degraded,
            "failed": failed,
            "success_rate": (total - failed) / total * 100,
            "perfect_rate": complete / total * 100,
            "avg_wait_ms": avg_wait,
        }


# ============================================================================
#                              USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    """
    Demonstration of Smart Queue behavior
    """
    import random

    def simulate_agent(
        queue: SmartAgentQueue, agent_type: str, delay: float, fail: bool = False
    ):
        """Simulate an agent with delay and possible failure"""
        time.sleep(delay)
        if fail:
            queue.submit_failure(agent_type, "API timeout")
        else:
            result = ContentResult(
                content_type=ContentType(agent_type),
                title=f"{agent_type.title()} content for {queue.point_id}",
                description=f"Found by {agent_type} agent",
                url=f"https://example.com/{agent_type}",
                source=f"Mock {agent_type.title()}",
                relevance_score=random.uniform(0.5, 1.0) * 10,
            )
            queue.submit_success(agent_type, result)

    print("=" * 60)
    print("SCENARIO 1: All agents succeed quickly")
    print("=" * 60)

    queue1 = SmartAgentQueue("point_1")
    threads = [
        threading.Thread(target=simulate_agent, args=(queue1, "video", 1.0)),
        threading.Thread(target=simulate_agent, args=(queue1, "music", 1.5)),
        threading.Thread(target=simulate_agent, args=(queue1, "text", 2.0)),
    ]
    for t in threads:
        t.start()

    results, metrics = queue1.wait_for_results()
    print(
        f"Results: {len(results)}, Status: {metrics.status.value}, Wait: {metrics.wait_time_ms}ms\n"
    )

    print("=" * 60)
    print("SCENARIO 2: One agent is slow (soft timeout with 2/3)")
    print("=" * 60)

    # Reduce timeout for demo
    SmartAgentQueue.SOFT_TIMEOUT_SECONDS = 3.0
    SmartAgentQueue.HARD_TIMEOUT_SECONDS = 5.0

    queue2 = SmartAgentQueue("point_2")
    threads = [
        threading.Thread(target=simulate_agent, args=(queue2, "video", 1.0)),
        threading.Thread(target=simulate_agent, args=(queue2, "music", 2.0)),
        threading.Thread(
            target=simulate_agent, args=(queue2, "text", 10.0)
        ),  # Very slow!
    ]
    for t in threads:
        t.start()

    results, metrics = queue2.wait_for_results()
    print(
        f"Results: {len(results)}, Status: {metrics.status.value}, Wait: {metrics.wait_time_ms}ms\n"
    )

    print("=" * 60)
    print("SCENARIO 3: Two agents fail (hard timeout with 1/3)")
    print("=" * 60)

    queue3 = SmartAgentQueue("point_3")
    threads = [
        threading.Thread(target=simulate_agent, args=(queue3, "video", 1.0)),
        threading.Thread(
            target=simulate_agent, args=(queue3, "music", 1.5, True)
        ),  # Fails
        threading.Thread(
            target=simulate_agent, args=(queue3, "text", 2.0, True)
        ),  # Fails
    ]
    for t in threads:
        t.start()

    results, metrics = queue3.wait_for_results()
    print(f"Results: {len(results)}, Status: {metrics.status.value}")
    print(f"Succeeded: {metrics.agents_succeeded}")
    print(f"Failed: {metrics.agents_failed}\n")

    # Print overall stats
    manager = QueueManager()
    manager.complete_queue("point_1", queue1.metrics)
    manager.complete_queue("point_2", queue2.metrics)
    manager.complete_queue("point_3", queue3.metrics)

    print("=" * 60)
    print("OVERALL STATISTICS")
    print("=" * 60)
    stats = manager.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
