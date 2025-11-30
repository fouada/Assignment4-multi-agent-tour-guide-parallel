# ADR-003: Circuit Breaker for Resilience

## Status

Accepted

## Date

2025-11

## Context

The system makes external API calls to:
- LLM providers (Anthropic, OpenAI)
- YouTube API
- Spotify API
- Wikipedia API

These external dependencies can:
1. **Fail temporarily** (network issues, rate limits)
2. **Fail persistently** (service outage)
3. **Degrade** (slow responses)

Without protection, cascading failures can occur:
- Failed requests timeout
- Timeouts consume threads
- Thread pool exhaustion
- System-wide failure

## Decision

Implement the **Circuit Breaker pattern** as described by Michael Nygard.

### States

```
     ┌─────────────────────────────────────────────────┐
     │                    CLOSED                        │
     │            (normal operation)                    │
     │      Failure count < threshold (5)              │
     └─────────────────────────────────────────────────┘
                          │
                          │ 5 failures
                          ▼
     ┌─────────────────────────────────────────────────┐
     │                     OPEN                         │
     │         (fail fast, don't call service)         │
     │            Timer: 60 seconds                     │
     └─────────────────────────────────────────────────┘
                          │
                          │ timeout expires
                          ▼
     ┌─────────────────────────────────────────────────┐
     │                  HALF_OPEN                       │
     │          (allow test request)                    │
     │     Success → CLOSED | Failure → OPEN           │
     └─────────────────────────────────────────────────┘
```

### Configuration

```python
@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5      # Failures to trip
    success_threshold: int = 3      # Successes to close
    reset_timeout: float = 60.0     # Seconds in OPEN state
    excluded_exceptions: tuple = () # Don't count these
```

### Usage

```python
# As decorator
@circuit_breaker(name="youtube_api")
def search_youtube(query: str) -> dict:
    return youtube_client.search(query)

# As context manager
with CircuitBreaker("spotify_api") as cb:
    if cb.allow_request():
        result = spotify_client.search(query)
        cb.record_success()
```

## Consequences

### Positive

- **Fail Fast**: Don't waste resources on known-failing services
- **Recovery**: Automatic recovery when service returns
- **Visibility**: Clear metrics on service health
- **Protection**: Prevents cascading failures

### Negative

- **False Positives**: May trip on transient failures
- **Complexity**: Additional state to manage
- **Latency**: Adds small overhead to each call

### Neutral

- Requires tuning of thresholds
- Needs monitoring dashboard

## Alternatives Considered

### Alternative 1: Simple Retry Only

**Description**: Just retry failed requests

**Pros**:
- Simple
- Works for transient failures

**Cons**:
- Amplifies load on failing service
- Doesn't help with persistent failures

**Why Rejected**: Can cause cascading failures

### Alternative 2: Bulkhead Only

**Description**: Isolate resources per service

**Pros**:
- Prevents resource exhaustion
- Service isolation

**Cons**:
- Doesn't provide fail-fast behavior
- Still attempts failing calls

**Why Rejected**: Complementary pattern, not replacement

### Alternative 3: External Service Mesh

**Description**: Use Istio/Envoy for circuit breaking

**Pros**:
- Infrastructure-level
- Language-agnostic

**Cons**:
- Operational complexity
- Overkill for single application

**Why Rejected**: Too heavy for current deployment model

## References

- [Nygard, M.T. (2018). Release It! - Circuit Breaker](https://pragprog.com/titles/mnee2/release-it-second-edition/)
- [Martin Fowler - Circuit Breaker](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Netflix Hystrix (archived)](https://github.com/Netflix/Hystrix)

## Notes

Implementation includes:
- Per-service circuit breakers
- Metrics export (Prometheus-compatible)
- Health check endpoint integration
- Configurable per API

