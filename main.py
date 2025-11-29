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
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.cli.main import main

if __name__ == "__main__":
    sys.exit(main())
