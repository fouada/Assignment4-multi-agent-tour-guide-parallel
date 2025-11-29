"""
Unit tests for TourGuideOutput and SystemState models.

Test Coverage:
- TourGuideOutput creation with routes and decisions
- Playlist generation (to_playlist method)
- SystemState tracking
- Edge cases: empty routes, missing decisions
"""
import pytest
from datetime import datetime
from io import StringIO
import sys

from src.models.output import TourGuideOutput, SystemState
from src.models.route import Route, RoutePoint
from src.models.decision import JudgeDecision
from src.models.content import ContentResult, ContentType, AgentStatus


class TestTourGuideOutput:
    """Tests for TourGuideOutput model."""

    @pytest.fixture
    def sample_route(self):
        """Create sample route for testing."""
        return Route(
            source="Tel Aviv, Israel",
            destination="Jerusalem, Israel",
            points=[
                RoutePoint(id="p1", index=0, address="Tel Aviv", location_name="Rabin Square", latitude=32.0853, longitude=34.7818),
                RoutePoint(id="p2", index=1, address="Latrun", location_name="Latrun Monastery", latitude=31.8389, longitude=34.9789),
                RoutePoint(id="p3", index=2, address="Jerusalem", location_name="Old City", latitude=31.7683, longitude=35.2137),
            ],
            total_distance=55000,
            total_duration=2700
        )

    @pytest.fixture
    def sample_decisions(self, sample_route):
        """Create sample decisions for testing."""
        return [
            JudgeDecision(
                point_id="p1",
                selected_content=ContentResult(
                    point_id="p1",
                    content_type=ContentType.VIDEO,
                    title="Tel Aviv City Tour",
                    url="https://youtube.com/watch?v=abc",
                    source="YouTube",
                    relevance_score=8.5
                ),
                all_candidates=[],
                reasoning="Great video for city introduction"
            ),
            JudgeDecision(
                point_id="p2",
                selected_content=ContentResult(
                    point_id="p2",
                    content_type=ContentType.TEXT,
                    title="History of Latrun Monastery",
                    url="https://wikipedia.org/wiki/Latrun",
                    source="Wikipedia",
                    relevance_score=9.0
                ),
                all_candidates=[],
                reasoning="Rich historical content"
            ),
            JudgeDecision(
                point_id="p3",
                selected_content=ContentResult(
                    point_id="p3",
                    content_type=ContentType.MUSIC,
                    title="Jerusalem of Gold",
                    url="https://spotify.com/track/xyz",
                    source="Spotify",
                    relevance_score=9.5
                ),
                all_candidates=[],
                reasoning="Iconic song for Jerusalem"
            ),
        ]

    def test_create_empty_output(self, sample_route):
        """Test creating output with no decisions."""
        output = TourGuideOutput(route=sample_route)
        assert output.route == sample_route
        assert output.decisions == []
        assert output.processing_stats == {}

    def test_create_full_output(self, sample_route, sample_decisions):
        """Test creating output with all data."""
        output = TourGuideOutput(
            route=sample_route,
            decisions=sample_decisions,
            processing_stats={
                "total_points": 3,
                "processed_points": 3,
                "processing_time_seconds": 5.2,
                "average_relevance_score": 9.0
            }
        )
        assert len(output.decisions) == 3
        assert output.processing_stats["total_points"] == 3
        assert output.processing_stats["processing_time_seconds"] == 5.2

    def test_generated_at_auto(self, sample_route):
        """Test generated_at is automatically set."""
        before = datetime.now()
        output = TourGuideOutput(route=sample_route)
        after = datetime.now()
        assert before <= output.generated_at <= after

    def test_to_playlist(self, sample_route, sample_decisions):
        """Test playlist generation."""
        output = TourGuideOutput(
            route=sample_route,
            decisions=sample_decisions
        )
        playlist = output.to_playlist()

        assert len(playlist) == 3

        # Check first item
        assert playlist[0]["point_index"] == 0
        assert playlist[0]["location"] == "Tel Aviv"
        assert playlist[0]["location_name"] == "Rabin Square"
        assert playlist[0]["content_type"] == "video"
        assert playlist[0]["title"] == "Tel Aviv City Tour"
        assert playlist[0]["url"] == "https://youtube.com/watch?v=abc"
        assert playlist[0]["reason"] == "Great video for city introduction"

        # Check content types
        assert playlist[0]["content_type"] == "video"
        assert playlist[1]["content_type"] == "text"
        assert playlist[2]["content_type"] == "music"

    def test_to_playlist_empty(self, sample_route):
        """Test playlist generation with no decisions."""
        output = TourGuideOutput(route=sample_route)
        playlist = output.to_playlist()
        assert playlist == []

    def test_to_playlist_partial_decisions(self, sample_route):
        """Test playlist with only some decisions."""
        decisions = [
            JudgeDecision(
                point_id="p1",
                selected_content=ContentResult(
                    point_id="p1",
                    content_type=ContentType.VIDEO,
                    title="Test Video",
                    source="YouTube"
                ),
                all_candidates=[],
                reasoning="Test"
            ),
        ]
        output = TourGuideOutput(route=sample_route, decisions=decisions)
        playlist = output.to_playlist()
        assert len(playlist) == 1
        assert playlist[0]["point_index"] == 0

    def test_to_playlist_missing_point(self, sample_route):
        """Test playlist when decision references missing point."""
        decisions = [
            JudgeDecision(
                point_id="nonexistent",
                selected_content=ContentResult(
                    point_id="nonexistent",
                    content_type=ContentType.TEXT,
                    title="Test",
                    source="Wikipedia"
                ),
                all_candidates=[],
                reasoning="Test"
            ),
        ]
        output = TourGuideOutput(route=sample_route, decisions=decisions)
        playlist = output.to_playlist()
        # Should skip decisions with no matching point
        assert len(playlist) == 0

    def test_print_playlist(self, sample_route, sample_decisions, capsys):
        """Test print_playlist output."""
        output = TourGuideOutput(
            route=sample_route,
            decisions=sample_decisions
        )
        output.print_playlist()

        captured = capsys.readouterr()
        assert "TOUR GUIDE PLAYLIST" in captured.out
        assert "Tel Aviv" in captured.out
        assert "Jerusalem" in captured.out
        assert "VIDEO" in captured.out or "🎬" in captured.out

    def test_processing_stats_complex(self, sample_route, sample_decisions):
        """Test complex processing stats."""
        output = TourGuideOutput(
            route=sample_route,
            decisions=sample_decisions,
            processing_stats={
                "total_points": 3,
                "processed_points": 3,
                "processing_time_seconds": 5.234,
                "content_type_distribution": {
                    "video": 1,
                    "music": 1,
                    "text": 1
                },
                "average_relevance_score": 9.0,
                "agent_stats": {
                    "video_agent": {"successes": 3, "failures": 0},
                    "music_agent": {"successes": 2, "failures": 1},
                    "text_agent": {"successes": 3, "failures": 0}
                }
            }
        )
        stats = output.processing_stats
        assert stats["content_type_distribution"]["video"] == 1
        assert stats["agent_stats"]["video_agent"]["successes"] == 3

    def test_json_serialization(self, sample_route, sample_decisions):
        """Test output JSON serialization."""
        output = TourGuideOutput(
            route=sample_route,
            decisions=sample_decisions
        )
        json_dict = output.model_dump()
        assert json_dict["route"]["source"] == "Tel Aviv, Israel"
        assert len(json_dict["decisions"]) == 3


class TestSystemState:
    """Tests for SystemState model."""

    def test_create_default_system_state(self):
        """Test creating system state with defaults."""
        state = SystemState()
        assert state.active_threads == 0
        assert state.pending_points == 0
        assert state.processed_points == 0
        assert state.active_agents == {}

    def test_create_active_system_state(self):
        """Test creating system state with activity."""
        state = SystemState(
            active_threads=5,
            pending_points=3,
            processed_points=10,
            active_agents={
                "video_agent_0": AgentStatus.RUNNING,
                "music_agent_0": AgentStatus.RUNNING,
                "text_agent_0": AgentStatus.COMPLETED,
                "video_agent_1": AgentStatus.PENDING
            }
        )
        assert state.active_threads == 5
        assert state.pending_points == 3
        assert state.processed_points == 10
        assert len(state.active_agents) == 4
        assert state.active_agents["video_agent_0"] == AgentStatus.RUNNING

    def test_last_updated_auto(self):
        """Test last_updated is automatically set."""
        before = datetime.now()
        state = SystemState()
        after = datetime.now()
        assert before <= state.last_updated <= after

    def test_system_state_update(self):
        """Test updating system state."""
        state = SystemState(
            active_threads=2,
            pending_points=5
        )
        assert state.active_threads == 2

        # Simulate state update
        new_state = SystemState(
            active_threads=4,
            pending_points=3,
            processed_points=2,
            active_agents={"video_0": AgentStatus.RUNNING}
        )
        assert new_state.active_threads == 4
        assert new_state.pending_points == 3

    def test_system_state_all_agent_statuses(self):
        """Test system state with all agent status types."""
        state = SystemState(
            active_agents={
                "agent_pending": AgentStatus.PENDING,
                "agent_running": AgentStatus.RUNNING,
                "agent_completed": AgentStatus.COMPLETED,
                "agent_failed": AgentStatus.FAILED,
                "agent_timeout": AgentStatus.TIMEOUT
            }
        )
        assert len(state.active_agents) == 5

    def test_system_state_json_serialization(self):
        """Test system state serialization."""
        state = SystemState(
            active_threads=3,
            pending_points=2,
            processed_points=5,
            active_agents={"agent_0": AgentStatus.RUNNING}
        )
        json_dict = state.model_dump()
        assert json_dict["active_threads"] == 3
        assert json_dict["pending_points"] == 2
        assert json_dict["active_agents"]["agent_0"] == "running"


class TestOutputEdgeCases:
    """Edge case tests for output models."""

    def test_empty_route_with_decisions(self):
        """Test output with empty route but has decisions."""
        route = Route(source="A", destination="B")
        decisions = [
            JudgeDecision(
                point_id="orphan",
                selected_content=ContentResult(
                    content_type=ContentType.TEXT,
                    title="Orphan Content",
                    source="Unknown"
                ),
                all_candidates=[],
                reasoning="Test"
            )
        ]
        output = TourGuideOutput(route=route, decisions=decisions)
        playlist = output.to_playlist()
        assert playlist == []  # No matching points

    def test_large_processing_stats(self):
        """Test output with large processing stats."""
        route = Route(source="A", destination="B")
        output = TourGuideOutput(
            route=route,
            processing_stats={
                "total_points": 1000,
                "processed_points": 1000,
                "processing_time_seconds": 3600.5,
                "memory_usage_mb": 512.75,
                "api_calls": {
                    "youtube": 3000,
                    "spotify": 3000,
                    "wikipedia": 3000
                }
            }
        )
        assert output.processing_stats["total_points"] == 1000
        assert output.processing_stats["api_calls"]["youtube"] == 3000

    def test_unicode_in_playlist(self):
        """Test playlist with unicode content."""
        route = Route(
            source="תל אביב",
            destination="ירושלים",
            points=[
                RoutePoint(
                    id="p1",
                    index=0,
                    address="ירושלים",
                    location_name="העיר העתיקה",
                    latitude=31.7683,
                    longitude=35.2137
                )
            ]
        )
        decisions = [
            JudgeDecision(
                point_id="p1",
                selected_content=ContentResult(
                    point_id="p1",
                    content_type=ContentType.MUSIC,
                    title="ירושלים של זהב",
                    url="https://spotify.com/track/hebrew",
                    source="Spotify"
                ),
                all_candidates=[],
                reasoning="שיר אייקוני על ירושלים"
            )
        ]
        output = TourGuideOutput(route=route, decisions=decisions)
        playlist = output.to_playlist()

        assert len(playlist) == 1
        assert "ירושלים" in playlist[0]["title"]
        assert "ירושלים" in playlist[0]["reason"]

    def test_system_state_many_agents(self):
        """Test system state with many agents."""
        agents = {f"agent_{i}": AgentStatus.RUNNING for i in range(100)}
        state = SystemState(
            active_threads=100,
            active_agents=agents
        )
        assert len(state.active_agents) == 100

    def test_playlist_no_url(self):
        """Test playlist item without URL."""
        route = Route(
            source="A",
            destination="B",
            points=[
                RoutePoint(id="p1", index=0, address="Test", latitude=31.0, longitude=35.0)
            ]
        )
        decisions = [
            JudgeDecision(
                point_id="p1",
                selected_content=ContentResult(
                    point_id="p1",
                    content_type=ContentType.TEXT,
                    title="No URL Content",
                    source="Internal",
                    url=None
                ),
                all_candidates=[],
                reasoning="Test"
            )
        ]
        output = TourGuideOutput(route=route, decisions=decisions)
        playlist = output.to_playlist()
        assert playlist[0]["url"] is None

