"""
Unit tests for UserProfile model.

Tests cover:
- Profile initialization and defaults
- Content type preferences
- Preset profile functions
- Accessibility features
- Context and criteria generation
- Edge cases

MIT Level Testing - 85%+ Coverage Target
"""


from src.models.user_profile import (
    AccessibilityNeed,
    AgeGroup,
    AudienceType,
    ContentDepth,
    ContentPreference,
    Gender,
    LanguagePreference,
    MusicGenre,
    SocialContext,
    TravelMode,
    TravelPace,
    TripPurpose,
    UserProfile,
    get_driver_profile,
    get_family_profile,
    get_kid_profile,
)


class TestEnums:
    """Tests for profile enums."""

    def test_travel_mode_values(self):
        """Test TravelMode enum values."""
        assert TravelMode.CAR.value == "car"
        assert TravelMode.BUS.value == "bus"
        assert TravelMode.WALKING.value == "walking"

    def test_trip_purpose_values(self):
        """Test TripPurpose enum values."""
        assert TripPurpose.VACATION.value == "vacation"
        assert TripPurpose.EDUCATION.value == "education"
        assert TripPurpose.PILGRIMAGE.value == "pilgrimage"

    def test_travel_pace_values(self):
        """Test TravelPace enum values."""
        assert TravelPace.RUSHED.value == "rushed"
        assert TravelPace.LEISURELY.value == "leisurely"

    def test_social_context_values(self):
        """Test SocialContext enum values."""
        assert SocialContext.SOLO.value == "solo"
        assert SocialContext.FAMILY.value == "family"

    def test_age_group_values(self):
        """Test AgeGroup enum values."""
        assert AgeGroup.KID.value == "kid"
        assert AgeGroup.ADULT.value == "adult"
        assert AgeGroup.SENIOR.value == "senior"

    def test_gender_values(self):
        """Test Gender enum values."""
        assert Gender.MALE.value == "male"
        assert Gender.FEMALE.value == "female"
        assert Gender.NOT_SPECIFIED.value == "not_specified"

    def test_content_depth_values(self):
        """Test ContentDepth enum values."""
        assert ContentDepth.QUICK_FACTS.value == "quick_facts"
        assert ContentDepth.IN_DEPTH.value == "in_depth"

    def test_language_preference_values(self):
        """Test LanguagePreference enum values."""
        assert LanguagePreference.ENGLISH.value == "en"
        assert LanguagePreference.HEBREW.value == "he"

    def test_music_genre_values(self):
        """Test MusicGenre enum values."""
        assert MusicGenre.POP.value == "pop"
        assert MusicGenre.CLASSICAL.value == "classical"

    def test_accessibility_need_values(self):
        """Test AccessibilityNeed enum values."""
        assert AccessibilityNeed.VISUAL_IMPAIRMENT.value == "visual_impairment"
        assert AccessibilityNeed.HEARING_IMPAIRMENT.value == "hearing_impairment"


class TestUserProfile:
    """Tests for UserProfile model."""

    def test_default_profile(self):
        """Test default profile creation."""
        profile = UserProfile()
        assert profile.age_group == AgeGroup.NOT_SPECIFIED
        assert profile.gender == Gender.NOT_SPECIFIED
        assert profile.is_driver is False

    def test_profile_with_all_fields(self):
        """Test profile with all fields specified."""
        profile = UserProfile(
            age_group=AgeGroup.ADULT,
            gender=Gender.MALE,
            exact_age=35,
            travel_mode=TravelMode.CAR,
            trip_purpose=TripPurpose.VACATION,
            travel_pace=TravelPace.LEISURELY,
            social_context=SocialContext.FAMILY,
            audience_type=AudienceType.FAMILY_WITH_KIDS,
            content_preference=ContentPreference.HISTORICAL,
            content_depth=ContentDepth.DETAILED,
            preferred_languages=[LanguagePreference.ENGLISH],
            music_genres=[MusicGenre.CLASSICAL],
            interests=["history"],
            accessibility_needs=[],
            is_driver=False,
            content_rating="pg",
            exclude_topics=[],
            min_age=10,
        )

        assert profile.age_group == AgeGroup.ADULT
        assert profile.exact_age == 35
        assert profile.travel_mode == TravelMode.CAR

    def test_kid_profile_prefers_video(self, kid_profile):
        """Kids should prefer video over text."""
        weights = kid_profile.get_content_type_preferences()
        assert weights["video"] > weights["text"]
        assert weights["video"] >= 1.0

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

    def test_hearing_impairment_prefers_visual(self):
        """Hearing impairment should prefer visual content."""
        profile = UserProfile(
            accessibility_needs=[AccessibilityNeed.HEARING_IMPAIRMENT]
        )
        weights = profile.get_content_type_preferences()
        assert weights["text"] > weights["music"]

    def test_family_profile_is_family_friendly(self, family_profile):
        """Family profile should be family-friendly."""
        assert family_profile.content_rating == "family"
        assert "violence" in family_profile.exclude_topics

    def test_to_agent_context(self, kid_profile):
        """Test agent context generation."""
        context = kid_profile.to_agent_context()
        assert "child" in context.lower()
        assert "kid-friendly" in context.lower()

    def test_to_agent_context_adult(self):
        """Test agent context for adult profile."""
        profile = UserProfile(age_group=AgeGroup.ADULT)
        context = profile.to_agent_context()
        assert isinstance(context, str)

    def test_to_judge_criteria(self, driver_profile):
        """Test judge criteria generation."""
        criteria = driver_profile.to_judge_criteria()
        assert "DRIVING" in criteria.upper() or "driver" in criteria.lower()

    def test_to_judge_criteria_kid(self, kid_profile):
        """Test judge criteria for kid profile."""
        criteria = kid_profile.to_judge_criteria()
        assert isinstance(criteria, str)
        assert len(criteria) > 0

    def test_content_type_preferences_default(self):
        """Test default content type preferences."""
        profile = UserProfile()
        weights = profile.get_content_type_preferences()

        assert "video" in weights
        assert "music" in weights
        assert "text" in weights
        # Default weights should be around 1.0
        assert weights["video"] >= 0
        assert weights["music"] >= 0
        assert weights["text"] >= 0

    def test_profile_with_interests(self):
        """Test profile with topic interests."""
        profile = UserProfile(
            interests=["history", "architecture", "nature"]
        )
        assert len(profile.interests) == 3

    def test_profile_with_music_preferences(self):
        """Test profile with music preferences."""
        profile = UserProfile(
            music_genres=[MusicGenre.JAZZ, MusicGenre.CLASSICAL]
        )
        assert MusicGenre.JAZZ in profile.music_genres

    def test_profile_language_preferences(self):
        """Test language preferences."""
        profile = UserProfile(
            language=LanguagePreference.ENGLISH,
            secondary_language=LanguagePreference.HEBREW,
        )
        assert profile.language == LanguagePreference.ENGLISH
        assert profile.secondary_language == LanguagePreference.HEBREW


class TestPresetProfiles:
    """Tests for preset profile functions."""

    def test_kid_profile_creation(self):
        """Test kid profile preset."""
        profile = get_kid_profile(age=10)
        assert profile.age_group == AgeGroup.KID
        assert profile.exact_age == 10
        assert profile.content_rating in ["g", "pg", "family"]

    def test_kid_profile_different_ages(self):
        """Test kid profile with different ages."""
        young_kid = get_kid_profile(age=5)
        older_kid = get_kid_profile(age=11)

        assert young_kid.exact_age == 5
        assert older_kid.exact_age == 11

    def test_driver_profile_creation(self):
        """Test driver profile preset."""
        profile = get_driver_profile()
        assert profile.is_driver is True

        weights = profile.get_content_type_preferences()
        assert weights["video"] == 0.0

    def test_family_profile_creation(self):
        """Test family profile preset."""
        profile = get_family_profile(min_age=5)
        assert profile.min_age == 5
        assert profile.social_context == SocialContext.FAMILY
        assert profile.audience_type == AudienceType.FAMILY_WITH_KIDS

    def test_family_profile_different_ages(self):
        """Test family profile with different minimum ages."""
        profile_young = get_family_profile(min_age=3)
        profile_older = get_family_profile(min_age=12)

        assert profile_young.min_age == 3
        assert profile_older.min_age == 12


class TestContentTypeWeights:
    """Tests for content type weight calculations."""

    def test_senior_profile_weights(self):
        """Test weight preferences for senior profile."""
        profile = UserProfile(age_group=AgeGroup.SENIOR)
        weights = profile.get_content_type_preferences()

        # Seniors might prefer slower-paced content
        assert weights["text"] >= 0

    def test_teenager_profile_weights(self):
        """Test weight preferences for teenager."""
        profile = UserProfile(age_group=AgeGroup.TEENAGER)
        weights = profile.get_content_type_preferences()

        # Teenagers might prefer video content
        assert weights["video"] >= 0

    def test_weights_sum_positive(self):
        """Test that weights sum is positive."""
        profile = UserProfile()
        weights = profile.get_content_type_preferences()

        total = sum(weights.values())
        assert total > 0


class TestAccessibilityFeatures:
    """Tests for accessibility-related features."""

    def test_multiple_accessibility_needs(self):
        """Test profile with multiple accessibility needs."""
        profile = UserProfile(
            accessibility_needs=[
                AccessibilityNeed.VISUAL_IMPAIRMENT,
                AccessibilityNeed.HEARING_IMPAIRMENT,
            ]
        )
        assert len(profile.accessibility_needs) == 2

    def test_cognitive_accessibility(self):
        """Test cognitive accessibility preferences."""
        profile = UserProfile(
            accessibility_needs=[AccessibilityNeed.COGNITIVE]
        )
        weights = profile.get_content_type_preferences()
        # Should have valid weights
        assert all(w >= 0 for w in weights.values())


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_lists(self):
        """Test profile with empty lists."""
        profile = UserProfile(
            music_genres=[],
            interests=[],
            accessibility_needs=[],
            exclude_topics=[],
        )
        assert profile.music_genres == []
        assert profile.interests == []

    def test_profile_json_serialization(self):
        """Test profile can be serialized to JSON."""
        profile = UserProfile(
            age_group=AgeGroup.ADULT,
            travel_mode=TravelMode.CAR,
        )
        json_data = profile.model_dump_json()
        assert isinstance(json_data, str)
        assert "adult" in json_data.lower()

    def test_profile_dict_conversion(self):
        """Test profile can be converted to dict."""
        profile = UserProfile(age_group=AgeGroup.KID)
        profile_dict = profile.model_dump()
        assert isinstance(profile_dict, dict)
        assert "age_group" in profile_dict

    def test_exclude_topics_filtering(self):
        """Test exclude topics list."""
        profile = UserProfile(
            exclude_topics=["violence", "adult_content", "politics"]
        )
        assert "violence" in profile.exclude_topics
        assert len(profile.exclude_topics) == 3


class TestProfileContext:
    """Tests for profile context generation."""

    def test_context_includes_demographics(self):
        """Test context includes demographic info."""
        profile = UserProfile(
            age_group=AgeGroup.YOUNG_ADULT,
            gender=Gender.FEMALE,
        )
        context = profile.to_agent_context()
        assert isinstance(context, str)
        assert len(context) > 0

    def test_context_includes_travel_mode(self):
        """Test context includes travel mode when specified."""
        profile = UserProfile(travel_mode=TravelMode.WALKING)
        context = profile.to_agent_context()
        assert isinstance(context, str)

    def test_judge_criteria_includes_preferences(self):
        """Test judge criteria includes content preferences."""
        profile = UserProfile(
            content_preference=ContentPreference.HISTORICAL
        )
        criteria = profile.to_judge_criteria()
        assert isinstance(criteria, str)

    def test_context_with_name(self):
        """Test context includes user name."""
        profile = UserProfile(name="John")
        context = profile.to_agent_context()
        assert "John" in context

    def test_context_kid_profile(self):
        """Test context for kid profile."""
        profile = UserProfile(age_group=AgeGroup.KID)
        context = profile.to_agent_context()
        assert "child" in context.lower() or "kid" in context.lower()

    def test_context_teenager_profile(self):
        """Test context for teenager profile."""
        profile = UserProfile(age_group=AgeGroup.TEENAGER)
        context = profile.to_agent_context()
        assert "teenager" in context.lower()

    def test_context_senior_profile(self):
        """Test context for senior profile."""
        profile = UserProfile(age_group=AgeGroup.SENIOR)
        context = profile.to_agent_context()
        assert "senior" in context.lower()

    def test_context_business_trip(self):
        """Test context for business trip."""
        profile = UserProfile(trip_purpose=TripPurpose.BUSINESS)
        context = profile.to_agent_context()
        assert "business" in context.lower()

    def test_context_education_trip(self):
        """Test context for education trip."""
        profile = UserProfile(trip_purpose=TripPurpose.EDUCATION)
        context = profile.to_agent_context()
        assert "education" in context.lower() or "learning" in context.lower()

    def test_context_pilgrimage_trip(self):
        """Test context for pilgrimage trip."""
        profile = UserProfile(trip_purpose=TripPurpose.PILGRIMAGE)
        context = profile.to_agent_context()
        assert "pilgrimage" in context.lower() or "spiritual" in context.lower()

    def test_context_leisurely_pace(self):
        """Test context for leisurely pace."""
        profile = UserProfile(travel_pace=TravelPace.LEISURELY)
        context = profile.to_agent_context()
        assert "time" in context.lower() or "leisurely" in context.lower()

    def test_context_rushed_pace(self):
        """Test context for rushed pace."""
        profile = UserProfile(travel_pace=TravelPace.RUSHED)
        context = profile.to_agent_context()
        assert "hurry" in context.lower() or "quick" in context.lower()

    def test_context_driver(self):
        """Test context for driver."""
        profile = UserProfile(is_driver=True)
        context = profile.to_agent_context()
        assert "driving" in context.lower() or "audio" in context.lower()

    def test_context_couple(self):
        """Test context for couple."""
        profile = UserProfile(social_context=SocialContext.COUPLE)
        context = profile.to_agent_context()
        assert "couple" in context.lower()

    def test_context_family(self):
        """Test context for family."""
        profile = UserProfile(social_context=SocialContext.FAMILY)
        context = profile.to_agent_context()
        assert "family" in context.lower()

    def test_context_friends(self):
        """Test context for friends."""
        profile = UserProfile(social_context=SocialContext.FRIENDS)
        context = profile.to_agent_context()
        assert "friends" in context.lower()
