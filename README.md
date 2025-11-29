# 🗺️ Multi-Agent Tour Guide System

<div align="center">

![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg?style=for-the-badge&logo=python)
![UV](https://img.shields.io/badge/uv-package%20manager-blueviolet.svg?style=for-the-badge)
![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)
![Architecture](https://img.shields.io/badge/Architecture-MIT%20Level-green.svg?style=for-the-badge)

**Enterprise-Grade Multi-Agent Orchestration System**

*Parallel AI agents • Plugin architecture • Resilience patterns • Full observability*

[Quick Start](#-quick-start) •
[Architecture](#-architecture) •
[Installation](#-installation) •
[Usage](#-usage) •
[Monitoring](#-monitoring-traffic-on-all-hops) •
[Plugins](#-plugin-system)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Usage](#-usage)
- [Monitoring Traffic on All Hops](#-monitoring-traffic-on-all-hops)
- [Plugin System](#-plugin-system)
- [Configuration](#-configuration)
- [Testing](#-testing)
- [API Reference](#-api-reference)
- [Documentation](#-documentation)

---

## 🎯 Overview

A **production-grade multi-agent AI system** that creates personalized tour guides. Given a route, the system uses **parallel AI agents** to find the most relevant content (video, music, text) for each point, with a **Judge agent** selecting the best based on **user profile**.

### ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🤖 **Parallel Agents** | Video, Music, Text agents work simultaneously using ThreadPoolExecutor |
| 📬 **Smart Queue** | Wait for 3 agents, accept 2 after 15s, accept 1 after 30s |
| 👤 **User Profiles** | Content personalized by age, gender, interests |
| 🔌 **Plugin Architecture** | Add new agents without modifying core code |
| ⚡ **Resilience Patterns** | Circuit breaker, retry, timeout, rate limiting |
| 📊 **Full Observability** | Metrics, distributed tracing, health checks |
| 💉 **Dependency Injection** | Loose coupling, testability, extensibility |
| 🎣 **Hook System** | AOP-style before/after/around hooks |

---

## 🚀 Quick Start

```bash
# 1. Install UV (ultra-fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone and setup
git clone <your-repo-url>
cd Assignment4-multi-agent-tour-guide-parallel
make setup

# 3. Run demo with full traffic visibility
make run-demo

# 4. Run with queue mode (recommended - shows all hops)
make run-queue
```

### 30-Second Demo

```bash
# See agents racing and queue synchronization
uv run python main.py --demo --mode queue

# Expected output:
# 📬 Queue-based processing: Tel Aviv → Jerusalem
# 📍 [1/4] Ammunition Hill
#    ✅ Video Agent submitted (1/3)
#    ✅ Music Agent submitted (2/3)
#    ✅ Text Agent submitted (3/3)
#    ⏳ Queue ready! Judge evaluating...
#    🏆 Winner: VIDEO - "Battle of Ammunition Hill"
```

---

## 🏗️ Architecture

### High-Level System Overview

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                         MULTI-AGENT TOUR GUIDE SYSTEM                        ║
║                        MIT-Level Production Architecture                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  ┌────────────────────────────────────────────────────────────────────────┐ ║
║  │                         👤 USER INPUT                                   │ ║
║  │           Source: "Tel Aviv"  →  Destination: "Jerusalem"              │ ║
║  │           Profile: { age: "adult", interests: ["history"] }            │ ║
║  └──────────────────────────────┬─────────────────────────────────────────┘ ║
║                                 │                                            ║
║                                 ▼                                            ║
║  ┌────────────────────────────────────────────────────────────────────────┐ ║
║  │                      🗺️ GOOGLE MAPS API                                │ ║
║  │              Returns: [Point1, Point2, Point3, Point4]                 │ ║
║  └──────────────────────────────┬─────────────────────────────────────────┘ ║
║                                 │                                            ║
║                                 ▼                                            ║
║  ┌────────────────────────────────────────────────────────────────────────┐ ║
║  │                       ⏱️ TIMER/SCHEDULER                               │ ║
║  │           Emits points at intervals (streaming mode)                   │ ║
║  │           Or processes all at once (instant mode)                      │ ║
║  └──────────────────────────────┬─────────────────────────────────────────┘ ║
║                                 │                                            ║
║  ╔══════════════════════════════▼═════════════════════════════════════════╗ ║
║  ║                        🎯 ORCHESTRATOR                                  ║ ║
║  ║              ThreadPoolExecutor (max_workers=12)                        ║ ║
║  ║                                                                         ║ ║
║  ║   FOR EACH POINT:                                                       ║ ║
║  ║   ╔═════════════════════════════════════════════════════════════════╗  ║ ║
║  ║   ║              PARALLEL AGENT EXECUTION                           ║  ║ ║
║  ║   ║                                                                 ║  ║ ║
║  ║   ║   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐          ║  ║ ║
║  ║   ║   │ 🎬 VIDEO    │   │ 🎵 MUSIC    │   │ 📖 TEXT     │          ║  ║ ║
║  ║   ║   │   AGENT     │   │   AGENT     │   │   AGENT     │          ║  ║ ║
║  ║   ║   │             │   │             │   │             │          ║  ║ ║
║  ║   ║   │ • YouTube   │   │ • Spotify   │   │ • Wikipedia │          ║  ║ ║
║  ║   ║   │ • Retry: 3x │   │ • Retry: 3x │   │ • Retry: 3x │          ║  ║ ║
║  ║   ║   │ • Timeout   │   │ • Timeout   │   │ • Timeout   │          ║  ║ ║
║  ║   ║   └──────┬──────┘   └──────┬──────┘   └──────┬──────┘          ║  ║ ║
║  ║   ║          │                 │                 │                  ║  ║ ║
║  ║   ║          └─────────────────┼─────────────────┘                  ║  ║ ║
║  ║   ║                            ▼                                    ║  ║ ║
║  ║   ║   ┌─────────────────────────────────────────────────────────┐  ║  ║ ║
║  ║   ║   │                   📬 SMART QUEUE                        │  ║  ║ ║
║  ║   ║   │                                                         │  ║  ║ ║
║  ║   ║   │   Timeline: [0s]────────[15s]────────[30s]             │  ║  ║ ║
║  ║   ║   │              │           │            │                 │  ║  ║ ║
║  ║   ║   │              │ Wait for  │ Accept 2   │ Accept 1       │  ║  ║ ║
║  ║   ║   │              │ 3 agents  │ (graceful) │ (fallback)     │  ║  ║ ║
║  ║   ║   │                                                         │  ║  ║ ║
║  ║   ║   │   Status: [Video ✅] [Music ✅] [Text ✅] → READY!     │  ║  ║ ║
║  ║   ║   └─────────────────────────┬───────────────────────────────┘  ║  ║ ║
║  ║   ║                             ▼                                   ║  ║ ║
║  ║   ║   ┌─────────────────────────────────────────────────────────┐  ║  ║ ║
║  ║   ║   │                   ⚖️ JUDGE AGENT                        │  ║  ║ ║
║  ║   ║   │                                                         │  ║  ║ ║
║  ║   ║   │   Input: 3 candidates + User Profile                   │  ║  ║ ║
║  ║   ║   │                                                         │  ║  ║ ║
║  ║   ║   │   Scoring (with profile weights):                      │  ║  ║ ║
║  ║   ║   │     Video: 8.5 × 1.0 (adult) = 8.5                     │  ║  ║ ║
║  ║   ║   │     Music: 7.0 × 1.0 (adult) = 7.0                     │  ║  ║ ║
║  ║   ║   │     Text:  9.0 × 1.0 (adult) = 9.0 ⭐ WINNER          │  ║  ║ ║
║  ║   ║   │                                                         │  ║  ║ ║
║  ║   ║   │   DECISION: TEXT (historical content preferred)       │  ║  ║ ║
║  ║   ║   └─────────────────────────┬───────────────────────────────┘  ║  ║ ║
║  ║   ╚═════════════════════════════╪═══════════════════════════════════╝  ║ ║
║  ║                                 │                                       ║ ║
║  ╚═════════════════════════════════╪═══════════════════════════════════════╝ ║
║                                    ▼                                         ║
║  ┌────────────────────────────────────────────────────────────────────────┐ ║
║  │                        📦 COLLECTOR                                    │ ║
║  │              Aggregates decisions, maintains order                     │ ║
║  └──────────────────────────────┬─────────────────────────────────────────┘ ║
║                                 │                                            ║
║                                 ▼                                            ║
║  ┌────────────────────────────────────────────────────────────────────────┐ ║
║  │                      🎵 FINAL PLAYLIST                                 │ ║
║  │                                                                        │ ║
║  │  Point 1: Ammunition Hill  → 📖 TEXT: "Battle of Ammunition Hill"    │ ║
║  │  Point 2: Old City         → 🎵 MUSIC: "Jerusalem of Gold"           │ ║
║  │  Point 3: Western Wall     → 🎬 VIDEO: "History Documentary"         │ ║
║  │  Point 4: Mount of Olives  → 📖 TEXT: "Ancient Burial Ground"        │ ║
║  └────────────────────────────────────────────────────────────────────────┘ ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### Plugin & Infrastructure Layer

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                          INFRASTRUCTURE LAYER                                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  ┌─────────────────────────────────────────────────────────────────────────┐ ║
║  │                      🔌 PLUGIN ARCHITECTURE                             │ ║
║  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │ ║
║  │  │   Weather   │ │    Food     │ │   Events    │ │   Custom    │       │ ║
║  │  │   Plugin    │ │   Plugin    │ │   Plugin    │ │   Plugins   │       │ ║
║  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘       │ ║
║  │         │               │               │               │               │ ║
║  │         └───────────────┴───────────────┴───────────────┘               │ ║
║  │                                 │                                        │ ║
║  │                    ┌────────────▼────────────┐                          │ ║
║  │                    │    Plugin Registry     │                           │ ║
║  │                    │  • Auto-discovery      │                           │ ║
║  │                    │  • Lifecycle mgmt      │                           │ ║
║  │                    │  • Dependency resolve  │                           │ ║
║  │                    └─────────────────────────┘                          │ ║
║  └─────────────────────────────────────────────────────────────────────────┘ ║
║                                                                              ║
║  ┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────────┐ ║
║  │   🛡️ RESILIENCE      │ │   📊 OBSERVABILITY   │ │   💉 DEPENDENCY     │ ║
║  │                      │ │                      │ │      INJECTION      │ ║
║  │ • Circuit Breaker   │ │ • Metrics (Counter,  │ │                      │ ║
║  │ • Retry + Backoff   │ │   Gauge, Histogram)  │ │ • IoC Container     │ ║
║  │ • Timeout           │ │ • Distributed Trace  │ │ • Lifetime mgmt     │ ║
║  │ • Rate Limiter      │ │ • Health Checks      │ │ • Auto-wiring       │ ║
║  │ • Bulkhead          │ │ • Structured Logs    │ │ • Scoped deps       │ ║
║  └──────────────────────┘ └──────────────────────┘ └──────────────────────┘ ║
║                                                                              ║
║  ┌─────────────────────────────────────────────────────────────────────────┐ ║
║  │                        🎣 EVENT BUS & HOOKS                             │ ║
║  │                                                                         │ ║
║  │   Events:  AgentStarted → AgentCompleted → JudgeDecision → RouteComplete│ ║
║  │   Hooks:   @before_hook → @around_hook → @after_hook → @error_hook     │ ║
║  └─────────────────────────────────────────────────────────────────────────┘ ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### Data Flow Sequence

```
                                    TIME →
    
    User Input ──────┐
                     │
                     ▼
    Google Maps ─────┤ Returns 4 route points
                     │
                     ▼
    ┌────────────────┼────────────────────────────────────────────────────┐
    │ POINT 1        │                                                    │
    │                ▼                                                    │
    │   ┌─────────────────────────────────────────────────────────────┐  │
    │   │ Video ─────████████░░░░░░░░ (slower - YouTube API)          │  │
    │   │                    │ submit()                                │  │
    │   │ Music ─────████░░░░░░░░░░░░░ (faster)                       │  │
    │   │                │ submit()                                    │  │
    │   │ Text ──────██████░░░░░░░░░░░ (medium)                       │  │
    │   │                  │ submit()                                  │  │
    │   │                  ▼                                           │  │
    │   │ Queue ─────[1/3]──[2/3]──[3/3 READY!]                       │  │
    │   │                          │                                   │  │
    │   │                          ▼                                   │  │
    │   │ Judge ─────░░░░░░░░░░░░████ (evaluates all 3)               │  │
    │   └─────────────────────────────────────────────────────────────┘  │
    │                              │                                      │
    │                              ▼                                      │
    │   Decision: "TEXT - The Silent Monks of Latrun"                    │
    └────────────────────────────────────────────────────────────────────┘
                     │
                     ▼
    (Repeat for Points 2, 3, 4 - can run in parallel!)
                     │
                     ▼
    ┌────────────────────────────────────────────────────────────────────┐
    │                     FINAL PLAYLIST OUTPUT                          │
    │  Point 1: 📖 TEXT - "The Silent Monks of Latrun"                  │
    │  Point 2: 🎬 VIDEO - "Battle of Ammunition Hill"                  │
    │  Point 3: 🎵 MUSIC - "Jerusalem of Gold"                          │
    │  Point 4: 📖 TEXT - "Old City History"                            │
    └────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Installation

### Prerequisites

- Python 3.10+ 
- [UV](https://docs.astral.sh/uv/) - Ultra-fast Python package manager

### Step 1: Install UV

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with Homebrew
brew install uv
```

### Step 2: Clone & Setup

```bash
# Clone repository
git clone <your-repo-url>
cd Assignment4-multi-agent-tour-guide-parallel

# Full setup (creates venv + installs all dependencies)
make setup

# Or step by step:
uv venv              # Create virtual environment
uv sync              # Install production dependencies
uv sync --extra dev  # Include dev tools
```

### Step 3: Configure Environment

Create a `.env` file:

```bash
# Required for LLM-powered agents
OPENAI_API_KEY=sk-your-key-here

# Optional: Use Anthropic instead
ANTHROPIC_API_KEY=your-key-here

# Optional: Real API integrations
GOOGLE_MAPS_API_KEY=your-key
YOUTUBE_API_KEY=your-key
SPOTIFY_CLIENT_ID=your-id
SPOTIFY_CLIENT_SECRET=your-secret

# Optional: Weather plugin
OPENWEATHERMAP_API_KEY=your-key
```

### Verify Installation

```bash
# Check everything is working
make check

# Or run a quick test
uv run python main.py --demo --mode queue
```

---

## 🎮 Usage

### Basic Commands

```bash
# Demo mode (uses mock APIs, no keys needed)
uv run python main.py --demo

# Queue mode (recommended - shows synchronization)
uv run python main.py --demo --mode queue

# Interactive mode (prompts for input)
uv run python main.py --interactive

# Custom route
uv run python main.py --origin "Paris, France" --destination "Lyon, France"

# With user profile
uv run python main.py --demo --profile family --min-age 5
uv run python main.py --demo --profile history
```

### All Running Modes

| Mode | Command | Description |
|------|---------|-------------|
| **Queue** | `--mode queue` | ⭐ Recommended. Shows queue synchronization between agents |
| **Streaming** | `--mode streaming` | Real-time simulation, points arrive at intervals |
| **Instant** | `--mode instant` | Process all points in parallel immediately |
| **Sequential** | `--mode sequential` | Process one point at a time (debugging) |

### Makefile Commands

```bash
# === Running ===
make run              # Run demo mode
make run-queue        # Run with queue synchronization
make run-streaming    # Run streaming simulation
make run-api          # Start REST API server

# === Development ===
make test             # Run all tests
make test-cov         # Tests with coverage report
make lint             # Check code quality
make format           # Auto-format code

# === Package Management ===
make sync             # Install production deps
make dev              # Install dev deps
make all              # Install all deps
make add PKG=name     # Add a package
make upgrade          # Upgrade all packages

# === Cleanup ===
make clean            # Remove cache files
make clean-all        # Remove cache + venv
```

---

## 📡 Monitoring Traffic on All Hops

### Enable Verbose Logging

```bash
# Set log level to DEBUG to see all traffic
export LOG_LEVEL=DEBUG

# Run with full visibility
uv run python main.py --demo --mode queue 2>&1 | tee tour_log.txt
```

### Expected Output (Traffic on All Hops)

```
╔══════════════════════════════════════════════════════════════╗
║   🗺️  MULTI-AGENT TOUR GUIDE SYSTEM  🗺️                      ║
╚══════════════════════════════════════════════════════════════╝

🎭 Running DEMO MODE with sample route...

📬 Queue-based processing: Tel Aviv, Israel → Jerusalem, Israel
   Total points: 4
   Profile: default

🔄 Using QUEUE synchronization between agents and judge...

==================================================
📍 [1/4] Latrun
==================================================

[2024-11-29 10:15:32] 🎬 VideoAgent    | Starting search for "Latrun"
[2024-11-29 10:15:32] 🎵 MusicAgent    | Starting search for "Latrun"
[2024-11-29 10:15:32] 📖 TextAgent     | Starting search for "Latrun"
[2024-11-29 10:15:33] 🎵 MusicAgent    | ✅ Submitted to queue (1/3)
[2024-11-29 10:15:33] 📖 TextAgent     | ✅ Submitted to queue (2/3)
[2024-11-29 10:15:34] 🎬 VideoAgent    | ✅ Submitted to queue (3/3)
[2024-11-29 10:15:34] 📬 Queue         | ✅ All 3 agents ready!
[2024-11-29 10:15:34] ⚖️ JudgeAgent    | Evaluating 3 candidates...
[2024-11-29 10:15:35] ⚖️ JudgeAgent    | Decision: TEXT
[2024-11-29 10:15:35] ⚖️ JudgeAgent    | Reasoning: Historical monastery content...

   🏆 Winner: TEXT
      Title: The Silent Monks of Latrun
      Reason: Unique story about the monastery - more memorable than generic video

==================================================
📍 [2/4] Ammunition Hill
==================================================

[2024-11-29 10:15:35] 🎬 VideoAgent    | Starting search for "Ammunition Hill"
[2024-11-29 10:15:35] 🎵 MusicAgent    | Starting search for "Ammunition Hill"
[2024-11-29 10:15:35] 📖 TextAgent     | Starting search for "Ammunition Hill"
...

============================================================
🗺️  TOUR GUIDE PLAYLIST
============================================================
Route: Tel Aviv, Israel → Jerusalem, Israel
Total Points: 4
------------------------------------------------------------

📍 Point 1: Latrun
   (Latrun Monastery)
   📖 TEXT: The Silent Monks of Latrun
   🔗 https://en.wikipedia.org/wiki/Latrun
   💭 Unique story about the monastery - more memorable

📍 Point 2: Ammunition Hill
   (Ammunition Hill Memorial)
   🎬 VIDEO: Battle of Ammunition Hill Documentary
   🔗 https://youtube.com/watch?v=...
   💭 Historical significance demands visual content

📍 Point 3: Old City Jerusalem
   (Old City)
   🎵 MUSIC: Jerusalem of Gold
   🔗 https://open.spotify.com/track/...
   💭 Iconic arrival song - emotional impact

📍 Point 4: Mount of Olives
   (Mount of Olives)
   📖 TEXT: Ancient Burial Ground History
   🔗 https://en.wikipedia.org/wiki/Mount_of_Olives
   💭 Rich historical content about the location

============================================================

📊 Processing Statistics:
   total_points: 4
   successful_decisions: 4
   average_processing_time: 2.34s
   queue_timeouts: 0
   agents_failed: 0

✨ Tour guide generation complete!
```

### Monitor Specific Components

```bash
# Monitor only Queue operations
uv run python main.py --demo --mode queue 2>&1 | grep -E "(Queue|📬)"

# Monitor only Agent activity
uv run python main.py --demo --mode queue 2>&1 | grep -E "(Agent|🎬|🎵|📖)"

# Monitor only Judge decisions
uv run python main.py --demo --mode queue 2>&1 | grep -E "(Judge|⚖️|Winner|🏆)"

# Monitor timing
uv run python main.py --demo --mode queue 2>&1 | grep -E "(took|seconds|duration)"
```

### Real-time Metrics

```python
# In your code, access metrics:
from src.core.observability import MetricsRegistry

# Get all metrics
metrics = MetricsRegistry.collect_all()
print(metrics)

# Export in Prometheus format
print(MetricsRegistry.to_prometheus())
```

### Health Check Endpoint

```bash
# Start API server
make run-api

# Check health
curl http://localhost:8000/health

# Response:
{
    "status": "healthy",
    "checks": {
        "video_agent": {"status": "healthy", "latency_ms": 12},
        "music_agent": {"status": "healthy", "latency_ms": 8},
        "text_agent": {"status": "healthy", "latency_ms": 15},
        "judge_agent": {"status": "healthy", "latency_ms": 5}
    }
}
```

### Distributed Tracing

```python
# Access trace data
from src.core.observability import get_tracer

tracer = get_tracer("tour-guide")
spans = tracer.get_spans(limit=100)

for span in spans:
    print(f"{span.name}: {span.duration_ms}ms")
```

---

## 🔌 Plugin System

### Adding a New Agent (5 Minutes)

1. **Create plugin directory:**

```bash
mkdir -p plugins/food
```

2. **Create plugin manifest (`plugins/food/plugin.yaml`):**

```yaml
name: food
version: 1.0.0
description: Restaurant recommendations for route points
capabilities:
  - CONTENT_PROVIDER
enabled: true
```

3. **Implement plugin (`plugins/food/plugin.py`):**

```python
from src.core.plugins.base import BasePlugin
from src.core.plugins.registry import PluginRegistry

@PluginRegistry.register("food")
class FoodPlugin(BasePlugin):
    def _on_start(self):
        self.api = RestaurantAPI(self.config.api_key)
    
    def _on_stop(self):
        self.api.close()
    
    def find_restaurants(self, location: str):
        return self.api.search(location, limit=5)
```

4. **That's it!** The plugin is auto-discovered on startup.

### Available Plugins

| Plugin | Status | Description |
|--------|--------|-------------|
| `weather` | ✅ Included | Weather information for points |
| `food` | 🔧 Template | Restaurant recommendations |
| `events` | 📋 Planned | Local events and activities |
| `safety` | 📋 Planned | Safety alerts and warnings |

---

## ⚙️ Configuration

### Default Configuration (`config/default.yaml`)

```yaml
# Agent settings
agents:
  timeout_seconds: 30
  max_retries: 3
  parallel_workers: 3

# Queue settings
queue:
  expected_agents: 3
  soft_timeout_seconds: 15
  hard_timeout_seconds: 30
  min_required_agents: 1

# LLM settings
llm:
  provider: openai  # or anthropic
  model: gpt-4o-mini
  temperature: 0.7
  max_tokens: 1024

# Logging
logging:
  level: INFO
  format: structured
  include_thread_name: true
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `LOG_LEVEL` | Logging level | `INFO` |
| `MAX_CONCURRENT_THREADS` | Max thread pool size | `12` |
| `AGENT_TIMEOUT_SECONDS` | Agent execution timeout | `30` |
| `QUEUE_SOFT_TIMEOUT` | Wait time before accepting 2/3 | `15` |
| `QUEUE_HARD_TIMEOUT` | Wait time before accepting 1/3 | `30` |

---

## 🧪 Testing

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
uv run pytest tests/unit/test_queue.py -v

# Run integration tests
uv run pytest tests/integration/ -v

# Run e2e tests
uv run pytest tests/e2e/ -v
```

### Test Coverage Report

```bash
make test-cov
# Opens HTML report in browser
open htmlcov/index.html
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [MIT_PRODUCTION_ARCHITECTURE.md](docs/MIT_PRODUCTION_ARCHITECTURE.md) | Full architecture documentation |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design and data flow |
| [STARTUP_DESIGN.md](docs/STARTUP_DESIGN.md) | Production deployment design |
| [DEVELOPMENT_PROMPTS.md](docs/DEVELOPMENT_PROMPTS.md) | Prompts for building components |

---

## 🎓 Academic References

1. **Martin, R.C.** (2017). *Clean Architecture*. Prentice Hall.
2. **Gamma et al.** (1994). *Design Patterns*. Addison-Wesley.
3. **Nygard, M.T.** (2018). *Release It!* Pragmatic Bookshelf.
4. **Fowler, M.** (2002). *Patterns of Enterprise Application Architecture*. Addison-Wesley.

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file.

---

<div align="center">

**Built with ❤️ using production-grade architecture patterns**

*Parallel agents • Plugin architecture • Production-grade resilience*

</div>
