"""
User Profile - Configuration for personalizing the tour guide experience.

User Profile Features:
- User setup includes profile characteristics
- Example: "traveling with kids age 5"
- These preferences affect content selection by agents and judge

This is part of the "Setup" that goes into the User Input module.

Profile Categories:
1. DEMOGRAPHICS: age, gender, language
2. TRAVEL CONTEXT: mode, purpose, pace, group
3. CONTENT PREFERENCES: type, duration, depth
4. INTERESTS: hobbies, music genres, topics
5. ACCESSIBILITY: visual, hearing, mobility needs
6. EXPERIENCE: familiarity with area, travel experience
7. MOOD & ENERGY: current state, attention span
"""

from enum import Enum

from pydantic import BaseModel, Field

# =============================================================================
# ENUMS - All profile options
# =============================================================================


class TravelMode(str, Enum):
    """Mode of travel."""

    CAR = "car"
    BUS = "bus"
    TRAIN = "train"
    WALKING = "walking"
    BICYCLE = "bicycle"
    MOTORCYCLE = "motorcycle"


class TripPurpose(str, Enum):
    """Purpose of the trip."""

    VACATION = "vacation"
    BUSINESS = "business"
    EDUCATION = "education"  # School trip, learning
    PILGRIMAGE = "pilgrimage"  # Religious travel
    ADVENTURE = "adventure"
    ROMANTIC = "romantic"  # Honeymoon, anniversary
    REUNION = "reunion"  # Family gathering
    NO_SPECIFIC = "no_specific"


class TravelPace(str, Enum):
    """Pace of travel - affects content length."""

    RUSHED = "rushed"  # Quick facts only
    NORMAL = "normal"  # Standard content
    LEISURELY = "leisurely"  # Detailed, in-depth
    EXPLORATORY = "exploratory"  # Extra details, hidden gems


class SocialContext(str, Enum):
    """Who is traveling together."""

    SOLO = "solo"
    COUPLE = "couple"
    FAMILY = "family"
    FRIENDS = "friends"
    BUSINESS_GROUP = "business_group"
    TOUR_GROUP = "tour_group"
    SCHOOL_GROUP = "school_group"


class AudienceType(str, Enum):
    """Type of audience for content."""

    ADULTS_ONLY = "adults_only"
    FAMILY_WITH_KIDS = "family_with_kids"
    TEENAGERS = "teenagers"
    SENIORS = "seniors"
    MIXED = "mixed"


class ContentPreference(str, Enum):
    """Preferred type of content."""

    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    HISTORICAL = "historical"
    CULTURAL = "cultural"
    RELAXING = "relaxing"
    INSPIRATIONAL = "inspirational"
    HUMOROUS = "humorous"
    MIXED = "mixed"  # Variety of content types
    NO_PREFERENCE = "no_preference"


class ContentDepth(str, Enum):
    """How detailed should content be."""

    QUICK_FACTS = "quick_facts"  # 30 seconds
    SUMMARY = "summary"  # 1-2 minutes
    DETAILED = "detailed"  # 3-5 minutes
    IN_DEPTH = "in_depth"  # 5+ minutes


class LanguagePreference(str, Enum):
    """Preferred language for content."""

    HEBREW = "he"
    ENGLISH = "en"
    ARABIC = "ar"
    RUSSIAN = "ru"
    FRENCH = "fr"
    SPANISH = "es"
    GERMAN = "de"
    CHINESE = "zh"
    BOTH = "both"  # Hebrew + English


class Gender(str, Enum):
    """User gender for content personalization."""

    MALE = "male"
    FEMALE = "female"
    NOT_SPECIFIED = "not_specified"


class AgeGroup(str, Enum):
    """Age group of the user."""

    KID = "kid"  # 0-12
    TEENAGER = "teenager"  # 13-19
    YOUNG_ADULT = "young_adult"  # 20-35
    ADULT = "adult"  # 36-55
    SENIOR = "senior"  # 56+
    NOT_SPECIFIED = "not_specified"


class MusicGenre(str, Enum):
    """Preferred music genres."""

    POP = "pop"
    ROCK = "rock"
    CLASSICAL = "classical"
    JAZZ = "jazz"
    ELECTRONIC = "electronic"
    HIP_HOP = "hip_hop"
    FOLK = "folk"
    WORLD = "world"
    ISRAELI = "israeli"
    RELIGIOUS = "religious"
    AMBIENT = "ambient"
    NO_PREFERENCE = "no_preference"


class AccessibilityNeed(str, Enum):
    """Accessibility requirements."""

    NONE = "none"
    VISUAL_IMPAIRMENT = "visual_impairment"  # Prefer audio
    HEARING_IMPAIRMENT = "hearing_impairment"  # Prefer text/subtitles
    COGNITIVE = "cognitive"  # Simple, clear content
    MOTION_SENSITIVITY = "motion_sensitivity"  # Avoid shaky videos


class ExperienceLevel(str, Enum):
    """Travel/location experience level."""

    FIRST_TIME = "first_time"  # Never been here
    RETURNING = "returning"  # Been before
    LOCAL = "local"  # Lives nearby
    EXPERT = "expert"  # Knows area well


class EnergyLevel(str, Enum):
    """Current energy/attention level."""

    LOW = "low"  # Tired, prefer calming content
    MEDIUM = "medium"  # Normal
    HIGH = "high"  # Energetic, ready for action
    FOCUSED = "focused"  # Deep learning mode


class TimeOfDay(str, Enum):
    """Time of travel - affects content mood."""

    MORNING = "morning"  # Fresh, energetic
    AFTERNOON = "afternoon"  # Standard
    EVENING = "evening"  # Relaxed, romantic
    NIGHT = "night"  # Mysterious, nightlife


class UserProfile(BaseModel):
    """
    Comprehensive user profile for personalizing the tour guide.

    Categories:
    1. Demographics: age, gender, language
    2. Travel Context: mode, purpose, pace, group
    3. Content Preferences: type, duration, depth
    4. Interests: hobbies, music, topics
    5. Accessibility: special needs
    6. Experience: familiarity with area
    7. Current State: mood, energy, time
    """

    # =========================================================================
    # 1. BASIC INFO & DEMOGRAPHICS
    # =========================================================================
    name: str | None = Field(
        default=None, description="User's name for personalized greetings"
    )

    gender: Gender = Field(
        default=Gender.NOT_SPECIFIED,
        description="User gender for content personalization",
    )

    age_group: AgeGroup = Field(
        default=AgeGroup.NOT_SPECIFIED,
        description="Age group: kid, teenager, young_adult, adult, senior",
    )

    exact_age: int | None = Field(
        default=None,
        ge=0,
        le=120,
        description="Exact age if known (for precise content filtering)",
    )

    language: LanguagePreference = Field(
        default=LanguagePreference.BOTH, description="Preferred language for content"
    )

    secondary_language: LanguagePreference | None = Field(
        default=None, description="Secondary language acceptable"
    )

    # =========================================================================
    # 2. TRAVEL CONTEXT
    # =========================================================================
    travel_mode: TravelMode = Field(
        default=TravelMode.CAR, description="How they are traveling"
    )

    trip_purpose: TripPurpose = Field(
        default=TripPurpose.VACATION, description="Purpose of the trip"
    )

    travel_pace: TravelPace = Field(
        default=TravelPace.NORMAL, description="Pace of travel - affects content length"
    )

    social_context: SocialContext = Field(
        default=SocialContext.SOLO, description="Who is traveling together"
    )

    group_size: int | None = Field(
        default=None, ge=1, description="Number of people in the group"
    )

    # =========================================================================
    # 3. GROUP/AUDIENCE (when traveling with others)
    # =========================================================================
    audience_type: AudienceType = Field(
        default=AudienceType.MIXED, description="Who is traveling/listening"
    )

    min_age: int | None = Field(
        default=None, description="Minimum age in the group (for content filtering)"
    )

    max_age: int | None = Field(default=None, description="Maximum age in the group")

    # =========================================================================
    # 4. CONTENT PREFERENCES
    # =========================================================================
    content_preference: ContentPreference = Field(
        default=ContentPreference.NO_PREFERENCE, description="Preferred type of content"
    )

    content_depth: ContentDepth = Field(
        default=ContentDepth.SUMMARY, description="How detailed should content be"
    )

    content_rating: str = Field(
        default="family", description="Content rating: family, teen, adult"
    )

    max_content_duration_seconds: int | None = Field(
        default=None, description="Maximum duration for videos/songs"
    )

    prefer_local_content: bool = Field(
        default=True, description="Prefer content from local creators"
    )

    prefer_recent_content: bool = Field(
        default=False, description="Prefer recently published content"
    )

    # =========================================================================
    # 5. INTERESTS & HOBBIES
    # =========================================================================
    interests: list[str] = Field(
        default_factory=list,
        description="Specific interests (e.g., 'history', 'nature', 'food', 'architecture')",
    )

    music_genres: list[MusicGenre] = Field(
        default_factory=list, description="Preferred music genres"
    )

    favorite_artists: list[str] = Field(
        default_factory=list,
        description="Favorite musicians/bands for music suggestions",
    )

    hobbies: list[str] = Field(
        default_factory=list,
        description="User hobbies for content matching (e.g., 'photography', 'hiking')",
    )

    # =========================================================================
    # 6. EXCLUSIONS & SENSITIVITIES
    # =========================================================================
    exclude_topics: list[str] = Field(
        default_factory=list,
        description="Topics to avoid (e.g., 'violence', 'politics', 'religion')",
    )

    dietary_restrictions: list[str] = Field(
        default_factory=list,
        description="For food recommendations (e.g., 'kosher', 'vegan', 'halal')",
    )

    # =========================================================================
    # 7. ACCESSIBILITY NEEDS
    # =========================================================================
    accessibility_needs: list[AccessibilityNeed] = Field(
        default_factory=lambda: [AccessibilityNeed.NONE],
        description="Accessibility requirements",
    )

    requires_subtitles: bool = Field(
        default=False, description="Always include subtitles for videos"
    )

    prefer_audio_description: bool = Field(
        default=False, description="Prefer audio descriptions for visual content"
    )

    # =========================================================================
    # 8. EXPERIENCE & FAMILIARITY
    # =========================================================================
    experience_level: ExperienceLevel = Field(
        default=ExperienceLevel.FIRST_TIME, description="Familiarity with the area"
    )

    knowledge_level: str = Field(
        default="beginner",
        description="Knowledge level about local history: beginner, intermediate, expert",
    )

    visited_places: list[str] = Field(
        default_factory=list, description="Places already visited (to avoid repetition)"
    )

    # =========================================================================
    # 9. CURRENT STATE & CONTEXT
    # =========================================================================
    energy_level: EnergyLevel = Field(
        default=EnergyLevel.MEDIUM, description="Current energy/attention level"
    )

    time_of_day: TimeOfDay | None = Field(
        default=None, description="Time of travel for mood matching"
    )

    is_driver: bool = Field(
        default=False, description="Is user the driver (affects video recommendations)"
    )

    attention_span_minutes: int | None = Field(
        default=None, description="How long can user focus on content"
    )

    # =========================================================================
    # 10. PREFERENCES HISTORY (for ML/personalization)
    # =========================================================================
    previously_liked_content: list[str] = Field(
        default_factory=list, description="IDs of content user liked before"
    )

    previously_disliked_content: list[str] = Field(
        default_factory=list, description="IDs of content user disliked"
    )

    def to_agent_context(self) -> str:
        """
        Convert profile to context string for agents.
        This is injected into agent prompts.
        """
        parts = []

        # ─────────────────────────────────────────────────────────────────
        # DEMOGRAPHICS
        # ─────────────────────────────────────────────────────────────────
        if self.name:
            parts.append(f"The user's name is {self.name}.")

        if self.age_group == AgeGroup.KID:
            parts.append(
                "The user is a child. Content must be kid-friendly, educational, and engaging."
            )
        elif self.age_group == AgeGroup.TEENAGER:
            parts.append(
                "The user is a teenager. Content should be modern, relatable, and engaging."
            )
        elif self.age_group == AgeGroup.YOUNG_ADULT:
            parts.append(
                "The user is a young adult. Content can be more sophisticated and trendy."
            )
        elif self.age_group == AgeGroup.SENIOR:
            parts.append(
                "The user is a senior. Prefer clear, slower-paced, nostalgic content."
            )

        if self.gender == Gender.MALE:
            parts.append("The user is male.")
        elif self.gender == Gender.FEMALE:
            parts.append("The user is female.")

        # ─────────────────────────────────────────────────────────────────
        # TRAVEL CONTEXT
        # ─────────────────────────────────────────────────────────────────
        if self.trip_purpose == TripPurpose.BUSINESS:
            parts.append(
                "This is a business trip - professional, informative content preferred."
            )
        elif self.trip_purpose == TripPurpose.EDUCATION:
            parts.append(
                "This is an educational trip - learning-focused content required."
            )
        elif self.trip_purpose == TripPurpose.ROMANTIC:
            parts.append(
                "This is a romantic trip - focus on beautiful, romantic content."
            )
        elif self.trip_purpose == TripPurpose.PILGRIMAGE:
            parts.append(
                "This is a religious pilgrimage - spiritual content preferred."
            )

        if self.travel_pace == TravelPace.RUSHED:
            parts.append("User is in a hurry - quick, essential facts only.")
        elif self.travel_pace == TravelPace.LEISURELY:
            parts.append(
                "User has plenty of time - detailed, immersive content welcome."
            )
        elif self.travel_pace == TravelPace.EXPLORATORY:
            parts.append(
                "User wants to explore deeply - hidden gems and detailed stories welcome."
            )

        if self.is_driver:
            parts.append(
                "User is DRIVING - prefer audio content, NO videos requiring visual attention."
            )

        # ─────────────────────────────────────────────────────────────────
        # GROUP CONTEXT
        # ─────────────────────────────────────────────────────────────────
        if self.social_context == SocialContext.COUPLE:
            parts.append("Traveling as a couple.")
        elif self.social_context == SocialContext.FAMILY:
            parts.append("Traveling with family.")
        elif self.social_context == SocialContext.FRIENDS:
            parts.append("Traveling with friends - fun content appreciated.")

        if self.audience_type == AudienceType.FAMILY_WITH_KIDS:
            if self.min_age:
                parts.append(
                    f"The group includes children as young as {self.min_age} years old."
                )
            else:
                parts.append("The group includes children.")
            parts.append("Content should be family-friendly.")

        if self.audience_type == AudienceType.SENIORS:
            parts.append("The group includes seniors - clear, slower-paced content.")

        # ─────────────────────────────────────────────────────────────────
        # CONTENT PREFERENCES
        # ─────────────────────────────────────────────────────────────────
        if self.content_preference != ContentPreference.NO_PREFERENCE:
            parts.append(f"The user prefers {self.content_preference.value} content.")

        if self.content_depth == ContentDepth.QUICK_FACTS:
            parts.append("Keep content brief - 30 seconds max.")
        elif self.content_depth == ContentDepth.IN_DEPTH:
            parts.append("User wants in-depth content - 5+ minutes is fine.")

        # ─────────────────────────────────────────────────────────────────
        # LANGUAGE
        # ─────────────────────────────────────────────────────────────────
        if self.language == LanguagePreference.HEBREW:
            parts.append("Prefer Hebrew language content.")
        elif self.language == LanguagePreference.ENGLISH:
            parts.append("Prefer English language content.")
        elif self.language not in [LanguagePreference.BOTH]:
            parts.append(f"Prefer {self.language.value} language content.")

        # ─────────────────────────────────────────────────────────────────
        # INTERESTS
        # ─────────────────────────────────────────────────────────────────
        if self.interests:
            parts.append(f"User interests: {', '.join(self.interests)}.")

        if self.music_genres and MusicGenre.NO_PREFERENCE not in self.music_genres:
            genres = [g.value for g in self.music_genres]
            parts.append(f"Preferred music genres: {', '.join(genres)}.")

        if self.favorite_artists:
            parts.append(f"Favorite artists: {', '.join(self.favorite_artists[:3])}.")

        if self.hobbies:
            parts.append(f"Hobbies: {', '.join(self.hobbies)}.")

        # ─────────────────────────────────────────────────────────────────
        # EXCLUSIONS
        # ─────────────────────────────────────────────────────────────────
        if self.exclude_topics:
            parts.append(f"⚠️ AVOID these topics: {', '.join(self.exclude_topics)}.")

        # ─────────────────────────────────────────────────────────────────
        # ACCESSIBILITY
        # ─────────────────────────────────────────────────────────────────
        if AccessibilityNeed.VISUAL_IMPAIRMENT in self.accessibility_needs:
            parts.append("User has visual impairment - prefer AUDIO content.")
        if AccessibilityNeed.HEARING_IMPAIRMENT in self.accessibility_needs:
            parts.append(
                "User has hearing impairment - prefer TEXT content or videos with subtitles."
            )
        if AccessibilityNeed.COGNITIVE in self.accessibility_needs:
            parts.append("User needs simple, clear content - avoid complex language.")

        if self.requires_subtitles:
            parts.append("Videos MUST have subtitles.")

        # ─────────────────────────────────────────────────────────────────
        # EXPERIENCE LEVEL
        # ─────────────────────────────────────────────────────────────────
        if self.experience_level == ExperienceLevel.FIRST_TIME:
            parts.append("This is user's first visit - include basic background info.")
        elif self.experience_level == ExperienceLevel.LOCAL:
            parts.append(
                "User is a local - skip basic info, focus on lesser-known facts."
            )
        elif self.experience_level == ExperienceLevel.EXPERT:
            parts.append("User is an expert - provide advanced, detailed content.")

        # ─────────────────────────────────────────────────────────────────
        # CURRENT STATE
        # ─────────────────────────────────────────────────────────────────
        if self.energy_level == EnergyLevel.LOW:
            parts.append("User is tired - prefer calming, relaxing content.")
        elif self.energy_level == EnergyLevel.HIGH:
            parts.append("User is energetic - upbeat, engaging content welcome.")

        if self.time_of_day == TimeOfDay.MORNING:
            parts.append("It's morning - fresh, energetic content.")
        elif self.time_of_day == TimeOfDay.EVENING:
            parts.append("It's evening - relaxed, romantic content.")
        elif self.time_of_day == TimeOfDay.NIGHT:
            parts.append("It's nighttime - mysterious, nightlife-focused content.")

        # ─────────────────────────────────────────────────────────────────
        # DURATION
        # ─────────────────────────────────────────────────────────────────
        if self.max_content_duration_seconds:
            mins = self.max_content_duration_seconds // 60
            parts.append(f"Prefer content under {mins} minutes long.")

        return " ".join(parts) if parts else "No specific preferences."

    def to_judge_criteria(self) -> str:
        """
        Convert profile to criteria for the judge agent.
        Returns prioritized list of criteria for content selection.
        """
        criteria = []

        # ─────────────────────────────────────────────────────────────────
        # CRITICAL: Safety & Appropriateness
        # ─────────────────────────────────────────────────────────────────
        if self.age_group == AgeGroup.KID or (self.min_age and self.min_age < 13):
            criteria.append("🔴 CRITICAL: Content MUST be appropriate for children")

        if self.exclude_topics:
            criteria.append(
                f"🔴 CRITICAL: AVOID topics: {', '.join(self.exclude_topics)}"
            )

        # ─────────────────────────────────────────────────────────────────
        # Age Group Preferences
        # ─────────────────────────────────────────────────────────────────
        if self.age_group == AgeGroup.KID:
            criteria.append("Prefer fun, colorful, animated content")
            criteria.append("Educational value is highly valued")
            criteria.append("Short duration (under 3 minutes)")
        elif self.age_group == AgeGroup.TEENAGER:
            criteria.append("Content should be modern and relatable")
            criteria.append("Music and video are often preferred over text")
            criteria.append("Pop culture references are a plus")
        elif self.age_group == AgeGroup.YOUNG_ADULT:
            criteria.append("Modern, trendy content")
            criteria.append("Social media style content works well")
        elif self.age_group == AgeGroup.SENIOR:
            criteria.append("Prefer nostalgic or classical content")
            criteria.append("Clear audio and slower pacing")
            criteria.append("Historical content often appreciated")

        # ─────────────────────────────────────────────────────────────────
        # Trip Purpose
        # ─────────────────────────────────────────────────────────────────
        if self.trip_purpose == TripPurpose.EDUCATION:
            criteria.append("Educational value is the TOP priority")
            criteria.append("Factual accuracy required")
        elif self.trip_purpose == TripPurpose.ROMANTIC:
            criteria.append("Romantic, beautiful content preferred")
            criteria.append("Music may be ideal")
        elif self.trip_purpose == TripPurpose.BUSINESS:
            criteria.append("Professional, informative content")
            criteria.append("Quick facts preferred")
        elif self.trip_purpose == TripPurpose.PILGRIMAGE:
            criteria.append("Spiritual, religious content valued")
            criteria.append("Respectful tone required")

        # ─────────────────────────────────────────────────────────────────
        # Content Preferences
        # ─────────────────────────────────────────────────────────────────
        if self.content_preference == ContentPreference.EDUCATIONAL:
            criteria.append("Prioritize educational and informative content")
        elif self.content_preference == ContentPreference.ENTERTAINMENT:
            criteria.append("Prioritize entertaining and engaging content")
        elif self.content_preference == ContentPreference.HISTORICAL:
            criteria.append("Prioritize historical accuracy and depth")
        elif self.content_preference == ContentPreference.HUMOROUS:
            criteria.append("Fun, light-hearted content preferred")

        # ─────────────────────────────────────────────────────────────────
        # Travel Mode & Driver Status
        # ─────────────────────────────────────────────────────────────────
        if self.is_driver:
            criteria.append(
                "🚗 USER IS DRIVING: Audio-only content required (NO video)"
            )
            criteria.append("Music or text (read aloud) preferred")
        elif self.travel_mode == TravelMode.CAR:
            criteria.append("Audio-focused content works well (car)")
        elif self.travel_mode == TravelMode.WALKING:
            criteria.append("Brief, digestible content (walking)")

        # ─────────────────────────────────────────────────────────────────
        # Pace & Depth
        # ─────────────────────────────────────────────────────────────────
        if self.travel_pace == TravelPace.RUSHED:
            criteria.append("⚡ QUICK: 30-second facts only")
        elif self.content_depth == ContentDepth.QUICK_FACTS:
            criteria.append("Brief content (30 seconds max)")
        elif self.content_depth == ContentDepth.IN_DEPTH:
            criteria.append("Detailed, comprehensive content welcome")

        # ─────────────────────────────────────────────────────────────────
        # Accessibility
        # ─────────────────────────────────────────────────────────────────
        if AccessibilityNeed.VISUAL_IMPAIRMENT in self.accessibility_needs:
            criteria.append("♿ Visual impairment: AUDIO content required")
        if AccessibilityNeed.HEARING_IMPAIRMENT in self.accessibility_needs:
            criteria.append("♿ Hearing impairment: TEXT content preferred")
        if AccessibilityNeed.COGNITIVE in self.accessibility_needs:
            criteria.append("♿ Simple, clear language required")

        # ─────────────────────────────────────────────────────────────────
        # Music Preferences
        # ─────────────────────────────────────────────────────────────────
        if self.music_genres and MusicGenre.NO_PREFERENCE not in self.music_genres:
            genres = [g.value for g in self.music_genres[:3]]
            criteria.append(f"Music preference: {', '.join(genres)}")

        # ─────────────────────────────────────────────────────────────────
        # Energy & Time
        # ─────────────────────────────────────────────────────────────────
        if self.energy_level == EnergyLevel.LOW:
            criteria.append("User tired: calming, relaxing content")
        elif self.energy_level == EnergyLevel.HIGH:
            criteria.append("User energetic: upbeat content")

        if self.time_of_day == TimeOfDay.EVENING:
            criteria.append("Evening: relaxed mood content")
        elif self.time_of_day == TimeOfDay.NIGHT:
            criteria.append("Night: mysterious/nightlife content")

        # ─────────────────────────────────────────────────────────────────
        # Experience Level
        # ─────────────────────────────────────────────────────────────────
        if self.experience_level == ExperienceLevel.FIRST_TIME:
            criteria.append("First visit: include background/basics")
        elif self.experience_level == ExperienceLevel.EXPERT:
            criteria.append("Expert: advanced, detailed content")

        # ─────────────────────────────────────────────────────────────────
        # Group Context
        # ─────────────────────────────────────────────────────────────────
        if self.audience_type == AudienceType.FAMILY_WITH_KIDS:
            criteria.append("Family-friendly content required")
            if self.min_age and self.min_age < 10:
                criteria.append("Young kids: short, engaging content")

        return (
            "\n".join(f"- {c}" for c in criteria)
            if criteria
            else "- No specific criteria"
        )

    def get_content_type_preferences(self) -> dict[str, float]:
        """
        Get content type preference weights based on user profile.
        Returns multipliers for VIDEO, MUSIC, TEXT scoring.

        Higher = more preferred (1.0 = neutral, >1.0 = boost, <1.0 = penalty)
        0.0 = strictly prohibited (e.g., video for drivers)
        """
        weights = {"video": 1.0, "music": 1.0, "text": 1.0}

        # ─────────────────────────────────────────────────────────────────
        # Age-based preferences
        # ─────────────────────────────────────────────────────────────────
        if self.age_group == AgeGroup.KID:
            weights["video"] = 1.3  # Kids love videos
            weights["music"] = 1.2  # Fun songs
            weights["text"] = 0.7  # Less likely to engage with text
        elif self.age_group == AgeGroup.TEENAGER:
            weights["music"] = 1.4  # Teens love music
            weights["video"] = 1.2  # YouTube generation
            weights["text"] = 0.6  # Less text
        elif self.age_group == AgeGroup.YOUNG_ADULT:
            weights["video"] = 1.3  # Social media generation
            weights["music"] = 1.2
            weights["text"] = 0.8
        elif self.age_group == AgeGroup.SENIOR:
            weights["text"] = 1.3  # May prefer reading/listening
            weights["music"] = 1.2  # Classic music appreciation
            weights["video"] = 0.9  # Fine but not priority

        # ─────────────────────────────────────────────────────────────────
        # Content preference adjustments
        # ─────────────────────────────────────────────────────────────────
        if self.content_preference == ContentPreference.EDUCATIONAL:
            weights["text"] += 0.2
            weights["video"] += 0.15  # Educational videos
        elif self.content_preference == ContentPreference.ENTERTAINMENT:
            weights["video"] += 0.2
            weights["music"] += 0.2
        elif self.content_preference == ContentPreference.HISTORICAL:
            weights["text"] += 0.3  # Historical articles
        elif self.content_preference == ContentPreference.RELAXING:
            weights["music"] += 0.3  # Relaxing music

        # ─────────────────────────────────────────────────────────────────
        # Trip purpose
        # ─────────────────────────────────────────────────────────────────
        if self.trip_purpose == TripPurpose.ROMANTIC:
            weights["music"] += 0.3  # Romantic music
        elif self.trip_purpose == TripPurpose.EDUCATION:
            weights["text"] += 0.2
            weights["video"] += 0.1

        # ─────────────────────────────────────────────────────────────────
        # Travel mode
        # ─────────────────────────────────────────────────────────────────
        if self.travel_mode == TravelMode.WALKING:
            weights["text"] += 0.1  # Can read while walking
            weights["music"] += 0.1  # Audio while walking

        # ─────────────────────────────────────────────────────────────────
        # Energy level
        # ─────────────────────────────────────────────────────────────────
        if self.energy_level == EnergyLevel.LOW:
            weights["music"] += 0.2  # Relaxing music when tired
        elif self.energy_level == EnergyLevel.HIGH:
            weights["video"] += 0.1  # Engaging content when energetic

        # ═════════════════════════════════════════════════════════════════
        # CRITICAL SAFETY CONSTRAINTS (applied LAST to override all others)
        # ═════════════════════════════════════════════════════════════════

        # Driver: NO VIDEO allowed - SAFETY CRITICAL
        if self.is_driver:
            weights["video"] = 0.0  # Cannot watch video while driving!
            weights["music"] = max(weights["music"], 1.5)  # Boost music for driving
            weights["text"] = max(weights["text"], 1.2)  # Can be read aloud

        # Accessibility needs - applied after all other adjustments
        if AccessibilityNeed.VISUAL_IMPAIRMENT in self.accessibility_needs:
            weights["video"] = 0.0  # Can't see well - exclude video
            weights["music"] = max(weights["music"], 1.5)  # Audio is great
            weights["text"] = max(weights["text"], 1.3)  # Can be read aloud

        if AccessibilityNeed.HEARING_IMPAIRMENT in self.accessibility_needs:
            weights["music"] = 0.0  # Can't hear well - exclude music
            weights["text"] = max(weights["text"], 1.5)  # Reading is preferred
            # Video with subtitles is okay

        return weights

    def get_music_search_context(self) -> str:
        """Get context string for music agent searches."""
        parts = []

        if self.music_genres and MusicGenre.NO_PREFERENCE not in self.music_genres:
            genres = [g.value for g in self.music_genres]
            parts.append(f"Preferred genres: {', '.join(genres)}")

        if self.favorite_artists:
            parts.append(f"Similar to artists: {', '.join(self.favorite_artists[:5])}")

        if self.age_group == AgeGroup.KID:
            parts.append("Kid-friendly, fun songs")
        elif self.age_group == AgeGroup.TEENAGER:
            parts.append("Modern, trending songs")
        elif self.age_group == AgeGroup.SENIOR:
            parts.append("Classic, nostalgic songs")

        if self.trip_purpose == TripPurpose.ROMANTIC:
            parts.append("Romantic, love songs")

        if self.energy_level == EnergyLevel.LOW:
            parts.append("Calming, relaxing music")
        elif self.energy_level == EnergyLevel.HIGH:
            parts.append("Upbeat, energetic music")

        return " | ".join(parts) if parts else "No specific music preferences"

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Family Trip",
                "audience_type": "family_with_kids",
                "min_age": 5,
                "content_preference": "educational",
                "language": "both",
                "travel_mode": "car",
                "content_rating": "family",
                "interests": ["history", "nature"],
                "exclude_topics": ["violence"],
                "max_content_duration_seconds": 600,
            }
        }


class TourSetup(BaseModel):
    """
    Complete setup for a tour guide session.

    Includes:
    - Route information (source, destination)
    - User profile
    - System settings
    """

    # Route
    source: str = Field(..., description="Starting point")
    destination: str = Field(..., description="End point")
    waypoints: list[str] = Field(
        default_factory=list, description="Optional waypoints to include"
    )

    # User
    user_profile: UserProfile = Field(
        default_factory=UserProfile, description="User preferences and profile"
    )

    # Settings
    point_interval_seconds: float = Field(
        default=5.0, description="Time between route points"
    )
    country: str = Field(default="Israel", description="Country for the route")

    @classmethod
    def from_interactive(cls) -> "TourSetup":
        """Create setup from interactive user input."""
        print("\n" + "=" * 50)
        print("🗺️  TOUR GUIDE SETUP")
        print("=" * 50)

        # Route
        source = input("\n📍 Starting point: ").strip() or "Tel Aviv, Israel"
        destination = input("🎯 Destination: ").strip() or "Jerusalem, Israel"

        # Profile
        print("\n👤 User Profile (press Enter for defaults):")

        audience_input = input(
            "   Audience (1=Adults, 2=Family with kids, 3=Teens): "
        ).strip()
        audience_map = {
            "1": AudienceType.ADULTS_ONLY,
            "2": AudienceType.FAMILY_WITH_KIDS,
            "3": AudienceType.TEENAGERS,
        }
        audience = audience_map.get(audience_input, AudienceType.MIXED)

        min_age = None
        if audience == AudienceType.FAMILY_WITH_KIDS:
            age_input = input("   Youngest child's age: ").strip()
            min_age = int(age_input) if age_input.isdigit() else None

        pref_input = input(
            "   Content preference (1=Educational, 2=Entertainment, 3=Historical): "
        ).strip()
        pref_map = {
            "1": ContentPreference.EDUCATIONAL,
            "2": ContentPreference.ENTERTAINMENT,
            "3": ContentPreference.HISTORICAL,
        }
        preference = pref_map.get(pref_input, ContentPreference.NO_PREFERENCE)

        interests_input = input(
            "   Interests (comma-separated, e.g., 'history,nature'): "
        ).strip()
        interests = (
            [i.strip() for i in interests_input.split(",")] if interests_input else []
        )

        profile = UserProfile(
            audience_type=audience,
            min_age=min_age,
            content_preference=preference,
            interests=interests,
        )

        print("\n✅ Setup complete!")
        print(f"   Route: {source} → {destination}")
        print(f"   Profile: {profile.audience_type.value}")
        if profile.interests:
            print(f"   Interests: {', '.join(profile.interests)}")

        return cls(source=source, destination=destination, user_profile=profile)


# =============================================================================
# PRESET PROFILES - Common user types
# =============================================================================


def get_default_profile() -> UserProfile:
    """Get a default user profile."""
    return UserProfile()


def get_kid_profile(age: int = 8, gender: Gender = Gender.NOT_SPECIFIED) -> UserProfile:
    """Profile for a child."""
    return UserProfile(
        name="Young Explorer",
        age_group=AgeGroup.KID,
        exact_age=age,
        gender=gender,
        content_preference=ContentPreference.EDUCATIONAL,
        content_rating="family",
        content_depth=ContentDepth.QUICK_FACTS,
        max_content_duration_seconds=180,  # 3 minutes max
        exclude_topics=["violence", "adult content", "scary"],
        energy_level=EnergyLevel.HIGH,
    )


def get_teenager_profile(
    age: int = 15, gender: Gender = Gender.NOT_SPECIFIED
) -> UserProfile:
    """Profile for a teenager."""
    return UserProfile(
        name="Teen Traveler",
        age_group=AgeGroup.TEENAGER,
        exact_age=age,
        gender=gender,
        content_preference=ContentPreference.ENTERTAINMENT,
        music_genres=[MusicGenre.POP, MusicGenre.HIP_HOP],
        content_depth=ContentDepth.SUMMARY,
        max_content_duration_seconds=300,  # 5 minutes max
        energy_level=EnergyLevel.HIGH,
    )


def get_adult_profile(gender: Gender = Gender.NOT_SPECIFIED) -> UserProfile:
    """Profile for a general adult."""
    return UserProfile(
        age_group=AgeGroup.ADULT,
        gender=gender,
        content_preference=ContentPreference.NO_PREFERENCE,
        content_depth=ContentDepth.SUMMARY,
        experience_level=ExperienceLevel.FIRST_TIME,
    )


def get_senior_profile(gender: Gender = Gender.NOT_SPECIFIED) -> UserProfile:
    """Profile for a senior."""
    return UserProfile(
        name="Experienced Traveler",
        age_group=AgeGroup.SENIOR,
        gender=gender,
        content_preference=ContentPreference.HISTORICAL,
        music_genres=[MusicGenre.CLASSICAL, MusicGenre.JAZZ, MusicGenre.FOLK],
        content_depth=ContentDepth.DETAILED,
        travel_pace=TravelPace.LEISURELY,
        energy_level=EnergyLevel.MEDIUM,
    )


def get_family_profile(min_age: int = 5) -> UserProfile:
    """Profile for family with kids."""
    return UserProfile(
        name="Family Trip",
        audience_type=AudienceType.FAMILY_WITH_KIDS,
        social_context=SocialContext.FAMILY,
        min_age=min_age,
        content_preference=ContentPreference.EDUCATIONAL,
        content_rating="family",
        content_depth=ContentDepth.SUMMARY,
        max_content_duration_seconds=300,  # 5 minutes max
        exclude_topics=["violence", "adult content"],
    )


def get_couple_profile(trip_type: TripPurpose = TripPurpose.ROMANTIC) -> UserProfile:
    """Profile for a traveling couple."""
    return UserProfile(
        name="Couple's Journey",
        social_context=SocialContext.COUPLE,
        trip_purpose=trip_type,
        content_preference=ContentPreference.CULTURAL,
        music_genres=[MusicGenre.JAZZ, MusicGenre.AMBIENT],
        travel_pace=TravelPace.LEISURELY,
        time_of_day=TimeOfDay.EVENING,
    )


def get_history_buff_profile() -> UserProfile:
    """Profile for history enthusiasts."""
    return UserProfile(
        name="History Explorer",
        audience_type=AudienceType.ADULTS_ONLY,
        content_preference=ContentPreference.HISTORICAL,
        content_depth=ContentDepth.IN_DEPTH,
        interests=["history", "archaeology", "culture", "architecture"],
        knowledge_level="intermediate",
        travel_pace=TravelPace.EXPLORATORY,
        language=LanguagePreference.BOTH,
    )


def get_driver_profile() -> UserProfile:
    """Profile for someone who is driving - NO VIDEO!"""
    return UserProfile(
        name="Road Tripper",
        is_driver=True,
        travel_mode=TravelMode.CAR,
        content_depth=ContentDepth.SUMMARY,
        # Important: video will be penalized to 0 for drivers
    )


def get_business_traveler_profile() -> UserProfile:
    """Profile for business traveler."""
    return UserProfile(
        name="Business Traveler",
        age_group=AgeGroup.ADULT,
        trip_purpose=TripPurpose.BUSINESS,
        travel_pace=TravelPace.RUSHED,
        content_depth=ContentDepth.QUICK_FACTS,
        social_context=SocialContext.SOLO,
        max_content_duration_seconds=60,  # 1 minute max
    )


def get_accessibility_visual_profile() -> UserProfile:
    """Profile for visually impaired user."""
    return UserProfile(
        name="Audio Explorer",
        accessibility_needs=[AccessibilityNeed.VISUAL_IMPAIRMENT],
        prefer_audio_description=True,
        content_depth=ContentDepth.DETAILED,
    )


def get_accessibility_hearing_profile() -> UserProfile:
    """Profile for hearing impaired user."""
    return UserProfile(
        name="Visual Explorer",
        accessibility_needs=[AccessibilityNeed.HEARING_IMPAIRMENT],
        requires_subtitles=True,
        content_depth=ContentDepth.DETAILED,
    )


def get_local_expert_profile() -> UserProfile:
    """Profile for someone who knows the area well."""
    return UserProfile(
        name="Local Expert",
        experience_level=ExperienceLevel.LOCAL,
        knowledge_level="expert",
        content_depth=ContentDepth.IN_DEPTH,
        prefer_local_content=True,
        travel_pace=TravelPace.EXPLORATORY,
        interests=["hidden gems", "local secrets", "off the beaten path"],
    )


# =============================================================================
# PROFILE BUILDER - Interactive creation
# =============================================================================


class ProfileBuilder:
    """
    Helper class to build a user profile step by step.
    Use for interactive profile creation.
    """

    def __init__(self):
        self._profile = UserProfile()

    def set_demographics(
        self,
        age_group: AgeGroup | None = None,
        gender: Gender | None = None,
        language: LanguagePreference | None = None,
    ) -> "ProfileBuilder":
        if age_group:
            self._profile.age_group = age_group
        if gender:
            self._profile.gender = gender
        if language:
            self._profile.language = language
        return self

    def set_travel_context(
        self,
        mode: TravelMode | None = None,
        purpose: TripPurpose | None = None,
        pace: TravelPace | None = None,
        is_driver: bool | None = None,
    ) -> "ProfileBuilder":
        if mode:
            self._profile.travel_mode = mode
        if purpose:
            self._profile.trip_purpose = purpose
        if pace:
            self._profile.travel_pace = pace
        if is_driver is not None:
            self._profile.is_driver = is_driver
        return self

    def set_preferences(
        self,
        content_type: ContentPreference | None = None,
        depth: ContentDepth | None = None,
        interests: list[str] | None = None,
        music_genres: list[MusicGenre] | None = None,
    ) -> "ProfileBuilder":
        if content_type:
            self._profile.content_preference = content_type
        if depth:
            self._profile.content_depth = depth
        if interests:
            self._profile.interests = interests
        if music_genres:
            self._profile.music_genres = music_genres
        return self

    def set_accessibility(
        self,
        needs: list[AccessibilityNeed] | None = None,
        subtitles: bool | None = None,
    ) -> "ProfileBuilder":
        if needs:
            self._profile.accessibility_needs = needs
        if subtitles is not None:
            self._profile.requires_subtitles = subtitles
        return self

    def set_exclusions(self, topics: list[str] | None = None) -> "ProfileBuilder":
        if topics:
            self._profile.exclude_topics = topics
        return self

    def build(self) -> "UserProfile":
        profile: UserProfile = self._profile
        return profile
