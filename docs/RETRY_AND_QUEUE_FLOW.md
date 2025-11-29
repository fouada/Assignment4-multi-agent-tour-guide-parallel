# 🔄 Retry Mechanism & Queue Flow

## Complete System Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ORCHESTRATOR                                       │
│                                                                              │
│   For each Route Point, spawn 3 agents in parallel:                         │
│                                                                              │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                  │
│   │Video Agent  │     │Music Agent  │     │Text Agent   │                  │
│   │             │     │             │     │             │                  │
│   │ MAX_RETRIES │     │ MAX_RETRIES │     │ MAX_RETRIES │                  │
│   │    = 3      │     │    = 3      │     │    = 3      │                  │
│   └──────┬──────┘     └──────┬──────┘     └──────┬──────┘                  │
│          │                   │                   │                          │
└──────────┼───────────────────┼───────────────────┼──────────────────────────┘
           │                   │                   │
           ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      AGENT RETRY LOOP (Each Agent)                           │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ Attempt 1 (0s)                                                       │   │
│   │   └─► API Call → Success? ──YES──► Submit to Queue ✅                │   │
│   │                     │                                                │   │
│   │                    NO (Exception)                                    │   │
│   │                     │                                                │   │
│   │                     ▼                                                │   │
│   │   ┌─────────────────────────────────────────────────────┐           │   │
│   │   │  WAIT: 1 second  (exponential backoff: 2^0 = 1s)    │           │   │
│   │   └─────────────────────────────────────────────────────┘           │   │
│   │                     │                                                │   │
│   │                     ▼                                                │   │
│   │ Attempt 2 (~1s)                                                      │   │
│   │   └─► API Call → Success? ──YES──► Submit to Queue ✅                │   │
│   │                     │                                                │   │
│   │                    NO                                                │   │
│   │                     │                                                │   │
│   │                     ▼                                                │   │
│   │   ┌─────────────────────────────────────────────────────┐           │   │
│   │   │  WAIT: 2 seconds  (exponential backoff: 2^1 = 2s)   │           │   │
│   │   └─────────────────────────────────────────────────────┘           │   │
│   │                     │                                                │   │
│   │                     ▼                                                │   │
│   │ Attempt 3 (~3s)                                                      │   │
│   │   └─► API Call → Success? ──YES──► Submit to Queue ✅                │   │
│   │                     │                                                │   │
│   │                    NO                                                │   │
│   │                     │                                                │   │
│   │                     ▼                                                │   │
│   │   ┌─────────────────────────────────────────────────────┐           │   │
│   │   │  WAIT: 4 seconds  (exponential backoff: 2^2 = 4s)   │           │   │
│   │   └─────────────────────────────────────────────────────┘           │   │
│   │                     │                                                │   │
│   │                     ▼                                                │   │
│   │ Attempt 4 (~7s) - FINAL                                              │   │
│   │   └─► API Call → Success? ──YES──► Submit to Queue ✅                │   │
│   │                     │                                                │   │
│   │                    NO                                                │   │
│   │                     │                                                │   │
│   │                     ▼                                                │   │
│   │   ┌─────────────────────────────────────────────────────┐           │   │
│   │   │  ALL RETRIES EXHAUSTED → Submit FAILURE to Queue ❌ │           │   │
│   │   └─────────────────────────────────────────────────────┘           │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ (Success ✅ or Failure ❌)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SMART QUEUE                                        │
│                                                                              │
│   Queue stores results/failures and tracks timing:                          │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  Timeline                                                            │   │
│   │                                                                      │   │
│   │  0s            5s           10s           15s           30s         │   │
│   │  │─────────────│─────────────│─────────────│─────────────│          │   │
│   │  │             │             │             │             │          │   │
│   │  │ Video ✅    │ Music ✅    │             │ SOFT        │ HARD     │   │
│   │  │ (2s)        │ (5s)        │ Text still  │ TIMEOUT     │ TIMEOUT  │   │
│   │  │             │             │ retrying... │             │          │   │
│   │  │             │             │             │             │          │   │
│   │  │ _results:   │ _results:   │             │ Proceed     │          │   │
│   │  │ {video}     │ {video,     │             │ with 2/3    │          │   │
│   │  │             │  music}     │             │             │          │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   Decision Logic:                                                            │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                      │   │
│   │  IF all 3 agents submitted (success or failure):                    │   │
│   │      → Return immediately (COMPLETE or DEGRADED)                    │   │
│   │                                                                      │   │
│   │  ELSE IF elapsed >= 15s AND 2+ successes:                           │   │
│   │      → SOFT_DEGRADED - proceed with 2/3                             │   │
│   │                                                                      │   │
│   │  ELSE IF elapsed >= 30s AND 1+ successes:                           │   │
│   │      → HARD_DEGRADED - proceed with 1/3                             │   │
│   │                                                                      │   │
│   │  ELSE IF elapsed >= 30s AND 0 successes:                            │   │
│   │      → FAILED - raise error                                         │   │
│   │                                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Retry Configuration (base_agent.py)

```python
class BaseAgent:
    # Retry configuration
    MAX_RETRIES = 3              # Total attempts = 4 (1 initial + 3 retries)
    BASE_DELAY_SECONDS = 1.0    # First retry waits 1 second
    EXPONENTIAL_BASE = 2.0      # Each retry doubles the wait
    MAX_DELAY_SECONDS = 10.0    # Cap delay at 10 seconds
```

---

## Timing Analysis

### Retry Wait Times

| Attempt | Formula | Wait Time | Cumulative |
|---------|---------|-----------|------------|
| 1 | Initial | 0s | 0s |
| 2 | 1 × 2⁰ | 1s | 1s |
| 3 | 1 × 2¹ | 2s | 3s |
| 4 | 1 × 2² | 4s | 7s |

**Worst case per agent: ~8-9 seconds** (with jitter)

### Queue Timeouts

| Timeout | Time | Condition | Action |
|---------|------|-----------|--------|
| **None** | 0-15s | All 3 responded | Proceed immediately |
| **Soft** | 15s | 2/3 succeeded | Proceed with 2 |
| **Hard** | 30s | 1/3 succeeded | Proceed with 1 |
| **Failed** | 30s | 0/3 succeeded | Raise error |

---

## Complete Timeline Examples

### Scenario 1: All Agents Succeed Quickly

```
0s    │ Video: Attempt 1 → ✅ Success
      │ Music: Attempt 1 → ✅ Success
      │ Text:  Attempt 1 → ✅ Success
      │
2s    │ Queue: All 3 ready → COMPLETE
      │ Judge receives: [Video, Music, Text]
```

### Scenario 2: One Agent Needs Retries

```
0s    │ Video: Attempt 1 → ❌ Fail
      │ Music: Attempt 1 → ✅ Success
      │ Text:  Attempt 1 → ✅ Success
      │
1s    │ Video: Waiting... (1s backoff)
      │
2s    │ Video: Attempt 2 → ❌ Fail
      │
4s    │ Video: Waiting... (2s backoff)
      │
5s    │ Video: Attempt 3 → ✅ Success
      │
5s    │ Queue: All 3 ready → COMPLETE
      │ Judge receives: [Video, Music, Text]
```

### Scenario 3: One Agent Fails All Retries, Soft Timeout

```
0s    │ Video: Attempt 1 → ❌ Fail
      │ Music: Attempt 1 → ✅ Success (1s)
      │ Text:  Attempt 1 → ✅ Success (2s)
      │
1s    │ Video: Waiting... (1s backoff)
2s    │ Video: Attempt 2 → ❌ Fail
      │ Video: Waiting... (2s backoff)
4s    │ Video: Attempt 3 → ❌ Fail
      │ Video: Waiting... (4s backoff)
8s    │ Video: Attempt 4 → ❌ Fail (FINAL)
      │ Video: Submit FAILURE to queue
      │
8s    │ Queue: 3 responses (2 success, 1 fail)
      │        → SOFT_DEGRADED
      │ Judge receives: [Music, Text]
```

### Scenario 4: Soft Timeout with Slow Agent

```
0s    │ Video: Attempt 1 → ✅ Success (1s)
      │ Music: Attempt 1 → ✅ Success (2s)
      │ Text:  Attempt 1 → ❌ Fail (API timeout)
      │
3s    │ Text: Waiting... (1s backoff)
4s    │ Text: Attempt 2 → ❌ Fail (network error)
      │ Text: Waiting... (2s backoff)
6s    │ Text: Attempt 3 → ❌ Fail (rate limit)
      │ Text: Waiting... (4s backoff)
10s   │ Text: Attempt 4 → (still running...)
      │
15s   │ ⏱️ SOFT TIMEOUT reached
      │ Queue: 2 successes available
      │        → SOFT_DEGRADED (proceed with 2/3)
      │ Judge receives: [Video, Music]
      │
      │ (Text agent still running in background,
      │  but result ignored)
```

---

## Code Implementation

### In base_agent.py

```python
def execute(self, point: RoutePoint) -> Optional[ContentResult]:
    """Execute with retry logic."""
    
    for attempt in range(self.MAX_RETRIES + 1):
        try:
            result = self._search_content(point)
            if result:
                return result
            raise ValueError("No content found")
            
        except Exception as e:
            if attempt < self.MAX_RETRIES:
                # Calculate exponential backoff
                delay = self.BASE_DELAY_SECONDS * (self.EXPONENTIAL_BASE ** attempt)
                delay = min(delay, self.MAX_DELAY_SECONDS)
                
                # Add jitter (0-25%)
                delay += delay * random.uniform(0, 0.25)
                
                logger.warning(f"Attempt {attempt+1} failed. Waiting {delay:.2f}s...")
                time.sleep(delay)
            else:
                logger.error(f"All {self.MAX_RETRIES+1} attempts failed")
    
    return None


def execute_with_queue(self, point: RoutePoint, queue) -> None:
    """Execute and submit to queue."""
    result = self.execute(point)
    
    if result:
        queue.submit_success(self.agent_type, result)
    else:
        queue.submit_failure(self.agent_type, "All retries failed")
```

### In smart_queue.py

```python
def wait_for_results(self):
    """Wait with smart timeout strategy."""
    
    while True:
        elapsed = time.time() - self._start_time
        result_count = len(self._results)
        
        # All agents responded
        if total_responses >= 3:
            return results
        
        # Soft timeout: 2/3 ready
        if elapsed >= 15.0 and result_count >= 2:
            return results  # SOFT_DEGRADED
        
        # Hard timeout: 1/3 ready
        if elapsed >= 30.0 and result_count >= 1:
            return results  # HARD_DEGRADED
        
        # Wait for more results
        self._condition.wait(timeout=remaining_time)
```

---

## Summary

| Component | Responsibility |
|-----------|----------------|
| **Agent Retry** | Handle transient API failures (3 retries, exponential backoff) |
| **Smart Queue** | Synchronize agents, timeout management, graceful degradation |
| **Orchestrator** | Spawn agents in parallel, pass queue reference |
| **Judge** | Evaluate whatever results are available |

The system ensures:
1. ✅ **Resilience**: Agents retry on failure
2. ✅ **Responsiveness**: Never waits forever (30s max)
3. ✅ **Quality**: Prefers more results when available
4. ✅ **Graceful Degradation**: Always produces some output

