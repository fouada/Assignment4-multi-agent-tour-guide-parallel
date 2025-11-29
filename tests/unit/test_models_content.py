"""
Unit tests for Content model and related enums.

Test Coverage:
- ContentType enum values and string representation
- AgentStatus enum lifecycle
- ContentResult model creation and validation
- Edge cases: boundary values, missing fields, invalid data
"""
import pytest
from datetime import datetime
from pydantic import ValidationError

from src.models.content import ContentType, AgentStatus, ContentResult


class TestContentType:
    """Tests for ContentType enum."""

    def test_content_type_values(self):
        """Verify all content type enum values."""
        assert ContentType.VIDEO == "video"
        assert ContentType.MUSIC == "music"
        assert ContentType.TEXT == "text"

    def test_content_type_string_conversion(self):
        """Test string conversion of content types."""
        assert str(ContentType.VIDEO) == "ContentType.VIDEO"
        assert ContentType.VIDEO.value == "video"

    def test_content_type_from_string(self):
        """Test creating content type from string."""
        assert ContentType("video") == ContentType.VIDEO
        assert ContentType("music") == ContentType.MUSIC
        assert ContentType("text") == ContentType.TEXT

    def test_invalid_content_type(self):
        """Test that invalid content type raises error."""
        with pytest.raises(ValueError):
            ContentType("invalid_type")

    def test_content_type_iteration(self):
        """Test iterating over all content types."""
        types = list(ContentType)
        assert len(types) == 3
        assert ContentType.VIDEO in types
        assert ContentType.MUSIC in types
        assert ContentType.TEXT in types


class TestAgentStatus:
    """Tests for AgentStatus enum."""

    def test_agent_status_values(self):
        """Verify all agent status values."""
        assert AgentStatus.PENDING == "pending"
        assert AgentStatus.RUNNING == "running"
        assert AgentStatus.COMPLETED == "completed"
        assert AgentStatus.FAILED == "failed"
        assert AgentStatus.TIMEOUT == "timeout"

    def test_agent_status_lifecycle(self):
        """Test typical status lifecycle."""
        # Typical success path
        lifecycle = [AgentStatus.PENDING, AgentStatus.RUNNING, AgentStatus.COMPLETED]
        for status in lifecycle:
            assert status in AgentStatus

        # Failure path
        failure_lifecycle = [AgentStatus.PENDING, AgentStatus.RUNNING, AgentStatus.FAILED]
        for status in failure_lifecycle:
            assert status in AgentStatus

    def test_agent_status_count(self):
        """Test we have exactly 5 statuses."""
        assert len(list(AgentStatus)) == 5


class TestContentResult:
    """Tests for ContentResult model."""

    def test_create_minimal_content_result(self):
        """Test creating content result with minimum required fields."""
        result = ContentResult(
            content_type=ContentType.VIDEO,
            title="Test Video",
            source="YouTube"
        )
        assert result.content_type == ContentType.VIDEO
        assert result.title == "Test Video"
        assert result.source == "YouTube"
        assert result.point_id == ""  # Default
        assert result.relevance_score == 5.0  # Default

    def test_create_full_content_result(self):
        """Test creating content result with all fields."""
        now = datetime.now()
        result = ContentResult(
            point_id="point_123",
            content_type=ContentType.MUSIC,
            title="Test Song",
            description="A beautiful song",
            url="https://spotify.com/track/xyz",
            source="Spotify",
            relevance_score=8.5,
            duration_seconds=240,
            metadata={"artist": "Test Artist", "album": "Test Album"},
            found_at=now
        )
        assert result.point_id == "point_123"
        assert result.content_type == ContentType.MUSIC
        assert result.title == "Test Song"
        assert result.description == "A beautiful song"
        assert result.url == "https://spotify.com/track/xyz"
        assert result.source == "Spotify"
        assert result.relevance_score == 8.5
        assert result.duration_seconds == 240
        assert result.metadata["artist"] == "Test Artist"
        assert result.found_at == now

    def test_content_result_score_boundaries(self):
        """Test relevance score must be between 0 and 10."""
        # Valid boundary values
        result_min = ContentResult(
            content_type=ContentType.TEXT,
            title="Test",
            source="Wikipedia",
            relevance_score=0.0
        )
        assert result_min.relevance_score == 0.0

        result_max = ContentResult(
            content_type=ContentType.TEXT,
            title="Test",
            source="Wikipedia",
            relevance_score=10.0
        )
        assert result_max.relevance_score == 10.0

    def test_content_result_score_too_low(self):
        """Test relevance score below 0 raises error."""
        with pytest.raises(ValidationError) as exc_info:
            ContentResult(
                content_type=ContentType.TEXT,
                title="Test",
                source="Wikipedia",
                relevance_score=-1.0
            )
        assert "greater than or equal to 0" in str(exc_info.value)

    def test_content_result_score_too_high(self):
        """Test relevance score above 10 raises error."""
        with pytest.raises(ValidationError) as exc_info:
            ContentResult(
                content_type=ContentType.TEXT,
                title="Test",
                source="Wikipedia",
                relevance_score=11.0
            )
        assert "less than or equal to 10" in str(exc_info.value)

    def test_content_result_optional_fields(self):
        """Test optional fields can be None."""
        result = ContentResult(
            content_type=ContentType.VIDEO,
            title="Test",
            source="YouTube"
        )
        assert result.description is None
        assert result.url is None
        assert result.duration_seconds is None

    def test_content_result_json_serialization(self):
        """Test content result can be serialized to JSON."""
        result = ContentResult(
            point_id="p1",
            content_type=ContentType.VIDEO,
            title="Test",
            source="YouTube",
            relevance_score=7.5
        )
        json_dict = result.model_dump()
        assert json_dict["point_id"] == "p1"
        assert json_dict["content_type"] == "video"
        assert json_dict["title"] == "Test"
        assert json_dict["relevance_score"] == 7.5

    def test_content_result_metadata_default(self):
        """Test metadata defaults to empty dict."""
        result = ContentResult(
            content_type=ContentType.TEXT,
            title="Test",
            source="Wikipedia"
        )
        assert result.metadata == {}
        assert isinstance(result.metadata, dict)

    def test_content_result_metadata_complex(self):
        """Test metadata with complex nested data."""
        metadata = {
            "views": 150000,
            "channel": "History Channel",
            "tags": ["history", "documentary"],
            "stats": {"likes": 5000, "comments": 100}
        }
        result = ContentResult(
            content_type=ContentType.VIDEO,
            title="Documentary",
            source="YouTube",
            metadata=metadata
        )
        assert result.metadata["views"] == 150000
        assert "documentary" in result.metadata["tags"]
        assert result.metadata["stats"]["likes"] == 5000

    def test_content_result_found_at_auto(self):
        """Test found_at is automatically set."""
        before = datetime.now()
        result = ContentResult(
            content_type=ContentType.TEXT,
            title="Test",
            source="Wikipedia"
        )
        after = datetime.now()
        assert before <= result.found_at <= after

    def test_content_result_all_content_types(self):
        """Test content result works with all content types."""
        for content_type in ContentType:
            result = ContentResult(
                content_type=content_type,
                title=f"Test {content_type.value}",
                source="Test Source"
            )
            assert result.content_type == content_type


class TestContentResultEdgeCases:
    """Edge case tests for ContentResult."""

    def test_empty_title(self):
        """Test empty title is allowed."""
        result = ContentResult(
            content_type=ContentType.TEXT,
            title="",
            source="Wikipedia"
        )
        assert result.title == ""

    def test_very_long_title(self):
        """Test very long title is handled."""
        long_title = "A" * 10000
        result = ContentResult(
            content_type=ContentType.TEXT,
            title=long_title,
            source="Wikipedia"
        )
        assert len(result.title) == 10000

    def test_unicode_title(self):
        """Test unicode characters in title."""
        unicode_title = "ירושלים - 耶路撒冷 - القدس"
        result = ContentResult(
            content_type=ContentType.TEXT,
            title=unicode_title,
            source="Wikipedia"
        )
        assert result.title == unicode_title

    def test_special_characters_in_url(self):
        """Test special characters in URL."""
        url = "https://example.com/path?query=hello%20world&foo=bar#section"
        result = ContentResult(
            content_type=ContentType.VIDEO,
            title="Test",
            source="YouTube",
            url=url
        )
        assert result.url == url

    def test_zero_duration(self):
        """Test zero duration is valid."""
        result = ContentResult(
            content_type=ContentType.VIDEO,
            title="Test",
            source="YouTube",
            duration_seconds=0
        )
        assert result.duration_seconds == 0

    def test_large_duration(self):
        """Test large duration value."""
        result = ContentResult(
            content_type=ContentType.VIDEO,
            title="Long Documentary",
            source="YouTube",
            duration_seconds=86400  # 24 hours
        )
        assert result.duration_seconds == 86400

    def test_decimal_score(self):
        """Test decimal relevance score."""
        result = ContentResult(
            content_type=ContentType.TEXT,
            title="Test",
            source="Wikipedia",
            relevance_score=7.8234567
        )
        assert result.relevance_score == 7.8234567

