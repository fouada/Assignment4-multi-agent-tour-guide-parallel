#!/usr/bin/env python3
"""
🗺️ Multi-Agent Tour Guide - Full System Runner
================================================

MIT-Level Architecture: Starts both API and Dashboard with proper coordination.

This script ensures the proper architecture is used:
    ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
    │   Dashboard     │──────▶│    FastAPI      │──────▶│  TourService    │
    │   (Port 8051)   │ HTTP  │   (Port 8000)   │       │  (Agents+Queue) │
    └─────────────────┘       └─────────────────┘       └─────────────────┘

Usage:
    # Start both API and Dashboard (recommended)
    python run_full_system.py

    # Start with specific API mode
    python run_full_system.py --mode real      # Real APIs for demo
    python run_full_system.py --mode mock      # Mock data for testing

    # Custom ports
    python run_full_system.py --api-port 8000 --dashboard-port 8051

Author: Multi-Agent Tour Guide Research Team
Version: 2.0.0
"""

import argparse
import os
import subprocess
import sys
import time
import signal
import threading
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def check_port_available(port: int) -> bool:
    """Check if a port is available."""
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) != 0


def wait_for_api(port: int, timeout: float = 30.0) -> bool:
    """Wait for the API to be ready."""
    import httpx

    start = time.time()
    url = f"http://localhost:{port}/health"

    while time.time() - start < timeout:
        try:
            response = httpx.get(url, timeout=2.0)
            if response.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(0.5)

    return False


def print_banner():
    """Print the startup banner."""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   🗺️  MULTI-AGENT TOUR GUIDE SYSTEM - MIT-LEVEL ARCHITECTURE                ║
║                                                                              ║
║   ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐   ║
║   │   Dashboard     │──────▶│    FastAPI      │──────▶│  TourService    │   ║
║   │   (Port 8051)   │ HTTP  │   (Port 8000)   │       │  (Agents+Queue) │   ║
║   └─────────────────┘       └─────────────────┘       └─────────────────┘   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)


def main():
    parser = argparse.ArgumentParser(
        description="🗺️ Multi-Agent Tour Guide - Full System Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Architecture:
  This script starts both the FastAPI backend and Dash dashboard
  to ensure the proper MIT-level architecture is used.

Examples:
  python run_full_system.py                    # Start full system (auto mode)
  python run_full_system.py --mode real        # Real APIs for MIT demo
  python run_full_system.py --mode mock        # Mock data for testing
  python run_full_system.py --api-only         # Only start the API
  python run_full_system.py --dashboard-only   # Only start dashboard (assumes API running)
        """,
    )

    parser.add_argument(
        "--mode",
        type=str,
        choices=["auto", "real", "mock"],
        default="auto",
        help="API mode: auto (default), real (MIT demo), mock (testing)",
    )
    parser.add_argument(
        "--api-port",
        type=int,
        default=8000,
        help="Port for FastAPI (default: 8000)",
    )
    parser.add_argument(
        "--dashboard-port",
        type=int,
        default=8051,
        help="Port for Dashboard (default: 8051)",
    )
    parser.add_argument(
        "--api-only",
        action="store_true",
        help="Only start the API server",
    )
    parser.add_argument(
        "--dashboard-only",
        action="store_true",
        help="Only start the dashboard (assumes API is already running)",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't open browser automatically",
    )

    args = parser.parse_args()

    print_banner()

    # Set environment variables
    os.environ["TOUR_GUIDE_API_MODE"] = args.mode
    os.environ["TOUR_GUIDE_API_URL"] = f"http://localhost:{args.api_port}"

    mode_info = {
        "auto": ("🔄 AUTO", "Real APIs with mock fallback"),
        "real": ("🔴 REAL", "Actual API calls (YouTube, Spotify, Claude)"),
        "mock": ("⚪ MOCK", "Fast mocked data (no API calls)"),
    }
    mode_emoji, mode_desc = mode_info[args.mode]
    print(f"📋 API Mode: {mode_emoji} - {mode_desc}")
    print()

    processes = []

    try:
        # ================================================================
        # Start API Server
        # ================================================================
        if not args.dashboard_only:
            if not check_port_available(args.api_port):
                print(
                    f"⚠️  Port {args.api_port} is already in use. API may already be running."
                )
            else:
                print(f"🚀 Starting FastAPI server on port {args.api_port}...")

                api_cmd = [
                    sys.executable,
                    "-m",
                    "uvicorn",
                    "src.api.app:app",
                    "--host",
                    "0.0.0.0",
                    "--port",
                    str(args.api_port),
                    "--log-level",
                    "info",
                ]

                api_process = subprocess.Popen(
                    api_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
                processes.append(("API", api_process))

                # Wait for API to be ready
                print("   ⏳ Waiting for API to be ready...")
                if wait_for_api(args.api_port, timeout=30.0):
                    print(f"   ✅ API ready at http://localhost:{args.api_port}")
                    print(f"   📚 Swagger docs: http://localhost:{args.api_port}/docs")
                else:
                    print("   ❌ API failed to start within timeout")
                    raise Exception("API startup failed")

        if args.api_only:
            print("\n🎯 API-only mode. Press Ctrl+C to stop.")
            # Keep running
            while True:
                time.sleep(1)

        # ================================================================
        # Start Dashboard
        # ================================================================
        if not args.api_only:
            if not check_port_available(args.dashboard_port):
                print(f"⚠️  Port {args.dashboard_port} is already in use.")
            else:
                print(f"\n🚀 Starting Dashboard on port {args.dashboard_port}...")

                dashboard_cmd = [
                    sys.executable,
                    "run_tour_dashboard.py",
                    "--port",
                    str(args.dashboard_port),
                    "--mode",
                    args.mode,
                ]

                dashboard_process = subprocess.Popen(
                    dashboard_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
                processes.append(("Dashboard", dashboard_process))

                time.sleep(2)  # Give dashboard time to start

                print(
                    f"   ✅ Dashboard ready at http://localhost:{args.dashboard_port}"
                )

        # ================================================================
        # Open Browser
        # ================================================================
        if not args.no_browser and not args.api_only:
            print("\n🌐 Opening dashboard in browser...")
            import webbrowser

            webbrowser.open(f"http://localhost:{args.dashboard_port}")

        # ================================================================
        # Summary
        # ================================================================
        print("\n" + "=" * 60)
        print("✅ SYSTEM READY")
        print("=" * 60)

        if not args.dashboard_only:
            print(f"   🔧 API:       http://localhost:{args.api_port}")
            print(f"   📚 Docs:      http://localhost:{args.api_port}/docs")

        if not args.api_only:
            print(f"   🎨 Dashboard: http://localhost:{args.dashboard_port}")

        print("\n   Press Ctrl+C to stop all services.")
        print("=" * 60)

        # Stream logs from processes
        def stream_output(name, process):
            for line in iter(process.stdout.readline, ""):
                if line:
                    print(f"[{name}] {line.rstrip()}")

        threads = []
        for name, proc in processes:
            t = threading.Thread(target=stream_output, args=(name, proc), daemon=True)
            t.start()
            threads.append(t)

        # Wait for interrupt
        while True:
            time.sleep(1)
            # Check if any process died
            for name, proc in processes:
                if proc.poll() is not None:
                    print(f"\n⚠️  {name} process exited with code {proc.returncode}")

    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
    finally:
        # Cleanup
        for name, proc in processes:
            print(f"   Stopping {name}...")
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()

        print("✅ All services stopped.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
