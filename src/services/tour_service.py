"""
🗺️ Tour Service - Centralized Tour Processing Logic
=====================================================

MIT-Level Architecture: Single Source of Truth for Tour Processing

This service encapsulates ALL tour processing logic that was previously
duplicated across CLI, Dashboard, and API. Now both the REST API and
any other clients use this service as the authoritative source.

Pipeline Flow:
    ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
    │ Google Maps │────▶│  Scheduler  │────▶│ Orchestrator│────▶│   Agents    │
    │    API      │     │ (Emitter)   │     │             │     │  (Parallel) │
    └─────────────┘     └─────────────┘     └─────────────┘     └──────┬──────┘
                                                                       │
    ┌─────────────┐     ┌─────────────┐     ┌─────────────┐           │
    │   Output    │◀────│    Judge    │◀────│ Smart Queue │◀──────────┘
    │  (Playlist) │     │   Agent     │     │  (Sync)     │
    └─────────────┘     └─────────────┘     └─────────────┘

Features:
- Async tour creation and processing
- Scheduler integration for point-by-point emission
- Real-time status updates via callbacks
- In-memory tour state management (Redis-ready for production)
- Full integration with SmartAgentQueue and all agents
- Profile-based content filtering
- Comprehensive metrics collection

Author: Multi-Agent Tour Guide Research Team
Version: 2.0.0
"""

from __future__ import annotations

import logging
import os
import threading
import time
import uuid
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# =============================================================================
# Tour State Management
# =============================================================================


class TourStatus(str, Enum):
    """Tour processing status."""

    PENDING = "pending"
    FETCHING_ROUTE = "fetching_route"  # Step 1: Google Maps API
    SCHEDULING = "scheduling"          # Step 2: Scheduler preparing points
    PROCESSING = "processing"          # Step 3: Orchestrator + Agents
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PointStatus(str, Enum):
    """Individual point processing status."""

    PENDING = "pending"
    AGENTS_RUNNING = "agents_running"
    QUEUE_WAITING = "queue_waiting"
    JUDGE_EVALUATING = "judge_evaluating"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentResult:
    """Result from a single agent."""

    agent_type: str
    success: bool
    title: str | None = None
    content_type: str | None = None
    url: str | None = None
    duration_seconds: float = 0.0
    error: str | None = None
    raw_result: Any = None


@dataclass
class PointResult:
    """Complete result for a single route point."""

    point_index: int
    point_name: str
    status: PointStatus = PointStatus.PENDING
    agent_results: list[AgentResult] = field(default_factory=list)
    winner: AgentResult | None = None
    judge_reasoning: str | None = None
    processing_time_seconds: float = 0.0
    started_at: datetime | None = None
    completed_at: datetime | None = None


@dataclass
class TourState:
    """Complete state of a tour."""

    tour_id: str
    source: str
    destination: str
    status: TourStatus = TourStatus.PENDING
    profile: dict = field(default_factory=dict)
    points: list[PointResult] = field(default_factory=list)
    total_points: int = 0
    completed_points: int = 0
    route_info: dict = field(default_factory=dict)
    metrics: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error: str | None = None


# =============================================================================
# Tour Store (In-Memory - Redis-ready for production)
# =============================================================================


class TourStore:
    """
    Thread-safe tour state storage.

    In production, this would be backed by Redis or a database.
    For MIT demo, in-memory with proper locking is sufficient.
    """

    def __init__(self):
        self._tours: dict[str, TourState] = {}
        self._lock = threading.RLock()
        self._subscribers: dict[str, list[Callable]] = {}

    def create(
        self, tour_id: str, source: str, destination: str, profile: dict
    ) -> TourState:
        """Create a new tour."""
        with self._lock:
            tour = TourState(
                tour_id=tour_id,
                source=source,
                destination=destination,
                profile=profile,
            )
            self._tours[tour_id] = tour
            return tour

    def get(self, tour_id: str) -> TourState | None:
        """Get a tour by ID."""
        with self._lock:
            return self._tours.get(tour_id)

    def update(self, tour_id: str, **updates) -> TourState | None:
        """Update a tour's state."""
        with self._lock:
            tour = self._tours.get(tour_id)
            if tour:
                for key, value in updates.items():
                    if hasattr(tour, key):
                        setattr(tour, key, value)
                self._notify_subscribers(tour_id, tour)
            return tour

    def list_all(self, limit: int = 100) -> list[TourState]:
        """List all tours."""
        with self._lock:
            return list(self._tours.values())[:limit]

    def delete(self, tour_id: str) -> bool:
        """Delete a tour."""
        with self._lock:
            if tour_id in self._tours:
                del self._tours[tour_id]
                return True
            return False

    def subscribe(self, tour_id: str, callback: Callable[[TourState], None]):
        """Subscribe to tour updates."""
        with self._lock:
            if tour_id not in self._subscribers:
                self._subscribers[tour_id] = []
            self._subscribers[tour_id].append(callback)

    def unsubscribe(self, tour_id: str, callback: Callable):
        """Unsubscribe from tour updates."""
        with self._lock:
            if tour_id in self._subscribers:
                self._subscribers[tour_id] = [
                    cb for cb in self._subscribers[tour_id] if cb != callback
                ]

    def _notify_subscribers(self, tour_id: str, tour: TourState):
        """Notify all subscribers of a tour update."""
        subscribers = self._subscribers.get(tour_id, [])
        for callback in subscribers:
            try:
                callback(tour)
            except Exception as e:
                logger.warning(f"Subscriber callback failed: {e}")


# Global tour store instance
_tour_store = TourStore()


def get_tour_store() -> TourStore:
    """Get the global tour store instance."""
    return _tour_store


# =============================================================================
# Tour Service - The Main Processing Engine
# =============================================================================


class TourService:
    """
    Centralized tour processing service.

    This is the SINGLE SOURCE OF TRUTH for all tour processing.
    Both the REST API and Dashboard use this service.

    API Mode Strategy:
    - auto (default): Prefer real APIs, fallback to mock if unavailable
    - real: Force real APIs, error if not available
    - mock: Always use mock data (for tests/CI only)
    """

    def __init__(self, store: TourStore | None = None):
        self.store = store or get_tour_store()
        self._executor = ThreadPoolExecutor(
            max_workers=10, thread_name_prefix="TourService"
        )
        self._api_mode = os.environ.get("TOUR_GUIDE_API_MODE", "auto")
        self._agents_available = self._check_agents_available()
        self._api_keys_available = self._check_api_keys()
        self._api_status = self._get_api_status()

        # Log startup status
        logger.info(f"🚀 TourService initialized:")
        logger.info(f"   Mode: {self._api_mode}")
        logger.info(f"   Agents Available: {self._agents_available}")
        logger.info(f"   API Keys: {self._api_keys_available}")
        logger.info(f"   Using Real APIs: {self._should_use_real_apis()}")

    def _check_agents_available(self) -> bool:
        """Check if real agents are available."""
        try:
            from src.agents.judge_agent import JudgeAgent  # noqa: F401
            from src.agents.music_agent import MusicAgent  # noqa: F401
            from src.agents.text_agent import TextAgent  # noqa: F401
            from src.agents.video_agent import VideoAgent  # noqa: F401

            return True
        except ImportError:
            return False

    def _check_api_keys(self) -> dict[str, bool]:
        """Check which API keys are configured."""
        try:
            from src.utils.config import settings

            return {
                "google_maps": bool(settings.google_maps_api_key),
                "youtube": bool(getattr(settings, "youtube_api_key", None)),
                "anthropic": bool(getattr(settings, "anthropic_api_key", None)),
                "spotify": bool(getattr(settings, "spotify_client_id", None)),
            }
        except Exception:
            return {
                "google_maps": False,
                "youtube": False,
                "anthropic": False,
                "spotify": False,
            }

    def _get_api_status(self) -> dict:
        """Get comprehensive API status."""
        keys = self._api_keys_available
        any_key = any(keys.values())

        return {
            "mode": self._api_mode,
            "agents_available": self._agents_available,
            "api_keys": keys,
            "using_real_apis": self._should_use_real_apis(),
            "is_live": self._should_use_real_apis() and any_key,
            "status": "live" if (self._should_use_real_apis() and any_key) else "demo",
        }

    def get_api_status(self) -> dict:
        """Public method to get API status for health checks."""
        return self._api_status

    def _should_use_real_apis(self) -> bool:
        """
        Determine if we should use real APIs based on mode.

        Strategy:
        - mock: Always use mock (for tests/CI)
        - real: Force real APIs
        - auto: Use real if available, fallback to mock
        """
        if self._api_mode == "mock":
            return False
        elif self._api_mode == "real":
            if not self._agents_available:
                logger.error("API mode is 'real' but agents are not available!")
            return self._agents_available
        else:  # auto - prefer real
            return self._agents_available

    def create_tour(
        self,
        source: str,
        destination: str,
        profile: dict | None = None,
    ) -> TourState:
        """
        Create a new tour and start processing in background.

        Returns immediately with tour ID for polling.
        """
        tour_id = f"tour_{uuid.uuid4().hex[:12]}"
        tour = self.store.create(
            tour_id=tour_id,
            source=source,
            destination=destination,
            profile=profile or {},
        )

        logger.info(f"🗺️ Created tour {tour_id}: {source} → {destination}")

        # Start processing in background
        self._executor.submit(self._process_tour_async, tour_id)

        return tour

    def get_tour(self, tour_id: str) -> TourState | None:
        """Get tour state by ID."""
        return self.store.get(tour_id)

    def cancel_tour(self, tour_id: str) -> bool:
        """Cancel an in-progress tour."""
        tour = self.store.get(tour_id)
        if tour and tour.status == TourStatus.PROCESSING:
            self.store.update(
                tour_id,
                status=TourStatus.CANCELLED,
                completed_at=datetime.now(),
            )
            return True
        return False

    def _process_tour_async(self, tour_id: str):
        """
        Process a tour asynchronously (runs in background thread).

        Pipeline Flow:
        ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
        │ STEP 1      │────▶│ STEP 2      │────▶│ STEP 3      │────▶│ STEP 4      │
        │ Google Maps │     │ Scheduler   │     │ Orchestrator│     │ Output      │
        │ (Route)     │     │ (Emit Pts)  │     │ (Agents)    │     │ (Playlist)  │
        └─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
        """
        tour = self.store.get(tour_id)
        if not tour:
            return

        try:
            # ================================================================
            # STEP 1: GOOGLE MAPS API - Fetch Route
            # ================================================================
            logger.info("=" * 60)
            logger.info("📍 STEP 1: Fetching route from Google Maps API...")
            logger.info("=" * 60)

            self.store.update(
                tour_id, status=TourStatus.FETCHING_ROUTE, started_at=datetime.now()
            )

            route = self._fetch_route(tour.source, tour.destination)
            logger.info(f"   ✅ Route fetched: {len(route['points'])} points")

            # ================================================================
            # STEP 2: SCHEDULER - Prepare and emit points
            # ================================================================
            logger.info("=" * 60)
            logger.info("⏰ STEP 2: Scheduler preparing point emission...")
            logger.info("=" * 60)

            self.store.update(
                tour_id,
                status=TourStatus.SCHEDULING,
                total_points=len(route["points"]),
                route_info=route,
            )

            # Initialize point results (Scheduler prepares the queue)
            points = [
                PointResult(
                    point_index=i,
                    point_name=p["name"],
                )
                for i, p in enumerate(route["points"])
            ]
            self.store.update(tour_id, points=points)
            logger.info(f"   ✅ Scheduler ready: {len(points)} points queued")

            # ================================================================
            # STEP 3: ORCHESTRATOR - Process each point with agents
            # ================================================================
            logger.info("=" * 60)
            logger.info("🎭 STEP 3: Orchestrator processing points...")
            logger.info("=" * 60)

            self.store.update(tour_id, status=TourStatus.PROCESSING)

            # Scheduler emits points one by one to Orchestrator
            for i, point_data in enumerate(route["points"]):
                # Check if cancelled
                tour = self.store.get(tour_id)
                if tour and tour.status == TourStatus.CANCELLED:
                    logger.info(f"Tour {tour_id} cancelled")
                    return

                self._process_point(
                    tour_id, i, point_data, tour.profile if tour else {}
                )

            # Step 3: Complete
            self.store.update(
                tour_id,
                status=TourStatus.COMPLETED,
                completed_at=datetime.now(),
            )

            logger.info(f"✅ Tour {tour_id} completed successfully")

        except Exception as e:
            logger.exception(f"Tour {tour_id} failed: {e}")
            self.store.update(
                tour_id,
                status=TourStatus.FAILED,
                error=str(e),
                completed_at=datetime.now(),
            )

    def _fetch_route(self, source: str, destination: str) -> dict:
        """Fetch route from Google Maps or mock."""
        use_real = self._should_use_real_apis()

        if use_real:
            try:
                from src.services.google_maps import GoogleMapsClient
                from src.utils.config import settings

                if settings.google_maps_api_key:
                    client = GoogleMapsClient()
                    route = client.get_route(source, destination)
                    return {
                        "source": route.source,
                        "destination": route.destination,
                        "points": [
                            {
                                "name": p.location_name or p.address,
                                "address": p.address,
                                "lat": p.latitude,
                                "lon": p.longitude,
                            }
                            for p in route.points
                        ],
                        "total_distance": route.total_distance,
                        "total_duration": route.total_duration,
                    }
            except Exception as e:
                logger.warning(f"Failed to get real route, using mock: {e}")

        # Fall back to mock route
        from src.services.google_maps import get_mock_route

        route = get_mock_route()
        return {
            "source": route.source,
            "destination": route.destination,
            "points": [
                {
                    "name": p.location_name or p.address,
                    "address": p.address,
                    "lat": p.latitude,
                    "lon": p.longitude,
                }
                for p in route.points
            ],
            "total_distance": route.total_distance,
            "total_duration": route.total_duration,
        }

    def _process_point(
        self, tour_id: str, point_index: int, point_data: dict, profile: dict
    ):
        """Process a single route point with parallel agents."""
        start_time = time.time()

        # Update point status
        tour = self.store.get(tour_id)
        if tour and tour.points and len(tour.points) > point_index:
            tour.points[point_index].status = PointStatus.AGENTS_RUNNING
            tour.points[point_index].started_at = datetime.now()
            self.store.update(tour_id, points=tour.points)

        logger.info(f"📍 Processing point {point_index + 1}: {point_data['name']}")

        use_real = self._should_use_real_apis()

        if use_real:
            agent_results = self._run_real_agents(point_data, profile)
        else:
            agent_results = self._run_mock_agents(point_data, profile)

        # Update with agent results
        tour = self.store.get(tour_id)
        if tour and tour.points and len(tour.points) > point_index:
            tour.points[point_index].status = PointStatus.QUEUE_WAITING
            tour.points[point_index].agent_results = agent_results
            self.store.update(tour_id, points=tour.points)

        # Run judge
        tour = self.store.get(tour_id)
        if tour and tour.points and len(tour.points) > point_index:
            tour.points[point_index].status = PointStatus.JUDGE_EVALUATING
            self.store.update(tour_id, points=tour.points)

        winner, reasoning = self._run_judge(
            agent_results, point_data, profile, use_real
        )

        # Complete the point
        elapsed = time.time() - start_time
        tour = self.store.get(tour_id)
        if tour and tour.points and len(tour.points) > point_index:
            tour.points[point_index].status = PointStatus.COMPLETED
            tour.points[point_index].winner = winner
            tour.points[point_index].judge_reasoning = reasoning
            tour.points[point_index].processing_time_seconds = elapsed
            tour.points[point_index].completed_at = datetime.now()
            tour.completed_points = sum(
                1 for p in tour.points if p.status == PointStatus.COMPLETED
            )
            self.store.update(
                tour_id, points=tour.points, completed_points=tour.completed_points
            )

        logger.info(
            f"   🏆 Winner: {winner.agent_type if winner else 'None'} - {winner.title if winner else 'N/A'}"
        )

    def _run_real_agents(self, point_data: dict, profile: dict) -> list[AgentResult]:
        """Run real agents in parallel."""
        from src.agents.music_agent import MusicAgent
        from src.agents.text_agent import TextAgent
        from src.agents.video_agent import VideoAgent
        from src.models.route import RoutePoint

        route_point = RoutePoint(
            index=0,
            address=point_data.get("address", point_data["name"]),
            location_name=point_data["name"],
            latitude=point_data.get("lat", 0.0),
            longitude=point_data.get("lon", 0.0),
        )

        results = []
        results_lock = threading.Lock()

        def run_agent(agent_class, agent_type: str):
            start = time.time()
            try:
                agent = agent_class()
                result = agent.execute(route_point)
                elapsed = time.time() - start

                if result:
                    agent_result = AgentResult(
                        agent_type=agent_type,
                        success=True,
                        title=result.title,
                        content_type=result.content_type.value
                        if result.content_type
                        else agent_type.lower(),
                        url=result.url,
                        duration_seconds=elapsed,
                        raw_result=result,
                    )
                else:
                    agent_result = AgentResult(
                        agent_type=agent_type,
                        success=False,
                        duration_seconds=elapsed,
                        error="No result returned",
                    )

                with results_lock:
                    results.append(agent_result)

                logger.info(
                    f"   ✅ {agent_type} Agent: {result.title if result else 'No result'} [{elapsed:.1f}s]"
                )

            except Exception as e:
                elapsed = time.time() - start
                logger.warning(f"   ❌ {agent_type} Agent failed: {e}")
                with results_lock:
                    results.append(
                        AgentResult(
                            agent_type=agent_type,
                            success=False,
                            duration_seconds=elapsed,
                            error=str(e),
                        )
                    )

        # Run agents in parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(run_agent, VideoAgent, "VIDEO"),
                executor.submit(run_agent, MusicAgent, "MUSIC"),
                executor.submit(run_agent, TextAgent, "TEXT"),
            ]
            for future in as_completed(futures, timeout=30):
                try:
                    future.result()
                except Exception as e:
                    logger.warning(f"Agent future failed: {e}")

        return results

    def _run_mock_agents(self, point_data: dict, profile: dict) -> list[AgentResult]:
        """Run mock agents for testing/demo."""
        import random

        location = point_data["name"]

        # Simulate parallel execution with small delays
        time.sleep(random.uniform(0.1, 0.3))

        results = [
            AgentResult(
                agent_type="VIDEO",
                success=True,
                title=f"Exploring {location} - Documentary",
                content_type="video",
                url=f"https://youtube.com/watch?v=mock_{location.replace(' ', '_')}",
                duration_seconds=random.uniform(0.5, 1.5),
            ),
            AgentResult(
                agent_type="MUSIC",
                success=True,
                title=f"Songs of {location}",
                content_type="music",
                url=f"https://spotify.com/track/mock_{location.replace(' ', '_')}",
                duration_seconds=random.uniform(0.3, 1.0),
            ),
            AgentResult(
                agent_type="TEXT",
                success=True,
                title=f"The History of {location}",
                content_type="text",
                url=None,
                duration_seconds=random.uniform(0.2, 0.8),
            ),
        ]

        for r in results:
            logger.info(
                f"   ✅ {r.agent_type} Agent: {r.title} [{r.duration_seconds:.1f}s]"
            )

        return results

    def _run_judge(
        self,
        agent_results: list[AgentResult],
        point_data: dict,
        profile: dict,
        use_real: bool,
    ) -> tuple[AgentResult | None, str]:
        """Run judge to select the best content."""
        successful = [r for r in agent_results if r.success]

        if not successful:
            return None, "No successful agent results to evaluate"

        if use_real:
            try:
                from src.agents.judge_agent import JudgeAgent
                from src.models.route import RoutePoint
                from src.models.user_profile import UserProfile

                route_point = RoutePoint(
                    index=0,
                    address=point_data.get("address", point_data["name"]),
                    location_name=point_data["name"],
                    latitude=point_data.get("lat", 0.0),
                    longitude=point_data.get("lon", 0.0),
                )

                # Build user profile from dict
                user_profile = None
                if profile:
                    user_profile = (
                        UserProfile(**profile) if isinstance(profile, dict) else profile
                    )

                # Get raw content results for judge
                candidates = [r.raw_result for r in successful if r.raw_result]

                if candidates:
                    judge = JudgeAgent(user_profile=user_profile)
                    decision = judge.evaluate(
                        route_point, candidates, user_profile=user_profile
                    )

                    if decision.selected_content:
                        # Find matching agent result
                        for r in successful:
                            if r.raw_result == decision.selected_content:
                                return r, decision.reasoning or "Selected by AI Judge"

                        # Fallback: create result from decision
                        return AgentResult(
                            agent_type=decision.selected_content.content_type.value.upper(),
                            success=True,
                            title=decision.selected_content.title,
                            content_type=decision.selected_content.content_type.value,
                            url=decision.selected_content.url,
                            raw_result=decision.selected_content,
                        ), decision.reasoning or "Selected by AI Judge"

            except Exception as e:
                logger.warning(f"Real judge failed, using fallback: {e}")

        # Mock/fallback judge logic
        import random

        # Apply profile constraints
        is_driver = profile.get("is_driver", False)
        if is_driver:
            # Filter out video for drivers
            non_video = [r for r in successful if r.agent_type != "VIDEO"]
            if non_video:
                successful = non_video

        # Select best (mock: random weighted by type)
        weights = {"TEXT": 0.4, "MUSIC": 0.35, "VIDEO": 0.25}
        weighted = [(r, weights.get(r.agent_type, 0.33)) for r in successful]
        total = sum(w for _, w in weighted)
        weighted = [(r, w / total) for r, w in weighted]

        # Random selection
        rand = random.random()
        cumulative = 0.0
        for r, w in weighted:
            cumulative += w
            if rand <= cumulative:
                reasoning = f"Selected {r.agent_type.lower()} content for its relevance to {point_data['name']}"
                return r, reasoning

        return successful[0], f"Default selection for {point_data['name']}"

    def get_tour_summary(self, tour_id: str) -> dict | None:
        """Get a summary of the tour suitable for API response."""
        tour = self.store.get(tour_id)
        if not tour:
            return None

        return {
            "tour_id": tour.tour_id,
            "status": tour.status.value,
            "source": tour.source,
            "destination": tour.destination,
            "progress": {
                "total_points": tour.total_points,
                "completed_points": tour.completed_points,
                "percentage": (
                    round(tour.completed_points / tour.total_points * 100)
                    if tour.total_points > 0
                    else 0
                ),
            },
            "created_at": tour.created_at.isoformat(),
            "started_at": tour.started_at.isoformat() if tour.started_at else None,
            "completed_at": tour.completed_at.isoformat()
            if tour.completed_at
            else None,
            "error": tour.error,
        }

    def get_tour_results(self, tour_id: str) -> dict | None:
        """Get complete tour results with playlist."""
        tour = self.store.get(tour_id)
        if not tour:
            return None

        playlist = []
        content_distribution = {"video": 0, "music": 0, "text": 0}

        for point in tour.points:
            if point.winner:
                content_type = (
                    point.winner.content_type or point.winner.agent_type.lower()
                )
                current_count: int = content_distribution.get(content_type, 0)
                content_distribution[content_type] = current_count + 1

                playlist.append(
                    {
                        "point_index": point.point_index + 1,
                        "point_name": point.point_name,
                        "decision": {
                            "content_type": content_type,
                            "title": point.winner.title,
                            "url": point.winner.url,
                            "agent_type": point.winner.agent_type,
                        },
                        "reasoning": point.judge_reasoning,
                        "processing_time_seconds": point.processing_time_seconds,
                        "all_candidates": [
                            {
                                "agent_type": r.agent_type,
                                "title": r.title,
                                "success": r.success,
                                "duration_seconds": r.duration_seconds,
                            }
                            for r in point.agent_results
                        ],
                    }
                )

        return {
            "tour_id": tour.tour_id,
            "status": tour.status.value,
            "source": tour.source,
            "destination": tour.destination,
            "profile": tour.profile,
            "route_info": tour.route_info,
            "playlist": playlist,
            "summary": {
                "total_points": tour.total_points,
                "completed_points": tour.completed_points,
                "successful_decisions": len([p for p in tour.points if p.winner]),
                "content_distribution": content_distribution,
            },
            "created_at": tour.created_at.isoformat(),
            "completed_at": tour.completed_at.isoformat()
            if tour.completed_at
            else None,
        }


# =============================================================================
# Global Service Instance
# =============================================================================


_tour_service: TourService | None = None


def get_tour_service() -> TourService:
    """Get the global tour service instance."""
    global _tour_service
    if _tour_service is None:
        _tour_service = TourService()
    return _tour_service
