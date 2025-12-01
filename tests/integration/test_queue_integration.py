"""
Integration tests for queue-based synchronization.

Test Coverage:
- SmartAgentQueue with multiple agents
- QueueManager coordination
- End-to-end queue processing
- Graceful degradation scenarios
"""

import threading
import time

import pytest

from src.core.smart_queue import (
    QueueManager,
    QueueStatus,
    SmartAgentQueue,
)
from src.models.content import ContentResult, ContentType
from src.models.route import RoutePoint


class TestQueueWithAgents:
    """Integration tests for queue with simulated agents."""

    @pytest.fixture(autouse=True)
    def setup_timeouts(self):
        """Set up fast timeouts for testing."""
        SmartAgentQueue.SOFT_TIMEOUT_SECONDS = 0.5
        SmartAgentQueue.HARD_TIMEOUT_SECONDS = 1.0
        SmartAgentQueue.EXPECTED_AGENTS = 3
        SmartAgentQueue.MIN_REQUIRED_FOR_SOFT = 2
        SmartAgentQueue.MIN_REQUIRED_FOR_HARD = 1
        yield
        # Reset after test
        SmartAgentQueue.SOFT_TIMEOUT_SECONDS = 15.0
        SmartAgentQueue.HARD_TIMEOUT_SECONDS = 30.0

    def test_simulated_parallel_agents(self):
        """Test queue with simulated parallel agent submissions."""
        queue = SmartAgentQueue("integration_test_1")

        def video_agent():
            time.sleep(0.05)
            result = ContentResult(
                point_id="integration_test_1",
                content_type=ContentType.VIDEO,
                title="Video Result",
                source="YouTube",
                relevance_score=8.0,
            )
            queue.submit_success("video", result)

        def music_agent():
            time.sleep(0.1)
            result = ContentResult(
                point_id="integration_test_1",
                content_type=ContentType.MUSIC,
                title="Music Result",
                source="Spotify",
                relevance_score=7.5,
            )
            queue.submit_success("music", result)

        def text_agent():
            time.sleep(0.15)
            result = ContentResult(
                point_id="integration_test_1",
                content_type=ContentType.TEXT,
                title="Text Result",
                source="Wikipedia",
                relevance_score=9.0,
            )
            queue.submit_success("text", result)

        # Start all agents in parallel
        threads = [
            threading.Thread(target=video_agent),
            threading.Thread(target=music_agent),
            threading.Thread(target=text_agent),
        ]
        for t in threads:
            t.start()

        # Wait for results
        results, metrics = queue.wait_for_results()

        for t in threads:
            t.join()

        # Verify results
        assert len(results) == 3
        assert metrics.status == QueueStatus.COMPLETE

        # Check all content types present
        content_types = {r.content_type for r in results}
        assert ContentType.VIDEO in content_types
        assert ContentType.MUSIC in content_types
        assert ContentType.TEXT in content_types

    def test_partial_agent_failure(self):
        """Test queue handles partial agent failure."""
        queue = SmartAgentQueue("partial_fail_test")

        def successful_agent(agent_type, content_type, delay):
            time.sleep(delay)
            result = ContentResult(
                point_id="partial_fail_test",
                content_type=content_type,
                title=f"{agent_type} Result",
                source="Test",
            )
            queue.submit_success(agent_type, result)

        def failing_agent():
            time.sleep(0.1)
            queue.submit_failure("text", "API Error")

        threads = [
            threading.Thread(
                target=successful_agent, args=("video", ContentType.VIDEO, 0.05)
            ),
            threading.Thread(
                target=successful_agent, args=("music", ContentType.MUSIC, 0.08)
            ),
            threading.Thread(target=failing_agent),
        ]
        for t in threads:
            t.start()

        results, metrics = queue.wait_for_results()

        for t in threads:
            t.join()

        # Should have 2 successful results
        assert len(results) == 2
        assert metrics.status == QueueStatus.SOFT_DEGRADED
        assert "text" in metrics.agents_failed

    def test_slow_agent_soft_timeout(self):
        """Test queue proceeds at soft timeout with 2 results."""
        queue = SmartAgentQueue("slow_agent_test", soft_timeout=1.0, hard_timeout=2.0)

        def fast_agent(agent_type, content_type, delay):
            time.sleep(delay)
            result = ContentResult(
                point_id="slow_agent_test",
                content_type=content_type,
                title=f"{agent_type} Result",
                source="Test",
            )
            queue.submit_success(agent_type, result)

        def very_slow_agent():
            time.sleep(5.0)  # Way longer than timeout
            # This won't complete before soft timeout

        threads = [
            threading.Thread(
                target=fast_agent, args=("video", ContentType.VIDEO, 0.05)
            ),
            threading.Thread(target=fast_agent, args=("music", ContentType.MUSIC, 0.1)),
            threading.Thread(target=very_slow_agent, daemon=True),
        ]
        for t in threads:
            t.start()

        start = time.time()
        results, metrics = queue.wait_for_results()
        elapsed = time.time() - start

        # Should timeout after soft timeout
        assert elapsed < 1.5  # Should not wait for hard timeout
        assert len(results) == 2
        assert metrics.status == QueueStatus.SOFT_DEGRADED


class TestQueueManagerIntegration:
    """Integration tests for QueueManager."""

    def test_multiple_queues_concurrent(self):
        """Test managing multiple queues concurrently."""
        SmartAgentQueue.SOFT_TIMEOUT_SECONDS = 0.3
        SmartAgentQueue.HARD_TIMEOUT_SECONDS = 0.5

        manager = QueueManager()
        manager._queues.clear()
        manager._completed_metrics.clear()

        results = {}
        lock = threading.Lock()

        def process_point(point_id):
            queue = manager.get_or_create_queue(point_id)

            # Simulate agent submissions
            for agent_type in ["video", "music", "text"]:
                result = ContentResult(
                    point_id=point_id,
                    content_type=ContentType.VIDEO,
                    title=f"{agent_type} for {point_id}",
                    source="Test",
                )
                queue.submit_success(agent_type, result)

            point_results, metrics = queue.wait_for_results()
            manager.complete_queue(point_id, metrics)

            with lock:
                results[point_id] = point_results

        # Process multiple points concurrently
        threads = [
            threading.Thread(target=process_point, args=(f"point_{i}",))
            for i in range(5)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All points should have results
        assert len(results) == 5
        for _point_id, point_results in results.items():
            assert len(point_results) == 3

    def test_queue_manager_stats(self):
        """Test QueueManager aggregate statistics."""
        SmartAgentQueue.SOFT_TIMEOUT_SECONDS = 0.3
        SmartAgentQueue.HARD_TIMEOUT_SECONDS = 0.5

        manager = QueueManager()
        manager._queues.clear()
        manager._completed_metrics.clear()

        # Process some queues with different outcomes
        def process_complete():
            queue = manager.get_or_create_queue("complete_queue")
            for agent in ["video", "music", "text"]:
                result = ContentResult(
                    content_type=ContentType.VIDEO, title="Test", source="Test"
                )
                queue.submit_success(agent, result)
            _, metrics = queue.wait_for_results()
            manager.complete_queue("complete_queue", metrics)

        def process_degraded():
            queue = manager.get_or_create_queue("degraded_queue")
            for agent in ["video", "music"]:
                result = ContentResult(
                    content_type=ContentType.VIDEO, title="Test", source="Test"
                )
                queue.submit_success(agent, result)
            queue.submit_failure("text", "Error")
            _, metrics = queue.wait_for_results()
            manager.complete_queue("degraded_queue", metrics)

        process_complete()
        process_degraded()

        stats = manager.get_stats()
        assert stats["total"] == 2
        assert stats["complete"] == 1
        assert stats["soft_degraded"] == 1


class TestEndToEndQueueFlow:
    """End-to-end integration tests for queue flow."""

    def test_full_point_processing(self):
        """Test complete point processing flow."""
        SmartAgentQueue.SOFT_TIMEOUT_SECONDS = 1.0
        SmartAgentQueue.HARD_TIMEOUT_SECONDS = 2.0

        point = RoutePoint(
            id="e2e_test",
            index=0,
            address="Tel Aviv, Israel",
            location_name="Rabin Square",
            latitude=32.0853,
            longitude=34.7818,
        )

        queue = SmartAgentQueue(point.id)

        # Simulate agent processing
        agent_results = [
            ("video", ContentType.VIDEO, "Tel Aviv City Tour", 8.5),
            ("music", ContentType.MUSIC, "Tel Aviv Song", 7.0),
            ("text", ContentType.TEXT, "History of Tel Aviv", 9.0),
        ]

        def agent_worker(agent_type, content_type, title, score):
            time.sleep(0.05)  # Simulate work
            result = ContentResult(
                point_id=point.id,
                content_type=content_type,
                title=title,
                source="Test",
                relevance_score=score,
            )
            queue.submit_success(agent_type, result)

        threads = [
            threading.Thread(target=agent_worker, args=args) for args in agent_results
        ]

        for t in threads:
            t.start()

        results, metrics = queue.wait_for_results()

        for t in threads:
            t.join()

        # Verify complete processing
        assert len(results) == 3
        assert metrics.status == QueueStatus.COMPLETE
        assert metrics.agents_received == 3
        assert len(metrics.agents_succeeded) == 3

        # Verify results have correct data
        titles = {r.title for r in results}
        assert "Tel Aviv City Tour" in titles
        assert "Tel Aviv Song" in titles
        assert "History of Tel Aviv" in titles
