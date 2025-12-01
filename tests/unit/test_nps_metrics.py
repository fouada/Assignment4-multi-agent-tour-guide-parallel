"""
Tests for NPS (Net Promoter Score) and User Satisfaction Metrics.

MIT-Level Test Coverage for:
- NPS score calculation
- User engagement tracking
- Content rating aggregation
- Trend analysis
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from src.core.observability.nps_metrics import (
    UserSatisfactionCollector,
    FeedbackEntry,
    NPSReport,
    NPSCategory,
    EngagementMetrics,
    get_satisfaction_collector,
    collect_nps_score,
    get_nps_score,
)


class TestFeedbackEntry:
    """Tests for FeedbackEntry data class."""
    
    def test_feedback_entry_creation(self):
        """Test creating a feedback entry."""
        entry = FeedbackEntry(
            user_id="user_123",
            tour_id="tour_456",
            nps_score=9,
            content_rating=4.5,
            engagement_time_seconds=120.0,
        )
        
        assert entry.user_id == "user_123"
        assert entry.tour_id == "tour_456"
        assert entry.nps_score == 9
        assert entry.content_rating == 4.5
        assert entry.engagement_time_seconds == 120.0
    
    def test_nps_category_promoter(self):
        """Test promoter classification (9-10)."""
        entry = FeedbackEntry(
            user_id="u1",
            tour_id="t1",
            nps_score=9,
            content_rating=4.0,
            engagement_time_seconds=60.0,
        )
        assert entry.nps_category == NPSCategory.PROMOTER
        
        entry.nps_score = 10
        assert FeedbackEntry(
            user_id="u1", tour_id="t1", nps_score=10,
            content_rating=4.0, engagement_time_seconds=60.0
        ).nps_category == NPSCategory.PROMOTER
    
    def test_nps_category_passive(self):
        """Test passive classification (7-8)."""
        for score in [7, 8]:
            entry = FeedbackEntry(
                user_id="u1",
                tour_id="t1",
                nps_score=score,
                content_rating=4.0,
                engagement_time_seconds=60.0,
            )
            assert entry.nps_category == NPSCategory.PASSIVE
    
    def test_nps_category_detractor(self):
        """Test detractor classification (0-6)."""
        for score in [0, 1, 2, 3, 4, 5, 6]:
            entry = FeedbackEntry(
                user_id="u1",
                tour_id="t1",
                nps_score=score,
                content_rating=4.0,
                engagement_time_seconds=60.0,
            )
            assert entry.nps_category == NPSCategory.DETRACTOR


class TestUserSatisfactionCollector:
    """Tests for UserSatisfactionCollector."""
    
    @pytest.fixture
    def collector(self):
        """Create fresh collector for each test."""
        return UserSatisfactionCollector()
    
    def test_collect_feedback_valid(self, collector):
        """Test collecting valid feedback."""
        entry = collector.collect_feedback(
            user_id="user_1",
            tour_id="tour_1",
            nps_score=8,
            content_rating=4.0,
            engagement_time_seconds=90.0,
        )
        
        assert entry.user_id == "user_1"
        assert entry.nps_score == 8
    
    def test_collect_feedback_invalid_nps(self, collector):
        """Test rejection of invalid NPS score."""
        with pytest.raises(ValueError, match="NPS score must be 0-10"):
            collector.collect_feedback(
                user_id="u1",
                tour_id="t1",
                nps_score=11,  # Invalid
                content_rating=4.0,
                engagement_time_seconds=60.0,
            )
    
    def test_collect_feedback_invalid_rating(self, collector):
        """Test rejection of invalid content rating."""
        with pytest.raises(ValueError, match="Content rating must be 1-5"):
            collector.collect_feedback(
                user_id="u1",
                tour_id="t1",
                nps_score=8,
                content_rating=6.0,  # Invalid
                engagement_time_seconds=60.0,
            )
    
    def test_calculate_nps_no_data(self, collector):
        """Test NPS calculation with no data."""
        report = collector.calculate_nps()
        
        assert report.nps_score == 0.0
        assert report.total_responses == 0
    
    def test_calculate_nps_all_promoters(self, collector):
        """Test NPS with all promoters = 100."""
        for i in range(10):
            collector.collect_feedback(
                user_id=f"user_{i}",
                tour_id=f"tour_{i}",
                nps_score=10,  # Promoter
                content_rating=5.0,
                engagement_time_seconds=120.0,
            )
        
        report = collector.calculate_nps()
        
        assert report.nps_score == 100.0
        assert report.promoters_count == 10
        assert report.detractors_count == 0
        assert report.meets_target is True
    
    def test_calculate_nps_all_detractors(self, collector):
        """Test NPS with all detractors = -100."""
        for i in range(10):
            collector.collect_feedback(
                user_id=f"user_{i}",
                tour_id=f"tour_{i}",
                nps_score=3,  # Detractor
                content_rating=2.0,
                engagement_time_seconds=30.0,
            )
        
        report = collector.calculate_nps()
        
        assert report.nps_score == -100.0
        assert report.detractors_count == 10
        assert report.promoters_count == 0
        assert report.meets_target is False
    
    def test_calculate_nps_mixed(self, collector):
        """Test NPS with mixed responses."""
        # 5 promoters (50%)
        for i in range(5):
            collector.collect_feedback(
                user_id=f"promoter_{i}",
                tour_id=f"tour_{i}",
                nps_score=9,
                content_rating=5.0,
                engagement_time_seconds=120.0,
            )
        
        # 3 passives (30%)
        for i in range(3):
            collector.collect_feedback(
                user_id=f"passive_{i}",
                tour_id=f"tour_{i+5}",
                nps_score=7,
                content_rating=4.0,
                engagement_time_seconds=90.0,
            )
        
        # 2 detractors (20%)
        for i in range(2):
            collector.collect_feedback(
                user_id=f"detractor_{i}",
                tour_id=f"tour_{i+8}",
                nps_score=4,
                content_rating=2.0,
                engagement_time_seconds=30.0,
            )
        
        report = collector.calculate_nps()
        
        # NPS = 50% - 20% = 30
        assert report.nps_score == 30.0
        assert report.total_responses == 10
        assert report.promoters_count == 5
        assert report.passives_count == 3
        assert report.detractors_count == 2
    
    def test_calculate_nps_meets_target(self, collector):
        """Test NPS target threshold (> 50)."""
        # Create scenario with NPS > 50
        # 7 promoters, 1 passive, 2 detractors = 70% - 20% = 50
        for i in range(8):
            collector.collect_feedback(
                user_id=f"p_{i}",
                tour_id=f"t_{i}",
                nps_score=10,  # Promoter
                content_rating=5.0,
                engagement_time_seconds=120.0,
            )
        for i in range(2):
            collector.collect_feedback(
                user_id=f"d_{i}",
                tour_id=f"t_{i+8}",
                nps_score=3,  # Detractor
                content_rating=2.0,
                engagement_time_seconds=30.0,
            )
        
        report = collector.calculate_nps()
        
        # 80% promoters, 20% detractors = 60
        assert report.nps_score == 60.0
        assert report.meets_target is True
    
    def test_get_engagement_metrics_empty(self, collector):
        """Test engagement metrics with no data."""
        metrics = collector.get_engagement_metrics()
        
        assert metrics.average_session_duration == 0.0
        assert metrics.content_completion_rate == 0.0
    
    def test_get_engagement_metrics_with_data(self, collector):
        """Test engagement metrics calculation."""
        # Add feedback with varying engagement
        for i, duration in enumerate([30, 60, 120, 180, 300]):
            collector.collect_feedback(
                user_id=f"user_{i}",
                tour_id=f"tour_{i}",
                nps_score=8,
                content_rating=4.0,
                engagement_time_seconds=duration,
            )
        
        metrics = collector.get_engagement_metrics()
        
        # Average of [30, 60, 120, 180, 300] = 138
        assert metrics.average_session_duration == 138.0
        # Completion rate: 2/5 (strictly > 120 seconds: 180, 300)
        assert metrics.content_completion_rate == 0.4
        # Interaction rate calculated by implementation
        assert metrics.content_interaction_rate >= 0.0
    
    def test_get_content_rating_average(self, collector):
        """Test content rating average calculation."""
        ratings = [3.0, 4.0, 4.5, 5.0, 3.5]
        for i, rating in enumerate(ratings):
            collector.collect_feedback(
                user_id=f"user_{i}",
                tour_id=f"tour_{i}",
                nps_score=8,
                content_rating=rating,
                engagement_time_seconds=60.0,
            )
        
        avg = collector.get_content_rating_average()
        
        # Average of [3.0, 4.0, 4.5, 5.0, 3.5] = 4.0
        assert avg == 4.0
    
    def test_get_content_rating_by_agent(self, collector):
        """Test content rating filtered by agent type."""
        # Video ratings
        for i in range(3):
            collector.collect_feedback(
                user_id=f"video_user_{i}",
                tour_id=f"video_tour_{i}",
                nps_score=9,
                content_rating=5.0,  # High ratings for video
                engagement_time_seconds=120.0,
                agent_type_selected="video",
            )
        
        # Text ratings
        for i in range(3):
            collector.collect_feedback(
                user_id=f"text_user_{i}",
                tour_id=f"text_tour_{i}",
                nps_score=7,
                content_rating=3.0,  # Lower ratings for text
                engagement_time_seconds=60.0,
                agent_type_selected="text",
            )
        
        video_avg = collector.get_content_rating_average("video")
        text_avg = collector.get_content_rating_average("text")
        
        assert video_avg == 5.0
        assert text_avg == 3.0
    
    def test_get_satisfaction_summary(self, collector):
        """Test comprehensive satisfaction summary."""
        # Add some feedback
        for i in range(5):
            collector.collect_feedback(
                user_id=f"user_{i}",
                tour_id=f"tour_{i}",
                nps_score=9,
                content_rating=4.5,
                engagement_time_seconds=150.0,
            )
        
        summary = collector.get_satisfaction_summary()
        
        assert "nps" in summary
        assert "engagement" in summary
        assert "content_quality" in summary
        assert "overall_status" in summary
        assert summary["nps"]["score"] == 100.0
    
    def test_get_nps_trend(self, collector):
        """Test NPS trend over periods."""
        # Add feedback for different periods (mock timestamps)
        now = datetime.utcnow()
        
        # Would need to mock timestamps for proper trend testing
        # For now, just verify the method returns correctly
        trend = collector.get_nps_trend(periods=4, period_days=7)
        
        assert isinstance(trend, list)
        assert len(trend) <= 4
    
    def test_export_prometheus_metrics(self, collector):
        """Test Prometheus metrics export format."""
        collector.collect_feedback(
            user_id="u1",
            tour_id="t1",
            nps_score=9,
            content_rating=4.5,
            engagement_time_seconds=120.0,
        )
        
        metrics = collector.export_prometheus_metrics()
        
        assert "tour_guide_nps_score" in metrics
        assert "tour_guide_content_rating_average" in metrics
        assert "tour_guide_engagement_rate" in metrics


class TestGlobalFunctions:
    """Tests for module-level convenience functions."""
    
    def test_collect_nps_score(self):
        """Test convenience function for NPS collection."""
        entry = collect_nps_score(
            user_id="global_user",
            tour_id="global_tour",
            score=8,
            content_rating=4.0,
            engagement_time_seconds=90.0,
        )
        
        assert entry.nps_score == 8
    
    def test_get_nps_score(self):
        """Test getting current NPS score."""
        # Collect some feedback first
        collector = get_satisfaction_collector()
        collector.collect_feedback(
            user_id="test_user",
            tour_id="test_tour",
            nps_score=10,
            content_rating=5.0,
            engagement_time_seconds=120.0,
        )
        
        score = get_nps_score()
        
        assert isinstance(score, float)


class TestNPSTargetCompliance:
    """Tests for NPS target compliance (> 50)."""
    
    @pytest.fixture
    def collector(self):
        return UserSatisfactionCollector()
    
    def test_world_class_nps(self, collector):
        """Test achieving world-class NPS (> 70)."""
        # 9 promoters, 1 passive = 90% - 0% = 90
        for i in range(9):
            collector.collect_feedback(
                user_id=f"p_{i}",
                tour_id=f"t_{i}",
                nps_score=10,
                content_rating=5.0,
                engagement_time_seconds=180.0,
            )
        collector.collect_feedback(
            user_id="passive_1",
            tour_id="t_9",
            nps_score=8,
            content_rating=4.0,
            engagement_time_seconds=90.0,
        )
        
        report = collector.calculate_nps()
        
        assert report.nps_score >= 70
        assert report.meets_target is True
    
    def test_target_threshold(self, collector):
        """Test exact target threshold behavior."""
        # NPS = 50 should NOT meet target (> 50 required)
        # 6 promoters (60%), 4 detractors (40%) = 20
        # Need 6 promoters, 0 passives, 1 detractor = 60% - 10% = 50
        for i in range(6):
            collector.collect_feedback(
                user_id=f"p_{i}",
                tour_id=f"t_{i}",
                nps_score=9,
                content_rating=4.5,
                engagement_time_seconds=120.0,
            )
        for i in range(3):
            collector.collect_feedback(
                user_id=f"passive_{i}",
                tour_id=f"t_{i+6}",
                nps_score=7,
                content_rating=3.5,
                engagement_time_seconds=60.0,
            )
        collector.collect_feedback(
            user_id="d_1",
            tour_id="t_9",
            nps_score=3,
            content_rating=2.0,
            engagement_time_seconds=30.0,
        )
        
        report = collector.calculate_nps()
        
        # 60% promoters - 10% detractors = 50
        assert report.nps_score == 50.0
        assert report.meets_target is False  # Must be > 50, not >= 50

