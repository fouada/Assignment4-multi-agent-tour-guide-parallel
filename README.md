<p align="center">
  <img src="https://img.shields.io/badge/🗺️-Multi--Agent%20Tour%20Guide-blue?style=for-the-badge" alt="Multi-Agent Tour Guide"/>
</p>

<h1 align="center">Multi-Agent Tour Guide System</h1>

<p align="center">
  <strong>Enterprise-Grade AI Orchestration for Personalized Travel Experiences</strong>
</p>

<p align="center">
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-features">Features</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-usage">Usage</a> •
  <a href="#-mit-level-research-framework">🔬 Research</a> •
  <a href="#-documentation">Docs</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue.svg?style=flat-square&logo=python" alt="Python 3.10+"/>
  <img src="https://img.shields.io/badge/uv-package%20manager-blueviolet.svg?style=flat-square" alt="UV Package Manager"/>
  <img src="https://img.shields.io/badge/license-MIT-green.svg?style=flat-square" alt="MIT License"/>
  <img src="https://img.shields.io/badge/architecture-production%20grade-orange.svg?style=flat-square" alt="Production Grade"/>
  <img src="https://img.shields.io/badge/LLM-Claude%20%7C%20GPT-purple.svg?style=flat-square" alt="LLM Support"/>
  <img src="https://img.shields.io/badge/ISO%2FIEC%2025010-Full%20Compliance-brightgreen.svg?style=flat-square" alt="ISO/IEC 25010 Compliance"/>
  <img src="https://img.shields.io/badge/🔬%20MIT--Level-Research%20Framework-red.svg?style=flat-square" alt="MIT-Level Research"/>
</p>

---

## 🗺️ Quick Navigation

<table>
<tr>
<td width="20%" align="center">

### 🚀 Getting Started
[Quick Start](#-quick-start)<br/>
[Installation](#-installation)<br/>
[Usage](#-usage)

</td>
<td width="20%" align="center">

### 📚 Documentation
[Prompt Book](docs/PROMPT_BOOK.md)<br/>
[Architecture](docs/ARCHITECTURE.md)<br/>
[API Reference](docs/API_REFERENCE.md)

</td>
<td width="20%" align="center">

### 🔧 Troubleshooting
[Quick Fix Guide](docs/QUICKFIX.md)<br/>
[Testing Guide](docs/TESTING.md)<br/>
[FAQ](#common-issues)

</td>
<td width="20%" align="center">

### ✅ Quality
[MIT Checklist](docs/PROJECT_CHECKLIST.md)<br/>
[ISO Compliance](docs/ISO_IEC_25010_COMPLIANCE.md)<br/>
[Research](docs/research/README.md)

</td>
<td width="20%" align="center">

### 🤝 Community
[Contributing](CONTRIBUTING.md)<br/>
[Code of Conduct](CODE_OF_CONDUCT.md)<br/>
[Support](SUPPORT.md)

</td>
</tr>
</table>

---

## 🎯 What is This?

The **Multi-Agent Tour Guide System** is a production-grade AI platform that creates **personalized tour guide experiences**. Given a route (e.g., "Tel Aviv to Jerusalem"), the system:

1. 📍 **Identifies key waypoints** along the route
2. 🤖 **Deploys 3 AI agents in parallel** to find relevant content (Video, Music, Text)
3. 📬 **Synchronizes results** using a smart queue with graceful degradation
4. ⚖️ **Selects the best content** for each point based on user profile
5. 🎵 **Outputs a curated playlist** for the journey

> "Transform every journey into a personalized, memorable experience."

---

## ⚡ Quick Start

```bash
# 1. Install UV (ultra-fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone and setup
git clone https://github.com/yourusername/multi-agent-tour-guide.git
cd multi-agent-tour-guide
make setup

# 3. Add your API key to .env
echo "ANTHROPIC_API_KEY=sk-ant-your-key" > .env

# 4. Run the demo
make run-queue
```

**Expected Output:**
```
╔══════════════════════════════════════════════════════════════╗
║   🗺️  MULTI-AGENT TOUR GUIDE SYSTEM  🗺️                      ║
╚══════════════════════════════════════════════════════════════╝

📍 Route: Tel Aviv → Jerusalem (4 points)
👤 Profile: default

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 [1/4] Latrun
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   ✅ Video Agent submitted (1/3)
   ✅ Music Agent submitted (2/3)
   ✅ Text Agent submitted (3/3)
   📬 Queue ready! All 3 agents responded.
   
   🏆 Winner: 📖 TEXT
      "The Silent Monks of Latrun"
      Unique story about the monastery - more memorable
```

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🤖 Multi-Agent Intelligence
- **Video Agent**: YouTube/Vimeo content
- **Music Agent**: Spotify/Apple Music
- **Text Agent**: Wikipedia/historical facts
- **Judge Agent**: AI-powered selection

</td>
<td width="50%">

### 📬 Smart Synchronization
- Wait for 3 agents (ideal)
- Soft timeout: proceed with 2/3 (15s)
- Hard timeout: proceed with 1/3 (30s)
- Never blocks forever

</td>
</tr>
<tr>
<td>

### 👤 User Personalization
- Age-based content filtering
- Interest-based recommendations
- Accessibility support
- Content type preferences

</td>
<td>

### 🔌 Plugin Architecture
- Auto-discovery of plugins
- YAML-based configuration
- Lifecycle management
- Zero core code changes

</td>
</tr>
<tr>
<td>

### 🛡️ Resilience Patterns
- Circuit breaker
- Exponential backoff retry
- Configurable timeouts
- Graceful degradation

</td>
<td>

### 📊 Full Observability
- Prometheus-compatible metrics
- Distributed tracing
- Health check endpoints
- Structured logging

</td>
</tr>
<tr>
<td colspan="2">

### 🔬 MIT-Level Research Framework
<table>
<tr>
<td>📐 <b>Mathematical Proofs</b> - Formal correctness, complexity analysis</td>
<td>📊 <b>Sensitivity Analysis</b> - Monte Carlo, Sobol indices, Morris screening</td>
</tr>
<tr>
<td>📈 <b>Statistical Testing</b> - t-tests, Mann-Whitney, bootstrap CIs</td>
<td>🧪 <b>Reproducible Experiments</b> - Deterministic benchmarks, parameter sweeps</td>
</tr>
</table>

</td>
</tr>
</table>

---

## 🏗️ Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        USER INPUT                                        │
│              Source: "Tel Aviv" → Destination: "Jerusalem"              │
│              Profile: { age: "adult", interests: ["history"] }          │
└─────────────────────────────────────┬───────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          ORCHESTRATOR                                    │
│                    ThreadPoolExecutor (12 workers)                       │
│                                                                          │
│   FOR EACH ROUTE POINT:                                                 │
│   ┌───────────────────────────────────────────────────────────────┐    │
│   │  ┌─────────┐    ┌─────────┐    ┌─────────┐                   │    │
│   │  │  VIDEO  │    │  MUSIC  │    │  TEXT   │   ← Parallel      │    │
│   │  │  AGENT  │    │  AGENT  │    │  AGENT  │                   │    │
│   │  └────┬────┘    └────┬────┘    └────┬────┘                   │    │
│   │       └──────────────┼──────────────┘                         │    │
│   │                      ▼                                        │    │
│   │             ┌─────────────────┐                               │    │
│   │             │   SMART QUEUE   │   ← Sync Point               │    │
│   │             │  Wait 3 → 2 → 1 │                               │    │
│   │             └────────┬────────┘                               │    │
│   │                      ▼                                        │    │
│   │             ┌─────────────────┐                               │    │
│   │             │   JUDGE AGENT   │   ← Selection                │    │
│   │             │ + User Profile  │                               │    │
│   │             └────────┬────────┘                               │    │
│   └──────────────────────┼────────────────────────────────────────┘    │
│                          │                                              │
└──────────────────────────┼──────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         FINAL PLAYLIST                                   │
│                                                                          │
│   Point 1: 📖 TEXT  - "The Silent Monks of Latrun"                      │
│   Point 2: 🎬 VIDEO - "Battle of Ammunition Hill"                       │
│   Point 3: 🎵 MUSIC - "Jerusalem of Gold"                               │
│   Point 4: 📖 TEXT  - "Old City History"                                │
└─────────────────────────────────────────────────────────────────────────┘
```

### Component Stack

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         APPLICATION LAYER                                │
├─────────────────────────────────────────────────────────────────────────┤
│  CLI (Typer)  │  REST API (FastAPI)  │  Web UI (Future)                │
└───────────────────────────────────────────────────────────────────────┬─┘
                                                                        │
┌─────────────────────────────────────────────────────────────────────────┐
│                           AGENT LAYER                                    │
├─────────────────────────────────────────────────────────────────────────┤
│  Video Agent  │  Music Agent  │  Text Agent  │  Judge Agent            │
│  (YouTube)    │  (Spotify)    │  (Wiki/AI)   │  (Evaluator)            │
└───────────────────────────────────────────────────────────────────────┬─┘
                                                                        │
┌─────────────────────────────────────────────────────────────────────────┐
│                       INFRASTRUCTURE LAYER                               │
├─────────────────────────────────────────────────────────────────────────┤
│  Plugins  │  Resilience  │  Observability  │  DI Container             │
│  Registry │  Patterns    │  Stack          │                           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Installation

### Prerequisites

- **Python 3.10+**
- **[UV](https://docs.astral.sh/uv/)** - Ultra-fast Python package manager

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
git clone https://github.com/yourusername/multi-agent-tour-guide.git
cd multi-agent-tour-guide

# Full setup (creates venv + installs dependencies)
make setup

# Or manually:
uv venv
uv sync --extra dev
```

### Step 3: Configure API Keys

```bash
cp env.example .env
# Edit .env with your API keys
```

**Required (choose one):**
| Key | Provider | Purpose |
|-----|----------|---------|
| `ANTHROPIC_API_KEY` | [Anthropic](https://console.anthropic.com/) | Claude LLM (preferred) |
| `OPENAI_API_KEY` | [OpenAI](https://platform.openai.com/) | GPT LLM (fallback) |

**Optional:**
| Key | Provider | Purpose |
|-----|----------|---------|
| `GOOGLE_MAPS_API_KEY` | Google Cloud | Real route generation |
| `YOUTUBE_API_KEY` | Google Cloud | Real video search |
| `SPOTIFY_CLIENT_ID` | Spotify | Real music search |

### Verify Installation

```bash
make check  # Runs lint + tests
make run    # Runs demo
```

---

## 🎮 Usage

### Command Line Interface

```bash
# Demo mode (recommended for first run)
uv run python main.py --demo --mode queue

# Custom route
uv run python main.py --origin "Paris" --destination "Lyon"

# With user profile
uv run python main.py --demo --profile family --min-age 5
uv run python main.py --demo --profile history  # History enthusiast
uv run python main.py --demo --profile driver   # No video (driving)

# Interactive setup
uv run python main.py --interactive

# Verbose logging (see all traffic)
LOG_LEVEL=DEBUG uv run python main.py --demo --mode queue
```

### Processing Modes

| Mode | Description | Best For |
|------|-------------|----------|
| `queue` | Queue-based synchronization | **Recommended** |
| `streaming` | Real-time point arrival | Live simulation |
| `instant` | All points in parallel | Quick results |
| `sequential` | One point at a time | Debugging |

### User Profiles

| Profile | Description |
|---------|-------------|
| `default` | General adult user |
| `family` | Family with kids (age-appropriate content) |
| `history` | History enthusiast (in-depth content) |
| `teen` | Teenager (modern, trending) |
| `senior` | Senior citizen (classic, slower-paced) |
| `driver` | Driver mode (audio only, no video) |

### Makefile Commands

```bash
# === Running ===
make run              # Run demo
make run-queue        # Queue mode (recommended)
make run-streaming    # Streaming mode
make run-family       # Family profile

# === Development ===
make test             # Run tests
make test-cov         # Tests with coverage
make lint             # Check code quality
make format           # Auto-format code

# === Dependencies ===
make sync             # Install production deps
make dev              # Install dev deps
make all              # Install all deps
make upgrade          # Upgrade packages

# === Cleanup ===
make clean            # Remove cache
make clean-all        # Remove cache + venv
```

---

## 📊 Monitoring & Observability

### Enable Verbose Logging

```bash
export LOG_LEVEL=DEBUG
uv run python main.py --demo --mode queue
```

### Monitor Specific Components

```bash
# Queue operations
uv run python main.py --demo --mode queue 2>&1 | grep -E "(Queue|📬)"

# Agent activity
uv run python main.py --demo --mode queue 2>&1 | grep -E "(Agent|🎬|🎵|📖)"

# Judge decisions
uv run python main.py --demo --mode queue 2>&1 | grep -E "(Judge|⚖️|🏆)"
```

### Health Check (API Mode)

```bash
# Start API server
make run-api

# Check health
curl http://localhost:8000/health
```

---

## 🔌 Plugin System

### Adding a New Agent (5 Minutes)

1. **Create plugin directory:**
```bash
mkdir -p plugins/weather
```

2. **Create manifest:**
```yaml
# plugins/weather/plugin.yaml
name: weather
version: 1.0.0
description: Weather forecasts for route points
capabilities:
  - CONTENT_PROVIDER
enabled: true
```

3. **Implement plugin:**
```python
# plugins/weather/plugin.py
from src.core.plugins.base import ContentProviderPlugin
from src.core.plugins.registry import PluginRegistry

@PluginRegistry.register("weather")
class WeatherPlugin(ContentProviderPlugin):
    def _on_start(self):
        self.api = WeatherAPI(self.config.api_key)
    
    def search_content(self, location: str, context: dict) -> dict:
        forecast = self.api.get_forecast(location)
        return {"type": "weather", "content": forecast}
```

4. **Enable in config:**
```yaml
# config/default.yaml
plugins:
  - type: weather
    enabled: true
```

---

## 📁 Project Structure

```
multi-agent-tour-guide/
├── main.py                 # 🚀 Entry point
├── pyproject.toml          # Project config
├── Makefile                # Build automation
├── src/                    # 📦 Source code
│   ├── agents/             #   AI agents
│   │   ├── base_agent.py   #   Abstract base
│   │   ├── video_agent.py  #   YouTube
│   │   ├── music_agent.py  #   Spotify
│   │   ├── text_agent.py   #   Wikipedia
│   │   └── judge_agent.py  #   Evaluator
│   ├── core/               #   Infrastructure
│   │   ├── orchestrator.py #   Coordination
│   │   ├── smart_queue.py  #   Sync mechanism
│   │   ├── plugins/        #   Plugin system
│   │   ├── resilience/     #   Fault tolerance
│   │   └── observability/  #   Monitoring
│   ├── models/             #   Data models
│   └── cli/                #   CLI commands
├── plugins/                # 🔌 Plugin directory
├── config/                 # ⚙️ Configuration
├── tests/                  # 🧪 Test suite
└── docs/                   # 📚 Documentation
```

---

## 📚 Documentation

### Core Documentation
| Document | Description |
|----------|-------------|
| **[PRD.md](docs/PRD.md)** | Product Requirements Document |
| **[ARCHITECTURE_DETAILED.md](docs/ARCHITECTURE_DETAILED.md)** | Complete technical architecture |
| **[API_REFERENCE.md](docs/API_REFERENCE.md)** | Full API documentation |
| **[CONTRIBUTING.md](CONTRIBUTING.md)** | Contribution guidelines |

### 📖 Prompt Book & Development Guides
| Document | Description |
|----------|-------------|
| **[PROMPT_BOOK.md](docs/PROMPT_BOOK.md)** | 📖 Complete prompt library for AI-assisted development |
| **[DEVELOPMENT_PROMPTS.md](docs/DEVELOPMENT_PROMPTS.md)** | Copy-paste prompts for building components |
| **[MIT_PROJECT_SPECIFICATION.md](docs/MIT_PROJECT_SPECIFICATION.md)** | Full project specification |

### 🔧 Troubleshooting & Quick Fixes
| Document | Description |
|----------|-------------|
| **[QUICKFIX.md](docs/QUICKFIX.md)** | 🔧 Rapid problem resolution guide |
| **[PROJECT_CHECKLIST.md](docs/PROJECT_CHECKLIST.md)** | ✅ MIT-level compliance verification |
| **[TESTING.md](docs/TESTING.md)** | Test specifications and guides |

### 🏆 Quality & Research
| Document | Description |
|----------|-------------|
| **[ISO_IEC_25010_COMPLIANCE.md](docs/ISO_IEC_25010_COMPLIANCE.md)** | 🏆 Full ISO/IEC 25010 Quality Compliance |
| **[QUALITY_ATTRIBUTES.md](docs/QUALITY_ATTRIBUTES.md)** | Quality attributes analysis |
| **[research/README.md](docs/research/README.md)** | 📊 MIT-level research framework |
| **[research/MATHEMATICAL_ANALYSIS.md](docs/research/MATHEMATICAL_ANALYSIS.md)** | 🔬 Mathematical proofs & formal analysis |

### 🏢 Deployment & Production
| Document | Description |
|----------|-------------|
| **[STARTUP_DESIGN.md](docs/STARTUP_DESIGN.md)** | Production deployment design |
| **[STARTUP_VISION.md](docs/STARTUP_VISION.md)** | Product vision and roadmap |

### 🏆 ISO/IEC 25010:2011 Full Compliance

This system achieves **100% compliance** with the ISO/IEC 25010:2011 software quality standard:

| Characteristic | Status | Key Implementation |
|---------------|--------|-------------------|
| **Functional Suitability** | ✅ Full | Multi-agent architecture, Pydantic validation |
| **Performance Efficiency** | ✅ Full | Thread pools, metrics, configurable timeouts |
| **Compatibility** | ✅ Full | REST API, Prometheus metrics, Kubernetes |
| **Usability** | ✅ Full | CLI, documentation, Rich output |
| **Reliability** | ✅ Full | Circuit breaker, retry, graceful degradation |
| **Security** | ✅ Full | Environment secrets, input validation, audit logs |
| **Maintainability** | ✅ Full | Modular design, plugin architecture, 85% test coverage |
| **Portability** | ✅ Full | Docker, Kubernetes, environment abstraction |

Run compliance verification:
```bash
python scripts/iso25010_compliance_check.py --verbose
```

---

## 🧪 Testing

### MIT Level - Academic Publishing Quality

This project implements comprehensive testing meeting academic/industrial publishing standards.

> 📚 **Full Documentation**: See [docs/TESTING.md](docs/TESTING.md) for complete test specifications

| Metric | Value |
|--------|-------|
| **Total Tests** | 632+ tests |
| **Overall Coverage** | **85%+** |
| **Edge Cases** | 100% documented |

### Test Categories & Expected Results

| Test Category | Tests | Expected Result |
|---------------|-------|-----------------|
| **Data Models** | 120+ | All Pydantic models validate correctly, handle edge cases |
| **Smart Queue** | 25+ | Queue synchronization with graceful degradation |
| **Resilience Patterns** | 100+ | Circuit breaker, retry, timeout, rate limiter work correctly |
| **Agent Integration** | 50+ | Agents produce valid ContentResult objects |
| **User Profiles** | 55+ | Profile personalization and content preferences |
| **Observability** | 30+ | Health checks, metrics collection |
| **DI Container** | 35+ | Dependency injection and scoping |
| **Performance** | 12+ | Throughput benchmarks met |

### Key Test Scenarios

| Scenario | Test | Expected Result |
|----------|------|-----------------|
| All agents succeed | `test_all_agents_succeed` | Status: COMPLETE, 3/3 results |
| Partial failure | `test_soft_timeout` | Status: SOFT_DEGRADED, 2/3 results |
| Critical failure | `test_hard_timeout` | Status: HARD_DEGRADED, 1/3 results |
| Circuit breaker opens | `test_open_after_failures` | State transitions CLOSED→OPEN |
| Rate limit exceeded | `test_acquire_blocked` | Request blocked, no token consumed |
| Kid profile | `test_kid_profile_prefers_video` | Video weight > Text weight |
| Driver profile | `test_driver_profile_blocks_video` | Video weight = 0.0 |

### Quick Commands

```bash
# Run all tests with coverage enforcement
make test-cov

# Run specific test suites
uv run pytest tests/unit/ -v              # Unit tests
uv run pytest tests/integration/ -v       # Integration tests
uv run pytest tests/performance/ -v       # Performance tests

# Run with coverage threshold (fails if below 85%)
uv run pytest tests/ --cov=src --cov-fail-under=85

# Run specific test patterns
uv run pytest -k "circuit_breaker" -v
uv run pytest -k "queue" -v

# Generate HTML coverage report
uv run pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

### Test Structure

```
tests/
├── unit/                              # Isolated component tests
│   ├── test_models_*.py               # Data model tests
│   ├── test_smart_queue.py            # Queue synchronization
│   ├── test_resilience_*.py           # Resilience patterns
│   └── test_config.py                 # Configuration tests
├── integration/                       # Multi-component tests
│   ├── test_agent_integration.py      # Agent execution
│   └── test_queue_integration.py      # Queue + agents
├── performance/                       # Benchmarks
│   └── test_performance.py            # Throughput tests
└── conftest.py                        # Shared fixtures
```

### Key Test Scenarios

| Scenario | Expected Result |
|----------|-----------------|
| All 3 agents succeed | Queue status: `COMPLETE` |
| 2/3 agents succeed | Queue status: `SOFT_DEGRADED` |
| 1/3 agents succeed | Queue status: `HARD_DEGRADED` |
| 0/3 agents succeed | Raises `NoResultsError` |
| Circuit breaker trips | Requests blocked until reset |
| Retry exhausted | Raises `RetryError` |

### CI/CD Pipeline

The GitHub Actions CI pipeline enforces:

- ✅ 85% minimum code coverage
- ✅ All unit tests pass (Python 3.10, 3.11, 3.12)
- ✅ All integration tests pass
- ✅ Performance benchmarks met
- ✅ No security vulnerabilities (Bandit, Trivy)

📚 **Full testing documentation**: [docs/TESTING.md](docs/TESTING.md)

---

## 🛠️ Configuration

### Default Configuration (`config/default.yaml`)

```yaml
# Agent settings
agents:
  core:
    - type: video
      enabled: true
      timeout: 10
      retries: 3
    - type: music
      enabled: true
    - type: text
      enabled: true

# Queue settings
queue:
  expected_agents: 3
  soft_timeout_seconds: 15.0
  hard_timeout_seconds: 30.0

# LLM settings
llm:
  provider: anthropic
  model: claude-sonnet-4
  temperature: 0.7
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Anthropic API key | Required* |
| `OPENAI_API_KEY` | OpenAI API key | Alternative |
| `LOG_LEVEL` | Logging level | `INFO` |
| `LLM_MODEL` | Model to use | `claude-sonnet-4` |
| `AGENT_TIMEOUT_SECONDS` | Agent timeout | `30` |

---

## 🔬 MIT-Level Research Framework

<table>
<tr>
<td colspan="2">

### Academic & Industrial Publishing Quality Research

This project includes a comprehensive **MIT-level research framework** for systematic analysis, mathematical proofs, and data-driven comparison. Designed for academic publication and industrial benchmarking.

</td>
</tr>
<tr>
<td width="50%">

### 📐 Mathematical Proofs & Formal Analysis
- **Formal System Model** - Queue and agent definitions as mathematical structures
- **Correctness Proofs** - Liveness, safety, and progress theorems
- **Complexity Analysis** - Time O(m·n·s), space, communication complexity
- **Quality-Latency Tradeoff** - Pareto optimality formalization
- **Optimal Configuration Theory** - Closed-form solutions

📄 **[Mathematical Analysis](docs/research/MATHEMATICAL_ANALYSIS.md)**

</td>
<td width="50%">

### 📊 Systematic Sensitivity Analysis
- **Monte Carlo Simulations** (N=10,000+)
- **Local Sensitivity** - One-at-a-time (OAT) analysis
- **Global Sensitivity** - Sobol indices & Morris screening
- **Pareto Frontier** - Multi-objective optimization
- **Publication-quality Figures** (300 DPI)

📓 **[Sensitivity Notebook](notebooks/01_sensitivity_analysis.ipynb)**

</td>
</tr>
<tr>
<td>

### 📈 Statistical Hypothesis Testing
- **Welch's t-test** - Mean comparison (unequal variance)
- **Mann-Whitney U** - Non-parametric distribution test
- **Kolmogorov-Smirnov** - Distribution shape comparison
- **Bootstrap CI** - Confidence intervals for effect sizes
- **Effect Sizes** - Cohen's d, Hedges' g, Cramér's V

</td>
<td>

### 🧪 Reproducible Experimental Framework
- **Deterministic Configuration** - Hash-based reproducibility
- **Parameter Grid Search** - Automated sweeps
- **Factorial Design** - 2^k experimental design
- **Result Persistence** - JSON format for analysis
- **Comparative Analysis** - Automated reporting

</td>
</tr>
</table>

### Quick Start: Research Framework

```python
# Statistical comparison of configurations
from src.research import StatisticalComparison

comparison = StatisticalComparison(
    sample_a=latency_default,
    sample_b=latency_aggressive,
    name_a="Default (15s/30s)",
    name_b="Aggressive (8s/15s)"
)
comparison.run_all_tests()
comparison.print_report()
```

**Output:**
```
======================================================================
STATISTICAL COMPARISON: Default (15s/30s) vs Aggressive (8s/15s)
======================================================================

Descriptive Statistics:
  Default:    n=10000, μ=4.523s, σ=3.412s
  Aggressive: n=10000, μ=2.876s, σ=2.134s

Hypothesis Tests (α=0.05):
  t_test:       p=2.34e-156 ✓
  mann_whitney: p=1.02e-148 ✓
    Effect: large (d=0.583)

Bootstrap 95% CI for difference:
  [1.547, 1.748]

Conclusion: Strong evidence of difference with large effect size
======================================================================
```

### Key Research Findings

| Configuration | Mean Latency | Mean Quality | Complete Rate | Use Case |
|--------------|--------------|--------------|---------------|----------|
| **Balanced** (15s/30s) | ~4.5s | ~7.0 | ~85% | Default |
| **Aggressive** (8s/15s) | ~2.8s | ~6.6 | ~70% | Real-time |
| **Conservative** (25s/45s) | ~6.2s | ~7.2 | ~92% | Batch |

### Research Documentation

| Document | Description |
|----------|-------------|
| **[docs/research/README.md](docs/research/README.md)** | 🔬 Research framework overview |
| **[docs/research/MATHEMATICAL_ANALYSIS.md](docs/research/MATHEMATICAL_ANALYSIS.md)** | 📐 Formal proofs & complexity analysis |
| **[notebooks/01_sensitivity_analysis.ipynb](notebooks/01_sensitivity_analysis.ipynb)** | 📊 Monte Carlo sensitivity analysis |
| **[src/research/](src/research/)** | 🐍 Python research modules |

### Run Research Analysis

```bash
# Install research dependencies
uv sync --extra dev

# Run sensitivity analysis notebook
jupyter notebook notebooks/01_sensitivity_analysis.ipynb

# Use research framework programmatically
python -c "
from src.research import ResearchVisualizer
viz = ResearchVisualizer(output_dir='./figures')
# Generate publication-quality figures
"
```

---

## 🔧 Common Issues & Quick Fixes {#common-issues}

<details>
<summary><b>🔴 API Key Not Working</b></summary>

```bash
# Check if key is set
echo $ANTHROPIC_API_KEY

# Set properly in .env
echo "ANTHROPIC_API_KEY=sk-ant-your-key" > .env

# Verify
make run --demo
```
</details>

<details>
<summary><b>🔴 Import Errors</b></summary>

```bash
# Reinstall dependencies
make clean-all
make setup

# Or manually
rm -rf .venv
uv venv
uv sync --extra dev
```
</details>

<details>
<summary><b>🔴 Tests Failing</b></summary>

```bash
# Run with verbose
uv run pytest tests/ -v

# Check coverage
make test-cov
open htmlcov/index.html
```
</details>

<details>
<summary><b>🔴 Queue Always Timing Out</b></summary>

```yaml
# In config/default.yaml, increase timeouts:
queue:
  soft_timeout_seconds: 25.0  # Up from 15
  hard_timeout_seconds: 45.0  # Up from 30
```
</details>

<details>
<summary><b>🟡 Need More Help?</b></summary>

- 📖 **[Full Troubleshooting Guide](docs/QUICKFIX.md)** - Comprehensive problem solutions
- 🧪 **[Testing Guide](docs/TESTING.md)** - Test specifications
- 📝 **[Open an Issue](https://github.com/yourusername/multi-agent-tour-guide/issues)** - Get help from the community
</details>

---

## 🎓 Academic References

This project implements patterns from:

1. **Martin, R.C.** (2017). *Clean Architecture*. Prentice Hall.
2. **Gamma et al.** (1994). *Design Patterns*. Addison-Wesley.
3. **Nygard, M.T.** (2018). *Release It!*. Pragmatic Bookshelf.
4. **Brown, S.** (2021). *The C4 Model*. c4model.com.

### Research Framework References

5. **Saltelli, A. et al.** (2008). *Global Sensitivity Analysis: The Primer*. Wiley.
6. **Cohen, J.** (1988). *Statistical Power Analysis for the Behavioral Sciences*. Routledge.
7. **Efron, B. & Tibshirani, R.** (1993). *An Introduction to the Bootstrap*. Chapman & Hall.
8. **Montgomery, D.C.** (2017). *Design and Analysis of Experiments*. Wiley.

---

## 🤝 Contributing & Community

<table>
<tr>
<td width="50%">

### 💻 Start Contributing

We welcome contributions from everyone!

```bash
# Fork, clone, and create branch
git checkout -b feature/your-feature

# Make changes, test
make check

# Submit PR
```

📖 **[Full Contributing Guide](CONTRIBUTING.md)**

</td>
<td width="50%">

### 🌟 Community Resources

| Resource | Description |
|----------|-------------|
| [📖 Contributing Guide](CONTRIBUTING.md) | How to contribute |
| [🤝 Code of Conduct](CODE_OF_CONDUCT.md) | Community standards |
| [🆘 Getting Help](SUPPORT.md) | Support channels |
| [🏛️ Governance](GOVERNANCE.md) | Decision making |
| [👥 Authors](AUTHORS.md) | Contributors |

</td>
</tr>
</table>

### 📚 Open Source Documentation - Reusable Templates

**🎁 Free to use in your own projects!** All templates are MIT-licensed.

| Category | Templates | Use Case |
|----------|-----------|----------|
| **🤝 Community** | [CODE_OF_CONDUCT](CODE_OF_CONDUCT.md), [CONTRIBUTING](CONTRIBUTING.md), [GOVERNANCE](GOVERNANCE.md) | Open-source community setup |
| **📝 GitHub** | [Issue Templates](.github/ISSUE_TEMPLATE/), [PR Template](.github/PULL_REQUEST_TEMPLATE.md) | Repository automation |
| **🔧 Development** | [PROMPT_BOOK](docs/PROMPT_BOOK.md), [QUICKFIX](docs/QUICKFIX.md) | AI-assisted development |
| **🏆 Quality** | [ISO 25010](docs/ISO_IEC_25010_COMPLIANCE.md), [ADR Templates](docs/adr/) | Enterprise standards |
| **🔬 Research** | [Mathematical Analysis](docs/research/MATHEMATICAL_ANALYSIS.md) | Academic documentation |

📖 **[Full Template Catalog →](docs/REUSABLE_TEMPLATES.md)** - Copy, customize, and use!

### 📑 Cite This Project

If you use this project in research, please cite:

```bibtex
@software{multi_agent_tour_guide_2025,
  title = {Multi-Agent Tour Guide System},
  author = {LLMs and Multi-Agent Orchestration Course},
  year = {2025},
  version = {2.0.0},
  url = {https://github.com/yourusername/multi-agent-tour-guide}
}
```

📄 See [CITATION.cff](CITATION.cff) for full citation format.

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file.

**Free to use, modify, and distribute.** Attribution appreciated but not required.

---

---

## 📊 Project Health

<table>
<tr>
<td width="33%" align="center">

### 📁 Repository

| Metric | Status |
|--------|--------|
| License | MIT |
| Language | Python 3.10+ |
| Package Manager | UV |

</td>
<td width="33%" align="center">

### 🧪 Quality

| Metric | Status |
|--------|--------|
| Test Coverage | 85%+ |
| ISO 25010 | ✅ Compliant |
| Linting | Ruff |

</td>
<td width="33%" align="center">

### 🤝 Community

| Resource | Link |
|----------|------|
| Contributing | [Guide](CONTRIBUTING.md) |
| Code of Conduct | [Standards](CODE_OF_CONDUCT.md) |
| Support | [Help](SUPPORT.md) |

</td>
</tr>
</table>

---

## 📋 Quick Reference

### Essential Files

| File | Purpose |
|------|---------|
| [README.md](README.md) | Project overview |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guide |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Community standards |
| [CHANGELOG.md](CHANGELOG.md) | Version history |
| [LICENSE](LICENSE) | MIT License |
| [SECURITY.md](SECURITY.md) | Security policy |
| [SUPPORT.md](SUPPORT.md) | Getting help |
| [GOVERNANCE.md](GOVERNANCE.md) | Project governance |
| [AUTHORS.md](AUTHORS.md) | Contributors |
| [CITATION.cff](CITATION.cff) | Academic citation |

### Essential Directories

| Directory | Purpose |
|-----------|---------|
| [`src/`](src/) | Source code |
| [`tests/`](tests/) | Test suite |
| [`docs/`](docs/) | Documentation |
| [`config/`](config/) | Configuration |
| [`plugins/`](plugins/) | Plugin system |
| [`notebooks/`](notebooks/) | Jupyter notebooks |
| [`.github/`](.github/) | GitHub templates |

---

<p align="center">
  <strong>Built with ❤️ using production-grade architecture patterns</strong>
</p>

<p align="center">
  <em>Parallel agents • Plugin architecture • Graceful degradation • Full observability</em>
</p>

<p align="center">
  <a href="https://github.com/yourusername/multi-agent-tour-guide/issues">🐛 Report Bug</a> •
  <a href="https://github.com/yourusername/multi-agent-tour-guide/discussions">💡 Request Feature</a> •
  <a href="docs/">📚 Documentation</a> •
  <a href="CONTRIBUTING.md">🤝 Contribute</a>
</p>

<p align="center">
  <sub>Made with ❤️ by the Multi-Agent Tour Guide Community</sub>
</p>
