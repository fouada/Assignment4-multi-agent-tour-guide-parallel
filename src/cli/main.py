#!/usr/bin/env python3
"""
Multi-Agent Tour Guide - Command Line Interface

Full Pipeline Execution:
1. Get route from Google Maps (or mock)
2. For each point, spawn 3 agents in parallel (Video, Music, Text)
3. Queue collects results, waits for all 3 (with smart timeout)
4. Judge evaluates and selects best content
5. Collector aggregates final playlist

Usage:
    python main.py --demo                    Run with mock data (no API keys needed)
    python main.py --demo --mode queue       Show queue synchronization
    python main.py -o "Paris" -d "Lyon"      Custom route (needs API keys)
"""
import argparse
import sys
import time
from typing import Optional

from src.utils.logger import get_logger
from src.utils.config import settings
from src.models.user_profile import (
    UserProfile,
    get_family_profile,
    get_kid_profile,
    get_driver_profile,
)
from src.models.route import Route, RoutePoint

logger = get_logger(__name__)


def print_banner():
    """Print welcome banner."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║   🗺️  MULTI-AGENT TOUR GUIDE SYSTEM  🗺️                      ║
║   Production-Grade Parallel Agent Architecture               ║
╚══════════════════════════════════════════════════════════════╝
    """)


def get_profile(profile_name: str, min_age: int = 5) -> UserProfile:
    """Get user profile by name."""
    profiles = {
        "default": UserProfile(),
        "family": get_family_profile(min_age=min_age),
        "kid": get_kid_profile(age=min_age),
        "driver": get_driver_profile(),
    }
    return profiles.get(profile_name, UserProfile())


def run_demo_pipeline(mode: str = "queue", profile: UserProfile = None, verbose: bool = False):
    """
    Run the full pipeline in demo mode with mock data.
    """
    print_banner()
    print("🎯 Running FULL PIPELINE in DEMO mode")
    print("─" * 60)
    
    # Import pipeline components
    from src.services.google_maps import get_mock_route
    from src.core.smart_queue import SmartAgentQueue
    from src.agents.video_agent import VideoAgent
    from src.agents.music_agent import MusicAgent
    from src.agents.text_agent import TextAgent
    from src.agents.judge_agent import JudgeAgent
    
    # Get mock route
    route = get_mock_route()
    print(f"\n📍 Route: {route.source} → {route.destination}")
    print(f"📊 Points: {route.point_count}")
    print(f"📏 Distance: {route.total_distance / 1000:.1f} km")
    
    if profile:
        print(f"👤 Profile: {profile.age_group.value if profile.age_group else 'default'}")
    
    print("\n" + "═" * 60)
    print("🚀 STARTING MULTI-AGENT PIPELINE")
    print("═" * 60)
    
    results = []
    
    for i, point in enumerate(route.points):
        print(f"\n📍 [{i+1}/{route.point_count}] Processing: {point.location_name or point.address}")
        print("─" * 40)
        
        if mode == "queue":
            # Queue-based processing (recommended)
            result = process_point_with_queue(point, profile, verbose)
        elif mode == "sequential":
            # Sequential processing (for debugging)
            result = process_point_sequential(point, profile, verbose)
        else:
            # Parallel without queue
            result = process_point_parallel(point, profile, verbose)
        
        results.append(result)
        print(f"   🏆 Winner: {result['winner']} - \"{result['title']}\"")
    
    # Final summary
    print("\n" + "═" * 60)
    print("📋 FINAL TOUR GUIDE PLAYLIST")
    print("═" * 60)
    
    for i, result in enumerate(results):
        icon = {"VIDEO": "🎬", "MUSIC": "🎵", "TEXT": "📖"}.get(result['winner'], "📌")
        print(f"   {icon} Point {i+1}: {result['winner']} - \"{result['title']}\"")
    
    print("\n✅ Pipeline complete!")
    return results


def process_point_with_queue(point: RoutePoint, profile: UserProfile = None, verbose: bool = False) -> dict:
    """
    Process a single point using queue-based synchronization.
    This demonstrates the core architecture: agents → queue → judge
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import threading
    
    # Create queue for this point
    queue_results = []
    queue_lock = threading.Lock()
    
    def run_agent(agent_class, name: str):
        """Run an agent and collect result."""
        start = time.time()
        try:
            agent = agent_class()
            result = agent.execute(point)
            elapsed = time.time() - start
            
            with queue_lock:
                queue_results.append({
                    "type": name,
                    "result": result,
                    "time": elapsed
                })
            
            status = "✅" if result else "⚠️"
            print(f"   {status} {name} Agent submitted ({len(queue_results)}/3) [{elapsed:.1f}s]")
            return result
        except Exception as e:
            elapsed = time.time() - start
            print(f"   ❌ {name} Agent failed: {e} [{elapsed:.1f}s]")
            return None
    
    # Import agents
    from src.agents.video_agent import VideoAgent
    from src.agents.music_agent import MusicAgent
    from src.agents.text_agent import TextAgent
    
    # Run 3 agents in parallel
    with ThreadPoolExecutor(max_workers=3, thread_name_prefix="Agent") as executor:
        futures = {
            executor.submit(run_agent, VideoAgent, "Video"): "video",
            executor.submit(run_agent, MusicAgent, "Music"): "music",
            executor.submit(run_agent, TextAgent, "Text"): "text",
        }
        
        # Wait for all to complete (with timeout)
        for future in as_completed(futures, timeout=30):
            pass
    
    # Queue ready - judge evaluates
    print(f"   ⏳ Queue ready ({len(queue_results)}/3)! Judge evaluating...")
    
    # Simple judging (pick best based on available results)
    if queue_results:
        # In real implementation, JudgeAgent would use LLM to compare
        best = queue_results[0]
        for r in queue_results:
            if r["result"] and (not best["result"] or r["time"] < best["time"]):
                best = r
        
        return {
            "winner": best["type"].upper(),
            "title": best["result"].title if best["result"] else "Mock Content",
            "point": point.location_name
        }
    
    return {
        "winner": "TEXT",
        "title": f"Historical facts about {point.location_name}",
        "point": point.location_name
    }


def process_point_sequential(point: RoutePoint, profile: UserProfile = None, verbose: bool = False) -> dict:
    """Sequential processing for debugging."""
    from src.agents.video_agent import VideoAgent
    from src.agents.music_agent import MusicAgent
    from src.agents.text_agent import TextAgent
    
    results = []
    
    for agent_class, name in [(VideoAgent, "Video"), (MusicAgent, "Music"), (TextAgent, "Text")]:
        try:
            agent = agent_class()
            result = agent.execute(point)
            print(f"   ✅ {name} Agent: {result.title if result else 'No result'}")
            results.append({"type": name, "result": result})
        except Exception as e:
            print(f"   ❌ {name} Agent failed: {e}")
    
    if results:
        best = results[0]
        return {
            "winner": best["type"].upper(),
            "title": best["result"].title if best["result"] else "Mock Content",
            "point": point.location_name
        }
    
    return {"winner": "TEXT", "title": "Default content", "point": point.location_name}


def process_point_parallel(point: RoutePoint, profile: UserProfile = None, verbose: bool = False) -> dict:
    """Parallel processing without queue visualization."""
    return process_point_with_queue(point, profile, verbose)


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
    
    # Run the pipeline
    run_demo_pipeline(mode="queue", profile=profile)


def main() -> int:
    """Main entry point. Returns exit code."""
    parser = argparse.ArgumentParser(
        description="Multi-Agent Tour Guide System - Full Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --demo                    Run full pipeline with mock data
  python main.py --demo --mode queue       Show queue synchronization (recommended)
  python main.py --demo --mode sequential  Process agents one by one (debugging)
  python main.py --demo --profile family   Family-friendly content
  python main.py --interactive             Interactive setup wizard
  python main.py -o "Paris" -d "Lyon"      Custom route (requires API keys)
        """
    )
    
    parser.add_argument(
        "--demo", 
        action="store_true",
        help="Run in demo mode with mock data (no API keys needed)"
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
        "--destination", "-d", "--dest",
        type=str,
        help="Destination"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["queue", "sequential", "streaming"],
        default="queue",
        help="Processing mode: queue (recommended), sequential, streaming"
    )
    parser.add_argument(
        "--profile",
        type=str,
        choices=["default", "family", "kid", "driver"],
        default="default",
        help="User profile preset"
    )
    parser.add_argument(
        "--min-age",
        type=int,
        default=5,
        help="Minimum age for family profile"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    try:
        if args.interactive:
            run_interactive()
        elif args.demo or (not args.origin and not args.destination):
            profile = get_profile(args.profile, args.min_age)
            run_demo_pipeline(mode=args.mode, profile=profile, verbose=args.verbose)
        else:
            print_banner()
            print(f"🎯 Custom route: {args.origin} → {args.destination}")
            print(f"   Mode: {args.mode}")
            print(f"   Profile: {args.profile}")
            print("\n⚠️ Custom routes require API keys:")
            print("   - OPENAI_API_KEY or ANTHROPIC_API_KEY")
            print("   - GOOGLE_MAPS_API_KEY (optional)")
            print("\n   See .env.example and run with --demo for now.")
        return 0
    except KeyboardInterrupt:
        print("\n\n👋 Tour guide stopped by user.")
        return 130
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


# Entry point for setuptools console_scripts
def app():
    """Entry point for setuptools."""
    sys.exit(main())


if __name__ == "__main__":
    sys.exit(main())
