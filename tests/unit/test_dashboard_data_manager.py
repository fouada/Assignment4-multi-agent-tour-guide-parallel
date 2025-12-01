"""
Comprehensive Tests for Dashboard Data Manager
==============================================

MIT-Level test suite with edge case coverage for the dashboard data management layer.

Test Categories:
1. QueueConfig - Configuration validation
2. AgentConfig - Agent parameter validation  
3. SimulationResult - Result structure validation
4. SmartQueueSimulator - Core simulation engine
5. DashboardDataManager - Data management operations
6. Edge Cases - Boundary conditions and error handling

Coverage Target: 85%+

Author: Multi-Agent Tour Guide Research Team
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from src.dashboard.data_manager import (
    AgentConfig,
    DashboardDataManager,
    QueueConfig,
    QueueStatus,
    SimulationResult,
    SmartQueueSimulator,
)


# ============================================================================
# QueueConfig Tests
# ============================================================================

class TestQueueConfig:
    """Tests for QueueConfig dataclass."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = QueueConfig()
        assert config.soft_timeout == 15.0
        assert config.hard_timeout == 30.0
        assert config.min_for_soft == 2
        assert config.min_for_hard == 1
        assert config.expected_agents == 3
    
    def test_custom_values(self):
        """Test custom configuration values."""
        config = QueueConfig(
            soft_timeout=10.0,
            hard_timeout=20.0,
            min_for_soft=1,
            min_for_hard=1,
            expected_agents=5
        )
        assert config.soft_timeout == 10.0
        assert config.hard_timeout == 20.0
        assert config.min_for_soft == 1
        assert config.expected_agents == 5
    
    def test_edge_case_zero_timeout(self):
        """Test edge case with zero timeouts."""
        config = QueueConfig(soft_timeout=0.0, hard_timeout=0.0)
        assert config.soft_timeout == 0.0
        assert config.hard_timeout == 0.0
    
    def test_edge_case_large_timeout(self):
        """Test edge case with very large timeouts."""
        config = QueueConfig(soft_timeout=1000.0, hard_timeout=10000.0)
        assert config.soft_timeout == 1000.0
        assert config.hard_timeout == 10000.0
    
    def test_edge_case_negative_timeout(self):
        """Test edge case with negative timeouts (should still work as dataclass)."""
        config = QueueConfig(soft_timeout=-1.0, hard_timeout=-1.0)
        assert config.soft_timeout == -1.0  # Dataclass allows this


# ============================================================================
# AgentConfig Tests
# ============================================================================

class TestAgentConfig:
    """Tests for AgentConfig dataclass."""
    
    def test_agent_config_creation(self):
        """Test agent configuration creation."""
        agent = AgentConfig(
            name="test_agent",
            mu=1.0,
            sigma=0.5,
            shift=0.3,
            reliability=0.95,
            quality_mean=7.0,
            quality_std=1.5
        )
        assert agent.name == "test_agent"
        assert agent.mu == 1.0
        assert agent.sigma == 0.5
        assert agent.shift == 0.3
        assert agent.reliability == 0.95
        assert agent.quality_mean == 7.0
        assert agent.quality_std == 1.5
    
    def test_edge_case_zero_reliability(self):
        """Test agent with zero reliability (always fails)."""
        agent = AgentConfig(
            name="unreliable",
            mu=1.0, sigma=0.5, shift=0.3,
            reliability=0.0,
            quality_mean=7.0, quality_std=1.5
        )
        assert agent.reliability == 0.0
    
    def test_edge_case_perfect_reliability(self):
        """Test agent with perfect reliability (never fails)."""
        agent = AgentConfig(
            name="perfect",
            mu=1.0, sigma=0.5, shift=0.3,
            reliability=1.0,
            quality_mean=7.0, quality_std=1.5
        )
        assert agent.reliability == 1.0
    
    def test_edge_case_zero_variance(self):
        """Test agent with zero variance (deterministic response time)."""
        agent = AgentConfig(
            name="deterministic",
            mu=1.0, sigma=0.0, shift=0.5,
            reliability=0.95,
            quality_mean=7.0, quality_std=0.0
        )
        assert agent.sigma == 0.0
        assert agent.quality_std == 0.0


# ============================================================================
# QueueStatus Tests
# ============================================================================

class TestQueueStatus:
    """Tests for QueueStatus enum."""
    
    def test_all_status_values(self):
        """Test all queue status values exist."""
        assert QueueStatus.WAITING.value == "waiting"
        assert QueueStatus.COMPLETE.value == "complete"
        assert QueueStatus.SOFT_DEGRADED.value == "soft_degraded"
        assert QueueStatus.HARD_DEGRADED.value == "hard_degraded"
        assert QueueStatus.FAILED.value == "failed"
    
    def test_status_from_value(self):
        """Test creating status from string value."""
        status = QueueStatus("complete")
        assert status == QueueStatus.COMPLETE


# ============================================================================
# SimulationResult Tests
# ============================================================================

class TestSimulationResult:
    """Tests for SimulationResult dataclass."""
    
    def test_result_creation(self):
        """Test simulation result creation."""
        result = SimulationResult(
            status=QueueStatus.COMPLETE,
            latency=5.0,
            num_results=3,
            quality=8.5
        )
        assert result.status == QueueStatus.COMPLETE
        assert result.latency == 5.0
        assert result.num_results == 3
        assert result.quality == 8.5
        assert result.agent_times == {}
        assert result.agent_success == {}
    
    def test_result_with_agent_data(self):
        """Test result with agent-level data."""
        result = SimulationResult(
            status=QueueStatus.SOFT_DEGRADED,
            latency=15.0,
            num_results=2,
            quality=7.0,
            agent_times={"video": 3.0, "music": 2.0, "text": 20.0},
            agent_success={"video": True, "music": True, "text": False}
        )
        assert result.agent_times["video"] == 3.0
        assert result.agent_success["text"] is False
    
    def test_failed_result(self):
        """Test failed simulation result."""
        result = SimulationResult(
            status=QueueStatus.FAILED,
            latency=30.0,
            num_results=0,
            quality=0.0
        )
        assert result.status == QueueStatus.FAILED
        assert result.quality == 0.0


# ============================================================================
# SmartQueueSimulator Tests
# ============================================================================

class TestSmartQueueSimulator:
    """Comprehensive tests for SmartQueueSimulator."""
    
    def test_default_initialization(self):
        """Test simulator with default configuration."""
        sim = SmartQueueSimulator()
        assert sim.queue_config.soft_timeout == 15.0
        assert len(sim.agents) == 3
    
    def test_custom_config(self):
        """Test simulator with custom configuration."""
        config = QueueConfig(soft_timeout=10.0, hard_timeout=20.0)
        sim = SmartQueueSimulator(queue_config=config)
        assert sim.queue_config.soft_timeout == 10.0
        assert sim.queue_config.hard_timeout == 20.0
    
    def test_custom_agents(self):
        """Test simulator with custom agents."""
        agents = [
            AgentConfig("agent1", 0.5, 0.2, 0.1, 0.99, 8.0, 1.0),
            AgentConfig("agent2", 0.6, 0.3, 0.2, 0.95, 7.5, 1.2),
        ]
        config = QueueConfig(expected_agents=2)
        sim = SmartQueueSimulator(queue_config=config, agents=agents)
        assert len(sim.agents) == 2
    
    def test_simulate_single_returns_result(self):
        """Test that simulate_single returns a SimulationResult."""
        np.random.seed(42)
        sim = SmartQueueSimulator()
        result = sim.simulate_single()
        
        assert isinstance(result, SimulationResult)
        assert isinstance(result.status, QueueStatus)
        assert result.latency >= 0
        assert 0 <= result.quality <= 10
        assert 0 <= result.num_results <= 3
    
    def test_simulate_single_deterministic_with_seed(self):
        """Test simulation reproducibility with fixed seed."""
        np.random.seed(12345)
        sim = SmartQueueSimulator()
        result1 = sim.simulate_single()
        
        np.random.seed(12345)
        sim2 = SmartQueueSimulator()
        result2 = sim2.simulate_single()
        
        assert result1.latency == result2.latency
        assert result1.quality == result2.quality
        assert result1.status == result2.status
    
    def test_monte_carlo_returns_dataframe(self):
        """Test Monte Carlo simulation returns DataFrame."""
        np.random.seed(42)
        sim = SmartQueueSimulator()
        df = sim.run_monte_carlo(n_simulations=100)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 100
        assert 'status' in df.columns
        assert 'latency' in df.columns
        assert 'quality' in df.columns
        assert 'num_results' in df.columns
    
    def test_monte_carlo_includes_agent_data(self):
        """Test Monte Carlo includes agent-level data."""
        np.random.seed(42)
        sim = SmartQueueSimulator()
        df = sim.run_monte_carlo(n_simulations=50)
        
        assert 'video_time' in df.columns
        assert 'music_time' in df.columns
        assert 'text_time' in df.columns
        assert 'video_success' in df.columns
    
    def test_edge_case_all_agents_fail(self):
        """Test edge case where all agents fail."""
        agents = [
            AgentConfig("agent1", 0.5, 0.2, 0.1, 0.0, 8.0, 1.0),  # 0% reliability
            AgentConfig("agent2", 0.6, 0.3, 0.2, 0.0, 7.5, 1.2),
            AgentConfig("agent3", 0.7, 0.4, 0.3, 0.0, 7.0, 1.3),
        ]
        sim = SmartQueueSimulator(agents=agents)
        result = sim.simulate_single()
        
        assert result.status == QueueStatus.FAILED
        assert result.num_results == 0
        assert result.quality == 0.0
    
    def test_edge_case_all_agents_succeed_fast(self):
        """Test edge case where all agents succeed very fast."""
        np.random.seed(42)
        agents = [
            AgentConfig("agent1", -2.0, 0.1, 0.01, 1.0, 9.0, 0.1),  # Very fast, always succeeds
            AgentConfig("agent2", -2.0, 0.1, 0.01, 1.0, 9.0, 0.1),
            AgentConfig("agent3", -2.0, 0.1, 0.01, 1.0, 9.0, 0.1),
        ]
        sim = SmartQueueSimulator(agents=agents)
        result = sim.simulate_single()
        
        assert result.status == QueueStatus.COMPLETE
        assert result.num_results == 3
    
    def test_edge_case_very_short_timeout(self):
        """Test with very short timeouts causing degradation."""
        np.random.seed(42)
        config = QueueConfig(soft_timeout=0.1, hard_timeout=0.2)
        sim = SmartQueueSimulator(queue_config=config)
        
        # Run multiple times to ensure we hit timeout scenarios
        results = [sim.simulate_single() for _ in range(100)]
        
        # Should have mostly degraded or failed results due to short timeouts
        degraded_or_failed = sum(1 for r in results if r.status != QueueStatus.COMPLETE)
        assert degraded_or_failed > 0  # At least some should timeout
    
    def test_edge_case_single_simulation(self):
        """Test Monte Carlo with single simulation."""
        sim = SmartQueueSimulator()
        df = sim.run_monte_carlo(n_simulations=1)
        assert len(df) == 1
    
    def test_status_distribution_reasonable(self):
        """Test that status distribution is reasonable over many simulations."""
        np.random.seed(42)
        sim = SmartQueueSimulator()
        df = sim.run_monte_carlo(n_simulations=1000)
        
        status_counts = df['status'].value_counts(normalize=True)
        
        # With default config, we expect mostly complete/soft_degraded
        # and very few failed
        assert status_counts.get('failed', 0) < 0.1  # Less than 10% failed
    
    def test_quality_bounded(self):
        """Test that quality scores are always in valid range."""
        np.random.seed(42)
        sim = SmartQueueSimulator()
        df = sim.run_monte_carlo(n_simulations=500)
        
        assert df['quality'].min() >= 0
        assert df['quality'].max() <= 10
    
    def test_latency_non_negative(self):
        """Test that latency is always non-negative."""
        np.random.seed(42)
        sim = SmartQueueSimulator()
        df = sim.run_monte_carlo(n_simulations=500)
        
        assert df['latency'].min() >= 0


# ============================================================================
# DashboardDataManager Tests
# ============================================================================

class TestDashboardDataManager:
    """Comprehensive tests for DashboardDataManager."""
    
    @pytest.fixture
    def data_manager(self, tmp_path):
        """Create a data manager with temp cache directory."""
        return DashboardDataManager(cache_dir=tmp_path / "cache")
    
    def test_initialization(self, data_manager):
        """Test data manager initialization."""
        assert data_manager.cache_dir.exists()
        assert data_manager._cache == {}
    
    def test_get_baseline_simulation(self, data_manager):
        """Test baseline simulation generation."""
        np.random.seed(42)
        df = data_manager.get_baseline_simulation(n_sims=100)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 100
        assert 'status' in df.columns
        assert 'latency' in df.columns
    
    def test_baseline_caching(self, data_manager):
        """Test that baseline results are cached."""
        np.random.seed(42)
        df1 = data_manager.get_baseline_simulation(n_sims=100)
        df2 = data_manager.get_baseline_simulation(n_sims=100)
        
        # Should be same object from cache
        pd.testing.assert_frame_equal(df1, df2)
    
    def test_baseline_force_refresh(self, data_manager):
        """Test force refresh bypasses cache."""
        np.random.seed(42)
        df1 = data_manager.get_baseline_simulation(n_sims=100)
        
        np.random.seed(123)
        df2 = data_manager.get_baseline_simulation(n_sims=100, force_refresh=True)
        
        # Should be different due to different seeds
        assert not df1['latency'].equals(df2['latency'])
    
    def test_baseline_custom_config(self, data_manager):
        """Test baseline with custom configuration."""
        config = QueueConfig(soft_timeout=5.0, hard_timeout=10.0)
        df = data_manager.get_baseline_simulation(n_sims=100, config=config)
        
        # With shorter timeouts, more should hit the timeout limits
        assert len(df) == 100
    
    def test_run_sensitivity_analysis(self, data_manager):
        """Test sensitivity analysis execution."""
        np.random.seed(42)
        param_values = [5.0, 10.0, 15.0]
        results = data_manager.run_sensitivity_analysis(
            'soft_timeout', param_values, n_sims=50
        )
        
        assert isinstance(results, pd.DataFrame)
        assert len(results) == 3
        assert 'param_value' in results.columns
        assert 'latency_mean' in results.columns
        assert 'quality_mean' in results.columns
        assert 'complete_rate' in results.columns
        assert 'success_rate' in results.columns
    
    def test_sensitivity_with_callback(self, data_manager):
        """Test sensitivity analysis with progress callback."""
        progress_values = []
        
        def callback(progress):
            progress_values.append(progress)
        
        np.random.seed(42)
        data_manager.run_sensitivity_analysis(
            'soft_timeout', [5.0, 10.0], n_sims=50, callback=callback
        )
        
        assert len(progress_values) == 2
        assert progress_values[-1] == 1.0
    
    def test_run_pareto_analysis(self, data_manager):
        """Test Pareto frontier analysis."""
        np.random.seed(42)
        results = data_manager.run_pareto_analysis(
            soft_timeout_range=(5, 15),
            hard_timeout_range=(10, 25),
            n_points=9,  # 3x3 grid
            n_sims=50
        )
        
        assert isinstance(results, pd.DataFrame)
        assert 'soft_timeout' in results.columns
        assert 'hard_timeout' in results.columns
        assert 'latency_mean' in results.columns
        assert 'quality_mean' in results.columns
    
    def test_pareto_excludes_invalid_combos(self, data_manager):
        """Test that Pareto excludes hard <= soft combinations."""
        np.random.seed(42)
        results = data_manager.run_pareto_analysis(
            soft_timeout_range=(10, 20),
            hard_timeout_range=(10, 30),
            n_points=16,
            n_sims=50
        )
        
        # All hard_timeout should be > soft_timeout
        for _, row in results.iterrows():
            assert row['hard_timeout'] > row['soft_timeout']
    
    def test_compare_configurations(self, data_manager):
        """Test configuration comparison."""
        np.random.seed(42)
        config_a = QueueConfig(soft_timeout=15.0, hard_timeout=30.0)
        config_b = QueueConfig(soft_timeout=8.0, hard_timeout=15.0)
        
        comparison = data_manager.compare_configurations(config_a, config_b, n_sims=100)
        
        assert 'config_a' in comparison
        assert 'config_b' in comparison
        assert 'df_a' in comparison
        assert 'df_b' in comparison
        assert 'latency' in comparison
        assert 'quality' in comparison
        assert 'status_a' in comparison
        assert 'status_b' in comparison
    
    def test_compare_configurations_statistics(self, data_manager):
        """Test that comparison includes proper statistics."""
        np.random.seed(42)
        config_a = QueueConfig(soft_timeout=15.0, hard_timeout=30.0)
        config_b = QueueConfig(soft_timeout=8.0, hard_timeout=15.0)
        
        comparison = data_manager.compare_configurations(config_a, config_b, n_sims=500)
        
        # Check latency statistics
        lat = comparison['latency']
        assert 'mean_a' in lat
        assert 'mean_b' in lat
        assert 'std_a' in lat
        assert 'std_b' in lat
        assert 'p_value' in lat
        assert 'cohens_d' in lat
        
        # p_value should be valid
        assert 0 <= lat['p_value'] <= 1
    
    def test_get_real_time_metrics(self, data_manager):
        """Test real-time metrics generation."""
        metrics = data_manager.get_real_time_metrics()
        
        assert 'timestamp' in metrics
        assert 'active_tours' in metrics
        assert 'queue_depth' in metrics
        assert 'agents' in metrics
        assert 'throughput' in metrics
        assert 'error_rate' in metrics
    
    def test_real_time_metrics_agent_data(self, data_manager):
        """Test real-time metrics include agent data."""
        metrics = data_manager.get_real_time_metrics()
        
        agents = metrics['agents']
        assert 'video' in agents
        assert 'music' in agents
        assert 'text' in agents
        
        for agent_data in agents.values():
            assert 'status' in agent_data
            assert 'avg_response_time' in agent_data
            assert 'success_rate' in agent_data
    
    def test_export_results(self, data_manager, tmp_path):
        """Test exporting results to JSON."""
        np.random.seed(42)
        data_manager.get_baseline_simulation(n_sims=50)
        data_manager.run_sensitivity_analysis('soft_timeout', [5.0, 10.0], n_sims=50)
        
        output_path = tmp_path / "results.json"
        data_manager.export_results(output_path)
        
        assert output_path.exists()
        
        with open(output_path) as f:
            exported = json.load(f)
        
        assert 'timestamp' in exported
        assert 'baseline_stats' in exported
        assert 'sensitivity_data' in exported
    
    def test_export_results_empty(self, data_manager, tmp_path):
        """Test exporting when no data is cached."""
        output_path = tmp_path / "empty_results.json"
        data_manager.export_results(output_path)
        
        assert output_path.exists()
        
        with open(output_path) as f:
            exported = json.load(f)
        
        assert exported['baseline_stats'] is None


# ============================================================================
# Edge Cases and Error Handling Tests
# ============================================================================

class TestEdgeCases:
    """Edge case and boundary condition tests."""
    
    def test_empty_param_values_sensitivity(self):
        """Test sensitivity analysis with empty parameter list."""
        dm = DashboardDataManager()
        results = dm.run_sensitivity_analysis('soft_timeout', [], n_sims=50)
        assert len(results) == 0
    
    def test_single_param_value_sensitivity(self):
        """Test sensitivity analysis with single parameter value."""
        np.random.seed(42)
        dm = DashboardDataManager()
        results = dm.run_sensitivity_analysis('soft_timeout', [10.0], n_sims=50)
        assert len(results) == 1
    
    def test_large_simulation_count(self):
        """Test handling of large simulation count."""
        np.random.seed(42)
        sim = SmartQueueSimulator()
        df = sim.run_monte_carlo(n_simulations=5000)
        assert len(df) == 5000
    
    def test_extreme_timeout_values(self):
        """Test with extreme timeout values."""
        config = QueueConfig(soft_timeout=0.001, hard_timeout=0.001)
        sim = SmartQueueSimulator(queue_config=config)
        result = sim.simulate_single()
        
        # Should still produce valid result
        assert isinstance(result, SimulationResult)
    
    def test_thread_safety_cache(self, tmp_path):
        """Test that cache operations are thread-safe."""
        import threading
        
        dm = DashboardDataManager(cache_dir=tmp_path / "cache")
        errors = []
        
        def run_simulation():
            try:
                np.random.seed()
                dm.get_baseline_simulation(n_sims=50, force_refresh=True)
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=run_simulation) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0


# ============================================================================
# Statistical Validation Tests
# ============================================================================

class TestStatisticalValidation:
    """Tests validating statistical properties of simulations."""
    
    def test_mean_convergence(self):
        """Test that mean converges with more samples."""
        np.random.seed(42)
        sim = SmartQueueSimulator()
        
        df_small = sim.run_monte_carlo(n_simulations=100)
        np.random.seed(42)
        df_large = sim.run_monte_carlo(n_simulations=10000)
        
        # Means should be closer to true value with more samples
        # (We can't know the true value, but variance should decrease)
        assert df_large['latency'].std() / np.sqrt(10000) < df_small['latency'].std() / np.sqrt(100)
    
    def test_status_probability_distribution(self):
        """Test that status distribution follows expected probabilities."""
        np.random.seed(42)
        sim = SmartQueueSimulator()
        df = sim.run_monte_carlo(n_simulations=5000)
        
        status_dist = df['status'].value_counts(normalize=True)
        
        # Given default reliabilities (92%, 95%, 98%), failure rate should be low
        # P(all fail) ≈ 0.08 * 0.05 * 0.02 = 0.00008
        assert status_dist.get('failed', 0) < 0.01  # Less than 1%
    
    def test_agent_response_time_distribution(self):
        """Test that agent response times follow expected distribution."""
        np.random.seed(42)
        sim = SmartQueueSimulator()
        df = sim.run_monte_carlo(n_simulations=1000)
        
        # Video agent has highest mean (mu=1.0, shift=0.5)
        # Text agent has lowest mean (mu=0.6, shift=0.2)
        assert df['video_time'].mean() > df['text_time'].mean()

