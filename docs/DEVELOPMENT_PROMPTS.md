# 🛠️ Development Prompts Library
## Prompts for Building Multi-Agent Systems

This document contains **copy-paste ready prompts** for developing each component of the Multi-Agent Tour Guide System. Use these with any LLM (Claude, GPT-4, etc.) to generate code.

---

## Table of Contents

1. [Project Setup Prompts](#1-project-setup-prompts)
2. [Agent Development Prompts](#2-agent-development-prompts)
3. [Orchestration Prompts](#3-orchestration-prompts)
4. [Testing Prompts](#4-testing-prompts)
5. [Extension Prompts](#5-extension-prompts)

---

## 1. Project Setup Prompts

### 1.1 Create Project Structure

```
PROMPT: Create Python Project Structure for Multi-Agent System

Create a production-ready Python project structure for a multi-agent AI system with:

REQUIREMENTS:
1. Modular architecture with separate packages for:
   - agents/ (AI agents)
   - docs/ (documentation)
   - tests/ (test files)
   - plugins/ (future extensions)

2. Configuration:
   - YAML files for agent configs (agents/configs/*.yaml)
   - Python config.py for system settings
   - Support for .env files for API keys

3. Core files:
   - main.py (entry point with CLI arguments)
   - models.py (Pydantic data models)
   - logger_setup.py (colored logging with Rich)
   - requirements.txt (with pinned versions)

4. Documentation:
   - README.md with quick start
   - docs/ARCHITECTURE.md
   - Inline docstrings (Google style)

OUTPUT: Complete directory structure with empty __init__.py files and basic boilerplate.
```

### 1.2 Create Data Models

```
PROMPT: Create Pydantic Data Models for Tour Guide System

Create Pydantic v2 data models for a tour guide system:

MODELS NEEDED:

1. RoutePoint:
   - id: str
   - index: int
   - address: str
   - latitude: float
   - longitude: float
   - location_name: Optional[str]
   - estimated_arrival_seconds: Optional[int]

2. ContentResult:
   - content_type: Enum (VIDEO, MUSIC, TEXT)
   - title: str
   - description: str
   - url: str
   - source: str
   - relevance_score: float (0-10)
   - duration_seconds: Optional[int]
   - metadata: Dict[str, Any]

3. JudgeDecision:
   - point_id: str
   - selected_content: ContentResult
   - all_candidates: List[ContentResult]
   - reasoning: str
   - scores: Dict[ContentType, float]

4. TourGuideResult:
   - route_summary: str
   - points: List[PointResult]
   - statistics: Dict[str, Any]

REQUIREMENTS:
- Use Pydantic v2 syntax (model_validator, Field)
- Add JSON schema examples
- Include serialization methods
- Support optional fields with defaults
```

### 1.3 Create User Profile Model

```
PROMPT: Create Comprehensive User Profile for Personalization

Create a Pydantic model for user profiles with these categories:

DEMOGRAPHICS:
- name, gender, age_group, exact_age, language

TRAVEL CONTEXT:
- travel_mode (car/bus/walking)
- trip_purpose (vacation/business/romantic/education)
- travel_pace (rushed/normal/leisurely)
- is_driver: bool (CRITICAL: affects video recommendations)
- social_context (solo/couple/family/friends)

CONTENT PREFERENCES:
- content_preference (educational/entertainment/historical)
- content_depth (quick_facts/summary/detailed/in_depth)
- max_duration_seconds
- music_genres: List[MusicGenre]
- interests: List[str]

ACCESSIBILITY:
- accessibility_needs: List[AccessibilityNeed]
- requires_subtitles: bool
- prefer_audio_description: bool

EXCLUSIONS:
- exclude_topics: List[str]

METHODS TO INCLUDE:
1. to_agent_context() -> str  # For agent prompts
2. to_judge_criteria() -> str  # For judge evaluation
3. get_content_type_preferences() -> Dict[str, float]  # Scoring weights

PRESET PROFILES:
- get_kid_profile(age)
- get_teenager_profile()
- get_senior_profile()
- get_family_profile(min_age)
- get_driver_profile()  # NO VIDEO
- get_accessibility_visual_profile()
```

---

## 2. Agent Development Prompts

### 2.1 Create Base Agent Class

```
PROMPT: Create Abstract Base Agent for Multi-Agent System

Create an abstract base class for AI agents with:

CLASS: BaseAgent(ABC)

CONSTRUCTOR:
- agent_type: str
- Load YAML configuration from agents/configs/{agent_type}_agent.yaml
- Initialize LLM client (OpenAI API compatible)

ABSTRACT METHODS:
- get_content_type() -> ContentType
- _search_content(point: RoutePoint) -> Optional[ContentResult]

CONCRETE METHODS:
- execute(point: RoutePoint) -> Optional[ContentResult]
  - Wraps _search_content with retry logic
  - 3 retries with exponential backoff (1s, 2s, 4s)
  - Logs success/failure

- _call_llm(prompt: str) -> str
  - Calls OpenAI-compatible API
  - Uses config for model, temperature, max_tokens
  - Handles errors gracefully

- _load_config(agent_type: str) -> Dict
  - Loads YAML from agents/configs/
  - Returns agent configuration

YAML CONFIG STRUCTURE:
```yaml
agent:
  name: "Agent Name"
  version: "1.0.0"
  description: "What this agent does"

config:
  model: "gpt-4o-mini"
  temperature: 0.7
  max_tokens: 1000

skills:
  - name: "skill_name"
    description: "What skill does"
    search_strategy: "How to search"

scoring_criteria:
  - "Criterion 1"
  - "Criterion 2"
```

REQUIREMENTS:
- Thread-safe (agents run in parallel)
- Proper error handling
- Detailed logging
```

### 2.2 Create Video Agent

```
PROMPT: Create Video Agent for YouTube Search

Create VideoAgent extending BaseAgent:

PURPOSE:
Find relevant YouTube videos for travel locations.

SEARCH STRATEGY:
1. Build search queries:
   - "{location_name} documentary"
   - "{location_name} history"
   - "{location_name} travel guide"
   
2. Filter results:
   - Duration < user.max_duration (if specified)
   - Language matches user preference
   - Family-friendly if age_group is KID

3. CRITICAL CHECK:
   - If user.is_driver == True: Return None immediately
   - Drivers cannot watch videos!

LLM PROMPT TEMPLATE:
```
You are a video content curator for travelers.

Location: {location_name}
Address: {address}
User Profile: {user_context}

Find the most relevant YouTube video for this location.

Consider:
1. Educational value
2. Entertainment quality
3. Relevance to location
4. Appropriateness for user

Return in JSON format:
{
  "title": "...",
  "description": "...",
  "url": "https://youtube.com/...",
  "relevance_score": 8.5,
  "reasoning": "Why this video"
}
```

MOCK MODE:
- If no YouTube API key, return mock data
- Mock videos should be realistic

OUTPUT:
ContentResult with content_type=VIDEO
```

### 2.3 Create Music Agent

```
PROMPT: Create Music Agent for Song Search

Create MusicAgent extending BaseAgent:

PURPOSE:
Find relevant songs/music for travel locations.

SEARCH STRATEGY:
1. Search for songs about the location
2. Match user's music genre preferences
3. Consider artist preferences
4. Match energy level (calming vs upbeat)

SOURCES (priority order):
1. Spotify API (if available)
2. YouTube Music (fallback)
3. LLM-generated recommendations

USER PROFILE INTEGRATION:
- music_genres: Filter by preferred genres
- favorite_artists: Boost songs by these artists
- energy_level: LOW → calming, HIGH → upbeat
- trip_purpose: ROMANTIC → love songs

LLM PROMPT TEMPLATE:
```
You are a music curator for travelers.

Location: {location_name}
User Music Preferences: {music_context}

Find a song that:
1. Relates to this location (about the place, by local artist, or captures the mood)
2. Matches user's music taste
3. Fits the travel mood

Return in JSON format:
{
  "title": "Song Title",
  "artist": "Artist Name",
  "description": "Why this song fits",
  "url": "https://...",
  "genre": "...",
  "relevance_score": 7.5
}
```

MOCK MODE:
- Return location-appropriate mock songs
- Include variety of genres
```

### 2.4 Create Text Agent

```
PROMPT: Create Text Agent for Facts/Stories

Create TextAgent extending BaseAgent:

PURPOSE:
Find interesting facts, stories, and information about travel locations.

CONTENT TYPES:
1. Historical facts and events
2. Cultural significance
3. Famous people connections
4. Architectural features
5. Local legends
6. Fun/surprising facts

SOURCES:
1. Wikipedia API
2. LLM knowledge generation
3. Local knowledge bases

ADAPTATION BY USER PROFILE:
- age_group=KID: Simple language, fun facts
- age_group=TEENAGER: Interesting/surprising facts
- age_group=SENIOR: Historical, nostalgic content
- knowledge_level=expert: Deep, detailed content
- content_preference=HISTORICAL: Focus on history

LLM PROMPT TEMPLATE:
```
You are a knowledgeable tour guide.

Location: {location_name}
Address: {address}
User Profile: {user_context}

Provide an interesting fact or story about this location.

Requirements:
1. Match content to user's age and interests
2. Be engaging and memorable
3. Be accurate and well-sourced
4. Keep length appropriate: {content_depth}

Return in JSON format:
{
  "title": "Fact/Story Title",
  "content": "The full text (2-3 paragraphs)",
  "fact_type": "historical|cultural|fun|scientific",
  "source": "Wikipedia/other",
  "relevance_score": 8.0
}
```
```

### 2.5 Create Judge Agent

```
PROMPT: Create Judge Agent for Content Selection

Create JudgeAgent extending BaseAgent:

PURPOSE:
Evaluate content from Video, Music, and Text agents.
Select the BEST content for a specific user at a specific location.

DECISION LOGIC:

CASE 1: 3 CANDIDATES
- Full LLM comparison
- Apply user profile weights
- Consider location appropriateness

CASE 2: 2 CANDIDATES
- Compare available options
- Note missing agent in reasoning
- Apply same scoring

CASE 3: 1 CANDIDATE
- Accept if appropriate
- Verify against user restrictions
- Note limited options

SCORING WEIGHTS BY PROFILE:
```python
def get_weights(profile):
    weights = {"video": 1.0, "music": 1.0, "text": 1.0}
    
    if profile.age_group == AgeGroup.KID:
        weights = {"video": 1.3, "music": 1.2, "text": 0.7}
    elif profile.age_group == AgeGroup.TEENAGER:
        weights = {"video": 1.2, "music": 1.4, "text": 0.6}
    elif profile.age_group == AgeGroup.SENIOR:
        weights = {"video": 0.9, "music": 1.2, "text": 1.3}
    
    if profile.is_driver:
        weights["video"] = 0.0  # CRITICAL: No video
        weights["music"] = 1.5
    
    if VISUAL_IMPAIRMENT in profile.accessibility_needs:
        weights["video"] = 0.3
        weights["music"] = 1.5
    
    return weights
```

LLM EVALUATION PROMPT:
```
You are a content curator selecting the BEST content for a specific user.

LOCATION: {location}
USER PROFILE: {profile_context}
USER CRITERIA: {criteria}

CANDIDATES:
{candidate_list}

Evaluate each candidate and select the BEST one for THIS USER.

Consider:
1. Location relevance
2. User age and preferences
3. Accessibility needs
4. Trip purpose

Response format:
SCORES:
- Video: [0-10]
- Music: [0-10]
- Text: [0-10]

WINNER: [1, 2, or 3]
WINNER_SCORE: [0-10]
REASONING: [Why this is best for THIS user]
```

METHODS:
- evaluate(point, candidates, user_profile) -> JudgeDecision
- quick_evaluate(point, candidates) -> ContentResult (no LLM)
```

---

## 3. Orchestration Prompts

### 3.1 Create Smart Queue

```
PROMPT: Create Smart Queue with Tiered Timeouts

Create SmartAgentQueue class:

PURPOSE:
Synchronize agent results with graceful degradation.

TIMEOUT STRATEGY:
- Wait for ALL 3 agents (ideal: 0-15s)
- After 15s: Accept 2/3 (soft degradation)
- After 30s: Accept 1/3 (hard degradation)
- If 0 agents: Raise error

CONFIGURATION:
```python
EXPECTED_AGENTS = 3
SOFT_TIMEOUT_SECONDS = 15.0
HARD_TIMEOUT_SECONDS = 30.0
MIN_REQUIRED_FOR_SOFT = 2
MIN_REQUIRED_FOR_HARD = 1
```

STATES (Enum):
- WAITING: Collecting results
- COMPLETE: All 3 responded
- SOFT_DEGRADED: 2/3 responded
- HARD_DEGRADED: 1/3 responded
- FAILED: 0 responded

METHODS:
1. submit_success(agent_type: str, result: ContentResult)
   - Store result
   - Log success
   - Notify waiting thread

2. submit_failure(agent_type: str, error: str)
   - Store failure
   - Log error
   - Notify waiting thread

3. wait_for_results() -> Tuple[List[ContentResult], QueueMetrics]
   - Block until ready
   - Return results and metrics

THREAD SAFETY:
- Use threading.Condition for synchronization
- Proper locking on shared state

METRICS:
- QueueMetrics dataclass with:
  - point_id, start_time, end_time
  - status, agents_expected, agents_received
  - agents_succeeded, agents_failed
  - wait_time_ms
```

### 3.2 Create Orchestrator

```
PROMPT: Create Thread Pool Orchestrator

Create TourOrchestrator class:

PURPOSE:
Manage parallel execution of agents for route points.

COMPONENTS:
- ThreadPoolExecutor for parallel agents
- SmartQueue for synchronization
- JudgeAgent for content selection
- Collector for result aggregation

EXECUTION FLOW:
```python
def process_point(point: RoutePoint, profile: UserProfile):
    queue = SmartQueue(point.id)
    
    # Spawn 3 agents in parallel
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(video_agent.execute, point, queue),
            executor.submit(music_agent.execute, point, queue),
            executor.submit(text_agent.execute, point, queue),
        ]
    
    # Wait for results (with timeout)
    results, metrics = queue.wait_for_results()
    
    # Judge selects best
    decision = judge.evaluate(point, results, profile)
    
    return decision
```

MODES:
1. SEQUENTIAL: Process one point at a time
2. PARALLEL: Process multiple points at once
3. STREAMING: Timer-based point emission

CONFIGURATION:
- max_workers_per_point: 3 (one per agent type)
- max_parallel_points: 2 (prevent overload)
- point_interval_seconds: 5 (for streaming mode)

ERROR HANDLING:
- Catch exceptions per agent
- Continue with other agents
- Log all errors
```

---

## 4. Testing Prompts

### 4.1 Unit Test Generation

```
PROMPT: Generate Unit Tests for Multi-Agent System

Generate pytest unit tests for:

1. USER PROFILE TESTS:
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

2. SMART QUEUE TESTS:
```python
def test_queue_waits_for_all_three():
    queue = SmartQueue("test")
    # Submit all 3
    queue.submit_success("video", mock_video)
    queue.submit_success("music", mock_music)
    queue.submit_success("text", mock_text)
    results, metrics = queue.wait_for_results()
    assert len(results) == 3
    assert metrics.status == QueueStatus.COMPLETE

def test_queue_soft_timeout():
    queue = SmartQueue("test")
    queue.SOFT_TIMEOUT_SECONDS = 0.1  # Fast timeout for test
    queue.submit_success("video", mock_video)
    queue.submit_success("music", mock_music)
    # Don't submit text
    results, metrics = queue.wait_for_results()
    assert len(results) == 2
    assert metrics.status == QueueStatus.SOFT_DEGRADED
```

3. JUDGE TESTS:
```python
def test_judge_single_candidate():
    judge = JudgeAgent()
    decision = judge.evaluate(mock_point, [mock_video])
    assert decision.selected_content == mock_video

def test_judge_respects_profile():
    profile = get_kid_profile()
    judge = JudgeAgent(profile)
    # Kid should prefer video over text
    decision = judge.evaluate(mock_point, [mock_video, mock_text], profile)
    assert decision.selected_content.content_type == ContentType.VIDEO
```

4. INTEGRATION TESTS:
```python
def test_full_pipeline_demo_mode():
    result = run_tour_guide(
        source="Tel Aviv",
        destination="Jerusalem",
        demo=True
    )
    assert result.points is not None
    assert len(result.points) > 0
```

FIXTURES:
- mock_point, mock_video, mock_music, mock_text
- mock_user_profiles for each type
```

---

## 5. Extension Prompts

### 5.1 Add New Agent Type

```
PROMPT: Create Weather Agent Plugin

Create a new agent plugin for weather information:

DIRECTORY STRUCTURE:
```
plugins/weather/
├── __init__.py
├── agent.py
├── config.yaml
└── requirements.txt
```

CONFIG FILE (config.yaml):
```yaml
agent:
  name: "Weather Agent"
  type: "weather"
  version: "1.0.0"
  description: "Provides weather forecasts for route points"

config:
  model: "gpt-4o-mini"
  temperature: 0.3
  max_tokens: 500

api:
  provider: "openweathermap"
  cache_ttl: 3600

skills:
  - name: "weather_forecast"
    description: "Get current weather and forecast"
```

AGENT CODE (agent.py):
```python
from agents.base_agent import BaseAgent
from agents.registry import AgentRegistry

@AgentRegistry.register("weather")
class WeatherAgent(BaseAgent):
    def __init__(self):
        super().__init__("weather")
        self.api_key = os.getenv("WEATHER_API_KEY")
    
    def get_content_type(self) -> ContentType:
        return ContentType.TEXT  # Weather is text-based
    
    def _search_content(self, point: RoutePoint) -> ContentResult:
        weather = self._get_weather(point.coordinates)
        advice = self._generate_advice(weather, point)
        return ContentResult(
            content_type=ContentType.TEXT,
            title=f"Weather at {point.location_name}",
            description=advice,
            metadata={"temperature": weather.temp}
        )
```

REGISTRATION:
No code changes needed! Just enable in config/agents.yaml:
```yaml
plugins:
  - type: weather
    enabled: true
```
```

### 5.2 Add Caching Layer

```
PROMPT: Add Redis Caching to Agents

Add a caching layer to reduce API calls:

CACHE IMPLEMENTATION:
```python
from functools import lru_cache
import redis
import hashlib
import json

class AgentCache:
    def __init__(self, ttl_seconds=3600):
        self.redis = redis.Redis(host='localhost', port=6379)
        self.ttl = ttl_seconds
    
    def get_key(self, agent_type: str, location: str) -> str:
        data = f"{agent_type}:{location}"
        return hashlib.md5(data.encode()).hexdigest()
    
    def get(self, agent_type: str, location: str) -> Optional[ContentResult]:
        key = self.get_key(agent_type, location)
        data = self.redis.get(key)
        if data:
            return ContentResult(**json.loads(data))
        return None
    
    def set(self, agent_type: str, location: str, result: ContentResult):
        key = self.get_key(agent_type, location)
        self.redis.setex(key, self.ttl, result.model_dump_json())
```

INTEGRATION WITH BASE AGENT:
```python
class BaseAgent(ABC):
    def __init__(self, agent_type: str):
        self.cache = AgentCache()
    
    def execute(self, point: RoutePoint) -> Optional[ContentResult]:
        # Check cache first
        cached = self.cache.get(self.agent_type, point.address)
        if cached:
            logger.info(f"[{self.agent_type}] Cache HIT for {point.address}")
            return cached
        
        # Search and cache
        result = self._search_content(point)
        if result:
            self.cache.set(self.agent_type, point.address, result)
        
        return result
```

BENEFITS:
- Reduce API calls by 90%+
- Faster response for repeated locations
- Lower costs
```

---

## How to Use These Prompts

### Step 1: Initial Setup
Copy the "Project Structure" and "Data Models" prompts to generate the foundation.

### Step 2: Core Development
Use agent prompts to generate each agent class.

### Step 3: Orchestration
Use queue and orchestrator prompts to wire everything together.

### Step 4: Testing
Use test prompts to generate comprehensive test suite.

### Step 5: Extensions
Use extension prompts to add new capabilities.

---

**These prompts are designed to be used with Claude, GPT-4, or any capable LLM to generate production-quality code for the Multi-Agent Tour Guide System.**

