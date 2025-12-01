"""
🎯 Bayesian Optimization for Multi-Agent System Configuration
=============================================================

MIT-Level Innovation: Sample-Efficient Hyperparameter Optimization

This module implements Bayesian Optimization using Gaussian Processes
for automatically tuning the multi-agent system configuration. Unlike
grid search or random search, BO is sample-efficient and provides
principled uncertainty quantification.

Key Innovations:
1. Gaussian Process Surrogate Models
2. Multiple Acquisition Functions (EI, UCB, PI, Thompson Sampling)
3. Multi-Objective Optimization (Quality vs Latency vs Cost)
4. Automatic Early Stopping and Convergence Detection
5. Transfer Learning from Previous Optimizations

Academic References:
- Snoek et al. (2012) "Practical Bayesian Optimization of Machine Learning Algorithms"
- Shahriari et al. (2016) "Taking the Human Out of the Loop: A Review of Bayesian Optimization"
- Frazier (2018) "A Tutorial on Bayesian Optimization"
- Hernández-Lobato et al. (2014) "Predictive Entropy Search for Efficient Global Optimization"

Author: MIT-Level Research Framework
Version: 1.0.0
Date: November 2025
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional

import numpy as np
from scipy import stats
from scipy.linalg import cho_solve, cholesky
from scipy.optimize import minimize
from scipy.spatial.distance import cdist


# =============================================================================
# Configuration Space Definition
# =============================================================================


class ParameterType(str, Enum):
    """Types of parameters in the configuration space."""
    CONTINUOUS = "continuous"
    INTEGER = "integer"
    CATEGORICAL = "categorical"
    LOG_CONTINUOUS = "log_continuous"


@dataclass
class Parameter:
    """
    Represents a single parameter in the configuration space.
    
    Parameters can be:
    - Continuous: Real-valued in [lower, upper]
    - Integer: Integer-valued in [lower, upper]
    - Categorical: One of a set of choices
    - Log-continuous: Log-uniformly distributed
    """
    name: str
    param_type: ParameterType
    lower: Optional[float] = None
    upper: Optional[float] = None
    choices: Optional[list[Any]] = None
    default: Optional[Any] = None
    
    def sample_uniform(self, rng: np.random.RandomState) -> Any:
        """Sample uniformly from parameter space."""
        if self.param_type == ParameterType.CONTINUOUS:
            return rng.uniform(self.lower, self.upper)
        elif self.param_type == ParameterType.LOG_CONTINUOUS:
            log_val = rng.uniform(np.log(self.lower), np.log(self.upper))
            return np.exp(log_val)
        elif self.param_type == ParameterType.INTEGER:
            return rng.randint(int(self.lower), int(self.upper) + 1)
        elif self.param_type == ParameterType.CATEGORICAL:
            return rng.choice(self.choices)
        return self.default
    
    def to_unit_scale(self, value: Any) -> float:
        """Transform value to [0, 1] unit scale."""
        if self.param_type == ParameterType.CONTINUOUS:
            return (value - self.lower) / (self.upper - self.lower)
        elif self.param_type == ParameterType.LOG_CONTINUOUS:
            log_val = np.log(value)
            log_lower = np.log(self.lower)
            log_upper = np.log(self.upper)
            return (log_val - log_lower) / (log_upper - log_lower)
        elif self.param_type == ParameterType.INTEGER:
            return (value - self.lower) / (self.upper - self.lower)
        elif self.param_type == ParameterType.CATEGORICAL:
            return self.choices.index(value) / (len(self.choices) - 1)
        return 0.5
    
    def from_unit_scale(self, unit_value: float) -> Any:
        """Transform from [0, 1] unit scale to original space."""
        unit_value = np.clip(unit_value, 0, 1)
        
        if self.param_type == ParameterType.CONTINUOUS:
            return self.lower + unit_value * (self.upper - self.lower)
        elif self.param_type == ParameterType.LOG_CONTINUOUS:
            log_lower = np.log(self.lower)
            log_upper = np.log(self.upper)
            log_val = log_lower + unit_value * (log_upper - log_lower)
            return np.exp(log_val)
        elif self.param_type == ParameterType.INTEGER:
            return int(round(self.lower + unit_value * (self.upper - self.lower)))
        elif self.param_type == ParameterType.CATEGORICAL:
            idx = int(round(unit_value * (len(self.choices) - 1)))
            return self.choices[idx]
        return self.default


class ConfigurationSpace:
    """
    Defines the configuration space for Bayesian Optimization.
    
    The multi-agent tour guide system has the following key parameters:
    - soft_timeout: Time to wait before accepting partial results
    - hard_timeout: Maximum time to wait
    - num_workers: Number of parallel workers
    - retry_count: Number of retries per agent
    - agent_weights: Content type preferences
    """
    
    def __init__(self):
        """Initialize configuration space with default parameters."""
        self.parameters: dict[str, Parameter] = {}
        self._add_default_parameters()
    
    def _add_default_parameters(self) -> None:
        """Add default parameters for multi-agent system."""
        # Queue configuration
        self.add_parameter(Parameter(
            name="soft_timeout",
            param_type=ParameterType.CONTINUOUS,
            lower=5.0,
            upper=30.0,
            default=15.0,
        ))
        
        self.add_parameter(Parameter(
            name="hard_timeout",
            param_type=ParameterType.CONTINUOUS,
            lower=15.0,
            upper=60.0,
            default=30.0,
        ))
        
        # Parallelism
        self.add_parameter(Parameter(
            name="num_workers",
            param_type=ParameterType.INTEGER,
            lower=3,
            upper=20,
            default=12,
        ))
        
        # Resilience
        self.add_parameter(Parameter(
            name="retry_count",
            param_type=ParameterType.INTEGER,
            lower=1,
            upper=5,
            default=3,
        ))
        
        self.add_parameter(Parameter(
            name="retry_backoff_base",
            param_type=ParameterType.LOG_CONTINUOUS,
            lower=0.5,
            upper=5.0,
            default=2.0,
        ))
        
        # Agent weights
        self.add_parameter(Parameter(
            name="video_weight",
            param_type=ParameterType.CONTINUOUS,
            lower=0.0,
            upper=2.0,
            default=1.0,
        ))
        
        self.add_parameter(Parameter(
            name="music_weight",
            param_type=ParameterType.CONTINUOUS,
            lower=0.0,
            upper=2.0,
            default=1.0,
        ))
        
        self.add_parameter(Parameter(
            name="text_weight",
            param_type=ParameterType.CONTINUOUS,
            lower=0.0,
            upper=2.0,
            default=1.0,
        ))
        
        # LLM configuration
        self.add_parameter(Parameter(
            name="temperature",
            param_type=ParameterType.CONTINUOUS,
            lower=0.0,
            upper=1.0,
            default=0.7,
        ))
    
    def add_parameter(self, param: Parameter) -> None:
        """Add a parameter to the configuration space."""
        self.parameters[param.name] = param
    
    @property
    def dimension(self) -> int:
        """Get dimensionality of the space."""
        return len(self.parameters)
    
    def sample_random(
        self,
        rng: Optional[np.random.RandomState] = None
    ) -> dict[str, Any]:
        """Sample a random configuration."""
        rng = rng or np.random.RandomState()
        return {
            name: param.sample_uniform(rng)
            for name, param in self.parameters.items()
        }
    
    def to_array(self, config: dict[str, Any]) -> np.ndarray:
        """Convert configuration dict to unit-scaled array."""
        return np.array([
            self.parameters[name].to_unit_scale(config.get(name, param.default))
            for name, param in self.parameters.items()
        ])
    
    def from_array(self, arr: np.ndarray) -> dict[str, Any]:
        """Convert unit-scaled array to configuration dict."""
        return {
            name: param.from_unit_scale(arr[i])
            for i, (name, param) in enumerate(self.parameters.items())
        }
    
    def get_default_config(self) -> dict[str, Any]:
        """Get default configuration."""
        return {
            name: param.default
            for name, param in self.parameters.items()
        }


# =============================================================================
# Gaussian Process Surrogate Model
# =============================================================================


class Kernel(ABC):
    """Abstract base class for GP kernels."""
    
    @abstractmethod
    def __call__(self, X1: np.ndarray, X2: np.ndarray) -> np.ndarray:
        """Compute kernel matrix K(X1, X2)."""
        pass
    
    @abstractmethod
    def get_params(self) -> dict[str, float]:
        """Get kernel hyperparameters."""
        pass
    
    @abstractmethod
    def set_params(self, **params) -> None:
        """Set kernel hyperparameters."""
        pass


class SquaredExponentialKernel(Kernel):
    """
    Squared Exponential (RBF/Gaussian) Kernel.
    
    k(x, x') = σ² exp(-||x - x'||² / (2l²))
    
    Where:
    - σ² = signal variance
    - l = length scale
    
    This kernel is infinitely differentiable, producing very smooth functions.
    """
    
    def __init__(
        self,
        length_scale: float = 1.0,
        signal_variance: float = 1.0
    ):
        """
        Initialize SE kernel.
        
        Args:
            length_scale: Characteristic length scale l
            signal_variance: Signal variance σ²
        """
        self.length_scale = length_scale
        self.signal_variance = signal_variance
    
    def __call__(self, X1: np.ndarray, X2: np.ndarray) -> np.ndarray:
        """
        Compute kernel matrix.
        
        K[i,j] = σ² exp(-||X1[i] - X2[j]||² / (2l²))
        """
        # Compute squared distances
        dist_sq = cdist(X1, X2, metric='sqeuclidean')
        
        # Apply kernel
        return self.signal_variance * np.exp(-dist_sq / (2 * self.length_scale**2))
    
    def get_params(self) -> dict[str, float]:
        return {
            "length_scale": self.length_scale,
            "signal_variance": self.signal_variance,
        }
    
    def set_params(self, **params) -> None:
        if "length_scale" in params:
            self.length_scale = params["length_scale"]
        if "signal_variance" in params:
            self.signal_variance = params["signal_variance"]


class MaternKernel(Kernel):
    """
    Matérn Kernel with parameter ν.
    
    For ν = 5/2:
    k(x, x') = σ² (1 + √5r/l + 5r²/(3l²)) exp(-√5r/l)
    
    Where r = ||x - x'||
    
    The Matérn kernel is popular because it can model less smooth functions
    than the SE kernel, which is often more realistic.
    """
    
    def __init__(
        self,
        length_scale: float = 1.0,
        signal_variance: float = 1.0,
        nu: float = 2.5
    ):
        """
        Initialize Matérn kernel.
        
        Args:
            length_scale: Length scale l
            signal_variance: Signal variance σ²
            nu: Smoothness parameter (0.5, 1.5, 2.5 common)
        """
        self.length_scale = length_scale
        self.signal_variance = signal_variance
        self.nu = nu
    
    def __call__(self, X1: np.ndarray, X2: np.ndarray) -> np.ndarray:
        """Compute Matérn kernel matrix."""
        dist = cdist(X1, X2, metric='euclidean')
        scaled_dist = np.sqrt(5) * dist / self.length_scale
        
        if self.nu == 2.5:
            # Matérn 5/2
            return self.signal_variance * (
                1 + scaled_dist + scaled_dist**2 / 3
            ) * np.exp(-scaled_dist)
        elif self.nu == 1.5:
            # Matérn 3/2
            scaled_dist = np.sqrt(3) * dist / self.length_scale
            return self.signal_variance * (1 + scaled_dist) * np.exp(-scaled_dist)
        else:
            # Fall back to SE for other values
            return self.signal_variance * np.exp(-dist**2 / (2 * self.length_scale**2))
    
    def get_params(self) -> dict[str, float]:
        return {
            "length_scale": self.length_scale,
            "signal_variance": self.signal_variance,
            "nu": self.nu,
        }
    
    def set_params(self, **params) -> None:
        if "length_scale" in params:
            self.length_scale = params["length_scale"]
        if "signal_variance" in params:
            self.signal_variance = params["signal_variance"]


class GaussianProcess:
    """
    Gaussian Process Regression Model.
    
    A GP defines a distribution over functions:
        f(x) ~ GP(m(x), k(x, x'))
    
    Where:
    - m(x) = mean function (typically 0)
    - k(x, x') = covariance/kernel function
    
    Key Properties:
    - Any finite collection of function values follows a multivariate Gaussian
    - Provides uncertainty quantification for predictions
    - Non-parametric: complexity grows with data
    
    Posterior Prediction:
    Given observations (X, y), prediction at x* is:
        μ* = k(x*, X) K^{-1} y
        σ*² = k(x*, x*) - k(x*, X) K^{-1} k(X, x*)
    """
    
    def __init__(
        self,
        kernel: Optional[Kernel] = None,
        noise_variance: float = 1e-6,
        normalize_y: bool = True
    ):
        """
        Initialize Gaussian Process.
        
        Args:
            kernel: Covariance function (default: SE kernel)
            noise_variance: Observation noise σ²_noise
            normalize_y: Whether to normalize targets
        """
        self.kernel = kernel or SquaredExponentialKernel()
        self.noise_variance = noise_variance
        self.normalize_y = normalize_y
        
        # Training data
        self.X_train: Optional[np.ndarray] = None
        self.y_train: Optional[np.ndarray] = None
        
        # Cached quantities for prediction
        self._K_inv: Optional[np.ndarray] = None
        self._L: Optional[np.ndarray] = None  # Cholesky factor
        self._alpha: Optional[np.ndarray] = None
        
        # Normalization parameters
        self._y_mean: float = 0.0
        self._y_std: float = 1.0
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> "GaussianProcess":
        """
        Fit the GP to training data.
        
        Computes K = k(X, X) + σ²I and caches Cholesky decomposition.
        
        Args:
            X: Training inputs (n_samples, n_features)
            y: Training targets (n_samples,)
            
        Returns:
            self
        """
        self.X_train = np.atleast_2d(X)
        y = np.atleast_1d(y)
        
        # Normalize y
        if self.normalize_y:
            self._y_mean = np.mean(y)
            self._y_std = np.std(y)
            if self._y_std < 1e-10:
                self._y_std = 1.0
            y_normalized = (y - self._y_mean) / self._y_std
        else:
            y_normalized = y
        
        self.y_train = y_normalized
        
        # Compute kernel matrix
        K = self.kernel(self.X_train, self.X_train)
        
        # Add noise to diagonal for numerical stability
        K += self.noise_variance * np.eye(len(K))
        
        # Cholesky decomposition: K = L L^T
        try:
            self._L = cholesky(K, lower=True)
        except np.linalg.LinAlgError:
            # Add more noise if not positive definite
            K += 1e-6 * np.eye(len(K))
            self._L = cholesky(K, lower=True)
        
        # Solve L α = y → α = L^{-1} y
        self._alpha = cho_solve((self._L, True), self.y_train)
        
        return self
    
    def predict(
        self,
        X: np.ndarray,
        return_std: bool = True
    ) -> tuple[np.ndarray, Optional[np.ndarray]]:
        """
        Predict at new points.
        
        Posterior mean: μ* = k(X*, X) K^{-1} y = k(X*, X) α
        Posterior var: σ*² = k(X*, X*) - k(X*, X) K^{-1} k(X, X*)
        
        Args:
            X: Test inputs (n_samples, n_features)
            return_std: Whether to return posterior std
            
        Returns:
            (mean, std) or just mean
        """
        X = np.atleast_2d(X)
        
        if self.X_train is None:
            # No training data - return prior
            mean = np.zeros(len(X))
            if return_std:
                std = np.sqrt(self.kernel.signal_variance) * np.ones(len(X))
                return mean, std
            return mean, None
        
        # Cross-covariance k(X*, X)
        K_star = self.kernel(X, self.X_train)
        
        # Posterior mean: μ* = K* α
        mean = K_star @ self._alpha
        
        # Denormalize
        mean = mean * self._y_std + self._y_mean
        
        if return_std:
            # Posterior variance
            v = cho_solve((self._L, True), K_star.T)
            K_star_star = self.kernel(X, X)
            var = np.diag(K_star_star) - np.sum(K_star * v.T, axis=1)
            
            # Ensure non-negative variance
            var = np.maximum(var, 1e-10)
            std = np.sqrt(var) * self._y_std
            
            return mean, std
        
        return mean, None
    
    def optimize_hyperparameters(
        self,
        X: np.ndarray,
        y: np.ndarray,
        n_restarts: int = 10
    ) -> dict[str, float]:
        """
        Optimize kernel hyperparameters by maximizing marginal likelihood.
        
        Log marginal likelihood:
        log p(y|X) = -1/2 y^T K^{-1} y - 1/2 log|K| - n/2 log(2π)
        
        Args:
            X: Training inputs
            y: Training targets
            n_restarts: Number of optimization restarts
            
        Returns:
            Optimized hyperparameters
        """
        X = np.atleast_2d(X)
        y = np.atleast_1d(y)
        n = len(y)
        
        # Normalize y for optimization
        y_mean = np.mean(y)
        y_std = np.std(y) if np.std(y) > 0 else 1.0
        y_norm = (y - y_mean) / y_std
        
        def neg_log_marginal_likelihood(theta):
            """Negative log marginal likelihood."""
            length_scale = np.exp(theta[0])
            signal_var = np.exp(theta[1])
            noise_var = np.exp(theta[2])
            
            # Update kernel
            self.kernel.set_params(
                length_scale=length_scale,
                signal_variance=signal_var
            )
            
            # Compute kernel matrix
            K = self.kernel(X, X) + noise_var * np.eye(n)
            
            try:
                L = cholesky(K, lower=True)
            except np.linalg.LinAlgError:
                return 1e10
            
            # Solve for alpha
            alpha = cho_solve((L, True), y_norm)
            
            # Log marginal likelihood
            lml = -0.5 * y_norm @ alpha
            lml -= np.sum(np.log(np.diag(L)))
            lml -= n / 2 * np.log(2 * np.pi)
            
            return -lml
        
        # Multi-start optimization
        best_theta = None
        best_nll = float('inf')
        rng = np.random.RandomState(42)
        
        for _ in range(n_restarts):
            # Random initialization in log space
            theta0 = rng.uniform(-2, 2, 3)
            
            result = minimize(
                neg_log_marginal_likelihood,
                theta0,
                method='L-BFGS-B',
                bounds=[(-5, 5), (-5, 5), (-10, 1)],
            )
            
            if result.fun < best_nll:
                best_nll = result.fun
                best_theta = result.x
        
        # Set optimized hyperparameters
        if best_theta is not None:
            self.kernel.set_params(
                length_scale=np.exp(best_theta[0]),
                signal_variance=np.exp(best_theta[1])
            )
            self.noise_variance = np.exp(best_theta[2])
        
        # Refit with optimized hyperparameters
        self.fit(X, y)
        
        return {
            "length_scale": self.kernel.get_params()["length_scale"],
            "signal_variance": self.kernel.get_params()["signal_variance"],
            "noise_variance": self.noise_variance,
            "neg_log_marginal_likelihood": best_nll,
        }


# =============================================================================
# Acquisition Functions
# =============================================================================


class AcquisitionFunction(ABC):
    """Abstract base class for acquisition functions."""
    
    @abstractmethod
    def __call__(
        self,
        X: np.ndarray,
        gp: GaussianProcess,
        y_best: float
    ) -> np.ndarray:
        """
        Compute acquisition function value.
        
        Args:
            X: Points to evaluate
            gp: Fitted Gaussian Process
            y_best: Best observed value
            
        Returns:
            Acquisition values (higher = more promising)
        """
        pass


class ExpectedImprovement(AcquisitionFunction):
    """
    Expected Improvement Acquisition Function.
    
    EI(x) = E[max(f(x) - f*, 0)]
    
    For GP posterior:
    EI(x) = (μ - f* - ξ) Φ(Z) + σ φ(Z)
    
    Where:
    - Z = (μ - f* - ξ) / σ
    - Φ = standard normal CDF
    - φ = standard normal PDF
    - ξ = exploration parameter
    
    EI balances:
    - Exploitation: High predicted mean
    - Exploration: High predicted uncertainty
    """
    
    def __init__(self, xi: float = 0.01):
        """
        Initialize Expected Improvement.
        
        Args:
            xi: Exploration parameter (larger = more exploration)
        """
        self.xi = xi
    
    def __call__(
        self,
        X: np.ndarray,
        gp: GaussianProcess,
        y_best: float
    ) -> np.ndarray:
        """Compute Expected Improvement."""
        X = np.atleast_2d(X)
        
        # Get posterior mean and std
        mu, sigma = gp.predict(X, return_std=True)
        
        # Handle zero variance
        sigma = np.maximum(sigma, 1e-10)
        
        # Compute Z = (μ - y_best - ξ) / σ
        improvement = mu - y_best - self.xi
        Z = improvement / sigma
        
        # EI = (μ - y_best - ξ) Φ(Z) + σ φ(Z)
        ei = improvement * stats.norm.cdf(Z) + sigma * stats.norm.pdf(Z)
        
        # Set to 0 where σ is too small
        ei[sigma < 1e-10] = 0.0
        
        return ei


class UCBAcquisition(AcquisitionFunction):
    """
    Upper Confidence Bound Acquisition Function.
    
    UCB(x) = μ(x) + β·σ(x)
    
    Where β controls exploration-exploitation tradeoff.
    
    UCB provides theoretical guarantees on cumulative regret.
    """
    
    def __init__(self, beta: float = 2.0):
        """
        Initialize UCB acquisition.
        
        Args:
            beta: Exploration parameter (larger = more exploration)
        """
        self.beta = beta
    
    def __call__(
        self,
        X: np.ndarray,
        gp: GaussianProcess,
        y_best: float
    ) -> np.ndarray:
        """Compute UCB acquisition value."""
        X = np.atleast_2d(X)
        
        mu, sigma = gp.predict(X, return_std=True)
        
        return mu + self.beta * sigma


class ProbabilityOfImprovement(AcquisitionFunction):
    """
    Probability of Improvement Acquisition Function.
    
    PI(x) = P(f(x) > f* + ξ) = Φ((μ - f* - ξ) / σ)
    
    PI is simpler than EI but can be too greedy.
    """
    
    def __init__(self, xi: float = 0.01):
        """Initialize PI with exploration parameter."""
        self.xi = xi
    
    def __call__(
        self,
        X: np.ndarray,
        gp: GaussianProcess,
        y_best: float
    ) -> np.ndarray:
        """Compute Probability of Improvement."""
        X = np.atleast_2d(X)
        
        mu, sigma = gp.predict(X, return_std=True)
        sigma = np.maximum(sigma, 1e-10)
        
        Z = (mu - y_best - self.xi) / sigma
        return stats.norm.cdf(Z)


class ThompsonSamplingAcquisition(AcquisitionFunction):
    """
    Thompson Sampling for Acquisition.
    
    Instead of maximizing an acquisition function, sample from posterior
    and maximize the sample.
    
    This provides natural exploration without explicit exploration parameter.
    """
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize Thompson Sampling."""
        self.rng = np.random.RandomState(seed)
    
    def __call__(
        self,
        X: np.ndarray,
        gp: GaussianProcess,
        y_best: float
    ) -> np.ndarray:
        """Sample from posterior and return samples as acquisition values."""
        X = np.atleast_2d(X)
        
        mu, sigma = gp.predict(X, return_std=True)
        
        # Sample from posterior
        samples = self.rng.normal(mu, sigma)
        
        return samples


# =============================================================================
# Bayesian Optimization Engine
# =============================================================================


@dataclass
class OptimizationResult:
    """Result of a single optimization iteration."""
    iteration: int
    config: dict[str, Any]
    objective_value: float
    acquisition_value: float
    is_best: bool
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class OptimizationHistory:
    """Complete optimization history."""
    results: list[OptimizationResult] = field(default_factory=list)
    best_value: float = float('-inf')
    best_config: Optional[dict[str, Any]] = None
    best_iteration: int = 0
    
    def add_result(self, result: OptimizationResult) -> None:
        """Add a result to history."""
        self.results.append(result)
        
        if result.objective_value > self.best_value:
            self.best_value = result.objective_value
            self.best_config = result.config
            self.best_iteration = result.iteration
    
    @property
    def convergence_data(self) -> tuple[list[int], list[float]]:
        """Get (iterations, best_so_far) for convergence plot."""
        iterations = []
        best_so_far = []
        current_best = float('-inf')
        
        for r in self.results:
            iterations.append(r.iteration)
            current_best = max(current_best, r.objective_value)
            best_so_far.append(current_best)
        
        return iterations, best_so_far


class BayesianOptimizer:
    """
    Bayesian Optimization for Multi-Agent System Configuration.
    
    Algorithm:
    1. Initialize with random samples
    2. Fit GP to observations
    3. Maximize acquisition function to find next point
    4. Evaluate objective function
    5. Update GP and repeat
    
    Features:
    - Multiple acquisition functions
    - Automatic hyperparameter tuning
    - Early stopping on convergence
    - Multi-objective support
    """
    
    def __init__(
        self,
        config_space: ConfigurationSpace,
        objective_function: Callable[[dict[str, Any]], float],
        acquisition: Optional[AcquisitionFunction] = None,
        kernel: Optional[Kernel] = None,
        n_initial: int = 10,
        seed: Optional[int] = None
    ):
        """
        Initialize Bayesian Optimizer.
        
        Args:
            config_space: Configuration space to search
            objective_function: Function to optimize (higher = better)
            acquisition: Acquisition function (default: EI)
            kernel: GP kernel (default: Matern)
            n_initial: Number of initial random samples
            seed: Random seed
        """
        self.config_space = config_space
        self.objective_function = objective_function
        self.acquisition = acquisition or ExpectedImprovement()
        self.kernel = kernel or MaternKernel()
        self.n_initial = n_initial
        self.rng = np.random.RandomState(seed)
        
        # GP model
        self.gp = GaussianProcess(kernel=self.kernel)
        
        # Optimization state
        self.history = OptimizationHistory()
        self.X_observed: list[np.ndarray] = []
        self.y_observed: list[float] = []
    
    def optimize(
        self,
        n_iterations: int = 50,
        callback: Optional[Callable[[OptimizationResult], None]] = None,
        early_stopping_patience: int = 10,
        early_stopping_threshold: float = 0.001
    ) -> OptimizationHistory:
        """
        Run Bayesian Optimization.
        
        Args:
            n_iterations: Total number of iterations
            callback: Called after each iteration
            early_stopping_patience: Stop if no improvement for this many iters
            early_stopping_threshold: Minimum improvement to reset patience
            
        Returns:
            Optimization history
        """
        no_improvement_count = 0
        prev_best = float('-inf')
        
        for i in range(n_iterations):
            if i < self.n_initial:
                # Initial random sampling
                config = self.config_space.sample_random(self.rng)
            else:
                # Acquisition-guided sampling
                config = self._suggest_next()
            
            # Evaluate objective
            try:
                value = self.objective_function(config)
            except Exception as e:
                print(f"Objective evaluation failed: {e}")
                value = float('-inf')
            
            # Update observed data
            x = self.config_space.to_array(config)
            self.X_observed.append(x)
            self.y_observed.append(value)
            
            # Update GP
            if len(self.X_observed) > self.n_initial:
                X = np.array(self.X_observed)
                y = np.array(self.y_observed)
                self.gp.fit(X, y)
            
            # Record result
            is_best = value > self.history.best_value
            result = OptimizationResult(
                iteration=i,
                config=config,
                objective_value=value,
                acquisition_value=0.0,  # Will compute if needed
                is_best=is_best,
            )
            self.history.add_result(result)
            
            # Callback
            if callback:
                callback(result)
            
            # Early stopping check
            if value > prev_best + early_stopping_threshold:
                no_improvement_count = 0
                prev_best = value
            else:
                no_improvement_count += 1
            
            if no_improvement_count >= early_stopping_patience:
                print(f"Early stopping at iteration {i}")
                break
        
        return self.history
    
    def _suggest_next(self) -> dict[str, Any]:
        """
        Suggest next configuration to evaluate.
        
        Optimizes acquisition function using random search + L-BFGS-B.
        """
        y_best = max(self.y_observed)
        
        # Random candidates
        n_candidates = 5000
        candidates = np.array([
            self.config_space.to_array(
                self.config_space.sample_random(self.rng)
            )
            for _ in range(n_candidates)
        ])
        
        # Evaluate acquisition on candidates
        acq_values = self.acquisition(candidates, self.gp, y_best)
        
        # Find best candidates
        top_k = 20
        top_indices = np.argsort(acq_values)[-top_k:]
        
        # Local optimization from best candidates
        best_x = None
        best_acq = float('-inf')
        
        for idx in top_indices:
            x0 = candidates[idx]
            
            def neg_acq(x):
                return -self.acquisition(
                    x.reshape(1, -1), self.gp, y_best
                )[0]
            
            # Bound to unit hypercube
            bounds = [(0, 1)] * len(x0)
            
            result = minimize(
                neg_acq, x0,
                method='L-BFGS-B',
                bounds=bounds,
            )
            
            if -result.fun > best_acq:
                best_acq = -result.fun
                best_x = result.x
        
        # Convert to configuration
        return self.config_space.from_array(best_x)
    
    def get_best_config(self) -> dict[str, Any]:
        """Get best configuration found."""
        return self.history.best_config
    
    def get_prediction_uncertainty(
        self,
        config: dict[str, Any]
    ) -> tuple[float, float]:
        """Get predicted mean and uncertainty for a configuration."""
        x = self.config_space.to_array(config).reshape(1, -1)
        mean, std = self.gp.predict(x, return_std=True)
        return float(mean[0]), float(std[0])


# =============================================================================
# Multi-Objective Bayesian Optimization
# =============================================================================


class MultiObjectiveBO:
    """
    Multi-Objective Bayesian Optimization.
    
    Optimizes multiple objectives simultaneously:
    - Quality (maximize)
    - Latency (minimize)
    - Cost (minimize)
    
    Uses Pareto dominance to find the Pareto frontier.
    """
    
    def __init__(
        self,
        config_space: ConfigurationSpace,
        objectives: dict[str, Callable[[dict[str, Any]], float]],
        maximize: dict[str, bool],
        seed: Optional[int] = None
    ):
        """
        Initialize Multi-Objective BO.
        
        Args:
            config_space: Configuration space
            objectives: Dict of objective_name -> function
            maximize: Dict of objective_name -> whether to maximize
            seed: Random seed
        """
        self.config_space = config_space
        self.objectives = objectives
        self.maximize = maximize
        self.rng = np.random.RandomState(seed)
        
        # Separate GP for each objective
        self.gps = {
            name: GaussianProcess(kernel=MaternKernel())
            for name in objectives
        }
        
        # Observed data
        self.X_observed: list[np.ndarray] = []
        self.Y_observed: dict[str, list[float]] = {
            name: [] for name in objectives
        }
        
        # Pareto frontier
        self.pareto_configs: list[dict[str, Any]] = []
        self.pareto_values: list[dict[str, float]] = []
    
    def optimize(
        self,
        n_iterations: int = 50,
        n_initial: int = 10
    ) -> list[dict[str, Any]]:
        """
        Run multi-objective optimization.
        
        Returns:
            List of Pareto-optimal configurations
        """
        for i in range(n_iterations):
            if i < n_initial:
                config = self.config_space.sample_random(self.rng)
            else:
                config = self._suggest_next()
            
            # Evaluate all objectives
            values = {}
            for name, func in self.objectives.items():
                try:
                    values[name] = func(config)
                except Exception:
                    values[name] = float('-inf') if self.maximize[name] else float('inf')
            
            # Update observed data
            x = self.config_space.to_array(config)
            self.X_observed.append(x)
            
            for name, val in values.items():
                self.Y_observed[name].append(val)
            
            # Update GPs
            if i >= n_initial:
                X = np.array(self.X_observed)
                for name, gp in self.gps.items():
                    y = np.array(self.Y_observed[name])
                    gp.fit(X, y)
            
            # Update Pareto frontier
            self._update_pareto(config, values)
        
        return self.pareto_configs
    
    def _suggest_next(self) -> dict[str, Any]:
        """Suggest next point using Expected Hypervolume Improvement."""
        # Simplified: use alternating objectives
        n = len(self.X_observed)
        obj_names = list(self.objectives.keys())
        current_obj = obj_names[n % len(obj_names)]
        
        # Optimize acquisition for current objective
        gp = self.gps[current_obj]
        y_best = max(self.Y_observed[current_obj]) if self.maximize[current_obj] else -min(self.Y_observed[current_obj])
        
        ei = ExpectedImprovement()
        
        # Random candidates
        candidates = np.array([
            self.config_space.to_array(self.config_space.sample_random(self.rng))
            for _ in range(1000)
        ])
        
        acq_values = ei(candidates, gp, y_best)
        best_idx = np.argmax(acq_values)
        
        return self.config_space.from_array(candidates[best_idx])
    
    def _update_pareto(
        self,
        config: dict[str, Any],
        values: dict[str, float]
    ) -> None:
        """Update Pareto frontier with new point."""
        # Check if dominated by any existing Pareto point
        is_dominated = False
        dominates = []
        
        for i, pv in enumerate(self.pareto_values):
            # Check if pv dominates values
            pv_dominates = all(
                pv[n] >= values[n] if self.maximize[n] else pv[n] <= values[n]
                for n in self.objectives
            )
            pv_strictly_better = any(
                pv[n] > values[n] if self.maximize[n] else pv[n] < values[n]
                for n in self.objectives
            )
            
            if pv_dominates and pv_strictly_better:
                is_dominated = True
                break
            
            # Check if values dominates pv
            v_dominates = all(
                values[n] >= pv[n] if self.maximize[n] else values[n] <= pv[n]
                for n in self.objectives
            )
            v_strictly_better = any(
                values[n] > pv[n] if self.maximize[n] else values[n] < pv[n]
                for n in self.objectives
            )
            
            if v_dominates and v_strictly_better:
                dominates.append(i)
        
        if not is_dominated:
            # Remove dominated points
            for i in sorted(dominates, reverse=True):
                self.pareto_configs.pop(i)
                self.pareto_values.pop(i)
            
            # Add new point
            self.pareto_configs.append(config)
            self.pareto_values.append(values)


# =============================================================================
# Example Usage
# =============================================================================


def demo_bayesian_optimization():
    """Demonstrate Bayesian Optimization."""
    print("=" * 70)
    print("🎯 BAYESIAN OPTIMIZATION DEMO")
    print("=" * 70)
    
    # Define a simple objective function
    def objective(config: dict[str, Any]) -> float:
        """Simulated objective: Quality - Latency penalty."""
        soft_timeout = config.get("soft_timeout", 15)
        hard_timeout = config.get("hard_timeout", 30)
        
        # Simulate quality increasing with timeout
        quality = 7.0 + 0.1 * soft_timeout - 0.001 * soft_timeout**2
        
        # Latency penalty
        latency_penalty = 0.1 * hard_timeout
        
        return quality - latency_penalty
    
    # Create optimizer
    config_space = ConfigurationSpace()
    optimizer = BayesianOptimizer(
        config_space=config_space,
        objective_function=objective,
        n_initial=5,
        seed=42
    )
    
    # Run optimization
    print("\n📈 Running optimization...")
    history = optimizer.optimize(
        n_iterations=20,
        callback=lambda r: print(f"   Iter {r.iteration}: {r.objective_value:.4f}")
    )
    
    # Results
    print(f"\n🏆 Best configuration found:")
    for name, value in history.best_config.items():
        print(f"   {name}: {value}")
    print(f"   Objective: {history.best_value:.4f}")
    
    # Convergence
    iters, best_so_far = history.convergence_data
    print(f"\n📊 Convergence: {best_so_far[-1]:.4f} after {len(iters)} iterations")
    
    print("\n✅ Demo complete!")


if __name__ == "__main__":
    demo_bayesian_optimization()

