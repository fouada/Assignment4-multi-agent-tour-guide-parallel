# 📁 MIT-Level Project Structure
## Multi-Agent Tour Guide System

---

## Complete Directory Structure

```
multi-agent-tour-guide/
│
├── 📄 README.md                    # Project overview, quick start
├── 📄 LICENSE                      # MIT License
├── 📄 CHANGELOG.md                 # Version history
├── 📄 CONTRIBUTING.md              # How to contribute
├── 📄 .gitignore                   # Git ignore rules
├── 📄 .env.example                 # Environment variables template
├── 📄 pyproject.toml               # Modern Python project config
├── 📄 requirements.txt             # Production dependencies
├── 📄 requirements-dev.txt         # Development dependencies
├── 📄 Makefile                     # Common commands
├── 📄 Dockerfile                   # Container definition
├── 📄 docker-compose.yml           # Multi-container setup
│
├── 📁 docs/                        # 📚 DOCUMENTATION
│   ├── 📄 index.md                 # Documentation home
│   ├── 📄 MIT_PROJECT_SPECIFICATION.md  # Full project spec
│   ├── 📄 ARCHITECTURE.md          # System architecture
│   ├── 📄 DESIGN_DECISIONS.md      # Design rationale
│   ├── 📄 DEVELOPMENT_PROMPTS.md   # AI prompts for development
│   ├── 📄 API_REFERENCE.md         # API documentation
│   ├── 📄 USER_GUIDE.md            # End-user documentation
│   ├── 📄 DEPLOYMENT.md            # Deployment instructions
│   │
│   ├── 📁 diagrams/                # Architecture diagrams
│   │   ├── 📄 system_architecture.png
│   │   ├── 📄 data_flow.png
│   │   ├── 📄 sequence_diagram.png
│   │   └── 📄 component_diagram.png
│   │
│   └── 📁 adr/                     # Architecture Decision Records
│       ├── 📄 001-parallel-agents.md
│       ├── 📄 002-smart-queue.md
│       ├── 📄 003-yaml-config.md
│       └── 📄 template.md
│
├── 📁 src/                         # 🔧 SOURCE CODE
│   ├── 📄 __init__.py
│   │
│   ├── 📁 agents/                  # 🤖 AI AGENTS
│   │   ├── 📄 __init__.py
│   │   ├── 📄 base_agent.py        # Abstract base class
│   │   ├── 📄 video_agent.py       # YouTube video finder
│   │   ├── 📄 music_agent.py       # Music/song finder
│   │   ├── 📄 text_agent.py        # Facts/stories finder
│   │   ├── 📄 judge_agent.py       # Content evaluator
│   │   ├── 📄 registry.py          # Agent registration
│   │   │
│   │   └── 📁 configs/             # Agent YAML configurations
│   │       ├── 📄 video_agent.yaml
│   │       ├── 📄 music_agent.yaml
│   │       ├── 📄 text_agent.yaml
│   │       └── 📄 judge_agent.yaml
│   │
│   ├── 📁 core/                    # 🎯 CORE LOGIC
│   │   ├── 📄 __init__.py
│   │   ├── 📄 orchestrator.py      # Thread pool management
│   │   ├── 📄 smart_queue.py       # Queue with timeouts
│   │   ├── 📄 collector.py         # Result aggregation
│   │   ├── 📄 timer_scheduler.py   # Travel simulation
│   │   └── 📄 pipeline.py          # Main processing pipeline
│   │
│   ├── 📁 models/                  # 📋 DATA MODELS
│   │   ├── 📄 __init__.py
│   │   ├── 📄 route.py             # RoutePoint, Route
│   │   ├── 📄 content.py           # ContentResult, ContentType
│   │   ├── 📄 decision.py          # JudgeDecision
│   │   ├── 📄 user_profile.py      # UserProfile, presets
│   │   └── 📄 metrics.py           # QueueMetrics, SystemMetrics
│   │
│   ├── 📁 services/                # 🌐 EXTERNAL SERVICES
│   │   ├── 📄 __init__.py
│   │   ├── 📄 google_maps.py       # Google Maps API
│   │   ├── 📄 youtube.py           # YouTube Data API
│   │   ├── 📄 spotify.py           # Spotify API
│   │   ├── 📄 wikipedia.py         # Wikipedia API
│   │   ├── 📄 openai_client.py     # LLM client
│   │   └── 📄 cache.py             # Caching layer (Redis)
│   │
│   ├── 📁 utils/                   # 🛠️ UTILITIES
│   │   ├── 📄 __init__.py
│   │   ├── 📄 config.py            # Configuration loading
│   │   ├── 📄 logger.py            # Logging setup
│   │   ├── 📄 retry.py             # Retry with backoff
│   │   ├── 📄 validators.py        # Input validation
│   │   └── 📄 helpers.py           # Common helpers
│   │
│   ├── 📁 api/                     # 🌍 REST API (optional)
│   │   ├── 📄 __init__.py
│   │   ├── 📄 app.py               # FastAPI application
│   │   ├── 📄 routes.py            # API endpoints
│   │   ├── 📄 schemas.py           # Request/Response schemas
│   │   └── 📄 middleware.py        # API middleware
│   │
│   └── 📁 cli/                     # 💻 COMMAND LINE
│       ├── 📄 __init__.py
│       ├── 📄 main.py              # CLI entry point
│       ├── 📄 commands.py          # CLI commands
│       └── 📄 interactive.py       # Interactive mode
│
├── 📁 plugins/                     # 🔌 PLUGIN AGENTS
│   ├── 📄 README.md                # How to create plugins
│   │
│   ├── 📁 weather/                 # Example: Weather plugin
│   │   ├── 📄 __init__.py
│   │   ├── 📄 agent.py
│   │   ├── 📄 config.yaml
│   │   └── 📄 requirements.txt
│   │
│   └── 📁 food/                    # Example: Food/Restaurant plugin
│       ├── 📄 __init__.py
│       ├── 📄 agent.py
│       ├── 📄 config.yaml
│       └── 📄 requirements.txt
│
├── 📁 tests/                       # 🧪 TESTS
│   ├── 📄 __init__.py
│   ├── 📄 conftest.py              # Pytest fixtures
│   │
│   ├── 📁 unit/                    # Unit tests
│   │   ├── 📄 __init__.py
│   │   ├── 📄 test_agents.py
│   │   ├── 📄 test_queue.py
│   │   ├── 📄 test_models.py
│   │   ├── 📄 test_user_profile.py
│   │   └── 📄 test_orchestrator.py
│   │
│   ├── 📁 integration/             # Integration tests
│   │   ├── 📄 __init__.py
│   │   ├── 📄 test_pipeline.py
│   │   ├── 📄 test_api.py
│   │   └── 📄 test_services.py
│   │
│   ├── 📁 e2e/                     # End-to-end tests
│   │   ├── 📄 __init__.py
│   │   └── 📄 test_full_flow.py
│   │
│   └── 📁 fixtures/                # Test data
│       ├── 📄 mock_routes.json
│       ├── 📄 mock_content.json
│       └── 📄 mock_profiles.json
│
├── 📁 config/                      # ⚙️ CONFIGURATION
│   ├── 📄 default.yaml             # Default configuration
│   ├── 📄 development.yaml         # Development overrides
│   ├── 📄 production.yaml          # Production settings
│   ├── 📄 testing.yaml             # Test configuration
│   └── 📄 agents.yaml              # Enabled agents list
│
├── 📁 scripts/                     # 📜 SCRIPTS
│   ├── 📄 setup.sh                 # Initial setup
│   ├── 📄 run_dev.sh               # Run development server
│   ├── 📄 run_tests.sh             # Run test suite
│   ├── 📄 lint.sh                  # Run linters
│   ├── 📄 build.sh                 # Build for production
│   └── 📄 deploy.sh                # Deployment script
│
├── 📁 notebooks/                   # 📓 JUPYTER NOTEBOOKS
│   ├── 📄 01_exploration.ipynb     # Data exploration
│   ├── 📄 02_agent_testing.ipynb   # Agent experiments
│   ├── 📄 03_profile_analysis.ipynb # Profile impact analysis
│   └── 📄 04_demo.ipynb            # Demo notebook
│
├── 📁 data/                        # 📊 DATA FILES
│   ├── 📁 cache/                   # Cached API responses
│   ├── 📁 logs/                    # Log files
│   ├── 📁 exports/                 # Exported results
│   └── 📁 samples/                 # Sample data
│       ├── 📄 sample_route.json
│       └── 📄 sample_profile.json
│
└── 📁 .github/                     # 🔄 GITHUB ACTIONS
    ├── 📁 workflows/
    │   ├── 📄 ci.yml               # Continuous Integration
    │   ├── 📄 cd.yml               # Continuous Deployment
    │   └── 📄 tests.yml            # Test automation
    │
    ├── 📄 ISSUE_TEMPLATE.md
    ├── 📄 PULL_REQUEST_TEMPLATE.md
    └── 📄 CODEOWNERS
```

---

## Directory Descriptions

### 📁 Root Level Files

| File | Purpose |
|------|---------|
| `README.md` | Project overview, quick start guide |
| `LICENSE` | MIT License |
| `CHANGELOG.md` | Version history (Keep a Changelog format) |
| `CONTRIBUTING.md` | Contribution guidelines |
| `pyproject.toml` | Modern Python project configuration (PEP 518) |
| `Makefile` | Common commands (`make test`, `make run`) |
| `Dockerfile` | Container definition for deployment |

### 📁 docs/ - Documentation

```
docs/
├── index.md                    # Documentation home page
├── MIT_PROJECT_SPECIFICATION.md  # Complete project spec
├── ARCHITECTURE.md             # System architecture
├── DESIGN_DECISIONS.md         # Design rationale
├── DEVELOPMENT_PROMPTS.md      # AI prompts for building
├── API_REFERENCE.md            # API documentation
├── USER_GUIDE.md               # How to use the system
├── DEPLOYMENT.md               # How to deploy
│
├── diagrams/                   # Visual diagrams (PNG/SVG)
│   ├── system_architecture.png
│   ├── data_flow.png
│   └── sequence_diagram.png
│
└── adr/                        # Architecture Decision Records
    ├── 001-parallel-agents.md  # Why parallel agents
    ├── 002-smart-queue.md      # Why smart queue
    └── template.md             # ADR template
```

### 📁 src/ - Source Code

```
src/
├── agents/         # AI agents (Video, Music, Text, Judge)
├── core/           # Core logic (Orchestrator, Queue, Collector)
├── models/         # Pydantic data models
├── services/       # External API integrations
├── utils/          # Utilities (logging, config, retry)
├── api/            # REST API (FastAPI) - optional
└── cli/            # Command-line interface
```

### 📁 tests/ - Test Suite

```
tests/
├── unit/           # Unit tests (isolated components)
├── integration/    # Integration tests (components together)
├── e2e/            # End-to-end tests (full pipeline)
└── fixtures/       # Test data (mock JSON files)
```

### 📁 config/ - Configuration

```
config/
├── default.yaml      # Base configuration
├── development.yaml  # Development overrides
├── production.yaml   # Production settings
└── agents.yaml       # Which agents are enabled
```

---

## File Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Python modules | `snake_case.py` | `video_agent.py` |
| Classes | `PascalCase` | `VideoAgent` |
| Functions | `snake_case` | `search_content()` |
| Constants | `UPPER_SNAKE` | `MAX_RETRIES` |
| Config files | `snake_case.yaml` | `video_agent.yaml` |
| Test files | `test_*.py` | `test_agents.py` |
| Documentation | `UPPER_SNAKE.md` | `ARCHITECTURE.md` |

---

## Module Organization

### Agents Module (`src/agents/`)

```python
# src/agents/__init__.py
from .base_agent import BaseAgent
from .video_agent import VideoAgent
from .music_agent import MusicAgent
from .text_agent import TextAgent
from .judge_agent import JudgeAgent
from .registry import AgentRegistry

__all__ = [
    "BaseAgent",
    "VideoAgent",
    "MusicAgent",
    "TextAgent",
    "JudgeAgent",
    "AgentRegistry",
]
```

### Models Module (`src/models/`)

```python
# src/models/__init__.py
from .route import RoutePoint, Route
from .content import ContentResult, ContentType
from .decision import JudgeDecision
from .user_profile import UserProfile, AgeGroup, Gender
from .metrics import QueueMetrics, QueueStatus

__all__ = [
    "RoutePoint",
    "Route",
    "ContentResult",
    "ContentType",
    "JudgeDecision",
    "UserProfile",
    "AgeGroup",
    "Gender",
    "QueueMetrics",
    "QueueStatus",
]
```

---

## Configuration Examples

### pyproject.toml

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "multi-agent-tour-guide"
version = "2.0.0"
description = "Multi-Agent Tour Guide System with Parallel Processing"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.10"
authors = [
    {name = "Your Name", email = "your@email.com"}
]
keywords = ["ai", "agents", "tour-guide", "multi-agent", "llm"]

dependencies = [
    "pydantic>=2.0",
    "openai>=1.0",
    "httpx>=0.24",
    "pyyaml>=6.0",
    "rich>=13.0",
    "typer>=0.9",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-asyncio>=0.21",
    "pytest-cov>=4.0",
    "black>=23.0",
    "ruff>=0.1",
    "mypy>=1.0",
]
api = [
    "fastapi>=0.100",
    "uvicorn>=0.23",
]

[project.scripts]
tour-guide = "src.cli.main:app"

[tool.black]
line-length = 88
target-version = ["py310"]

[tool.ruff]
line-length = 88
select = ["E", "F", "I", "N", "W"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "-v --cov=src"
```

### Makefile

```makefile
.PHONY: install test lint run clean

install:
	pip install -e ".[dev]"

test:
	pytest tests/ -v --cov=src

lint:
	ruff check src/ tests/
	black --check src/ tests/
	mypy src/

format:
	black src/ tests/
	ruff check --fix src/ tests/

run:
	python -m src.cli.main --demo

run-api:
	uvicorn src.api.app:app --reload

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov dist build *.egg-info
```

---

## Import Structure

### Recommended Import Style

```python
# Standard library
import os
import sys
from typing import Optional, List, Dict

# Third-party
from pydantic import BaseModel, Field
import openai
import yaml

# Local - absolute imports
from src.agents.base_agent import BaseAgent
from src.models.content import ContentResult, ContentType
from src.core.smart_queue import SmartQueue
from src.utils.logger import get_logger
```

### Within Package

```python
# src/agents/video_agent.py
from .base_agent import BaseAgent  # Relative import within package
from ..models.content import ContentResult  # Up one level, then into models
from ..services.youtube import YouTubeClient
```

---

## Best Practices Summary

| Practice | Implementation |
|----------|----------------|
| **Single Responsibility** | One class/module = one purpose |
| **Dependency Injection** | Pass dependencies, don't hardcode |
| **Configuration as Code** | YAML files, not hardcoded values |
| **Type Hints** | All functions have type annotations |
| **Docstrings** | Google-style docstrings |
| **Logging** | Structured logging with context |
| **Error Handling** | Custom exceptions, graceful degradation |
| **Testing** | Unit + Integration + E2E coverage |
| **CI/CD** | Automated testing and deployment |

---

This structure follows **MIT/industry standards** and is designed for:
- ✅ Easy navigation
- ✅ Clear separation of concerns
- ✅ Scalability
- ✅ Testability
- ✅ Maintainability

