"""
Unit tests for UserProfile model.
"""
import pytest
from src.models.user_profile import (
    UserProfile,
    AgeGroup,
    Gender,
    AccessibilityNeed,
    get_kid_profile,
    get_driver_profile,
    get_family_profile,
)


class TestUserProfile:
    """Tests for UserProfile model."""
    
    def test_default_profile(self):
        """Test default profile creation."""
        profile = UserProfile()
        assert profile.age_group == AgeGroup.NOT_SPECIFIED
        assert profile.gender == Gender.NOT_SPECIFIED
    
    def test_kid_profile_prefers_video(self, kid_profile):
        """Kids should prefer video over text."""
        weights = kid_profile.get_content_type_preferences()
        assert weights["video"] > weights["text"]
        assert weights["video"] == 1.3
        assert weights["text"] == 0.7
    
    def test_driver_profile_blocks_video(self, driver_profile):
        """Drivers should NOT get video content."""
        weights = driver_profile.get_content_type_preferences()
        assert weights["video"] == 0.0
        assert weights["music"] > 1.0
    
    def test_visual_impairment_prefers_audio(self):
        """Visual impairment should prefer audio content."""
        profile = UserProfile(
            accessibility_needs=[AccessibilityNeed.VISUAL_IMPAIRMENT]
        )
        weights = profile.get_content_type_preferences()
        assert weights["music"] > weights["video"]
        assert weights["video"] < 1.0
    
    def test_family_profile_is_family_friendly(self, family_profile):
        """Family profile should be family-friendly."""
        assert family_profile.content_rating == "family"
        assert "violence" in family_profile.exclude_topics
    
    def test_to_agent_context(self, kid_profile):
        """Test agent context generation."""
        context = kid_profile.to_agent_context()
        assert "child" in context.lower()
        assert "kid-friendly" in context.lower()
    
    def test_to_judge_criteria(self, driver_profile):
        """Test judge criteria generation."""
        criteria = driver_profile.to_judge_criteria()
        assert "DRIVING" in criteria.upper()
        assert "video" in criteria.lower() or "VIDEO" in criteria


class TestPresetProfiles:
    """Tests for preset profile functions."""
    
    def test_kid_profile(self):
        """Test kid profile preset."""
        profile = get_kid_profile(age=10)
        assert profile.age_group == AgeGroup.KID
        assert profile.exact_age == 10
    
    def test_driver_profile(self):
        """Test driver profile preset."""
        profile = get_driver_profile()
        assert profile.is_driver is True
    
    def test_family_profile(self):
        """Test family profile preset."""
        profile = get_family_profile(min_age=5)
        assert profile.min_age == 5

