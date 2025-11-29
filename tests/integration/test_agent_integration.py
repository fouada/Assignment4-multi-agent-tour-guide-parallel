"""
Integration tests for agent system.

Test Coverage:
- Agent base class functionality
- Mock LLM responses
- Content result generation
- Agent execution flow
"""

from datetime import datetime
from unittest.mock import patch

import pytest

from src.agents.music_agent import MusicAgent
from src.agents.text_agent import TextAgent
from src.agents.video_agent import VideoAgent
from src.models.content import ContentResult, ContentType
from src.models.route import RoutePoint


class TestAgentExecution:
    """Integration tests for agent execution."""

    @pytest.fixture
    def sample_point(self):
        """Create a sample route point."""
        return RoutePoint(
            id="test_point",
            index=0,
            address="Ammunition Hill, Jerusalem",
            location_name="Ammunition Hill",
            latitude=31.7944,
            longitude=35.2283,
        )

    def test_video_agent_mock_execution(self, sample_point):
        """Test video agent produces mock result without API."""
        # Create agent without API keys
        with patch.object(VideoAgent, "_init_youtube_client"):
            agent = VideoAgent()
            agent.youtube_client = None
            agent.llm_client = None

        result = agent.execute(sample_point)

        assert result is not None
        assert isinstance(result, ContentResult)
        assert result.content_type == ContentType.VIDEO
        assert result.point_id == sample_point.id
        assert result.source == "YouTube (Mock)"

    def test_music_agent_mock_execution(self, sample_point):
        """Test music agent produces mock result without API."""
        agent = MusicAgent()
        agent.llm_client = None

        result = agent.execute(sample_point)

        assert result is not None
        assert isinstance(result, ContentResult)
        assert result.content_type == ContentType.MUSIC
        assert result.point_id == sample_point.id

    def test_text_agent_mock_execution(self, sample_point):
        """Test text agent produces mock result without API."""
        agent = TextAgent()
        agent.llm_client = None

        result = agent.execute(sample_point)

        assert result is not None
        assert isinstance(result, ContentResult)
        assert result.content_type == ContentType.TEXT
        assert result.point_id == sample_point.id

    def test_agent_execution_with_different_locations(self):
        """Test agents handle different location types."""
        locations = [
            ("Tel Aviv, Israel", "Tel Aviv", 32.0853, 34.7818),
            ("Jerusalem, Israel", "Old City", 31.7683, 35.2137),
            ("Latrun, Israel", "Latrun Monastery", 31.8389, 34.9789),
        ]

        for address, name, lat, lng in locations:
            point = RoutePoint(
                id=f"point_{name.replace(' ', '_')}",
                index=0,
                address=address,
                location_name=name,
                latitude=lat,
                longitude=lng,
            )

            # Test with video agent (mock mode)
            with patch.object(VideoAgent, "_init_youtube_client"):
                agent = VideoAgent()
                agent.youtube_client = None
                agent.llm_client = None

            result = agent.execute(point)
            assert result is not None
            assert result.point_id == point.id

    def test_agent_thread_tracking(self, sample_point):
        """Test agent tracks thread information."""
        with patch.object(VideoAgent, "_init_youtube_client"):
            agent = VideoAgent()
            agent.youtube_client = None
            agent.llm_client = None

        agent.execute(sample_point)

        # After execution, agent should have tracked point and thread
        assert agent.current_point_id == sample_point.id


class TestAgentContentGeneration:
    """Tests for agent content generation."""

    @pytest.fixture
    def sample_point(self):
        """Create sample route point."""
        return RoutePoint(
            id="content_test",
            index=0,
            address="Test Location",
            location_name="Test Place",
            latitude=31.5,
            longitude=35.0,
        )

    def test_content_result_has_required_fields(self, sample_point):
        """Test generated content has all required fields."""
        with patch.object(VideoAgent, "_init_youtube_client"):
            agent = VideoAgent()
            agent.youtube_client = None
            agent.llm_client = None

        result = agent.execute(sample_point)

        assert result.point_id
        assert result.content_type
        assert result.title
        assert result.source
        assert 0 <= result.relevance_score <= 10

    def test_content_result_metadata(self, sample_point):
        """Test content result includes metadata."""
        with patch.object(VideoAgent, "_init_youtube_client"):
            agent = VideoAgent()
            agent.youtube_client = None
            agent.llm_client = None

        result = agent.execute(sample_point)

        assert isinstance(result.metadata, dict)

    def test_content_result_found_at_timestamp(self, sample_point):
        """Test content result has proper timestamp."""
        before = datetime.now()

        with patch.object(VideoAgent, "_init_youtube_client"):
            agent = VideoAgent()
            agent.youtube_client = None
            agent.llm_client = None

        result = agent.execute(sample_point)

        after = datetime.now()
        assert before <= result.found_at <= after


class TestAgentErrorHandling:
    """Tests for agent error handling."""

    @pytest.fixture
    def sample_point(self):
        """Create sample route point."""
        return RoutePoint(
            id="error_test",
            index=0,
            address="Error Location",
            latitude=31.0,
            longitude=35.0,
        )

    def test_agent_handles_missing_location_name(self):
        """Test agent handles point without location name."""
        point = RoutePoint(
            id="no_name",
            index=0,
            address="Some Address Without Name",
            latitude=31.0,
            longitude=35.0,
            location_name=None,  # No location name
        )

        with patch.object(VideoAgent, "_init_youtube_client"):
            agent = VideoAgent()
            agent.youtube_client = None
            agent.llm_client = None

        result = agent.execute(point)

        # Should still produce a result
        assert result is not None
        assert result.point_id == point.id

    def test_agent_handles_special_characters_in_address(self):
        """Test agent handles special characters in address."""
        point = RoutePoint(
            id="special_chars",
            index=0,
            address="ירושלים, ישראל - 耶路撒冷",
            location_name="העיר העתיקה",
            latitude=31.7683,
            longitude=35.2137,
        )

        with patch.object(VideoAgent, "_init_youtube_client"):
            agent = VideoAgent()
            agent.youtube_client = None
            agent.llm_client = None

        result = agent.execute(point)

        assert result is not None


class TestMultiAgentCoordination:
    """Tests for multiple agents working together."""

    @pytest.fixture
    def sample_point(self):
        """Create sample route point."""
        return RoutePoint(
            id="multi_agent_test",
            index=0,
            address="Jerusalem, Israel",
            location_name="Old City",
            latitude=31.7683,
            longitude=35.2137,
        )

    def test_all_agents_produce_results(self, sample_point):
        """Test all agent types produce results for same point."""
        results = {}

        # Video Agent
        with patch.object(VideoAgent, "_init_youtube_client"):
            video_agent = VideoAgent()
            video_agent.youtube_client = None
            video_agent.llm_client = None
        results["video"] = video_agent.execute(sample_point)

        # Music Agent
        music_agent = MusicAgent()
        music_agent.llm_client = None
        results["music"] = music_agent.execute(sample_point)

        # Text Agent
        text_agent = TextAgent()
        text_agent.llm_client = None
        results["text"] = text_agent.execute(sample_point)

        # All should produce results
        assert all(r is not None for r in results.values())

        # Each should have correct content type
        assert results["video"].content_type == ContentType.VIDEO
        assert results["music"].content_type == ContentType.MUSIC
        assert results["text"].content_type == ContentType.TEXT

    def test_all_agents_share_point_id(self, sample_point):
        """Test all agents use same point ID."""
        results = []

        with patch.object(VideoAgent, "_init_youtube_client"):
            video_agent = VideoAgent()
            video_agent.youtube_client = None
            video_agent.llm_client = None
        results.append(video_agent.execute(sample_point))

        music_agent = MusicAgent()
        music_agent.llm_client = None
        results.append(music_agent.execute(sample_point))

        text_agent = TextAgent()
        text_agent.llm_client = None
        results.append(text_agent.execute(sample_point))

        # All should have same point_id
        point_ids = [r.point_id for r in results]
        assert all(pid == sample_point.id for pid in point_ids)
