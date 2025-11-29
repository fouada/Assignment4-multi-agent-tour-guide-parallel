# Design Decisions

## Key Decision Points and Rationale

---

## 1. Why Queue-Based Synchronization?

### The Problem
We have 3 agents (Video, Music, Text) that run in parallel. The Judge needs to evaluate ALL 3 results together to make a fair comparison.

### Options Considered

| Option | Description | Verdict |
|--------|-------------|---------|
| **A. Sequential** | Wait for each agent one by one | ❌ Too slow, no parallelism |
| **B. Callbacks** | Each agent calls Judge when done | ❌ Judge sees results one at a time |
| **C. Shared Memory** | All agents write to shared dict | ⚠️ Race conditions, complex locking |
| **D. Queue** | Agents submit to queue, Judge waits | ✅ Clean, standard pattern |

### Decision: Queue

**Rationale:**
1. The Judge must see ALL candidates together for fair comparison
2. Queue provides clear "ready" signal when all 3 have submitted
3. Standard Python `queue.Queue` is thread-safe
4. Easy to track progress: "1/3", "2/3", "3/3 - READY!"

---

## 2. Why Separate Judge from Content Agents?

### The Problem
Could we have content agents self-evaluate and return only the best?

### Decision: Separate Judge Agent

**Rationale:**
1. **Fairness**: Judge sees all options simultaneously
2. **Separation of Concerns**: Search ≠ Evaluation
3. **Different Skills**: Finding content vs. comparing content
4. **Flexibility**: Can change judge logic without changing agents
5. **Transparency**: Clear decision trail with reasoning

---

## 3. Why YAML Configuration Files?

### Options Considered

| Format | Pros | Cons |
|--------|------|------|
| **Python Code** | Full flexibility | Hard to modify without coding |
| **JSON** | Universal, fast | No comments, verbose |
| **YAML** | Readable, comments | Slightly slower to parse |
| **TOML** | Modern, typed | Less common |

### Decision: YAML

**Rationale:**
1. **Readability**: Easy for non-programmers to modify
2. **Comments**: Can explain each configuration option
3. **Industry Adoption**: Widely used across cloud-native applications
4. **Industry Standard**: Used by Kubernetes, GitHub Actions, etc.

**Example benefit - can add comments:**
```yaml
# This agent finds YouTube videos about locations
agent:
  name: "Video Content Specialist"
  
skills:
  - name: "YouTube Search"
    # Criteria used to evaluate video quality
    criteria:
      - "Relevance to location"
      - "Duration (2-15 min ideal)"  # Not too long for travel
```

---

## 4. Why ThreadPoolExecutor over Raw Threads?

### Options Considered

| Option | Pros | Cons |
|--------|------|------|
| **Raw `threading.Thread`** | Full control | Manual management |
| **`ThreadPoolExecutor`** | Managed pool, futures | Less control |
| **`multiprocessing.Pool`** | True parallelism | GIL bypass overhead |
| **`asyncio`** | Efficient for I/O | Different paradigm |

### Decision: ThreadPoolExecutor

**Rationale:**
1. **Managed lifecycle**: Pool handles thread creation/destruction
2. **Futures**: Easy to wait for completion with `as_completed()`
3. **Appropriate for I/O**: Our agents do HTTP requests (I/O-bound)
4. **Meets requirements**: Shows multi-threading understanding
5. **Simpler than multiprocessing**: No serialization issues

**Note**: For CPU-bound work, would use `ProcessPoolExecutor`.

---

## 5. Why Mock Clients for Testing?

### The Problem
Real API calls are:
- Slow (network latency)
- Rate-limited
- Cost money (API quotas)
- Non-deterministic (results change)

### Decision: Mock + Real Clients

**Implementation:**
```python
def get_maps_client(use_mock=False):
    if use_mock or not settings.google_maps_api_key:
        return MockGoogleMapsClient()  # Returns sample data
    return GoogleMapsClient()          # Real API calls
```

**Rationale:**
1. **Fast iteration**: Mock tests run instantly
2. **No API costs**: Demo mode works without keys
3. **Deterministic**: Same mock data every time
4. **Graceful fallback**: Works even without API keys

---

## 6. Why User Profile?

### The Problem
Same content isn't appropriate for all travelers.

### Examples
- Family with 5-year-olds → needs family-friendly content
- History buffs → prefer detailed historical facts
- Quick trip → prefer shorter content

### Decision: User Profile System

**Implementation:**
```python
class UserProfile:
    audience_type: AudienceType  # adults, family_with_kids, etc.
    min_age: int                 # youngest in group
    content_preference: ContentPreference  # educational, entertainment
    language: LanguagePreference
```

**Rationale:**
1. **Personalization**: Content matches audience
2. **Safety**: Filter inappropriate content for kids
3. **Relevance**: Match interests (history, nature, etc.)
4. **Best Practice**: Enables content filtering and personalization

---

## 7. Why Timer/Scheduler?

### The Problem
In real life, you don't process all points instantly - you arrive at each one over time.

### Decision: Configurable Timer

**Modes:**
1. **Instant**: Process all points immediately (for testing)
2. **Timed**: Emit points every N seconds (simulates travel)
3. **Manual**: User triggers each point (for debugging)

**Rationale:**
1. **Realism**: Simulates actual travel experience
2. **Stress testing**: Creates "racing" scenario
3. **Flexibility**: Can adjust timing for demos
4. **Parallelism**: Creates overlapping point processing for efficient execution

---

## 8. Why Collector Component?

### The Problem
Results from Judge may arrive out of order when processing multiple points in parallel.

### Example
- Point 1 takes 10 seconds to process
- Point 2 takes 3 seconds to process
- Point 2 result arrives before Point 1

### Decision: Collector with Ordering

**Implementation:**
```python
class Collector:
    def add_decision(self, decision):
        self.decisions[decision.point_id] = decision
    
    def get_ordered_decisions(self):
        # Return in route order, not arrival order
        return [self.decisions[p.id] for p in self.route.points]
```

**Rationale:**
1. **Ordering**: Final playlist is in route order
2. **Aggregation**: Single place to collect all results
3. **Progress tracking**: Know how many points completed
4. **Statistics**: Calculate timing, scores, etc.

---

## 9. Why Skills-Based Agent Design?

### The Problem
How does an agent know what makes content "good"?

### Decision: Explicit Skills with Criteria

**Implementation:**
```yaml
# video_agent.yaml
skills:
  - name: "YouTube Search"
    criteria:
      - "Relevance to specific location"
      - "Educational or entertainment value"
      - "Duration appropriateness (2-15 min)"
      - "View count as quality signal"
```

**Rationale:**
1. **Explicit reasoning**: Clear why content is chosen
2. **Tuneable**: Can adjust criteria without code changes
3. **Documented**: Skills serve as documentation
4. **LLM guidance**: Criteria fed into prompts

---

## 10. Summary of Key Decisions

| Decision | Choice | Main Reason |
|----------|--------|-------------|
| Synchronization | Queue | Fair comparison, clean "ready" signal |
| Evaluation | Separate Judge | Separation of concerns |
| Configuration | YAML | Readable, commentable |
| Threading | ThreadPoolExecutor | Managed, I/O appropriate |
| Testing | Mock clients | Fast, deterministic, no API costs |
| Personalization | User Profile | Content appropriateness |
| Timing | Configurable Timer | Simulate real travel |
| Aggregation | Collector | Ordering, statistics |
| Agent Design | Skills-based | Explicit, tuneable criteria |

---

*These decisions reflect software engineering best practices and proven design patterns.*

