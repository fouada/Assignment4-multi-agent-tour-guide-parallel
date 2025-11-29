"""
Orchestrator - Manages the parallel execution of agents for each route point.
Coordinates multithreading and ensures proper synchronization.
"""
import queue
import threading
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from datetime import datetime

from src.agents.judge_agent import JudgeAgent
from src.agents.music_agent import MusicAgent
from src.agents.text_agent import TextAgent
from src.agents.video_agent import VideoAgent
from src.models.content import ContentResult
from src.models.decision import JudgeDecision
from src.models.route import RoutePoint
from src.utils.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PointProcessor:
    """
    Processes a single route point by running all agents in parallel.
    Each point gets its own set of agents running in separate threads.
    """

    def __init__(self, point: RoutePoint, result_callback: Callable[[JudgeDecision], None]):
        """
        Initialize processor for a single point.

        Args:
            point: The route point to process
            result_callback: Callback to invoke when processing is complete
        """
        self.point = point
        self.result_callback = result_callback
        self.content_results: list[ContentResult] = []
        self.decision: JudgeDecision | None = None
        self.lock = threading.Lock()
        self.completed = threading.Event()
        self.started_at: datetime | None = None
        self.completed_at: datetime | None = None

    def process(self):
        """
        Process the point by running all content agents in parallel,
        then running the judge on the results.
        """
        self.started_at = datetime.now()
        set_log_context(point_id=self.point.id, agent_type='orchestrator')

        logger.info(f"🎯 Starting processing for point {self.point.index}: {self.point.address}")

        # Create agents
        video_agent = VideoAgent()
        music_agent = MusicAgent()
        text_agent = TextAgent()
        judge_agent = JudgeAgent()

        # Run content agents in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=3, thread_name_prefix=f"Agent-P{self.point.index}") as executor:
            # Submit all agent tasks
            futures = {
                executor.submit(self._run_agent, video_agent): 'video',
                executor.submit(self._run_agent, music_agent): 'music',
                executor.submit(self._run_agent, text_agent): 'text',
            }

            # Collect results as they complete
            for future in as_completed(futures, timeout=settings.agent_timeout_seconds):
                agent_type = futures[future]
                try:
                    result = future.result()
                    if result:
                        with self.lock:
                            self.content_results.append(result)
                        logger.info(f"✅ {agent_type} agent completed for point {self.point.index}")
                except Exception as e:
                    logger.error(f"❌ {agent_type} agent failed: {e}")

        # Run judge on collected results
        if self.content_results:
            try:
                self.decision = judge_agent.evaluate(self.point, self.content_results)
                logger.info(
                    f"⚖️ Judge selected: {self.decision.selected_content.content_type.value} "
                    f"for point {self.point.index}"
                )
            except Exception as e:
                logger.error(f"Judge failed for point {self.point.index}: {e}")
                # Fallback: use the first result
                if self.content_results:
                    self.decision = JudgeDecision(
                        point_id=self.point.id,
                        selected_content=self.content_results[0],
                        all_candidates=self.content_results,
                        reasoning="Judge failed - using first available content",
                        scores={}
                    )

        self.completed_at = datetime.now()
        duration = (self.completed_at - self.started_at).total_seconds()
        logger.info(f"🏁 Point {self.point.index} completed in {duration:.2f}s")

        # Notify completion via callback
        if self.decision and self.result_callback:
            self.result_callback(self.decision)

        self.completed.set()

    def _run_agent(self, agent) -> ContentResult | None:
        """Run a single agent and return its result."""
        try:
            return agent.execute(self.point)
        except Exception as e:
            logger.error(f"Agent execution error: {e}")
            return None


class Orchestrator:
    """
    Main orchestrator that coordinates the processing of all route points.
    Manages thread pools and ensures proper parallel execution.
    """

    def __init__(self, max_concurrent_points: int = None):
        """
        Initialize the orchestrator.

        Args:
            max_concurrent_points: Maximum number of points to process simultaneously
        """
        self.max_concurrent_points = max_concurrent_points or (settings.max_concurrent_threads // 4)
        self.active_processors: dict[str, PointProcessor] = {}
        self.results: dict[str, JudgeDecision] = {}
        self.results_lock = threading.Lock()
        self.results_queue = queue.Queue()
        self.executor: ThreadPoolExecutor | None = None
        self.is_running = False
        self._futures: dict[Future, str] = {}

        log_orchestrator_event("Initialized", f"max_concurrent_points={self.max_concurrent_points}")

    def _on_point_complete(self, decision: JudgeDecision):
        """Callback when a point processing is complete."""
        with self.results_lock:
            self.results[decision.point_id] = decision
        self.results_queue.put(decision)
        log_orchestrator_event(
            "Point completed",
            f"point_id={decision.point_id}, content={decision.selected_content.title[:30]}..."
        )

    def process_point(self, point: RoutePoint):
        """
        Submit a single point for processing.

        Args:
            point: The route point to process
        """
        if not self.is_running:
            self.start()

        processor = PointProcessor(point, self._on_point_complete)
        self.active_processors[point.id] = processor

        future = self.executor.submit(processor.process)
        self._futures[future] = point.id

        log_orchestrator_event("Point submitted", f"point_id={point.id}, index={point.index}")

    def process_points(self, points: list[RoutePoint]) -> list[JudgeDecision]:
        """
        Process multiple points in parallel.

        Args:
            points: List of route points to process

        Returns:
            List of judge decisions in order
        """
        log_orchestrator_event("Batch processing started", f"{len(points)} points")

        self.start()

        try:
            # Submit all points
            for point in points:
                self.process_point(point)

            # Wait for all to complete
            self.wait_for_completion()

            # Return results in order
            ordered_results = []
            for point in points:
                if point.id in self.results:
                    ordered_results.append(self.results[point.id])

            return ordered_results

        finally:
            self.stop()

    def start(self):
        """Start the orchestrator's thread pool."""
        if not self.is_running:
            self.executor = ThreadPoolExecutor(
                max_workers=self.max_concurrent_points,
                thread_name_prefix="PointProcessor"
            )
            self.is_running = True
            log_orchestrator_event("Started", f"thread_pool_size={self.max_concurrent_points}")

    def stop(self):
        """Stop the orchestrator and cleanup."""
        if self.is_running:
            self.executor.shutdown(wait=True)
            self.is_running = False
            log_orchestrator_event("Stopped")

    def wait_for_completion(self, timeout: float = None):
        """
        Wait for all submitted points to complete.

        Args:
            timeout: Maximum time to wait in seconds
        """
        for future in as_completed(self._futures.keys(), timeout=timeout):
            point_id = self._futures[future]
            try:
                future.result()
            except Exception as e:
                logger.error(f"Point {point_id} processing failed: {e}")

    def get_result(self, point_id: str) -> JudgeDecision | None:
        """Get the result for a specific point."""
        with self.results_lock:
            return self.results.get(point_id)

    def get_next_result(self, timeout: float = None) -> JudgeDecision | None:
        """
        Get the next completed result from the queue.
        Useful for streaming results as they complete.

        Args:
            timeout: Maximum time to wait

        Returns:
            JudgeDecision or None if timeout
        """
        try:
            return self.results_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def get_stats(self) -> dict:
        """Get current processing statistics."""
        active_count = sum(1 for p in self.active_processors.values() if not p.completed.is_set())
        completed_count = len(self.results)

        return {
            'active_points': active_count,
            'completed_points': completed_count,
            'pending_points': len(self.active_processors) - active_count - completed_count,
            'is_running': self.is_running
        }


class StreamingOrchestrator(Orchestrator):
    """
    Extended orchestrator that supports streaming point processing.
    Points can be added dynamically as the timer triggers new locations.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._point_queue = queue.Queue()
        self._processing_thread: threading.Thread | None = None
        self._should_stop = threading.Event()

    def add_point(self, point: RoutePoint):
        """Add a point to the processing queue."""
        self._point_queue.put(point)
        log_orchestrator_event("Point queued", f"point_id={point.id}")

    def start_streaming(self):
        """Start processing points as they arrive."""
        self.start()
        self._should_stop.clear()

        self._processing_thread = threading.Thread(
            target=self._processing_loop,
            name="StreamingProcessor",
            daemon=True
        )
        self._processing_thread.start()
        log_orchestrator_event("Streaming started")

    def stop_streaming(self):
        """Stop the streaming processor."""
        self._should_stop.set()
        if self._processing_thread:
            self._processing_thread.join(timeout=5.0)
        self.stop()
        log_orchestrator_event("Streaming stopped")

    def _processing_loop(self):
        """Main loop for processing queued points."""
        while not self._should_stop.is_set():
            try:
                point = self._point_queue.get(timeout=1.0)
                self.process_point(point)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Streaming processing error: {e}")

