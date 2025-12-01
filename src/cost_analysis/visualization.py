"""
Cost Analysis Visualization
===========================

Publication-quality interactive visualizations for cost analysis.

Features:
- Cost breakdown charts (pie, treemap, sunburst)
- Time series cost trends
- ROI analysis visualizations
- Optimization impact comparisons
- Budget tracking dashboards

Author: Multi-Agent Tour Guide Research Team
Version: 1.0.0
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Color palette for consistent styling
COST_COLORS = {
    "primary": "#00D9FF",      # Cyan
    "secondary": "#FF6B6B",     # Coral
    "tertiary": "#4ECDC4",      # Teal
    "quaternary": "#FFE66D",    # Yellow
    "llm": "#667EEA",           # Purple-blue
    "api": "#F093FB",           # Pink
    "compute": "#4FD1C5",       # Teal
    "savings": "#68D391",       # Green
    "overhead": "#FC8181",      # Red
    "background": "#1a1a2e",    # Dark blue
    "text": "#e4e4e7",          # Light gray
    "grid": "#2d2d44",          # Muted grid
}


class CostVisualizationPanel:
    """
    Main visualization panel for cost analysis dashboard.
    
    Provides factory methods for creating various cost analysis visualizations.
    """
    
    @staticmethod
    def create_cost_overview_dashboard(
        cost_data: Dict[str, Any],
        tour_data: List[Dict[str, Any]] | None = None,
    ) -> go.Figure:
        """
        Create comprehensive cost overview dashboard.
        
        Args:
            cost_data: Cost breakdown dictionary
            tour_data: Optional tour-level cost data
            
        Returns:
            Plotly figure with multi-panel dashboard
        """
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=(
                "Cost Distribution",
                "Cost by Category",
                "Daily Cost Trend",
                "Agent Cost Comparison",
                "Savings Analysis",
                "Budget Utilization",
            ),
            specs=[
                [{"type": "pie"}, {"type": "bar"}, {"type": "scatter"}],
                [{"type": "bar"}, {"type": "waterfall"}, {"type": "indicator"}],
            ],
            vertical_spacing=0.12,
            horizontal_spacing=0.08,
        )
        
        # 1. Pie chart - Cost distribution
        categories = ["LLM", "API", "Compute", "Retry Overhead"]
        values = [
            cost_data.get("llm_cost", 45),
            cost_data.get("api_cost", 25),
            cost_data.get("compute_cost", 20),
            cost_data.get("retry_cost", 10),
        ]
        
        fig.add_trace(
            go.Pie(
                labels=categories,
                values=values,
                marker_colors=[COST_COLORS["llm"], COST_COLORS["api"], 
                              COST_COLORS["compute"], COST_COLORS["overhead"]],
                hole=0.4,
                textinfo="label+percent",
                textfont_size=10,
            ),
            row=1, col=1,
        )
        
        # 2. Bar chart - Cost by category
        fig.add_trace(
            go.Bar(
                x=categories,
                y=values,
                marker_color=[COST_COLORS["llm"], COST_COLORS["api"],
                             COST_COLORS["compute"], COST_COLORS["overhead"]],
                text=[f"${v:.2f}" for v in values],
                textposition="outside",
            ),
            row=1, col=2,
        )
        
        # 3. Line chart - Daily trend
        days = list(range(30))
        daily_costs = np.random.lognormal(2, 0.5, 30) + np.linspace(0, 5, 30)
        
        fig.add_trace(
            go.Scatter(
                x=days,
                y=daily_costs,
                mode="lines+markers",
                line=dict(color=COST_COLORS["primary"], width=2),
                fill="tozeroy",
                fillcolor=f"rgba(0, 217, 255, 0.1)",
                name="Daily Cost",
            ),
            row=1, col=3,
        )
        
        # 4. Agent comparison
        agents = ["Video", "Music", "Text", "Judge"]
        agent_costs = [
            cost_data.get("video_cost", 12),
            cost_data.get("music_cost", 8),
            cost_data.get("text_cost", 10),
            cost_data.get("judge_cost", 15),
        ]
        
        fig.add_trace(
            go.Bar(
                x=agents,
                y=agent_costs,
                marker_color=COST_COLORS["secondary"],
                text=[f"${c:.2f}" for c in agent_costs],
                textposition="outside",
            ),
            row=2, col=1,
        )
        
        # 5. Waterfall - Savings analysis
        fig.add_trace(
            go.Waterfall(
                x=["Gross Cost", "Cache Savings", "Circuit Breaker", "Net Cost"],
                y=[100, -21, -5, 74],
                measure=["absolute", "relative", "relative", "total"],
                connector={"line": {"color": COST_COLORS["text"]}},
                decreasing={"marker": {"color": COST_COLORS["savings"]}},
                increasing={"marker": {"color": COST_COLORS["overhead"]}},
                totals={"marker": {"color": COST_COLORS["primary"]}},
            ),
            row=2, col=2,
        )
        
        # 6. Gauge - Budget utilization
        budget_used = cost_data.get("budget_used", 65)
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=budget_used,
                delta={"reference": 80, "position": "bottom"},
                gauge={
                    "axis": {"range": [0, 100], "ticksuffix": "%"},
                    "bar": {"color": COST_COLORS["primary"]},
                    "steps": [
                        {"range": [0, 60], "color": COST_COLORS["savings"]},
                        {"range": [60, 80], "color": COST_COLORS["quaternary"]},
                        {"range": [80, 100], "color": COST_COLORS["overhead"]},
                    ],
                    "threshold": {
                        "line": {"color": "white", "width": 2},
                        "thickness": 0.75,
                        "value": 80,
                    },
                },
                title={"text": "Budget Used"},
            ),
            row=2, col=3,
        )
        
        # Update layout
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor=COST_COLORS["background"],
            plot_bgcolor=COST_COLORS["background"],
            font=dict(color=COST_COLORS["text"], size=11),
            showlegend=False,
            height=700,
            title=dict(
                text="💰 Cost Analysis Overview",
                font=dict(size=20, color=COST_COLORS["primary"]),
                x=0.5,
            ),
        )
        
        return fig


class CostBreakdownChart:
    """Cost breakdown visualizations."""
    
    @staticmethod
    def create_sunburst(
        cost_breakdown: Dict[str, Dict[str, float]],
    ) -> go.Figure:
        """
        Create sunburst chart for hierarchical cost breakdown.
        
        Args:
            cost_breakdown: Nested cost data {category: {subcategory: value}}
            
        Returns:
            Plotly sunburst figure
        """
        # Build hierarchical data
        ids = ["Total"]
        labels = ["Total Cost"]
        parents = [""]
        values = []
        
        total = 0
        for category, subcats in cost_breakdown.items():
            cat_total = sum(subcats.values())
            total += cat_total
            ids.append(category)
            labels.append(category)
            parents.append("Total")
            values.append(cat_total)
            
            for subcat, value in subcats.items():
                ids.append(f"{category}-{subcat}")
                labels.append(subcat)
                parents.append(category)
                values.append(value)
        
        values.insert(0, total)
        
        fig = go.Figure(go.Sunburst(
            ids=ids,
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            marker=dict(
                colors=px.colors.qualitative.Set3,
            ),
            textinfo="label+percent entry",
            hovertemplate="<b>%{label}</b><br>$%{value:.2f}<br>%{percentParent:.1%} of parent<extra></extra>",
        ))
        
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor=COST_COLORS["background"],
            title=dict(
                text="📊 Hierarchical Cost Breakdown",
                font=dict(size=18, color=COST_COLORS["primary"]),
                x=0.5,
            ),
            height=600,
        )
        
        return fig
    
    @staticmethod
    def create_treemap(
        cost_data: pd.DataFrame,
    ) -> go.Figure:
        """
        Create treemap for cost distribution.
        
        Args:
            cost_data: DataFrame with columns [category, subcategory, value]
            
        Returns:
            Plotly treemap figure
        """
        fig = px.treemap(
            cost_data,
            path=["category", "subcategory"],
            values="value",
            color="value",
            color_continuous_scale="Viridis",
            title="Cost Distribution Treemap",
        )
        
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor=COST_COLORS["background"],
            height=500,
        )
        
        return fig
    
    @staticmethod
    def create_stacked_bar_comparison(
        config_costs: Dict[str, Dict[str, float]],
    ) -> go.Figure:
        """
        Create stacked bar chart comparing costs across configurations.
        
        Args:
            config_costs: {config_name: {category: cost}}
            
        Returns:
            Plotly stacked bar figure
        """
        configs = list(config_costs.keys())
        categories = list(list(config_costs.values())[0].keys())
        
        colors = [COST_COLORS["llm"], COST_COLORS["api"], 
                  COST_COLORS["compute"], COST_COLORS["overhead"]]
        
        fig = go.Figure()
        
        for i, cat in enumerate(categories):
            fig.add_trace(go.Bar(
                name=cat,
                x=configs,
                y=[config_costs[c].get(cat, 0) for c in configs],
                marker_color=colors[i % len(colors)],
                text=[f"${config_costs[c].get(cat, 0):.2f}" for c in configs],
                textposition="inside",
            ))
        
        fig.update_layout(
            barmode="stack",
            template="plotly_dark",
            paper_bgcolor=COST_COLORS["background"],
            plot_bgcolor=COST_COLORS["background"],
            title=dict(
                text="⚖️ Configuration Cost Comparison",
                font=dict(size=18, color=COST_COLORS["primary"]),
                x=0.5,
            ),
            xaxis_title="Configuration",
            yaxis_title="Monthly Cost ($)",
            legend=dict(orientation="h", y=-0.15),
            height=500,
        )
        
        return fig


class CostTrendChart:
    """Time-series cost trend visualizations."""
    
    @staticmethod
    def create_cost_trend_with_forecast(
        historical_costs: pd.DataFrame,
        forecast_days: int = 30,
    ) -> go.Figure:
        """
        Create cost trend with forecast visualization.
        
        Args:
            historical_costs: DataFrame with date and cost columns
            forecast_days: Number of days to forecast
            
        Returns:
            Plotly figure with trend and forecast
        """
        fig = make_subplots(
            rows=2, cols=1,
            row_heights=[0.7, 0.3],
            shared_xaxes=True,
            subplot_titles=("Cost Trend with Forecast", "Daily Change"),
            vertical_spacing=0.08,
        )
        
        # Generate sample data if not provided
        if historical_costs is None or historical_costs.empty:
            dates = pd.date_range(end=datetime.now(), periods=90, freq="D")
            base_cost = 50 + np.cumsum(np.random.randn(90) * 2)
            historical_costs = pd.DataFrame({
                "date": dates,
                "cost": base_cost,
            })
        
        # Historical data
        fig.add_trace(
            go.Scatter(
                x=historical_costs["date"],
                y=historical_costs["cost"],
                mode="lines",
                name="Historical",
                line=dict(color=COST_COLORS["primary"], width=2),
                fill="tozeroy",
                fillcolor=f"rgba(0, 217, 255, 0.1)",
            ),
            row=1, col=1,
        )
        
        # Simple linear forecast
        last_date = historical_costs["date"].iloc[-1]
        last_cost = historical_costs["cost"].iloc[-1]
        daily_growth = (historical_costs["cost"].iloc[-1] - historical_costs["cost"].iloc[-30]) / 30
        
        forecast_dates = pd.date_range(start=last_date, periods=forecast_days + 1, freq="D")[1:]
        forecast_values = last_cost + daily_growth * np.arange(1, forecast_days + 1)
        forecast_upper = forecast_values * 1.2
        forecast_lower = forecast_values * 0.8
        
        # Forecast line
        fig.add_trace(
            go.Scatter(
                x=forecast_dates,
                y=forecast_values,
                mode="lines",
                name="Forecast",
                line=dict(color=COST_COLORS["secondary"], width=2, dash="dash"),
            ),
            row=1, col=1,
        )
        
        # Confidence interval
        fig.add_trace(
            go.Scatter(
                x=list(forecast_dates) + list(forecast_dates[::-1]),
                y=list(forecast_upper) + list(forecast_lower[::-1]),
                fill="toself",
                fillcolor=f"rgba(255, 107, 107, 0.2)",
                line=dict(color="rgba(255,255,255,0)"),
                name="Confidence Interval",
                showlegend=True,
            ),
            row=1, col=1,
        )
        
        # Daily change (second subplot)
        daily_change = historical_costs["cost"].diff()
        colors = [COST_COLORS["savings"] if c < 0 else COST_COLORS["overhead"] 
                  for c in daily_change]
        
        fig.add_trace(
            go.Bar(
                x=historical_costs["date"],
                y=daily_change,
                marker_color=colors,
                name="Daily Change",
                showlegend=False,
            ),
            row=2, col=1,
        )
        
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor=COST_COLORS["background"],
            plot_bgcolor=COST_COLORS["background"],
            title=dict(
                text="📈 Cost Trend Analysis & Forecast",
                font=dict(size=18, color=COST_COLORS["primary"]),
                x=0.5,
            ),
            legend=dict(orientation="h", y=1.02),
            height=600,
        )
        
        fig.update_yaxes(title_text="Cost ($)", row=1, col=1)
        fig.update_yaxes(title_text="Change ($)", row=2, col=1)
        
        return fig
    
    @staticmethod
    def create_cumulative_cost_chart(
        cost_events: pd.DataFrame,
    ) -> go.Figure:
        """
        Create cumulative cost chart by category.
        
        Args:
            cost_events: DataFrame with timestamp, category, amount columns
            
        Returns:
            Plotly figure with cumulative costs
        """
        # Generate sample data if empty
        if cost_events is None or cost_events.empty:
            dates = pd.date_range(end=datetime.now(), periods=100, freq="H")
            cost_events = pd.DataFrame({
                "timestamp": np.repeat(dates, 4),
                "category": ["LLM", "API", "Compute", "Overhead"] * 100,
                "amount": np.random.exponential(0.5, 400),
            })
        
        fig = go.Figure()
        
        categories = cost_events["category"].unique()
        colors = [COST_COLORS["llm"], COST_COLORS["api"], 
                  COST_COLORS["compute"], COST_COLORS["overhead"]]
        
        for i, cat in enumerate(categories):
            cat_data = cost_events[cost_events["category"] == cat].sort_values("timestamp")
            cat_data["cumsum"] = cat_data["amount"].cumsum()
            
            fig.add_trace(go.Scatter(
                x=cat_data["timestamp"],
                y=cat_data["cumsum"],
                mode="lines",
                name=cat,
                line=dict(color=colors[i % len(colors)], width=2),
                stackgroup="one",
            ))
        
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor=COST_COLORS["background"],
            plot_bgcolor=COST_COLORS["background"],
            title=dict(
                text="📊 Cumulative Cost by Category",
                font=dict(size=18, color=COST_COLORS["primary"]),
                x=0.5,
            ),
            xaxis_title="Time",
            yaxis_title="Cumulative Cost ($)",
            legend=dict(orientation="h", y=-0.15),
            height=500,
        )
        
        return fig


class ROIChart:
    """ROI analysis visualizations."""
    
    @staticmethod
    def create_roi_comparison(
        roi_data: List[Dict[str, Any]],
    ) -> go.Figure:
        """
        Create ROI comparison chart for optimization options.
        
        Args:
            roi_data: List of ROI analysis dictionaries
            
        Returns:
            Plotly figure comparing ROI across options
        """
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("ROI by Optimization", "Payback Period"),
            specs=[[{"type": "bar"}, {"type": "bar"}]],
        )
        
        names = [r.get("optimization_name", f"Opt {i}") for i, r in enumerate(roi_data)]
        rois = [r.get("metrics", {}).get("roi_1year", 0) for r in roi_data]
        paybacks = [r.get("metrics", {}).get("payback_period_months", 0) for r in roi_data]
        
        # Cap payback for visualization
        paybacks = [min(p, 24) for p in paybacks]
        
        # ROI bars
        fig.add_trace(
            go.Bar(
                x=names,
                y=rois,
                marker_color=[COST_COLORS["savings"] if r > 0 else COST_COLORS["overhead"] 
                             for r in rois],
                text=[f"{r:.0f}%" for r in rois],
                textposition="outside",
                name="ROI",
            ),
            row=1, col=1,
        )
        
        # Payback bars
        fig.add_trace(
            go.Bar(
                x=names,
                y=paybacks,
                marker_color=COST_COLORS["tertiary"],
                text=[f"{p:.1f}mo" for p in paybacks],
                textposition="outside",
                name="Payback",
            ),
            row=1, col=2,
        )
        
        # Add threshold line for payback
        fig.add_hline(
            y=6, line_dash="dash", line_color="white",
            annotation_text="6-month target",
            row=1, col=2,
        )
        
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor=COST_COLORS["background"],
            plot_bgcolor=COST_COLORS["background"],
            title=dict(
                text="💹 ROI Analysis: Optimization Options",
                font=dict(size=18, color=COST_COLORS["primary"]),
                x=0.5,
            ),
            showlegend=False,
            height=450,
        )
        
        fig.update_yaxes(title_text="ROI (%)", row=1, col=1)
        fig.update_yaxes(title_text="Months", row=1, col=2)
        
        return fig
    
    @staticmethod
    def create_savings_projection(
        monthly_savings: float,
        implementation_cost: float,
        months: int = 24,
    ) -> go.Figure:
        """
        Create savings projection over time.
        
        Args:
            monthly_savings: Expected monthly savings
            implementation_cost: One-time implementation cost
            months: Number of months to project
            
        Returns:
            Plotly figure showing cumulative savings vs cost
        """
        month_range = list(range(months + 1))
        cumulative_savings = [monthly_savings * m for m in month_range]
        net_benefit = [s - implementation_cost for s in cumulative_savings]
        
        # Find break-even point
        break_even_month = None
        for i, nb in enumerate(net_benefit):
            if nb >= 0:
                break_even_month = i
                break
        
        fig = go.Figure()
        
        # Implementation cost line
        fig.add_hline(
            y=implementation_cost,
            line_dash="dash",
            line_color=COST_COLORS["overhead"],
            annotation_text=f"Implementation Cost: ${implementation_cost:,.0f}",
        )
        
        # Cumulative savings
        fig.add_trace(go.Scatter(
            x=month_range,
            y=cumulative_savings,
            mode="lines+markers",
            name="Cumulative Savings",
            line=dict(color=COST_COLORS["savings"], width=3),
            fill="tozeroy",
            fillcolor=f"rgba(104, 211, 145, 0.2)",
        ))
        
        # Net benefit
        fig.add_trace(go.Scatter(
            x=month_range,
            y=net_benefit,
            mode="lines",
            name="Net Benefit",
            line=dict(color=COST_COLORS["primary"], width=2, dash="dot"),
        ))
        
        # Break-even annotation
        if break_even_month:
            fig.add_vline(
                x=break_even_month,
                line_dash="dash",
                line_color="white",
                annotation_text=f"Break-even: Month {break_even_month}",
            )
        
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor=COST_COLORS["background"],
            plot_bgcolor=COST_COLORS["background"],
            title=dict(
                text="🎯 Savings Projection & Break-Even Analysis",
                font=dict(size=18, color=COST_COLORS["primary"]),
                x=0.5,
            ),
            xaxis_title="Months",
            yaxis_title="Amount ($)",
            legend=dict(orientation="h", y=-0.15),
            height=500,
        )
        
        return fig
    
    @staticmethod
    def create_optimization_impact_matrix(
        recommendations: List[Dict[str, Any]],
    ) -> go.Figure:
        """
        Create impact vs effort matrix for optimization recommendations.
        
        Args:
            recommendations: List of recommendation dictionaries
            
        Returns:
            Plotly scatter plot with impact/effort matrix
        """
        effort_map = {"low": 1, "medium": 2, "high": 3}
        
        efforts = [effort_map.get(r.get("implementation", {}).get("effort", "medium"), 2) 
                   for r in recommendations]
        impacts = [r.get("costs", {}).get("savings_percent", 0) for r in recommendations]
        names = [r.get("title", "")[:30] for r in recommendations]
        priorities = [r.get("priority", "medium") for r in recommendations]
        
        priority_colors = {
            "critical": COST_COLORS["overhead"],
            "high": COST_COLORS["secondary"],
            "medium": COST_COLORS["quaternary"],
            "low": COST_COLORS["tertiary"],
        }
        
        colors = [priority_colors.get(p, COST_COLORS["text"]) for p in priorities]
        
        fig = go.Figure()
        
        # Add quadrant backgrounds
        fig.add_shape(
            type="rect", x0=0, x1=1.5, y0=15, y1=50,
            fillcolor="rgba(104, 211, 145, 0.1)",
            line=dict(width=0),
        )
        fig.add_annotation(x=0.75, y=45, text="Quick Wins", showarrow=False,
                          font=dict(size=14, color=COST_COLORS["savings"]))
        
        fig.add_shape(
            type="rect", x0=1.5, x1=3.5, y0=15, y1=50,
            fillcolor="rgba(255, 230, 109, 0.1)",
            line=dict(width=0),
        )
        fig.add_annotation(x=2.5, y=45, text="Strategic", showarrow=False,
                          font=dict(size=14, color=COST_COLORS["quaternary"]))
        
        # Scatter points
        fig.add_trace(go.Scatter(
            x=efforts,
            y=impacts,
            mode="markers+text",
            marker=dict(
                size=20,
                color=colors,
                line=dict(width=2, color="white"),
            ),
            text=names,
            textposition="top center",
            textfont=dict(size=9),
            hovertemplate="<b>%{text}</b><br>Effort: %{x}<br>Impact: %{y:.1f}%<extra></extra>",
        ))
        
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor=COST_COLORS["background"],
            plot_bgcolor=COST_COLORS["background"],
            title=dict(
                text="🎯 Optimization Impact vs Effort Matrix",
                font=dict(size=18, color=COST_COLORS["primary"]),
                x=0.5,
            ),
            xaxis=dict(
                title="Implementation Effort",
                ticktext=["Low", "Medium", "High"],
                tickvals=[1, 2, 3],
                range=[0.5, 3.5],
            ),
            yaxis=dict(
                title="Cost Savings Potential (%)",
                range=[0, max(impacts) * 1.2 if impacts else 50],
            ),
            height=550,
        )
        
        return fig


class CostDashboardComponents:
    """Additional dashboard components for cost analysis."""
    
    @staticmethod
    def create_kpi_cards(
        total_cost: float,
        budget: float,
        savings: float,
        cost_per_tour: float,
    ) -> go.Figure:
        """
        Create KPI indicator cards.
        
        Args:
            total_cost: Total cost for period
            budget: Budget limit
            savings: Total savings
            cost_per_tour: Average cost per tour
            
        Returns:
            Plotly figure with KPI indicators
        """
        fig = make_subplots(
            rows=1, cols=4,
            specs=[[{"type": "indicator"}] * 4],
            subplot_titles=("Total Cost", "Budget Utilization", "Savings", "Cost/Tour"),
        )
        
        # Total Cost
        fig.add_trace(
            go.Indicator(
                mode="number+delta",
                value=total_cost,
                number=dict(prefix="$", valueformat=",.2f"),
                delta=dict(reference=budget * 0.8, valueformat=".0f"),
                domain=dict(x=[0, 0.25], y=[0, 1]),
            ),
            row=1, col=1,
        )
        
        # Budget Utilization
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=total_cost / budget * 100 if budget > 0 else 0,
                number=dict(suffix="%"),
                gauge=dict(
                    axis=dict(range=[0, 100]),
                    bar=dict(color=COST_COLORS["primary"]),
                    steps=[
                        dict(range=[0, 60], color=COST_COLORS["savings"]),
                        dict(range=[60, 80], color=COST_COLORS["quaternary"]),
                        dict(range=[80, 100], color=COST_COLORS["overhead"]),
                    ],
                ),
            ),
            row=1, col=2,
        )
        
        # Savings
        fig.add_trace(
            go.Indicator(
                mode="number+delta",
                value=savings,
                number=dict(prefix="$", valueformat=",.2f"),
                delta=dict(reference=savings * 0.9, valueformat=".0f"),
                domain=dict(x=[0.5, 0.75], y=[0, 1]),
            ),
            row=1, col=3,
        )
        
        # Cost per Tour
        fig.add_trace(
            go.Indicator(
                mode="number",
                value=cost_per_tour,
                number=dict(prefix="$", valueformat=".4f"),
            ),
            row=1, col=4,
        )
        
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor=COST_COLORS["background"],
            height=200,
        )
        
        return fig
    
    @staticmethod
    def create_cost_heatmap(
        hourly_costs: pd.DataFrame,
    ) -> go.Figure:
        """
        Create heatmap of costs by hour and day.
        
        Args:
            hourly_costs: DataFrame with day, hour, cost columns
            
        Returns:
            Plotly heatmap figure
        """
        # Generate sample data if empty
        if hourly_costs is None or hourly_costs.empty:
            days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            hours = list(range(24))
            
            costs = np.random.lognormal(0, 0.5, (7, 24))
            # Add patterns: higher during business hours, lower weekends
            for h in range(9, 18):
                costs[:5, h] *= 2
            costs[5:, :] *= 0.5
            
            hourly_costs = pd.DataFrame(costs, index=days, columns=hours)
        
        fig = go.Figure(go.Heatmap(
            z=hourly_costs.values,
            x=hourly_costs.columns,
            y=hourly_costs.index,
            colorscale="Viridis",
            hovertemplate="Day: %{y}<br>Hour: %{x}:00<br>Cost: $%{z:.2f}<extra></extra>",
        ))
        
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor=COST_COLORS["background"],
            title=dict(
                text="🗓️ Cost Heatmap by Day and Hour",
                font=dict(size=18, color=COST_COLORS["primary"]),
                x=0.5,
            ),
            xaxis_title="Hour of Day",
            yaxis_title="Day of Week",
            height=400,
        )
        
        return fig

