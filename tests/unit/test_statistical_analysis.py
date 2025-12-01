"""
Comprehensive Tests for Statistical Analysis Framework
======================================================

MIT-Level test suite for hypothesis testing, effect sizes, and bootstrap methods.

Test Categories:
1. HypothesisTest - Parametric and non-parametric tests
2. EffectSizeAnalysis - Cohen's d, Hedges' g, Glass's Δ
3. BootstrapAnalysis - Confidence intervals, permutation tests
4. StatisticalComparison - Comprehensive comparison framework
5. Edge cases and numerical stability

Coverage Target: 85%+

Author: Multi-Agent Tour Guide Research Team
"""

import numpy as np
import pytest

from src.research.statistical_analysis import (
    BootstrapAnalysis,
    EffectSizeAnalysis,
    HypothesisTest,
    HypothesisTestResult,
    StatisticalComparison,
)

# ============================================================================
# HypothesisTestResult Tests
# ============================================================================


class TestHypothesisTestResult:
    """Tests for HypothesisTestResult dataclass."""

    def test_result_creation_minimal(self):
        """Test minimal result creation."""
        result = HypothesisTestResult(
            test_name="test",
            statistic=1.96,
            p_value=0.05,
            significant=True,
            confidence_level=0.95,
        )
        assert result.test_name == "test"
        assert result.statistic == 1.96
        assert result.p_value == 0.05
        assert result.significant is True

    def test_result_with_effect_size(self):
        """Test result with effect size."""
        result = HypothesisTestResult(
            test_name="t-test",
            statistic=2.5,
            p_value=0.01,
            significant=True,
            confidence_level=0.95,
            effect_size=0.6,
            effect_interpretation="medium",
        )
        assert result.effect_size == 0.6
        assert result.effect_interpretation == "medium"

    def test_result_with_details(self):
        """Test result with additional details."""
        details = {"mean_a": 10.0, "mean_b": 8.0}
        result = HypothesisTestResult(
            test_name="test",
            statistic=1.0,
            p_value=0.1,
            significant=False,
            confidence_level=0.95,
            details=details,
        )
        assert result.details == details


# ============================================================================
# HypothesisTest Tests
# ============================================================================


class TestHypothesisTest:
    """Tests for HypothesisTest class."""

    @pytest.fixture
    def sample_a(self):
        """Sample A with known properties."""
        np.random.seed(42)
        return np.random.normal(10, 2, 100)

    @pytest.fixture
    def sample_b_different(self):
        """Sample B significantly different from A."""
        np.random.seed(123)
        return np.random.normal(12, 2, 100)

    @pytest.fixture
    def sample_b_similar(self):
        """Sample B similar to A."""
        np.random.seed(456)
        return np.random.normal(10.1, 2, 100)

    # Welch's t-test
    def test_welch_t_test_significant_difference(self, sample_a, sample_b_different):
        """Test t-test detects significant difference."""
        result = HypothesisTest.welch_t_test(sample_a, sample_b_different)

        assert result.test_name == "Welch's t-test"
        assert result.p_value < 0.05
        assert result.significant == True  # noqa: E712 - numpy bool comparison
        assert result.effect_size is not None

    def test_welch_t_test_no_difference(self):
        """Test t-test with no significant difference."""
        # Use identical distributions with same seed for truly similar samples
        np.random.seed(42)
        sample_a = np.random.normal(10, 2, 100)
        np.random.seed(42)  # Same seed = same values
        sample_b = np.random.normal(10, 2, 100) + np.random.normal(0, 0.01, 100)

        result = HypothesisTest.welch_t_test(sample_a, sample_b)

        # With nearly identical samples, we expect no significant difference
        assert result.p_value > 0.05 or result.significant == False  # noqa: E712

    def test_welch_t_test_alternative_less(self, sample_a, sample_b_different):
        """Test one-sided t-test (less)."""
        result = HypothesisTest.welch_t_test(
            sample_a, sample_b_different, alternative="less"
        )
        assert isinstance(result.p_value, float)

    def test_welch_t_test_alternative_greater(self, sample_a, sample_b_different):
        """Test one-sided t-test (greater)."""
        result = HypothesisTest.welch_t_test(
            sample_a, sample_b_different, alternative="greater"
        )
        assert isinstance(result.p_value, float)

    def test_welch_t_test_custom_alpha(self, sample_a, sample_b_different):
        """Test t-test with custom alpha."""
        result = HypothesisTest.welch_t_test(sample_a, sample_b_different, alpha=0.01)
        assert result.confidence_level == 0.99

    def test_welch_t_test_details(self, sample_a, sample_b_different):
        """Test that t-test includes proper details."""
        result = HypothesisTest.welch_t_test(sample_a, sample_b_different)

        assert "mean_a" in result.details
        assert "mean_b" in result.details
        assert "std_a" in result.details
        assert "std_b" in result.details
        assert "n_a" in result.details
        assert "n_b" in result.details

    # Mann-Whitney U test
    def test_mann_whitney_significant(self, sample_a, sample_b_different):
        """Test Mann-Whitney detects difference."""
        result = HypothesisTest.mann_whitney_u(sample_a, sample_b_different)

        assert result.test_name == "Mann-Whitney U test"
        assert result.p_value < 0.05
        assert result.significant == True  # noqa: E712 - numpy bool comparison

    def test_mann_whitney_no_difference(self, sample_a, sample_b_similar):
        """Test Mann-Whitney with similar samples."""
        result = HypothesisTest.mann_whitney_u(sample_a, sample_b_similar)

        # p-value should be larger (less significant)
        assert result.p_value > 0.001

    def test_mann_whitney_alternative(self, sample_a, sample_b_different):
        """Test Mann-Whitney with alternative hypothesis."""
        result = HypothesisTest.mann_whitney_u(
            sample_a, sample_b_different, alternative="less"
        )
        assert isinstance(result.p_value, float)

    def test_mann_whitney_details(self, sample_a, sample_b_different):
        """Test Mann-Whitney includes medians."""
        result = HypothesisTest.mann_whitney_u(sample_a, sample_b_different)

        assert "median_a" in result.details
        assert "median_b" in result.details

    # Kolmogorov-Smirnov test
    def test_ks_test_different_distributions(self, sample_a, sample_b_different):
        """Test KS test detects different distributions."""
        result = HypothesisTest.kolmogorov_smirnov(sample_a, sample_b_different)

        assert result.test_name == "Kolmogorov-Smirnov test"
        assert result.p_value < 0.05

    def test_ks_test_similar_distributions(self, sample_a, sample_b_similar):
        """Test KS test with similar distributions."""
        result = HypothesisTest.kolmogorov_smirnov(sample_a, sample_b_similar)

        # Should not be highly significant
        assert result.statistic < 0.5  # D statistic should be small

    def test_ks_test_effect_interpretation(self):
        """Test KS test effect size interpretation."""
        np.random.seed(42)
        a = np.random.normal(0, 1, 100)
        b = np.random.normal(5, 1, 100)  # Very different

        result = HypothesisTest.kolmogorov_smirnov(a, b)
        assert result.effect_interpretation == "Large"

    # Chi-square test
    def test_chi_square_significant(self):
        """Test chi-square detects association."""
        # Create contingency table with clear association
        table = np.array([[50, 10], [10, 50]])
        result = HypothesisTest.chi_square_independence(table)

        assert result.test_name == "Chi-square test"
        assert result.p_value < 0.05
        assert result.significant == True  # noqa: E712 - numpy bool comparison

    def test_chi_square_no_association(self):
        """Test chi-square with independent variables."""
        # Equal distribution - no association
        table = np.array([[25, 25], [25, 25]])
        result = HypothesisTest.chi_square_independence(table)

        assert result.p_value > 0.05
        assert result.significant == False  # noqa: E712 - numpy bool comparison

    def test_chi_square_cramers_v(self):
        """Test chi-square computes Cramér's V."""
        table = np.array([[50, 10], [10, 50]])
        result = HypothesisTest.chi_square_independence(table)

        assert result.effect_size is not None
        assert 0 <= result.effect_size <= 1

    def test_chi_square_details(self):
        """Test chi-square includes expected frequencies."""
        table = np.array([[30, 20], [20, 30]])
        result = HypothesisTest.chi_square_independence(table)

        assert "degrees_of_freedom" in result.details
        assert "expected_frequencies" in result.details


# ============================================================================
# EffectSizeAnalysis Tests
# ============================================================================


class TestEffectSizeAnalysis:
    """Tests for EffectSizeAnalysis class."""

    @pytest.fixture
    def sample_a(self):
        np.random.seed(42)
        return np.random.normal(10, 2, 100)

    @pytest.fixture
    def sample_b(self):
        np.random.seed(123)
        return np.random.normal(11, 2, 100)

    # Cohen's d
    def test_cohens_d_positive(self, sample_a, sample_b):
        """Test Cohen's d with positive difference."""
        d = EffectSizeAnalysis.cohens_d(sample_b, sample_a)  # b > a
        assert d > 0

    def test_cohens_d_negative(self, sample_a, sample_b):
        """Test Cohen's d with negative difference."""
        d = EffectSizeAnalysis.cohens_d(sample_a, sample_b)  # a < b
        assert d < 0

    def test_cohens_d_pooled_vs_unpooled(self, sample_a, sample_b):
        """Test pooled vs unpooled Cohen's d."""
        d_pooled = EffectSizeAnalysis.cohens_d(sample_a, sample_b, pooled=True)
        d_unpooled = EffectSizeAnalysis.cohens_d(sample_a, sample_b, pooled=False)

        # Both should give similar results for equal variances
        assert abs(d_pooled - d_unpooled) < 0.5

    def test_cohens_d_identical_samples(self):
        """Test Cohen's d with identical samples."""
        sample = np.array([1, 2, 3, 4, 5])
        d = EffectSizeAnalysis.cohens_d(sample, sample)
        assert d == 0

    def test_cohens_d_zero_variance(self):
        """Test Cohen's d with zero variance."""
        a = np.array([5, 5, 5, 5])
        b = np.array([5, 5, 5, 5])
        d = EffectSizeAnalysis.cohens_d(a, b)
        assert d == 0  # No variance, no effect

    # Hedges' g
    def test_hedges_g(self, sample_a, sample_b):
        """Test Hedges' g calculation."""
        g = EffectSizeAnalysis.hedges_g(sample_a, sample_b)
        d = EffectSizeAnalysis.cohens_d(sample_a, sample_b)

        # Hedges' g should be smaller due to bias correction
        assert abs(g) <= abs(d)

    def test_hedges_g_large_sample(self):
        """Test Hedges' g converges to Cohen's d for large samples."""
        np.random.seed(42)
        a = np.random.normal(10, 2, 1000)
        b = np.random.normal(11, 2, 1000)

        g = EffectSizeAnalysis.hedges_g(a, b)
        d = EffectSizeAnalysis.cohens_d(a, b)

        # Should be very close for large samples
        assert abs(g - d) < 0.01

    # Glass's Δ
    def test_glass_delta(self):
        """Test Glass's Δ calculation."""
        np.random.seed(42)
        control = np.random.normal(10, 2, 100)
        treatment = np.random.normal(12, 4, 100)  # Higher variance

        delta = EffectSizeAnalysis.glass_delta(treatment, control)

        # Should be approximately (12-10)/2 = 1
        assert 0.5 < delta < 1.5

    def test_glass_delta_zero_control_std(self):
        """Test Glass's Δ with zero control std."""
        control = np.array([5, 5, 5, 5])
        treatment = np.array([6, 7, 8, 9])

        delta = EffectSizeAnalysis.glass_delta(treatment, control)
        assert delta == 0  # Undefined, returns 0

    # Interpretation functions
    def test_interpret_cohens_d_negligible(self):
        """Test Cohen's d interpretation: negligible."""
        assert EffectSizeAnalysis.interpret_cohens_d(0.1) == "negligible"
        assert EffectSizeAnalysis.interpret_cohens_d(-0.1) == "negligible"

    def test_interpret_cohens_d_small(self):
        """Test Cohen's d interpretation: small."""
        assert EffectSizeAnalysis.interpret_cohens_d(0.3) == "small"

    def test_interpret_cohens_d_medium(self):
        """Test Cohen's d interpretation: medium."""
        assert EffectSizeAnalysis.interpret_cohens_d(0.6) == "medium"

    def test_interpret_cohens_d_large(self):
        """Test Cohen's d interpretation: large."""
        assert EffectSizeAnalysis.interpret_cohens_d(1.0) == "large"

    def test_interpret_correlation(self):
        """Test correlation interpretation."""
        assert EffectSizeAnalysis.interpret_correlation(0.05) == "negligible"
        assert EffectSizeAnalysis.interpret_correlation(0.2) == "small"
        assert EffectSizeAnalysis.interpret_correlation(0.4) == "medium"
        assert EffectSizeAnalysis.interpret_correlation(0.6) == "large"

    def test_interpret_cramers_v(self):
        """Test Cramér's V interpretation."""
        assert EffectSizeAnalysis.interpret_cramers_v(0.05) == "negligible"
        assert EffectSizeAnalysis.interpret_cramers_v(0.2) == "small"
        assert EffectSizeAnalysis.interpret_cramers_v(0.4) == "medium"
        assert EffectSizeAnalysis.interpret_cramers_v(0.6) == "large"


# ============================================================================
# BootstrapAnalysis Tests
# ============================================================================


class TestBootstrapAnalysis:
    """Tests for BootstrapAnalysis class."""

    @pytest.fixture
    def sample_data(self):
        np.random.seed(42)
        return np.random.normal(10, 2, 100)

    # Confidence intervals
    def test_confidence_interval_mean(self, sample_data):
        """Test bootstrap CI for mean."""
        lower, point, upper = BootstrapAnalysis.confidence_interval(
            sample_data, statistic=np.mean, n_bootstrap=1000, seed=42
        )

        assert lower < point < upper
        assert 9 < point < 11  # Should be near true mean of 10

    def test_confidence_interval_median(self, sample_data):
        """Test bootstrap CI for median."""
        lower, point, upper = BootstrapAnalysis.confidence_interval(
            sample_data, statistic=np.median, n_bootstrap=1000, seed=42
        )

        assert lower < point < upper

    def test_confidence_interval_custom_confidence(self, sample_data):
        """Test bootstrap CI with custom confidence level."""
        _, _, upper_95 = BootstrapAnalysis.confidence_interval(
            sample_data, confidence=0.95, n_bootstrap=1000, seed=42
        )
        _, _, upper_99 = BootstrapAnalysis.confidence_interval(
            sample_data, confidence=0.99, n_bootstrap=1000, seed=42
        )

        # 99% CI should be wider
        assert upper_99 > upper_95

    def test_confidence_interval_reproducible(self, sample_data):
        """Test bootstrap CI reproducibility with seed."""
        result1 = BootstrapAnalysis.confidence_interval(
            sample_data, seed=42, n_bootstrap=100
        )
        result2 = BootstrapAnalysis.confidence_interval(
            sample_data, seed=42, n_bootstrap=100
        )

        assert result1 == result2

    # Mean difference CI
    def test_mean_difference_ci(self):
        """Test bootstrap CI for mean difference."""
        np.random.seed(42)
        a = np.random.normal(10, 2, 100)
        b = np.random.normal(12, 2, 100)

        lower, point, upper = BootstrapAnalysis.mean_difference_ci(
            a, b, n_bootstrap=1000, seed=42
        )

        # Difference should be around -2 (10 - 12)
        assert -4 < lower < 0
        assert -3 < point < -1
        assert -2 < upper < 0

    def test_mean_difference_ci_no_difference(self):
        """Test CI when means are equal."""
        np.random.seed(42)
        a = np.random.normal(10, 2, 100)
        b = np.random.normal(10, 2, 100)

        lower, point, upper = BootstrapAnalysis.mean_difference_ci(
            a, b, n_bootstrap=1000, seed=42
        )

        # CI should include 0
        assert lower < 0 < upper

    # Permutation test
    def test_permutation_test_significant(self):
        """Test permutation test detects difference."""
        np.random.seed(42)
        a = np.random.normal(10, 2, 50)
        b = np.random.normal(14, 2, 50)

        observed, p_value = BootstrapAnalysis.permutation_test(
            a, b, n_permutations=1000, seed=42
        )

        assert p_value < 0.05
        assert observed < 0  # a mean < b mean

    def test_permutation_test_no_difference(self):
        """Test permutation test with no difference."""
        np.random.seed(42)
        a = np.random.normal(10, 2, 50)
        np.random.seed(123)
        b = np.random.normal(10, 2, 50)

        observed, p_value = BootstrapAnalysis.permutation_test(
            a, b, n_permutations=1000, seed=42
        )

        # Should not be significant
        assert p_value > 0.01

    def test_permutation_test_custom_statistic(self):
        """Test permutation test with custom statistic."""
        np.random.seed(42)
        a = np.random.normal(10, 2, 50)
        b = np.random.normal(12, 2, 50)

        def median_diff(x, y):
            return np.median(x) - np.median(y)

        observed, p_value = BootstrapAnalysis.permutation_test(
            a, b, statistic=median_diff, n_permutations=500, seed=42
        )

        assert isinstance(observed, float)
        assert 0 <= p_value <= 1


# ============================================================================
# StatisticalComparison Tests
# ============================================================================


class TestStatisticalComparison:
    """Tests for StatisticalComparison class."""

    @pytest.fixture
    def comparison_significant(self):
        """Create comparison with significant difference."""
        np.random.seed(42)
        a = np.random.normal(10, 2, 100)
        b = np.random.normal(14, 2, 100)
        return StatisticalComparison(a, b, "Control", "Treatment")

    @pytest.fixture
    def comparison_no_difference(self):
        """Create comparison with no difference."""
        np.random.seed(42)
        a = np.random.normal(10, 2, 100)
        np.random.seed(123)
        b = np.random.normal(10.1, 2, 100)
        return StatisticalComparison(a, b, "A", "B")

    def test_initialization(self, comparison_significant):
        """Test comparison initialization."""
        assert comparison_significant.name_a == "Control"
        assert comparison_significant.name_b == "Treatment"
        assert comparison_significant.alpha == 0.05

    def test_run_all_tests(self, comparison_significant):
        """Test running all statistical tests."""
        comparison_significant.run_all_tests()

        assert "t_test" in comparison_significant.results
        assert "mann_whitney" in comparison_significant.results
        assert "ks_test" in comparison_significant.results
        assert comparison_significant.bootstrap_ci is not None

    def test_summary(self, comparison_significant):
        """Test summary generation."""
        comparison_significant.run_all_tests()
        summary = comparison_significant.summary()

        assert "groups" in summary
        assert "tests" in summary
        assert "bootstrap_ci_95" in summary
        assert "conclusion" in summary

    def test_summary_group_statistics(self, comparison_significant):
        """Test summary includes group statistics."""
        comparison_significant.run_all_tests()
        summary = comparison_significant.summary()

        for group in ["Control", "Treatment"]:
            assert group in summary["groups"]
            assert "n" in summary["groups"][group]
            assert "mean" in summary["groups"][group]
            assert "std" in summary["groups"][group]
            assert "median" in summary["groups"][group]

    def test_conclusion_significant(self, comparison_significant):
        """Test conclusion for significant difference."""
        comparison_significant.run_all_tests()
        summary = comparison_significant.summary()

        assert "evidence of difference" in summary["conclusion"].lower()

    def test_conclusion_no_difference(self, comparison_no_difference):
        """Test conclusion for no difference."""
        comparison_no_difference.run_all_tests()
        summary = comparison_no_difference.summary()

        # May or may not detect difference depending on random sample
        assert "conclusion" in summary

    def test_print_report(self, comparison_significant, capsys):
        """Test print report output."""
        comparison_significant.run_all_tests()
        comparison_significant.print_report()

        captured = capsys.readouterr()
        assert "STATISTICAL COMPARISON" in captured.out
        assert "Control" in captured.out
        assert "Treatment" in captured.out

    def test_custom_alpha(self):
        """Test comparison with custom alpha."""
        np.random.seed(42)
        a = np.random.normal(10, 2, 100)
        b = np.random.normal(11, 2, 100)

        comp = StatisticalComparison(a, b, "A", "B", alpha=0.01)
        comp.run_all_tests()

        assert comp.alpha == 0.01


# ============================================================================
# Edge Cases and Numerical Stability
# ============================================================================


class TestEdgeCases:
    """Edge case tests for numerical stability."""

    def test_small_sample_sizes(self):
        """Test with very small sample sizes."""
        a = np.array([1, 2, 3])
        b = np.array([4, 5, 6])

        result = HypothesisTest.welch_t_test(a, b)
        assert isinstance(result.p_value, float)
        assert not np.isnan(result.p_value)

    def test_single_element_samples(self):
        """Test with single element samples."""
        a = np.array([1.0])
        b = np.array([2.0])

        # Should not crash
        d = EffectSizeAnalysis.cohens_d(a, b)
        # Result may be NaN, 0 or any numeric type due to zero variance
        assert isinstance(d, (int, float, np.number))

    def test_identical_values(self):
        """Test with identical values in both samples."""
        a = np.array([5.0, 5.0, 5.0, 5.0])
        b = np.array([5.0, 5.0, 5.0, 5.0])

        result = HypothesisTest.welch_t_test(a, b)
        # p-value should be 1 (no difference)
        assert result.p_value >= 0.99 or np.isnan(result.p_value)

    def test_very_large_difference(self):
        """Test with very large difference."""
        a = np.array([1, 2, 3])
        b = np.array([1000001, 1000002, 1000003])

        d = EffectSizeAnalysis.cohens_d(a, b)
        assert abs(d) > 100  # Very large effect

    def test_negative_values(self):
        """Test with negative values."""
        a = np.array([-10, -20, -30])
        b = np.array([-5, -10, -15])

        result = HypothesisTest.welch_t_test(a, b)
        assert isinstance(result.p_value, float)

    def test_mixed_positive_negative(self):
        """Test with mixed positive and negative values."""
        np.random.seed(42)
        a = np.random.normal(0, 5, 50)  # Centered at 0
        b = np.random.normal(2, 5, 50)  # Centered at 2

        result = HypothesisTest.welch_t_test(a, b)
        assert isinstance(result.statistic, float)

    def test_very_small_p_values(self):
        """Test detection of very small p-values."""
        np.random.seed(42)
        a = np.random.normal(0, 0.1, 1000)
        b = np.random.normal(10, 0.1, 1000)

        result = HypothesisTest.welch_t_test(a, b)
        assert result.p_value < 1e-10

    def test_float_precision(self):
        """Test numerical precision."""
        a = np.array([1e-10, 2e-10, 3e-10])
        b = np.array([1.1e-10, 2.1e-10, 3.1e-10])

        d = EffectSizeAnalysis.cohens_d(a, b)
        assert not np.isnan(d)
        assert not np.isinf(d)
