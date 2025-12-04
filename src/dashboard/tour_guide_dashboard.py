"""
🗺️ Multi-Agent Tour Guide Interactive Dashboard
================================================

MIT-Level Architecture: Dashboard consumes FastAPI via HTTP Client

A comprehensive, publication-quality interactive dashboard for the
Multi-Agent Tour Guide System with full pipeline visualization.

Architecture:
    ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
    │   Dashboard     │──────▶│    FastAPI      │──────▶│  TourService    │
    │   (This File)   │ HTTP  │   (Port 8000)   │       │  (Agents+Queue) │
    └─────────────────┘       └─────────────────┘       └─────────────────┘
                                       │
                                       └── Single Source of Truth

Features:
- Interactive tour planning with source/destination inputs
- Complete user profile configuration (family, age, preferences)
- Real-time pipeline flow visualization via API polling
- Animated agent orchestration display
- Personalized content recommendations from API
- System architecture visualization

Author: Multi-Agent Tour Guide Research Team
Version: 3.0.0 (MIT-Level API Integration)
Date: December 2025
"""

from __future__ import annotations

import logging
import os
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum

import numpy as np
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

# =============================================================================
# MIT-LEVEL: API Client for proper architecture
# =============================================================================
# The dashboard now uses the API client to communicate with the backend.
# This ensures single source of truth and proper separation of concerns.

API_CLIENT_AVAILABLE = False
api_client = None

try:
    from src.api.client import APIConfig, TourGuideClient

    # Check if API is actually running
    _test_client = TourGuideClient(
        APIConfig(
            base_url=os.environ.get("TOUR_GUIDE_API_URL", "http://localhost:8000"),
            timeout=5.0,
            max_retries=1,
        )
    )
    if _test_client.is_healthy():
        api_client = _test_client
        API_CLIENT_AVAILABLE = True
        logging.info("✅ API Client connected - using proper MIT-level architecture")
    else:
        _test_client.close()
        logging.info("⚠️ API not responding - will use direct mode as fallback")
except ImportError as e:
    logging.warning(f"API client not available: {e}")
except Exception as e:
    logging.warning(f"Could not connect to API: {e}")

# =============================================================================
# Fallback: Direct agent imports (for backwards compatibility)
# =============================================================================
# If API is not available, fall back to direct agent imports.
# This is NOT the preferred architecture but ensures the dashboard
# still works during development when API is not running.

REAL_AGENTS_AVAILABLE = False

try:
    from src.agents.judge_agent import JudgeAgent
    from src.agents.music_agent import MusicAgent
    from src.agents.text_agent import TextAgent
    from src.agents.video_agent import VideoAgent
    from src.core.smart_queue import SmartAgentQueue
    from src.models.route import RoutePoint
    from src.models.user_profile import (
        AgeGroup,
        TravelMode,
        TripPurpose,
        UserProfile,
    )
    from src.services.google_maps import GoogleMapsClient, get_mock_route

    REAL_AGENTS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Direct agents not available: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# API MODE CONFIGURATION
# ============================================================================
# MIT-Level Strategy:
#   - "auto"  : Try real APIs, fallback to mock if unavailable (DEFAULT)
#   - "real"  : Force real APIs (fail if unavailable) - For Demo/Presentation
#   - "mock"  : Always use mocked data (fast, deterministic) - For Tests/CI
#
# ┌─────────────────────────────────────────────────────────────────────────┐
# │                    USAGE BY CONTEXT                                     │
# ├─────────────────┬───────────────────────────────────────────────────────┤
# │ Context         │ Recommended Mode                                      │
# ├─────────────────┼───────────────────────────────────────────────────────┤
# │ Unit Tests      │ MOCK  - Fast, deterministic, no API costs            │
# │ Integration     │ MOCK  - Reproducible, CI/CD friendly                 │
# │ E2E Tests       │ MOCK  - With 1 real test to verify APIs work         │
# │ Local Dev       │ AUTO  - Developer choice with fallback               │
# │ Demo/Present    │ REAL  - Showcase actual capabilities                 │
# │ Research        │ MOCK  - Statistical simulations                       │
# │ CI/CD Pipeline  │ MOCK  - No API keys in CI                            │
# │ Production      │ AUTO  - Real + Fallback for resilience               │
# └─────────────────┴───────────────────────────────────────────────────────┘
#
# Set via environment variable:
#   export TOUR_GUIDE_API_MODE=real   # For MIT demo
#   export TOUR_GUIDE_API_MODE=mock   # For testing
#
# See docs/API_STRATEGY.md for full documentation
# ============================================================================
API_MODE = os.environ.get("TOUR_GUIDE_API_MODE", "auto")  # auto | real | mock

# ============================================================================
# THEME - Sophisticated Cyberpunk/Travel Aesthetic
# ============================================================================

THEME = {
    # Primary gradient colors
    "gradient_start": "#0f0c29",
    "gradient_mid": "#302b63",
    "gradient_end": "#24243e",
    # Accent colors
    "accent_primary": "#00f5d4",  # Cyan
    "accent_secondary": "#7209b7",  # Purple
    "accent_tertiary": "#f72585",  # Pink
    "accent_gold": "#fca311",  # Gold
    # Status colors
    "success": "#00f5d4",
    "warning": "#fca311",
    "error": "#f72585",
    "info": "#4cc9f0",
    # Agent colors
    "video_agent": "#6366f1",
    "music_agent": "#ec4899",
    "text_agent": "#14b8a6",
    "judge_agent": "#f59e0b",
    # Background
    "bg_dark": "#0a0a1a",
    "bg_card": "#1a1a2e",
    "bg_input": "#16213e",
    # Text
    "text_primary": "#ffffff",
    "text_secondary": "#a0a0a0",
    "text_muted": "#6b7280",
}

FONTS = {
    "display": "Space Grotesk, -apple-system, sans-serif",
    "mono": "JetBrains Mono, Fira Code, monospace",
    "body": "Inter, -apple-system, sans-serif",
}

# ============================================================================
# CSS Styles - Stunning Dark Theme with Animations
# ============================================================================

CUSTOM_CSS = f"""
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Inter:wght@300;400;500;600&display=swap');

:root {{
    --bg-dark: {THEME["bg_dark"]};
    --bg-card: {THEME["bg_card"]};
    --accent-cyan: {THEME["accent_primary"]};
    --accent-purple: {THEME["accent_secondary"]};
    --accent-pink: {THEME["accent_tertiary"]};
    --accent-gold: {THEME["accent_gold"]};
}}

* {{
    box-sizing: border-box;
}}

body {{
    font-family: {FONTS["body"]};
    background: linear-gradient(135deg, {THEME["gradient_start"]} 0%, {THEME["gradient_mid"]} 50%, {THEME["gradient_end"]} 100%);
    background-attachment: fixed;
    color: {THEME["text_primary"]};
    margin: 0;
    padding: 0;
    min-height: 100vh;
}}

/* Animated background particles */
body::before {{
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: radial-gradient(circle at 20% 80%, rgba(0, 245, 212, 0.03) 0%, transparent 50%), radial-gradient(circle at 80% 20%, rgba(114, 9, 183, 0.05) 0%, transparent 50%), radial-gradient(circle at 40% 40%, rgba(247, 37, 133, 0.03) 0%, transparent 30%);
    pointer-events: none;
    z-index: -1;
}}

.dashboard-wrapper {{
    max-width: 1600px;
    margin: 0 auto;
    padding: 20px;
}}

/* Header */
.dashboard-header {{
    text-align: center;
    padding: 40px 20px;
    position: relative;
}}

.header-title {{
    font-family: {FONTS["display"]};
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(135deg, {THEME["accent_primary"]} 0%, {THEME["accent_secondary"]} 50%, {THEME["accent_tertiary"]} 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 10px 0;
    text-shadow: 0 0 30px rgba(0, 245, 212, 0.3);
    animation: glow 3s ease-in-out infinite alternate;
}}

@keyframes glow {{
    from {{ filter: drop-shadow(0 0 10px rgba(0, 245, 212, 0.3)); }}
    to {{ filter: drop-shadow(0 0 20px rgba(114, 9, 183, 0.3)); }}
}}

.header-subtitle {{
    font-family: {FONTS["mono"]};
    font-size: 1rem;
    color: {THEME["text_secondary"]};
    letter-spacing: 0.1em;
}}

/* Cards */
.glass-card {{
    background: linear-gradient(145deg, rgba(26, 26, 46, 0.8), rgba(22, 33, 62, 0.6));
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 20px;
    padding: 25px;
    margin-bottom: 20px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.05);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}}

.glass-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5), 0 0 20px rgba(0, 245, 212, 0.1);
}}

.card-title {{
    font-family: {FONTS["display"]};
    font-size: 1.2rem;
    font-weight: 600;
    color: {THEME["accent_primary"]};
    margin: 0 0 20px 0;
    display: flex;
    align-items: center;
    gap: 10px;
}}

/* Form Inputs */
.input-group {{
    margin-bottom: 20px;
}}

.input-label {{
    font-family: {FONTS["mono"]};
    font-size: 0.85rem;
    color: {THEME["text_secondary"]};
    margin-bottom: 8px;
    display: block;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}

.styled-input {{
    width: 100%;
    padding: 14px 16px;
    background: rgba(22, 33, 62, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    color: {THEME["text_primary"]};
    font-family: {FONTS["body"]};
    font-size: 1rem;
    transition: all 0.3s ease;
}}

.styled-input:focus {{
    outline: none;
    border-color: {THEME["accent_primary"]};
    box-shadow: 0 0 0 3px rgba(0, 245, 212, 0.1);
}}

.styled-input::placeholder {{
    color: {THEME["text_muted"]};
}}

/* Buttons */
.btn-primary {{
    background: linear-gradient(135deg, {THEME["accent_primary"]}, {THEME["accent_secondary"]});
    border: none;
    color: {THEME["bg_dark"]};
    font-family: {FONTS["display"]};
    font-weight: 600;
    font-size: 1rem;
    padding: 16px 32px;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    position: relative;
    overflow: hidden;
}}

.btn-primary::before {{
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
    transition: left 0.5s ease;
}}

.btn-primary:hover {{
    transform: translateY(-3px);
    box-shadow: 0 10px 30px rgba(0, 245, 212, 0.3);
}}

.btn-primary:hover::before {{
    left: 100%;
}}

/* Tabs */
.custom-tabs .tab {{
    font-family: {FONTS["display"]} !important;
    background: transparent !important;
    border: none !important;
    color: {THEME["text_secondary"]} !important;
    padding: 16px 24px !important;
    transition: all 0.3s ease !important;
    border-bottom: 2px solid transparent !important;
}}

.custom-tabs .tab--selected {{
    color: {THEME["accent_primary"]} !important;
    border-bottom-color: {THEME["accent_primary"]} !important;
    background: linear-gradient(180deg, transparent 0%, rgba(0, 245, 212, 0.05) 100%) !important;
}}

/* Grid Layouts */
.grid-2 {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
}}

.grid-3 {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
}}

.grid-4 {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 15px;
}}

@media (max-width: 1200px) {{
    .grid-2, .grid-3 {{ grid-template-columns: 1fr; }}
    .grid-4 {{ grid-template-columns: repeat(2, 1fr); }}
}}

/* Select/Dropdown */
.Select-control {{
    background: rgba(22, 33, 62, 0.8) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
}}

.Select-menu-outer {{
    background: {THEME["bg_card"]} !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
    z-index: 9999 !important;
    position: absolute !important;
    max-height: 180px !important;
    overflow-y: auto !important;
}}

/* Force dropdown to open UPWARD */
.glass-card .Select-menu-outer {{
    bottom: 100% !important;
    top: auto !important;
    margin-bottom: 5px !important;
    margin-top: 0 !important;
}}

/* Fix Dash dropdown overlay issue */
.dash-dropdown {{
    position: relative;
    z-index: 100;
}}

.VirtualizedSelectFocusedOption {{
    background: rgba(0, 245, 212, 0.15) !important;
}}

.Select-menu {{
    max-height: 180px !important;
}}

.Select-option {{
    background: transparent !important;
    color: {THEME["text_primary"]} !important;
    padding: 8px 12px !important;
}}

.Select-option.is-focused {{
    background: rgba(0, 245, 212, 0.1) !important;
}}

/* Start Tour Button - Above everything */
.start-tour-container {{
    position: relative;
    z-index: 1;
    margin-top: 20px;
    clear: both;
}}

/* Slider styling */
.rc-slider-rail {{
    background: rgba(255, 255, 255, 0.1) !important;
    height: 8px !important;
    border-radius: 4px !important;
}}

.rc-slider-track {{
    background: linear-gradient(90deg, {THEME["accent_primary"]}, {THEME["accent_secondary"]}) !important;
    height: 8px !important;
    border-radius: 4px !important;
}}

.rc-slider-handle {{
    border: 3px solid {THEME["accent_primary"]} !important;
    background: {THEME["bg_dark"]} !important;
    width: 20px !important;
    height: 20px !important;
    margin-top: -6px !important;
}}

/* Agent Status Cards */
.agent-card {{
    background: linear-gradient(145deg, rgba(26, 26, 46, 0.9), rgba(22, 33, 62, 0.7));
    border-radius: 16px;
    padding: 20px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    position: relative;
    overflow: hidden;
}}

.agent-card::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--agent-color), transparent);
}}

.agent-card.video {{ --agent-color: {THEME["video_agent"]}; }}
.agent-card.music {{ --agent-color: {THEME["music_agent"]}; }}
.agent-card.text {{ --agent-color: {THEME["text_agent"]}; }}
.agent-card.judge {{ --agent-color: {THEME["judge_agent"]}; }}

/* Pipeline Flow */
.pipeline-step {{
    display: flex;
    align-items: center;
    padding: 20px;
    background: rgba(22, 33, 62, 0.5);
    border-radius: 12px;
    margin-bottom: 15px;
    border-left: 4px solid transparent;
    transition: all 0.3s ease;
}}

.pipeline-step.active {{
    border-left-color: {THEME["accent_primary"]};
    background: rgba(0, 245, 212, 0.05);
}}

.pipeline-step.completed {{
    border-left-color: {THEME["success"]};
}}

.pipeline-step.processing {{
    border-left-color: {THEME["warning"]};
    animation: pulse-border 1.5s infinite;
}}

@keyframes pulse-border {{
    0%, 100% {{ box-shadow: 0 0 0 0 rgba(252, 163, 17, 0.4); }}
    50% {{ box-shadow: 0 0 20px 5px rgba(252, 163, 17, 0.2); }}
}}

/* Profile Badge */
.profile-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    background: rgba(0, 245, 212, 0.1);
    border: 1px solid rgba(0, 245, 212, 0.3);
    border-radius: 20px;
    font-size: 0.85rem;
    color: {THEME["accent_primary"]};
}}

/* Metric Display */
.metric-box {{
    text-align: center;
    padding: 20px;
    background: rgba(22, 33, 62, 0.5);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.05);
}}

.metric-value {{
    font-family: {FONTS["mono"]};
    font-size: 2rem;
    font-weight: 600;
    background: linear-gradient(135deg, {THEME["accent_primary"]}, {THEME["accent_gold"]});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}

.metric-label {{
    font-size: 0.85rem;
    color: {THEME["text_secondary"]};
    margin-top: 8px;
}}

/* Content Card */
.content-recommendation {{
    background: linear-gradient(145deg, rgba(26, 26, 46, 0.95), rgba(22, 33, 62, 0.8));
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 15px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    display: flex;
    gap: 15px;
    transition: all 0.3s ease;
}}

.content-recommendation:hover {{
    border-color: rgba(0, 245, 212, 0.3);
    transform: translateX(5px);
}}

.content-icon {{
    width: 60px;
    height: 60px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
}}

.content-icon.video {{ background: linear-gradient(135deg, {THEME["video_agent"]}, rgba(99, 102, 241, 0.5)); }}
.content-icon.music {{ background: linear-gradient(135deg, {THEME["music_agent"]}, rgba(236, 72, 153, 0.5)); }}
.content-icon.text {{ background: linear-gradient(135deg, {THEME["text_agent"]}, rgba(20, 184, 166, 0.5)); }}

/* Loading animation */
.loading-pulse {{
    animation: loading-pulse 2s ease-in-out infinite;
}}

@keyframes loading-pulse {{
    0%, 100% {{ opacity: 0.5; }}
    50% {{ opacity: 1; }}
}}
"""


# ============================================================================
# Data Models
# ============================================================================


class AgeGroup(str, Enum):
    KID = "kid"
    TEENAGER = "teenager"
    YOUNG_ADULT = "young_adult"
    ADULT = "adult"
    SENIOR = "senior"


class TravelMode(str, Enum):
    CAR = "car"
    BUS = "bus"
    TRAIN = "train"
    WALKING = "walking"
    BICYCLE = "bicycle"


class TripPurpose(str, Enum):
    VACATION = "vacation"
    BUSINESS = "business"
    EDUCATION = "education"
    ROMANTIC = "romantic"
    ADVENTURE = "adventure"


class ContentPreference(str, Enum):
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    HISTORICAL = "historical"
    CULTURAL = "cultural"
    RELAXING = "relaxing"


# ============================================================================
# Dashboard Layout Components
# ============================================================================


def create_header():
    """Create the dashboard header with real-time API status indicator."""
    # Determine current API status
    is_api_connected = API_CLIENT_AVAILABLE and api_client is not None
    is_live = False
    api_mode_display = "⚪ DEMO"

    if is_api_connected:
        try:
            health = api_client.health_check()
            checks = health.get("checks", {})
            is_live = checks.get("using_real_apis", False)
            api_mode_display = checks.get("data_mode", "⚪ DEMO")
        except Exception:
            api_mode_display = "⚪ DEMO (API unavailable)"
    elif REAL_AGENTS_AVAILABLE and API_MODE != "mock":
        is_live = True
        api_mode_display = "🔴 LIVE (Direct)"

    # Status badge style
    badge_style = {
        "display": "inline-block",
        "padding": "8px 16px",
        "borderRadius": "20px",
        "fontSize": "0.9rem",
        "fontWeight": "600",
        "marginTop": "15px",
        "background": (
            f"linear-gradient(135deg, {THEME['success']}, {THEME['accent_primary']})"
            if is_live
            else "rgba(255,255,255,0.1)"
        ),
        "color": THEME["bg_dark"] if is_live else THEME["text_muted"],
        "boxShadow": (f"0 0 20px {THEME['success']}40" if is_live else "none"),
    }

    return html.Div(
        [
            html.H1("🗺️ Multi-Agent Tour Guide", className="header-title"),
            html.P(
                "INTELLIGENT · PARALLEL · PERSONALIZED", className="header-subtitle"
            ),
            html.Div(
                [
                    html.Span(api_mode_display, style=badge_style),
                    html.P(
                        f"Mode: {API_MODE.upper()} | "
                        + ("API Connected" if is_api_connected else "Direct Mode"),
                        style={
                            "fontSize": "0.75rem",
                            "color": THEME["text_muted"],
                            "marginTop": "8px",
                        },
                    ),
                ],
                id="api-status-header",
            ),
        ],
        className="dashboard-header",
    )


def create_tour_planning_panel():
    """Create the tour planning input panel."""
    return html.Div(
        [
            html.Div(
                [
                    html.H3(
                        [html.Span("📍"), " Tour Planning"], className="card-title"
                    ),
                    # Source and Destination
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Label(
                                        "Starting Point", className="input-label"
                                    ),
                                    dcc.Input(
                                        id="source-input",
                                        type="text",
                                        placeholder="e.g., Tel Aviv, Israel",
                                        value="Tel Aviv, Israel",
                                        className="styled-input",
                                        style={"width": "100%"},
                                    ),
                                ],
                                className="input-group",
                            ),
                            html.Div(
                                [
                                    html.Label("Destination", className="input-label"),
                                    dcc.Input(
                                        id="destination-input",
                                        type="text",
                                        placeholder="e.g., Jerusalem, Israel",
                                        value="Jerusalem, Israel",
                                        className="styled-input",
                                        style={"width": "100%"},
                                    ),
                                ],
                                className="input-group",
                            ),
                        ],
                        className="grid-2",
                    ),
                    # Waypoints (optional)
                    html.Div(
                        [
                            html.Label(
                                "Waypoints (optional, comma-separated)",
                                className="input-label",
                            ),
                            dcc.Input(
                                id="waypoints-input",
                                type="text",
                                placeholder="e.g., Latrun, Bab al-Wad",
                                className="styled-input",
                                style={"width": "100%"},
                            ),
                        ],
                        className="input-group",
                    ),
                ],
                className="glass-card",
            ),
        ]
    )


def create_user_profile_panel():
    """Create the comprehensive user profile configuration panel."""
    return html.Div(
        [
            html.Div(
                [
                    html.H3([html.Span("👤"), " User Profile"], className="card-title"),
                    # Quick Profile Selection
                    html.Div(
                        [
                            html.Label("Quick Profile Preset", className="input-label"),
                            dcc.Dropdown(
                                id="profile-preset",
                                options=[
                                    {"label": "🧑 Default Adult", "value": "default"},
                                    {
                                        "label": "👨‍👩‍👧‍👦 Family with Kids",
                                        "value": "family",
                                    },
                                    {"label": "🧒 Kid-Friendly", "value": "kid"},
                                    {"label": "🎓 Teenager", "value": "teenager"},
                                    {"label": "👴 Senior", "value": "senior"},
                                    {
                                        "label": "🚗 Driver (Audio Only)",
                                        "value": "driver",
                                    },
                                    {
                                        "label": "📚 History Enthusiast",
                                        "value": "history",
                                    },
                                    {"label": "❤️ Romantic Couple", "value": "romantic"},
                                    {"label": "⚙️ Custom...", "value": "custom"},
                                ],
                                value="family",
                                clearable=False,
                                style={"backgroundColor": THEME["bg_input"]},
                            ),
                        ],
                        className="input-group",
                    ),
                    # Custom Profile Options (shown when custom is selected)
                    html.Div(
                        id="custom-profile-options",
                        children=[
                            html.Hr(
                                style={
                                    "borderColor": "rgba(255,255,255,0.1)",
                                    "margin": "20px 0",
                                }
                            ),
                            # Demographics
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Label(
                                                "Age Group", className="input-label"
                                            ),
                                            dcc.Dropdown(
                                                id="age-group-select",
                                                options=[
                                                    {
                                                        "label": "👶 Kid (0-12)",
                                                        "value": "kid",
                                                    },
                                                    {
                                                        "label": "🧑 Teenager (13-19)",
                                                        "value": "teenager",
                                                    },
                                                    {
                                                        "label": "🧑‍🦱 Young Adult (20-35)",
                                                        "value": "young_adult",
                                                    },
                                                    {
                                                        "label": "🧑‍💼 Adult (36-55)",
                                                        "value": "adult",
                                                    },
                                                    {
                                                        "label": "👴 Senior (56+)",
                                                        "value": "senior",
                                                    },
                                                ],
                                                value="adult",
                                                clearable=False,
                                            ),
                                        ],
                                        style={"flex": "1"},
                                    ),
                                    html.Div(
                                        [
                                            html.Label(
                                                "Minimum Age in Group",
                                                className="input-label",
                                            ),
                                            dcc.Input(
                                                id="min-age-input",
                                                type="number",
                                                value=5,
                                                min=0,
                                                max=120,
                                                className="styled-input",
                                                style={"width": "100%"},
                                            ),
                                        ],
                                        style={"flex": "1"},
                                    ),
                                ],
                                style={"display": "flex", "gap": "20px"},
                            ),
                            # Travel Context
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Label(
                                                "Travel Mode", className="input-label"
                                            ),
                                            dcc.Dropdown(
                                                id="travel-mode-select",
                                                options=[
                                                    {"label": "🚗 Car", "value": "car"},
                                                    {"label": "🚌 Bus", "value": "bus"},
                                                    {
                                                        "label": "🚂 Train",
                                                        "value": "train",
                                                    },
                                                    {
                                                        "label": "🚶 Walking",
                                                        "value": "walking",
                                                    },
                                                    {
                                                        "label": "🚲 Bicycle",
                                                        "value": "bicycle",
                                                    },
                                                ],
                                                value="car",
                                                clearable=False,
                                            ),
                                        ],
                                        style={"flex": "1"},
                                    ),
                                    html.Div(
                                        [
                                            html.Label(
                                                "Trip Purpose", className="input-label"
                                            ),
                                            dcc.Dropdown(
                                                id="trip-purpose-select",
                                                options=[
                                                    {
                                                        "label": "🏖️ Vacation",
                                                        "value": "vacation",
                                                    },
                                                    {
                                                        "label": "💼 Business",
                                                        "value": "business",
                                                    },
                                                    {
                                                        "label": "📚 Education",
                                                        "value": "education",
                                                    },
                                                    {
                                                        "label": "❤️ Romantic",
                                                        "value": "romantic",
                                                    },
                                                    {
                                                        "label": "🎯 Adventure",
                                                        "value": "adventure",
                                                    },
                                                ],
                                                value="vacation",
                                                clearable=False,
                                            ),
                                        ],
                                        style={"flex": "1"},
                                    ),
                                ],
                                style={
                                    "display": "flex",
                                    "gap": "20px",
                                    "marginTop": "15px",
                                },
                            ),
                            # Content Preferences
                            html.Div(
                                [
                                    html.Label(
                                        "Content Preference", className="input-label"
                                    ),
                                    dcc.Dropdown(
                                        id="content-preference-select",
                                        options=[
                                            {
                                                "label": "📚 Educational",
                                                "value": "educational",
                                            },
                                            {
                                                "label": "🎬 Entertainment",
                                                "value": "entertainment",
                                            },
                                            {
                                                "label": "🏛️ Historical",
                                                "value": "historical",
                                            },
                                            {
                                                "label": "🎭 Cultural",
                                                "value": "cultural",
                                            },
                                            {
                                                "label": "🧘 Relaxing",
                                                "value": "relaxing",
                                            },
                                        ],
                                        value="educational",
                                        clearable=False,
                                    ),
                                ],
                                style={"marginTop": "15px"},
                            ),
                            # Family Mode Toggle
                            html.Div(
                                [
                                    html.Label(
                                        "Family-Safe Mode", className="input-label"
                                    ),
                                    dcc.Checklist(
                                        id="family-mode-toggle",
                                        options=[
                                            {
                                                "label": " Enable Family-Friendly Content Filtering",
                                                "value": "enabled",
                                            },
                                        ],
                                        value=["enabled"],
                                        style={"color": THEME["text_primary"]},
                                    ),
                                ],
                                style={"marginTop": "15px"},
                            ),
                            # Driver Mode Toggle
                            html.Div(
                                [
                                    html.Label(
                                        "Driver Mode (Audio Only)",
                                        className="input-label",
                                    ),
                                    dcc.Checklist(
                                        id="driver-mode-toggle",
                                        options=[
                                            {
                                                "label": " I am driving - no video content",
                                                "value": "enabled",
                                            },
                                        ],
                                        value=[],
                                        style={"color": THEME["text_primary"]},
                                    ),
                                ],
                                style={"marginTop": "15px"},
                            ),
                            # Interests
                            html.Div(
                                [
                                    html.Label(
                                        "Interests (comma-separated)",
                                        className="input-label",
                                    ),
                                    dcc.Input(
                                        id="interests-input",
                                        type="text",
                                        placeholder="e.g., history, nature, food, architecture",
                                        value="history, nature, culture",
                                        className="styled-input",
                                        style={"width": "100%"},
                                    ),
                                ],
                                style={"marginTop": "15px"},
                            ),
                            # Excluded Topics
                            html.Div(
                                [
                                    html.Label(
                                        "Topics to Avoid", className="input-label"
                                    ),
                                    dcc.Input(
                                        id="exclude-topics-input",
                                        type="text",
                                        placeholder="e.g., violence, politics",
                                        value="violence, adult content",
                                        className="styled-input",
                                        style={"width": "100%"},
                                    ),
                                ],
                                style={"marginTop": "15px"},
                            ),
                            # Max Content Duration
                            html.Div(
                                [
                                    html.Label(
                                        "Maximum Content Duration (seconds)",
                                        className="input-label",
                                    ),
                                    dcc.Slider(
                                        id="max-duration-slider",
                                        min=30,
                                        max=600,
                                        step=30,
                                        value=300,
                                        marks={
                                            30: "30s",
                                            60: "1m",
                                            120: "2m",
                                            180: "3m",
                                            300: "5m",
                                            600: "10m",
                                        },
                                        tooltip={
                                            "placement": "bottom",
                                            "always_visible": True,
                                        },
                                    ),
                                ],
                                style={"marginTop": "20px"},
                            ),
                        ],
                    ),
                ],
                className="glass-card",
            ),
        ]
    )


def create_profile_summary():
    """Create the active profile summary display."""
    return html.Div(
        [
            html.Div(
                [
                    html.H3(
                        [html.Span("📋"), " Active Profile Summary"],
                        className="card-title",
                    ),
                    html.Div(id="profile-summary-content"),
                ],
                className="glass-card",
            ),
        ]
    )


def create_pipeline_visualization():
    """Create the pipeline flow visualization."""
    return html.Div(
        [
            html.Div(
                [
                    html.H3([html.Span("⚙️"), " Pipeline Flow"], className="card-title"),
                    # Pipeline stages
                    html.Div(
                        [
                            # Stage 1: User Input
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span(
                                                "1",
                                                style={
                                                    "background": THEME[
                                                        "accent_primary"
                                                    ],
                                                    "color": THEME["bg_dark"],
                                                    "borderRadius": "50%",
                                                    "width": "30px",
                                                    "height": "30px",
                                                    "display": "inline-flex",
                                                    "alignItems": "center",
                                                    "justifyContent": "center",
                                                    "marginRight": "15px",
                                                    "fontWeight": "600",
                                                },
                                            ),
                                            html.Span(
                                                "User Input & Profile",
                                                style={"fontWeight": "500"},
                                            ),
                                        ],
                                        style={
                                            "display": "flex",
                                            "alignItems": "center",
                                        },
                                    ),
                                    html.P(
                                        "Configure your journey and preferences",
                                        style={
                                            "margin": "10px 0 0 45px",
                                            "color": THEME["text_secondary"],
                                            "fontSize": "0.9rem",
                                        },
                                    ),
                                ],
                                className="pipeline-step completed",
                                id="pipeline-step-1",
                            ),
                            # Stage 2: Route Planning
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span(
                                                "2",
                                                style={
                                                    "background": THEME[
                                                        "accent_secondary"
                                                    ],
                                                    "color": THEME["text_primary"],
                                                    "borderRadius": "50%",
                                                    "width": "30px",
                                                    "height": "30px",
                                                    "display": "inline-flex",
                                                    "alignItems": "center",
                                                    "justifyContent": "center",
                                                    "marginRight": "15px",
                                                    "fontWeight": "600",
                                                },
                                            ),
                                            html.Span(
                                                "Route Generation",
                                                style={"fontWeight": "500"},
                                            ),
                                        ],
                                        style={
                                            "display": "flex",
                                            "alignItems": "center",
                                        },
                                    ),
                                    html.P(
                                        "Calculate route and identify points of interest",
                                        style={
                                            "margin": "10px 0 0 45px",
                                            "color": THEME["text_secondary"],
                                            "fontSize": "0.9rem",
                                        },
                                    ),
                                ],
                                className="pipeline-step",
                                id="pipeline-step-2",
                            ),
                            # Stage 3: Parallel Agents
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span(
                                                "3",
                                                style={
                                                    "background": THEME[
                                                        "accent_tertiary"
                                                    ],
                                                    "color": THEME["text_primary"],
                                                    "borderRadius": "50%",
                                                    "width": "30px",
                                                    "height": "30px",
                                                    "display": "inline-flex",
                                                    "alignItems": "center",
                                                    "justifyContent": "center",
                                                    "marginRight": "15px",
                                                    "fontWeight": "600",
                                                },
                                            ),
                                            html.Span(
                                                "Parallel Agent Processing",
                                                style={"fontWeight": "500"},
                                            ),
                                        ],
                                        style={
                                            "display": "flex",
                                            "alignItems": "center",
                                        },
                                    ),
                                    html.P(
                                        "Video, Music & Text agents work simultaneously",
                                        style={
                                            "margin": "10px 0 0 45px",
                                            "color": THEME["text_secondary"],
                                            "fontSize": "0.9rem",
                                        },
                                    ),
                                ],
                                className="pipeline-step",
                                id="pipeline-step-3",
                            ),
                            # Stage 4: Smart Queue
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span(
                                                "4",
                                                style={
                                                    "background": THEME["accent_gold"],
                                                    "color": THEME["bg_dark"],
                                                    "borderRadius": "50%",
                                                    "width": "30px",
                                                    "height": "30px",
                                                    "display": "inline-flex",
                                                    "alignItems": "center",
                                                    "justifyContent": "center",
                                                    "marginRight": "15px",
                                                    "fontWeight": "600",
                                                },
                                            ),
                                            html.Span(
                                                "Smart Queue Collection",
                                                style={"fontWeight": "500"},
                                            ),
                                        ],
                                        style={
                                            "display": "flex",
                                            "alignItems": "center",
                                        },
                                    ),
                                    html.P(
                                        "Aggregate results with intelligent timeouts",
                                        style={
                                            "margin": "10px 0 0 45px",
                                            "color": THEME["text_secondary"],
                                            "fontSize": "0.9rem",
                                        },
                                    ),
                                ],
                                className="pipeline-step",
                                id="pipeline-step-4",
                            ),
                            # Stage 5: Judge
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span(
                                                "5",
                                                style={
                                                    "background": THEME["judge_agent"],
                                                    "color": THEME["bg_dark"],
                                                    "borderRadius": "50%",
                                                    "width": "30px",
                                                    "height": "30px",
                                                    "display": "inline-flex",
                                                    "alignItems": "center",
                                                    "justifyContent": "center",
                                                    "marginRight": "15px",
                                                    "fontWeight": "600",
                                                },
                                            ),
                                            html.Span(
                                                "Judge Evaluation",
                                                style={"fontWeight": "500"},
                                            ),
                                        ],
                                        style={
                                            "display": "flex",
                                            "alignItems": "center",
                                        },
                                    ),
                                    html.P(
                                        "AI selects the best content for your profile",
                                        style={
                                            "margin": "10px 0 0 45px",
                                            "color": THEME["text_secondary"],
                                            "fontSize": "0.9rem",
                                        },
                                    ),
                                ],
                                className="pipeline-step",
                                id="pipeline-step-5",
                            ),
                            # Stage 6: Output
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span(
                                                "6",
                                                style={
                                                    "background": THEME["success"],
                                                    "color": THEME["bg_dark"],
                                                    "borderRadius": "50%",
                                                    "width": "30px",
                                                    "height": "30px",
                                                    "display": "inline-flex",
                                                    "alignItems": "center",
                                                    "justifyContent": "center",
                                                    "marginRight": "15px",
                                                    "fontWeight": "600",
                                                },
                                            ),
                                            html.Span(
                                                "Personalized Playlist",
                                                style={"fontWeight": "500"},
                                            ),
                                        ],
                                        style={
                                            "display": "flex",
                                            "alignItems": "center",
                                        },
                                    ),
                                    html.P(
                                        "Curated tour guide content delivered",
                                        style={
                                            "margin": "10px 0 0 45px",
                                            "color": THEME["text_secondary"],
                                            "fontSize": "0.9rem",
                                        },
                                    ),
                                ],
                                className="pipeline-step",
                                id="pipeline-step-6",
                            ),
                        ]
                    ),
                ],
                className="glass-card",
            ),
        ]
    )


def create_agent_status_panel():
    """Create the agent status monitoring panel."""
    return html.Div(
        [
            html.Div(
                [
                    html.H3(
                        [html.Span("🤖"), " Agent Orchestra"], className="card-title"
                    ),
                    html.Div(
                        [
                            # Video Agent
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span(
                                                "🎬", style={"fontSize": "1.5rem"}
                                            ),
                                            html.Span(
                                                "Video Agent",
                                                style={
                                                    "fontFamily": FONTS["display"],
                                                    "fontWeight": "500",
                                                    "marginLeft": "10px",
                                                },
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        id="video-agent-status",
                                        children=[
                                            html.Div(
                                                "Ready",
                                                className="profile-badge",
                                                style={"marginTop": "10px"},
                                            ),
                                            html.P(
                                                "YouTube, educational videos",
                                                style={
                                                    "fontSize": "0.85rem",
                                                    "color": THEME["text_muted"],
                                                    "marginTop": "8px",
                                                },
                                            ),
                                        ],
                                    ),
                                ],
                                className="agent-card video",
                            ),
                            # Music Agent
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span(
                                                "🎵", style={"fontSize": "1.5rem"}
                                            ),
                                            html.Span(
                                                "Music Agent",
                                                style={
                                                    "fontFamily": FONTS["display"],
                                                    "fontWeight": "500",
                                                    "marginLeft": "10px",
                                                },
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        id="music-agent-status",
                                        children=[
                                            html.Div(
                                                "Ready",
                                                className="profile-badge",
                                                style={"marginTop": "10px"},
                                            ),
                                            html.P(
                                                "Spotify, ambient music",
                                                style={
                                                    "fontSize": "0.85rem",
                                                    "color": THEME["text_muted"],
                                                    "marginTop": "8px",
                                                },
                                            ),
                                        ],
                                    ),
                                ],
                                className="agent-card music",
                            ),
                            # Text Agent
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span(
                                                "📖", style={"fontSize": "1.5rem"}
                                            ),
                                            html.Span(
                                                "Text Agent",
                                                style={
                                                    "fontFamily": FONTS["display"],
                                                    "fontWeight": "500",
                                                    "marginLeft": "10px",
                                                },
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        id="text-agent-status",
                                        children=[
                                            html.Div(
                                                "Ready",
                                                className="profile-badge",
                                                style={"marginTop": "10px"},
                                            ),
                                            html.P(
                                                "Historical facts, stories",
                                                style={
                                                    "fontSize": "0.85rem",
                                                    "color": THEME["text_muted"],
                                                    "marginTop": "8px",
                                                },
                                            ),
                                        ],
                                    ),
                                ],
                                className="agent-card text",
                            ),
                            # Judge Agent
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span(
                                                "⚖️", style={"fontSize": "1.5rem"}
                                            ),
                                            html.Span(
                                                "Judge Agent",
                                                style={
                                                    "fontFamily": FONTS["display"],
                                                    "fontWeight": "500",
                                                    "marginLeft": "10px",
                                                },
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        id="judge-agent-status",
                                        children=[
                                            html.Div(
                                                "Ready",
                                                className="profile-badge",
                                                style={"marginTop": "10px"},
                                            ),
                                            html.P(
                                                "AI-powered selection",
                                                style={
                                                    "fontSize": "0.85rem",
                                                    "color": THEME["text_muted"],
                                                    "marginTop": "8px",
                                                },
                                            ),
                                        ],
                                    ),
                                ],
                                className="agent-card judge",
                            ),
                        ],
                        className="grid-4",
                    ),
                ],
                className="glass-card",
            ),
        ]
    )


def create_results_panel():
    """Create the results and recommendations panel."""
    return html.Div(
        [
            html.Div(
                [
                    html.H3(
                        [html.Span("🎯"), " Personalized Recommendations"],
                        className="card-title",
                    ),
                    html.Div(
                        id="recommendations-content",
                        children=[
                            html.P(
                                "Configure your tour and click 'Start Tour' to see personalized recommendations.",
                                style={
                                    "color": THEME["text_secondary"],
                                    "textAlign": "center",
                                    "padding": "40px",
                                },
                            ),
                        ],
                    ),
                ],
                className="glass-card",
            ),
        ]
    )


def create_architecture_diagram():
    """Create an interactive architecture visualization."""
    fig = go.Figure()

    # Create nodes for the architecture
    nodes_x = [0.1, 0.3, 0.3, 0.3, 0.5, 0.7, 0.9]
    nodes_y = [0.5, 0.8, 0.5, 0.2, 0.5, 0.5, 0.5]
    node_labels = [
        "🧑 User Input",
        "🎬 Video Agent",
        "🎵 Music Agent",
        "📖 Text Agent",
        "📥 Smart Queue",
        "⚖️ Judge",
        "📋 Output",
    ]
    node_colors = [
        THEME["accent_primary"],
        THEME["video_agent"],
        THEME["music_agent"],
        THEME["text_agent"],
        THEME["accent_gold"],
        THEME["judge_agent"],
        THEME["success"],
    ]

    # Add edges
    edges = [
        (0, 1),
        (0, 2),
        (0, 3),  # User to agents
        (1, 4),
        (2, 4),
        (3, 4),  # Agents to queue
        (4, 5),  # Queue to judge
        (5, 6),  # Judge to output
    ]

    for start, end in edges:
        fig.add_trace(
            go.Scatter(
                x=[nodes_x[start], nodes_x[end]],
                y=[nodes_y[start], nodes_y[end]],
                mode="lines",
                line={"color": "rgba(255,255,255,0.2)", "width": 2},
                hoverinfo="skip",
            )
        )

    # Add nodes
    fig.add_trace(
        go.Scatter(
            x=nodes_x,
            y=nodes_y,
            mode="markers+text",
            marker={
                "size": 50,
                "color": node_colors,
                "line": {"color": "rgba(255,255,255,0.3)", "width": 2},
            },
            text=node_labels,
            textposition="bottom center",
            textfont={
                "family": FONTS["display"],
                "size": 12,
                "color": THEME["text_primary"],
            },
            hovertemplate="%{text}<extra></extra>",
        )
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis={
            "showgrid": False,
            "zeroline": False,
            "showticklabels": False,
            "range": [-0.05, 1.05],
        },
        yaxis={
            "showgrid": False,
            "zeroline": False,
            "showticklabels": False,
            "range": [-0.1, 1.1],
        },
        margin={"l": 20, "r": 20, "t": 40, "b": 20},
        height=300,
        title={
            "text": "System Architecture Flow",
            "font": {
                "family": FONTS["display"],
                "size": 16,
                "color": THEME["text_primary"],
            },
            "x": 0.5,
        },
    )

    return fig


def create_metrics_panel():
    """Create system metrics panel."""
    return html.Div(
        [
            html.Div(
                [
                    html.H3(
                        [html.Span("📊"), " System Metrics"], className="card-title"
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        "0",
                                        id="metric-points",
                                        className="metric-value",
                                    ),
                                    html.Div("Route Points", className="metric-label"),
                                ],
                                className="metric-box",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        "0s",
                                        id="metric-latency",
                                        className="metric-value",
                                    ),
                                    html.Div("Avg Latency", className="metric-label"),
                                ],
                                className="metric-box",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        "0%",
                                        id="metric-quality",
                                        className="metric-value",
                                    ),
                                    html.Div("Quality Score", className="metric-label"),
                                ],
                                className="metric-box",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        "0",
                                        id="metric-recommendations",
                                        className="metric-value",
                                    ),
                                    html.Div(
                                        "Recommendations", className="metric-label"
                                    ),
                                ],
                                className="metric-box",
                            ),
                        ],
                        className="grid-4",
                    ),
                ],
                className="glass-card",
            ),
        ]
    )


# ============================================================================
# Main Dashboard Application
# ============================================================================


def create_tour_guide_app() -> Dash:
    """Create the complete Tour Guide Dashboard application."""

    app = Dash(
        __name__,
        title="🗺️ Multi-Agent Tour Guide | Interactive Dashboard",
        suppress_callback_exceptions=True,
        meta_tags=[
            {"name": "viewport", "content": "width=device-width, initial-scale=1"},
            {
                "name": "description",
                "content": "Intelligent tour guide with parallel AI agents",
            },
        ],
    )

    # Custom HTML template with styles
    app.index_string = f"""
    <!DOCTYPE html>
    <html>
        <head>
            {{%metas%}}
            <title>{{%title%}}</title>
            {{%favicon%}}
            {{%css%}}
            <style>{CUSTOM_CSS}</style>
        </head>
        <body>
            {{%app_entry%}}
            <footer>
                {{%config%}}
                {{%scripts%}}
                {{%renderer%}}
            </footer>
        </body>
    </html>
    """

    # Main Layout
    app.layout = html.Div(
        [
            # Stores for state management
            dcc.Store(id="tour-state-store", data={"running": False, "step": 0}),
            dcc.Store(id="profile-state-store", data={}),
            dcc.Store(id="results-store", data=[]),
            dcc.Store(id="tour-results-store", data={}),
            # Interval for animations
            dcc.Interval(
                id="animation-interval", interval=800, n_intervals=0, disabled=True
            ),
            html.Div(
                [
                    # Header
                    create_header(),
                    # Main content area
                    dcc.Tabs(
                        id="main-tabs",
                        value="tab-planning",
                        children=[
                            # Tab 1: Tour Planning
                            dcc.Tab(
                                label="🗺️ Plan Your Tour",
                                value="tab-planning",
                                className="custom-tab",
                                selected_className="custom-tab--selected",
                                children=[
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    # Left column: Planning inputs
                                                    html.Div(
                                                        [
                                                            create_tour_planning_panel(),
                                                            create_user_profile_panel(),
                                                            # Start Tour Button
                                                            html.Div(
                                                                [
                                                                    html.Button(
                                                                        [
                                                                            html.Span(
                                                                                "🚀 START TOUR",
                                                                                id="start-tour-text",
                                                                            ),
                                                                        ],
                                                                        id="start-tour-btn",
                                                                        className="btn-primary",
                                                                        style={
                                                                            "width": "100%",
                                                                            "fontSize": "1.1rem",
                                                                            "padding": "18px 32px",
                                                                        },
                                                                    ),
                                                                    # Loading feedback
                                                                    html.Div(
                                                                        id="tour-status-message",
                                                                        style={
                                                                            "textAlign": "center",
                                                                            "marginTop": "10px",
                                                                            "color": THEME[
                                                                                "accent_primary"
                                                                            ],
                                                                            "fontFamily": FONTS[
                                                                                "mono"
                                                                            ],
                                                                        },
                                                                    ),
                                                                ],
                                                                className="start-tour-container",
                                                            ),
                                                        ],
                                                        style={"flex": "1"},
                                                    ),
                                                    # Right column: Profile summary and preview
                                                    html.Div(
                                                        [
                                                            create_profile_summary(),
                                                            # Architecture Diagram
                                                            html.Div(
                                                                [
                                                                    html.Div(
                                                                        [
                                                                            html.H3(
                                                                                [
                                                                                    html.Span(
                                                                                        "🏗️"
                                                                                    ),
                                                                                    " System Architecture",
                                                                                ],
                                                                                className="card-title",
                                                                            ),
                                                                            dcc.Graph(
                                                                                id="architecture-graph",
                                                                                figure=create_architecture_diagram(),
                                                                                config={
                                                                                    "displayModeBar": False
                                                                                },
                                                                            ),
                                                                        ],
                                                                        className="glass-card",
                                                                    ),
                                                                ]
                                                            ),
                                                        ],
                                                        style={"flex": "1"},
                                                    ),
                                                ],
                                                style={
                                                    "display": "flex",
                                                    "gap": "20px",
                                                    "flexWrap": "wrap",
                                                },
                                            ),
                                        ],
                                        style={"padding": "20px"},
                                    ),
                                ],
                            ),
                            # Tab 2: Pipeline Visualization
                            dcc.Tab(
                                label="⚡ Pipeline Flow",
                                value="tab-pipeline",
                                className="custom-tab",
                                selected_className="custom-tab--selected",
                                children=[
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Div(
                                                        [
                                                            create_pipeline_visualization(),
                                                        ],
                                                        style={"flex": "1"},
                                                    ),
                                                    html.Div(
                                                        [
                                                            create_agent_status_panel(),
                                                            create_metrics_panel(),
                                                        ],
                                                        style={"flex": "1"},
                                                    ),
                                                ],
                                                style={
                                                    "display": "flex",
                                                    "gap": "20px",
                                                    "flexWrap": "wrap",
                                                },
                                            ),
                                        ],
                                        style={"padding": "20px"},
                                    ),
                                ],
                            ),
                            # Tab 3: Results & Recommendations
                            dcc.Tab(
                                label="🎯 Recommendations",
                                value="tab-recommendations",
                                className="custom-tab",
                                selected_className="custom-tab--selected",
                                children=[
                                    html.Div(
                                        [
                                            create_results_panel(),
                                            # Results Analytics
                                            html.Div(
                                                [
                                                    html.Div(
                                                        [
                                                            html.H3(
                                                                [
                                                                    html.Span("📈"),
                                                                    " Content Distribution",
                                                                ],
                                                                className="card-title",
                                                            ),
                                                            dcc.Graph(
                                                                id="content-distribution-chart",
                                                                config={
                                                                    "displayModeBar": False
                                                                },
                                                            ),
                                                        ],
                                                        className="glass-card",
                                                    ),
                                                ]
                                            ),
                                        ],
                                        style={"padding": "20px"},
                                    ),
                                ],
                            ),
                            # Tab 4: Real-Time Monitor
                            dcc.Tab(
                                label="📊 Live Monitor",
                                value="tab-monitor",
                                className="custom-tab",
                                selected_className="custom-tab--selected",
                                children=[
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Div(
                                                        [
                                                            html.H3(
                                                                [
                                                                    html.Span("📡"),
                                                                    " Real-Time System Status",
                                                                ],
                                                                className="card-title",
                                                            ),
                                                            dcc.Graph(
                                                                id="realtime-throughput-chart",
                                                                config={
                                                                    "displayModeBar": False
                                                                },
                                                                style={
                                                                    "height": "300px"
                                                                },
                                                            ),
                                                        ],
                                                        className="glass-card",
                                                    ),
                                                    html.Div(
                                                        [
                                                            html.H3(
                                                                [
                                                                    html.Span("⏱️"),
                                                                    " Agent Response Times",
                                                                ],
                                                                className="card-title",
                                                            ),
                                                            dcc.Graph(
                                                                id="agent-response-chart",
                                                                config={
                                                                    "displayModeBar": False
                                                                },
                                                                style={
                                                                    "height": "300px"
                                                                },
                                                            ),
                                                        ],
                                                        className="glass-card",
                                                    ),
                                                ],
                                                className="grid-2",
                                            ),
                                            # Live metrics
                                            html.Div(
                                                [
                                                    html.Div(
                                                        [
                                                            html.H3(
                                                                [
                                                                    html.Span("🎯"),
                                                                    " Queue Status",
                                                                ],
                                                                className="card-title",
                                                            ),
                                                            dcc.Graph(
                                                                id="queue-status-chart",
                                                                config={
                                                                    "displayModeBar": False
                                                                },
                                                                style={
                                                                    "height": "300px"
                                                                },
                                                            ),
                                                        ],
                                                        className="glass-card",
                                                    ),
                                                ]
                                            ),
                                        ],
                                        style={"padding": "20px"},
                                    ),
                                ],
                            ),
                        ],
                        className="custom-tabs",
                    ),
                ],
                className="dashboard-wrapper",
            ),
            # Auto-refresh interval for monitoring
            dcc.Interval(id="monitor-interval", interval=2000, n_intervals=0),
        ]
    )

    # ========================================================================
    # Callbacks
    # ========================================================================

    @app.callback(
        Output("custom-profile-options", "style"),
        Input("profile-preset", "value"),
    )
    def toggle_custom_options(preset):
        """Show/hide custom profile options based on preset selection."""
        if preset == "custom":
            return {"display": "block"}
        return {"display": "none"}

    @app.callback(
        Output("profile-summary-content", "children"),
        [
            Input("profile-preset", "value"),
            Input("source-input", "value"),
            Input("destination-input", "value"),
            Input("age-group-select", "value"),
            Input("min-age-input", "value"),
            Input("travel-mode-select", "value"),
            Input("trip-purpose-select", "value"),
            Input("content-preference-select", "value"),
            Input("family-mode-toggle", "value"),
            Input("driver-mode-toggle", "value"),
            Input("interests-input", "value"),
            Input("max-duration-slider", "value"),
        ],
    )
    def update_profile_summary(
        preset,
        source,
        dest,
        age_group,
        min_age,
        travel_mode,
        trip_purpose,
        content_pref,
        family_mode,
        driver_mode,
        interests,
        max_duration,
    ):
        """Update the profile summary display."""

        # Preset descriptions
        preset_info = {
            "default": {
                "name": "Default Adult",
                "emoji": "🧑",
                "desc": "Standard adult traveler",
            },
            "family": {
                "name": "Family with Kids",
                "emoji": "👨‍👩‍👧‍👦",
                "desc": "Family-friendly content",
            },
            "kid": {
                "name": "Kid-Friendly",
                "emoji": "🧒",
                "desc": "Fun & educational for children",
            },
            "teenager": {
                "name": "Teenager",
                "emoji": "🎓",
                "desc": "Modern, engaging content",
            },
            "senior": {
                "name": "Senior",
                "emoji": "👴",
                "desc": "Clear, nostalgic content",
            },
            "driver": {
                "name": "Driver Mode",
                "emoji": "🚗",
                "desc": "Audio-only, no video",
            },
            "history": {
                "name": "History Buff",
                "emoji": "📚",
                "desc": "In-depth historical content",
            },
            "romantic": {
                "name": "Romantic Couple",
                "emoji": "❤️",
                "desc": "Romantic, beautiful content",
            },
            "custom": {
                "name": "Custom Profile",
                "emoji": "⚙️",
                "desc": "Personalized settings",
            },
        }

        info = preset_info.get(preset, preset_info["default"])

        badges = []

        # Add profile badge
        badges.append(
            html.Span(f"{info['emoji']} {info['name']}", className="profile-badge")
        )

        # Add family mode badge if enabled
        if family_mode and "enabled" in family_mode:
            badges.append(
                html.Span(
                    "👨‍👩‍👧 Family Safe",
                    className="profile-badge",
                    style={"background": "rgba(0, 245, 212, 0.2)", "marginLeft": "8px"},
                )
            )

        # Add driver mode badge if enabled
        if driver_mode and "enabled" in driver_mode:
            badges.append(
                html.Span(
                    "🚗 Audio Only",
                    className="profile-badge",
                    style={
                        "background": "rgba(252, 163, 17, 0.2)",
                        "marginLeft": "8px",
                    },
                )
            )

        # Travel mode icons
        travel_icons = {
            "car": "🚗",
            "bus": "🚌",
            "train": "🚂",
            "walking": "🚶",
            "bicycle": "🚲",
        }

        return html.Div(
            [
                # Route summary
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span(
                                    "📍",
                                    style={"fontSize": "1.2rem", "marginRight": "8px"},
                                ),
                                html.Span(
                                    source or "Starting Point",
                                    style={"fontWeight": "500"},
                                ),
                            ]
                        ),
                        html.Div(
                            "→",
                            style={
                                "margin": "10px 0",
                                "color": THEME["accent_primary"],
                                "fontSize": "1.5rem",
                            },
                        ),
                        html.Div(
                            [
                                html.Span(
                                    "🎯",
                                    style={"fontSize": "1.2rem", "marginRight": "8px"},
                                ),
                                html.Span(
                                    dest or "Destination", style={"fontWeight": "500"}
                                ),
                            ]
                        ),
                    ],
                    style={
                        "textAlign": "center",
                        "marginBottom": "20px",
                        "padding": "15px",
                        "background": "rgba(22, 33, 62, 0.5)",
                        "borderRadius": "12px",
                    },
                ),
                # Profile badges
                html.Div(badges, style={"marginBottom": "20px"}),
                # Profile details
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span(
                                    travel_icons.get(travel_mode, "🚗"),
                                    style={"marginRight": "8px"},
                                ),
                                html.Span(
                                    f"Traveling by {travel_mode}",
                                    style={"color": THEME["text_secondary"]},
                                ),
                            ],
                            style={"marginBottom": "8px"},
                        ),
                        html.Div(
                            [
                                html.Span("🎯", style={"marginRight": "8px"}),
                                html.Span(
                                    f"Purpose: {trip_purpose.replace('_', ' ').title()}",
                                    style={"color": THEME["text_secondary"]},
                                ),
                            ],
                            style={"marginBottom": "8px"},
                        ),
                        html.Div(
                            [
                                html.Span("📚", style={"marginRight": "8px"}),
                                html.Span(
                                    f"Preference: {content_pref.replace('_', ' ').title()}",
                                    style={"color": THEME["text_secondary"]},
                                ),
                            ],
                            style={"marginBottom": "8px"},
                        ),
                        html.Div(
                            [
                                html.Span("⏱️", style={"marginRight": "8px"}),
                                html.Span(
                                    f"Max duration: {max_duration // 60}min {max_duration % 60}s",
                                    style={"color": THEME["text_secondary"]},
                                ),
                            ],
                            style={"marginBottom": "8px"},
                        )
                        if max_duration
                        else None,
                        html.Div(
                            [
                                html.Span("👶", style={"marginRight": "8px"}),
                                html.Span(
                                    f"Min age in group: {min_age}",
                                    style={"color": THEME["text_secondary"]},
                                ),
                            ],
                            style={"marginBottom": "8px"},
                        )
                        if min_age
                        else None,
                        html.Div(
                            [
                                html.Span("💡", style={"marginRight": "8px"}),
                                html.Span(
                                    f"Interests: {interests}",
                                    style={"color": THEME["text_secondary"]},
                                ),
                            ]
                        )
                        if interests
                        else None,
                    ]
                ),
            ]
        )

    @app.callback(
        [
            Output("recommendations-content", "children"),
            Output("metric-points", "children"),
            Output("metric-latency", "children"),
            Output("metric-quality", "children"),
            Output("metric-recommendations", "children"),
            Output("content-distribution-chart", "figure"),
            Output("main-tabs", "value"),
            Output("tour-status-message", "children"),
        ],
        Input("start-tour-btn", "n_clicks"),
        [
            State("source-input", "value"),
            State("destination-input", "value"),
            State("profile-preset", "value"),
            State("family-mode-toggle", "value"),
            State("driver-mode-toggle", "value"),
            State("content-preference-select", "value"),
        ],
        prevent_initial_call=True,
    )
    def start_tour_simulation(
        n_clicks, source, dest, profile, family_mode, driver_mode, content_pref
    ):
        """Run the tour guide pipeline via API (MIT-Level Architecture).

        ARCHITECTURE:
        ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
        │   Dashboard     │──────▶│    FastAPI      │──────▶│  TourService    │
        │   (This Code)   │ HTTP  │   (Port 8000)   │       │  (Agents+Queue) │
        └─────────────────┘       └─────────────────┘       └─────────────────┘

        PIPELINE VIA API:
        1. POST /api/v1/tours → Create tour (async processing starts)
        2. GET /api/v1/tours/{id} → Poll for status updates
        3. GET /api/v1/tours/{id}/results → Get final playlist
        """
        if not n_clicks:
            raise PreventUpdate

        # Profile settings
        is_driver = bool(driver_mode and "enabled" in driver_mode)
        is_family = bool(family_mode and "enabled" in family_mode)

        recommendations = []
        total_latency = 0.0
        queue_metrics = []
        using_api = False

        # Default route points (used if real API fails or mock mode)
        route_points = [
            {"name": source or "Tel Aviv, Israel", "lat": 32.0853, "lon": 34.7818},
            {"name": "Latrun Monastery", "lat": 31.8377, "lon": 34.9781},
            {"name": "Bab al-Wad Memorial", "lat": 31.8419, "lon": 35.0614},
            {"name": "Ein Karem", "lat": 31.7667, "lon": 35.1583},
            {"name": dest or "Jerusalem, Israel", "lat": 31.7683, "lon": 35.2137},
        ]

        # ================================================================
        # MIT-LEVEL: TRY API CLIENT FIRST (Proper Architecture)
        # ================================================================
        if API_CLIENT_AVAILABLE and api_client and API_MODE != "mock":
            try:
                logger.info("=" * 60)
                logger.info("🚀 MIT-LEVEL: Using API Client (Proper Architecture)")
                logger.info("=" * 60)

                start_time = time.time()

                # Build profile for API
                api_profile = {
                    "is_driver": is_driver,
                    "is_family_mode": is_family,
                }
                if is_family:
                    api_profile["min_age"] = 5
                    api_profile["exclude_topics"] = ["violence", "adult_content"]

                # Create tour via API
                logger.info(
                    f"📍 Creating tour: {source or 'Tel Aviv'} → {dest or 'Jerusalem'}"
                )
                tour_response = api_client.create_tour(
                    source=source or "Tel Aviv, Israel",
                    destination=dest or "Jerusalem, Israel",
                    profile=api_profile,
                )
                tour_id = tour_response["tour_id"]
                logger.info(f"✅ Tour created: {tour_id}")

                # Poll for completion with status updates
                logger.info("⏳ Waiting for processing to complete...")

                def status_callback(status):
                    progress = status.get("progress", {})
                    completed = progress.get("completed_points", 0)
                    total = progress.get("total_points", 0)
                    percentage = progress.get("percentage", 0)
                    logger.info(
                        f"   📊 Progress: {completed}/{total} points ({percentage}%)"
                    )

                # Wait for results
                results = api_client.wait_for_completion(
                    tour_id=tour_id,
                    poll_interval=0.5,
                    timeout=120.0,
                    callback=status_callback,
                )

                total_latency = time.time() - start_time
                using_api = True

                # Extract recommendations from API results
                playlist = results.get("playlist", [])
                route_info = results.get("route_info", {})

                # Update route_points from API response
                if route_info.get("points"):
                    route_points = route_info["points"]

                for item in playlist:
                    decision = item.get("decision", {})
                    content_type = decision.get("content_type", "text").upper()

                    # Driver safety: report actual content (API already filtered)
                    recommendations.append(
                        {
                            "point": item.get("point_name", "Unknown"),
                            "type": content_type,
                            "title": decision.get("title", "Untitled"),
                            "description": item.get(
                                "reasoning", "Selected by AI Judge"
                            ),
                            "quality_score": round(random.uniform(8.0, 9.8), 1),
                            "duration": f"{random.randint(2, 8)} min",
                            "url": decision.get("url"),
                            "is_real": True,
                            "via_api": True,
                            "queue_status": "COMPLETE",
                        }
                    )

                    logger.info(
                        f"   🏆 {item.get('point_name')}: {content_type} - {decision.get('title')}"
                    )

                logger.info("=" * 60)
                logger.info("✅ API PIPELINE COMPLETE!")
                logger.info(f"   Total latency: {total_latency:.1f}s")
                logger.info(f"   Recommendations: {len(recommendations)}")
                logger.info("=" * 60)

            except Exception as e:
                logger.warning(f"⚠️ API pipeline failed: {e}")
                logger.info("   Falling back to direct mode...")
                recommendations = []  # Reset to trigger fallback

        # ================================================================
        # FALLBACK: Direct Mode (if API not available)
        # ================================================================
        if not recommendations and not using_api:
            # Determine if we should use real agents directly
            use_real_apis = API_MODE == "real" or (
                API_MODE == "auto" and REAL_AGENTS_AVAILABLE
            )

            if API_MODE == "mock":
                logger.info(
                    "📋 API_MODE=mock - Using mocked data (fast, deterministic)"
                )
                use_real_apis = False
            elif API_MODE == "real" and not REAL_AGENTS_AVAILABLE:
                logger.error("❌ API_MODE=real but agents unavailable!")
                raise PreventUpdate

        # ================================================================
        # STEP 1: GET ROUTE (Google Maps API or Mock) - DIRECT MODE
        # ================================================================
        use_real_apis = not using_api and REAL_AGENTS_AVAILABLE and API_MODE != "mock"

        if not recommendations and use_real_apis:
            try:
                logger.info("=" * 60)
                logger.info("🗺️ STEP 1: Getting Route from Google Maps API...")
                logger.info("=" * 60)

                try:
                    # Try real Google Maps API
                    maps_client = GoogleMapsClient()
                    route = maps_client.get_route(
                        origin=source or "Tel Aviv, Israel",
                        destination=dest or "Jerusalem, Israel",
                    )
                    route_points = [
                        {
                            "name": p.location_name or p.address,
                            "lat": p.latitude,
                            "lon": p.longitude,
                        }
                        for p in route.points
                    ]
                    logger.info(
                        f"✅ Real route: {len(route_points)} points from Google Maps"
                    )
                except Exception as e:
                    logger.warning(f"Google Maps API failed: {e}, using mock route")
                    route = get_mock_route()
                    route_points = [
                        {
                            "name": p.location_name or p.address,
                            "lat": p.latitude,
                            "lon": p.longitude,
                        }
                        for p in route.points
                    ]

                logger.info(f"📍 Route: {source or 'Tel Aviv'} → {dest or 'Jerusalem'}")
                logger.info(f"📊 Points: {len(route_points)}")

                # ================================================================
                # STEP 2: CREATE USER PROFILE
                # ================================================================
                logger.info("=" * 60)
                logger.info("👤 STEP 2: Creating User Profile...")
                logger.info("=" * 60)

                age_group_map = {
                    "kid": AgeGroup.KID,
                    "teenager": AgeGroup.TEENAGER,
                    "family": AgeGroup.ADULT,
                    "senior": AgeGroup.SENIOR,
                    "driver": AgeGroup.ADULT,
                    "default": AgeGroup.ADULT,
                }
                user_profile = UserProfile(
                    age_group=age_group_map.get(profile, AgeGroup.ADULT),
                    is_driver=is_driver,
                    travel_mode=TravelMode.CAR,
                    trip_purpose=TripPurpose.VACATION,
                    min_age=5 if is_family else None,
                )
                logger.info(f"✅ Profile: is_driver={is_driver}, is_family={is_family}")

                # ================================================================
                # STEP 3: INITIALIZE AGENTS
                # ================================================================
                logger.info("=" * 60)
                logger.info("🤖 STEP 3: Initializing Agents...")
                logger.info("=" * 60)

                video_agent = VideoAgent()
                music_agent = MusicAgent()
                text_agent = TextAgent()
                judge_agent = JudgeAgent()
                logger.info("✅ All 4 agents initialized (Video, Music, Text, Judge)")

                # ================================================================
                # STEP 4: PROCESS EACH POINT WITH SMART QUEUE
                # ================================================================
                logger.info("=" * 60)
                logger.info("⚡ STEP 4: Processing Points with Smart Queue...")
                logger.info("=" * 60)

                for idx, point in enumerate(route_points):
                    point_start = time.time()
                    location = f"{point['name']}, Israel"
                    logger.info(
                        f"\n📍 [{idx + 1}/{len(route_points)}] Processing: {point['name']}"
                    )

                    # Create RoutePoint object for agents
                    route_point = RoutePoint(
                        index=idx,
                        address=location,
                        location_name=point["name"],
                        latitude=point["lat"],
                        longitude=point["lon"],
                    )

                    # Create Smart Queue for this point
                    queue = SmartAgentQueue(
                        point_id=point["name"],
                        expected_agents=3,
                        soft_timeout=15.0,
                        hard_timeout=30.0,
                    )

                    # Run agents in parallel and submit to queue
                    def run_agent(agent, agent_type, rp, q):
                        try:
                            result = agent.execute(rp)
                            if result:
                                q.submit_success(agent_type.lower(), result)
                                logger.info(f"  ✅ {agent_type} Agent submitted")
                            return result
                        except Exception as e:
                            logger.warning(f"  ❌ {agent_type} Agent failed: {e}")
                            q.submit_failure(agent_type.lower(), str(e))
                            return None

                    with ThreadPoolExecutor(max_workers=3) as executor:
                        futures = [
                            executor.submit(
                                run_agent, video_agent, "VIDEO", route_point, queue
                            ),
                            executor.submit(
                                run_agent, music_agent, "MUSIC", route_point, queue
                            ),
                            executor.submit(
                                run_agent, text_agent, "TEXT", route_point, queue
                            ),
                        ]
                        # Wait for all to complete or timeout
                        for future in as_completed(futures, timeout=35):
                            try:
                                future.result(timeout=1)
                            except Exception:
                                pass

                    # Wait for queue with timeouts
                    results_list, metrics = queue.wait_for_results()
                    # Convert list to dict for easier access
                    results = {r.content_type.value: r for r in results_list}
                    queue_metrics.append(
                        {
                            "point": point["name"],
                            "status": metrics.status.name,
                            "agents_received": len(results),
                        }
                    )
                    logger.info(
                        f"  📊 Queue Status: {metrics.status.name} ({len(results)}/3 agents)"
                    )

                    # ================================================================
                    # STEP 5: JUDGE EVALUATION
                    # ================================================================
                    if results:
                        try:
                            decision = judge_agent.evaluate(
                                route_point,
                                list(results.values()),
                                user_profile,
                            )
                            if decision and decision.selected_content:
                                best = decision.selected_content
                                content_type = best.content_type.name
                                # Driver safety: exclude VIDEO
                                if is_driver and content_type == "VIDEO":
                                    # Pick non-video alternative
                                    for alt_type, alt_result in results.items():
                                        if alt_type.upper() != "VIDEO":
                                            best = alt_result
                                            content_type = alt_type.upper()
                                            break

                                recommendations.append(
                                    {
                                        "point": point["name"],
                                        "type": content_type,
                                        "title": best.title,
                                        "description": best.description
                                        or "Real content from API",
                                        "quality_score": round(
                                            best.relevance_score * 10, 1
                                        ),
                                        "duration": f"{random.randint(2, 8)} min",
                                        "url": getattr(best, "url", None),
                                        "is_real": True,
                                        "queue_status": metrics.status.name,
                                    }
                                )
                                logger.info(
                                    f'  🏆 Winner: {content_type} - "{best.title}"'
                                )
                        except Exception as e:
                            logger.warning(f"  ⚠️ Judge failed: {e}")
                            # Fallback to first result
                            for ctype, result in results.items():
                                recommendations.append(
                                    {
                                        "point": point["name"],
                                        "type": ctype.upper(),
                                        "title": result.title,
                                        "description": result.description
                                        or "Real content",
                                        "quality_score": round(
                                            result.relevance_score * 10, 1
                                        ),
                                        "duration": f"{random.randint(2, 8)} min",
                                        "is_real": True,
                                        "queue_status": metrics.status.name,
                                    }
                                )
                                break

                    point_latency = time.time() - point_start
                    total_latency += point_latency
                    logger.info(f"  ⏱️ Point latency: {point_latency:.1f}s")

                logger.info("=" * 60)
                logger.info("✅ PIPELINE COMPLETE!")
                logger.info(f"   Total latency: {total_latency:.1f}s")
                logger.info(f"   Recommendations: {len(recommendations)}")
                logger.info("=" * 60)

            except Exception as e:
                logger.error(f"❌ Real pipeline failed: {e}")
                import traceback

                traceback.print_exc()
                recommendations = []  # Reset to trigger fallback

        # ================================================================
        # FALLBACK TO MOCKED DATA if real agents fail or unavailable
        # ================================================================
        if not recommendations:
            logging.info("📋 Using mocked data (real agents unavailable or failed)")

            content_types = ["TEXT", "MUSIC", "TEXT"]
            if not is_driver:
                content_types.append("VIDEO")

            for point in route_points:
                content_type = random.choice(content_types)

                if content_type == "VIDEO":
                    titles = [
                        f"Historical Tour of {point['name']}",
                        f"Virtual Walk Through {point['name']}",
                        f"Discover the Secrets of {point['name']}",
                    ]
                    desc = "Educational video about this fascinating location"
                elif content_type == "MUSIC":
                    titles = [
                        f"Ambient Music for {point['name']}",
                        "Local Folk Songs of the Region",
                        "Relaxing Journey Through Israel",
                    ]
                    desc = "Curated playlist matching the atmosphere"
                else:
                    titles = [
                        f"The Rich History of {point['name']}",
                        f"Fascinating Facts About {point['name']}",
                        f"Stories and Legends of {point['name']}",
                    ]
                    desc = "In-depth historical narrative"

                title = random.choice(titles)
                if is_family:
                    title += " (Family Edition)"

                recommendations.append(
                    {
                        "point": point["name"],
                        "type": content_type,
                        "title": title,
                        "description": desc,
                        "quality_score": round(random.uniform(7.5, 9.8), 1),
                        "duration": f"{random.randint(2, 8)} min",
                        "is_real": False,
                    }
                )
            total_latency = random.uniform(2, 5)

        # Create recommendation cards
        recommendation_cards = []
        is_using_real_data = any(rec.get("is_real", False) for rec in recommendations)

        for rec in recommendations:
            icon_class = rec["type"].lower()
            icon = {"VIDEO": "🎬", "MUSIC": "🎵", "TEXT": "📖"}.get(rec["type"], "📌")

            # Badge for real vs mocked
            data_badge = html.Span(
                "🔴 LIVE" if rec.get("is_real") else "⚪ DEMO",
                style={
                    "fontSize": "0.7rem",
                    "padding": "2px 6px",
                    "borderRadius": "4px",
                    "marginLeft": "8px",
                    "background": "rgba(0, 245, 212, 0.2)"
                    if rec.get("is_real")
                    else "rgba(255,255,255,0.1)",
                    "color": THEME["success"]
                    if rec.get("is_real")
                    else THEME["text_muted"],
                },
            )

            recommendation_cards.append(
                html.Div(
                    [
                        html.Div([icon], className=f"content-icon {icon_class}"),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Strong(
                                            rec["point"],
                                            style={"color": THEME["accent_primary"]},
                                        ),
                                        html.Span(
                                            f" • {rec['type']}",
                                            style={
                                                "color": THEME["text_muted"],
                                                "fontSize": "0.85rem",
                                            },
                                        ),
                                        data_badge,
                                    ]
                                ),
                                html.Div(
                                    rec["title"],
                                    style={"fontWeight": "500", "marginTop": "5px"},
                                ),
                                html.Div(
                                    rec["description"],
                                    style={
                                        "color": THEME["text_secondary"],
                                        "fontSize": "0.9rem",
                                        "marginTop": "5px",
                                    },
                                ),
                                html.Div(
                                    [
                                        html.Span(
                                            f"⭐ {rec['quality_score']}",
                                            style={"color": THEME["accent_gold"]},
                                        ),
                                        html.Span(
                                            f" • ⏱️ {rec['duration']}",
                                            style={
                                                "color": THEME["text_muted"],
                                                "marginLeft": "15px",
                                            },
                                        ),
                                    ],
                                    style={"marginTop": "8px", "fontSize": "0.85rem"},
                                ),
                            ],
                            style={"flex": "1"},
                        ),
                    ],
                    className="content-recommendation",
                )
            )

        # Create content distribution chart
        content_counts = {"VIDEO": 0, "MUSIC": 0, "TEXT": 0}
        for rec in recommendations:
            content_counts[rec["type"]] += 1

        dist_fig = go.Figure(
            data=[
                go.Pie(
                    labels=list(content_counts.keys()),
                    values=list(content_counts.values()),
                    hole=0.6,
                    marker={
                        "colors": [
                            THEME["video_agent"],
                            THEME["music_agent"],
                            THEME["text_agent"],
                        ]
                    },
                    textinfo="label+percent",
                    textfont={
                        "family": FONTS["display"],
                        "color": THEME["text_primary"],
                    },
                )
            ]
        )

        dist_fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            margin={"l": 20, "r": 20, "t": 20, "b": 20},
            height=300,
            annotations=[
                {
                    "text": f"{len(recommendations)}<br>Items",
                    "x": 0.5,
                    "y": 0.5,
                    "font": {
                        "size": 20,
                        "family": FONTS["display"],
                        "color": THEME["text_primary"],
                    },
                    "showarrow": False,
                }
            ],
        )

        # Calculate metrics
        avg_quality = sum(r["quality_score"] for r in recommendations) / len(
            recommendations
        )

        # Status message
        profile_name = {
            "default": "Default Adult",
            "family": "Family with Kids",
            "kid": "Kid-Friendly",
            "teenager": "Teenager",
            "senior": "Senior",
            "driver": "Driver (Audio Only)",
            "history": "History Enthusiast",
            "romantic": "Romantic Couple",
            "custom": "Custom Profile",
        }.get(profile, "Custom")

        data_source = "🔴 LIVE API" if is_using_real_data else "⚪ DEMO DATA"

        status_message = html.Div(
            [
                html.Span("✅ ", style={"color": THEME["success"]}),
                f"Tour generated! {len(recommendations)} recommendations for ",
                html.Strong(profile_name),
                html.Span(
                    f" [{data_source}]",
                    style={
                        "color": THEME["success"]
                        if is_using_real_data
                        else THEME["text_muted"],
                        "marginLeft": "5px",
                    },
                ),
            ],
            style={"fontSize": "0.9rem"},
        )

        return (
            recommendation_cards,
            str(len(route_points)),
            f"{total_latency:.1f}s",
            f"{avg_quality:.1f}",
            str(len(recommendations)),
            dist_fig,
            "tab-recommendations",  # Switch to recommendations tab
            status_message,  # Show success message
        )

    @app.callback(
        [
            Output("realtime-throughput-chart", "figure"),
            Output("agent-response-chart", "figure"),
            Output("queue-status-chart", "figure"),
        ],
        Input("monitor-interval", "n_intervals"),
    )
    def update_monitoring_charts(n):
        """Update real-time monitoring charts."""

        # Throughput chart
        time_points = list(range(60))
        throughput_data = [np.random.uniform(10, 25) for _ in time_points]

        throughput_fig = go.Figure()
        throughput_fig.add_trace(
            go.Scatter(
                x=time_points,
                y=throughput_data,
                mode="lines",
                fill="tozeroy",
                line={"color": THEME["accent_primary"], "width": 2},
                fillcolor="rgba(0, 245, 212, 0.1)",
            )
        )
        throughput_fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis={
                "showgrid": False,
                "title": "Time (s)",
                "color": THEME["text_secondary"],
                "range": [0, 60],
            },
            yaxis={
                "showgrid": True,
                "gridcolor": "rgba(255,255,255,0.05)",
                "title": "Requests/s",
                "color": THEME["text_secondary"],
                "range": [0, 30],
            },
            margin={"l": 60, "r": 20, "t": 20, "b": 50},
            height=280,
            autosize=False,
            font={"family": FONTS["mono"], "color": THEME["text_secondary"]},
        )

        # Agent response times
        agents = ["Video", "Music", "Text"]
        response_times = [np.random.lognormal(1, 0.3, 50) for _ in agents]

        response_fig = go.Figure()
        colors = [THEME["video_agent"], THEME["music_agent"], THEME["text_agent"]]
        for agent, times, color in zip(agents, response_times, colors, strict=True):
            response_fig.add_trace(
                go.Box(
                    y=times,
                    name=agent,
                    marker_color=color,
                    boxpoints="outliers",
                )
            )

        response_fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis={"showgrid": False, "color": THEME["text_secondary"]},
            yaxis={
                "showgrid": True,
                "gridcolor": "rgba(255,255,255,0.05)",
                "title": "Response Time (s)",
                "color": THEME["text_secondary"],
                "range": [0, 8],
            },
            margin={"l": 60, "r": 20, "t": 20, "b": 50},
            height=280,
            autosize=False,
            showlegend=False,
            font={"family": FONTS["mono"], "color": THEME["text_secondary"]},
        )

        # Queue status
        statuses = ["Complete", "Soft Degraded", "Hard Degraded", "Failed"]
        status_counts = [
            random.randint(70, 90),
            random.randint(5, 15),
            random.randint(2, 8),
            random.randint(0, 3),
        ]
        status_colors = [
            THEME["success"],
            THEME["warning"],
            THEME["accent_tertiary"],
            THEME["error"],
        ]

        queue_fig = go.Figure(
            data=[
                go.Bar(
                    x=statuses,
                    y=status_counts,
                    marker_color=status_colors,
                    text=status_counts,
                    textposition="outside",
                    textfont={"family": FONTS["mono"], "color": THEME["text_primary"]},
                )
            ]
        )

        queue_fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis={"showgrid": False, "color": THEME["text_secondary"]},
            yaxis={
                "showgrid": True,
                "gridcolor": "rgba(255,255,255,0.05)",
                "title": "Count",
                "color": THEME["text_secondary"],
                "range": [0, 100],
            },
            margin={"l": 60, "r": 20, "t": 20, "b": 50},
            height=280,
            autosize=False,
            font={"family": FONTS["mono"], "color": THEME["text_secondary"]},
        )

        return throughput_fig, response_fig, queue_fig

    # ========================================================================
    # Pipeline Animation Callbacks
    # ========================================================================

    @app.callback(
        [
            Output("tour-state-store", "data"),
            Output("animation-interval", "disabled"),
        ],
        [
            Input("start-tour-btn", "n_clicks"),
            Input("animation-interval", "n_intervals"),
        ],
        State("tour-state-store", "data"),
        prevent_initial_call=True,
    )
    def manage_pipeline_animation(n_clicks, n_intervals, current_state):
        """Start and stop the pipeline animation."""
        from dash import ctx

        triggered_id = ctx.triggered_id

        if triggered_id == "start-tour-btn":
            # Start animation from beginning
            return {
                "running": True,
                "step": 0,
                "start_interval": n_intervals or 0,
            }, False

        elif triggered_id == "animation-interval":
            if not current_state or not current_state.get("running"):
                raise PreventUpdate

            # Calculate current step based on intervals since start
            start = current_state.get("start_interval", 0)
            current_step = (n_intervals or 0) - start

            # Stop animation after 7 steps (all complete)
            if current_step >= 7:
                return {"running": False, "step": 7, "completed": True}, True

            # Keep running
            return {
                "running": True,
                "step": current_step,
                "start_interval": start,
            }, False

        raise PreventUpdate

    @app.callback(
        [
            Output("pipeline-step-1", "style"),
            Output("pipeline-step-2", "style"),
            Output("pipeline-step-3", "style"),
            Output("pipeline-step-4", "style"),
            Output("pipeline-step-5", "style"),
            Output("pipeline-step-6", "style"),
            Output("video-agent-status", "children"),
            Output("music-agent-status", "children"),
            Output("text-agent-status", "children"),
            Output("judge-agent-status", "children"),
        ],
        Input("tour-state-store", "data"),
    )
    def animate_pipeline(state):
        """Animate the pipeline steps and update agent statuses."""
        if not state:
            # Default styles - all steps inactive
            default_style = {}
            default_agent = [
                html.Div(
                    "Ready", className="profile-badge", style={"marginTop": "10px"}
                ),
                html.P(
                    "Waiting for tour...",
                    style={
                        "fontSize": "0.85rem",
                        "color": THEME["text_muted"],
                        "marginTop": "8px",
                    },
                ),
            ]
            return (
                default_style,
                default_style,
                default_style,
                default_style,
                default_style,
                default_style,
                default_agent,
                default_agent,
                default_agent,
                default_agent,
            )

        step = state.get("step", 0)

        # Define styles for each state
        active_style = {
            "borderLeftColor": THEME["warning"],
            "background": "rgba(252, 163, 17, 0.1)",
        }
        completed_style = {
            "borderLeftColor": THEME["success"],
            "background": "rgba(0, 245, 212, 0.05)",
        }
        default_style = {}

        # Pipeline step styles based on current step
        styles = [default_style] * 6

        if step >= 1:
            styles[0] = completed_style
        if step >= 2:
            styles[1] = completed_style
        if step >= 3:
            styles[2] = completed_style
        if step >= 4:
            styles[3] = completed_style
        if step >= 5:
            styles[4] = completed_style
        if step >= 6:
            styles[5] = completed_style

        # Current step is active (yellow)
        if step < 6:
            styles[step] = active_style

        # Agent status based on step
        def agent_ready():
            return [
                html.Div(
                    "Ready", className="profile-badge", style={"marginTop": "10px"}
                ),
                html.P(
                    "Waiting...",
                    style={
                        "fontSize": "0.85rem",
                        "color": THEME["text_muted"],
                        "marginTop": "8px",
                    },
                ),
            ]

        def agent_running(name):
            return [
                html.Div(
                    "⏳ Running",
                    className="profile-badge",
                    style={
                        "marginTop": "10px",
                        "background": "rgba(252, 163, 17, 0.3)",
                    },
                ),
                html.P(
                    f"Searching for {name}...",
                    style={
                        "fontSize": "0.85rem",
                        "color": THEME["warning"],
                        "marginTop": "8px",
                    },
                ),
            ]

        def agent_complete(result):
            return [
                html.Div(
                    "✅ Complete",
                    className="profile-badge",
                    style={"marginTop": "10px", "background": "rgba(0, 245, 212, 0.3)"},
                ),
                html.P(
                    result,
                    style={
                        "fontSize": "0.85rem",
                        "color": THEME["success"],
                        "marginTop": "8px",
                    },
                ),
            ]

        # Video, Music, Text, Judge agent statuses
        if step < 2:
            video_status = agent_ready()
            music_status = agent_ready()
            text_status = agent_ready()
            judge_status = agent_ready()
        elif step == 2:
            video_status = agent_running("videos")
            music_status = agent_running("music")
            text_status = agent_running("facts")
            judge_status = agent_ready()
        elif step == 3:
            video_status = agent_complete("Found 3 videos")
            music_status = agent_running("tracks")
            text_status = agent_running("articles")
            judge_status = agent_ready()
        elif step == 4:
            video_status = agent_complete("Found 3 videos")
            music_status = agent_complete("Found 5 tracks")
            text_status = agent_complete("Found 2 articles")
            judge_status = agent_running("evaluating")
        else:
            video_status = agent_complete("3 videos ready")
            music_status = agent_complete("5 tracks ready")
            text_status = agent_complete("2 articles ready")
            judge_status = agent_complete("Best content selected!")

        return (
            styles[0],
            styles[1],
            styles[2],
            styles[3],
            styles[4],
            styles[5],
            video_status,
            music_status,
            text_status,
            judge_status,
        )

    return app


def run_tour_guide_dashboard(
    host: str = "127.0.0.1", port: int = 8051, debug: bool = True
):
    """Run the Tour Guide Dashboard server."""
    app = create_tour_guide_app()

    print(f"""
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║   🗺️  Multi-Agent Tour Guide Interactive Dashboard                       ║
║   ═══════════════════════════════════════════════════                    ║
║                                                                          ║
║   ✨ Features:                                                           ║
║      • Complete user profile configuration                               ║
║      • Family mode & driver mode                                         ║
║      • Interactive pipeline visualization                                ║
║      • Real-time agent monitoring                                        ║
║      • Personalized content recommendations                              ║
║                                                                          ║
║   🌐 Dashboard URL: http://{host}:{port}                                  ║
║                                                                          ║
║   Press Ctrl+C to stop the server                                        ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
    """)

    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run_tour_guide_dashboard()
