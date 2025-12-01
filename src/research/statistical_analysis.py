"""
Statistical Analysis Framework
==============================

MIT-Level statistical analysis tools for rigorous data-driven comparison:
1. Hypothesis testing (parametric and non-parametric)
2. Effect size analysis (Cohen's d, Hedges' g, Cramér's V)
3. Bootstrap confidence intervals
4. Multiple comparison corrections

Author: Multi-Agent Tour Guide Research Team
Version: 1.0.0
Date: November 2025

References:
    - Cohen, J. (1988). Statistical Power Analysis for the Behavioral Sciences.
    - Efron, B. & Tibshirani, R. (1993). An Introduction to the Bootstrap.
"""

from dataclasses import dataclass

import numpy as np
from scipy import stats


@dataclass
class HypothesisTestResult:
    """Result container for hypothesis tests."""

    test_name: str
    statistic: float
    p_value: float
    significant: bool
    confidence_level: float
    effect_size: float | None = None
    effect_interpretation: str | None = None
    details: dict | None = None


class HypothesisTest:
    """
    Collection of hypothesis tests for comparing distributions.

    Provides both parametric and non-parametric tests with appropriate
    effect size measures.
    """

    @staticmethod
    def welch_t_test(
        sample_a: np.ndarray,
        sample_b: np.ndarray,
        alpha: float = 0.05,
        alternative: str = "two-sided",
    ) -> HypothesisTestResult:
        """
        Welch's t-test for unequal variances.

        More robust than Student's t-test when sample sizes and
        variances differ between groups.

        Args:
            sample_a: First sample
            sample_b: Second sample
            alpha: Significance level
            alternative: 'two-sided', 'less', or 'greater'

        Returns:
            HypothesisTestResult with test statistics
        """
        sample_a = np.asarray(sample_a)
        sample_b = np.asarray(sample_b)

        t_stat, p_value = stats.ttest_ind(
            sample_a, sample_b, equal_var=False, alternative=alternative
        )

        # Cohen's d effect size
        pooled_std = np.sqrt((np.var(sample_a) + np.var(sample_b)) / 2)
        cohens_d = (
            (np.mean(sample_a) - np.mean(sample_b)) / pooled_std
            if pooled_std > 0
            else 0
        )

        return HypothesisTestResult(
            test_name="Welch's t-test",
            statistic=t_stat,
            p_value=p_value,
            significant=p_value < alpha,
            confidence_level=1 - alpha,
            effect_size=cohens_d,
            effect_interpretation=EffectSizeAnalysis.interpret_cohens_d(cohens_d),
            details={
                "mean_a": float(np.mean(sample_a)),
                "mean_b": float(np.mean(sample_b)),
                "std_a": float(np.std(sample_a)),
                "std_b": float(np.std(sample_b)),
                "n_a": len(sample_a),
                "n_b": len(sample_b),
            },
        )

    @staticmethod
    def mann_whitney_u(
        sample_a: np.ndarray,
        sample_b: np.ndarray,
        alpha: float = 0.05,
        alternative: str = "two-sided",
    ) -> HypothesisTestResult:
        """
        Mann-Whitney U test (non-parametric).

        Robust alternative to t-test when normality assumption is violated.
        Tests whether one distribution is stochastically greater than another.

        Args:
            sample_a: First sample
            sample_b: Second sample
            alpha: Significance level
            alternative: 'two-sided', 'less', or 'greater'

        Returns:
            HypothesisTestResult with test statistics
        """
        sample_a = np.asarray(sample_a)
        sample_b = np.asarray(sample_b)

        u_stat, p_value = stats.mannwhitneyu(
            sample_a, sample_b, alternative=alternative
        )

        # Compute rank-biserial correlation as effect size
        n_a, n_b = len(sample_a), len(sample_b)
        r = 1 - (2 * u_stat) / (n_a * n_b)  # Rank-biserial correlation

        return HypothesisTestResult(
            test_name="Mann-Whitney U test",
            statistic=u_stat,
            p_value=p_value,
            significant=p_value < alpha,
            confidence_level=1 - alpha,
            effect_size=r,
            effect_interpretation=EffectSizeAnalysis.interpret_correlation(abs(r)),
            details={
                "median_a": float(np.median(sample_a)),
                "median_b": float(np.median(sample_b)),
                "n_a": n_a,
                "n_b": n_b,
            },
        )

    @staticmethod
    def kolmogorov_smirnov(
        sample_a: np.ndarray, sample_b: np.ndarray, alpha: float = 0.05
    ) -> HypothesisTestResult:
        """
        Two-sample Kolmogorov-Smirnov test.

        Tests whether two samples come from the same distribution.
        Sensitive to both location and shape differences.

        Args:
            sample_a: First sample
            sample_b: Second sample
            alpha: Significance level

        Returns:
            HypothesisTestResult with test statistics
        """
        sample_a = np.asarray(sample_a)
        sample_b = np.asarray(sample_b)

        ks_stat, p_value = stats.ks_2samp(sample_a, sample_b)

        return HypothesisTestResult(
            test_name="Kolmogorov-Smirnov test",
            statistic=ks_stat,
            p_value=p_value,
            significant=p_value < alpha,
            confidence_level=1 - alpha,
            effect_size=ks_stat,  # D statistic is itself an effect size
            effect_interpretation="Large"
            if ks_stat > 0.2
            else "Small"
            if ks_stat > 0.1
            else "Negligible",
        )

    @staticmethod
    def chi_square_independence(
        contingency_table: np.ndarray, alpha: float = 0.05
    ) -> HypothesisTestResult:
        """
        Chi-square test for independence.

        Tests whether two categorical variables are independent.

        Args:
            contingency_table: 2D array of observed frequencies
            alpha: Significance level

        Returns:
            HypothesisTestResult with test statistics
        """
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)

        # Cramér's V effect size
        n = contingency_table.sum()
        min_dim = min(contingency_table.shape) - 1
        cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0

        return HypothesisTestResult(
            test_name="Chi-square test",
            statistic=chi2,
            p_value=p_value,
            significant=p_value < alpha,
            confidence_level=1 - alpha,
            effect_size=cramers_v,
            effect_interpretation=EffectSizeAnalysis.interpret_cramers_v(cramers_v),
            details={
                "degrees_of_freedom": dof,
                "expected_frequencies": expected.tolist(),
            },
        )


class EffectSizeAnalysis:
    """
    Effect size calculations and interpretations.

    Provides standardized measures of effect magnitude that are
    independent of sample size.
    """

    @staticmethod
    def cohens_d(
        sample_a: np.ndarray, sample_b: np.ndarray, pooled: bool = True
    ) -> float:
        """
        Calculate Cohen's d effect size.

        Args:
            sample_a: First sample
            sample_b: Second sample
            pooled: Use pooled standard deviation (True) or sample_a's std (False)

        Returns:
            Cohen's d value
        """
        sample_a = np.asarray(sample_a)
        sample_b = np.asarray(sample_b)

        mean_diff = np.mean(sample_a) - np.mean(sample_b)

        if pooled:
            n_a, n_b = len(sample_a), len(sample_b)
            var_a, var_b = np.var(sample_a, ddof=1), np.var(sample_b, ddof=1)
            pooled_var = ((n_a - 1) * var_a + (n_b - 1) * var_b) / (n_a + n_b - 2)
            std = np.sqrt(pooled_var)
        else:
            std = np.std(sample_a, ddof=1)

        return mean_diff / std if std > 0 else 0

    @staticmethod
    def hedges_g(sample_a: np.ndarray, sample_b: np.ndarray) -> float:
        """
        Calculate Hedges' g (bias-corrected Cohen's d).

        Provides less biased estimate for small samples.

        Args:
            sample_a: First sample
            sample_b: Second sample

        Returns:
            Hedges' g value
        """
        d = EffectSizeAnalysis.cohens_d(sample_a, sample_b)
        n = len(sample_a) + len(sample_b)

        # Bias correction factor
        correction = 1 - (3 / (4 * n - 9))

        return d * correction

    @staticmethod
    def glass_delta(treatment: np.ndarray, control: np.ndarray) -> float:
        """
        Calculate Glass's Δ effect size.

        Uses only control group's standard deviation,
        appropriate when treatment affects variance.

        Args:
            treatment: Treatment group sample
            control: Control group sample

        Returns:
            Glass's Δ value
        """
        treatment = np.asarray(treatment)
        control = np.asarray(control)

        mean_diff = np.mean(treatment) - np.mean(control)
        control_std = np.std(control, ddof=1)

        return mean_diff / control_std if control_std > 0 else 0

    @staticmethod
    def interpret_cohens_d(d: float) -> str:
        """
        Interpret Cohen's d using conventional thresholds.

        Reference: Cohen, J. (1988)
        """
        d = abs(d)
        if d < 0.2:
            return "negligible"
        elif d < 0.5:
            return "small"
        elif d < 0.8:
            return "medium"
        else:
            return "large"

    @staticmethod
    def interpret_correlation(r: float) -> str:
        """Interpret correlation coefficient magnitude."""
        r = abs(r)
        if r < 0.1:
            return "negligible"
        elif r < 0.3:
            return "small"
        elif r < 0.5:
            return "medium"
        else:
            return "large"

    @staticmethod
    def interpret_cramers_v(v: float) -> str:
        """Interpret Cramér's V effect size."""
        if v < 0.1:
            return "negligible"
        elif v < 0.3:
            return "small"
        elif v < 0.5:
            return "medium"
        else:
            return "large"


class BootstrapAnalysis:
    """
    Bootstrap methods for confidence intervals and hypothesis testing.

    Non-parametric approach that makes minimal distributional assumptions.

    Reference: Efron, B. & Tibshirani, R. (1993). An Introduction to the Bootstrap.
    """

    @staticmethod
    def confidence_interval(
        data: np.ndarray,
        statistic: callable = np.mean,
        confidence: float = 0.95,
        n_bootstrap: int = 10000,
        seed: int | None = None,
    ) -> tuple[float, float, float]:
        """
        Compute bootstrap confidence interval for a statistic.

        Uses percentile method (bias-corrected and accelerated available
        in scipy.stats.bootstrap).

        Args:
            data: Sample data
            statistic: Function to compute statistic (default: mean)
            confidence: Confidence level
            n_bootstrap: Number of bootstrap samples
            seed: Random seed for reproducibility

        Returns:
            Tuple of (lower_bound, point_estimate, upper_bound)
        """
        if seed is not None:
            np.random.seed(seed)

        data = np.asarray(data)
        point_estimate = statistic(data)

        # Generate bootstrap distribution
        bootstrap_stats = []
        for _ in range(n_bootstrap):
            resample = np.random.choice(data, size=len(data), replace=True)
            bootstrap_stats.append(statistic(resample))

        bootstrap_stats = np.array(bootstrap_stats)

        # Percentile confidence interval
        alpha = 1 - confidence
        lower = np.percentile(bootstrap_stats, 100 * alpha / 2)
        upper = np.percentile(bootstrap_stats, 100 * (1 - alpha / 2))

        return (lower, point_estimate, upper)

    @staticmethod
    def mean_difference_ci(
        sample_a: np.ndarray,
        sample_b: np.ndarray,
        confidence: float = 0.95,
        n_bootstrap: int = 10000,
        seed: int | None = None,
    ) -> tuple[float, float, float]:
        """
        Bootstrap CI for difference in means.

        Args:
            sample_a: First sample
            sample_b: Second sample
            confidence: Confidence level
            n_bootstrap: Number of bootstrap samples
            seed: Random seed

        Returns:
            Tuple of (lower, point_estimate, upper)
        """
        if seed is not None:
            np.random.seed(seed)

        sample_a = np.asarray(sample_a)
        sample_b = np.asarray(sample_b)

        point_estimate = np.mean(sample_a) - np.mean(sample_b)

        # Bootstrap the difference
        diffs = []
        for _ in range(n_bootstrap):
            boot_a = np.random.choice(sample_a, size=len(sample_a), replace=True)
            boot_b = np.random.choice(sample_b, size=len(sample_b), replace=True)
            diffs.append(np.mean(boot_a) - np.mean(boot_b))

        diffs = np.array(diffs)

        alpha = 1 - confidence
        lower = np.percentile(diffs, 100 * alpha / 2)
        upper = np.percentile(diffs, 100 * (1 - alpha / 2))

        return (lower, point_estimate, upper)

    @staticmethod
    def permutation_test(
        sample_a: np.ndarray,
        sample_b: np.ndarray,
        statistic: callable = lambda a, b: np.mean(a) - np.mean(b),
        n_permutations: int = 10000,
        seed: int | None = None,
    ) -> tuple[float, float]:
        """
        Permutation test for comparing two groups.

        Tests the null hypothesis that the two samples come from
        the same distribution by randomly permuting group labels.

        Args:
            sample_a: First sample
            sample_b: Second sample
            statistic: Test statistic function
            n_permutations: Number of permutations
            seed: Random seed

        Returns:
            Tuple of (observed_statistic, p_value)
        """
        if seed is not None:
            np.random.seed(seed)

        sample_a = np.asarray(sample_a)
        sample_b = np.asarray(sample_b)

        observed = statistic(sample_a, sample_b)
        combined = np.concatenate([sample_a, sample_b])
        n_a = len(sample_a)

        # Generate null distribution
        null_stats = []
        for _ in range(n_permutations):
            np.random.shuffle(combined)
            perm_a = combined[:n_a]
            perm_b = combined[n_a:]
            null_stats.append(statistic(perm_a, perm_b))

        null_stats = np.array(null_stats)

        # Two-sided p-value
        p_value = np.mean(np.abs(null_stats) >= np.abs(observed))

        return (observed, p_value)


class StatisticalComparison:
    """
    Comprehensive comparison of two experimental conditions.

    Runs multiple statistical tests and aggregates results for
    robust inference.
    """

    def __init__(
        self,
        sample_a: np.ndarray,
        sample_b: np.ndarray,
        name_a: str = "A",
        name_b: str = "B",
        alpha: float = 0.05,
    ):
        self.sample_a = np.asarray(sample_a)
        self.sample_b = np.asarray(sample_b)
        self.name_a = name_a
        self.name_b = name_b
        self.alpha = alpha

        self.results: dict[str, HypothesisTestResult] = {}
        self.bootstrap_ci: tuple | None = None

    def run_all_tests(self) -> "StatisticalComparison":
        """Run all applicable statistical tests."""
        # Parametric test
        self.results["t_test"] = HypothesisTest.welch_t_test(
            self.sample_a, self.sample_b, self.alpha
        )

        # Non-parametric tests
        self.results["mann_whitney"] = HypothesisTest.mann_whitney_u(
            self.sample_a, self.sample_b, self.alpha
        )

        self.results["ks_test"] = HypothesisTest.kolmogorov_smirnov(
            self.sample_a, self.sample_b, self.alpha
        )

        # Bootstrap CI
        self.bootstrap_ci = BootstrapAnalysis.mean_difference_ci(
            self.sample_a, self.sample_b, confidence=1 - self.alpha
        )

        return self

    def summary(self) -> dict:
        """Generate summary of all comparisons."""
        return {
            "groups": {
                self.name_a: {
                    "n": len(self.sample_a),
                    "mean": float(np.mean(self.sample_a)),
                    "std": float(np.std(self.sample_a)),
                    "median": float(np.median(self.sample_a)),
                },
                self.name_b: {
                    "n": len(self.sample_b),
                    "mean": float(np.mean(self.sample_b)),
                    "std": float(np.std(self.sample_b)),
                    "median": float(np.median(self.sample_b)),
                },
            },
            "tests": {
                name: {
                    "statistic": result.statistic,
                    "p_value": result.p_value,
                    "significant": result.significant,
                    "effect_size": result.effect_size,
                    "effect_interpretation": result.effect_interpretation,
                }
                for name, result in self.results.items()
            },
            "bootstrap_ci_95": {
                "lower": self.bootstrap_ci[0] if self.bootstrap_ci else None,
                "point": self.bootstrap_ci[1] if self.bootstrap_ci else None,
                "upper": self.bootstrap_ci[2] if self.bootstrap_ci else None,
            },
            "conclusion": self._generate_conclusion(),
        }

    def _generate_conclusion(self) -> str:
        """Generate interpretive conclusion."""
        # Check agreement across tests
        significant_tests = sum(1 for r in self.results.values() if r.significant)
        total_tests = len(self.results)

        if significant_tests == total_tests:
            strength = "Strong"
        elif significant_tests >= total_tests / 2:
            strength = "Moderate"
        else:
            strength = "Weak"

        effect = self.results.get("t_test")
        if effect and effect.effect_size is not None:
            effect_str = f"with {effect.effect_interpretation} effect size (d={effect.effect_size:.3f})"
        else:
            effect_str = ""

        if significant_tests > 0:
            return f"{strength} evidence of difference between {self.name_a} and {self.name_b} {effect_str}"
        else:
            return f"No significant difference detected between {self.name_a} and {self.name_b}"

    def print_report(self):
        """Print formatted comparison report."""
        summary = self.summary()

        print("=" * 70)
        print(f"STATISTICAL COMPARISON: {self.name_a} vs {self.name_b}")
        print("=" * 70)

        print("\nDescriptive Statistics:")
        for name, group_stats in summary["groups"].items():
            print(
                f"  {name}: n={group_stats['n']}, μ={group_stats['mean']:.4f}, σ={group_stats['std']:.4f}"
            )

        print(f"\nHypothesis Tests (α={self.alpha}):")
        for test_name, test_result in summary["tests"].items():
            sig = "✓" if test_result["significant"] else "✗"
            print(f"  {test_name}: p={test_result['p_value']:.4e} {sig}")
            if test_result["effect_size"] is not None:
                print(
                    f"    Effect: {test_result['effect_interpretation']} ({test_result['effect_size']:.3f})"
                )

        print("\nBootstrap 95% CI for difference:")
        ci = summary["bootstrap_ci_95"]
        if ci["lower"] is not None:
            print(f"  [{ci['lower']:.4f}, {ci['upper']:.4f}]")

        print(f"\nConclusion: {summary['conclusion']}")
        print("=" * 70)
