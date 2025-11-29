"""
Unit tests for Google Maps service module.

Tests cover:
- GoogleMapsClient initialization and route fetching
- MockGoogleMapsClient for testing without API
- Route parsing and address extraction
- Edge cases: missing API key, empty routes, invalid data

MIT Level Testing - 85%+ Coverage Target
"""

import sys
from unittest.mock import MagicMock, patch

import pytest

# Mock googlemaps before importing the module
sys.modules['googlemaps'] = MagicMock()

from src.models.route import Route, RoutePoint  # noqa: E402
from src.services.google_maps import (  # noqa: E402
    GoogleMapsClient,
    MockGoogleMapsClient,
    get_maps_client,
    get_mock_route,
)


class TestMockGoogleMapsClient:
    """Tests for MockGoogleMapsClient class."""
    
    def test_initialization(self):
        """Test MockGoogleMapsClient initialization."""
        MockGoogleMapsClient()
        # Should not raise

    def test_initialization_with_api_key(self):
        """Test initialization ignores API key."""
        MockGoogleMapsClient(api_key="test_key")
        # Should not raise
    
    def test_get_route_returns_route(self):
        """Test get_route returns a Route object."""
        client = MockGoogleMapsClient()

        route = client.get_route("Origin", "Destination")
        
        assert isinstance(route, Route)
        assert route.source == "Origin"
        assert route.destination == "Destination"
        assert len(route.points) == 4
    
    def test_get_route_points_valid(self):
        """Test mock route has valid points."""
        client = MockGoogleMapsClient()

        route = client.get_route("A", "B")
        
        for point in route.points:
            assert isinstance(point, RoutePoint)
            assert point.latitude != 0
            assert point.longitude != 0
            assert point.address is not None

    def test_get_route_with_kwargs(self):
        """Test get_route accepts extra kwargs."""
        client = MockGoogleMapsClient()

        route = client.get_route("A", "B", mode="walking", waypoints=["C"])

        assert isinstance(route, Route)
    
    def test_get_place_details(self):
        """Test get_place_details returns dict."""
        client = MockGoogleMapsClient()

        result = client.get_place_details("Test Place")

        assert result is not None
        assert result["name"] == "Test Place"
        assert result["mock"] is True


class TestGoogleMapsClient:
    """Tests for GoogleMapsClient class."""

    @patch("src.services.google_maps.googlemaps.Client")
    def test_initialization_with_api_key(self, mock_client):
        """Test initialization with explicit API key."""
        client = GoogleMapsClient(api_key="test_api_key")

        assert client.api_key == "test_api_key"
        mock_client.assert_called_once_with(key="test_api_key")

    def test_initialization_without_api_key_raises(self):
        """Test initialization without API key raises ValueError."""
        with patch("src.services.google_maps.settings") as mock_settings:
            mock_settings.google_maps_api_key = None

            with pytest.raises(ValueError, match="API key is required"):
                GoogleMapsClient()

    @patch("src.services.google_maps.googlemaps.Client")
    def test_get_route_success(self, mock_client_class):
        """Test successful route fetching."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        # Mock directions response
        mock_client.directions.return_value = [
            {
                "legs": [
                    {
                        "start_location": {"lat": 32.0, "lng": 34.0},
                        "start_address": "Start Address",
                        "end_location": {"lat": 32.1, "lng": 34.1},
                        "end_address": "End Address",
                        "distance": {"value": 10000},
                        "duration": {"value": 600},
                        "steps": [
                            {
                                "end_location": {"lat": 32.1, "lng": 34.1},
                                "distance": {"value": 10000},
                                "duration": {"value": 600},
                                "html_instructions": "<b>Head</b> north",
                            }
                        ],
                    }
                ]
            }
        ]
        mock_client.reverse_geocode.return_value = [
            {"formatted_address": "Test Address"}
        ]

        client = GoogleMapsClient(api_key="test_key")
        route = client.get_route("Origin", "Destination")

        assert isinstance(route, Route)
        assert route.source == "Origin"
        assert route.destination == "Destination"
        assert len(route.points) > 0

    @patch("src.services.google_maps.googlemaps.Client")
    def test_get_route_no_results(self, mock_client_class):
        """Test get_route when no route found."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.directions.return_value = []

        client = GoogleMapsClient(api_key="test_key")

        with pytest.raises(ValueError, match="No route found"):
            client.get_route("Origin", "Destination")

    @patch("src.services.google_maps.googlemaps.Client")
    def test_get_route_api_error(self, mock_client_class):
        """Test get_route handles API errors."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.directions.side_effect = Exception("API Error")

        client = GoogleMapsClient(api_key="test_key")

        with pytest.raises(Exception, match="API Error"):
            client.get_route("Origin", "Destination")

    @patch("src.services.google_maps.googlemaps.Client")
    def test_get_route_with_waypoints(self, mock_client_class):
        """Test get_route with waypoints."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.directions.return_value = [
            {
                "legs": [
                    {
                        "start_location": {"lat": 32.0, "lng": 34.0},
                        "start_address": "Start",
                        "distance": {"value": 5000},
                        "duration": {"value": 300},
                        "steps": [],
                    }
                ]
            }
        ]

        client = GoogleMapsClient(api_key="test_key")
        client.get_route("A", "B", waypoints=["C", "D"], mode="walking")

        mock_client.directions.assert_called_once()
        call_kwargs = mock_client.directions.call_args[1]
        assert call_kwargs["waypoints"] == ["C", "D"]
        assert call_kwargs["mode"] == "walking"

    @patch("src.services.google_maps.googlemaps.Client")
    def test_extract_location_name(self, mock_client_class):
        """Test location name extraction from address."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        client = GoogleMapsClient(api_key="test_key")

        # Test normal address
        result = client._extract_location_name("123 Main Street, City, Country")
        assert result == "Main Street"

        # Test empty address
        result = client._extract_location_name("")
        assert result is None

        # Test None
        result = client._extract_location_name(None)
        assert result is None

        # Test address with no number
        result = client._extract_location_name("Central Park, New York")
        assert result == "Central Park"

    @patch("src.services.google_maps.googlemaps.Client")
    def test_clean_html(self, mock_client_class):
        """Test HTML cleaning."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        client = GoogleMapsClient(api_key="test_key")

        result = client._clean_html("<b>Turn</b> <i>left</i> on <div>Main St</div>")
        assert result == "Turn left on Main St"

        result = client._clean_html("No HTML here")
        assert result == "No HTML here"

        result = client._clean_html("")
        assert result == ""

    @patch("src.services.google_maps.googlemaps.Client")
    def test_get_address_from_location_success(self, mock_client_class):
        """Test reverse geocoding success."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.reverse_geocode.return_value = [
            {"formatted_address": "123 Test Street"}
        ]

        client = GoogleMapsClient(api_key="test_key")
        result = client._get_address_from_location(32.0, 34.0)

        assert result == "123 Test Street"

    @patch("src.services.google_maps.googlemaps.Client")
    def test_get_address_from_location_empty(self, mock_client_class):
        """Test reverse geocoding with no results."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.reverse_geocode.return_value = []

        client = GoogleMapsClient(api_key="test_key")
        result = client._get_address_from_location(32.0, 34.0)

        assert result is None

    @patch("src.services.google_maps.googlemaps.Client")
    def test_get_address_from_location_error(self, mock_client_class):
        """Test reverse geocoding error handling."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.reverse_geocode.side_effect = Exception("API Error")

        client = GoogleMapsClient(api_key="test_key")
        result = client._get_address_from_location(32.0, 34.0)

        assert result is None

    @patch("src.services.google_maps.googlemaps.Client")
    def test_get_place_details_success(self, mock_client_class):
        """Test successful place details fetch."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.places.return_value = {
            "results": [{"place_id": "abc123", "name": "Test Place"}]
        }
        mock_client.place.return_value = {
            "result": {"name": "Test Place", "rating": 4.5}
        }

        client = GoogleMapsClient(api_key="test_key")
        result = client.get_place_details("Test Place")

        assert result is not None
        assert result["name"] == "Test Place"

    @patch("src.services.google_maps.googlemaps.Client")
    def test_get_place_details_no_results(self, mock_client_class):
        """Test place details with no search results."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.places.return_value = {"results": []}

        client = GoogleMapsClient(api_key="test_key")
        result = client.get_place_details("Unknown Place")

        assert result is None

    @patch("src.services.google_maps.googlemaps.Client")
    def test_get_place_details_error(self, mock_client_class):
        """Test place details error handling."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.places.side_effect = Exception("API Error")

        client = GoogleMapsClient(api_key="test_key")
        result = client.get_place_details("Test Place")

        assert result is None


class TestGetMapsClient:
    """Tests for get_maps_client factory function."""

    def test_get_mock_client_explicitly(self):
        """Test getting mock client when requested."""
        client = get_maps_client(use_mock=True)

        assert isinstance(client, MockGoogleMapsClient)

    @patch("src.services.google_maps.settings")
    def test_get_mock_client_no_api_key(self, mock_settings):
        """Test getting mock client when no API key."""
        mock_settings.google_maps_api_key = None

        client = get_maps_client(use_mock=False)

        assert isinstance(client, MockGoogleMapsClient)

    @patch("src.services.google_maps.googlemaps.Client")
    @patch("src.services.google_maps.settings")
    def test_get_real_client_with_api_key(self, mock_settings, mock_client):
        """Test getting real client when API key is set."""
        mock_settings.google_maps_api_key = "valid_api_key"

        client = get_maps_client(use_mock=False)

        assert isinstance(client, GoogleMapsClient)


class TestGetMockRoute:
    """Tests for get_mock_route helper function."""
    
    def test_get_mock_route_default(self):
        """Test get_mock_route with default params."""
        route = get_mock_route()
        
        assert isinstance(route, Route)
        assert route.source == "Tel Aviv, Israel"
        assert route.destination == "Jerusalem, Israel"
        assert len(route.points) > 0
    
    def test_get_mock_route_custom(self):
        """Test get_mock_route with custom params."""
        route = get_mock_route(origin="Custom Origin", destination="Custom Dest")

        assert route.source == "Custom Origin"
        assert route.destination == "Custom Dest"

    def test_mock_route_has_required_fields(self):
        """Test mock route points have all required fields."""
        route = get_mock_route()
        
        for point in route.points:
            assert point.id is not None
            assert point.index >= 0
            assert point.address is not None
            assert point.latitude != 0
            assert point.longitude != 0


class TestRouteParsingEdgeCases:
    """Tests for route parsing edge cases."""

    @patch("src.services.google_maps.googlemaps.Client")
    def test_parse_route_missing_fields(self, mock_client_class):
        """Test parsing route with missing optional fields."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        # Minimal route data
        mock_client.directions.return_value = [
            {
                "legs": [
                    {
                        "start_location": {"lat": 32.0, "lng": 34.0},
                        "steps": [],
                    }
                ]
            }
        ]

        client = GoogleMapsClient(api_key="test_key")
        route = client.get_route("A", "B")

        assert isinstance(route, Route)
        assert route.total_distance == 0
        assert route.total_duration == 0

    @patch("src.services.google_maps.googlemaps.Client")
    def test_parse_route_multiple_legs(self, mock_client_class):
        """Test parsing route with multiple legs (waypoints)."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_client.directions.return_value = [
            {
                "legs": [
                    {
                        "start_location": {"lat": 32.0, "lng": 34.0},
                        "start_address": "Start",
                        "distance": {"value": 5000},
                        "duration": {"value": 300},
                        "steps": [],
                    },
                    {
                        "start_location": {"lat": 32.1, "lng": 34.1},
                        "start_address": "Waypoint",
                        "distance": {"value": 5000},
                        "duration": {"value": 300},
                        "steps": [],
                    },
                ]
            }
        ]

        client = GoogleMapsClient(api_key="test_key")
        route = client.get_route("A", "B", waypoints=["C"])

        assert route.total_distance == 10000
        assert route.total_duration == 600

    @patch("src.services.google_maps.googlemaps.Client")
    def test_parse_route_step_fallback_address(self, mock_client_class):
        """Test step address fallback to coordinates."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_client.directions.return_value = [
            {
                "legs": [
                    {
                        "start_location": {"lat": 32.0, "lng": 34.0},
                        "start_address": "Start",
                        "distance": {"value": 1000},
                        "duration": {"value": 60},
                        "steps": [
                            {
                                "end_location": {"lat": 32.1234, "lng": 34.5678},
                                "distance": {"value": 1000},
                                "duration": {"value": 60},
                                "html_instructions": "Turn right",
                            }
                        ],
                    }
                ]
            }
        ]
        # Return None for reverse geocode to trigger fallback
        mock_client.reverse_geocode.return_value = None

        client = GoogleMapsClient(api_key="test_key")
        route = client.get_route("A", "B")

        # Should have a fallback address with coordinates
        assert "32.1234" in route.points[-1].address
