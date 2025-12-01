"""
End-to-End Accessibility Compliance Tests.

MIT-Level E2E Test Coverage:
- Visual impairment accommodations
- Hearing impairment accommodations
- Cognitive accessibility
- Multi-disability support
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
    UserProfile,
)


class TestVisualImpairmentAccessibility:
    """E2E tests for users with visual impairments."""

    @pytest.fixture
    def visually_impaired_profile(self) -> UserProfile:
        """Profile for user with visual impairment."""
        return UserProfile(
            name="Vision User",
            gender=Gender.NOT_SPECIFIED,
            age_group=AgeGroup.ADULT,
            exact_age=45,
            content_preference=ContentPreference.EDUCATIONAL,
            is_driver=False,
            accessibility_needs=[AccessibilityNeed.VISUAL_IMPAIRMENT],
            prefer_audio_description=True,
            interests=["history", "music"],
        )

    @pytest.fixture
    def test_point(self) -> RoutePoint:
        """Test route point."""
        return RoutePoint(
            id="accessibility_test",
            address="Historic Site",
            latitude=48.8584,
            longitude=2.2945,
            location_name="Historic Monument",
        )

    @pytest.mark.e2e
    def test_visual_impairment_prefers_audio(
        self, visually_impaired_profile, test_point
    ):
        """Test that visually impaired users get audio-friendly content."""
        queue = SmartAgentQueue(point_id=test_point.id)

        # Submit various content types
        queue.submit_result(
            ContentType.VIDEO,
            ContentResult(
                content_type=ContentType.VIDEO,
                title="Visual Documentary",
                description="Heavy on visuals",
                url="https://youtube.com/watch?v=visual",
                source="YouTube",
                relevance_score=9.0,
                duration_seconds=300,
            ),
        )
        queue.submit_result(
            ContentType.MUSIC,
            ContentResult(
                content_type=ContentType.MUSIC,
                title="Historical Music",
                description="Period-appropriate music",
                url="https://spotify.com/track/historical",
                source="Spotify",
                relevance_score=8.0,
                duration_seconds=240,
            ),
        )
        queue.submit_result(
            ContentType.TEXT,
            ContentResult(
                content_type=ContentType.TEXT,
                title="Audio Guide Script",
                description="Can be read aloud by screen reader",
                url="https://example.com/audio-guide",
                source="AudioGuide",
                relevance_score=8.5,
                duration_seconds=180,
            ),
        )

        results, _ = queue.wait_for_results()
        judge = JudgeAgent()
        decision = judge.evaluate(test_point, results, visually_impaired_profile)

        # Should prefer audio-friendly content (music or text for TTS)
        assert decision.selected_content.content_type in [
            ContentType.MUSIC,
            ContentType.TEXT,
        ]

    @pytest.mark.e2e
    def test_visual_impairment_video_weight_reduced(self, visually_impaired_profile):
        """Test that video weight is reduced for visually impaired users."""
        weights = visually_impaired_profile.get_content_type_preferences()

        video_weight = weights.get("video", weights.get(ContentType.VIDEO, 1.0))
        music_weight = weights.get("music", weights.get(ContentType.MUSIC, 1.0))

        # Video should be deprioritized compared to music
        assert video_weight < music_weight


class TestHearingImpairmentAccessibility:
    """E2E tests for users with hearing impairments."""

    @pytest.fixture
    def hearing_impaired_profile(self) -> UserProfile:
        """Profile for user with hearing impairment."""
        return UserProfile(
            name="Hearing User",
            gender=Gender.FEMALE,
            age_group=AgeGroup.ADULT,
            exact_age=38,
            content_preference=ContentPreference.EDUCATIONAL,
            is_driver=False,
            accessibility_needs=[AccessibilityNeed.HEARING_IMPAIRMENT],
            requires_subtitles=True,
            interests=["art", "photography", "history"],
        )

    @pytest.fixture
    def test_point(self) -> RoutePoint:
        """Test route point."""
        return RoutePoint(
            id="hearing_test",
            address="Art Gallery",
            latitude=48.8606,
            longitude=2.3376,
            location_name="Art Museum",
        )

    @pytest.mark.e2e
    def test_hearing_impairment_prefers_visual(
        self, hearing_impaired_profile, test_point
    ):
        """Test that hearing impaired users get visual-friendly content."""
        queue = SmartAgentQueue(point_id=test_point.id)

        queue.submit_result(
            ContentType.VIDEO,
            ContentResult(
                content_type=ContentType.VIDEO,
                title="Art Documentary with Subtitles",
                description="Visual content with captions",
                url="https://youtube.com/watch?v=art",
                source="YouTube",
                relevance_score=8.5,
                duration_seconds=300,
                metadata={"has_subtitles": True},
            ),
        )
        queue.submit_result(
            ContentType.MUSIC,
            ContentResult(
                content_type=ContentType.MUSIC,
                title="Classical Music",
                description="Audio only",
                url="https://spotify.com/classical",
                source="Spotify",
                relevance_score=9.0,  # Higher score but not accessible
                duration_seconds=240,
            ),
        )
        queue.submit_result(
            ContentType.TEXT,
            ContentResult(
                content_type=ContentType.TEXT,
                title="Art History Guide",
                description="Detailed written content",
                url="https://example.com/art-guide",
                source="ArtGuide",
                relevance_score=8.0,
                duration_seconds=180,
            ),
        )

        results, _ = queue.wait_for_results()
        judge = JudgeAgent()
        decision = judge.evaluate(test_point, results, hearing_impaired_profile)

        # Should prefer visual content (video with subtitles or text)
        assert decision.selected_content.content_type in [
            ContentType.VIDEO,
            ContentType.TEXT,
        ]

    @pytest.mark.e2e
    def test_hearing_impairment_music_weight_reduced(self, hearing_impaired_profile):
        """Test that music weight is reduced for hearing impaired users."""
        weights = hearing_impaired_profile.get_content_type_preferences()

        music_weight = weights.get("music", weights.get(ContentType.MUSIC, 1.0))
        text_weight = weights.get("text", weights.get(ContentType.TEXT, 1.0))

        # Music should be deprioritized compared to text
        assert music_weight < text_weight


class TestCognitiveAccessibility:
    """E2E tests for users with cognitive accessibility needs."""

    @pytest.fixture
    def cognitive_needs_profile(self) -> UserProfile:
        """Profile for user with cognitive accessibility needs."""
        return UserProfile(
            name="Cognitive User",
            gender=Gender.NOT_SPECIFIED,
            age_group=AgeGroup.ADULT,
            exact_age=30,
            content_preference=ContentPreference.EDUCATIONAL,  # Simpler content
            is_driver=False,
            accessibility_needs=[AccessibilityNeed.COGNITIVE],
            interests=["nature", "animals"],
        )

    @pytest.mark.e2e
    def test_cognitive_needs_gets_simple_content(self, cognitive_needs_profile):
        """Test that users with cognitive needs get simpler content."""
        test_point = RoutePoint(
            id="cognitive_test",
            address="Nature Park",
            latitude=48.87,
            longitude=2.35,
            location_name="City Park",
        )

        queue = SmartAgentQueue(point_id=test_point.id)

        # Simple, short content
        queue.submit_result(
            ContentType.TEXT,
            ContentResult(
                content_type=ContentType.TEXT,
                title="Quick Park Facts",
                description="Simple bullet points about the park",
                url="https://example.com/quick-facts",
                source="SimpleGuide",
                relevance_score=8.0,
                duration_seconds=30,  # Short duration
            ),
        )

        results, _ = queue.wait_for_results()
        judge = JudgeAgent()
        decision = judge.evaluate(test_point, results, cognitive_needs_profile)

        # Should receive simple, short content
        assert decision.selected_content.duration_seconds <= 180


class TestMultipleAccessibilityNeed:
    """E2E tests for users with multiple accessibility needs."""

    @pytest.fixture
    def multi_accessibility_profile(self) -> UserProfile:
        """Profile with multiple accessibility needs."""
        return UserProfile(
            name="Multi-Need User",
            gender=Gender.MALE,
            age_group=AgeGroup.SENIOR,
            exact_age=70,
            content_preference=ContentPreference.EDUCATIONAL,
            is_driver=False,
            accessibility_needs=[
                AccessibilityNeed.VISUAL_IMPAIRMENT,
                AccessibilityNeed.HEARING_IMPAIRMENT,
            ],
            interests=["history"],
        )

    @pytest.mark.e2e
    def test_multiple_needs_finds_best_compromise(self, multi_accessibility_profile):
        """Test that system finds best content for multiple needs."""
        test_point = RoutePoint(
            id="multi_test",
            address="History Museum",
            latitude=48.86,
            longitude=2.33,
            location_name="History Museum",
        )

        queue = SmartAgentQueue(point_id=test_point.id)

        # Text is accessible for both visual (TTS) and hearing impaired
        queue.submit_result(
            ContentType.TEXT,
            ContentResult(
                content_type=ContentType.TEXT,
                title="Accessible History Guide",
                description="Can be read by screen reader or visually",
                url="https://example.com/accessible",
                source="AccessibleGuide",
                relevance_score=8.0,
                duration_seconds=120,
            ),
        )
        queue.submit_result(
            ContentType.VIDEO,
            ContentResult(
                content_type=ContentType.VIDEO,
                title="History Video",
                description="Visual content",
                url="https://youtube.com/watch?v=history",
                source="YouTube",
                relevance_score=8.5,
                duration_seconds=300,
            ),
        )
        queue.submit_result(
            ContentType.MUSIC,
            ContentResult(
                content_type=ContentType.MUSIC,
                title="Historical Music",
                description="Audio only",
                url="https://spotify.com/historical",
                source="Spotify",
                relevance_score=7.5,
                duration_seconds=240,
            ),
        )

        results, _ = queue.wait_for_results()
        judge = JudgeAgent()
        decision = judge.evaluate(test_point, results, multi_accessibility_profile)

        # Text is most accessible for both visual and hearing needs
        assert decision.selected_content.content_type == ContentType.TEXT


class TestAccessibilityEdgeCases:
    """E2E tests for accessibility edge cases."""

    @pytest.mark.e2e
    def test_no_accessible_content_handling(self):
        """Test handling when no fully accessible content is available."""
        profile = UserProfile(
            name="Edge Case User",
            gender=Gender.NOT_SPECIFIED,
            age_group=AgeGroup.ADULT,
            accessibility_needs=[AccessibilityNeed.VISUAL_IMPAIRMENT, AccessibilityNeed.HEARING_IMPAIRMENT],
        )

        test_point = RoutePoint(
            id="edge_test",
            address="Edge Location",
            latitude=48.85,
            longitude=2.30,
            location_name="Test Site",
        )

        queue = SmartAgentQueue(point_id=test_point.id)

        # Only video available (not ideal for either need)
        queue.submit_result(
            ContentType.VIDEO,
            ContentResult(
                content_type=ContentType.VIDEO,
                title="Only Available Content",
                description="Video without accessibility features",
                url="https://youtube.com/watch?v=only",
                source="YouTube",
                relevance_score=7.0,
                duration_seconds=180,
            ),
        )

        results, _ = queue.wait_for_results()
        judge = JudgeAgent()
        decision = judge.evaluate(test_point, results, profile)

        # System should still provide something (graceful degradation)
        # The decision reasoning should note accessibility limitations
        assert decision is not None
