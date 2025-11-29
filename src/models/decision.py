"""
Decision and task-related data models.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from src.models.content import AgentStatus, ContentResult, ContentType


class JudgeDecision(BaseModel):
    """Decision made by the judge agent."""

    point_id: str
    selected_content: ContentResult
    all_candidates: list[ContentResult]
    reasoning: str
    scores: dict[ContentType, float] = Field(default_factory=dict)
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
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result: ContentResult | None = None
    error: str | None = None
    thread_name: str | None = None

    @property
    def duration_seconds(self) -> float | None:
        """Calculate task duration if completed."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
