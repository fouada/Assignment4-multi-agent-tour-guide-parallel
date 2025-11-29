"""
Multi-Agent Tour Guide System

A parallel multi-agent system for intelligent tour guidance.
"""

__version__ = "2.0.0"
__author__ = "Student"
__email__ = "student@university.edu"

from src.models.content import ContentResult, ContentType
from src.models.route import RoutePoint, Route
from src.models.user_profile import UserProfile
from src.core.smart_queue import SmartAgentQueue

__all__ = [
    "ContentResult",
    "ContentType",
    "RoutePoint",
    "Route",
    "UserProfile",
    "SmartAgentQueue",
]

