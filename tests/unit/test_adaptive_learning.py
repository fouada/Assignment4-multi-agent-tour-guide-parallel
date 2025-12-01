"""
Tests for Adaptive Learning Framework (Multi-Armed Bandits).

MIT-Level Test Coverage for:
- Thompson Sampling
- UCB (Upper Confidence Bound)
- Contextual Thompson Sampling
- Adaptive Agent Selector
- Bandit Experiments
"""

import pytest

np = pytest.importorskip("numpy", reason="numpy required for research tests")

from src.research.adaptive_learning import (
    UCB,
    AdaptiveAgentSelector,
    AgentType,
    BanditExperiment,
    BanditStatistics,
    Context,
    ContextualThompsonSampling,
    LocationCategory,
    Reward,
    ThompsonSampling,
    demo_adaptive_selection,
)

# =============================================================================
# Context Tests
# =============================================================================


class TestContext:
    """Test Context dataclass and feature extraction."""

    def test_context_creation(self):
        """Test basic context creation."""
        context = Context(
            location_category=LocationCategory.HISTORICAL,
            user_age_group="adult",
            time_of_day="morning",
            trip_purpose="vacation",
        )
        assert context.location_category == LocationCategory.HISTORICAL
        assert context.user_age_group == "adult"

    def test_context_with_previous_selections(self):
        """Test context with selection history."""
        context = Context(
            location_category=LocationCategory.URBAN,
            user_age_group="teen",
            time_of_day="afternoon",
            trip_purpose="education",
            previous_selections=[AgentType.VIDEO, AgentType.MUSIC],
        )
        assert len(context.previous_selections) == 2

    def test_context_to_feature_vector(self):
        """Test feature vector extraction."""
        context = Context(
            location_category=LocationCategory.CULTURAL,
            user_age_group="senior",
            time_of_day="evening",
            trip_purpose="business",
            location_popularity=0.8,
        )
        features = context.to_feature_vector()

        # Should return a numpy array
        assert isinstance(features, np.ndarray)
        assert len(features) > 0

    def test_context_feature_normalization(self):
        """Test that features are reasonably valued."""
        context = Context(
            location_category=LocationCategory.ENTERTAINMENT,
            user_age_group="kid",
            time_of_day="night",
            trip_purpose="vacation",
            location_popularity=0.5,
        )
        features = context.to_feature_vector()

        # All values should be non-negative
        assert np.all(features >= 0)


# =============================================================================
# Reward Tests
# =============================================================================


class TestReward:
    """Test Reward dataclass."""

    def test_reward_creation(self):
        """Test basic reward creation."""
        reward = Reward(value=0.8)
        assert reward.value == 0.8

    def test_reward_bounds(self):
        """Test reward values at boundaries."""
        reward_low = Reward(value=0.0)
        reward_high = Reward(value=1.0)

        assert reward_low.value == 0.0
        assert reward_high.value == 1.0

    def test_composite_reward(self):
        """Test composite reward calculation."""
        reward = Reward(
            value=0.8,
            user_engagement=30.0,
            content_quality_score=7.0,
        )
        composite = reward.composite_reward
        assert 0.0 <= composite <= 1.0


# =============================================================================
# Bandit Statistics Tests
# =============================================================================


class TestBanditStatistics:
    """Test BanditStatistics tracking."""

    def test_statistics_initialization(self):
        """Test initial statistics."""
        stats = BanditStatistics()
        assert stats.total_pulls == 0
        assert stats.total_reward == 0.0
        assert stats.cumulative_regret == 0.0

    def test_record_pull(self):
        """Test recording a pull."""
        stats = BanditStatistics()
        stats.record_pull(AgentType.VIDEO, reward=0.8, optimal_reward=0.9)

        assert stats.total_pulls == 1
        assert stats.total_reward == 0.8
        assert stats.arm_pulls[AgentType.VIDEO] == 1

    def test_multiple_records(self):
        """Test multiple records."""
        stats = BanditStatistics()

        stats.record_pull(AgentType.VIDEO, 0.8, 0.9)
        stats.record_pull(AgentType.MUSIC, 0.6, 0.9)
        stats.record_pull(AgentType.TEXT, 0.7, 0.9)

        assert stats.total_pulls == 3
        assert abs(stats.total_reward - 2.1) < 0.001

    def test_arm_mean_reward(self):
        """Test per-arm mean reward."""
        stats = BanditStatistics()
        stats.record_pull(AgentType.VIDEO, 0.9, 1.0)
        stats.record_pull(AgentType.VIDEO, 0.7, 1.0)

        assert stats.arm_mean_reward(AgentType.VIDEO) == 0.8

    def test_average_reward(self):
        """Test average reward calculation."""
        stats = BanditStatistics()
        stats.record_pull(AgentType.VIDEO, 0.8, 1.0)
        stats.record_pull(AgentType.VIDEO, 0.6, 1.0)

        assert stats.average_reward == 0.7

    def test_regret_bound(self):
        """Test theoretical regret bound."""
        stats = BanditStatistics()
        for _ in range(100):
            stats.record_pull(AgentType.VIDEO, 0.7, 0.8)

        bound = stats.regret_bound()
        assert bound > 0
        assert np.isfinite(bound)


# =============================================================================
# Thompson Sampling Tests
# =============================================================================


class TestThompsonSampling:
    """Test Thompson Sampling algorithm."""

    @pytest.fixture
    def ts(self):
        """Create Thompson Sampling instance."""
        return ThompsonSampling(list(AgentType), seed=42)

    def test_initialization(self, ts):
        """Test TS initializes with prior."""
        assert ts is not None
        assert len(ts.arms) == 3

    def test_select_arm_returns_valid_agent(self, ts):
        """Test arm selection returns valid agent type."""
        arm = ts.select_arm()
        assert arm in AgentType

    def test_select_arm_is_stochastic(self):
        """Test that arm selection is stochastic."""
        ts1 = ThompsonSampling(list(AgentType), seed=42)
        ts2 = ThompsonSampling(list(AgentType), seed=123)

        selections1 = [ts1.select_arm() for _ in range(100)]
        selections2 = [ts2.select_arm() for _ in range(100)]

        # Different seeds should give different selections
        assert selections1 != selections2

    def test_update(self, ts):
        """Test update with reward."""
        arm = ts.select_arm()
        reward = Reward(value=0.8)
        ts.update(arm, reward)

        # After update, should still be able to select
        next_arm = ts.select_arm()
        assert next_arm in AgentType

    def test_statistics(self, ts):
        """Test getting bandit statistics."""
        for _ in range(10):
            arm = ts.select_arm()
            ts.update(arm, Reward(value=0.7))

        assert ts.statistics.total_pulls == 10


# =============================================================================
# UCB Tests
# =============================================================================


class TestUCB:
    """Test UCB algorithm."""

    @pytest.fixture
    def ucb(self):
        """Create UCB instance."""
        return UCB(list(AgentType), seed=42)

    def test_initialization(self, ucb):
        """Test UCB initialization."""
        assert ucb is not None

    def test_initial_exploration(self, ucb):
        """Test UCB explores all arms initially."""
        selected = set()
        for _ in range(10):
            arm = ucb.select_arm()
            selected.add(arm)
            ucb.update(arm, Reward(value=0.5))

        # Should have explored all arms
        assert len(selected) == 3

    def test_select_arm(self, ucb):
        """Test arm selection."""
        arm = ucb.select_arm()
        assert arm in AgentType

    def test_update(self, ucb):
        """Test update."""
        arm = ucb.select_arm()
        ucb.update(arm, Reward(value=0.6))

        # Should still work
        next_arm = ucb.select_arm()
        assert next_arm in AgentType

    def test_regret_analysis(self, ucb):
        """Test comprehensive regret analysis."""
        for _ in range(20):
            arm = ucb.select_arm()
            ucb.update(arm, Reward(value=0.7))

        report = ucb.regret_analysis()
        assert report["algorithm"] == "UCB1"
        assert "theoretical_upper_bound" in report
        assert "arm_statistics" in report
        assert "ucb_index" in report["arm_statistics"][AgentType.VIDEO.value]


# =============================================================================
# Contextual Thompson Sampling Tests
# =============================================================================


class TestContextualThompsonSampling:
    """Test Contextual Thompson Sampling."""

    @pytest.fixture
    def cts(self):
        """Create Contextual TS instance."""
        return ContextualThompsonSampling(list(AgentType), context_dim=22, seed=42)

    def test_initialization(self, cts):
        """Test initialization."""
        assert cts is not None

    def test_select_arm_with_context(self, cts):
        """Test selection with context."""
        context = Context(
            location_category=LocationCategory.HISTORICAL,
            user_age_group="adult",
            time_of_day="morning",
            trip_purpose="vacation",
        )
        arm = cts.select_arm(context)
        assert arm in AgentType

    def test_update_with_context(self, cts):
        """Test update with context."""
        context = Context(
            location_category=LocationCategory.HISTORICAL,
            user_age_group="adult",
            time_of_day="morning",
            trip_purpose="vacation",
        )
        arm = cts.select_arm(context)
        cts.update(arm, Reward(value=0.9), context)

        # Verify statistics update
        assert cts.statistics.total_pulls == 1

    def test_regret_analysis(self, cts):
        """Test regret analysis for contextual bandit."""
        context = Context(
            location_category=LocationCategory.HISTORICAL,
            user_age_group="adult",
            time_of_day="morning",
            trip_purpose="vacation",
        )

        for _ in range(5):
            arm = cts.select_arm(context)
            cts.update(arm, Reward(value=0.8), context)

        report = cts.regret_analysis()
        assert report["algorithm"] == "Contextual Thompson Sampling"
        assert report["context_dimension"] == 22


# =============================================================================
# Adaptive Agent Selector Tests
# =============================================================================


class TestAdaptiveAgentSelector:
    """Test Adaptive Agent Selector."""

    def test_initialization(self):
        """Test initialization with different algorithms."""
        selector = AdaptiveAgentSelector(algorithm="thompson_sampling")
        assert selector is not None

        selector = AdaptiveAgentSelector(algorithm="ucb")
        assert selector is not None

        selector = AdaptiveAgentSelector(algorithm="contextual_ts")
        assert selector is not None

    def test_select_agent(self):
        """Test agent selection."""
        selector = AdaptiveAgentSelector(seed=42)
        agent = selector.select_agent()
        assert agent in AgentType

    def test_record_feedback(self):
        """Test feedback recording."""
        selector = AdaptiveAgentSelector(seed=42)
        agent = selector.select_agent()

        reward = Reward(value=0.8)
        selector.record_feedback(agent, reward)

        # Should still work
        next_agent = selector.select_agent()
        assert next_agent in AgentType

    def test_multiple_selections(self):
        """Test multiple selections and feedback."""
        selector = AdaptiveAgentSelector(seed=42)

        for _ in range(20):
            agent = selector.select_agent()
            selector.record_feedback(agent, Reward(value=0.7))

        # Should have learned something
        report = selector.get_performance_report()
        assert report is not None

    def test_get_arm_probabilities(self):
        """Test getting arm probabilities."""
        # Test for Thompson Sampling
        selector_ts = AdaptiveAgentSelector(algorithm="thompson_sampling", seed=42)
        probs_ts = selector_ts.get_arm_probabilities()
        assert isinstance(probs_ts, dict)
        assert sum(probs_ts.values()) > 0.99  # Approximate sum to 1

        # Test for UCB
        selector_ucb = AdaptiveAgentSelector(algorithm="ucb", seed=42)
        # Initialize UCB to avoid infinities
        for _ in range(5):
            agent = selector_ucb.select_agent()
            selector_ucb.record_feedback(agent, Reward(value=0.5))

        probs_ucb = selector_ucb.get_arm_probabilities()
        assert isinstance(probs_ucb, dict)
        assert sum(probs_ucb.values()) > 0.99


# =============================================================================
# Bandit Experiment Tests
# =============================================================================


class TestBanditExperiment:
    """Test experiment runner for validation."""

    @pytest.fixture
    def experiment(self):
        """Create experiment with known arm rewards."""
        return BanditExperiment(
            true_arm_means={
                AgentType.VIDEO: 0.8,
                AgentType.MUSIC: 0.5,
                AgentType.TEXT: 0.6,
            },
            seed=42,
        )

    def test_experiment_initialization(self, experiment):
        """Test experiment initialization."""
        assert experiment.optimal_arm == AgentType.VIDEO
        assert experiment.optimal_reward == 0.8

    def test_sample_reward(self, experiment):
        """Test reward sampling."""
        rewards = [experiment.sample_reward(AgentType.VIDEO) for _ in range(100)]
        mean_reward = np.mean([r.value for r in rewards])

        # Should be close to true mean
        assert abs(mean_reward - 0.8) < 0.15

    def test_run_experiment_thompson_sampling(self, experiment):
        """Test running experiment with Thompson Sampling."""
        ts = ThompsonSampling(list(AgentType), seed=42)
        results = experiment.run_experiment(ts, num_rounds=100)

        assert results is not None


# =============================================================================
# Demo Tests
# =============================================================================


class TestDemo:
    """Test demo function."""

    def test_demo_runs(self):
        """Test that demo runs without error."""
        try:
            demo_adaptive_selection()
        except Exception as e:
            pytest.fail(f"Demo failed: {e}")


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_previous_selections(self):
        """Test context with empty previous selections."""
        context = Context(
            location_category=LocationCategory.NATURAL,
            user_age_group="adult",
            time_of_day="morning",
            trip_purpose="vacation",
            previous_selections=[],
        )
        features = context.to_feature_vector()
        assert len(features) > 0

    def test_zero_reward(self):
        """Test handling of zero reward."""
        ts = ThompsonSampling(list(AgentType), seed=42)
        arm = ts.select_arm()
        ts.update(arm, Reward(value=0.0))

        # Should still be able to select
        next_arm = ts.select_arm()
        assert next_arm in AgentType

    def test_all_rewards_same(self):
        """Test when all arms have same reward."""
        experiment = BanditExperiment(
            true_arm_means=dict.fromkeys(AgentType, 0.5), seed=42
        )

        ts = ThompsonSampling(list(AgentType), seed=42)
        results = experiment.run_experiment(ts, num_rounds=50)

        assert results is not None

    def test_single_round(self):
        """Test single round experiment."""
        experiment = BanditExperiment(
            true_arm_means={
                AgentType.VIDEO: 0.8,
                AgentType.MUSIC: 0.5,
                AgentType.TEXT: 0.6,
            },
            seed=42,
        )

        ts = ThompsonSampling(list(AgentType), seed=42)
        results = experiment.run_experiment(ts, num_rounds=1)

        assert results is not None
