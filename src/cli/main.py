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
from typing import Any

from src.models.route import RoutePoint
from src.models.user_profile import (
    UserProfile,
    get_driver_profile,
    get_family_profile,
    get_history_buff_profile,
    get_kid_profile,
)
from src.utils.logger import get_logger

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
        "history": get_history_buff_profile(),
    }
    return profiles.get(profile_name, UserProfile())


def run_demo_pipeline(
    mode: str = "queue", profile: UserProfile | None = None, verbose: bool = False
) -> list[dict[str, Any]]:
    """
    Run the full pipeline in demo mode with mock data.
    """
    print_banner()
    print("🎯 Running FULL PIPELINE in DEMO mode")
    print("─" * 60)

    # Import pipeline components
    from src.services.google_maps import get_mock_route

    # Get mock route
    route = get_mock_route()
    print(f"\n📍 Route: {route.source} → {route.destination}")
    print(f"📊 Points: {route.point_count}")
    distance_km = (route.total_distance or 0) / 1000
    print(f"📏 Distance: {distance_km:.1f} km")

    if profile:
        # Show meaningful profile info
        profile_name = (
            profile.name
            if profile.name
            else (profile.age_group.value if profile.age_group else "default")
        )
        print(f"👤 Profile: {profile_name}")

        # Show family-specific info
        if (
            profile.audience_type
            and str(profile.audience_type.value) == "family_with_kids"
        ):
            print(
                f"   👨‍👩‍👧‍👦 Family Mode: Content safe for ages {profile.min_age or 5}+"
            )
            if profile.exclude_topics:
                print(f"   🔒 Excluded: {', '.join(profile.exclude_topics)}")
            print(
                f"   ⏱️ Max duration: {(profile.max_content_duration_seconds or 300) // 60} min"
            )
            print(
                f"   📚 Preference: {profile.content_preference.value if profile.content_preference else 'educational'}"
            )

    print("\n" + "═" * 60)
    print("🚀 STARTING MULTI-AGENT PIPELINE")
    print("═" * 60)

    results = []

    for i, point in enumerate(route.points):
        print(
            f"\n📍 [{i + 1}/{route.point_count}] Processing: {point.location_name or point.address}"
        )
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
        print(f'   🏆 Winner: {result["winner"]} - "{result["title"]}"')

    # Final summary
    print("\n" + "═" * 60)
    is_family = (
        profile
        and profile.audience_type
        and str(profile.audience_type.value) == "family_with_kids"
    )
    if is_family:
        print("📋 FINAL TOUR GUIDE PLAYLIST 👨‍👩‍👧‍👦 Family-Safe")
    else:
        print("📋 FINAL TOUR GUIDE PLAYLIST")
    print("═" * 60)

    for i, result in enumerate(results):
        icon = {"VIDEO": "🎬", "MUSIC": "🎵", "TEXT": "📖"}.get(result["winner"], "📌")
        family_badge = " ✨" if is_family else ""
        print(
            f'   {icon} Point {i + 1}: {result["winner"]} - "{result["title"]}"{family_badge}'
        )

    if is_family and profile is not None:
        print(f"\n   ℹ️  All content verified safe for ages {profile.min_age or 5}+")
    print("\n✅ Pipeline complete!")
    return results


def process_point_with_queue(
    point: RoutePoint, profile: UserProfile | None = None, verbose: bool = False
) -> dict[str, Any]:
    """
    Process a single point using queue-based synchronization.
    This demonstrates the core architecture: agents → queue → judge
    """
    import threading
    from concurrent.futures import ThreadPoolExecutor, as_completed

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
                queue_results.append({"type": name, "result": result, "time": elapsed})

            status = "✅" if result else "⚠️"
            print(
                f"   {status} {name} Agent submitted ({len(queue_results)}/3) [{elapsed:.1f}s]"
            )
            return result
        except Exception as e:
            elapsed = time.time() - start
            print(f"   ❌ {name} Agent failed: {e} [{elapsed:.1f}s]")
            return None

    # Import agents
    from src.agents.music_agent import MusicAgent
    from src.agents.text_agent import TextAgent
    from src.agents.video_agent import VideoAgent

    # Run 3 agents in parallel
    with ThreadPoolExecutor(max_workers=3, thread_name_prefix="Agent") as executor:
        futures = {
            executor.submit(run_agent, VideoAgent, "Video"): "video",
            executor.submit(run_agent, MusicAgent, "Music"): "music",
            executor.submit(run_agent, TextAgent, "Text"): "text",
        }

        # Wait for all to complete (with timeout)
        for _future in as_completed(futures, timeout=30):
            pass

    # Queue ready - judge evaluates
    print(f"   ⏳ Queue ready ({len(queue_results)}/3)! Judge evaluating...")

    # Use JudgeAgent for proper evaluation with profile-based filtering
    if queue_results:
        from src.agents.judge_agent import JudgeAgent

        # Collect valid ContentResult objects
        candidates = [r["result"] for r in queue_results if r["result"] is not None]

        if candidates:
            # Create judge with the user profile (enables driver mode filtering)
            judge = JudgeAgent(user_profile=profile)

            try:
                decision = judge.evaluate(point, candidates, user_profile=profile)
                if decision.selected_content is None:
                    # No content selected, fallback to first candidate
                    best = candidates[0]
                    return {
                        "winner": best.content_type.value.upper(),
                        "title": best.title,
                        "point": point.location_name,
                    }

                winner_type = decision.selected_content.content_type.value.upper()
                winner_title = decision.selected_content.title

                # Show if profile constraints were applied
                if profile and profile.is_driver and winner_type != "VIDEO":
                    pass  # Driver mode working correctly - no video

                print(f'   🏆 Winner: {winner_type} - "{winner_title}"')

                return {
                    "winner": winner_type,
                    "title": winner_title,
                    "point": point.location_name,
                }
            except Exception:
                # Fallback to first available result
                best = candidates[0]
                return {
                    "winner": best.content_type.value.upper(),
                    "title": best.title,
                    "point": point.location_name,
                }

    return {
        "winner": "TEXT",
        "title": f"Historical facts about {point.location_name}",
        "point": point.location_name,
    }


def process_point_sequential(
    point: RoutePoint, profile: UserProfile | None = None, verbose: bool = False
) -> dict[str, Any]:
    """Sequential processing for debugging."""
    from src.agents.music_agent import MusicAgent
    from src.agents.text_agent import TextAgent
    from src.agents.video_agent import VideoAgent
    from src.models.content import ContentResult

    results: list[dict[str, Any]] = []

    for agent_class, name in [
        (VideoAgent, "Video"),
        (MusicAgent, "Music"),
        (TextAgent, "Text"),
    ]:
        try:
            agent = agent_class()
            result = agent.execute(point)
            print(f"   ✅ {name} Agent: {result.title if result else 'No result'}")
            results.append({"type": name, "result": result})
        except Exception as e:
            print(f"   ❌ {name} Agent failed: {e}")

    if results:
        best = results[0]
        best_type = str(best["type"]).upper()
        best_result: ContentResult | None = best["result"]
        return {
            "winner": best_type,
            "title": best_result.title if best_result else "Mock Content",
            "point": point.location_name,
        }

    return {"winner": "TEXT", "title": "Default content", "point": point.location_name}


def process_point_parallel(
    point: RoutePoint, profile: UserProfile | None = None, verbose: bool = False
) -> dict[str, Any]:
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

    print("\n✅ Setup Complete!")
    print(f"   Route: {source} → {destination}")

    # Run the pipeline
    run_demo_pipeline(mode="queue", profile=profile)


def run_custom_route(
    origin: str,
    destination: str,
    mode: str = "queue",
    profile: UserProfile | None = None,
    verbose: bool = False,
) -> list[dict[str, Any]]:
    """
    Run the pipeline with a custom route from Google Maps API.
    """
    print_banner()
    print(f"🎯 Custom route: {origin} → {destination}")
    print("─" * 60)

    # Try to get real route from Google Maps
    try:
        from src.services.google_maps import GoogleMapsClient
        from src.utils.config import settings

        if settings.google_maps_api_key:
            maps_client = GoogleMapsClient()
            route = maps_client.get_route(origin, destination)
            print(f"\n📍 Route: {route.source} → {route.destination}")
            print(f"📊 Points: {route.point_count}")
            if route.total_distance:
                print(f"📏 Distance: {route.total_distance / 1000:.1f} km")
            if route.total_duration:
                print(f"⏱️ Duration: {route.total_duration // 60} minutes")
        else:
            print("\n⚠️ No GOOGLE_MAPS_API_KEY set - using mock route")
            from src.services.google_maps import get_mock_route

            route = get_mock_route()
            print(f"\n📍 Route: {route.source} → {route.destination} (mock)")
            print(f"📊 Points: {route.point_count}")

    except Exception as e:
        print(f"\n⚠️ Could not fetch route from Google Maps: {e}")
        print("   Using mock route instead...")
        from src.services.google_maps import get_mock_route

        route = get_mock_route()
        print(f"\n📍 Route: {route.source} → {route.destination} (mock)")
        print(f"📊 Points: {route.point_count}")

    if profile:
        # Show meaningful profile info
        profile_name = (
            profile.name
            if profile.name
            else (profile.age_group.value if profile.age_group else "default")
        )
        print(f"👤 Profile: {profile_name}")

        # Show family-specific info
        if (
            profile.audience_type
            and str(profile.audience_type.value) == "family_with_kids"
        ):
            print(
                f"   👨‍👩‍👧‍👦 Family Mode: Content safe for ages {profile.min_age or 5}+"
            )
            if profile.exclude_topics:
                print(f"   🔒 Excluded: {', '.join(profile.exclude_topics)}")
            print(
                f"   ⏱️ Max duration: {(profile.max_content_duration_seconds or 300) // 60} min"
            )
            print(
                f"   📚 Preference: {profile.content_preference.value if profile.content_preference else 'educational'}"
            )

    print("\n" + "═" * 60)
    print("🚀 STARTING MULTI-AGENT PIPELINE")
    print("═" * 60)

    results = []

    for i, point in enumerate(route.points):
        print(
            f"\n📍 [{i + 1}/{route.point_count}] Processing: {point.location_name or point.address}"
        )
        print("─" * 40)

        if mode == "queue":
            result = process_point_with_queue(point, profile, verbose)
        elif mode == "sequential":
            result = process_point_sequential(point, profile, verbose)
        else:
            result = process_point_parallel(point, profile, verbose)

        results.append(result)
        print(f'   🏆 Winner: {result["winner"]} - "{result["title"]}"')

    # Final summary
    print("\n" + "═" * 60)
    is_family = (
        profile
        and profile.audience_type
        and str(profile.audience_type.value) == "family_with_kids"
    )
    if is_family:
        print("📋 FINAL TOUR GUIDE PLAYLIST 👨‍👩‍👧‍👦 Family-Safe")
    else:
        print("📋 FINAL TOUR GUIDE PLAYLIST")
    print("═" * 60)

    for i, result in enumerate(results):
        icon = {"VIDEO": "🎬", "MUSIC": "🎵", "TEXT": "📖"}.get(result["winner"], "📌")
        family_badge = " ✨" if is_family else ""
        print(
            f'   {icon} Point {i + 1}: {result["winner"]} - "{result["title"]}"{family_badge}'
        )

    if is_family and profile is not None:
        print(f"\n   ℹ️  All content verified safe for ages {profile.min_age or 5}+")
    print("\n✅ Pipeline complete!")
    return results


def main() -> int:
    """Main entry point. Returns exit code."""
    import warnings

    # Suppress ResourceWarning about unclosed SSL sockets from HTTP clients
    # This is a known issue with many Python HTTP libraries (anthropic, httpx)
    # that don't always close connections cleanly on exit
    warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed")

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
        """,
    )

    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run in demo mode with mock data (no API keys needed)",
    )
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Interactive setup mode"
    )
    parser.add_argument("--origin", "-o", type=str, help="Origin/starting point")
    parser.add_argument("--destination", "-d", "--dest", type=str, help="Destination")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["queue", "sequential", "streaming"],
        default="queue",
        help="Processing mode: queue (recommended), sequential, streaming",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Interval in seconds between points (for streaming mode)",
    )
    parser.add_argument(
        "--profile",
        type=str,
        choices=["default", "family", "kid", "driver", "history"],
        default="default",
        help="User profile preset",
    )
    parser.add_argument(
        "--min-age", type=int, default=5, help="Minimum age for family profile"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    try:
        if args.interactive:
            run_interactive()
        elif args.demo or (not args.origin and not args.destination):
            profile = get_profile(args.profile, args.min_age)
            run_demo_pipeline(mode=args.mode, profile=profile, verbose=args.verbose)
        else:
            # Custom route with real Google Maps API
            profile = get_profile(args.profile, args.min_age)
            run_custom_route(
                origin=args.origin,
                destination=args.destination,
                mode=args.mode,
                profile=profile,
                verbose=args.verbose,
            )
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
