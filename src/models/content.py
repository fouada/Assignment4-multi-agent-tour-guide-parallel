"""
Content-related data models.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


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


class ContentResult(BaseModel):
    """Result from a content agent."""

    point_id: str = ""
    content_type: ContentType
    title: str
    description: str | None = None
    url: str | None = None
    source: str  # e.g., "YouTube", "Spotify", "Wikipedia"
    relevance_score: float = Field(ge=0.0, le=10.0, default=5.0)
    duration_seconds: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
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
                "duration_seconds": 754,
                "metadata": {"views": 150000, "channel": "History Channel"},
            }
        }
