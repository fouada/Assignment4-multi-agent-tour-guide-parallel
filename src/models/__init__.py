"""
Data models for the Multi-Agent Tour Guide system.
"""
from src.models.content import ContentResult, ContentType, AgentStatus
from src.models.route import RoutePoint, Route
from src.models.decision import JudgeDecision, AgentTask
from src.models.user_profile import (
    UserProfile, 
    AgeGroup, 
    Gender,
    TravelMode,
    TripPurpose,
    ContentPreference,
    get_kid_profile,
    get_teenager_profile,
    get_senior_profile,
    get_family_profile,
    get_driver_profile,
)
from src.models.output import TourGuideOutput, SystemState
from src.models.metrics import QueueMetrics, QueueStatus

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

