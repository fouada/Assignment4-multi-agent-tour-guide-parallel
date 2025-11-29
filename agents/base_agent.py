"""
Base Agent class that all specialized agents inherit from.
Provides common functionality for LLM interaction and logging.
"""
from abc import ABC, abstractmethod
from typing import Optional, Any, Dict
import threading
from datetime import datetime

from openai import OpenAI
import anthropic

from config import settings, AGENT_SKILLS
from models import ContentResult, ContentType, RoutePoint
from logger_setup import logger, set_log_context, log_agent_start, log_agent_result, log_agent_error


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
        self.current_point_id: Optional[str] = None
        self.thread_name: Optional[str] = None
    
    def _init_llm_client(self):
        """Initialize the appropriate LLM client."""
        if settings.llm_provider == "anthropic" and settings.anthropic_api_key:
            self.llm_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            self.llm_type = "anthropic"
        elif settings.openai_api_key:
            self.llm_client = OpenAI(api_key=settings.openai_api_key)
            self.llm_type = "openai"
        else:
            self.llm_client = None
            self.llm_type = None
            logger.warning(f"{self.name}: No LLM API key configured")
    
    def _call_llm(self, prompt: str, system_prompt: Optional[str] = None) -> str:
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
                    model=settings.llm_model if "claude" in settings.llm_model else "claude-3-haiku-20240307",
                    max_tokens=1024,
                    system=system_prompt or self._get_system_prompt(),
                    messages=messages
                )
                return response.content[0].text
            else:  # OpenAI
                messages = []
                if system_prompt or self._get_system_prompt():
                    messages.append({
                        "role": "system",
                        "content": system_prompt or self._get_system_prompt()
                    })
                messages.append({"role": "user", "content": prompt})
                
                response = self.llm_client.chat.completions.create(
                    model=settings.llm_model,
                    messages=messages,
                    temperature=settings.llm_temperature
                )
                return response.choices[0].message.content
                
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
    
    # Retry configuration
    MAX_RETRIES = 3
    BASE_DELAY_SECONDS = 1.0
    EXPONENTIAL_BASE = 2.0
    MAX_DELAY_SECONDS = 10.0
    
    def execute(self, point: RoutePoint) -> Optional[ContentResult]:
        """
        Execute the agent's task for a given route point WITH RETRY.
        
        Retry Strategy:
        - Up to MAX_RETRIES attempts (default: 3)
        - Exponential backoff: 1s, 2s, 4s
        - If all retries fail: return None
        
        Args:
            point: The route point to find content for
            
        Returns:
            ContentResult or None if all retries failed
        """
        self.current_point_id = point.id
        self.thread_name = threading.current_thread().name
        
        set_log_context(point_id=point.id, agent_type=self.agent_type)
        log_agent_start(self.agent_type, point.id, point.address)
        
        start_time = datetime.now()
        last_error = None
        
        # ═══════════════════════════════════════════════════════════════════
        # RETRY LOOP with Exponential Backoff
        # ═══════════════════════════════════════════════════════════════════
        for attempt in range(self.MAX_RETRIES + 1):  # +1 for initial attempt
            try:
                logger.info(
                    f"[{point.id}][{self.agent_type}] "
                    f"Attempt {attempt + 1}/{self.MAX_RETRIES + 1}"
                )
                
                result = self._search_content(point)
                
                if result:
                    duration = (datetime.now() - start_time).total_seconds()
                    log_agent_result(
                        self.agent_type, 
                        point.id, 
                        f"{result.title} (took {duration:.2f}s, attempts: {attempt + 1})"
                    )
                    return result
                else:
                    # No result but no exception - still a failure
                    raise ValueError("No content found")
                    
            except Exception as e:
                last_error = str(e)
                
                if attempt < self.MAX_RETRIES:
                    # Calculate exponential backoff delay
                    delay = self._calculate_backoff_delay(attempt)
                    
                    logger.warning(
                        f"[{point.id}][{self.agent_type}] "
                        f"Attempt {attempt + 1} failed: {e}. "
                        f"Waiting {delay:.2f}s before retry..."
                    )
                    
                    import time
                    time.sleep(delay)
                else:
                    # All retries exhausted
                    duration = (datetime.now() - start_time).total_seconds()
                    log_agent_error(
                        self.agent_type, 
                        point.id, 
                        f"All {self.MAX_RETRIES + 1} attempts failed after {duration:.2f}s. "
                        f"Last error: {last_error}"
                    )
        
        return None
    
    def _calculate_backoff_delay(self, attempt: int) -> float:
        """
        Calculate delay using exponential backoff with jitter.
        
        Formula: delay = BASE_DELAY * (EXPONENTIAL_BASE ^ attempt) + jitter
        
        Example (with BASE_DELAY=1, EXPONENTIAL_BASE=2):
            Attempt 0: 1 * 2^0 = 1 second
            Attempt 1: 1 * 2^1 = 2 seconds
            Attempt 2: 1 * 2^2 = 4 seconds
            
        Returns:
            Delay in seconds
        """
        import random
        
        delay = self.BASE_DELAY_SECONDS * (self.EXPONENTIAL_BASE ** attempt)
        delay = min(delay, self.MAX_DELAY_SECONDS)
        
        # Add jitter (0-25% of delay) to prevent thundering herd
        jitter = delay * random.uniform(0, 0.25)
        delay += jitter
        
        return delay
    
    def execute_with_queue(self, point: RoutePoint, queue) -> None:
        """
        Execute agent and submit result to queue.
        
        This method is used when running with queue-based synchronization.
        The queue will handle waiting for all agents.
        
        Args:
            point: The route point to find content for
            queue: SmartAgentQueue to submit results to
        """
        try:
            result = self.execute(point)
            
            if result:
                queue.submit_success(self.agent_type, result)
            else:
                queue.submit_failure(
                    self.agent_type, 
                    f"No content found after {self.MAX_RETRIES + 1} attempts"
                )
        except Exception as e:
            queue.submit_failure(self.agent_type, str(e))
    
    @abstractmethod
    def _search_content(self, point: RoutePoint) -> Optional[ContentResult]:
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
    
    def _calculate_relevance_score(self, content: Dict[str, Any], location: str) -> float:
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
- Title: {content.get('title', 'Unknown')}
- Description: {content.get('description', 'No description')}
- Source: {content.get('source', 'Unknown')}

Consider:
1. How directly related is this content to the specific location?
2. Would this enhance a traveler's experience at this location?
3. Is the content informative or entertaining about this place?

Respond with ONLY a number between 0 and 10 (can include decimals)."""

        try:
            response = self._call_llm(prompt)
            # Extract number from response
            import re
            numbers = re.findall(r'\d+\.?\d*', response)
            if numbers:
                score = float(numbers[0])
                return min(max(score, 0.0), 10.0)
        except Exception:
            pass
        
        return 5.0  # Default score

