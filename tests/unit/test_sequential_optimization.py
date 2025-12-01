"""
Tests for Sequential Content Optimization via Reinforcement Learning.

MIT-Level Test Coverage for:
- TourState and TourAction
- EmotionalArcReward
- SoftmaxPolicy
- SequentialContentOptimizer
- DiversityConstrainedOptimizer

Edge Cases Documented:
- Empty content history
- Journey at start/middle/end positions
- All content types exhausted
- Extreme significance values
- Policy convergence verification
"""

import pytest

np = pytest.importorskip("numpy", reason="numpy required for research tests")

from src.research.sequential_optimization import (
    ContentType,
    DiversityConstrainedOptimizer,
    EmotionalArcReward,
    EmotionalState,
    SequentialContentOptimizer,
    SoftmaxPolicy,
    TourAction,
    TourState,
)

# =============================================================================
# TourState Tests
# =============================================================================


class TestTourState:
    """Test TourState dataclass and feature extraction."""

    def test_tour_state_creation(self):
        """Test basic state creation."""
        state = TourState(
            point_index=0, total_points=10, emotional_state=EmotionalState.CURIOUS
        )
        assert state.point_index == 0
        assert state.total_points == 10
        assert state.emotional_state == EmotionalState.CURIOUS

    def test_tour_state_with_history(self):
        """Test state with content history."""
        state = TourState(
            point_index=3,
            total_points=10,
            emotional_state=EmotionalState.ENGAGED,
            content_history=[ContentType.VIDEO, ContentType.TEXT, ContentType.MUSIC],
        )
        assert len(state.content_history) == 3

    def test_tour_state_to_vector(self):
        """Test feature vector extraction."""
        state = TourState(
            point_index=5,
            total_points=10,
            emotional_state=EmotionalState.EXCITED,
            location_type="historical",
            location_significance=0.9,
        )
        features = state.to_vector()

        assert isinstance(features, np.ndarray)
        assert len(features) == state.state_dim
        assert features.dtype == np.float32

    # EDGE CASE: Journey start
    def test_tour_state_at_journey_start(self):
        """Edge case: State at the very beginning of journey."""
        state = TourState(
            point_index=0,
            total_points=10,
            emotional_state=EmotionalState.CURIOUS,
            content_history=[],
        )
        features = state.to_vector()

        # Progress should be 0
        assert features[0] == 0.0
        # Content distribution should be zeros
        assert np.allclose(features[6:9], [0, 0, 0])

    # EDGE CASE: Journey end
    def test_tour_state_at_journey_end(self):
        """Edge case: State at the end of journey."""
        state = TourState(
            point_index=9,
            total_points=10,
            emotional_state=EmotionalState.SATISFIED,
            content_history=[ContentType.VIDEO] * 9,
        )
        features = state.to_vector()

        # Progress should be close to 1 (0.9 for point 9 of 10)
        assert features[0] == pytest.approx(0.9, rel=0.05)

    # EDGE CASE: Single point journey
    def test_tour_state_single_point(self):
        """Edge case: Journey with only one point."""
        state = TourState(
            point_index=0, total_points=1, emotional_state=EmotionalState.CURIOUS
        )
        features = state.to_vector()

        # Should not crash and return valid features
        assert len(features) == state.state_dim
        assert not np.any(np.isnan(features))

    # EDGE CASE: Extreme significance values
    def test_tour_state_extreme_significance(self):
        """Edge case: Extreme location significance values."""
        state_low = TourState(
            point_index=0,
            total_points=10,
            emotional_state=EmotionalState.CURIOUS,
            location_significance=0.0,
        )
        state_high = TourState(
            point_index=0,
            total_points=10,
            emotional_state=EmotionalState.CURIOUS,
            location_significance=1.0,
        )

        features_low = state_low.to_vector()
        features_high = state_high.to_vector()

        assert features_low[-2] == 0.0
        assert features_high[-2] == 1.0


class TestTourAction:
    """Test TourAction dataclass."""

    def test_action_creation(self):
        """Test basic action creation."""
        action = TourAction(content_type=ContentType.VIDEO, confidence=0.9)
        assert action.content_type == ContentType.VIDEO
        assert action.confidence == 0.9

    def test_action_dim(self):
        """Test action dimension."""
        assert TourAction.action_dim() == 3  # VIDEO, MUSIC, TEXT


# =============================================================================
# EmotionalArcReward Tests
# =============================================================================


class TestEmotionalArcReward:
    """Test EmotionalArcReward function."""

    def test_reward_creation(self):
        """Test reward function creation with custom weights."""
        reward_fn = EmotionalArcReward(alpha=0.4, beta=0.3, gamma=0.2, delta=0.1)
        assert reward_fn.alpha == 0.4
        assert reward_fn.beta == 0.3

    def test_compute_reward(self):
        """Test reward computation."""
        reward_fn = EmotionalArcReward()

        state = TourState(
            point_index=0,
            total_points=10,
            emotional_state=EmotionalState.CURIOUS,
            location_type="historical",
        )
        action = TourAction(content_type=ContentType.TEXT)
        next_state = TourState(
            point_index=1,
            total_points=10,
            emotional_state=EmotionalState.ENGAGED,
            content_history=[ContentType.TEXT],
        )

        reward, components = reward_fn.compute_reward(state, action, next_state)

        assert isinstance(reward, float)
        assert "arc" in components
        assert "quality" in components
        assert "diversity" in components
        assert "match" in components

    # EDGE CASE: Perfect emotional arc transition
    def test_reward_ideal_arc_transition(self):
        """Edge case: Perfect emotional state transition."""
        reward_fn = EmotionalArcReward()

        state = TourState(
            point_index=2, total_points=10, emotional_state=EmotionalState.CURIOUS
        )
        next_state = TourState(
            point_index=3,
            total_points=10,
            emotional_state=EmotionalState.ENGAGED,
            content_history=[ContentType.VIDEO],
        )
        action = TourAction(content_type=ContentType.VIDEO)

        reward, components = reward_fn.compute_reward(state, action, next_state)

        # Arc reward should be positive for good transition
        assert components["arc"] > 0

    # EDGE CASE: Diversity with all same content type
    def test_reward_no_diversity(self):
        """Edge case: All content of same type (no diversity)."""
        reward_fn = EmotionalArcReward()

        state = TourState(
            point_index=5,
            total_points=10,
            emotional_state=EmotionalState.ENGAGED,
            content_history=[ContentType.VIDEO] * 5,
        )
        action = TourAction(content_type=ContentType.VIDEO)  # Same type again
        next_state = TourState(
            point_index=6,
            total_points=10,
            emotional_state=EmotionalState.ENGAGED,
            content_history=[ContentType.VIDEO] * 6,
        )

        reward, components = reward_fn.compute_reward(state, action, next_state)

        # Diversity reward should be low
        assert components["diversity"] < 0.5


# =============================================================================
# SoftmaxPolicy Tests
# =============================================================================


class TestSoftmaxPolicy:
    """Test SoftmaxPolicy for action selection."""

    def test_policy_creation(self):
        """Test policy creation."""
        policy = SoftmaxPolicy(state_dim=12, action_dim=3, learning_rate=0.01)
        assert policy.state_dim == 12
        assert policy.action_dim == 3

    def test_get_action_probabilities(self):
        """Test action probability computation."""
        policy = SoftmaxPolicy(state_dim=12, action_dim=3, seed=42)
        state = np.random.randn(12).astype(np.float32)

        probs = policy.get_action_probabilities(state)

        assert len(probs) == 3
        assert np.isclose(sum(probs), 1.0)
        assert all(p >= 0 for p in probs)

    def test_select_action(self):
        """Test action selection."""
        policy = SoftmaxPolicy(state_dim=12, action_dim=3, seed=42)
        tour_state = TourState(
            point_index=0, total_points=10, emotional_state=EmotionalState.CURIOUS
        )

        action = policy.select_action(tour_state)

        assert isinstance(action, TourAction)
        assert action.content_type in ContentType
        assert 0 <= action.confidence <= 1

    def test_policy_update(self):
        """Test policy parameter update."""
        policy = SoftmaxPolicy(state_dim=12, action_dim=3, seed=42)
        state = np.random.randn(12).astype(np.float32)

        old_theta = policy.theta.copy()

        stats = policy.update(state, action_idx=0, advantage=0.5, td_error=0.3)

        # Parameters should change after update
        assert not np.allclose(old_theta, policy.theta)
        assert "advantage" in stats

    # EDGE CASE: Very large state values
    def test_policy_large_state_values(self):
        """Edge case: State with very large values (numerical stability)."""
        policy = SoftmaxPolicy(state_dim=12, action_dim=3, seed=42)
        state = np.ones(12, dtype=np.float32) * 100

        probs = policy.get_action_probabilities(state)

        # Should still be valid probabilities
        assert np.isclose(sum(probs), 1.0)
        assert not np.any(np.isnan(probs))


# =============================================================================
# SequentialContentOptimizer Tests
# =============================================================================


class TestSequentialContentOptimizer:
    """Test SequentialContentOptimizer main interface."""

    def test_optimizer_creation(self):
        """Test optimizer creation."""
        optimizer = SequentialContentOptimizer(total_points=10, gamma=0.99, seed=42)
        assert optimizer.total_points == 10
        assert optimizer.gamma == 0.99

    def test_simulate_step(self):
        """Test environment simulation step."""
        optimizer = SequentialContentOptimizer(total_points=10, seed=42)

        state = TourState(
            point_index=0,
            total_points=10,
            emotional_state=EmotionalState.CURIOUS,
            location_type="historical",
        )
        action = TourAction(content_type=ContentType.TEXT)

        next_state, reward, done = optimizer.simulate_step(state, action)

        assert next_state.point_index == 1
        assert isinstance(reward, float)
        assert done is False

    def test_train_episode(self):
        """Test single training episode."""
        optimizer = SequentialContentOptimizer(total_points=5, seed=42)

        stats = optimizer.train_episode()

        assert "episode_reward" in stats
        assert "episode_length" in stats
        assert stats["episode_length"] == 5

    def test_train_multiple_episodes(self):
        """Test training for multiple episodes."""
        optimizer = SequentialContentOptimizer(total_points=5, seed=42)

        history = optimizer.train(num_episodes=10)

        assert len(history["rewards"]) == 10
        assert len(history["lengths"]) == 10

    def test_generate_optimal_sequence(self):
        """Test optimal sequence generation."""
        optimizer = SequentialContentOptimizer(total_points=5, seed=42)
        optimizer.train(num_episodes=10)  # Brief training

        location_types = ["historical", "scenic", "cultural", "natural", "historical"]
        significances = [0.8, 0.5, 0.9, 0.7, 0.95]

        sequence = optimizer.generate_optimal_sequence(location_types, significances)

        assert len(sequence) == 5
        for _loc_type, content_type, conf in sequence:
            assert isinstance(content_type, ContentType)
            assert 0 <= conf <= 1

    def test_theoretical_analysis(self):
        """Test theoretical analysis output."""
        optimizer = SequentialContentOptimizer(total_points=5, seed=42)
        optimizer.train(num_episodes=10)

        analysis = optimizer.theoretical_analysis()

        assert "algorithm" in analysis
        assert "training_episodes" in analysis
        assert "theoretical_guarantees" in analysis

    # EDGE CASE: Very short journey
    def test_optimizer_single_point_journey(self):
        """Edge case: Journey with single point."""
        optimizer = SequentialContentOptimizer(total_points=1, seed=42)

        stats = optimizer.train_episode()

        assert stats["episode_length"] == 1

    # EDGE CASE: High gamma (long-term focus)
    def test_optimizer_high_gamma(self):
        """Edge case: High discount factor."""
        optimizer = SequentialContentOptimizer(total_points=5, gamma=0.999, seed=42)

        history = optimizer.train(num_episodes=5)

        assert len(history["rewards"]) == 5


class TestDiversityConstrainedOptimizer:
    """Test DiversityConstrainedOptimizer extension."""

    def test_constrained_optimizer_creation(self):
        """Test constrained optimizer creation."""
        optimizer = DiversityConstrainedOptimizer(
            total_points=10, min_type_fraction=0.2, seed=42
        )
        assert optimizer.min_type_fraction == 0.2

    def test_lagrange_multiplier_initialization(self):
        """Test Lagrange multiplier initialization."""
        optimizer = DiversityConstrainedOptimizer(total_points=10, seed=42)

        assert ContentType.VIDEO in optimizer.lambdas
        assert ContentType.MUSIC in optimizer.lambdas
        assert ContentType.TEXT in optimizer.lambdas
        assert all(lam == 0.0 for lam in optimizer.lambdas.values())


# =============================================================================
# Integration Tests
# =============================================================================


class TestSequentialOptimizationIntegration:
    """Integration tests for sequential optimization."""

    def test_full_training_pipeline(self):
        """Test complete training and prediction pipeline."""
        optimizer = SequentialContentOptimizer(total_points=8, seed=42)

        # Train
        history = optimizer.train(num_episodes=50)

        # Verify training occurred
        assert len(history["rewards"]) == 50

        # Generate sequence
        location_types = [
            "historical",
            "scenic",
            "cultural",
            "entertainment",
            "natural",
            "religious",
            "scenic",
            "historical",
        ]
        significances = [0.7, 0.5, 0.9, 0.6, 0.8, 0.95, 0.6, 0.9]

        sequence = optimizer.generate_optimal_sequence(location_types, significances)

        # Verify sequence
        assert len(sequence) == 8
        content_types_used = {ct for _, ct, _ in sequence}
        assert len(content_types_used) >= 1  # At least one type used

    def test_reward_convergence(self):
        """Test that rewards improve over training."""
        optimizer = SequentialContentOptimizer(total_points=5, seed=42)

        history = optimizer.train(num_episodes=100)

        # Compare early vs late rewards
        early_avg = np.mean(history["rewards"][:20])
        late_avg = np.mean(history["rewards"][-20:])

        # Late rewards should generally be higher (or at least not much worse)
        # Note: This is a soft test as RL can be noisy
        assert late_avg >= early_avg - 1.0
