#!/usr/bin/env python3
"""
Multi-Agent Tour Guide - Command Line Interface

Usage:
    python -m src.cli.main --demo
    python -m src.cli.main --origin "Tel Aviv" --destination "Jerusalem"
    python -m src.cli.main --interactive
"""
import argparse
import sys
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(__file__).rsplit('/src/', 1)[0])

from src.utils.logger import get_logger
from src.utils.config import settings
from src.models.user_profile import (
    UserProfile,
    get_family_profile,
    get_kid_profile,
    get_driver_profile,
)

logger = get_logger(__name__)


def print_banner():
    """Print welcome banner."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║   🗺️  MULTI-AGENT TOUR GUIDE SYSTEM  🗺️                      ║
║   MIT-Level Project - Parallel Agent Architecture            ║
╚══════════════════════════════════════════════════════════════╝
    """)


def run_demo():
    """Run demo mode with mock data."""
    print_banner()
    print("🎯 Running in DEMO mode (using mock data)")
    print("─" * 60)
    
    # Import here to avoid circular imports
    from src.services.google_maps import get_mock_route
    
    route = get_mock_route()
    print(f"\n📍 Route: {route.source} → {route.destination}")
    print(f"📊 Points: {route.point_count}")
    print(f"📏 Distance: {route.total_distance / 1000:.1f} km")
    
    print("\n🤖 Agents would be spawned for each point:")
    for point in route.points:
        print(f"   • Point {point.index + 1}: {point.location_name or point.address}")
        print(f"     └─ Video Agent, Music Agent, Text Agent → Judge")
    
    print("\n✅ Demo complete! Run with real API keys for full functionality.")
    print("   See docs/MIT_PROJECT_SPECIFICATION.md for details.")


def run_interactive():
    """Run interactive setup mode."""
    print_banner()
    print("🎯 Interactive Setup Mode")
    print("─" * 60)
    
    source = input("\n📍 Enter starting point: ").strip() or "Tel Aviv, Israel"
    destination = input("🎯 Enter destination: ").strip() or "Jerusalem, Israel"
    
    print("\n👤 Profile Selection:")
    print("   1. Default (Adult)")
    print("   2. Family with Kids")
    print("   3. Driver (no video)")
    print("   4. Custom")
    
    choice = input("\nSelect profile [1-4]: ").strip() or "1"
    
    if choice == "2":
        age = input("   Youngest child's age: ").strip()
        profile = get_family_profile(min_age=int(age) if age.isdigit() else 5)
    elif choice == "3":
        profile = get_driver_profile()
    else:
        profile = UserProfile()
    
    print(f"\n✅ Setup Complete!")
    print(f"   Route: {source} → {destination}")
    print(f"   Profile: {profile.age_group.value if profile.age_group else 'default'}")
    
    # Here you would call the main processing pipeline
    print("\n⚠️ Full processing requires API keys. Running in demo mode.")
    run_demo()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Multi-Agent Tour Guide System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.cli.main --demo                    Run with mock data
  python -m src.cli.main --interactive             Interactive setup
  python -m src.cli.main -o "Tel Aviv" -d "Haifa"  Custom route
        """
    )
    
    parser.add_argument(
        "--demo", 
        action="store_true",
        help="Run in demo mode with mock data"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Interactive setup mode"
    )
    parser.add_argument(
        "--origin", "-o",
        type=str,
        help="Origin/starting point"
    )
    parser.add_argument(
        "--destination", "-d",
        type=str,
        help="Destination"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["queue", "sequential", "streaming"],
        default="queue",
        help="Processing mode (default: queue)"
    )
    parser.add_argument(
        "--profile",
        type=str,
        choices=["default", "family", "kid", "driver"],
        default="default",
        help="User profile preset"
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=5.0,
        help="Point interval in seconds (for streaming mode)"
    )
    
    args = parser.parse_args()
    
    if args.interactive:
        run_interactive()
    elif args.demo or (not args.origin and not args.destination):
        run_demo()
    else:
        print_banner()
        print(f"🎯 Processing route: {args.origin} → {args.destination}")
        print(f"   Mode: {args.mode}")
        print(f"   Profile: {args.profile}")
        print("\n⚠️ Requires API keys. See .env.example")


# Typer app for modern CLI (optional)
def app():
    """Entry point for setuptools."""
    main()


if __name__ == "__main__":
    main()

