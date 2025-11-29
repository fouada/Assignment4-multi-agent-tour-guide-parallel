"""
Configuration settings for the Multi-Agent Tour Guide system.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    google_maps_api_key: str = Field(default="", env="GOOGLE_MAPS_API_KEY")
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", env="ANTHROPIC_API_KEY")
    youtube_api_key: str = Field(default="", env="YOUTUBE_API_KEY")
    spotify_client_id: Optional[str] = Field(default=None, env="SPOTIFY_CLIENT_ID")
    spotify_client_secret: Optional[str] = Field(default=None, env="SPOTIFY_CLIENT_SECRET")
    
    # Route Settings
    default_country: str = Field(default="Israel", env="DEFAULT_COUNTRY")
    travel_mode: str = Field(default="driving", env="TRAVEL_MODE")  # driving, walking, bicycling, transit
    language: str = Field(default="he", env="LANGUAGE")  # Hebrew
    
    # Timer Settings
    point_interval_seconds: float = Field(default=5.0, env="POINT_INTERVAL_SECONDS")
    
    # Agent Settings
    max_agents_per_point: int = Field(default=4, env="MAX_AGENTS_PER_POINT")  # 3 content + 1 judge
    agent_timeout_seconds: float = Field(default=30.0, env="AGENT_TIMEOUT_SECONDS")
    
    # LLM Settings
    llm_provider: str = Field(default="openai", env="LLM_PROVIDER")  # openai, anthropic
    llm_model: str = Field(default="gpt-4o-mini", env="LLM_MODEL")
    llm_temperature: float = Field(default=0.7, env="LLM_TEMPERATURE")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="tour_guide.log", env="LOG_FILE")
    
    # Threading
    max_concurrent_threads: int = Field(default=12, env="MAX_CONCURRENT_THREADS")
    use_multiprocessing: bool = Field(default=False, env="USE_MULTIPROCESSING")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Singleton settings instance
settings = Settings()


# Agent skill definitions
AGENT_SKILLS = {
    "video_agent": {
        "name": "Video Content Specialist",
        "description": "Expert at finding relevant YouTube videos for locations",
        "scoring_criteria": [
            "Relevance to the specific location",
            "Educational or entertainment value",
            "Video quality and production",
            "View count and engagement",
            "Duration appropriateness for travel"
        ]
    },
    "music_agent": {
        "name": "Music Content Specialist", 
        "description": "Expert at finding songs related to locations",
        "scoring_criteria": [
            "Lyrical connection to the location",
            "Historical or cultural significance",
            "Musical quality",
            "Mood appropriateness for travel",
            "Artist connection to the area"
        ]
    },
    "text_agent": {
        "name": "Historical/Facts Specialist",
        "description": "Expert at finding interesting stories and facts about locations",
        "scoring_criteria": [
            "Historical accuracy",
            "Interesting or surprising facts",
            "Relevance to the location",
            "Educational value",
            "Engagement potential for travelers"
        ]
    },
    "judge_agent": {
        "name": "Content Judge",
        "description": "Expert at evaluating and selecting the best content for each location",
        "scoring_criteria": [
            "Overall relevance to specific location",
            "Engagement potential",
            "Uniqueness and memorability",
            "Appropriateness for the audience",
            "Travel experience enhancement"
        ]
    }
}

