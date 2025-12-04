# 🎯 API Mode Strategy Guide

## MIT-Level Architecture: Real Data First, Mock as Fallback

This document defines the strategy for when to use real API calls vs mocked data in the Multi-Agent Tour Guide System.

---

## 📋 Core Principle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MIT-LEVEL API STRATEGY (UPDATED)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌────────────────┐    ┌────────────────┐    ┌────────────────┐           │
│   │  🖥️ ALL UI     │    │   🧪 TESTS    │    │   🔄 CI/CD     │           │
│   │  REAL DATA     │    │   ALWAYS      │    │   ALWAYS       │           │
│   │  (+ fallback)  │    │   MOCKED      │    │   MOCKED       │           │
│   └────────────────┘    └────────────────┘    └────────────────┘           │
│         │                      │                     │                      │
│         ▼                      ▼                     ▼                      │
│   Production-ready       Deterministic         No API keys                 │
│   demonstrations         reproducible          in CI                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎛️ Available Modes

| Mode | Description | Default For |
|------|-------------|-------------|
| `auto` | **Prefer real**, fallback to mock | All UI dashboards, CLI |
| `real` | Force real APIs (error if unavailable) | MIT demos, presentations |
| `mock` | Always use mocked data | Tests, CI/CD only |

---

## 📊 Mode Assignment by Component

| Component | Default Mode | Reason |
|-----------|--------------|--------|
| **Tour Guide Dashboard** | `auto` (prefers real) | Showcase actual capabilities |
| **Research Dashboard** | `auto` (prefers real) | Real system metrics |
| **CLI** | `auto` (prefers real) | Interactive demonstrations |
| **Unit Tests** | `mock` | Fast, deterministic |
| **Integration Tests** | `mock` | Reproducible results |
| **E2E Tests** | `mock` + 1 real | Verify real APIs work |
| **CI/CD Pipeline** | `mock` | No API keys in CI |
| **Performance Tests** | `mock` | Consistent benchmarks |

---

## 🚀 Usage

### For UI (Dashboards) - Real Data by Default

```bash
# Start with real data (default behavior now)
python run_tour_dashboard.py

# Or explicitly
python run_tour_dashboard.py --mode auto

# Force real APIs (error if unavailable)
python run_tour_dashboard.py --mode real
```

### For Tests - Always Mocked

```bash
# Run tests (automatically uses mock via pyproject.toml)
make test

# Environment is set automatically
# TOUR_GUIDE_API_MODE=mock
```

### Environment Variable Override

```bash
# For development - prefer real
export TOUR_GUIDE_API_MODE=auto

# For CI/CD - force mock
export TOUR_GUIDE_API_MODE=mock
```

---

## 🏗️ Decision Flow

```
                              ┌─────────────────────┐
                              │   Application       │
                              │   Starts            │
                              └──────────┬──────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │  Check Environment  │
                              │  TOUR_GUIDE_API_MODE│
                              └──────────┬──────────┘
                                         │
              ┌──────────────────────────┼──────────────────────────┐
              │                          │                          │
              ▼                          ▼                          ▼
       ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
       │ mode=mock   │          │ mode=auto   │          │ mode=real   │
       │ (CI/Tests)  │          │ (UI Default)│          │ (MIT Demo)  │
       └──────┬──────┘          └──────┬──────┘          └──────┬──────┘
              │                        │                        │
              ▼                        ▼                        ▼
       ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
       │ Use mock    │          │ Check API   │          │ Force real  │
       │ data always │          │ availability│          │ APIs only   │
       └─────────────┘          └──────┬──────┘          └─────────────┘
                                       │
                          ┌────────────┴────────────┐
                          │                         │
                          ▼                         ▼
                   ┌─────────────┐          ┌─────────────┐
                   │ APIs Ready  │          │ APIs NOT    │
                   │ → Use Real  │          │ Available   │
                   │ 🔴 LIVE     │          │ → Fallback  │
                   └─────────────┘          │ ⚪ DEMO     │
                                            └─────────────┘
```

---

## 📱 UI Indicators

All dashboards show real-time data status:

| Badge | Meaning | Color |
|-------|---------|-------|
| 🔴 **LIVE** | Real API data active | Green/Cyan |
| ⚪ **DEMO** | Using mock data (fallback) | Gray |
| 🟡 **PARTIAL** | Some APIs real, some mock | Yellow |

### Example Header

```
┌────────────────────────────────────────────────────────┐
│  🗺️ MULTI-AGENT TOUR GUIDE          [🔴 LIVE DATA]    │
│                                                        │
│  APIs: YouTube ✅ | Spotify ✅ | Claude ✅ | Maps ✅   │
└────────────────────────────────────────────────────────┘
```

---

## 🔧 Configuration Files

### pyproject.toml (Tests)

```toml
[tool.pytest.ini_options]
env = [
    "TOUR_GUIDE_API_MODE=mock",  # Tests ALWAYS use mock
]
```

### .github/workflows/ci.yml (CI/CD)

```yaml
env:
  TOUR_GUIDE_API_MODE: "mock"  # CI NEVER uses real APIs
```

### .env.example (Local Development)

```bash
# API Mode (auto = real with fallback, mock = always mock, real = force real)
TOUR_GUIDE_API_MODE=auto

# API Keys (required for real mode)
GOOGLE_MAPS_API_KEY=your_key_here
YOUTUBE_API_KEY=your_key_here
SPOTIFY_CLIENT_ID=your_id_here
SPOTIFY_CLIENT_SECRET=your_secret_here
ANTHROPIC_API_KEY=your_key_here
```

---

## 📈 Performance Characteristics

| Mode | Latency | API Calls | Cost | Reproducible |
|------|---------|-----------|------|--------------|
| `mock` | ~50ms | 0 | $0 | ✅ Yes |
| `auto` (real available) | 2-10s | 3-4 per point | ~$0.01 | ❌ No |
| `auto` (fallback) | ~100ms | 0 | $0 | ✅ Yes |
| `real` | 2-10s | 3-4 per point | ~$0.01 | ❌ No |

---

## 🔒 Security

### API Keys Protection

- ✅ Never commit API keys to git
- ✅ Use `.env` file (gitignored) for local development
- ✅ Use GitHub Secrets for production
- ✅ CI/CD always uses mock mode (no keys needed)

### Rate Limiting

- YouTube: 10,000 units/day
- Spotify: 100 requests/minute
- Claude: Check your plan limits
- Google Maps: Check your billing

---

## 🧪 Test Configuration

### All Unit/Integration Tests

```python
# conftest.py - Enforced mock mode
import os
os.environ["TOUR_GUIDE_API_MODE"] = "mock"
```

### One Real API Smoke Test

```python
@pytest.mark.real_api
@pytest.mark.skipif(
    os.environ.get("TOUR_GUIDE_API_MODE") == "mock",
    reason="Skipped in mock mode - run locally"
)
def test_real_youtube_api():
    """Verify YouTube API works (run locally only)."""
    from src.agents.video_agent import VideoAgent
    agent = VideoAgent()
    result = agent.execute(RoutePoint(index=0, address="Tel Aviv"))
    assert result is not None
```

---

## 📚 Quick Reference

```bash
# UI with real data (default)
make run-system
python run_tour_dashboard.py

# Force real APIs (MIT demo)
TOUR_GUIDE_API_MODE=real python run_tour_dashboard.py

# Run tests (always mock)
make test

# Check current mode
curl http://localhost:8000/health | jq .api_mode
```

---

*This strategy ensures: Real data for demos, Fast tests, Secure CI/CD*
