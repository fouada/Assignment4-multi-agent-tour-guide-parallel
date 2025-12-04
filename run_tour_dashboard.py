#!/usr/bin/env python3
"""
🗺️ Multi-Agent Tour Guide - Interactive Dashboard Runner
==========================================================

Launch the comprehensive interactive dashboard for the Tour Guide system.

Features:
- Complete tour planning with source/destination inputs
- Full user profile configuration (family mode, age, preferences)
- Pipeline flow visualization
- Real-time agent monitoring
- Personalized content recommendations

API MODE STRATEGY (MIT-Level):
------------------------------
  --mode auto   : Try real APIs, fallback to mock (DEFAULT)
  --mode real   : Force real APIs - For Demo/Presentation
  --mode mock   : Use mocked data - For Testing/Development

Usage:
    python run_tour_dashboard.py                    # Default (auto mode)
    python run_tour_dashboard.py --mode real        # MIT Demo (real APIs)
    python run_tour_dashboard.py --mode mock        # Fast testing

Author: Multi-Agent Tour Guide Research Team
"""

import argparse
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))


def main():
    """Main entry point for the Tour Guide Dashboard."""
    parser = argparse.ArgumentParser(
        description="🗺️ Multi-Agent Tour Guide Interactive Dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
API Mode Strategy (MIT-Level):
==============================
  auto  : Try real APIs, fallback to mock if unavailable (DEFAULT)
  real  : Force real APIs - Use for Demo/Presentation
  mock  : Always use mocked data - Use for Testing/CI

Examples:
  uv run python run_tour_dashboard.py                    # Auto mode
  uv run python run_tour_dashboard.py --mode real        # MIT Demo (real APIs)
  uv run python run_tour_dashboard.py --mode mock        # Fast testing
  uv run python run_tour_dashboard.py --port 8080        # Custom port
  uv run python run_tour_dashboard.py --host 0.0.0.0     # Network accessible
        """,
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind the dashboard server (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8051,
        help="Port to run the dashboard server (default: 8051)",
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["auto", "real", "mock"],
        default="auto",
        help="API mode: auto (default), real (MIT demo), mock (testing)",
    )
    parser.add_argument(
        "--no-debug",
        action="store_true",
        help="Disable debug mode (for production)",
    )
    
    args = parser.parse_args()
    
    # Set API mode via environment variable
    os.environ["TOUR_GUIDE_API_MODE"] = args.mode
    
    # Print mode banner
    mode_info = {
        "auto": ("🔄 AUTO", "Real APIs with mock fallback"),
        "real": ("🔴 REAL", "Actual API calls (YouTube, Spotify, Claude)"),
        "mock": ("⚪ MOCK", "Fast mocked data (no API calls)"),
    }
    mode_emoji, mode_desc = mode_info[args.mode]
    print(f"\n📋 API Mode: {mode_emoji} - {mode_desc}\n")
    
    try:
        from src.dashboard.tour_guide_dashboard import run_tour_guide_dashboard
        
        run_tour_guide_dashboard(
            host=args.host,
            port=args.port,
            debug=not args.no_debug,
        )
    except ImportError as e:
        print(f"""
╔══════════════════════════════════════════════════════════════════════════╗
║  ⚠️  Missing Dependencies                                                 ║
╚══════════════════════════════════════════════════════════════════════════╝

The dashboard requires additional dependencies. Install them with:

    pip install dash plotly pandas numpy

Error: {e}
        """)
        return 1
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard stopped by user.")
        return 0
    except Exception as e:
        print(f"\n❌ Error starting dashboard: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

