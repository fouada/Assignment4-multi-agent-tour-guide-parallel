"""
Comprehensive Tests for Experimental Framework
==============================================

MIT-Level test suite for reproducible experiment infrastructure.

Test Categories:
1. ExperimentConfig - Configuration management
2. ExperimentResult - Result storage and analysis
3. ReproducibleExperiment - Base experiment class
4. ExperimentRunner - Experiment orchestration
5. FactorialDesign - Experimental design methods
6. Edge cases and error handling

Coverage Target: 85%+

Author: Multi-Agent Tour Guide Research Team
"""

import json
import tempfile
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pytest

from src.research.experimental_framework import (
    ExperimentConfig,
    ExperimentResult,
    ExperimentRunner,
    FactorialDesign,
    ReproducibleExperiment,
)


# ============================================================================
# ExperimentConfig Tests
# ============================================================================

class TestExperimentConfig:
    """Tests for ExperimentConfig dataclass."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = ExperimentConfig(name="test_exp")
        
        assert config.name == "test_exp"
        assert config.seed == 42
        assert config.n_replications == 10
        assert config.parameters == {}
    
    def test_custom_values(self):
        """Test custom configuration values."""
        params = {'soft_timeout': 15, 'hard_timeout': 30}
        config = ExperimentConfig(
            name="custom_exp",
            seed=123,
            n_replications=50,
            parameters=params
        )
        
        assert config.seed == 123
        assert config.n_replications == 50
        assert config.parameters == params
    
    def test_metadata_created_at(self):
        """Test that created_at timestamp is added."""
        config = ExperimentConfig(name="test")
        
        assert 'created_at' in config.metadata
    
    def test_metadata_config_hash(self):
        """Test that config hash is computed."""
        config = ExperimentConfig(name="test")
        
        assert 'config_hash' in config.metadata
        assert len(config.metadata['config_hash']) == 16
    
    def test_config_hash_deterministic(self):
        """Test that config hash is deterministic."""
        config1 = ExperimentConfig(name="test", seed=42, parameters={'a': 1})
        config2 = ExperimentConfig(name="test", seed=42, parameters={'a': 1})
        
        # Hashes should be the same (ignoring created_at)
        assert config1._compute_hash() == config2._compute_hash()
    
    def test_config_hash_different(self):
        """Test that different configs have different hashes."""
        config1 = ExperimentConfig(name="test", parameters={'a': 1})
        config2 = ExperimentConfig(name="test", parameters={'a': 2})
        
        assert config1._compute_hash() != config2._compute_hash()
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = ExperimentConfig(
            name="test",
            seed=123,
            parameters={'x': 10}
        )
        
        d = config.to_dict()
        
        assert d['name'] == "test"
        assert d['seed'] == 123
        assert d['parameters'] == {'x': 10}
    
    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            'name': 'loaded',
            'seed': 456,
            'n_replications': 20,
            'parameters': {'y': 5},
            'metadata': {'custom': 'data'}
        }
        
        config = ExperimentConfig.from_dict(data)
        
        assert config.name == 'loaded'
        assert config.seed == 456
        assert config.n_replications == 20


# ============================================================================
# ExperimentResult Tests
# ============================================================================

class TestExperimentResult:
    """Tests for ExperimentResult dataclass."""
    
    @pytest.fixture
    def sample_config(self):
        return ExperimentConfig(name="test_result", seed=42)
    
    @pytest.fixture
    def sample_result(self, sample_config):
        return ExperimentResult(
            config=sample_config,
            metrics={'latency_mean': 10.5, 'quality_mean': 7.2},
            raw_data={'latency': [9, 10, 11, 12], 'quality': [7, 7, 7.5, 7.3]},
            duration_seconds=5.5,
            status="completed"
        )
    
    def test_result_creation(self, sample_config):
        """Test basic result creation."""
        result = ExperimentResult(config=sample_config)
        
        assert result.config == sample_config
        assert result.metrics == {}
        assert result.status == "completed"
    
    def test_result_with_data(self, sample_result):
        """Test result with metrics and raw data."""
        assert sample_result.metrics['latency_mean'] == 10.5
        assert len(sample_result.raw_data['latency']) == 4
    
    def test_summary(self, sample_result):
        """Test summary generation."""
        summary = sample_result.summary()
        
        assert summary['experiment_name'] == 'test_result'
        assert summary['status'] == 'completed'
        assert summary['duration_seconds'] == 5.5
        assert 'metrics' in summary
        
        # Should include statistical summaries
        assert 'latency_mean' in summary
        assert 'latency_std' in summary
        assert 'latency_median' in summary
    
    def test_summary_min_max(self, sample_result):
        """Test summary includes min/max."""
        summary = sample_result.summary()
        
        assert summary['latency_min'] == 9
        assert summary['latency_max'] == 12
    
    def test_save_and_load(self, sample_result, tmp_path):
        """Test saving and loading results."""
        path = tmp_path / "result.json"
        sample_result.save(path)
        
        assert path.exists()
        
        loaded = ExperimentResult.load(path)
        
        assert loaded.config.name == sample_result.config.name
        assert loaded.metrics == sample_result.metrics
        assert loaded.duration_seconds == sample_result.duration_seconds
    
    def test_save_creates_directory(self, sample_result, tmp_path):
        """Test that save creates parent directories."""
        path = tmp_path / "nested" / "dir" / "result.json"
        sample_result.save(path)
        
        assert path.exists()
    
    def test_failed_result(self, sample_config):
        """Test failed result with error message."""
        result = ExperimentResult(
            config=sample_config,
            status="failed",
            error_message="Test error"
        )
        
        assert result.status == "failed"
        assert result.error_message == "Test error"


# ============================================================================
# ReproducibleExperiment Tests
# ============================================================================

class DummyExperiment(ReproducibleExperiment):
    """Concrete implementation for testing."""
    
    def __init__(self, config: ExperimentConfig):
        super().__init__(config)
        self.setup_called = False
        self.teardown_called = False
        self.trial_count = 0
    
    def setup(self):
        self.setup_called = True
    
    def run_trial(self, trial_id: int) -> Dict[str, Any]:
        self.trial_count += 1
        # Use numpy random which was seeded
        latency = 10 + np.random.normal(0, 1)
        quality = 7 + np.random.normal(0, 0.5)
        return {'latency': latency, 'quality': quality}
    
    def teardown(self):
        self.teardown_called = True


class FailingExperiment(ReproducibleExperiment):
    """Experiment that fails for testing error handling."""
    
    def setup(self):
        pass
    
    def run_trial(self, trial_id: int) -> Dict[str, Any]:
        if trial_id >= 2:
            raise ValueError("Simulated failure")
        return {'value': trial_id}
    
    def teardown(self):
        pass


class TestReproducibleExperiment:
    """Tests for ReproducibleExperiment base class."""
    
    def test_experiment_execution(self):
        """Test basic experiment execution."""
        config = ExperimentConfig(name="test", n_replications=5)
        exp = DummyExperiment(config)
        
        result = exp.execute()
        
        assert exp.setup_called
        assert exp.teardown_called
        assert exp.trial_count == 5
        assert result.status == "completed"
    
    def test_experiment_reproducibility(self):
        """Test that experiments are reproducible with same seed."""
        config = ExperimentConfig(name="test", seed=42, n_replications=3)
        
        exp1 = DummyExperiment(config)
        result1 = exp1.execute()
        
        exp2 = DummyExperiment(config)
        result2 = exp2.execute()
        
        # Results should be identical
        assert result1.raw_data['latency'] == result2.raw_data['latency']
    
    def test_experiment_different_seeds(self):
        """Test that different seeds give different results."""
        config1 = ExperimentConfig(name="test", seed=42, n_replications=3)
        config2 = ExperimentConfig(name="test", seed=123, n_replications=3)
        
        result1 = DummyExperiment(config1).execute()
        result2 = DummyExperiment(config2).execute()
        
        assert result1.raw_data['latency'] != result2.raw_data['latency']
    
    def test_experiment_metrics_computed(self):
        """Test that aggregate metrics are computed."""
        config = ExperimentConfig(name="test", n_replications=10)
        result = DummyExperiment(config).execute()
        
        assert 'latency_mean' in result.metrics
        assert 'latency_std' in result.metrics
        assert 'latency_ci_lower' in result.metrics
        assert 'latency_ci_upper' in result.metrics
    
    def test_experiment_failure_handling(self):
        """Test handling of experiment failures."""
        config = ExperimentConfig(name="failing", n_replications=5)
        exp = FailingExperiment(config)
        
        result = exp.execute()
        
        assert result.status == "failed"
        assert result.error_message is not None
        assert "Simulated failure" in result.error_message
    
    def test_experiment_duration_recorded(self):
        """Test that duration is recorded."""
        config = ExperimentConfig(name="test", n_replications=3)
        result = DummyExperiment(config).execute()
        
        assert result.duration_seconds > 0


# ============================================================================
# ExperimentRunner Tests
# ============================================================================

class TestExperimentRunner:
    """Tests for ExperimentRunner class."""
    
    @pytest.fixture
    def runner(self, tmp_path):
        return ExperimentRunner(
            experiment_class=DummyExperiment,
            output_dir=tmp_path,
            verbose=False
        )
    
    def test_run_single(self, runner):
        """Test running a single experiment."""
        config = ExperimentConfig(name="single_test", n_replications=3)
        result = runner.run_single(config)
        
        assert result.status == "completed"
        assert len(runner.results) == 1
    
    def test_run_single_saves_result(self, runner, tmp_path):
        """Test that result is saved to disk."""
        config = ExperimentConfig(name="save_test", n_replications=2)
        runner.run_single(config)
        
        # Check that file was created
        files = list(tmp_path.glob("*.json"))
        assert len(files) == 1
    
    def test_run_parameter_sweep(self, runner):
        """Test parameter sweep execution."""
        base_config = ExperimentConfig(
            name="sweep",
            n_replications=2,
            parameters={'base_param': 1}
        )
        
        results = runner.run_parameter_sweep(
            base_config,
            parameter_grid={
                'x': [1, 2],
                'y': [10, 20]
            }
        )
        
        # Should have 2x2 = 4 configurations
        assert len(results) == 4
        assert len(runner.results) == 4
    
    def test_parameter_sweep_preserves_base(self, runner):
        """Test that sweep preserves base parameters."""
        base_config = ExperimentConfig(
            name="sweep",
            n_replications=2,
            parameters={'fixed': 100}
        )
        
        results = runner.run_parameter_sweep(
            base_config,
            parameter_grid={'varied': [1, 2]}
        )
        
        for result in results:
            assert result.config.parameters['fixed'] == 100
    
    def test_compare_results(self, runner):
        """Test result comparison."""
        # Run some experiments
        for i in range(3):
            config = ExperimentConfig(
                name=f"comp_{i}",
                n_replications=5,
                parameters={'variant': i}
            )
            runner.run_single(config)
        
        comparison = runner.compare_results('latency')
        
        assert comparison['metric'] == 'latency'
        assert len(comparison['experiments']) == 3
        assert comparison['best'] is not None
        assert comparison['worst'] is not None
    
    def test_compare_results_empty(self, runner):
        """Test comparison with no results."""
        comparison = runner.compare_results('latency')
        
        assert comparison['experiments'] == []
        assert comparison['best'] is None
    
    def test_verbose_logging(self, tmp_path, capsys):
        """Test verbose logging output."""
        runner = ExperimentRunner(
            experiment_class=DummyExperiment,
            output_dir=tmp_path,
            verbose=True
        )
        
        config = ExperimentConfig(name="verbose_test", n_replications=2)
        runner.run_single(config)
        
        captured = capsys.readouterr()
        assert "Starting experiment" in captured.out
        assert "Completed" in captured.out


# ============================================================================
# FactorialDesign Tests
# ============================================================================

class TestFactorialDesign:
    """Tests for FactorialDesign class."""
    
    def test_full_factorial_2k_two_factors(self):
        """Test 2^2 factorial design."""
        factors = {
            'A': (0, 1),
            'B': (0, 1)
        }
        
        designs = FactorialDesign.full_factorial_2k(factors)
        
        assert len(designs) == 4  # 2^2 = 4
        
        # Check all combinations present
        combos = [(d['A'], d['B']) for d in designs]
        assert (0, 0) in combos
        assert (0, 1) in combos
        assert (1, 0) in combos
        assert (1, 1) in combos
    
    def test_full_factorial_2k_three_factors(self):
        """Test 2^3 factorial design."""
        factors = {
            'X': (10, 20),
            'Y': (100, 200),
            'Z': (0.1, 0.9)
        }
        
        designs = FactorialDesign.full_factorial_2k(factors)
        
        assert len(designs) == 8  # 2^3 = 8
    
    def test_full_factorial_values(self):
        """Test that factorial uses actual values."""
        factors = {
            'temp': (20, 80),
            'pressure': (1, 10)
        }
        
        designs = FactorialDesign.full_factorial_2k(factors)
        
        # Should have actual values, not coded
        temps = {d['temp'] for d in designs}
        assert temps == {20, 80}
    
    def test_add_center_points(self):
        """Test adding center points."""
        factors = {
            'A': (0, 10),
            'B': (100, 200)
        }
        
        designs = FactorialDesign.full_factorial_2k(factors)
        designs_with_center = FactorialDesign.add_center_points(designs, factors, n_center=3)
        
        assert len(designs_with_center) == 4 + 3  # 4 corners + 3 centers
        
        # Check center point values
        center_points = designs_with_center[4:]
        for cp in center_points:
            assert cp['A'] == 5  # (0+10)/2
            assert cp['B'] == 150  # (100+200)/2
    
    def test_add_center_points_custom_count(self):
        """Test adding custom number of center points."""
        factors = {'X': (0, 1)}
        designs = FactorialDesign.full_factorial_2k(factors)
        
        designs_5 = FactorialDesign.add_center_points(designs, factors, n_center=5)
        assert len(designs_5) == 2 + 5
    
    def test_analyze_effects(self):
        """Test effect analysis."""
        factors = {
            'A': (0, 10),
            'B': (0, 20)
        }
        
        # Create results: response = 5*A + 2*B + interaction
        results = [
            ({'A': 0, 'B': 0}, 0),
            ({'A': 10, 'B': 0}, 50),
            ({'A': 0, 'B': 20}, 40),
            ({'A': 10, 'B': 20}, 100),  # 50 + 40 + 10 interaction
        ]
        
        effects = FactorialDesign.analyze_effects(results, factors)
        
        assert 'A' in effects
        assert 'B' in effects
        assert 'A:B' in effects
        
        # A has larger effect than B in this example
        assert effects['A'] > effects['B']
    
    def test_analyze_effects_no_interaction(self):
        """Test effect analysis with no interaction."""
        factors = {
            'X': (0, 1),
            'Y': (0, 1)
        }
        
        # Pure additive: response = 10*X + 5*Y
        results = [
            ({'X': 0, 'Y': 0}, 0),
            ({'X': 1, 'Y': 0}, 10),
            ({'X': 0, 'Y': 1}, 5),
            ({'X': 1, 'Y': 1}, 15),
        ]
        
        effects = FactorialDesign.analyze_effects(results, factors)
        
        # Interaction should be zero or very small
        assert abs(effects['X:Y']) < 0.1


# ============================================================================
# Edge Cases
# ============================================================================

class TestEdgeCases:
    """Edge case tests for the framework."""
    
    def test_empty_parameters(self):
        """Test config with empty parameters."""
        config = ExperimentConfig(name="empty", parameters={})
        assert config.parameters == {}
    
    def test_single_replication(self):
        """Test with single replication."""
        config = ExperimentConfig(name="single", n_replications=1)
        result = DummyExperiment(config).execute()
        
        assert len(result.raw_data['latency']) == 1
    
    def test_zero_replications(self):
        """Test with zero replications."""
        config = ExperimentConfig(name="zero", n_replications=0)
        result = DummyExperiment(config).execute()
        
        assert result.raw_data == {}
    
    def test_large_replications(self):
        """Test with many replications."""
        config = ExperimentConfig(name="large", n_replications=100)
        result = DummyExperiment(config).execute()
        
        assert len(result.raw_data['latency']) == 100
    
    def test_special_characters_in_name(self):
        """Test config name with special characters."""
        config = ExperimentConfig(name="test-exp_v1.0")
        assert config.name == "test-exp_v1.0"
    
    def test_nested_parameters(self):
        """Test nested parameter structures."""
        config = ExperimentConfig(
            name="nested",
            parameters={
                'outer': {
                    'inner': [1, 2, 3]
                }
            }
        )
        assert config.parameters['outer']['inner'] == [1, 2, 3]
    
    def test_result_empty_raw_data(self):
        """Test result summary with empty raw data."""
        config = ExperimentConfig(name="empty")
        result = ExperimentResult(config=config, raw_data={})
        
        summary = result.summary()
        assert 'experiment_name' in summary
    
    def test_factorial_single_factor(self):
        """Test factorial design with single factor."""
        factors = {'X': (0, 1)}
        designs = FactorialDesign.full_factorial_2k(factors)
        
        assert len(designs) == 2
    
    def test_runner_missing_metric(self, tmp_path):
        """Test comparison with missing metric."""
        runner = ExperimentRunner(
            DummyExperiment,
            output_dir=tmp_path,
            verbose=False
        )
        
        config = ExperimentConfig(name="test", n_replications=2)
        runner.run_single(config)
        
        # Try to compare non-existent metric
        comparison = runner.compare_results('nonexistent')
        assert comparison['experiments'] == []

