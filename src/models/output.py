"""
Output and system state data models.
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from src.models.route import Route
from src.models.decision import JudgeDecision
from src.models.content import AgentStatus


class TourGuideOutput(BaseModel):
    """Final output of the tour guide system."""
    route: Route
    decisions: List[JudgeDecision] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.now)
    processing_stats: Dict[str, Any] = Field(default_factory=dict)
    
    def to_playlist(self) -> List[Dict[str, Any]]:
        """Convert to a simple playlist format."""
        playlist = []
        for decision in self.decisions:
            point = self.route.get_point_by_id(decision.point_id)
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
            emoji = {"video": "🎬", "music": "🎵", "text": "📖"}.get(item['content_type'], "📄")
            print(f"\n📍 Point {item['point_index'] + 1}: {item['location']}")
            if item['location_name']:
                print(f"   ({item['location_name']})")
            print(f"   {emoji} {item['content_type'].upper()}: {item['title']}")
            if item['url']:
                print(f"   🔗 {item['url']}")
            print(f"   💭 {item['reason']}")
        
        print("\n" + "="*60)


class SystemState(BaseModel):
    """Current state of the system for monitoring."""
    active_threads: int = 0
    pending_points: int = 0
    processed_points: int = 0
    active_agents: Dict[str, AgentStatus] = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=datetime.now)

