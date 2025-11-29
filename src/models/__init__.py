"""
Data models for the Multi-Agent Tour Guide system.
"""

from src.models.content import AgentStatus, ContentResult, ContentType
from src.models.decision import AgentTask, JudgeDecision
from src.models.metrics import QueueMetrics, QueueStatus
from src.models.output import SystemState, TourGuideOutput
from src.models.route import Route, RoutePoint
from src.models.user_profile import (
    AgeGroup,
    ContentPreference,
    Gender,
    TravelMode,
    TripPurpose,
    UserProfile,
    get_driver_profile,
    get_family_profile,
    get_kid_profile,
    get_senior_profile,
    get_teenager_profile,
)

__all__ = [
    # Content
    "ContentResult",
    "ContentType",
    "AgentStatus",
    # Route
    "RoutePoint",
    "Route",
    # Decision
    "JudgeDecision",
    "AgentTask",
    # User Profile
    "UserProfile",
    "AgeGroup",
    "Gender",
    "TravelMode",
    "TripPurpose",
    "ContentPreference",
    "get_kid_profile",
    "get_teenager_profile",
    "get_senior_profile",
    "get_family_profile",
    "get_driver_profile",
    # Output
    "TourGuideOutput",
    "SystemState",
    # Metrics
    "QueueMetrics",
    "QueueStatus",
]
