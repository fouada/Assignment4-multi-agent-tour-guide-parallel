"""
🗺️ Multi-Agent Tour Guide Interactive Dashboard
================================================

A comprehensive, publication-quality interactive dashboard for the
Multi-Agent Tour Guide System with full pipeline visualization.

Features:
- Interactive tour planning with source/destination inputs
- Complete user profile configuration (family, age, preferences)
- Real-time pipeline flow visualization
- Animated agent orchestration display
- Personalized content recommendations
- System architecture visualization

Author: Multi-Agent Tour Guide Research Team
Version: 2.0.0
Date: December 2025
"""

from __future__ import annotations

import random
from enum import Enum

import numpy as np
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

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
}}

.Select-option {{
    background: transparent !important;
    color: {THEME["text_primary"]} !important;
}}

.Select-option.is-focused {{
    background: rgba(0, 245, 212, 0.1) !important;
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
    """Create the dashboard header."""
    return html.Div(
        [
            html.H1("🗺️ Multi-Agent Tour Guide", className="header-title"),
            html.P(
                "INTELLIGENT · PARALLEL · PERSONALIZED", className="header-subtitle"
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
            dcc.Store(id="tour-state-store", data={}),
            dcc.Store(id="profile-state-store", data={}),
            dcc.Store(id="results-store", data=[]),
            # Interval for animations
            dcc.Interval(
                id="animation-interval", interval=1000, n_intervals=0, disabled=True
            ),
            html.Div(
                [
                    # Header
                    create_header(),
                    # Main content area
                    dcc.Tabs(
                        [
                            # Tab 1: Tour Planning
                            dcc.Tab(
                                label="🗺️ Plan Your Tour",
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
                                                                        "🚀 Start Tour",
                                                                        id="start-tour-btn",
                                                                        className="btn-primary",
                                                                        style={
                                                                            "width": "100%",
                                                                            "marginTop": "10px",
                                                                        },
                                                                    ),
                                                                ]
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
        """Simulate the tour guide pipeline and generate recommendations."""
        if not n_clicks:
            raise PreventUpdate

        # Simulate route points
        mock_points = [
            {"name": source or "Starting Point", "lat": 32.0853, "lon": 34.7818},
            {"name": "Latrun Monastery", "lat": 31.8377, "lon": 34.9781},
            {"name": "Bab al-Wad Memorial", "lat": 31.8419, "lon": 35.0614},
            {"name": "Ein Karem", "lat": 31.7667, "lon": 35.1583},
            {"name": dest or "Destination", "lat": 31.7683, "lon": 35.2137},
        ]

        # Determine content types based on profile
        is_driver = driver_mode and "enabled" in driver_mode
        is_family = family_mode and "enabled" in family_mode

        content_types = ["TEXT", "MUSIC", "TEXT"]
        if not is_driver:
            content_types.append("VIDEO")

        # Generate mock recommendations
        recommendations = []
        for point in mock_points:
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
                }
            )

        # Create recommendation cards
        recommendation_cards = []
        for rec in recommendations:
            icon_class = rec["type"].lower()
            icon = {"VIDEO": "🎬", "MUSIC": "🎵", "TEXT": "📖"}.get(rec["type"], "📌")

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

        return (
            recommendation_cards,
            str(len(mock_points)),
            f"{random.uniform(2, 5):.1f}s",
            f"{avg_quality:.1f}",
            str(len(recommendations)),
            dist_fig,
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
            },
            yaxis={
                "showgrid": True,
                "gridcolor": "rgba(255,255,255,0.05)",
                "title": "Requests/s",
                "color": THEME["text_secondary"],
            },
            margin={"l": 50, "r": 20, "t": 20, "b": 50},
            height=250,
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
            },
            margin={"l": 50, "r": 20, "t": 20, "b": 50},
            height=250,
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
            },
            margin={"l": 50, "r": 20, "t": 20, "b": 50},
            height=300,
            font={"family": FONTS["mono"], "color": THEME["text_secondary"]},
        )

        return throughput_fig, response_fig, queue_fig

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
