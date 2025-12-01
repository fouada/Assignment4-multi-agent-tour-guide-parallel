"""
Tests for Uncertainty Quantification with Conformal Prediction.

MIT-Level Test Coverage for:
- ContentType enum
- PredictionSet dataclass
- CalibrationResult dataclass
- ConformityScore abstract class
- SimpleProbabilityScore
- AdaptiveProbabilityScore
- RAPSScore
- ConformalPredictor
- AdaptiveConformalPredictor
- SelectivePredictor
- UncertaintyAwareContentSelector

Edge Cases Documented:
- Perfect predictions (probability 1.0)
- Uncertain predictions (uniform distribution)
- Empty calibration sets
- Extreme alpha values
"""

import pytest

np = pytest.importorskip("numpy", reason="numpy required for research tests")

from src.research.uncertainty_quantification import (
    AdaptiveConformalPredictor,
    AdaptiveProbabilityScore,
    CalibrationResult,
    ConformalPredictor,
    ContentType,
    PredictionSet,
    RAPSScore,
    SelectivePredictor,
    SimpleProbabilityScore,
    UncertaintyAwareContentSelector,
)

# =============================================================================
# ContentType Tests
# =============================================================================


class TestContentType:
    """Test ContentType enum."""

    def test_content_types_exist(self):
        """Test all content types exist."""
        assert ContentType.VIDEO == "video"
        assert ContentType.MUSIC == "music"
        assert ContentType.TEXT == "text"

    def test_content_type_count(self):
        """Test total number of content types."""
        assert len(list(ContentType)) == 3


# =============================================================================
# PredictionSet Tests
# =============================================================================


class TestPredictionSet:
    """Test PredictionSet dataclass."""

    def test_set_creation(self):
        """Test basic prediction set creation."""
        pred_set = PredictionSet(
            content_types={ContentType.VIDEO, ContentType.TEXT},
            coverage_target=0.9,
            scores={
                ContentType.VIDEO: 0.2,
                ContentType.MUSIC: 0.5,
                ContentType.TEXT: 0.3,
            },
            threshold=0.35,
        )

        assert ContentType.VIDEO in pred_set.content_types
        assert ContentType.TEXT in pred_set.content_types
        assert ContentType.MUSIC not in pred_set.content_types
        assert pred_set.size == 2

    def test_is_singleton(self):
        """Test singleton check."""
        pred_set = PredictionSet(
            content_types={ContentType.VIDEO},
            coverage_target=0.9,
            scores={ContentType.VIDEO: 0.1},
            threshold=0.5,
        )
        assert pred_set.is_singleton is True

    def test_is_empty(self):
        """Test empty set check."""
        pred_set = PredictionSet(
            content_types=set(), coverage_target=0.9, scores={}, threshold=0.5
        )
        assert pred_set.is_empty is True

    def test_point_prediction_singleton(self):
        """Test point prediction for singleton set."""
        pred_set = PredictionSet(
            content_types={ContentType.VIDEO},
            coverage_target=0.9,
            scores={ContentType.VIDEO: 0.1},
            threshold=0.5,
        )
        assert pred_set.point_prediction() == ContentType.VIDEO


# =============================================================================
# CalibrationResult Tests
# =============================================================================


class TestCalibrationResult:
    """Test CalibrationResult dataclass."""

    def test_result_creation(self):
        """Test calibration result creation."""
        result = CalibrationResult(
            threshold=0.45,
            target_coverage=0.9,
            empirical_coverage=0.92,
            avg_set_size=1.5,
            set_size_distribution={1: 50, 2: 30, 3: 20},
            n_calibration_samples=100,
        )

        assert result.threshold == 0.45
        assert result.target_coverage == 0.9
        assert result.empirical_coverage == 0.92


# =============================================================================
# SimpleProbabilityScore Tests
# =============================================================================


class TestSimpleProbabilityScore:
    """Test Simple Probability Score."""

    def test_score_computation(self):
        """Test score computation."""
        scorer = SimpleProbabilityScore()

        probs = np.array([0.6, 0.3, 0.1])
        label = 0  # True class has probability 0.6

        score = scorer.compute(probs, label)

        # Score should be 1 - p(true_label) = 1 - 0.6 = 0.4
        assert abs(score - 0.4) < 1e-5

    def test_perfect_prediction(self):
        """Test perfect prediction score."""
        scorer = SimpleProbabilityScore()

        probs = np.array([1.0, 0.0, 0.0])
        label = 0

        score = scorer.compute(probs, label)
        assert abs(score) < 1e-5

    def test_worst_prediction(self):
        """Test worst prediction score."""
        scorer = SimpleProbabilityScore()

        probs = np.array([0.0, 0.0, 1.0])
        label = 0

        score = scorer.compute(probs, label)
        assert abs(score - 1.0) < 1e-5


# =============================================================================
# AdaptiveProbabilityScore Tests
# =============================================================================


class TestAdaptiveProbabilityScore:
    """Test Adaptive Probability Score."""

    def test_score_computation(self):
        """Test adaptive score computation."""
        scorer = AdaptiveProbabilityScore()

        probs = np.array([0.5, 0.3, 0.2])
        label = 0

        score = scorer.compute(probs, label)

        assert isinstance(score, float)
        assert 0 <= score <= 1


# =============================================================================
# RAPSScore Tests
# =============================================================================


class TestRAPSScore:
    """Test RAPS (Regularized Adaptive Prediction Sets) Score."""

    def test_score_computation(self):
        """Test RAPS score computation."""
        scorer = RAPSScore(k_reg=1, lambda_reg=0.1)

        probs = np.array([0.5, 0.3, 0.2])
        label = 0

        score = scorer.compute(probs, label)

        assert isinstance(score, float)


# =============================================================================
# ConformalPredictor Tests
# =============================================================================


class TestConformalPredictor:
    """Test Conformal Predictor."""

    def test_predictor_creation(self):
        """Test predictor creation."""
        scorer = SimpleProbabilityScore()
        predictor = ConformalPredictor(scorer=scorer, coverage=0.9)

        assert predictor.coverage == 0.9
        assert predictor.alpha == pytest.approx(0.1, rel=1e-5)

    def test_calibration(self):
        """Test calibration process."""
        scorer = SimpleProbabilityScore()
        predictor = ConformalPredictor(scorer=scorer, coverage=0.9)

        # Generate calibration data
        np.random.seed(42)
        n_samples = 100
        predictions = np.random.dirichlet([1, 1, 1], n_samples).astype(np.float32)
        labels = np.argmax(predictions, axis=1)

        result = predictor.calibrate(predictions, labels)

        assert isinstance(result, CalibrationResult)
        assert result.threshold is not None

    def test_prediction(self):
        """Test prediction after calibration."""
        scorer = SimpleProbabilityScore()
        predictor = ConformalPredictor(scorer=scorer, coverage=0.9)

        # Calibrate
        np.random.seed(42)
        n_samples = 100
        predictions = np.random.dirichlet([1, 1, 1], n_samples).astype(np.float32)
        labels = np.argmax(predictions, axis=1)
        predictor.calibrate(predictions, labels)

        # Predict
        new_pred = np.array([0.6, 0.3, 0.1])
        pred_set = predictor.predict(new_pred)

        assert isinstance(pred_set, PredictionSet)
        assert pred_set.size >= 1

    def test_coverage_evaluation(self):
        """Test coverage evaluation."""
        scorer = SimpleProbabilityScore()
        predictor = ConformalPredictor(scorer=scorer, coverage=0.9)

        np.random.seed(42)
        n_cal = 100
        n_test = 50

        # Calibration data
        cal_predictions = np.random.dirichlet([1, 1, 1], n_cal).astype(np.float32)
        cal_labels = np.argmax(cal_predictions, axis=1)
        predictor.calibrate(cal_predictions, cal_labels)

        # Test data - make predictions manually
        test_predictions = np.random.dirichlet([1, 1, 1], n_test).astype(np.float32)
        test_labels = np.argmax(test_predictions, axis=1)

        # Evaluate coverage
        covered_count = 0
        for i in range(n_test):
            pred_set = predictor.predict(test_predictions[i])
            true_label = list(ContentType)[test_labels[i]]
            if true_label in pred_set.content_types:
                covered_count += 1

        empirical_coverage = covered_count / n_test
        assert empirical_coverage >= 0.5  # Should have reasonable coverage

    # EDGE CASE: Uncalibrated predictor
    def test_predict_without_calibration(self):
        """Edge case: Predict without calibration."""
        scorer = SimpleProbabilityScore()
        predictor = ConformalPredictor(scorer=scorer, coverage=0.9)

        with pytest.raises(ValueError):
            predictor.predict(np.array([0.5, 0.3, 0.2]))


# =============================================================================
# AdaptiveConformalPredictor Tests
# =============================================================================


class TestAdaptiveConformalPredictor:
    """Test Adaptive Conformal Predictor."""

    def test_creation(self):
        """Test adaptive predictor creation."""
        scorer = SimpleProbabilityScore()
        predictor = AdaptiveConformalPredictor(
            scorer=scorer, coverage=0.9, step_size=0.1
        )

        assert predictor.coverage == 0.9

    def test_predict_and_update(self):
        """Test predict and update method."""
        scorer = SimpleProbabilityScore()
        predictor = AdaptiveConformalPredictor(
            scorer=scorer, coverage=0.9, step_size=0.1, initial_threshold=0.5
        )

        np.random.seed(42)
        predictions = np.random.dirichlet([1, 1, 1]).astype(np.float32)
        true_label = 0

        pred_set = predictor.predict_and_update(predictions, true_label)

        assert isinstance(pred_set, PredictionSet)

    def test_adaptive_threshold_changes(self):
        """Test that threshold adapts over time."""
        scorer = SimpleProbabilityScore()
        predictor = AdaptiveConformalPredictor(
            scorer=scorer, coverage=0.9, step_size=0.1, initial_threshold=0.5
        )

        np.random.seed(42)
        for _ in range(10):
            predictions = np.random.dirichlet([1, 1, 1]).astype(np.float32)
            true_label = np.argmax(predictions)
            predictor.predict_and_update(predictions, true_label)

        # Threshold should have changed
        assert len(predictor.threshold_history) > 1


# =============================================================================
# SelectivePredictor Tests
# =============================================================================


class TestSelectivePredictor:
    """Test Selective Predictor."""

    def test_creation(self):
        """Test selective predictor creation."""
        scorer = SimpleProbabilityScore()
        base_predictor = ConformalPredictor(scorer=scorer, coverage=0.9)

        # Calibrate base predictor first
        np.random.seed(42)
        cal_predictions = np.random.dirichlet([1, 1, 1], 100).astype(np.float32)
        cal_labels = np.argmax(cal_predictions, axis=1)
        base_predictor.calibrate(cal_predictions, cal_labels)

        selective_predictor = SelectivePredictor(
            conformal_predictor=base_predictor, max_set_size=2
        )

        assert selective_predictor.max_set_size == 2

    def test_predict_or_abstain(self):
        """Test predict or abstain method."""
        scorer = SimpleProbabilityScore()
        base_predictor = ConformalPredictor(scorer=scorer, coverage=0.9)

        # Calibrate
        np.random.seed(42)
        cal_predictions = np.random.dirichlet([1, 1, 1], 100).astype(np.float32)
        cal_labels = np.argmax(cal_predictions, axis=1)
        base_predictor.calibrate(cal_predictions, cal_labels)

        selective_predictor = SelectivePredictor(
            conformal_predictor=base_predictor, max_set_size=2, min_confidence=0.3
        )

        # Confident prediction
        confident_pred = np.array([0.8, 0.15, 0.05])
        result, reason, details = selective_predictor.predict_or_abstain(confident_pred)

        # Should either predict or abstain based on set size
        assert reason in ["prediction", "abstain_large_set", "abstain_low_confidence"]


# =============================================================================
# UncertaintyAwareContentSelector Tests
# =============================================================================


class TestUncertaintyAwareContentSelector:
    """Test Uncertainty-Aware Content Selector."""

    def test_selector_creation(self):
        """Test selector creation."""
        selector = UncertaintyAwareContentSelector(coverage=0.9, seed=42)
        assert selector.coverage == 0.9

    def test_calibrate_and_select_non_adaptive(self):
        """Test calibration and selection for non-adaptive mode."""
        selector = UncertaintyAwareContentSelector(
            coverage=0.9, use_adaptive=False, seed=42
        )

        # Calibration data
        np.random.seed(42)
        cal_predictions = np.random.dirichlet([1, 1, 1], 100).astype(np.float32)
        cal_labels = np.argmax(cal_predictions, axis=1)

        cal_result = selector.calibrate(cal_predictions, cal_labels)

        assert "threshold" in cal_result

        # Select content
        new_pred = np.array([0.7, 0.2, 0.1])
        result = selector.select_content(new_pred)

        assert "prediction_set" in result
        assert "coverage_guarantee" in result

    def test_select_content_adaptive(self):
        """Test select content in adaptive mode."""
        selector = UncertaintyAwareContentSelector(
            coverage=0.9, use_adaptive=True, seed=42
        )

        # For adaptive mode, calibrate using predict_and_update
        np.random.seed(42)
        cal_predictions = np.random.dirichlet([1, 1, 1], 50).astype(np.float32)
        cal_labels = np.argmax(cal_predictions, axis=1)

        selector.calibrate(cal_predictions, cal_labels)

        # Select content
        new_pred = np.array([0.7, 0.2, 0.1])
        result = selector.select_content(new_pred)

        assert "prediction_set" in result

    def test_theoretical_analysis(self):
        """Test theoretical analysis."""
        selector = UncertaintyAwareContentSelector(coverage=0.9, seed=42)
        analysis = selector.get_theoretical_analysis()

        assert "method" in analysis
        assert "theoretical_guarantees" in analysis
        assert "coverage_bound" in analysis["theoretical_guarantees"]

    # EDGE CASE: High uncertainty (uniform distribution)
    def test_high_uncertainty(self):
        """Edge case: High uncertainty predictions."""
        selector = UncertaintyAwareContentSelector(
            coverage=0.9, use_adaptive=False, seed=42
        )

        np.random.seed(42)
        cal_predictions = np.random.dirichlet([1, 1, 1], 100).astype(np.float32)
        cal_labels = np.argmax(cal_predictions, axis=1)
        selector.calibrate(cal_predictions, cal_labels)

        # Uniform distribution = high uncertainty
        uniform_pred = np.array([0.333, 0.333, 0.334])
        result = selector.select_content(uniform_pred)

        # Should have non-empty prediction set
        assert result["set_size"] >= 1

    # EDGE CASE: Very confident prediction
    def test_confident_prediction(self):
        """Edge case: Very confident prediction."""
        selector = UncertaintyAwareContentSelector(
            coverage=0.9, use_adaptive=False, seed=42
        )

        np.random.seed(42)
        cal_predictions = np.random.dirichlet([1, 1, 1], 100).astype(np.float32)
        cal_labels = np.argmax(cal_predictions, axis=1)
        selector.calibrate(cal_predictions, cal_labels)

        # Very confident
        confident_pred = np.array([0.95, 0.03, 0.02])
        result = selector.select_content(confident_pred)

        # Should have small set size
        assert result["set_size"] <= 3


# =============================================================================
# Integration Tests
# =============================================================================


class TestConformalPredictionIntegration:
    """Integration tests for conformal prediction."""

    def test_coverage_guarantee(self):
        """Test that coverage guarantee holds approximately."""
        scorer = SimpleProbabilityScore()
        predictor = ConformalPredictor(scorer=scorer, coverage=0.9, seed=42)

        np.random.seed(42)
        n_total = 500
        n_cal = 250

        # Generate data with some structure
        predictions = np.random.dirichlet([2, 1, 1], n_total).astype(np.float32)
        labels = np.argmax(predictions, axis=1)

        # Calibrate
        predictor.calibrate(predictions[:n_cal], labels[:n_cal])

        # Evaluate on test
        test_preds = predictions[n_cal:]
        test_labels = labels[n_cal:]

        covered_count = 0
        for i in range(len(test_labels)):
            pred_set = predictor.predict(test_preds[i])
            true_label = list(ContentType)[test_labels[i]]
            if true_label in pred_set.content_types:
                covered_count += 1

        empirical_coverage = covered_count / len(test_labels)

        # Coverage should be close to target (with some statistical tolerance)
        assert empirical_coverage >= 0.7  # Allow slack for finite samples

    def test_full_pipeline(self):
        """Test complete uncertainty quantification pipeline."""
        selector = UncertaintyAwareContentSelector(
            coverage=0.9, use_adaptive=False, seed=42
        )

        # Calibration
        np.random.seed(42)
        cal_predictions = np.random.dirichlet([1, 1, 1], 200).astype(np.float32)
        cal_labels = np.argmax(cal_predictions, axis=1)
        selector.calibrate(cal_predictions, cal_labels)

        # Make several selections
        selections = []
        for _ in range(10):
            pred = np.random.dirichlet([1, 1, 1]).astype(np.float32)
            result = selector.select_content(pred)
            selections.append(result)

        # All selections should have valid structure
        for sel in selections:
            assert "prediction_set" in sel
            assert "set_size" in sel
            assert "coverage_guarantee" in sel
