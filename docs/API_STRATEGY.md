# 🎯 API Mode Strategy Guide

## MIT-Level Architecture for Mocked vs Real API Usage

This document defines the strategy for when to use mocked data vs real API calls in the Multi-Agent Tour Guide System.

---

## 📋 Strategy Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    MIT-LEVEL API STRATEGY                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐           │
│   │   🧪 TEST    │     │  📊 DEMO     │     │ 🚀 PRODUCTION│           │
│   │   Always     │     │  Configurable│     │  Real + Cache│           │
│   │   MOCKED     │     │  MOCKED/REAL │     │  + Fallback  │           │
│   └──────────────┘     └──────────────┘     └──────────────┘           │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🎛️ Available Modes

| Mode | Description | When to Use |
|------|-------------|-------------|
| `auto` | Try real APIs, fallback to mock | Development, Production |
| `real` | Force real APIs (fail if unavailable) | Demo, Presentation |
| `mock` | Always use mocked data | Testing, CI/CD, Research |

---

## 📊 When to Use Each Mode

| Scenario | Mode | Reason |
|----------|------|--------|
| **Unit Tests** | 🎲 `mock` | Fast, deterministic, no API costs |
| **Integration Tests** | 🎲 `mock` | Reproducible, CI/CD friendly |
| **E2E Tests** | 🔀 `mock` + 1 real | Verify real APIs work |
| **Local Development** | 🔀 `auto` | Developer choice with fallback |
| **Demo/Presentation** | 🔴 `real` | Showcase actual capabilities |
| **Research Dashboard** | 🎲 `mock` | Statistical simulations |
| **Tour Guide Dashboard** | 🔴 `real` | Showcase real pipeline |
| **CI/CD Pipeline** | 🎲 `mock` | No API keys in CI |
| **Production** | 🔀 `auto` | Real + fallback for resilience |

---

## 🚀 Usage

### Command Line

```bash
# MIT Demo - Real APIs
uv run python run_tour_dashboard.py --mode real

# Fast Testing - Mocked Data  
uv run python run_tour_dashboard.py --mode mock

# Development - Auto (default)
uv run python run_tour_dashboard.py --mode auto
```

### Environment Variable

```bash
# Set globally
export TOUR_GUIDE_API_MODE=real   # For MIT demo
export TOUR_GUIDE_API_MODE=mock   # For testing
export TOUR_GUIDE_API_MODE=auto   # For development

# Run
uv run python run_tour_dashboard.py
```

### In Tests (pyproject.toml)

```toml
[tool.pytest.ini_options]
env = [
    "TOUR_GUIDE_API_MODE=mock",  # Tests always use mock
]
```

### In CI/CD (.github/workflows/ci.yml)

```yaml
env:
  TOUR_GUIDE_API_MODE: "mock"  # CI never uses real APIs
```

---

## 🏗️ Architecture

### Decision Flow

```
                        ┌─────────────────┐
                        │ TOUR_GUIDE_API  │
                        │     _MODE       │
                        └────────┬────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          ▼                      ▼                      ▼
   ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
   │  mode=mock   │      │  mode=auto   │      │  mode=real   │
   └──────┬───────┘      └──────┬───────┘      └──────┬───────┘
          │                     │                     │
          ▼                     ▼                     ▼
   ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
   │ Use mocked   │      │ Try real     │      │ Force real   │
   │ data always  │      │ → fallback   │      │ APIs only    │
   │              │      │   to mock    │      │ (fail if N/A)│
   └──────────────┘      └──────────────┘      └──────────────┘
```

### Code Implementation

```python
# In tour_guide_dashboard.py
import os
API_MODE = os.environ.get("TOUR_GUIDE_API_MODE", "auto")

# Decision logic
if API_MODE == "mock":
    use_real_apis = False  # Always mock
elif API_MODE == "real":
    use_real_apis = True   # Always real
elif API_MODE == "auto":
    use_real_apis = REAL_AGENTS_AVAILABLE  # Try real, fallback
```

---

## 📱 Dashboard Indicators

The Tour Guide Dashboard shows which mode is active:

| Badge | Meaning |
|-------|---------|
| 🔴 **LIVE** | Real API data (YouTube, Spotify, Claude) |
| ⚪ **DEMO** | Mocked/simulated data |

---

## 🔒 Security Considerations

### CI/CD Pipeline
- **Never** store API keys in CI
- Always use `TOUR_GUIDE_API_MODE=mock` in workflows
- Real API tests should be run locally before push

### Production
- Use `auto` mode for graceful degradation
- Implement caching for API responses
- Monitor API quota usage

---

## 📈 Performance Comparison

| Mode | Latency | API Calls | Cost | Reproducible |
|------|---------|-----------|------|--------------|
| `mock` | ~50ms | 0 | $0 | ✅ Yes |
| `auto` | 2-10s | 3-4 per point | ~$0.01 | ❌ No |
| `real` | 2-10s | 3-4 per point | ~$0.01 | ❌ No |

---

## 🧪 Test Configuration

### Unit Tests
```python
# Always mocked via pytest env
@pytest.fixture
def mock_agents():
    with patch('src.agents.video_agent.VideoAgent') as mock:
        yield mock
```

### One Real API Test (E2E)
```python
@pytest.mark.real_api
@pytest.mark.skipif(os.environ.get("TOUR_GUIDE_API_MODE") == "mock",
                    reason="Skipped in mock mode")
def test_real_youtube_api():
    """Verify YouTube API works (run locally only)."""
    agent = VideoAgent()
    result = agent.search("Tel Aviv")
    assert result is not None
```

---

## 📚 Related Documentation

- [README.md](../README.md) - Project overview
- [OPERATIONS_GUIDE.md](./OPERATIONS_GUIDE.md) - Full operational steps
- [API_KEYS_SETUP.md](./API_KEYS_SETUP.md) - How to get API keys

---

*This strategy ensures fast development, reliable CI/CD, and impressive demos.*

