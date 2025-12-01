# 🔑 Complete API Keys Setup Guide

## How to Get All API Keys and Run Real Flows

---

## 📋 Quick Overview

| API Key | Required? | Purpose | Cost |
|---------|-----------|---------|------|
| **Anthropic Claude** | ✅ Required | Judge Agent LLM | ~$3/1M tokens |
| **Google Maps** | ⭐ Recommended | Real route generation | Free tier: 200$/month |
| **YouTube Data** | Optional | Real video search | Free: 10,000 units/day |
| **Spotify** | Optional | Real music search | Free |

---

## 1️⃣ Anthropic Claude API Key (REQUIRED for Real LLM)

### What It Does
- Powers the **Judge Agent** to intelligently select the best content
- Generates contextual explanations for content selection

### How to Get It

1. **Go to:** [console.anthropic.com](https://console.anthropic.com/)

2. **Sign Up / Log In:**
   - Click "Sign Up" if you don't have an account
   - Verify your email

3. **Get API Key:**
   - Go to **Settings** → **API Keys**
   - Click **"Create Key"**
   - Copy the key (starts with `sk-ant-...`)

4. **Add to `.env`:**
   ```bash
   ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

### Pricing
- **Free credits:** $5 for new accounts
- **Pay-as-you-go:** ~$3 per 1M input tokens, ~$15 per 1M output tokens
- **For this project:** ~$0.01 per tour (very cheap!)

---

## 2️⃣ Google Maps API Key (RECOMMENDED for Real Routes)

### What It Does
- Generates **real driving routes** between locations
- Provides accurate waypoints with addresses and coordinates
- Calculates real distances and durations

### How to Get It

1. **Go to:** [console.cloud.google.com](https://console.cloud.google.com/)

2. **Create Project:**
   - Click "Select a project" → "New Project"
   - Name: `multi-agent-tour-guide`
   - Click "Create"

3. **Enable APIs:**
   - Go to **APIs & Services** → **Library**
   - Search and enable:
     - ✅ **Directions API**
     - ✅ **Geocoding API**
     - ✅ **Places API**

4. **Create API Key:**
   - Go to **APIs & Services** → **Credentials**
   - Click **"+ CREATE CREDENTIALS"** → **"API Key"**
   - Copy the key (starts with `AIza...`)

5. **Add to `.env`:**
   ```bash
   GOOGLE_MAPS_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXX
   ```

### Pricing
- **Free tier:** $200/month credit (covers ~40,000 requests)
- **Directions API:** $5 per 1,000 requests
- **For this project:** FREE for normal usage

### Security (Optional but Recommended)
- Go to **Credentials** → Click your API Key
- Under "API restrictions" → Select "Restrict key"
- Choose: Directions API, Geocoding API, Places API

---

## 3️⃣ YouTube Data API Key (OPTIONAL for Real Videos)

### What It Does
- Searches for **real YouTube videos** related to locations
- Gets video thumbnails, durations, and descriptions

### How to Get It

1. **Go to:** [console.cloud.google.com](https://console.cloud.google.com/)

2. **Enable API:**
   - Go to **APIs & Services** → **Library**
   - Search: "YouTube Data API v3"
   - Click **Enable**

3. **Create API Key:**
   - Go to **APIs & Services** → **Credentials**
   - Click **"+ CREATE CREDENTIALS"** → **"API Key"**
   - (You can use same key as Google Maps or create separate)

4. **Add to `.env`:**
   ```bash
   YOUTUBE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXX
   ```

### Pricing
- **Free:** 10,000 units/day
- **Search costs:** 100 units per search
- **For this project:** FREE (100 searches/day)

---

## 4️⃣ Spotify API Credentials (OPTIONAL for Real Music)

### What It Does
- Searches for **real Spotify tracks** related to locations
- Gets album art, artist info, preview URLs

### How to Get It

1. **Go to:** [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)

2. **Log In:**
   - Use your Spotify account (free or premium)

3. **Create App:**
   - Click **"Create App"**
   - App name: `Multi-Agent Tour Guide`
   - App description: `Tour guide content system`
   - Redirect URI: `http://localhost:8000/callback`
   - Click **Create**

4. **Get Credentials:**
   - Click your app
   - Go to **Settings**
   - Copy **Client ID** and **Client Secret**

5. **Add to `.env`:**
   ```bash
   SPOTIFY_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   SPOTIFY_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

### Pricing
- **Free:** Unlimited for development
- No cost for search API

---

## 📁 Complete `.env` File

Create your `.env` file with all keys:

```bash
# ═══════════════════════════════════════════════════════════════════════════════
# MULTI-AGENT TOUR GUIDE SYSTEM - FULL API CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────────────
# 🤖 LLM PROVIDER (REQUIRED for real Judge Agent)
# ─────────────────────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# Alternative: OpenAI (if you prefer GPT)
# OPENAI_API_KEY=sk-proj-your-key-here

# ─────────────────────────────────────────────────────────────────────────────────
# 🗺️ GOOGLE MAPS API (RECOMMENDED for real routes)
# ─────────────────────────────────────────────────────────────────────────────────
GOOGLE_MAPS_API_KEY=AIzaSyYour-Google-Maps-Key-Here

# ─────────────────────────────────────────────────────────────────────────────────
# 🎬 YOUTUBE DATA API (OPTIONAL for real video search)
# ─────────────────────────────────────────────────────────────────────────────────
YOUTUBE_API_KEY=AIzaSyYour-YouTube-Key-Here

# ─────────────────────────────────────────────────────────────────────────────────
# 🎵 SPOTIFY API (OPTIONAL for real music search)
# ─────────────────────────────────────────────────────────────────────────────────
SPOTIFY_CLIENT_ID=your-spotify-client-id
SPOTIFY_CLIENT_SECRET=your-spotify-client-secret

# ─────────────────────────────────────────────────────────────────────────────────
# ⚙️ SYSTEM CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────────
LOG_LEVEL=INFO
LLM_PROVIDER=anthropic
LLM_MODEL=claude-sonnet-4-20250514
LLM_TEMPERATURE=0.7
AGENT_TIMEOUT_SECONDS=30
```

---

## 🚀 Running Real Flows

### Flow 1: Full Real Flow (All APIs)

With all API keys configured:

```bash
# Real route from Paris to Lyon
uv run python main.py --origin "Paris, France" --destination "Lyon, France" --mode queue

# Real route in Israel
uv run python main.py --origin "Tel Aviv" --destination "Jerusalem" --mode queue

# Real route in USA
uv run python main.py --origin "New York" --destination "Boston" --mode queue
```

**Expected Output:**
```
📍 Route: Paris, France → Lyon, France (12 points)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 [1/12] Paris - Eiffel Tower Area
   ✅ Video Agent: "Paris Travel Guide" (YouTube)
   ✅ Music Agent: "La Vie en Rose" (Spotify)
   ✅ Text Agent: "History of Paris" (Wikipedia)
   🏆 Winner: 🎬 VIDEO - "Paris Travel Guide"
   📊 Scores: VIDEO=9.2 | MUSIC=7.5 | TEXT=8.1
```

---

### Flow 2: Real Routes Only (Google Maps)

Only with Google Maps API key:

```bash
# Set only Google Maps key
ANTHROPIC_API_KEY=  # empty - will use mock
GOOGLE_MAPS_API_KEY=AIzaSy...  # your key

# Run - real route, mock content
uv run python main.py --origin "London" --destination "Manchester" --mode queue
```

---

### Flow 3: Real LLM Only (Anthropic)

Only with Anthropic API key:

```bash
# Set only Anthropic key
ANTHROPIC_API_KEY=sk-ant-...  # your key
GOOGLE_MAPS_API_KEY=  # empty - will use mock route

# Run - mock route, real LLM Judge
make run-queue
```

---

### Flow 4: Family Mode (Real)

```bash
uv run python main.py \
  --origin "Disneyland, California" \
  --destination "San Diego Zoo" \
  --mode queue \
  --profile family \
  --min-age 5
```

---

### Flow 5: Driver Mode (Audio Only)

```bash
uv run python main.py \
  --origin "San Francisco" \
  --destination "Los Angeles" \
  --mode queue \
  --profile driver
```

---

### Flow 6: Streaming Mode (Real-Time Simulation)

```bash
uv run python main.py \
  --origin "Rome, Italy" \
  --destination "Florence, Italy" \
  --mode streaming \
  --interval 10
```

---

## 📊 API Cost Estimation

### Per Tour (4 points):

| API | Calls | Cost |
|-----|-------|------|
| Google Maps Directions | 1 | $0.005 |
| Google Maps Geocoding | 4 | $0.02 |
| YouTube Search | 4 | FREE |
| Spotify Search | 4 | FREE |
| Anthropic Claude | 4 | $0.01 |
| **Total** | | **~$0.035** |

### Monthly (100 tours/month):
- **Total:** ~$3.50/month
- **Google Maps Free Tier:** $200 credit = ~5,700 tours FREE

---

## ✅ Verification Checklist

Run these commands to verify your setup:

```bash
# 1. Check environment variables are set
cat .env | grep -v "^#" | grep -v "^$"

# 2. Test the system
uv run python -c "
from src.utils.config import settings
print('Anthropic Key:', 'SET' if settings.anthropic_api_key else 'NOT SET')
print('Google Maps Key:', 'SET' if settings.google_maps_api_key else 'NOT SET')
print('YouTube Key:', 'SET' if settings.youtube_api_key else 'NOT SET')
"

# 3. Run full pipeline
uv run python main.py --origin "Tel Aviv" --destination "Jerusalem" --mode queue
```

---

## 🔧 Troubleshooting

### "No LLM API key configured"
```bash
# Check your .env file has:
ANTHROPIC_API_KEY=sk-ant-...
# Make sure there are no quotes around the key
```

### "Google Maps API key is required"
```bash
# For demo mode, use --demo flag:
make run-queue  # Uses mock automatically

# Or set the key in .env:
GOOGLE_MAPS_API_KEY=AIza...
```

### "Rate limit exceeded"
```bash
# YouTube has daily limits (10,000 units)
# Wait 24 hours or use mock mode
```

---

## 📚 Quick Reference Links

| Service | Console | Documentation |
|---------|---------|---------------|
| **Anthropic** | [console.anthropic.com](https://console.anthropic.com/) | [docs.anthropic.com](https://docs.anthropic.com/) |
| **Google Cloud** | [console.cloud.google.com](https://console.cloud.google.com/) | [developers.google.com/maps](https://developers.google.com/maps) |
| **YouTube API** | Same as Google Cloud | [developers.google.com/youtube](https://developers.google.com/youtube/v3) |
| **Spotify** | [developer.spotify.com](https://developer.spotify.com/dashboard) | [developer.spotify.com/docs](https://developer.spotify.com/documentation/web-api) |

---

**Document Version:** 1.0.0  
**Last Updated:** December 2025

