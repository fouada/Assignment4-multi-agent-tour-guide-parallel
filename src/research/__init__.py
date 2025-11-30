"""
Research Framework for MIT-Level Analysis
==========================================

This module provides tools for:
- Systematic sensitivity analysis
- Statistical hypothesis testing
- Monte Carlo simulations
- Experimental benchmarking

Academic Reference:
    - Saltelli, A. et al. (2008). Global Sensitivity Analysis: The Primer. Wiley.
    - Montgomery, D.C. (2017). Design and Analysis of Experiments. Wiley.
"""

from .experimental_framework import (
    ExperimentConfig,
    ExperimentResult,
    ExperimentRunner,
    ReproducibleExperiment,
)

from .statistical_analysis import (
    StatisticalComparison,
    EffectSizeAnalysis,
    HypothesisTest,
    BootstrapAnalysis,
)

from .visualization import (
    ResearchVisualizer,
    create_publication_figure,
)

__all__ = [
    # Experimental Framework
    "ExperimentConfig",
    "ExperimentResult",
    "ExperimentRunner",
    "ReproducibleExperiment",
    # Statistical Analysis
    "StatisticalComparison",
    "EffectSizeAnalysis",
    "HypothesisTest",
    "BootstrapAnalysis",
    # Visualization
    "ResearchVisualizer",
    "create_publication_figure",
]

