"""
Unit tests for Decision and AgentTask models.

Test Coverage:
- JudgeDecision creation and validation
- AgentTask lifecycle (pending -> running -> completed/failed)
- Duration calculation
- Edge cases: empty candidates, missing results
"""
from datetime import datetime

import pytest

from src.models.content import AgentStatus, ContentResult, ContentType
from src.models.decision import AgentTask, JudgeDecision


class TestJudgeDecision:
    """Tests for JudgeDecision model."""

    @pytest.fixture
    def sample_content_results(self):
        """Create sample content results for testing."""
        return [
            ContentResult(
                point_id="p1",
                content_type=ContentType.VIDEO,
                title="Test Video",
                source="YouTube",
                relevance_score=8.5
            ),
            ContentResult(
                point_id="p1",
                content_type=ContentType.MUSIC,
                title="Test Song",
                source="Spotify",
                relevance_score=7.0
            ),
            ContentResult(
                point_id="p1",
                content_type=ContentType.TEXT,
                title="Test Article",
                source="Wikipedia",
                relevance_score=9.0
            ),
        ]

    def test_create_judge_decision(self, sample_content_results):
        """Test creating a judge decision."""
        decision = JudgeDecision(
            point_id="point_1",
            selected_content=sample_content_results[2],  # Text with highest score
            all_candidates=sample_content_results,
            reasoning="Text content provides the most educational value"
        )
        assert decision.point_id == "point_1"
        assert decision.selected_content.title == "Test Article"
        assert len(decision.all_candidates) == 3
        assert decision.reasoning == "Text content provides the most educational value"
        assert decision.confidence == 1.0  # Default

    def test_judge_decision_with_scores(self, sample_content_results):
        """Test judge decision with explicit scores."""
        decision = JudgeDecision(
            point_id="p1",
            selected_content=sample_content_results[0],
            all_candidates=sample_content_results,
            reasoning="Video is most engaging",
            scores={
                ContentType.VIDEO: 9.5,
                ContentType.MUSIC: 7.5,
                ContentType.TEXT: 8.0
            },
            confidence=0.95
        )
        assert decision.scores[ContentType.VIDEO] == 9.5
        assert decision.scores[ContentType.MUSIC] == 7.5
        assert decision.confidence == 0.95

    def test_judge_decision_confidence_boundaries(self, sample_content_results):
        """Test confidence must be between 0 and 1."""
        # Valid boundaries
        decision_low = JudgeDecision(
            point_id="p1",
            selected_content=sample_content_results[0],
            all_candidates=sample_content_results,
            reasoning="Test",
            confidence=0.0
        )
        assert decision_low.confidence == 0.0

        decision_high = JudgeDecision(
            point_id="p1",
            selected_content=sample_content_results[0],
            all_candidates=sample_content_results,
            reasoning="Test",
            confidence=1.0
        )
        assert decision_high.confidence == 1.0

    def test_judge_decision_invalid_confidence(self, sample_content_results):
        """Test invalid confidence values."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            JudgeDecision(
                point_id="p1",
                selected_content=sample_content_results[0],
                all_candidates=sample_content_results,
                reasoning="Test",
                confidence=1.5
            )

        with pytest.raises(ValidationError):
            JudgeDecision(
                point_id="p1",
                selected_content=sample_content_results[0],
                all_candidates=sample_content_results,
                reasoning="Test",
                confidence=-0.1
            )

    def test_judge_decision_single_candidate(self, sample_content_results):
        """Test decision with only one candidate."""
        decision = JudgeDecision(
            point_id="p1",
            selected_content=sample_content_results[0],
            all_candidates=[sample_content_results[0]],
            reasoning="Only one option available"
        )
        assert len(decision.all_candidates) == 1
        assert decision.selected_content == decision.all_candidates[0]

    def test_judge_decision_decided_at_auto(self, sample_content_results):
        """Test decided_at is automatically set."""
        before = datetime.now()
        decision = JudgeDecision(
            point_id="p1",
            selected_content=sample_content_results[0],
            all_candidates=sample_content_results,
            reasoning="Test"
        )
        after = datetime.now()
        assert before <= decision.decided_at <= after

    def test_judge_decision_empty_scores(self, sample_content_results):
        """Test decision with empty scores dict."""
        decision = JudgeDecision(
            point_id="p1",
            selected_content=sample_content_results[0],
            all_candidates=sample_content_results,
            reasoning="Test"
        )
        assert decision.scores == {}

    def test_judge_decision_json_serialization(self, sample_content_results):
        """Test decision serialization."""
        decision = JudgeDecision(
            point_id="p1",
            selected_content=sample_content_results[0],
            all_candidates=sample_content_results,
            reasoning="Best choice",
            confidence=0.9
        )
        json_dict = decision.model_dump()
        assert json_dict["point_id"] == "p1"
        assert json_dict["reasoning"] == "Best choice"
        assert json_dict["confidence"] == 0.9
        assert len(json_dict["all_candidates"]) == 3


class TestAgentTask:
    """Tests for AgentTask model."""

    def test_create_minimal_agent_task(self):
        """Test creating agent task with minimum fields."""
        task = AgentTask(
            point_id="p1",
            agent_type="video",
            location="Jerusalem",
            address="Old City, Jerusalem"
        )
        assert task.point_id == "p1"
        assert task.agent_type == "video"
        assert task.status == AgentStatus.PENDING  # Default
        assert task.id  # Auto-generated
        assert len(task.id) == 8

    def test_agent_task_lifecycle_success(self):
        """Test successful task lifecycle."""
        task = AgentTask(
            point_id="p1",
            agent_type="music",
            location="Tel Aviv",
            address="Dizengoff Square"
        )
        assert task.status == AgentStatus.PENDING

        # Start task
        task.status = AgentStatus.RUNNING
        task.started_at = datetime.now()
        assert task.status == AgentStatus.RUNNING

        # Complete task
        task.status = AgentStatus.COMPLETED
        task.completed_at = datetime.now()
        task.result = ContentResult(
            content_type=ContentType.MUSIC,
            title="Tel Aviv Song",
            source="Spotify"
        )
        assert task.status == AgentStatus.COMPLETED
        assert task.result is not None

    def test_agent_task_lifecycle_failure(self):
        """Test failed task lifecycle."""
        task = AgentTask(
            point_id="p1",
            agent_type="text",
            location="Haifa",
            address="Bahai Gardens"
        )

        task.status = AgentStatus.RUNNING
        task.started_at = datetime.now()

        task.status = AgentStatus.FAILED
        task.completed_at = datetime.now()
        task.error = "API rate limit exceeded"

        assert task.status == AgentStatus.FAILED
        assert task.error == "API rate limit exceeded"
        assert task.result is None

    def test_agent_task_timeout(self):
        """Test timeout task status."""
        task = AgentTask(
            point_id="p1",
            agent_type="video",
            location="Test",
            address="Test Address"
        )

        task.status = AgentStatus.RUNNING
        task.started_at = datetime.now()

        task.status = AgentStatus.TIMEOUT
        task.completed_at = datetime.now()
        task.error = "Operation timed out after 30 seconds"

        assert task.status == AgentStatus.TIMEOUT

    def test_duration_seconds_property(self):
        """Test duration calculation when completed."""
        task = AgentTask(
            point_id="p1",
            agent_type="video",
            location="Test",
            address="Test Address"
        )
        task.started_at = datetime(2024, 1, 1, 12, 0, 0)
        task.completed_at = datetime(2024, 1, 1, 12, 0, 5)

        assert task.duration_seconds == 5.0

    def test_duration_seconds_not_completed(self):
        """Test duration is None when not completed."""
        task = AgentTask(
            point_id="p1",
            agent_type="video",
            location="Test",
            address="Test Address"
        )
        assert task.duration_seconds is None

        task.started_at = datetime.now()
        assert task.duration_seconds is None  # Still no completed_at

    def test_duration_seconds_long_task(self):
        """Test duration for long-running tasks."""
        task = AgentTask(
            point_id="p1",
            agent_type="video",
            location="Test",
            address="Test Address"
        )
        task.started_at = datetime(2024, 1, 1, 12, 0, 0)
        task.completed_at = datetime(2024, 1, 1, 12, 5, 30)  # 5 min 30 sec

        assert task.duration_seconds == 330.0

    def test_agent_task_thread_name(self):
        """Test thread name tracking."""
        task = AgentTask(
            point_id="p1",
            agent_type="video",
            location="Test",
            address="Test",
            thread_name="Agent-P0-0"
        )
        assert task.thread_name == "Agent-P0-0"

    def test_agent_task_all_agent_types(self):
        """Test tasks for all agent types."""
        for agent_type in ["video", "music", "text", "judge"]:
            task = AgentTask(
                point_id="p1",
                agent_type=agent_type,
                location="Test",
                address="Test Address"
            )
            assert task.agent_type == agent_type

    def test_agent_task_json_serialization(self):
        """Test task serialization."""
        task = AgentTask(
            point_id="p1",
            agent_type="video",
            location="Jerusalem",
            address="Old City",
            status=AgentStatus.COMPLETED
        )
        json_dict = task.model_dump()
        assert json_dict["point_id"] == "p1"
        assert json_dict["agent_type"] == "video"
        assert json_dict["status"] == "completed"


class TestDecisionEdgeCases:
    """Edge case tests for decision models."""

    def test_decision_with_empty_reasoning(self):
        """Test decision with empty reasoning."""
        content = ContentResult(
            content_type=ContentType.TEXT,
            title="Test",
            source="Wikipedia"
        )
        decision = JudgeDecision(
            point_id="p1",
            selected_content=content,
            all_candidates=[content],
            reasoning=""
        )
        assert decision.reasoning == ""

    def test_decision_with_very_long_reasoning(self):
        """Test decision with very long reasoning."""
        content = ContentResult(
            content_type=ContentType.TEXT,
            title="Test",
            source="Wikipedia"
        )
        long_reasoning = "A" * 10000
        decision = JudgeDecision(
            point_id="p1",
            selected_content=content,
            all_candidates=[content],
            reasoning=long_reasoning
        )
        assert len(decision.reasoning) == 10000

    def test_task_with_special_characters(self):
        """Test task with special characters in fields."""
        task = AgentTask(
            point_id="p1-2024/01/01",
            agent_type="video",
            location="ירושלים - Jerusalem",
            address="Old City, 🏛️ Historical District"
        )
        assert "ירושלים" in task.location
        assert "🏛️" in task.address

    def test_decision_many_candidates(self):
        """Test decision with many candidates."""
        candidates = [
            ContentResult(
                point_id="p1",
                content_type=ContentType.VIDEO,
                title=f"Video {i}",
                source="YouTube",
                relevance_score=float(i % 10)
            )
            for i in range(100)
        ]
        decision = JudgeDecision(
            point_id="p1",
            selected_content=candidates[50],
            all_candidates=candidates,
            reasoning="Selected middle option"
        )
        assert len(decision.all_candidates) == 100

