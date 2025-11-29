"""
Music Agent - Specializes in finding relevant songs for locations.
Uses YouTube Music search (or Spotify) and LLM for smart recommendations.
"""
import re
from typing import Any

from src.agents.base_agent import BaseAgent
from src.models.content import ContentResult, ContentType
from src.models.route import RoutePoint
from src.utils.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MusicAgent(BaseAgent):
    """
    Agent specialized in finding songs relevant to locations.
    Can use YouTube, Spotify, or web search for music discovery.
    """

    def __init__(self):
        super().__init__("music")
        self._init_music_clients()

    def _init_music_clients(self):
        """Initialize music API clients."""
        self.spotify_client = None
        self.youtube_music_available = False

        # Try Spotify
        if settings.spotify_client_id and settings.spotify_client_secret:
            try:
                import spotipy
                from spotipy.oauth2 import SpotifyClientCredentials

                auth_manager = SpotifyClientCredentials(
                    client_id=settings.spotify_client_id,
                    client_secret=settings.spotify_client_secret
                )
                self.spotify_client = spotipy.Spotify(auth_manager=auth_manager)
                logger.info("Spotify client initialized")
            except Exception as e:
                logger.warning(f"Could not initialize Spotify client: {e}")

        # Try YouTube search for music
        try:
            from youtubesearchpython import VideosSearch
            self.youtube_music_available = True
            logger.info("YouTube music search available")
        except ImportError:
            logger.warning("youtube-search-python not available for music search")

    def get_content_type(self) -> ContentType:
        return ContentType.MUSIC

    def _search_content(self, point: RoutePoint) -> ContentResult | None:
        """Search for relevant songs."""

        # Generate search queries using LLM
        search_queries = self._generate_search_queries(point)

        # Try different sources
        songs = []

        # Try Spotify first
        if self.spotify_client:
            for query in search_queries[:2]:
                results = self._search_spotify(query)
                songs.extend(results)

        # Try YouTube Music
        if not songs and self.youtube_music_available:
            for query in search_queries[:2]:
                results = self._search_youtube_music(query)
                songs.extend(results)

        if not songs:
            return self._get_mock_result(point)

        # Rank and select best song
        best_song = self._select_best_song(songs, point)

        if best_song:
            return ContentResult(
                point_id=point.id,
                content_type=ContentType.MUSIC,
                title=best_song.get('title', 'Unknown Song'),
                description=f"by {best_song.get('artist', 'Unknown Artist')}",
                url=best_song.get('url', ''),
                source=best_song.get('source', 'Music'),
                relevance_score=best_song.get('relevance_score', 5.0),
                metadata={
                    'artist': best_song.get('artist'),
                    'album': best_song.get('album'),
                    'duration': best_song.get('duration'),
                    'preview_url': best_song.get('preview_url')
                }
            )

        return self._get_mock_result(point)

    def _generate_search_queries(self, point: RoutePoint) -> list[str]:
        """Use LLM to generate music search queries."""

        location = point.location_name or point.address

        prompt = f"""Generate 3 search queries to find songs related to this location in Israel.
Songs could be:
- About the location directly
- By artists from the area
- That mention the location in lyrics
- That capture the mood/spirit of the place
- Israeli songs related to the location

Location: {location}
Full Address: {point.address}

Return ONLY 3 search queries, one per line, no numbering or bullets.
Include both Hebrew and English search terms if relevant."""

        try:
            response = self._call_llm(prompt)
            queries = [q.strip() for q in response.strip().split('\n') if q.strip()]
            return queries[:3] if queries else [f"{location} song", f"{location} music"]
        except Exception:
            return [f"{location} song", f"{location} Israeli song", f"{location} music"]

    def _search_spotify(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """Search Spotify for songs."""

        if not self.spotify_client:
            return []

        try:
            results = self.spotify_client.search(
                q=query,
                type='track',
                limit=limit,
                market='IL'
            )

            songs = []
            for track in results.get('tracks', {}).get('items', []):
                artists = ', '.join([a['name'] for a in track.get('artists', [])])
                songs.append({
                    'title': track.get('name', ''),
                    'artist': artists,
                    'album': track.get('album', {}).get('name', ''),
                    'url': track.get('external_urls', {}).get('spotify', ''),
                    'preview_url': track.get('preview_url'),
                    'duration': track.get('duration_ms', 0) // 1000,
                    'source': 'Spotify'
                })

            return songs

        except Exception as e:
            logger.warning(f"Spotify search failed: {e}")
            return []

    def _search_youtube_music(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """Search YouTube for music videos."""

        if not self.youtube_music_available:
            return []

        try:
            from youtubesearchpython import VideosSearch

            # Add "music" or "song" to query for better results
            music_query = f"{query} official music video OR {query} song"

            search = VideosSearch(music_query, limit=limit)
            results = search.result()

            songs = []
            for video in results.get('result', []):
                songs.append({
                    'title': video.get('title', ''),
                    'artist': video.get('channel', {}).get('name', ''),
                    'url': video.get('link', ''),
                    'duration': video.get('duration', ''),
                    'thumbnail': video.get('thumbnails', [{}])[0].get('url') if video.get('thumbnails') else None,
                    'source': 'YouTube Music'
                })

            return songs

        except Exception as e:
            logger.warning(f"YouTube music search failed: {e}")
            return []

    def _select_best_song(self, songs: list[dict], point: RoutePoint) -> dict | None:
        """Use LLM to select the most relevant song."""

        if not songs:
            return None

        location = point.location_name or point.address

        # Create song list for LLM
        song_list = "\n".join([
            f"{i+1}. \"{s['title']}\" by {s.get('artist', 'Unknown')}"
            for i, s in enumerate(songs[:5])
        ])

        prompt = f"""Select the BEST song for a traveler passing through this location.

Location: {location}

Available Songs:
{song_list}

Consider:
1. Direct connection to the location (lyrics, artist origin)
2. Cultural or historical significance
3. Mood appropriateness for travel
4. Recognition/popularity

Respond with:
- The number of the best song (1-{len(songs[:5])})
- A relevance score from 0-10
- Brief reason for selection

Format:
SONG: [number]
SCORE: [0-10]
REASON: [one sentence]"""

        try:
            response = self._call_llm(prompt)

            # Parse response
            song_match = re.search(r'SONG:\s*(\d+)', response)
            score_match = re.search(r'SCORE:\s*([\d.]+)', response)
            reason_match = re.search(r'REASON:\s*(.+)', response)

            if song_match:
                idx = int(song_match.group(1)) - 1
                if 0 <= idx < len(songs):
                    selected = songs[idx].copy()
                    selected['relevance_score'] = float(score_match.group(1)) if score_match else 5.0
                    selected['selection_reason'] = reason_match.group(1) if reason_match else ""
                    return selected
        except Exception as e:
            logger.warning(f"Song selection failed: {e}")

        # Fallback: return first song
        if songs:
            songs[0]['relevance_score'] = 5.0
            return songs[0]

        return None

    def _get_mock_result(self, point: RoutePoint) -> ContentResult:
        """Return mock result for testing."""
        location = point.location_name or point.address

        # Some realistic mock songs for Israeli locations
        mock_songs = {
            "Ammunition Hill": {
                "title": "Givat HaTachmoshet (Ammunition Hill)",
                "artist": "Yehoram Gaon",
                "url": "https://www.youtube.com/watch?v=ammunition_hill"
            },
            "Tel Aviv": {
                "title": "Tel Aviv",
                "artist": "Omer Adam",
                "url": "https://www.youtube.com/watch?v=telaviv"
            },
            "Jerusalem": {
                "title": "Jerusalem of Gold (Yerushalayim Shel Zahav)",
                "artist": "Naomi Shemer",
                "url": "https://www.youtube.com/watch?v=jerusalem_gold"
            },
            "Latrun": {
                "title": "In the Fields of the Land",
                "artist": "HaGashash HaHiver",
                "url": "https://www.youtube.com/watch?v=latrun"
            }
        }

        # Find matching mock or create generic one
        mock = None
        for key, song in mock_songs.items():
            if key in location or key in point.address:
                mock = song
                break

        if not mock:
            mock = {
                "title": f"Song About {location}",
                "artist": "Israeli Artist",
                "url": f"https://www.youtube.com/watch?v=mock_{point.id}"
            }

        return ContentResult(
            point_id=point.id,
            content_type=ContentType.MUSIC,
            title=mock["title"],
            description=f"by {mock['artist']}",
            url=mock["url"],
            source="YouTube Music (Mock)",
            relevance_score=7.0,
            metadata={'artist': mock['artist'], 'mock': True}
        )

