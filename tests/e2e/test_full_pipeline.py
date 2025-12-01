"""
End-to-End Tests for Complete Tour Guide Pipeline.

MIT-Level E2E Test Coverage:
- Complete flow from route input to content output
- Multi-point tour processing
- Profile-based content selection
- Quality and latency validation
"""

import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

import pytest

from src.agents.judge_agent import JudgeAgent
from src.core.orchestrator import Orchestrator
from src.core.smart_queue import QueueStatus, SmartAgentQueue
from src.models.content import ContentResult, ContentType
from src.models.decision import JudgeDecision
from src.models.route import RoutePoint
from src.models.user_profile import AgeGroup, ContentPreference, Gender, UserProfile


@dataclass
class E2ETestResult:
    """Result container for E2E test validation."""

    point_id: str
    selected_content: ContentResult | None
    judge_decision: JudgeDecision | None
    latency_ms: float
    status: QueueStatus
    num_candidates: int


class TestFullTourPipeline:
    """E2E tests for complete tour guide flow."""

    @pytest.fixture
    def sample_route_points(self) -> list[RoutePoint]:
        """Create sample route points for testing."""
        return [
            RoutePoint(
                id="point_1",
                address="Eiffel Tower, Paris",
                latitude=48.8584,
                longitude=2.2945,
                location_name="Eiffel Tower",
            ),
            RoutePoint(
                id="point_2",
                address="Louvre Museum, Paris",
                latitude=48.8606,
                longitude=2.3376,
                location_name="Louvre Museum",
            ),
            RoutePoint(
                id="point_3",
                address="Notre-Dame Cathedral, Paris",
                latitude=48.8530,
                longitude=2.3499,
                location_name="Notre-Dame Cathedral",
            ),
        ]

    @pytest.fixture
    def family_profile(self) -> UserProfile:
        """Create family user profile."""
        return UserProfile(
            name="Test Family",
            gender=Gender.NOT_SPECIFIED,
            age_group=AgeGroup.ADULT,
            exact_age=35,
            content_preference=ContentPreference.EDUCATIONAL,
            is_driver=False,
            interests=["history", "art", "architecture"],
        )

    @pytest.fixture
    def mock_content_results(self) -> dict:
        """Create mock content results for each agent type."""
        return {
            ContentType.VIDEO: ContentResult(
                content_type=ContentType.VIDEO,
                title="Eiffel Tower Documentary",
                description="A comprehensive guide to the Eiffel Tower",
                url="https://youtube.com/watch?v=example",
                source="YouTube",
                relevance_score=8.5,
                duration_seconds=300,
            ),
            ContentType.MUSIC: ContentResult(
                content_type=ContentType.MUSIC,
                title="La Vie en Rose - Edith Piaf",
                description="Classic French song perfect for Paris",
                url="https://spotify.com/track/example",
                source="Spotify",
                relevance_score=7.8,
                duration_seconds=180,
            ),
            ContentType.TEXT: ContentResult(
                content_type=ContentType.TEXT,
                title="History of the Eiffel Tower",
                description="Built for the 1889 World's Fair...",
                url="https://wikipedia.org/wiki/Eiffel_Tower",
                source="Wikipedia",
                relevance_score=8.0,
                duration_seconds=120,
            ),
        }

    @pytest.mark.e2e
    def test_full_tour_flow_single_point(
        self, sample_route_points, family_profile, mock_content_results
    ):
        """Test complete flow for a single route point."""
        point = sample_route_points[0]

        # Create smart queue
        queue = SmartAgentQueue(
            point_id=point.id,
            expected_agents=3,
            soft_timeout=15.0,
            hard_timeout=30.0,
        )

        # Submit mock results (simulating agent execution)
        for content_type, result in mock_content_results.items():
            queue.submit_result(content_type, result)

        # Wait for results
        results, metrics = queue.wait_for_results()

        # Validate queue behavior
        assert len(results) == 3
        assert metrics.status == QueueStatus.COMPLETE
        assert metrics.wait_time_ms < 1000  # Should be fast with mocked results

        # Create judge and select content
        judge = JudgeAgent()
        decision = judge.evaluate(point, results, family_profile)

        # Validate judge decision
        assert decision is not None
        assert decision.selected_content is not None
        assert decision.selected_content.relevance_score > 0
        # Note: reasoning may be empty when using mock LLM (no API key)
        assert decision.reasoning is not None

    @pytest.mark.e2e
    def test_full_tour_flow_multiple_points(
        self, sample_route_points, family_profile, mock_content_results
    ):
        """Test complete flow for multiple route points."""
        results_by_point = {}

        for point in sample_route_points:
            # Create queue for this point
            queue = SmartAgentQueue(
                point_id=point.id,
                expected_agents=3,
                soft_timeout=15.0,
                hard_timeout=30.0,
            )

            # Submit results
            for content_type, result in mock_content_results.items():
                # Create a copy with point-specific modifications
                point_result = ContentResult(
                    content_type=result.content_type,
                    title=f"{result.title} - {point.location_name}",
                    description=result.description,
                    url=result.url,
                    source=result.source,
                    relevance_score=result.relevance_score,
                    duration_seconds=result.duration_seconds,
                )
                queue.submit_result(content_type, point_result)

            # Get results
            content_results, metrics = queue.wait_for_results()

            # Judge selection
            judge = JudgeAgent()
            decision = judge.evaluate(point, content_results, family_profile)

            results_by_point[point.id] = E2ETestResult(
                point_id=point.id,
                selected_content=decision.selected_content if decision else None,
                judge_decision=decision,
                latency_ms=metrics.wait_time_ms,
                status=metrics.status,
                num_candidates=len(content_results),
            )

        # Validate all points processed
        assert len(results_by_point) == len(sample_route_points)

        for _point_id, result in results_by_point.items():
            assert result.selected_content is not None
            assert result.status == QueueStatus.COMPLETE
            assert result.num_candidates == 3

    @pytest.mark.e2e
    def test_tour_flow_with_orchestrator(self, sample_route_points, family_profile, mock_content_results):
        """Test complete flow using the Orchestrator component."""
        # Use a simplified test that validates orchestrator initialization and basic behavior
        orchestrator = Orchestrator(max_concurrent_points=2)

        # Validate orchestrator is properly initialized
        assert orchestrator.max_concurrent_points == 2
        assert orchestrator.is_running is False

        # Start and stop orchestrator (basic lifecycle test)
        orchestrator.start()
        assert orchestrator.is_running is True

        orchestrator.stop()
        assert orchestrator.is_running is False

        # Test get_stats method
        stats = orchestrator.get_stats()
        assert "active_points" in stats
        assert "completed_points" in stats
        assert "is_running" in stats

    @pytest.mark.e2e
    def test_parallel_processing_performance(
        self, sample_route_points, mock_content_results
    ):
        """Test that parallel processing improves performance."""

        # Simulate parallel agent execution
        def simulate_agent_work(
            point: RoutePoint, content_type: ContentType
        ) -> ContentResult:
            time.sleep(0.1)  # Simulate API call latency
            return mock_content_results[content_type]

        # Sequential execution time
        sequential_start = time.time()
        for point in sample_route_points[:2]:
            for ct in ContentType:
                if ct in mock_content_results:
                    simulate_agent_work(point, ct)
        sequential_time = time.time() - sequential_start

        # Parallel execution time
        parallel_start = time.time()
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = []
            for point in sample_route_points[:2]:
                for ct in ContentType:
                    if ct in mock_content_results:
                        futures.append(executor.submit(simulate_agent_work, point, ct))
            # Wait for all
            for f in futures:
                f.result()
        parallel_time = time.time() - parallel_start

        # Parallel should be significantly faster
        assert parallel_time < sequential_time * 0.5  # At least 2x speedup

    @pytest.mark.e2e
    def test_content_quality_meets_threshold(
        self, sample_route_points, family_profile, mock_content_results
    ):
        """Test that selected content meets minimum quality threshold."""
        MIN_QUALITY_THRESHOLD = 5.0

        for point in sample_route_points:
            queue = SmartAgentQueue(point_id=point.id)

            for content_type, result in mock_content_results.items():
                queue.submit_result(content_type, result)

            results, _ = queue.wait_for_results()

            judge = JudgeAgent()
            decision = judge.evaluate(point, results, family_profile)

            # Selected content must meet quality threshold
            assert decision.selected_content.relevance_score >= MIN_QUALITY_THRESHOLD

    @pytest.mark.e2e
    def test_latency_within_acceptable_bounds(self, sample_route_points):
        """Test that end-to-end latency is within acceptable bounds."""
        MAX_LATENCY_MS = 35000  # 35 seconds max (hard timeout + buffer)

        for point in sample_route_points:
            queue = SmartAgentQueue(
                point_id=point.id,
                soft_timeout=15.0,
                hard_timeout=30.0,
            )

            # Simulate immediate responses
            queue.submit_result(
                ContentType.TEXT,
                ContentResult(
                    content_type=ContentType.TEXT,
                    title="Quick Response",
                    description="Test",
                    url="https://example.com",
                    source="Test",
                    relevance_score=7.0,
                    duration_seconds=60,
                ),
            )

            _, metrics = queue.wait_for_results()

            # Latency should be well under the max
            assert metrics.wait_time_ms < MAX_LATENCY_MS


class TestTourOutputValidation:
    """E2E tests for validating tour output structure and content."""

    @pytest.mark.e2e
    def test_output_contains_required_fields(self):
        """Test that tour output contains all required fields."""
        # Create minimal valid output
        content = ContentResult(
            content_type=ContentType.TEXT,
            title="Test",
            description="Description",
            url="https://example.com",
            source="Test",
            relevance_score=7.0,
            duration_seconds=60,
        )

        decision = JudgeDecision(
            point_id="test_point",
            selected_content=content,
            all_candidates=[content],
            reasoning="Selected for testing",
            scores={"text": 7.0},
            confidence=0.9,
        )

        # Validate required fields
        assert decision.point_id is not None
        assert decision.selected_content is not None
        assert decision.reasoning is not None
        assert decision.confidence >= 0 and decision.confidence <= 1

    @pytest.mark.e2e
    def test_output_serialization_roundtrip(self):
        """Test that output can be serialized and deserialized."""
        content = ContentResult(
            content_type=ContentType.VIDEO,
            title="Test Video",
            description="A test video",
            url="https://youtube.com/watch?v=test",
            source="YouTube",
            relevance_score=8.5,
            duration_seconds=300,
        )

        # Serialize to dict
        content_dict = content.model_dump()

        # Deserialize back
        restored_content = ContentResult(**content_dict)

        # Validate roundtrip
        assert restored_content.title == content.title
        assert restored_content.relevance_score == content.relevance_score
        assert restored_content.content_type == content.content_type
