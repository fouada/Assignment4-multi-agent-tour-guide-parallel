"""
Metrics and monitoring data models.
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from dataclasses import dataclass, field


class QueueStatus(Enum):
    """Queue completion status."""
    WAITING = "waiting"
    COMPLETE = "complete"           # All agents responded
    SOFT_DEGRADED = "soft_degraded" # 2/3 agents responded
    HARD_DEGRADED = "hard_degraded" # 1/3 agents responded
    FAILED = "failed"               # No agents responded


@dataclass
class QueueMetrics:
    """Metrics for monitoring queue performance."""
    point_id: str
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    status: QueueStatus = QueueStatus.WAITING
    agents_expected: int = 3
    agents_received: int = 0
    agents_succeeded: List[str] = field(default_factory=list)
    agents_failed: List[str] = field(default_factory=list)
    wait_time_ms: int = 0
    
    def complete(self, status: QueueStatus):
        """Mark the queue as complete."""
        self.end_time = datetime.now()
        self.status = status
        self.wait_time_ms = int((self.end_time - self.start_time).total_seconds() * 1000)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.agents_expected == 0:
            return 0.0
        return len(self.agents_succeeded) / self.agents_expected
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "point_id": self.point_id,
            "status": self.status.value,
            "agents_expected": self.agents_expected,
            "agents_succeeded": self.agents_succeeded,
            "agents_failed": self.agents_failed,
            "wait_time_ms": self.wait_time_ms,
            "success_rate": self.success_rate,
        }

