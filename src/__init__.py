"""
Multi-Agent Tour Guide System

A parallel multi-agent system for intelligent tour guidance.
"""

__version__ = "2.0.0"
__author__ = "Student"
__email__ = "student@university.edu"

from src.core.smart_queue import SmartAgentQueue
from src.models.content import ContentResult, ContentType
from src.models.route import Route, RoutePoint
from src.models.user_profile import UserProfile

__all__ = [
    "ContentResult",
    "ContentType",
    "RoutePoint",
    "Route",
    "UserProfile",
    "SmartAgentQueue",
]
