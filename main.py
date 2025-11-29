#!/usr/bin/env python3
"""
Multi-Agent Tour Guide System - Main Application

A system that creates an intelligent tour guide using multiple AI agents.
For each point in a route, agents search for relevant content (video, music, stories)
and a judge agent selects the best content to present.

Architecture:
- User Input → Google Maps API → Timer/Scheduler → Orchestrator
- For each point: 3 agents work in parallel, submit to QUEUE
- Judge waits for queue to be ready (all 3 submitted)
- Judge evaluates all together and selects best
- Collector aggregates final results

Usage:
    python main.py                    # Interactive mode
    python main.py --demo             # Run demo with sample route
    python main.py --origin "Tel Aviv" --destination "Jerusalem"  # Direct route
    python main.py --demo --profile family --min-age 5  # Family-friendly mode
"""
import argparse
import sys
import threading
import time
from typing import Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from config import settings
from models import Route, TourGuideOutput
from google_maps_api import get_maps_client, MockGoogleMapsClient
from orchestrator import Orchestrator, StreamingOrchestrator
from timer_scheduler import TravelSimulator, InstantTravelSimulator
from collector import ResultCollector, StreamingCollector
from agent_queue import AgentResultQueue, QueueManager, SynchronizedPointProcessor
from user_profile import UserProfile, TourSetup, get_family_profile, get_history_buff_profile
from logger_setup import logger, log_orchestrator_event


def print_banner():
    """Print the application banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║   🗺️  MULTI-AGENT TOUR GUIDE SYSTEM  🗺️                      ║
    ║                                                              ║
    ║   Intelligent content discovery for your journey            ║
    ║   Using parallel AI agents for video, music & stories       ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def get_user_input() -> TourSetup:
    """Get route and profile from user interactively."""
    return TourSetup.from_interactive()


def get_simple_route_input() -> tuple[str, str]:
    """Get just route origin and destination from user."""
    print("\n📍 Enter your route details:\n")
    
    origin = input("   Origin (starting point): ").strip()
    if not origin:
        origin = "Tel Aviv, Israel"
        print(f"   Using default: {origin}")
    
    destination = input("   Destination: ").strip()
    if not destination:
        destination = "Jerusalem, Israel"
        print(f"   Using default: {destination}")
    
    return origin, destination


def run_demo_mode():
    """Run a demonstration with a sample route."""
    print("\n🎭 Running DEMO MODE with sample route...\n")
    
    # Use mock client for demo
    maps_client = MockGoogleMapsClient()
    route = maps_client.get_route(
        origin="Tel Aviv, Israel",
        destination="Jerusalem, Israel"
    )
    
    return route


def run_streaming_mode(route: Route):
    """
    Run in streaming mode - process points as they arrive.
    Simulates real-time travel experience.
    """
    print(f"\n🚗 Starting streaming tour from {route.source} to {route.destination}")
    print(f"   Total points: {route.point_count}")
    print(f"   Point interval: {settings.point_interval_seconds}s")
    print("\n" + "="*60)
    
    # Create streaming components
    orchestrator = StreamingOrchestrator()
    collector = StreamingCollector(
        route,
        on_decision=lambda d: print(f"   📢 New content for point: {d.selected_content.title[:40]}...")
    )
    
    # Start the orchestrator
    orchestrator.start_streaming()
    
    # Create timer simulator
    def on_point_arrival(point):
        print(f"\n📍 Arriving at: {point.location_name or point.address}")
        orchestrator.add_point(point)
    
    simulator = TravelSimulator(
        route=route,
        on_point_arrival=on_point_arrival
    )
    
    # Start simulation
    print("\n⏱️ Starting travel simulation...\n")
    simulator.start()
    
    # Wait for completion
    try:
        while simulator.is_running:
            time.sleep(0.5)
            
            # Check for new results
            result = orchestrator.get_next_result(timeout=0.1)
            if result:
                collector.add_decision(result)
        
        # Wait for all processing to complete
        print("\n⏳ Waiting for all content to be processed...")
        orchestrator.wait_for_completion(timeout=60)
        
        # Collect remaining results
        while True:
            result = orchestrator.get_next_result(timeout=1.0)
            if result:
                collector.add_decision(result)
            else:
                break
        
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping simulation...")
    finally:
        simulator.stop()
        orchestrator.stop_streaming()
    
    return collector.generate_output()


def run_instant_mode(route: Route):
    """
    Run in instant mode - process all points immediately.
    Faster but less realistic.
    """
    print(f"\n⚡ Processing route: {route.source} → {route.destination}")
    print(f"   Total points: {route.point_count}")
    print("\n" + "="*60)
    
    # Create components
    orchestrator = Orchestrator()
    collector = ResultCollector(route)
    
    # Process all points
    print("\n🔄 Processing all points in parallel...\n")
    
    start_time = time.time()
    
    # Use the orchestrator to process all points
    decisions = orchestrator.process_points(route.points)
    
    # Collect results
    for decision in decisions:
        collector.add_decision(decision)
    
    duration = time.time() - start_time
    print(f"\n✅ All points processed in {duration:.2f}s")
    
    return collector.generate_output()


def run_sequential_mode(route: Route, user_profile: UserProfile = None):
    """
    Run in sequential mode - process points one by one.
    Easiest to understand and debug.
    """
    print(f"\n🚶 Sequential processing: {route.source} → {route.destination}")
    print(f"   Total points: {route.point_count}")
    if user_profile:
        print(f"   Profile: {user_profile.audience_type.value}")
    print("\n" + "="*60)
    
    from agents import VideoAgent, MusicAgent, TextAgent, JudgeAgent
    
    collector = ResultCollector(route)
    
    video_agent = VideoAgent()
    music_agent = MusicAgent()
    text_agent = TextAgent()
    judge_agent = JudgeAgent()
    
    for i, point in enumerate(route.points):
        print(f"\n📍 [{i+1}/{route.point_count}] Processing: {point.location_name or point.address}")
        
        # Run agents (in this mode, still run them in parallel per point)
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        candidates = []
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(video_agent.execute, point): 'video',
                executor.submit(music_agent.execute, point): 'music',
                executor.submit(text_agent.execute, point): 'text',
            }
            
            for future in as_completed(futures):
                result = future.result()
                if result:
                    candidates.append(result)
                    print(f"   ✓ Found {futures[future]}: {result.title[:40]}...")
        
        # Judge
        if candidates:
            decision = judge_agent.evaluate(point, candidates)
            collector.add_decision(decision)
            print(f"   ⚖️ Selected: {decision.selected_content.content_type.value}")
        else:
            print(f"   ⚠️ No content found for this point")
    
    return collector.generate_output()


def run_queue_mode(route: Route, user_profile: UserProfile = None):
    """
    Run with queue-based synchronization.
    
    This is the recommended architecture:
    - Each point gets its own queue
    - 3 agents submit to queue
    - Judge waits for queue to be ready (all 3 submitted)
    - Then evaluates all together
    """
    print(f"\n📬 Queue-based processing: {route.source} → {route.destination}")
    print(f"   Total points: {route.point_count}")
    if user_profile:
        print(f"   Profile: {user_profile.audience_type.value}")
    print("\n" + "="*60)
    print("\n🔄 Using QUEUE synchronization between agents and judge...")
    print("   (Each queue waits for all 3 agents before judge evaluates)\n")
    
    collector = ResultCollector(route)
    
    for i, point in enumerate(route.points):
        print(f"\n{'='*50}")
        print(f"📍 [{i+1}/{route.point_count}] {point.location_name or point.address}")
        print(f"{'='*50}")
        
        # Use synchronized processor with queue
        processor = SynchronizedPointProcessor(
            point=point,
            user_profile=user_profile.model_dump() if user_profile else None
        )
        
        # Process (queue handles synchronization)
        decision = processor.process()
        
        if decision:
            collector.add_decision(decision)
            print(f"\n   🏆 Winner: {decision.selected_content.content_type.value.upper()}")
            print(f"      Title: {decision.selected_content.title}")
            print(f"      Reason: {decision.reasoning[:80]}...")
    
    return collector.generate_output()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Multi-Agent Tour Guide System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --demo                           # Quick demo
  python main.py --demo --mode queue              # Demo with queue sync (recommended)
  python main.py --demo --profile family --min-age 5  # Family mode
  python main.py -o "Tel Aviv" -d "Jerusalem"    # Custom route
        """
    )
    parser.add_argument(
        "--origin", "-o",
        help="Starting point address"
    )
    parser.add_argument(
        "--destination", "-d",
        help="Destination address"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run demo mode with sample route"
    )
    parser.add_argument(
        "--mode", "-m",
        choices=["streaming", "instant", "sequential", "queue"],
        default="queue",
        help="Processing mode (default: queue - recommended)"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock APIs (no real API calls)"
    )
    parser.add_argument(
        "--interval", "-i",
        type=float,
        default=settings.point_interval_seconds,
        help="Interval between points in streaming mode (seconds)"
    )
    parser.add_argument(
        "--profile", "-p",
        choices=["default", "family", "history"],
        default="default",
        help="User profile preset"
    )
    parser.add_argument(
        "--min-age",
        type=int,
        help="Minimum age (for family profile)"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run interactive setup"
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    # Setup user profile
    user_profile = None
    if args.profile == "family":
        min_age = args.min_age or 5
        user_profile = get_family_profile(min_age)
        print(f"\n👨‍👩‍👧 Using FAMILY profile (kids age {min_age}+)")
    elif args.profile == "history":
        user_profile = get_history_buff_profile()
        print("\n📚 Using HISTORY BUFF profile")
    else:
        user_profile = UserProfile()
    
    # Determine route
    if args.interactive:
        setup = get_user_input()
        route_origin = setup.source
        route_dest = setup.destination
        user_profile = setup.user_profile
        maps_client = get_maps_client(use_mock=args.mock)
        route = maps_client.get_route(route_origin, route_dest)
    elif args.demo:
        route = run_demo_mode()
    elif args.origin and args.destination:
        print(f"\n🗺️ Fetching route: {args.origin} → {args.destination}")
        maps_client = get_maps_client(use_mock=args.mock)
        route = maps_client.get_route(args.origin, args.destination)
    else:
        origin, destination = get_simple_route_input()
        print(f"\n🗺️ Fetching route: {origin} → {destination}")
        maps_client = get_maps_client(use_mock=args.mock)
        route = maps_client.get_route(origin, destination)
    
    print(f"\n📊 Route details:")
    print(f"   Points: {route.point_count}")
    if route.total_distance:
        print(f"   Distance: {route.total_distance/1000:.1f} km")
    if route.total_duration:
        print(f"   Duration: {route.total_duration/60:.0f} min")
    
    # Show profile context
    if user_profile:
        context = user_profile.to_agent_context()
        if context != "No specific preferences.":
            print(f"\n👤 Profile context for agents:")
            print(f"   {context}")
    
    # Update settings with command line args
    if args.interval:
        settings.point_interval_seconds = args.interval
    
    # Run in selected mode
    if args.mode == "streaming":
        output = run_streaming_mode(route)
    elif args.mode == "sequential":
        output = run_sequential_mode(route, user_profile)
    elif args.mode == "queue":
        output = run_queue_mode(route, user_profile)
    else:  # instant
        output = run_instant_mode(route)
    
    # Print final output
    output.print_playlist()
    
    # Print stats
    print("\n📊 Processing Statistics:")
    for key, value in output.processing_stats.items():
        print(f"   {key}: {value}")
    
    print("\n✨ Tour guide generation complete!")
    
    return output


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)

