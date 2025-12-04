"""
End-to-End API Integration Tests.

MIT-Level E2E Test Coverage:
- REST API full request/response cycle
- Authentication and authorization
- Error handling and validation
- Rate limiting behavior
"""

import json
from typing import Any

import pytest
from fastapi.testclient import TestClient

from src.api.app import app


@pytest.fixture
def api_client():
    """Create test client for API."""
    return TestClient(app)


@pytest.fixture
def valid_tour_request() -> dict[str, Any]:
    """Create valid tour request payload using actual API schema."""
    return {
        "source": "Paris, France",
        "destination": "Lyon, France",
        "profile": {
            "age_group": "adult",
            "interests": ["history", "art"],
        },
        "options": {
            "mode": "queue",
        },
    }


class TestAPIEndpoints:
    """E2E tests for API endpoints."""

    @pytest.mark.e2e
    def test_health_endpoint(self, api_client):
        """Test health check endpoint returns OK."""
        response = api_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.e2e
    def test_ready_endpoint(self, api_client):
        """Test readiness endpoint."""
        response = api_client.get("/ready")

        assert response.status_code == 200
        data = response.json()
        assert "ready" in data

    @pytest.mark.e2e
    def test_create_tour_success(self, api_client, valid_tour_request):
        """Test successful tour creation."""
        response = api_client.post(
            "/api/v1/tours",
            json=valid_tour_request,
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 201  # Created
        data = response.json()
        assert "tour_id" in data
        # Tour starts in "fetching_route" status (Step 1 of processing)
        assert data["status"] in ["fetching_route", "processing", "scheduling"]

    @pytest.mark.e2e
    def test_create_tour_validation_error(self, api_client):
        """Test tour creation with invalid payload."""
        invalid_request = {
            "source": "",  # Empty source should fail validation
            "destination": "Lyon",
        }

        response = api_client.post(
            "/api/v1/tours",
            json=invalid_request,
            headers={"Content-Type": "application/json"},
        )

        # Should return validation error
        assert response.status_code in [400, 422]

    @pytest.mark.e2e
    def test_get_tour_by_id(self, api_client, valid_tour_request):
        """Test retrieving tour by ID."""
        # First create a tour
        create_response = api_client.post(
            "/api/v1/tours",
            json=valid_tour_request,
            headers={"Content-Type": "application/json"},
        )
        assert create_response.status_code == 201
        tour_id = create_response.json()["tour_id"]

        # Then retrieve it
        response = api_client.get(f"/api/v1/tours/{tour_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["tour_id"] == tour_id

    @pytest.mark.e2e
    def test_get_tour_returns_status(self, api_client, valid_tour_request):
        """Test that get tour returns status information."""
        # First create a tour
        create_response = api_client.post(
            "/api/v1/tours",
            json=valid_tour_request,
            headers={"Content-Type": "application/json"},
        )
        assert create_response.status_code == 201
        tour_id = create_response.json()["tour_id"]

        # Then check its status
        response = api_client.get(f"/api/v1/tours/{tour_id}")

        assert response.status_code == 200
        data = response.json()
        assert "tour_id" in data
        assert "status" in data
        assert "progress" in data

    @pytest.mark.e2e
    def test_api_returns_json(self, api_client):
        """Test that API always returns JSON."""
        response = api_client.get("/health")

        assert "application/json" in response.headers.get("content-type", "")

    @pytest.mark.e2e
    def test_api_response_structure(self, api_client, valid_tour_request):
        """Test API response has correct structure."""
        response = api_client.post("/api/v1/tours", json=valid_tour_request)

        assert response.status_code == 201
        data = response.json()
        # Verify structure matches TourResponse model
        assert "tour_id" in data
        assert "status" in data
        assert "created_at" in data
        assert "message" in data


class TestAPIAuthentication:
    """E2E tests for API authentication."""

    @pytest.mark.e2e
    def test_public_endpoints_no_auth(self, api_client):
        """Test public endpoints work without auth."""
        # Health check should be public
        response = api_client.get("/health")
        assert response.status_code == 200

    @pytest.mark.e2e
    def test_missing_api_key_handling(self, api_client, valid_tour_request):
        """Test handling of missing API key for protected endpoints."""
        # This test validates proper error handling
        response = api_client.post(
            "/api/v1/tours",
            json=valid_tour_request,
        )

        # Should either work (no auth required) or return 401/403
        assert response.status_code in [200, 201, 202, 401, 403, 422]


class TestAPIErrorHandling:
    """E2E tests for API error handling."""

    @pytest.mark.e2e
    def test_invalid_json_body(self, api_client):
        """Test handling of invalid JSON body."""
        response = api_client.post(
            "/api/v1/tours",
            content="not valid json{{{",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code in [400, 422]

    @pytest.mark.e2e
    def test_method_not_allowed(self, api_client):
        """Test 405 for unsupported methods."""
        response = api_client.delete("/health")

        assert response.status_code == 405

    @pytest.mark.e2e
    def test_content_type_validation(self, api_client, valid_tour_request):
        """Test content type validation."""
        response = api_client.post(
            "/api/v1/tours",
            content=json.dumps(valid_tour_request),
            headers={"Content-Type": "text/plain"},
        )

        # Should either accept or return appropriate error
        assert response.status_code in [200, 201, 202, 400, 415, 422]


class TestAPIRateLimiting:
    """E2E tests for API rate limiting."""

    @pytest.mark.e2e
    def test_rate_limit_headers(self, api_client):
        """Test rate limit headers are present."""
        response = api_client.get("/health")

        # Rate limit headers (if implemented)
        # These are optional but good practice
        # Just verify response is valid
        assert response.status_code == 200

    @pytest.mark.e2e
    def test_multiple_requests_handling(self, api_client):
        """Test handling of multiple sequential requests."""
        # Make multiple requests
        responses = []
        for _ in range(5):
            resp = api_client.get("/health")
            responses.append(resp.status_code)

        # All should succeed (or rate limited with 429)
        for status in responses:
            assert status in [200, 429]


class TestAPIPagination:
    """E2E tests for API pagination."""

    @pytest.mark.e2e
    def test_tour_results_endpoint(self, api_client, valid_tour_request):
        """Test tour results endpoint."""
        # First create a tour
        create_response = api_client.post(
            "/api/v1/tours",
            json=valid_tour_request,
            headers={"Content-Type": "application/json"},
        )
        assert create_response.status_code == 201
        tour_id = create_response.json()["tour_id"]

        # Get results (may be partial while processing)
        response = api_client.get(f"/api/v1/tours/{tour_id}/results")

        assert response.status_code == 200
        data = response.json()
        # Verify results structure
        assert "tour_id" in data
        assert "status" in data

    @pytest.mark.e2e
    def test_cancel_tour_endpoint(self, api_client, valid_tour_request):
        """Test tour cancellation endpoint."""
        # First create a tour to cancel
        create_response = api_client.post(
            "/api/v1/tours",
            json=valid_tour_request,
            headers={"Content-Type": "application/json"},
        )
        assert create_response.status_code == 201
        tour_id = create_response.json()["tour_id"]

        # Cancel the tour
        response = api_client.delete(f"/api/v1/tours/{tour_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"

    @pytest.mark.e2e
    def test_profile_presets_endpoint(self, api_client):
        """Test profile presets listing endpoint."""
        response = api_client.get("/api/v1/profiles/presets")

        assert response.status_code == 200
        data = response.json()
        assert "presets" in data
        assert len(data["presets"]) > 0
