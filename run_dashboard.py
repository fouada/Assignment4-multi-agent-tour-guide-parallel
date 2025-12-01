#!/usr/bin/env python3
"""
MIT-Level Interactive Research Dashboard Launcher
=================================================

Launch the interactive visualization dashboard for the
Multi-Agent Tour Guide System.

Usage:
    python run_dashboard.py [--host HOST] [--port PORT] [--no-debug]

Example:
    python run_dashboard.py                     # Default: localhost:8050
    python run_dashboard.py --port 8080         # Custom port
    python run_dashboard.py --host 0.0.0.0      # Public access

Author: Multi-Agent Tour Guide Research Team
Version: 1.0.0
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def main():
    """Main entry point for the dashboard."""
    parser = argparse.ArgumentParser(
        description='🗺️ MIT-Level Research Dashboard for Multi-Agent Tour Guide System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_dashboard.py                    Launch with defaults (localhost:8050)
  python run_dashboard.py --port 8080        Use custom port
  python run_dashboard.py --host 0.0.0.0     Allow external access
  python run_dashboard.py --no-debug         Disable debug mode for production

Dashboard Features:
  📊 System Monitor    - Real-time agent health and throughput monitoring
  🔬 Sensitivity       - Interactive parameter impact analysis
  🎯 Pareto Explorer   - Quality-latency tradeoff visualization
  📐 A/B Testing       - Statistical comparison of configurations
  🎲 Monte Carlo       - Stochastic simulation and analysis
        """
    )
    
    parser.add_argument(
        '--host',
        type=str,
        default='127.0.0.1',
        help='Host address to bind to (default: 127.0.0.1)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8050,
        help='Port to run on (default: 8050)'
    )
    
    parser.add_argument(
        '--no-debug',
        action='store_true',
        help='Disable debug mode (for production)'
    )
    
    args = parser.parse_args()
    
    try:
        from src.dashboard.app import run_dashboard
        run_dashboard(
            host=args.host,
            port=args.port,
            debug=not args.no_debug
        )
    except ImportError as e:
        print(f"""
╔══════════════════════════════════════════════════════════════════════╗
║  ⚠️  Missing Dependencies                                             ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  The dashboard requires additional packages. Install with:           ║
║                                                                      ║
║    uv sync --extra dashboard                                         ║
║                                                                      ║
║  Or install all dependencies:                                        ║
║                                                                      ║
║    uv sync --extra all                                               ║
║                                                                      ║
║  Error: {str(e)[:50]:50s}   ║
╚══════════════════════════════════════════════════════════════════════╝
        """)
        sys.exit(1)
    except Exception as e:
        print(f"Error starting dashboard: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

