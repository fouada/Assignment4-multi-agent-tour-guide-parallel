"""
NPS (Net Promoter Score) and User Satisfaction Metrics.

MIT-Level User Satisfaction Tracking:
- NPS score collection and calculation
- User engagement metrics
- Satisfaction trend analysis
- Real-time feedback processing

Target Metrics:
- NPS > 50 (World-class)
- User Engagement > 70%
- Content Relevance > 4.0/5.0
"""

import statistics
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class NPSCategory(Enum):
    """NPS respondent categories."""

    DETRACTOR = "detractor"  # Score 0-6
    PASSIVE = "passive"  # Score 7-8
    PROMOTER = "promoter"  # Score 9-10


@dataclass
class FeedbackEntry:
    """Single user feedback entry."""

    user_id: str
    tour_id: str
    nps_score: int  # 0-10
    content_rating: float  # 1-5
    engagement_time_seconds: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    feedback_text: str | None = None
    agent_type_selected: str | None = None

    @property
    def nps_category(self) -> NPSCategory:
        """Classify NPS score into category."""
        if self.nps_score <= 6:
            return NPSCategory.DETRACTOR
        elif self.nps_score <= 8:
            return NPSCategory.PASSIVE
        else:
            return NPSCategory.PROMOTER


@dataclass
class NPSReport:
    """NPS calculation report."""

    nps_score: float
    promoters_count: int
    passives_count: int
    detractors_count: int
    total_responses: int
    promoters_percentage: float
    passives_percentage: float
    detractors_percentage: float
    period_start: datetime
    period_end: datetime

    @property
    def meets_target(self) -> bool:
        """Check if NPS meets target (> 50)."""
        return self.nps_score > 50


@dataclass
class EngagementMetrics:
    """User engagement metrics."""

    average_session_duration: float
    content_completion_rate: float
    return_user_rate: float
    points_per_tour_average: float
    content_interaction_rate: float


class UserSatisfactionCollector:
    """
    Collects and calculates user satisfaction metrics.

    Implements:
    - NPS (Net Promoter Score) calculation
    - User engagement tracking
    - Content relevance scoring
    - Trend analysis
    """

    # Target thresholds
    NPS_TARGET = 50
    ENGAGEMENT_TARGET = 0.70
    CONTENT_RATING_TARGET = 4.0

    def __init__(self, retention_days: int = 90):
        """
        Initialize the satisfaction collector.

        Args:
            retention_days: How many days to retain feedback data
        """
        self._feedback: list[FeedbackEntry] = []
        self._lock = threading.RLock()
        self._retention_days = retention_days
        self._user_sessions: dict[str, list[float]] = defaultdict(list)

    def collect_feedback(
        self,
        user_id: str,
        tour_id: str,
        nps_score: int,
        content_rating: float = 4.0,
        engagement_time_seconds: float = 0.0,
        feedback_text: str | None = None,
        agent_type_selected: str | None = None,
    ) -> FeedbackEntry:
        """
        Collect user feedback for a tour.

        Args:
            user_id: Unique user identifier
            tour_id: Tour session identifier
            nps_score: NPS score (0-10)
            content_rating: Content quality rating (1-5)
            engagement_time_seconds: Time spent engaging with content
            feedback_text: Optional text feedback
            agent_type_selected: Which agent's content was selected

        Returns:
            The recorded feedback entry

        Raises:
            ValueError: If scores are out of valid range
        """
        # Validate inputs
        if not 0 <= nps_score <= 10:
            raise ValueError(f"NPS score must be 0-10, got {nps_score}")
        if not 1 <= content_rating <= 5:
            raise ValueError(f"Content rating must be 1-5, got {content_rating}")

        entry = FeedbackEntry(
            user_id=user_id,
            tour_id=tour_id,
            nps_score=nps_score,
            content_rating=content_rating,
            engagement_time_seconds=engagement_time_seconds,
            feedback_text=feedback_text,
            agent_type_selected=agent_type_selected,
        )

        with self._lock:
            self._feedback.append(entry)
            self._user_sessions[user_id].append(engagement_time_seconds)
            self._cleanup_old_entries()

        return entry

    def calculate_nps(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> NPSReport:
        """
        Calculate NPS for a given time period.

        NPS = % Promoters - % Detractors

        Args:
            start_date: Start of period (default: 30 days ago)
            end_date: End of period (default: now)

        Returns:
            NPSReport with detailed breakdown
        """
        end_date = end_date or datetime.utcnow()
        start_date = start_date or (end_date - timedelta(days=30))

        with self._lock:
            entries = [
                e for e in self._feedback if start_date <= e.timestamp <= end_date
            ]

        if not entries:
            return NPSReport(
                nps_score=0.0,
                promoters_count=0,
                passives_count=0,
                detractors_count=0,
                total_responses=0,
                promoters_percentage=0.0,
                passives_percentage=0.0,
                detractors_percentage=0.0,
                period_start=start_date,
                period_end=end_date,
            )

        # Count categories
        promoters = sum(1 for e in entries if e.nps_category == NPSCategory.PROMOTER)
        passives = sum(1 for e in entries if e.nps_category == NPSCategory.PASSIVE)
        detractors = sum(1 for e in entries if e.nps_category == NPSCategory.DETRACTOR)
        total = len(entries)

        # Calculate percentages
        promoters_pct = (promoters / total) * 100
        passives_pct = (passives / total) * 100
        detractors_pct = (detractors / total) * 100

        # NPS = % Promoters - % Detractors
        nps = promoters_pct - detractors_pct

        return NPSReport(
            nps_score=round(nps, 2),
            promoters_count=promoters,
            passives_count=passives,
            detractors_count=detractors,
            total_responses=total,
            promoters_percentage=round(promoters_pct, 2),
            passives_percentage=round(passives_pct, 2),
            detractors_percentage=round(detractors_pct, 2),
            period_start=start_date,
            period_end=end_date,
        )

    def get_engagement_metrics(self) -> EngagementMetrics:
        """
        Calculate user engagement metrics.

        Returns:
            EngagementMetrics with engagement statistics
        """
        with self._lock:
            if not self._feedback:
                return EngagementMetrics(
                    average_session_duration=0.0,
                    content_completion_rate=0.0,
                    return_user_rate=0.0,
                    points_per_tour_average=0.0,
                    content_interaction_rate=0.0,
                )

            # Average session duration
            durations = [
                e.engagement_time_seconds
                for e in self._feedback
                if e.engagement_time_seconds > 0
            ]
            avg_duration = statistics.mean(durations) if durations else 0.0

            # Return user rate
            user_tour_counts: dict[str, int] = defaultdict(int)
            for entry in self._feedback:
                user_tour_counts[entry.user_id] += 1
            return_users = sum(1 for count in user_tour_counts.values() if count > 1)
            return_rate = (
                return_users / len(user_tour_counts) if user_tour_counts else 0.0
            )

            # Content interaction (engagement > 30 seconds)
            interacted = sum(
                1 for e in self._feedback if e.engagement_time_seconds > 30
            )
            interaction_rate = (
                interacted / len(self._feedback) if self._feedback else 0.0
            )

            # Content completion (engagement > 120 seconds)
            completed = sum(
                1 for e in self._feedback if e.engagement_time_seconds > 120
            )
            completion_rate = completed / len(self._feedback) if self._feedback else 0.0

        return EngagementMetrics(
            average_session_duration=round(avg_duration, 2),
            content_completion_rate=round(completion_rate, 4),
            return_user_rate=round(return_rate, 4),
            points_per_tour_average=0.0,  # Would need tour data
            content_interaction_rate=round(interaction_rate, 4),
        )

    def get_content_rating_average(
        self,
        agent_type: str | None = None,
    ) -> float:
        """
        Get average content rating, optionally filtered by agent type.

        Args:
            agent_type: Filter by specific agent (video, music, text)

        Returns:
            Average content rating (1-5 scale)
        """
        with self._lock:
            entries = self._feedback
            if agent_type:
                entries = [e for e in entries if e.agent_type_selected == agent_type]

            if not entries:
                return 0.0

            return round(statistics.mean(e.content_rating for e in entries), 2)

    def get_nps_trend(
        self,
        periods: int = 6,
        period_days: int = 7,
    ) -> list[tuple[datetime, float]]:
        """
        Get NPS trend over multiple periods.

        Args:
            periods: Number of periods to analyze
            period_days: Days per period

        Returns:
            List of (period_end_date, nps_score) tuples
        """
        end = datetime.utcnow()
        trend = []

        for i in range(periods):
            period_end = end - timedelta(days=i * period_days)
            period_start = period_end - timedelta(days=period_days)
            report = self.calculate_nps(period_start, period_end)
            trend.append((period_end, report.nps_score))

        return list(reversed(trend))

    def get_satisfaction_summary(self) -> dict:
        """
        Get comprehensive satisfaction summary.

        Returns:
            Dictionary with all satisfaction metrics and status
        """
        nps_report = self.calculate_nps()
        engagement = self.get_engagement_metrics()
        content_rating = self.get_content_rating_average()

        return {
            "nps": {
                "score": nps_report.nps_score,
                "target": self.NPS_TARGET,
                "meets_target": nps_report.meets_target,
                "total_responses": nps_report.total_responses,
                "breakdown": {
                    "promoters": nps_report.promoters_percentage,
                    "passives": nps_report.passives_percentage,
                    "detractors": nps_report.detractors_percentage,
                },
            },
            "engagement": {
                "average_session_seconds": engagement.average_session_duration,
                "completion_rate": engagement.content_completion_rate,
                "return_user_rate": engagement.return_user_rate,
                "interaction_rate": engagement.content_interaction_rate,
                "target": self.ENGAGEMENT_TARGET,
                "meets_target": engagement.content_interaction_rate
                >= self.ENGAGEMENT_TARGET,
            },
            "content_quality": {
                "average_rating": content_rating,
                "target": self.CONTENT_RATING_TARGET,
                "meets_target": content_rating >= self.CONTENT_RATING_TARGET,
                "ratings_by_agent": {
                    "video": self.get_content_rating_average("video"),
                    "music": self.get_content_rating_average("music"),
                    "text": self.get_content_rating_average("text"),
                },
            },
            "overall_status": self._get_overall_status(
                nps_report, engagement, content_rating
            ),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _get_overall_status(
        self,
        nps: NPSReport,
        engagement: EngagementMetrics,
        content_rating: float,
    ) -> str:
        """Determine overall satisfaction status."""
        checks_passed = sum(
            [
                nps.meets_target,
                engagement.content_interaction_rate >= self.ENGAGEMENT_TARGET,
                content_rating >= self.CONTENT_RATING_TARGET,
            ]
        )

        if checks_passed == 3:
            return "excellent"
        elif checks_passed == 2:
            return "good"
        elif checks_passed == 1:
            return "needs_improvement"
        else:
            return "critical"

    def _cleanup_old_entries(self) -> None:
        """Remove entries older than retention period."""
        cutoff = datetime.utcnow() - timedelta(days=self._retention_days)
        self._feedback = [e for e in self._feedback if e.timestamp > cutoff]

    def export_prometheus_metrics(self) -> str:
        """
        Export metrics in Prometheus format.

        Returns:
            Prometheus-formatted metrics string
        """
        summary = self.get_satisfaction_summary()

        lines = [
            "# HELP tour_guide_nps_score Net Promoter Score",
            "# TYPE tour_guide_nps_score gauge",
            f"tour_guide_nps_score {summary['nps']['score']}",
            "",
            "# HELP tour_guide_nps_responses_total Total NPS responses",
            "# TYPE tour_guide_nps_responses_total counter",
            f"tour_guide_nps_responses_total {summary['nps']['total_responses']}",
            "",
            "# HELP tour_guide_content_rating_average Average content rating",
            "# TYPE tour_guide_content_rating_average gauge",
            f"tour_guide_content_rating_average {summary['content_quality']['average_rating']}",
            "",
            "# HELP tour_guide_engagement_rate User engagement rate",
            "# TYPE tour_guide_engagement_rate gauge",
            f"tour_guide_engagement_rate {summary['engagement']['interaction_rate']}",
        ]

        return "\n".join(lines)


# Global collector instance
_collector: UserSatisfactionCollector | None = None


def get_satisfaction_collector() -> UserSatisfactionCollector:
    """Get the global satisfaction collector instance."""
    global _collector
    if _collector is None:
        _collector = UserSatisfactionCollector()
    return _collector


def collect_nps_score(
    user_id: str, tour_id: str, score: int, **kwargs
) -> FeedbackEntry:
    """
    Convenience function to collect NPS score.

    Args:
        user_id: User identifier
        tour_id: Tour identifier
        score: NPS score (0-10)
        **kwargs: Additional feedback fields

    Returns:
        Recorded feedback entry
    """
    collector = get_satisfaction_collector()
    return collector.collect_feedback(
        user_id=user_id, tour_id=tour_id, nps_score=score, **kwargs
    )


def get_nps_score() -> float:
    """Get current NPS score."""
    collector = get_satisfaction_collector()
    report = collector.calculate_nps()
    return report.nps_score
