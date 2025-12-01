# 🔧 Quick Fix Guide

## Multi-Agent Tour Guide System - Troubleshooting Reference

**Purpose:** Rapid problem resolution for common issues  
**Last Updated:** November 2025

---

## 📚 Quick Navigation

| Problem | Jump To |
|---------|---------|
| Installation fails | [Section 1](#1-installation-issues) |
| API key errors | [Section 2](#2-api-configuration) |
| Tests failing | [Section 3](#3-test-failures) |
| Import errors | [Section 4](#4-import-errors) |
| Agent not working | [Section 5](#5-agent-issues) |
| Queue timeouts | [Section 6](#6-queue-issues) |
| Performance slow | [Section 7](#7-performance-issues) |
| Docker issues | [Section 8](#8-docker-issues) |

---

## 1. Installation Issues

### 1.1 UV Not Found

**Symptom:**
```bash
command not found: uv
```

**Fix:**
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH (add to ~/.zshrc or ~/.bashrc)
export PATH="$HOME/.cargo/bin:$PATH"

# Reload shell
source ~/.zshrc
```

### 1.2 Python Version Mismatch

**Symptom:**
```
ERROR: Python 3.10+ required
```

**Fix:**
```bash
# Install Python 3.10+ with UV
uv python install 3.11

# Or specify version
uv venv --python 3.11
```

### 1.3 Dependencies Won't Install

**Symptom:**
```
ERROR: Could not find a version that satisfies the requirement...
```

**Fix:**
```bash
# Clear cache and reinstall
rm -rf .venv uv.lock
uv venv
uv sync --all-extras
```

### 1.4 Lock File Conflicts

**Symptom:**
```
ERROR: Lock file is out of date
```

**Fix:**
```bash
# Regenerate lock file
uv lock --upgrade
uv sync
```

---

## 2. API Configuration

### 2.1 Missing API Key

**Symptom:**
```
ERROR: ANTHROPIC_API_KEY not set
```

**Fix:**
```bash
# Create .env file
cp env.example .env

# Add your key
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" >> .env
```

### 2.2 Invalid API Key

**Symptom:**
```
AuthenticationError: Invalid API key
```

**Fix:**
1. Verify key at [Anthropic Console](https://console.anthropic.com/)
2. Check for extra spaces/quotes in .env
3. Ensure key starts with `sk-ant-`

```bash
# Debug: Print key (first 10 chars only)
python -c "import os; print(os.getenv('ANTHROPIC_API_KEY', 'NOT SET')[:10])"
```

### 2.3 Rate Limit Exceeded

**Symptom:**
```
RateLimitError: Rate limit exceeded
```

**Fix:**
```bash
# Option 1: Add delay between runs
sleep 60 && make run

# Option 2: Use demo mode (no API calls)
make run --demo

# Option 3: Configure lower concurrency
# In config/default.yaml:
# orchestrator:
#   max_parallel_agents: 1
```

### 2.4 Wrong Model

**Symptom:**
```
ModelNotFoundError: claude-sonnet-4 not found
```

**Fix:**
```yaml
# In config/default.yaml, update model:
llm:
  model: "claude-sonnet-4-20250514"  # Use exact model name
```

---

## 3. Test Failures

### 3.1 Tests Not Found

**Symptom:**
```
collected 0 items
```

**Fix:**
```bash
# Ensure in project root
cd /path/to/project

# Run with verbose
uv run pytest tests/ -v --collect-only
```

### 3.2 Import Errors in Tests

**Symptom:**
```
ModuleNotFoundError: No module named 'src'
```

**Fix:**
```bash
# Install package in dev mode
uv sync --extra dev

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### 3.3 Fixture Not Found

**Symptom:**
```
fixture 'mock_point' not found
```

**Fix:**
```bash
# Ensure conftest.py exists
ls tests/conftest.py

# Check fixture scope
# In conftest.py, ensure:
@pytest.fixture(scope="function")
def mock_point():
    ...
```

### 3.4 Coverage Below Threshold

**Symptom:**
```
FAIL Required test coverage of 85% not reached. Total coverage: 82%
```

**Fix:**
```bash
# Find uncovered code
uv run pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html

# Add tests for uncovered sections
# Or temporarily lower threshold:
uv run pytest tests/ --cov=src --cov-fail-under=80
```

---

## 4. Import Errors

### 4.1 Circular Import

**Symptom:**
```
ImportError: cannot import name 'X' from partially initialized module
```

**Fix:**
```python
# Use TYPE_CHECKING for type hints
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.content import ContentResult

# Or use string annotations
def my_func() -> "ContentResult":
    ...
```

### 4.2 Module Not Found

**Symptom:**
```
ModuleNotFoundError: No module named 'src.agents'
```

**Fix:**
```bash
# Check __init__.py files exist
find src -name "__init__.py" | head

# Create missing ones
touch src/__init__.py
touch src/agents/__init__.py

# Reinstall
uv sync
```

### 4.3 Relative Import Issues

**Symptom:**
```
ImportError: attempted relative import with no known parent package
```

**Fix:**
```python
# Use absolute imports instead
# Bad:
from ..models import ContentResult

# Good:
from src.models import ContentResult
```

---

## 5. Agent Issues

### 5.1 Video Agent Returns None

**Symptom:**
```
VideoAgent returned None for all locations
```

**Causes & Fixes:**

| Cause | Check | Fix |
|-------|-------|-----|
| Driver profile | `profile.is_driver` | Expected behavior! |
| No YouTube API | `YOUTUBE_API_KEY` | Add key or use mock |
| Rate limited | Check logs | Wait and retry |

```python
# Debug agent
import logging
logging.getLogger("src.agents").setLevel(logging.DEBUG)

result = video_agent.execute(point, profile, queue)
```

### 5.2 Agent Timeout

**Symptom:**
```
TimeoutError: Agent did not respond within 30s
```

**Fix:**
```yaml
# In config/default.yaml, increase timeout:
agents:
  core:
    - type: video
      timeout: 60  # Increase from 30
```

### 5.3 Low Relevance Scores

**Symptom:**
```
All content has relevance_score < 5.0
```

**Fix:**
```python
# Check LLM prompt - may need better context
# In src/agents/video_agent.py:
def _build_search_prompt(self, point, profile):
    # Add more location context
    return f"""
    Location: {point.location_name}
    Region: {point.region}
    Historical significance: {point.significance}
    ...
    """
```

### 5.4 Wrong Content Selected

**Symptom:**
```
Judge selected video for driver profile
```

**Fix:**
```python
# Check weight calculation in judge_agent.py
weights = profile.get_content_type_preferences()
assert weights.get("video", 1.0) == 0.0, "Driver should have 0 video weight"
```

---

## 6. Queue Issues

### 6.1 Always Soft Degraded

**Symptom:**
```
Queue status: SOFT_DEGRADED (every time)
```

**Causes:**
- One agent consistently slow
- Timeout too short
- Agent failing silently

**Fix:**
```bash
# Check agent timing
LOG_LEVEL=DEBUG make run-queue 2>&1 | grep -E "(submit_success|submit_failure)"

# Increase timeout
# In config/default.yaml:
queue:
  soft_timeout_seconds: 20.0  # Default: 15.0
```

### 6.2 Queue Never Completes

**Symptom:**
```
Queue hangs indefinitely
```

**Fix:**
```python
# Check for deadlock in smart_queue.py
# Ensure condition.notify_all() is called on every submit

# Add timeout to wait_for_results
results, metrics = queue.wait_for_results(timeout=60)
```

### 6.3 Missing Results

**Symptom:**
```
Expected 3 results, got 1
```

**Debug:**
```python
# Check queue state
print(f"Succeeded: {queue._succeeded_agents}")
print(f"Failed: {queue._failed_agents}")
print(f"Results count: {len(queue._results)}")
```

---

## 7. Performance Issues

### 7.1 System Slow

**Symptom:**
```
Processing takes > 60s per point
```

**Fixes:**

```bash
# 1. Enable caching
export ENABLE_CACHE=true

# 2. Reduce concurrent points
# In config/default.yaml:
orchestrator:
  max_parallel_points: 2  # Down from 4

# 3. Use faster model
llm:
  model: "gpt-4o-mini"  # Faster than claude-sonnet-4
```

### 7.2 Memory Issues

**Symptom:**
```
MemoryError or process killed
```

**Fix:**
```bash
# Limit batch size
# In config/default.yaml:
orchestrator:
  batch_size: 5  # Process 5 points at a time

# Or run with memory limit
ulimit -m 2097152  # 2GB limit
make run
```

### 7.3 High CPU Usage

**Symptom:**
```
CPU at 100% continuously
```

**Fix:**
```python
# Add sleep between API calls
import time
time.sleep(0.5)  # 500ms between calls

# Or reduce thread pool size
MAX_WORKERS = 6  # Down from 12
```

---

## 8. Docker Issues

### 8.1 Build Fails

**Symptom:**
```
ERROR: failed to solve: dockerfile parse error
```

**Fix:**
```bash
# Use correct Dockerfile syntax
# Ensure Dockerfile starts with:
# syntax=docker/dockerfile:1

docker build --no-cache -t tour-guide .
```

### 8.2 Container Can't Access API

**Symptom:**
```
Connection refused to API
```

**Fix:**
```bash
# Pass env vars to container
docker run -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY tour-guide

# Or use env file
docker run --env-file .env tour-guide
```

### 8.3 Port Conflicts

**Symptom:**
```
Error: port 8000 already in use
```

**Fix:**
```bash
# Find and kill process
lsof -i :8000
kill -9 <PID>

# Or use different port
docker run -p 8001:8000 tour-guide
```

---

## 9. Quick Diagnostic Commands

### Health Check
```bash
# Full system check
make check

# Just tests
make test-unit

# Just linting
make lint
```

### View Logs
```bash
# Verbose mode
LOG_LEVEL=DEBUG make run

# Filter by component
make run 2>&1 | grep -E "(ERROR|WARN)"

# Save to file
make run 2>&1 | tee run.log
```

### Reset Environment
```bash
# Full reset
make clean-all
rm -rf .venv uv.lock
make setup
```

### Verify Configuration
```bash
# Print effective config
uv run python -c "
from src.utils.config import get_config
import yaml
print(yaml.dump(get_config()))
"
```

---

## 10. Getting Help

### Check Documentation
```bash
# Open docs
ls docs/

# Key files:
# - ARCHITECTURE.md - System design
# - API_REFERENCE.md - API docs
# - TESTING.md - Test guide
# - PROMPT_BOOK.md - All prompts
```

### Search Issues
```bash
# Search for similar problems
grep -r "error message" docs/
grep -r "symptom" tests/
```

### Contact
- Open GitHub Issue with:
  - Error message (full traceback)
  - Steps to reproduce
  - Environment (OS, Python version, UV version)
  - Configuration (sanitized, no API keys)

---

## 11. Fix Checklist

When something breaks, go through this checklist:

```markdown
□ 1. Read the full error message
□ 2. Check this QUICKFIX.md for the symptom
□ 3. Run make check to see full status
□ 4. Check configuration files (.env, config/*.yaml)
□ 5. Check logs (LOG_LEVEL=DEBUG)
□ 6. Search docs/ for related information
□ 7. Try make clean-all && make setup (fresh install)
□ 8. Open GitHub issue if still stuck
```

---

**Document Version:** 1.0.0  
**Maintainer:** Multi-Agent Tour Guide Team

