#!/usr/bin/env python3
"""
Multi-Agent Tour Guide System - Entry Point

A production-grade multi-agent system for creating intelligent tour guides.
Uses parallel processing, queue-based synchronization, and plugin architecture.

Usage:
    python main.py                                    # Interactive mode
    python main.py --demo                             # Demo with mock data
    python main.py --origin "Tel Aviv" --dest "Jerusalem"
    python main.py --demo --mode streaming           # Streaming mode
    python main.py --demo --profile family           # Family-friendly content
"""

# ============================================================================
# WARNINGS SUPPRESSION (must be at the very top, before any other imports)
# ============================================================================
# Suppress known third-party library warnings:
# 1. DuckDuckGo search package rename warning (RuntimeWarning)
# 2. Unclosed SSL sockets from HTTP clients like anthropic/httpx (ResourceWarning)
import warnings

# Suppress ResourceWarnings (unclosed sockets)
warnings.simplefilter("ignore", ResourceWarning)

# Suppress the specific DuckDuckGo rename warning
# The library raises this with stacklevel=2 so it appears from our code
warnings.filterwarnings(
    "ignore",
    message=".*has been renamed.*",
    category=RuntimeWarning,
    module=".*text_agent.*",
)
warnings.filterwarnings(
    "ignore",
    message=".*duckduckgo.*",
    category=RuntimeWarning,
)
# ============================================================================

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.cli.main import main

if __name__ == "__main__":
    sys.exit(main())
