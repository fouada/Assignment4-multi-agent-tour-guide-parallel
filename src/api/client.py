"""
🗺️ Tour Guide API Client
=========================

MIT-Level Architecture: HTTP Client for Dashboard → API Communication

This client provides a clean interface for the Dashboard (and any other clients)
to communicate with the FastAPI backend via HTTP.

Features:
- Sync and async HTTP methods
- Automatic retry with exponential backoff
- WebSocket support for real-time updates
- Connection pooling for performance
- Comprehensive error handling
- Type-safe response models

Usage:
    from src.api.client import TourGuideClient

    client = TourGuideClient(base_url="http://localhost:8000")

    # Create a tour
    tour = client.create_tour("Tel Aviv", "Jerusalem")

    # Poll for status
    status = client.get_tour_status(tour["tour_id"])

    # Get results when complete
    if status["status"] == "completed":
        results = client.get_tour_results(tour["tour_id"])

Author: Multi-Agent Tour Guide Research Team
Version: 2.0.0
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from collections.abc import Callable, Generator
from dataclasses import dataclass
from typing import Any

import httpx

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================


@dataclass
class APIConfig:
    """API client configuration."""

    base_url: str = "http://localhost:8000"
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0
    verify_ssl: bool = True

    @classmethod
    def from_env(cls) -> APIConfig:
        """Create config from environment variables."""
        return cls(
            base_url=os.environ.get("TOUR_GUIDE_API_URL", "http://localhost:8000"),
            timeout=float(os.environ.get("TOUR_GUIDE_API_TIMEOUT", "30.0")),
            max_retries=int(os.environ.get("TOUR_GUIDE_API_RETRIES", "3")),
        )


# =============================================================================
# Exceptions
# =============================================================================


class TourGuideAPIError(Exception):
    """Base exception for API errors."""

    def __init__(
        self, message: str, status_code: int | None = None, response: dict | None = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class TourNotFoundError(TourGuideAPIError):
    """Tour not found."""

    pass


class TourCreationError(TourGuideAPIError):
    """Failed to create tour."""

    pass


class APIConnectionError(TourGuideAPIError):
    """Cannot connect to API."""

    pass


# =============================================================================
# Response Models
# =============================================================================


@dataclass
class TourCreatedResponse:
    """Response from creating a tour."""

    tour_id: str
    status: str
    created_at: str
    message: str


@dataclass
class TourStatusResponse:
    """Response from getting tour status."""

    tour_id: str
    status: str
    source: str
    destination: str
    progress: dict
    created_at: str
    started_at: str | None
    completed_at: str | None
    error: str | None


@dataclass
class HealthResponse:
    """Response from health check."""

    status: str
    version: str
    uptime_seconds: float
    api_mode: str
    checks: dict


# =============================================================================
# Synchronous API Client
# =============================================================================


class TourGuideClient:
    """
    Synchronous HTTP client for the Tour Guide API.

    This client is used by the Dashboard to communicate with the FastAPI backend.
    """

    def __init__(self, config: APIConfig | None = None):
        self.config = config or APIConfig.from_env()
        self._client = httpx.Client(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            verify=self.config.verify_ssl,
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close the HTTP client."""
        self._client.close()

    def _request(
        self,
        method: str,
        path: str,
        **kwargs,
    ) -> dict:
        """Make an HTTP request with retry logic."""
        url = path
        last_exception: TourGuideAPIError | None = None

        for attempt in range(self.config.max_retries):
            try:
                response = self._client.request(method, url, **kwargs)

                if response.status_code == 404:
                    raise TourNotFoundError(
                        f"Resource not found: {path}",
                        status_code=404,
                    )

                if response.status_code >= 400:
                    error_data = response.json() if response.content else {}
                    raise TourGuideAPIError(
                        f"API error: {response.status_code}",
                        status_code=response.status_code,
                        response=error_data,
                    )

                return response.json()

            except httpx.ConnectError as e:
                last_exception = APIConnectionError(
                    f"Cannot connect to API at {self.config.base_url}: {e}"
                )
                logger.warning(
                    f"Connection failed (attempt {attempt + 1}/{self.config.max_retries}): {e}"
                )

            except httpx.TimeoutException as e:
                last_exception = TourGuideAPIError(f"Request timeout: {e}")
                logger.warning(
                    f"Request timeout (attempt {attempt + 1}/{self.config.max_retries}): {e}"
                )

            # Exponential backoff
            if attempt < self.config.max_retries - 1:
                delay = self.config.retry_delay * (2**attempt)
                time.sleep(delay)

        raise last_exception or TourGuideAPIError("Request failed after retries")

    # =========================================================================
    # Health Endpoints
    # =========================================================================

    def health_check(self) -> dict:
        """Check API health."""
        return self._request("GET", "/health")

    def is_healthy(self) -> bool:
        """Quick check if API is healthy."""
        try:
            health = self.health_check()
            return health.get("status") == "healthy"
        except Exception:
            return False

    def get_api_mode(self) -> str:
        """Get current API mode (auto/real/mock)."""
        try:
            health = self.health_check()
            return health.get("api_mode", "unknown")
        except Exception:
            return "unknown"

    # =========================================================================
    # Tour Endpoints
    # =========================================================================

    def create_tour(
        self,
        source: str,
        destination: str,
        profile: dict | None = None,
        options: dict | None = None,
    ) -> dict:
        """
        Create a new tour.

        Args:
            source: Starting location
            destination: Ending location
            profile: User profile settings (optional)
            options: Processing options (optional)

        Returns:
            Tour creation response with tour_id
        """
        payload: dict[str, Any] = {
            "source": source,
            "destination": destination,
        }
        if profile:
            payload["profile"] = profile
        if options:
            payload["options"] = options

        return self._request("POST", "/api/v1/tours", json=payload)

    def get_tour_status(self, tour_id: str) -> dict:
        """
        Get tour status and progress.

        Args:
            tour_id: The tour ID

        Returns:
            Tour status with progress information
        """
        return self._request("GET", f"/api/v1/tours/{tour_id}")

    def get_tour_results(self, tour_id: str) -> dict:
        """
        Get complete tour results with playlist.

        Args:
            tour_id: The tour ID

        Returns:
            Complete tour results including playlist
        """
        return self._request("GET", f"/api/v1/tours/{tour_id}/results")

    def cancel_tour(self, tour_id: str) -> dict:
        """
        Cancel an in-progress tour.

        Args:
            tour_id: The tour ID

        Returns:
            Cancellation confirmation
        """
        return self._request("DELETE", f"/api/v1/tours/{tour_id}")

    def list_tours(self, limit: int = 20) -> dict:
        """
        List all tours.

        Args:
            limit: Maximum number of tours to return

        Returns:
            List of tours with their status
        """
        return self._request("GET", f"/api/v1/tours?limit={limit}")

    # =========================================================================
    # Polling Helpers
    # =========================================================================

    def wait_for_completion(
        self,
        tour_id: str,
        poll_interval: float = 1.0,
        timeout: float = 120.0,
        callback: Callable[[dict], None] | None = None,
    ) -> dict:
        """
        Wait for a tour to complete, polling for status.

        Args:
            tour_id: The tour ID
            poll_interval: Seconds between polls
            timeout: Maximum time to wait
            callback: Optional callback for status updates

        Returns:
            Final tour results

        Raises:
            TimeoutError: If tour doesn't complete within timeout
            TourGuideAPIError: If tour fails
        """
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise TimeoutError(f"Tour {tour_id} did not complete within {timeout}s")

            status = self.get_tour_status(tour_id)

            if callback:
                callback(status)

            tour_status = status.get("status", "")

            if tour_status == "completed":
                return self.get_tour_results(tour_id)

            if tour_status == "failed":
                raise TourGuideAPIError(
                    f"Tour failed: {status.get('error', 'Unknown error')}",
                    response=status,
                )

            if tour_status == "cancelled":
                raise TourGuideAPIError("Tour was cancelled", response=status)

            time.sleep(poll_interval)

    def poll_status(
        self,
        tour_id: str,
        poll_interval: float = 1.0,
    ) -> Generator[dict, None, None]:
        """
        Generator that yields status updates until completion.

        Args:
            tour_id: The tour ID
            poll_interval: Seconds between polls

        Yields:
            Status updates (final yield includes results if completed)
        """
        while True:
            status = self.get_tour_status(tour_id)
            tour_status = status.get("status", "")

            if tour_status in ("completed", "failed", "cancelled"):
                if tour_status == "completed":
                    results = self.get_tour_results(tour_id)
                    yield results
                else:
                    yield status
                return

            yield status
            time.sleep(poll_interval)

    # =========================================================================
    # Profile Endpoints
    # =========================================================================

    def get_profile_presets(self) -> dict:
        """Get available profile presets."""
        return self._request("GET", "/api/v1/profiles/presets")


# =============================================================================
# Async API Client
# =============================================================================


class AsyncTourGuideClient:
    """
    Asynchronous HTTP client for the Tour Guide API.

    Use this for async applications or when you need concurrent requests.
    """

    def __init__(self, config: APIConfig | None = None):
        self.config = config or APIConfig.from_env()
        self._client = httpx.AsyncClient(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            verify=self.config.verify_ssl,
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs,
    ) -> dict:
        """Make an async HTTP request with retry logic."""
        url = path
        last_exception: TourGuideAPIError | None = None

        for attempt in range(self.config.max_retries):
            try:
                response = await self._client.request(method, url, **kwargs)

                if response.status_code == 404:
                    raise TourNotFoundError(
                        f"Resource not found: {path}",
                        status_code=404,
                    )

                if response.status_code >= 400:
                    error_data = response.json() if response.content else {}
                    raise TourGuideAPIError(
                        f"API error: {response.status_code}",
                        status_code=response.status_code,
                        response=error_data,
                    )

                return response.json()

            except httpx.ConnectError as e:
                last_exception = APIConnectionError(
                    f"Cannot connect to API at {self.config.base_url}: {e}"
                )
                logger.warning(
                    f"Connection failed (attempt {attempt + 1}/{self.config.max_retries}): {e}"
                )

            except httpx.TimeoutException as e:
                last_exception = TourGuideAPIError(f"Request timeout: {e}")
                logger.warning(
                    f"Request timeout (attempt {attempt + 1}/{self.config.max_retries}): {e}"
                )

            # Exponential backoff
            if attempt < self.config.max_retries - 1:
                delay = self.config.retry_delay * (2**attempt)
                await asyncio.sleep(delay)

        raise last_exception or TourGuideAPIError("Request failed after retries")

    async def health_check(self) -> dict:
        """Check API health."""
        return await self._request("GET", "/health")

    async def create_tour(
        self,
        source: str,
        destination: str,
        profile: dict | None = None,
    ) -> dict:
        """Create a new tour."""
        payload: dict[str, Any] = {
            "source": source,
            "destination": destination,
        }
        if profile:
            payload["profile"] = profile

        return await self._request("POST", "/api/v1/tours", json=payload)

    async def get_tour_status(self, tour_id: str) -> dict:
        """Get tour status."""
        return await self._request("GET", f"/api/v1/tours/{tour_id}")

    async def get_tour_results(self, tour_id: str) -> dict:
        """Get tour results."""
        return await self._request("GET", f"/api/v1/tours/{tour_id}/results")

    async def wait_for_completion(
        self,
        tour_id: str,
        poll_interval: float = 1.0,
        timeout: float = 120.0,
    ) -> dict:
        """Wait for tour completion."""
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise TimeoutError(f"Tour {tour_id} did not complete within {timeout}s")

            status = await self.get_tour_status(tour_id)
            tour_status = status.get("status", "")

            if tour_status == "completed":
                return await self.get_tour_results(tour_id)

            if tour_status in ("failed", "cancelled"):
                raise TourGuideAPIError(f"Tour {tour_status}", response=status)

            await asyncio.sleep(poll_interval)


# =============================================================================
# Convenience Functions
# =============================================================================


def get_client(base_url: str | None = None) -> TourGuideClient:
    """Get a configured API client."""
    config = APIConfig.from_env()
    if base_url:
        config.base_url = base_url
    return TourGuideClient(config)


def quick_tour(
    source: str,
    destination: str,
    profile: dict | None = None,
    base_url: str | None = None,
) -> dict:
    """
    Quick helper to create a tour and wait for results.

    Args:
        source: Starting location
        destination: Ending location
        profile: Optional user profile
        base_url: Optional API URL override

    Returns:
        Complete tour results
    """
    with get_client(base_url) as client:
        # Create tour
        tour = client.create_tour(source, destination, profile)
        tour_id = tour["tour_id"]

        # Wait for completion
        return client.wait_for_completion(tour_id)
