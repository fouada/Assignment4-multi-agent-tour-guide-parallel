# ADR-001: Parallel Agent Architecture

## Status

Accepted

## Date

2025-11

## Context

The Multi-Agent Tour Guide System needs to fetch content from multiple sources (Video, Music, Text) for each route point. The key challenge is balancing:

1. **Latency**: Users expect responsive results
2. **Quality**: More agents = better content selection
3. **Reliability**: External APIs may fail or be slow
4. **Resource Efficiency**: Optimal use of system resources

Sequential execution would result in cumulative latency:
```
T_sequential = T_video + T_music + T_text ≈ 3-9 seconds per point
```

## Decision

We will use **parallel agent execution** with `ThreadPoolExecutor` for concurrent API calls.

### Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Orchestrator                      │
│                ThreadPoolExecutor(12)                │
├─────────────────────────────────────────────────────┤
│                                                      │
│   Point 1        Point 2        Point 3             │
│   ┌─────┐        ┌─────┐        ┌─────┐            │
│   │V│M│T│        │V│M│T│        │V│M│T│            │
│   └─────┘        └─────┘        └─────┘            │
│      ↓              ↓              ↓                │
│   Queue          Queue          Queue               │
│      ↓              ↓              ↓                │
│   Judge          Judge          Judge               │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### Implementation

```python
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = {
        executor.submit(video_agent.search, point): "video",
        executor.submit(music_agent.search, point): "music",
        executor.submit(text_agent.search, point): "text",
    }
    for future in as_completed(futures, timeout=30):
        result = future.result()
```

## Consequences

### Positive

- **Reduced Latency**: `T_parallel = max(T_video, T_music, T_text) ≈ 1-3 seconds`
- **Better UX**: 3x faster response time
- **Scalability**: Can process multiple points concurrently
- **Fault Isolation**: One slow/failed agent doesn't block others

### Negative

- **Complexity**: Thread synchronization required
- **Resource Usage**: More concurrent connections
- **Debugging**: Harder to trace parallel execution
- **Rate Limits**: May hit API rate limits faster

### Neutral

- Memory usage roughly constant (I/O bound, not CPU bound)
- Requires careful timeout management

## Alternatives Considered

### Alternative 1: Sequential Execution

**Description**: Execute agents one after another

**Pros**:
- Simple implementation
- Easy debugging
- Predictable resource usage

**Cons**:
- 3x slower latency
- Poor user experience

**Why Rejected**: Unacceptable latency for interactive use

### Alternative 2: Async/Await (asyncio)

**Description**: Use Python's asyncio for concurrency

**Pros**:
- Lower overhead than threads
- Better for I/O-bound tasks
- Modern Python pattern

**Cons**:
- Requires async-compatible libraries
- More complex error handling
- Less familiar to team

**Why Rejected**: Many LLM client libraries have better thread support than async support

### Alternative 3: Multiprocessing

**Description**: Use separate processes for each agent

**Pros**:
- True parallelism (bypasses GIL)
- Process isolation

**Cons**:
- High overhead for I/O-bound tasks
- Complex inter-process communication
- Memory overhead

**Why Rejected**: Overkill for I/O-bound API calls

## References

- [Python ThreadPoolExecutor Documentation](https://docs.python.org/3/library/concurrent.futures.html)
- [Nygard, M.T. (2018). Release It! - Stability Patterns](https://pragprog.com/titles/mnee2/release-it-second-edition/)

## Notes

Performance measurements show:
- Sequential: ~4.5s average per point
- Parallel: ~1.5s average per point
- Improvement: ~3x faster

