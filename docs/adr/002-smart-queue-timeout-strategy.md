# ADR-002: Smart Queue Tiered Timeout Strategy

## Status

Accepted

## Date

2025-11

## Context

With parallel agent execution (ADR-001), we need a synchronization mechanism to:

1. **Collect Results**: Gather responses from multiple agents
2. **Handle Failures**: Gracefully degrade when agents fail
3. **Prevent Blocking**: Never wait indefinitely
4. **Optimize Tradeoffs**: Balance latency vs. quality

The challenge is the **Quality-Latency Tradeoff**:
- Waiting longer → More results → Better selection
- Waiting less → Faster response → Possibly missing good content

## Decision

Implement a **Smart Queue with Tiered Timeout Strategy** providing graceful degradation.

### Timeout Tiers

| Tier | Timeout | Min Results | Status | Use Case |
|------|---------|-------------|--------|----------|
| Ideal | - | 3/3 | COMPLETE | All agents respond |
| Soft | 15s | 2/3 | SOFT_DEGRADED | Minor degradation |
| Hard | 30s | 1/3 | HARD_DEGRADED | Major degradation |
| Fail | 30s | 0/3 | FAILED | Total failure |

### State Machine

```
                    ┌──────────────────────────────────────┐
                    │              WAITING                  │
                    │         (collecting results)         │
                    └──────────────────────────────────────┘
                                      │
            ┌─────────────────────────┼─────────────────────────┐
            │                         │                         │
            ▼                         ▼                         ▼
    ┌──────────────┐         ┌──────────────┐         ┌──────────────┐
    │   COMPLETE   │         │SOFT_DEGRADED │         │HARD_DEGRADED │
    │    (3/3)     │         │    (2/3)     │         │    (1/3)     │
    └──────────────┘         └──────────────┘         └──────────────┘
                                                              │
                                                              ▼
                                                      ┌──────────────┐
                                                      │    FAILED    │
                                                      │    (0/3)     │
                                                      └──────────────┘
```

### Mathematical Justification

Given agent response times T_i ~ LogNormal(μ, σ²):

- P(all 3 respond by 15s) ≈ 0.85
- P(at least 2 respond by 15s) ≈ 0.97
- P(at least 1 responds by 30s) ≈ 0.999

The tiered approach provides:
- **85% optimal** (all 3)
- **12% acceptable degradation** (2/3)
- **2.9% significant degradation** (1/3)
- **0.1% failure** (0/3)

## Consequences

### Positive

- **Bounded Latency**: Maximum 30s wait time
- **Graceful Degradation**: System remains functional under stress
- **Predictable Behavior**: Clear state machine
- **Observable**: Metrics for each state transition

### Negative

- **Complexity**: More states to manage
- **Parameter Tuning**: Timeouts need calibration
- **Potential Quality Loss**: Soft/hard degradation may miss best content

### Neutral

- Requires monitoring to validate timeout choices
- May need adjustment per deployment environment

## Alternatives Considered

### Alternative 1: Fixed Timeout

**Description**: Single timeout for all agents

**Pros**:
- Simple implementation
- Predictable

**Cons**:
- Either too aggressive (miss results) or too slow (poor UX)

**Why Rejected**: Can't optimize for both latency and quality

### Alternative 2: First-N Strategy

**Description**: Return as soon as N agents respond

**Pros**:
- Fast for common case
- Simple

**Cons**:
- May consistently miss slower but higher-quality agents

**Why Rejected**: Systematically biases against certain content types

### Alternative 3: Adaptive Timeout

**Description**: Dynamically adjust timeouts based on historical data

**Pros**:
- Self-tuning
- Optimal for current conditions

**Cons**:
- Complex implementation
- Cold start problem
- Potential instability

**Why Rejected**: Added complexity not justified for MVP

## References

- [Nygard, M.T. (2018). Release It! - Timeout Pattern](https://pragprog.com/titles/mnee2/release-it-second-edition/)
- [Amazon Builder's Library - Timeouts, retries, and backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)

## Notes

Sensitivity analysis (see `notebooks/01_sensitivity_analysis.ipynb`) shows:
- `soft_timeout` is the most sensitive parameter for latency
- Optimal range: 12-18s for balanced performance
- `hard_timeout` primarily affects failure rate

