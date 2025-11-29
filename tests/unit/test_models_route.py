"""
Unit tests for Route and RoutePoint models.

Test Coverage:
- RoutePoint creation and properties
- Route creation with points
- get_point_by_id functionality
- Coordinate handling
- Edge cases: empty routes, missing data
"""

from datetime import datetime

from src.models.route import Route, RoutePoint


class TestRoutePoint:
    """Tests for RoutePoint model."""

    def test_create_minimal_route_point(self):
        """Test creating route point with minimum required fields."""
        point = RoutePoint(
            index=0, address="Tel Aviv, Israel", latitude=32.0853, longitude=34.7818
        )
        assert point.index == 0
        assert point.address == "Tel Aviv, Israel"
        assert point.latitude == 32.0853
        assert point.longitude == 34.7818
        assert point.id  # Auto-generated

    def test_create_full_route_point(self):
        """Test creating route point with all fields."""
        point = RoutePoint(
            id="custom_id",
            index=1,
            address="Ammunition Hill, Jerusalem",
            location_name="Ammunition Hill",
            latitude=31.7944,
            longitude=35.2283,
            instruction="Turn right onto Derech Shlomo Goren",
            distance_from_start=55000.0,
            duration_from_start=2700.0,
        )
        assert point.id == "custom_id"
        assert point.location_name == "Ammunition Hill"
        assert point.instruction == "Turn right onto Derech Shlomo Goren"
        assert point.distance_from_start == 55000.0
        assert point.duration_from_start == 2700.0

    def test_route_point_auto_generated_id(self):
        """Test that ID is auto-generated if not provided."""
        point1 = RoutePoint(index=0, address="Test", latitude=31.0, longitude=35.0)
        point2 = RoutePoint(index=1, address="Test 2", latitude=31.1, longitude=35.1)
        assert point1.id
        assert point2.id
        assert point1.id != point2.id
        assert len(point1.id) == 8  # UUID truncated to 8 chars

    def test_coordinates_property(self):
        """Test coordinates tuple property."""
        point = RoutePoint(index=0, address="Test", latitude=31.7683, longitude=35.2137)
        assert point.coordinates == (31.7683, 35.2137)
        assert isinstance(point.coordinates, tuple)

    def test_route_point_negative_coordinates(self):
        """Test negative coordinates (Western/Southern hemisphere)."""
        point = RoutePoint(
            index=0,
            address="Buenos Aires, Argentina",
            latitude=-34.6037,
            longitude=-58.3816,
        )
        assert point.latitude == -34.6037
        assert point.longitude == -58.3816
        assert point.coordinates == (-34.6037, -58.3816)

    def test_route_point_boundary_coordinates(self):
        """Test extreme coordinate values."""
        # North Pole
        north = RoutePoint(index=0, address="North Pole", latitude=90.0, longitude=0.0)
        assert north.latitude == 90.0

        # South Pole
        south = RoutePoint(index=1, address="South Pole", latitude=-90.0, longitude=0.0)
        assert south.latitude == -90.0

        # International Date Line
        dateline = RoutePoint(index=2, address="Pacific", latitude=0.0, longitude=180.0)
        assert dateline.longitude == 180.0

    def test_route_point_optional_fields(self):
        """Test optional fields default to None."""
        point = RoutePoint(index=0, address="Test", latitude=31.0, longitude=35.0)
        assert point.location_name is None
        assert point.instruction is None
        assert point.distance_from_start is None
        assert point.duration_from_start is None

    def test_route_point_json_serialization(self):
        """Test route point serialization."""
        point = RoutePoint(
            id="test_id",
            index=0,
            address="Jerusalem",
            location_name="Old City",
            latitude=31.7683,
            longitude=35.2137,
        )
        json_dict = point.model_dump()
        assert json_dict["id"] == "test_id"
        assert json_dict["index"] == 0
        assert json_dict["address"] == "Jerusalem"
        assert json_dict["location_name"] == "Old City"


class TestRoute:
    """Tests for Route model."""

    def test_create_empty_route(self):
        """Test creating route with no points."""
        route = Route(source="Tel Aviv", destination="Jerusalem")
        assert route.source == "Tel Aviv"
        assert route.destination == "Jerusalem"
        assert route.points == []
        assert route.point_count == 0

    def test_create_route_with_points(self):
        """Test creating route with multiple points."""
        points = [
            RoutePoint(
                id="p1",
                index=0,
                address="Tel Aviv",
                latitude=32.0853,
                longitude=34.7818,
            ),
            RoutePoint(
                id="p2", index=1, address="Latrun", latitude=31.8389, longitude=34.9789
            ),
            RoutePoint(
                id="p3",
                index=2,
                address="Jerusalem",
                latitude=31.7683,
                longitude=35.2137,
            ),
        ]
        route = Route(
            source="Tel Aviv",
            destination="Jerusalem",
            points=points,
            total_distance=55000,
            total_duration=2700,
        )
        assert route.point_count == 3
        assert route.total_distance == 55000
        assert route.total_duration == 2700

    def test_route_auto_generated_id(self):
        """Test that route ID is auto-generated."""
        route = Route(source="A", destination="B")
        assert route.id
        assert len(route.id) == 36  # Full UUID

    def test_get_point_by_id_found(self):
        """Test getting point by ID when it exists."""
        points = [
            RoutePoint(
                id="point_1", index=0, address="Start", latitude=31.0, longitude=35.0
            ),
            RoutePoint(
                id="point_2", index=1, address="Middle", latitude=31.5, longitude=35.5
            ),
            RoutePoint(
                id="point_3", index=2, address="End", latitude=32.0, longitude=36.0
            ),
        ]
        route = Route(source="Start", destination="End", points=points)

        found = route.get_point_by_id("point_2")
        assert found is not None
        assert found.id == "point_2"
        assert found.address == "Middle"

    def test_get_point_by_id_not_found(self):
        """Test getting point by ID when it doesn't exist."""
        points = [
            RoutePoint(
                id="p1", index=0, address="Start", latitude=31.0, longitude=35.0
            ),
        ]
        route = Route(source="Start", destination="End", points=points)

        found = route.get_point_by_id("nonexistent")
        assert found is None

    def test_get_point_by_id_empty_route(self):
        """Test getting point from empty route."""
        route = Route(source="A", destination="B")
        assert route.get_point_by_id("any_id") is None

    def test_route_point_count(self):
        """Test point_count property."""
        route_empty = Route(source="A", destination="B")
        assert route_empty.point_count == 0

        points = [
            RoutePoint(
                id=f"p{i}",
                index=i,
                address=f"Point {i}",
                latitude=31.0 + i * 0.1,
                longitude=35.0,
            )
            for i in range(5)
        ]
        route_with_points = Route(source="A", destination="B", points=points)
        assert route_with_points.point_count == 5

    def test_route_created_at_auto(self):
        """Test created_at is automatically set."""
        before = datetime.now()
        route = Route(source="A", destination="B")
        after = datetime.now()
        assert before <= route.created_at <= after

    def test_route_json_serialization(self):
        """Test route serialization."""
        points = [
            RoutePoint(
                id="p1",
                index=0,
                address="Tel Aviv",
                latitude=32.0853,
                longitude=34.7818,
            ),
        ]
        route = Route(
            source="Tel Aviv",
            destination="Jerusalem",
            points=points,
            total_distance=55000,
        )
        json_dict = route.model_dump()
        assert json_dict["source"] == "Tel Aviv"
        assert json_dict["destination"] == "Jerusalem"
        assert len(json_dict["points"]) == 1
        assert json_dict["total_distance"] == 55000


class TestRouteEdgeCases:
    """Edge case tests for Route models."""

    def test_unicode_addresses(self):
        """Test unicode characters in addresses."""
        point = RoutePoint(
            index=0,
            address="ירושלים, ישראל",
            location_name="העיר העתיקה",
            latitude=31.7683,
            longitude=35.2137,
        )
        assert "ירושלים" in point.address

        route = Route(source="תל אביב", destination="ירושלים")
        assert route.source == "תל אביב"

    def test_very_long_route(self):
        """Test route with many points."""
        points = [
            RoutePoint(
                id=f"p{i}",
                index=i,
                address=f"Point {i}",
                latitude=31.0 + i * 0.001,
                longitude=35.0,
            )
            for i in range(1000)
        ]
        route = Route(source="Start", destination="End", points=points)
        assert route.point_count == 1000
        assert route.get_point_by_id("p500") is not None

    def test_duplicate_point_ids(self):
        """Test handling duplicate point IDs (gets first match)."""
        points = [
            RoutePoint(
                id="same_id", index=0, address="First", latitude=31.0, longitude=35.0
            ),
            RoutePoint(
                id="same_id", index=1, address="Second", latitude=32.0, longitude=36.0
            ),
        ]
        route = Route(source="A", destination="B", points=points)
        found = route.get_point_by_id("same_id")
        assert found.address == "First"  # Returns first match

    def test_zero_distance_and_duration(self):
        """Test route with zero distance and duration."""
        route = Route(
            source="Same Place",
            destination="Same Place",
            total_distance=0,
            total_duration=0,
        )
        assert route.total_distance == 0
        assert route.total_duration == 0

    def test_very_large_distance(self):
        """Test very large distance values."""
        route = Route(
            source="Sydney",
            destination="London",
            total_distance=17000000,  # ~17000 km in meters
            total_duration=86400 * 7,  # 7 days
        )
        assert route.total_distance == 17000000
        assert route.total_duration == 86400 * 7

    def test_route_point_with_empty_address(self):
        """Test route point with empty address."""
        point = RoutePoint(index=0, address="", latitude=31.0, longitude=35.0)
        assert point.address == ""

    def test_route_source_destination_same(self):
        """Test route where source and destination are the same."""
        route = Route(source="Jerusalem", destination="Jerusalem")
        assert route.source == route.destination
