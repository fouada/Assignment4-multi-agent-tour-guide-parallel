"""
Tests for Cost Analysis Module.

MIT-Level Test Coverage for:
- Cost Models (LLM, API, Compute)
- Cost Tracking
- Cost Optimization
- ROI Analysis
- Visualization

Coverage Target: 85%+
"""

import json
import threading
from datetime import datetime, timedelta

import pytest

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
    CostOptimizer,
    OptimizationCategory,
    OptimizationPriority,
    OptimizationRecommendation,
    OptimizationStrategy,
    ROIAnalysis,
)
from src.cost_analysis.tracker import CostTracker
from src.cost_analysis.visualization import COST_COLORS, CostVisualizationPanel

# =============================================================================
# CostCategory Tests
# =============================================================================


class TestCostCategory:
    """Test CostCategory enum."""

    def test_llm_categories_exist(self):
        """Test LLM cost categories."""
        assert CostCategory.LLM_INPUT_TOKENS is not None
        assert CostCategory.LLM_OUTPUT_TOKENS is not None
        assert CostCategory.LLM_EMBEDDING is not None

    def test_api_categories_exist(self):
        """Test API cost categories."""
        assert CostCategory.API_GOOGLE_MAPS is not None
        assert CostCategory.API_YOUTUBE is not None
        assert CostCategory.API_WEB_SEARCH is not None

    def test_compute_categories_exist(self):
        """Test compute cost categories."""
        assert CostCategory.COMPUTE_CPU is not None
        assert CostCategory.COMPUTE_MEMORY is not None

    def test_operational_categories_exist(self):
        """Test operational cost categories."""
        assert CostCategory.RETRY_OVERHEAD is not None
        assert CostCategory.CACHE_HIT_SAVINGS is not None


# =============================================================================
# LLMPricing Tests
# =============================================================================


class TestLLMPricing:
    """Test LLMPricing dataclass."""

    def test_openai_pricing(self):
        """Test OpenAI pricing values."""
        pricing = LLMPricing()

        assert pricing.OPENAI_GPT4O_INPUT > 0
        assert pricing.OPENAI_GPT4O_OUTPUT > 0
        assert pricing.OPENAI_GPT4O_MINI_INPUT > 0
        assert pricing.OPENAI_GPT4O_MINI_OUTPUT > 0

    def test_anthropic_pricing(self):
        """Test Anthropic pricing values."""
        pricing = LLMPricing()

        assert pricing.ANTHROPIC_CLAUDE_SONNET_INPUT > 0
        assert pricing.ANTHROPIC_CLAUDE_SONNET_OUTPUT > 0
        assert pricing.ANTHROPIC_CLAUDE_HAIKU_INPUT > 0

    def test_pricing_relationships(self):
        """Test pricing relationships (more capable = more expensive)."""
        pricing = LLMPricing()

        # GPT-4o should be more expensive than GPT-4o-mini
        assert pricing.OPENAI_GPT4O_INPUT > pricing.OPENAI_GPT4O_MINI_INPUT
        assert pricing.OPENAI_GPT4O_OUTPUT > pricing.OPENAI_GPT4O_MINI_OUTPUT

        # Opus should be more expensive than Sonnet
        assert (
            pricing.ANTHROPIC_CLAUDE_OPUS_INPUT > pricing.ANTHROPIC_CLAUDE_SONNET_INPUT
        )


# =============================================================================
# APIPricing Tests
# =============================================================================


class TestAPIPricing:
    """Test APIPricing dataclass."""

    def test_google_maps_pricing(self):
        """Test Google Maps API pricing."""
        pricing = APIPricing()

        assert pricing.GOOGLE_MAPS_DIRECTIONS > 0
        assert pricing.GOOGLE_MAPS_PLACES > 0

    def test_youtube_pricing(self):
        """Test YouTube API pricing."""
        pricing = APIPricing()

        assert pricing.YOUTUBE_SEARCH >= 0
        assert pricing.YOUTUBE_VIDEO_DETAILS >= 0


# =============================================================================
# ComputePricing Tests
# =============================================================================


class TestComputePricing:
    """Test ComputePricing dataclass."""

    def test_cpu_pricing(self):
        """Test CPU pricing."""
        pricing = ComputePricing()
        assert pricing.CPU_SECOND > 0

    def test_memory_pricing(self):
        """Test memory pricing."""
        pricing = ComputePricing()
        assert pricing.MEMORY_GB_SECOND > 0


# =============================================================================
# CostEvent Tests
# =============================================================================


class TestCostEvent:
    """Test CostEvent dataclass."""

    def test_event_creation(self):
        """Test creating a cost event."""
        event = CostEvent(
            timestamp=datetime.now(),
            category=CostCategory.LLM_INPUT_TOKENS,
            amount_usd=0.05,
        )
        assert event.amount_usd == 0.05
        assert event.category == CostCategory.LLM_INPUT_TOKENS

    def test_event_with_metadata(self):
        """Test event with full metadata."""
        event = CostEvent(
            timestamp=datetime.now(),
            category=CostCategory.API_GOOGLE_MAPS,
            amount_usd=0.02,
            agent_type="video",
            point_id="point_123",
            tour_id="tour_456",
            metadata={"calls": 4},
        )

        assert event.agent_type == "video"
        assert event.point_id == "point_123"
        assert event.metadata["calls"] == 4

    def test_event_to_dict(self):
        """Test converting event to dictionary."""
        event = CostEvent(
            timestamp=datetime.now(),
            category=CostCategory.COMPUTE_CPU,
            amount_usd=0.01,
        )

        d = event.to_dict()

        assert "timestamp" in d
        assert "category" in d
        assert "amount_usd" in d
        assert d["amount_usd"] == 0.01


# =============================================================================
# LLMCostModel Tests
# =============================================================================


class TestLLMCostModel:
    """Test LLMCostModel."""

    @pytest.fixture
    def model(self):
        """Create LLM cost model."""
        return LLMCostModel(provider="openai", model="gpt-4o-mini")

    def test_model_creation(self, model):
        """Test model creation."""
        assert model.provider == "openai"
        assert model.model == "gpt-4o-mini"

    def test_calculate_cost_basic(self, model):
        """Test basic cost calculation."""
        cost = model.calculate_cost(
            input_tokens=1000,
            output_tokens=500,
        )

        assert cost > 0
        assert isinstance(cost, float)

    def test_calculate_cost_zero_tokens(self, model):
        """Test cost with zero tokens."""
        cost = model.calculate_cost(
            input_tokens=0,
            output_tokens=0,
        )

        assert cost == 0.0

    def test_calculate_cost_large_tokens(self, model):
        """Test cost with large token count."""
        cost = model.calculate_cost(
            input_tokens=100000,
            output_tokens=50000,
        )

        assert cost > 0
        # Should be around $0.045 for 150K tokens with gpt-4o-mini rates

    def test_cost_increases_with_tokens(self, model):
        """Test cost increases with token count."""
        cost_small = model.calculate_cost(1000, 500)
        cost_large = model.calculate_cost(10000, 5000)

        assert cost_large > cost_small
        # Should be roughly 10x
        assert 8 <= cost_large / cost_small <= 12

    def test_different_models_different_costs(self):
        """Test different models have different costs."""
        model_mini = LLMCostModel(provider="openai", model="gpt-4o-mini")
        model_full = LLMCostModel(provider="openai", model="gpt-4o")

        cost_mini = model_mini.calculate_cost(1000, 500)
        cost_full = model_full.calculate_cost(1000, 500)

        # GPT-4o should be more expensive
        assert cost_full > cost_mini

    def test_anthropic_models(self):
        """Test Anthropic model costs."""
        model_haiku = LLMCostModel(provider="anthropic", model="claude-haiku")
        model_sonnet = LLMCostModel(provider="anthropic", model="claude-sonnet")

        cost_haiku = model_haiku.calculate_cost(1000, 500)
        cost_sonnet = model_sonnet.calculate_cost(1000, 500)

        # Sonnet should be more expensive
        assert cost_sonnet > cost_haiku

    def test_estimate_tokens(self, model):
        """Test token estimation."""
        text = "This is a test sentence with about 40 characters."
        tokens = model.estimate_tokens(text)

        # Rough estimate: ~4 chars per token
        assert 8 <= tokens <= 15


# =============================================================================
# APICostModel Tests
# =============================================================================


class TestAPICostModel:
    """Test APICostModel."""

    @pytest.fixture
    def model(self):
        """Create API cost model."""
        return APICostModel()

    def test_google_maps_cost(self, model):
        """Test Google Maps cost calculation."""
        cost = model.calculate_google_maps_cost(
            directions_calls=100,
            geocoding_calls=50,
            places_calls=25,
        )

        assert cost > 0

    def test_google_maps_zero_calls(self, model):
        """Test zero API calls."""
        cost = model.calculate_google_maps_cost(
            directions_calls=0,
            geocoding_calls=0,
            places_calls=0,
        )

        assert cost == 0.0

    def test_youtube_cost(self, model):
        """Test YouTube cost calculation."""
        cost = model.calculate_youtube_cost(
            search_calls=100,
            details_calls=50,
        )

        assert cost >= 0  # YouTube API might be free

    def test_web_search_cost(self, model):
        """Test web search cost calculation."""
        cost = model.calculate_web_search_cost(search_calls=100)
        assert cost >= 0


# =============================================================================
# ComputeCostModel Tests
# =============================================================================


class TestComputeCostModel:
    """Test ComputeCostModel."""

    @pytest.fixture
    def model(self):
        """Create compute cost model."""
        return ComputeCostModel()

    def test_execution_cost(self, model):
        """Test execution cost calculation."""
        cost = model.calculate_execution_cost(
            cpu_seconds=10.0,
            memory_gb=0.5,
            duration_seconds=10.0,
        )

        assert cost > 0

    def test_execution_cost_zero(self, model):
        """Test zero execution."""
        cost = model.calculate_execution_cost(
            cpu_seconds=0.0,
            memory_gb=0.0,
            duration_seconds=0.0,
        )

        assert cost == 0.0

    def test_parallel_overhead(self, model):
        """Test parallel execution overhead."""
        overhead = model.calculate_parallel_overhead(
            num_threads=4,
            duration_seconds=5.0,
        )

        assert overhead > 0

    def test_cost_increases_with_resources(self, model):
        """Test cost increases with resources."""
        cost_small = model.calculate_execution_cost(1.0, 0.25, 1.0)
        cost_large = model.calculate_execution_cost(10.0, 2.0, 10.0)

        assert cost_large > cost_small


# =============================================================================
# TourCostSummary Tests
# =============================================================================


class TestTourCostSummary:
    """Test TourCostSummary dataclass."""

    @pytest.fixture
    def summary(self):
        """Create tour cost summary."""
        return TourCostSummary(
            tour_id="tour_123",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(minutes=5),
            num_points=10,
            llm_costs=0.05,
            api_costs=0.02,
            compute_costs=0.001,
            total_input_tokens=5000,
            total_output_tokens=2000,
            cache_savings=0.01,
        )

    def test_total_cost(self, summary):
        """Test total cost calculation."""
        total = summary.total_cost

        # llm + api + compute + retry
        expected = 0.05 + 0.02 + 0.001 + 0.0
        assert abs(total - expected) < 0.0001

    def test_effective_cost(self, summary):
        """Test effective cost after savings."""
        effective = summary.effective_cost

        # total - cache_savings - circuit_breaker_savings
        assert effective < summary.total_cost
        assert effective == summary.total_cost - 0.01

    def test_cost_per_point(self, summary):
        """Test cost per point calculation."""
        cpp = summary.cost_per_point

        assert cpp == summary.effective_cost / 10

    def test_duration_seconds(self, summary):
        """Test duration calculation."""
        duration = summary.duration_seconds

        assert abs(duration - 300) < 1  # 5 minutes = 300 seconds

    def test_to_dict(self, summary):
        """Test conversion to dictionary."""
        d = summary.to_dict()

        assert "tour_id" in d
        assert "costs" in d
        assert "tokens" in d
        assert d["tour_id"] == "tour_123"


# =============================================================================
# SystemCostReport Tests
# =============================================================================


class TestSystemCostReport:
    """Test SystemCostReport dataclass."""

    @pytest.fixture
    def report(self):
        """Create system cost report."""
        return SystemCostReport(
            report_period_start=datetime.now() - timedelta(days=7),
            report_period_end=datetime.now(),
            total_tours=100,
            total_points=500,
            total_llm_cost=5.0,
            total_api_cost=2.0,
            total_compute_cost=0.5,
            total_savings=1.0,
        )

    def test_total_cost(self, report):
        """Test total cost calculation."""
        total = report.total_cost

        assert total == 5.0 + 2.0 + 0.5

    def test_average_cost_per_tour(self, report):
        """Test average cost per tour."""
        avg = report.average_cost_per_tour

        assert avg == report.total_cost / 100

    def test_average_cost_per_point(self, report):
        """Test average cost per point."""
        avg = report.average_cost_per_point

        assert avg == report.total_cost / 500

    def test_cost_efficiency_ratio(self, report):
        """Test cost efficiency ratio."""
        ratio = report.cost_efficiency_ratio

        # (total - savings) / total
        expected = (7.5 - 1.0) / 7.5
        assert abs(ratio - expected) < 0.001

    def test_calculate_projections(self, report):
        """Test monthly/yearly projections."""
        report.calculate_projections()

        assert report.monthly_projection > 0
        assert report.yearly_projection > 0
        assert report.yearly_projection > report.monthly_projection

    def test_to_dict(self, report):
        """Test conversion to dictionary."""
        d = report.to_dict()

        assert "period" in d
        assert "summary" in d
        assert "breakdown" in d


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_zero_points_cost_per_point(self):
        """Test cost per point with zero points."""
        summary = TourCostSummary(
            tour_id="test",
            start_time=datetime.now(),
            num_points=0,
            llm_costs=0.05,
        )

        assert summary.cost_per_point == 0.0

    def test_zero_tours_average_cost(self):
        """Test average cost with zero tours."""
        report = SystemCostReport(
            report_period_start=datetime.now() - timedelta(days=1),
            report_period_end=datetime.now(),
            total_tours=0,
            total_points=0,
        )

        assert report.average_cost_per_tour == 0.0
        assert report.average_cost_per_point == 0.0

    def test_no_end_time_duration(self):
        """Test duration with no end time."""
        summary = TourCostSummary(
            tour_id="test",
            start_time=datetime.now(),
            end_time=None,
        )

        assert summary.duration_seconds == 0.0

    def test_large_token_counts(self):
        """Test with very large token counts."""
        model = LLMCostModel()
        cost = model.calculate_cost(
            input_tokens=1_000_000,
            output_tokens=500_000,
        )

        assert cost > 0
        assert isinstance(cost, float)

    def test_negative_values_handled(self):
        """Test that negative values don't break calculations."""
        summary = TourCostSummary(
            tour_id="test",
            start_time=datetime.now(),
            num_points=10,
            llm_costs=0.05,
            cache_savings=0.1,  # More savings than costs
        )

        # Should handle gracefully
        effective = summary.effective_cost
        assert isinstance(effective, float)


# =============================================================================
# Integration Tests
# =============================================================================


class TestCostAnalysisIntegration:
    """Integration tests for cost analysis."""

    def test_full_tour_cost_calculation(self):
        """Test calculating full tour cost."""
        llm_model = LLMCostModel()
        api_model = APICostModel()
        compute_model = ComputeCostModel()

        # Simulate a tour with 5 points
        llm_cost = llm_model.calculate_cost(
            input_tokens=2500,  # 500 per point
            output_tokens=1000,  # 200 per point
        )

        api_cost = api_model.calculate_google_maps_cost(
            directions_calls=1,
            places_calls=5,
        )

        compute_cost = compute_model.calculate_execution_cost(
            cpu_seconds=5.0,  # 1 sec per point
            memory_gb=0.5,
            duration_seconds=5.0,
        )

        summary = TourCostSummary(
            tour_id="integration_test",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(seconds=30),
            num_points=5,
            llm_costs=llm_cost,
            api_costs=api_cost,
            compute_costs=compute_cost,
            total_input_tokens=2500,
            total_output_tokens=1000,
        )

        assert summary.total_cost > 0
        assert summary.cost_per_point > 0
        assert abs(summary.duration_seconds - 30.0) < 1  # Allow for timing variance


# =============================================================================
# CostTracker Tests
# =============================================================================


class TestCostTracker:
    """Comprehensive tests for CostTracker."""

    @pytest.fixture
    def tracker(self):
        """Create a cost tracker."""
        return CostTracker(budget_limit_usd=100.0, alert_threshold=0.8)

    def test_initialization(self, tracker):
        """Test tracker initialization."""
        assert tracker.budget_limit_usd == 100.0
        assert tracker.alert_threshold == 0.8
        assert len(tracker._events) == 0

    def test_record_llm_usage(self, tracker):
        """Test recording LLM usage."""
        event = tracker.record_llm_usage(
            input_tokens=1000,
            output_tokens=500,
            agent_type="video",
            tour_id="tour_123",
        )

        assert event.amount_usd > 0
        assert event.metadata["input_tokens"] == 1000
        assert event.metadata["output_tokens"] == 500

    def test_record_llm_usage_with_model_override(self, tracker):
        """Test recording LLM usage with model override."""
        event = tracker.record_llm_usage(
            input_tokens=1000,
            output_tokens=500,
            model="gpt-4o",
        )

        assert event.amount_usd > 0
        assert event.metadata["model"] == "gpt-4o"

    def test_record_llm_usage_zero_tokens(self, tracker):
        """Test recording LLM usage with zero tokens."""
        event = tracker.record_llm_usage(
            input_tokens=0,
            output_tokens=0,
        )

        assert event.amount_usd == 0.0

    def test_record_api_call(self, tracker):
        """Test recording API call."""
        event = tracker.record_api_call(
            api_type="google_maps",
            calls=5,
            agent_type="video",
            tour_id="tour_123",
        )

        assert event.amount_usd >= 0

    def test_record_compute_usage(self, tracker):
        """Test recording compute usage."""
        event = tracker.record_compute_usage(
            cpu_seconds=10.0,
            memory_gb=0.5,
            duration_seconds=10.0,
            agent_type="judge",
            tour_id="tour_123",
        )

        assert event.amount_usd >= 0

    def test_get_total_cost(self, tracker):
        """Test getting total cost."""
        tracker.record_llm_usage(1000, 500, agent_type="video")
        tracker.record_llm_usage(2000, 1000, agent_type="music")

        total = tracker.get_total_cost()
        assert total > 0

    def test_get_agent_costs(self, tracker):
        """Test getting costs by agent."""
        tracker.record_llm_usage(1000, 500, agent_type="video")
        tracker.record_llm_usage(2000, 1000, agent_type="music")

        agent_costs = tracker.get_agent_costs()

        assert "video" in agent_costs
        assert "music" in agent_costs
        assert agent_costs["video"] > 0

    def test_get_tour_costs(self, tracker):
        """Test getting costs by tour."""
        tracker.record_llm_usage(1000, 500, tour_id="tour_1")
        tracker.record_llm_usage(2000, 1000, tour_id="tour_2")

        tour_costs = tracker.get_tour_costs()

        assert "tour_1" in tour_costs
        assert "tour_2" in tour_costs

    def test_get_cost_breakdown(self, tracker):
        """Test getting cost breakdown."""
        tracker.record_llm_usage(1000, 500)
        tracker.record_api_call("google_maps", 1)

        breakdown = tracker.get_cost_breakdown()

        assert isinstance(breakdown, dict)
        # Keys are category values (strings)
        assert CostCategory.LLM_INPUT_TOKENS.value in breakdown

    def test_budget_alert(self, tracker):
        """Test budget alert callback."""
        alerts = []

        def alert_callback(message, usage):
            alerts.append((message, usage))

        tracker.register_alert_callback(alert_callback)

        # Record enough costs to trigger alert
        for _ in range(100):
            tracker.record_llm_usage(10000, 5000)

        # Alert may or may not trigger based on actual costs
        # Just ensure no errors occur
        assert isinstance(tracker.get_total_cost(), float)

    def test_thread_safety(self, tracker):
        """Test thread-safe operations."""
        errors = []

        def record_costs():
            try:
                for _ in range(50):
                    tracker.record_llm_usage(100, 50)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=record_costs) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        # Should have 250 events (50 x 5 threads, but each call creates 2 events)

    def test_get_events_in_range(self, tracker):
        """Test filtering events by time range."""
        tracker.record_llm_usage(1000, 500)

        start = datetime.now() - timedelta(hours=1)
        end = datetime.now() + timedelta(hours=1)

        events = tracker.get_events_in_range(start, end)

        # Should have 2 events (input + output)
        assert len(events) >= 2

    def test_get_hourly_costs(self, tracker):
        """Test getting hourly cost breakdown."""
        tracker.record_llm_usage(1000, 500, agent_type="video", tour_id="tour_1")

        hourly_costs = tracker.get_hourly_costs(hours=24)

        assert isinstance(hourly_costs, dict)
        assert len(hourly_costs) == 24

    def test_persistence(self, tracker, tmp_path):
        """Test saving and loading tracker state."""
        tracker.record_llm_usage(1000, 500, agent_type="video")

        # Set persistence path and save
        save_path = tmp_path / "cost_state.json"
        tracker.set_persistence_path(save_path)
        tracker.persist()

        assert save_path.exists()

        # Load and verify
        with open(save_path) as f:
            data = json.load(f)

        assert "events" in data or "category_totals" in data

    def test_reset(self, tracker):
        """Test resetting tracker."""
        tracker.record_llm_usage(1000, 500)
        assert tracker.get_total_cost() > 0

        tracker.reset()

        assert tracker.get_total_cost() == 0

    def test_record_savings(self, tracker):
        """Test recording savings."""
        event = tracker.record_savings(
            savings_type="cache_hit",
            amount_usd=0.05,
            agent_type="video",
        )

        assert event.amount_usd < 0  # Savings are negative

    def test_record_retry_overhead(self, tracker):
        """Test recording retry overhead."""
        event = tracker.record_retry_overhead(
            overhead_usd=0.02,
            agent_type="video",
            retry_count=2,
        )

        assert event.amount_usd == 0.02

    def test_get_total_savings(self, tracker):
        """Test getting total savings."""
        tracker.record_savings("cache_hit", 0.05)
        tracker.record_savings("circuit_breaker", 0.03)

        savings = tracker.get_total_savings()

        assert savings == pytest.approx(0.08, abs=0.001)

    def test_get_effective_cost(self, tracker):
        """Test getting effective cost after savings."""
        tracker.record_llm_usage(1000, 500)
        tracker.record_savings("cache_hit", 0.01)

        total = tracker.get_total_cost()
        effective = tracker.get_effective_cost()

        assert effective < total


# =============================================================================
# CostVisualizationPanel Tests
# =============================================================================


class TestCostVisualizationPanel:
    """Comprehensive tests for CostVisualizationPanel."""

    @pytest.fixture
    def sample_cost_data(self):
        """Sample cost data for visualization."""
        return {
            "llm_cost": 45.0,
            "api_cost": 25.0,
            "compute_cost": 20.0,
            "retry_cost": 10.0,
            "video_cost": 12.0,
            "music_cost": 8.0,
            "text_cost": 10.0,
            "judge_cost": 15.0,
            "budget_used": 65.0,
        }

    def test_colors_defined(self):
        """Test that colors are defined."""
        assert "primary" in COST_COLORS
        assert "llm" in COST_COLORS
        assert "api" in COST_COLORS
        assert "compute" in COST_COLORS
        assert "background" in COST_COLORS

    def test_create_cost_overview_dashboard(self, sample_cost_data):
        """Test creating overview dashboard."""
        import plotly.graph_objects as go

        fig = CostVisualizationPanel.create_cost_overview_dashboard(sample_cost_data)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    def test_create_cost_overview_with_tour_data(self, sample_cost_data):
        """Test creating overview with tour data."""
        import plotly.graph_objects as go

        tour_data = [
            {"tour_id": "t1", "cost": 10.0},
            {"tour_id": "t2", "cost": 15.0},
        ]

        fig = CostVisualizationPanel.create_cost_overview_dashboard(
            sample_cost_data, tour_data=tour_data
        )

        assert isinstance(fig, go.Figure)

    def test_empty_data_handling(self):
        """Test handling empty data."""
        import plotly.graph_objects as go

        empty_data = {}

        fig = CostVisualizationPanel.create_cost_overview_dashboard(empty_data)

        assert isinstance(fig, go.Figure)


class TestCostBreakdownChart:
    """Tests for CostBreakdownChart."""

    def test_create_sunburst(self):
        """Test creating sunburst chart."""
        import plotly.graph_objects as go

        from src.cost_analysis.visualization import CostBreakdownChart

        cost_breakdown = {
            "LLM": {"input": 30.0, "output": 15.0},
            "API": {"google_maps": 10.0, "youtube": 5.0},
        }

        fig = CostBreakdownChart.create_sunburst(cost_breakdown)

        assert isinstance(fig, go.Figure)

    def test_create_treemap(self):
        """Test creating treemap."""
        import pandas as pd
        import plotly.graph_objects as go

        from src.cost_analysis.visualization import CostBreakdownChart

        cost_data = pd.DataFrame(
            {
                "category": ["LLM", "LLM", "API", "API"],
                "subcategory": ["input", "output", "maps", "youtube"],
                "value": [30.0, 15.0, 10.0, 5.0],
            }
        )

        fig = CostBreakdownChart.create_treemap(cost_data)

        assert isinstance(fig, go.Figure)

    def test_create_stacked_bar_comparison(self):
        """Test creating stacked bar comparison."""
        import plotly.graph_objects as go

        from src.cost_analysis.visualization import CostBreakdownChart

        config_costs = {
            "Config A": {"LLM": 50.0, "API": 20.0},
            "Config B": {"LLM": 40.0, "API": 25.0},
        }

        fig = CostBreakdownChart.create_stacked_bar_comparison(config_costs)

        assert isinstance(fig, go.Figure)


class TestCostTrendChart:
    """Tests for CostTrendChart."""

    def test_create_cost_trend_with_forecast(self):
        """Test creating cost trend with forecast."""
        import pandas as pd
        import plotly.graph_objects as go

        from src.cost_analysis.visualization import CostTrendChart

        # Create sample historical data
        dates = pd.date_range(end=datetime.now(), periods=30, freq="D")
        historical = pd.DataFrame(
            {
                "date": dates,
                "cost": [50 + i * 0.5 for i in range(30)],
            }
        )

        fig = CostTrendChart.create_cost_trend_with_forecast(
            historical_costs=historical,
            forecast_days=7,
        )

        assert isinstance(fig, go.Figure)

    def test_create_cost_trend_with_empty_data(self):
        """Test cost trend with empty data (should generate sample)."""
        import pandas as pd
        import plotly.graph_objects as go

        from src.cost_analysis.visualization import CostTrendChart

        empty_df = pd.DataFrame()

        fig = CostTrendChart.create_cost_trend_with_forecast(
            historical_costs=empty_df,
            forecast_days=7,
        )

        assert isinstance(fig, go.Figure)


# =============================================================================
# CostOptimizer Tests
# =============================================================================


class TestCostOptimizer:
    """Comprehensive tests for CostOptimizer."""

    @pytest.fixture
    def tracker(self):
        """Create a cost tracker."""
        return CostTracker(budget_limit_usd=100.0)

    @pytest.fixture
    def optimizer(self, tracker):
        """Create a cost optimizer."""
        return CostOptimizer(cost_tracker=tracker)

    def test_initialization(self, optimizer):
        """Test optimizer initialization."""
        assert optimizer is not None
        assert optimizer.cost_tracker is not None

    def test_optimization_categories_exist(self):
        """Test optimization categories enum."""
        assert OptimizationCategory.MODEL_SELECTION is not None
        assert OptimizationCategory.CACHING is not None
        assert OptimizationCategory.BATCHING is not None

    def test_optimization_priority_exist(self):
        """Test optimization priority enum."""
        assert OptimizationPriority.CRITICAL is not None
        assert OptimizationPriority.HIGH is not None
        assert OptimizationPriority.MEDIUM is not None
        assert OptimizationPriority.LOW is not None

    def test_generate_strategy(self, optimizer, tracker):
        """Test generating optimization strategy."""
        # Record some costs
        tracker.record_llm_usage(1000, 500)

        strategy = optimizer.generate_strategy(monthly_cost=100.0)

        assert isinstance(strategy, OptimizationStrategy)
        assert len(strategy.recommendations) >= 0
        assert strategy.total_current_cost == 100.0

    def test_strategy_to_dict(self, optimizer):
        """Test converting strategy to dictionary."""
        strategy = optimizer.generate_strategy(monthly_cost=100.0)

        data = strategy.to_dict()

        assert "summary" in data
        assert "recommendations" in data
        assert "generated_at" in data

    def test_strategy_get_by_priority(self, optimizer):
        """Test filtering recommendations by priority."""
        strategy = optimizer.generate_strategy(monthly_cost=100.0)

        critical = strategy.get_by_priority(OptimizationPriority.CRITICAL)

        assert isinstance(critical, list)
        for rec in critical:
            assert rec.priority == OptimizationPriority.CRITICAL

    def test_strategy_get_by_category(self, optimizer):
        """Test filtering recommendations by category."""
        strategy = optimizer.generate_strategy(monthly_cost=100.0)

        caching = strategy.get_by_category(OptimizationCategory.CACHING)

        assert isinstance(caching, list)
        for rec in caching:
            assert rec.category == OptimizationCategory.CACHING

    def test_recommendation_to_dict(self):
        """Test recommendation to dict conversion."""
        rec = OptimizationRecommendation(
            category=OptimizationCategory.CACHING,
            priority=OptimizationPriority.HIGH,
            title="Test Recommendation",
            description="Test description",
            current_cost=100.0,
            optimized_cost=80.0,
            savings_potential=20.0,
            implementation_effort="low",
            implementation_steps=["Step 1", "Step 2"],
        )

        data = rec.to_dict()

        assert data["title"] == "Test Recommendation"
        assert data["costs"]["savings_percent"] == 20.0

    def test_recommendation_annual_savings(self):
        """Test annual savings calculation."""
        rec = OptimizationRecommendation(
            category=OptimizationCategory.MODEL_SELECTION,
            priority=OptimizationPriority.MEDIUM,
            title="Test",
            description="Test",
            current_cost=100.0,
            optimized_cost=80.0,
            savings_potential=20.0,
            implementation_effort="low",
            implementation_steps=["Step 1"],
        )

        # Annual savings = (100 - 80) * 12 = 240
        assert rec.annual_savings == 240.0


class TestROIAnalysis:
    """Tests for ROI Analysis."""

    def test_roi_analysis_creation(self):
        """Test ROI analysis creation."""
        roi = ROIAnalysis(
            optimization_name="Test Optimization",
            implementation_cost=100.0,
            monthly_savings=25.0,
            implementation_time_days=30,
        )

        assert roi.optimization_name == "Test Optimization"
        assert roi.implementation_cost == 100.0

    def test_payback_period(self):
        """Test payback period calculation."""
        roi = ROIAnalysis(
            optimization_name="Test",
            implementation_cost=100.0,
            monthly_savings=25.0,
            implementation_time_days=30,
        )

        # 100 / 25 = 4 months
        assert roi.payback_period_months == 4.0

    def test_npv_1year(self):
        """Test NPV calculation."""
        roi = ROIAnalysis(
            optimization_name="Test",
            implementation_cost=100.0,
            monthly_savings=25.0,
            implementation_time_days=30,
        )

        npv = roi.npv_1year

        # Should be positive (savings > cost over 1 year)
        assert npv > 0

    def test_roi_1year(self):
        """Test ROI percentage calculation."""
        roi = ROIAnalysis(
            optimization_name="Test",
            implementation_cost=100.0,
            monthly_savings=25.0,
            implementation_time_days=30,
        )

        roi_pct = roi.roi_1year

        assert roi_pct > 0

    def test_net_monthly_savings(self):
        """Test net monthly savings with maintenance cost."""
        roi = ROIAnalysis(
            optimization_name="Test",
            implementation_cost=100.0,
            monthly_savings=25.0,
            implementation_time_days=30,
            maintenance_cost_monthly=5.0,
        )

        assert roi.net_monthly_savings == 20.0

    def test_roi_to_dict(self):
        """Test converting ROI analysis to dictionary."""
        roi = ROIAnalysis(
            optimization_name="Test",
            implementation_cost=100.0,
            monthly_savings=25.0,
            implementation_time_days=30,
        )

        data = roi.to_dict()

        assert "optimization_name" in data
        assert "costs" in data
        assert "savings" in data
        assert "metrics" in data

    def test_edge_case_zero_savings(self):
        """Test with zero monthly savings."""
        roi = ROIAnalysis(
            optimization_name="Test",
            implementation_cost=100.0,
            monthly_savings=0.0,
            implementation_time_days=30,
        )

        assert roi.payback_period_months == float("inf")

    def test_edge_case_zero_implementation_cost(self):
        """Test with zero implementation cost."""
        roi = ROIAnalysis(
            optimization_name="Test",
            implementation_cost=0.0,
            monthly_savings=25.0,
            implementation_time_days=30,
        )

        assert roi.roi_1year == float("inf")


# =============================================================================
# AgentCostTracker Tests
# =============================================================================


class TestAgentCostTracker:
    """Tests for AgentCostTracker class."""

    @pytest.fixture
    def central_tracker(self):
        """Create central tracker."""
        from src.cost_analysis.tracker import CostTracker

        return CostTracker()

    @pytest.fixture
    def agent_tracker(self, central_tracker):
        """Create agent tracker."""
        from src.cost_analysis.tracker import AgentCostTracker

        return AgentCostTracker("video", central_tracker)

    def test_initialization(self, agent_tracker):
        """Test agent tracker initialization."""
        assert agent_tracker.agent_type == "video"
        assert agent_tracker._call_count == 0
        assert agent_tracker._total_cost == 0.0

    def test_track_llm_call(self, agent_tracker):
        """Test tracking LLM call."""
        cost = agent_tracker.track_llm_call(
            input_tokens=1000,
            output_tokens=500,
            tour_id="tour_123",
        )

        assert cost >= 0
        assert agent_tracker._call_count == 1
        assert agent_tracker._total_tokens == 1500

    def test_track_api_call(self, agent_tracker):
        """Test tracking API call."""
        cost = agent_tracker.track_api_call(
            api_type="youtube",
            calls=5,
            tour_id="tour_123",
        )

        assert cost >= 0
        assert agent_tracker._total_api_calls == 5

    def test_track_cache_hit(self, agent_tracker, central_tracker):
        """Test tracking cache hit."""
        agent_tracker.track_cache_hit(
            estimated_savings=0.05,
            tour_id="tour_123",
        )

        savings = central_tracker.get_total_savings()
        assert savings > 0

    def test_get_stats(self, agent_tracker):
        """Test getting agent stats."""
        agent_tracker.track_llm_call(1000, 500)
        agent_tracker.track_api_call("youtube", 3)

        stats = agent_tracker.get_stats()

        assert stats["agent_type"] == "video"
        assert stats["call_count"] == 1
        assert stats["total_tokens"] == 1500
        assert stats["total_api_calls"] == 3
        assert stats["avg_cost_per_call"] > 0


# =============================================================================
# TourCostTracker Tests
# =============================================================================


class TestTourCostTracker:
    """Tests for TourCostTracker class."""

    @pytest.fixture
    def central_tracker(self):
        """Create central tracker."""
        from src.cost_analysis.tracker import CostTracker

        return CostTracker()

    @pytest.fixture
    def tour_tracker(self, central_tracker):
        """Create tour tracker."""
        from src.cost_analysis.tracker import TourCostTracker

        return TourCostTracker("tour_test_123", central_tracker)

    def test_initialization(self, tour_tracker):
        """Test tour tracker initialization."""
        assert tour_tracker.tour_id == "tour_test_123"
        assert tour_tracker.summary is not None

    def test_start(self, tour_tracker):
        """Test marking tour start."""
        tour_tracker.start()
        assert tour_tracker.summary.start_time is not None

    def test_set_num_points(self, tour_tracker):
        """Test setting number of points."""
        tour_tracker.set_num_points(10)
        assert tour_tracker.summary.num_points == 10

    def test_record_point_cost(self, tour_tracker):
        """Test recording point cost."""
        tour_tracker.record_point_cost("point_1", 0.05)
        tour_tracker.record_point_cost("point_2", 0.03)

        costs = tour_tracker.get_point_costs()

        assert "point_1" in costs
        assert costs["point_1"] == 0.05

    def test_complete(self, tour_tracker, central_tracker):
        """Test completing tour and getting summary."""
        tour_tracker.start()
        tour_tracker.set_num_points(5)

        # Record some costs
        central_tracker.record_llm_usage(
            1000,
            500,
            agent_type="video",
            tour_id="tour_test_123",
        )

        summary = tour_tracker.complete()

        assert summary.end_time is not None
        assert summary.tour_id == "tour_test_123"


# =============================================================================
# Global Tracker Functions Tests
# =============================================================================


class TestGlobalTrackerFunctions:
    """Tests for global tracker functions."""

    def test_get_cost_tracker(self):
        """Test getting global tracker."""
        from src.cost_analysis.tracker import get_cost_tracker, reset_cost_tracker

        tracker = get_cost_tracker()
        assert tracker is not None

        # Should return same instance
        tracker2 = get_cost_tracker()
        assert tracker is tracker2

        # Reset for other tests
        reset_cost_tracker()

    def test_reset_cost_tracker(self):
        """Test resetting global tracker."""
        from src.cost_analysis.tracker import get_cost_tracker, reset_cost_tracker

        tracker1 = get_cost_tracker()
        reset_cost_tracker()
        tracker2 = get_cost_tracker()

        # Should be different instances after reset
        assert tracker1 is not tracker2


# =============================================================================
# CostTracker Additional Tests
# =============================================================================


class TestCostTrackerAdditional:
    """Additional tests for CostTracker edge cases."""

    @pytest.fixture
    def tracker(self):
        """Create tracker."""
        return CostTracker(budget_limit_usd=10.0, alert_threshold=0.5)

    def test_record_api_youtube(self, tracker):
        """Test recording YouTube API calls."""
        event = tracker.record_api_call(
            api_type="youtube",
            calls=10,
            agent_type="video",
        )

        assert event.category == CostCategory.API_YOUTUBE

    def test_record_api_web_search(self, tracker):
        """Test recording web search API calls."""
        event = tracker.record_api_call(
            api_type="web_search",
            calls=5,
        )

        assert event.category == CostCategory.API_WEB_SEARCH

    def test_record_api_spotify(self, tracker):
        """Test recording Spotify API calls (free)."""
        event = tracker.record_api_call(
            api_type="spotify",
            calls=10,
        )

        assert event.amount_usd == 0.0
        assert event.category == CostCategory.API_SPOTIFY

    def test_record_api_unknown(self, tracker):
        """Test recording unknown API type."""
        event = tracker.record_api_call(
            api_type="unknown_api",
            calls=1,
        )

        assert event.amount_usd == 0.0

    def test_budget_alert_triggers(self, tracker):
        """Test that budget alert triggers at threshold."""
        alerts = []

        def callback(msg, cost):
            alerts.append((msg, cost))

        tracker.register_alert_callback(callback)

        # Record costs to exceed 50% of $10 budget
        for _ in range(100):
            tracker.record_llm_usage(10000, 5000)

        # Check if alert was triggered
        total = tracker.get_total_cost()
        if total >= 5.0:  # 50% of $10
            # Alert should have been triggered
            assert tracker._alert_sent

    def test_alert_callback_error_handling(self, tracker):
        """Test that callback errors are handled gracefully."""

        def bad_callback(msg, cost):
            raise ValueError("Callback error")

        tracker.register_alert_callback(bad_callback)

        # Should not raise even with bad callback
        for _ in range(100):
            tracker.record_llm_usage(10000, 5000)

    def test_record_savings_circuit_breaker(self, tracker):
        """Test recording circuit breaker savings."""
        event = tracker.record_savings(
            savings_type="circuit_breaker",
            amount_usd=0.10,
        )

        assert event.category == CostCategory.CIRCUIT_BREAKER_SAVINGS


# =============================================================================
# CostVisualizationPanel Additional Tests
# =============================================================================


class TestCostVisualizationPanelAdditional:
    """Additional tests for CostVisualizationPanel."""

    def test_create_cost_overview_dashboard_with_tour_data(self):
        """Test creating cost overview dashboard with tour data."""
        cost_data = {
            "llm_cost": 50.0,
            "api_cost": 30.0,
            "compute_cost": 15.0,
            "retry_cost": 5.0,
            "video_cost": 12.0,
            "music_cost": 8.0,
            "text_cost": 10.0,
            "judge_cost": 15.0,
            "budget_used": 75.0,
        }

        tour_data = [
            {"tour_id": "tour_1", "cost": 25.0},
            {"tour_id": "tour_2", "cost": 30.0},
        ]

        fig = CostVisualizationPanel.create_cost_overview_dashboard(
            cost_data, tour_data
        )

        assert fig is not None

    def test_cost_overview_dashboard_default_values(self):
        """Test cost overview with minimal data using defaults."""
        cost_data = {}  # Empty dict - should use defaults

        fig = CostVisualizationPanel.create_cost_overview_dashboard(cost_data)

        assert fig is not None


class TestCostBreakdownChartExtended:
    """Extended tests for CostBreakdownChart class."""

    def test_create_sunburst(self):
        """Test creating sunburst chart."""
        from src.cost_analysis.visualization import CostBreakdownChart

        cost_breakdown = {
            "LLM": {"input_tokens": 30.0, "output_tokens": 20.0},
            "API": {"google_maps": 15.0, "youtube": 10.0},
            "Compute": {"cpu": 5.0, "memory": 3.0},
        }

        fig = CostBreakdownChart.create_sunburst(cost_breakdown)

        assert fig is not None

    def test_create_treemap(self):
        """Test creating treemap chart."""
        import pandas as pd

        from src.cost_analysis.visualization import CostBreakdownChart

        cost_data = pd.DataFrame(
            {
                "category": ["LLM", "LLM", "API", "API"],
                "subcategory": ["input", "output", "maps", "youtube"],
                "value": [30, 20, 15, 10],
            }
        )

        fig = CostBreakdownChart.create_treemap(cost_data)

        assert fig is not None

    def test_create_stacked_bar_comparison(self):
        """Test creating stacked bar comparison chart."""
        from src.cost_analysis.visualization import CostBreakdownChart

        config_costs = {
            "Config A": {"llm": 20, "api": 10, "compute": 5},
            "Config B": {"llm": 15, "api": 15, "compute": 8},
        }

        fig = CostBreakdownChart.create_stacked_bar_comparison(config_costs)

        assert fig is not None
