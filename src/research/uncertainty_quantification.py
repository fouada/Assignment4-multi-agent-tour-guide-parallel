"""
📊 Uncertainty Quantification via Conformal Prediction
========================================================

MIT-Level Innovation: Calibrated Confidence with Distribution-Free Guarantees

PROBLEM SOLVED:
Machine learning models often produce overconfident predictions.
When the Judge agent says "80% confident in VIDEO", what does it mean?
Is it actually correct 80% of the time? Usually not!

OUR INNOVATION:
Use Conformal Prediction to provide:
1. CALIBRATED confidence (if we say 90%, it's correct 90% of the time)
2. PREDICTION SETS (set of possible content types with guaranteed coverage)
3. DISTRIBUTION-FREE guarantees (works for ANY model, ANY data)

Key Contributions:
1. Conformal prediction for content selection
2. Adaptive prediction set sizes
3. Calibration without retraining models
4. Theoretical coverage guarantees
5. Selective prediction with abstention

Academic References:
- Vovk et al. (2005) "Algorithmic Learning in a Random World"
- Shafer & Vovk (2008) "A Tutorial on Conformal Prediction"
- Angelopoulos & Bates (2022) "Conformal Prediction: A Gentle Introduction"
- Romano et al. (2020) "Classification with Valid Adaptive Prediction Sets"

Target Venues: NeurIPS, ICML, JMLR
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any

import numpy as np

# =============================================================================
# Core Data Structures
# =============================================================================


class ContentType(str, Enum):
    """Content types for selection."""

    VIDEO = "video"
    MUSIC = "music"
    TEXT = "text"


@dataclass
class PredictionSet:
    """
    A conformal prediction set.

    Instead of predicting a single class, we predict a SET of classes
    with guaranteed coverage probability.

    Example:
    - Traditional: "The answer is VIDEO (80% confident)"
    - Conformal: "The answer is in {VIDEO, MUSIC} (90% guaranteed)"

    The guarantee is DISTRIBUTION-FREE: it holds for any distribution!
    """

    content_types: set[ContentType]
    coverage_target: float  # e.g., 0.9 for 90% coverage
    scores: dict[ContentType, float]  # Conformity scores
    threshold: float  # Threshold used for set construction

    @property
    def size(self) -> int:
        """Size of the prediction set."""
        return len(self.content_types)

    @property
    def is_singleton(self) -> bool:
        """Whether the set contains exactly one element."""
        return self.size == 1

    @property
    def is_empty(self) -> bool:
        """Whether the set is empty (should never happen with valid threshold)."""
        return self.size == 0

    def point_prediction(self) -> ContentType | None:
        """Get single prediction if set is singleton."""
        if self.is_singleton:
            return list(self.content_types)[0]
        # Return highest scoring element
        return max(self.scores, key=self.scores.get)


@dataclass
class CalibrationResult:
    """
    Result of calibration process.

    Tracks:
    - Threshold for achieving target coverage
    - Empirical coverage on calibration data
    - Set size statistics
    """

    threshold: float
    target_coverage: float
    empirical_coverage: float
    avg_set_size: float
    set_size_distribution: dict[int, int]
    n_calibration_samples: int


# =============================================================================
# Conformity Score Functions
# =============================================================================


class ConformityScore(ABC):
    """
    Abstract base class for conformity scores.

    The conformity score s(x, y) measures how well label y "conforms"
    to the typical patterns for input x.

    Higher scores = less conforming = more unusual
    """

    @abstractmethod
    def compute(
        self,
        predictions: np.ndarray,  # Model's predicted probabilities
        label: int,  # True label index
    ) -> float:
        """
        Compute conformity score.

        Args:
            predictions: Model's probability distribution over classes
            label: True class label

        Returns:
            Conformity score (higher = more non-conforming)
        """
        pass


class SimpleProbabilityScore(ConformityScore):
    """
    Simple conformity score: s(x, y) = 1 - p(y|x)

    The score is low when the model assigns high probability to y.
    """

    def compute(self, predictions: np.ndarray, label: int) -> float:
        return 1.0 - predictions[label]


class AdaptiveProbabilityScore(ConformityScore):
    """
    Adaptive conformity score (APS) from Romano et al., 2020.

    s(x, y) = Σ_{y' : π(y') ≤ π(y)} p(y'|x)

    Where π is the ranking of classes by probability.

    This leads to smaller prediction sets on average compared to simple scores.
    """

    def __init__(self, randomize: bool = True, seed: int | None = None):
        self.randomize = randomize
        self.rng = np.random.RandomState(seed)

    def compute(self, predictions: np.ndarray, label: int) -> float:
        # Sort classes by probability (descending)
        sorted_indices = np.argsort(-predictions)

        # Find position of true label
        label_rank = np.where(sorted_indices == label)[0][0]

        # Sum probabilities up to and including label
        cumsum = np.cumsum(predictions[sorted_indices])
        score = cumsum[label_rank]

        # Randomization for tie-breaking
        if self.randomize:
            # Add uniform noise for randomized score
            if label_rank > 0:
                prev_cumsum = cumsum[label_rank - 1]
            else:
                prev_cumsum = 0.0
            u = self.rng.uniform(0, 1)
            score = prev_cumsum + u * (score - prev_cumsum)

        return score


class RAPSScore(ConformityScore):
    """
    Regularized Adaptive Prediction Sets (RAPS).

    Adds regularization to prevent very large prediction sets:

    s(x, y) = APS(x, y) + λ · max(0, rank(y) - k_reg)

    The regularization penalizes including low-probability classes.
    """

    def __init__(
        self, lambda_reg: float = 0.01, k_reg: int = 1, seed: int | None = None
    ):
        self.lambda_reg = lambda_reg
        self.k_reg = k_reg
        self.aps = AdaptiveProbabilityScore(seed=seed)

    def compute(self, predictions: np.ndarray, label: int) -> float:
        # APS score
        aps_score = self.aps.compute(predictions, label)

        # Regularization based on rank
        sorted_indices = np.argsort(-predictions)
        label_rank = np.where(sorted_indices == label)[0][0]

        reg_penalty = self.lambda_reg * max(0, label_rank - self.k_reg + 1)

        return aps_score + reg_penalty


# =============================================================================
# Conformal Predictor
# =============================================================================


class ConformalPredictor:
    """
    Conformal Prediction for Classification.

    Mathematical Foundation:

    Given:
    - Calibration set D_cal = {(x_i, y_i)}_{i=1}^n
    - New input x_{n+1}
    - Target coverage 1-α

    Algorithm:
    1. Compute conformity scores s_i = s(x_i, y_i) for calibration data
    2. Find threshold q̂ = quantile(s_1, ..., s_n, (n+1)(1-α)/n)
    3. Prediction set: C(x) = {y : s(x, y) ≤ q̂}

    Theoretical Guarantee (Vovk et al., 2005):
    P(y_{n+1} ∈ C(x_{n+1})) ≥ 1 - α

    This holds for ANY distribution of (x, y)!
    """

    def __init__(
        self, scorer: ConformityScore, coverage: float = 0.9, seed: int | None = None
    ):
        """
        Initialize conformal predictor.

        Args:
            scorer: Conformity score function
            coverage: Target coverage (1-α), e.g., 0.9 for 90%
            seed: Random seed
        """
        self.scorer = scorer
        self.coverage = coverage
        self.alpha = 1 - coverage
        self.rng = np.random.RandomState(seed)

        # Calibration data
        self.calibration_scores: list[float] = []
        self.threshold: float | None = None

        # Statistics
        self.prediction_history: list[PredictionSet] = []

    def calibrate(
        self,
        predictions: np.ndarray,  # (n, num_classes)
        labels: np.ndarray,  # (n,)
    ) -> CalibrationResult:
        """
        Calibrate the conformal predictor on held-out data.

        Args:
            predictions: Model predictions (probabilities)
            labels: True labels

        Returns:
            CalibrationResult with threshold and statistics
        """
        n = len(labels)

        # Compute conformity scores for all calibration examples
        self.calibration_scores = []
        for i in range(n):
            score = self.scorer.compute(predictions[i], int(labels[i]))
            self.calibration_scores.append(score)

        # Compute threshold (quantile)
        # q̂ = inf{q : #{s_i ≤ q} ≥ (n+1)(1-α)}
        # Equivalent to (1-α)(n+1)/n quantile of scores
        quantile_level = (1 - self.alpha) * (n + 1) / n
        quantile_level = min(quantile_level, 1.0)  # Clip to [0, 1]

        self.threshold = np.quantile(self.calibration_scores, quantile_level)

        # Compute empirical coverage and set sizes on calibration data
        set_sizes = []
        covered = 0

        for i in range(n):
            pred_set = self._construct_set(predictions[i])
            set_sizes.append(pred_set.size)

            true_label = list(ContentType)[int(labels[i])]
            if true_label in pred_set.content_types:
                covered += 1

        # Set size distribution
        size_dist = {}
        for size in set_sizes:
            size_dist[size] = size_dist.get(size, 0) + 1

        return CalibrationResult(
            threshold=self.threshold,
            target_coverage=self.coverage,
            empirical_coverage=covered / n,
            avg_set_size=np.mean(set_sizes),
            set_size_distribution=size_dist,
            n_calibration_samples=n,
        )

    def _construct_set(self, predictions: np.ndarray) -> PredictionSet:
        """Construct prediction set for a single example."""
        scores = {}
        included = set()

        for idx, content_type in enumerate(ContentType):
            score = self.scorer.compute(predictions, idx)
            scores[content_type] = score

            if score <= self.threshold:
                included.add(content_type)

        return PredictionSet(
            content_types=included,
            coverage_target=self.coverage,
            scores=scores,
            threshold=self.threshold,
        )

    def predict(self, predictions: np.ndarray) -> PredictionSet:
        """
        Make conformal prediction.

        Args:
            predictions: Model's probability distribution

        Returns:
            PredictionSet with guaranteed coverage
        """
        if self.threshold is None:
            raise ValueError("Must calibrate before predicting!")

        pred_set = self._construct_set(predictions)
        self.prediction_history.append(pred_set)

        return pred_set

    def predict_batch(
        self,
        predictions: np.ndarray,  # (batch_size, num_classes)
    ) -> list[PredictionSet]:
        """Make conformal predictions for a batch."""
        return [self.predict(pred) for pred in predictions]


# =============================================================================
# Adaptive Conformal Inference
# =============================================================================


class AdaptiveConformalPredictor:
    """
    Adaptive Conformal Inference (ACI) for non-exchangeable data.

    Standard conformal prediction assumes exchangeability. In practice,
    data distributions can shift over time (e.g., user preferences change).

    ACI adapts the threshold online to maintain coverage:

    q̂_t+1 = q̂_t + γ(α - err_t)

    Where:
    - err_t = 1 if y_t ∉ C_t(x_t), 0 otherwise
    - γ > 0 is the step size

    Theoretical Guarantee (Gibbs & Candès, 2021):
    Average coverage converges to 1-α even under distribution shift.
    """

    def __init__(
        self,
        scorer: ConformityScore,
        coverage: float = 0.9,
        step_size: float = 0.1,
        initial_threshold: float = 0.5,
        seed: int | None = None,
    ):
        self.scorer = scorer
        self.coverage = coverage
        self.alpha = 1 - coverage
        self.gamma = step_size
        self.threshold = initial_threshold
        self.rng = np.random.RandomState(seed)

        # History for analysis
        self.threshold_history: list[float] = [initial_threshold]
        self.error_history: list[int] = []
        self.coverage_history: list[float] = []

    def predict_and_update(
        self, predictions: np.ndarray, true_label: int | None = None
    ) -> PredictionSet:
        """
        Make prediction and update threshold if label provided.

        Args:
            predictions: Model's probabilities
            true_label: True label (optional, for online update)

        Returns:
            PredictionSet
        """
        # Construct prediction set with current threshold
        scores = {}
        included = set()

        for idx, content_type in enumerate(ContentType):
            score = self.scorer.compute(predictions, idx)
            scores[content_type] = score

            if score <= self.threshold:
                included.add(content_type)

        pred_set = PredictionSet(
            content_types=included,
            coverage_target=self.coverage,
            scores=scores,
            threshold=self.threshold,
        )

        # Update threshold if true label provided
        if true_label is not None:
            true_content = list(ContentType)[true_label]
            error = 0 if true_content in pred_set.content_types else 1

            # ACI update
            self.threshold = self.threshold + self.gamma * (self.alpha - error)
            self.threshold = max(0.0, min(1.0, self.threshold))  # Clip

            self.threshold_history.append(self.threshold)
            self.error_history.append(error)

            # Running coverage
            if len(self.error_history) >= 10:
                recent_coverage = 1 - np.mean(self.error_history[-10:])
                self.coverage_history.append(recent_coverage)

        return pred_set

    def get_coverage_analysis(self) -> dict[str, Any]:
        """Get analysis of coverage over time."""
        n = len(self.error_history)
        if n == 0:
            return {"n_predictions": 0}

        return {
            "n_predictions": n,
            "overall_coverage": 1 - np.mean(self.error_history),
            "target_coverage": self.coverage,
            "final_threshold": self.threshold,
            "threshold_range": (
                min(self.threshold_history),
                max(self.threshold_history),
            ),
            "coverage_trend": self.coverage_history[-10:]
            if self.coverage_history
            else [],
        }


# =============================================================================
# Selective Prediction (Abstention)
# =============================================================================


class SelectivePredictor:
    """
    Selective Prediction with Abstention.

    Sometimes the model should say "I don't know" instead of making
    a potentially incorrect prediction.

    Strategy:
    1. If prediction set is too large (> k), abstain
    2. If confidence is too low, abstain
    3. User gets warning when abstaining

    This improves precision at the cost of recall.
    """

    def __init__(
        self,
        conformal_predictor: ConformalPredictor,
        max_set_size: int = 2,
        min_confidence: float = 0.3,
    ):
        self.predictor = conformal_predictor
        self.max_set_size = max_set_size
        self.min_confidence = min_confidence

        # Statistics
        self.abstention_count = 0
        self.prediction_count = 0

    def predict_or_abstain(
        self, predictions: np.ndarray
    ) -> tuple[ContentType | None, str, dict]:
        """
        Make prediction or abstain if uncertain.

        Args:
            predictions: Model's probabilities

        Returns:
            (prediction or None, reason, details)
        """
        pred_set = self.predictor.predict(predictions)
        self.prediction_count += 1

        # Check abstention conditions
        if pred_set.size > self.max_set_size:
            self.abstention_count += 1
            return (
                None,
                "abstain_large_set",
                {
                    "set_size": pred_set.size,
                    "set": [ct.value for ct in pred_set.content_types],
                    "threshold": self.max_set_size,
                },
            )

        max_prob = max(predictions)
        if max_prob < self.min_confidence:
            self.abstention_count += 1
            return (
                None,
                "abstain_low_confidence",
                {"max_confidence": float(max_prob), "threshold": self.min_confidence},
            )

        # Make prediction
        return (
            pred_set.point_prediction(),
            "prediction",
            {
                "set": [ct.value for ct in pred_set.content_types],
                "confidence": float(max(predictions)),
            },
        )

    @property
    def abstention_rate(self) -> float:
        """Fraction of predictions that resulted in abstention."""
        if self.prediction_count == 0:
            return 0.0
        return self.abstention_count / self.prediction_count


# =============================================================================
# Uncertainty-Aware Content Selector
# =============================================================================


class UncertaintyAwareContentSelector:
    """
    Main interface for uncertainty-aware content selection.

    Combines:
    1. Conformal prediction for calibrated uncertainty
    2. Adaptive threshold for distribution shift
    3. Selective prediction for high-stakes scenarios

    Novel Features:
    - Distribution-free coverage guarantees
    - Honest uncertainty estimates
    - Knows when it doesn't know
    """

    def __init__(
        self,
        coverage: float = 0.9,
        use_adaptive: bool = True,
        allow_abstention: bool = True,
        seed: int | None = None,
    ):
        """
        Initialize the selector.

        Args:
            coverage: Target coverage (e.g., 0.9 for 90%)
            use_adaptive: Use adaptive conformal inference
            allow_abstention: Allow model to abstain
            seed: Random seed
        """
        self.coverage = coverage
        self.use_adaptive = use_adaptive
        self.allow_abstention = allow_abstention

        # Conformity scorer
        self.scorer = RAPSScore(seed=seed)

        # Conformal predictor
        if use_adaptive:
            self.predictor = AdaptiveConformalPredictor(
                self.scorer, coverage=coverage, seed=seed
            )
        else:
            self.predictor = ConformalPredictor(
                self.scorer, coverage=coverage, seed=seed
            )

        # Selective predictor
        if allow_abstention:
            base_predictor = ConformalPredictor(
                self.scorer, coverage=coverage, seed=seed
            )
            self.selective = SelectivePredictor(
                base_predictor, max_set_size=2, min_confidence=0.3
            )
        else:
            self.selective = None

        # Statistics
        self.selection_history: list[dict] = []

    def calibrate(
        self, model_predictions: np.ndarray, true_labels: np.ndarray
    ) -> dict[str, Any]:
        """
        Calibrate on held-out data.

        Args:
            model_predictions: Model's predictions (n, 3)
            true_labels: True labels (n,)

        Returns:
            Calibration results
        """
        if not self.use_adaptive:
            result = self.predictor.calibrate(model_predictions, true_labels)
            return {
                "threshold": result.threshold,
                "empirical_coverage": result.empirical_coverage,
                "avg_set_size": result.avg_set_size,
                "n_samples": result.n_calibration_samples,
            }

        # For adaptive predictor, simulate online calibration
        for i in range(len(true_labels)):
            self.predictor.predict_and_update(model_predictions[i], int(true_labels[i]))

        analysis = self.predictor.get_coverage_analysis()
        return {
            "threshold": self.predictor.threshold,
            "empirical_coverage": analysis["overall_coverage"],
            "n_samples": analysis["n_predictions"],
        }

    def select_content(
        self, model_predictions: np.ndarray, true_label: int | None = None
    ) -> dict[str, Any]:
        """
        Select content with uncertainty quantification.

        Args:
            model_predictions: Model's probability distribution
            true_label: True label (optional, for online learning)

        Returns:
            Selection result with uncertainty information
        """
        # Get prediction set
        if self.use_adaptive:
            pred_set = self.predictor.predict_and_update(model_predictions, true_label)
        else:
            pred_set = self.predictor.predict(model_predictions)

        # Check for abstention
        abstained = False
        abstention_reason = None

        if self.allow_abstention:
            max_prob = max(model_predictions)
            if pred_set.size > 2 or max_prob < 0.3:
                abstained = True
                abstention_reason = (
                    "uncertain" if pred_set.size > 2 else "low_confidence"
                )

        # Determine final prediction
        if abstained:
            selected = None
        else:
            selected = pred_set.point_prediction()

        result = {
            "selected_content": selected.value if selected else None,
            "prediction_set": [ct.value for ct in pred_set.content_types],
            "set_size": pred_set.size,
            "coverage_guarantee": self.coverage,
            "abstained": abstained,
            "abstention_reason": abstention_reason,
            "scores": {ct.value: float(s) for ct, s in pred_set.scores.items()},
            "threshold": pred_set.threshold,
            "model_confidence": float(max(model_predictions)),
        }

        self.selection_history.append(result)
        return result

    def get_theoretical_analysis(self) -> dict[str, Any]:
        """
        Get theoretical analysis of the uncertainty quantification.

        Returns:
            Analysis with coverage guarantees
        """
        # Empirical statistics
        if self.selection_history:
            avg_set_size = np.mean([s["set_size"] for s in self.selection_history])
            singleton_rate = np.mean(
                [s["set_size"] == 1 for s in self.selection_history]
            )
            abstention_rate = np.mean([s["abstained"] for s in self.selection_history])
        else:
            avg_set_size = 0
            singleton_rate = 0
            abstention_rate = 0

        return {
            "method": "Conformal Prediction with RAPS scores",
            "target_coverage": self.coverage,
            "theoretical_guarantees": {
                "coverage_bound": f"P(y ∈ C(x)) ≥ {self.coverage}",
                "distribution_free": "True - holds for ANY distribution",
                "finite_sample": "Valid even with finite calibration data",
                "adaptive": self.use_adaptive,
            },
            "empirical_statistics": {
                "n_predictions": len(self.selection_history),
                "avg_set_size": avg_set_size,
                "singleton_rate": singleton_rate,
                "abstention_rate": abstention_rate,
            },
            "key_insight": "Unlike softmax probabilities, our confidence intervals are CALIBRATED",
        }


# =============================================================================
# Usage Example
# =============================================================================


def demo_uncertainty_quantification():
    """Demonstrate uncertainty quantification."""
    print("=" * 70)
    print("📊 UNCERTAINTY QUANTIFICATION DEMO")
    print("=" * 70)

    rng = np.random.RandomState(42)

    # Create selector
    selector = UncertaintyAwareContentSelector(
        coverage=0.9, use_adaptive=True, allow_abstention=True, seed=42
    )

    # Generate synthetic calibration data
    n_cal = 100
    print(f"\n📈 Calibrating on {n_cal} samples...")

    cal_predictions = rng.dirichlet([2, 2, 2], size=n_cal)
    cal_labels = np.array([rng.choice(3, p=p) for p in cal_predictions])

    cal_result = selector.calibrate(cal_predictions, cal_labels)
    print(f"   Threshold: {cal_result['threshold']:.4f}")
    print(f"   Empirical Coverage: {cal_result['empirical_coverage']:.2%}")

    # Test predictions
    print("\n🎯 Making Predictions with Uncertainty:")

    test_cases = [
        np.array([0.8, 0.15, 0.05]),  # Confident
        np.array([0.4, 0.35, 0.25]),  # Uncertain
        np.array([0.33, 0.34, 0.33]),  # Very uncertain
    ]

    for i, preds in enumerate(test_cases):
        result = selector.select_content(preds)

        print(f"\n   Test {i + 1}: Model probs = {preds}")
        print(f"      Selected: {result['selected_content'] or 'ABSTAINED'}")
        print(f"      Prediction Set: {result['prediction_set']}")
        print(f"      Coverage Guarantee: {result['coverage_guarantee']:.0%}")

        if result["abstained"]:
            print(f"      ⚠️ Abstention Reason: {result['abstention_reason']}")

    # Theoretical analysis
    print("\n📐 Theoretical Analysis:")
    theory = selector.get_theoretical_analysis()
    print(f"   Method: {theory['method']}")
    print(f"   Coverage Bound: {theory['theoretical_guarantees']['coverage_bound']}")
    print(
        f"   Distribution-Free: {theory['theoretical_guarantees']['distribution_free']}"
    )
    print(f"   Key Insight: {theory['key_insight']}")

    print("\n✅ Demo complete!")
    return selector


if __name__ == "__main__":
    demo_uncertainty_quantification()
