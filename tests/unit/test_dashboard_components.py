"""
Comprehensive Tests for Dashboard Components
=============================================

MIT-Level test suite for visualization components with edge case coverage.

Test Categories:
1. Color scheme validation
2. Layout creation
3. SystemMonitorPanel
4. SensitivityPanel
5. ParetoFrontierPanel
6. StatisticalComparisonPanel
7. MonteCarloPanel
8. AgentPerformancePanel
9. Edge cases for visualizations

Coverage Target: 85%+

Author: Multi-Agent Tour Guide Research Team
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pytest

from src.dashboard.components import (
    COLORS,
    FONTS,
    AgentPerformancePanel,
    MonteCarloPanel,
    ParetoFrontierPanel,
    SensitivityPanel,
    StatisticalComparisonPanel,
    SystemMonitorPanel,
    create_base_layout,
)


# ============================================================================
# Color and Font Configuration Tests
# ============================================================================

class TestColorConfiguration:
    """Tests for color scheme configuration."""
    
    def test_primary_colors_exist(self):
        """Test that primary colors are defined."""
        assert 'primary' in COLORS
        assert 'secondary' in COLORS
        assert 'accent' in COLORS
        assert 'highlight' in COLORS
    
    def test_status_colors_exist(self):
        """Test that status colors are defined."""
        assert 'complete' in COLORS
        assert 'soft_degraded' in COLORS
        assert 'hard_degraded' in COLORS
        assert 'failed' in COLORS
    
    def test_agent_colors_exist(self):
        """Test that agent colors are defined."""
        assert 'video' in COLORS
        assert 'music' in COLORS
        assert 'text' in COLORS
        assert 'judge' in COLORS
    
    def test_colors_are_valid_hex(self):
        """Test that color values are valid hex codes."""
        for key, value in COLORS.items():
            if isinstance(value, str) and value.startswith('#'):
                # Should be valid 6-digit hex
                assert len(value) == 7
                int(value[1:], 16)  # Should not raise
    
    def test_gradient_colors(self):
        """Test gradient color list exists."""
        assert 'gradient' in COLORS
        assert isinstance(COLORS['gradient'], list)
        assert len(COLORS['gradient']) >= 2


class TestFontConfiguration:
    """Tests for font configuration."""
    
    def test_font_families_exist(self):
        """Test that font families are defined."""
        assert 'title' in FONTS
        assert 'body' in FONTS
        assert 'mono' in FONTS
    
    def test_fonts_are_strings(self):
        """Test that fonts are string values."""
        for font in FONTS.values():
            assert isinstance(font, str)


# ============================================================================
# Base Layout Tests
# ============================================================================

class TestBaseLayout:
    """Tests for base layout creation."""
    
    def test_create_base_layout_default(self):
        """Test default layout creation."""
        layout = create_base_layout()
        
        assert 'paper_bgcolor' in layout
        assert 'plot_bgcolor' in layout
        assert 'font' in layout
        assert 'margin' in layout
    
    def test_create_base_layout_with_title(self):
        """Test layout with custom title."""
        layout = create_base_layout(title='Test Title')
        
        assert layout['title']['text'] == 'Test Title'
    
    def test_create_base_layout_with_height(self):
        """Test layout with custom height."""
        layout = create_base_layout(height=800)
        
        assert layout['height'] == 800
    
    def test_layout_has_axis_styling(self):
        """Test that layout includes axis styling."""
        layout = create_base_layout()
        
        assert 'xaxis' in layout
        assert 'yaxis' in layout
        assert 'gridcolor' in layout['xaxis']


# ============================================================================
# SystemMonitorPanel Tests
# ============================================================================

class TestSystemMonitorPanel:
    """Tests for SystemMonitorPanel."""
    
    @pytest.fixture
    def sample_metrics(self):
        """Sample metrics data."""
        return {
            'agents': {
                'video': {'status': 'healthy', 'avg_response_time': 2.5, 'success_rate': 0.92},
                'music': {'status': 'healthy', 'avg_response_time': 2.0, 'success_rate': 0.95},
                'text': {'status': 'degraded', 'avg_response_time': 1.5, 'success_rate': 0.98},
            },
            'throughput': 15.5,
            'queue_depth': 8,
        }
    
    def test_create_agent_status_cards(self, sample_metrics):
        """Test agent status card creation."""
        fig = SystemMonitorPanel.create_agent_status_cards(sample_metrics)
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 3  # One indicator per agent
    
    def test_agent_status_cards_empty_metrics(self):
        """Test with empty metrics."""
        fig = SystemMonitorPanel.create_agent_status_cards({'agents': {}})
        
        assert isinstance(fig, go.Figure)
    
    def test_create_throughput_chart_with_data(self):
        """Test throughput chart with history data."""
        history = [
            {'timestamp': i, 'throughput': np.random.uniform(5, 20)}
            for i in range(30)
        ]
        fig = SystemMonitorPanel.create_throughput_chart(history)
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) >= 1
    
    def test_create_throughput_chart_empty(self):
        """Test throughput chart with empty history."""
        fig = SystemMonitorPanel.create_throughput_chart([])
        
        assert isinstance(fig, go.Figure)
        # Should generate default data
    
    def test_create_queue_depth_chart_with_data(self):
        """Test queue depth chart with data."""
        depth_history = [np.random.randint(0, 20) for _ in range(60)]
        fig = SystemMonitorPanel.create_queue_depth_chart(depth_history)
        
        assert isinstance(fig, go.Figure)
    
    def test_create_queue_depth_chart_empty(self):
        """Test queue depth chart with empty data."""
        fig = SystemMonitorPanel.create_queue_depth_chart([])
        
        assert isinstance(fig, go.Figure)


# ============================================================================
# SensitivityPanel Tests
# ============================================================================

class TestSensitivityPanel:
    """Tests for SensitivityPanel."""
    
    @pytest.fixture
    def sample_sensitivity_data(self):
        """Sample sensitivity analysis data."""
        return pd.DataFrame({
            'param_value': [5, 10, 15, 20, 25],
            'latency_mean': [8.0, 10.0, 12.0, 14.0, 16.0],
            'latency_std': [1.0, 1.2, 1.4, 1.6, 1.8],
            'quality_mean': [5.5, 6.0, 6.5, 7.0, 7.2],
            'quality_std': [0.5, 0.6, 0.7, 0.8, 0.9],
            'complete_rate': [0.4, 0.5, 0.6, 0.7, 0.75],
            'degraded_rate': [0.4, 0.35, 0.3, 0.25, 0.2],
            'failed_rate': [0.2, 0.15, 0.1, 0.05, 0.05],
            'success_rate': [0.8, 0.85, 0.9, 0.95, 0.95],
        })
    
    def test_create_parameter_impact_chart(self, sample_sensitivity_data):
        """Test parameter impact chart creation."""
        fig = SensitivityPanel.create_parameter_impact_chart(
            sample_sensitivity_data, 'soft_timeout'
        )
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) >= 4  # Multiple traces
    
    def test_create_tornado_chart(self):
        """Test tornado chart creation."""
        sensitivities = {
            'Latency Impact': 0.35,
            'Quality Impact': -0.15,
            'Success Rate': 0.10,
        }
        fig = SensitivityPanel.create_tornado_chart(sensitivities)
        
        assert isinstance(fig, go.Figure)
    
    def test_tornado_chart_empty(self):
        """Test tornado chart with empty data."""
        fig = SensitivityPanel.create_tornado_chart({})
        
        assert isinstance(fig, go.Figure)
    
    def test_tornado_chart_negative_values(self):
        """Test tornado chart with negative values."""
        sensitivities = {
            'Param A': -0.5,
            'Param B': -0.3,
            'Param C': -0.1,
        }
        fig = SensitivityPanel.create_tornado_chart(sensitivities)
        
        assert isinstance(fig, go.Figure)


# ============================================================================
# ParetoFrontierPanel Tests
# ============================================================================

class TestParetoFrontierPanel:
    """Tests for ParetoFrontierPanel."""
    
    @pytest.fixture
    def sample_pareto_data(self):
        """Sample Pareto analysis data."""
        np.random.seed(42)
        n_points = 20
        
        soft_vals = np.linspace(5, 25, 5)
        hard_vals = np.linspace(10, 50, 4)
        
        rows = []
        for soft in soft_vals:
            for hard in hard_vals:
                if hard > soft:
                    rows.append({
                        'soft_timeout': soft,
                        'hard_timeout': hard,
                        'latency_mean': soft + np.random.uniform(-1, 1),
                        'quality_mean': 5 + (soft / 5) + np.random.uniform(-0.5, 0.5),
                        'success_rate': 0.9 + np.random.uniform(0, 0.1),
                        'complete_rate': 0.7 + np.random.uniform(0, 0.2),
                    })
        
        return pd.DataFrame(rows)
    
    def test_create_3d_pareto_surface(self, sample_pareto_data):
        """Test 3D Pareto surface creation."""
        fig = ParetoFrontierPanel.create_3d_pareto_surface(sample_pareto_data)
        
        assert isinstance(fig, go.Figure)
    
    def test_create_pareto_scatter(self, sample_pareto_data):
        """Test 2D Pareto scatter creation."""
        fig = ParetoFrontierPanel.create_pareto_scatter(sample_pareto_data)
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) >= 2  # At least non-pareto and pareto points
    
    def test_create_heatmap(self, sample_pareto_data):
        """Test heatmap creation."""
        fig = ParetoFrontierPanel.create_heatmap(sample_pareto_data)
        
        assert isinstance(fig, go.Figure)
    
    def test_pareto_scatter_identifies_optimal(self, sample_pareto_data):
        """Test that Pareto scatter identifies optimal points."""
        fig = ParetoFrontierPanel.create_pareto_scatter(sample_pareto_data)
        
        # Should have trace for pareto-optimal points
        trace_names = [t.name for t in fig.data if hasattr(t, 'name')]
        assert 'Pareto-optimal' in trace_names


# ============================================================================
# StatisticalComparisonPanel Tests
# ============================================================================

class TestStatisticalComparisonPanel:
    """Tests for StatisticalComparisonPanel."""
    
    @pytest.fixture
    def sample_comparison_dfs(self):
        """Sample comparison DataFrames."""
        np.random.seed(42)
        n = 500
        
        df_a = pd.DataFrame({
            'latency': np.random.normal(15, 3, n),
            'quality': np.random.normal(7, 1, n),
            'status': np.random.choice(['complete', 'soft_degraded', 'failed'], n, p=[0.7, 0.25, 0.05]),
        })
        
        df_b = pd.DataFrame({
            'latency': np.random.normal(10, 2, n),
            'quality': np.random.normal(6.5, 1.2, n),
            'status': np.random.choice(['complete', 'soft_degraded', 'failed'], n, p=[0.6, 0.3, 0.1]),
        })
        
        return df_a, df_b
    
    @pytest.fixture
    def sample_comparison_stats(self):
        """Sample comparison statistics."""
        return {
            'latency': {
                'mean_a': 15.0, 'mean_b': 10.0,
                'std_a': 3.0, 'std_b': 2.0,
                'p_value': 0.001, 'cohens_d': 0.5,
            },
            'quality': {
                'mean_a': 7.0, 'mean_b': 6.5,
                'std_a': 1.0, 'std_b': 1.2,
                'p_value': 0.02, 'cohens_d': 0.3,
            },
        }
    
    def test_create_distribution_comparison(self, sample_comparison_dfs):
        """Test distribution comparison creation."""
        df_a, df_b = sample_comparison_dfs
        fig = StatisticalComparisonPanel.create_distribution_comparison(
            df_a, df_b, ('Config A', 'Config B')
        )
        
        assert isinstance(fig, go.Figure)
    
    def test_create_effect_size_chart(self, sample_comparison_stats):
        """Test effect size chart creation."""
        fig = StatisticalComparisonPanel.create_effect_size_chart(sample_comparison_stats)
        
        assert isinstance(fig, go.Figure)
    
    def test_create_significance_summary(self, sample_comparison_stats):
        """Test significance summary creation."""
        fig = StatisticalComparisonPanel.create_significance_summary(sample_comparison_stats)
        
        assert isinstance(fig, go.Figure)


# ============================================================================
# MonteCarloPanel Tests
# ============================================================================

class TestMonteCarloPanel:
    """Tests for MonteCarloPanel."""
    
    @pytest.fixture
    def sample_mc_data(self):
        """Sample Monte Carlo simulation data."""
        np.random.seed(42)
        n = 200
        
        return pd.DataFrame({
            'status': np.random.choice(['complete', 'soft_degraded', 'hard_degraded', 'failed'], n, p=[0.6, 0.25, 0.1, 0.05]),
            'latency': np.random.lognormal(2, 0.5, n),
            'quality': np.clip(np.random.normal(7, 1.5, n), 0, 10),
            'num_results': np.random.randint(0, 4, n),
            'video_time': np.random.lognormal(1, 0.5, n),
            'music_time': np.random.lognormal(0.8, 0.4, n),
            'text_time': np.random.lognormal(0.6, 0.3, n),
            'video_success': np.random.random(n) > 0.08,
            'music_success': np.random.random(n) > 0.05,
            'text_success': np.random.random(n) > 0.02,
        })
    
    def test_create_simulation_results(self, sample_mc_data):
        """Test simulation results visualization."""
        fig = MonteCarloPanel.create_simulation_results(sample_mc_data)
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) >= 3  # Multiple subplots
    
    def test_create_convergence_plot(self):
        """Test convergence plot creation."""
        n_values = [100, 500, 1000, 2000, 5000]
        metric_values = [12.5, 12.2, 12.1, 12.05, 12.0]
        
        fig = MonteCarloPanel.create_convergence_plot(n_values, metric_values, 'Mean Latency')
        
        assert isinstance(fig, go.Figure)
    
    def test_convergence_plot_single_point(self):
        """Test convergence plot with single point."""
        fig = MonteCarloPanel.create_convergence_plot([100], [12.0], 'Mean')
        
        assert isinstance(fig, go.Figure)


# ============================================================================
# AgentPerformancePanel Tests
# ============================================================================

class TestAgentPerformancePanel:
    """Tests for AgentPerformancePanel."""
    
    @pytest.fixture
    def sample_agent_data(self):
        """Sample agent performance data."""
        np.random.seed(42)
        n = 200
        
        return pd.DataFrame({
            'video_time': np.random.lognormal(1, 0.5, n),
            'music_time': np.random.lognormal(0.8, 0.4, n),
            'text_time': np.random.lognormal(0.6, 0.3, n),
            'video_success': np.random.random(n) > 0.08,
            'music_success': np.random.random(n) > 0.05,
            'text_success': np.random.random(n) > 0.02,
            'latency': np.random.lognormal(2, 0.5, n),
            'quality': np.clip(np.random.normal(7, 1.5, n), 0, 10),
        })
    
    def test_create_response_time_comparison(self, sample_agent_data):
        """Test response time comparison creation."""
        fig = AgentPerformancePanel.create_response_time_comparison(sample_agent_data)
        
        assert isinstance(fig, go.Figure)
    
    def test_create_reliability_gauge(self, sample_agent_data):
        """Test reliability gauge creation."""
        fig = AgentPerformancePanel.create_reliability_gauge(sample_agent_data)
        
        assert isinstance(fig, go.Figure)
    
    def test_create_correlation_matrix(self, sample_agent_data):
        """Test correlation matrix creation."""
        fig = AgentPerformancePanel.create_correlation_matrix(sample_agent_data)
        
        assert isinstance(fig, go.Figure)


# ============================================================================
# Edge Cases for Visualizations
# ============================================================================

class TestVisualizationEdgeCases:
    """Edge case tests for all visualization components."""
    
    def test_empty_dataframe_handling(self):
        """Test handling of empty DataFrames."""
        empty_df = pd.DataFrame(columns=['status', 'latency', 'quality', 'num_results'])
        
        # Should not raise
        fig = MonteCarloPanel.create_simulation_results(empty_df)
        assert isinstance(fig, go.Figure)
    
    def test_single_row_dataframe(self):
        """Test handling of single-row DataFrame."""
        single_df = pd.DataFrame({
            'status': ['complete'],
            'latency': [10.0],
            'quality': [7.5],
            'num_results': [3],
            'video_time': [3.0],
            'music_time': [2.0],
            'text_time': [1.5],
            'video_success': [True],
            'music_success': [True],
            'text_success': [True],
        })
        
        fig = MonteCarloPanel.create_simulation_results(single_df)
        assert isinstance(fig, go.Figure)
    
    def test_extreme_values_in_data(self):
        """Test handling of extreme values."""
        extreme_df = pd.DataFrame({
            'soft_timeout': [0.001, 1000],
            'hard_timeout': [0.002, 10000],
            'latency_mean': [0.0001, 9999],
            'quality_mean': [0, 10],
            'success_rate': [0, 1],
            'complete_rate': [0, 1],
        })
        
        fig = ParetoFrontierPanel.create_pareto_scatter(extreme_df)
        assert isinstance(fig, go.Figure)
    
    def test_nan_values_in_data(self):
        """Test handling of NaN values."""
        nan_df = pd.DataFrame({
            'soft_timeout': [5, 10, np.nan, 20],
            'hard_timeout': [10, 20, 30, np.nan],
            'latency_mean': [10, np.nan, 14, 16],
            'quality_mean': [np.nan, 6, 7, 8],
            'success_rate': [0.9, 0.95, np.nan, 0.92],
            'complete_rate': [0.7, 0.75, 0.8, 0.85],
        })
        
        # Should handle NaN gracefully
        fig = ParetoFrontierPanel.create_heatmap(nan_df)
        assert isinstance(fig, go.Figure)
    
    def test_all_same_values(self):
        """Test with all identical values."""
        uniform_df = pd.DataFrame({
            'param_value': [10, 10, 10, 10],
            'latency_mean': [5, 5, 5, 5],
            'latency_std': [0, 0, 0, 0],
            'quality_mean': [7, 7, 7, 7],
            'quality_std': [0, 0, 0, 0],
            'complete_rate': [0.8, 0.8, 0.8, 0.8],
            'degraded_rate': [0.15, 0.15, 0.15, 0.15],
            'failed_rate': [0.05, 0.05, 0.05, 0.05],
            'success_rate': [0.95, 0.95, 0.95, 0.95],
        })
        
        fig = SensitivityPanel.create_parameter_impact_chart(uniform_df, 'test_param')
        assert isinstance(fig, go.Figure)
    
    def test_unicode_in_labels(self):
        """Test handling of unicode characters in labels."""
        sensitivities = {
            '延迟影响': 0.3,  # Chinese
            'השפעה': 0.2,    # Hebrew
            'تأثير': 0.1,    # Arabic
        }
        
        fig = SensitivityPanel.create_tornado_chart(sensitivities)
        assert isinstance(fig, go.Figure)
    
    def test_very_long_labels(self):
        """Test handling of very long labels."""
        sensitivities = {
            'A' * 100: 0.3,
            'B' * 100: 0.2,
        }
        
        fig = SensitivityPanel.create_tornado_chart(sensitivities)
        assert isinstance(fig, go.Figure)


# ============================================================================
# Performance Tests
# ============================================================================

class TestVisualizationPerformance:
    """Performance-related tests for visualizations."""
    
    def test_large_dataset_handling(self):
        """Test handling of large datasets."""
        np.random.seed(42)
        large_df = pd.DataFrame({
            'status': np.random.choice(['complete', 'soft_degraded', 'failed'], 10000),
            'latency': np.random.lognormal(2, 0.5, 10000),
            'quality': np.clip(np.random.normal(7, 1.5, 10000), 0, 10),
            'num_results': np.random.randint(0, 4, 10000),
            'video_time': np.random.lognormal(1, 0.5, 10000),
            'music_time': np.random.lognormal(0.8, 0.4, 10000),
            'text_time': np.random.lognormal(0.6, 0.3, 10000),
            'video_success': np.random.random(10000) > 0.08,
            'music_success': np.random.random(10000) > 0.05,
            'text_success': np.random.random(10000) > 0.02,
        })
        
        # Should complete without error
        fig = MonteCarloPanel.create_simulation_results(large_df)
        assert isinstance(fig, go.Figure)
    
    def test_many_pareto_points(self):
        """Test Pareto with many data points."""
        np.random.seed(42)
        n = 500
        
        pareto_df = pd.DataFrame({
            'soft_timeout': np.random.uniform(5, 30, n),
            'hard_timeout': np.random.uniform(10, 60, n),
            'latency_mean': np.random.uniform(5, 30, n),
            'quality_mean': np.random.uniform(4, 9, n),
            'success_rate': np.random.uniform(0.7, 1, n),
            'complete_rate': np.random.uniform(0.5, 0.9, n),
        })
        
        fig = ParetoFrontierPanel.create_pareto_scatter(pareto_df)
        assert isinstance(fig, go.Figure)

