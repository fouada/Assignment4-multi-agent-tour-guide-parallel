"""
Decision and task-related data models.
"""
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
import uuid

from src.models.content import ContentResult, ContentType, AgentStatus


class JudgeDecision(BaseModel):
    """Decision made by the judge agent."""
    point_id: str
    selected_content: ContentResult
    all_candidates: List[ContentResult]
    reasoning: str
    scores: Dict[ContentType, float] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
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
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate task duration if completed."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

