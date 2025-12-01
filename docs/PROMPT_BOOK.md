# 📖 MIT-Level Prompt Engineering Book

## Multi-Agent Tour Guide System - Complete Prompt Library

**Version:** 2.0.0  
**License:** MIT  
**Last Updated:** November 2025  
**Academic Level:** MIT / Publication-Ready

---

## 📚 Table of Contents

1. [Introduction](#1-introduction)
2. [Prompt Engineering Principles](#2-prompt-engineering-principles)
3. [System Architecture Prompts](#3-system-architecture-prompts)
4. [Agent Development Prompts](#4-agent-development-prompts)
5. [Orchestration & Infrastructure Prompts](#5-orchestration--infrastructure-prompts)
6. [Testing & Quality Prompts](#6-testing--quality-prompts)
7. [Research & Analysis Prompts](#7-research--analysis-prompts)
8. [Documentation Prompts](#8-documentation-prompts)
9. [Troubleshooting Prompts](#9-troubleshooting-prompts)
10. [Advanced Extension Prompts](#10-advanced-extension-prompts)
11. [Prompt Templates Library](#11-prompt-templates-library)

---

## 1. Introduction

### 1.1 What is This Document?

This **Prompt Book** is a comprehensive library of **copy-paste ready prompts** used to develop the Multi-Agent Tour Guide System. Each prompt follows MIT-level engineering standards and can be used with any LLM (Claude, GPT-4, Gemini).

### 1.2 How to Use This Book

```
📋 QUICK REFERENCE
├── 🏗️ Building Features → Section 3-5
├── 🧪 Testing → Section 6
├── 🔬 Research → Section 7
├── 📚 Documentation → Section 8
├── 🔧 Troubleshooting → Section 9
└── 🔌 Extensions → Section 10
```

### 1.3 Prompt Difficulty Levels

| Level | Icon | Description |
|-------|------|-------------|
| Beginner | 🟢 | Simple, single-task prompts |
| Intermediate | 🟡 | Multi-step prompts |
| Advanced | 🔴 | Complex, architectural prompts |
| Research | 🔬 | Academic/publication-level prompts |

---

## 2. Prompt Engineering Principles

### 2.1 The CRISPE Framework

All prompts in this book follow the **CRISPE** framework:

```
C - Capacity (Role): Define the AI's expertise
R - Request (Task): What to accomplish
I - Information (Context): Background data
S - Style (Format): Output format
P - Personality (Tone): Communication style
E - Examples: Sample inputs/outputs
```

### 2.2 Best Practices Applied

| Practice | Implementation |
|----------|----------------|
| **Be Specific** | Include exact requirements, constraints |
| **Provide Context** | System architecture, dependencies |
| **Define Output** | JSON schemas, code format |
| **Include Examples** | Input/output samples |
| **Set Boundaries** | Edge cases, error handling |

### 2.3 Prompt Quality Checklist

```markdown
✅ Clear role definition
✅ Specific task description
✅ Context and constraints
✅ Expected output format
✅ Error handling requirements
✅ Edge case coverage
✅ Example input/output
```

---

## 3. System Architecture Prompts

### 3.1 🔴 Initial Project Setup

```markdown
# PROMPT: Create Multi-Agent System Project Structure

## Capacity (Role)
You are a senior software architect specializing in Python multi-agent AI systems
with expertise in clean architecture, SOLID principles, and MIT-level software engineering.

## Request (Task)
Create a production-ready Python project structure for a multi-agent tour guide system.

## Information (Context)
The system will:
- Accept source/destination locations from users
- Query Google Maps API for route waypoints
- Deploy 3 parallel AI agents (Video, Music, Text) per waypoint
- Use Smart Queue with tiered timeouts for synchronization
- Have Judge agent select best content based on user profile

## Style (Output Format)
Provide:
1. Complete directory tree with descriptions
2. Key file boilerplates
3. Configuration file templates
4. Import structure guidelines

## Constraints
- Python 3.10+
- Use UV for package management
- Pydantic v2 for data models
- Type hints required
- 85%+ test coverage target

## Example Output Structure
```
src/
├── agents/           # AI agent implementations
├── core/             # Infrastructure (queue, orchestrator)
├── models/           # Pydantic data models
├── services/         # External service clients
└── utils/            # Utilities
```
```

### 3.2 🔴 System Architecture Design

```markdown
# PROMPT: Design Multi-Agent Tour Guide Architecture

## Capacity
You are an enterprise architect designing production-grade AI orchestration systems.

## Request
Design the complete system architecture for the Multi-Agent Tour Guide System.

## Information
Requirements:
1. **Parallel Processing**: 3 agents per point, concurrent execution
2. **Fault Tolerance**: Graceful degradation, retry, circuit breaker
3. **User Personalization**: Content selection based on demographics
4. **Extensibility**: Plugin architecture for new agents
5. **Observability**: Metrics, logging, tracing

## Style
Provide:
1. C4 Model diagrams (Context, Container, Component)
2. Data flow diagrams
3. Sequence diagrams for key flows
4. Component interface definitions

## Constraints
- Maximum 12 concurrent threads
- < 30s total processing time per point
- Support 100+ concurrent users
- ISO/IEC 25010 quality compliance

## Expected Deliverables
1. Architecture decision records (ADRs)
2. Component specifications
3. API contracts
4. Error handling strategy
```

### 3.3 🟡 Data Models Design

```markdown
# PROMPT: Create Pydantic Data Models

## Capacity
You are a data modeling expert using Pydantic v2 for Python type validation.

## Request
Create comprehensive Pydantic models for the tour guide system.

## Models Required

### RoutePoint
```python
@dataclass
class RoutePoint:
    id: str                              # Unique identifier
    index: int                           # Position in route
    address: str                         # Full address
    latitude: float                      # GPS coordinates
    longitude: float
    location_name: Optional[str]         # Human-readable name
    estimated_arrival_seconds: Optional[int]
```

### ContentResult
```python
class ContentResult:
    content_type: ContentType            # VIDEO | MUSIC | TEXT
    title: str                           # Content title
    description: str                     # Brief description
    url: str                             # Source URL
    source: str                          # Provider name
    relevance_score: float               # 0-10 score
    duration_seconds: Optional[int]      # Content duration
    metadata: Dict[str, Any]             # Additional data
```

### JudgeDecision
```python
class JudgeDecision:
    point_id: str
    selected_content: ContentResult
    all_candidates: List[ContentResult]
    reasoning: str                       # Why this was selected
    scores: Dict[ContentType, float]     # Per-type scores
    confidence: float                    # Decision confidence
```

## Style
- Use Pydantic v2 syntax (model_validator, Field)
- Include JSON schema examples
- Add serialization methods
- Support optional fields with defaults
- Include validators for all fields

## Constraints
- All scores: 0.0-10.0 range
- URLs must be valid
- Coordinates must be valid lat/lng
```

### 3.4 🔴 User Profile System

```markdown
# PROMPT: Create Comprehensive User Profile for Personalization

## Capacity
You are a UX researcher and personalization system designer.

## Request
Create a comprehensive user profile model that captures all dimensions
needed for content personalization.

## Profile Dimensions

### Demographics
- name, gender, age_group (KID|TEENAGER|ADULT|SENIOR)
- exact_age (for fine-grained filtering)
- language preference

### Travel Context
- travel_mode: CAR | BUS | WALKING | BICYCLE
- trip_purpose: VACATION | BUSINESS | EDUCATION | ROMANTIC
- is_driver: bool  # CRITICAL: No video content if true!
- social_context: SOLO | COUPLE | FAMILY | FRIENDS

### Content Preferences
- content_preference: EDUCATIONAL | ENTERTAINMENT | HISTORICAL
- content_depth: QUICK_FACTS | DETAILED | IN_DEPTH
- max_duration_seconds: int
- music_genres: List[MusicGenre]
- interests: List[str]

### Accessibility
- accessibility_needs: List[VISUAL | HEARING | COGNITIVE | MOBILITY]
- requires_subtitles: bool
- prefer_audio_description: bool

### Exclusions
- exclude_topics: List[str]  # Content filter

## Required Methods
```python
def to_agent_context(self) -> str:
    """Generate context string for agent prompts"""
    
def to_judge_criteria(self) -> str:
    """Generate criteria for judge evaluation"""
    
def get_content_type_preferences(self) -> Dict[str, float]:
    """Return scoring weights per content type"""
```

## Preset Profiles Required
- get_kid_profile(age: int)
- get_teenager_profile()
- get_senior_profile()
- get_family_profile(min_age: int)
- get_driver_profile()  # VIDEO weight = 0
- get_accessibility_visual_profile()

## Critical Rules
1. Driver profile must NEVER recommend video
2. Kid profiles must filter adult content
3. Accessibility needs override preferences
```

---

## 4. Agent Development Prompts

### 4.1 🟡 Base Agent Class

```markdown
# PROMPT: Create Abstract Base Agent

## Capacity
You are a Python developer specializing in multi-agent AI systems with
expertise in LLM integration and fault-tolerant design.

## Request
Create an abstract base class for AI agents that provides common functionality.

## Class: BaseAgent(ABC)

### Constructor
```python
def __init__(self, agent_type: str):
    self.agent_type = agent_type
    self.config = self._load_config(agent_type)
    self.llm_client = self._init_llm_client()
```

### Abstract Methods
```python
@abstractmethod
def get_content_type(self) -> ContentType:
    """Return the type of content this agent produces"""
    
@abstractmethod
def _search_content(self, point: RoutePoint, profile: UserProfile) -> Optional[ContentResult]:
    """Search for content - implement in subclass"""
```

### Concrete Methods
```python
def execute(self, point: RoutePoint, profile: UserProfile, queue: SmartQueue) -> None:
    """
    Execute agent task with retry logic:
    1. Retry 3 times with exponential backoff (1s, 2s, 4s)
    2. Submit success/failure to queue
    3. Log all attempts
    """
    
def _call_llm(self, prompt: str) -> str:
    """
    Call LLM API with error handling:
    - Support Anthropic and OpenAI
    - Use config for model, temperature, max_tokens
    - Handle rate limits and timeouts
    """
    
def _load_config(self, agent_type: str) -> Dict:
    """Load YAML config from src/agents/configs/{agent_type}_agent.yaml"""
```

## YAML Configuration Structure
```yaml
agent:
  name: "Agent Name"
  version: "1.0.0"
  description: "What this agent does"

config:
  model: "claude-sonnet-4-20250514"
  temperature: 0.7
  max_tokens: 1000
  timeout_seconds: 30

skills:
  - name: "skill_name"
    description: "What the skill does"
    search_strategy: "How to search"

scoring_criteria:
  - "Criterion 1"
  - "Criterion 2"
```

## Thread Safety Requirements
- Agents run in parallel ThreadPoolExecutor
- No shared mutable state
- Queue submissions are thread-safe
```

### 4.2 🟡 Video Agent

```markdown
# PROMPT: Create Video Agent for YouTube Content

## Capacity
You are VideoAgent, an AI agent specialized in finding relevant YouTube videos
for travel locations.

## Request
Implement the VideoAgent that searches for location-relevant videos.

## Input
- RoutePoint: {id, address, coordinates, location_name}
- UserProfile: {age_group, language, interests, is_driver, accessibility_needs}

## Task Logic
```python
def _search_content(self, point: RoutePoint, profile: UserProfile) -> Optional[ContentResult]:
    # CRITICAL CHECK FIRST
    if profile.is_driver:
        return None  # Drivers cannot watch videos!
    
    # Build search queries
    queries = [
        f"{point.location_name} documentary",
        f"{point.location_name} history",
        f"{point.location_name} travel guide"
    ]
    
    # Search and filter
    results = self._search_youtube(queries)
    results = self._filter_by_profile(results, profile)
    
    # Select best result
    return self._select_best(results, point, profile)
```

## Filtering Rules
| Profile | Filter |
|---------|--------|
| is_driver=True | Return None immediately |
| age_group=KID | Only family-friendly content |
| VISUAL_IMPAIRMENT | Prefer videos with audio descriptions |
| max_duration | Filter by duration limit |

## LLM Prompt for Selection
```
You are a video content curator for travelers.

Location: {location_name}
Address: {address}
User Profile: {profile_context}

Find the most relevant YouTube video for this location.

Consider:
1. Educational value
2. Entertainment quality
3. Relevance to location
4. Appropriateness for user

Return JSON:
{
  "title": "...",
  "description": "...",
  "url": "https://youtube.com/...",
  "relevance_score": 8.5,
  "reasoning": "Why this video"
}
```

## Output
ContentResult with content_type=VIDEO
```

### 4.3 🟡 Music Agent

```markdown
# PROMPT: Create Music Agent for Song Recommendations

## Capacity
You are MusicAgent, an AI agent specialized in finding relevant songs
for travel locations.

## Request
Implement the MusicAgent that searches for location-relevant music.

## Search Strategy
1. Search for songs ABOUT the location
2. Search for songs BY artists FROM the region
3. Match user's music genre preferences
4. Match energy level (calming vs upbeat)

## Profile Integration
```python
def _apply_preferences(self, results: List, profile: UserProfile) -> List:
    # Genre matching
    if profile.music_genres:
        results = [r for r in results if r.genre in profile.music_genres]
    
    # Energy level matching
    if profile.trip_purpose == TripPurpose.ROMANTIC:
        results = self._filter_by_mood(results, "romantic")
    elif profile.energy_level == EnergyLevel.HIGH:
        results = self._filter_by_mood(results, "upbeat")
    
    return results
```

## LLM Prompt
```
You are a music curator for travelers.

Location: {location_name}
User Music Preferences:
  - Genres: {music_genres}
  - Artists: {favorite_artists}
  - Energy: {energy_level}
  - Trip: {trip_purpose}

Find a song that:
1. Relates to this location (about the place, by local artist, or captures mood)
2. Matches user's music taste
3. Fits the travel experience

Return JSON:
{
  "title": "Song Title - Artist",
  "artist": "Artist Name",
  "genre": "genre",
  "description": "Why this song fits",
  "url": "https://...",
  "relevance_score": 7.5
}
```
```

### 4.4 🟡 Text Agent

```markdown
# PROMPT: Create Text Agent for Facts/Stories

## Capacity
You are TextAgent, an AI agent specialized in finding interesting facts
and stories about travel locations.

## Request
Implement the TextAgent that provides educational/entertaining text content.

## Content Categories
1. Historical facts and events
2. Cultural significance
3. Famous people connections
4. Architectural/geological features
5. Local legends and stories
6. Fun/surprising facts

## Profile Adaptation
| Profile | Content Style |
|---------|---------------|
| age_group=KID | Simple language, fun facts |
| age_group=TEENAGER | Surprising, trending facts |
| age_group=SENIOR | Historical, nostalgic content |
| knowledge_level=EXPERT | Deep, detailed content |
| content_preference=HISTORICAL | Focus on history |

## LLM Prompt
```
You are a knowledgeable tour guide creating content about locations.

Location: {location_name}
Address: {address}
User Profile:
  - Age Group: {age_group}
  - Interests: {interests}
  - Content Depth: {content_depth}
  - Language: {language}

Provide an engaging fact or story about this location.

Requirements:
1. Match content to user's age and interests
2. Be engaging and memorable
3. Be accurate (cite sources if possible)
4. Length: {content_depth_length}

Return JSON:
{
  "title": "Fact/Story Title",
  "content": "The full text (2-3 paragraphs)",
  "fact_type": "historical | cultural | fun | scientific",
  "source": "Wikipedia/other",
  "relevance_score": 8.0
}
```
```

### 4.5 🔴 Judge Agent

```markdown
# PROMPT: Create Judge Agent for Content Selection

## Capacity
You are JudgeAgent, an AI agent that evaluates content from Video, Music,
and Text agents and selects the BEST one for a specific user.

## Request
Implement the JudgeAgent with profile-aware content selection.

## Decision Logic

### Case 1: All 3 Agents Responded
- Full LLM comparison
- Apply user profile weights
- Consider location appropriateness
- Evaluate uniqueness

### Case 2: Only 2 Agents Responded
- Compare available options
- Note missing agent in reasoning
- Slightly lower confidence

### Case 3: Only 1 Agent Responded
- Verify meets minimum requirements
- Accept if appropriate
- Flag if potentially inappropriate

## Scoring Weights
```python
PROFILE_WEIGHTS = {
    AgeGroup.KID: {"video": 1.3, "music": 1.2, "text": 0.7},
    AgeGroup.TEENAGER: {"video": 1.2, "music": 1.4, "text": 0.6},
    AgeGroup.ADULT: {"video": 1.0, "music": 1.0, "text": 1.0},
    AgeGroup.SENIOR: {"video": 0.9, "music": 1.2, "text": 1.3},
}

ACCESSIBILITY_OVERRIDES = {
    AccessibilityNeed.VISUAL: {"video": 0.3, "music": 1.5, "text": 1.3},
    AccessibilityNeed.HEARING: {"video": 1.2, "music": 0.3, "text": 1.5},
}

# CRITICAL: Driver override
if profile.is_driver:
    weights["video"] = 0.0  # No video for drivers!
    weights["music"] = 1.5
```

## LLM Evaluation Prompt
```
You are a content curator selecting the BEST content for a specific user.

LOCATION: {location}
USER PROFILE: {profile_context}
USER CRITERIA: {criteria}

CANDIDATES:
1. {candidate_1}
2. {candidate_2}
3. {candidate_3}

Evaluate each candidate and select the BEST one for THIS USER.

Consider:
1. Location relevance
2. User age and preferences
3. Accessibility needs
4. Trip purpose and mood

Response format:
{
  "scores": {"video": 7.5, "music": 8.0, "text": 6.5},
  "winner": 2,
  "reasoning": "Selected MUSIC because...",
  "confidence": 0.85
}
```

## Quick Evaluate Method
```python
def quick_evaluate(self, candidates: List[ContentResult], profile: UserProfile) -> ContentResult:
    """No LLM fallback - use scoring weights only"""
    weights = self._get_weights(profile)
    best = max(candidates, key=lambda c: c.relevance_score * weights[c.content_type])
    return best
```
```

---

## 5. Orchestration & Infrastructure Prompts

### 5.1 🔴 Smart Queue Implementation

```markdown
# PROMPT: Create Smart Queue with Tiered Timeouts

## Capacity
You are a systems programmer specializing in concurrent programming and
synchronization primitives.

## Request
Create SmartAgentQueue that synchronizes agent results with graceful degradation.

## Timeout Strategy
```
Timeline:
0s                    15s (soft)            30s (hard)
│─────────────────────│─────────────────────│
│                     │                     │
│  Wait for 3         │  Accept 2           │  Accept 1
│  (ideal)            │  (graceful)         │  (emergency)
```

## Configuration
```python
@dataclass
class QueueConfig:
    expected_agents: int = 3
    soft_timeout_seconds: float = 15.0
    hard_timeout_seconds: float = 30.0
    min_required_for_soft: int = 2
    min_required_for_hard: int = 1
```

## States
```python
class QueueStatus(Enum):
    WAITING = "waiting"           # Collecting results
    COMPLETE = "complete"         # All 3 responded
    SOFT_DEGRADED = "soft"        # 2/3 responded
    HARD_DEGRADED = "hard"        # 1/3 responded
    FAILED = "failed"             # 0 responded
```

## Interface
```python
class SmartAgentQueue:
    def submit_success(self, agent_type: str, result: ContentResult) -> None:
        """Thread-safe result submission"""
        
    def submit_failure(self, agent_type: str, error: str) -> None:
        """Thread-safe failure submission"""
        
    def wait_for_results(self) -> Tuple[List[ContentResult], QueueMetrics]:
        """Block until ready, return results and metrics"""
```

## Thread Safety
- Use threading.Condition for synchronization
- Proper locking on all shared state
- No race conditions possible

## Metrics
```python
@dataclass
class QueueMetrics:
    point_id: str
    start_time: datetime
    end_time: datetime
    status: QueueStatus
    agents_expected: int
    agents_succeeded: List[str]
    agents_failed: List[str]
    wait_time_ms: int
```
```

### 5.2 🔴 Orchestrator Design

```markdown
# PROMPT: Create Thread Pool Orchestrator

## Capacity
You are a concurrent systems architect designing high-throughput
multi-agent orchestration.

## Request
Create TourOrchestrator that manages parallel execution of agents.

## Components
- ThreadPoolExecutor for parallel agents
- SmartQueue for synchronization per point
- JudgeAgent for content selection
- Collector for result aggregation

## Execution Flow
```python
def process_point(self, point: RoutePoint, profile: UserProfile) -> JudgeDecision:
    queue = SmartQueue(point.id)
    
    # Spawn 3 agents in parallel
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(self.video_agent.execute, point, profile, queue),
            executor.submit(self.music_agent.execute, point, profile, queue),
            executor.submit(self.text_agent.execute, point, profile, queue),
        ]
    
    # Wait for results
    results, metrics = queue.wait_for_results()
    
    # Judge selects best
    decision = self.judge.evaluate(point, results, profile)
    
    return decision
```

## Processing Modes
| Mode | Description | Use Case |
|------|-------------|----------|
| SEQUENTIAL | One point at a time | Debugging |
| QUEUE | Queue sync per point | **Recommended** |
| INSTANT | All points parallel | Quick results |
| STREAMING | Timer-based emission | Real-time demo |

## Resource Management
```python
MAX_WORKERS_PER_POINT = 3   # Video, Music, Text
MAX_PARALLEL_POINTS = 4     # Prevent overload
TOTAL_MAX_THREADS = 12      # 3 * 4

# Thread pool configuration
self.executor = ThreadPoolExecutor(
    max_workers=TOTAL_MAX_THREADS,
    thread_name_prefix="agent-"
)
```
```

### 5.3 🟡 Resilience Patterns

```markdown
# PROMPT: Implement Resilience Patterns

## Capacity
You are a site reliability engineer implementing fault-tolerant patterns.

## Request
Implement resilience patterns for the agent system.

## Patterns Required

### Circuit Breaker
```python
class CircuitBreaker:
    """
    States: CLOSED → OPEN → HALF_OPEN → CLOSED
    
    - CLOSED: Normal operation
    - OPEN: Fail fast after threshold failures
    - HALF_OPEN: Test if service recovered
    """
    def __init__(self, failure_threshold=5, reset_timeout=60):
        ...
    
    def call(self, func, *args, **kwargs):
        if self.state == State.OPEN:
            if time.time() - self.last_failure > self.reset_timeout:
                self.state = State.HALF_OPEN
            else:
                raise CircuitOpenError()
        ...
```

### Retry with Exponential Backoff
```python
def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    jitter: bool = True
) -> Any:
    """
    Retry pattern: delay = min(base * (exp ^ attempt), max)
    With optional jitter to prevent thundering herd
    """
```

### Rate Limiter
```python
class RateLimiter:
    """Token bucket algorithm"""
    def __init__(self, rate: float, burst: int):
        self.rate = rate      # Tokens per second
        self.burst = burst    # Max tokens
        self.tokens = burst
        self.last_update = time.time()
    
    def acquire(self, tokens: int = 1) -> bool:
        """Return True if tokens acquired, False if rate limited"""
```

### Timeout Wrapper
```python
def with_timeout(timeout_seconds: float):
    """Decorator for timeout enforcement"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(func, *args, **kwargs)
                return future.result(timeout=timeout_seconds)
        return wrapper
    return decorator
```
```

---

## 6. Testing & Quality Prompts

### 6.1 🟡 Unit Test Generation

```markdown
# PROMPT: Generate Comprehensive Unit Tests

## Capacity
You are a test engineer creating MIT-level test suites with pytest.

## Request
Generate comprehensive unit tests covering all components.

## Test Categories

### User Profile Tests
```python
def test_kid_profile_prefers_video():
    profile = get_kid_profile(age=8)
    weights = profile.get_content_type_preferences()
    assert weights["video"] > weights["text"]

def test_driver_profile_blocks_video():
    profile = get_driver_profile()
    weights = profile.get_content_type_preferences()
    assert weights["video"] == 0.0

def test_visual_impairment_prefers_audio():
    profile = get_accessibility_visual_profile()
    weights = profile.get_content_type_preferences()
    assert weights["music"] > weights["video"]
```

### Smart Queue Tests
```python
def test_queue_completes_with_all_three():
    queue = SmartQueue("test-point")
    queue.submit_success("video", mock_video_result)
    queue.submit_success("music", mock_music_result)
    queue.submit_success("text", mock_text_result)
    
    results, metrics = queue.wait_for_results()
    assert len(results) == 3
    assert metrics.status == QueueStatus.COMPLETE

def test_queue_soft_timeout_with_two():
    queue = SmartQueue("test-point", soft_timeout=0.1)
    queue.submit_success("video", mock_video_result)
    queue.submit_success("music", mock_music_result)
    # Don't submit text - trigger soft timeout
    
    results, metrics = queue.wait_for_results()
    assert len(results) == 2
    assert metrics.status == QueueStatus.SOFT_DEGRADED
```

### Judge Tests
```python
def test_judge_respects_driver_profile():
    profile = get_driver_profile()
    judge = JudgeAgent(profile)
    
    decision = judge.evaluate(
        mock_point,
        [mock_video_result, mock_music_result],
        profile
    )
    
    # Should never select video for driver
    assert decision.selected_content.content_type != ContentType.VIDEO
```

## Coverage Requirements
- 85% minimum coverage
- All edge cases documented
- All error paths tested
- All configuration variations tested

## Fixtures
```python
@pytest.fixture
def mock_point():
    return RoutePoint(
        id="test-1",
        index=0,
        address="123 Test St",
        latitude=32.0,
        longitude=34.0,
        location_name="Test Location"
    )

@pytest.fixture
def mock_video_result():
    return ContentResult(
        content_type=ContentType.VIDEO,
        title="Test Video",
        description="A test video",
        url="https://youtube.com/test",
        source="YouTube",
        relevance_score=8.0
    )
```
```

### 6.2 🟡 Integration Test Prompts

```markdown
# PROMPT: Generate Integration Tests

## Capacity
You are a QA engineer testing multi-component interactions.

## Request
Create integration tests for the complete agent pipeline.

## Test Scenarios

### Full Pipeline Test
```python
def test_full_pipeline_demo_mode():
    result = run_tour_guide(
        source="Tel Aviv",
        destination="Jerusalem",
        demo=True,
        mode="queue"
    )
    
    assert result.points is not None
    assert len(result.points) > 0
    for point in result.points:
        assert point.selected_content is not None
        assert point.decision.reasoning is not None

def test_pipeline_with_family_profile():
    profile = get_family_profile(min_age=5)
    result = run_tour_guide(
        source="Tel Aviv",
        destination="Jerusalem",
        demo=True,
        profile=profile
    )
    
    # Verify all content is family-appropriate
    for point in result.points:
        assert point.selected_content.metadata.get("is_family_friendly", True)
```

### Timeout Handling Test
```python
@pytest.mark.timeout(60)
def test_handles_slow_agent():
    """Verify queue degrades gracefully with slow agent"""
    # Mock video agent to be very slow
    with patch.object(VideoAgent, 'execute', side_effect=slow_mock):
        result = run_single_point(mock_point, default_profile)
        
        # Should complete with music/text only
        assert result is not None
        assert result.metrics.status in [QueueStatus.SOFT_DEGRADED, QueueStatus.HARD_DEGRADED]
```
```

---

## 7. Research & Analysis Prompts

### 7.1 🔬 Sensitivity Analysis Setup

```markdown
# PROMPT: Create Sensitivity Analysis Framework

## Capacity
You are a research scientist implementing Monte Carlo sensitivity analysis
for academic publication.

## Request
Create a framework for analyzing how parameters affect system behavior.

## Parameters to Analyze
| Parameter | Range | Default |
|-----------|-------|---------|
| soft_timeout | [5s, 30s] | 15s |
| hard_timeout | [15s, 60s] | 30s |
| agent_reliability | [0.7, 1.0] | 0.95 |
| response_time_mean | [1s, 10s] | 3s |

## Analysis Methods

### Local Sensitivity (OAT)
```python
def local_sensitivity_analysis(baseline_config, param_name, values):
    """One-at-a-time sensitivity analysis"""
    results = []
    for value in values:
        config = baseline_config.copy()
        config[param_name] = value
        metrics = run_simulation(config, n_runs=1000)
        results.append({
            'param_value': value,
            'mean_latency': np.mean(metrics['latency']),
            'mean_quality': np.mean(metrics['quality']),
            'complete_rate': np.mean(metrics['status'] == 'complete')
        })
    return pd.DataFrame(results)
```

### Global Sensitivity (Sobol Indices)
```python
def sobol_sensitivity_analysis(n_samples=10000):
    """Calculate first-order and total Sobol indices"""
    # Generate samples using Sobol sequence
    # Run simulations
    # Calculate indices
    return {
        'S1': first_order_indices,   # Main effects
        'ST': total_indices,         # Total effects including interactions
    }
```

### Statistical Comparison
```python
def compare_configurations(config_a, config_b, n_runs=10000):
    """Statistical hypothesis testing between configurations"""
    results_a = run_simulation(config_a, n_runs)
    results_b = run_simulation(config_b, n_runs)
    
    return {
        't_test': ttest_ind(results_a['latency'], results_b['latency']),
        'mann_whitney': mannwhitneyu(results_a['latency'], results_b['latency']),
        'effect_size': cohens_d(results_a['latency'], results_b['latency']),
        'bootstrap_ci': bootstrap_confidence_interval(results_a, results_b)
    }
```

## Output Requirements
- Publication-quality figures (300 DPI)
- Statistical significance (p < 0.05)
- Effect sizes with confidence intervals
- Reproducible results (fixed seeds)
```

### 7.2 🔬 Mathematical Proofs

```markdown
# PROMPT: Formal Analysis of Queue System

## Capacity
You are a theoretical computer scientist writing formal proofs
for publication in peer-reviewed journals.

## Request
Provide formal analysis of the Smart Queue system.

## Proofs Required

### Theorem 1: Liveness
```
For any configuration (soft_timeout, hard_timeout), the queue
terminates within hard_timeout seconds.

Proof:
Let t_h be hard_timeout.
The wait_for_results() method has bounded wait:
  wait(t) ≤ t_h for all executions.
  
By construction, after t_h:
  if |results| ≥ 1: return (results, HARD_DEGRADED)
  else: raise NoResultsError
  
Therefore, termination is guaranteed. ∎
```

### Theorem 2: Quality Degradation Bound
```
Let Q(n) be expected quality with n agents responding.
Then: Q(1) ≤ Q(2) ≤ Q(3)

Proof:
Expected quality with n agents:
  Q(n) = max(score_1, ..., score_n)
  
For independent agent scores with CDF F:
  E[Q(n)] = n ∫ x·F(x)^(n-1)·f(x) dx
  
Since n₁ < n₂ implies F(x)^(n₁-1) ≤ F(x)^(n₂-1) for x ≤ median:
  E[Q(n₁)] ≤ E[Q(n₂)] ∎
```

### Theorem 3: Time Complexity
```
Time complexity: O(m·n·s) where:
  m = route points
  n = agents per point (3)
  s = average agent response time

Proof:
Each point processed in parallel:
  T_point = max(T_video, T_music, T_text)
  E[T_point] = ∫₀^∞ (1 - F_max(t)) dt
  
With m points and bounded parallelism p:
  T_total = ⌈m/p⌉ · E[T_point]
  
Substituting: O(m·n·s) ∎
```
```

---

## 8. Documentation Prompts

### 8.1 🟢 README Generation

```markdown
# PROMPT: Generate Production README

## Capacity
You are a technical writer creating documentation for open-source projects.

## Request
Generate a comprehensive README.md with:
1. Project overview with badges
2. Quick start guide (< 5 commands)
3. Architecture overview
4. Installation instructions
5. Usage examples
6. Configuration reference
7. Contributing guidelines

## Style
- Clear, scannable sections
- Code examples with expected output
- Tables for configuration reference
- Emoji icons for visual navigation
- Links to detailed documentation

## Sections Required
- What is This?
- Quick Start
- Features
- Architecture
- Installation
- Usage
- Configuration
- Testing
- Contributing
- License
```

### 8.2 🟡 ADR Template

```markdown
# PROMPT: Create Architecture Decision Record

## Capacity
You are an architect documenting key technical decisions.

## Request
Document the following decision in ADR format.

## ADR Template
```markdown
# ADR-{NUMBER}: {TITLE}

## Status
{Proposed | Accepted | Deprecated | Superseded}

## Context
{What is the issue that we're seeing that is motivating this decision?}

## Decision
{What is the change that we're proposing/doing?}

## Consequences
{What becomes easier or more difficult because of this change?}

### Positive
- ...

### Negative
- ...

### Neutral
- ...

## Alternatives Considered
{What other options were considered?}

## References
- ...
```
```

---

## 9. Troubleshooting Prompts

### 9.1 🟢 Debug Agent Failures

```markdown
# PROMPT: Debug Agent Not Returning Results

## Problem
{Agent type} agent is not returning results for certain locations.

## Debug Checklist
1. Check API key configuration
2. Verify rate limits not exceeded
3. Check timeout settings
4. Review retry logs
5. Verify profile restrictions

## Debug Code
```python
import logging
logging.getLogger("agents").setLevel(logging.DEBUG)

# Run with verbose output
result = agent.execute(
    point=problematic_point,
    profile=user_profile
)

# Check logs for:
# - API call attempts
# - Response parsing
# - Score calculation
```

## Common Issues
| Symptom | Cause | Solution |
|---------|-------|----------|
| Always None | is_driver=True | Check profile |
| Timeout | API slow | Increase timeout |
| Low scores | Bad query | Review search terms |
```

### 9.2 🟢 Queue Timeout Issues

```markdown
# PROMPT: Debug Queue Timeout Problems

## Problem
Queue frequently hitting soft/hard timeout.

## Analysis
```python
# Check queue metrics
metrics = queue.wait_for_results()[1]
print(f"Status: {metrics.status}")
print(f"Wait time: {metrics.wait_time_ms}ms")
print(f"Succeeded: {metrics.agents_succeeded}")
print(f"Failed: {metrics.agents_failed}")
```

## Solutions
| Issue | Solution |
|-------|----------|
| One agent always slow | Increase that agent's timeout |
| All agents slow | Check API rate limits |
| Frequent failures | Add more retry attempts |
| Network issues | Add circuit breaker |
```

---

## 10. Advanced Extension Prompts

### 10.1 🔴 Create New Agent Plugin

```markdown
# PROMPT: Create Weather Agent Plugin

## Capacity
You are a plugin developer extending the agent system.

## Request
Create a new Weather Agent as a plugin.

## Directory Structure
```
plugins/weather/
├── __init__.py
├── plugin.yaml
├── agent.py
└── requirements.txt
```

## Plugin Manifest (plugin.yaml)
```yaml
name: weather
version: 1.0.0
description: Weather forecasts for route points
author: Your Name

capabilities:
  - CONTENT_PROVIDER

dependencies:
  - openweathermap-api>=1.0

config:
  api_key_env: WEATHER_API_KEY
  cache_ttl: 3600
```

## Agent Implementation
```python
from src.core.plugins.base import ContentProviderPlugin
from src.core.plugins.registry import PluginRegistry

@PluginRegistry.register("weather")
class WeatherPlugin(ContentProviderPlugin):
    def _on_start(self):
        self.api = WeatherAPI(self.config.api_key)
    
    def search_content(self, location: str, context: dict) -> dict:
        weather = self.api.get_forecast(location)
        advice = self._generate_advice(weather)
        return {
            "type": "text",
            "content": advice,
            "metadata": {"temperature": weather.temp}
        }
```

## Registration
No code changes needed! Enable in config:
```yaml
plugins:
  - type: weather
    enabled: true
```
```

### 10.2 🔴 Add Caching Layer

```markdown
# PROMPT: Implement Redis Caching for Agents

## Capacity
You are a performance engineer optimizing API usage.

## Request
Add a caching layer to reduce API calls by 90%+.

## Cache Implementation
```python
class AgentCache:
    def __init__(self, ttl_seconds=3600, redis_url="redis://localhost:6379"):
        self.redis = redis.Redis.from_url(redis_url)
        self.ttl = ttl_seconds
    
    def _get_key(self, agent_type: str, location: str, profile_hash: str) -> str:
        data = f"{agent_type}:{location}:{profile_hash}"
        return hashlib.md5(data.encode()).hexdigest()
    
    def get(self, agent_type: str, location: str, profile: UserProfile) -> Optional[ContentResult]:
        key = self._get_key(agent_type, location, profile.cache_key)
        data = self.redis.get(key)
        if data:
            logger.info(f"Cache HIT: {agent_type} @ {location}")
            return ContentResult.model_validate_json(data)
        return None
    
    def set(self, agent_type: str, location: str, profile: UserProfile, result: ContentResult):
        key = self._get_key(agent_type, location, profile.cache_key)
        self.redis.setex(key, self.ttl, result.model_dump_json())
```

## Integration with BaseAgent
```python
class BaseAgent(ABC):
    def execute(self, point: RoutePoint, profile: UserProfile, queue: SmartQueue):
        # Check cache first
        cached = self.cache.get(self.agent_type, point.address, profile)
        if cached:
            queue.submit_success(self.agent_type, cached)
            return
        
        # Search and cache
        result = self._search_content(point, profile)
        if result:
            self.cache.set(self.agent_type, point.address, profile, result)
            queue.submit_success(self.agent_type, result)
```
```

---

## 11. Prompt Templates Library

### 11.1 Generic Feature Prompt

```markdown
# PROMPT: Implement {FEATURE_NAME}

## Capacity
You are a {ROLE} implementing {DOMAIN} functionality.

## Request
{CLEAR_TASK_DESCRIPTION}

## Information
### Context
{BACKGROUND_INFORMATION}

### Requirements
{LIST_OF_REQUIREMENTS}

### Constraints
{LIMITATIONS_AND_BOUNDARIES}

## Style
### Output Format
{EXPECTED_OUTPUT_FORMAT}

### Code Style
- Python 3.10+
- Type hints required
- Docstrings (Google style)
- Error handling

## Examples
### Input
{SAMPLE_INPUT}

### Expected Output
{SAMPLE_OUTPUT}

## Edge Cases
{EDGE_CASES_TO_HANDLE}
```

### 11.2 Bug Fix Prompt

```markdown
# PROMPT: Fix Bug in {COMPONENT}

## Problem Description
{DESCRIBE_THE_BUG}

## Steps to Reproduce
1. {STEP_1}
2. {STEP_2}
3. {STEP_3}

## Expected Behavior
{WHAT_SHOULD_HAPPEN}

## Actual Behavior
{WHAT_ACTUALLY_HAPPENS}

## Relevant Code
```python
{CODE_SNIPPET}
```

## Error Messages
```
{ERROR_OUTPUT}
```

## Request
1. Identify root cause
2. Propose fix
3. Add test to prevent regression
```

### 11.3 Code Review Prompt

```markdown
# PROMPT: Review Code for {COMPONENT}

## Capacity
You are a senior engineer performing code review for MIT-level quality.

## Request
Review the following code for:
1. Correctness
2. Performance
3. Security
4. Maintainability
5. Test coverage

## Code to Review
```python
{CODE}
```

## Review Criteria
- [ ] No bugs or logic errors
- [ ] Efficient algorithms (O(?) complexity)
- [ ] No security vulnerabilities
- [ ] Clear naming and structure
- [ ] Adequate error handling
- [ ] Sufficient documentation
- [ ] Test coverage > 85%

## Output Format
### Issues Found
| Severity | Line | Issue | Suggestion |
|----------|------|-------|------------|
| HIGH | ... | ... | ... |

### Positive Aspects
- ...

### Recommendations
- ...
```

---

## 📚 Quick Reference Card

### Prompt Selection Guide

| Need | Section | Level |
|------|---------|-------|
| Start new project | 3.1 | 🔴 |
| Design architecture | 3.2 | 🔴 |
| Create data models | 3.3 | 🟡 |
| Build agent | 4.x | 🟡 |
| Add queue/orchestration | 5.x | 🔴 |
| Write tests | 6.x | 🟡 |
| Run analysis | 7.x | 🔬 |
| Write docs | 8.x | 🟢 |
| Debug issues | 9.x | 🟢 |
| Add extensions | 10.x | 🔴 |

### LLM Recommendations

| Prompt Type | Best LLM | Why |
|-------------|----------|-----|
| Architecture | Claude 3.5 | Long-form reasoning |
| Code Generation | GPT-4 | Code quality |
| Research | Claude 3.5 | Academic rigor |
| Quick Tasks | GPT-4-mini | Speed + cost |

---

**Document Version:** 2.0.0  
**Last Updated:** November 2025  
**Maintainer:** Multi-Agent Tour Guide Team  
**License:** MIT

