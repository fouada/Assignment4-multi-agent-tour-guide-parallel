"""
Video Agent - Specializes in finding relevant YouTube videos for locations.
"""
from typing import Optional, List, Dict, Any
import re

from src.agents.base_agent import BaseAgent
from src.models.content import ContentResult, ContentType
from src.models.route import RoutePoint
from src.utils.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class VideoAgent(BaseAgent):
    """
    Agent specialized in finding YouTube videos relevant to locations.
    Uses YouTube Data API and LLM for smart search and ranking.
    """
    
    def __init__(self):
        super().__init__("video")
        self._init_youtube_client()
    
    def _init_youtube_client(self):
        """Initialize YouTube API client."""
        self.youtube_client = None
        
        if settings.youtube_api_key:
            try:
                from googleapiclient.discovery import build
                self.youtube_client = build(
                    'youtube', 'v3',
                    developerKey=settings.youtube_api_key
                )
                logger.info("YouTube API client initialized")
            except Exception as e:
                logger.warning(f"Could not initialize YouTube client: {e}")
    
    def get_content_type(self) -> ContentType:
        return ContentType.VIDEO
    
    def _search_content(self, point: RoutePoint) -> Optional[ContentResult]:
        """Search for relevant YouTube videos."""
        
        # Generate search queries using LLM
        search_queries = self._generate_search_queries(point)
        
        # Search YouTube
        videos = []
        for query in search_queries[:3]:  # Limit to 3 queries
            results = self._search_youtube(query)
            videos.extend(results)
        
        if not videos:
            # Fallback to mock data
            return self._get_mock_result(point)
        
        # Rank videos and select best one
        best_video = self._select_best_video(videos, point)
        
        if best_video:
            return ContentResult(
                point_id=point.id,
                content_type=ContentType.VIDEO,
                title=best_video.get('title', 'Unknown Video'),
                description=best_video.get('description', ''),
                url=f"https://www.youtube.com/watch?v={best_video.get('video_id', '')}",
                source="YouTube",
                relevance_score=best_video.get('relevance_score', 5.0),
                metadata={
                    'video_id': best_video.get('video_id'),
                    'channel': best_video.get('channel'),
                    'duration': best_video.get('duration'),
                    'views': best_video.get('views'),
                    'thumbnail': best_video.get('thumbnail')
                }
            )
        
        return self._get_mock_result(point)
    
    def _generate_search_queries(self, point: RoutePoint) -> List[str]:
        """Use LLM to generate effective search queries."""
        
        location = point.location_name or point.address
        
        prompt = f"""Generate 3 YouTube search queries to find interesting videos about this location.
The videos should be suitable to watch/listen while traveling.

Location: {location}
Full Address: {point.address}

Consider searching for:
- Documentaries about the place
- Historical videos
- Travel vlogs
- Music videos filmed there
- News reports about significant events there

Return ONLY 3 search queries, one per line, no numbering or bullets."""

        try:
            response = self._call_llm(prompt)
            queries = [q.strip() for q in response.strip().split('\n') if q.strip()]
            return queries[:3] if queries else [location]
        except Exception:
            return [location, f"{location} history", f"{location} documentary"]
    
    def _search_youtube(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search YouTube for videos."""
        
        if not self.youtube_client:
            return []
        
        try:
            request = self.youtube_client.search().list(
                part='snippet',
                q=query,
                type='video',
                maxResults=max_results,
                relevanceLanguage=settings.language,
                videoDuration='medium',  # 4-20 minutes
                safeSearch='moderate'
            )
            response = request.execute()
            
            videos = []
            for item in response.get('items', []):
                snippet = item.get('snippet', {})
                videos.append({
                    'video_id': item.get('id', {}).get('videoId'),
                    'title': snippet.get('title', ''),
                    'description': snippet.get('description', ''),
                    'channel': snippet.get('channelTitle', ''),
                    'thumbnail': snippet.get('thumbnails', {}).get('medium', {}).get('url'),
                    'published_at': snippet.get('publishedAt')
                })
            
            return videos
            
        except Exception as e:
            logger.warning(f"YouTube search failed: {e}")
            return []
    
    def _select_best_video(self, videos: List[Dict], point: RoutePoint) -> Optional[Dict]:
        """Use LLM to select the most relevant video."""
        
        if not videos:
            return None
        
        location = point.location_name or point.address
        
        # Create video list for LLM
        video_list = "\n".join([
            f"{i+1}. Title: {v['title']}\n   Channel: {v['channel']}\n   Description: {v['description'][:100]}..."
            for i, v in enumerate(videos[:5])
        ])
        
        prompt = f"""Select the BEST video for a traveler passing through this location.

Location: {location}

Available Videos:
{video_list}

Consider:
1. Relevance to the specific location
2. Educational or entertainment value
3. Appropriate length for travel
4. Production quality (based on channel/title)

Respond with:
- The number of the best video (1-{len(videos[:5])})
- A relevance score from 0-10
- Brief reason for selection

Format:
VIDEO: [number]
SCORE: [0-10]
REASON: [one sentence]"""

        try:
            response = self._call_llm(prompt)
            
            # Parse response
            video_match = re.search(r'VIDEO:\s*(\d+)', response)
            score_match = re.search(r'SCORE:\s*([\d.]+)', response)
            reason_match = re.search(r'REASON:\s*(.+)', response)
            
            if video_match:
                idx = int(video_match.group(1)) - 1
                if 0 <= idx < len(videos):
                    selected = videos[idx].copy()
                    selected['relevance_score'] = float(score_match.group(1)) if score_match else 5.0
                    selected['selection_reason'] = reason_match.group(1) if reason_match else ""
                    return selected
        except Exception as e:
            logger.warning(f"Video selection failed: {e}")
        
        # Fallback: return first video
        if videos:
            videos[0]['relevance_score'] = 5.0
            return videos[0]
        
        return None
    
    def _get_mock_result(self, point: RoutePoint) -> ContentResult:
        """Return mock result for testing."""
        location = point.location_name or point.address
        
        # Some realistic mock videos for Israeli locations
        mock_videos = {
            "Ammunition Hill": {
                "title": "The Battle of Ammunition Hill - Documentary",
                "video_id": "dQw4w9WgXcQ",
                "description": "Documentary about the fierce battle during the Six-Day War"
            },
            "Tel Aviv": {
                "title": "Tel Aviv: The City That Never Sleeps",
                "video_id": "abc123",
                "description": "Explore the vibrant streets of Israel's cultural capital"
            },
            "Jerusalem": {
                "title": "Jerusalem: 3000 Years of History",
                "video_id": "xyz789",
                "description": "A journey through the holy city's fascinating past"
            },
            "Latrun": {
                "title": "Latrun Tank Museum - Israel's Armored Corps",
                "video_id": "tank456",
                "description": "Explore the impressive tank collection at Latrun"
            }
        }
        
        # Find matching mock or create generic one
        mock = None
        for key, video in mock_videos.items():
            if key in location or key in point.address:
                mock = video
                break
        
        if not mock:
            mock = {
                "title": f"Discovering {location}",
                "video_id": "mock_" + point.id,
                "description": f"An exploration of {location} and its surroundings"
            }
        
        return ContentResult(
            point_id=point.id,
            content_type=ContentType.VIDEO,
            title=mock["title"],
            description=mock["description"],
            url=f"https://www.youtube.com/watch?v={mock['video_id']}",
            source="YouTube (Mock)",
            relevance_score=7.5,
            metadata={'video_id': mock['video_id'], 'mock': True}
        )

