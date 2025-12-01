"""
Cost Analysis Module
====================

MIT-Level comprehensive cost analysis framework for the Multi-Agent Tour Guide System.

This module provides:
1. Cost Models - Pricing structures for LLM, API, and compute resources
2. Cost Tracking - Real-time and historical cost tracking
3. Cost Optimization - Recommendations and automated optimization
4. Visualization - Publication-quality cost analysis charts

Author: Multi-Agent Tour Guide Research Team
Version: 1.0.0
Date: November 2025

Academic References:
    - Bommasani et al. (2021) "On the Opportunities and Risks of Foundation Models"
    - Patterson et al. (2021) "Carbon Emissions and Large Neural Network Training"
"""

from src.cost_analysis.models import (
    APICostModel,
    APIPricing,
    ComputeCostModel,
    ComputePricing,
    CostCategory,
    CostEvent,
    LLMCostModel,
    LLMPricing,
    SystemCostReport,
    TourCostSummary,
)
from src.cost_analysis.optimizer import (
    CostAwareConfigOptimizer,
    CostOptimizer,
    OptimizationCategory,
    OptimizationPriority,
    OptimizationRecommendation,
    OptimizationStrategy,
    ROIAnalysis,
)
from src.cost_analysis.tracker import (
    AgentCostTracker,
    CostTracker,
    TourCostTracker,
    get_cost_tracker,
    reset_cost_tracker,
)
from src.cost_analysis.visualization import (
    COST_COLORS,
    CostBreakdownChart,
    CostDashboardComponents,
    CostTrendChart,
    CostVisualizationPanel,
    ROIChart,
)

__all__ = [
    # Models
    "CostCategory",
    "CostEvent",
    "LLMCostModel",
    "APICostModel",
    "ComputeCostModel",
    "TourCostSummary",
    "SystemCostReport",
    "LLMPricing",
    "APIPricing",
    "ComputePricing",
    # Tracking
    "CostTracker",
    "AgentCostTracker",
    "TourCostTracker",
    "get_cost_tracker",
    "reset_cost_tracker",
    # Optimization
    "CostOptimizer",
    "OptimizationRecommendation",
    "OptimizationStrategy",
    "OptimizationCategory",
    "OptimizationPriority",
    "ROIAnalysis",
    "CostAwareConfigOptimizer",
    # Visualization
    "CostVisualizationPanel",
    "CostBreakdownChart",
    "CostTrendChart",
    "ROIChart",
    "CostDashboardComponents",
    "COST_COLORS",
]
