"""
Logging setup with colored console output and file logging.
Provides thread-safe logging for the multi-agent system.
"""
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
import threading

from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme

from config import settings

# Thread-local storage for context
_thread_local = threading.local()

# Custom theme for rich console
CUSTOM_THEME = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red bold",
    "critical": "red bold reverse",
    "agent.video": "magenta",
    "agent.music": "green",
    "agent.text": "blue",
    "agent.judge": "yellow bold",
    "orchestrator": "cyan bold",
    "timer": "white",
    "collector": "green bold",
    "route": "bright_blue",
})

console = Console(theme=CUSTOM_THEME)


class ContextFilter(logging.Filter):
    """Add context information to log records."""
    
    def filter(self, record):
        # Add thread name
        record.thread_name = threading.current_thread().name
        
        # Add point ID if available
        record.point_id = getattr(_thread_local, 'point_id', '-')
        
        # Add agent type if available
        record.agent_type = getattr(_thread_local, 'agent_type', '-')
        
        return True


def set_log_context(point_id: Optional[str] = None, agent_type: Optional[str] = None):
    """Set logging context for the current thread."""
    if point_id is not None:
        _thread_local.point_id = point_id
    if agent_type is not None:
        _thread_local.agent_type = agent_type


def clear_log_context():
    """Clear logging context for the current thread."""
    _thread_local.point_id = '-'
    _thread_local.agent_type = '-'


class AgentFormatter(logging.Formatter):
    """Custom formatter with agent and point context."""
    
    def format(self, record):
        # Add color coding based on agent type
        agent_colors = {
            'video': '\033[35m',      # Magenta
            'music': '\033[32m',      # Green
            'text': '\033[34m',       # Blue
            'judge': '\033[33m',      # Yellow
            'orchestrator': '\033[36m', # Cyan
            'timer': '\033[37m',      # White
            'collector': '\033[32m',  # Green
        }
        reset = '\033[0m'
        
        agent_type = getattr(record, 'agent_type', '-')
        color = agent_colors.get(agent_type, '')
        
        # Add context to message
        point_id = getattr(record, 'point_id', '-')
        thread_name = getattr(record, 'thread_name', '-')
        
        record.context = f"[Point:{point_id}][Agent:{agent_type}][Thread:{thread_name}]"
        
        return super().format(record)


def setup_logger(name: str = "tour_guide") -> logging.Logger:
    """
    Setup and return a configured logger.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Add context filter
    context_filter = ContextFilter()
    logger.addFilter(context_filter)
    
    # Console handler with Rich
    console_handler = RichHandler(
        console=console,
        show_time=True,
        show_path=False,
        rich_tracebacks=True,
        tracebacks_show_locals=True,
    )
    console_handler.setLevel(logging.DEBUG)
    console_format = logging.Formatter(
        "%(context)s %(message)s",
        datefmt="[%X]"
    )
    console_handler.setFormatter(AgentFormatter(
        "%(context)s %(message)s"
    ))
    logger.addHandler(console_handler)
    
    # File handler
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"{settings.log_file.replace('.log', '')}_{timestamp}.log"
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_format = AgentFormatter(
        "%(asctime)s | %(levelname)-8s | %(context)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_format)
    file_handler.addFilter(context_filter)
    logger.addHandler(file_handler)
    
    logger.info(f"Logger initialized. Log file: {log_file}")
    
    return logger


# Create default logger
logger = setup_logger()


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


def log_orchestrator_event(event: str, details: str = ""):
    """Log orchestrator events."""
    set_log_context(agent_type='orchestrator')
    logger.info(f"🎭 Orchestrator: {event} {details}")


def log_timer_tick(point_id: str, location: str):
    """Log timer tick for new point."""
    set_log_context(point_id=point_id, agent_type='timer')
    logger.info(f"⏱️ Timer: New point reached - {location}")


def log_collector_update(point_id: str, content_type: str):
    """Log collector receiving content."""
    set_log_context(point_id=point_id, agent_type='collector')
    logger.info(f"📥 Collector: Received {content_type} content for point {point_id}")

