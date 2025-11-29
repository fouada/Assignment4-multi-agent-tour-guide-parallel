# 🤝 Contributing to Multi-Agent Tour Guide

Thank you for your interest in contributing to the Multi-Agent Tour Guide System! This document provides guidelines and information for contributors.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Project Structure](#project-structure)
5. [Making Changes](#making-changes)
6. [Coding Standards](#coding-standards)
7. [Testing](#testing)
8. [Documentation](#documentation)
9. [Submitting Changes](#submitting-changes)
10. [Creating Plugins](#creating-plugins)

---

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/). By participating, you are expected to uphold this code.

**Key Points:**
- Be respectful and inclusive
- Focus on constructive feedback
- Accept constructive criticism gracefully
- Prioritize the community's best interests

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- [UV](https://docs.astral.sh/uv/) package manager
- Git
- An LLM API key (Anthropic or OpenAI)

### Quick Start

```bash
# 1. Fork the repository on GitHub

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/multi-agent-tour-guide.git
cd multi-agent-tour-guide

# 3. Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/multi-agent-tour-guide.git

# 4. Set up the development environment
make setup

# 5. Create a branch for your changes
git checkout -b feature/your-feature-name

# 6. Make your changes and test
make test

# 7. Submit a pull request
```

---

## Development Setup

### Install Dependencies

```bash
# Install UV (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install all dependencies (dev + optional extras)
make all

# Or manually
uv sync --all-extras
```

### Environment Configuration

Create a `.env` file from the template:

```bash
cp env.example .env
```

Required environment variables:

```bash
# At least one LLM provider (Claude preferred)
ANTHROPIC_API_KEY=sk-ant-your-key-here
# OR
OPENAI_API_KEY=sk-your-key-here

# Optional for development
LOG_LEVEL=DEBUG
```

### Verify Setup

```bash
# Run checks
make check

# Run demo
make run-demo
```

---

## Project Structure

```
multi-agent-tour-guide/
├── src/                    # Main source code
│   ├── agents/            # AI agents (Video, Music, Text, Judge)
│   │   ├── base_agent.py  # Abstract base class
│   │   ├── video_agent.py
│   │   ├── music_agent.py
│   │   ├── text_agent.py
│   │   ├── judge_agent.py
│   │   └── configs/       # YAML agent configurations
│   │
│   ├── core/              # Core infrastructure
│   │   ├── orchestrator.py    # Agent coordination
│   │   ├── smart_queue.py     # Sync with timeouts
│   │   ├── collector.py       # Result aggregation
│   │   ├── plugins/           # Plugin architecture
│   │   ├── resilience/        # Circuit breaker, retry, etc.
│   │   ├── observability/     # Metrics, tracing, health
│   │   └── di/                # Dependency injection
│   │
│   ├── models/            # Pydantic data models
│   ├── services/          # External API clients
│   ├── cli/               # Command-line interface
│   └── utils/             # Utilities (config, logging)
│
├── plugins/               # Plugin directory
│   ├── weather/          # Example plugin
│   └── food/             # Template plugin
│
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── e2e/              # End-to-end tests
│
├── docs/                  # Documentation
├── config/                # Configuration files
└── data/                  # Runtime data (cache, logs)
```

### Key Files

| File | Purpose |
|------|---------|
| `main.py` | Application entry point |
| `pyproject.toml` | Project configuration and dependencies |
| `Makefile` | Build automation |
| `config/default.yaml` | Default configuration |

---

## Making Changes

### Types of Contributions

We welcome:

1. **Bug Fixes** - Fix issues and improve stability
2. **Features** - Add new functionality
3. **Documentation** - Improve docs, add examples
4. **Tests** - Increase coverage
5. **Plugins** - Create new content providers
6. **Performance** - Optimize existing code

### Branch Naming

Use descriptive branch names:

```
feature/add-weather-agent
fix/queue-timeout-handling
docs/api-reference-update
refactor/simplify-orchestrator
test/add-judge-tests
```

### Commit Messages

Follow conventional commits:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `chore`: Maintenance

**Examples:**

```
feat(agents): add weather agent for route points

Implements WeatherAgent using OpenWeatherMap API.
Includes caching and rate limiting.

Closes #123

---

fix(queue): handle edge case when all agents timeout

Previously, the queue would hang indefinitely if all
agents failed. Now properly raises NoResultsError.

---

docs(readme): update installation instructions for UV
```

---

## Coding Standards

### Python Style

We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting.

```bash
# Format code
make format

# Check linting
make lint
```

**Key Rules:**

- Line length: 88 characters
- Indentation: 4 spaces
- Quotes: Double quotes for strings
- Imports: Sorted with isort (via Ruff)

### Type Hints

Use type hints for all public functions:

```python
def evaluate(
    self,
    point: RoutePoint,
    candidates: List[ContentResult],
    user_profile: Optional[UserProfile] = None
) -> JudgeDecision:
    """
    Evaluate content candidates and select the best one.
    
    Args:
        point: The route point being evaluated
        candidates: List of content options
        user_profile: Optional user preferences
        
    Returns:
        JudgeDecision with selected content and reasoning
    """
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def search_content(self, location: str) -> Optional[ContentResult]:
    """
    Search for content related to a location.
    
    This method queries external APIs and uses LLM to
    generate relevant content recommendations.
    
    Args:
        location: Name or address of the location
        
    Returns:
        ContentResult if found, None otherwise
        
    Raises:
        APIError: If external API call fails
        
    Example:
        >>> agent = VideoAgent()
        >>> result = agent.search_content("Eiffel Tower")
        >>> print(result.title)
        "Eiffel Tower Documentary"
    """
```

### Error Handling

```python
# Good - specific exceptions with context
try:
    result = await api.fetch(location)
except APITimeoutError as e:
    logger.warning(f"API timeout for {location}: {e}")
    return self._fallback_content(location)
except APIError as e:
    logger.error(f"API error for {location}: {e}")
    raise ContentSearchError(f"Failed to search content: {e}") from e

# Bad - broad exception catching
try:
    result = await api.fetch(location)
except Exception as e:  # Too broad!
    return None
```

---

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
uv run pytest tests/unit/test_queue.py -v

# Run tests matching pattern
uv run pytest -k "test_timeout" -v
```

### Writing Tests

```python
# tests/unit/test_smart_queue.py

import pytest
from src.core.smart_queue import SmartAgentQueue, QueueStatus

class TestSmartQueue:
    """Tests for SmartAgentQueue."""
    
    def test_complete_when_all_agents_respond(self):
        """Queue should complete when all 3 agents submit results."""
        queue = SmartAgentQueue("test_point_1")
        
        queue.submit_success("video", mock_content("video"))
        queue.submit_success("music", mock_content("music"))
        queue.submit_success("text", mock_content("text"))
        
        results, metrics = queue.wait_for_results()
        
        assert len(results) == 3
        assert metrics.status == QueueStatus.COMPLETE
    
    def test_soft_degradation_after_timeout(self):
        """Queue should proceed with 2/3 after soft timeout."""
        queue = SmartAgentQueue("test_point_2")
        queue.SOFT_TIMEOUT_SECONDS = 0.1  # Fast for testing
        
        queue.submit_success("video", mock_content("video"))
        queue.submit_success("music", mock_content("music"))
        # Text agent doesn't respond
        
        results, metrics = queue.wait_for_results()
        
        assert len(results) == 2
        assert metrics.status == QueueStatus.SOFT_DEGRADED
    
    @pytest.fixture
    def mock_content(self, content_type: str) -> ContentResult:
        return ContentResult(
            content_type=content_type,
            title=f"Test {content_type}",
            source="Test"
        )
```

### Test Coverage

Aim for >80% coverage on new code:

```bash
# Generate coverage report
make test-cov

# View HTML report
open htmlcov/index.html
```

---

## Documentation

### Updating Documentation

1. **Code documentation**: Update docstrings
2. **API documentation**: Update `docs/API_REFERENCE.md`
3. **Architecture**: Update `docs/ARCHITECTURE_DETAILED.md`
4. **README**: Update if adding features

### Documentation Style

- Use clear, concise language
- Include code examples
- Add diagrams for complex concepts
- Keep docs in sync with code

---

## Submitting Changes

### Pull Request Process

1. **Ensure tests pass**: `make check`
2. **Update documentation**: If needed
3. **Create PR with descriptive title**
4. **Fill out PR template**
5. **Request review**

### PR Title Format

```
feat(scope): Short description

# Examples:
feat(agents): Add weather forecast agent
fix(queue): Handle timeout edge case correctly
docs(readme): Update installation instructions
```

### PR Description Template

```markdown
## Description
Brief description of the changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Refactoring
- [ ] Performance improvement

## Testing
Describe how you tested the changes.

## Checklist
- [ ] Tests pass (`make test`)
- [ ] Code is formatted (`make format`)
- [ ] Linting passes (`make lint`)
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

---

## Creating Plugins

### Plugin Development

Creating a new plugin is the best way to extend the system!

#### 1. Create Plugin Directory

```bash
mkdir -p plugins/my_plugin
```

#### 2. Create Plugin Manifest

```yaml
# plugins/my_plugin/plugin.yaml
name: my_plugin
version: 1.0.0
description: My awesome custom plugin
author: Your Name
capabilities:
  - CONTENT_PROVIDER
enabled: true
```

#### 3. Implement Plugin

```python
# plugins/my_plugin/plugin.py
from src.core.plugins.base import ContentProviderPlugin
from src.core.plugins.registry import PluginRegistry

@PluginRegistry.register("my_plugin")
class MyPlugin(ContentProviderPlugin):
    """My custom content provider."""
    
    def _on_start(self) -> None:
        """Initialize resources."""
        self.api_client = MyAPIClient(self.config.api_key)
    
    def _on_stop(self) -> None:
        """Cleanup resources."""
        self.api_client.close()
    
    def search_content(self, location: str, context: dict) -> dict:
        """Search for content at location."""
        result = self.api_client.search(location)
        return {
            "type": "my_content",
            "title": result.title,
            "description": result.description,
            "url": result.url
        }
    
    def get_content_type(self) -> str:
        return "my_content"
```

#### 4. Add Tests

```python
# tests/unit/test_my_plugin.py
from plugins.my_plugin.plugin import MyPlugin

def test_plugin_search():
    plugin = MyPlugin()
    plugin.configure({"api_key": "test"})
    plugin.start()
    
    result = plugin.search_content("Paris", {})
    
    assert result["type"] == "my_content"
    assert "title" in result
```

#### 5. Document Your Plugin

Add a README.md to your plugin directory explaining:
- What it does
- Required configuration
- Usage examples

---

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/yourusername/multi-agent-tour-guide/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/multi-agent-tour-guide/discussions)
- **Documentation**: [docs/](docs/)

---

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- README acknowledgments

Thank you for contributing! 🙏

---

<div align="center">

**Happy Contributing!** 🎉

</div>

