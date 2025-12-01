# 🚀 Operations Guide - Multi-Agent Tour Guide System

## Complete Guide to Installation, Features, and Execution

---

## 📋 Table of Contents

1. [Installation](#1-installation)
2. [API Keys Setup](#2-api-keys-setup)
3. [All Features Overview](#3-all-features-overview)
4. [Running Each Mode](#4-running-each-mode)
5. [Real Flow Execution](#5-real-flow-execution)
6. [Screenshot Guide](#6-screenshot-guide)
7. [API Operations](#7-api-operations)
8. [Dashboard Operations](#8-dashboard-operations)
9. [Testing Operations](#9-testing-operations)

---

## 1. Installation

### Step 1: Install UV Package Manager

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify
uv --version
```

### Step 2: Clone and Setup

```bash
# Navigate to project
cd /path/to/Assignment4-multi-agent-tour-guide-parallel

# Install all dependencies
make setup

# Or manually:
uv sync --all-extras
```

### Step 3: Configure API Keys

```bash
# Copy example env file
cp env.example .env

# Edit .env and add your API key
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" > .env
```

### Step 4: Verify Installation

```bash
# Check everything works
make check

# Or run tests
make test
```

---

## 2. API Keys Setup

📖 **Full Guide:** [API_KEYS_SETUP.md](API_KEYS_SETUP.md)

### Quick Summary

| API Key | Required? | Get It From | Purpose |
|---------|-----------|-------------|---------|
| **Anthropic Claude** | ✅ Required for real LLM | [console.anthropic.com](https://console.anthropic.com/) | Judge Agent |
| **Google Maps** | ⭐ Recommended | [console.cloud.google.com](https://console.cloud.google.com/) | Real routes |
| **YouTube** | Optional | Google Cloud Console | Real videos |
| **Spotify** | Optional | [developer.spotify.com](https://developer.spotify.com/dashboard) | Real music |

### Quick Setup

```bash
# 1. Copy env.example to .env
cp env.example .env

# 2. Edit .env with your API keys
nano .env  # or open with any editor

# 3. Add your keys:
ANTHROPIC_API_KEY=sk-ant-your-key-here
GOOGLE_MAPS_API_KEY=AIzaSy-your-key-here
```

---

## 3. All Features Overview

### 📊 Feature Matrix

| Feature | Command | Description |
|---------|---------|-------------|
| **Demo Mode** | `make run` | Basic demo with default settings |
| **Queue Mode** | `make run-queue` | Recommended - shows all hops with graceful degradation |
| **Streaming Mode** | `make run-streaming` | Real-time simulation with intervals |
| **Instant Mode** | `make run-instant` | All points processed in parallel |
| **Sequential Mode** | `make run-sequential` | One point at a time (debug) |
| **Family Mode** | `make run-family` | Child-friendly content filtering |
| **History Mode** | `make run-history` | In-depth historical content |
| **Verbose Mode** | `make run-verbose` | Debug logging (see all traffic) |
| **API Server** | `make run-api` | REST API on port 8000 |
| **Dashboard** | `make run-dashboard` | Interactive research dashboard |
| **Tests** | `make test` | Run 683+ tests |
| **Coverage** | `make test-cov` | Tests with coverage report |

---

## 3. Running Each Mode

### 🎯 Mode 1: Queue Mode (RECOMMENDED)

**What it does:** Processes each route point with Smart Queue graceful degradation (3→2→1 agents)

```bash
make run-queue
```

**Expected Output:**
```
📍 Route: Tel Aviv → Jerusalem (4 points)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 [1/4] Latrun
   ✅ Video Agent (1/3) ✅ Music Agent (2/3) ✅ Text Agent (3/3)
   🏆 Winner: 📖 TEXT - "The Silent Monks of Latrun"
   📊 Scores: TEXT=8.5 | VIDEO=7.2 | MUSIC=6.8
   ⏱️  Latency: 3.2s | Status: COMPLETE

📍 [2/4] Abu Ghosh
   ✅ Video Agent (1/3) ✅ Music Agent (2/3) ✅ Text Agent (3/3)
   🏆 Winner: 🎵 MUSIC - "Abu Ghosh Music Festival"
   📊 Scores: MUSIC=9.0 | TEXT=7.5 | VIDEO=6.3
   ⏱️  Latency: 2.8s | Status: COMPLETE

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Tour complete! 4/4 points processed
```

---

### 🎯 Mode 2: Demo Mode (Default)

**What it does:** Quick demo showing basic functionality

```bash
make run
# or
uv run python main.py --demo
```

---

### 🎯 Mode 3: Streaming Mode

**What it does:** Simulates real-time driving with timed intervals

```bash
make run-streaming
# or
uv run python main.py --demo --mode streaming --interval 5
```

**Expected Output:**
```
🚗 Starting streaming mode (interval: 5s)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏳ Point 1 arriving in 5 seconds...
📍 Processing: Latrun
   ✅ Content selected: TEXT - "The Silent Monks"
   
⏳ Point 2 arriving in 5 seconds...
📍 Processing: Abu Ghosh
   ✅ Content selected: MUSIC - "Abu Ghosh Festival"
```

---

### 🎯 Mode 4: Instant Mode

**What it does:** Processes all points in parallel simultaneously

```bash
make run-instant
# or
uv run python main.py --demo --mode instant
```

---

### 🎯 Mode 5: Sequential Mode (Debug)

**What it does:** Processes one point at a time for debugging

```bash
make run-sequential
# or
uv run python main.py --demo --mode sequential
```

---

### 🎯 Mode 6: Family Mode

**What it does:** Filters content for children (age 5+)

```bash
make run-family
# or
uv run python main.py --demo --mode queue --profile family --min-age 5
```

**Expected Output:**
```
👨‍👩‍👧 Family Mode Active (min age: 5)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 [1/4] Latrun
   🎬 VIDEO preferred for children
   🏆 Winner: 🎬 VIDEO - "Fun Facts about Latrun" (kid-friendly)
```

---

### 🎯 Mode 7: History Mode

**What it does:** In-depth historical content

```bash
make run-history
# or
uv run python main.py --demo --mode queue --profile history
```

---

### 🎯 Mode 8: Verbose/Debug Mode

**What it does:** Shows all internal traffic and logging

```bash
make run-verbose
# or
LOG_LEVEL=DEBUG uv run python main.py --demo --mode queue
```

**Expected Output:**
```
DEBUG:src.agents.video_agent:Starting video search for "Latrun"
DEBUG:src.core.smart_queue:Queue created for point_1 (timeout: 15s/30s)
DEBUG:src.agents.music_agent:Searching Spotify for "Latrun"
DEBUG:src.agents.text_agent:Fetching Wikipedia for "Latrun"
DEBUG:src.core.smart_queue:Result received: video (1/3)
DEBUG:src.core.smart_queue:Result received: music (2/3)
DEBUG:src.core.smart_queue:Result received: text (3/3)
DEBUG:src.core.smart_queue:Queue complete! Status: COMPLETE
DEBUG:src.agents.judge_agent:Evaluating 3 candidates...
```

---

### 🎯 Mode 9: Custom Route

**What it does:** Process a custom route

```bash
uv run python main.py --origin "Paris" --destination "Lyon"

# Or with specific mode
uv run python main.py --origin "New York" --destination "Boston" --mode queue
```

---

## 5. Real Flow Execution (With API Keys)

📖 **Full API Keys Guide:** [API_KEYS_SETUP.md](API_KEYS_SETUP.md)

### Prerequisites

Before running real flows, ensure you have API keys set in `.env`:

```bash
# Check your .env file
cat .env
```

### 🌍 Real Flow 1: Full Real Pipeline

**Requirements:** All API keys (Anthropic + Google Maps + YouTube + Spotify)

```bash
# Real route with real content from all sources
uv run python main.py \
  --origin "Paris, France" \
  --destination "Lyon, France" \
  --mode queue
```

**Expected Real Output:**
```
📍 Route: Paris, France → Lyon, France (8 points)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 [1/8] Eiffel Tower, Paris
   ✅ Video Agent: "Paris - City of Light" (YouTube)
   ✅ Music Agent: "La Vie en Rose - Édith Piaf" (Spotify)
   ✅ Text Agent: "The Eiffel Tower History" (Wikipedia)
   🏆 Winner: 🎬 VIDEO - "Paris - City of Light"
   📊 LLM Analysis: Selected video for visual impact of iconic landmark
```

---

### 🗺️ Real Flow 2: Real Routes Only

**Requirements:** Google Maps API key only

```bash
# Real Google Maps route, mock content
uv run python main.py \
  --origin "London, UK" \
  --destination "Manchester, UK" \
  --mode queue \
  --demo  # Use demo for mock content
```

---

### 🤖 Real Flow 3: Real LLM Judge Only

**Requirements:** Anthropic API key only

```bash
# Mock route, real LLM Judge decisions
make run-queue
```

---

### 👨‍👩‍👧 Real Flow 4: Family Trip

**Requirements:** All API keys recommended

```bash
uv run python main.py \
  --origin "Disneyland, Anaheim, CA" \
  --destination "Universal Studios, Hollywood, CA" \
  --mode queue \
  --profile family \
  --min-age 5
```

---

### 🚗 Real Flow 5: Road Trip (Driver Mode)

**Requirements:** All API keys recommended

```bash
uv run python main.py \
  --origin "San Francisco, CA" \
  --destination "Los Angeles, CA" \
  --mode queue \
  --profile driver
```

**Note:** Driver mode excludes video content (audio only for safety)

---

### 🇮🇱 Real Flow 6: Israel Tour

**Requirements:** All API keys recommended

```bash
uv run python main.py \
  --origin "Tel Aviv, Israel" \
  --destination "Jerusalem, Israel" \
  --mode queue
```

---

### 🇮🇹 Real Flow 7: European Tour

**Requirements:** All API keys recommended

```bash
uv run python main.py \
  --origin "Rome, Italy" \
  --destination "Florence, Italy" \
  --mode queue
```

---

### ⏱️ Real Flow 8: Streaming Simulation

**Requirements:** All API keys recommended

```bash
uv run python main.py \
  --origin "Amsterdam, Netherlands" \
  --destination "Brussels, Belgium" \
  --mode streaming \
  --interval 10
```

---

### 📊 API Keys Status Check

Run this to verify which APIs are configured:

```bash
uv run python -c "
from src.utils.config import settings
print('=' * 50)
print('API KEYS STATUS')
print('=' * 50)
print(f'Anthropic:   {'✅ SET' if settings.anthropic_api_key else '❌ NOT SET'}')
print(f'Google Maps: {'✅ SET' if settings.google_maps_api_key else '❌ NOT SET (using mock)'}')
print(f'YouTube:     {'✅ SET' if settings.youtube_api_key else '❌ NOT SET (using mock)'}')
print(f'Spotify:     {'✅ SET' if settings.spotify_client_id else '❌ NOT SET (using mock)'}')
print('=' * 50)
"
```

---

## 6. Screenshot Guide

### Taking Screenshots

**macOS:**
- Full screen: `Cmd + Shift + 3`
- Selection: `Cmd + Shift + 4`
- Window: `Cmd + Shift + 4`, then `Space`, click window

**Recommended Screenshots to Capture:**

| # | Screenshot | Command to Run First |
|---|------------|---------------------|
| 1 | Queue Mode Output | `make run-queue` |
| 2 | Graceful Degradation | Run with slow network |
| 3 | Family Mode | `make run-family` |
| 4 | Verbose Logging | `make run-verbose` |
| 5 | API Health Check | `curl localhost:8000/health` |
| 6 | Test Results | `make test` |
| 7 | Coverage Report | `make test-cov && open htmlcov/index.html` |
| 8 | Dashboard | `make run-dashboard` |

---

## 5. API Operations

### Start API Server

```bash
make run-api
# Server starts at http://localhost:8000
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/tour` | POST | Process a tour |
| `/docs` | GET | Swagger UI |
| `/redoc` | GET | ReDoc documentation |

### Test API

```bash
# Health check
curl http://localhost:8000/health

# Process tour
curl -X POST http://localhost:8000/tour \
  -H "Content-Type: application/json" \
  -d '{"origin": "Tel Aviv", "destination": "Jerusalem"}'

# Open Swagger docs
open http://localhost:8000/docs
```

---

## 6. Dashboard Operations

### Start Dashboard

```bash
# If run_dashboard.py exists:
uv run python run_dashboard.py

# Or directly:
uv run python -m src.dashboard.app
```

### Dashboard Features

| Panel | Function |
|-------|----------|
| System Monitor | Real-time agent performance |
| Monte Carlo | Sensitivity simulations |
| Pareto Frontier | Quality-Latency tradeoffs |
| Statistical Comparison | A/B testing |

---

## 7. Testing Operations

### Run All Tests

```bash
make test
```

### Run Specific Test Categories

```bash
# Unit tests only
make test-unit

# Integration tests
make test-integration

# E2E tests (requires API keys)
make test-e2e

# With coverage
make test-cov
```

### View Coverage Report

```bash
make test-cov
open htmlcov/index.html
```

### Run Specific Test Files

```bash
# Smart Queue tests
uv run pytest tests/unit/test_smart_queue.py -v

# Circuit Breaker tests
uv run pytest tests/unit/test_circuit_breaker.py -v

# Judge Agent tests
uv run pytest tests/unit/test_judge_agent.py -v
```

---

## 📸 Quick Screenshot Workflow

### Step-by-Step for All Features

```bash
# 1. Queue Mode (main feature)
make run-queue
# Screenshot the colorful output

# 2. Test Suite
make test
# Screenshot showing 683+ tests passing

# 3. Coverage
make test-cov
open htmlcov/index.html
# Screenshot the coverage report

# 4. API
make run-api &
curl localhost:8000/health
open http://localhost:8000/docs
# Screenshot Swagger UI

# 5. Family Mode
make run-family
# Screenshot kid-friendly output

# 6. Verbose/Debug
make run-verbose
# Screenshot detailed logging
```

---

## 📁 Save Screenshots To

```
assets/images/
├── architecture-overview.png     ✅ Already have
├── queue-mode-output.png        📸 To capture
├── test-results.png             📸 To capture
├── coverage-report.png          📸 To capture
├── api-swagger.png              📸 To capture
├── family-mode.png              📸 To capture
├── dashboard-overview.png       📸 To capture
└── verbose-logging.png          📸 To capture
```

---

**Document Version:** 1.0.0  
**Last Updated:** December 2025

