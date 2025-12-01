"""
Cost Models
===========

Data models for comprehensive cost analysis of the Multi-Agent Tour Guide System.

This module defines pricing structures and cost events for:
1. LLM API calls (OpenAI, Anthropic)
2. External API calls (Google Maps, YouTube, Spotify)
3. Compute resources (CPU time, memory, concurrent threads)

Author: Multi-Agent Tour Guide Research Team
Version: 1.0.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class CostCategory(Enum):
    """Categories of costs in the system."""
    
    # LLM Costs
    LLM_INPUT_TOKENS = "llm_input_tokens"
    LLM_OUTPUT_TOKENS = "llm_output_tokens"
    LLM_EMBEDDING = "llm_embedding"
    
    # API Costs
    API_GOOGLE_MAPS = "api_google_maps"
    API_YOUTUBE = "api_youtube"
    API_SPOTIFY = "api_spotify"
    API_WEB_SEARCH = "api_web_search"
    
    # Compute Costs
    COMPUTE_CPU = "compute_cpu"
    COMPUTE_MEMORY = "compute_memory"
    COMPUTE_NETWORK = "compute_network"
    
    # Operational Costs
    RETRY_OVERHEAD = "retry_overhead"
    CIRCUIT_BREAKER_SAVINGS = "circuit_breaker_savings"
    CACHE_HIT_SAVINGS = "cache_hit_savings"


@dataclass
class LLMPricing:
    """Pricing structure for LLM providers."""
    
    # OpenAI Pricing (per 1M tokens as of Nov 2024)
    OPENAI_GPT4O_INPUT = 2.50  # $/1M tokens
    OPENAI_GPT4O_OUTPUT = 10.00
    OPENAI_GPT4O_MINI_INPUT = 0.15
    OPENAI_GPT4O_MINI_OUTPUT = 0.60
    OPENAI_GPT35_INPUT = 0.50
    OPENAI_GPT35_OUTPUT = 1.50
    
    # Anthropic Pricing (per 1M tokens as of Nov 2024)
    ANTHROPIC_CLAUDE_SONNET_INPUT = 3.00
    ANTHROPIC_CLAUDE_SONNET_OUTPUT = 15.00
    ANTHROPIC_CLAUDE_HAIKU_INPUT = 0.25
    ANTHROPIC_CLAUDE_HAIKU_OUTPUT = 1.25
    ANTHROPIC_CLAUDE_OPUS_INPUT = 15.00
    ANTHROPIC_CLAUDE_OPUS_OUTPUT = 75.00


@dataclass
class APIPricing:
    """Pricing structure for external APIs."""
    
    # Google Maps API (per 1000 requests)
    GOOGLE_MAPS_DIRECTIONS = 5.00
    GOOGLE_MAPS_GEOCODING = 5.00
    GOOGLE_MAPS_PLACES = 17.00
    
    # YouTube Data API (quota-based, estimated cost)
    YOUTUBE_SEARCH = 0.001  # Estimated cost per search
    YOUTUBE_VIDEO_DETAILS = 0.0005
    
    # Spotify API (free tier, but consider rate limits)
    SPOTIFY_SEARCH = 0.0  # Free but rate-limited
    SPOTIFY_TRACK_DETAILS = 0.0
    
    # Web Search API (estimated)
    WEB_SEARCH_QUERY = 0.005


@dataclass
class ComputePricing:
    """Pricing for compute resources (based on cloud pricing)."""
    
    # AWS Lambda-equivalent pricing
    CPU_SECOND = 0.0000166667  # $/second for 1 vCPU
    MEMORY_GB_SECOND = 0.0000166667  # $/GB-second
    NETWORK_GB = 0.09  # $/GB outbound
    
    # Concurrent execution overhead
    THREAD_OVERHEAD_SECOND = 0.000001


@dataclass
class CostEvent:
    """A single cost event in the system."""
    
    timestamp: datetime
    category: CostCategory
    amount_usd: float
    agent_type: Optional[str] = None
    point_id: Optional[str] = None
    tour_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "category": self.category.value,
            "amount_usd": self.amount_usd,
            "agent_type": self.agent_type,
            "point_id": self.point_id,
            "tour_id": self.tour_id,
            "metadata": self.metadata,
        }


@dataclass
class LLMCostModel:
    """
    Cost model for LLM API usage.
    
    Calculates costs based on token usage and model selection.
    """
    
    provider: str = "openai"  # openai or anthropic
    model: str = "gpt-4o-mini"
    
    def calculate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """
        Calculate cost for an LLM API call.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Cost in USD
        """
        pricing = LLMPricing()
        
        # Get pricing based on provider and model
        if self.provider == "openai":
            if "gpt-4o-mini" in self.model:
                input_rate = pricing.OPENAI_GPT4O_MINI_INPUT
                output_rate = pricing.OPENAI_GPT4O_MINI_OUTPUT
            elif "gpt-4o" in self.model or "gpt-4" in self.model:
                input_rate = pricing.OPENAI_GPT4O_INPUT
                output_rate = pricing.OPENAI_GPT4O_OUTPUT
            else:
                input_rate = pricing.OPENAI_GPT35_INPUT
                output_rate = pricing.OPENAI_GPT35_OUTPUT
        else:  # anthropic
            if "haiku" in self.model.lower():
                input_rate = pricing.ANTHROPIC_CLAUDE_HAIKU_INPUT
                output_rate = pricing.ANTHROPIC_CLAUDE_HAIKU_OUTPUT
            elif "opus" in self.model.lower():
                input_rate = pricing.ANTHROPIC_CLAUDE_OPUS_INPUT
                output_rate = pricing.ANTHROPIC_CLAUDE_OPUS_OUTPUT
            else:  # sonnet
                input_rate = pricing.ANTHROPIC_CLAUDE_SONNET_INPUT
                output_rate = pricing.ANTHROPIC_CLAUDE_SONNET_OUTPUT
        
        # Calculate cost (rates are per 1M tokens)
        input_cost = (input_tokens / 1_000_000) * input_rate
        output_cost = (output_tokens / 1_000_000) * output_rate
        
        return input_cost + output_cost
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count from text (rough approximation)."""
        # Rough estimation: ~4 characters per token for English
        return len(text) // 4


@dataclass
class APICostModel:
    """Cost model for external API usage."""
    
    def calculate_google_maps_cost(
        self,
        directions_calls: int = 0,
        geocoding_calls: int = 0,
        places_calls: int = 0,
    ) -> float:
        """Calculate Google Maps API cost."""
        pricing = APIPricing()
        return (
            (directions_calls / 1000) * pricing.GOOGLE_MAPS_DIRECTIONS +
            (geocoding_calls / 1000) * pricing.GOOGLE_MAPS_GEOCODING +
            (places_calls / 1000) * pricing.GOOGLE_MAPS_PLACES
        )
    
    def calculate_youtube_cost(
        self,
        search_calls: int = 0,
        details_calls: int = 0,
    ) -> float:
        """Calculate YouTube API cost."""
        pricing = APIPricing()
        return (
            search_calls * pricing.YOUTUBE_SEARCH +
            details_calls * pricing.YOUTUBE_VIDEO_DETAILS
        )
    
    def calculate_web_search_cost(self, search_calls: int = 0) -> float:
        """Calculate web search API cost."""
        return search_calls * APIPricing.WEB_SEARCH_QUERY


@dataclass
class ComputeCostModel:
    """Cost model for compute resources."""
    
    def calculate_execution_cost(
        self,
        cpu_seconds: float,
        memory_gb: float = 0.5,
        duration_seconds: float = 0,
    ) -> float:
        """Calculate compute execution cost."""
        pricing = ComputePricing()
        
        cpu_cost = cpu_seconds * pricing.CPU_SECOND
        memory_cost = memory_gb * duration_seconds * pricing.MEMORY_GB_SECOND
        
        return cpu_cost + memory_cost
    
    def calculate_parallel_overhead(
        self,
        num_threads: int,
        duration_seconds: float,
    ) -> float:
        """Calculate overhead cost for parallel execution."""
        pricing = ComputePricing()
        return num_threads * duration_seconds * pricing.THREAD_OVERHEAD_SECOND


@dataclass
class TourCostSummary:
    """Cost summary for a single tour execution."""
    
    tour_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    num_points: int = 0
    
    # Cost breakdowns
    llm_costs: float = 0.0
    api_costs: float = 0.0
    compute_costs: float = 0.0
    
    # Token usage
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    
    # API calls
    google_maps_calls: int = 0
    youtube_calls: int = 0
    web_search_calls: int = 0
    
    # Savings
    cache_savings: float = 0.0
    circuit_breaker_savings: float = 0.0
    retry_overhead: float = 0.0
    
    # Agent-level breakdown
    agent_costs: Dict[str, float] = field(default_factory=dict)
    
    @property
    def total_cost(self) -> float:
        """Calculate total cost."""
        return self.llm_costs + self.api_costs + self.compute_costs + self.retry_overhead
    
    @property
    def effective_cost(self) -> float:
        """Calculate effective cost after savings."""
        return self.total_cost - self.cache_savings - self.circuit_breaker_savings
    
    @property
    def cost_per_point(self) -> float:
        """Calculate cost per route point."""
        if self.num_points == 0:
            return 0.0
        return self.effective_cost / self.num_points
    
    @property
    def duration_seconds(self) -> float:
        """Calculate tour duration."""
        if self.end_time is None:
            return 0.0
        return (self.end_time - self.start_time).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "tour_id": self.tour_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "num_points": self.num_points,
            "costs": {
                "llm": self.llm_costs,
                "api": self.api_costs,
                "compute": self.compute_costs,
                "total": self.total_cost,
                "effective": self.effective_cost,
            },
            "tokens": {
                "input": self.total_input_tokens,
                "output": self.total_output_tokens,
                "total": self.total_input_tokens + self.total_output_tokens,
            },
            "api_calls": {
                "google_maps": self.google_maps_calls,
                "youtube": self.youtube_calls,
                "web_search": self.web_search_calls,
            },
            "savings": {
                "cache": self.cache_savings,
                "circuit_breaker": self.circuit_breaker_savings,
                "total": self.cache_savings + self.circuit_breaker_savings,
            },
            "overhead": {
                "retry": self.retry_overhead,
            },
            "agent_costs": self.agent_costs,
            "metrics": {
                "cost_per_point": self.cost_per_point,
                "duration_seconds": self.duration_seconds,
            },
        }


@dataclass  
class SystemCostReport:
    """Comprehensive system cost report."""
    
    report_period_start: datetime
    report_period_end: datetime
    
    # Tour summaries
    tour_summaries: List[TourCostSummary] = field(default_factory=list)
    
    # Aggregated metrics
    total_tours: int = 0
    total_points: int = 0
    
    # Cost totals
    total_llm_cost: float = 0.0
    total_api_cost: float = 0.0
    total_compute_cost: float = 0.0
    total_savings: float = 0.0
    
    # Projections
    monthly_projection: float = 0.0
    yearly_projection: float = 0.0
    
    @property
    def total_cost(self) -> float:
        """Total cost for the period."""
        return self.total_llm_cost + self.total_api_cost + self.total_compute_cost
    
    @property
    def average_cost_per_tour(self) -> float:
        """Average cost per tour."""
        if self.total_tours == 0:
            return 0.0
        return self.total_cost / self.total_tours
    
    @property
    def average_cost_per_point(self) -> float:
        """Average cost per route point."""
        if self.total_points == 0:
            return 0.0
        return self.total_cost / self.total_points
    
    @property
    def cost_efficiency_ratio(self) -> float:
        """Ratio of effective cost to gross cost (lower is better)."""
        if self.total_cost == 0:
            return 1.0
        return (self.total_cost - self.total_savings) / self.total_cost
    
    def calculate_projections(self) -> None:
        """Calculate monthly and yearly projections."""
        period_days = (self.report_period_end - self.report_period_start).days
        if period_days <= 0:
            period_days = 1
        
        daily_cost = self.total_cost / period_days
        self.monthly_projection = daily_cost * 30
        self.yearly_projection = daily_cost * 365
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "period": {
                "start": self.report_period_start.isoformat(),
                "end": self.report_period_end.isoformat(),
            },
            "summary": {
                "total_tours": self.total_tours,
                "total_points": self.total_points,
                "total_cost": self.total_cost,
                "total_savings": self.total_savings,
            },
            "breakdown": {
                "llm": self.total_llm_cost,
                "api": self.total_api_cost,
                "compute": self.total_compute_cost,
            },
            "metrics": {
                "avg_cost_per_tour": self.average_cost_per_tour,
                "avg_cost_per_point": self.average_cost_per_point,
                "efficiency_ratio": self.cost_efficiency_ratio,
            },
            "projections": {
                "monthly": self.monthly_projection,
                "yearly": self.yearly_projection,
            },
        }

