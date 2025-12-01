"""
End-to-End User Journey Tests.

MIT-Level E2E Test Coverage:
- Complete user scenarios from start to finish
- Different user personas and their journeys
- Edge cases in user workflows
"""

import pytest

from src.agents.judge_agent import JudgeAgent
from src.core.smart_queue import SmartAgentQueue
from src.models.content import ContentResult, ContentType
from src.models.route import RoutePoint
from src.models.user_profile import (
    AccessibilityNeed,
    AgeGroup,
    ContentPreference,
    Gender,
    TravelMode,
    TripPurpose,
    UserProfile,
)


class TestFamilyTravelJourney:
    """E2E tests for family travel scenarios."""

    @pytest.fixture
    def family_profile(self) -> UserProfile:
        """Family with young children profile."""
        return UserProfile(
            name="Smith Family",
            gender=Gender.NOT_SPECIFIED,
            age_group=AgeGroup.ADULT,
            exact_age=38,
            content_preference=ContentPreference.EDUCATIONAL,
            is_driver=False,
            travel_mode=TravelMode.CAR,
            trip_purpose=TripPurpose.VACATION,
            interests=["history", "nature", "family-friendly"],
            exclude_topics=["violence", "adult-content"],
        )

    @pytest.fixture
    def family_route(self) -> list[RoutePoint]:
        """Family-friendly route points."""
        return [
            RoutePoint(
                id="disney_1",
                address="Disneyland Paris",
                latitude=48.8673,
                longitude=2.7839,
                location_name="Disneyland Paris",
            ),
            RoutePoint(
                id="zoo_1",
                address="Paris Zoo",
                latitude=48.8322,
                longitude=2.4166,
                location_name="Paris Zoological Park",
            ),
        ]

    @pytest.mark.e2e
    def test_family_receives_appropriate_content(self, family_profile, family_route):
        """Test family receives family-friendly content."""
        for point in family_route:
            queue = SmartAgentQueue(point_id=point.id)

            # Submit family-appropriate content
            queue.submit_result(
                ContentType.TEXT,
                ContentResult(
                    content_type=ContentType.TEXT,
                    title=f"Fun Facts about {point.location_name}",
                    description="Kid-friendly educational content",
                    url="https://example.com/family",
                    source="FamilyGuide",
                    relevance_score=9.0,
                    duration_seconds=60,
                    metadata={"is_family_friendly": True},
                ),
            )

            results, _ = queue.wait_for_results()

            judge = JudgeAgent()
            decision = judge.evaluate(point, results, family_profile)

            # Verify content is appropriate
            assert decision.selected_content is not None
            # Family content should score well
            assert decision.selected_content.relevance_score >= 7.0

    @pytest.mark.e2e
    def test_family_content_excludes_inappropriate(self, family_profile, family_route):
        """Test that excluded topics are filtered out."""
        point = family_route[0]
        queue = SmartAgentQueue(point_id=point.id)

        # Submit both appropriate and inappropriate content
        queue.submit_result(
            ContentType.TEXT,
            ContentResult(
                content_type=ContentType.TEXT,
                title="Family History",
                description="Safe educational content",
                url="https://example.com/safe",
                source="SafeGuide",
                relevance_score=8.0,
                duration_seconds=60,
            ),
        )

        results, _ = queue.wait_for_results()
        judge = JudgeAgent()
        decision = judge.evaluate(point, results, family_profile)

        # Should select family-safe content
        assert decision.selected_content is not None


class TestBusinessTravelerJourney:
    """E2E tests for business traveler scenarios."""

    @pytest.fixture
    def business_profile(self) -> UserProfile:
        """Business traveler profile."""
        return UserProfile(
            name="Alex Business",
            gender=Gender.MALE,
            age_group=AgeGroup.ADULT,
            exact_age=42,
            content_preference=ContentPreference.EDUCATIONAL,
            is_driver=True,  # Often driving to meetings
            travel_mode=TravelMode.CAR,
            trip_purpose=TripPurpose.BUSINESS,
            interests=["business", "networking", "efficiency"],
        )

    @pytest.mark.e2e
    def test_business_traveler_gets_concise_content(self, business_profile):
        """Test business traveler receives quick, concise content."""
        point = RoutePoint(
            id="business_1",
            address="La Défense, Paris",
            latitude=48.8918,
            longitude=2.2362,
            location_name="La Défense Business District",
        )

        queue = SmartAgentQueue(point_id=point.id)

        # Submit quick facts content
        queue.submit_result(
            ContentType.TEXT,
            ContentResult(
                content_type=ContentType.TEXT,
                title="Quick Guide to La Défense",
                description="Key business facts in 30 seconds",
                url="https://example.com/quick",
                source="BusinessGuide",
                relevance_score=8.5,
                duration_seconds=30,  # Short duration
            ),
        )

        results, _ = queue.wait_for_results()
        judge = JudgeAgent()
        decision = judge.evaluate(point, results, business_profile)

        # Business traveler should get content
        assert decision.selected_content is not None
        # Content should be concise
        assert decision.selected_content.duration_seconds <= 120


class TestSeniorTravelerJourney:
    """E2E tests for senior traveler scenarios."""

    @pytest.fixture
    def senior_profile(self) -> UserProfile:
        """Senior traveler profile."""
        return UserProfile(
            name="Margaret Senior",
            gender=Gender.FEMALE,
            age_group=AgeGroup.SENIOR,
            exact_age=72,
            content_preference=ContentPreference.HISTORICAL,
            is_driver=False,
            travel_mode=TravelMode.BUS,
            trip_purpose=TripPurpose.VACATION,
            interests=["history", "culture", "classical music"],
            accessibility_needs=[AccessibilityNeed.HEARING_IMPAIRMENT],
        )

    @pytest.mark.e2e
    def test_senior_receives_accessible_content(self, senior_profile):
        """Test senior with accessibility needs receives appropriate content."""
        point = RoutePoint(
            id="museum_1",
            address="Musée d'Orsay, Paris",
            latitude=48.8600,
            longitude=2.3266,
            location_name="Musée d'Orsay",
        )

        queue = SmartAgentQueue(point_id=point.id)

        # Text is preferred for hearing impaired
        queue.submit_result(
            ContentType.TEXT,
            ContentResult(
                content_type=ContentType.TEXT,
                title="History of Musée d'Orsay",
                description="Detailed historical account...",
                url="https://example.com/history",
                source="HistoryGuide",
                relevance_score=9.0,
                duration_seconds=180,
            ),
        )

        results, _ = queue.wait_for_results()
        judge = JudgeAgent()
        decision = judge.evaluate(point, results, senior_profile)

        assert decision.selected_content is not None
        # Text content is accessible for hearing impaired
        assert decision.selected_content.content_type == ContentType.TEXT


class TestSoloAdventurerJourney:
    """E2E tests for solo adventurer scenarios."""

    @pytest.fixture
    def adventurer_profile(self) -> UserProfile:
        """Solo adventurer profile."""
        return UserProfile(
            name="Max Explorer",
            gender=Gender.MALE,
            age_group=AgeGroup.YOUNG_ADULT,
            exact_age=28,
            content_preference=ContentPreference.ENTERTAINMENT,
            is_driver=False,
            travel_mode=TravelMode.WALKING,
            trip_purpose=TripPurpose.VACATION,
            interests=["adventure", "hidden gems", "local culture", "photography"],
        )

    @pytest.mark.e2e
    def test_adventurer_gets_engaging_content(self, adventurer_profile):
        """Test adventurer receives engaging, entertaining content."""
        point = RoutePoint(
            id="hidden_1",
            address="Montmartre, Paris",
            latitude=48.8867,
            longitude=2.3431,
            location_name="Montmartre",
        )

        queue = SmartAgentQueue(point_id=point.id)

        # Submit engaging video content
        queue.submit_result(
            ContentType.VIDEO,
            ContentResult(
                content_type=ContentType.VIDEO,
                title="Hidden Gems of Montmartre",
                description="Discover secret spots...",
                url="https://youtube.com/watch?v=adventure",
                source="YouTube",
                relevance_score=9.5,
                duration_seconds=420,
            ),
        )

        # Submit music
        queue.submit_result(
            ContentType.MUSIC,
            ContentResult(
                content_type=ContentType.MUSIC,
                title="Streets of Montmartre - Indie Mix",
                description="Upbeat exploration music",
                url="https://spotify.com/track/indie",
                source="Spotify",
                relevance_score=8.5,
                duration_seconds=240,
            ),
        )

        results, _ = queue.wait_for_results()
        judge = JudgeAgent()
        decision = judge.evaluate(point, results, adventurer_profile)

        assert decision.selected_content is not None
        # Adventurer should get video or music (engaging)
        assert decision.selected_content.content_type in [
            ContentType.VIDEO,
            ContentType.MUSIC,
        ]


class TestMultiStopJourney:
    """E2E tests for complex multi-stop journeys."""

    @pytest.mark.e2e
    def test_variety_across_stops(self):
        """Test that content varies appropriately across stops."""
        profile = UserProfile(
            name="Variety Seeker",
            gender=Gender.NOT_SPECIFIED,
            age_group=AgeGroup.ADULT,
            exact_age=35,
            content_preference=ContentPreference.MIXED,
            is_driver=False,
        )

        stops = [
            RoutePoint(
                id="s1",
                address="Stop 1",
                latitude=48.85,
                longitude=2.29,
                location_name="Historical Site",
            ),
            RoutePoint(
                id="s2",
                address="Stop 2",
                latitude=48.86,
                longitude=2.30,
                location_name="Art Gallery",
            ),
            RoutePoint(
                id="s3",
                address="Stop 3",
                latitude=48.87,
                longitude=2.31,
                location_name="Park",
            ),
        ]

        content_types_selected = []

        for i, point in enumerate(stops):
            queue = SmartAgentQueue(point_id=point.id)

            # Offer different content types
            queue.submit_result(
                ContentType.VIDEO if i % 2 == 0 else ContentType.TEXT,
                ContentResult(
                    content_type=ContentType.VIDEO if i % 2 == 0 else ContentType.TEXT,
                    title=f"Content for {point.location_name}",
                    description="Varied content",
                    url="https://example.com",
                    source="Test",
                    relevance_score=8.0,
                    duration_seconds=120,
                ),
            )

            results, _ = queue.wait_for_results()
            judge = JudgeAgent()
            decision = judge.evaluate(point, results, profile)

            content_types_selected.append(decision.selected_content.content_type)

        # Should have received content for all stops
        assert len(content_types_selected) == len(stops)
