"""
Agent Queue - Synchronization mechanism between content agents and judge.

Design Principles:
- The 3 content agents (video, music, text) work asynchronously
- We don't know which agent will finish first
- The judge can only make a decision AFTER all 3 agents have finished
- The queue collects results until it's "full" (all agents responded)

This is the synchronization point between parallel agents.
"""
import threading
import queue
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime
from enum import Enum

from models import ContentResult, RoutePoint, ContentType
from logger_setup import logger, set_log_context


class QueueStatus(str, Enum):
    """Status of the agent queue."""
    WAITING = "waiting"      # Waiting for agents to submit
    READY = "ready"          # All agents have submitted, ready for judge
    PROCESSING = "processing"  # Judge is processing
    COMPLETED = "completed"  # Judge has made decision


class AgentResultQueue:
    """
    Queue for collecting results from content agents.
    
    The judge waits until all expected agents have submitted their results.
    This ensures fair comparison between all content types.
    
    Architecture:
    
        ┌─────────────┐
        │ Video Agent │──┐
        └─────────────┘  │
                         │
        ┌─────────────┐  │    ┌─────────────────┐    ┌─────────────┐
        │ Music Agent │──┼───▶│  Result Queue   │───▶│   Judge     │
        └─────────────┘  │    │  (waits for 3)  │    │   Agent     │
                         │    └─────────────────┘    └─────────────┘
        ┌─────────────┐  │
        │ Text Agent  │──┘
        └─────────────┘
    """
    
    EXPECTED_AGENTS = 3  # video, music, text
    
    def __init__(
        self, 
        point: RoutePoint,
        on_ready: Optional[Callable[[List[ContentResult]], None]] = None,
        timeout_seconds: float = 30.0
    ):
        """
        Initialize the queue for a specific route point.
        
        Args:
            point: The route point this queue is for
            on_ready: Callback when all agents have submitted
            timeout_seconds: Maximum time to wait for all agents
        """
        self.point = point
        self.point_id = point.id
        self.on_ready = on_ready
        self.timeout = timeout_seconds
        
        # Internal queue and state
        self._queue = queue.Queue()
        self._results: Dict[ContentType, ContentResult] = {}
        self._lock = threading.Lock()
        self._ready_event = threading.Event()
        self._status = QueueStatus.WAITING
        
        # Tracking
        self.created_at = datetime.now()
        self.ready_at: Optional[datetime] = None
        self.submitted_agents: List[str] = []
        
        set_log_context(point_id=point.id, agent_type='queue')
        logger.info(f"📬 Queue created for point {point.index}: {point.address}")
    
    @property
    def status(self) -> QueueStatus:
        """Get current queue status."""
        return self._status
    
    @property
    def is_ready(self) -> bool:
        """Check if all agents have submitted."""
        with self._lock:
            return len(self._results) >= self.EXPECTED_AGENTS
    
    @property
    def pending_count(self) -> int:
        """Number of agents still pending."""
        with self._lock:
            return self.EXPECTED_AGENTS - len(self._results)
    
    @property
    def results(self) -> List[ContentResult]:
        """Get all submitted results."""
        with self._lock:
            return list(self._results.values())
    
    def submit(self, result: ContentResult) -> bool:
        """
        Submit a result from an agent.
        
        Args:
            result: The content result from an agent
            
        Returns:
            True if this was the last needed result (queue is now ready)
        """
        with self._lock:
            # Check if this content type already submitted
            if result.content_type in self._results:
                logger.warning(
                    f"⚠️ Duplicate submission from {result.content_type.value} agent - ignoring"
                )
                return False
            
            # Store result
            self._results[result.content_type] = result
            self.submitted_agents.append(result.content_type.value)
            
            logger.info(
                f"📥 Queue received {result.content_type.value}: {result.title[:30]}... "
                f"({len(self._results)}/{self.EXPECTED_AGENTS})"
            )
            
            # Check if ready
            if len(self._results) >= self.EXPECTED_AGENTS:
                self._status = QueueStatus.READY
                self.ready_at = datetime.now()
                self._ready_event.set()
                
                logger.info(f"✅ Queue READY - all {self.EXPECTED_AGENTS} agents submitted")
                
                # Notify callback
                if self.on_ready:
                    try:
                        self.on_ready(list(self._results.values()))
                    except Exception as e:
                        logger.error(f"Queue ready callback error: {e}")
                
                return True
            
            return False
    
    def wait_until_ready(self, timeout: float = None) -> bool:
        """
        Block until all agents have submitted.
        
        Args:
            timeout: Maximum time to wait (uses default if None)
            
        Returns:
            True if ready, False if timeout
        """
        timeout = timeout or self.timeout
        
        logger.info(f"⏳ Waiting for queue to be ready (timeout: {timeout}s)...")
        
        ready = self._ready_event.wait(timeout=timeout)
        
        if not ready:
            logger.warning(
                f"⏱️ Queue timeout! Only {len(self._results)}/{self.EXPECTED_AGENTS} agents submitted"
            )
            # Still mark as ready with partial results
            self._status = QueueStatus.READY
            self.ready_at = datetime.now()
        
        return ready
    
    def get_results_for_judge(self) -> List[ContentResult]:
        """
        Get results for the judge to evaluate.
        Marks the queue as processing.
        
        Returns:
            List of content results (may be less than expected if timeout)
        """
        with self._lock:
            self._status = QueueStatus.PROCESSING
            results = list(self._results.values())
            
            logger.info(f"⚖️ Passing {len(results)} results to judge")
            return results
    
    def mark_completed(self):
        """Mark the queue as completed after judge decision."""
        self._status = QueueStatus.COMPLETED
        logger.info(f"🏁 Queue completed for point {self.point.index}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        with self._lock:
            wait_time = None
            if self.ready_at:
                wait_time = (self.ready_at - self.created_at).total_seconds()
            
            return {
                'point_id': self.point_id,
                'point_index': self.point.index,
                'status': self._status.value,
                'submitted_count': len(self._results),
                'expected_count': self.EXPECTED_AGENTS,
                'submitted_agents': self.submitted_agents.copy(),
                'missing_agents': [
                    ct.value for ct in ContentType 
                    if ct not in self._results
                ],
                'wait_time_seconds': wait_time,
                'is_complete': len(self._results) >= self.EXPECTED_AGENTS
            }


class QueueManager:
    """
    Manages multiple queues for different route points.
    
    Each point gets its own queue, allowing parallel processing
    of multiple points while maintaining synchronization within each point.
    """
    
    def __init__(self):
        """Initialize the queue manager."""
        self._queues: Dict[str, AgentResultQueue] = {}
        self._lock = threading.Lock()
        
        logger.info("📮 Queue Manager initialized")
    
    def create_queue(
        self, 
        point: RoutePoint,
        on_ready: Optional[Callable] = None,
        timeout_seconds: float = 30.0
    ) -> AgentResultQueue:
        """
        Create a new queue for a route point.
        
        Args:
            point: The route point
            on_ready: Callback when queue is ready
            timeout_seconds: Timeout for agent submissions
            
        Returns:
            The created queue
        """
        with self._lock:
            if point.id in self._queues:
                logger.warning(f"Queue already exists for point {point.id}")
                return self._queues[point.id]
            
            q = AgentResultQueue(point, on_ready, timeout_seconds)
            self._queues[point.id] = q
            
            return q
    
    def get_queue(self, point_id: str) -> Optional[AgentResultQueue]:
        """Get queue for a specific point."""
        with self._lock:
            return self._queues.get(point_id)
    
    def submit_result(self, result: ContentResult) -> bool:
        """
        Submit a result to the appropriate queue.
        
        Args:
            result: Content result (contains point_id)
            
        Returns:
            True if queue is now ready
        """
        q = self.get_queue(result.point_id)
        if q:
            return q.submit(result)
        else:
            logger.error(f"No queue found for point {result.point_id}")
            return False
    
    def remove_queue(self, point_id: str):
        """Remove a completed queue."""
        with self._lock:
            if point_id in self._queues:
                del self._queues[point_id]
    
    def get_all_stats(self) -> List[Dict[str, Any]]:
        """Get stats for all queues."""
        with self._lock:
            return [q.get_stats() for q in self._queues.values()]
    
    @property
    def active_count(self) -> int:
        """Number of active queues."""
        with self._lock:
            return len(self._queues)


class SynchronizedPointProcessor:
    """
    Processes a single point using queue-based synchronization.
    
    This is the recommended pattern for multi-agent coordination:
    1. Create queue for the point
    2. Start 3 content agents in parallel
    3. Each agent submits to the queue when done
    4. Queue notifies when all 3 have submitted
    5. Judge evaluates all results together
    """
    
    def __init__(
        self,
        point: RoutePoint,
        user_profile: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize processor with queue synchronization.
        
        Args:
            point: Route point to process
            user_profile: Optional user preferences (e.g., "kids age 5")
        """
        from agents import VideoAgent, MusicAgent, TextAgent, JudgeAgent
        
        self.point = point
        self.user_profile = user_profile or {}
        
        # Create agents
        self.video_agent = VideoAgent()
        self.music_agent = MusicAgent()
        self.text_agent = TextAgent()
        self.judge_agent = JudgeAgent()
        
        # Create queue
        self.queue = AgentResultQueue(point)
        
        # Result storage
        self.decision = None
        self._completed = threading.Event()
    
    def process(self):
        """
        Process the point with queue synchronization.
        
        Flow:
        1. Start 3 agents in parallel threads
        2. Each agent submits result to queue
        3. Wait for queue to be ready
        4. Judge evaluates all results
        """
        from concurrent.futures import ThreadPoolExecutor
        
        set_log_context(point_id=self.point.id, agent_type='processor')
        logger.info(f"🎯 Starting synchronized processing for: {self.point.address}")
        
        # Start agents in parallel
        with ThreadPoolExecutor(max_workers=3, thread_name_prefix=f"Agent-{self.point.index}") as executor:
            # Submit agent tasks
            executor.submit(self._run_agent, self.video_agent)
            executor.submit(self._run_agent, self.music_agent)
            executor.submit(self._run_agent, self.text_agent)
            
            # Wait for queue to be ready (all agents submitted)
            self.queue.wait_until_ready()
        
        # Get results and run judge
        candidates = self.queue.get_results_for_judge()
        
        if candidates:
            self.decision = self.judge_agent.evaluate(self.point, candidates)
            logger.info(
                f"⚖️ Judge decision: {self.decision.selected_content.content_type.value} - "
                f"{self.decision.selected_content.title[:30]}..."
            )
        else:
            logger.error("No candidates for judge!")
        
        self.queue.mark_completed()
        self._completed.set()
        
        return self.decision
    
    def _run_agent(self, agent):
        """Run an agent and submit result to queue."""
        try:
            result = agent.execute(self.point)
            if result:
                self.queue.submit(result)
        except Exception as e:
            logger.error(f"Agent error: {e}")
    
    def wait_for_completion(self, timeout: float = None) -> bool:
        """Wait for processing to complete."""
        return self._completed.wait(timeout=timeout)

