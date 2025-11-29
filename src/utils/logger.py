"""
Logging setup with colored console output.
Provides thread-safe logging for the multi-agent system.
"""
import logging
import sys
import threading

# Thread-local storage for context
_thread_local = threading.local()

# Try to import rich for colored output
try:
    from rich.console import Console
    from rich.logging import RichHandler
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


def set_log_context(point_id: str | None = None, agent_type: str | None = None):
    """Set logging context for the current thread."""
    if point_id is not None:
        _thread_local.point_id = point_id
    if agent_type is not None:
        _thread_local.agent_type = agent_type


def clear_log_context():
    """Clear logging context for the current thread."""
    _thread_local.point_id = '-'
    _thread_local.agent_type = '-'


class ContextFilter(logging.Filter):
    """Add context information to log records."""

    def filter(self, record):
        record.thread_name = threading.current_thread().name
        record.point_id = getattr(_thread_local, 'point_id', '-')
        record.agent_type = getattr(_thread_local, 'agent_type', '-')
        record.context = f"[{record.point_id}][{record.agent_type}]"
        return True


def get_logger(name: str = "tour_guide") -> logging.Logger:
    """
    Get a configured logger.

    Args:
        name: Logger name

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Add context filter
    context_filter = ContextFilter()
    logger.addFilter(context_filter)

    # Console handler
    if HAS_RICH:
        console = Console()
        handler = RichHandler(
            console=console,
            show_time=True,
            show_path=False,
        )
    else:
        handler = logging.StreamHandler(sys.stdout)

    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(context)s %(message)s")
    handler.setFormatter(formatter)
    handler.addFilter(context_filter)
    logger.addHandler(handler)

    return logger


# Default logger instance
logger = get_logger()


def log_agent_start(agent_type: str, point_id: str, location: str):
    """Log when an agent starts working."""
    set_log_context(point_id=point_id, agent_type=agent_type)
    logger.info(f"🚀 Starting {agent_type} agent for location: {location}")


def log_agent_result(agent_type: str, point_id: str, result_summary: str):
    """Log agent result."""
    set_log_context(point_id=point_id, agent_type=agent_type)
    logger.info(f"✅ {agent_type} agent completed: {result_summary}")


def log_agent_error(agent_type: str, point_id: str, error: str):
    """Log agent error."""
    set_log_context(point_id=point_id, agent_type=agent_type)
    logger.error(f"❌ {agent_type} agent error: {error}")


def log_judge_decision(point_id: str, winner: str, reason: str):
    """Log judge's decision."""
    set_log_context(point_id=point_id, agent_type='judge')
    logger.info(f"⚖️ Judge selected: {winner} - Reason: {reason}")

