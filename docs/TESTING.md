# 🧪 Testing Documentation

## MIT Level - Academic/Industrial Publishing Quality

This document describes the comprehensive testing strategy for the Multi-Agent Tour Guide System, designed to meet academic publishing standards with **85%+ code coverage**.

---

## 📊 Test Coverage Summary

| Category | Coverage Target | Description |
|----------|----------------|-------------|
| **Unit Tests** | 85%+ | Test individual components in isolation |
| **Integration Tests** | 75%+ | Test component interactions |
| **Performance Tests** | N/A | Benchmark critical paths |
| **Edge Cases** | 100% documented | All edge cases identified and tested |

---

## 🏗️ Test Structure

```
tests/
├── __init__.py
├── conftest.py                    # Shared fixtures
├── unit/                          # Unit tests
│   ├── __init__.py
│   ├── test_models_content.py     # Content model tests
│   ├── test_models_route.py       # Route model tests
│   ├── test_models_decision.py    # Decision model tests
│   ├── test_models_output.py      # Output model tests
│   ├── test_user_profile.py       # User profile tests
│   ├── test_smart_queue.py        # Smart queue tests
│   ├── test_config.py             # Configuration tests
│   ├── test_resilience_circuit_breaker.py
│   ├── test_resilience_retry.py
│   ├── test_resilience_timeout.py
│   └── test_resilience_rate_limiter.py
├── integration/                   # Integration tests
│   ├── __init__.py
│   ├── test_agent_integration.py
│   └── test_queue_integration.py
├── performance/                   # Performance tests
│   ├── __init__.py
│   └── test_performance.py
├── e2e/                          # End-to-end tests
│   └── __init__.py
└── fixtures/                     # Test data
```

---

## 🧩 Test Categories

### 1. Unit Tests (`tests/unit/`)

#### Data Models

| Test File | Component | Tests | Expected Result |
|-----------|-----------|-------|-----------------|
| `test_models_content.py` | ContentType, AgentStatus, ContentResult | 25+ | All content models validate correctly |
| `test_models_route.py` | RoutePoint, Route | 20+ | Route navigation works correctly |
| `test_models_decision.py` | JudgeDecision, AgentTask | 20+ | Decision workflow validates |
| `test_models_output.py` | TourGuideOutput, SystemState | 20+ | Output generation works |
| `test_user_profile.py` | UserProfile, presets | 10+ | Profile personalization works |

**Key Tests:**
- Content result validation with boundary scores (0-10)
- Route point coordinate handling (all hemispheres)
- Decision confidence validation (0-1)
- Unicode and special character handling

#### Core Infrastructure

| Test File | Component | Tests | Expected Result |
|-----------|-----------|-------|-----------------|
| `test_smart_queue.py` | SmartAgentQueue, QueueManager | 30+ | Queue synchronization works correctly |
| `test_config.py` | Settings, AGENT_SKILLS | 15+ | Configuration loads correctly |

**Key Tests:**
- All 3 agents succeed → COMPLETE status
- 2/3 agents succeed → SOFT_DEGRADED
- 1/3 agents succeed → HARD_DEGRADED  
- 0/3 agents succeed → FAILED with error

#### Resilience Patterns

| Test File | Pattern | Tests | Expected Result |
|-----------|---------|-------|-----------------|
| `test_resilience_circuit_breaker.py` | Circuit Breaker | 30+ | State transitions work correctly |
| `test_resilience_retry.py` | Retry with backoff | 25+ | Retries with exponential backoff |
| `test_resilience_timeout.py` | Timeout | 15+ | Operations timeout correctly |
| `test_resilience_rate_limiter.py` | Rate Limiting | 20+ | Request rate controlled |

**Key Tests:**
- Circuit breaker: CLOSED → OPEN → HALF_OPEN → CLOSED
- Retry: Exponential backoff with jitter
- Timeout: Sync and async timeout handling
- Rate limiter: Token bucket and sliding window

---

### 2. Integration Tests (`tests/integration/`)

| Test File | Scope | Tests | Expected Result |
|-----------|-------|-------|-----------------|
| `test_agent_integration.py` | Agent execution | 15+ | Agents produce valid content |
| `test_queue_integration.py` | Queue + Agents | 10+ | End-to-end queue processing |

**Key Scenarios:**
- Multiple agents processing same point
- Parallel agent execution
- Graceful degradation under failures
- Queue timeout handling

---

### 3. Performance Tests (`tests/performance/`)

| Test Area | Metric | Target | Purpose |
|-----------|--------|--------|---------|
| Queue throughput | Points/second | >10 | Verify scalability |
| Memory efficiency | Object growth | <1000 per 100 ops | No memory leaks |
| Lock contention | Time/increment | <1ms | Thread safety |
| Circuit breaker overhead | μs/call | <100 | Minimal overhead |
| Route creation | Time/1000 points | <1s | Model efficiency |

---

## 🚀 Running Tests

### Quick Commands

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test categories
uv run pytest tests/unit/ -v
uv run pytest tests/integration/ -v
uv run pytest tests/performance/ -v

# Run with coverage threshold enforcement
uv run pytest tests/ --cov=src --cov-fail-under=85

# Run specific test file
uv run pytest tests/unit/test_smart_queue.py -v

# Run tests matching pattern
uv run pytest -k "circuit_breaker" -v

# Run with verbose output
uv run pytest -v --tb=long
```

### Coverage Report

```bash
# Generate HTML coverage report
uv run pytest tests/ --cov=src --cov-report=html

# View report
open htmlcov/index.html

# Terminal coverage report
uv run pytest tests/ --cov=src --cov-report=term-missing
```

---

## 📋 Edge Cases Documented

### Content Models
- ✅ Relevance score at boundaries (0.0, 10.0)
- ✅ Empty titles and descriptions
- ✅ Unicode characters in all text fields
- ✅ Very long content (10,000+ chars)
- ✅ Special characters in URLs

### Route Models
- ✅ Empty route (no points)
- ✅ Very long routes (1000+ points)
- ✅ Negative coordinates (Western/Southern hemisphere)
- ✅ Boundary coordinates (poles, date line)
- ✅ Duplicate point IDs

### Queue System
- ✅ All agents succeed
- ✅ Partial agent failure (1, 2 agents fail)
- ✅ All agents fail
- ✅ Soft timeout with 2/3 results
- ✅ Hard timeout with 1/3 results
- ✅ Concurrent submissions
- ✅ Race conditions

### Resilience Patterns
- ✅ Circuit breaker state transitions
- ✅ Excluded exceptions
- ✅ Retry exhaustion
- ✅ Non-retryable exceptions
- ✅ Zero timeout
- ✅ Rate limit exceeded
- ✅ Token refill timing

---

## 🔧 Test Fixtures

### Common Fixtures (`conftest.py`)

```python
@pytest.fixture
def mock_route_point():
    """Standard route point for testing."""

@pytest.fixture
def mock_route():
    """Complete route with multiple points."""

@pytest.fixture
def mock_video_result():
    """Sample video content result."""

@pytest.fixture
def mock_music_result():
    """Sample music content result."""

@pytest.fixture
def mock_text_result():
    """Sample text content result."""

@pytest.fixture
def adult_profile():
    """Adult user profile."""

@pytest.fixture
def kid_profile():
    """Kid user profile (age-appropriate content)."""

@pytest.fixture
def driver_profile():
    """Driver profile (no video)."""
```

---

## 📈 CI/CD Integration

### GitHub Actions Workflow

The CI/CD pipeline runs:

1. **Lint & Format** - Ruff linter and formatter
2. **Unit Tests** - Python 3.10, 3.11, 3.12 matrix
3. **Integration Tests** - Component interaction testing
4. **Performance Tests** - Benchmark validation
5. **Coverage Report** - 85% threshold enforcement
6. **Security Scan** - Bandit, pip-audit, Trivy

### Coverage Threshold

```yaml
env:
  COVERAGE_THRESHOLD: 85

- name: Check coverage threshold
  run: |
    uv run coverage report --fail-under=${{ env.COVERAGE_THRESHOLD }}
```

### Test Artifacts

The CI generates:
- `coverage.xml` - Codecov integration
- `htmlcov/` - HTML coverage report
- `junit-*.xml` - Test results for reporting
- `bandit-report.json` - Security scan results

---

## 📊 Expected Test Results

### Passing Criteria

| Test Suite | Pass Criteria |
|------------|---------------|
| Unit Tests | All tests pass, 85%+ coverage |
| Integration Tests | All tests pass |
| Performance Tests | Meet benchmark targets |
| Security Scan | No CRITICAL vulnerabilities |

### Sample Output

```
======================== test session starts =========================
platform darwin -- Python 3.11.0, pytest-7.4.0
plugins: cov-4.1.0, asyncio-0.23.0
collected 180 tests

tests/unit/test_models_content.py::TestContentType::test_content_type_values PASSED
tests/unit/test_models_content.py::TestContentType::test_content_type_from_string PASSED
tests/unit/test_smart_queue.py::TestSmartAgentQueue::test_all_agents_succeed PASSED
...

----------- coverage: platform darwin, python 3.11.0-final-0 -----------
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
src/agents/base_agent.py                   82     12    85%
src/core/smart_queue.py                   148     20    86%
src/core/resilience/circuit_breaker.py   142     15    89%
src/models/content.py                      35      3    91%
...
-----------------------------------------------------------
TOTAL                                    1250    165    87%

======================== 180 passed in 12.54s =========================
```

---

## 🔍 Debugging Failed Tests

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure src is in PYTHONPATH
   export PYTHONPATH="${PYTHONPATH}:${PWD}"
   ```

2. **Timeout Issues**
   ```python
   # Increase timeouts for slow CI
   SmartAgentQueue.SOFT_TIMEOUT_SECONDS = 30.0
   ```

3. **Flaky Tests**
   ```bash
   # Run with retries
   uv run pytest --reruns 3 --reruns-delay 1
   ```

### Verbose Debugging

```bash
# Maximum verbosity
uv run pytest tests/unit/test_smart_queue.py -vvv --tb=long -s

# Stop on first failure
uv run pytest -x

# Run last failed tests
uv run pytest --lf
```

---

## 📝 Writing New Tests

### Test Template

```python
"""
Unit tests for [Component Name].

Test Coverage:
- [Feature 1]
- [Feature 2]
- Edge cases: [list edge cases]
"""
import pytest
from src.module import Component


class TestComponent:
    """Tests for Component class."""

    @pytest.fixture
    def component(self):
        """Create component instance."""
        return Component()

    def test_feature_basic(self, component):
        """Test basic feature functionality."""
        result = component.feature()
        assert result == expected

    def test_feature_edge_case(self, component):
        """Test feature with edge case input."""
        with pytest.raises(ValueError):
            component.feature(invalid_input)
```

### Naming Conventions

- Test files: `test_<module>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<feature>_<scenario>`

---

## 📚 References

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Plugin](https://pytest-cov.readthedocs.io/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [ISO/IEC 25010 Quality Standards](docs/ISO_IEC_25010_COMPLIANCE.md)

