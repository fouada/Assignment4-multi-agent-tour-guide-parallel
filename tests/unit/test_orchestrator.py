"""
Unit tests for the Orchestrator module.

Tests cover:
- PointProcessor initialization and execution
- Orchestrator lifecycle (start, stop)
- Processing single and multiple points
- Result collection and ordering
- Statistics tracking
- StreamingOrchestrator functionality

MIT Level Testing - 85%+ Coverage Target
"""
import pytest
import threading
import time
import sys
from unittest.mock import Mock, patch, MagicMock
from concurrent.futures import Future

from src.models.route import RoutePoint
from src.models.content import ContentResult, ContentType
from src.models.decision import JudgeDecision


# Mock the logger functions that may not exist
@pytest.fixture(autouse=True)
def mock_logger_functions():
    """Mock all logger functions used in orchestrator."""
    with patch.dict(sys.modules, {
        'src.core.orchestrator': MagicMock()
    }):
        # Import the module fresh with mocks
        import importlib
        from src.core import orchestrator
        
        # Add missing functions if they don't exist
        if not hasattr(orchestrator, 'set_log_context'):
            orchestrator.set_log_context = Mock()
        if not hasattr(orchestrator, 'log_orchestrator_event'):
            orchestrator.log_orchestrator_event = Mock()
        
        yield


class TestPointProcessor:
    """Tests for PointProcessor class."""
    
    def test_initialization(self, mock_route_point):
        """Test PointProcessor initialization."""
        # Import directly and mock what we need
        with patch('src.core.orchestrator.set_log_context', create=True):
            with patch('src.core.orchestrator.log_orchestrator_event', create=True):
                from src.core.orchestrator import PointProcessor
                
                callback = Mock()
                processor = PointProcessor(mock_route_point, callback)
                
                assert processor.point == mock_route_point
                assert processor.result_callback == callback
                assert processor.content_results == []
                assert processor.decision is None
                assert processor.started_at is None
                assert processor.completed_at is None
                assert not processor.completed.is_set()
    
    def test_lock_exists(self, mock_route_point):
        """Test that processor has a thread lock."""
        with patch('src.core.orchestrator.set_log_context', create=True):
            with patch('src.core.orchestrator.log_orchestrator_event', create=True):
                from src.core.orchestrator import PointProcessor
                
                processor = PointProcessor(mock_route_point, Mock())
                assert isinstance(processor.lock, type(threading.Lock()))
    
    def test_run_agent_returns_none_on_error(self, mock_route_point):
        """Test _run_agent returns None on exception."""
        with patch('src.core.orchestrator.set_log_context', create=True):
            with patch('src.core.orchestrator.log_orchestrator_event', create=True):
                from src.core.orchestrator import PointProcessor
                
                processor = PointProcessor(mock_route_point, Mock())
                
                mock_agent = Mock()
                mock_agent.execute.side_effect = Exception("Agent error")
                
                result = processor._run_agent(mock_agent)
                assert result is None


class TestOrchestrator:
    """Tests for Orchestrator class."""
    
    def test_initialization_default(self):
        """Test Orchestrator initialization with defaults."""
        with patch('src.core.orchestrator.set_log_context', create=True):
            with patch('src.core.orchestrator.log_orchestrator_event', create=True):
                from src.core.orchestrator import Orchestrator
                
                orchestrator = Orchestrator()
                
                assert orchestrator.max_concurrent_points is not None
                assert orchestrator.active_processors == {}
                assert orchestrator.results == {}
                assert orchestrator.executor is None
                assert not orchestrator.is_running
    
    def test_initialization_custom_workers(self):
        """Test Orchestrator initialization with custom workers."""
        with patch('src.core.orchestrator.set_log_context', create=True):
            with patch('src.core.orchestrator.log_orchestrator_event', create=True):
                from src.core.orchestrator import Orchestrator
                
                orchestrator = Orchestrator(max_concurrent_points=5)
                assert orchestrator.max_concurrent_points == 5
    
    def test_start_stop_lifecycle(self):
        """Test start and stop lifecycle."""
        with patch('src.core.orchestrator.set_log_context', create=True):
            with patch('src.core.orchestrator.log_orchestrator_event', create=True):
                from src.core.orchestrator import Orchestrator
                
                orchestrator = Orchestrator(max_concurrent_points=2)
                
                # Initially not running
                assert not orchestrator.is_running
                
                # Start
                orchestrator.start()
                assert orchestrator.is_running
                assert orchestrator.executor is not None
                
                # Stop
                orchestrator.stop()
                assert not orchestrator.is_running
    
    def test_get_stats(self):
        """Test statistics retrieval."""
        with patch('src.core.orchestrator.set_log_context', create=True):
            with patch('src.core.orchestrator.log_orchestrator_event', create=True):
                from src.core.orchestrator import Orchestrator
                
                orchestrator = Orchestrator(max_concurrent_points=2)
                
                stats = orchestrator.get_stats()
                
                assert 'active_points' in stats
                assert 'completed_points' in stats
                assert 'pending_points' in stats
                assert 'is_running' in stats
    
    def test_get_result_not_found(self):
        """Test getting result for non-existent point."""
        with patch('src.core.orchestrator.set_log_context', create=True):
            with patch('src.core.orchestrator.log_orchestrator_event', create=True):
                from src.core.orchestrator import Orchestrator
                
                orchestrator = Orchestrator()
                result = orchestrator.get_result("non_existent")
                assert result is None
    
    def test_get_next_result_empty(self):
        """Test getting next result from empty queue."""
        with patch('src.core.orchestrator.set_log_context', create=True):
            with patch('src.core.orchestrator.log_orchestrator_event', create=True):
                from src.core.orchestrator import Orchestrator
                
                orchestrator = Orchestrator()
                result = orchestrator.get_next_result(timeout=0.1)
                assert result is None
    
    def test_on_point_complete_callback(self):
        """Test internal callback updates results."""
        with patch('src.core.orchestrator.set_log_context', create=True):
            with patch('src.core.orchestrator.log_orchestrator_event', create=True):
                from src.core.orchestrator import Orchestrator
                
                orchestrator = Orchestrator()
                
                mock_decision = Mock()
                mock_decision.point_id = "test_point"
                mock_decision.selected_content.title = "Test Title"
                
                orchestrator._on_point_complete(mock_decision)
                
                assert "test_point" in orchestrator.results
                assert orchestrator.results["test_point"] == mock_decision


class TestStreamingOrchestrator:
    """Tests for StreamingOrchestrator class."""
    
    def test_initialization(self):
        """Test StreamingOrchestrator initialization."""
        with patch('src.core.orchestrator.set_log_context', create=True):
            with patch('src.core.orchestrator.log_orchestrator_event', create=True):
                from src.core.orchestrator import StreamingOrchestrator
                
                orchestrator = StreamingOrchestrator()
                
                assert orchestrator._point_queue is not None
                assert orchestrator._processing_thread is None
                assert not orchestrator._should_stop.is_set()
    
    def test_add_point(self, mock_route_point):
        """Test adding point to queue."""
        with patch('src.core.orchestrator.set_log_context', create=True):
            with patch('src.core.orchestrator.log_orchestrator_event', create=True):
                from src.core.orchestrator import StreamingOrchestrator
                
                orchestrator = StreamingOrchestrator()
                
                orchestrator.add_point(mock_route_point)
                
                # Point should be in queue
                assert not orchestrator._point_queue.empty()
    
    def test_start_stop_streaming(self):
        """Test streaming start and stop."""
        with patch('src.core.orchestrator.set_log_context', create=True):
            with patch('src.core.orchestrator.log_orchestrator_event', create=True):
                from src.core.orchestrator import StreamingOrchestrator
                
                orchestrator = StreamingOrchestrator()
                
                orchestrator.start_streaming()
                
                assert orchestrator.is_running
                assert orchestrator._processing_thread is not None
                
                orchestrator.stop_streaming()
                
                assert not orchestrator.is_running
