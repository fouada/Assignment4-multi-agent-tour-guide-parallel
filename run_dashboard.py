#!/usr/bin/env python3
"""
MIT-Level Interactive Research Dashboard Launcher
=================================================

Launch the interactive visualization dashboard for the
Multi-Agent Tour Guide System.

DATA MODE: SIMULATED (By Design)
--------------------------------
The Research Dashboard uses SIMULATED data for:
- Reproducible statistical experiments
- Fast Monte Carlo simulations (10,000+ runs)
- Parameter sensitivity analysis
- No API costs for research purposes

For REAL API tour processing, use run_tour_dashboard.py instead.

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
import os
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
  🔬 Sensitivity       - Interactive parameter impact analysis (Simulated)
  🎯 Pareto Explorer   - Quality-latency tradeoff visualization (Simulated)
  📐 A/B Testing       - Statistical comparison of configurations (Simulated)
  🎲 Monte Carlo       - Stochastic simulation and analysis (Simulated)

NOTE: This Research Dashboard uses SIMULATED data for reproducible experiments.
      For REAL API tour processing, use: python run_tour_dashboard.py
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

    parser.add_argument(
        '--data-source',
        type=str,
        choices=['simulated', 'live', 'hybrid'],
        default='simulated',
        help='Data source mode: simulated (default), live (real API), hybrid (mixed)'
    )

    args = parser.parse_args()

    # Set data source environment variable
    os.environ["RESEARCH_DASHBOARD_DATA_SOURCE"] = args.data_source

    # Print mode banner based on data source
    data_source_info = {
        'simulated': ('📊 SIMULATED', 'Fast Monte Carlo (10K+ runs, reproducible)'),
        'live': ('🔴 LIVE', 'Real TourService API data (actual tours)'),
        'hybrid': ('🔀 HYBRID', 'Mixed: Real data + simulated extrapolation'),
    }
    mode_emoji, mode_desc = data_source_info[args.data_source]

    print(f"""
╔══════════════════════════════════════════════════════════════════════════╗
║   🔬 RESEARCH DASHBOARD - Data Source: {mode_emoji:18s}                  ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║   Mode: {mode_desc:60s}  ║
║                                                                          ║
║   Features:                                                              ║
║   • Monte Carlo simulations                                              ║
║   • Parameter sensitivity analysis                                       ║
║   • Statistical A/B testing                                              ║
║   • Pareto frontier exploration                                          ║
║                                                                          ║
║   Change data source with: --data-source [simulated|live|hybrid]         ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
    """)

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

