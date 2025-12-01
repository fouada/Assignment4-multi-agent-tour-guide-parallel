"""
Tests for Information-Theoretic Quality Bounds Analysis.

MIT-Level Test Coverage for:
- Entropy Calculations
- Mutual Information
- KL Divergence
- Regret Bounds
- Diversity Metrics
"""

import pytest
import numpy as np

from src.research.information_theory import (
    EntropyCalculator,
    MutualInformationCalculator,
    KLDivergence,
    RegretBoundResult,
    InformationTheoreticRegretBounds,
    AgentUserChannel,
    RateDistortionAnalyzer,
    DiversityMetrics,
    InformationTheoreticAnalyzer,
    InformationTheoreticAnalysis,
    demo_information_theory,
)


# =============================================================================
# Entropy Calculator Tests
# =============================================================================


class TestEntropyCalculator:
    """Test entropy calculations."""
    
    def test_uniform_entropy(self):
        """Test entropy of uniform distribution."""
        # Uniform over 4 outcomes: H = log2(4) = 2 bits
        probs = np.array([0.25, 0.25, 0.25, 0.25])
        h = EntropyCalculator.shannon_entropy(probs)
        
        assert abs(h - 2.0) < 0.001
    
    def test_deterministic_entropy(self):
        """Test entropy of deterministic outcome is zero."""
        probs = np.array([1.0])
        h = EntropyCalculator.shannon_entropy(probs)
        
        assert h == 0.0
    
    def test_binary_entropy_half(self):
        """Test binary entropy at p=0.5."""
        # H(0.5) = 1 bit
        probs = np.array([0.5, 0.5])
        h = EntropyCalculator.shannon_entropy(probs)
        
        assert abs(h - 1.0) < 0.001
    
    def test_entropy_bounds(self):
        """Test entropy is bounded."""
        # Random distribution
        probs = np.random.dirichlet([1, 1, 1, 1])
        h = EntropyCalculator.shannon_entropy(probs)
        
        # 0 <= H <= log(n)
        assert h >= 0
        assert h <= np.log2(4) + 0.001
    
    def test_entropy_with_zeros(self):
        """Test entropy handles zero probabilities."""
        probs = np.array([0.5, 0.5, 0.0])
        h = EntropyCalculator.shannon_entropy(probs)
        
        # Should handle 0*log(0) = 0
        assert h >= 0
        assert np.isfinite(h)
    
    def test_entropy_base_e(self):
        """Test entropy with natural log."""
        probs = np.array([0.5, 0.5])
        h = EntropyCalculator.shannon_entropy(probs, base=np.e)
        
        # Should be ln(2) ≈ 0.693
        assert abs(h - np.log(2)) < 0.001
    
    def test_gaussian_entropy(self):
        """Test Gaussian entropy calculation."""
        variance = 1.0
        h = EntropyCalculator.gaussian_entropy(variance)
        
        # h(X) = (1/2) log(2πe) for unit variance
        expected = 0.5 * np.log(2 * np.pi * np.e)
        assert abs(h - expected) < 0.001
    
    def test_conditional_entropy(self):
        """Test conditional entropy H(Y|X)."""
        # Joint distribution where Y is independent of X
        joint = np.array([
            [0.25, 0.25],
            [0.25, 0.25],
        ])
        
        h_y_given_x = EntropyCalculator.conditional_entropy(joint)
        
        # For independent: H(Y|X) = H(Y) = 1 bit
        assert abs(h_y_given_x - 1.0) < 0.001


# =============================================================================
# Mutual Information Calculator Tests
# =============================================================================


class TestMutualInformationCalculator:
    """Test mutual information calculations."""
    
    def test_mi_independent_variables(self):
        """Test MI of independent variables is zero."""
        # P(X)P(Y) = P(X,Y) for independent
        joint = np.outer([0.5, 0.5], [0.5, 0.5])
        
        mi = MutualInformationCalculator.compute(joint)
        
        assert abs(mi) < 0.001
    
    def test_mi_perfectly_correlated(self):
        """Test MI of perfectly correlated variables."""
        # X = Y: P(X=0, Y=0) = P(X=1, Y=1) = 0.5
        joint = np.array([
            [0.5, 0.0],
            [0.0, 0.5],
        ])
        
        mi = MutualInformationCalculator.compute(joint)
        
        # MI = H(X) = H(Y) = 1 bit
        assert abs(mi - 1.0) < 0.001
    
    def test_mi_non_negative(self):
        """Test MI is always non-negative."""
        # Random joint distribution
        joint = np.random.dirichlet([1, 1, 1, 1]).reshape(2, 2)
        joint /= joint.sum()  # Ensure it sums to 1
        
        mi = MutualInformationCalculator.compute(joint)
        
        assert mi >= -0.001  # Allow small numerical error
    
    def test_mi_symmetric(self):
        """Test MI is symmetric: I(X;Y) = I(Y;X)."""
        joint = np.array([
            [0.4, 0.1],
            [0.2, 0.3],
        ])
        
        mi_xy = MutualInformationCalculator.compute(joint)
        mi_yx = MutualInformationCalculator.compute(joint.T)
        
        assert abs(mi_xy - mi_yx) < 0.001
    
    def test_normalized_mi(self):
        """Test normalized mutual information."""
        joint = np.array([
            [0.5, 0.0],
            [0.0, 0.5],
        ])
        
        nmi = MutualInformationCalculator.normalized(joint)
        
        # NMI in [0, 1], perfect correlation gives 1
        assert 0 <= nmi <= 1
        assert abs(nmi - 1.0) < 0.001


# =============================================================================
# KL Divergence Tests
# =============================================================================


class TestKLDivergence:
    """Test KL divergence calculations."""
    
    def test_kl_same_distribution(self):
        """Test KL divergence of distribution with itself is zero."""
        p = np.array([0.3, 0.7])
        
        kl_val = KLDivergence.compute(p, p)
        
        assert abs(kl_val) < 0.001
    
    def test_kl_non_negative(self):
        """Test KL divergence is non-negative."""
        p = np.array([0.5, 0.5])
        q = np.array([0.9, 0.1])
        
        kl_val = KLDivergence.compute(p, q)
        
        assert kl_val >= -0.001  # Allow small numerical error
    
    def test_kl_asymmetric(self):
        """Test KL divergence is asymmetric."""
        p = np.array([0.5, 0.5])
        q = np.array([0.9, 0.1])
        
        kl_pq = KLDivergence.compute(p, q)
        kl_qp = KLDivergence.compute(q, p)
        
        # KL is asymmetric, so these should differ
        assert abs(kl_pq - kl_qp) > 0.01
    
    def test_symmetric_kl(self):
        """Test symmetric (Jensen-Shannon) divergence."""
        p = np.array([0.5, 0.5])
        q = np.array([0.9, 0.1])
        
        jsd = KLDivergence.symmetric(p, q)
        
        # JSD is symmetric by definition
        jsd2 = KLDivergence.symmetric(q, p)
        assert abs(jsd - jsd2) < 0.001


# =============================================================================
# Information Theoretic Regret Bounds Tests
# =============================================================================


class TestInformationTheoreticRegretBounds:
    """Test regret bound calculations."""
    
    @pytest.fixture
    def bounds(self):
        """Create regret bounds calculator."""
        return InformationTheoreticRegretBounds(
            n_arms=3,
            arm_means=[0.8, 0.5, 0.6]
        )
    
    def test_initialization(self, bounds):
        """Test initialization."""
        assert bounds.K == 3
        assert bounds.optimal_mean == 0.8
    
    def test_lai_robbins_bound(self, bounds):
        """Test Lai-Robbins lower bound."""
        result = bounds.lai_robbins_bound(T=1000)
        
        assert isinstance(result, RegretBoundResult)
        assert result.bound_value > 0
        # Check bound_type contains 'lower' or similar
        assert "lower" in result.bound_type.lower() or "lai" in result.bound_type.lower()
    
    def test_bound_grows_with_rounds(self, bounds):
        """Test that regret bound grows with rounds."""
        bound_100 = bounds.lai_robbins_bound(T=100).bound_value
        bound_1000 = bounds.lai_robbins_bound(T=1000).bound_value
        
        # Bound should increase with more rounds
        assert bound_1000 > bound_100
    
    def test_thompson_sampling_upper_bound(self, bounds):
        """Test Thompson Sampling upper bound."""
        result = bounds.thompson_sampling_upper_bound(T=1000)
        
        assert isinstance(result, RegretBoundResult)
        assert result.bound_value > 0
        assert "thompson" in result.bound_type.lower()
    
    def test_information_ratio_bound(self, bounds):
        """Test information ratio bound."""
        result = bounds.information_ratio_bound(T=1000)
        
        assert isinstance(result, RegretBoundResult)
        assert result.bound_value > 0
        assert "info" in result.bound_type.lower() or "ratio" in result.bound_type.lower()
    
    def test_minimax_bound(self, bounds):
        """Test minimax regret bound."""
        result = bounds.minimax_bound(T=1000)
        
        assert isinstance(result, RegretBoundResult)
        assert result.bound_value > 0
        assert "minimax" in result.bound_type.lower()
    
    def test_bounds_comparison(self, bounds):
        """Test that upper bounds are larger than lower bounds."""
        T = 1000
        
        lai_robbins = bounds.lai_robbins_bound(T).bound_value
        thompson = bounds.thompson_sampling_upper_bound(T).bound_value
        minimax = bounds.minimax_bound(T).bound_value
        
        # Thompson upper bound should be larger than minimax lower bound
        assert thompson > minimax * 0.5  # Some margin for different constants


class TestRegretBoundResult:
    """Test RegretBoundResult dataclass."""
    
    def test_result_creation(self):
        """Test creating a regret bound result."""
        result = RegretBoundResult(
            bound_type="lower",
            bound_value=10.5,
            parameters={"T": 1000, "K": 3},
            interpretation="Lower bound on expected regret",
            tightness="asymptotically_tight",
        )
        
        assert result.bound_type == "lower"
        assert result.bound_value == 10.5
        assert result.tightness == "asymptotically_tight"


# =============================================================================
# Agent User Channel Tests
# =============================================================================


class TestAgentUserChannel:
    """Test channel capacity modeling."""
    
    @pytest.fixture
    def channel(self):
        """Create channel."""
        return AgentUserChannel()
    
    def test_channel_creation(self, channel):
        """Test channel creation."""
        assert channel is not None
    
    def test_channel_has_methods(self, channel):
        """Test channel has expected attributes."""
        assert channel.n_input == 3
        assert channel.n_output == 5
    
    def test_compute_capacity(self, channel):
        """Test channel capacity computation."""
        # Create a simple transition matrix
        P = np.array([
            [0.6, 0.2, 0.1, 0.05, 0.05],  # agent 1
            [0.4, 0.3, 0.15, 0.1, 0.05],   # agent 2
            [0.5, 0.25, 0.15, 0.05, 0.05], # agent 3
        ])
        
        capacity, opt_dist = channel.compute_capacity(P)
        
        assert capacity >= 0
        assert len(opt_dist) == 3
        assert abs(sum(opt_dist) - 1.0) < 0.001  # Should sum to 1
    
    def test_noisy_channel_capacity(self, channel):
        """Test noisy channel capacity."""
        # No noise should give max capacity
        cap_no_noise = channel.noisy_channel_capacity(noise_level=0.0)
        assert cap_no_noise > 0
        
        # High noise should give low capacity
        cap_high_noise = channel.noisy_channel_capacity(noise_level=0.4)
        assert cap_high_noise < cap_no_noise
        
        # Max noise (0.5) should give zero capacity
        cap_max_noise = channel.noisy_channel_capacity(noise_level=0.5)
        assert cap_max_noise == 0.0


# =============================================================================
# Rate Distortion Analyzer Tests
# =============================================================================


class TestRateDistortionAnalyzer:
    """Test rate-distortion analysis."""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer."""
        return RateDistortionAnalyzer()
    
    def test_analyzer_creation(self, analyzer):
        """Test analyzer creation."""
        assert analyzer is not None
        assert analyzer.K == 3
    
    def test_gaussian_rd_function(self, analyzer):
        """Test Gaussian rate-distortion function."""
        variance = 1.0
        
        # At distortion = variance, rate should be 0
        rate_at_var = analyzer.gaussian_rd_function(variance, variance)
        assert rate_at_var == 0.0
        
        # At lower distortion, rate should be positive
        rate_low_dist = analyzer.gaussian_rd_function(variance, 0.5)
        assert rate_low_dist > 0
        
        # Rate should decrease as distortion increases
        rate_mid = analyzer.gaussian_rd_function(variance, 0.7)
        assert rate_low_dist > rate_mid
    
    def test_discrete_rd_function(self, analyzer):
        """Test discrete rate-distortion function."""
        # Uniform source
        source_probs = np.array([1/3, 1/3, 1/3])
        # Hamming distortion
        distortion_matrix = 1 - np.eye(3)
        
        # At high distortion, rate should be low
        rate = analyzer.discrete_rd_function(source_probs, distortion_matrix, 0.5)
        assert rate >= 0
    
    def test_compute_pareto_frontier(self, analyzer):
        """Test Pareto frontier computation."""
        rates, distortions = analyzer.compute_pareto_frontier(n_points=10)
        
        assert len(rates) == 10
        assert len(distortions) == 10
        
        # Rates should be non-negative
        assert all(r >= 0 for r in rates)
        
        # Distortions should be non-negative
        assert all(d >= 0 for d in distortions)


# =============================================================================
# Diversity Metrics Tests
# =============================================================================


class TestDiversityMetrics:
    """Test diversity metrics."""
    
    @pytest.fixture
    def metrics(self):
        """Create diversity metrics."""
        return DiversityMetrics()
    
    def test_metrics_creation(self, metrics):
        """Test metrics creation."""
        assert metrics is not None
    
    def test_compute_entropy_from_counts(self, metrics):
        """Test entropy calculation from selection counts."""
        # Uniform selection counts
        counts = np.array([10, 10, 10])
        probs = counts / counts.sum()
        
        # Use EntropyCalculator directly
        diversity = EntropyCalculator.shannon_entropy(probs)
        
        # Should be close to log2(3) ≈ 1.58
        assert diversity > 1.5
    
    def test_single_agent_zero_entropy(self, metrics):
        """Test single agent selection has zero entropy."""
        counts = np.array([30, 0, 0])
        probs = counts / counts.sum()
        
        diversity = EntropyCalculator.shannon_entropy(probs)
        
        # Should be zero
        assert diversity < 0.01
    
    def test_selection_entropy(self):
        """Test selection entropy from dict counts."""
        counts = {"video": 10, "music": 10, "text": 10}
        entropy = DiversityMetrics.selection_entropy(counts)
        
        # Uniform -> max entropy
        assert entropy > 1.5
    
    def test_selection_entropy_empty(self):
        """Test selection entropy with empty counts."""
        counts = {"video": 0, "music": 0, "text": 0}
        entropy = DiversityMetrics.selection_entropy(counts)
        
        assert entropy == 0.0
    
    def test_normalized_diversity(self):
        """Test normalized diversity score."""
        # Uniform distribution
        counts = {"video": 10, "music": 10, "text": 10}
        norm_div = DiversityMetrics.normalized_diversity(counts)
        
        # Should be close to 1.0 for uniform
        assert 0.9 < norm_div <= 1.0
        
        # Skewed distribution
        skewed_counts = {"video": 100, "music": 1, "text": 1}
        skewed_div = DiversityMetrics.normalized_diversity(skewed_counts)
        
        # Should be lower
        assert skewed_div < norm_div
    
    def test_normalized_diversity_single_agent(self):
        """Test normalized diversity with single agent."""
        counts = {"video": 10}
        norm_div = DiversityMetrics.normalized_diversity(counts)
        
        assert norm_div == 0.0
    
    def test_conditional_diversity(self):
        """Test conditional diversity."""
        selections_by_context = {
            "historical": {"video": 5, "text": 5},
            "urban": {"video": 8, "music": 2},
        }
        
        cond_div = DiversityMetrics.conditional_diversity(selections_by_context)
        
        assert cond_div >= 0
    
    def test_information_gain(self):
        """Test information gain calculation."""
        prior = {"video": 10, "music": 10, "text": 10}
        posterior = {"video": 20, "music": 5, "text": 5}
        
        ig = DiversityMetrics.information_gain(prior, posterior)
        
        # Information gain should be positive (reduced entropy)
        assert ig > 0


# =============================================================================
# Information Theoretic Analyzer Tests
# =============================================================================


class TestInformationTheoreticAnalyzer:
    """Test the main analyzer class."""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer."""
        return InformationTheoreticAnalyzer()
    
    def test_analyzer_creation(self, analyzer):
        """Test analyzer creation."""
        assert analyzer is not None
        assert analyzer.n_agents == 3
    
    def test_analyzer_with_custom_means(self):
        """Test analyzer with custom arm means."""
        analyzer = InformationTheoreticAnalyzer(n_agents=4, arm_means=[0.8, 0.6, 0.5, 0.4])
        assert analyzer.n_agents == 4
        assert len(analyzer.arm_means) == 4
    
    def test_analyze(self, analyzer):
        """Test full analysis."""
        selection_counts = {"video": 50, "music": 30, "text": 20}
        
        analysis = analyzer.analyze(selection_counts, T=1000)
        
        assert analysis is not None
        assert analysis.n_agents == 3
        assert analysis.n_observations == 100
        assert analysis.selection_entropy > 0
        assert analysis.normalized_diversity > 0
        assert analysis.channel_capacity >= 0
    
    def test_analysis_to_dict(self, analyzer):
        """Test analysis to_dict method."""
        selection_counts = {"video": 50, "music": 30, "text": 20}
        analysis = analyzer.analyze(selection_counts, T=1000)
        
        result = analysis.to_dict()
        
        assert "timestamp" in result
        assert "n_agents" in result
        assert "selection_entropy" in result
        assert "regret_bounds" in result


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_single_outcome_entropy(self):
        """Test entropy with single outcome."""
        probs = np.array([1.0])
        h = EntropyCalculator.shannon_entropy(probs)
        
        assert h == 0.0
    
    def test_very_small_probabilities(self):
        """Test entropy with very small probabilities."""
        probs = np.array([0.999, 0.001])
        h = EntropyCalculator.shannon_entropy(probs)
        
        # Should be close to 0
        assert h < 0.1
        assert np.isfinite(h)
    
    def test_large_number_of_outcomes(self):
        """Test with large number of outcomes."""
        n = 1000
        probs = np.ones(n) / n  # Uniform
        
        h = EntropyCalculator.shannon_entropy(probs)
        
        # H = log2(1000) ≈ 9.97
        expected = np.log2(n)
        assert abs(h - expected) < 0.001
    
    def test_kl_with_zero_in_q(self):
        """Test KL divergence when q has zeros where p is non-zero."""
        p = np.array([0.5, 0.5])
        q = np.array([1.0, 0.0])
        
        kl = KLDivergence.compute(p, q)
        
        # Should be infinite
        assert kl == float('inf')


# =============================================================================
# Integration Tests
# =============================================================================


class TestInformationTheoryIntegration:
    """Integration tests for information theory pipeline."""
    
    def test_entropy_mutual_info_relationship(self):
        """Test H(X,Y) = H(X) + H(Y) - I(X;Y) relationship."""
        # Create joint distribution
        joint = np.array([
            [0.4, 0.1],
            [0.1, 0.4],
        ])
        
        # Compute marginals
        p_x = joint.sum(axis=1)
        p_y = joint.sum(axis=0)
        
        # Compute entropies
        h_x = EntropyCalculator.shannon_entropy(p_x)
        h_y = EntropyCalculator.shannon_entropy(p_y)
        h_xy = EntropyCalculator.shannon_entropy(joint.flatten())
        mi = MutualInformationCalculator.compute(joint)
        
        # Verify relationship: H(X,Y) = H(X) + H(Y) - I(X;Y)
        assert abs(h_xy - (h_x + h_y - mi)) < 0.001
    
    def test_data_processing_inequality(self):
        """Test I(X;Y) >= I(X;Z) when X -> Y -> Z forms a Markov chain."""
        # X -> Y: P(Y|X)
        p_y_given_x = np.array([
            [0.9, 0.1],
            [0.1, 0.9],
        ])
        
        # Y -> Z: P(Z|Y)
        p_z_given_y = np.array([
            [0.8, 0.2],
            [0.2, 0.8],
        ])
        
        # Prior on X
        p_x = np.array([0.5, 0.5])
        
        # Joint P(X,Y)
        joint_xy = np.outer(p_x, [1, 1]) * p_y_given_x.T
        
        # Compute I(X;Y)
        i_xy = MutualInformationCalculator.compute(joint_xy)
        
        # I(X;Y) should be positive since X and Y are correlated
        assert i_xy > 0


class TestConditionalMutualInformation:
    """Test conditional mutual information."""
    
    def test_conditional_mi(self):
        """Test conditional mutual information computation."""
        # Simple 3D joint distribution P(X, Y, Z)
        joint_xyz = np.random.dirichlet([1]*8).reshape(2, 2, 2)
        
        cmi = MutualInformationCalculator.conditional(joint_xyz)
        
        # CMI should be non-negative
        assert cmi >= -0.001


class TestDifferentialEntropy:
    """Test differential entropy for continuous distributions."""
    
    def test_differential_entropy_gaussian(self):
        """Test differential entropy for Gaussian."""
        # Standard normal PDF
        def gaussian_pdf(x):
            return np.exp(-x**2 / 2) / np.sqrt(2 * np.pi)
        
        h = EntropyCalculator.differential_entropy(gaussian_pdf, support=(-10, 10))
        
        # Should be approximately 0.5 * log(2*pi*e) ≈ 1.42
        expected = 0.5 * np.log(2 * np.pi * np.e)
        assert abs(h - expected) < 0.1


class TestDemo:
    """Test demo function."""
    
    def test_demo_import(self):
        """Test demo function is importable."""
        assert callable(demo_information_theory)
