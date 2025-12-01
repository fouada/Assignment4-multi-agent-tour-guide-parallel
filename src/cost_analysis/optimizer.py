"""
Cost Optimization Engine
========================

Advanced cost optimization framework with actionable recommendations.

Features:
1. Model Selection Optimization - Choose optimal LLM model for quality/cost trade-off
2. Caching Strategy Analysis - Quantify benefits of caching strategies
3. Batching Optimization - Optimize batch sizes for API calls
4. Resource Allocation - Optimize thread/memory allocation
5. ROI Analysis - Calculate return on investment for optimizations

Author: Multi-Agent Tour Guide Research Team
Version: 1.0.0

Academic References:
    - Bommasani et al. (2021) "On the Opportunities and Risks of Foundation Models"
    - Strubell et al. (2019) "Energy and Policy Considerations for Deep Learning in NLP"
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from src.cost_analysis.models import (
    APICostModel,
    ComputeCostModel,
    LLMCostModel,
    LLMPricing,
    SystemCostReport,
    TourCostSummary,
)
from src.cost_analysis.tracker import CostTracker

logger = logging.getLogger(__name__)


class OptimizationCategory(Enum):
    """Categories of cost optimization."""
    
    MODEL_SELECTION = "model_selection"
    CACHING = "caching"
    BATCHING = "batching"
    PARALLELIZATION = "parallelization"
    RETRY_STRATEGY = "retry_strategy"
    TOKEN_OPTIMIZATION = "token_optimization"
    API_OPTIMIZATION = "api_optimization"
    RESOURCE_ALLOCATION = "resource_allocation"


class OptimizationPriority(Enum):
    """Priority levels for recommendations."""
    
    CRITICAL = "critical"  # > 30% cost reduction potential
    HIGH = "high"         # 15-30% cost reduction
    MEDIUM = "medium"     # 5-15% cost reduction
    LOW = "low"          # < 5% cost reduction


@dataclass
class OptimizationRecommendation:
    """A single optimization recommendation."""
    
    category: OptimizationCategory
    priority: OptimizationPriority
    title: str
    description: str
    current_cost: float
    optimized_cost: float
    savings_potential: float  # Percentage
    implementation_effort: str  # low, medium, high
    implementation_steps: List[str]
    risks: List[str] = field(default_factory=list)
    metrics_impact: Dict[str, str] = field(default_factory=dict)
    
    @property
    def annual_savings(self) -> float:
        """Calculate annual savings potential."""
        return (self.current_cost - self.optimized_cost) * 12
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "category": self.category.value,
            "priority": self.priority.value,
            "title": self.title,
            "description": self.description,
            "costs": {
                "current": self.current_cost,
                "optimized": self.optimized_cost,
                "savings_percent": self.savings_potential,
                "annual_savings": self.annual_savings,
            },
            "implementation": {
                "effort": self.implementation_effort,
                "steps": self.implementation_steps,
                "risks": self.risks,
            },
            "metrics_impact": self.metrics_impact,
        }


@dataclass
class OptimizationStrategy:
    """Complete optimization strategy with multiple recommendations."""
    
    generated_at: datetime
    recommendations: List[OptimizationRecommendation]
    total_current_cost: float
    total_optimized_cost: float
    
    @property
    def total_savings_potential(self) -> float:
        """Calculate total savings potential percentage."""
        if self.total_current_cost == 0:
            return 0.0
        return ((self.total_current_cost - self.total_optimized_cost) / 
                self.total_current_cost * 100)
    
    @property
    def total_annual_savings(self) -> float:
        """Calculate total annual savings."""
        return sum(r.annual_savings for r in self.recommendations)
    
    def get_by_priority(self, priority: OptimizationPriority) -> List[OptimizationRecommendation]:
        """Get recommendations by priority."""
        return [r for r in self.recommendations if r.priority == priority]
    
    def get_by_category(self, category: OptimizationCategory) -> List[OptimizationRecommendation]:
        """Get recommendations by category."""
        return [r for r in self.recommendations if r.category == category]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "generated_at": self.generated_at.isoformat(),
            "summary": {
                "total_current_cost": self.total_current_cost,
                "total_optimized_cost": self.total_optimized_cost,
                "total_savings_potential": self.total_savings_potential,
                "total_annual_savings": self.total_annual_savings,
                "num_recommendations": len(self.recommendations),
            },
            "recommendations": [r.to_dict() for r in self.recommendations],
            "by_priority": {
                p.value: len(self.get_by_priority(p))
                for p in OptimizationPriority
            },
            "by_category": {
                c.value: len(self.get_by_category(c))
                for c in OptimizationCategory
            },
        }


@dataclass
class ROIAnalysis:
    """
    Return on Investment analysis for optimization implementations.
    
    Calculates payback period, NPV, and IRR for optimization investments.
    """
    
    optimization_name: str
    implementation_cost: float
    monthly_savings: float
    implementation_time_days: int
    maintenance_cost_monthly: float = 0.0
    discount_rate: float = 0.1  # 10% annual
    
    @property
    def net_monthly_savings(self) -> float:
        """Monthly savings minus maintenance."""
        return self.monthly_savings - self.maintenance_cost_monthly
    
    @property
    def payback_period_months(self) -> float:
        """Calculate payback period in months."""
        if self.net_monthly_savings <= 0:
            return float('inf')
        return self.implementation_cost / self.net_monthly_savings
    
    @property
    def npv_1year(self) -> float:
        """Calculate 1-year Net Present Value."""
        monthly_rate = self.discount_rate / 12
        npv = -self.implementation_cost
        
        for month in range(1, 13):
            npv += self.net_monthly_savings / ((1 + monthly_rate) ** month)
        
        return npv
    
    @property
    def roi_1year(self) -> float:
        """Calculate 1-year ROI percentage."""
        if self.implementation_cost == 0:
            return float('inf')
        return (self.npv_1year / self.implementation_cost) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "optimization_name": self.optimization_name,
            "costs": {
                "implementation": self.implementation_cost,
                "maintenance_monthly": self.maintenance_cost_monthly,
            },
            "savings": {
                "monthly_gross": self.monthly_savings,
                "monthly_net": self.net_monthly_savings,
                "annual_net": self.net_monthly_savings * 12,
            },
            "metrics": {
                "payback_period_months": self.payback_period_months,
                "npv_1year": self.npv_1year,
                "roi_1year": self.roi_1year,
            },
        }


class CostOptimizer:
    """
    Advanced cost optimization engine.
    
    Analyzes current cost patterns and generates actionable
    recommendations for cost reduction.
    """
    
    def __init__(
        self,
        cost_tracker: CostTracker,
        llm_model: LLMCostModel | None = None,
    ):
        """
        Initialize optimizer.
        
        Args:
            cost_tracker: Cost tracking system for analysis
            llm_model: Current LLM model configuration
        """
        self.cost_tracker = cost_tracker
        self.llm_model = llm_model or LLMCostModel()
    
    def generate_strategy(
        self,
        monthly_cost: float | None = None,
        tour_summaries: List[TourCostSummary] | None = None,
    ) -> OptimizationStrategy:
        """
        Generate comprehensive optimization strategy.
        
        Args:
            monthly_cost: Current monthly cost (or estimate from tracker)
            tour_summaries: Historical tour cost summaries
            
        Returns:
            Complete optimization strategy with recommendations
        """
        if monthly_cost is None:
            # Estimate from tracker
            monthly_cost = self.cost_tracker.get_total_cost() * 30  # Scale to monthly
        
        recommendations = []
        
        # 1. Model Selection Optimization
        recommendations.extend(self._analyze_model_selection(monthly_cost))
        
        # 2. Caching Strategy
        recommendations.extend(self._analyze_caching_potential(monthly_cost, tour_summaries))
        
        # 3. Token Optimization
        recommendations.extend(self._analyze_token_usage(monthly_cost))
        
        # 4. Batching Optimization
        recommendations.extend(self._analyze_batching_potential(monthly_cost))
        
        # 5. Retry Strategy
        recommendations.extend(self._analyze_retry_costs(monthly_cost))
        
        # 6. Parallelization Optimization
        recommendations.extend(self._analyze_parallelization(monthly_cost))
        
        # 7. API Optimization
        recommendations.extend(self._analyze_api_usage(monthly_cost))
        
        # Sort by priority and potential savings
        recommendations.sort(
            key=lambda r: (
                list(OptimizationPriority).index(r.priority),
                -r.savings_potential
            )
        )
        
        total_optimized = monthly_cost * (1 - sum(r.savings_potential for r in recommendations) / 100)
        
        return OptimizationStrategy(
            generated_at=datetime.now(),
            recommendations=recommendations,
            total_current_cost=monthly_cost,
            total_optimized_cost=max(0, total_optimized),
        )
    
    def _analyze_model_selection(self, monthly_cost: float) -> List[OptimizationRecommendation]:
        """Analyze opportunities for model selection optimization."""
        recommendations = []
        pricing = LLMPricing()
        
        # Get current model costs
        current_model = self.llm_model.model
        llm_cost_share = 0.6  # Estimate LLM costs as 60% of total
        current_llm_cost = monthly_cost * llm_cost_share
        
        # Calculate costs with different models
        model_options = [
            {
                "name": "GPT-4o-mini",
                "input_rate": pricing.OPENAI_GPT4O_MINI_INPUT,
                "output_rate": pricing.OPENAI_GPT4O_MINI_OUTPUT,
                "quality_factor": 0.90,  # Relative quality
            },
            {
                "name": "Claude Haiku",
                "input_rate": pricing.ANTHROPIC_CLAUDE_HAIKU_INPUT,
                "output_rate": pricing.ANTHROPIC_CLAUDE_HAIKU_OUTPUT,
                "quality_factor": 0.88,
            },
            {
                "name": "GPT-3.5 Turbo",
                "input_rate": pricing.OPENAI_GPT35_INPUT,
                "output_rate": pricing.OPENAI_GPT35_OUTPUT,
                "quality_factor": 0.80,
            },
        ]
        
        # Current model rates (assuming GPT-4o or similar)
        if "gpt-4o" in current_model and "mini" not in current_model:
            current_rate = pricing.OPENAI_GPT4O_INPUT + pricing.OPENAI_GPT4O_OUTPUT
        elif "claude" in current_model.lower() and "haiku" not in current_model.lower():
            current_rate = pricing.ANTHROPIC_CLAUDE_SONNET_INPUT + pricing.ANTHROPIC_CLAUDE_SONNET_OUTPUT
        else:
            current_rate = pricing.OPENAI_GPT4O_MINI_INPUT + pricing.OPENAI_GPT4O_MINI_OUTPUT
        
        # Check for cheaper alternatives
        for alt in model_options:
            alt_rate = alt["input_rate"] + alt["output_rate"]
            if alt_rate < current_rate * 0.7:  # At least 30% cheaper
                savings_pct = (1 - alt_rate / current_rate) * llm_cost_share * 100
                optimized_llm = current_llm_cost * (alt_rate / current_rate)
                
                if savings_pct > 5:
                    priority = (
                        OptimizationPriority.CRITICAL if savings_pct > 30 else
                        OptimizationPriority.HIGH if savings_pct > 15 else
                        OptimizationPriority.MEDIUM
                    )
                    
                    recommendations.append(OptimizationRecommendation(
                        category=OptimizationCategory.MODEL_SELECTION,
                        priority=priority,
                        title=f"Switch to {alt['name']} for Non-Critical Tasks",
                        description=(
                            f"Use {alt['name']} for routine content search tasks while "
                            f"reserving current model for judge decisions. "
                            f"Expected quality impact: {(1 - alt['quality_factor']) * 100:.0f}% reduction."
                        ),
                        current_cost=current_llm_cost,
                        optimized_cost=optimized_llm,
                        savings_potential=savings_pct,
                        implementation_effort="low",
                        implementation_steps=[
                            "Update agent configuration to use model routing",
                            "Configure model selection based on task type",
                            "Set up A/B testing to validate quality",
                            "Monitor quality metrics for 1 week",
                            "Roll out to all non-critical agents",
                        ],
                        risks=[
                            f"Potential {(1 - alt['quality_factor']) * 100:.0f}% quality degradation",
                            "May require prompt adjustments for new model",
                        ],
                        metrics_impact={
                            "cost": f"-{savings_pct:.0f}%",
                            "quality": f"-{(1 - alt['quality_factor']) * 100:.0f}%",
                            "latency": "neutral",
                        },
                    ))
        
        # Tiered model strategy
        if current_rate > pricing.OPENAI_GPT4O_MINI_INPUT + pricing.OPENAI_GPT4O_MINI_OUTPUT:
            recommendations.append(OptimizationRecommendation(
                category=OptimizationCategory.MODEL_SELECTION,
                priority=OptimizationPriority.HIGH,
                title="Implement Tiered Model Strategy",
                description=(
                    "Use a tiered approach: cheap model for content search, "
                    "medium model for initial ranking, premium model for judge decisions only. "
                    "This maintains quality where it matters while reducing routine costs."
                ),
                current_cost=current_llm_cost,
                optimized_cost=current_llm_cost * 0.55,
                savings_potential=27.0,
                implementation_effort="medium",
                implementation_steps=[
                    "Define task tiers: search (tier 1), ranking (tier 2), judge (tier 3)",
                    "Configure model routing logic in orchestrator",
                    "Implement model registry with fallback logic",
                    "Add quality monitoring per tier",
                    "Fine-tune prompts for each tier",
                ],
                risks=[
                    "Increased code complexity",
                    "May need different prompts per model",
                    "Fallback logic adds latency",
                ],
                metrics_impact={
                    "cost": "-27%",
                    "quality": "< 5% reduction",
                    "latency": "+10% (routing overhead)",
                },
            ))
        
        return recommendations
    
    def _analyze_caching_potential(
        self,
        monthly_cost: float,
        tour_summaries: List[TourCostSummary] | None = None,
    ) -> List[OptimizationRecommendation]:
        """Analyze caching optimization potential."""
        recommendations = []
        
        # Estimate cache hit potential based on route similarity
        # Common routes (e.g., Tel Aviv -> Jerusalem) should have high cache hits
        estimated_cache_hit_rate = 0.35  # 35% of queries could be cached
        llm_cost_share = 0.6
        
        savings_from_caching = monthly_cost * llm_cost_share * estimated_cache_hit_rate
        savings_pct = (savings_from_caching / monthly_cost) * 100
        
        recommendations.append(OptimizationRecommendation(
            category=OptimizationCategory.CACHING,
            priority=OptimizationPriority.CRITICAL,
            title="Implement Semantic Response Caching",
            description=(
                "Cache LLM responses for similar queries using semantic similarity. "
                "For location-based queries, cache results by location + content type. "
                f"Expected cache hit rate: {estimated_cache_hit_rate * 100:.0f}%."
            ),
            current_cost=monthly_cost * llm_cost_share,
            optimized_cost=monthly_cost * llm_cost_share * (1 - estimated_cache_hit_rate),
            savings_potential=savings_pct,
            implementation_effort="medium",
            implementation_steps=[
                "Design cache key strategy (location hash + content type)",
                "Implement Redis/Memcached caching layer",
                "Add cache-aside pattern to agent base class",
                "Set TTL based on content volatility (7 days for historical)",
                "Implement cache warming for popular routes",
                "Add cache hit/miss metrics",
            ],
            risks=[
                "Stale content for time-sensitive queries",
                "Redis memory costs (estimate: $20-50/month)",
                "Cache invalidation complexity",
            ],
            metrics_impact={
                "cost": f"-{savings_pct:.0f}%",
                "quality": "neutral (same responses)",
                "latency": "-60% for cache hits",
            },
        ))
        
        # Prompt caching (for repeated system prompts)
        prompt_cache_savings = monthly_cost * 0.05
        
        recommendations.append(OptimizationRecommendation(
            category=OptimizationCategory.CACHING,
            priority=OptimizationPriority.MEDIUM,
            title="Enable Prompt Caching (OpenAI/Anthropic)",
            description=(
                "Use provider prompt caching features for repeated system prompts. "
                "OpenAI and Anthropic both offer 50% discount on cached prompt tokens."
            ),
            current_cost=monthly_cost * 0.1,  # System prompts ~10% of tokens
            optimized_cost=monthly_cost * 0.05,
            savings_potential=5.0,
            implementation_effort="low",
            implementation_steps=[
                "Enable prompt caching in API configuration",
                "Ensure system prompts are consistent across calls",
                "Monitor cache hit rates via API dashboard",
            ],
            risks=[
                "Only works with consistent system prompts",
                "Provider-specific implementation",
            ],
            metrics_impact={
                "cost": "-5%",
                "quality": "neutral",
                "latency": "-10% (cached prompts faster)",
            },
        ))
        
        return recommendations
    
    def _analyze_token_usage(self, monthly_cost: float) -> List[OptimizationRecommendation]:
        """Analyze token usage optimization opportunities."""
        recommendations = []
        
        # Prompt engineering optimization
        recommendations.append(OptimizationRecommendation(
            category=OptimizationCategory.TOKEN_OPTIMIZATION,
            priority=OptimizationPriority.HIGH,
            title="Optimize Prompt Length and Structure",
            description=(
                "Reduce prompt verbosity while maintaining quality. "
                "Use structured outputs (JSON mode) to reduce output tokens. "
                "Implement few-shot examples selectively."
            ),
            current_cost=monthly_cost * 0.6,
            optimized_cost=monthly_cost * 0.6 * 0.75,
            savings_potential=15.0,
            implementation_effort="medium",
            implementation_steps=[
                "Audit current prompts for redundancy",
                "Convert verbose instructions to structured formats",
                "Implement JSON mode for all agent responses",
                "A/B test shortened prompts vs. quality",
                "Create prompt templates with minimal tokens",
                "Remove unnecessary context from system prompts",
            ],
            risks=[
                "May reduce response quality",
                "Requires careful prompt testing",
            ],
            metrics_impact={
                "cost": "-15%",
                "quality": "monitor closely",
                "latency": "-5% (fewer tokens to process)",
            },
        ))
        
        # Output length control
        recommendations.append(OptimizationRecommendation(
            category=OptimizationCategory.TOKEN_OPTIMIZATION,
            priority=OptimizationPriority.MEDIUM,
            title="Implement Strict Output Length Limits",
            description=(
                "Set max_tokens appropriately for each agent type. "
                "Video/Music agents need < 200 tokens, Text agent < 400, Judge < 300."
            ),
            current_cost=monthly_cost * 0.3,  # Output tokens more expensive
            optimized_cost=monthly_cost * 0.3 * 0.7,
            savings_potential=9.0,
            implementation_effort="low",
            implementation_steps=[
                "Analyze current output token distribution",
                "Set max_tokens per agent type in config",
                "Add output truncation handlers",
                "Monitor for truncation errors",
            ],
            risks=[
                "Truncated responses may lose information",
            ],
            metrics_impact={
                "cost": "-9%",
                "quality": "-2% (minor truncation)",
                "latency": "-3%",
            },
        ))
        
        return recommendations
    
    def _analyze_batching_potential(self, monthly_cost: float) -> List[OptimizationRecommendation]:
        """Analyze batching optimization potential."""
        recommendations = []
        
        # Batch API requests
        recommendations.append(OptimizationRecommendation(
            category=OptimizationCategory.BATCHING,
            priority=OptimizationPriority.MEDIUM,
            title="Implement Request Batching for Multi-Point Routes",
            description=(
                "Batch similar API requests when processing multiple route points. "
                "Use OpenAI Batch API for non-time-critical processing (50% discount). "
                "Batch Google Maps requests for route optimization."
            ),
            current_cost=monthly_cost,
            optimized_cost=monthly_cost * 0.88,
            savings_potential=12.0,
            implementation_effort="medium",
            implementation_steps=[
                "Implement request aggregation layer",
                "Use OpenAI Batch API for historical content lookups",
                "Batch Google Maps requests (multi-origin/destination)",
                "Add batch size configuration per API",
                "Implement async batch processing with callbacks",
            ],
            risks=[
                "Increased latency for batched requests",
                "Batch API has 24-hour SLA",
                "Complexity in error handling",
            ],
            metrics_impact={
                "cost": "-12%",
                "quality": "neutral",
                "latency": "+200ms for batching (acceptable for routes > 3 points)",
            },
        ))
        
        return recommendations
    
    def _analyze_retry_costs(self, monthly_cost: float) -> List[OptimizationRecommendation]:
        """Analyze retry-related cost optimization."""
        recommendations = []
        
        # Get retry overhead from tracker
        retry_overhead = self.cost_tracker.get_cost_breakdown().get("retry_overhead", 0)
        if retry_overhead == 0:
            retry_overhead = monthly_cost * 0.08  # Estimate 8% retry overhead
        
        recommendations.append(OptimizationRecommendation(
            category=OptimizationCategory.RETRY_STRATEGY,
            priority=OptimizationPriority.HIGH,
            title="Optimize Retry Strategy with Circuit Breakers",
            description=(
                "Implement intelligent retry with exponential backoff and circuit breakers. "
                "Avoid retrying on non-transient errors (e.g., invalid input). "
                "Use fallback content instead of expensive retries."
            ),
            current_cost=retry_overhead,
            optimized_cost=retry_overhead * 0.3,
            savings_potential=(retry_overhead / monthly_cost * 70),
            implementation_effort="medium",
            implementation_steps=[
                "Classify errors as transient vs. permanent",
                "Implement exponential backoff (1s, 2s, 4s)",
                "Add circuit breaker per external service",
                "Create fallback content database",
                "Limit retries to 2 for LLM calls",
                "Add retry budget per tour",
            ],
            risks=[
                "May reduce success rate for transient failures",
                "Fallback content may be lower quality",
            ],
            metrics_impact={
                "cost": f"-{(retry_overhead / monthly_cost * 70):.0f}%",
                "quality": "-1% (fallback usage)",
                "latency": "-20% (fewer retries)",
            },
        ))
        
        return recommendations
    
    def _analyze_parallelization(self, monthly_cost: float) -> List[OptimizationRecommendation]:
        """Analyze parallelization cost optimization."""
        recommendations = []
        
        compute_share = 0.1  # Compute is ~10% of costs
        
        recommendations.append(OptimizationRecommendation(
            category=OptimizationCategory.PARALLELIZATION,
            priority=OptimizationPriority.LOW,
            title="Optimize Thread Pool Configuration",
            description=(
                "Right-size thread pools based on actual concurrency needs. "
                "Use async I/O instead of thread pools for I/O-bound operations."
            ),
            current_cost=monthly_cost * compute_share,
            optimized_cost=monthly_cost * compute_share * 0.6,
            savings_potential=4.0,
            implementation_effort="medium",
            implementation_steps=[
                "Profile thread utilization under load",
                "Migrate to asyncio for network calls",
                "Reduce max_workers to match actual parallelism",
                "Implement work-stealing for unbalanced loads",
            ],
            risks=[
                "May reduce throughput under high load",
                "Async migration requires code changes",
            ],
            metrics_impact={
                "cost": "-4%",
                "quality": "neutral",
                "latency": "+5% under low load, -10% under high load",
            },
        ))
        
        return recommendations
    
    def _analyze_api_usage(self, monthly_cost: float) -> List[OptimizationRecommendation]:
        """Analyze external API usage optimization."""
        recommendations = []
        
        api_share = 0.15  # APIs ~15% of costs
        
        recommendations.append(OptimizationRecommendation(
            category=OptimizationCategory.API_OPTIMIZATION,
            priority=OptimizationPriority.MEDIUM,
            title="Implement API Response Caching and Rate Limit Optimization",
            description=(
                "Cache Google Maps and YouTube API responses. "
                "Use YouTube Data API quota efficiently. "
                "Implement request deduplication."
            ),
            current_cost=monthly_cost * api_share,
            optimized_cost=monthly_cost * api_share * 0.5,
            savings_potential=7.5,
            implementation_effort="low",
            implementation_steps=[
                "Cache Google Maps routes (TTL: 24 hours)",
                "Cache YouTube video metadata (TTL: 7 days)",
                "Implement request deduplication",
                "Use Fields parameter to reduce response size",
                "Monitor API quota usage",
            ],
            risks=[
                "Stale route data (road closures)",
                "Video availability may change",
            ],
            metrics_impact={
                "cost": "-7.5%",
                "quality": "neutral",
                "latency": "-40% for cached responses",
            },
        ))
        
        return recommendations
    
    def calculate_roi(
        self,
        recommendation: OptimizationRecommendation,
        implementation_cost_hours: float,
        hourly_rate: float = 100.0,  # Engineering hourly rate
        maintenance_hours_monthly: float = 2.0,
    ) -> ROIAnalysis:
        """
        Calculate ROI for implementing a recommendation.
        
        Args:
            recommendation: The optimization recommendation
            implementation_cost_hours: Hours to implement
            hourly_rate: Engineering hourly rate
            maintenance_hours_monthly: Monthly maintenance hours
            
        Returns:
            ROI analysis
        """
        implementation_cost = implementation_cost_hours * hourly_rate
        maintenance_cost = maintenance_hours_monthly * hourly_rate
        monthly_savings = recommendation.current_cost - recommendation.optimized_cost
        
        return ROIAnalysis(
            optimization_name=recommendation.title,
            implementation_cost=implementation_cost,
            monthly_savings=monthly_savings,
            implementation_time_days=int(implementation_cost_hours / 8) + 1,
            maintenance_cost_monthly=maintenance_cost,
        )
    
    def get_quick_wins(
        self,
        strategy: OptimizationStrategy,
        max_effort: str = "low",
    ) -> List[OptimizationRecommendation]:
        """
        Get quick-win recommendations with high ROI.
        
        Args:
            strategy: Generated optimization strategy
            max_effort: Maximum implementation effort (low, medium, high)
            
        Returns:
            List of quick-win recommendations
        """
        effort_order = ["low", "medium", "high"]
        max_idx = effort_order.index(max_effort)
        
        return [
            r for r in strategy.recommendations
            if effort_order.index(r.implementation_effort) <= max_idx
            and r.savings_potential > 5.0
        ]
    
    def generate_implementation_roadmap(
        self,
        strategy: OptimizationStrategy,
        monthly_budget_hours: float = 40.0,
    ) -> List[Dict[str, Any]]:
        """
        Generate phased implementation roadmap.
        
        Args:
            strategy: Optimization strategy
            monthly_budget_hours: Available engineering hours per month
            
        Returns:
            Phased implementation plan
        """
        effort_hours = {
            "low": 8,
            "medium": 24,
            "high": 60,
        }
        
        # Sort by ROI (savings_potential / effort)
        recs_with_roi = [
            (r, r.savings_potential / effort_hours[r.implementation_effort])
            for r in strategy.recommendations
        ]
        recs_with_roi.sort(key=lambda x: -x[1])
        
        roadmap = []
        remaining_hours = monthly_budget_hours
        phase = 1
        phase_items = []
        
        for rec, roi in recs_with_roi:
            hours = effort_hours[rec.implementation_effort]
            
            if hours <= remaining_hours:
                phase_items.append({
                    "recommendation": rec.title,
                    "effort_hours": hours,
                    "savings_potential": rec.savings_potential,
                    "priority": rec.priority.value,
                })
                remaining_hours -= hours
            else:
                # Start new phase
                if phase_items:
                    roadmap.append({
                        "phase": phase,
                        "total_hours": monthly_budget_hours - remaining_hours,
                        "items": phase_items,
                        "expected_savings": sum(i["savings_potential"] for i in phase_items),
                    })
                phase += 1
                phase_items = [{
                    "recommendation": rec.title,
                    "effort_hours": hours,
                    "savings_potential": rec.savings_potential,
                    "priority": rec.priority.value,
                }]
                remaining_hours = monthly_budget_hours - hours
        
        # Add final phase
        if phase_items:
            roadmap.append({
                "phase": phase,
                "total_hours": monthly_budget_hours - remaining_hours,
                "items": phase_items,
                "expected_savings": sum(i["savings_potential"] for i in phase_items),
            })
        
        return roadmap


class CostAwareConfigOptimizer:
    """
    Optimize system configuration for cost efficiency.
    
    Balances quality, latency, and cost based on constraints.
    """
    
    def __init__(self, cost_tracker: CostTracker):
        """Initialize with cost tracker."""
        self.cost_tracker = cost_tracker
        self.llm_model = LLMCostModel()
    
    def optimize_for_budget(
        self,
        monthly_budget_usd: float,
        min_quality_score: float = 7.0,
        max_latency_seconds: float = 30.0,
    ) -> Dict[str, Any]:
        """
        Find optimal configuration for a given budget.
        
        Args:
            monthly_budget_usd: Target monthly budget
            min_quality_score: Minimum acceptable quality (0-10)
            max_latency_seconds: Maximum acceptable latency
            
        Returns:
            Recommended configuration
        """
        pricing = LLMPricing()
        
        # Model options with quality/cost trade-offs
        models = [
            {
                "name": "gpt-4o",
                "provider": "openai",
                "quality": 9.5,
                "latency": 2.5,
                "cost_per_1k_tokens": (pricing.OPENAI_GPT4O_INPUT + pricing.OPENAI_GPT4O_OUTPUT) / 1000,
            },
            {
                "name": "gpt-4o-mini",
                "provider": "openai",
                "quality": 8.5,
                "latency": 1.5,
                "cost_per_1k_tokens": (pricing.OPENAI_GPT4O_MINI_INPUT + pricing.OPENAI_GPT4O_MINI_OUTPUT) / 1000,
            },
            {
                "name": "claude-3-sonnet",
                "provider": "anthropic",
                "quality": 9.0,
                "latency": 2.0,
                "cost_per_1k_tokens": (pricing.ANTHROPIC_CLAUDE_SONNET_INPUT + pricing.ANTHROPIC_CLAUDE_SONNET_OUTPUT) / 1000,
            },
            {
                "name": "claude-3-haiku",
                "provider": "anthropic",
                "quality": 7.5,
                "latency": 1.0,
                "cost_per_1k_tokens": (pricing.ANTHROPIC_CLAUDE_HAIKU_INPUT + pricing.ANTHROPIC_CLAUDE_HAIKU_OUTPUT) / 1000,
            },
            {
                "name": "gpt-3.5-turbo",
                "provider": "openai",
                "quality": 7.0,
                "latency": 1.0,
                "cost_per_1k_tokens": (pricing.OPENAI_GPT35_INPUT + pricing.OPENAI_GPT35_OUTPUT) / 1000,
            },
        ]
        
        # Estimate monthly token usage (1000 tours * 4 points * 4 agents * 500 tokens)
        estimated_monthly_tokens = 8_000_000  # 8M tokens
        
        # Find best model within constraints
        valid_models = [
            m for m in models
            if m["quality"] >= min_quality_score
            and m["latency"] <= max_latency_seconds / 4  # Per-agent latency
        ]
        
        if not valid_models:
            valid_models = models  # Fallback to all
        
        # Find cheapest that fits budget
        for model in sorted(valid_models, key=lambda m: m["cost_per_1k_tokens"]):
            monthly_cost = (estimated_monthly_tokens / 1000) * model["cost_per_1k_tokens"]
            if monthly_cost <= monthly_budget_usd:
                return {
                    "recommended_model": model["name"],
                    "provider": model["provider"],
                    "expected_monthly_cost": monthly_cost,
                    "expected_quality": model["quality"],
                    "expected_latency_per_agent": model["latency"],
                    "budget_utilization": monthly_cost / monthly_budget_usd * 100,
                    "recommendations": self._get_config_recommendations(model, monthly_budget_usd),
                }
        
        # If no model fits, recommend cheapest with caching
        cheapest = min(valid_models, key=lambda m: m["cost_per_1k_tokens"])
        base_cost = (estimated_monthly_tokens / 1000) * cheapest["cost_per_1k_tokens"]
        
        return {
            "recommended_model": cheapest["name"],
            "provider": cheapest["provider"],
            "expected_monthly_cost": base_cost,
            "budget_exceeded_by": base_cost - monthly_budget_usd,
            "expected_quality": cheapest["quality"],
            "recommendations": [
                "Enable aggressive caching to reduce costs",
                "Consider reducing tour frequency or route points",
                "Implement tiered model strategy",
            ],
        }
    
    def _get_config_recommendations(
        self,
        selected_model: Dict[str, Any],
        budget: float,
    ) -> List[str]:
        """Generate configuration recommendations."""
        recommendations = []
        
        if selected_model["quality"] < 8.0:
            recommendations.append("Consider using premium model for judge agent only")
        
        if selected_model["cost_per_1k_tokens"] > 0.001:
            recommendations.append("Enable response caching to reduce repeat queries")
        
        recommendations.append(f"Set max_tokens to 500 for content agents, 300 for judge")
        recommendations.append("Enable prompt caching for system prompts")
        
        return recommendations

