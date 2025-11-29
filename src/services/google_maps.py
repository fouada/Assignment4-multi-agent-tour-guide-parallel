"""
Google Maps API module for route extraction.
Fetches directions and extracts waypoints with addresses.
"""
import googlemaps
from typing import List, Optional, Tuple
import re

from src.utils.config import settings
from src.models.route import Route, RoutePoint
from src.utils.logger import get_logger

logger = get_logger(__name__)


class GoogleMapsClient:
    """Client for interacting with Google Maps Directions API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Google Maps client.
        
        Args:
            api_key: Google Maps API key. Uses settings if not provided.
        """
        self.api_key = api_key or settings.google_maps_api_key
        if not self.api_key:
            raise ValueError("Google Maps API key is required. Set GOOGLE_MAPS_API_KEY in .env")
        
        self.client = googlemaps.Client(key=self.api_key)
        set_log_context(agent_type='route')
        logger.info("Google Maps client initialized")
    
    def get_route(
        self, 
        origin: str, 
        destination: str,
        waypoints: Optional[List[str]] = None,
        mode: str = None
    ) -> Route:
        """
        Get a route from origin to destination with detailed waypoints.
        
        Args:
            origin: Starting address
            destination: Ending address
            waypoints: Optional list of waypoints to include
            mode: Travel mode (driving, walking, bicycling, transit)
            
        Returns:
            Route object with all waypoints
        """
        mode = mode or settings.travel_mode
        set_log_context(agent_type='route')
        
        logger.info(f"Fetching route: {origin} → {destination}")
        
        try:
            # Request directions from Google Maps
            directions_result = self.client.directions(
                origin=origin,
                destination=destination,
                mode=mode,
                waypoints=waypoints,
                language=settings.language,
                region="il" if settings.default_country == "Israel" else None,
                alternatives=False
            )
            
            if not directions_result:
                raise ValueError("No route found between the specified locations")
            
            # Parse the first (best) route
            route_data = directions_result[0]
            route = self._parse_route(origin, destination, route_data)
            
            logger.info(f"Route fetched successfully: {route.point_count} points")
            return route
            
        except Exception as e:
            logger.error(f"Error fetching route: {str(e)}")
            raise
    
    def _parse_route(self, origin: str, destination: str, route_data: dict) -> Route:
        """
        Parse Google Maps route data into our Route model.
        
        Args:
            origin: Origin address
            destination: Destination address
            route_data: Raw route data from Google Maps API
            
        Returns:
            Parsed Route object
        """
        points = []
        total_distance = 0
        total_duration = 0
        point_index = 0
        
        # Get the legs (segments between waypoints)
        for leg in route_data.get('legs', []):
            total_distance += leg.get('distance', {}).get('value', 0)
            total_duration += leg.get('duration', {}).get('value', 0)
            
            # Add start location of this leg
            start_location = leg.get('start_location', {})
            start_address = leg.get('start_address', '')
            
            if point_index == 0:  # First point
                points.append(RoutePoint(
                    index=point_index,
                    address=start_address,
                    location_name=self._extract_location_name(start_address),
                    latitude=start_location.get('lat', 0),
                    longitude=start_location.get('lng', 0),
                    instruction="Start",
                    distance_from_start=0,
                    duration_from_start=0
                ))
                point_index += 1
            
            # Process steps within this leg
            cumulative_distance = 0
            cumulative_duration = 0
            
            for step in leg.get('steps', []):
                step_distance = step.get('distance', {}).get('value', 0)
                step_duration = step.get('duration', {}).get('value', 0)
                cumulative_distance += step_distance
                cumulative_duration += step_duration
                
                # Get end location of this step
                end_location = step.get('end_location', {})
                
                # Extract address from HTML instructions or use coordinates
                instruction = self._clean_html(step.get('html_instructions', ''))
                address = self._get_address_from_location(
                    end_location.get('lat'),
                    end_location.get('lng')
                )
                
                points.append(RoutePoint(
                    index=point_index,
                    address=address or f"Point at {end_location.get('lat'):.4f}, {end_location.get('lng'):.4f}",
                    location_name=self._extract_location_name(address) if address else None,
                    latitude=end_location.get('lat', 0),
                    longitude=end_location.get('lng', 0),
                    instruction=instruction,
                    distance_from_start=cumulative_distance,
                    duration_from_start=cumulative_duration
                ))
                point_index += 1
        
        return Route(
            source=origin,
            destination=destination,
            points=points,
            total_distance=total_distance,
            total_duration=total_duration
        )
    
    def _get_address_from_location(self, lat: float, lng: float) -> Optional[str]:
        """
        Reverse geocode to get address from coordinates.
        
        Args:
            lat: Latitude
            lng: Longitude
            
        Returns:
            Address string or None
        """
        try:
            result = self.client.reverse_geocode(
                (lat, lng),
                language=settings.language
            )
            if result:
                return result[0].get('formatted_address', '')
        except Exception:
            pass
        return None
    
    def _extract_location_name(self, address: str) -> Optional[str]:
        """
        Extract a meaningful location name from an address.
        
        Args:
            address: Full address string
            
        Returns:
            Location name or None
        """
        if not address:
            return None
        
        # Split by comma and get the first part (usually the most specific)
        parts = address.split(',')
        if parts:
            name = parts[0].strip()
            # Remove numbers (street numbers)
            name = re.sub(r'^\d+\s*', '', name)
            return name if name else None
        return None
    
    def _clean_html(self, html_text: str) -> str:
        """Remove HTML tags from text."""
        clean = re.sub(r'<[^>]+>', '', html_text)
        return clean.strip()
    
    def get_place_details(self, place_name: str) -> Optional[dict]:
        """
        Get detailed information about a place.
        
        Args:
            place_name: Name of the place to search
            
        Returns:
            Place details dictionary or None
        """
        try:
            # Search for the place
            places_result = self.client.places(
                query=place_name,
                language=settings.language
            )
            
            if places_result.get('results'):
                place = places_result['results'][0]
                place_id = place.get('place_id')
                
                # Get detailed info
                details = self.client.place(
                    place_id=place_id,
                    language=settings.language
                )
                
                return details.get('result', {})
        except Exception as e:
            logger.warning(f"Could not get place details for {place_name}: {e}")
        
        return None


# Mock client for testing without API key
class MockGoogleMapsClient:
    """Mock client for testing without actual API calls."""
    
    def __init__(self, api_key: Optional[str] = None):
        logger.info("Using MOCK Google Maps client (for testing)")
    
    def get_route(self, origin: str, destination: str, **kwargs) -> Route:
        """Return a sample route for testing."""
        # Sample route in Israel
        sample_points = [
            RoutePoint(
                index=0,
                address="Tel Aviv, Israel",
                location_name="Tel Aviv",
                latitude=32.0853,
                longitude=34.7818,
                instruction="Start",
                distance_from_start=0,
                duration_from_start=0
            ),
            RoutePoint(
                index=1,
                address="Latrun, Israel",
                location_name="Latrun Monastery",
                latitude=31.8389,
                longitude=34.9783,
                instruction="Continue on Route 1",
                distance_from_start=25000,
                duration_from_start=1200
            ),
            RoutePoint(
                index=2,
                address="Ammunition Hill, Jerusalem",
                location_name="Ammunition Hill",
                latitude=31.7944,
                longitude=35.2283,
                instruction="Take exit toward Jerusalem",
                distance_from_start=50000,
                duration_from_start=2400
            ),
            RoutePoint(
                index=3,
                address="Old City, Jerusalem",
                location_name="Old City",
                latitude=31.7767,
                longitude=35.2345,
                instruction="Arrive at destination",
                distance_from_start=55000,
                duration_from_start=2700
            ),
        ]
        
        return Route(
            source=origin,
            destination=destination,
            points=sample_points,
            total_distance=55000,
            total_duration=2700
        )
    
    def get_place_details(self, place_name: str) -> Optional[dict]:
        return {"name": place_name, "mock": True}


def get_maps_client(use_mock: bool = False) -> GoogleMapsClient:
    """
    Get the appropriate maps client.
    
    Args:
        use_mock: If True, return mock client for testing
        
    Returns:
        Maps client instance
    """
    if use_mock or not settings.google_maps_api_key:
        logger.warning("Using mock Google Maps client - set GOOGLE_MAPS_API_KEY for real routes")
        return MockGoogleMapsClient()
    return GoogleMapsClient()


def get_mock_route(origin: str = "Tel Aviv, Israel", destination: str = "Jerusalem, Israel") -> Route:
    """
    Get a mock route for demo/testing purposes.
    
    Returns:
        Route object with sample waypoints
    """
    client = MockGoogleMapsClient()
    return client.get_route(origin, destination)

