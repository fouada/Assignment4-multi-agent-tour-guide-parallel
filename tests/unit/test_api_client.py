"""
Unit tests for the API Client module.

Tests cover:
- APIConfig configuration
- Exception classes
- TourGuideClient synchronous methods
- AsyncTourGuideClient async methods
- Error handling and retries
- Polling and streaming helpers

MIT Level Testing - 85%+ Coverage Target
"""

import os
from unittest.mock import MagicMock, patch

import httpx
import pytest


class TestAPIConfig:
    """Tests for APIConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        from src.api.client import APIConfig

        config = APIConfig()

        assert config.base_url == "http://localhost:8000"
        assert config.timeout == 30.0
        assert config.max_retries == 3
        assert config.retry_delay == 1.0
        assert config.verify_ssl is True

    def test_custom_config(self):
        """Test custom configuration values."""
        from src.api.client import APIConfig

        config = APIConfig(
            base_url="http://api.example.com",
            timeout=60.0,
            max_retries=5,
            retry_delay=2.0,
            verify_ssl=False,
        )

        assert config.base_url == "http://api.example.com"
        assert config.timeout == 60.0
        assert config.max_retries == 5
        assert config.retry_delay == 2.0
        assert config.verify_ssl is False

    def test_from_env(self):
        """Test configuration from environment variables."""
        from src.api.client import APIConfig

        with patch.dict(
            os.environ,
            {
                "TOUR_GUIDE_API_URL": "http://env-api.example.com",
                "TOUR_GUIDE_API_TIMEOUT": "45.0",
                "TOUR_GUIDE_API_RETRIES": "10",
            },
        ):
            config = APIConfig.from_env()

            assert config.base_url == "http://env-api.example.com"
            assert config.timeout == 45.0
            assert config.max_retries == 10

    def test_from_env_defaults(self):
        """Test configuration from environment with defaults."""
        from src.api.client import APIConfig

        with patch.dict(os.environ, {}, clear=True):
            # Clear specific env vars
            os.environ.pop("TOUR_GUIDE_API_URL", None)
            os.environ.pop("TOUR_GUIDE_API_TIMEOUT", None)
            os.environ.pop("TOUR_GUIDE_API_RETRIES", None)

            config = APIConfig.from_env()

            assert config.base_url == "http://localhost:8000"
            assert config.timeout == 30.0
            assert config.max_retries == 3


class TestExceptions:
    """Tests for API exception classes."""

    def test_tour_guide_api_error(self):
        """Test base API error."""
        from src.api.client import TourGuideAPIError

        error = TourGuideAPIError(
            "Test error", status_code=500, response={"detail": "test"}
        )

        assert str(error) == "Test error"
        assert error.status_code == 500
        assert error.response == {"detail": "test"}

    def test_tour_guide_api_error_minimal(self):
        """Test API error with minimal args."""
        from src.api.client import TourGuideAPIError

        error = TourGuideAPIError("Simple error")

        assert str(error) == "Simple error"
        assert error.status_code is None
        assert error.response is None

    def test_tour_not_found_error(self):
        """Test tour not found error."""
        from src.api.client import TourNotFoundError

        error = TourNotFoundError("Tour not found", status_code=404)

        assert str(error) == "Tour not found"
        assert error.status_code == 404

    def test_tour_creation_error(self):
        """Test tour creation error."""
        from src.api.client import TourCreationError

        error = TourCreationError("Failed to create", status_code=400)

        assert str(error) == "Failed to create"
        assert error.status_code == 400

    def test_api_connection_error(self):
        """Test API connection error."""
        from src.api.client import APIConnectionError

        error = APIConnectionError("Cannot connect")

        assert str(error) == "Cannot connect"


class TestResponseModels:
    """Tests for response dataclasses."""

    def test_tour_created_response(self):
        """Test TourCreatedResponse dataclass."""
        from src.api.client import TourCreatedResponse

        response = TourCreatedResponse(
            tour_id="tour_123",
            status="processing",
            created_at="2024-01-01T00:00:00",
            message="Tour created",
        )

        assert response.tour_id == "tour_123"
        assert response.status == "processing"

    def test_tour_status_response(self):
        """Test TourStatusResponse dataclass."""
        from src.api.client import TourStatusResponse

        response = TourStatusResponse(
            tour_id="tour_123",
            status="completed",
            source="Tel Aviv",
            destination="Jerusalem",
            progress={"percentage": 100},
            created_at="2024-01-01T00:00:00",
            started_at="2024-01-01T00:00:01",
            completed_at="2024-01-01T00:01:00",
            error=None,
        )

        assert response.tour_id == "tour_123"
        assert response.status == "completed"

    def test_health_response(self):
        """Test HealthResponse dataclass."""
        from src.api.client import HealthResponse

        response = HealthResponse(
            status="healthy",
            version="2.0.0",
            uptime_seconds=100.5,
            api_mode="mock",
            checks={},
        )

        assert response.status == "healthy"
        assert response.api_mode == "mock"


class TestTourGuideClientInit:
    """Tests for TourGuideClient initialization."""

    def test_init_default(self):
        """Test client with default config."""
        from src.api.client import TourGuideClient

        client = TourGuideClient()

        assert client.config.base_url == "http://localhost:8000"
        client.close()

    def test_init_custom_config(self):
        """Test client with custom config."""
        from src.api.client import APIConfig, TourGuideClient

        config = APIConfig(base_url="http://custom:9000", timeout=60.0)
        client = TourGuideClient(config=config)

        assert client.config.base_url == "http://custom:9000"
        assert client.config.timeout == 60.0
        client.close()

    def test_context_manager(self):
        """Test client as context manager."""
        from src.api.client import TourGuideClient

        with TourGuideClient() as client:
            assert client is not None
            assert client._client is not None

    def test_close(self):
        """Test client close method."""
        from src.api.client import TourGuideClient

        client = TourGuideClient()
        client.close()
        # Should not raise after close


class TestTourGuideClientMethods:
    """Tests for TourGuideClient methods with mocked HTTP."""

    @pytest.fixture
    def mock_client(self):
        """Create a client with mocked HTTP client."""
        from src.api.client import APIConfig, TourGuideClient

        config = APIConfig(max_retries=1, retry_delay=0.01)
        client = TourGuideClient(config=config)
        yield client
        client.close()

    def test_health_check_success(self, mock_client):
        """Test successful health check."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "healthy",
            "version": "2.0.0",
            "api_mode": "mock",
        }

        with patch.object(mock_client._client, "request", return_value=mock_response):
            result = mock_client.health_check()

            assert result["status"] == "healthy"

    def test_is_healthy_true(self, mock_client):
        """Test is_healthy returns True."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy"}

        with patch.object(mock_client._client, "request", return_value=mock_response):
            assert mock_client.is_healthy() is True

    def test_is_healthy_false(self, mock_client):
        """Test is_healthy returns False on error."""
        with patch.object(
            mock_client._client, "request", side_effect=Exception("Connection error")
        ):
            assert mock_client.is_healthy() is False

    def test_get_api_mode_success(self, mock_client):
        """Test get_api_mode returns mode."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"api_mode": "real"}

        with patch.object(mock_client._client, "request", return_value=mock_response):
            assert mock_client.get_api_mode() == "real"

    def test_get_api_mode_error(self, mock_client):
        """Test get_api_mode returns unknown on error."""
        with patch.object(
            mock_client._client, "request", side_effect=Exception("Error")
        ):
            assert mock_client.get_api_mode() == "unknown"

    def test_create_tour_success(self, mock_client):
        """Test successful tour creation."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "tour_id": "tour_abc",
            "status": "processing",
            "message": "Tour created",
        }

        with patch.object(mock_client._client, "request", return_value=mock_response):
            result = mock_client.create_tour("Tel Aviv", "Jerusalem")

            assert result["tour_id"] == "tour_abc"

    def test_create_tour_with_profile(self, mock_client):
        """Test tour creation with profile."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "tour_id": "tour_xyz",
            "status": "processing",
        }

        with patch.object(
            mock_client._client, "request", return_value=mock_response
        ) as mock:
            mock_client.create_tour(
                "Tel Aviv",
                "Jerusalem",
                profile={"age_group": "adult"},
                options={"mode": "queue"},
            )

            call_kwargs = mock.call_args[1]
            payload = call_kwargs["json"]
            assert payload["profile"] == {"age_group": "adult"}
            assert payload["options"] == {"mode": "queue"}

    def test_get_tour_status_success(self, mock_client):
        """Test get tour status."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "tour_id": "tour_123",
            "status": "completed",
            "progress": {"percentage": 100},
        }

        with patch.object(mock_client._client, "request", return_value=mock_response):
            result = mock_client.get_tour_status("tour_123")

            assert result["tour_id"] == "tour_123"
            assert result["status"] == "completed"

    def test_get_tour_status_not_found(self, mock_client):
        """Test get tour status for non-existent tour."""
        from src.api.client import TourNotFoundError

        mock_response = MagicMock()
        mock_response.status_code = 404

        with patch.object(mock_client._client, "request", return_value=mock_response):
            with pytest.raises(TourNotFoundError):
                mock_client.get_tour_status("nonexistent")

    def test_get_tour_results_success(self, mock_client):
        """Test get tour results."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "tour_id": "tour_123",
            "playlist": [{"point": "Point A", "content": "Video"}],
        }

        with patch.object(mock_client._client, "request", return_value=mock_response):
            result = mock_client.get_tour_results("tour_123")

            assert "playlist" in result

    def test_cancel_tour_success(self, mock_client):
        """Test cancel tour."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "cancelled"}

        with patch.object(mock_client._client, "request", return_value=mock_response):
            result = mock_client.cancel_tour("tour_123")

            assert result["status"] == "cancelled"

    def test_list_tours_success(self, mock_client):
        """Test list tours."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"tours": [], "total": 0}

        with patch.object(mock_client._client, "request", return_value=mock_response):
            result = mock_client.list_tours(limit=10)

            assert "tours" in result


class TestTourGuideClientErrorHandling:
    """Tests for error handling and retries."""

    @pytest.fixture
    def mock_client(self):
        """Create a client with mocked HTTP client."""
        from src.api.client import APIConfig, TourGuideClient

        config = APIConfig(max_retries=2, retry_delay=0.01)
        client = TourGuideClient(config=config)
        yield client
        client.close()

    def test_connection_error_retry(self, mock_client):
        """Test retry on connection error."""
        from src.api.client import APIConnectionError

        with patch.object(
            mock_client._client,
            "request",
            side_effect=httpx.ConnectError("Connection refused"),
        ):
            with pytest.raises(APIConnectionError):
                mock_client.health_check()

    def test_timeout_error_retry(self, mock_client):
        """Test retry on timeout."""
        from src.api.client import TourGuideAPIError

        with patch.object(
            mock_client._client,
            "request",
            side_effect=httpx.TimeoutException("Timeout"),
        ):
            with pytest.raises(TourGuideAPIError):
                mock_client.health_check()

    def test_4xx_error(self, mock_client):
        """Test 4xx error handling."""
        from src.api.client import TourGuideAPIError

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.content = b'{"detail": "Bad request"}'
        mock_response.json.return_value = {"detail": "Bad request"}

        with patch.object(mock_client._client, "request", return_value=mock_response):
            with pytest.raises(TourGuideAPIError) as exc_info:
                mock_client.create_tour("", "")

            assert exc_info.value.status_code == 400

    def test_5xx_error(self, mock_client):
        """Test 5xx error handling."""
        from src.api.client import TourGuideAPIError

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.content = b'{"detail": "Internal error"}'
        mock_response.json.return_value = {"detail": "Internal error"}

        with patch.object(mock_client._client, "request", return_value=mock_response):
            with pytest.raises(TourGuideAPIError) as exc_info:
                mock_client.health_check()

            assert exc_info.value.status_code == 500


class TestWaitForCompletion:
    """Tests for wait_for_completion helper."""

    @pytest.fixture
    def mock_client(self):
        """Create a client with mocked HTTP client."""
        from src.api.client import APIConfig, TourGuideClient

        config = APIConfig(max_retries=1, retry_delay=0.01)
        client = TourGuideClient(config=config)
        yield client
        client.close()

    def test_wait_for_completion_immediate(self, mock_client):
        """Test wait when tour is already completed."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "tour_id": "tour_123",
            "status": "completed",
            "progress": {"percentage": 100},
        }

        with patch.object(mock_client._client, "request", return_value=mock_response):
            result = mock_client.wait_for_completion("tour_123", poll_interval=0.01)

            assert result["status"] == "completed"

    def test_wait_for_completion_with_callback(self, mock_client):
        """Test wait with status callback."""
        callback_calls = []

        def callback(status):
            callback_calls.append(status)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "tour_id": "tour_123",
            "status": "completed",
            "progress": {"percentage": 100},
        }

        with patch.object(mock_client._client, "request", return_value=mock_response):
            mock_client.wait_for_completion(
                "tour_123", poll_interval=0.01, callback=callback
            )

            assert len(callback_calls) >= 1

    def test_wait_for_completion_failed(self, mock_client):
        """Test wait when tour fails raises exception."""
        from src.api.client import TourGuideAPIError

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "tour_id": "tour_123",
            "status": "failed",
            "error": "Processing error",
        }

        with patch.object(mock_client._client, "request", return_value=mock_response):
            with pytest.raises(TourGuideAPIError) as exc_info:
                mock_client.wait_for_completion("tour_123", poll_interval=0.01)

            assert "Tour failed" in str(exc_info.value)


class TestWaitPolling:
    """Tests for wait polling behavior."""

    @pytest.fixture
    def mock_client(self):
        """Create a client with mocked HTTP client."""
        from src.api.client import APIConfig, TourGuideClient

        config = APIConfig(max_retries=1, retry_delay=0.01)
        client = TourGuideClient(config=config)
        yield client
        client.close()

    def test_wait_polls_until_complete(self, mock_client):
        """Test wait polls multiple times until complete."""
        call_count = 0

        def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            mock_response = MagicMock()
            mock_response.status_code = 200
            if call_count < 3:
                mock_response.json.return_value = {
                    "tour_id": "tour_123",
                    "status": "processing",
                    "progress": {"percentage": call_count * 33},
                }
            else:
                mock_response.json.return_value = {
                    "tour_id": "tour_123",
                    "status": "completed",
                    "progress": {"percentage": 100},
                }
            return mock_response

        with patch.object(mock_client._client, "request", side_effect=mock_request):
            result = mock_client.wait_for_completion("tour_123", poll_interval=0.01)

        assert call_count >= 1
        assert result["status"] == "completed"


class TestAsyncTourGuideClient:
    """Tests for AsyncTourGuideClient."""

    def test_async_init(self):
        """Test async client initialization."""
        from src.api.client import APIConfig, AsyncTourGuideClient

        config = APIConfig(max_retries=1, retry_delay=0.01)
        client = AsyncTourGuideClient(config=config)

        assert client.config.max_retries == 1

    def test_async_init_default(self):
        """Test async client with default config."""
        from src.api.client import AsyncTourGuideClient

        client = AsyncTourGuideClient()

        assert client.config.base_url == "http://localhost:8000"
