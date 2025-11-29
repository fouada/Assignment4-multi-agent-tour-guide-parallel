# 🎓 MIT-Level Project Specification
## Multi-Agent Tour Guide System with Parallel Processing

**Version:** 2.0.0  
**Date:** November 2025  
**License:** MIT  

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture](#2-system-architecture)
3. [Design Decisions & Rationale](#3-design-decisions--rationale)
4. [Component Specifications](#4-component-specifications)
5. [Prompts for Development](#5-prompts-for-development)
6. [Quality Attributes](#6-quality-attributes)
7. [Implementation Roadmap](#7-implementation-roadmap)
8. [Testing Strategy](#8-testing-strategy)
9. [Future Extensions](#9-future-extensions)

---

## 1. Executive Summary

### 1.1 Problem Statement

Travelers on road trips lack contextual, personalized content about locations they pass. Current solutions are either:
- **Static** (pre-recorded audio guides)
- **Generic** (same content for everyone)
- **Single-modal** (only text OR only audio)

### 1.2 Solution

A **multi-agent AI system** that:
1. Takes a route (source → destination)
2. Identifies points of interest along the route
3. Deploys **parallel AI agents** to find relevant content (video, music, text)
4. Uses a **Judge agent** to select the best content based on **user profile**
5. Delivers a personalized, multi-modal tour guide experience

### 1.3 Key Innovations

| Innovation | Description |
|------------|-------------|
| **Parallel Processing** | 3 agents work simultaneously per point |
| **Smart Queue** | Wait for all, gracefully degrade to 2/3 or 1/3 |
| **Profile-Based Selection** | Content matches user demographics |
| **Plugin Architecture** | Add new agents without code changes |
| **Graceful Degradation** | Never fails completely |

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Input: Source, Destination, User Profile                           │   │
│  │  Output: Personalized Tour Guide Playlist                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ROUTE PLANNER                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Google Maps API → Extract route points with coordinates            │   │
│  │  Cache: Check if route exists in cache                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ORCHESTRATOR                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  ThreadPoolExecutor → Manage parallel agent execution               │   │
│  │  For each point: spawn Video, Music, Text agents                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
              ▼                      ▼                      ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│    VIDEO AGENT      │  │    MUSIC AGENT      │  │    TEXT AGENT       │
│  ┌───────────────┐  │  │  ┌───────────────┐  │  │  ┌───────────────┐  │
│  │ YouTube API   │  │  │  │ Spotify API   │  │  │  │ Wikipedia     │  │
│  │ Retry: 3x     │  │  │  │ Retry: 3x     │  │  │  │ Retry: 3x     │  │
│  │ Backoff: exp  │  │  │  │ Backoff: exp  │  │  │  │ Backoff: exp  │  │
│  └───────────────┘  │  │  └───────────────┘  │  │  └───────────────┘  │
└──────────┬──────────┘  └──────────┬──────────┘  └──────────┬──────────┘
           │                        │                        │
           └────────────────────────┼────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              SMART QUEUE                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Timeline: [0s]────────[15s soft]────────[30s hard]                 │   │
│  │  Wait for 3 → Accept 2 after soft timeout → Accept 1 after hard    │   │
│  │  Track: success/failure per agent for metrics                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              JUDGE AGENT                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Input: N candidates (1-3) + User Profile                           │   │
│  │  Process: Score each against profile preferences                    │   │
│  │  Output: Best content with reasoning                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              COLLECTOR                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Aggregate results for all points                                   │   │
│  │  Generate final playlist                                            │   │
│  │  Store to database for history                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow Diagram

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  User    │────▶│  Route   │────▶│ Orchestr │────▶│  Smart   │────▶│  Judge   │
│  Input   │     │ Planner  │     │   ator   │     │  Queue   │     │  Agent   │
└──────────┘     └──────────┘     └──────────┘     └──────────┘     └──────────┘
     │                │                │                │                │
     │                │                │                │                │
     ▼                ▼                ▼                ▼                ▼
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ Profile  │     │  Route   │     │ Agent    │     │ Content  │     │ Selected │
│   JSON   │     │  Points  │     │ Results  │     │ Results  │     │ Content  │
└──────────┘     └──────────┘     └──────────┘     └──────────┘     └──────────┘

Data Types:
- Profile: UserProfile (age, gender, interests, accessibility, etc.)
- Route Points: List[RoutePoint] (coordinates, address, distance)
- Agent Results: ContentResult (type, title, url, score)
- Selected Content: JudgeDecision (winner, reasoning, scores)
```

---

## 3. Design Decisions & Rationale

### 3.1 Why Parallel Agents?

| Approach | Time for 4 Points | Quality |
|----------|-------------------|---------|
| **Sequential** | 4 × 3 × 5s = 60s | ⭐⭐⭐ |
| **Parallel per Point** | 4 × 5s = 20s | ⭐⭐⭐⭐⭐ |
| **Fully Parallel** | 5s | ⭐⭐⭐⭐ (memory issues) |

**Decision:** Parallel per point - best balance of speed and resource usage.

### 3.2 Why Smart Queue (Not Simple Wait)?

| Strategy | Behavior | Problem |
|----------|----------|---------|
| **Wait Forever** | Block until all 3 respond | One slow agent blocks everything |
| **First Wins** | Take first response | Miss better content |
| **Smart Queue** | Wait for 3, accept 2 after 15s | ✅ Best of both |

**Decision:** Smart Queue with tiered timeouts.

### 3.3 Why Judge Agent (Not Simple Scoring)?

| Approach | Capability |
|----------|-----------|
| **Max Score** | Just picks highest number |
| **Rule-Based** | "If historical location, prefer text" |
| **LLM Judge** | ✅ Understands context, user profile, content quality |

**Decision:** LLM-powered Judge with profile-aware evaluation.

### 3.4 Why YAML Configuration?

Configuration format best practices:

| Use Case | Format | Reason |
|----------|--------|--------|
| Agent Config | YAML | Comments, readable |
| API Data | JSON | Universal, fast |
| Documentation | Markdown | Easy to write |

**Decision:** YAML for agents, JSON for data, Markdown for docs.

---

## 4. Component Specifications

### 4.1 User Profile Model

```yaml
# user_profile.yaml specification
UserProfile:
  demographics:
    - name: string                    # Optional user name
    - gender: MALE | FEMALE | NOT_SPECIFIED
    - age_group: KID | TEENAGER | YOUNG_ADULT | ADULT | SENIOR
    - exact_age: int (0-120)
    - language: HEBREW | ENGLISH | ARABIC | ...
  
  travel_context:
    - travel_mode: CAR | BUS | WALKING | BICYCLE
    - trip_purpose: VACATION | BUSINESS | EDUCATION | ROMANTIC | PILGRIMAGE
    - travel_pace: RUSHED | NORMAL | LEISURELY | EXPLORATORY
    - is_driver: boolean              # CRITICAL: No video if true!
    - social_context: SOLO | COUPLE | FAMILY | FRIENDS
  
  content_preferences:
    - content_preference: EDUCATIONAL | ENTERTAINMENT | HISTORICAL | ...
    - content_depth: QUICK_FACTS | SUMMARY | DETAILED | IN_DEPTH
    - max_duration_seconds: int
    - music_genres: list[MusicGenre]
    - interests: list[string]
  
  accessibility:
    - accessibility_needs: list[VISUAL | HEARING | COGNITIVE | ...]
    - requires_subtitles: boolean
    - prefer_audio_description: boolean
  
  exclusions:
    - exclude_topics: list[string]    # CRITICAL: Content filter
    - dietary_restrictions: list[string]
```

### 4.2 Agent Interface

```yaml
# base_agent.yaml specification
BaseAgent:
  interface:
    - execute(point: RoutePoint) -> ContentResult
    - search_content(point: RoutePoint) -> ContentResult
    - call_llm(prompt: string) -> string
  
  configuration:
    - name: string
    - model: string (e.g., "gpt-4o-mini")
    - temperature: float (0.0-1.0)
    - max_tokens: int
    - retry_count: int (default: 3)
    - timeout_seconds: int
  
  skills:
    - skill_name: string
    - description: string
    - search_strategy: string
    - scoring_criteria: list[string]
```

### 4.3 Smart Queue Specification

```yaml
SmartQueue:
  configuration:
    - expected_agents: 3
    - soft_timeout_seconds: 15.0
    - hard_timeout_seconds: 30.0
    - min_required_for_soft: 2
    - min_required_for_hard: 1
  
  states:
    - WAITING: Collecting results
    - COMPLETE: All 3 agents responded
    - SOFT_DEGRADED: 2/3 agents responded (soft timeout hit)
    - HARD_DEGRADED: 1/3 agents responded (hard timeout hit)
    - FAILED: No agents responded
  
  methods:
    - submit_success(agent_type, result)
    - submit_failure(agent_type, error)
    - wait_for_results() -> (list[ContentResult], QueueMetrics)
```

---

## 5. Prompts for Development

### 5.1 System Architecture Prompt

```markdown
# PROMPT: Create Multi-Agent Tour Guide Architecture

## Context
I am building a multi-agent AI system for personalized tour guides. The system should:
- Accept source and destination locations
- Query Google Maps API for route points
- Deploy 3 parallel agents (Video, Music, Text) per point
- Use a Smart Queue with tiered timeouts (15s soft, 30s hard)
- Have a Judge agent select best content based on user profile
- Support graceful degradation (proceed with 2/3 or 1/3 agents)

## Requirements
1. **Parallel Processing**: Use ThreadPoolExecutor for agent management
2. **Fault Tolerance**: Retry 3x with exponential backoff before failing
3. **User Personalization**: Content selection based on age, gender, interests
4. **Extensibility**: Plugin architecture for adding new agent types
5. **Configuration**: YAML files for agent definitions

## User Profile Considerations
- Age groups: KID, TEENAGER, ADULT, SENIOR
- Demographics: gender, language preference
- Accessibility: visual/hearing impairment needs
- Context: is_driver (NO VIDEO), trip purpose, energy level
- Preferences: music genres, interests, excluded topics

## Expected Output
1. System architecture diagram
2. Data flow between components
3. Class/interface definitions
4. Configuration file structure
5. Error handling strategy
```

### 5.2 Video Agent Prompt

```markdown
# PROMPT: Create Video Content Agent

## Role
You are VideoAgent, an AI agent specialized in finding relevant YouTube videos for travel locations.

## Input
- RoutePoint: {id, address, coordinates, location_name}
- UserProfile: {age_group, language, interests, is_driver, accessibility_needs}

## Task
1. Analyze the location to understand its significance
2. Search for relevant YouTube videos about this location
3. Filter results based on user profile:
   - If is_driver=true: Return EMPTY (user cannot watch video while driving)
   - If age_group=KID: Only family-friendly content
   - If visual_impairment: Prefer videos with audio descriptions
4. Score video relevance (0-10)
5. Return the best matching video

## Output Format
{
  "content_type": "video",
  "title": "Video title",
  "description": "Brief description",
  "url": "https://youtube.com/...",
  "source": "YouTube",
  "relevance_score": 8.5,
  "duration_seconds": 180,
  "metadata": {
    "channel": "...",
    "views": 1000000,
    "is_family_friendly": true
  }
}

## Search Strategy
1. Search: "{location_name} documentary"
2. Search: "{location_name} history"
3. Search: "{location_name} travel guide"
4. Filter by: duration < user.max_duration, language matches
5. Score by: relevance, quality, views, recency
```

### 5.3 Music Agent Prompt

```markdown
# PROMPT: Create Music Content Agent

## Role
You are MusicAgent, an AI agent specialized in finding relevant songs for travel locations.

## Input
- RoutePoint: {id, address, coordinates, location_name}
- UserProfile: {age_group, music_genres, favorite_artists, energy_level}

## Task
1. Analyze the location for musical associations
2. Search for songs related to the location
3. Filter based on user music preferences:
   - Match preferred genres
   - Consider artist preferences
   - Match energy level (calming vs upbeat)
4. Score song relevance (0-10)
5. Return the best matching song

## Output Format
{
  "content_type": "music",
  "title": "Song Title - Artist",
  "description": "Why this song fits",
  "url": "https://spotify.com/... or https://youtube.com/...",
  "source": "Spotify/YouTube",
  "relevance_score": 7.5,
  "duration_seconds": 240,
  "metadata": {
    "artist": "...",
    "album": "...",
    "genre": "...",
    "year": 2020
  }
}

## Search Strategy
1. Direct search: Songs about {location_name}
2. Genre match: {user.music_genres} songs about {region}
3. Artist match: Songs by {user.favorite_artists} about travel
4. Mood match: {user.energy_level} music for {trip_purpose}
```

### 5.4 Text Agent Prompt

```markdown
# PROMPT: Create Text Content Agent

## Role
You are TextAgent, an AI agent specialized in finding interesting facts and stories about travel locations.

## Input
- RoutePoint: {id, address, coordinates, location_name}
- UserProfile: {age_group, content_preference, interests, knowledge_level}

## Task
1. Research the location for interesting facts
2. Find historical stories, cultural significance, or fun facts
3. Adapt content to user profile:
   - age_group=KID: Simple language, fun facts
   - knowledge_level=expert: Advanced, detailed content
   - content_preference=HISTORICAL: Deep historical context
4. Score content relevance (0-10)
5. Return the best text content

## Output Format
{
  "content_type": "text",
  "title": "Fact/Story Title",
  "description": "The full text content (2-3 paragraphs)",
  "url": "https://wikipedia.org/... (source)",
  "source": "Wikipedia/AI-Generated",
  "relevance_score": 8.0,
  "metadata": {
    "fact_type": "historical | cultural | fun | scientific",
    "reading_time_seconds": 60,
    "sources_count": 3
  }
}

## Content Categories
1. Historical facts and events
2. Cultural significance
3. Famous people connected to location
4. Architectural/geological features
5. Local legends and stories
6. Fun/surprising facts
```

### 5.5 Judge Agent Prompt

```markdown
# PROMPT: Create Judge Agent for Content Selection

## Role
You are JudgeAgent, an AI agent that evaluates content from Video, Music, and Text agents and selects the BEST one for a specific user at a specific location.

## Input
- RoutePoint: {id, address, location_name}
- Candidates: List of ContentResult (1-3 items)
- UserProfile: Full user profile

## Decision Logic

### Case 1: All 3 Agents Responded
Compare all three against user profile:
- Apply content type weights based on age_group
- Check for accessibility requirements
- Consider user's explicit preferences
- Evaluate location-content match

### Case 2: Only 2 Agents Responded
Compare the two available options:
- Note the missing agent in reasoning
- Apply same scoring logic
- Slightly lower confidence in decision

### Case 3: Only 1 Agent Responded
Accept the available content:
- Verify it meets minimum requirements
- Note limited options in reasoning
- Flag if content is inappropriate for user

## Scoring Weights by User Profile

| Profile | Video Weight | Music Weight | Text Weight |
|---------|--------------|--------------|-------------|
| KID | 1.3 | 1.2 | 0.7 |
| TEENAGER | 1.2 | 1.4 | 0.6 |
| ADULT | 1.0 | 1.0 | 1.0 |
| SENIOR | 0.9 | 1.2 | 1.3 |
| DRIVER | 0.0 ⛔ | 1.5 | 1.2 |
| VISUAL_IMPAIRMENT | 0.3 | 1.5 | 1.3 |
| HEARING_IMPAIRMENT | 1.2 | 0.3 | 1.5 |

## Output Format
{
  "point_id": "point_1",
  "selected_content": ContentResult,
  "all_candidates": [ContentResult, ...],
  "reasoning": "Selected VIDEO because...",
  "scores": {
    "video": 8.5,
    "music": 7.0,
    "text": 6.5
  },
  "confidence": 0.85
}
```

### 5.6 Smart Queue Prompt

```markdown
# PROMPT: Create Smart Queue with Tiered Timeouts

## Role
SmartQueue manages synchronization between content agents and the Judge agent.

## Requirements
1. Wait for ALL 3 agents to respond (ideal case)
2. After 15 seconds: If 2/3 responded, proceed (graceful degradation)
3. After 30 seconds: If 1/3 responded, proceed (emergency fallback)
4. If 0 agents respond after 30s: Raise error

## Timeline
```
0s                    15s                   30s
│─────────────────────│─────────────────────│
│                     │                     │
│  PHASE 1            │  PHASE 2            │  PHASE 3
│  Wait for 3         │  Accept 2           │  Accept 1
│  (ideal quality)    │  (graceful)         │  (fallback)
│                     │                     │
```

## Interface
```python
class SmartQueue:
    def submit_success(agent_type: str, result: ContentResult)
    def submit_failure(agent_type: str, error: str)
    def wait_for_results() -> Tuple[List[ContentResult], QueueMetrics]
```

## Metrics to Track
- Time elapsed since queue creation
- Agents that succeeded
- Agents that failed
- Final status (COMPLETE | SOFT_DEGRADED | HARD_DEGRADED | FAILED)
- Wait time in milliseconds
```

---

## 6. Quality Attributes

### 6.1 Fault Tolerance

| Failure Scenario | Handling |
|------------------|----------|
| API timeout | Retry 3x with exponential backoff |
| API error | Log error, return failure to queue |
| Agent crash | Thread isolation, doesn't affect others |
| All agents fail | Graceful error message, skip point |

### 6.2 Scalability

| Dimension | Approach |
|-----------|----------|
| More users | Horizontal scaling (multiple instances) |
| More points | Async processing, streaming results |
| More agents | Plugin architecture, config-driven |
| More APIs | Adapter pattern, abstracted interfaces |

### 6.3 Extensibility

```
To add new agent (e.g., WeatherAgent):
1. Create: plugins/weather/agent.py
2. Create: plugins/weather/config.yaml
3. Enable: config/agents.yaml → enabled: true
4. Done! No core code changes.
```

### 6.4 Performance Targets

| Metric | Target |
|--------|--------|
| Single point processing | < 10 seconds |
| Full route (10 points) | < 60 seconds |
| API call latency | < 2 seconds |
| Memory per request | < 100 MB |

---

## 7. Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
- [ ] Project structure setup
- [ ] Data models (Pydantic)
- [ ] Configuration system (YAML)
- [ ] Logging infrastructure
- [ ] Google Maps API integration

### Phase 2: Core Agents (Week 3-4)
- [ ] Base agent class
- [ ] Video agent (YouTube)
- [ ] Music agent (Spotify/YouTube)
- [ ] Text agent (Wikipedia/AI)
- [ ] Agent configuration files

### Phase 3: Orchestration (Week 5-6)
- [ ] ThreadPoolExecutor orchestrator
- [ ] Smart Queue with timeouts
- [ ] Judge agent with profile matching
- [ ] Collector for results

### Phase 4: User Profile (Week 7)
- [ ] Comprehensive profile model
- [ ] Profile-based content weighting
- [ ] Accessibility support
- [ ] Preset profiles

### Phase 5: Production Readiness (Week 8)
- [ ] Retry/backoff mechanisms
- [ ] Caching layer
- [ ] Metrics and monitoring
- [ ] Error handling
- [ ] Documentation

---

## 8. Testing Strategy

### 8.1 Unit Tests

```python
# Test cases for each component
def test_video_agent_returns_content():
    agent = VideoAgent()
    result = agent.execute(mock_point)
    assert result.content_type == ContentType.VIDEO
    assert result.relevance_score > 0

def test_smart_queue_soft_timeout():
    queue = SmartQueue("test")
    queue.submit_success("video", mock_result)
    queue.submit_success("text", mock_result)
    # Wait for soft timeout
    results, metrics = queue.wait_for_results()
    assert len(results) == 2
    assert metrics.status == QueueStatus.SOFT_DEGRADED

def test_judge_respects_driver_profile():
    profile = UserProfile(is_driver=True)
    judge = JudgeAgent(profile)
    weights = profile.get_content_type_preferences()
    assert weights["video"] == 0.0  # Driver cannot watch video
```

### 8.2 Integration Tests

```python
def test_full_pipeline():
    setup = TourSetup(
        source="Tel Aviv",
        destination="Jerusalem",
        user_profile=get_family_profile(min_age=5)
    )
    result = run_tour_guide(setup)
    assert len(result.points) > 0
    for point in result.points:
        assert point.selected_content is not None
```

---

## 9. Future Extensions

### 9.1 Planned Features

| Feature | Description | Priority |
|---------|-------------|----------|
| AR Agent | Augmented reality overlays | Medium |
| Voice Agent | Audio narration | High |
| Food Agent | Restaurant recommendations | Medium |
| Weather Agent | Weather forecasts | Low |
| Event Agent | Local events happening | Medium |

### 9.2 ML Enhancements

| Enhancement | Purpose |
|-------------|---------|
| Content Ranking ML | Learn from user feedback |
| Profile Clustering | Similar user recommendations |
| Route Optimization | Best content distribution |

### 9.3 Platform Expansion

| Platform | Status |
|----------|--------|
| CLI | ✅ Current |
| REST API | Planned |
| Mobile App | Future |
| Web App | Future |
| Car Integration | Future |

---

## Appendix A: File Structure

```
Assignment4-multi-agent-tour-guide-parallel/
│
├── docs/                           # 📚 Documentation
│   ├── MIT_PROJECT_SPECIFICATION.md  # This file
│   ├── ARCHITECTURE.md             # Architecture details
│   ├── DESIGN_DECISIONS.md         # Design rationale
│   ├── QUALITY_ATTRIBUTES.md       # Quality analysis
│   └── STARTUP_DESIGN.md           # Production design
│
├── agents/                         # 🤖 AI Agents
│   ├── __init__.py
│   ├── base_agent.py               # Abstract base class
│   ├── video_agent.py              # YouTube video finder
│   ├── music_agent.py              # Music finder
│   ├── text_agent.py               # Text/facts finder
│   ├── judge_agent.py              # Content evaluator
│   ├── config_loader.py            # YAML config loader
│   └── configs/                    # YAML configurations
│       ├── video_agent.yaml
│       ├── music_agent.yaml
│       ├── text_agent.yaml
│       └── judge_agent.yaml
│
├── plugins/                        # 🔌 Future plugin agents
│   └── README.md
│
├── smart_queue.py                  # 📬 Queue with timeouts
├── orchestrator.py                 # 🎭 Thread management
├── timer_scheduler.py              # ⏱️ Travel simulation
├── collector.py                    # 📦 Result aggregation
│
├── google_maps_api.py              # 🗺️ Route extraction
├── user_profile.py                 # 👤 User preferences
├── models.py                       # 📋 Data models
├── config.py                       # ⚙️ System configuration
├── logger_setup.py                 # 📝 Logging
│
├── main.py                         # 🚀 Entry point
├── requirements.txt                # 📦 Dependencies
└── README.md                       # 📖 Quick start
```

---

## Appendix B: Quick Start Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run demo mode
python main.py --demo --mode queue

# Run with custom profile
python main.py --demo --profile family --min-age 5

# Run with custom route (requires API key)
python main.py --origin "Tel Aviv" --destination "Jerusalem"

# Interactive setup
python main.py --interactive
```

---

**Document End**

*This specification follows MIT-level project documentation standards and provides a complete blueprint for implementing, testing, and extending the Multi-Agent Tour Guide System.*

