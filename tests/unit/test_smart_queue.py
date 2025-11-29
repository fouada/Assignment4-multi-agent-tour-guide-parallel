"""
Unit tests for SmartAgentQueue and QueueManager.

Test Coverage:
- Queue initialization and configuration
- Agent result submission (success/failure)
- Timeout strategies (soft/hard)
- Queue status transitions
- QueueManager singleton behavior
- Edge cases: all fail, partial success, concurrent access
"""

import threading
import time

import pytest

from src.core.smart_queue import (
    NoResultsError,
    QueueManager,
    QueueMetrics,
    QueueStatus,
    SmartAgentQueue,
)
from src.models.content import ContentResult, ContentType


class TestQueueMetrics:
    """Tests for QueueMetrics dataclass."""

    def test_create_metrics(self):
        """Test creating queue metrics."""
        metrics = QueueMetrics(point_id="p1")
        assert metrics.point_id == "p1"
        assert metrics.status == QueueStatus.WAITING
        assert metrics.agents_expected == 3
        assert metrics.agents_received == 0
        assert metrics.agents_succeeded == []
        assert metrics.agents_failed == []

    def test_complete_metrics(self):
        """Test completing metrics."""
        metrics = QueueMetrics(point_id="p1")
        time.sleep(0.01)  # Small delay
        metrics.complete(QueueStatus.COMPLETE)

        assert metrics.status == QueueStatus.COMPLETE
        assert metrics.end_time is not None
        assert metrics.wait_time_ms > 0

    def test_metrics_timing(self):
        """Test metrics timing calculation."""
        metrics = QueueMetrics(point_id="p1")
        time.sleep(0.1)  # 100ms delay
        metrics.complete(QueueStatus.COMPLETE)

        assert metrics.wait_time_ms >= 100


class TestQueueStatus:
    """Tests for QueueStatus enum."""

    def test_all_status_values(self):
        """Test all queue status values exist."""
        assert QueueStatus.WAITING.value == "waiting"
        assert QueueStatus.COMPLETE.value == "complete"
        assert QueueStatus.SOFT_DEGRADED.value == "soft_degraded"
        assert QueueStatus.HARD_DEGRADED.value == "hard_degraded"
        assert QueueStatus.FAILED.value == "failed"


class TestSmartAgentQueue:
    """Tests for SmartAgentQueue."""

    @pytest.fixture
    def queue(self):
        """Create a queue with short timeouts for testing."""
        queue = SmartAgentQueue("test_point")
        # Use very short timeouts for fast tests
        SmartAgentQueue.SOFT_TIMEOUT_SECONDS = 0.3
        SmartAgentQueue.HARD_TIMEOUT_SECONDS = 0.5
        SmartAgentQueue.EXPECTED_AGENTS = 3
        SmartAgentQueue.MIN_REQUIRED_FOR_SOFT = 2
        SmartAgentQueue.MIN_REQUIRED_FOR_HARD = 1
        return queue

    @pytest.fixture
    def sample_result(self):
        """Create sample content result."""
        return ContentResult(
            point_id="test_point",
            content_type=ContentType.VIDEO,
            title="Test Video",
            source="YouTube",
            relevance_score=8.0,
        )

    def test_queue_initialization(self, queue):
        """Test queue is properly initialized."""
        assert queue.point_id == "test_point"
        assert queue._results == {}
        assert queue._failures == {}

    def test_submit_success(self, queue, sample_result):
        """Test submitting successful result."""
        queue.submit_success("video", sample_result)

        assert "video" in queue._results
        assert queue._results["video"] == sample_result
        assert "video" in queue._metrics.agents_succeeded
        assert queue._metrics.agents_received == 1

    def test_submit_failure(self, queue):
        """Test submitting failure."""
        queue.submit_failure("video", "API timeout")

        assert "video" in queue._failures
        assert queue._failures["video"] == "API timeout"
        assert "video" in queue._metrics.agents_failed
        assert queue._metrics.agents_received == 1

    def test_all_agents_succeed(self, queue, sample_result):
        """Test when all agents succeed."""

        def submit_results():
            time.sleep(0.05)
            queue.submit_success("video", sample_result)
            queue.submit_success("music", sample_result)
            queue.submit_success("text", sample_result)

        thread = threading.Thread(target=submit_results)
        thread.start()

        results, metrics = queue.wait_for_results()
        thread.join()

        assert len(results) == 3
        assert metrics.status == QueueStatus.COMPLETE

    def test_two_agents_succeed(self, queue, sample_result):
        """Test when only two agents succeed."""

        def submit_results():
            time.sleep(0.05)
            queue.submit_success("video", sample_result)
            queue.submit_success("music", sample_result)
            queue.submit_failure("text", "Failed")

        thread = threading.Thread(target=submit_results)
        thread.start()

        results, metrics = queue.wait_for_results()
        thread.join()

        assert len(results) == 2
        assert metrics.status == QueueStatus.SOFT_DEGRADED

    def test_one_agent_succeeds(self, queue, sample_result):
        """Test when only one agent succeeds."""

        def submit_results():
            time.sleep(0.05)
            queue.submit_success("video", sample_result)
            queue.submit_failure("music", "Failed")
            queue.submit_failure("text", "Failed")

        thread = threading.Thread(target=submit_results)
        thread.start()

        results, metrics = queue.wait_for_results()
        thread.join()

        assert len(results) == 1
        assert metrics.status == QueueStatus.HARD_DEGRADED

    def test_all_agents_fail(self, queue):
        """Test when all agents fail."""

        def submit_results():
            time.sleep(0.05)
            queue.submit_failure("video", "Failed")
            queue.submit_failure("music", "Failed")
            queue.submit_failure("text", "Failed")

        thread = threading.Thread(target=submit_results)
        thread.start()

        with pytest.raises(NoResultsError):
            queue.wait_for_results()

        thread.join()

    def test_soft_timeout_with_two(self, queue, sample_result):
        """Test soft timeout triggers with 2/3 agents."""

        def submit_slow():
            time.sleep(0.05)
            queue.submit_success("video", sample_result)
            queue.submit_success("music", sample_result)
            # Third agent is slow (won't arrive before soft timeout)

        thread = threading.Thread(target=submit_slow)
        thread.start()

        results, metrics = queue.wait_for_results()
        thread.join()

        assert len(results) == 2
        assert metrics.status == QueueStatus.SOFT_DEGRADED

    def test_hard_timeout_with_one(self, queue, sample_result):
        """Test hard timeout triggers with 1/3 agents."""

        def submit_very_slow():
            time.sleep(0.05)
            queue.submit_success("video", sample_result)
            # Other agents are too slow

        thread = threading.Thread(target=submit_very_slow)
        thread.start()

        results, metrics = queue.wait_for_results()
        thread.join()

        assert len(results) == 1
        assert metrics.status == QueueStatus.HARD_DEGRADED

    def test_hard_timeout_no_results(self, queue):
        """Test hard timeout with no results raises error."""
        # No submissions - should timeout
        with pytest.raises(NoResultsError):
            queue.wait_for_results()

    def test_get_missing_agents(self, queue, sample_result):
        """Test identifying missing agents."""
        queue.submit_success("video", sample_result)

        missing = queue._get_missing_agents()
        assert "video" not in missing
        assert "music" in missing
        assert "text" in missing

    def test_metrics_property(self, queue):
        """Test accessing metrics property."""
        metrics = queue.metrics
        assert metrics.point_id == "test_point"
        assert isinstance(metrics, QueueMetrics)


class TestQueueManagerSingleton:
    """Tests for QueueManager singleton."""

    def test_singleton_pattern(self):
        """Test that QueueManager is a singleton."""
        manager1 = QueueManager()
        manager2 = QueueManager()
        assert manager1 is manager2

    def test_get_or_create_queue(self):
        """Test getting or creating queues."""
        manager = QueueManager()
        # Clear any existing state
        manager._queues.clear()
        manager._completed_metrics.clear()

        queue1 = manager.get_or_create_queue("point_1")
        queue2 = manager.get_or_create_queue("point_1")
        queue3 = manager.get_or_create_queue("point_2")

        assert queue1 is queue2  # Same queue for same point
        assert queue1 is not queue3  # Different queue for different point

    def test_complete_queue(self):
        """Test completing a queue."""
        manager = QueueManager()
        manager._queues.clear()
        manager._completed_metrics.clear()

        manager.get_or_create_queue("point_test")
        metrics = QueueMetrics(point_id="point_test")
        metrics.complete(QueueStatus.COMPLETE)

        manager.complete_queue("point_test", metrics)

        assert "point_test" not in manager._queues
        assert len(manager._completed_metrics) == 1

    def test_get_stats_empty(self):
        """Test stats with no completed queues."""
        manager = QueueManager()
        manager._completed_metrics.clear()

        stats = manager.get_stats()
        assert stats["total"] == 0

    def test_get_stats_with_data(self):
        """Test stats with completed queues."""
        manager = QueueManager()
        manager._completed_metrics.clear()

        # Add some completed metrics
        m1 = QueueMetrics(point_id="p1")
        m1.status = QueueStatus.COMPLETE
        m1.wait_time_ms = 100

        m2 = QueueMetrics(point_id="p2")
        m2.status = QueueStatus.SOFT_DEGRADED
        m2.wait_time_ms = 200

        m3 = QueueMetrics(point_id="p3")
        m3.status = QueueStatus.FAILED
        m3.wait_time_ms = 300

        manager._completed_metrics = [m1, m2, m3]

        stats = manager.get_stats()
        assert stats["total"] == 3
        assert stats["complete"] == 1
        assert stats["soft_degraded"] == 1
        assert stats["failed"] == 1
        assert stats["avg_wait_ms"] == 200


class TestSmartQueueConcurrency:
    """Concurrency tests for SmartAgentQueue."""

    def test_concurrent_submissions(self):
        """Test concurrent agent submissions."""
        SmartAgentQueue.SOFT_TIMEOUT_SECONDS = 2.0
        SmartAgentQueue.HARD_TIMEOUT_SECONDS = 4.0
        queue = SmartAgentQueue("concurrent_test")

        results_collected = []
        lock = threading.Lock()

        def submit_agent(agent_type):
            # Use fixed small delays
            time.sleep(0.1)
            result = ContentResult(
                content_type=ContentType.VIDEO,
                title=f"{agent_type} result",
                source="Test",
            )
            queue.submit_success(agent_type, result)
            with lock:
                results_collected.append(agent_type)

        threads = [
            threading.Thread(target=submit_agent, args=("video",)),
            threading.Thread(target=submit_agent, args=("music",)),
            threading.Thread(target=submit_agent, args=("text",)),
        ]

        for t in threads:
            t.start()

        results, metrics = queue.wait_for_results()

        for t in threads:
            t.join()

        assert len(results) == 3
        assert metrics.status == QueueStatus.COMPLETE

    def test_race_condition_submit_and_wait(self):
        """Test race condition between submit and wait."""
        SmartAgentQueue.SOFT_TIMEOUT_SECONDS = 1.0
        SmartAgentQueue.HARD_TIMEOUT_SECONDS = 2.0
        queue = SmartAgentQueue("race_test")

        def submit_delayed():
            time.sleep(0.2)
            result = ContentResult(
                content_type=ContentType.VIDEO, title="Delayed result", source="Test"
            )
            queue.submit_success("video", result)
            queue.submit_success("music", result)
            queue.submit_success("text", result)

        thread = threading.Thread(target=submit_delayed)
        thread.start()

        results, metrics = queue.wait_for_results()
        thread.join()

        assert len(results) == 3


class TestSmartQueueEdgeCases:
    """Edge case tests for SmartAgentQueue."""

    def test_duplicate_agent_submission(self):
        """Test submitting from same agent twice."""
        SmartAgentQueue.SOFT_TIMEOUT_SECONDS = 0.3
        SmartAgentQueue.HARD_TIMEOUT_SECONDS = 0.5
        queue = SmartAgentQueue("dup_test")

        result1 = ContentResult(
            content_type=ContentType.VIDEO, title="First submission", source="Test"
        )
        result2 = ContentResult(
            content_type=ContentType.VIDEO, title="Second submission", source="Test"
        )

        queue.submit_success("video", result1)
        queue.submit_success("video", result2)  # Duplicate
        queue.submit_success("music", result1)
        queue.submit_success("text", result1)

        results, metrics = queue.wait_for_results()

        # Second submission overwrites first
        assert len(queue._results) == 3
        assert queue._results["video"].title == "Second submission"

    def test_mixed_success_and_failure_same_agent(self):
        """Test agent reporting both success and failure."""
        SmartAgentQueue.SOFT_TIMEOUT_SECONDS = 0.3
        SmartAgentQueue.HARD_TIMEOUT_SECONDS = 0.5
        queue = SmartAgentQueue("mixed_test")

        result = ContentResult(
            content_type=ContentType.VIDEO, title="Video result", source="Test"
        )

        # Submit success first, then failure for same agent
        queue.submit_success("video", result)
        queue.submit_failure("video", "Late failure")

        # Both should be recorded separately
        assert "video" in queue._results
        assert "video" in queue._failures
