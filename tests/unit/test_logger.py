"""
Unit tests for logger module.

Tests cover:
- Context setting and clearing
- Log helper functions
"""

from src.utils.logger import (
    clear_log_context,
    log_agent_error,
    log_agent_result,
    log_agent_start,
    log_judge_decision,
    set_log_context,
)


class TestLogContext:
    """Tests for log context functions."""

    def test_set_log_context(self):
        """Test setting log context."""
        set_log_context(point_id="p1", agent_type="video")
        # No assertion needed - just verifying no exception

    def test_clear_log_context(self):
        """Test clearing log context."""
        set_log_context(point_id="p1", agent_type="video")
        clear_log_context()
        # No assertion needed - just verifying no exception


class TestLogHelpers:
    """Tests for log helper functions."""

    def test_log_agent_start(self):
        """Test logging agent start."""
        log_agent_start("video", "p1", "Test Location")

    def test_log_agent_result(self):
        """Test logging agent result."""
        log_agent_result("video", "p1", "Found 5 results")

    def test_log_agent_error(self):
        """Test logging agent error."""
        log_agent_error("video", "p1", "Connection timeout")

    def test_log_judge_decision(self):
        """Test logging judge decision."""
        log_judge_decision("p1", "video", "Best quality content")
