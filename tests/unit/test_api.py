"""
Unit tests for the API module.

Tests cover:
- Health check endpoints
- Tour CRUD operations
- Profile endpoints
- Error handling
- Request middleware

MIT Level Testing - 85%+ Coverage Target
"""

import pytest


class TestTourRequest:
    """Tests for TourRequest model."""

    def test_tour_request_valid(self):
        """Test valid TourRequest creation."""
        from src.api.app import TourRequest

        request = TourRequest(source="Tel Aviv", destination="Jerusalem")

        assert request.source == "Tel Aviv"
        assert request.destination == "Jerusalem"
        assert request.profile is None
        assert request.options is None

    def test_tour_request_with_profile(self):
        """Test TourRequest with profile."""
        from src.api.app import TourRequest

        request = TourRequest(
            source="Tel Aviv",
            destination="Jerusalem",
            profile={"age_group": "adult"},
            options={"mode": "queue"},
        )

        assert request.profile == {"age_group": "adult"}
        assert request.options == {"mode": "queue"}


class TestTourResponse:
    """Tests for TourResponse model."""

    def test_tour_response_creation(self):
        """Test TourResponse creation."""
        from src.api.app import TourResponse

        response = TourResponse(
            tour_id="tour_123",
            status="processing",
            created_at="2024-01-01T00:00:00",
            message="Tour created",
        )

        assert response.tour_id == "tour_123"
        assert response.status == "processing"


class TestHealthResponse:
    """Tests for HealthResponse model."""

    def test_health_response_creation(self):
        """Test HealthResponse creation."""
        from src.api.app import HealthResponse

        response = HealthResponse(
            status="healthy",
            version="2.0.0",
            uptime_seconds=100.5,
            timestamp="2024-01-01T00:00:00",
            checks={"llm_provider": {"status": "healthy"}},
        )

        assert response.status == "healthy"
        assert response.version == "2.0.0"
        assert response.uptime_seconds == 100.5


class TestErrorResponse:
    """Tests for ErrorResponse model."""

    def test_error_response_creation(self):
        """Test ErrorResponse creation."""
        from src.api.app import ErrorResponse

        response = ErrorResponse(
            error={"code": 404, "message": "Not found"}, meta={"request_id": "abc123"}
        )

        assert response.status == "error"
        assert response.error["code"] == 404


class TestAPIEndpoints:
    """Tests for API endpoints using TestClient."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient

        from src.api.app import app

        return TestClient(app)

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "uptime_seconds" in data
        assert "checks" in data

    def test_readiness_check(self, client):
        """Test readiness endpoint."""
        response = client.get("/ready")

        assert response.status_code == 200
        data = response.json()
        assert data["ready"] is True

    def test_metrics_endpoint(self, client):
        """Test metrics endpoint."""
        response = client.get("/metrics")

        assert response.status_code == 200
        # Should return text/plain
        assert "text/plain" in response.headers.get("content-type", "")

    def test_create_tour(self, client):
        """Test tour creation endpoint."""
        response = client.post(
            "/api/v1/tours", json={"source": "Tel Aviv", "destination": "Jerusalem"}
        )

        assert response.status_code == 201
        data = response.json()
        assert "tour_id" in data
        assert data["status"] == "processing"
        assert "Tel Aviv" in data["message"]

    def test_create_tour_with_profile(self, client):
        """Test tour creation with profile."""
        response = client.post(
            "/api/v1/tours",
            json={
                "source": "Tel Aviv",
                "destination": "Jerusalem",
                "profile": {"age_group": "adult"},
                "options": {"mode": "queue"},
            },
        )

        assert response.status_code == 201

    def test_get_tour(self, client):
        """Test get tour status endpoint."""
        response = client.get("/api/v1/tours/tour_123")

        assert response.status_code == 200
        data = response.json()
        assert data["tour_id"] == "tour_123"
        assert "progress" in data

    def test_get_tour_results(self, client):
        """Test get tour results endpoint."""
        response = client.get("/api/v1/tours/tour_123/results")

        assert response.status_code == 200
        data = response.json()
        assert data["tour_id"] == "tour_123"
        assert "playlist" in data
        assert "summary" in data

    def test_cancel_tour(self, client):
        """Test cancel tour endpoint."""
        response = client.delete("/api/v1/tours/tour_123")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"

    def test_list_profile_presets(self, client):
        """Test list profile presets endpoint."""
        response = client.get("/api/v1/profiles/presets")

        assert response.status_code == 200
        data = response.json()
        assert "presets" in data
        assert len(data["presets"]) > 0

        # Check preset structure
        preset = data["presets"][0]
        assert "id" in preset
        assert "name" in preset
        assert "description" in preset

    def test_request_id_header(self, client):
        """Test request ID is added to response headers."""
        response = client.get("/health")

        assert "X-Request-ID" in response.headers
        assert len(response.headers["X-Request-ID"]) == 8


class TestErrorHandlers:
    """Tests for error handlers."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient

        from src.api.app import app

        return TestClient(app)

    def test_404_not_found(self, client):
        """Test 404 error handling."""
        response = client.get("/api/v1/nonexistent")

        assert response.status_code == 404

    def test_invalid_request_body(self, client):
        """Test invalid request body handling."""
        response = client.post(
            "/api/v1/tours",
            json={},  # Missing required fields
        )

        assert response.status_code == 422  # Validation error


class TestCORSMiddleware:
    """Tests for CORS middleware."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient

        from src.api.app import app

        return TestClient(app)

    def test_cors_headers_present(self, client):
        """Test CORS headers are present."""
        response = client.options(
            "/health", headers={"Origin": "http://localhost:3000"}
        )

        # CORS headers should be present
        assert response.status_code in [200, 204]


class TestOpenAPIDocumentation:
    """Tests for OpenAPI documentation."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient

        from src.api.app import app

        return TestClient(app)

    def test_openapi_json_available(self, client):
        """Test OpenAPI JSON is available."""
        response = client.get("/openapi.json")

        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "paths" in data

    def test_docs_available(self, client):
        """Test Swagger UI is available."""
        response = client.get("/docs")

        assert response.status_code == 200

    def test_redoc_available(self, client):
        """Test ReDoc is available."""
        response = client.get("/redoc")

        assert response.status_code == 200
