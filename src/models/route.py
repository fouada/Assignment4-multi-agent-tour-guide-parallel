"""
Route-related data models.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
import uuid


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
    
    @property
    def coordinates(self) -> tuple:
        """Return (lat, lng) tuple."""
        return (self.latitude, self.longitude)
    
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
    points: List[RoutePoint] = Field(default_factory=list)
    total_distance: Optional[float] = None  # in meters
    total_duration: Optional[float] = None  # in seconds
    created_at: datetime = Field(default_factory=datetime.now)
    
    @property
    def point_count(self) -> int:
        return len(self.points)
    
    def get_point_by_id(self, point_id: str) -> Optional[RoutePoint]:
        """Get a point by its ID."""
        for point in self.points:
            if point.id == point_id:
                return point
        return None

