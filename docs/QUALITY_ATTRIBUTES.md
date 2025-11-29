# Quality Attributes Analysis

## ISO/IEC 25010:2011 Compliant Quality Framework

> **📋 Full Compliance:** This document aligns with ISO/IEC 25010:2011 Systems and Software Quality Requirements and Evaluation (SQuaRE).  
> See [ISO_IEC_25010_COMPLIANCE.md](./ISO_IEC_25010_COMPLIANCE.md) for complete compliance mapping.

---

### ISO/IEC 25010 Mapping

| Quality Attribute | ISO/IEC 25010 Characteristic | Sub-Characteristic |
|-------------------|------------------------------|-------------------|
| Fault Tolerance | Reliability | Fault Tolerance |
| Error Handling | Reliability | Recoverability |
| Scalability | Performance Efficiency | Capacity |
| Extensibility | Maintainability | Modifiability |

---

## Fault Tolerance, Error Handling, Scalability & Extensibility

---

## 1. Fault Tolerance

### Current Status: ⚠️ Partial Support

**What we have:**
- Mock clients as fallback when APIs unavailable
- Try/catch in agent execution

**What's missing:**
- No retry mechanism for failed API calls
- No circuit breaker pattern
- Single agent failure can block the queue
- No graceful degradation strategy

### Proposed Improvements

#### 1.1 Retry Mechanism

```python
from tenacity import retry, stop_after_attempt, wait_exponential

class BaseAgent:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def _call_api(self, endpoint, params):
        """API call with automatic retry"""
        return requests.get(endpoint, params=params)
```

#### 1.2 Timeout Protection

```python
from concurrent.futures import TimeoutError

def execute_with_timeout(agent, point, timeout=30):
    """Execute agent with timeout protection"""
    future = executor.submit(agent.execute, point)
    try:
        return future.result(timeout=timeout)
    except TimeoutError:
        logger.warning(f"Agent {agent.name} timed out for point {point.id}")
        return agent.get_fallback_result(point)
```

#### 1.3 Queue Timeout (Already Implemented)

```python
class AgentResultQueue:
    def wait_until_ready(self, timeout: float = 30.0) -> bool:
        """Wait with timeout - doesn't block forever"""
        ready = self._ready_event.wait(timeout=timeout)
        if not ready:
            # Proceed with partial results instead of failing
            logger.warning("Queue timeout - proceeding with partial results")
            self._status = QueueStatus.READY
        return ready
```

#### 1.4 Graceful Degradation Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    DEGRADATION LEVELS                        │
├─────────────────────────────────────────────────────────────┤
│ Level 0: All agents succeed → Judge picks best              │
│ Level 1: 2/3 agents succeed → Judge picks from available    │
│ Level 2: 1/3 agents succeed → Use that result               │
│ Level 3: 0/3 agents succeed → Use cached/default content    │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Error Handling

### Current Status: ⚠️ Basic Support

**What we have:**
- Try/catch in main execution paths
- Logging of errors
- Return None on failure

**What's missing:**
- No structured error types
- No error aggregation
- No user-friendly error messages
- No error recovery strategies

### Proposed Improvements

#### 2.1 Custom Exception Hierarchy

```python
# errors.py

class TourGuideError(Exception):
    """Base exception for Tour Guide system"""
    pass

class AgentError(TourGuideError):
    """Base exception for agent errors"""
    def __init__(self, agent_type: str, point_id: str, message: str):
        self.agent_type = agent_type
        self.point_id = point_id
        super().__init__(f"[{agent_type}][Point:{point_id}] {message}")

class APIError(AgentError):
    """External API failure"""
    pass

class TimeoutError(AgentError):
    """Operation timed out"""
    pass

class ContentNotFoundError(AgentError):
    """No content found for location"""
    pass

class QueueError(TourGuideError):
    """Queue synchronization error"""
    pass

class ConfigurationError(TourGuideError):
    """Configuration/setup error"""
    pass
```

#### 2.2 Error Result Pattern

```python
from dataclasses import dataclass
from typing import Union, Optional

@dataclass
class Success:
    value: ContentResult

@dataclass  
class Failure:
    error: AgentError
    fallback: Optional[ContentResult] = None

Result = Union[Success, Failure]

class BaseAgent:
    def execute_safe(self, point: RoutePoint) -> Result:
        """Execute with structured result"""
        try:
            result = self._search_content(point)
            if result:
                return Success(result)
            else:
                return Failure(
                    ContentNotFoundError(self.agent_type, point.id, "No content found"),
                    fallback=self._get_fallback(point)
                )
        except Exception as e:
            return Failure(
                APIError(self.agent_type, point.id, str(e)),
                fallback=self._get_fallback(point)
            )
```

#### 2.3 Error Aggregation in Queue

```python
class AgentResultQueue:
    def __init__(self, point: RoutePoint):
        self._results: Dict[ContentType, ContentResult] = {}
        self._errors: Dict[ContentType, AgentError] = {}  # NEW
    
    def submit_error(self, content_type: ContentType, error: AgentError):
        """Record an agent failure"""
        self._errors[content_type] = error
        self._check_ready()  # May still be ready if have enough results
    
    def get_status_report(self) -> dict:
        """Get detailed status including errors"""
        return {
            'successful': list(self._results.keys()),
            'failed': list(self._errors.keys()),
            'errors': {k.value: str(v) for k, v in self._errors.items()}
        }
```

---

## 3. Scalability

### Current Status: ⚠️ Limited Support

**What we have:**
- ThreadPoolExecutor with configurable size
- Can process multiple points in parallel

**What's missing:**
- No rate limiting for external APIs
- No connection pooling
- No caching layer
- Memory grows with concurrent points
- No distributed processing support

### Proposed Improvements

#### 3.1 Rate Limiting

```python
from ratelimit import limits, sleep_and_retry

class YouTubeClient:
    # YouTube API: 10,000 units/day, ~100 search requests
    @sleep_and_retry
    @limits(calls=100, period=86400)  # 100 calls per day
    def search(self, query: str):
        return self._api.search().list(q=query, ...)
```

#### 3.2 Caching Layer

```python
from functools import lru_cache
from cachetools import TTLCache
import hashlib

class CachedContentSearch:
    """Cache layer for expensive API calls"""
    
    def __init__(self, ttl_seconds=3600):  # 1 hour cache
        self._cache = TTLCache(maxsize=1000, ttl=ttl_seconds)
    
    def _cache_key(self, location: str, content_type: str) -> str:
        return hashlib.md5(f"{location}:{content_type}".encode()).hexdigest()
    
    def get_or_search(self, location: str, content_type: str, search_func):
        key = self._cache_key(location, content_type)
        if key in self._cache:
            logger.info(f"Cache HIT for {location}")
            return self._cache[key]
        
        result = search_func(location)
        self._cache[key] = result
        return result
```

#### 3.3 Connection Pooling

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session_with_retry():
    """Create HTTP session with connection pooling and retry"""
    session = requests.Session()
    
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    
    adapter = HTTPAdapter(
        pool_connections=10,
        pool_maxsize=20,
        max_retries=retry_strategy
    )
    
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session
```

#### 3.4 Scalability Limits Configuration

```python
# config.py

class ScalabilityConfig:
    # Thread pool limits
    MAX_CONCURRENT_POINTS = 5      # Points processed simultaneously
    MAX_AGENTS_PER_POINT = 3       # Video, Music, Text
    MAX_TOTAL_THREADS = 20         # Hard limit
    
    # API rate limits
    YOUTUBE_CALLS_PER_DAY = 100
    GOOGLE_MAPS_CALLS_PER_DAY = 1000
    
    # Timeouts
    AGENT_TIMEOUT_SECONDS = 30
    QUEUE_TIMEOUT_SECONDS = 60
    
    # Cache
    CACHE_TTL_SECONDS = 3600
    CACHE_MAX_SIZE = 1000
```

#### 3.5 Backpressure Mechanism

```python
class Orchestrator:
    def __init__(self, max_concurrent: int = 5):
        self._semaphore = threading.Semaphore(max_concurrent)
        self._queue_depth = 0
    
    def process_point(self, point: RoutePoint):
        """Process with backpressure"""
        if not self._semaphore.acquire(timeout=5):
            logger.warning("System overloaded - delaying point processing")
            time.sleep(1)  # Backpressure
        
        try:
            self._do_process(point)
        finally:
            self._semaphore.release()
```

---

## 4. Extensibility

### Current Status: ✅ Good Support

**What we have:**
- Abstract base class for agents
- YAML configuration for agent behavior
- Plugin-style agent design

**Could be better:**
- No plugin discovery mechanism
- No runtime agent registration
- Content types are hardcoded enum

### Current Good Patterns

#### 4.1 Base Agent Pattern (Already Have)

```python
class BaseAgent(ABC):
    @abstractmethod
    def _search_content(self, point: RoutePoint) -> Optional[ContentResult]:
        pass
    
    @abstractmethod
    def get_content_type(self) -> ContentType:
        pass
```

To add a new agent (e.g., PodcastAgent):
1. Create `podcast_agent.py`
2. Extend `BaseAgent`
3. Implement required methods
4. Register in orchestrator

#### 4.2 YAML Configuration (Already Have)

Agents behavior is externalized to YAML:
```yaml
# Easy to modify without code changes
skills:
  - name: "YouTube Search"
    criteria:
      - "Relevance to location"
      - "Duration (2-15 min)"  # Can change this!
```

### Proposed Improvements

#### 4.3 Plugin Registry Pattern

```python
# agent_registry.py

class AgentRegistry:
    """Registry for dynamically adding new agent types"""
    
    _agents: Dict[str, Type[BaseAgent]] = {}
    
    @classmethod
    def register(cls, content_type: str):
        """Decorator to register new agent types"""
        def decorator(agent_class: Type[BaseAgent]):
            cls._agents[content_type] = agent_class
            return agent_class
        return decorator
    
    @classmethod
    def get_agent(cls, content_type: str) -> BaseAgent:
        if content_type not in cls._agents:
            raise ValueError(f"Unknown agent type: {content_type}")
        return cls._agents[content_type]()
    
    @classmethod
    def list_agents(cls) -> List[str]:
        return list(cls._agents.keys())

# Usage:
@AgentRegistry.register("video")
class VideoAgent(BaseAgent):
    ...

@AgentRegistry.register("podcast")  # Easy to add new!
class PodcastAgent(BaseAgent):
    ...
```

#### 4.4 Dynamic Content Types

```python
# Instead of hardcoded enum:
class ContentType(str, Enum):
    VIDEO = "video"
    MUSIC = "music"
    TEXT = "text"

# Use dynamic registration:
class ContentTypeRegistry:
    _types: Set[str] = set()
    
    @classmethod
    def register(cls, name: str):
        cls._types.add(name)
    
    @classmethod
    def is_valid(cls, name: str) -> bool:
        return name in cls._types
```

#### 4.5 Configurable Agent Pipeline

```yaml
# pipeline.yaml - Define which agents run
pipeline:
  agents:
    - type: video
      enabled: true
      weight: 1.0
    - type: music
      enabled: true
      weight: 1.0
    - type: text
      enabled: true
      weight: 0.8
    - type: podcast    # New agent type!
      enabled: false   # Disabled for now
      weight: 0.5
```

```python
class ConfigurablePipeline:
    def __init__(self, config_path: str):
        self.config = yaml.safe_load(open(config_path))
    
    def get_active_agents(self) -> List[BaseAgent]:
        """Return only enabled agents"""
        return [
            AgentRegistry.get_agent(a['type'])
            for a in self.config['pipeline']['agents']
            if a['enabled']
        ]
```

---

## 5. Summary Matrix

| Quality | Current | Proposed | Priority |
|---------|---------|----------|----------|
| **Fault Tolerance** | ⚠️ Basic | ✅ Full | HIGH |
| - Retry mechanism | ❌ | ✅ | HIGH |
| - Timeout protection | ✅ | ✅ | - |
| - Graceful degradation | ⚠️ | ✅ | MEDIUM |
| - Circuit breaker | ❌ | ✅ | LOW |
| **Error Handling** | ⚠️ Basic | ✅ Full | HIGH |
| - Custom exceptions | ❌ | ✅ | MEDIUM |
| - Result pattern | ❌ | ✅ | MEDIUM |
| - Error aggregation | ❌ | ✅ | LOW |
| **Scalability** | ⚠️ Limited | ✅ Good | MEDIUM |
| - Rate limiting | ❌ | ✅ | HIGH |
| - Caching | ❌ | ✅ | MEDIUM |
| - Connection pooling | ❌ | ✅ | LOW |
| - Backpressure | ❌ | ✅ | LOW |
| **Extensibility** | ✅ Good | ✅ Excellent | LOW |
| - Base class pattern | ✅ | ✅ | - |
| - YAML configuration | ✅ | ✅ | - |
| - Plugin registry | ❌ | ✅ | LOW |
| - Dynamic pipeline | ❌ | ✅ | LOW |

---

## 6. Implementation Priority

### Phase 1: Critical (For Assignment)
1. ✅ Basic timeout in queue (already done)
2. Add retry mechanism to agents
3. Add graceful degradation (2/3 agents enough)

### Phase 2: Important (Production Ready)
4. Custom exception hierarchy
5. Rate limiting for APIs
6. Caching layer

### Phase 3: Nice to Have (Advanced)
7. Circuit breaker pattern
8. Plugin registry
9. Distributed processing

---

## 7. Quick Wins to Implement Now

### 7.1 Add Retry to Base Agent

```python
# In base_agent.py
MAX_RETRIES = 3

def execute(self, point: RoutePoint) -> Optional[ContentResult]:
    for attempt in range(MAX_RETRIES):
        try:
            result = self._search_content(point)
            if result:
                return result
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                logger.warning(f"Attempt {attempt+1} failed, retrying...")
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                logger.error(f"All {MAX_RETRIES} attempts failed")
    return self._get_fallback_result(point)
```

### 7.2 Graceful Queue Degradation

```python
# In agent_queue.py
MIN_REQUIRED_AGENTS = 2  # Can proceed with 2/3

def is_ready(self) -> bool:
    # Ready if all submitted OR enough for degraded mode
    return (len(self._results) >= self.EXPECTED_AGENTS or 
            len(self._results) >= MIN_REQUIRED_AGENTS)
```

### 7.3 Simple Cache

```python
# In config.py
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_search(location: str, content_type: str) -> ContentResult:
    # Results cached for identical requests
    pass
```

---

*This document should be reviewed and updated as the system evolves.*

