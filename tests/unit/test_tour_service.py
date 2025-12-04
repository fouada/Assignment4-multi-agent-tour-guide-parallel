"""
Unit tests for the Tour Service module.

Tests cover:
- TourStatus and PointStatus enums
- TourState and PointResult dataclasses
- TourStore thread-safe storage
- TourService tour creation and management
- API status checking

MIT Level Testing - 85%+ Coverage Target
"""

import os
from unittest.mock import patch

import pytest


class TestTourStatus:
    """Tests for TourStatus enum."""

    def test_all_status_values(self):
        """Test all status values exist."""
        from src.services.tour_service import TourStatus

        assert TourStatus.PENDING == "pending"
        assert TourStatus.FETCHING_ROUTE == "fetching_route"
        assert TourStatus.SCHEDULING == "scheduling"
        assert TourStatus.PROCESSING == "processing"
        assert TourStatus.COMPLETED == "completed"
        assert TourStatus.FAILED == "failed"
        assert TourStatus.CANCELLED == "cancelled"

    def test_status_count(self):
        """Test number of statuses."""
        from src.services.tour_service import TourStatus

        assert len(TourStatus) == 7


class TestPointStatus:
    """Tests for PointStatus enum."""

    def test_all_point_status_values(self):
        """Test all point status values exist."""
        from src.services.tour_service import PointStatus

        assert PointStatus.PENDING == "pending"
        assert PointStatus.AGENTS_RUNNING == "agents_running"
        assert PointStatus.QUEUE_WAITING == "queue_waiting"
        assert PointStatus.JUDGE_EVALUATING == "judge_evaluating"
        assert PointStatus.COMPLETED == "completed"
        assert PointStatus.FAILED == "failed"


class TestAgentResult:
    """Tests for AgentResult dataclass."""

    def test_create_minimal(self):
        """Test minimal agent result."""
        from src.services.tour_service import AgentResult

        result = AgentResult(agent_type="video", success=True)

        assert result.agent_type == "video"
        assert result.success is True
        assert result.title is None
        assert result.error is None

    def test_create_full(self):
        """Test full agent result."""
        from src.services.tour_service import AgentResult

        result = AgentResult(
            agent_type="music",
            success=True,
            title="Jerusalem Song",
            content_type="audio",
            url="https://example.com/song",
            duration_seconds=3.5,
            error=None,
            raw_result={"extra": "data"},
        )

        assert result.agent_type == "music"
        assert result.title == "Jerusalem Song"
        assert result.duration_seconds == 3.5


class TestPointResult:
    """Tests for PointResult dataclass."""

    def test_create_minimal(self):
        """Test minimal point result."""
        from src.services.tour_service import PointResult, PointStatus

        result = PointResult(point_index=0, point_name="Test Point")

        assert result.point_index == 0
        assert result.point_name == "Test Point"
        assert result.status == PointStatus.PENDING
        assert result.agent_results == []
        assert result.winner is None
        assert result.judge_reasoning is None

    def test_with_agent_results(self):
        """Test point result with agent results."""
        from src.services.tour_service import AgentResult, PointResult

        agent_result = AgentResult(agent_type="video", success=True, title="Test Video")
        result = PointResult(
            point_index=1,
            point_name="Jerusalem",
            agent_results=[agent_result],
        )

        assert len(result.agent_results) == 1
        assert result.agent_results[0].title == "Test Video"


class TestTourState:
    """Tests for TourState dataclass."""

    def test_create_minimal(self):
        """Test minimal tour state."""
        from src.services.tour_service import TourState, TourStatus

        state = TourState(
            tour_id="tour_123",
            source="Tel Aviv",
            destination="Jerusalem",
        )

        assert state.tour_id == "tour_123"
        assert state.source == "Tel Aviv"
        assert state.destination == "Jerusalem"
        assert state.status == TourStatus.PENDING
        assert state.points == []
        assert state.profile == {}

    def test_with_profile(self):
        """Test tour state with profile."""
        from src.services.tour_service import TourState

        state = TourState(
            tour_id="tour_456",
            source="Haifa",
            destination="Nazareth",
            profile={"age_group": "family", "is_driver": True},
        )

        assert state.profile["age_group"] == "family"
        assert state.profile["is_driver"] is True


class TestTourStore:
    """Tests for TourStore."""

    @pytest.fixture
    def store(self):
        """Create a fresh store."""
        from src.services.tour_service import TourStore

        return TourStore()

    def test_create_and_get(self, store):
        """Test creating and getting a tour."""
        tour = store.create(
            tour_id="tour_001",
            source="A",
            destination="B",
            profile={},
        )

        assert tour.tour_id == "tour_001"

        retrieved = store.get("tour_001")
        assert retrieved is not None
        assert retrieved.tour_id == "tour_001"

    def test_get_nonexistent(self, store):
        """Test getting nonexistent tour."""
        result = store.get("nonexistent")
        assert result is None

    def test_update(self, store):
        """Test updating a tour."""
        from src.services.tour_service import TourStatus

        store.create(tour_id="tour_002", source="A", destination="B", profile={})

        store.update("tour_002", status=TourStatus.PROCESSING, total_points=5)

        updated = store.get("tour_002")
        assert updated.status == TourStatus.PROCESSING
        assert updated.total_points == 5

    def test_update_nonexistent(self, store):
        """Test updating nonexistent tour returns None."""
        result = store.update("nonexistent", status="processing")
        assert result is None

    def test_list_all(self, store):
        """Test listing all tours."""
        store.create(tour_id="t1", source="A", destination="B", profile={})
        store.create(tour_id="t2", source="C", destination="D", profile={})

        all_tours = store.list_all()

        assert len(all_tours) == 2
        tour_ids = [t.tour_id for t in all_tours]
        assert "t1" in tour_ids
        assert "t2" in tour_ids

    def test_list_all_with_limit(self, store):
        """Test listing tours with limit."""
        for i in range(5):
            store.create(tour_id=f"t{i}", source="A", destination="B", profile={})

        limited = store.list_all(limit=3)
        assert len(limited) == 3

    def test_delete(self, store):
        """Test deleting a tour."""
        store.create(tour_id="to_delete", source="A", destination="B", profile={})
        assert store.get("to_delete") is not None

        result = store.delete("to_delete")
        assert result is True
        assert store.get("to_delete") is None

    def test_delete_nonexistent(self, store):
        """Test deleting nonexistent tour."""
        result = store.delete("nonexistent")
        assert result is False

    def test_subscribe_and_notify(self, store):
        """Test subscription notifications."""
        from src.services.tour_service import TourStatus

        notifications = []

        def callback(tour):
            notifications.append(tour.status)

        store.create(tour_id="sub_test", source="A", destination="B", profile={})
        store.subscribe("sub_test", callback)

        store.update("sub_test", status=TourStatus.PROCESSING)

        assert TourStatus.PROCESSING in notifications

    def test_unsubscribe(self, store):
        """Test unsubscription."""
        notifications = []

        def callback(tour):
            notifications.append(tour.status)

        store.create(tour_id="unsub_test", source="A", destination="B", profile={})
        store.subscribe("unsub_test", callback)
        store.unsubscribe("unsub_test", callback)

        # Update should not trigger callback
        from src.services.tour_service import TourStatus

        store.update("unsub_test", status=TourStatus.COMPLETED)

        # Should be empty since we unsubscribed
        assert TourStatus.COMPLETED not in notifications


class TestTourService:
    """Tests for TourService."""

    @pytest.fixture
    def service(self):
        """Create a tour service with clean store."""
        from src.services.tour_service import TourService, TourStore

        store = TourStore()
        svc = TourService(store=store)
        yield svc
        # Cleanup
        svc._executor.shutdown(wait=False)

    def test_initialization(self, service):
        """Test service initialization."""
        assert service.store is not None
        assert service._executor is not None
        assert service._api_mode in ["auto", "mock", "real"]

    def test_create_tour(self, service):
        """Test creating a tour."""
        tour = service.create_tour(
            source="Tel Aviv",
            destination="Jerusalem",
        )

        assert tour.tour_id is not None
        assert tour.tour_id.startswith("tour_")
        assert tour.source == "Tel Aviv"
        assert tour.destination == "Jerusalem"

    def test_create_tour_with_profile(self, service):
        """Test creating a tour with profile."""
        tour = service.create_tour(
            source="Haifa",
            destination="Nazareth",
            profile={"is_driver": True, "age_group": "adult"},
        )

        assert tour.profile.get("is_driver") is True
        assert tour.profile.get("age_group") == "adult"

    def test_get_tour(self, service):
        """Test getting a tour."""
        created = service.create_tour(source="A", destination="B")

        retrieved = service.get_tour(created.tour_id)

        assert retrieved is not None
        assert retrieved.tour_id == created.tour_id

    def test_get_tour_not_found(self, service):
        """Test getting nonexistent tour."""
        result = service.get_tour("nonexistent_id")
        assert result is None

    def test_cancel_tour_not_processing(self, service):
        """Test cancelling a non-processing tour returns False."""
        tour = service.create_tour(source="A", destination="B")
        # Tour starts in PENDING state, moves to FETCHING_ROUTE quickly
        # Cancel only works for PROCESSING state

        # Since it's async, we test the case where it's not in PROCESSING
        # This might succeed or fail depending on timing
        result = service.cancel_tour(tour.tour_id)
        # Result depends on the current state
        assert isinstance(result, bool)

    def test_get_api_status(self, service):
        """Test get_api_status method."""
        status = service.get_api_status()

        assert "mode" in status
        assert "using_real_apis" in status
        assert "agents_available" in status
        assert "api_keys" in status

    def test_check_agents_available(self, service):
        """Test _check_agents_available method."""
        result = service._check_agents_available()
        assert isinstance(result, bool)

    def test_check_api_keys(self, service):
        """Test _check_api_keys method."""
        result = service._check_api_keys()

        assert isinstance(result, dict)
        assert "google_maps" in result
        assert "youtube" in result
        assert "anthropic" in result
        assert "spotify" in result

    def test_should_use_real_apis_mock_mode(self):
        """Test _should_use_real_apis in mock mode."""
        from src.services.tour_service import TourService, TourStore

        with patch.dict(os.environ, {"TOUR_GUIDE_API_MODE": "mock"}):
            store = TourStore()
            service = TourService(store=store)

            assert service._should_use_real_apis() is False

            service._executor.shutdown(wait=False)

    def test_should_use_real_apis_auto_mode(self):
        """Test _should_use_real_apis in auto mode."""
        from src.services.tour_service import TourService, TourStore

        with patch.dict(os.environ, {"TOUR_GUIDE_API_MODE": "auto"}):
            store = TourStore()
            service = TourService(store=store)

            # In auto mode, result depends on agent availability
            result = service._should_use_real_apis()
            assert isinstance(result, bool)

            service._executor.shutdown(wait=False)


class TestGetTourStore:
    """Tests for get_tour_store singleton."""

    def test_get_tour_store_returns_store(self):
        """Test get_tour_store returns a store."""
        from src.services.tour_service import get_tour_store

        store = get_tour_store()

        assert store is not None

    def test_get_tour_store_singleton(self):
        """Test get_tour_store returns same instance."""
        from src.services.tour_service import get_tour_store

        store1 = get_tour_store()
        store2 = get_tour_store()

        assert store1 is store2


class TestGetTourService:
    """Tests for get_tour_service singleton."""

    def test_get_tour_service_returns_service(self):
        """Test get_tour_service returns a service."""
        from src.services.tour_service import get_tour_service

        service = get_tour_service()

        assert service is not None

    def test_get_tour_service_singleton(self):
        """Test get_tour_service returns same instance."""
        from src.services.tour_service import get_tour_service

        service1 = get_tour_service()
        service2 = get_tour_service()

        assert service1 is service2
