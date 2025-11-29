"""
Weather Plugin Implementation
=============================

Complete plugin demonstrating production-grade architecture.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from src.core.plugins.base import BasePlugin, PluginMetadata, PluginCapability
from src.core.plugins.registry import PluginRegistry
from src.core.plugins.events import EventBus, Event, publish
from src.core.observability import Counter, health_check

logger = logging.getLogger(__name__)


# ============== Configuration ==============

class WeatherConfig(BaseModel):
    """Configuration for Weather Plugin."""
    
    # API settings
    api_provider: str = Field(
        default="mock",
        description="Weather API provider",
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for weather service",
    )
    api_base_url: Optional[str] = None
    
    # Cache settings
    cache_ttl_seconds: int = Field(
        default=1800,
        description="Cache TTL in seconds",
    )
    
    # Display settings
    temperature_unit: str = Field(
        default="celsius",
        description="Temperature unit",
    )
    
    # Features
    include_forecast: bool = True
    forecast_hours: int = 12
    generate_advice: bool = True
    
    # LLM settings
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.7


# ============== Events ==============

class WeatherDataFetched(Event):
    """Emitted when weather data is fetched."""
    location: str
    temperature: float
    conditions: str
    cached: bool = False


class WeatherAdviceGenerated(Event):
    """Emitted when weather advice is generated."""
    location: str
    advice: str


# ============== Plugin Metrics ==============

weather_requests = Counter(
    "weather_requests_total",
    "Total weather API requests",
    labels=["provider", "status"],
)


# ============== Plugin Implementation ==============

@PluginRegistry.register("weather")
class WeatherPlugin(BasePlugin[WeatherConfig]):
    """
    Weather Plugin - Provides weather information for route points.
    
    Features:
    - Real-time weather data from multiple providers
    - Weather forecasts
    - LLM-powered travel advice
    - Caching for performance
    - Health monitoring
    
    Usage:
        plugin = WeatherPlugin()
        plugin.configure({"api_provider": "openweathermap", "api_key": "..."})
        plugin.start()
        
        weather = plugin.get_weather("Paris, France")
        print(weather["temperature"], weather["conditions"])
    """
    
    # Plugin metadata
    metadata = PluginMetadata(
        name="weather",
        version="1.0.0",
        description="Weather information for tour guide routes",
        author="Tour Guide Team",
        category="enrichment",
        capabilities=[
            PluginCapability.CONTENT_PROVIDER,
            PluginCapability.ENRICHMENT,
        ],
        priority=150,
    )
    
    config_class = WeatherConfig
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # API client (initialized on start)
        self._api_client: Optional[WeatherAPIClient] = None
        
        # Cache
        self._cache: Dict[str, Dict[str, Any]] = {}
        
        # LLM client
        self._llm_client = None
    
    # ==================== Lifecycle ====================
    
    def _on_start(self) -> None:
        """Initialize resources when plugin starts."""
        logger.info(f"Starting Weather Plugin v{self.version}")
        
        # Initialize API client based on provider
        provider = self.config.api_provider
        if provider == "openweathermap":
            self._api_client = OpenWeatherMapClient(
                api_key=self.config.api_key,
                base_url=self.config.api_base_url,
            )
        elif provider == "weatherapi":
            self._api_client = WeatherAPIClient(
                api_key=self.config.api_key,
            )
        else:
            self._api_client = MockWeatherClient()
        
        # Initialize LLM if advice generation is enabled
        if self.config.generate_advice:
            self._init_llm_client()
        
        logger.info(f"Weather Plugin started with provider: {provider}")
    
    def _on_stop(self) -> None:
        """Clean up resources when plugin stops."""
        logger.info("Stopping Weather Plugin")
        
        # Clear cache
        self._cache.clear()
        
        # Close API client
        if self._api_client and hasattr(self._api_client, "close"):
            self._api_client.close()
    
    def _check_health(self) -> bool:
        """Check if plugin is healthy."""
        if not self._api_client:
            return False
        
        try:
            # Try a simple API call
            return self._api_client.is_available()
        except Exception:
            return False
    
    # ==================== API Methods ====================
    
    def get_weather(
        self,
        location: str,
        include_forecast: bool = None,
    ) -> Dict[str, Any]:
        """
        Get current weather for a location.
        
        Args:
            location: Location name or coordinates
            include_forecast: Include forecast (default from config)
            
        Returns:
            Weather data dictionary
        """
        if not self.is_running:
            raise RuntimeError("Plugin not started")
        
        include_forecast = (
            include_forecast 
            if include_forecast is not None 
            else self.config.include_forecast
        )
        
        # Check cache
        cache_key = f"{location}:{include_forecast}"
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            age = (datetime.now() - cached["fetched_at"]).total_seconds()
            if age < self.config.cache_ttl_seconds:
                logger.debug(f"Cache hit for {location}")
                publish(WeatherDataFetched(
                    source="WeatherPlugin",
                    location=location,
                    temperature=cached["temperature"],
                    conditions=cached["conditions"],
                    cached=True,
                ))
                return cached
        
        # Fetch from API
        try:
            weather = self._api_client.get_current_weather(location)
            weather_requests.inc(
                provider=self.config.api_provider,
                status="success",
            )
            
            # Add forecast if requested
            if include_forecast:
                weather["forecast"] = self._api_client.get_forecast(
                    location,
                    hours=self.config.forecast_hours,
                )
            
            # Convert temperature if needed
            if self.config.temperature_unit == "fahrenheit":
                weather["temperature"] = self._celsius_to_fahrenheit(
                    weather["temperature"]
                )
                weather["temperature_unit"] = "F"
            else:
                weather["temperature_unit"] = "C"
            
            # Add metadata
            weather["fetched_at"] = datetime.now()
            weather["location"] = location
            
            # Cache result
            self._cache[cache_key] = weather
            
            # Emit event
            publish(WeatherDataFetched(
                source="WeatherPlugin",
                location=location,
                temperature=weather["temperature"],
                conditions=weather["conditions"],
                cached=False,
            ))
            
            return weather
            
        except Exception as e:
            logger.error(f"Failed to fetch weather for {location}: {e}")
            weather_requests.inc(
                provider=self.config.api_provider,
                status="error",
            )
            raise
    
    def get_travel_advice(
        self,
        location: str,
        weather: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Get LLM-generated travel advice based on weather.
        
        Args:
            location: Location name
            weather: Weather data (fetched if not provided)
            
        Returns:
            Travel advice string
        """
        if not self.config.generate_advice:
            return ""
        
        if weather is None:
            weather = self.get_weather(location)
        
        # Generate advice using LLM
        advice = self._generate_advice(location, weather)
        
        # Emit event
        publish(WeatherAdviceGenerated(
            source="WeatherPlugin",
            location=location,
            advice=advice,
        ))
        
        return advice
    
    # ==================== Private Methods ====================
    
    def _init_llm_client(self) -> None:
        """Initialize LLM client for advice generation."""
        try:
            from openai import OpenAI
            import os
            
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self._llm_client = OpenAI(api_key=api_key)
                logger.debug("LLM client initialized for advice generation")
        except ImportError:
            logger.warning("OpenAI not installed, advice generation disabled")
    
    def _generate_advice(
        self,
        location: str,
        weather: Dict[str, Any],
    ) -> str:
        """Generate travel advice using LLM."""
        if not self._llm_client:
            return self._generate_mock_advice(weather)
        
        prompt = f"""
        Location: {location}
        Current Weather:
        - Temperature: {weather['temperature']}°{weather.get('temperature_unit', 'C')}
        - Conditions: {weather['conditions']}
        - Humidity: {weather.get('humidity', 'N/A')}%
        - Wind: {weather.get('wind_speed', 'N/A')} km/h
        
        Please provide brief travel advice for someone visiting this location.
        """
        
        try:
            response = self._llm_client.chat.completions.create(
                model=self.config.llm_model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful travel weather advisor. "
                            "Provide brief, practical advice in 2-3 sentences."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=self.config.llm_temperature,
                max_tokens=150,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"LLM advice generation failed: {e}")
            return self._generate_mock_advice(weather)
    
    def _generate_mock_advice(self, weather: Dict[str, Any]) -> str:
        """Generate simple mock advice without LLM."""
        temp = weather.get("temperature", 20)
        conditions = weather.get("conditions", "clear").lower()
        
        if temp < 10:
            temp_advice = "It's cold, so dress warmly with layers."
        elif temp < 20:
            temp_advice = "The weather is mild, a light jacket should be enough."
        else:
            temp_advice = "It's warm, light clothing is recommended."
        
        if "rain" in conditions:
            condition_advice = "Bring an umbrella!"
        elif "snow" in conditions:
            condition_advice = "Watch for slippery conditions."
        elif "sun" in conditions or "clear" in conditions:
            condition_advice = "Great weather for outdoor sightseeing!"
        else:
            condition_advice = "Conditions look good for your visit."
        
        return f"{temp_advice} {condition_advice}"
    
    @staticmethod
    def _celsius_to_fahrenheit(celsius: float) -> float:
        """Convert Celsius to Fahrenheit."""
        return (celsius * 9 / 5) + 32


# ============== Weather API Clients ==============

class WeatherAPIClient:
    """Base class for weather API clients."""
    
    def get_current_weather(self, location: str) -> Dict[str, Any]:
        raise NotImplementedError
    
    def get_forecast(
        self,
        location: str,
        hours: int = 12,
    ) -> List[Dict[str, Any]]:
        raise NotImplementedError
    
    def is_available(self) -> bool:
        return True
    
    def close(self) -> None:
        pass


class MockWeatherClient(WeatherAPIClient):
    """Mock weather client for testing."""
    
    # Simulated weather data for common locations
    MOCK_DATA = {
        "tel aviv": {"temperature": 25, "conditions": "Sunny", "humidity": 60},
        "jerusalem": {"temperature": 22, "conditions": "Partly Cloudy", "humidity": 45},
        "paris": {"temperature": 18, "conditions": "Cloudy", "humidity": 70},
        "london": {"temperature": 15, "conditions": "Rainy", "humidity": 85},
        "new york": {"temperature": 20, "conditions": "Clear", "humidity": 55},
    }
    
    def get_current_weather(self, location: str) -> Dict[str, Any]:
        # Normalize location
        loc_lower = location.lower()
        for key, data in self.MOCK_DATA.items():
            if key in loc_lower:
                return {
                    **data,
                    "wind_speed": 15,
                    "visibility": 10,
                }
        
        # Default weather
        return {
            "temperature": 20,
            "conditions": "Clear",
            "humidity": 50,
            "wind_speed": 10,
            "visibility": 10,
        }
    
    def get_forecast(
        self,
        location: str,
        hours: int = 12,
    ) -> List[Dict[str, Any]]:
        current = self.get_current_weather(location)
        forecast = []
        
        for i in range(hours):
            forecast.append({
                "hour": i + 1,
                "temperature": current["temperature"] + (i % 5) - 2,
                "conditions": current["conditions"],
            })
        
        return forecast


class OpenWeatherMapClient(WeatherAPIClient):
    """OpenWeatherMap API client."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.api_key = api_key
        self.base_url = base_url or "https://api.openweathermap.org/data/2.5"
        self._session = None
    
    def get_current_weather(self, location: str) -> Dict[str, Any]:
        if not self.api_key:
            # Fall back to mock
            return MockWeatherClient().get_current_weather(location)
        
        import httpx
        
        response = httpx.get(
            f"{self.base_url}/weather",
            params={
                "q": location,
                "appid": self.api_key,
                "units": "metric",
            },
        )
        response.raise_for_status()
        data = response.json()
        
        return {
            "temperature": data["main"]["temp"],
            "conditions": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "visibility": data.get("visibility", 0) / 1000,  # Convert to km
        }
    
    def get_forecast(
        self,
        location: str,
        hours: int = 12,
    ) -> List[Dict[str, Any]]:
        if not self.api_key:
            return MockWeatherClient().get_forecast(location, hours)
        
        import httpx
        
        response = httpx.get(
            f"{self.base_url}/forecast",
            params={
                "q": location,
                "appid": self.api_key,
                "units": "metric",
                "cnt": hours // 3,  # API returns 3-hour intervals
            },
        )
        response.raise_for_status()
        data = response.json()
        
        return [
            {
                "hour": i * 3,
                "temperature": item["main"]["temp"],
                "conditions": item["weather"][0]["description"],
            }
            for i, item in enumerate(data["list"])
        ]
    
    def is_available(self) -> bool:
        if not self.api_key:
            return True  # Mock is always available
        
        try:
            import httpx
            response = httpx.get(
                f"{self.base_url}/weather",
                params={"q": "London", "appid": self.api_key},
                timeout=5.0,
            )
            return response.status_code == 200
        except Exception:
            return False

