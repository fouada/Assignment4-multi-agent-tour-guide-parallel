"""
Unit tests for the Timer/Scheduler module.

Tests cover:
- TravelSimulator initialization and lifecycle
- InstantTravelSimulator functionality
- ScheduledPointEmitter functionality
- Point arrival callbacks
- Progress tracking

MIT Level Testing - 85%+ Coverage Target
"""

import time
from unittest.mock import Mock, patch

import pytest

from src.models.route import Route, RoutePoint


@pytest.fixture
def sample_route():
    """Create a sample route for testing."""
    return Route(
        source="A",
        destination="B",
        points=[
            RoutePoint(
                id="p1",
                index=0,
                address="Point 1",
                location_name="Loc1",
                latitude=32.0,
                longitude=34.0,
            ),
            RoutePoint(
                id="p2",
                index=1,
                address="Point 2",
                location_name="Loc2",
                latitude=32.1,
                longitude=34.1,
            ),
            RoutePoint(
                id="p3",
                index=2,
                address="Point 3",
                location_name="Loc3",
                latitude=32.2,
                longitude=34.2,
            ),
        ],
        total_distance=3000,
        total_duration=180,
    )


class TestTravelSimulator:
    """Tests for TravelSimulator class."""

    def test_initialization(self, sample_route):
        """Test TravelSimulator initialization."""
        with patch("src.core.timer_scheduler.set_log_context", create=True):
            with patch("src.core.timer_scheduler.log_timer_tick", create=True):
                from src.core.timer_scheduler import TravelSimulator

                callback = Mock()
                simulator = TravelSimulator(
                    route=sample_route, interval_seconds=1.0, on_point_arrival=callback
                )

                assert simulator.route == sample_route
                assert simulator.interval == 1.0
                assert simulator.on_point_arrival == callback
                assert simulator._current_index == 0
                assert not simulator._is_running

    def test_current_point_property(self, sample_route):
        """Test current_point property."""
        with patch("src.core.timer_scheduler.set_log_context", create=True):
            with patch("src.core.timer_scheduler.log_timer_tick", create=True):
                from src.core.timer_scheduler import TravelSimulator

                simulator = TravelSimulator(route=sample_route, interval_seconds=0.1)

                assert simulator.current_point == sample_route.points[0]

                # Move to next
                simulator._current_index = 1
                assert simulator.current_point == sample_route.points[1]

    def test_current_point_out_of_range(self, sample_route):
        """Test current_point returns None when out of range."""
        with patch("src.core.timer_scheduler.set_log_context", create=True):
            with patch("src.core.timer_scheduler.log_timer_tick", create=True):
                from src.core.timer_scheduler import TravelSimulator

                simulator = TravelSimulator(route=sample_route, interval_seconds=0.1)

                simulator._current_index = 100  # Out of range
                assert simulator.current_point is None

    def test_progress_property(self, sample_route):
        """Test progress property."""
        with patch("src.core.timer_scheduler.set_log_context", create=True):
            with patch("src.core.timer_scheduler.log_timer_tick", create=True):
                from src.core.timer_scheduler import TravelSimulator

                simulator = TravelSimulator(route=sample_route, interval_seconds=0.1)

                assert simulator.progress == 0.0

                simulator._current_index = 1
                assert simulator.progress == pytest.approx(33.33, rel=0.1)

                simulator._current_index = 3
                assert simulator.progress == 100.0

    def test_is_running_property(self, sample_route):
        """Test is_running property."""
        with patch("src.core.timer_scheduler.set_log_context", create=True):
            with patch("src.core.timer_scheduler.log_timer_tick", create=True):
                from src.core.timer_scheduler import TravelSimulator

                simulator = TravelSimulator(route=sample_route, interval_seconds=0.1)

                assert not simulator.is_running

                simulator._is_running = True
                simulator._should_stop.clear()
                assert simulator.is_running

                simulator._should_stop.set()
                assert not simulator.is_running

    def test_start_stop(self, sample_route):
        """Test start and stop lifecycle."""
        with patch("src.core.timer_scheduler.set_log_context", create=True):
            with patch("src.core.timer_scheduler.log_timer_tick", create=True):
                from src.core.timer_scheduler import TravelSimulator

                callback = Mock()
                simulator = TravelSimulator(
                    route=sample_route, interval_seconds=0.1, on_point_arrival=callback
                )

                simulator.start()
                assert simulator._is_running

                time.sleep(0.2)  # Let it run briefly

                simulator.stop()
                assert not simulator._is_running

    def test_start_when_already_running(self, sample_route):
        """Test starting when already running does nothing."""
        with patch("src.core.timer_scheduler.set_log_context", create=True):
            with patch("src.core.timer_scheduler.log_timer_tick", create=True):
                from src.core.timer_scheduler import TravelSimulator

                simulator = TravelSimulator(route=sample_route, interval_seconds=1.0)

                simulator._is_running = True
                thread_before = simulator._thread

                simulator.start()

                # Thread should not change
                assert simulator._thread == thread_before

    def test_pause_resume(self, sample_route):
        """Test pause and resume functionality."""
        with patch("src.core.timer_scheduler.set_log_context", create=True):
            with patch("src.core.timer_scheduler.log_timer_tick", create=True):
                from src.core.timer_scheduler import TravelSimulator

                simulator = TravelSimulator(route=sample_route, interval_seconds=0.1)

                simulator.start()
                time.sleep(0.15)

                simulator.pause()
                assert simulator._is_paused.is_set()

                simulator.resume()
                assert not simulator._is_paused.is_set()

                simulator.stop()

    def test_skip_to_next(self, sample_route):
        """Test skip_to_next functionality."""
        with patch("src.core.timer_scheduler.set_log_context", create=True):
            with patch("src.core.timer_scheduler.log_timer_tick", create=True):
                from src.core.timer_scheduler import TravelSimulator

                callback = Mock()
                simulator = TravelSimulator(
                    route=sample_route, interval_seconds=1.0, on_point_arrival=callback
                )

                assert simulator._current_index == 0

                simulator.skip_to_next()

                assert simulator._current_index == 1
                callback.assert_called_once()

    def test_skip_at_end_does_nothing(self, sample_route):
        """Test skip at end does nothing."""
        with patch("src.core.timer_scheduler.set_log_context", create=True):
            with patch("src.core.timer_scheduler.log_timer_tick", create=True):
                from src.core.timer_scheduler import TravelSimulator

                simulator = TravelSimulator(route=sample_route, interval_seconds=1.0)

                # Move to last point
                simulator._current_index = len(sample_route.points) - 1

                simulator.skip_to_next()

                # Should not change
                assert simulator._current_index == len(sample_route.points) - 1

    def test_callback_error_handled(self, sample_route):
        """Test callback errors are handled gracefully."""
        with patch("src.core.timer_scheduler.set_log_context", create=True):
            with patch("src.core.timer_scheduler.log_timer_tick", create=True):
                from src.core.timer_scheduler import TravelSimulator

                callback = Mock(side_effect=Exception("Callback error"))
                simulator = TravelSimulator(
                    route=sample_route, interval_seconds=0.1, on_point_arrival=callback
                )

                # Should not raise
                simulator._emit_current_point()

    def test_emit_no_callback(self, sample_route):
        """Test emit with no callback."""
        with patch("src.core.timer_scheduler.set_log_context", create=True):
            with patch("src.core.timer_scheduler.log_timer_tick", create=True):
                from src.core.timer_scheduler import TravelSimulator

                simulator = TravelSimulator(route=sample_route, interval_seconds=0.1)

                # Should not raise
                simulator._emit_current_point()


class TestInstantTravelSimulator:
    """Tests for InstantTravelSimulator class."""

    def test_initialization(self, sample_route):
        """Test InstantTravelSimulator initialization."""
        from src.core.timer_scheduler import InstantTravelSimulator

        callback = Mock()
        simulator = InstantTravelSimulator(
            route=sample_route, on_point_arrival=callback, delay_between_points=0.1
        )

        assert simulator.route == sample_route
        assert simulator.on_point_arrival == callback
        assert simulator.delay == 0.1

    def test_process_all(self, sample_route):
        """Test process_all returns all points."""
        with patch("src.core.timer_scheduler.set_log_context", create=True):
            with patch("src.core.timer_scheduler.log_timer_tick", create=True):
                from src.core.timer_scheduler import InstantTravelSimulator

                callback = Mock()
                simulator = InstantTravelSimulator(
                    route=sample_route, on_point_arrival=callback
                )

                points = simulator.process_all()

                assert len(points) == len(sample_route.points)
                assert callback.call_count == len(sample_route.points)

    def test_process_all_with_delay(self, sample_route):
        """Test process_all with delay."""
        with patch("src.core.timer_scheduler.set_log_context", create=True):
            with patch("src.core.timer_scheduler.log_timer_tick", create=True):
                from src.core.timer_scheduler import InstantTravelSimulator

                simulator = InstantTravelSimulator(
                    route=sample_route, delay_between_points=0.05
                )

                start = time.time()
                simulator.process_all()
                elapsed = time.time() - start

                # Should take at least delay * (points - 1)
                expected_min = 0.05 * (len(sample_route.points) - 1)
                assert elapsed >= expected_min * 0.8  # Allow some tolerance

    def test_process_all_callback_error(self, sample_route):
        """Test process_all handles callback errors."""
        with patch("src.core.timer_scheduler.set_log_context", create=True):
            with patch("src.core.timer_scheduler.log_timer_tick", create=True):
                from src.core.timer_scheduler import InstantTravelSimulator

                callback = Mock(side_effect=Exception("Error"))
                simulator = InstantTravelSimulator(
                    route=sample_route, on_point_arrival=callback
                )

                # Should not raise
                points = simulator.process_all()
                assert len(points) == len(sample_route.points)

    def test_process_all_no_callback(self, sample_route):
        """Test process_all without callback."""
        with patch("src.core.timer_scheduler.set_log_context", create=True):
            with patch("src.core.timer_scheduler.log_timer_tick", create=True):
                from src.core.timer_scheduler import InstantTravelSimulator

                simulator = InstantTravelSimulator(route=sample_route)

                points = simulator.process_all()
                assert len(points) == len(sample_route.points)


class TestScheduledPointEmitter:
    """Tests for ScheduledPointEmitter class."""

    def test_initialization(self, sample_route):
        """Test ScheduledPointEmitter initialization."""
        from src.core.timer_scheduler import ScheduledPointEmitter

        callback = Mock()
        emitter = ScheduledPointEmitter(route=sample_route, on_point_arrival=callback)

        assert emitter.route == sample_route
        assert emitter.on_point_arrival == callback
        assert len(emitter._emitted_indices) == 0

    def test_emit_point_valid(self, sample_route):
        """Test emitting a valid point."""
        with patch("src.core.timer_scheduler.log_timer_tick", create=True):
            from src.core.timer_scheduler import ScheduledPointEmitter

            callback = Mock()
            emitter = ScheduledPointEmitter(
                route=sample_route, on_point_arrival=callback
            )

            point = emitter.emit_point(0)

            assert point == sample_route.points[0]
            callback.assert_called_once_with(sample_route.points[0])
            assert 0 in emitter._emitted_indices

    def test_emit_point_invalid_index(self, sample_route):
        """Test emitting with invalid index."""
        from src.core.timer_scheduler import ScheduledPointEmitter

        emitter = ScheduledPointEmitter(route=sample_route)

        # Negative index
        point = emitter.emit_point(-1)
        assert point is None

        # Out of range
        point = emitter.emit_point(100)
        assert point is None

    def test_emit_point_already_emitted(self, sample_route):
        """Test emitting already emitted point."""
        with patch("src.core.timer_scheduler.log_timer_tick", create=True):
            from src.core.timer_scheduler import ScheduledPointEmitter

            callback = Mock()
            emitter = ScheduledPointEmitter(
                route=sample_route, on_point_arrival=callback
            )

            # Emit once
            emitter.emit_point(0)

            # Emit again
            point = emitter.emit_point(0)

            assert point == sample_route.points[0]
            assert callback.call_count == 1  # Only called once

    def test_emit_next(self, sample_route):
        """Test emit_next functionality."""
        with patch("src.core.timer_scheduler.log_timer_tick", create=True):
            from src.core.timer_scheduler import ScheduledPointEmitter

            callback = Mock()
            emitter = ScheduledPointEmitter(
                route=sample_route, on_point_arrival=callback
            )

            # First call
            point1 = emitter.emit_next()
            assert point1 == sample_route.points[0]

            # Second call
            point2 = emitter.emit_next()
            assert point2 == sample_route.points[1]

    def test_emit_next_when_all_emitted(self, sample_route):
        """Test emit_next returns None when all emitted."""
        with patch("src.core.timer_scheduler.log_timer_tick", create=True):
            from src.core.timer_scheduler import ScheduledPointEmitter

            emitter = ScheduledPointEmitter(route=sample_route)

            # Emit all
            for _ in sample_route.points:
                emitter.emit_next()

            # Next should return None
            point = emitter.emit_next()
            assert point is None

    def test_emit_all_remaining(self, sample_route):
        """Test emit_all_remaining functionality."""
        with patch("src.core.timer_scheduler.log_timer_tick", create=True):
            from src.core.timer_scheduler import ScheduledPointEmitter

            emitter = ScheduledPointEmitter(route=sample_route)

            # Emit first one
            emitter.emit_point(0)

            # Emit remaining
            remaining = emitter.emit_all_remaining()

            assert len(remaining) == len(sample_route.points) - 1

    def test_remaining_count(self, sample_route):
        """Test remaining_count property."""
        with patch("src.core.timer_scheduler.log_timer_tick", create=True):
            from src.core.timer_scheduler import ScheduledPointEmitter

            emitter = ScheduledPointEmitter(route=sample_route)

            assert emitter.remaining_count == len(sample_route.points)

            emitter.emit_point(0)
            assert emitter.remaining_count == len(sample_route.points) - 1

    def test_progress(self, sample_route):
        """Test progress property."""
        with patch("src.core.timer_scheduler.log_timer_tick", create=True):
            from src.core.timer_scheduler import ScheduledPointEmitter

            emitter = ScheduledPointEmitter(route=sample_route)

            assert emitter.progress == 0.0

            emitter.emit_point(0)
            expected = (1 / len(sample_route.points)) * 100
            assert emitter.progress == pytest.approx(expected)

    def test_progress_empty_route(self):
        """Test progress with empty route."""
        from src.core.timer_scheduler import ScheduledPointEmitter

        empty_route = Route(
            source="A", destination="B", points=[], total_distance=0, total_duration=0
        )

        emitter = ScheduledPointEmitter(route=empty_route)
        assert emitter.progress == 100.0

    def test_callback_error_handled(self, sample_route):
        """Test callback error is handled."""
        with patch("src.core.timer_scheduler.log_timer_tick", create=True):
            from src.core.timer_scheduler import ScheduledPointEmitter

            callback = Mock(side_effect=Exception("Error"))
            emitter = ScheduledPointEmitter(
                route=sample_route, on_point_arrival=callback
            )

            # Should not raise
            point = emitter.emit_point(0)
            assert point == sample_route.points[0]


class TestEmptyRoute:
    """Test edge cases with empty routes."""

    def test_travel_simulator_empty_route(self):
        """Test TravelSimulator with empty route."""
        with patch("src.core.timer_scheduler.set_log_context", create=True):
            with patch("src.core.timer_scheduler.log_timer_tick", create=True):
                from src.core.timer_scheduler import TravelSimulator

                empty_route = Route(
                    source="A",
                    destination="B",
                    points=[],
                    total_distance=0,
                    total_duration=0,
                )

                simulator = TravelSimulator(route=empty_route, interval_seconds=0.1)

                assert simulator.progress == 100.0
                assert simulator.current_point is None

    def test_instant_simulator_empty_route(self):
        """Test InstantTravelSimulator with empty route."""
        with patch("src.core.timer_scheduler.set_log_context", create=True):
            with patch("src.core.timer_scheduler.log_timer_tick", create=True):
                from src.core.timer_scheduler import InstantTravelSimulator

                empty_route = Route(
                    source="A",
                    destination="B",
                    points=[],
                    total_distance=0,
                    total_duration=0,
                )

                simulator = InstantTravelSimulator(route=empty_route)
                points = simulator.process_all()

                assert points == []
