"""
Agent Configuration Loader

Loads agent configurations from YAML files following best practices
for AI agent configuration management.

Benefits of YAML configs:
- Human readable
- Supports comments
- Easy to modify without code changes
- Standard for CI/CD and configuration
"""

from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]
from logger_setup import logger


class AgentConfigLoader:
    """
    Loads agent configurations from YAML files.

    Usage:
        loader = AgentConfigLoader()
        video_config = loader.load("video_agent")

        # Access config
        print(video_config['agent']['name'])
        print(video_config['skills'])
        print(video_config['prompt'])
    """

    DEFAULT_CONFIG_DIR = Path(__file__).parent / "configs"

    def __init__(self, config_dir: Path | None = None):
        """
        Initialize the config loader.

        Args:
            config_dir: Directory containing YAML configs.
                       Defaults to ./agents/configs/
        """
        self.config_dir = config_dir or self.DEFAULT_CONFIG_DIR
        self._cache: dict[str, dict] = {}

        if not self.config_dir.exists():
            logger.warning(f"Config directory not found: {self.config_dir}")

    def load(self, agent_name: str, use_cache: bool = True) -> dict[str, Any]:
        """
        Load configuration for an agent.

        Args:
            agent_name: Name of the agent (e.g., "video_agent")
            use_cache: Whether to use cached config

        Returns:
            Agent configuration dictionary
        """
        # Check cache
        if use_cache and agent_name in self._cache:
            return self._cache[agent_name]

        # Build file path
        config_file = self.config_dir / f"{agent_name}.yaml"

        if not config_file.exists():
            logger.warning(f"Config file not found: {config_file}")
            return self._get_default_config(agent_name)

        try:
            with open(config_file, encoding="utf-8") as f:
                config = yaml.safe_load(f)

            # Cache it
            self._cache[agent_name] = config

            logger.info(f"Loaded config for {agent_name} from {config_file}")
            return dict(config) if config else self._get_default_config(agent_name)

        except Exception as e:
            logger.error(f"Error loading config {config_file}: {e}")
            return self._get_default_config(agent_name)

    def _get_default_config(self, agent_name: str) -> dict[str, Any]:
        """Get default configuration if YAML not found."""
        return {
            "agent": {
                "name": agent_name.replace("_", " ").title(),
                "version": "1.0.0",
                "description": f"Default config for {agent_name}",
            },
            "config": {
                "model": "gpt-4o-mini",
                "temperature": 0.7,
                "max_tokens": 2000,
                "timeout_seconds": 30,
            },
            "skills": [],
            "tools": [],
            "prompt": f"You are a {agent_name.replace('_', ' ')}.",
        }

    def get_prompt(self, agent_name: str) -> str:
        """Get the system prompt for an agent."""
        config = self.load(agent_name)
        return str(config.get("prompt", ""))

    def get_skills(self, agent_name: str) -> list[Any]:
        """Get the skills defined for an agent."""
        config = self.load(agent_name)
        return list(config.get("skills", []))

    def get_tools(self, agent_name: str) -> list[Any]:
        """Get the tools configured for an agent."""
        config = self.load(agent_name)
        return list(config.get("tools", []))

    def list_available_agents(self) -> list[str]:
        """List all available agent configurations."""
        if not self.config_dir.exists():
            return []

        return [f.stem for f in self.config_dir.glob("*.yaml")]

    def reload(self, agent_name: str | None = None) -> None:
        """
        Reload configuration(s) from disk.

        Args:
            agent_name: Specific agent to reload, or None for all
        """
        if agent_name:
            if agent_name in self._cache:
                del self._cache[agent_name]
            self.load(agent_name)
        else:
            self._cache.clear()
            for name in self.list_available_agents():
                self.load(name)


# Singleton instance
_loader = None


def get_config_loader() -> AgentConfigLoader:
    """Get the singleton config loader instance."""
    global _loader
    if _loader is None:
        _loader = AgentConfigLoader()
    return _loader


def load_agent_config(agent_name: str) -> dict[str, Any]:
    """
    Convenience function to load an agent's config.

    Args:
        agent_name: Name of agent (e.g., "video_agent")

    Returns:
        Configuration dictionary
    """
    return get_config_loader().load(agent_name)


# Example usage and testing
if __name__ == "__main__":
    loader = AgentConfigLoader()

    print("Available agents:", loader.list_available_agents())
    print()

    for agent in loader.list_available_agents():
        config = loader.load(agent)
        print(f"Agent: {config['agent']['name']}")
        print(f"  Description: {config['agent']['description'][:50]}...")
        print(f"  Skills: {len(config.get('skills', []))}")
        print()
