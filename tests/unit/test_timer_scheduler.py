"""
Unit tests for Timer/Scheduler module.

Tests cover:
- TravelSimulator lifecycle (start, stop, pause, resume)
- Point emission and callbacks
- InstantTravelSimulator for immediate processing
- ScheduledPointEmitter for controlled emission
- Edge cases: empty routes, callback errors

MIT Level Testing - 85%+ Coverage Target
"""

import threading
import time
from unittest.mock import Mock

import pytest

from src.core.timer_scheduler import (
    InstantTravelSimulator,
    ScheduledPointEmitter,
    TravelSimulator,
    log_timer_tick,
)
from src.models.route import Route, RoutePoint


@pytest.fixture
def sample_route():
    """Create a sample route for testing."""
    return Route(
        source="Start",
        destination="End",
        points=[
            RoutePoint(
                id=f"point_{i}",
                index=i,
                address=f"Address {i}",
                location_name=f"Location {i}",
                latitude=32.0 + i * 0.1,
                longitude=34.0 + i * 0.1,
            )
            for i in range(5)
        ],
        total_distance=10000,
        total_duration=600,
    )


@pytest.fixture
def empty_route():
    """Create an empty route for edge case testing."""
    return Route(
        source="Start",
        destination="End",
        points=[],
        total_distance=0,
        total_duration=0,
    )


@pytest.fixture
def single_point_route():
    """Create a route with just one point."""
    return Route(
        source="Start",
        destination="End",
        points=[
            RoutePoint(
                id="single_point",
                index=0,
                address="Single Address",
                location_name="Single Location",
                latitude=32.0,
                longitude=34.0,
            )
        ],
        total_distance=1000,
        total_duration=60,
    )


class TestLogTimerTick:
    """Tests for log_timer_tick function."""

    def test_log_timer_tick_executes(self):
        """Test log_timer_tick doesn't raise."""
        log_timer_tick("test_point", "Test Location")


class TestTravelSimulator:
    """Tests for TravelSimulator class."""

    def test_initialization(self, sample_route):
        """Test TravelSimulator initialization."""
        simulator = TravelSimulator(sample_route, interval_seconds=1.0)
        assert simulator.route == sample_route
        assert simulator.interval == 1.0
        assert simulator._current_index == 0
        assert not simulator.is_running

    def test_initialization_with_callback(self, sample_route):
        """Test initialization with callback."""
        callback = Mock()
        simulator = TravelSimulator(
            sample_route,
            interval_seconds=0.1,
            on_point_arrival=callback,
        )
        assert simulator.on_point_arrival == callback

    def test_current_point_initial(self, sample_route):
        """Test current_point returns first point initially."""
        simulator = TravelSimulator(sample_route)
        assert simulator.current_point == sample_route.points[0]

    def test_current_point_empty_route(self, empty_route):
        """Test current_point returns None for empty route."""
        simulator = TravelSimulator(empty_route)
        assert simulator.current_point is None

    def test_progress_initial(self, sample_route):
        """Test progress is 0% initially."""
        simulator = TravelSimulator(sample_route)
        assert simulator.progress == 0.0

    def test_progress_empty_route(self, empty_route):
        """Test progress is 100% for empty route."""
        simulator = TravelSimulator(empty_route)
        assert simulator.progress == 100.0

    def test_start_stop(self, sample_route):
        """Test start and stop lifecycle."""
        simulator = TravelSimulator(sample_route, interval_seconds=10.0)
        assert not simulator.is_running
        simulator.start()
        assert simulator.is_running
        simulator.stop()
        assert not simulator.is_running

    def test_start_already_running(self, sample_route):
        """Test starting when already running."""
        simulator = TravelSimulator(sample_route, interval_seconds=10.0)
        simulator.start()
        simulator.start()  # Should log warning but not raise
        simulator.stop()

    def test_pause_resume(self, sample_route):
        """Test pause and resume."""
        simulator = TravelSimulator(sample_route, interval_seconds=10.0)
        simulator.start()
        simulator.pause()
        assert simulator._is_paused.is_set()
        simulator.resume()
        assert not simulator._is_paused.is_set()
        simulator.stop()

    def test_skip_to_next(self, sample_route):
        """Test skip_to_next advances index."""
        callback = Mock()
        simulator = TravelSimulator(
            sample_route,
            interval_seconds=10.0,
            on_point_arrival=callback,
        )
        initial_index = simulator._current_index
        simulator.skip_to_next()
        assert simulator._current_index == initial_index + 1
        callback.assert_called_once()

    def test_skip_to_next_at_end(self, single_point_route):
        """Test skip_to_next at last point does nothing."""
        simulator = TravelSimulator(single_point_route)
        simulator.skip_to_next()
        assert simulator._current_index == 0  # Unchanged

    def test_point_emission_with_callback(self, sample_route):
        """Test points are emitted to callback."""
        received_points = []

        def callback(point):
            received_points.append(point)

        simulator = TravelSimulator(
            sample_route,
            interval_seconds=0.01,
            on_point_arrival=callback,
        )
        simulator.start()
        time.sleep(0.1)
        simulator.stop()
        assert len(received_points) > 0
        assert received_points[0] == sample_route.points[0]

    def test_callback_error_handling(self, sample_route):
        """Test callback errors are handled gracefully."""

        def failing_callback(point):
            raise Exception("Callback error")

        simulator = TravelSimulator(
            sample_route,
            interval_seconds=0.01,
            on_point_arrival=failing_callback,
        )
        simulator.start()
        time.sleep(0.05)
        simulator.stop()

    def test_simulation_completes_naturally(self, single_point_route):
        """Test simulation stops when reaching destination."""
        callback = Mock()
        simulator = TravelSimulator(
            single_point_route,
            interval_seconds=0.01,
            on_point_arrival=callback,
        )
        simulator.start()
        time.sleep(0.1)
        assert not simulator.is_running


class TestInstantTravelSimulator:
    """Tests for InstantTravelSimulator class."""

    def test_initialization(self, sample_route):
        """Test InstantTravelSimulator initialization."""
        simulator = InstantTravelSimulator(sample_route)
        assert simulator.route == sample_route
        assert simulator.delay == 0.0

    def test_initialization_with_delay(self, sample_route):
        """Test initialization with delay."""
        simulator = InstantTravelSimulator(sample_route, delay_between_points=0.1)
        assert simulator.delay == 0.1

    def test_process_all_returns_all_points(self, sample_route):
        """Test process_all returns all points."""
        simulator = InstantTravelSimulator(sample_route)
        result = simulator.process_all()
        assert result == sample_route.points
        assert len(result) == 5

    def test_process_all_calls_callback(self, sample_route):
        """Test process_all calls callback for each point."""
        callback = Mock()
        simulator = InstantTravelSimulator(sample_route, on_point_arrival=callback)
        simulator.process_all()
        assert callback.call_count == 5

    def test_process_all_empty_route(self, empty_route):
        """Test process_all with empty route."""
        callback = Mock()
        simulator = InstantTravelSimulator(empty_route, on_point_arrival=callback)
        result = simulator.process_all()
        assert result == []
        callback.assert_not_called()

    def test_process_all_with_delay(self, single_point_route):
        """Test process_all respects delay."""
        simulator = InstantTravelSimulator(
            single_point_route,
            delay_between_points=0.01,
        )
        start = time.time()
        simulator.process_all()
        elapsed = time.time() - start
        assert elapsed >= 0.01

    def test_callback_error_handling(self, sample_route):
        """Test callback errors are handled."""

        def failing_callback(point):
            raise Exception("Callback error")

        simulator = InstantTravelSimulator(
            sample_route,
            on_point_arrival=failing_callback,
        )
        result = simulator.process_all()
        assert len(result) == 5


class TestScheduledPointEmitter:
    """Tests for ScheduledPointEmitter class."""

    def test_initialization(self, sample_route):
        """Test ScheduledPointEmitter initialization."""
        emitter = ScheduledPointEmitter(sample_route)
        assert emitter.route == sample_route
        assert emitter.remaining_count == 5
        assert emitter.progress == 0.0

    def test_emit_point_valid_index(self, sample_route):
        """Test emit_point with valid index."""
        callback = Mock()
        emitter = ScheduledPointEmitter(sample_route, on_point_arrival=callback)
        result = emitter.emit_point(0)
        assert result == sample_route.points[0]
        callback.assert_called_once_with(sample_route.points[0])

    def test_emit_point_invalid_index(self, sample_route):
        """Test emit_point with invalid index."""
        emitter = ScheduledPointEmitter(sample_route)
        result = emitter.emit_point(-1)
        assert result is None
        result = emitter.emit_point(100)
        assert result is None

    def test_emit_point_duplicate(self, sample_route):
        """Test emit_point for already emitted point."""
        callback = Mock()
        emitter = ScheduledPointEmitter(sample_route, on_point_arrival=callback)
        emitter.emit_point(0)
        result = emitter.emit_point(0)  # Duplicate
        assert result == sample_route.points[0]
        assert callback.call_count == 1

    def test_emit_next(self, sample_route):
        """Test emit_next emits sequentially."""
        emitter = ScheduledPointEmitter(sample_route)
        for i in range(5):
            result = emitter.emit_next()
            assert result == sample_route.points[i]
        result = emitter.emit_next()
        assert result is None

    def test_emit_all_remaining(self, sample_route):
        """Test emit_all_remaining."""
        emitter = ScheduledPointEmitter(sample_route)
        emitter.emit_point(0)
        emitter.emit_point(1)
        result = emitter.emit_all_remaining()
        assert len(result) == 3
        assert emitter.remaining_count == 0
        assert emitter.progress == 100.0

    def test_progress_tracking(self, sample_route):
        """Test progress updates correctly."""
        emitter = ScheduledPointEmitter(sample_route)
        assert emitter.progress == 0.0
        emitter.emit_point(0)
        assert emitter.progress == 20.0
        emitter.emit_point(1)
        assert emitter.progress == 40.0

    def test_remaining_count(self, sample_route):
        """Test remaining_count decreases."""
        emitter = ScheduledPointEmitter(sample_route)
        assert emitter.remaining_count == 5
        emitter.emit_point(0)
        assert emitter.remaining_count == 4
        emitter.emit_all_remaining()
        assert emitter.remaining_count == 0

    def test_progress_empty_route(self, empty_route):
        """Test progress for empty route."""
        emitter = ScheduledPointEmitter(empty_route)
        assert emitter.progress == 100.0

    def test_callback_error_handling(self, sample_route):
        """Test callback errors are handled."""

        def failing_callback(point):
            raise Exception("Callback error")

        emitter = ScheduledPointEmitter(
            sample_route,
            on_point_arrival=failing_callback,
        )
        result = emitter.emit_point(0)
        assert result is not None

    def test_thread_safety(self, sample_route):
        """Test thread-safe emission."""
        emitter = ScheduledPointEmitter(sample_route)
        emitted = []
        lock = threading.Lock()

        def emit_worker():
            for _ in range(10):
                result = emitter.emit_next()
                if result:
                    with lock:
                        emitted.append(result)

        threads = [threading.Thread(target=emit_worker) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert len(emitted) == 5
