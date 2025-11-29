"""
Unit tests for the Google Maps service module.

Tests cover:
- MockGoogleMapsClient functionality
- Route generation
- Helper functions
- get_mock_route function

Note: GoogleMapsClient tests require the googlemaps package.
These tests focus on the MockGoogleMapsClient which doesn't require external dependencies.

MIT Level Testing - 85%+ Coverage Target
"""
import pytest
import sys
from unittest.mock import patch, Mock, MagicMock

from src.models.route import Route, RoutePoint


# Mock googlemaps before importing
@pytest.fixture(autouse=True)
def mock_googlemaps():
    """Mock the googlemaps module."""
    mock_module = MagicMock()
    mock_module.Client = MagicMock()
    sys.modules['googlemaps'] = mock_module
    yield mock_module
    # Clean up
    if 'googlemaps' in sys.modules:
        del sys.modules['googlemaps']


class TestMockGoogleMapsClient:
    """Tests for MockGoogleMapsClient class."""
    
    def test_initialization(self, mock_googlemaps):
        """Test MockGoogleMapsClient initialization."""
        # Force reimport with mocked googlemaps
        import importlib
        import src.services.google_maps
        importlib.reload(src.services.google_maps)
        
        from src.services.google_maps import MockGoogleMapsClient
        
        client = MockGoogleMapsClient()
        # Should not raise
    
    def test_get_route_returns_route(self, mock_googlemaps):
        """Test get_route returns a Route object."""
        import importlib
        import src.services.google_maps
        importlib.reload(src.services.google_maps)
        
        from src.services.google_maps import MockGoogleMapsClient
        
        client = MockGoogleMapsClient()
        route = client.get_route("Tel Aviv", "Jerusalem")
        
        assert isinstance(route, Route)
        assert route.source == "Tel Aviv"
        assert route.destination == "Jerusalem"
    
    def test_get_route_has_points(self, mock_googlemaps):
        """Test get_route returns route with points."""
        import importlib
        import src.services.google_maps
        importlib.reload(src.services.google_maps)
        
        from src.services.google_maps import MockGoogleMapsClient
        
        client = MockGoogleMapsClient()
        route = client.get_route("Tel Aviv", "Jerusalem")
        
        assert len(route.points) > 0
        assert all(isinstance(p, RoutePoint) for p in route.points)
    
    def test_get_route_points_have_required_fields(self, mock_googlemaps):
        """Test route points have all required fields."""
        import importlib
        import src.services.google_maps
        importlib.reload(src.services.google_maps)
        
        from src.services.google_maps import MockGoogleMapsClient
        
        client = MockGoogleMapsClient()
        route = client.get_route("Tel Aviv", "Jerusalem")
        
        for point in route.points:
            assert point.id is not None
            assert point.address is not None
            assert point.latitude is not None
            assert point.longitude is not None
    
    def test_get_place_details_returns_dict(self, mock_googlemaps):
        """Test get_place_details returns a dict."""
        import importlib
        import src.services.google_maps
        importlib.reload(src.services.google_maps)
        
        from src.services.google_maps import MockGoogleMapsClient
        
        client = MockGoogleMapsClient()
        details = client.get_place_details("Tel Aviv")
        
        assert isinstance(details, dict)
        assert details["name"] == "Tel Aviv"
        assert details["mock"] is True


class TestGetMockRoute:
    """Tests for get_mock_route function."""
    
    def test_get_mock_route_default(self, mock_googlemaps):
        """Test get_mock_route with default params."""
        import importlib
        import src.services.google_maps
        importlib.reload(src.services.google_maps)
        
        from src.services.google_maps import get_mock_route
        
        route = get_mock_route()
        
        assert isinstance(route, Route)
        assert route.source == "Tel Aviv, Israel"
        assert route.destination == "Jerusalem, Israel"
    
    def test_get_mock_route_custom(self, mock_googlemaps):
        """Test get_mock_route with custom params."""
        import importlib
        import src.services.google_maps
        importlib.reload(src.services.google_maps)
        
        from src.services.google_maps import get_mock_route
        
        route = get_mock_route(origin="A", destination="B")
        
        assert route.source == "A"
        assert route.destination == "B"


class TestGetMapsClient:
    """Tests for get_maps_client function."""
    
    def test_get_maps_client_mock(self, mock_googlemaps):
        """Test get_maps_client returns mock when requested."""
        import importlib
        import src.services.google_maps
        importlib.reload(src.services.google_maps)
        
        from src.services.google_maps import get_maps_client, MockGoogleMapsClient
        
        client = get_maps_client(use_mock=True)
        assert isinstance(client, MockGoogleMapsClient)


class TestGoogleMapsClientHelpers:
    """Tests for GoogleMapsClient helper methods."""
    
    def test_extract_location_name(self, mock_googlemaps):
        """Test location name extraction."""
        import importlib
        import src.services.google_maps
        importlib.reload(src.services.google_maps)
        
        from src.services.google_maps import GoogleMapsClient
        
        # Create client with mocked API
        with patch.object(GoogleMapsClient, '__init__', lambda x, **k: None):
            client = GoogleMapsClient()
            client.api_key = "test"
            client.client = Mock()
            
            # Add the method manually since __init__ is mocked
            from src.services.google_maps import GoogleMapsClient as OrigClass
            client._extract_location_name = OrigClass._extract_location_name.__get__(client, OrigClass)
            
            # Test with address
            name = client._extract_location_name("Tel Aviv, Israel")
            assert name == "Tel Aviv"
            
            # Test with street number
            name = client._extract_location_name("123 Main Street, City")
            assert name == "Main Street"
            
            # Test with empty
            name = client._extract_location_name("")
            assert name is None
            
            # Test with None
            name = client._extract_location_name(None)
            assert name is None
    
    def test_clean_html(self, mock_googlemaps):
        """Test HTML cleaning."""
        import importlib
        import src.services.google_maps
        importlib.reload(src.services.google_maps)
        
        from src.services.google_maps import GoogleMapsClient
        
        with patch.object(GoogleMapsClient, '__init__', lambda x, **k: None):
            client = GoogleMapsClient()
            
            from src.services.google_maps import GoogleMapsClient as OrigClass
            client._clean_html = OrigClass._clean_html.__get__(client, OrigClass)
            
            # Test with HTML
            clean = client._clean_html("<div>Turn <b>left</b></div>")
            assert clean == "Turn left"
            
            # Test without HTML
            clean = client._clean_html("Plain text")
            assert clean == "Plain text"


class TestRoutePoints:
    """Additional tests for route point structure."""
    
    def test_mock_route_has_latrun(self, mock_googlemaps):
        """Test mock route includes Latrun."""
        import importlib
        import src.services.google_maps
        importlib.reload(src.services.google_maps)
        
        from src.services.google_maps import get_mock_route
        
        route = get_mock_route()
        
        latrun_point = next(
            (p for p in route.points if "Latrun" in p.address),
            None
        )
        assert latrun_point is not None
    
    def test_mock_route_has_ammunition_hill(self, mock_googlemaps):
        """Test mock route includes Ammunition Hill."""
        import importlib
        import src.services.google_maps
        importlib.reload(src.services.google_maps)
        
        from src.services.google_maps import get_mock_route
        
        route = get_mock_route()
        
        ammo_point = next(
            (p for p in route.points if "Ammunition" in p.address),
            None
        )
        assert ammo_point is not None
    
    def test_mock_route_points_ordered(self, mock_googlemaps):
        """Test mock route points are ordered by index."""
        import importlib
        import src.services.google_maps
        importlib.reload(src.services.google_maps)
        
        from src.services.google_maps import get_mock_route
        
        route = get_mock_route()
        
        for i, point in enumerate(route.points):
            assert point.index == i
    
    def test_mock_route_total_distance(self, mock_googlemaps):
        """Test mock route has valid total distance."""
        import importlib
        import src.services.google_maps
        importlib.reload(src.services.google_maps)
        
        from src.services.google_maps import get_mock_route
        
        route = get_mock_route()
        
        assert route.total_distance > 0
        assert route.total_duration > 0
