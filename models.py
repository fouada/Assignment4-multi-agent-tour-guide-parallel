"""
Data models for the Multi-Agent Tour Guide system.
Uses Pydantic for validation and serialization.
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import uuid


class ContentType(str, Enum):
    """Types of content that agents can provide."""
    VIDEO = "video"
    MUSIC = "music"
    TEXT = "text"


class AgentStatus(str, Enum):
    """Status of an agent's task."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class RoutePoint(BaseModel):
    """A single point/waypoint in the route."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    index: int
    address: str
    location_name: Optional[str] = None
    latitude: float
    longitude: float
    instruction: Optional[str] = None  # e.g., "Turn right"
    distance_from_start: Optional[float] = None  # in meters
    duration_from_start: Optional[float] = None  # in seconds
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "abc123",
                "index": 0,
                "address": "Ammunition Hill, Jerusalem",
                "location_name": "Ammunition Hill",
                "latitude": 31.7944,
                "longitude": 35.2283,
                "instruction": "Head north",
                "distance_from_start": 0,
                "duration_from_start": 0
            }
        }


class Route(BaseModel):
    """Complete route from source to destination."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: str
    destination: str
    points: List[RoutePoint] = []
    total_distance: Optional[float] = None  # in meters
    total_duration: Optional[float] = None  # in seconds
    created_at: datetime = Field(default_factory=datetime.now)
    
    @property
    def point_count(self) -> int:
        return len(self.points)


class ContentResult(BaseModel):
    """Result from a content agent."""
    point_id: str
    content_type: ContentType
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    source: str  # e.g., "YouTube", "Spotify", "Wikipedia"
    relevance_score: float = Field(ge=0.0, le=10.0)
    metadata: Dict[str, Any] = {}
    found_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "point_id": "abc123",
                "content_type": "video",
                "title": "The Battle of Ammunition Hill",
                "description": "Documentary about the Six-Day War battle",
                "url": "https://youtube.com/watch?v=...",
                "source": "YouTube",
                "relevance_score": 9.5,
                "metadata": {"duration": "12:34", "views": 150000}
            }
        }


class JudgeDecision(BaseModel):
    """Decision made by the judge agent."""
    point_id: str
    selected_content: ContentResult
    all_candidates: List[ContentResult]
    reasoning: str
    scores: Dict[ContentType, float]
    decided_at: datetime = Field(default_factory=datetime.now)


class AgentTask(BaseModel):
    """Task assigned to an agent."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    point_id: str
    agent_type: str
    location: str
    address: str
    status: AgentStatus = AgentStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[ContentResult] = None
    error: Optional[str] = None
    thread_name: Optional[str] = None


class TourGuideOutput(BaseModel):
    """Final output of the tour guide system."""
    route: Route
    decisions: List[JudgeDecision] = []
    generated_at: datetime = Field(default_factory=datetime.now)
    processing_stats: Dict[str, Any] = {}
    
    def to_playlist(self) -> List[Dict[str, Any]]:
        """Convert to a simple playlist format."""
        playlist = []
        for decision in self.decisions:
            point = next(
                (p for p in self.route.points if p.id == decision.point_id), 
                None
            )
            if point:
                playlist.append({
                    "point_index": point.index,
                    "location": point.address,
                    "location_name": point.location_name,
                    "content_type": decision.selected_content.content_type.value,
                    "title": decision.selected_content.title,
                    "url": decision.selected_content.url,
                    "reason": decision.reasoning
                })
        return playlist
    
    def print_playlist(self):
        """Print a formatted playlist."""
        print("\n" + "="*60)
        print("🗺️  TOUR GUIDE PLAYLIST")
        print("="*60)
        print(f"Route: {self.route.source} → {self.route.destination}")
        print(f"Total Points: {self.route.point_count}")
        print("-"*60)
        
        for item in self.to_playlist():
            print(f"\n📍 Point {item['point_index'] + 1}: {item['location']}")
            if item['location_name']:
                print(f"   ({item['location_name']})")
            print(f"   🎬 {item['content_type'].upper()}: {item['title']}")
            if item['url']:
                print(f"   🔗 {item['url']}")
            print(f"   💭 {item['reason']}")
        
        print("\n" + "="*60)


class SystemState(BaseModel):
    """Current state of the system for monitoring."""
    active_threads: int = 0
    pending_points: int = 0
    processed_points: int = 0
    active_agents: Dict[str, AgentStatus] = {}
    last_updated: datetime = Field(default_factory=datetime.now)

