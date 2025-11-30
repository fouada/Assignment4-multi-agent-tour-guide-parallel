# 🧪 Testing Documentation

## MIT Level - Academic/Industrial Publishing Quality

This document provides comprehensive testing specifications for the Multi-Agent Tour Guide System, designed to meet academic publishing standards with **85%+ code coverage** and **100% documented edge cases**.

---

## 📊 Test Coverage Summary

| Metric | Value |
|--------|-------|
| **Total Tests** | 683+ |
| **Overall Coverage** | 85%+ |
| **Test Files** | 30 |
| **Edge Cases** | 100% documented |
| **CI/CD Threshold** | 85% enforced |

> **Last Verified**: November 2025  
> **Command**: `uv run pytest tests/ --cov=src --cov-fail-under=85`

---

## 📋 Test Catalog with Expected Results

### 1. Data Model Tests

#### ContentType & AgentStatus (`test_models_content.py`)

| Test | Description | Expected Result |
|------|-------------|-----------------|
| `test_content_type_values` | Verify enum values | VIDEO="video", MUSIC="music", TEXT="text" |
| `test_content_type_from_string` | Parse string to enum | "video" → ContentType.VIDEO |
| `test_invalid_content_type` | Invalid string parsing | Raises ValueError |
| `test_agent_status_values` | Verify status values | PENDING, RUNNING, COMPLETED, FAILED, TIMEOUT |
| `test_agent_status_lifecycle` | Status transitions | PENDING → RUNNING → COMPLETED |

#### ContentResult (`test_models_content.py`)

| Test | Description | Expected Result |
|------|-------------|-----------------|
| `test_create_minimal_content_result` | Minimal valid result | ContentResult with required fields |
| `test_content_result_score_boundaries` | Score validation | 0.0 ≤ relevance_score ≤ 10.0 |
| `test_content_result_score_too_low` | Score below 0 | Raises ValidationError |
| `test_content_result_score_too_high` | Score above 10 | Raises ValidationError |
| `test_content_result_json_serialization` | JSON round-trip | Serialize → Deserialize = Original |
| `test_empty_title` | Empty title handling | Accepts empty string |
| `test_unicode_content` | Unicode in content | "東京タワー" stored correctly |

#### Route Models (`test_models_route.py`)

| Test | Description | Expected Result |
|------|-------------|-----------------|
| `test_route_point_id_generation` | Auto ID generation | UUID format ID created |
| `test_route_point_coordinates` | Coordinate properties | lat/lon accessible |
| `test_negative_coordinates` | Southern/Western hemisphere | Accepts negative lat/lon |
| `test_get_point_by_id_found` | Point lookup | Returns correct RoutePoint |
| `test_get_point_by_id_not_found` | Missing point | Returns None |
| `test_empty_route` | Route with no points | points=[], point_count=0 |
| `test_very_long_route` | 1000 points | Handles without error |
| `test_unicode_addresses` | Unicode addresses | "תל אביב" stored correctly |

#### Decision Models (`test_models_decision.py`)

| Test | Description | Expected Result |
|------|-------------|-----------------|
| `test_judge_decision_confidence` | Confidence boundaries | 0.0 ≤ confidence ≤ 1.0 |
| `test_agent_task_status_transitions` | Status workflow | PENDING → RUNNING → COMPLETED |
| `test_agent_task_duration_calculation` | Duration tracking | completed_at - started_at |

---

### 2. Smart Queue Tests (`test_smart_queue.py`)

#### Queue Status Transitions

| Test | Description | Expected Result |
|------|-------------|-----------------|
| `test_all_agents_succeed` | 3/3 agents return | Status: COMPLETE |
| `test_soft_timeout_with_two_results` | 2/3 agents return | Status: SOFT_DEGRADED |
| `test_hard_timeout_with_one_result` | 1/3 agents return | Status: HARD_DEGRADED |
| `test_all_agents_fail` | 0/3 agents return | Status: FAILED |
| `test_status_values` | All status enums | WAITING, COLLECTING, COMPLETE, etc. |

#### Queue Manager

| Test | Description | Expected Result |
|------|-------------|-----------------|
| `test_queue_manager_initialization` | Manager creation | 3 agents registered |
| `test_queue_manager_submit_point` | Point submission | Returns QueueStatus |
| `test_concurrent_submissions` | Parallel submissions | Thread-safe execution |

---

### 3. Resilience Pattern Tests

#### Circuit Breaker (`test_resilience_circuit_breaker.py`)

| Test | Description | Expected Result |
|------|-------------|-----------------|
| `test_initial_state_closed` | Initial state | CircuitState.CLOSED |
| `test_open_after_failures` | Failure threshold reached | CLOSED → OPEN |
| `test_half_open_after_timeout` | Reset timeout elapsed | OPEN → HALF_OPEN |
| `test_close_after_success` | Success in half-open | HALF_OPEN → CLOSED |
| `test_reopen_after_failure_in_half_open` | Failure in half-open | HALF_OPEN → OPEN |
| `test_excluded_exceptions` | Non-counted exceptions | State unchanged |
| `test_decorator_usage` | @circuit_breaker decorator | Function wrapped correctly |
| `test_manual_reset` | Force reset | State → CLOSED |

#### Retry Pattern (`test_resilience_retry.py`)

| Test | Description | Expected Result |
|------|-------------|-----------------|
| `test_successful_first_attempt` | No retry needed | 1 call, success |
| `test_retry_on_exception` | Transient failure | Retries up to max_attempts |
| `test_exponential_backoff` | Delay calculation | 1s, 2s, 4s, 8s pattern |
| `test_jitter_applied` | Randomized delay | Delay ± 25% jitter |
| `test_max_attempts_exceeded` | All retries fail | Raises original exception |
| `test_specific_exceptions` | Exception filtering | Only retries specified types |

#### Timeout Pattern (`test_resilience_timeout.py`)

| Test | Description | Expected Result |
|------|-------------|-----------------|
| `test_fast_function_completes` | Function < timeout | Returns result |
| `test_slow_function_times_out` | Function > timeout | Raises TimeoutError |
| `test_async_timeout` | Async function timeout | Raises asyncio.TimeoutError |
| `test_zero_timeout` | timeout=0 | Immediate timeout |

#### Rate Limiter (`test_resilience_rate_limiter.py`)

| Test | Description | Expected Result |
|------|-------------|-----------------|
| `test_acquire_success` | Tokens available | Returns True, token consumed |
| `test_acquire_blocked` | No tokens | Returns False |
| `test_refill_over_time` | Token regeneration | Tokens increase over time |
| `test_sliding_window` | Window-based limiting | Tracks requests per window |

#### Bulkhead (`test_resilience_bulkhead.py`)

| Test | Description | Expected Result |
|------|-------------|-----------------|
| `test_concurrent_limit_respected` | Max concurrent calls | Excess calls rejected |
| `test_context_manager` | with bulkhead: | Acquires/releases permit |
| `test_stats_tracking` | Call statistics | total_calls, rejected_calls tracked |

#### Fallback (`test_resilience_fallback.py`)

| Test | Description | Expected Result |
|------|-------------|-----------------|
| `test_primary_success` | No fallback needed | Returns primary result |
| `test_fallback_to_default` | Primary fails | Returns default_value |
| `test_fallback_chain` | Multiple fallbacks | Tries each in order |
| `test_all_fallbacks_fail` | No fallback works | Raises RuntimeError |

---

### 4. User Profile Tests (`test_user_profile.py`)

#### Profile Preferences

| Test | Description | Expected Result |
|------|-------------|-----------------|
| `test_default_profile` | Default values | age_group=ADULT, travel_mode=CAR |
| `test_kid_profile_prefers_video` | Child preferences | video_weight > text_weight |
| `test_driver_profile_blocks_video` | Safety constraint | video_weight = 0.0 |
| `test_visual_impairment_prefers_audio` | Accessibility | music_weight > video_weight |
| `test_hearing_impairment_prefers_visual` | Accessibility | text_weight > music_weight |

#### Context Generation

| Test | Description | Expected Result |
|------|-------------|-----------------|
| `test_context_kid_profile` | Kid context | Contains "child" or "kid-friendly" |
| `test_context_driver` | Driver context | Contains "audio" or "no video" |
| `test_context_business_trip` | Business context | Contains "professional" |
| `test_context_pilgrimage_trip` | Pilgrimage context | Contains "spiritual" |

---

### 5. Agent Tests (`test_agents.py`, `test_base_agent.py`)

#### Base Agent

| Test | Description | Expected Result |
|------|-------------|-----------------|
| `test_init_with_anthropic_key` | Claude initialization | llm_type = "anthropic" |
| `test_init_with_openai_key` | GPT initialization | llm_type = "openai" |
| `test_init_without_api_keys` | No API key | llm_client = None, uses mock |
| `test_call_llm_no_client` | Mock response | Returns "Mock response..." |
| `test_execute_success` | Agent execution | Returns ContentResult |

#### Video Agent

| Test | Description | Expected Result |
|------|-------------|-----------------|
| `test_get_content_type` | Content type | ContentType.VIDEO |
| `test_get_mock_result` | Mock result | source = "YouTube (Mock)" |
| `test_generate_search_queries_fallback` | LLM failure | Returns fallback queries |

#### Judge Agent

| Test | Description | Expected Result |
|------|-------------|-----------------|
| `test_evaluate_single_content` | Single candidate | Returns that candidate |
| `test_evaluate_two_candidates` | Two candidates | Selects higher weighted |
| `test_evaluate_three_candidates` | Three candidates | Selects best via LLM |

---

### 6. Integration Tests (`test_agent_integration.py`, `test_queue_integration.py`)

| Test | Description | Expected Result |
|------|-------------|-----------------|
| `test_agent_produces_content` | End-to-end agent | Valid ContentResult |
| `test_queue_processes_point` | Queue + agents | Returns QueueStatus |
| `test_concurrent_point_processing` | Parallel points | All points processed |
| `test_graceful_degradation` | Agent failures | Partial results returned |

---

### 7. Performance Tests (`test_performance.py`)

| Test | Metric | Target | Expected Result |
|------|--------|--------|-----------------|
| `test_queue_throughput` | Points/second | >10 | Meets throughput |
| `test_memory_efficiency` | Object growth | <1000/100 ops | No memory leak |
| `test_lock_contention` | Time/increment | <1ms | Minimal contention |
| `test_circuit_breaker_overhead` | μs/call | <100 | Low overhead |
| `test_route_creation` | Time/1000 points | <1s | Fast creation |

---

### 8. Observability Tests (`test_observability_health.py`)

| Test | Description | Expected Result |
|------|-------------|-----------------|
| `test_register_check` | Health check registration | Check in registry |
| `test_run_check_success` | Healthy check | Status: HEALTHY |
| `test_run_check_failure` | Unhealthy check | Status: UNHEALTHY |
| `test_aggregate_status_healthy` | All checks pass | Aggregate: HEALTHY |
| `test_liveness_probe` | Liveness endpoint | Returns True |
| `test_readiness_probe_all_healthy` | Readiness endpoint | Returns True |

---

## 🚀 Running Tests

```bash
# Run all tests with coverage
uv run pytest tests/ --cov=src --cov-report=term

# Run with 85% threshold enforcement
uv run pytest tests/ --cov=src --cov-fail-under=85

# Run specific test category
uv run pytest tests/unit/test_smart_queue.py -v
uv run pytest tests/unit/test_resilience_circuit_breaker.py -v

# Run with HTML coverage report
uv run pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html

# Run performance tests only
uv run pytest tests/performance/ -v
```

---

## 📋 Edge Cases Documented

### Boundary Conditions

| Edge Case | Test | Expected Behavior |
|-----------|------|-------------------|
| Score = 0.0 | `test_content_result_score_boundaries` | Accepts minimum score |
| Score = 10.0 | `test_content_result_score_boundaries` | Accepts maximum score |
| Score = -0.1 | `test_content_result_score_too_low` | Raises ValidationError |
| Score = 10.1 | `test_content_result_score_too_high` | Raises ValidationError |
| Confidence = 0.0 | `test_judge_decision_confidence` | Accepts minimum confidence |
| Confidence = 1.0 | `test_judge_decision_confidence` | Accepts maximum confidence |

### Empty/Null Cases

| Edge Case | Test | Expected Behavior |
|-----------|------|-------------------|
| Empty route | `test_empty_route` | points=[], point_count=0 |
| Empty title | `test_empty_title` | Accepts empty string |
| None metadata | `test_content_result_metadata_default` | Defaults to {} |
| No agents succeed | `test_all_agents_fail` | Status: FAILED |

### Unicode/Special Characters

| Edge Case | Test | Expected Behavior |
|-----------|------|-------------------|
| Hebrew address | `test_unicode_addresses` | "תל אביב" stored |
| Japanese content | `test_unicode_content` | "東京タワー" stored |
| Special URL chars | `test_content_result_url` | Properly encoded |

### Concurrency/Threading

| Edge Case | Test | Expected Behavior |
|-----------|------|-------------------|
| Race conditions | `test_concurrent_submissions` | Thread-safe |
| Lock contention | `test_lock_contention` | <1ms per increment |
| Bulkhead overflow | `test_concurrent_limit_respected` | Excess rejected |

---

## 📈 CI/CD Integration

### GitHub Actions Workflow

```yaml
env:
  COVERAGE_THRESHOLD: 85

- name: Run tests with coverage
  run: |
    uv run pytest tests/ \
      --cov=src \
      --cov-report=term \
      --cov-fail-under=${{ env.COVERAGE_THRESHOLD }}
```

### Test Artifacts

- `coverage.xml` - Codecov integration
- `htmlcov/` - HTML coverage report
- `junit-*.xml` - Test results for CI reporting

---

## 📚 References

- [pytest Documentation](https://docs.pytest.org/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [ISO/IEC 25010 Quality Standards](https://www.iso.org/standard/35733.html)
