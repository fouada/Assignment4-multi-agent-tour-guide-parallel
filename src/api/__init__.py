"""
Multi-Agent Tour Guide - REST API Module

MIT-Level Architecture: Provides FastAPI-based REST API and HTTP Client

Components:
- app: FastAPI application with all tour endpoints
- TourGuideClient: Sync HTTP client for Dashboard/external consumers
- AsyncTourGuideClient: Async HTTP client for high-performance applications
"""

from src.api.app import app
from src.api.client import (
    APIConfig,
    APIConnectionError,
    AsyncTourGuideClient,
    TourGuideAPIError,
    TourGuideClient,
    TourNotFoundError,
    get_client,
    quick_tour,
)

__all__ = [
    "app",
    "TourGuideClient",
    "AsyncTourGuideClient",
    "APIConfig",
    "TourGuideAPIError",
    "TourNotFoundError",
    "APIConnectionError",
    "get_client",
    "quick_tour",
]
