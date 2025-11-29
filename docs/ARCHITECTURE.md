# Multi-Agent Tour Guide System
## Architecture & Design Document

---

## 1. Problem Statement

### 1.1 The Ask

Build an **intelligent tour guide system** that:

1. Takes a **source** and **destination** from the user
2. Gets the **route** from Google Maps API with waypoints (addresses at each junction)
3. For each point in the route, **3 specialized agents** search for relevant content:
   - **Video Agent**: Finds YouTube videos about the location
   - **Music Agent**: Finds songs related to the location
   - **Text Agent**: Finds historical facts or interesting stories
4. A **Judge Agent** evaluates all 3 results and selects the **single best** content for that point
5. Output a **playlist**: "At point 1, play X; at point 2, play Y; etc."

### 1.2 Key Constraints

| Constraint | Description |
|------------|-------------|
| **Parallelism** | Agents must work in parallel (not sequentially) |
| **Synchronization** | Judge can only decide AFTER all 3 agents finish |
| **Streaming** | New points can arrive while previous ones are still processing |
| **Logging** | Full visibility into the process (logs, thread names, timing) |
| **Scalability** | Should handle multiple points being processed simultaneously |

### 1.3 Expected Output

```
Route: Tel Aviv → Jerusalem
Total Points: 4

Point 1: Tel Aviv
   → 🎬 VIDEO: "Tel Aviv: City That Never Sleeps"
   Reason: Best captures the vibrant atmosphere of the starting point

Point 2: Latrun  
   → 📖 TEXT: "The Silent Monks of Latrun"
   Reason: Unique story about the monastery - more memorable than generic video

Point 3: Ammunition Hill
   → 🎬 VIDEO: "Battle of Ammunition Hill Documentary"
   Reason: Historical significance demands visual content

Point 4: Old City Jerusalem
   → 🎵 MUSIC: "Jerusalem of Gold"
   Reason: Iconic arrival song - emotional impact
```

---

## 2. Architecture Options

### 2.1 Option A: Simple Sequential Processing

```
For each point:
    1. Run Video Agent → wait for result
    2. Run Music Agent → wait for result  
    3. Run Text Agent → wait for result
    4. Run Judge → get decision
    Move to next point
```

**Advantages:**
- ✅ Simple to implement
- ✅ Easy to debug
- ✅ No synchronization issues
- ✅ Predictable execution order

**Disadvantages:**
- ❌ Very slow (agents wait for each other)
- ❌ No parallelism within a point
- ❌ Cannot process multiple points simultaneously
- ❌ Does not meet assignment requirements

**Verdict:** ❌ Does not meet requirements

---

### 2.2 Option B: Parallel Agents per Point (Thread Pool)

```
For each point:
    ThreadPool.submit(VideoAgent)
    ThreadPool.submit(MusicAgent)
    ThreadPool.submit(TextAgent)
    Wait for all 3 to complete
    Run Judge
    Move to next point
```

**Advantages:**
- ✅ Agents work in parallel within each point
- ✅ Faster than sequential
- ✅ Relatively simple synchronization
- ✅ Clear completion point

**Disadvantages:**
- ❌ Still processes points one at a time
- ❌ No overlap between points
- ❌ Judge blocks next point processing

**Verdict:** ⚠️ Partial solution - good for simple cases

---

### 2.3 Option C: Queue-Based Synchronization (Recommended)

```
┌─────────────┐
│ Video Agent │──┐
└─────────────┘  │
                 │
┌─────────────┐  │    ┌─────────────────┐    ┌─────────────┐
│ Music Agent │──┼───▶│  RESULT QUEUE   │───▶│   JUDGE     │
└─────────────┘  │    │  (waits for 3)  │    │   AGENT     │
                 │    └─────────────────┘    └─────────────┘
┌─────────────┐  │
│ Text Agent  │──┘
└─────────────┘
```

**How it works:**
1. Each point gets its own **Result Queue**
2. 3 agents run in parallel, each **submits to queue** when done
3. Queue tracks: "received 1/3", "received 2/3", "received 3/3 - READY!"
4. When queue is ready, **Judge is notified**
5. Judge evaluates all 3 together

**Advantages:**
- ✅ True parallelism within each point
- ✅ Clean synchronization point
- ✅ Judge always sees ALL candidates together
- ✅ Easy to track progress (queue status)
- ✅ Can handle multiple points simultaneously
- ✅ Decoupled components (agents don't know about judge)

**Disadvantages:**
- ⚠️ More complex to implement
- ⚠️ Need to manage queue lifecycle
- ⚠️ Potential memory overhead for many queues

**Verdict:** ✅ **RECOMMENDED** - Meets all requirements

---

### 2.4 Option D: Streaming with Overlapping Points

```
Timer emits points: P1, P2, P3...
           │
           ▼
    ┌──────────────────────────────────────────────┐
    │              ORCHESTRATOR                     │
    │                                               │
    │   Point 1: [V][M][T] → Queue1 → Judge1       │
    │   Point 2: [V][M][T] → Queue2 → Judge2       │  (running in parallel!)
    │   Point 3: [V][M][T] → Queue3 → Judge3       │
    │                                               │
    └──────────────────────────────────────────────┘
           │
           ▼
      COLLECTOR (aggregates all decisions)
```

**How it works:**
1. Timer emits new points at intervals (e.g., every 5 seconds)
2. Each point immediately spawns its own agent group
3. Multiple points can be processing simultaneously
4. Results arrive out of order, Collector sorts them

**Advantages:**
- ✅ Maximum parallelism
- ✅ Simulates real-time travel
- ✅ Can handle fast point arrival
- ✅ Creates "racing" scenario for agent parallelism
- ✅ Full decoupling between points

**Disadvantages:**
- ⚠️ Most complex to implement
- ⚠️ Need careful thread management
- ⚠️ Results may arrive out of order
- ⚠️ Higher resource usage

**Verdict:** ✅ **ADVANCED** - For full marks / extra credit

---

## 3. Recommended Architecture

### 3.1 Chosen Approach: Option C + D Hybrid

Combine Queue-Based Synchronization (C) with Streaming capability (D):

```
┌─────────────────────────────────────────────────────────────────────┐
│                           USER INPUT                                 │
│                      (Source, Destination, Profile)                  │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        GOOGLE MAPS API                               │
│                     (Returns route with waypoints)                   │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      TIMER / SCHEDULER                               │
│                   (Emits points at intervals)                        │
│                   Setup: interval_seconds = 5                        │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATOR                                 │
│              (Manages ThreadPool, creates queues per point)          │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                     POINT PROCESSOR (per point)                 │ │
│  │                                                                 │ │
│  │   ┌─────────┐  ┌─────────┐  ┌─────────┐                        │ │
│  │   │  VIDEO  │  │  MUSIC  │  │  TEXT   │  (3 parallel threads)  │ │
│  │   │  AGENT  │  │  AGENT  │  │  AGENT  │                        │ │
│  │   └────┬────┘  └────┬────┘  └────┬────┘                        │ │
│  │        │            │            │                              │ │
│  │        └────────────┼────────────┘                              │ │
│  │                     ▼                                           │ │
│  │              ┌─────────────┐                                    │ │
│  │              │   QUEUE     │  (waits for 3/3)                   │ │
│  │              └──────┬──────┘                                    │ │
│  │                     ▼                                           │ │
│  │              ┌─────────────┐                                    │ │
│  │              │    JUDGE    │  (evaluates all together)          │ │
│  │              └──────┬──────┘                                    │ │
│  └─────────────────────┼──────────────────────────────────────────┘ │
│                        │                                             │
└────────────────────────┼─────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          COLLECTOR                                   │
│               (Aggregates decisions, maintains order)                │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        FINAL OUTPUT                                  │
│                   (Ordered playlist for route)                       │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Component Responsibilities

| Component | Responsibility |
|-----------|---------------|
| **User Input** | Get source, destination, user profile (audience, preferences) |
| **Google Maps API** | Fetch route, extract waypoints with addresses |
| **Timer/Scheduler** | Emit points at configurable intervals |
| **Orchestrator** | Manage thread pool, create Point Processors |
| **Point Processor** | Process single point with queue synchronization |
| **Video Agent** | Search YouTube for relevant videos |
| **Music Agent** | Search Spotify/YouTube for relevant songs |
| **Text Agent** | Search web for historical facts/stories |
| **Queue** | Collect agent results, notify when ready |
| **Judge Agent** | Evaluate all candidates, select best |
| **Collector** | Aggregate decisions, maintain route order |

---

## 4. Data Flow

### 4.1 Main Flow

```
1. User provides: "Tel Aviv" → "Jerusalem"
2. Google Maps returns: [Point1, Point2, Point3, Point4]
3. Timer emits Point1
4. Orchestrator creates PointProcessor for Point1
5. PointProcessor:
   a. Creates Queue for Point1
   b. Spawns VideoAgent thread → searches YouTube → submits to Queue
   c. Spawns MusicAgent thread → searches Spotify → submits to Queue
   d. Spawns TextAgent thread → searches web → submits to Queue
   e. Queue receives 3/3 → notifies Judge
   f. Judge evaluates all 3 → selects winner → returns decision
6. Decision sent to Collector
7. Timer emits Point2 (may overlap with Point1 processing)
8. ... repeat ...
9. Collector outputs final playlist
```

### 4.2 Queue Synchronization Detail

```
Time →

VideoAgent:  ████████░░░░░░ (slower - API call)
                      │
                      ▼ submit(video_result)
                      │
MusicAgent:  ████░░░░░░░░░░ (faster)
                 │
                 ▼ submit(music_result)
                 │
TextAgent:   ██████░░░░░░░░ (medium)
                   │
                   ▼ submit(text_result)
                   │
Queue:       [1/3]──[2/3]──[3/3 READY!]
                            │
                            ▼
Judge:       ░░░░░░░░░░░░░░████ (starts after queue ready)
```

---

## 5. Threading Model

### 5.1 Thread Hierarchy

```
Main Thread
    │
    ├── Timer Thread (if streaming mode)
    │
    └── Orchestrator ThreadPool
            │
            ├── PointProcessor-1
            │       ├── VideoAgent-P1
            │       ├── MusicAgent-P1
            │       └── TextAgent-P1
            │
            ├── PointProcessor-2
            │       ├── VideoAgent-P2
            │       ├── MusicAgent-P2
            │       └── TextAgent-P2
            │
            └── ... (more points)
```

### 5.2 Thread Pool Configuration

```python
# Maximum concurrent threads
MAX_ORCHESTRATOR_THREADS = 3  # Process 3 points simultaneously
MAX_AGENTS_PER_POINT = 3      # Video, Music, Text

# Total possible threads = 3 × 3 = 9 agent threads + 3 judge threads = 12
```

---

## 6. Agent Design

### 6.1 Agent Skills

Each agent needs **skills** - criteria for finding and evaluating content:

**Video Agent Skills:**
- Relevance to specific location
- Educational/entertainment value
- Video quality and production
- Duration appropriateness (2-15 min ideal)
- View count as quality signal

**Music Agent Skills:**
- Lyrical connection to location
- Artist from the region
- Cultural/historical significance
- Mood fit for travel
- Duration appropriateness

**Text Agent Skills:**
- Historical accuracy
- Surprising/interesting facts
- Brevity (2-3 sentences)
- Engagement potential
- Memorability

**Judge Agent Skills:**
- Comparative analysis across types
- Location-specific relevance
- Audience appropriateness
- Uniqueness/irreplaceability

### 6.2 Agent Interface

```python
class BaseAgent:
    def execute(self, point: RoutePoint) -> ContentResult:
        """
        Search for content relevant to this point.
        Returns a ContentResult with:
        - title: str
        - description: str
        - url: str
        - relevance_score: float (0-10)
        - source: str (YouTube, Spotify, Web)
        """
        pass
```

---

## 7. Advantages & Disadvantages Summary

### 7.1 Chosen Architecture (Queue-Based + Streaming)

| Aspect | Advantage | Disadvantage |
|--------|-----------|--------------|
| **Parallelism** | ✅ Full parallelism at all levels | ⚠️ Higher resource usage |
| **Synchronization** | ✅ Clean queue-based sync | ⚠️ Queue management overhead |
| **Scalability** | ✅ Can handle many points | ⚠️ Need to limit concurrency |
| **Debugging** | ✅ Clear component boundaries | ⚠️ More complex traces |
| **Flexibility** | ✅ Can run in different modes | ⚠️ More configuration |
| **Real-time** | ✅ Supports streaming | ⚠️ Results may be out of order |

### 7.2 Why This is the Best Approach

1. **Meets all requirements**: Parallel agents, queue synchronization, streaming
2. **Clean separation**: Each component has clear responsibility
3. **Testable**: Can test each component independently
4. **Flexible**: Can run in simple or advanced mode
5. **Observable**: Full logging at every step
6. **Well-designed**: Follows best practices for multi-agent systems

---

## 8. Implementation Plan

### Phase 1: Core Components (MVP)
1. ✅ Data models (RoutePoint, ContentResult, JudgeDecision)
2. ✅ Google Maps API client (with mock for testing)
3. ✅ Base Agent class with LLM integration
4. ✅ Configuration system

### Phase 2: Agents
5. ✅ Video Agent with YouTube search
6. ✅ Music Agent with Spotify/YouTube search
7. ✅ Text Agent with web search
8. ✅ Judge Agent with evaluation logic

### Phase 3: Synchronization
9. ✅ Queue mechanism (AgentResultQueue)
10. ✅ Point Processor with queue integration
11. ✅ Orchestrator with thread pool

### Phase 4: Integration
12. ✅ Timer/Scheduler for streaming
13. ✅ Collector for result aggregation
14. ✅ Main application with all modes
15. ✅ YAML configuration for agents

### Phase 5: Polish
16. ⬜ Comprehensive testing
17. ⬜ Performance optimization
18. ⬜ Documentation

---

## 9. Running Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `--mode sequential` | Process points one by one | Debugging, understanding flow |
| `--mode queue` | Queue-based sync per point | **Recommended for assignment** |
| `--mode instant` | All points parallel, no timing | Quick results |
| `--mode streaming` | Timer-based, simulates travel | Full demo |

---

## 10. Success Criteria

The system is successful if it:

1. ✅ Accepts source and destination input
2. ✅ Retrieves route with multiple waypoints
3. ✅ Processes each point with 3 parallel agents
4. ✅ Uses queue to synchronize before judge
5. ✅ Judge evaluates ALL candidates together
6. ✅ Outputs ordered playlist with reasoning
7. ✅ Shows proper logging with thread names
8. ✅ Demonstrates multi-threading/multi-processing

---

*Document Version: 1.0*
*Last Updated: November 2024*

