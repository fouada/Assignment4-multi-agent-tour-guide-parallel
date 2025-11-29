"""
Weather Plugin
==============

A complete example plugin demonstrating the full plugin architecture.

This plugin provides weather information for route points, showing:
- Plugin lifecycle management
- Event emission
- Hook integration
- Metrics collection
- Health checks
- Configuration validation
- LLM integration for advice

Usage:
    # The plugin is auto-discovered from the plugins/ directory
    # Just ensure plugin.yaml is present
    
    # Or register manually:
    from plugins.weather import WeatherPlugin
    PluginRegistry.register("weather")(WeatherPlugin)
"""

from plugins.weather.plugin import WeatherPlugin, WeatherConfig
from plugins.weather.agent import WeatherAgent, WeatherAgentConfig

__all__ = [
    "WeatherPlugin",
    "WeatherConfig",
    "WeatherAgent",
    "WeatherAgentConfig",
]

