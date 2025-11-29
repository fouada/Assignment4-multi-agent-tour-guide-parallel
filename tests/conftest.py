"""
Pytest fixtures for Multi-Agent Tour Guide tests.

This module provides shared fixtures for all test suites:
- Route and RoutePoint fixtures
- Content result fixtures
- User profile fixtures
- Mock agent fixtures

MIT Level Testing - 85%+ Coverage Target
"""
import sys
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.content import ContentResult, ContentType
from src.models.decision import JudgeDecision
from src.models.route import Route, RoutePoint
from src.models.user_profile import (
    AgeGroup,
    Gender,
    UserProfile,
    get_driver_profile,
    get_family_profile,
    get_kid_profile,
)


# Configure pytest-asyncio
def pytest_configure(config):
    """Configure pytest plugins."""
    config.addinivalue_line(
        "markers", "benchmark: mark test as a benchmark test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
)


@pytest.fixture
def mock_route_point():
    """Create a mock route point."""
    return RoutePoint(
        id="test_point_1",
        index=0,
        address="Ammunition Hill, Jerusalem",
        location_name="Ammunition Hill",
        latitude=31.7944,
        longitude=35.2283,
    )


@pytest.fixture
def mock_route():
    """Create a mock route."""
    return Route(
        source="Tel Aviv, Israel",
        destination="Jerusalem, Israel",
        points=[
            RoutePoint(
                id="point_1",
                index=0,
                address="Tel Aviv",
                location_name="Tel Aviv",
                latitude=32.0853,
                longitude=34.7818,
            ),
            RoutePoint(
                id="point_2",
                index=1,
                address="Latrun",
                location_name="Latrun",
                latitude=31.8389,
                longitude=34.9789,
            ),
            RoutePoint(
                id="point_3",
                index=2,
                address="Jerusalem",
                location_name="Jerusalem",
                latitude=31.7683,
                longitude=35.2137,
            ),
        ],
        total_distance=55000,
        total_duration=2700,
    )


@pytest.fixture
def mock_video_result():
    """Create a mock video content result."""
    return ContentResult(
        point_id="test_point_1",
        content_type=ContentType.VIDEO,
        title="The Battle of Ammunition Hill",
        description="Documentary about the Six-Day War battle",
        url="https://youtube.com/watch?v=test123",
        source="YouTube",
        relevance_score=8.5,
        duration_seconds=720,
    )


@pytest.fixture
def mock_music_result():
    """Create a mock music content result."""
    return ContentResult(
        point_id="test_point_1",
        content_type=ContentType.MUSIC,
        title="Jerusalem of Gold",
        description="Famous song about Jerusalem",
        url="https://spotify.com/track/test456",
        source="Spotify",
        relevance_score=9.0,
        duration_seconds=240,
    )


@pytest.fixture
def mock_text_result():
    """Create a mock text content result."""
    return ContentResult(
        point_id="test_point_1",
        content_type=ContentType.TEXT,
        title="The History of Ammunition Hill",
        description="Detailed historical account of the battle...",
        url="https://wikipedia.org/wiki/Ammunition_Hill",
        source="Wikipedia",
        relevance_score=7.5,
    )


@pytest.fixture
def adult_profile():
    """Create an adult user profile."""
    return UserProfile(
        age_group=AgeGroup.ADULT,
        gender=Gender.MALE,
    )


@pytest.fixture
def kid_profile():
    """Create a kid user profile."""
    return get_kid_profile(age=8)


@pytest.fixture
def family_profile():
    """Create a family user profile."""
    return get_family_profile(min_age=5)


@pytest.fixture
def driver_profile():
    """Create a driver user profile (no video!)."""
    return get_driver_profile()


# =============================================================================
# Decision Fixtures
# =============================================================================

@pytest.fixture
def mock_judge_decision(mock_route_point, mock_video_result, mock_music_result, mock_text_result):
    """Create a mock judge decision with all candidates."""
    return JudgeDecision(
        point_id=mock_route_point.id,
        selected_content=mock_text_result,
        all_candidates=[mock_video_result, mock_music_result, mock_text_result],
        reasoning="Text content provides the most educational value for this historical site",
        scores={
            ContentType.VIDEO: 8.5,
            ContentType.MUSIC: 9.0,
            ContentType.TEXT: 9.5,
        },
        confidence=0.95
    )


# =============================================================================
# Multiple Route Points Fixture
# =============================================================================

@pytest.fixture
def mock_route_with_decisions(mock_route, mock_video_result, mock_music_result, mock_text_result):
    """Create a mock route with associated decisions."""
    decisions = []
    for i, point in enumerate(mock_route.points):
        # Rotate through content types
        if i % 3 == 0:
            content = ContentResult(
                point_id=point.id,
                content_type=ContentType.VIDEO,
                title=f"Video for {point.location_name}",
                source="YouTube",
                relevance_score=8.0 + (i * 0.1)
            )
        elif i % 3 == 1:
            content = ContentResult(
                point_id=point.id,
                content_type=ContentType.MUSIC,
                title=f"Song about {point.location_name}",
                source="Spotify",
                relevance_score=8.5 + (i * 0.1)
            )
        else:
            content = ContentResult(
                point_id=point.id,
                content_type=ContentType.TEXT,
                title=f"History of {point.location_name}",
                source="Wikipedia",
                relevance_score=9.0 + (i * 0.1)
            )

        decisions.append(JudgeDecision(
            point_id=point.id,
            selected_content=content,
            all_candidates=[content],
            reasoning=f"Best content for {point.location_name}"
        ))

    return mock_route, decisions


# =============================================================================
# Queue Testing Fixtures
# =============================================================================

@pytest.fixture
def queue_test_results():
    """Create sample content results for queue testing."""
    return {
        "video": ContentResult(
            point_id="queue_test",
            content_type=ContentType.VIDEO,
            title="Queue Test Video",
            source="YouTube",
            relevance_score=8.0
        ),
        "music": ContentResult(
            point_id="queue_test",
            content_type=ContentType.MUSIC,
            title="Queue Test Music",
            source="Spotify",
            relevance_score=7.5
        ),
        "text": ContentResult(
            point_id="queue_test",
            content_type=ContentType.TEXT,
            title="Queue Test Text",
            source="Wikipedia",
            relevance_score=9.0
        ),
    }

