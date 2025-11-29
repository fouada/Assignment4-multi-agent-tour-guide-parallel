"""
Base Agent class that all specialized agents inherit from.
Provides common functionality for LLM interaction and logging.
"""

import threading
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

import anthropic
from openai import OpenAI

from src.models.content import ContentResult, ContentType
from src.models.route import RoutePoint
from src.utils.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Agent skills loaded from config (can be extended via YAML)
AGENT_SKILLS: dict[str, Any] = {}


class BaseAgent(ABC):
    """
    Abstract base class for all content agents.

    Provides:
    - LLM integration (OpenAI/Anthropic)
    - Logging with context
    - Standard interface for content search
    """

    def __init__(self, agent_type: str):
        """
        Initialize the agent.

        Args:
            agent_type: Type of agent (video, music, text, judge)
        """
        self.agent_type = agent_type
        self.skills = AGENT_SKILLS.get(f"{agent_type}_agent", {})
        self.name = self.skills.get("name", f"{agent_type.title()} Agent")
        self.description = self.skills.get("description", "")
        self.scoring_criteria = self.skills.get("scoring_criteria", [])

        # Initialize LLM client
        self._init_llm_client()

        # Track execution
        self.current_point_id: str | None = None
        self.thread_name: str | None = None

    def _init_llm_client(self):
        """Initialize the appropriate LLM client. Prioritizes Claude/Anthropic."""
        # Priority 1: Anthropic/Claude (preferred)
        if settings.anthropic_api_key:
            self.llm_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            self.llm_type = "anthropic"
            logger.info(f"{self.name}: Using Claude (Anthropic)")
        # Priority 2: OpenAI (fallback)
        elif settings.openai_api_key:
            self.llm_client = OpenAI(api_key=settings.openai_api_key)
            self.llm_type = "openai"
            logger.info(f"{self.name}: Using GPT (OpenAI)")
        # Priority 3: No API key - use mock responses
        else:
            self.llm_client = None
            self.llm_type = None
            logger.warning(
                f"{self.name}: No LLM API key configured - using mock responses"
            )

    def _call_llm(self, prompt: str, system_prompt: str | None = None) -> str:
        """
        Call the LLM with the given prompt.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt

        Returns:
            LLM response text
        """
        if not self.llm_client:
            return self._mock_llm_response(prompt)

        try:
            if self.llm_type == "anthropic":
                messages = [{"role": "user", "content": prompt}]
                response = self.llm_client.messages.create(
                    model=settings.llm_model
                    if "claude" in settings.llm_model
                    else "claude-3-haiku-20240307",
                    max_tokens=1024,
                    system=system_prompt or self._get_system_prompt(),
                    messages=messages,
                )
                return str(response.content[0].text)
            else:  # OpenAI
                messages = []
                if system_prompt or self._get_system_prompt():
                    messages.append(
                        {
                            "role": "system",
                            "content": system_prompt or self._get_system_prompt(),
                        }
                    )
                messages.append({"role": "user", "content": prompt})

                response = self.llm_client.chat.completions.create(
                    model=settings.llm_model,
                    messages=messages,
                    temperature=settings.llm_temperature,
                )
                return str(response.choices[0].message.content or "")

        except Exception as e:
            logger.error(f"{self.name}: LLM call failed - {e}")
            return self._mock_llm_response(prompt)

    def _mock_llm_response(self, prompt: str) -> str:
        """Provide a mock response when LLM is unavailable."""
        return f"Mock response for: {prompt[:100]}..."

    def _get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        criteria_text = "\n".join(f"- {c}" for c in self.scoring_criteria)
        return f"""You are the {self.name}. {self.description}

When evaluating content, consider these criteria:
{criteria_text}

Always provide relevant, accurate, and engaging content recommendations.
Respond in a structured format that can be easily parsed."""

    def execute(self, point: RoutePoint) -> ContentResult | None:
        """
        Execute the agent's task for a given route point.

        Args:
            point: The route point to find content for

        Returns:
            ContentResult or None if failed
        """
        self.current_point_id = point.id
        self.thread_name = threading.current_thread().name

        logger.info(f"[{self.agent_type}] Starting search for: {point.address}")

        start_time = datetime.now()

        try:
            result = self._search_content(point)

            if result:
                duration = (datetime.now() - start_time).total_seconds()
                logger.info(
                    f"[{self.agent_type}] Found: {result.title} ({duration:.2f}s)"
                )
                return result
            else:
                logger.warning(
                    f"[{self.agent_type}] No content found for {point.address}"
                )
                return None

        except Exception as e:
            logger.error(f"[{self.agent_type}] Error: {e}")
            return None

    @abstractmethod
    def _search_content(self, point: RoutePoint) -> ContentResult | None:
        """
        Search for content relevant to the route point.
        Must be implemented by subclasses.

        Args:
            point: The route point to find content for

        Returns:
            ContentResult or None
        """
        pass

    @abstractmethod
    def get_content_type(self) -> ContentType:
        """Return the type of content this agent provides."""
        pass

    def _calculate_relevance_score(
        self, content: dict[str, Any], location: str
    ) -> float:
        """
        Use LLM to calculate relevance score for content.

        Args:
            content: Content metadata
            location: Location name/address

        Returns:
            Relevance score 0-10
        """
        prompt = f"""Rate the relevance of this content to the location on a scale of 0-10.

Location: {location}

Content:
- Title: {content.get("title", "Unknown")}
- Description: {content.get("description", "No description")}
- Source: {content.get("source", "Unknown")}

Consider:
1. How directly related is this content to the specific location?
2. Would this enhance a traveler's experience at this location?
3. Is the content informative or entertaining about this place?

Respond with ONLY a number between 0 and 10 (can include decimals)."""

        try:
            response = self._call_llm(prompt)
            # Extract number from response
            import re

            numbers = re.findall(r"\d+\.?\d*", response)
            if numbers:
                score = float(numbers[0])
                return min(max(score, 0.0), 10.0)
        except Exception:
            pass

        return 5.0  # Default score
