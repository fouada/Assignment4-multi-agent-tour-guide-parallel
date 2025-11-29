"""
Timer/Scheduler - Simulates live travel by triggering point arrivals at intervals.
Controls the pace of the tour guide experience.
"""
import threading
import time
from collections.abc import Callable

from src.models.route import Route, RoutePoint
from src.utils.config import settings
from src.utils.logger import get_logger, set_log_context

logger = get_logger(__name__)


def log_timer_tick(point_id: str, location: str):
    """Log timer tick for a point."""
    set_log_context(point_id=point_id, agent_type='timer')
    logger.info(f"⏰ Arrived at: {location}")


class TravelSimulator:
    """
    Simulates traveling along a route by emitting points at regular intervals.
    This creates the effect of "arriving" at each point along the journey.
    """

    def __init__(
        self,
        route: Route,
        interval_seconds: float = None,
        on_point_arrival: Callable[[RoutePoint], None] = None
    ):
        """
        Initialize the travel simulator.

        Args:
            route: The route to simulate traveling
            interval_seconds: Time between point arrivals
            on_point_arrival: Callback when arriving at a point
        """
        self.route = route
        self.interval = interval_seconds or settings.point_interval_seconds
        self.on_point_arrival = on_point_arrival

        self._current_index = 0
        self._thread: threading.Thread | None = None
        self._should_stop = threading.Event()
        self._is_paused = threading.Event()
        self._is_running = False

        set_log_context(agent_type='timer')
        logger.info(f"Timer initialized: {len(route.points)} points, {self.interval}s interval")

    @property
    def current_point(self) -> RoutePoint | None:
        """Get the current point."""
        if 0 <= self._current_index < len(self.route.points):
            return self.route.points[self._current_index]
        return None

    @property
    def progress(self) -> float:
        """Get progress as percentage (0-100)."""
        if not self.route.points:
            return 100.0
        return (self._current_index / len(self.route.points)) * 100

    @property
    def is_running(self) -> bool:
        return self._is_running and not self._should_stop.is_set()

    def start(self):
        """Start the travel simulation."""
        if self._is_running:
            logger.warning("Timer already running")
            return

        self._should_stop.clear()
        self._is_running = True

        self._thread = threading.Thread(
            target=self._simulation_loop,
            name="TravelSimulator",
            daemon=True
        )
        self._thread.start()

        set_log_context(agent_type='timer')
        logger.info(f"🚗 Travel simulation started: {self.route.source} → {self.route.destination}")

    def stop(self):
        """Stop the travel simulation."""
        self._should_stop.set()
        if self._thread:
            self._thread.join(timeout=5.0)
        self._is_running = False

        set_log_context(agent_type='timer')
        logger.info("🛑 Travel simulation stopped")

    def pause(self):
        """Pause the simulation."""
        self._is_paused.set()
        set_log_context(agent_type='timer')
        logger.info("⏸️ Travel simulation paused")

    def resume(self):
        """Resume the simulation."""
        self._is_paused.clear()
        set_log_context(agent_type='timer')
        logger.info("▶️ Travel simulation resumed")

    def skip_to_next(self):
        """Skip to the next point immediately."""
        if self._current_index < len(self.route.points) - 1:
            self._current_index += 1
            self._emit_current_point()

    def _simulation_loop(self):
        """Main simulation loop."""
        set_log_context(agent_type='timer')

        while not self._should_stop.is_set():
            # Check if paused
            if self._is_paused.is_set():
                time.sleep(0.1)
                continue

            # Check if we've reached the end
            if self._current_index >= len(self.route.points):
                logger.info("🏁 Reached destination!")
                self._is_running = False
                break

            # Emit current point
            self._emit_current_point()

            # Wait for interval or stop signal
            if self._should_stop.wait(timeout=self.interval):
                break

            # Move to next point
            self._current_index += 1

        self._is_running = False

    def _emit_current_point(self):
        """Emit the current point to the callback."""
        point = self.current_point
        if point and self.on_point_arrival:
            log_timer_tick(point.id, point.address)
            try:
                self.on_point_arrival(point)
            except Exception as e:
                logger.error(f"Point arrival callback error: {e}")


class InstantTravelSimulator:
    """
    Alternative simulator that processes all points immediately.
    Useful for testing or when you want results without waiting.
    """

    def __init__(
        self,
        route: Route,
        on_point_arrival: Callable[[RoutePoint], None] = None,
        delay_between_points: float = 0.0
    ):
        """
        Initialize instant simulator.

        Args:
            route: The route to process
            on_point_arrival: Callback for each point
            delay_between_points: Optional small delay between points
        """
        self.route = route
        self.on_point_arrival = on_point_arrival
        self.delay = delay_between_points

    def process_all(self) -> list[RoutePoint]:
        """
        Process all points immediately.

        Returns:
            List of processed points
        """
        set_log_context(agent_type='timer')
        logger.info(f"⚡ Instant processing: {len(self.route.points)} points")

        for point in self.route.points:
            log_timer_tick(point.id, point.address)

            if self.on_point_arrival:
                try:
                    self.on_point_arrival(point)
                except Exception as e:
                    logger.error(f"Point arrival callback error: {e}")

            if self.delay > 0:
                time.sleep(self.delay)

        logger.info("✅ All points processed")
        return self.route.points


class ScheduledPointEmitter:
    """
    Emits points based on a schedule or external triggers.
    Allows for more flexible control than time-based simulation.
    """

    def __init__(
        self,
        route: Route,
        on_point_arrival: Callable[[RoutePoint], None] = None
    ):
        self.route = route
        self.on_point_arrival = on_point_arrival
        self._emitted_indices = set()
        self._lock = threading.Lock()

    def emit_point(self, index: int) -> RoutePoint | None:
        """
        Emit a specific point by index.

        Args:
            index: Point index to emit

        Returns:
            The emitted point or None if invalid
        """
        with self._lock:
            if index < 0 or index >= len(self.route.points):
                logger.warning(f"Invalid point index: {index}")
                return None

            point = self.route.points[index]

            if index in self._emitted_indices:
                logger.warning(f"Point {index} already emitted")
                return point

            self._emitted_indices.add(index)

            log_timer_tick(point.id, point.address)

            if self.on_point_arrival:
                try:
                    self.on_point_arrival(point)
                except Exception as e:
                    logger.error(f"Point arrival callback error: {e}")

            return point

    def emit_next(self) -> RoutePoint | None:
        """Emit the next unemitted point."""
        with self._lock:
            for i in range(len(self.route.points)):
                if i not in self._emitted_indices:
                    return self.emit_point(i)
        return None

    def emit_all_remaining(self) -> list[RoutePoint]:
        """Emit all remaining unemitted points."""
        emitted = []
        while True:
            point = self.emit_next()
            if point is None:
                break
            emitted.append(point)
        return emitted

    @property
    def remaining_count(self) -> int:
        """Get count of unemitted points."""
        return len(self.route.points) - len(self._emitted_indices)

    @property
    def progress(self) -> float:
        """Get progress as percentage."""
        if not self.route.points:
            return 100.0
        return (len(self._emitted_indices) / len(self.route.points)) * 100

