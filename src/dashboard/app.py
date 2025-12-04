"""
MIT-Level Interactive Research Dashboard
========================================

A stunning, publication-quality interactive dashboard for the
Multi-Agent Tour Guide System research analysis.

Features:
- Real-time system monitoring with live updates
- Interactive parameter exploration
- Statistical comparison tools
- Monte Carlo simulation controls
- Publication-quality visualizations

API MODE STRATEGY:
------------------
This Research Dashboard ALWAYS uses SIMULATED/MOCKED data.
This is intentional for:
- Reproducible statistical experiments
- Fast Monte Carlo simulations (10,000+ runs)
- Parameter sensitivity analysis
- No API costs for research

For REAL API calls, use the Tour Guide Dashboard instead.
See docs/API_STRATEGY.md for full documentation.

Author: Multi-Agent Tour Guide Research Team
Version: 1.0.0
Date: November 2025
"""

from __future__ import annotations

import numpy as np
from dash import Dash, Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

from .components import (
    COLORS,
    AgentPerformancePanel,
    MonteCarloPanel,
    ParetoFrontierPanel,
    SensitivityPanel,
    StatisticalComparisonPanel,
    SystemMonitorPanel,
)
from .data_manager import DashboardDataManager, QueueConfig

# ============================================================================
# Custom CSS Styles - Sophisticated dark theme
# ============================================================================

CUSTOM_STYLES = """
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --bg-primary: #0f0f1a;
    --bg-secondary: #1a1a2e;
    --bg-card: #16213e;
    --accent-primary: #e94560;
    --accent-secondary: #0f3460;
    --text-primary: #e0e0e0;
    --text-secondary: #b0b0b0;
    --success: #00d9a5;
    --warning: #ffc107;
    --danger: #dc3545;
    --gradient-start: #667eea;
    --gradient-end: #764ba2;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
    color: var(--text-primary);
    margin: 0;
    padding: 0;
    min-height: 100vh;
}

.dashboard-container {
    max-width: 1800px;
    margin: 0 auto;
    padding: 20px;
}

.dashboard-header {
    text-align: center;
    padding: 30px 0;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    margin-bottom: 30px;
}

.dashboard-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2.5rem;
    font-weight: 600;
    background: linear-gradient(90deg, var(--gradient-start), var(--gradient-end), var(--accent-primary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 10px 0;
}

.dashboard-subtitle {
    font-size: 1rem;
    color: var(--text-secondary);
    font-weight: 300;
}

.card {
    background: linear-gradient(145deg, var(--bg-card), var(--bg-secondary));
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
    border: 1px solid rgba(255,255,255,0.05);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    backdrop-filter: blur(4px);
}

.card-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.1rem;
    font-weight: 500;
    color: var(--text-primary);
    margin: 0 0 15px 0;
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(255,255,255,0.1);
}

.tab-container {
    margin-bottom: 20px;
}

.custom-tabs {
    border: none !important;
}

.custom-tab {
    font-family: 'JetBrains Mono', monospace !important;
    background: var(--bg-card) !important;
    border: none !important;
    color: var(--text-secondary) !important;
    padding: 15px 25px !important;
    border-radius: 10px 10px 0 0 !important;
    margin-right: 5px !important;
    transition: all 0.3s ease !important;
}

.custom-tab--selected {
    background: linear-gradient(135deg, var(--accent-secondary), var(--bg-card)) !important;
    color: var(--text-primary) !important;
    border-bottom: 3px solid var(--accent-primary) !important;
}

.control-panel {
    background: rgba(15, 52, 96, 0.5);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
}

.slider-container {
    margin: 15px 0;
}

.slider-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
    color: var(--text-secondary);
    margin-bottom: 8px;
}

.rc-slider-rail {
    background: rgba(255,255,255,0.1) !important;
}

.rc-slider-track {
    background: linear-gradient(90deg, var(--gradient-start), var(--accent-primary)) !important;
}

.rc-slider-handle {
    border-color: var(--accent-primary) !important;
    background: var(--bg-card) !important;
}

.btn-primary {
    background: linear-gradient(135deg, var(--accent-primary), var(--gradient-end));
    border: none;
    color: white;
    padding: 12px 30px;
    border-radius: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(233, 69, 96, 0.3);
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(233, 69, 96, 0.4);
}

.metric-card {
    background: linear-gradient(145deg, var(--bg-card), var(--accent-secondary));
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.05);
}

.metric-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2rem;
    font-weight: 600;
    color: var(--text-primary);
}

.metric-label {
    font-size: 0.85rem;
    color: var(--text-secondary);
    margin-top: 5px;
}

.status-indicator {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    margin-right: 8px;
    animation: pulse 2s infinite;
}

.status-healthy { background: var(--success); }
.status-warning { background: var(--warning); }
.status-critical { background: var(--danger); }

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

.grid-2 {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
}

.grid-3 {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
}

.grid-4 {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 15px;
}

@media (max-width: 1200px) {
    .grid-2, .grid-3, .grid-4 {
        grid-template-columns: 1fr;
    }
}

.loading-spinner {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 200px;
}

.spinner {
    width: 50px;
    height: 50px;
    border: 3px solid rgba(255,255,255,0.1);
    border-top-color: var(--accent-primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

/* Dropdown styling */
.Select-control {
    background: var(--bg-card) !important;
    border-color: rgba(255,255,255,0.1) !important;
}

.Select-menu-outer {
    background: var(--bg-card) !important;
}

.Select-option {
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
}

.Select-option:hover {
    background: var(--accent-secondary) !important;
}

/* Input styling */
input[type="number"] {
    background: var(--bg-card);
    border: 1px solid rgba(255,255,255,0.1);
    color: var(--text-primary);
    padding: 10px;
    border-radius: 8px;
    font-family: 'JetBrains Mono', monospace;
}
"""


def create_app() -> Dash:
    """Create and configure the Dash application."""

    app = Dash(
        __name__,
        title="🗺️ MIT Research Dashboard | Multi-Agent Tour Guide",
        suppress_callback_exceptions=True,
        meta_tags=[
            {"name": "viewport", "content": "width=device-width, initial-scale=1"}
        ],
    )

    # Initialize data manager
    data_manager = DashboardDataManager()

    # ========================================================================
    # Layout Definition
    # ========================================================================

    # External stylesheets and custom CSS
    app.index_string = f"""
    <!DOCTYPE html>
    <html>
        <head>
            {{%metas%}}
            <title>{{%title%}}</title>
            {{%favicon%}}
            {{%css%}}
            <style>{CUSTOM_STYLES}</style>
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

    app.layout = html.Div(
        [
            # Store components for data persistence
            dcc.Store(id="simulation-data-store"),
            dcc.Store(id="comparison-data-store"),
            dcc.Store(id="sensitivity-data-store"),
            # Interval for real-time updates
            dcc.Interval(id="interval-component", interval=2000, n_intervals=0),
            html.Div(
                [
                    # Header
                    html.Div(
                        [
                            html.H1(
                                "🗺️ Multi-Agent Tour Guide", className="dashboard-title"
                            ),
                            html.P(
                                "MIT-Level Research Dashboard | Parallel Processing Analysis",
                                className="dashboard-subtitle",
                            ),
                        ],
                        className="dashboard-header",
                    ),
                    # Main tabs
                    dcc.Tabs(
                        [
                            # ============================================================
                            # Tab 1: System Monitor
                            # ============================================================
                            dcc.Tab(
                                label="📊 System Monitor",
                                className="custom-tab",
                                selected_className="custom-tab--selected",
                                children=[
                                    html.Div(
                                        [
                                            # Real-time metrics row
                                            html.Div(
                                                [
                                                    html.Div(
                                                        [
                                                            html.Div(
                                                                id="metric-active-tours",
                                                                className="metric-value",
                                                            ),
                                                            html.Div(
                                                                "Active Tours",
                                                                className="metric-label",
                                                            ),
                                                        ],
                                                        className="metric-card",
                                                    ),
                                                    html.Div(
                                                        [
                                                            html.Div(
                                                                id="metric-queue-depth",
                                                                className="metric-value",
                                                            ),
                                                            html.Div(
                                                                "Queue Depth",
                                                                className="metric-label",
                                                            ),
                                                        ],
                                                        className="metric-card",
                                                    ),
                                                    html.Div(
                                                        [
                                                            html.Div(
                                                                id="metric-throughput",
                                                                className="metric-value",
                                                            ),
                                                            html.Div(
                                                                "Throughput (req/s)",
                                                                className="metric-label",
                                                            ),
                                                        ],
                                                        className="metric-card",
                                                    ),
                                                    html.Div(
                                                        [
                                                            html.Div(
                                                                id="metric-error-rate",
                                                                className="metric-value",
                                                            ),
                                                            html.Div(
                                                                "Error Rate",
                                                                className="metric-label",
                                                            ),
                                                        ],
                                                        className="metric-card",
                                                    ),
                                                ],
                                                className="grid-4",
                                            ),
                                            # Agent status cards
                                            html.Div(
                                                [
                                                    dcc.Graph(
                                                        id="agent-status-graph",
                                                        config={
                                                            "displayModeBar": False
                                                        },
                                                    ),
                                                ],
                                                className="card",
                                            ),
                                            # Charts row
                                            html.Div(
                                                [
                                                    html.Div(
                                                        [
                                                            dcc.Graph(
                                                                id="throughput-chart",
                                                                config={
                                                                    "displayModeBar": False
                                                                },
                                                            ),
                                                        ],
                                                        className="card",
                                                    ),
                                                    html.Div(
                                                        [
                                                            dcc.Graph(
                                                                id="queue-depth-chart",
                                                                config={
                                                                    "displayModeBar": False
                                                                },
                                                            ),
                                                        ],
                                                        className="card",
                                                    ),
                                                ],
                                                className="grid-2",
                                            ),
                                        ],
                                        style={"padding": "20px"},
                                    ),
                                ],
                            ),
                            # ============================================================
                            # Tab 2: Sensitivity Analysis
                            # ============================================================
                            dcc.Tab(
                                label="🔬 Sensitivity Analysis",
                                className="custom-tab",
                                selected_className="custom-tab--selected",
                                children=[
                                    html.Div(
                                        [
                                            # Control panel
                                            html.Div(
                                                [
                                                    html.H4(
                                                        "🎛️ Analysis Controls",
                                                        className="card-title",
                                                    ),
                                                    html.Div(
                                                        [
                                                            html.Div(
                                                                [
                                                                    html.Label(
                                                                        "Parameter to Analyze",
                                                                        className="slider-label",
                                                                    ),
                                                                    dcc.Dropdown(
                                                                        id="sensitivity-param-dropdown",
                                                                        options=[
                                                                            {
                                                                                "label": "Soft Timeout",
                                                                                "value": "soft_timeout",
                                                                            },
                                                                            {
                                                                                "label": "Hard Timeout",
                                                                                "value": "hard_timeout",
                                                                            },
                                                                        ],
                                                                        value="soft_timeout",
                                                                        style={
                                                                            "backgroundColor": COLORS[
                                                                                "secondary"
                                                                            ]
                                                                        },
                                                                    ),
                                                                ],
                                                                style={
                                                                    "flex": 1,
                                                                    "marginRight": "20px",
                                                                },
                                                            ),
                                                            html.Div(
                                                                [
                                                                    html.Label(
                                                                        "Parameter Range",
                                                                        className="slider-label",
                                                                    ),
                                                                    dcc.RangeSlider(
                                                                        id="sensitivity-range-slider",
                                                                        min=1,
                                                                        max=60,
                                                                        step=1,
                                                                        value=[5, 30],
                                                                        marks={
                                                                            i: f"{i}s"
                                                                            for i in range(
                                                                                0,
                                                                                65,
                                                                                10,
                                                                            )
                                                                        },
                                                                        tooltip={
                                                                            "placement": "bottom",
                                                                            "always_visible": True,
                                                                        },
                                                                    ),
                                                                ],
                                                                style={
                                                                    "flex": 2,
                                                                    "marginRight": "20px",
                                                                },
                                                            ),
                                                            html.Div(
                                                                [
                                                                    html.Label(
                                                                        "Simulations per Point",
                                                                        className="slider-label",
                                                                    ),
                                                                    dcc.Input(
                                                                        id="sensitivity-n-sims",
                                                                        type="number",
                                                                        value=2000,
                                                                        min=100,
                                                                        max=10000,
                                                                        step=100,
                                                                    ),
                                                                ],
                                                                style={
                                                                    "flex": 1,
                                                                    "marginRight": "20px",
                                                                },
                                                            ),
                                                            html.Button(
                                                                "🚀 Run Analysis",
                                                                id="run-sensitivity-btn",
                                                                className="btn-primary",
                                                            ),
                                                        ],
                                                        style={
                                                            "display": "flex",
                                                            "alignItems": "flex-end",
                                                            "flexWrap": "wrap",
                                                            "gap": "15px",
                                                        },
                                                    ),
                                                ],
                                                className="control-panel",
                                            ),
                                            # Progress indicator
                                            html.Div(
                                                id="sensitivity-progress",
                                                style={"marginBottom": "20px"},
                                            ),
                                            # Results
                                            html.Div(
                                                [
                                                    dcc.Loading(
                                                        dcc.Graph(
                                                            id="sensitivity-results-graph"
                                                        ),
                                                        type="circle",
                                                        color=COLORS["highlight"],
                                                    ),
                                                ],
                                                className="card",
                                            ),
                                            # Tornado chart
                                            html.Div(
                                                [
                                                    dcc.Graph(id="tornado-chart"),
                                                ],
                                                className="card",
                                            ),
                                        ],
                                        style={"padding": "20px"},
                                    ),
                                ],
                            ),
                            # ============================================================
                            # Tab 3: Pareto Frontier
                            # ============================================================
                            dcc.Tab(
                                label="🎯 Pareto Explorer",
                                className="custom-tab",
                                selected_className="custom-tab--selected",
                                children=[
                                    html.Div(
                                        [
                                            # Controls
                                            html.Div(
                                                [
                                                    html.H4(
                                                        "🗻 Pareto Frontier Controls",
                                                        className="card-title",
                                                    ),
                                                    html.Div(
                                                        [
                                                            html.Div(
                                                                [
                                                                    html.Label(
                                                                        "Soft Timeout Range",
                                                                        className="slider-label",
                                                                    ),
                                                                    dcc.RangeSlider(
                                                                        id="pareto-soft-range",
                                                                        min=1,
                                                                        max=40,
                                                                        step=1,
                                                                        value=[5, 30],
                                                                        marks={
                                                                            i: f"{i}s"
                                                                            for i in range(
                                                                                0,
                                                                                45,
                                                                                10,
                                                                            )
                                                                        },
                                                                    ),
                                                                ],
                                                                style={
                                                                    "flex": 1,
                                                                    "marginRight": "30px",
                                                                },
                                                            ),
                                                            html.Div(
                                                                [
                                                                    html.Label(
                                                                        "Hard Timeout Range",
                                                                        className="slider-label",
                                                                    ),
                                                                    dcc.RangeSlider(
                                                                        id="pareto-hard-range",
                                                                        min=5,
                                                                        max=80,
                                                                        step=1,
                                                                        value=[10, 60],
                                                                        marks={
                                                                            i: f"{i}s"
                                                                            for i in range(
                                                                                0,
                                                                                85,
                                                                                20,
                                                                            )
                                                                        },
                                                                    ),
                                                                ],
                                                                style={
                                                                    "flex": 1,
                                                                    "marginRight": "30px",
                                                                },
                                                            ),
                                                            html.Button(
                                                                "🗺️ Generate Pareto",
                                                                id="run-pareto-btn",
                                                                className="btn-primary",
                                                            ),
                                                        ],
                                                        style={
                                                            "display": "flex",
                                                            "alignItems": "flex-end",
                                                            "gap": "20px",
                                                        },
                                                    ),
                                                ],
                                                className="control-panel",
                                            ),
                                            # Visualizations
                                            html.Div(
                                                [
                                                    html.Div(
                                                        [
                                                            dcc.Loading(
                                                                dcc.Graph(
                                                                    id="pareto-3d-surface"
                                                                ),
                                                                type="circle",
                                                                color=COLORS[
                                                                    "highlight"
                                                                ],
                                                            ),
                                                        ],
                                                        className="card",
                                                    ),
                                                    html.Div(
                                                        [
                                                            dcc.Loading(
                                                                dcc.Graph(
                                                                    id="pareto-scatter"
                                                                ),
                                                                type="circle",
                                                                color=COLORS[
                                                                    "highlight"
                                                                ],
                                                            ),
                                                        ],
                                                        className="card",
                                                    ),
                                                ],
                                                className="grid-2",
                                            ),
                                            html.Div(
                                                [
                                                    dcc.Graph(id="pareto-heatmap"),
                                                ],
                                                className="card",
                                            ),
                                        ],
                                        style={"padding": "20px"},
                                    ),
                                ],
                            ),
                            # ============================================================
                            # Tab 4: Statistical Comparison
                            # ============================================================
                            dcc.Tab(
                                label="📐 A/B Testing",
                                className="custom-tab",
                                selected_className="custom-tab--selected",
                                children=[
                                    html.Div(
                                        [
                                            # Configuration panels
                                            html.Div(
                                                [
                                                    html.H4(
                                                        "⚖️ Configuration Comparison",
                                                        className="card-title",
                                                    ),
                                                    html.Div(
                                                        [
                                                            # Config A
                                                            html.Div(
                                                                [
                                                                    html.H5(
                                                                        "Configuration A",
                                                                        style={
                                                                            "color": COLORS[
                                                                                "comparison"
                                                                            ][0]
                                                                        },
                                                                    ),
                                                                    html.Label(
                                                                        "Soft Timeout (s)",
                                                                        className="slider-label",
                                                                    ),
                                                                    dcc.Input(
                                                                        id="config-a-soft",
                                                                        type="number",
                                                                        value=15,
                                                                        min=1,
                                                                        max=60,
                                                                    ),
                                                                    html.Label(
                                                                        "Hard Timeout (s)",
                                                                        className="slider-label",
                                                                        style={
                                                                            "marginTop": "10px"
                                                                        },
                                                                    ),
                                                                    dcc.Input(
                                                                        id="config-a-hard",
                                                                        type="number",
                                                                        value=30,
                                                                        min=5,
                                                                        max=120,
                                                                    ),
                                                                ],
                                                                className="card",
                                                                style={"flex": 1},
                                                            ),
                                                            # VS indicator
                                                            html.Div(
                                                                [
                                                                    html.Span(
                                                                        "VS",
                                                                        style={
                                                                            "fontSize": "2rem",
                                                                            "fontWeight": "700",
                                                                            "background": f"linear-gradient(135deg, {COLORS['comparison'][0]}, {COLORS['comparison'][1]})",
                                                                            "-webkit-background-clip": "text",
                                                                            "-webkit-text-fill-color": "transparent",
                                                                        },
                                                                    ),
                                                                ],
                                                                style={
                                                                    "display": "flex",
                                                                    "alignItems": "center",
                                                                    "justifyContent": "center",
                                                                    "padding": "20px",
                                                                },
                                                            ),
                                                            # Config B
                                                            html.Div(
                                                                [
                                                                    html.H5(
                                                                        "Configuration B",
                                                                        style={
                                                                            "color": COLORS[
                                                                                "comparison"
                                                                            ][1]
                                                                        },
                                                                    ),
                                                                    html.Label(
                                                                        "Soft Timeout (s)",
                                                                        className="slider-label",
                                                                    ),
                                                                    dcc.Input(
                                                                        id="config-b-soft",
                                                                        type="number",
                                                                        value=8,
                                                                        min=1,
                                                                        max=60,
                                                                    ),
                                                                    html.Label(
                                                                        "Hard Timeout (s)",
                                                                        className="slider-label",
                                                                        style={
                                                                            "marginTop": "10px"
                                                                        },
                                                                    ),
                                                                    dcc.Input(
                                                                        id="config-b-hard",
                                                                        type="number",
                                                                        value=15,
                                                                        min=5,
                                                                        max=120,
                                                                    ),
                                                                ],
                                                                className="card",
                                                                style={"flex": 1},
                                                            ),
                                                        ],
                                                        style={
                                                            "display": "flex",
                                                            "gap": "20px",
                                                            "alignItems": "stretch",
                                                        },
                                                    ),
                                                    html.Div(
                                                        [
                                                            html.Label(
                                                                "Simulations per Config",
                                                                className="slider-label",
                                                            ),
                                                            dcc.Input(
                                                                id="comparison-n-sims",
                                                                type="number",
                                                                value=5000,
                                                                min=1000,
                                                                max=20000,
                                                                step=1000,
                                                            ),
                                                            html.Button(
                                                                "⚡ Compare",
                                                                id="run-comparison-btn",
                                                                className="btn-primary",
                                                                style={
                                                                    "marginLeft": "20px"
                                                                },
                                                            ),
                                                        ],
                                                        style={
                                                            "marginTop": "20px",
                                                            "display": "flex",
                                                            "alignItems": "flex-end",
                                                        },
                                                    ),
                                                ],
                                                className="control-panel",
                                            ),
                                            # Results
                                            html.Div(
                                                [
                                                    dcc.Loading(
                                                        dcc.Graph(
                                                            id="comparison-distributions"
                                                        ),
                                                        type="circle",
                                                        color=COLORS["highlight"],
                                                    ),
                                                ],
                                                className="card",
                                            ),
                                            html.Div(
                                                [
                                                    html.Div(
                                                        [
                                                            dcc.Graph(
                                                                id="effect-size-chart"
                                                            ),
                                                        ],
                                                        className="card",
                                                    ),
                                                    html.Div(
                                                        [
                                                            dcc.Graph(
                                                                id="significance-summary"
                                                            ),
                                                        ],
                                                        className="card",
                                                    ),
                                                ],
                                                className="grid-2",
                                            ),
                                        ],
                                        style={"padding": "20px"},
                                    ),
                                ],
                            ),
                            # ============================================================
                            # Tab 5: Monte Carlo
                            # ============================================================
                            dcc.Tab(
                                label="🎲 Monte Carlo",
                                className="custom-tab",
                                selected_className="custom-tab--selected",
                                children=[
                                    html.Div(
                                        [
                                            # Controls
                                            html.Div(
                                                [
                                                    html.H4(
                                                        "🎲 Monte Carlo Simulation",
                                                        className="card-title",
                                                    ),
                                                    html.Div(
                                                        [
                                                            html.Div(
                                                                [
                                                                    html.Label(
                                                                        "Soft Timeout (s)",
                                                                        className="slider-label",
                                                                    ),
                                                                    dcc.Slider(
                                                                        id="mc-soft-timeout",
                                                                        min=1,
                                                                        max=40,
                                                                        step=1,
                                                                        value=15,
                                                                        marks={
                                                                            i: f"{i}"
                                                                            for i in range(
                                                                                0,
                                                                                45,
                                                                                10,
                                                                            )
                                                                        },
                                                                    ),
                                                                ],
                                                                style={
                                                                    "flex": 1,
                                                                    "marginRight": "30px",
                                                                },
                                                            ),
                                                            html.Div(
                                                                [
                                                                    html.Label(
                                                                        "Hard Timeout (s)",
                                                                        className="slider-label",
                                                                    ),
                                                                    dcc.Slider(
                                                                        id="mc-hard-timeout",
                                                                        min=5,
                                                                        max=80,
                                                                        step=1,
                                                                        value=30,
                                                                        marks={
                                                                            i: f"{i}"
                                                                            for i in range(
                                                                                0,
                                                                                85,
                                                                                20,
                                                                            )
                                                                        },
                                                                    ),
                                                                ],
                                                                style={
                                                                    "flex": 1,
                                                                    "marginRight": "30px",
                                                                },
                                                            ),
                                                            html.Div(
                                                                [
                                                                    html.Label(
                                                                        "Number of Simulations",
                                                                        className="slider-label",
                                                                    ),
                                                                    dcc.Input(
                                                                        id="mc-n-sims",
                                                                        type="number",
                                                                        value=5000,
                                                                        min=100,
                                                                        max=50000,
                                                                        step=1000,
                                                                    ),
                                                                ],
                                                                style={
                                                                    "marginRight": "20px"
                                                                },
                                                            ),
                                                            html.Button(
                                                                "🎲 Run Simulation",
                                                                id="run-mc-btn",
                                                                className="btn-primary",
                                                            ),
                                                        ],
                                                        style={
                                                            "display": "flex",
                                                            "alignItems": "flex-end",
                                                            "flexWrap": "wrap",
                                                            "gap": "20px",
                                                        },
                                                    ),
                                                ],
                                                className="control-panel",
                                            ),
                                            # Summary stats
                                            html.Div(
                                                id="mc-summary-stats",
                                                className="grid-4",
                                                style={"marginBottom": "20px"},
                                            ),
                                            # Main results
                                            html.Div(
                                                [
                                                    dcc.Loading(
                                                        dcc.Graph(
                                                            id="mc-results-graph"
                                                        ),
                                                        type="circle",
                                                        color=COLORS["highlight"],
                                                    ),
                                                ],
                                                className="card",
                                            ),
                                            # Additional analysis
                                            html.Div(
                                                [
                                                    html.Div(
                                                        [
                                                            dcc.Graph(
                                                                id="mc-agent-response"
                                                            ),
                                                        ],
                                                        className="card",
                                                    ),
                                                    html.Div(
                                                        [
                                                            dcc.Graph(
                                                                id="mc-agent-reliability"
                                                            ),
                                                        ],
                                                        className="card",
                                                    ),
                                                ],
                                                className="grid-2",
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
                className="dashboard-container",
            ),
        ]
    )

    # ========================================================================
    # Callbacks
    # ========================================================================

    @app.callback(
        [
            Output("metric-active-tours", "children"),
            Output("metric-queue-depth", "children"),
            Output("metric-throughput", "children"),
            Output("metric-error-rate", "children"),
            Output("agent-status-graph", "figure"),
            Output("throughput-chart", "figure"),
            Output("queue-depth-chart", "figure"),
        ],
        Input("interval-component", "n_intervals"),
    )
    def update_system_monitor(n):
        """Update real-time system monitoring."""
        metrics = data_manager.get_real_time_metrics()

        # Metrics cards
        active_tours = f"{metrics['active_tours']}"
        queue_depth = f"{metrics['queue_depth']}"
        throughput = f"{metrics['throughput']:.1f}"
        error_rate = f"{metrics['error_rate']:.1%}"

        # Agent status
        agent_fig = SystemMonitorPanel.create_agent_status_cards(metrics)

        # Generate history data (simulated)
        history = [
            {"timestamp": i, "throughput": np.random.uniform(5, 20)} for i in range(60)
        ]
        throughput_fig = SystemMonitorPanel.create_throughput_chart(history)

        depth_history = [np.random.randint(0, 20) for _ in range(60)]
        queue_fig = SystemMonitorPanel.create_queue_depth_chart(depth_history)

        return (
            active_tours,
            queue_depth,
            throughput,
            error_rate,
            agent_fig,
            throughput_fig,
            queue_fig,
        )

    @app.callback(
        [
            Output("sensitivity-results-graph", "figure"),
            Output("tornado-chart", "figure"),
            Output("sensitivity-data-store", "data"),
        ],
        Input("run-sensitivity-btn", "n_clicks"),
        [
            State("sensitivity-param-dropdown", "value"),
            State("sensitivity-range-slider", "value"),
            State("sensitivity-n-sims", "value"),
        ],
        prevent_initial_call=True,
    )
    def run_sensitivity_analysis(n_clicks, param, range_val, n_sims):
        """Run sensitivity analysis and update visualizations."""
        if not n_clicks:
            raise PreventUpdate

        param_values = np.linspace(range_val[0], range_val[1], 11).tolist()
        results_df = data_manager.run_sensitivity_analysis(param, param_values, n_sims)

        # Create visualizations
        results_fig = SensitivityPanel.create_parameter_impact_chart(results_df, param)

        # Calculate sensitivities for tornado chart
        sensitivities = {
            "Latency Impact": (
                results_df["latency_mean"].iloc[-1] - results_df["latency_mean"].iloc[0]
            )
            / results_df["latency_mean"].mean(),
            "Quality Impact": (
                results_df["quality_mean"].iloc[-1] - results_df["quality_mean"].iloc[0]
            )
            / results_df["quality_mean"].mean(),
            "Success Rate": (
                results_df["success_rate"].iloc[-1] - results_df["success_rate"].iloc[0]
            ),
            "Complete Rate": (
                results_df["complete_rate"].iloc[-1]
                - results_df["complete_rate"].iloc[0]
            ),
        }
        tornado_fig = SensitivityPanel.create_tornado_chart(sensitivities)

        return results_fig, tornado_fig, results_df.to_dict()

    @app.callback(
        [
            Output("pareto-3d-surface", "figure"),
            Output("pareto-scatter", "figure"),
            Output("pareto-heatmap", "figure"),
        ],
        Input("run-pareto-btn", "n_clicks"),
        [State("pareto-soft-range", "value"), State("pareto-hard-range", "value")],
        prevent_initial_call=True,
    )
    def run_pareto_analysis(n_clicks, soft_range, hard_range):
        """Generate Pareto frontier visualizations."""
        if not n_clicks:
            raise PreventUpdate

        data = data_manager.run_pareto_analysis(
            soft_timeout_range=tuple(soft_range),
            hard_timeout_range=tuple(hard_range),
            n_points=64,
            n_sims=500,
        )

        surface_fig = ParetoFrontierPanel.create_3d_pareto_surface(data)
        scatter_fig = ParetoFrontierPanel.create_pareto_scatter(data)
        heatmap_fig = ParetoFrontierPanel.create_heatmap(data)

        return surface_fig, scatter_fig, heatmap_fig

    @app.callback(
        [
            Output("comparison-distributions", "figure"),
            Output("effect-size-chart", "figure"),
            Output("significance-summary", "figure"),
            Output("comparison-data-store", "data"),
        ],
        Input("run-comparison-btn", "n_clicks"),
        [
            State("config-a-soft", "value"),
            State("config-a-hard", "value"),
            State("config-b-soft", "value"),
            State("config-b-hard", "value"),
            State("comparison-n-sims", "value"),
        ],
        prevent_initial_call=True,
    )
    def run_comparison(n_clicks, a_soft, a_hard, b_soft, b_hard, n_sims):
        """Run statistical comparison."""
        if not n_clicks:
            raise PreventUpdate

        config_a = QueueConfig(soft_timeout=a_soft, hard_timeout=a_hard)
        config_b = QueueConfig(soft_timeout=b_soft, hard_timeout=b_hard)

        comparison = data_manager.compare_configurations(config_a, config_b, n_sims)

        dist_fig = StatisticalComparisonPanel.create_distribution_comparison(
            comparison["df_a"],
            comparison["df_b"],
            (f"A (soft={a_soft}s)", f"B (soft={b_soft}s)"),
        )
        effect_fig = StatisticalComparisonPanel.create_effect_size_chart(comparison)
        sig_fig = StatisticalComparisonPanel.create_significance_summary(comparison)

        # Store without DataFrames
        store_data = {
            "config_a": comparison["config_a"],
            "config_b": comparison["config_b"],
            "latency": comparison["latency"],
            "quality": comparison["quality"],
        }

        return dist_fig, effect_fig, sig_fig, store_data

    @app.callback(
        [
            Output("mc-results-graph", "figure"),
            Output("mc-agent-response", "figure"),
            Output("mc-agent-reliability", "figure"),
            Output("mc-summary-stats", "children"),
            Output("simulation-data-store", "data"),
        ],
        Input("run-mc-btn", "n_clicks"),
        [
            State("mc-soft-timeout", "value"),
            State("mc-hard-timeout", "value"),
            State("mc-n-sims", "value"),
        ],
        prevent_initial_call=True,
    )
    def run_monte_carlo(n_clicks, soft_timeout, hard_timeout, n_sims):
        """Run Monte Carlo simulation."""
        if not n_clicks:
            raise PreventUpdate

        config = QueueConfig(soft_timeout=soft_timeout, hard_timeout=hard_timeout)
        df = data_manager.get_baseline_simulation(n_sims, config, force_refresh=True)

        results_fig = MonteCarloPanel.create_simulation_results(df)
        response_fig = AgentPerformancePanel.create_response_time_comparison(df)
        reliability_fig = AgentPerformancePanel.create_reliability_gauge(df)

        # Summary stats cards
        summary_cards = [
            html.Div(
                [
                    html.Div(f"{df['latency'].mean():.2f}s", className="metric-value"),
                    html.Div("Mean Latency", className="metric-label"),
                ],
                className="metric-card",
            ),
            html.Div(
                [
                    html.Div(f"{df['quality'].mean():.2f}", className="metric-value"),
                    html.Div("Mean Quality", className="metric-label"),
                ],
                className="metric-card",
            ),
            html.Div(
                [
                    html.Div(
                        f"{(df['status'] == 'complete').mean():.1%}",
                        className="metric-value",
                    ),
                    html.Div("Complete Rate", className="metric-label"),
                ],
                className="metric-card",
            ),
            html.Div(
                [
                    html.Div(
                        f"{(df['status'] != 'failed').mean():.1%}",
                        className="metric-value",
                    ),
                    html.Div("Success Rate", className="metric-label"),
                ],
                className="metric-card",
            ),
        ]

        return (
            results_fig,
            response_fig,
            reliability_fig,
            summary_cards,
            df.head(100).to_dict(),
        )

    return app


def run_dashboard(host: str = "127.0.0.1", port: int = 8050, debug: bool = True):
    """Run the interactive dashboard server."""
    app = create_app()
    print(f"""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   🗺️  MIT-Level Research Dashboard                                   ║
║   Multi-Agent Tour Guide System                                      ║
║                                                                      ║
║   📊 Starting interactive dashboard server...                        ║
║                                                                      ║
║   🌐 URL: http://{host}:{port}                                        ║
║                                                                      ║
║   Features:                                                          ║
║   • Real-time system monitoring                                      ║
║   • Interactive sensitivity analysis                                 ║
║   • Pareto frontier exploration                                      ║
║   • Statistical A/B testing                                          ║
║   • Monte Carlo simulation                                           ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run_dashboard()
