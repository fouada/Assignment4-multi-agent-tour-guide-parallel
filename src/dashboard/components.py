"""
Dashboard Components
====================

High-quality, interactive visualization components for the MIT-level dashboard.
Each panel provides deep insights into system behavior with publication-quality visuals.

Author: Multi-Agent Tour Guide Research Team
Version: 1.0.0
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# ============================================================================
# Color Schemes - Sophisticated MIT-level aesthetics
# ============================================================================

COLORS = {
    # Primary palette - Deep research aesthetics
    'primary': '#1a1a2e',
    'secondary': '#16213e',
    'accent': '#0f3460',
    'highlight': '#e94560',
    
    # Status colors
    'complete': '#00d9a5',
    'soft_degraded': '#ffc107',
    'hard_degraded': '#fd7e14',
    'failed': '#dc3545',
    'healthy': '#00d9a5',
    'degraded': '#ffc107',
    
    # Agent colors
    'video': '#6366f1',
    'music': '#ec4899',
    'text': '#14b8a6',
    'judge': '#f59e0b',
    
    # Chart colors
    'gradient': ['#667eea', '#764ba2', '#6B8DD6', '#8E37D7'],
    'comparison': ['#00d9a5', '#e94560'],
    'heatmap': 'RdYlGn',
}

FONTS = {
    'title': 'JetBrains Mono, Fira Code, monospace',
    'body': 'Inter, -apple-system, sans-serif',
    'mono': 'JetBrains Mono, Fira Code, Consolas, monospace',
}


def create_base_layout(title: str = '', height: int = 500) -> dict:
    """Create base layout with MIT-level styling."""
    return {
        'title': {
            'text': title,
            'font': {'family': FONTS['title'], 'size': 18, 'color': '#e0e0e0'},
            'x': 0.5,
            'xanchor': 'center',
        },
        'paper_bgcolor': 'rgba(26, 26, 46, 0.95)',
        'plot_bgcolor': 'rgba(22, 33, 62, 0.8)',
        'font': {'family': FONTS['body'], 'color': '#b0b0b0', 'size': 12},
        'height': height,
        'margin': {'l': 60, 'r': 40, 't': 80, 'b': 60},
        'xaxis': {
            'gridcolor': 'rgba(255,255,255,0.1)',
            'zerolinecolor': 'rgba(255,255,255,0.2)',
            'tickfont': {'family': FONTS['mono']},
        },
        'yaxis': {
            'gridcolor': 'rgba(255,255,255,0.1)',
            'zerolinecolor': 'rgba(255,255,255,0.2)',
            'tickfont': {'family': FONTS['mono']},
        },
        'legend': {
            'bgcolor': 'rgba(0,0,0,0.3)',
            'bordercolor': 'rgba(255,255,255,0.1)',
            'borderwidth': 1,
        },
        'hoverlabel': {
            'bgcolor': 'rgba(26, 26, 46, 0.95)',
            'bordercolor': '#e94560',
            'font': {'family': FONTS['mono'], 'size': 11},
        },
    }


# ============================================================================
# System Monitor Panel
# ============================================================================

class SystemMonitorPanel:
    """Real-time system monitoring visualization."""
    
    @staticmethod
    def create_agent_status_cards(metrics: dict) -> go.Figure:
        """Create agent status indicator cards."""
        agents = metrics.get('agents', {})
        
        fig = make_subplots(
            rows=1, cols=3,
            specs=[[{'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}]],
            subplot_titles=['🎬 Video Agent', '🎵 Music Agent', '📖 Text Agent']
        )
        
        for i, (agent, data) in enumerate(agents.items()):
            status_color = COLORS['healthy'] if data['status'] == 'healthy' else COLORS['degraded']
            
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=data['success_rate'] * 100,
                    number={'suffix': '%', 'font': {'size': 28, 'family': FONTS['mono']}},
                    delta={'reference': 95, 'increasing': {'color': COLORS['complete']}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickcolor': '#b0b0b0'},
                        'bar': {'color': status_color},
                        'bgcolor': 'rgba(22, 33, 62, 0.8)',
                        'borderwidth': 2,
                        'bordercolor': 'rgba(255,255,255,0.2)',
                        'steps': [
                            {'range': [0, 80], 'color': 'rgba(220, 53, 69, 0.3)'},
                            {'range': [80, 90], 'color': 'rgba(255, 193, 7, 0.3)'},
                            {'range': [90, 100], 'color': 'rgba(0, 217, 165, 0.3)'},
                        ],
                        'threshold': {
                            'line': {'color': '#e94560', 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ),
                row=1, col=i+1
            )
        
        fig.update_layout(
            **create_base_layout('🔬 Agent Health Monitor', 280),
            showlegend=False,
        )
        
        return fig
    
    @staticmethod
    def create_throughput_chart(history: list[dict]) -> go.Figure:
        """Create real-time throughput line chart."""
        if not history:
            history = [{'timestamp': i, 'throughput': np.random.uniform(5, 20)} for i in range(60)]
        
        df = pd.DataFrame(history)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['timestamp'] if 'timestamp' in df else list(range(len(df))),
            y=df['throughput'],
            mode='lines',
            name='Throughput',
            line={'color': COLORS['highlight'], 'width': 2},
            fill='tozeroy',
            fillcolor='rgba(233, 69, 96, 0.2)',
        ))
        
        fig.update_layout(
            **create_base_layout('📈 System Throughput (requests/s)', 300),
            xaxis_title='Time',
            yaxis_title='Throughput',
        )
        
        return fig
    
    @staticmethod
    def create_queue_depth_chart(depth_history: list[int]) -> go.Figure:
        """Create queue depth visualization."""
        if not depth_history:
            depth_history = [np.random.randint(0, 20) for _ in range(60)]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=list(range(len(depth_history))),
            y=depth_history,
            marker_color=[
                COLORS['complete'] if d < 10 else 
                COLORS['soft_degraded'] if d < 15 else 
                COLORS['failed'] for d in depth_history
            ],
            opacity=0.8,
        ))
        
        # Add threshold lines
        fig.add_hline(y=10, line_dash='dash', line_color=COLORS['soft_degraded'],
                     annotation_text='Warning', annotation_position='right')
        fig.add_hline(y=15, line_dash='dash', line_color=COLORS['failed'],
                     annotation_text='Critical', annotation_position='right')
        
        fig.update_layout(
            **create_base_layout('📊 Queue Depth Monitor', 300),
            xaxis_title='Time Window',
            yaxis_title='Queue Depth',
            bargap=0.1,
        )
        
        return fig


# ============================================================================
# Sensitivity Analysis Panel
# ============================================================================

class SensitivityPanel:
    """Interactive sensitivity analysis visualization."""
    
    @staticmethod
    def create_parameter_impact_chart(data: pd.DataFrame, param_name: str) -> go.Figure:
        """Create multi-metric sensitivity plot."""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                '⏱️ Latency Impact', 
                '⭐ Quality Impact',
                '📊 Status Distribution', 
                '🎯 Pareto Frontier'
            ],
            vertical_spacing=0.12,
            horizontal_spacing=0.1,
        )
        
        # Latency plot
        fig.add_trace(
            go.Scatter(
                x=data['param_value'], y=data['latency_mean'],
                mode='lines+markers',
                name='Mean Latency',
                line={'color': COLORS['gradient'][0], 'width': 3},
                marker={'size': 8, 'symbol': 'diamond'},
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=data['param_value'],
                y=data['latency_mean'] + data['latency_std'],
                mode='lines',
                name='Upper Bound',
                line={'color': COLORS['gradient'][0], 'width': 0},
                showlegend=False,
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=data['param_value'],
                y=data['latency_mean'] - data['latency_std'],
                mode='lines',
                name='Lower Bound',
                line={'color': COLORS['gradient'][0], 'width': 0},
                fill='tonexty',
                fillcolor='rgba(102, 126, 234, 0.2)',
                showlegend=False,
            ),
            row=1, col=1
        )
        
        # Quality plot
        fig.add_trace(
            go.Scatter(
                x=data['param_value'], y=data['quality_mean'],
                mode='lines+markers',
                name='Mean Quality',
                line={'color': COLORS['complete'], 'width': 3},
                marker={'size': 8, 'symbol': 'circle'},
            ),
            row=1, col=2
        )
        
        fig.add_trace(
            go.Scatter(
                x=data['param_value'],
                y=data['quality_mean'] + data['quality_std'],
                mode='lines', line={'width': 0}, showlegend=False,
            ),
            row=1, col=2
        )
        
        fig.add_trace(
            go.Scatter(
                x=data['param_value'],
                y=data['quality_mean'] - data['quality_std'],
                mode='lines', line={'width': 0},
                fill='tonexty',
                fillcolor='rgba(0, 217, 165, 0.2)',
                showlegend=False,
            ),
            row=1, col=2
        )
        
        # Status distribution (stacked area)
        fig.add_trace(
            go.Scatter(
                x=data['param_value'], y=data['complete_rate'],
                mode='lines', name='Complete',
                stackgroup='one',
                line={'color': COLORS['complete']},
                fillcolor='rgba(0, 217, 165, 0.6)',
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=data['param_value'], y=data['degraded_rate'],
                mode='lines', name='Degraded',
                stackgroup='one',
                line={'color': COLORS['soft_degraded']},
                fillcolor='rgba(255, 193, 7, 0.6)',
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=data['param_value'], y=data['failed_rate'],
                mode='lines', name='Failed',
                stackgroup='one',
                line={'color': COLORS['failed']},
                fillcolor='rgba(220, 53, 69, 0.6)',
            ),
            row=2, col=1
        )
        
        # Pareto frontier
        fig.add_trace(
            go.Scatter(
                x=data['latency_mean'], y=data['quality_mean'],
                mode='markers+text',
                text=[f"{v:.0f}s" for v in data['param_value']],
                textposition='top center',
                textfont={'size': 9, 'color': '#b0b0b0'},
                marker={
                    'size': 12,
                    'color': data['param_value'],
                    'colorscale': 'Viridis',
                    'showscale': True,
                    'colorbar': {'title': param_name.replace('_', ' ').title()},
                },
                name='Configurations',
            ),
            row=2, col=2
        )
        
        # Connect points on Pareto
        fig.add_trace(
            go.Scatter(
                x=data['latency_mean'], y=data['quality_mean'],
                mode='lines',
                line={'color': 'rgba(255,255,255,0.3)', 'dash': 'dot', 'width': 1},
                showlegend=False,
            ),
            row=2, col=2
        )
        
        layout = create_base_layout(f'🔬 Sensitivity Analysis: {param_name.replace("_", " ").title()}', 650)
        layout['showlegend'] = True
        fig.update_layout(**layout)
        
        # Update axis labels
        fig.update_xaxes(title_text=param_name.replace('_', ' ').title(), row=1, col=1)
        fig.update_yaxes(title_text='Latency (s)', row=1, col=1)
        fig.update_xaxes(title_text=param_name.replace('_', ' ').title(), row=1, col=2)
        fig.update_yaxes(title_text='Quality Score', row=1, col=2)
        fig.update_xaxes(title_text=param_name.replace('_', ' ').title(), row=2, col=1)
        fig.update_yaxes(title_text='Proportion', row=2, col=1)
        fig.update_xaxes(title_text='Mean Latency (s)', row=2, col=2)
        fig.update_yaxes(title_text='Mean Quality', row=2, col=2)
        
        return fig
    
    @staticmethod
    def create_tornado_chart(sensitivities: dict[str, float]) -> go.Figure:
        """Create tornado/waterfall chart for parameter importance."""
        sorted_params = sorted(sensitivities.items(), key=lambda x: abs(x[1]), reverse=True)
        params = [p[0] for p in sorted_params]
        values = [p[1] for p in sorted_params]
        
        colors = [COLORS['complete'] if v > 0 else COLORS['failed'] for v in values]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=params,
            x=values,
            orientation='h',
            marker_color=colors,
            text=[f'{v:+.2f}' for v in values],
            textposition='outside',
            textfont={'family': FONTS['mono']},
        ))
        
        fig.add_vline(x=0, line_color='rgba(255,255,255,0.5)', line_width=2)
        
        fig.update_layout(
            **create_base_layout('🌪️ Parameter Sensitivity (Impact on Quality)', 400),
            xaxis_title='Sensitivity Coefficient',
            yaxis_title='Parameter',
        )
        
        return fig


# ============================================================================
# Pareto Frontier Panel
# ============================================================================

class ParetoFrontierPanel:
    """Interactive Pareto frontier exploration."""
    
    @staticmethod
    def create_3d_pareto_surface(data: pd.DataFrame) -> go.Figure:
        """Create 3D surface plot for Pareto exploration."""
        # Pivot data for surface
        pivot = data.pivot_table(
            values='quality_mean', 
            index='soft_timeout', 
            columns='hard_timeout',
            aggfunc='mean'
        ).fillna(0)
        
        fig = go.Figure(data=[
            go.Surface(
                z=pivot.values,
                x=pivot.columns,
                y=pivot.index,
                colorscale='Viridis',
                colorbar={'title': {'text': 'Quality', 'font': {'family': FONTS['mono']}}},
                opacity=0.9,
                contours={
                    'z': {'show': True, 'usecolormap': True, 'highlightcolor': '#e94560', 'project_z': True}
                }
            )
        ])
        
        fig.update_layout(
            title={
                'text': '🗻 Quality Response Surface',
                'font': {'family': FONTS['title'], 'size': 18, 'color': '#e0e0e0'},
            },
            scene={
                'xaxis': {'title': {'text': 'Hard Timeout (s)'}, 'backgroundcolor': 'rgba(22,33,62,0.8)'},
                'yaxis': {'title': {'text': 'Soft Timeout (s)'}, 'backgroundcolor': 'rgba(22,33,62,0.8)'},
                'zaxis': {'title': {'text': 'Quality Score'}, 'backgroundcolor': 'rgba(22,33,62,0.8)'},
                'camera': {'eye': {'x': 1.5, 'y': 1.5, 'z': 1}},
            },
            paper_bgcolor='rgba(26, 26, 46, 0.95)',
            height=600,
            margin={'l': 0, 'r': 0, 't': 50, 'b': 0},
        )
        
        return fig
    
    @staticmethod
    def create_pareto_scatter(data: pd.DataFrame) -> go.Figure:
        """Create 2D Pareto frontier visualization with optimal points highlighted."""
        # Identify Pareto-optimal points
        pareto_mask = []
        for i, row in data.iterrows():
            is_pareto = True
            for j, other in data.iterrows():
                if i != j:
                    # Minimize latency, maximize quality
                    if other['latency_mean'] <= row['latency_mean'] and other['quality_mean'] >= row['quality_mean']:
                        if other['latency_mean'] < row['latency_mean'] or other['quality_mean'] > row['quality_mean']:
                            is_pareto = False
                            break
            pareto_mask.append(is_pareto)
        
        data = data.copy()
        data['is_pareto'] = pareto_mask
        
        fig = go.Figure()
        
        # Non-Pareto points
        non_pareto = data[~data['is_pareto']]
        fig.add_trace(go.Scatter(
            x=non_pareto['latency_mean'],
            y=non_pareto['quality_mean'],
            mode='markers',
            name='Sub-optimal',
            marker={
                'size': 10,
                'color': non_pareto['success_rate'],
                'colorscale': 'Blues',
                'opacity': 0.4,
            },
            hovertemplate='<b>Latency:</b> %{x:.2f}s<br><b>Quality:</b> %{y:.2f}<br><b>Success:</b> %{marker.color:.1%}<extra></extra>',
        ))
        
        # Pareto-optimal points
        pareto_data = data[data['is_pareto']].sort_values('latency_mean')
        fig.add_trace(go.Scatter(
            x=pareto_data['latency_mean'],
            y=pareto_data['quality_mean'],
            mode='markers+lines',
            name='Pareto-optimal',
            line={'color': COLORS['highlight'], 'width': 2, 'dash': 'dot'},
            marker={
                'size': 16,
                'color': COLORS['highlight'],
                'symbol': 'star',
                'line': {'width': 2, 'color': 'white'},
            },
            hovertemplate='<b>⭐ OPTIMAL</b><br>Latency: %{x:.2f}s<br>Quality: %{y:.2f}<extra></extra>',
        ))
        
        # Add annotations for recommended configs
        if len(pareto_data) > 0:
            best_quality = pareto_data.loc[pareto_data['quality_mean'].idxmax()]
            best_latency = pareto_data.loc[pareto_data['latency_mean'].idxmin()]
            
            fig.add_annotation(
                x=best_quality['latency_mean'], y=best_quality['quality_mean'],
                text='High Quality', showarrow=True, arrowhead=2,
                font={'color': COLORS['complete']},
                arrowcolor=COLORS['complete'],
            )
            
            fig.add_annotation(
                x=best_latency['latency_mean'], y=best_latency['quality_mean'],
                text='Low Latency', showarrow=True, arrowhead=2,
                font={'color': COLORS['soft_degraded']},
                arrowcolor=COLORS['soft_degraded'],
            )
        
        fig.update_layout(
            **create_base_layout('🎯 Quality-Latency Pareto Frontier', 500),
            xaxis_title='Mean Latency (s)',
            yaxis_title='Mean Quality Score',
        )
        
        return fig
    
    @staticmethod
    def create_heatmap(data: pd.DataFrame) -> go.Figure:
        """Create heatmap of parameter combinations."""
        pivot = data.pivot_table(
            values='quality_mean',
            index='soft_timeout',
            columns='hard_timeout',
            aggfunc='mean'
        ).fillna(0)
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot.values,
            x=[f'{x:.0f}s' for x in pivot.columns],
            y=[f'{y:.0f}s' for y in pivot.index],
            colorscale='RdYlGn',
            colorbar={'title': 'Quality'},
            hovertemplate='Soft: %{y}<br>Hard: %{x}<br>Quality: %{z:.2f}<extra></extra>',
        ))
        
        fig.update_layout(
            **create_base_layout('🔥 Parameter Interaction Heatmap', 450),
            xaxis_title='Hard Timeout',
            yaxis_title='Soft Timeout',
        )
        
        return fig


# ============================================================================
# Statistical Comparison Panel
# ============================================================================

class StatisticalComparisonPanel:
    """A/B testing and statistical comparison visualization."""
    
    @staticmethod
    def create_distribution_comparison(
        df_a: pd.DataFrame, 
        df_b: pd.DataFrame,
        config_names: tuple[str, str] = ('Config A', 'Config B')
    ) -> go.Figure:
        """Create side-by-side distribution comparison."""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                '📊 Latency Distribution',
                '⭐ Quality Distribution',
                '🎯 Status Distribution',
                '📈 Cumulative Latency'
            ],
            vertical_spacing=0.12,
        )
        
        # Latency histograms
        fig.add_trace(
            go.Histogram(
                x=df_a['latency'], name=config_names[0],
                marker_color=COLORS['comparison'][0],
                opacity=0.6, nbinsx=50,
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Histogram(
                x=df_b['latency'], name=config_names[1],
                marker_color=COLORS['comparison'][1],
                opacity=0.6, nbinsx=50,
            ),
            row=1, col=1
        )
        
        # Quality histograms
        fig.add_trace(
            go.Histogram(
                x=df_a['quality'], name=config_names[0],
                marker_color=COLORS['comparison'][0],
                opacity=0.6, nbinsx=30, showlegend=False,
            ),
            row=1, col=2
        )
        fig.add_trace(
            go.Histogram(
                x=df_b['quality'], name=config_names[1],
                marker_color=COLORS['comparison'][1],
                opacity=0.6, nbinsx=30, showlegend=False,
            ),
            row=1, col=2
        )
        
        # Status comparison
        status_a = df_a['status'].value_counts(normalize=True)
        status_b = df_b['status'].value_counts(normalize=True)
        
        statuses = ['complete', 'soft_degraded', 'hard_degraded', 'failed']
        status_colors = [COLORS['complete'], COLORS['soft_degraded'], COLORS['hard_degraded'], COLORS['failed']]
        
        for status, color in zip(statuses, status_colors):
            fig.add_trace(
                go.Bar(
                    x=[config_names[0], config_names[1]],
                    y=[status_a.get(status, 0), status_b.get(status, 0)],
                    name=status.replace('_', ' ').title(),
                    marker_color=color,
                ),
                row=2, col=1
            )
        
        # Cumulative distribution
        for df, name, color in [(df_a, config_names[0], COLORS['comparison'][0]), 
                                 (df_b, config_names[1], COLORS['comparison'][1])]:
            sorted_latency = np.sort(df['latency'])
            cdf = np.arange(1, len(sorted_latency) + 1) / len(sorted_latency)
            fig.add_trace(
                go.Scatter(
                    x=sorted_latency, y=cdf,
                    mode='lines', name=f'{name} CDF',
                    line={'color': color, 'width': 2},
                ),
                row=2, col=2
            )
        
        fig.update_layout(
            **create_base_layout('📊 Statistical Comparison Dashboard', 650),
            barmode='group',
        )
        
        return fig
    
    @staticmethod
    def create_effect_size_chart(comparison: dict) -> go.Figure:
        """Create effect size visualization with confidence intervals."""
        metrics = ['Latency', 'Quality']
        effect_sizes = [comparison['latency']['cohens_d'], comparison['quality']['cohens_d']]
        
        fig = go.Figure()
        
        # Effect size bars
        colors = [COLORS['comparison'][1] if d > 0 else COLORS['comparison'][0] for d in effect_sizes]
        
        fig.add_trace(go.Bar(
            y=metrics,
            x=effect_sizes,
            orientation='h',
            marker_color=colors,
            text=[f"d = {d:.3f}" for d in effect_sizes],
            textposition='outside',
            textfont={'family': FONTS['mono'], 'size': 14},
        ))
        
        # Reference lines for effect size thresholds
        fig.add_vline(x=0, line_color='white', line_width=2)
        fig.add_vline(x=0.2, line_color='rgba(255,255,255,0.3)', line_dash='dash', 
                     annotation_text='Small', annotation_position='top')
        fig.add_vline(x=-0.2, line_color='rgba(255,255,255,0.3)', line_dash='dash')
        fig.add_vline(x=0.5, line_color='rgba(255,255,255,0.3)', line_dash='dash',
                     annotation_text='Medium', annotation_position='top')
        fig.add_vline(x=-0.5, line_color='rgba(255,255,255,0.3)', line_dash='dash')
        fig.add_vline(x=0.8, line_color='rgba(255,255,255,0.3)', line_dash='dash',
                     annotation_text='Large', annotation_position='top')
        fig.add_vline(x=-0.8, line_color='rgba(255,255,255,0.3)', line_dash='dash')
        
        fig.update_layout(
            **create_base_layout("📐 Cohen's d Effect Size", 300),
            xaxis_title="Effect Size (Cohen's d)",
        )
        
        return fig
    
    @staticmethod
    def create_significance_summary(comparison: dict) -> go.Figure:
        """Create statistical significance summary card."""
        metrics = ['Latency', 'Quality']
        p_values = [comparison['latency']['p_value'], comparison['quality']['p_value']]
        
        fig = go.Figure()
        
        for i, (metric, p) in enumerate(zip(metrics, p_values)):
            sig_level = 'p < 0.001 ✓✓✓' if p < 0.001 else 'p < 0.01 ✓✓' if p < 0.01 else 'p < 0.05 ✓' if p < 0.05 else 'n.s.'
            color = COLORS['complete'] if p < 0.05 else COLORS['failed']
            
            fig.add_trace(go.Indicator(
                mode="number+delta",
                value=p,
                number={'font': {'size': 32, 'family': FONTS['mono']}, 'valueformat': '.2e'},
                delta={'reference': 0.05, 'decreasing': {'color': COLORS['complete']}},
                title={'text': f'{metric}<br><span style="font-size:0.8em;color:{color}">{sig_level}</span>'},
                domain={'row': 0, 'column': i}
            ))
        
        fig.update_layout(
            **create_base_layout('🔬 Statistical Significance', 200),
            grid={'rows': 1, 'columns': 2, 'pattern': 'independent'},
        )
        
        return fig


# ============================================================================
# Monte Carlo Simulation Panel
# ============================================================================

class MonteCarloPanel:
    """Monte Carlo simulation controls and results visualization."""
    
    @staticmethod
    def create_simulation_results(df: pd.DataFrame) -> go.Figure:
        """Create comprehensive simulation results dashboard."""
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=[
                '⏱️ Latency Distribution',
                '⭐ Quality Distribution', 
                '📊 Status Breakdown',
                '🎯 Quality vs Latency',
                '📈 Agent Response Times',
                '✅ Success Rates'
            ],
            specs=[
                [{'type': 'histogram'}, {'type': 'histogram'}, {'type': 'pie'}],
                [{'type': 'scatter'}, {'type': 'violin'}, {'type': 'bar'}]
            ],
            vertical_spacing=0.12,
            horizontal_spacing=0.08,
        )
        
        # Latency histogram with KDE approximation
        fig.add_trace(
            go.Histogram(
                x=df['latency'],
                nbinsx=50,
                marker_color=COLORS['gradient'][0],
                opacity=0.7,
                name='Latency',
            ),
            row=1, col=1
        )
        
        # Quality histogram
        fig.add_trace(
            go.Histogram(
                x=df['quality'],
                nbinsx=30,
                marker_color=COLORS['complete'],
                opacity=0.7,
                name='Quality',
            ),
            row=1, col=2
        )
        
        # Status pie chart
        status_counts = df['status'].value_counts()
        status_colors = [
            COLORS.get(s, '#888888') for s in status_counts.index
        ]
        
        fig.add_trace(
            go.Pie(
                labels=status_counts.index,
                values=status_counts.values,
                marker_colors=status_colors,
                textinfo='label+percent',
                textfont={'size': 10},
                hole=0.4,
            ),
            row=1, col=3
        )
        
        # Quality vs Latency scatter
        fig.add_trace(
            go.Scatter(
                x=df['latency'],
                y=df['quality'],
                mode='markers',
                marker={
                    'size': 4,
                    'color': df['num_results'],
                    'colorscale': 'RdYlGn',
                    'opacity': 0.5,
                },
                name='Samples',
            ),
            row=2, col=1
        )
        
        # Agent response time violin plots
        agent_cols = [c for c in df.columns if c.endswith('_time')]
        if agent_cols:
            for col in agent_cols:
                agent_name = col.replace('_time', '')
                fig.add_trace(
                    go.Violin(
                        y=df[col],
                        name=agent_name.title(),
                        marker_color=COLORS.get(agent_name, '#888888'),
                        box_visible=True,
                        meanline_visible=True,
                    ),
                    row=2, col=2
                )
        
        # Success rates bar chart
        success_cols = [c for c in df.columns if c.endswith('_success')]
        if success_cols:
            agents = [c.replace('_success', '') for c in success_cols]
            rates = [df[c].mean() * 100 for c in success_cols]
            
            fig.add_trace(
                go.Bar(
                    x=agents,
                    y=rates,
                    marker_color=[COLORS.get(a, '#888888') for a in agents],
                    text=[f'{r:.1f}%' for r in rates],
                    textposition='outside',
                ),
                row=2, col=3
            )
        
        fig.update_layout(
            **create_base_layout(f'🎲 Monte Carlo Simulation Results (N={len(df):,})', 650),
            showlegend=False,
        )
        
        return fig
    
    @staticmethod
    def create_convergence_plot(n_values: list[int], metric_values: list[float], 
                                 metric_name: str = 'Mean Latency') -> go.Figure:
        """Create convergence visualization for Monte Carlo estimation."""
        fig = go.Figure()
        
        # Main convergence line
        fig.add_trace(go.Scatter(
            x=n_values,
            y=metric_values,
            mode='lines+markers',
            name='Estimate',
            line={'color': COLORS['highlight'], 'width': 2},
            marker={'size': 6},
        ))
        
        # Confidence band (approximate)
        if len(n_values) > 1:
            final_value = metric_values[-1]
            stds = [abs(v - final_value) * 2 for v in metric_values]
            
            fig.add_trace(go.Scatter(
                x=n_values + n_values[::-1],
                y=[v + s for v, s in zip(metric_values, stds)] + 
                  [v - s for v, s in zip(metric_values[::-1], stds[::-1])],
                fill='toself',
                fillcolor='rgba(233, 69, 96, 0.2)',
                line={'color': 'rgba(0,0,0,0)'},
                name='95% CI',
            ))
        
        fig.update_layout(
            **create_base_layout(f'📈 Monte Carlo Convergence: {metric_name}', 350),
            xaxis_title='Number of Simulations',
            yaxis_title=metric_name,
            xaxis_type='log',
        )
        
        return fig


# ============================================================================
# Agent Performance Panel
# ============================================================================

class AgentPerformancePanel:
    """Agent-level performance analytics."""
    
    @staticmethod
    def create_response_time_comparison(df: pd.DataFrame) -> go.Figure:
        """Create agent response time comparison."""
        agent_cols = [c for c in df.columns if c.endswith('_time')]
        
        fig = go.Figure()
        
        for col in agent_cols:
            agent_name = col.replace('_time', '')
            fig.add_trace(go.Box(
                y=df[col],
                name=agent_name.title(),
                marker_color=COLORS.get(agent_name, '#888888'),
                boxpoints='outliers',
                jitter=0.3,
            ))
        
        fig.update_layout(
            **create_base_layout('⏱️ Agent Response Time Distribution', 400),
            yaxis_title='Response Time (s)',
        )
        
        return fig
    
    @staticmethod
    def create_reliability_gauge(df: pd.DataFrame) -> go.Figure:
        """Create agent reliability gauges."""
        success_cols = [c for c in df.columns if c.endswith('_success')]
        n_agents = len(success_cols)
        
        fig = make_subplots(
            rows=1, cols=n_agents,
            specs=[[{'type': 'indicator'}] * n_agents],
        )
        
        for i, col in enumerate(success_cols):
            agent_name = col.replace('_success', '')
            reliability = df[col].mean() * 100
            
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=reliability,
                    number={'suffix': '%', 'font': {'family': FONTS['mono'], 'size': 24}},
                    title={'text': agent_name.title(), 'font': {'size': 14}},
                    gauge={
                        'axis': {'range': [80, 100]},
                        'bar': {'color': COLORS.get(agent_name, '#888888')},
                        'steps': [
                            {'range': [80, 90], 'color': 'rgba(220, 53, 69, 0.3)'},
                            {'range': [90, 95], 'color': 'rgba(255, 193, 7, 0.3)'},
                            {'range': [95, 100], 'color': 'rgba(0, 217, 165, 0.3)'},
                        ],
                        'threshold': {
                            'line': {'color': 'white', 'width': 2},
                            'thickness': 0.75,
                            'value': 95
                        }
                    }
                ),
                row=1, col=i+1
            )
        
        fig.update_layout(
            **create_base_layout('✅ Agent Reliability', 250),
        )
        
        return fig
    
    @staticmethod
    def create_correlation_matrix(df: pd.DataFrame) -> go.Figure:
        """Create correlation matrix of agent metrics."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        corr = df[numeric_cols].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.index,
            colorscale='RdBu_r',
            zmid=0,
            text=np.round(corr.values, 2),
            texttemplate='%{text}',
            textfont={'size': 10},
            colorbar={'title': 'Correlation'},
        ))
        
        layout = create_base_layout('🔗 Metric Correlations', 500)
        layout['xaxis']['tickangle'] = 45
        fig.update_layout(**layout)
        
        return fig

