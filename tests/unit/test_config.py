"""
Unit tests for configuration settings.

Test Coverage:
- Settings initialization
- Environment variable loading
- Default values
- Agent skills configuration
"""

import os
from unittest.mock import patch

from src.utils.config import AGENT_SKILLS, Settings, settings


class TestSettings:
    """Tests for Settings configuration."""

    def test_default_settings(self):
        """Test default configuration values."""
        # Create settings without env file
        with patch.dict(os.environ, {}, clear=True):
            test_settings = Settings(_env_file=None)

        assert test_settings.default_country == "Israel"
        assert test_settings.travel_mode == "driving"
        assert test_settings.point_interval_seconds == 5.0
        assert test_settings.max_agents_per_point == 4
        assert test_settings.agent_timeout_seconds == 30.0
        assert test_settings.llm_provider == "anthropic"
        assert test_settings.llm_model == "claude-sonnet-4"
        assert test_settings.llm_temperature == 0.7
        assert test_settings.log_level == "INFO"
        assert test_settings.max_concurrent_threads == 12

    def test_api_keys_empty_default(self):
        """Test API keys default to empty."""
        with patch.dict(os.environ, {}, clear=True):
            test_settings = Settings(_env_file=None)

        assert test_settings.google_maps_api_key == ""
        assert test_settings.openai_api_key == ""
        assert test_settings.anthropic_api_key == ""
        assert test_settings.youtube_api_key == ""
        assert test_settings.spotify_client_id is None
        assert test_settings.spotify_client_secret is None

    def test_environment_variable_override(self):
        """Test environment variables override defaults."""
        env_vars = {
            "DEFAULT_COUNTRY": "USA",
            "TRAVEL_MODE": "walking",
            "POINT_INTERVAL_SECONDS": "10.0",
            "MAX_AGENTS_PER_POINT": "6",
            "AGENT_TIMEOUT_SECONDS": "60.0",
            "LLM_PROVIDER": "openai",
            "LLM_MODEL": "gpt-4",
            "LLM_TEMPERATURE": "0.5",
            "LOG_LEVEL": "DEBUG",
            "MAX_CONCURRENT_THREADS": "24",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            test_settings = Settings(_env_file=None)

        assert test_settings.default_country == "USA"
        assert test_settings.travel_mode == "walking"
        assert test_settings.point_interval_seconds == 10.0
        assert test_settings.max_agents_per_point == 6
        assert test_settings.agent_timeout_seconds == 60.0
        assert test_settings.llm_provider == "openai"
        assert test_settings.llm_model == "gpt-4"
        assert test_settings.llm_temperature == 0.5
        assert test_settings.log_level == "DEBUG"
        assert test_settings.max_concurrent_threads == 24

    def test_api_key_environment_variables(self):
        """Test API keys from environment."""
        env_vars = {
            "GOOGLE_MAPS_API_KEY": "test_maps_key",
            "OPENAI_API_KEY": "test_openai_key",
            "ANTHROPIC_API_KEY": "test_anthropic_key",
            "YOUTUBE_API_KEY": "test_youtube_key",
            "SPOTIFY_CLIENT_ID": "test_spotify_id",
            "SPOTIFY_CLIENT_SECRET": "test_spotify_secret",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            test_settings = Settings(_env_file=None)

        assert test_settings.google_maps_api_key == "test_maps_key"
        assert test_settings.openai_api_key == "test_openai_key"
        assert test_settings.anthropic_api_key == "test_anthropic_key"
        assert test_settings.youtube_api_key == "test_youtube_key"
        assert test_settings.spotify_client_id == "test_spotify_id"
        assert test_settings.spotify_client_secret == "test_spotify_secret"

    def test_queue_settings(self):
        """Test queue-related settings."""
        env_vars = {"QUEUE_SOFT_TIMEOUT": "20.0", "QUEUE_HARD_TIMEOUT": "45.0"}

        with patch.dict(os.environ, env_vars, clear=True):
            test_settings = Settings(_env_file=None)

        assert test_settings.queue_soft_timeout == 20.0
        assert test_settings.queue_hard_timeout == 45.0

    def test_language_setting(self):
        """Test language setting."""
        with patch.dict(os.environ, {"LANGUAGE": "en"}, clear=True):
            test_settings = Settings(_env_file=None)
        assert test_settings.language == "en"


class TestAgentSkills:
    """Tests for AGENT_SKILLS configuration."""

    def test_all_agents_defined(self):
        """Test all agent types have skill definitions."""
        expected_agents = ["video_agent", "music_agent", "text_agent", "judge_agent"]
        for agent in expected_agents:
            assert agent in AGENT_SKILLS
            assert "name" in AGENT_SKILLS[agent]
            assert "description" in AGENT_SKILLS[agent]
            assert "scoring_criteria" in AGENT_SKILLS[agent]

    def test_video_agent_skills(self):
        """Test video agent skill definition."""
        video = AGENT_SKILLS["video_agent"]
        assert video["name"] == "Video Content Specialist"
        assert "YouTube" in video["description"]
        assert isinstance(video["scoring_criteria"], list)
        assert len(video["scoring_criteria"]) > 0

    def test_music_agent_skills(self):
        """Test music agent skill definition."""
        music = AGENT_SKILLS["music_agent"]
        assert music["name"] == "Music Content Specialist"
        assert "songs" in music["description"].lower()
        assert isinstance(music["scoring_criteria"], list)

    def test_text_agent_skills(self):
        """Test text agent skill definition."""
        text = AGENT_SKILLS["text_agent"]
        assert text["name"] == "Historical/Facts Specialist"
        assert (
            "stories" in text["description"].lower()
            or "facts" in text["description"].lower()
        )
        assert isinstance(text["scoring_criteria"], list)

    def test_judge_agent_skills(self):
        """Test judge agent skill definition."""
        judge = AGENT_SKILLS["judge_agent"]
        assert judge["name"] == "Content Judge"
        assert (
            "evaluating" in judge["description"].lower()
            or "selecting" in judge["description"].lower()
        )
        assert isinstance(judge["scoring_criteria"], list)

    def test_scoring_criteria_not_empty(self):
        """Test all agents have non-empty scoring criteria."""
        for agent_name, skills in AGENT_SKILLS.items():
            assert len(skills["scoring_criteria"]) >= 3, (
                f"{agent_name} should have at least 3 criteria"
            )


class TestSingletonSettings:
    """Tests for singleton settings instance."""

    def test_settings_is_instantiated(self):
        """Test that settings singleton exists."""
        assert settings is not None
        assert isinstance(settings, Settings)

    def test_settings_has_required_attributes(self):
        """Test settings has all required attributes."""
        required_attrs = [
            "google_maps_api_key",
            "openai_api_key",
            "anthropic_api_key",
            "youtube_api_key",
            "default_country",
            "travel_mode",
            "language",
            "point_interval_seconds",
            "max_agents_per_point",
            "agent_timeout_seconds",
            "queue_soft_timeout",
            "queue_hard_timeout",
            "llm_provider",
            "llm_model",
            "llm_temperature",
            "log_level",
            "log_file",
            "max_concurrent_threads",
        ]

        for attr in required_attrs:
            assert hasattr(settings, attr), f"Settings missing attribute: {attr}"
