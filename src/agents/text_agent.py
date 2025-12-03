"""
Text Agent - Specializes in finding historical facts and interesting stories about locations.
Uses web search and LLM for intelligent content discovery.
"""

import re
import warnings
from typing import Any

# Suppress the deprecation warning about duckduckgo_search package rename
# This warning is triggered when importing the package
warnings.filterwarnings("ignore", message=".*has been renamed.*", category=RuntimeWarning)

from src.agents.base_agent import BaseAgent
from src.models.content import ContentResult, ContentType
from src.models.route import RoutePoint
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TextAgent(BaseAgent):
    """
    Agent specialized in finding historical and interesting textual content.
    Uses DuckDuckGo search and LLM for summarization.
    """

    def __init__(self):
        super().__init__("text")
        self._init_search_client()

    def _init_search_client(self):
        """Initialize web search client."""
        self.search_available = False

        try:
            # Suppress RuntimeWarning from duckduckgo_search about package rename
            # This uses filterwarnings with lineno=0 to catch all warnings from this module
            warnings.filterwarnings(
                "ignore",
                message=".*renamed.*",
                category=RuntimeWarning,
                lineno=0,  # Match any line
            )
            from duckduckgo_search import DDGS

            self.search_client = DDGS()

            self.search_available = True
            logger.info("DuckDuckGo search client initialized")
        except ImportError:
            logger.warning("duckduckgo-search not available")
            self.search_client = None

    def get_content_type(self) -> ContentType:
        return ContentType.TEXT

    def _search_content(self, point: RoutePoint) -> ContentResult | None:
        """Search for interesting facts and stories."""

        # Generate search queries using LLM
        search_queries = self._generate_search_queries(point)

        # Search the web
        all_results = []
        for query in search_queries[:3]:
            results = self._search_web(query)
            all_results.extend(results)

        if not all_results:
            return self._get_mock_result(point)

        # Synthesize the best story/fact using LLM
        content = self._synthesize_content(all_results, point)

        if content:
            return ContentResult(
                point_id=point.id,
                content_type=ContentType.TEXT,
                title=content.get(
                    "title", f"About {point.location_name or point.address}"
                ),
                description=content.get("story", ""),
                url=content.get("source_url", ""),
                source=content.get("source", "Web Search"),
                relevance_score=content.get("relevance_score", 5.0),
                metadata={
                    "fact_type": content.get("fact_type", "general"),
                    "sources": content.get("sources", []),
                    "is_historical": content.get("is_historical", False),
                },
            )

        return self._get_mock_result(point)

    def _generate_search_queries(self, point: RoutePoint) -> list[str]:
        """Use LLM to generate search queries for interesting facts."""

        location = point.location_name or point.address

        prompt = f"""Generate 3 web search queries to find interesting facts, stories, or history about this location.

Location: {location}
Full Address: {point.address}

Search for:
- Historical events that happened here
- Famous people associated with this place
- Interesting or surprising facts
- Cultural significance
- Unique characteristics

Return ONLY 3 search queries, one per line, no numbering or bullets.
Mix Hebrew and English queries for better coverage."""

        try:
            response = self._call_llm(prompt)
            queries = [q.strip() for q in response.strip().split("\n") if q.strip()]
            return (
                queries[:3] if queries else [f"{location} history", f"{location} facts"]
            )
        except Exception:
            return [
                f"{location} history",
                f"{location} interesting facts",
                f"{location} historical facts",
            ]

    def _search_web(self, query: str, max_results: int = 5) -> list[dict[str, Any]]:
        """Search the web for information."""

        if not self.search_available or not self.search_client:
            return []

        try:
            results = list(
                self.search_client.text(
                    query,
                    max_results=max_results,
                    region="il-he",  # Israel, Hebrew
                )
            )

            parsed_results = []
            for result in results:
                parsed_results.append(
                    {
                        "title": result.get("title", ""),
                        "snippet": result.get("body", ""),
                        "url": result.get("href", ""),
                        "source": self._extract_domain(result.get("href", "")),
                    }
                )

            return parsed_results

        except Exception as e:
            logger.warning(f"Web search failed: {e}")
            return []

    def _extract_domain(self, url: str) -> str:
        """Extract domain name from URL."""
        try:
            from urllib.parse import urlparse

            parsed = urlparse(url)
            domain = parsed.netloc.replace("www.", "")
            return domain
        except Exception:
            return url

    def _synthesize_content(
        self, results: list[dict], point: RoutePoint
    ) -> dict | None:
        """Use LLM to create an engaging story from search results."""

        if not results:
            return None

        location = point.location_name or point.address

        # Compile snippets for LLM
        snippets = "\n\n".join(
            [
                f"Source: {r['source']}\nTitle: {r['title']}\nContent: {r['snippet']}"
                for r in results[:5]
            ]
        )

        prompt = f"""Based on these search results, create an engaging short story or interesting fact about this location.

Location: {location}

Search Results:
{snippets}

Create a compelling 2-3 sentence story or fact that would interest a traveler passing through.
Focus on:
- Surprising or little-known facts
- Historical significance
- Human interest stories
- Unique characteristics of the place

Respond in this format:
TITLE: [Catchy title for the story/fact]
TYPE: [historical/cultural/fun_fact/human_interest]
STORY: [The 2-3 sentence engaging content]
SCORE: [Relevance score 0-10]"""

        try:
            response = self._call_llm(prompt)

            # Parse response
            title_match = re.search(r"TITLE:\s*(.+)", response)
            type_match = re.search(r"TYPE:\s*(.+)", response)
            story_match = re.search(r"STORY:\s*(.+?)(?=SCORE:|$)", response, re.DOTALL)
            score_match = re.search(r"SCORE:\s*([\d.]+)", response)

            return {
                "title": title_match.group(1).strip()
                if title_match
                else f"About {location}",
                "fact_type": type_match.group(1).strip() if type_match else "general",
                "story": story_match.group(1).strip()
                if story_match
                else response[:200],
                "relevance_score": float(score_match.group(1)) if score_match else 5.0,
                "sources": [r["source"] for r in results[:3]],
                "source_url": results[0]["url"] if results else "",
                "source": results[0]["source"] if results else "Web Search",
                "is_historical": "historical"
                in (type_match.group(1) if type_match else ""),
            }

        except Exception as e:
            logger.warning(f"Content synthesis failed: {e}")
            return None

    def _get_mock_result(self, point: RoutePoint) -> ContentResult:
        """Return mock result for testing."""
        location = point.location_name or point.address

        # Some realistic mock stories for Israeli locations
        mock_stories = {
            "Ammunition Hill": {
                "title": "The Fierce Battle of Ammunition Hill",
                "story": "On June 6, 1967, Israeli paratroopers fought one of the bloodiest battles of the Six-Day War here. The 4-hour battle to capture this Jordanian military position became a symbol of Israeli courage. Today, a museum honors the 36 soldiers who fell in battle.",
                "type": "historical",
            },
            "Tel Aviv": {
                "title": "The First Hebrew City",
                "story": "Founded in 1909 on sand dunes north of the ancient port of Jaffa, Tel Aviv was the first modern Hebrew city. Its founders held a lottery using seashells to divide the land plots. The city's name means 'Hill of Spring' - combining the ancient and the new.",
                "type": "historical",
            },
            "Jerusalem": {
                "title": "The City of Three Faiths",
                "story": "Jerusalem has been conquered, destroyed, and rebuilt over 40 times throughout its 5,000-year history. It remains the only city in the world considered holy by three major religions simultaneously - Judaism, Christianity, and Islam.",
                "type": "cultural",
            },
            "Latrun": {
                "title": "The Silent Monks of Latrun",
                "story": "The Trappist monastery at Latrun has been producing wine since 1890. The monks who live there observe strict vows of silence, yet their wines 'speak' volumes - becoming some of Israel's most celebrated vintages.",
                "type": "fun_fact",
            },
        }

        # Find matching mock or create generic one
        mock = None
        for key, story in mock_stories.items():
            if key in location or key in point.address:
                mock = story
                break

        if not mock:
            mock = {
                "title": f"Discovering {location}",
                "story": f"This area of {location} has been inhabited for thousands of years and has witnessed countless historical events. From ancient times to modern day, it continues to be a place where history comes alive.",
                "type": "general",
            }

        return ContentResult(
            point_id=point.id,
            content_type=ContentType.TEXT,
            title=mock["title"],
            description=mock["story"],
            url="",
            source="Historical Archives (Mock)",
            relevance_score=7.5,
            metadata={"fact_type": mock["type"], "mock": True},
        )
