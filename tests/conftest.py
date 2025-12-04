"""
Pytest fixtures for Multi-Agent Tour Guide tests.

This module provides shared fixtures for all test suites:
- Route and RoutePoint fixtures
- Content result fixtures
- User profile fixtures
- Mock agent fixtures

MIT Level Testing - 85%+ Coverage Target

API Mode Strategy:
- Tests ALWAYS use mock mode (no real API calls)
- This ensures: deterministic results, fast execution, no API costs
- Real API testing should be done locally before push
"""

import os
import sys
from pathlib import Path

import pytest

# =============================================================================
# CRITICAL: Force mock mode for all tests
# =============================================================================
# This ensures tests are:
# - Deterministic and reproducible
# - Fast (no network calls)
# - Cost-free (no API usage)
# - CI/CD friendly (no API keys needed)
os.environ["TOUR_GUIDE_API_MODE"] = "mock"

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
    config.addinivalue_line("markers", "benchmark: mark test as a benchmark test")
    config.addinivalue_line("markers", "slow: mark test as slow running")


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
def mock_judge_decision(
    mock_route_point, mock_video_result, mock_music_result, mock_text_result
):
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
        confidence=0.95,
    )


# =============================================================================
# Multiple Route Points Fixture
# =============================================================================


@pytest.fixture
def mock_route_with_decisions(
    mock_route, mock_video_result, mock_music_result, mock_text_result
):
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
                relevance_score=8.0 + (i * 0.1),
            )
        elif i % 3 == 1:
            content = ContentResult(
                point_id=point.id,
                content_type=ContentType.MUSIC,
                title=f"Song about {point.location_name}",
                source="Spotify",
                relevance_score=8.5 + (i * 0.1),
            )
        else:
            content = ContentResult(
                point_id=point.id,
                content_type=ContentType.TEXT,
                title=f"History of {point.location_name}",
                source="Wikipedia",
                relevance_score=9.0 + (i * 0.1),
            )

        decisions.append(
            JudgeDecision(
                point_id=point.id,
                selected_content=content,
                all_candidates=[content],
                reasoning=f"Best content for {point.location_name}",
            )
        )

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
            relevance_score=8.0,
        ),
        "music": ContentResult(
            point_id="queue_test",
            content_type=ContentType.MUSIC,
            title="Queue Test Music",
            source="Spotify",
            relevance_score=7.5,
        ),
        "text": ContentResult(
            point_id="queue_test",
            content_type=ContentType.TEXT,
            title="Queue Test Text",
            source="Wikipedia",
            relevance_score=9.0,
        ),
    }


# =============================================================================
# Research Framework Fixtures (MIT-Level Innovations)
# =============================================================================


@pytest.fixture
def sample_tour_route():
    """Create a sample tour route for research tests."""
    return [
        {
            "name": "Colosseum",
            "type": "historical",
            "lat": 41.8902,
            "lng": 12.4922,
            "significance": 0.95,
        },
        {
            "name": "Roman Forum",
            "type": "historical",
            "lat": 41.8925,
            "lng": 12.4853,
            "significance": 0.9,
        },
        {
            "name": "Trevi Fountain",
            "type": "scenic",
            "lat": 41.9009,
            "lng": 12.4833,
            "significance": 0.85,
        },
        {
            "name": "Pantheon",
            "type": "religious",
            "lat": 41.8986,
            "lng": 12.4769,
            "significance": 0.92,
        },
        {
            "name": "Vatican City",
            "type": "religious",
            "lat": 41.9022,
            "lng": 12.4533,
            "significance": 0.98,
        },
    ]


@pytest.fixture
def sample_agent_valuations():
    """Create sample agent valuations for negotiation tests."""
    from src.research.agent_negotiation import AgentType

    return {
        AgentType.VIDEO: 0.85,
        AgentType.MUSIC: 0.72,
        AgentType.TEXT: 0.78,
    }


@pytest.fixture
def sample_user_features():
    """Create sample user features for meta-learning tests."""
    import numpy as np

    return np.array(
        [
            0.5,  # age_normalized (middle-aged)
            0.8,  # history_interest
            0.6,  # art_interest
            0.4,  # music_interest
            0.7,  # education_interest
            0.3,  # adventure_level
            0.5,  # attention_span
            0.6,  # visual_preference
            0.4,  # audio_preference
            0.7,  # text_preference
        ],
        dtype=np.float32,
    )


@pytest.fixture
def sample_calibration_data():
    """Create sample calibration data for conformal prediction tests."""
    import numpy as np

    np.random.seed(42)

    n_samples = 100
    features = np.random.randn(n_samples, 10).astype(np.float32)
    predictions = np.random.rand(n_samples).astype(np.float32)
    true_values = predictions + np.random.randn(n_samples).astype(np.float32) * 0.1

    return list(
        zip(
            features,
            range(3) * (n_samples // 3 + 1)[:n_samples],
            true_values,
            strict=False,
        )
    )


@pytest.fixture
def random_seed():
    """Provide a fixed random seed for reproducible tests."""
    return 42


@pytest.fixture
def small_neural_network_config():
    """Configuration for small neural networks in tests."""
    return {
        "input_dim": 10,
        "hidden_dim": 16,
        "output_dim": 3,
        "learning_rate": 0.01,
    }


@pytest.fixture
def mock_route_graph_data():
    """Create mock data for graph neural network tests."""
    import numpy as np

    n_nodes = 5
    feature_dim = 16

    # Node features
    node_features = np.random.randn(n_nodes, feature_dim).astype(np.float32)

    # Adjacency matrix (linear path)
    adj_matrix = np.zeros((n_nodes, n_nodes), dtype=np.float32)
    for i in range(n_nodes - 1):
        adj_matrix[i, i + 1] = 1.0

    # Labels (agent selection for each node)
    labels = np.array([0, 1, 2, 0, 1])  # Rotating agent selection

    return {
        "node_features": node_features,
        "adjacency": adj_matrix,
        "labels": labels,
        "n_nodes": n_nodes,
        "feature_dim": feature_dim,
    }


# =============================================================================
# Performance Testing Fixtures
# =============================================================================


@pytest.fixture
def large_route():
    """Create a large route for performance testing."""
    import numpy as np

    np.random.seed(42)

    n_points = 50
    points = []

    base_lat, base_lng = 41.9, 12.5  # Rome area

    for i in range(n_points):
        points.append(
            {
                "name": f"Point_{i}",
                "type": [
                    "historical",
                    "cultural",
                    "scenic",
                    "religious",
                    "entertainment",
                ][i % 5],
                "lat": base_lat + np.random.randn() * 0.1,
                "lng": base_lng + np.random.randn() * 0.1,
                "significance": np.random.rand(),
            }
        )

    return points


@pytest.fixture
def benchmark_iterations():
    """Number of iterations for benchmark tests."""
    return 100


# =============================================================================
# Tour Guide Dashboard Fixtures
# =============================================================================


@pytest.fixture
def dashboard_family_profile():
    """Create a family profile for dashboard testing."""
    return {
        "preset": "family",
        "age_group": "adult",
        "min_age": 5,
        "travel_mode": "car",
        "trip_purpose": "vacation",
        "content_preference": "educational",
        "family_mode": ["enabled"],
        "driver_mode": [],
        "interests": "history, nature, culture",
        "exclude_topics": "violence, adult content",
        "max_duration": 300,
    }


@pytest.fixture
def dashboard_driver_profile():
    """Create a driver profile for dashboard testing (no video)."""
    return {
        "preset": "driver",
        "age_group": "adult",
        "min_age": 30,
        "travel_mode": "car",
        "trip_purpose": "business",
        "content_preference": "educational",
        "family_mode": [],
        "driver_mode": ["enabled"],
        "interests": "podcasts, audio books",
        "exclude_topics": "",
        "max_duration": 600,
    }


@pytest.fixture
def dashboard_tour_route():
    """Create a sample tour route for dashboard testing."""
    return {
        "source": "Tel Aviv, Israel",
        "destination": "Jerusalem, Israel",
        "waypoints": "Latrun, Bab al-Wad",
        "points": [
            {"name": "Tel Aviv", "lat": 32.0853, "lon": 34.7818},
            {"name": "Latrun Monastery", "lat": 31.8377, "lon": 34.9781},
            {"name": "Bab al-Wad Memorial", "lat": 31.8419, "lon": 35.0614},
            {"name": "Ein Karem", "lat": 31.7667, "lon": 35.1583},
            {"name": "Jerusalem", "lat": 31.7683, "lon": 35.2137},
        ],
    }


@pytest.fixture
def dashboard_mock_recommendations():
    """Create mock recommendations for dashboard testing."""
    return [
        {
            "point": "Tel Aviv",
            "type": "TEXT",
            "title": "The Story of Tel Aviv",
            "description": "Historical narrative about the founding of Tel Aviv",
            "quality_score": 8.5,
            "duration": "3 min",
        },
        {
            "point": "Latrun",
            "type": "VIDEO",
            "title": "Latrun Tank Museum Virtual Tour",
            "description": "Interactive tour of the famous tank museum",
            "quality_score": 9.2,
            "duration": "5 min",
        },
        {
            "point": "Jerusalem",
            "type": "MUSIC",
            "title": "Jerusalem of Gold",
            "description": "Famous song celebrating Jerusalem",
            "quality_score": 9.8,
            "duration": "4 min",
        },
    ]


@pytest.fixture
def dashboard_edge_case_inputs():
    """Edge case inputs for dashboard testing."""
    return {
        "empty_source": "",
        "empty_destination": "",
        "unicode_location": "ירושלים, ישראל",  # Hebrew
        "long_location": "A" * 500,
        "min_age_zero": 0,
        "max_age": 120,
        "min_duration": 30,
        "max_duration": 600,
        "special_chars": "Location with <special> & 'chars'",
    }
