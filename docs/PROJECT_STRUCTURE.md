# 📁 MIT-Level Project Structure

## Multi-Agent Tour Guide System

This document describes the complete project structure following MIT-level academic and industrial software engineering standards.

---

## Directory Tree

```
multi-agent-tour-guide/
│
├── 📄 README.md                      # Project overview and quick start
├── 📄 CHANGELOG.md                   # Version history (Keep a Changelog format)
├── 📄 CONTRIBUTING.md                # Contribution guidelines
├── 📄 SECURITY.md                    # Security policy
├── 📄 LICENSE                        # MIT License
├── 📄 pyproject.toml                 # Project configuration (PEP 621)
├── 📄 Makefile                       # Build automation
├── 📄 main.py                        # Entry point
│
├── 📁 src/                           # 🐍 SOURCE CODE
│   ├── __init__.py
│   │
│   ├── 📁 agents/                    # AI Agent implementations
│   │   ├── __init__.py
│   │   ├── base_agent.py             # Abstract base class
│   │   ├── video_agent.py            # YouTube content
│   │   ├── music_agent.py            # Spotify/audio content
│   │   ├── text_agent.py             # Wikipedia/text content
│   │   ├── judge_agent.py            # Content selection
│   │   └── 📁 configs/               # Agent YAML configs
│   │
│   ├── 📁 core/                      # Core infrastructure
│   │   ├── __init__.py
│   │   ├── orchestrator.py           # Multi-agent coordination
│   │   ├── smart_queue.py            # Tiered timeout queue
│   │   │
│   │   ├── 📁 di/                    # Dependency Injection
│   │   │   ├── container.py
│   │   │   ├── providers.py
│   │   │   └── scope.py
│   │   │
│   │   ├── 📁 resilience/            # Fault tolerance patterns
│   │   │   ├── circuit_breaker.py
│   │   │   ├── retry.py
│   │   │   ├── rate_limiter.py
│   │   │   ├── timeout.py
│   │   │   ├── bulkhead.py
│   │   │   └── fallback.py
│   │   │
│   │   ├── 📁 observability/         # Monitoring & tracing
│   │   │   ├── health.py
│   │   │   ├── metrics.py
│   │   │   └── tracing.py
│   │   │
│   │   └── 📁 plugins/               # Plugin system
│   │       ├── base.py
│   │       ├── registry.py
│   │       ├── manager.py
│   │       ├── hooks.py
│   │       └── events.py
│   │
│   ├── 📁 models/                    # Data models (Pydantic)
│   │   ├── __init__.py
│   │   ├── content.py                # ContentResult, ContentType
│   │   ├── decision.py               # JudgeDecision
│   │   ├── route.py                  # RoutePoint, Route
│   │   ├── user_profile.py           # UserProfile
│   │   ├── metrics.py                # QueueMetrics, QueueStatus
│   │   └── output.py                 # Output formatting
│   │
│   ├── 📁 research/                  # 🔬 MIT Research Framework
│   │   ├── __init__.py
│   │   ├── experimental_framework.py # Reproducible experiments
│   │   ├── statistical_analysis.py   # Hypothesis testing
│   │   └── visualization.py          # Publication figures
│   │
│   ├── 📁 api/                       # REST API (FastAPI)
│   │   ├── __init__.py
│   │   └── app.py
│   │
│   ├── 📁 cli/                       # Command-line interface
│   │   ├── __init__.py
│   │   └── main.py
│   │
│   ├── 📁 services/                  # External service clients
│   │   ├── __init__.py
│   │   └── google_maps.py
│   │
│   └── 📁 utils/                     # Utilities
│       ├── __init__.py
│       ├── config.py
│       ├── logger.py
│       └── retry.py
│
├── 📁 tests/                         # 🧪 TEST SUITE
│   ├── __init__.py
│   ├── conftest.py                   # Pytest fixtures
│   │
│   ├── 📁 unit/                      # Unit tests (632+ tests)
│   │   ├── test_models_*.py
│   │   ├── test_smart_queue.py
│   │   ├── test_resilience_*.py
│   │   └── ...
│   │
│   ├── 📁 integration/               # Integration tests
│   │   ├── test_agent_integration.py
│   │   └── test_queue_integration.py
│   │
│   ├── 📁 performance/               # Performance benchmarks
│   │   └── test_performance.py
│   │
│   ├── 📁 e2e/                       # End-to-end tests
│   │   └── (planned)
│   │
│   └── 📁 fixtures/                  # Test data
│
├── 📁 docs/                          # 📚 DOCUMENTATION
│   ├── 📄 PRD.md                     # Product Requirements
│   ├── 📄 ARCHITECTURE.md            # C4 Architecture
│   ├── 📄 ARCHITECTURE_DETAILED.md   # Detailed design
│   ├── 📄 API_REFERENCE.md           # API documentation
│   ├── 📄 TESTING.md                 # Test specifications
│   ├── 📄 QUALITY_ATTRIBUTES.md      # Quality analysis
│   ├── 📄 ISO_IEC_25010_COMPLIANCE.md # ISO compliance
│   ├── 📄 PROJECT_STRUCTURE.md       # This file
│   │
│   ├── 📁 adr/                       # Architecture Decision Records
│   │   ├── README.md
│   │   ├── template.md
│   │   ├── 001-parallel-agent-architecture.md
│   │   ├── 002-smart-queue-timeout-strategy.md
│   │   ├── 003-circuit-breaker-pattern.md
│   │   ├── 004-plugin-architecture.md
│   │   └── 005-statistical-analysis-framework.md
│   │
│   ├── 📁 diagrams/                  # Mermaid diagrams
│   │   ├── README.md
│   │   ├── system-architecture.mmd
│   │   ├── smart-queue-flow.mmd
│   │   ├── agent-sequence.mmd
│   │   └── research-pipeline.mmd
│   │
│   └── 📁 research/                  # Research documentation
│       ├── README.md                 # Research framework overview
│       └── MATHEMATICAL_ANALYSIS.md  # Formal proofs
│
├── 📁 notebooks/                     # 📓 JUPYTER NOTEBOOKS
│   ├── README.md                     # Notebook index
│   └── 01_sensitivity_analysis.ipynb # Monte Carlo analysis
│
├── 📁 benchmarks/                    # 🏋️ BENCHMARKS
│   ├── README.md
│   ├── 📁 configs/                   # Benchmark configurations
│   │   ├── baseline.yaml
│   │   ├── low_latency.yaml
│   │   └── high_quality.yaml
│   ├── 📁 results/                   # Benchmark results (gitignored)
│   └── 📁 scripts/                   # Benchmark runners
│
├── 📁 experiments/                   # 🧪 EXPERIMENT TRACKING
│   ├── README.md
│   ├── registry.json                 # Experiment registry
│   ├── 📁 templates/                 # Experiment templates
│   │   └── sensitivity_template.yaml
│   ├── 📁 active/                    # Running experiments
│   └── 📁 completed/                 # Archived experiments
│
├── 📁 reports/                       # 📑 REPORTS
│   ├── README.md
│   ├── 📁 templates/                 # Report templates
│   ├── 📁 generated/                 # Auto-generated reports
│   └── 📁 published/                 # Finalized reports
│
├── 📁 data/                          # 📊 DATA
│   ├── 📁 cache/                     # Cached API responses
│   ├── 📁 figures/                   # Generated plots
│   ├── 📁 logs/                      # Application logs
│   └── 📁 samples/                   # Sample data
│
├── 📁 config/                        # ⚙️ CONFIGURATION
│   └── default.yaml                  # Default settings
│
├── 📁 plugins/                       # 🔌 PLUGINS
│   ├── 📁 weather/                   # Weather plugin (example)
│   │   ├── plugin.yaml
│   │   ├── plugin.py
│   │   └── agent.py
│   └── 📁 food/                      # Food plugin (placeholder)
│
├── 📁 scripts/                       # 🔧 SCRIPTS
│   ├── setup.sh                      # Setup script
│   └── iso25010_compliance_check.py  # Compliance checker
│
└── 📁 deploy/                        # 🚀 DEPLOYMENT
    ├── Dockerfile
    ├── docker-compose.yml
    ├── 📁 kubernetes/
    │   └── deployment.yaml
    ├── 📁 prometheus/
    │   └── prometheus.yml
    └── 📁 grafana/
        └── provisioning/
```

---

## MIT-Level Standards Compliance

### ✅ Software Engineering

| Standard | Implementation |
|----------|----------------|
| Clean Architecture | Layered separation (agents, core, models, services) |
| SOLID Principles | DI container, plugin interfaces, single responsibility |
| Design Patterns | Circuit breaker, retry, observer, strategy |
| Code Quality | 85%+ test coverage, linting, type hints |

### ✅ Documentation

| Standard | Implementation |
|----------|----------------|
| ADRs | Architecture Decision Records for key decisions |
| API Docs | OpenAPI/Swagger specification |
| Diagrams | C4 model with Mermaid |
| Changelog | Keep a Changelog format |

### ✅ Research Framework

| Standard | Implementation |
|----------|----------------|
| Reproducibility | Fixed seeds, versioned configs, experiment tracking |
| Statistical Rigor | Hypothesis testing, effect sizes, confidence intervals |
| Sensitivity Analysis | OAT, Sobol indices, Monte Carlo |
| Publication Quality | 300 DPI figures, proper formatting |

### ✅ DevOps

| Standard | Implementation |
|----------|----------------|
| CI/CD | GitHub Actions with quality gates |
| Containerization | Docker + Kubernetes |
| Observability | Prometheus + Grafana |
| Security | Secret management, input validation |

---

## File Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Python modules | `snake_case.py` | `smart_queue.py` |
| Test files | `test_*.py` | `test_smart_queue.py` |
| Classes | `PascalCase` | `SmartAgentQueue` |
| Functions | `snake_case` | `wait_for_results()` |
| Constants | `UPPER_SNAKE` | `SOFT_TIMEOUT_SECONDS` |
| Config files | `snake_case.yaml` | `default.yaml` |
| Documentation | `UPPER_SNAKE.md` | `ARCHITECTURE.md` |
| ADRs | `NNN-kebab-case.md` | `001-parallel-agent-architecture.md` |
| Notebooks | `NN_snake_case.ipynb` | `01_sensitivity_analysis.ipynb` |

---

## Import Structure

```python
# Standard library
import os
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# Third-party
import numpy as np
import pandas as pd
from pydantic import BaseModel

# Local - absolute imports
from src.core.smart_queue import SmartAgentQueue
from src.models.content import ContentResult
from src.research import StatisticalComparison
```

---

## Version

**Document Version**: 2.0.0  
**Last Updated**: November 2025  
**Maintainer**: Multi-Agent Tour Guide Team
