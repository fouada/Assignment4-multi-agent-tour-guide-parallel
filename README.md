<p align="center">
  <img src="https://img.shields.io/badge/🗺️-Multi--Agent%20Tour%20Guide-blue?style=for-the-badge" alt="Multi-Agent Tour Guide"/>
</p>

<h1 align="center">Multi-Agent Tour Guide System</h1>

<p align="center">
  <strong>Enterprise-Grade AI Orchestration for Personalized Travel Experiences.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue.svg?style=flat-square&logo=python" alt="Python 3.10+"/>
  <img src="https://img.shields.io/badge/license-MIT-green.svg?style=flat-square" alt="MIT License"/>
  <img src="https://img.shields.io/badge/coverage-85%25+-brightgreen.svg?style=flat-square" alt="Coverage 85%+"/>
  <img src="https://img.shields.io/badge/tests-683+-blue.svg?style=flat-square" alt="683+ Tests"/>
  <img src="https://img.shields.io/badge/ISO%2FIEC%2025010-Compliant-brightgreen.svg?style=flat-square" alt="ISO Compliant"/>
  <img src="https://img.shields.io/badge/MIT--Level-Research-red.svg?style=flat-square" alt="MIT-Level Research"/>
</p>

---

## 📋 Table of Contents

| Section | Description |
|---------|-------------|
| [1. Overview](#1-overview) | What this project does |
| [2. Quick Start](#2-quick-start) | Get running in 4 steps |
| [3. Features](#3-features) | Key capabilities |
| [4. Architecture](#4-architecture) | System design |
| [5. Installation](#5-installation) | Detailed setup |
| [6. Usage](#6-usage) | Commands and modes |
| [7. Testing](#7-testing) | Test catalog with expected results |
| [8. Research Framework](#8-research-framework) | MIT-level analysis |
| [9. Documentation](#9-documentation) | Full documentation index |
| [10. Contributing](#10-contributing) | Community & open source |
| [11. License & Citation](#11-license--citation) | Legal and academic |

---

## 1. Overview

The **Multi-Agent Tour Guide System** creates personalized travel experiences using parallel AI agents:

```
Route Input → [Video Agent] + [Music Agent] + [Text Agent] → Smart Queue → Judge → Playlist
```

**Key Capabilities:**
- 🤖 **3 AI agents** running in parallel (Video, Music, Text)
- 📬 **Smart Queue** with graceful degradation (3→2→1 agents)
- ⚖️ **Judge Agent** selects best content per user profile
- 🛡️ **Resilience patterns** (circuit breaker, retry, timeout)
- 🔌 **Plugin architecture** for extensibility

---

## 2. Quick Start

```bash
# 1. Install UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone and setup
git clone https://github.com/yourusername/multi-agent-tour-guide.git
cd multi-agent-tour-guide && make setup

# 3. Configure API key
echo "ANTHROPIC_API_KEY=sk-ant-your-key" > .env

# 4. Run
make run-queue
```

**Expected Output:**
```
📍 Route: Tel Aviv → Jerusalem (4 points)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 [1/4] Latrun
   ✅ Video Agent (1/3) ✅ Music Agent (2/3) ✅ Text Agent (3/3)
   🏆 Winner: 📖 TEXT - "The Silent Monks of Latrun"
```

---

## 3. Features

| Category | Features |
|----------|----------|
| **🤖 Multi-Agent** | Video (YouTube), Music (Spotify), Text (Wikipedia), Judge (AI selection) |
| **📬 Smart Queue** | 3/3 ideal → 2/3 soft timeout (15s) → 1/3 hard timeout (30s) |
| **👤 Personalization** | Age filtering, interests, accessibility, driver mode (no video) |
| **🛡️ Resilience** | Circuit breaker, exponential backoff retry, rate limiter, bulkhead |
| **🔌 Plugins** | Auto-discovery, YAML config, lifecycle hooks, zero code changes |
| **📊 Observability** | Prometheus metrics, health checks, structured logging |
| **🔬 Research** | Monte Carlo analysis, statistical testing, mathematical proofs |

---

## 4. Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INPUT                               │
│        Source: "Tel Aviv" → Destination: "Jerusalem"            │
└───────────────────────────────┬─────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        ORCHESTRATOR                              │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐                     │
│   │  VIDEO  │    │  MUSIC  │    │  TEXT   │  ← Parallel         │
│   │  AGENT  │    │  AGENT  │    │  AGENT  │                     │
│   └────┬────┘    └────┬────┘    └────┬────┘                     │
│        └──────────────┼──────────────┘                          │
│                       ▼                                          │
│              ┌─────────────────┐                                 │
│              │   SMART QUEUE   │  ← Graceful Degradation        │
│              │  Wait 3 → 2 → 1 │                                 │
│              └────────┬────────┘                                 │
│                       ▼                                          │
│              ┌─────────────────┐                                 │
│              │   JUDGE AGENT   │  ← Content Selection           │
│              └────────┬────────┘                                 │
└───────────────────────┼─────────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FINAL PLAYLIST                              │
│   Point 1: 📖 TEXT  │ Point 2: 🎬 VIDEO │ Point 3: 🎵 MUSIC    │
└─────────────────────────────────────────────────────────────────┘
```

**Layer Stack:**
```
┌─────────────────────────────────────────────────────┐
│  CLI (Typer)  │  REST API (FastAPI)  │  Web UI     │  APPLICATION
├─────────────────────────────────────────────────────┤
│  Video Agent  │  Music Agent  │  Text Agent        │  AGENTS
├─────────────────────────────────────────────────────┤
│  Plugins  │  Resilience  │  Observability  │  DI   │  INFRASTRUCTURE
└─────────────────────────────────────────────────────┘
```

📖 [Full Architecture Documentation](docs/ARCHITECTURE.md)

---

## 5. Installation

### Prerequisites
- Python 3.10+
- [UV Package Manager](https://docs.astral.sh/uv/)

### Setup

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows

# Clone & install
git clone https://github.com/yourusername/multi-agent-tour-guide.git
cd multi-agent-tour-guide
make setup  # Creates venv + installs dependencies

# Configure
cp env.example .env
# Edit .env with your API key
```

### API Keys

| Key | Provider | Required |
|-----|----------|----------|
| `ANTHROPIC_API_KEY` | [Anthropic](https://console.anthropic.com/) | ✅ (preferred) |
| `OPENAI_API_KEY` | [OpenAI](https://platform.openai.com/) | Alternative |
| `GOOGLE_MAPS_API_KEY` | Google Cloud | Optional |

### Verify

```bash
make check  # Runs lint + tests
make run    # Runs demo
```

---

## 6. Usage

### Essential Commands

| Command | Description |
|---------|-------------|
| `make run-queue` | **Recommended** - Queue mode with all hops |
| `make run` | Demo mode (default) |
| `make run-family` | Family-friendly mode |
| `make run-verbose` | Debug logging |
| `make run-api` | Start REST API server |
| `make test` | Run all tests |
| `make test-cov` | Tests with 85% coverage |
| `make check` | Lint + test |

### Processing Modes

| Mode | Description | Command |
|------|-------------|---------|
| `queue` | Queue-based sync **(recommended)** | `--mode queue` |
| `streaming` | Real-time simulation | `--mode streaming` |
| `instant` | All points parallel | `--mode instant` |
| `sequential` | One at a time (debug) | `--mode sequential` |

### User Profiles

| Profile | Description | Command |
|---------|-------------|---------|
| `default` | General adult | (none) |
| `family` | Child-friendly | `--profile family --min-age 5` |
| `history` | In-depth content | `--profile history` |
| `driver` | Audio only (no video) | `--profile driver` |

### Example Commands

```bash
# Custom route
uv run python main.py --origin "Paris" --destination "Lyon"

# Family mode
uv run python main.py --demo --profile family --min-age 5

# Verbose logging
LOG_LEVEL=DEBUG uv run python main.py --demo --mode queue

# API server
make run-api  # Then: curl http://localhost:8000/health
```

---

## 7. Testing

### Test Summary

| Metric | Value |
|--------|-------|
| **Total Tests** | 683+ |
| **Coverage** | 85%+ |
| **Test Files** | 45+ |
| **Edge Cases** | 100% documented |

### Test Catalog with Expected Results

#### Smart Queue Tests

| Test | Input | Expected Result |
|------|-------|-----------------|
| `test_all_agents_succeed` | 3/3 agents respond | Status: `COMPLETE` |
| `test_soft_timeout` | 2/3 agents respond | Status: `SOFT_DEGRADED` |
| `test_hard_timeout` | 1/3 agents respond | Status: `HARD_DEGRADED` |
| `test_all_agents_fail` | 0/3 agents respond | Raises `NoResultsError` |

#### Circuit Breaker Tests

| Test | Trigger | Expected Result |
|------|---------|-----------------|
| `test_initial_state` | Creation | State: `CLOSED` |
| `test_open_after_failures` | 5 failures | `CLOSED` → `OPEN` |
| `test_half_open_after_timeout` | 60s elapsed | `OPEN` → `HALF_OPEN` |
| `test_close_after_success` | 1 success in half-open | `HALF_OPEN` → `CLOSED` |

#### User Profile Tests

| Test | Profile | Expected Result |
|------|---------|-----------------|
| `test_kid_profile_prefers_video` | Kid (age<12) | video_weight > text_weight |
| `test_driver_profile_blocks_video` | Driver | video_weight = 0.0 |
| `test_visual_impairment` | Blind user | music_weight > video_weight |

#### Resilience Pattern Tests

| Pattern | Test | Expected Result |
|---------|------|-----------------|
| **Retry** | `test_exponential_backoff` | Delays: 1s → 2s → 4s → 8s |
| **Rate Limiter** | `test_acquire_blocked` | Returns False when no tokens |
| **Timeout** | `test_slow_function_times_out` | Raises `TimeoutError` |
| **Bulkhead** | `test_concurrent_limit` | Excess calls rejected |

### Run Tests

```bash
make test              # All tests
make test-cov          # With coverage (85% enforced)
make test-unit         # Unit tests only
make test-e2e          # End-to-end tests

# Specific patterns
uv run pytest -k "queue" -v
uv run pytest -k "circuit_breaker" -v

# Coverage report
uv run pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

📖 [Full Testing Documentation](docs/TESTING.md)

---

## 8. Research Framework

### MIT-Level Capabilities

| Capability | Methods | Output |
|------------|---------|--------|
| **Statistical Analysis** | t-test, Mann-Whitney, Kolmogorov-Smirnov, Bootstrap CI | p-values, effect sizes |
| **Sensitivity Analysis** | Monte Carlo (N=10,000+), Sobol indices, Morris screening | Parameter rankings |
| **Mathematical Proofs** | Liveness, safety, progress theorems | Formal correctness |
| **Experimental Design** | 2^k factorial, parameter sweeps | Reproducible results |

### Example: Statistical Comparison

```python
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
STATISTICAL COMPARISON: Default vs Aggressive
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Descriptive: μ=4.523s vs μ=2.876s
t-test: p=2.34e-156 ✓  Effect: large (d=0.583)
Conclusion: Strong evidence of difference
```

### Research Documentation

| Document | Description |
|----------|-------------|
| [research/README.md](docs/research/README.md) | Framework overview |
| [MATHEMATICAL_ANALYSIS.md](docs/research/MATHEMATICAL_ANALYSIS.md) | Formal proofs |
| [01_sensitivity_analysis.ipynb](notebooks/01_sensitivity_analysis.ipynb) | Monte Carlo notebook |

---

## 9. Documentation

### Documentation Index

| Category | Documents |
|----------|-----------|
| **📚 Core** | [PRD](docs/PRD.md) • [Architecture](docs/ARCHITECTURE.md) • [API Reference](docs/API_REFERENCE.md) |
| **🔧 Development** | [Prompt Book](docs/PROMPT_BOOK.md) • [Quick Fix](docs/QUICKFIX.md) • [Testing](docs/TESTING.md) |
| **🏆 Quality** | [ISO 25010 Compliance](docs/ISO_IEC_25010_COMPLIANCE.md) • [Project Checklist](docs/PROJECT_CHECKLIST.md) |
| **🔬 Research** | [Research README](docs/research/README.md) • [Mathematical Analysis](docs/research/MATHEMATICAL_ANALYSIS.md) |
| **🏢 Deployment** | [Startup Design](docs/STARTUP_DESIGN.md) • [Production Architecture](docs/MIT_PRODUCTION_ARCHITECTURE.md) |

### ISO/IEC 25010:2011 Compliance

| Characteristic | Status | Implementation |
|---------------|--------|----------------|
| Functional Suitability | ✅ | Multi-agent architecture |
| Performance Efficiency | ✅ | Thread pools, metrics |
| Compatibility | ✅ | REST API, Kubernetes |
| Usability | ✅ | CLI, Rich output |
| Reliability | ✅ | Circuit breaker, retry |
| Security | ✅ | Environment secrets |
| Maintainability | ✅ | Plugin architecture, 85% coverage |
| Portability | ✅ | Docker, environment abstraction |

---

## 10. Contributing

### Community Resources

| Resource | Description |
|----------|-------------|
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Community standards |
| [SUPPORT.md](SUPPORT.md) | Getting help |
| [GOVERNANCE.md](GOVERNANCE.md) | Decision making |
| [AUTHORS.md](AUTHORS.md) | Contributors |

### Quick Contribute

```bash
git checkout -b feature/your-feature
# Make changes
make check  # Lint + test
# Submit PR
```

### Reusable Templates (Open Source)

**🎁 Free to use in your projects!** All MIT-licensed.

| Category | Templates |
|----------|-----------|
| **Community** | [CODE_OF_CONDUCT](CODE_OF_CONDUCT.md), [CONTRIBUTING](CONTRIBUTING.md), [GOVERNANCE](GOVERNANCE.md) |
| **GitHub** | [Issue Templates](.github/ISSUE_TEMPLATE/), [PR Template](.github/PULL_REQUEST_TEMPLATE.md) |
| **Quality** | [ISO 25010](docs/ISO_IEC_25010_COMPLIANCE.md), [ADR Templates](docs/adr/) |

📖 **[Full Template Catalog](docs/REUSABLE_TEMPLATES.md)**

---

## 11. License & Citation

### License

**MIT License** - See [LICENSE](LICENSE)

Free to use, modify, and distribute. Attribution appreciated.

### Citation

```bibtex
@software{multi_agent_tour_guide_2025,
  title  = {Multi-Agent Tour Guide System},
  author = {LLMs and Multi-Agent Orchestration Course},
  year   = {2025},
  url    = {https://github.com/yourusername/multi-agent-tour-guide}
}
```

📄 See [CITATION.cff](CITATION.cff) for full format.

### Academic References

1. Martin, R.C. (2017). *Clean Architecture*. Prentice Hall.
2. Gamma et al. (1994). *Design Patterns*. Addison-Wesley.
3. Nygard, M.T. (2018). *Release It!*. Pragmatic Bookshelf.
4. Saltelli, A. et al. (2008). *Global Sensitivity Analysis*. Wiley.

---

## 📁 Project Structure

```
multi-agent-tour-guide/
├── main.py                 # Entry point
├── src/                    # Source code
│   ├── agents/            # AI agents (video, music, text, judge)
│   ├── core/              # Orchestrator, queue, plugins, resilience
│   ├── models/            # Pydantic data models
│   └── research/          # Statistical analysis framework
├── tests/                  # 683+ tests (unit, integration, e2e)
├── docs/                   # Comprehensive documentation
├── plugins/                # Plugin system
├── notebooks/              # Jupyter research notebooks
├── config/                 # YAML configuration
└── .github/                # Issue/PR templates
```

### Essential Files

| File | Purpose |
|------|---------|
| [README.md](README.md) | Project overview |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guide |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Community standards |
| [LICENSE](LICENSE) | MIT License |
| [CITATION.cff](CITATION.cff) | Academic citation |
| [CHANGELOG.md](CHANGELOG.md) | Version history |

---

<p align="center">
  <strong>Built with ❤️ for MIT-Level Excellence</strong>
</p>

<p align="center">
  <em>Parallel Agents • Smart Queue • Graceful Degradation • Full Observability • Research Framework</em>
</p>

<p align="center">
  <a href="https://github.com/yourusername/multi-agent-tour-guide/issues">🐛 Report Bug</a> •
  <a href="https://github.com/yourusername/multi-agent-tour-guide/discussions">💡 Request Feature</a> •
  <a href="docs/">📚 Documentation</a> •
  <a href="CONTRIBUTING.md">🤝 Contribute</a>
</p>
