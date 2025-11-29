"""
Unit tests for the Collector module.

Tests cover:
- ResultCollector initialization
- Adding decisions
- Completion tracking
- Progress monitoring
- Output generation
- StreamingCollector functionality

MIT Level Testing - 85%+ Coverage Target
"""

import threading
from unittest.mock import Mock, patch

from src.models.content import ContentResult, ContentType
from src.models.decision import JudgeDecision
from src.models.route import Route


class TestResultCollector:
    """Tests for ResultCollector class."""

    def test_initialization(self, mock_route):
        """Test ResultCollector initialization."""
        with patch("src.core.collector.set_log_context", create=True):
            with patch("src.core.collector.log_collector_update", create=True):
                from src.core.collector import ResultCollector

                collector = ResultCollector(mock_route)

                assert collector.route == mock_route
                assert collector.decisions == {}
                assert collector.started_at is not None
                assert not collector._completion_event.is_set()

    def test_add_decision(self, mock_route, mock_judge_decision):
        """Test adding a decision."""
        with patch("src.core.collector.set_log_context", create=True):
            with patch("src.core.collector.log_collector_update", create=True):
                from src.core.collector import ResultCollector

                collector = ResultCollector(mock_route)

                # Modify decision to match route point
                mock_judge_decision.point_id = mock_route.points[0].id

                collector.add_decision(mock_judge_decision)

                assert mock_route.points[0].id in collector.decisions
                assert (
                    collector.decisions[mock_route.points[0].id] == mock_judge_decision
                )

    def test_completion_event_set_when_all_collected(self, mock_route):
        """Test completion event is set when all decisions collected."""
        with patch("src.core.collector.set_log_context", create=True):
            with patch("src.core.collector.log_collector_update", create=True):
                from src.core.collector import ResultCollector

                collector = ResultCollector(mock_route)

                # Add decisions for all points
                for point in mock_route.points:
                    decision = JudgeDecision(
                        point_id=point.id,
                        selected_content=ContentResult(
                            point_id=point.id,
                            content_type=ContentType.TEXT,
                            title="Test",
                            source="Test",
                        ),
                        all_candidates=[],
                        reasoning="Test",
                    )
                    collector.add_decision(decision)

                assert collector._completion_event.is_set()
                assert collector.is_complete()

    def test_get_decision(self, mock_route, mock_judge_decision):
        """Test retrieving a specific decision."""
        with patch("src.core.collector.set_log_context", create=True):
            with patch("src.core.collector.log_collector_update", create=True):
                from src.core.collector import ResultCollector

                collector = ResultCollector(mock_route)

                mock_judge_decision.point_id = "test_id"
                collector.decisions["test_id"] = mock_judge_decision

                result = collector.get_decision("test_id")
                assert result == mock_judge_decision

                # Non-existent decision
                result = collector.get_decision("non_existent")
                assert result is None

    def test_is_complete_false_initially(self, mock_route):
        """Test is_complete returns False initially."""
        with patch("src.core.collector.set_log_context", create=True):
            with patch("src.core.collector.log_collector_update", create=True):
                from src.core.collector import ResultCollector

                collector = ResultCollector(mock_route)
                assert not collector.is_complete()

    def test_wait_for_completion_timeout(self, mock_route):
        """Test wait_for_completion with timeout."""
        with patch("src.core.collector.set_log_context", create=True):
            with patch("src.core.collector.log_collector_update", create=True):
                from src.core.collector import ResultCollector

                collector = ResultCollector(mock_route)

                result = collector.wait_for_completion(timeout=0.1)
                assert result is False  # Timeout, not complete

    def test_wait_for_completion_success(self, mock_route):
        """Test wait_for_completion succeeds when complete."""
        with patch("src.core.collector.set_log_context", create=True):
            with patch("src.core.collector.log_collector_update", create=True):
                from src.core.collector import ResultCollector

                collector = ResultCollector(mock_route)

                def add_decisions():
                    for point in mock_route.points:
                        decision = JudgeDecision(
                            point_id=point.id,
                            selected_content=ContentResult(
                                point_id=point.id,
                                content_type=ContentType.TEXT,
                                title="Test",
                                source="Test",
                            ),
                            all_candidates=[],
                            reasoning="Test",
                        )
                        collector.add_decision(decision)

                # Add decisions in separate thread
                thread = threading.Thread(target=add_decisions)
                thread.start()

                result = collector.wait_for_completion(timeout=5.0)
                thread.join()

                assert result is True

    def test_get_progress(self, mock_route):
        """Test progress tracking."""
        with patch("src.core.collector.set_log_context", create=True):
            with patch("src.core.collector.log_collector_update", create=True):
                from src.core.collector import ResultCollector

                collector = ResultCollector(mock_route)

                progress = collector.get_progress()

                assert progress["collected"] == 0
                assert progress["total"] == len(mock_route.points)
                assert progress["percentage"] == 0
                assert progress["remaining"] == len(mock_route.points)

    def test_get_progress_partial(self, mock_route):
        """Test progress after partial collection."""
        with patch("src.core.collector.set_log_context", create=True):
            with patch("src.core.collector.log_collector_update", create=True):
                from src.core.collector import ResultCollector

                collector = ResultCollector(mock_route)

                # Add one decision
                decision = JudgeDecision(
                    point_id=mock_route.points[0].id,
                    selected_content=ContentResult(
                        point_id=mock_route.points[0].id,
                        content_type=ContentType.TEXT,
                        title="Test",
                        source="Test",
                    ),
                    all_candidates=[],
                    reasoning="Test",
                )
                collector.add_decision(decision)

                progress = collector.get_progress()

                assert progress["collected"] == 1
                assert progress["remaining"] == len(mock_route.points) - 1

    def test_get_ordered_decisions(self, mock_route):
        """Test decisions are returned in route order."""
        with patch("src.core.collector.set_log_context", create=True):
            with patch("src.core.collector.log_collector_update", create=True):
                from src.core.collector import ResultCollector

                collector = ResultCollector(mock_route)

                # Add decisions in reverse order
                for point in reversed(mock_route.points):
                    decision = JudgeDecision(
                        point_id=point.id,
                        selected_content=ContentResult(
                            point_id=point.id,
                            content_type=ContentType.TEXT,
                            title=f"Test {point.index}",
                            source="Test",
                        ),
                        all_candidates=[],
                        reasoning="Test",
                    )
                    collector.add_decision(decision)

                ordered = collector.get_ordered_decisions()

                # Should be in route order, not insertion order
                for i, decision in enumerate(ordered):
                    assert decision.point_id == mock_route.points[i].id

    def test_generate_output(self, mock_route):
        """Test output generation."""
        with patch("src.core.collector.set_log_context", create=True):
            with patch("src.core.collector.log_collector_update", create=True):
                from src.core.collector import ResultCollector

                collector = ResultCollector(mock_route)

                # Add all decisions
                for point in mock_route.points:
                    decision = JudgeDecision(
                        point_id=point.id,
                        selected_content=ContentResult(
                            point_id=point.id,
                            content_type=ContentType.TEXT,
                            title=f"Test {point.index}",
                            source="Test",
                            relevance_score=8.0,
                        ),
                        all_candidates=[],
                        reasoning="Test",
                    )
                    collector.add_decision(decision)

                output = collector.generate_output()

                assert output.route == mock_route
                assert len(output.decisions) == len(mock_route.points)
                assert "total_points" in output.processing_stats
                assert "processed_points" in output.processing_stats
                assert "content_type_distribution" in output.processing_stats

    def test_print_summary(self, mock_route, capsys):
        """Test summary printing."""
        with patch("src.core.collector.set_log_context", create=True):
            with patch("src.core.collector.log_collector_update", create=True):
                from src.core.collector import ResultCollector

                collector = ResultCollector(mock_route)

                # Add a decision
                decision = JudgeDecision(
                    point_id=mock_route.points[0].id,
                    selected_content=ContentResult(
                        point_id=mock_route.points[0].id,
                        content_type=ContentType.VIDEO,
                        title="Test Video",
                        source="YouTube",
                        relevance_score=8.5,
                    ),
                    all_candidates=[],
                    reasoning="Test",
                )
                collector.add_decision(decision)

                collector.print_summary()

                captured = capsys.readouterr()
                assert "COLLECTION SUMMARY" in captured.out
                assert mock_route.source in captured.out


class TestStreamingCollector:
    """Tests for StreamingCollector class."""

    def test_initialization(self, mock_route):
        """Test StreamingCollector initialization."""
        with patch("src.core.collector.set_log_context", create=True):
            with patch("src.core.collector.log_collector_update", create=True):
                from src.core.collector import StreamingCollector

                callback = Mock()
                collector = StreamingCollector(mock_route, on_decision=callback)

                assert collector.route == mock_route
                assert collector.on_decision == callback
                assert collector._decision_order == []

    def test_add_decision_calls_callback(self, mock_route):
        """Test add_decision triggers callback."""
        with patch("src.core.collector.set_log_context", create=True):
            with patch("src.core.collector.log_collector_update", create=True):
                from src.core.collector import StreamingCollector

                callback = Mock()
                collector = StreamingCollector(mock_route, on_decision=callback)

                decision = JudgeDecision(
                    point_id=mock_route.points[0].id,
                    selected_content=ContentResult(
                        point_id=mock_route.points[0].id,
                        content_type=ContentType.TEXT,
                        title="Test",
                        source="Test",
                    ),
                    all_candidates=[],
                    reasoning="Test",
                )

                collector.add_decision(decision)

                callback.assert_called_once_with(decision)

    def test_add_decision_callback_error_handled(self, mock_route):
        """Test callback error is handled gracefully."""
        with patch("src.core.collector.set_log_context", create=True):
            with patch("src.core.collector.log_collector_update", create=True):
                from src.core.collector import StreamingCollector

                callback = Mock(side_effect=Exception("Callback error"))
                collector = StreamingCollector(mock_route, on_decision=callback)

                decision = JudgeDecision(
                    point_id=mock_route.points[0].id,
                    selected_content=ContentResult(
                        point_id=mock_route.points[0].id,
                        content_type=ContentType.TEXT,
                        title="Test",
                        source="Test",
                    ),
                    all_candidates=[],
                    reasoning="Test",
                )

                # Should not raise
                collector.add_decision(decision)

                # Decision should still be added
                assert decision.point_id in collector.decisions

    def test_decision_order_tracking(self, mock_route):
        """Test decision order is tracked."""
        with patch("src.core.collector.set_log_context", create=True):
            with patch("src.core.collector.log_collector_update", create=True):
                from src.core.collector import StreamingCollector

                collector = StreamingCollector(mock_route)

                # Add decisions
                for point in mock_route.points:
                    decision = JudgeDecision(
                        point_id=point.id,
                        selected_content=ContentResult(
                            point_id=point.id,
                            content_type=ContentType.TEXT,
                            title="Test",
                            source="Test",
                        ),
                        all_candidates=[],
                        reasoning="Test",
                    )
                    collector.add_decision(decision)

                assert len(collector._decision_order) == len(mock_route.points)

    def test_get_latest_decisions(self, mock_route):
        """Test getting latest decisions."""
        with patch("src.core.collector.set_log_context", create=True):
            with patch("src.core.collector.log_collector_update", create=True):
                from src.core.collector import StreamingCollector

                collector = StreamingCollector(mock_route)

                # Add decisions
                for point in mock_route.points:
                    decision = JudgeDecision(
                        point_id=point.id,
                        selected_content=ContentResult(
                            point_id=point.id,
                            content_type=ContentType.TEXT,
                            title=f"Test {point.index}",
                            source="Test",
                        ),
                        all_candidates=[],
                        reasoning="Test",
                    )
                    collector.add_decision(decision)

                latest = collector.get_latest_decisions(count=2)

                assert len(latest) == 2
                # Should be the last 2 added
                assert latest[-1].point_id == mock_route.points[-1].id


class TestEmptyRoute:
    """Tests with empty route edge cases."""

    def test_empty_route_progress(self):
        """Test progress with empty route."""
        with patch("src.core.collector.set_log_context", create=True):
            with patch("src.core.collector.log_collector_update", create=True):
                from src.core.collector import ResultCollector

                empty_route = Route(
                    source="A",
                    destination="B",
                    points=[],
                    total_distance=0,
                    total_duration=0,
                )

                collector = ResultCollector(empty_route)

                progress = collector.get_progress()
                assert progress["percentage"] == 0
                assert progress["total"] == 0

    def test_empty_route_output(self):
        """Test output generation with empty route."""
        with patch("src.core.collector.set_log_context", create=True):
            with patch("src.core.collector.log_collector_update", create=True):
                from src.core.collector import ResultCollector

                empty_route = Route(
                    source="A",
                    destination="B",
                    points=[],
                    total_distance=0,
                    total_duration=0,
                )

                collector = ResultCollector(empty_route)

                output = collector.generate_output()

                assert output.decisions == []
                assert output.processing_stats["average_relevance_score"] == 0
