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

Usage:
    python run_tour_dashboard.py
    python run_tour_dashboard.py --port 8080
    python run_tour_dashboard.py --host 0.0.0.0 --port 8080

Author: Multi-Agent Tour Guide Research Team
"""

import argparse
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
Examples:
  python run_tour_dashboard.py                    # Start on localhost:8051
  python run_tour_dashboard.py --port 8080        # Custom port
  python run_tour_dashboard.py --host 0.0.0.0     # Accessible from network
  python run_tour_dashboard.py --no-debug         # Production mode
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
        "--no-debug",
        action="store_true",
        help="Disable debug mode (for production)",
    )
    
    args = parser.parse_args()
    
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

