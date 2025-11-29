"""
Unit tests for Agent modules.

Tests cover:
- VideoAgent initialization and search
- MusicAgent initialization and search
- TextAgent initialization and search
- JudgeAgent evaluation logic
- Mock content generation
- LLM call mocking

MIT Level Testing - 85%+ Coverage Target
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import re

from src.models.route import RoutePoint
from src.models.content import ContentResult, ContentType
from src.models.decision import JudgeDecision
from src.models.user_profile import UserProfile, AgeGroup, Gender


class TestVideoAgent:
    """Tests for VideoAgent class."""
    
    @patch('src.agents.video_agent.AGENT_SKILLS', {'video_agent': {'search_preferences': []}})
    def test_initialization(self):
        """Test VideoAgent initialization."""
        from src.agents.video_agent import VideoAgent
        
        agent = VideoAgent()
        assert agent.agent_type == "video"
    
    @patch('src.agents.video_agent.AGENT_SKILLS', {'video_agent': {'search_preferences': []}})
    def test_get_content_type(self):
        """Test content type is VIDEO."""
        from src.agents.video_agent import VideoAgent
        
        agent = VideoAgent()
        assert agent.get_content_type() == ContentType.VIDEO
    
    @patch('src.agents.video_agent.AGENT_SKILLS', {'video_agent': {'search_preferences': []}})
    def test_get_mock_result(self, mock_route_point):
        """Test mock result generation."""
        from src.agents.video_agent import VideoAgent
        
        agent = VideoAgent()
        result = agent._get_mock_result(mock_route_point)
        
        assert isinstance(result, ContentResult)
        assert result.content_type == ContentType.VIDEO
        assert result.point_id == mock_route_point.id
        assert result.source == "YouTube (Mock)"
    
    @patch('src.agents.video_agent.AGENT_SKILLS', {'video_agent': {'search_preferences': []}})
    def test_mock_result_ammunition_hill(self):
        """Test mock result for Ammunition Hill location."""
        from src.agents.video_agent import VideoAgent
        
        point = RoutePoint(
            id="ammo_hill",
            index=0,
            address="Ammunition Hill, Jerusalem",
            location_name="Ammunition Hill",
            latitude=31.7944,
            longitude=35.2283
        )
        
        agent = VideoAgent()
        result = agent._get_mock_result(point)
        
        # Should match the predefined mock for Ammunition Hill
        assert "Ammunition" in result.title or "Battle" in result.title or "ammo_hill" in result.url
    
    @patch('src.agents.video_agent.AGENT_SKILLS', {'video_agent': {'search_preferences': []}})
    def test_generate_search_queries_fallback(self, mock_route_point):
        """Test search query generation fallback."""
        from src.agents.video_agent import VideoAgent
        
        agent = VideoAgent()
        
        # Mock LLM to fail
        with patch.object(agent, '_call_llm', side_effect=Exception("LLM Error")):
            queries = agent._generate_search_queries(mock_route_point)
        
        assert len(queries) >= 2
        assert any("Ammunition Hill" in q for q in queries)


class TestMusicAgent:
    """Tests for MusicAgent class."""
    
    def test_initialization(self):
        """Test MusicAgent initialization."""
        from src.agents.music_agent import MusicAgent
        
        with patch.object(MusicAgent, '_init_music_clients'):
            agent = MusicAgent()
            assert agent.agent_type == "music"
    
    def test_get_content_type(self):
        """Test content type is MUSIC."""
        from src.agents.music_agent import MusicAgent
        
        with patch.object(MusicAgent, '_init_music_clients'):
            agent = MusicAgent()
            assert agent.get_content_type() == ContentType.MUSIC
    
    def test_get_mock_result(self, mock_route_point):
        """Test mock result generation."""
        from src.agents.music_agent import MusicAgent
        
        with patch.object(MusicAgent, '_init_music_clients'):
            agent = MusicAgent()
            result = agent._get_mock_result(mock_route_point)
        
        assert isinstance(result, ContentResult)
        assert result.content_type == ContentType.MUSIC
        assert result.point_id == mock_route_point.id
    
    def test_mock_result_jerusalem(self):
        """Test mock result for Jerusalem location."""
        from src.agents.music_agent import MusicAgent
        
        point = RoutePoint(
            id="jerusalem",
            index=0,
            address="Old City, Jerusalem",
            location_name="Jerusalem",
            latitude=31.7767,
            longitude=35.2345
        )
        
        with patch.object(MusicAgent, '_init_music_clients'):
            agent = MusicAgent()
            result = agent._get_mock_result(point)
        
        # Should contain Jerusalem of Gold or similar
        assert "Jerusalem" in result.title or "Yerushalayim" in result.title
    
    def test_search_spotify_no_client(self, mock_route_point):
        """Test Spotify search returns empty when no client."""
        from src.agents.music_agent import MusicAgent
        
        with patch.object(MusicAgent, '_init_music_clients'):
            agent = MusicAgent()
            agent.spotify_client = None
            
            results = agent._search_spotify("test query")
            assert results == []
    
    def test_search_youtube_music_not_available(self, mock_route_point):
        """Test YouTube music search when not available."""
        from src.agents.music_agent import MusicAgent
        
        with patch.object(MusicAgent, '_init_music_clients'):
            agent = MusicAgent()
            agent.youtube_music_available = False
            
            results = agent._search_youtube_music("test query")
            assert results == []
    
    def test_select_best_song_empty_list(self, mock_route_point):
        """Test song selection with empty list."""
        from src.agents.music_agent import MusicAgent
        
        with patch.object(MusicAgent, '_init_music_clients'):
            agent = MusicAgent()
            
            result = agent._select_best_song([], mock_route_point)
            assert result is None
    
    def test_select_best_song_fallback(self, mock_route_point):
        """Test song selection fallback when LLM fails."""
        from src.agents.music_agent import MusicAgent
        
        songs = [
            {'title': 'Song 1', 'artist': 'Artist 1', 'url': 'http://example.com/1'},
            {'title': 'Song 2', 'artist': 'Artist 2', 'url': 'http://example.com/2'},
        ]
        
        with patch.object(MusicAgent, '_init_music_clients'):
            agent = MusicAgent()
            
            with patch.object(agent, '_call_llm', side_effect=Exception("LLM Error")):
                result = agent._select_best_song(songs, mock_route_point)
        
        assert result is not None
        assert result['title'] == 'Song 1'
        assert result['relevance_score'] == 5.0


class TestTextAgent:
    """Tests for TextAgent class."""
    
    def test_initialization(self):
        """Test TextAgent initialization."""
        from src.agents.text_agent import TextAgent
        
        with patch.object(TextAgent, '_init_search_client'):
            agent = TextAgent()
            assert agent.agent_type == "text"
    
    def test_get_content_type(self):
        """Test content type is TEXT."""
        from src.agents.text_agent import TextAgent
        
        with patch.object(TextAgent, '_init_search_client'):
            agent = TextAgent()
            assert agent.get_content_type() == ContentType.TEXT
    
    def test_get_mock_result(self, mock_route_point):
        """Test mock result generation."""
        from src.agents.text_agent import TextAgent
        
        with patch.object(TextAgent, '_init_search_client'):
            agent = TextAgent()
            result = agent._get_mock_result(mock_route_point)
        
        assert isinstance(result, ContentResult)
        assert result.content_type == ContentType.TEXT
        assert result.point_id == mock_route_point.id
    
    def test_mock_result_latrun(self):
        """Test mock result for Latrun location."""
        from src.agents.text_agent import TextAgent
        
        point = RoutePoint(
            id="latrun",
            index=0,
            address="Latrun, Israel",
            location_name="Latrun",
            latitude=31.8389,
            longitude=34.9783
        )
        
        with patch.object(TextAgent, '_init_search_client'):
            agent = TextAgent()
            result = agent._get_mock_result(point)
        
        # Should contain Latrun-related content
        assert "Latrun" in result.title or "Monks" in result.title
    
    def test_extract_domain(self):
        """Test domain extraction from URL."""
        from src.agents.text_agent import TextAgent
        
        with patch.object(TextAgent, '_init_search_client'):
            agent = TextAgent()
        
        domain = agent._extract_domain("https://www.example.com/path/to/page")
        assert domain == "example.com"
        
        domain = agent._extract_domain("http://subdomain.example.org")
        assert domain == "subdomain.example.org"
    
    def test_extract_domain_invalid(self):
        """Test domain extraction with invalid URL."""
        from src.agents.text_agent import TextAgent
        
        with patch.object(TextAgent, '_init_search_client'):
            agent = TextAgent()
        
        result = agent._extract_domain("not a url")
        assert result == "not a url"
    
    def test_search_web_no_client(self, mock_route_point):
        """Test web search returns empty when no client."""
        from src.agents.text_agent import TextAgent
        
        with patch.object(TextAgent, '_init_search_client'):
            agent = TextAgent()
            agent.search_available = False
            
            results = agent._search_web("test query")
            assert results == []
    
    def test_synthesize_content_empty_results(self, mock_route_point):
        """Test content synthesis with empty results."""
        from src.agents.text_agent import TextAgent
        
        with patch.object(TextAgent, '_init_search_client'):
            agent = TextAgent()
            
            result = agent._synthesize_content([], mock_route_point)
            assert result is None


class TestJudgeAgent:
    """Tests for JudgeAgent class."""
    
    @patch('src.agents.judge_agent.AGENT_SKILLS', {
        'judge_agent': {'scoring_criteria': ['relevance', 'quality', 'engagement']}
    })
    def test_initialization(self):
        """Test JudgeAgent initialization."""
        from src.agents.judge_agent import JudgeAgent
        
        agent = JudgeAgent()
        assert agent.agent_type == "judge"
        assert agent.user_profile is not None
    
    @patch('src.agents.judge_agent.AGENT_SKILLS', {
        'judge_agent': {'scoring_criteria': ['relevance', 'quality', 'engagement']}
    })
    def test_initialization_with_profile(self, adult_profile):
        """Test JudgeAgent initialization with user profile."""
        from src.agents.judge_agent import JudgeAgent
        
        agent = JudgeAgent(user_profile=adult_profile)
        assert agent.user_profile == adult_profile
    
    @patch('src.agents.judge_agent.AGENT_SKILLS', {
        'judge_agent': {'scoring_criteria': ['relevance', 'quality', 'engagement']}
    })
    def test_get_content_type(self):
        """Test default content type is TEXT."""
        from src.agents.judge_agent import JudgeAgent
        
        agent = JudgeAgent()
        assert agent.get_content_type() == ContentType.TEXT
    
    @patch('src.agents.judge_agent.AGENT_SKILLS', {
        'judge_agent': {'scoring_criteria': ['relevance', 'quality', 'engagement']}
    })
    def test_search_content_returns_none(self, mock_route_point):
        """Test _search_content returns None (judge doesn't search)."""
        from src.agents.judge_agent import JudgeAgent
        
        agent = JudgeAgent()
        result = agent._search_content(mock_route_point)
        assert result is None
    
    @patch('src.agents.judge_agent.AGENT_SKILLS', {
        'judge_agent': {'scoring_criteria': ['relevance', 'quality', 'engagement']}
    })
    @patch('src.agents.judge_agent.log_judge_decision')
    def test_evaluate_single_candidate(
        self, mock_log, mock_route_point, mock_text_result
    ):
        """Test evaluation with single candidate."""
        from src.agents.judge_agent import JudgeAgent
        
        agent = JudgeAgent()
        mock_text_result.point_id = mock_route_point.id
        
        decision = agent.evaluate(mock_route_point, [mock_text_result])
        
        assert isinstance(decision, JudgeDecision)
        assert decision.selected_content == mock_text_result
        assert "Only" in decision.reasoning
    
    @patch('src.agents.judge_agent.AGENT_SKILLS', {
        'judge_agent': {'scoring_criteria': ['relevance', 'quality', 'engagement']}
    })
    def test_evaluate_no_candidates_raises(self, mock_route_point):
        """Test evaluation raises error with no candidates."""
        from src.agents.judge_agent import JudgeAgent
        
        agent = JudgeAgent()
        
        with pytest.raises(ValueError, match="No candidates"):
            agent.evaluate(mock_route_point, [])
    
    @patch('src.agents.judge_agent.AGENT_SKILLS', {
        'judge_agent': {'scoring_criteria': ['relevance', 'quality', 'engagement']}
    })
    @patch('src.agents.judge_agent.log_judge_decision')
    def test_evaluate_two_candidates(
        self, mock_log, mock_route_point, mock_video_result, mock_music_result
    ):
        """Test evaluation with two candidates."""
        from src.agents.judge_agent import JudgeAgent
        
        agent = JudgeAgent()
        mock_video_result.point_id = mock_route_point.id
        mock_music_result.point_id = mock_route_point.id
        
        # Mock LLM to avoid actual calls
        with patch.object(agent, '_call_llm', return_value="WINNER: 1\nWINNER_SCORE: 8.5\nREASONING: Video is best"):
            decision = agent.evaluate(
                mock_route_point, 
                [mock_video_result, mock_music_result]
            )
        
        assert isinstance(decision, JudgeDecision)
        assert len(decision.all_candidates) == 2
    
    @patch('src.agents.judge_agent.AGENT_SKILLS', {
        'judge_agent': {'scoring_criteria': ['relevance', 'quality', 'engagement']}
    })
    @patch('src.agents.judge_agent.log_judge_decision')
    def test_evaluate_three_candidates(
        self, mock_log, mock_route_point, 
        mock_video_result, mock_music_result, mock_text_result
    ):
        """Test evaluation with three candidates."""
        from src.agents.judge_agent import JudgeAgent
        
        agent = JudgeAgent()
        for result in [mock_video_result, mock_music_result, mock_text_result]:
            result.point_id = mock_route_point.id
        
        llm_response = """SCORES:
- Video: 8.0
- Music: 7.5
- Text: 9.0

WINNER: 3
WINNER_SCORE: 9.0
REASONING: Text provides best educational value"""
        
        with patch.object(agent, '_call_llm', return_value=llm_response):
            decision = agent.evaluate(
                mock_route_point, 
                [mock_video_result, mock_music_result, mock_text_result]
            )
        
        assert isinstance(decision, JudgeDecision)
        assert decision.selected_content == mock_text_result
    
    @patch('src.agents.judge_agent.AGENT_SKILLS', {
        'judge_agent': {'scoring_criteria': ['relevance', 'quality', 'engagement']}
    })
    def test_quick_evaluate_single_candidate(self, mock_route_point, mock_text_result):
        """Test quick evaluation with single candidate."""
        from src.agents.judge_agent import JudgeAgent
        
        agent = JudgeAgent()
        mock_text_result.point_id = mock_route_point.id
        
        result = agent.quick_evaluate(mock_route_point, [mock_text_result])
        assert result == mock_text_result
    
    @patch('src.agents.judge_agent.AGENT_SKILLS', {
        'judge_agent': {'scoring_criteria': ['relevance', 'quality', 'engagement']}
    })
    def test_quick_evaluate_no_candidates_raises(self, mock_route_point):
        """Test quick evaluation raises with no candidates."""
        from src.agents.judge_agent import JudgeAgent
        
        agent = JudgeAgent()
        
        with pytest.raises(ValueError, match="No candidates"):
            agent.quick_evaluate(mock_route_point, [])
    
    @patch('src.agents.judge_agent.AGENT_SKILLS', {
        'judge_agent': {'scoring_criteria': ['relevance', 'quality', 'engagement']}
    })
    def test_quick_evaluate_location_boost(self, mock_route_point, mock_text_result):
        """Test quick evaluation gives boost for location in title."""
        from src.agents.judge_agent import JudgeAgent
        
        agent = JudgeAgent()
        mock_text_result.point_id = mock_route_point.id
        mock_text_result.title = "History of Ammunition Hill"  # Contains location name
        
        video_result = ContentResult(
            point_id=mock_route_point.id,
            content_type=ContentType.VIDEO,
            title="Generic Documentary",
            source="YouTube",
            relevance_score=8.0
        )
        
        result = agent.quick_evaluate(mock_route_point, [video_result, mock_text_result])
        
        # Text should win due to location boost
        assert result.content_type == ContentType.TEXT
    
    @patch('src.agents.judge_agent.AGENT_SKILLS', {
        'judge_agent': {'scoring_criteria': ['relevance', 'quality', 'engagement']}
    })
    def test_generate_single_candidate_reasoning(self, mock_text_result, adult_profile):
        """Test reasoning generation for single candidate."""
        from src.agents.judge_agent import JudgeAgent
        
        agent = JudgeAgent(user_profile=adult_profile)
        
        reasoning = agent._generate_single_candidate_reasoning(mock_text_result, adult_profile)
        
        assert "Only" in reasoning
        assert "text" in reasoning.lower()
    
    @patch('src.agents.judge_agent.AGENT_SKILLS', {
        'judge_agent': {'scoring_criteria': ['relevance', 'quality', 'engagement']}
    })
    def test_parse_evaluation_response_valid(self):
        """Test parsing valid LLM response."""
        from src.agents.judge_agent import JudgeAgent
        
        agent = JudgeAgent()
        
        response = """SCORES:
- Video: 8.5
- Music: 7.0
- Text: 9.2

WINNER: 3
WINNER_SCORE: 9.2
REASONING: Text provides comprehensive historical context."""
        
        candidates = [
            ContentResult(point_id="p1", content_type=ContentType.VIDEO, title="V", source="Y"),
            ContentResult(point_id="p1", content_type=ContentType.MUSIC, title="M", source="S"),
            ContentResult(point_id="p1", content_type=ContentType.TEXT, title="T", source="W"),
        ]
        
        result = agent._parse_evaluation_response(response, candidates)
        
        assert result['winner_index'] == 2  # 3-1 = 2
        assert result['winner_score'] == 9.2
        assert ContentType.VIDEO in result['scores']
        assert result['scores'][ContentType.VIDEO] == 8.5
    
    @patch('src.agents.judge_agent.AGENT_SKILLS', {
        'judge_agent': {'scoring_criteria': ['relevance', 'quality', 'engagement']}
    })
    def test_parse_evaluation_response_invalid(self):
        """Test parsing invalid LLM response."""
        from src.agents.judge_agent import JudgeAgent
        
        agent = JudgeAgent()
        
        response = "This is not a valid response format"
        candidates = []
        
        result = agent._parse_evaluation_response(response, candidates)
        
        # Should return defaults
        assert result['winner_index'] == 0
        assert result['scores'] == {}
    
    @patch('src.agents.judge_agent.AGENT_SKILLS', {
        'judge_agent': {'scoring_criteria': ['relevance', 'quality', 'engagement']}
    })
    def test_fallback_two_candidate_selection(self, mock_video_result, mock_music_result, adult_profile):
        """Test fallback selection for two candidates."""
        from src.agents.judge_agent import JudgeAgent
        
        agent = JudgeAgent(user_profile=adult_profile)
        
        type_preferences = {'video': 1.2, 'music': 0.9}
        
        result = agent._fallback_two_candidate_selection(
            [mock_video_result, mock_music_result],
            type_preferences
        )
        
        assert 'winner_index' in result
        assert 'winner_score' in result
        assert 'reasoning' in result

