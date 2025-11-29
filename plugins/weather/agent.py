"""
Weather Agent
=============

Agent that provides weather content for route points.
Demonstrates integration with the plugin architecture and enhanced base agent.
"""

from __future__ import annotations

import logging
from typing import Optional

from pydantic import BaseModel, Field

from src.agents.base_agent_v2 import (
    EnhancedBaseAgent,
    AgentMetadata,
    AgentCapability,
    AgentConfig,
)
from src.models import ContentResult, ContentType, RoutePoint
from src.core.plugins.registry import PluginRegistry

logger = logging.getLogger(__name__)


class WeatherAgentConfig(AgentConfig):
    """Configuration for Weather Agent."""
    
    # Weather-specific settings
    include_forecast: bool = True
    include_advice: bool = True
    temperature_unit: str = "celsius"
    
    # Content generation
    max_advice_length: int = 200


class WeatherAgent(EnhancedBaseAgent[WeatherAgentConfig]):
    """
    Weather content agent for the tour guide system.
    
    Provides weather information and travel advice for each route point.
    Uses the Weather Plugin for API integration.
    
    Features:
    - Current weather conditions
    - Weather forecast
    - LLM-powered travel advice
    - Content relevance scoring
    
    Example:
        agent = WeatherAgent()
        result = agent.execute(route_point)
        print(result.title)  # "Weather at Paris: 18°C, Partly Cloudy"
        print(result.description)  # Travel advice
    """
    
    metadata = AgentMetadata(
        name="weather",
        version="1.0.0",
        description="Provides weather information for route points",
        capabilities=[
            AgentCapability.CONTENT_PROVIDER,
            AgentCapability.REALTIME_DATA,
        ],
        content_type=ContentType.TEXT,
        priority=150,
        timeout=15.0,
        max_retries=2,
    )
    
    config_class = WeatherAgentConfig
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._weather_plugin = None
    
    def _get_weather_plugin(self):
        """Get the weather plugin instance."""
        if self._weather_plugin is None:
            try:
                self._weather_plugin = PluginRegistry.get_instance("weather")
                if not self._weather_plugin.is_running:
                    self._weather_plugin.configure({})
                    self._weather_plugin.start()
            except Exception as e:
                logger.warning(f"Weather plugin not available: {e}")
        return self._weather_plugin
    
    def _search_content(self, point: RoutePoint) -> Optional[ContentResult]:
        """
        Search for weather content for the route point.
        
        Args:
            point: Route point to get weather for
            
        Returns:
            ContentResult with weather information
        """
        location = point.location_name or point.address
        
        # Try to get weather from plugin
        plugin = self._get_weather_plugin()
        
        if plugin and plugin.is_running:
            try:
                weather = plugin.get_weather(
                    location,
                    include_forecast=self.config.include_forecast,
                )
                
                # Get travel advice
                advice = ""
                if self.config.include_advice:
                    advice = plugin.get_travel_advice(location, weather)
                
                return self._create_result(point, weather, advice)
                
            except Exception as e:
                logger.error(f"Failed to get weather from plugin: {e}")
        
        # Fallback: generate mock weather
        return self._create_mock_result(point)
    
    def _create_result(
        self,
        point: RoutePoint,
        weather: dict,
        advice: str,
    ) -> ContentResult:
        """Create content result from weather data."""
        temp = weather["temperature"]
        unit = weather.get("temperature_unit", "C")
        conditions = weather["conditions"]
        
        title = f"Weather at {point.location_name or point.address}: {temp}°{unit}, {conditions}"
        
        # Build description
        description_parts = [f"Current conditions: {conditions}"]
        description_parts.append(f"Temperature: {temp}°{unit}")
        
        if "humidity" in weather:
            description_parts.append(f"Humidity: {weather['humidity']}%")
        
        if "wind_speed" in weather:
            description_parts.append(f"Wind: {weather['wind_speed']} km/h")
        
        if advice:
            description_parts.append("")
            description_parts.append(f"💡 {advice}")
        
        # Add forecast summary if available
        if "forecast" in weather and weather["forecast"]:
            forecast = weather["forecast"]
            avg_temp = sum(f["temperature"] for f in forecast) / len(forecast)
            description_parts.append("")
            description_parts.append(
                f"📊 Next {len(forecast)} hours: Average {avg_temp:.1f}°{unit}"
            )
        
        description = "\n".join(description_parts)
        
        # Calculate relevance score
        # Weather is always relevant, but score based on data quality
        relevance_score = 7.0
        if advice:
            relevance_score += 1.0
        if "forecast" in weather:
            relevance_score += 1.0
        if weather.get("humidity") and weather.get("wind_speed"):
            relevance_score += 1.0
        
        return ContentResult(
            point_id=point.id,
            content_type=ContentType.TEXT,
            title=title,
            description=description,
            source="WeatherPlugin",
            relevance_score=min(relevance_score, 10.0),
            metadata={
                "temperature": temp,
                "temperature_unit": unit,
                "conditions": conditions,
                "humidity": weather.get("humidity"),
                "wind_speed": weather.get("wind_speed"),
                "has_forecast": "forecast" in weather,
                "has_advice": bool(advice),
            },
        )
    
    def _create_mock_result(self, point: RoutePoint) -> ContentResult:
        """Create a mock weather result when plugin is unavailable."""
        location = point.location_name or point.address
        
        return ContentResult(
            point_id=point.id,
            content_type=ContentType.TEXT,
            title=f"Weather information for {location}",
            description=(
                "Weather data currently unavailable. "
                "Check local weather services for current conditions."
            ),
            source="WeatherAgent (mock)",
            relevance_score=3.0,
            metadata={"mock": True},
        )
    
    def get_content_type(self) -> ContentType:
        """Return the content type this agent provides."""
        return ContentType.TEXT
    
    def on_before_execute(self, point: RoutePoint) -> None:
        """Called before execution."""
        logger.debug(f"Weather agent preparing for {point.address}")
    
    def on_after_execute(
        self,
        point: RoutePoint,
        result: Optional[ContentResult],
    ) -> None:
        """Called after execution."""
        if result:
            logger.debug(
                f"Weather agent completed for {point.address}: "
                f"{result.metadata.get('temperature')}°"
            )
    
    def on_error(self, point: RoutePoint, error: Exception) -> None:
        """Called on error."""
        logger.error(f"Weather agent error for {point.address}: {error}")

