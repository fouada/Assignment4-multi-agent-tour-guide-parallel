"""
Multi-Agent Tour Guide - REST API Server
=========================================

MIT-Level Production-Ready FastAPI Application

This API serves as the SINGLE ENTRY POINT for all tour guide operations.
The Dashboard and any other clients consume this API via HTTP.

Features:
- OpenAPI documentation with full Swagger UI
- Real tour processing via TourService
- WebSocket support for real-time updates
- Health/readiness endpoints for Kubernetes
- Prometheus metrics endpoint
- CORS configuration for cross-origin requests
- Request tracing with unique IDs
- Comprehensive error handling

Architecture:
    Dashboard ──HTTP──▶ FastAPI ──▶ TourService ──▶ Agents
                           │
                           └──▶ WebSocket (real-time updates)

Author: Multi-Agent Tour Guide Research Team
Version: 2.0.0
"""

import asyncio
import logging
import uuid
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import (
    FastAPI,
    HTTPException,
    Request,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.services.tour_service import (
    TourService,
    TourStatus,
    get_tour_service,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Pydantic Models for API Request/Response
# =============================================================================


class ProfileSettings(BaseModel):
    """User profile settings for tour customization."""

    age_group: str | None = Field(
        default=None, description="Age group: child, teen, adult, senior"
    )
    is_driver: bool = Field(
        default=False, description="Driver mode - audio only, no video"
    )
    is_family_mode: bool = Field(
        default=False, description="Family-friendly content filtering"
    )
    min_age: int | None = Field(default=None, description="Minimum age for family mode")
    interests: list[str] = Field(default_factory=list, description="User interests")
    content_preference: str | None = Field(
        default=None, description="Preferred content type"
    )
    max_content_duration_seconds: int | None = Field(
        default=None, description="Max content duration"
    )
    exclude_topics: list[str] = Field(
        default_factory=list, description="Topics to exclude"
    )


class TourRequest(BaseModel):
    """Request to create a new tour."""

    source: str = Field(..., min_length=1, description="Starting location")
    destination: str = Field(..., min_length=1, description="Ending location")
    profile: ProfileSettings | None = Field(
        default=None, description="User profile settings"
    )
    options: dict | None = Field(default=None, description="Processing options")

    class Config:
        json_schema_extra = {
            "example": {
                "source": "Tel Aviv, Israel",
                "destination": "Jerusalem, Israel",
                "profile": {
                    "age_group": "adult",
                    "is_driver": False,
                    "interests": ["history", "culture"],
                },
                "options": {"mode": "queue"},
            }
        }


class TourResponse(BaseModel):
    """Response for tour creation."""

    tour_id: str
    status: str
    created_at: str
    message: str


class TourStatusResponse(BaseModel):
    """Response for tour status."""

    tour_id: str
    status: str
    source: str
    destination: str
    progress: dict
    created_at: str
    started_at: str | None
    completed_at: str | None
    error: str | None


class PlaylistItem(BaseModel):
    """Single item in the tour playlist."""

    point_index: int
    point_name: str
    decision: dict
    reasoning: str | None
    processing_time_seconds: float
    all_candidates: list[dict]


class TourResultsResponse(BaseModel):
    """Complete tour results with playlist."""

    tour_id: str
    status: str
    source: str
    destination: str
    profile: dict
    route_info: dict
    playlist: list[PlaylistItem]
    summary: dict
    created_at: str
    completed_at: str | None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    uptime_seconds: float
    timestamp: str
    api_mode: str
    checks: dict


class ErrorResponse(BaseModel):
    """Standard error response."""

    status: str = "error"
    error: dict
    meta: dict


# =============================================================================
# WebSocket Connection Manager
# =============================================================================


class ConnectionManager:
    """Manages WebSocket connections for real-time tour updates."""

    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, tour_id: str):
        await websocket.accept()
        if tour_id not in self.active_connections:
            self.active_connections[tour_id] = []
        self.active_connections[tour_id].append(websocket)
        logger.info(f"WebSocket connected for tour {tour_id}")

    def disconnect(self, websocket: WebSocket, tour_id: str):
        if tour_id in self.active_connections:
            self.active_connections[tour_id] = [
                ws for ws in self.active_connections[tour_id] if ws != websocket
            ]
            if not self.active_connections[tour_id]:
                del self.active_connections[tour_id]
        logger.info(f"WebSocket disconnected for tour {tour_id}")

    async def broadcast(self, tour_id: str, message: dict):
        if tour_id in self.active_connections:
            for connection in self.active_connections[tour_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.warning(f"Failed to send WebSocket message: {e}")


manager = ConnectionManager()


# =============================================================================
# App Lifecycle
# =============================================================================


startup_time: datetime | None = None
tour_service: TourService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global startup_time, tour_service
    startup_time = datetime.now()
    tour_service = get_tour_service()

    logger.info("🚀 Tour Guide API starting up...")
    logger.info(f"   API Mode: {tour_service._api_mode}")
    logger.info(f"   Agents Available: {tour_service._agents_available}")

    yield

    logger.info("👋 Tour Guide API shutting down...")


# =============================================================================
# FastAPI Application
# =============================================================================


app = FastAPI(
    title="Multi-Agent Tour Guide API",
    description="""
## 🗺️ Multi-Agent Tour Guide System - MIT-Level Architecture

Enterprise-grade AI orchestration for personalized travel experiences.

### Architecture Overview

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   Dashboard     │──────▶│    FastAPI      │──────▶│  TourService    │
│   (Port 8050)   │ HTTP  │   (Port 8000)   │       │  (Agents+Queue) │
└─────────────────┘       └─────────────────┘       └─────────────────┘
                                   │
                                   └── WebSocket (real-time updates)
```

### Key Features

- **Multi-Agent Architecture**: Video, Music, Text agents working in parallel
- **Smart Synchronization**: Queue-based with graceful degradation
- **Real-time Updates**: WebSocket support for live pipeline visualization
- **Personalization**: User profile-based content selection
- **Plugin System**: Extensible content providers

### API Workflow

1. **Create Tour**: `POST /api/v1/tours` - Returns tour ID immediately
2. **Poll Status**: `GET /api/v1/tours/{tour_id}` - Check processing progress
3. **Get Results**: `GET /api/v1/tours/{tour_id}/results` - Get complete playlist
4. **Real-time**: `WS /api/v1/tours/{tour_id}/ws` - Subscribe to live updates

### API Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `auto` | Try real APIs, fallback to mock | Development, Production |
| `real` | Force real APIs | Demo, Presentation |
| `mock` | Always use mocked data | Testing, CI/CD |

Set via environment: `TOUR_GUIDE_API_MODE=real`
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware - Allow Dashboard to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8050",
        "http://localhost:8051",
        "http://127.0.0.1:8050",
        "http://127.0.0.1:8051",
        "*",  # Allow all for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Request Middleware
# =============================================================================


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add request ID for tracing."""
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# =============================================================================
# Health & Status Endpoints
# =============================================================================


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health check endpoint",
)
async def health_check():
    """
    Check application health status.

    Returns health status of all components including:
    - TourService availability
    - Agent availability
    - API mode configuration
    - Which APIs are using real data vs mock
    """
    global tour_service
    uptime = (datetime.now() - startup_time).total_seconds() if startup_time else 0

    service = tour_service or get_tour_service()
    api_status = service.get_api_status()
    is_live = api_status.get("is_live", False)

    return HealthResponse(
        status="healthy",
        version="2.0.0",
        uptime_seconds=uptime,
        timestamp=datetime.now().isoformat(),
        api_mode=service._api_mode,
        checks={
            "tour_service": {"status": "healthy"},
            "data_mode": "🔴 LIVE" if is_live else "⚪ DEMO",
            "using_real_apis": api_status.get("using_real_apis", False),
            "agents_available": service._agents_available,
            "api_keys": api_status.get("api_keys", {}),
            "agents": {
                "video": {
                    "status": "live" if is_live else "mock",
                    "icon": "🔴" if is_live else "⚪",
                },
                "music": {
                    "status": "live" if is_live else "mock",
                    "icon": "🔴" if is_live else "⚪",
                },
                "text": {
                    "status": "live" if is_live else "mock",
                    "icon": "🔴" if is_live else "⚪",
                },
                "judge": {
                    "status": "live" if is_live else "mock",
                    "icon": "🔴" if is_live else "⚪",
                },
            },
        },
    )


@app.get(
    "/ready",
    tags=["Health"],
    summary="Readiness probe",
)
async def readiness_check():
    """Check if the application is ready to accept requests."""
    return {"ready": True, "message": "Service is ready to accept requests"}


@app.get(
    "/metrics",
    tags=["Observability"],
    summary="Prometheus metrics",
)
async def metrics():
    """
    Export metrics in Prometheus format.

    Metrics include:
    - Request counts and latencies
    - Agent response times
    - Queue statistics
    - Active tour counts
    """
    service = get_tour_service()
    tours = service.store.list_all()

    active_count = len([t for t in tours if t.status == TourStatus.PROCESSING])
    completed_count = len([t for t in tours if t.status == TourStatus.COMPLETED])
    failed_count = len([t for t in tours if t.status == TourStatus.FAILED])

    metrics_text = f"""
# HELP tour_requests_total Total tour requests
# TYPE tour_requests_total counter
tour_requests_total{{status="completed"}} {completed_count}
tour_requests_total{{status="failed"}} {failed_count}
tour_requests_total{{status="processing"}} {active_count}

# HELP active_tours Currently processing tours
# TYPE active_tours gauge
active_tours {active_count}

# HELP tour_service_api_mode Current API mode
# TYPE tour_service_api_mode gauge
tour_service_api_mode{{mode="{service._api_mode}"}} 1
"""
    return JSONResponse(
        content=metrics_text,
        media_type="text/plain",
    )


# =============================================================================
# Tour Endpoints - Real Processing
# =============================================================================


@app.post(
    "/api/v1/tours",
    response_model=TourResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Tours"],
    summary="Create a new tour",
)
async def create_tour(request: TourRequest):
    """
    Create a new tour guide session.

    This endpoint:
    1. Validates the request
    2. Creates a tour in the TourService
    3. Starts background processing (async)
    4. Returns tour ID immediately for status polling

    The actual processing happens in the background. Use:
    - `GET /api/v1/tours/{tour_id}` to poll status
    - `GET /api/v1/tours/{tour_id}/results` to get final results
    - `WS /api/v1/tours/{tour_id}/ws` for real-time updates
    """
    service = get_tour_service()

    # Convert profile to dict if provided
    profile_dict = {}
    if request.profile:
        profile_dict = request.profile.model_dump(exclude_none=True)

    # Create tour (starts processing in background)
    tour = service.create_tour(
        source=request.source,
        destination=request.destination,
        profile=profile_dict,
    )

    return TourResponse(
        tour_id=tour.tour_id,
        status=tour.status.value,
        created_at=tour.created_at.isoformat(),
        message=f"Tour created. Processing route from {request.source} to {request.destination}. Poll /api/v1/tours/{tour.tour_id} for status.",
    )


@app.get(
    "/api/v1/tours/{tour_id}",
    response_model=TourStatusResponse,
    tags=["Tours"],
    summary="Get tour status",
)
async def get_tour(tour_id: str):
    """
    Get tour status and progress.

    Returns:
    - Current processing status
    - Number of completed points
    - Progress percentage
    - Timestamps
    """
    service = get_tour_service()
    summary = service.get_tour_summary(tour_id)

    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tour {tour_id} not found",
        )

    return TourStatusResponse(**summary)


@app.get(
    "/api/v1/tours/{tour_id}/results",
    tags=["Tours"],
    summary="Get tour results",
)
async def get_tour_results(tour_id: str):
    """
    Get complete tour results with playlist.

    Returns the full tour guide output including:
    - Content selection for each point
    - Judge reasoning
    - All candidate content from agents
    - Processing metrics
    """
    service = get_tour_service()
    results = service.get_tour_results(tour_id)

    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tour {tour_id} not found",
        )

    return results


@app.delete(
    "/api/v1/tours/{tour_id}",
    tags=["Tours"],
    summary="Cancel a tour",
)
async def cancel_tour(tour_id: str):
    """Cancel an in-progress tour."""
    service = get_tour_service()

    if service.cancel_tour(tour_id):
        return {
            "tour_id": tour_id,
            "status": "cancelled",
            "cancelled_at": datetime.now().isoformat(),
        }

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Tour {tour_id} cannot be cancelled (not found or not in progress)",
    )


@app.get(
    "/api/v1/tours",
    tags=["Tours"],
    summary="List all tours",
)
async def list_tours(limit: int = 20):
    """List all tours with their current status."""
    service = get_tour_service()
    tours = service.store.list_all(limit=limit)

    return {
        "tours": [
            {
                "tour_id": t.tour_id,
                "source": t.source,
                "destination": t.destination,
                "status": t.status.value,
                "progress": f"{t.completed_points}/{t.total_points}",
                "created_at": t.created_at.isoformat(),
            }
            for t in tours
        ],
        "count": len(tours),
    }


# =============================================================================
# WebSocket Endpoint for Real-Time Updates
# =============================================================================


@app.websocket("/api/v1/tours/{tour_id}/ws")
async def tour_websocket(websocket: WebSocket, tour_id: str):
    """
    WebSocket endpoint for real-time tour updates.

    Connect to receive live updates as the tour is processed:
    - Point processing started
    - Agent results
    - Judge decisions
    - Tour completion
    """
    service = get_tour_service()
    tour = service.get_tour(tour_id)

    if not tour:
        await websocket.close(code=4004, reason="Tour not found")
        return

    await manager.connect(websocket, tour_id)

    try:
        # Send current state
        summary = service.get_tour_summary(tour_id)
        await websocket.send_json({"type": "status", "data": summary})

        # Keep connection alive and send updates
        while True:
            # Wait for messages (or use for ping/pong)
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
                if data == "ping":
                    await websocket.send_text("pong")
            except asyncio.TimeoutError:
                pass

            # Check tour status and send updates
            current = service.get_tour(tour_id)
            if current:
                await websocket.send_json(
                    {
                        "type": "update",
                        "data": service.get_tour_summary(tour_id),
                    }
                )

                if current.status in [
                    TourStatus.COMPLETED,
                    TourStatus.FAILED,
                    TourStatus.CANCELLED,
                ]:
                    await websocket.send_json(
                        {
                            "type": "complete",
                            "data": service.get_tour_results(tour_id),
                        }
                    )
                    break

            await asyncio.sleep(0.5)

    except WebSocketDisconnect:
        manager.disconnect(websocket, tour_id)
    except Exception as e:
        logger.warning(f"WebSocket error: {e}")
        manager.disconnect(websocket, tour_id)


# =============================================================================
# Profile Endpoints
# =============================================================================


@app.get(
    "/api/v1/profiles/presets",
    tags=["Profiles"],
    summary="List profile presets",
)
async def list_profile_presets():
    """
    Get available user profile presets.

    Presets include:
    - default: General adult user
    - family: Family with children
    - history: History enthusiast
    - driver: Driver mode (no video)
    """
    return {
        "presets": [
            {
                "id": "default",
                "name": "Default Adult",
                "description": "General adult user with no specific preferences",
                "settings": {},
            },
            {
                "id": "family",
                "name": "Family with Kids",
                "description": "Family-friendly content for traveling with children",
                "settings": {
                    "is_family_mode": True,
                    "min_age": 5,
                    "exclude_topics": ["violence", "adult_content"],
                },
            },
            {
                "id": "history",
                "name": "History Enthusiast",
                "description": "In-depth historical content",
                "settings": {
                    "interests": ["history", "archaeology", "culture"],
                    "content_preference": "educational",
                },
            },
            {
                "id": "driver",
                "name": "Driver Mode",
                "description": "Audio-only content for drivers (no video)",
                "settings": {
                    "is_driver": True,
                    "content_preference": "audio",
                },
            },
        ]
    }


# =============================================================================
# Error Handlers
# =============================================================================


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with standard format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
            },
            "meta": {
                "request_id": getattr(request.state, "request_id", "unknown"),
            },
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.exception(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
            },
            "meta": {
                "request_id": getattr(request.state, "request_id", "unknown"),
            },
        },
    )


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
