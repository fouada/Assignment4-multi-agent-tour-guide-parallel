# 📚 API Reference

## Multi-Agent Tour Guide System

---

<div align="center">

**Version:** 2.0.0  
**Last Updated:** November 2024  
**Format:** REST + CLI

</div>

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [CLI Interface](#cli-interface)
4. [REST API](#rest-api)
5. [Data Models](#data-models)
6. [Error Handling](#error-handling)
7. [Rate Limiting](#rate-limiting)
8. [Webhooks](#webhooks)
9. [SDK Examples](#sdk-examples)

---

## Overview

### Base URL

```
Production: https://api.tourguide.example.com/v1
Development: http://localhost:8000/api/v1
```

### Response Format

All responses are JSON with the following structure:

```json
{
  "status": "success|error",
  "data": { ... },
  "meta": {
    "request_id": "req_abc123",
    "processing_time_ms": 2340
  }
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Invalid API key |
| 404 | Not Found |
| 429 | Too Many Requests - Rate limited |
| 500 | Server Error |
| 503 | Service Unavailable |

---

## Authentication

### API Key Authentication

Include your API key in the request header:

```http
Authorization: Bearer your-api-key-here
```

### Environment Variables

```bash
# For CLI usage
export TOUR_GUIDE_API_KEY=your-api-key-here
```

---

## CLI Interface

### Installation

```bash
# Install with UV
uv sync

# Or install globally
pip install multi-agent-tour-guide
```

### Basic Commands

#### `tour-guide` - Main Command

```bash
tour-guide [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--origin`, `-o` | STRING | Required* | Starting location |
| `--destination`, `-d` | STRING | Required* | Ending location |
| `--demo` | FLAG | False | Use demo mode with mock data |
| `--mode` | CHOICE | "queue" | Processing mode |
| `--profile` | CHOICE | "default" | User profile preset |
| `--interactive` | FLAG | False | Interactive setup |
| `--verbose`, `-v` | FLAG | False | Enable debug logging |
| `--output`, `-o` | PATH | stdout | Output file path |
| `--format` | CHOICE | "text" | Output format (text/json) |

**Mode Options:**
- `queue` - Queue-based synchronization (recommended)
- `streaming` - Real-time point processing
- `instant` - All points in parallel
- `sequential` - One point at a time (debugging)

**Profile Options:**
- `default` - General adult user
- `family` - Family with kids
- `history` - History enthusiast
- `teen` - Teenager
- `senior` - Senior citizen
- `business` - Business traveler
- `driver` - Driver (no video content)

### Usage Examples

```bash
# Basic demo run
tour-guide --demo --mode queue

# Custom route
tour-guide --origin "Paris, France" --destination "Lyon, France"

# Family-friendly with young children
tour-guide --demo --profile family --min-age 5

# History enthusiast mode
tour-guide --origin "Rome" --destination "Florence" --profile history

# Driver mode (audio only)
tour-guide --demo --profile driver

# Export to JSON
tour-guide --demo --format json --output tour.json

# Interactive setup
tour-guide --interactive

# Verbose debugging
tour-guide --demo --verbose
```

### Output Formats

#### Text Output (Default)

```
╔══════════════════════════════════════════════════════════════╗
║   🗺️  MULTI-AGENT TOUR GUIDE SYSTEM  🗺️                      ║
╚══════════════════════════════════════════════════════════════╝

📍 Route: Tel Aviv → Jerusalem
   Points: 4 | Profile: family

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 [1/4] Latrun
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏆 Winner: 🎵 MUSIC
   Title: Jerusalem of Gold
   Artist: Naomi Shemer
   URL: https://open.spotify.com/track/...
   
💭 Reason: Perfect family-friendly song for the journey
   Score: 9.2/10

[Processing: 2.3s | Agents: 3/3]
```

#### JSON Output

```json
{
  "tour_id": "tour_abc123",
  "route": {
    "source": "Tel Aviv, Israel",
    "destination": "Jerusalem, Israel"
  },
  "profile": {
    "age_group": "adult",
    "audience_type": "family_with_kids",
    "min_age": 5
  },
  "points": [
    {
      "index": 1,
      "name": "Latrun",
      "address": "Latrun, Israel",
      "decision": {
        "content_type": "music",
        "title": "Jerusalem of Gold",
        "url": "https://open.spotify.com/track/...",
        "score": 9.2,
        "reasoning": "Perfect family-friendly song..."
      },
      "metrics": {
        "agents_responded": 3,
        "processing_time_ms": 2340,
        "queue_status": "complete"
      }
    }
  ],
  "summary": {
    "total_points": 4,
    "successful_decisions": 4,
    "content_distribution": {
      "video": 1,
      "music": 2,
      "text": 1
    },
    "average_processing_time_ms": 2100
  }
}
```

---

## REST API

### Tours

#### Create Tour

Create a new tour guide session.

```http
POST /api/v1/tours
Content-Type: application/json
Authorization: Bearer {api_key}
```

**Request Body:**

```json
{
  "source": "Tel Aviv, Israel",
  "destination": "Jerusalem, Israel",
  "profile": {
    "age_group": "adult",
    "audience_type": "family_with_kids",
    "min_age": 5,
    "interests": ["history", "culture"],
    "content_preference": "educational",
    "exclude_topics": ["violence"],
    "language": "en"
  },
  "options": {
    "mode": "queue",
    "streaming": false,
    "max_points": 10
  }
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "tour_id": "tour_abc123",
    "status": "processing",
    "created_at": "2024-11-29T10:30:00Z",
    "estimated_completion": "2024-11-29T10:31:00Z",
    "route": {
      "source": "Tel Aviv, Israel",
      "destination": "Jerusalem, Israel",
      "points_count": 4
    }
  },
  "meta": {
    "request_id": "req_xyz789",
    "processing_time_ms": 150
  }
}
```

---

#### Get Tour

Retrieve tour details and status.

```http
GET /api/v1/tours/{tour_id}
Authorization: Bearer {api_key}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "tour_id": "tour_abc123",
    "status": "completed",
    "created_at": "2024-11-29T10:30:00Z",
    "completed_at": "2024-11-29T10:30:45Z",
    "route": {
      "source": "Tel Aviv, Israel",
      "destination": "Jerusalem, Israel"
    },
    "progress": {
      "total_points": 4,
      "completed_points": 4,
      "percentage": 100
    }
  }
}
```

---

#### Get Tour Results

Retrieve the complete tour playlist.

```http
GET /api/v1/tours/{tour_id}/results
Authorization: Bearer {api_key}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "tour_id": "tour_abc123",
    "playlist": [
      {
        "point_index": 1,
        "point_name": "Latrun",
        "coordinates": {
          "lat": 31.8389,
          "lng": 34.9825
        },
        "decision": {
          "content_type": "music",
          "title": "Jerusalem of Gold",
          "description": "Iconic Israeli song by Naomi Shemer",
          "url": "https://open.spotify.com/track/...",
          "source": "Spotify",
          "score": 9.2,
          "reasoning": "Family-friendly song capturing the journey spirit"
        },
        "alternatives": [
          {
            "content_type": "video",
            "title": "Latrun Tank Museum",
            "score": 7.8
          },
          {
            "content_type": "text",
            "title": "Battle of Latrun",
            "score": 6.5
          }
        ],
        "metrics": {
          "agents_responded": 3,
          "queue_status": "complete",
          "processing_time_ms": 2340
        }
      }
    ],
    "summary": {
      "total_points": 4,
      "successful_decisions": 4,
      "content_distribution": {
        "video": 1,
        "music": 2,
        "text": 1
      }
    }
  }
}
```

---

#### Cancel Tour

Cancel an in-progress tour.

```http
DELETE /api/v1/tours/{tour_id}
Authorization: Bearer {api_key}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "tour_id": "tour_abc123",
    "status": "cancelled",
    "cancelled_at": "2024-11-29T10:30:30Z"
  }
}
```

---

### Streaming API

#### Stream Tour Updates

Real-time updates via WebSocket.

```
WebSocket: wss://api.tourguide.example.com/v1/tours/{tour_id}/stream
```

**Event Types:**

```json
// Point processing started
{
  "event": "point_started",
  "point_index": 1,
  "point_name": "Latrun",
  "timestamp": "2024-11-29T10:30:10Z"
}

// Agent completed
{
  "event": "agent_completed",
  "point_index": 1,
  "agent_type": "video",
  "title": "Latrun Tank Museum",
  "score": 7.8,
  "timestamp": "2024-11-29T10:30:15Z"
}

// Queue ready
{
  "event": "queue_ready",
  "point_index": 1,
  "agents_count": 3,
  "status": "complete",
  "timestamp": "2024-11-29T10:30:18Z"
}

// Decision made
{
  "event": "decision_made",
  "point_index": 1,
  "winner": {
    "content_type": "music",
    "title": "Jerusalem of Gold",
    "score": 9.2
  },
  "timestamp": "2024-11-29T10:30:20Z"
}

// Tour completed
{
  "event": "tour_completed",
  "tour_id": "tour_abc123",
  "total_points": 4,
  "timestamp": "2024-11-29T10:30:45Z"
}
```

---

### Profiles

#### List Profile Presets

Get available profile presets.

```http
GET /api/v1/profiles/presets
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "presets": [
      {
        "id": "default",
        "name": "Default Adult",
        "description": "General adult user with no specific preferences",
        "settings": {
          "age_group": "adult",
          "content_preference": "no_preference"
        }
      },
      {
        "id": "family",
        "name": "Family with Kids",
        "description": "Family-friendly content for traveling with children",
        "settings": {
          "audience_type": "family_with_kids",
          "content_rating": "family",
          "exclude_topics": ["violence", "adult_content"]
        }
      },
      {
        "id": "history",
        "name": "History Enthusiast",
        "description": "In-depth historical content",
        "settings": {
          "content_preference": "historical",
          "content_depth": "in_depth",
          "interests": ["history", "archaeology", "culture"]
        }
      }
    ]
  }
}
```

---

### Health & Status

#### Health Check

```http
GET /api/v1/health
```

**Response:**

```json
{
  "status": "healthy",
  "version": "2.0.0",
  "uptime_seconds": 86400,
  "checks": {
    "database": "healthy",
    "cache": "healthy",
    "llm_provider": "healthy",
    "agents": {
      "video": "healthy",
      "music": "healthy",
      "text": "healthy",
      "judge": "healthy"
    }
  }
}
```

#### Readiness Check

```http
GET /api/v1/ready
```

**Response:**

```json
{
  "ready": true,
  "message": "Service is ready to accept requests"
}
```

#### Metrics

```http
GET /api/v1/metrics
```

**Response (Prometheus Format):**

```
# HELP tour_requests_total Total number of tour requests
# TYPE tour_requests_total counter
tour_requests_total{status="success"} 1234
tour_requests_total{status="error"} 12

# HELP agent_response_time_seconds Agent response time in seconds
# TYPE agent_response_time_seconds histogram
agent_response_time_seconds_bucket{agent="video",le="1.0"} 500
agent_response_time_seconds_bucket{agent="video",le="2.0"} 900
agent_response_time_seconds_bucket{agent="video",le="5.0"} 1200

# HELP queue_status Queue completion status
# TYPE queue_status counter
queue_status{status="complete"} 1100
queue_status{status="soft_degraded"} 100
queue_status{status="hard_degraded"} 10
```

---

## Data Models

### UserProfile

Complete user profile for personalization.

```python
class UserProfile:
    # Demographics
    name: Optional[str]
    age_group: AgeGroup  # kid, teenager, young_adult, adult, senior
    gender: Gender  # male, female, not_specified
    language: LanguagePreference  # en, he, ar, etc.
    
    # Travel Context
    travel_mode: TravelMode  # car, bus, train, walking
    trip_purpose: TripPurpose  # vacation, business, education
    travel_pace: TravelPace  # rushed, normal, leisurely
    is_driver: bool
    
    # Audience
    audience_type: AudienceType  # adults_only, family_with_kids, teens
    min_age: Optional[int]
    
    # Content Preferences
    content_preference: ContentPreference  # educational, entertainment, historical
    content_depth: ContentDepth  # quick_facts, summary, detailed
    max_content_duration_seconds: Optional[int]
    
    # Interests
    interests: List[str]  # ["history", "nature", "food"]
    music_genres: List[MusicGenre]
    exclude_topics: List[str]
    
    # Accessibility
    accessibility_needs: List[AccessibilityNeed]
    requires_subtitles: bool
```

### ContentResult

Result from a content agent.

```python
class ContentResult:
    point_id: str
    content_type: ContentType  # video, music, text
    title: str
    description: Optional[str]
    url: Optional[str]
    source: str  # YouTube, Spotify, Wikipedia
    relevance_score: float  # 0.0 - 10.0
    duration_seconds: Optional[int]
    metadata: Dict[str, Any]
    found_at: datetime
```

### JudgeDecision

Judge's final decision.

```python
class JudgeDecision:
    point_id: str
    selected_content: ContentResult
    all_candidates: List[ContentResult]
    reasoning: str
    scores: Dict[ContentType, float]
    profile_weights_applied: Dict[str, float]
    decided_at: datetime
```

### RoutePoint

A point along the route.

```python
class RoutePoint:
    id: str
    index: int
    address: str
    location_name: Optional[str]
    coordinates: Coordinates
    estimated_arrival: Optional[datetime]
    distance_from_start_km: float
```

### TourGuideOutput

Complete tour output.

```python
class TourGuideOutput:
    tour_id: str
    route: Route
    profile: UserProfile
    decisions: List[JudgeDecision]
    statistics: TourStatistics
    created_at: datetime
    processing_time_seconds: float
```

---

## Error Handling

### Error Response Format

```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "profile.min_age",
        "message": "Must be a positive integer"
      }
    ]
  },
  "meta": {
    "request_id": "req_xyz789"
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid input data |
| `AUTHENTICATION_ERROR` | 401 | Invalid or missing API key |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `AGENT_TIMEOUT` | 500 | Agent failed to respond |
| `LLM_ERROR` | 500 | LLM provider error |
| `INTERNAL_ERROR` | 500 | Unexpected error |

### Retry Strategy

For transient errors (5xx), implement exponential backoff:

```python
import time

def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except TransientError:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
```

---

## Rate Limiting

### Limits

| Tier | Requests/Minute | Concurrent Tours |
|------|-----------------|------------------|
| Free | 10 | 1 |
| Basic | 60 | 5 |
| Pro | 300 | 25 |
| Enterprise | Custom | Custom |

### Rate Limit Headers

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1701234567
```

---

## Webhooks

### Configuration

Register webhooks via API:

```http
POST /api/v1/webhooks
Content-Type: application/json

{
  "url": "https://your-server.com/webhook",
  "events": ["tour.completed", "tour.failed"],
  "secret": "your-webhook-secret"
}
```

### Event Payloads

#### tour.completed

```json
{
  "event": "tour.completed",
  "tour_id": "tour_abc123",
  "timestamp": "2024-11-29T10:30:45Z",
  "data": {
    "total_points": 4,
    "successful_decisions": 4,
    "processing_time_seconds": 45
  }
}
```

#### tour.failed

```json
{
  "event": "tour.failed",
  "tour_id": "tour_abc123",
  "timestamp": "2024-11-29T10:30:45Z",
  "error": {
    "code": "AGENT_TIMEOUT",
    "message": "All agents failed to respond"
  }
}
```

### Signature Verification

```python
import hmac
import hashlib

def verify_webhook(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

---

## SDK Examples

### Python

```python
from tour_guide import TourGuideClient, UserProfile

# Initialize client
client = TourGuideClient(api_key="your-api-key")

# Create profile
profile = UserProfile(
    age_group="adult",
    audience_type="family_with_kids",
    min_age=5,
    interests=["history", "nature"]
)

# Create tour
tour = client.create_tour(
    source="Tel Aviv",
    destination="Jerusalem",
    profile=profile
)

# Wait for completion
results = tour.wait_for_results(timeout=120)

# Process results
for point in results.playlist:
    print(f"{point.name}: {point.decision.title}")
```

### Async Python

```python
import asyncio
from tour_guide import AsyncTourGuideClient

async def main():
    async with AsyncTourGuideClient(api_key="your-api-key") as client:
        # Stream updates
        async for event in client.stream_tour("tour_abc123"):
            print(f"Event: {event.type}")
            if event.type == "decision_made":
                print(f"  Winner: {event.winner.title}")

asyncio.run(main())
```

### JavaScript/TypeScript

```typescript
import { TourGuideClient, UserProfile } from '@tour-guide/sdk';

const client = new TourGuideClient({ apiKey: 'your-api-key' });

const profile: UserProfile = {
  ageGroup: 'adult',
  audienceType: 'family_with_kids',
  minAge: 5,
  interests: ['history', 'nature']
};

// Create and stream tour
const tour = await client.createTour({
  source: 'Tel Aviv',
  destination: 'Jerusalem',
  profile
});

for await (const event of tour.stream()) {
  console.log(`Event: ${event.type}`);
}
```

### cURL

```bash
# Create tour
curl -X POST https://api.tourguide.example.com/v1/tours \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "Tel Aviv, Israel",
    "destination": "Jerusalem, Israel",
    "profile": {
      "age_group": "adult",
      "interests": ["history"]
    }
  }'

# Get results
curl https://api.tourguide.example.com/v1/tours/tour_abc123/results \
  -H "Authorization: Bearer your-api-key"
```

---

## Changelog

### v2.0.0 (November 2024)

- Added user profile personalization
- Added plugin architecture
- Added queue-based synchronization
- Added graceful degradation
- Added streaming API

### v1.0.0 (October 2024)

- Initial release
- Basic multi-agent system
- CLI interface

---

<div align="center">

**API Version:** 2.0.0  
**Last Updated:** November 2024

[Report Issues](https://github.com/yourusername/multi-agent-tour-guide/issues) •
[Request Features](https://github.com/yourusername/multi-agent-tour-guide/discussions)

</div>

