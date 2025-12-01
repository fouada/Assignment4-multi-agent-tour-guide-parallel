"""
Experimental Framework for Reproducible Benchmarks
==================================================

MIT-Level Research Framework providing:
1. Reproducible experiment configuration
2. Systematic parameter exploration
3. Result persistence and analysis
4. Statistical validation

Author: Multi-Agent Tour Guide Research Team
Version: 1.0.0
Date: November 2025
"""

import hashlib
import json
import random
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np


@dataclass
class ExperimentConfig:
    """
    Configuration for a reproducible experiment.

    Attributes:
        name: Experiment identifier
        seed: Random seed for reproducibility
        n_replications: Number of experiment replications
        parameters: Dictionary of parameter settings
        metadata: Additional experiment metadata
    """

    name: str
    seed: int = 42
    n_replications: int = 10
    parameters: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.metadata["created_at"] = datetime.now().isoformat()
        self.metadata["config_hash"] = self._compute_hash()

    def _compute_hash(self) -> str:
        """Compute deterministic hash of configuration."""
        config_str = json.dumps(
            {
                "name": self.name,
                "seed": self.seed,
                "n_replications": self.n_replications,
                "parameters": self.parameters,
            },
            sort_keys=True,
        )
        return hashlib.sha256(config_str.encode()).hexdigest()[:16]

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ExperimentConfig":
        return cls(**data)


@dataclass
class ExperimentResult:
    """
    Result container for experiment outputs.

    Attributes:
        config: The experiment configuration
        metrics: Dictionary of measured metrics
        raw_data: Raw experiment data
        duration_seconds: Total experiment runtime
        status: Experiment completion status
    """

    config: ExperimentConfig
    metrics: dict[str, float] = field(default_factory=dict)
    raw_data: dict[str, list] = field(default_factory=dict)
    duration_seconds: float = 0.0
    status: str = "completed"
    error_message: str | None = None

    def summary(self) -> dict:
        """Generate summary statistics for the experiment."""
        summary = {
            "experiment_name": self.config.name,
            "config_hash": self.config.metadata.get("config_hash"),
            "status": self.status,
            "duration_seconds": self.duration_seconds,
            "metrics": self.metrics,
        }

        # Add statistical summaries for raw data
        for key, values in self.raw_data.items():
            if isinstance(values, list) and len(values) > 0:
                arr = np.array(values)
                summary[f"{key}_mean"] = float(np.mean(arr))
                summary[f"{key}_std"] = float(np.std(arr))
                summary[f"{key}_median"] = float(np.median(arr))
                summary[f"{key}_min"] = float(np.min(arr))
                summary[f"{key}_max"] = float(np.max(arr))

        return summary

    def save(self, path: Path):
        """Save result to JSON file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "config": self.config.to_dict(),
            "metrics": self.metrics,
            "raw_data": {k: list(v) for k, v in self.raw_data.items()},
            "duration_seconds": self.duration_seconds,
            "status": self.status,
            "error_message": self.error_message,
            "summary": self.summary(),
        }

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, path: Path) -> "ExperimentResult":
        """Load result from JSON file."""
        with open(path) as f:
            data = json.load(f)

        return cls(
            config=ExperimentConfig.from_dict(data["config"]),
            metrics=data["metrics"],
            raw_data=data["raw_data"],
            duration_seconds=data["duration_seconds"],
            status=data["status"],
            error_message=data.get("error_message"),
        )


class ReproducibleExperiment(ABC):
    """
    Abstract base class for reproducible experiments.

    Subclass this to create specific experiment types:

    Example:
        class QueueSensitivityExperiment(ReproducibleExperiment):
            def setup(self):
                # Initialize resources
                pass

            def run_trial(self, trial_id: int) -> Dict:
                # Run single trial
                return {'latency': measure_latency(), 'quality': measure_quality()}

            def teardown(self):
                # Cleanup
                pass
    """

    def __init__(self, config: ExperimentConfig):
        self.config = config
        self._set_seeds()

    def _set_seeds(self):
        """Set random seeds for reproducibility."""
        seed = self.config.seed
        random.seed(seed)
        np.random.seed(seed)

    @abstractmethod
    def setup(self):
        """Initialize experiment resources."""
        pass

    @abstractmethod
    def run_trial(self, trial_id: int) -> dict[str, Any]:
        """
        Run a single trial of the experiment.

        Args:
            trial_id: Unique identifier for this trial

        Returns:
            Dictionary of measurements from this trial
        """
        pass

    @abstractmethod
    def teardown(self):
        """Clean up experiment resources."""
        pass

    def execute(self) -> ExperimentResult:
        """
        Execute the full experiment.

        Returns:
            ExperimentResult containing all measurements
        """
        result = ExperimentResult(config=self.config)
        start_time = time.time()

        try:
            self.setup()

            # Run all replications
            trial_results = []
            for trial_id in range(self.config.n_replications):
                trial_data = self.run_trial(trial_id)
                trial_results.append(trial_data)

                # Aggregate into raw_data
                for key, value in trial_data.items():
                    if key not in result.raw_data:
                        result.raw_data[key] = []
                    result.raw_data[key].append(value)

            # Compute aggregate metrics
            for key, values in result.raw_data.items():
                arr = np.array(values)
                result.metrics[f"{key}_mean"] = float(np.mean(arr))
                result.metrics[f"{key}_std"] = float(np.std(arr))
                result.metrics[f"{key}_ci_lower"] = float(np.percentile(arr, 2.5))
                result.metrics[f"{key}_ci_upper"] = float(np.percentile(arr, 97.5))

            result.status = "completed"

        except Exception as e:
            result.status = "failed"
            result.error_message = str(e)

        finally:
            self.teardown()
            result.duration_seconds = time.time() - start_time

        return result


class ExperimentRunner:
    """
    Orchestrates execution of multiple experiments.

    Features:
    - Parameter grid search
    - Result persistence
    - Progress tracking
    - Comparative analysis

    Example:
        runner = ExperimentRunner(
            experiment_class=QueueSensitivityExperiment,
            output_dir=Path("./results")
        )

        results = runner.run_parameter_sweep(
            base_config=ExperimentConfig("sweep"),
            parameter_grid={
                'soft_timeout': [5, 10, 15, 20, 25, 30],
                'hard_timeout': [15, 30, 45, 60]
            }
        )
    """

    def __init__(
        self,
        experiment_class: type,
        output_dir: Path = Path("./experiment_results"),
        verbose: bool = True,
    ):
        self.experiment_class = experiment_class
        self.output_dir = Path(output_dir)
        self.verbose = verbose
        self.results: list[ExperimentResult] = []

    def _log(self, message: str):
        if self.verbose:
            print(f"[ExperimentRunner] {message}")

    def run_single(self, config: ExperimentConfig) -> ExperimentResult:
        """Run a single experiment configuration."""
        self._log(f"Starting experiment: {config.name}")

        experiment = self.experiment_class(config)
        result = experiment.execute()

        # Save result
        result_path = (
            self.output_dir / f"{config.name}_{config.metadata['config_hash']}.json"
        )
        result.save(result_path)

        self._log(f"Completed: {config.name} in {result.duration_seconds:.2f}s")
        self.results.append(result)

        return result

    def run_parameter_sweep(
        self, base_config: ExperimentConfig, parameter_grid: dict[str, list]
    ) -> list[ExperimentResult]:
        """
        Run experiments across a parameter grid.

        Args:
            base_config: Base configuration to modify
            parameter_grid: Dictionary mapping parameter names to value lists

        Returns:
            List of ExperimentResults for all configurations
        """
        from itertools import product

        # Generate all parameter combinations
        param_names = list(parameter_grid.keys())
        param_values = list(parameter_grid.values())
        combinations = list(product(*param_values))

        self._log(f"Running parameter sweep with {len(combinations)} configurations")

        results = []
        for i, combo in enumerate(combinations):
            # Create config for this combination
            params = dict(zip(param_names, combo, strict=False))
            config = ExperimentConfig(
                name=f"{base_config.name}_sweep_{i}",
                seed=base_config.seed,
                n_replications=base_config.n_replications,
                parameters={**base_config.parameters, **params},
                metadata={**base_config.metadata, "sweep_index": i},
            )

            result = self.run_single(config)
            results.append(result)

        return results

    def compare_results(self, metric_name: str) -> dict:
        """
        Compare a specific metric across all experiment results.

        Args:
            metric_name: Name of metric to compare

        Returns:
            Dictionary with comparison statistics
        """
        comparison = {
            "metric": metric_name,
            "experiments": [],
            "best": None,
            "worst": None,
        }

        for result in self.results:
            mean_key = f"{metric_name}_mean"
            if mean_key in result.metrics:
                entry = {
                    "name": result.config.name,
                    "parameters": result.config.parameters,
                    "value": result.metrics[mean_key],
                    "std": result.metrics.get(f"{metric_name}_std", 0),
                }
                comparison["experiments"].append(entry)

        if comparison["experiments"]:
            sorted_exp = sorted(comparison["experiments"], key=lambda x: x["value"])
            comparison["best"] = sorted_exp[0]
            comparison["worst"] = sorted_exp[-1]

        return comparison


class FactorialDesign:
    """
    Implements factorial experimental design for parameter analysis.

    Supports:
    - Full factorial (2^k)
    - Fractional factorial
    - Center points for curvature detection

    Reference: Montgomery, D.C. (2017). Design and Analysis of Experiments.
    """

    @staticmethod
    def full_factorial_2k(
        factors: dict[str, tuple[float, float]],
    ) -> list[dict[str, float]]:
        """
        Generate full 2^k factorial design.

        Args:
            factors: Dictionary mapping factor names to (low, high) tuples

        Returns:
            List of design points (parameter combinations)
        """
        from itertools import product

        factor_names = list(factors.keys())
        levels = [factors[f] for f in factor_names]

        designs = []
        for combo in product(*levels):
            designs.append(dict(zip(factor_names, combo, strict=False)))

        return designs

    @staticmethod
    def add_center_points(
        designs: list[dict[str, float]],
        factors: dict[str, tuple[float, float]],
        n_center: int = 3,
    ) -> list[dict[str, float]]:
        """
        Add center points to detect curvature.

        Args:
            designs: Existing design points
            factors: Factor bounds
            n_center: Number of center points to add

        Returns:
            Extended design with center points
        """
        center = {}
        for name, (low, high) in factors.items():
            center[name] = (low + high) / 2

        return designs + [center.copy() for _ in range(n_center)]

    @staticmethod
    def analyze_effects(
        results: list[tuple[dict[str, float], float]],
        factors: dict[str, tuple[float, float]],
    ) -> dict[str, float]:
        """
        Compute main effects and interactions for 2^k design.

        Args:
            results: List of (parameters, response) tuples
            factors: Factor bounds for coding

        Returns:
            Dictionary of effect estimates
        """
        # Code factors to -1/+1
        coded_results = []
        for params, response in results:
            coded = {}
            for name, value in params.items():
                low, high = factors[name]
                coded[name] = (2 * value - (high + low)) / (high - low)
            coded_results.append((coded, response))

        # Compute main effects
        effects = {}
        factor_names = list(factors.keys())

        for name in factor_names:
            high_mean = np.mean([r for p, r in coded_results if p[name] > 0])
            low_mean = np.mean([r for p, r in coded_results if p[name] < 0])
            effects[name] = high_mean - low_mean

        # Compute two-factor interactions
        for i, f1 in enumerate(factor_names):
            for f2 in factor_names[i + 1 :]:
                high_high = np.mean(
                    [r for p, r in coded_results if p[f1] > 0 and p[f2] > 0]
                )
                low_low = np.mean(
                    [r for p, r in coded_results if p[f1] < 0 and p[f2] < 0]
                )
                high_low = np.mean(
                    [r for p, r in coded_results if p[f1] > 0 and p[f2] < 0]
                )
                low_high = np.mean(
                    [r for p, r in coded_results if p[f1] < 0 and p[f2] > 0]
                )

                effects[f"{f1}:{f2}"] = (
                    (high_high + low_low) - (high_low + low_high)
                ) / 2

        return effects
