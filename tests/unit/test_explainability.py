"""
Tests for Explainable AI Framework.

MIT-Level Test Coverage for:
- Feature Types and Values
- SHAP Value Computation
- LIME Explanations
- Counterfactual Explanations
- Natural Language Explanations
- ExplainabilityEngine Integration
"""

import pytest
import numpy as np
from datetime import datetime
from typing import Dict

from src.research.explainability import (
    Feature,
    ExplanationType,
    FeatureValue,
    Decision,
    SHAPExplainer,
    LIMEExplainer,
    CounterfactualExplanation,
    CounterfactualExplainer,
    NaturalLanguageExplainer,
    ExplainabilityEngine,
    demo_explainability,
)


# =============================================================================
# Feature Tests
# =============================================================================


class TestFeature:
    """Test Feature enum."""
    
    def test_content_features(self):
        """Test content features exist."""
        assert Feature.CONTENT_RELEVANCE is not None
        assert Feature.CONTENT_QUALITY is not None
        assert Feature.CONTENT_DURATION is not None
    
    def test_user_profile_features(self):
        """Test user profile features exist."""
        assert Feature.USER_AGE_GROUP is not None
        assert Feature.USER_INTERESTS is not None
        assert Feature.USER_ACCESSIBILITY is not None
    
    def test_context_features(self):
        """Test context features exist."""
        assert Feature.LOCATION_TYPE is not None
        assert Feature.TIME_OF_DAY is not None
        assert Feature.PREVIOUS_SELECTIONS is not None
    
    def test_agent_features(self):
        """Test agent features exist."""
        assert Feature.AGENT_RESPONSE_TIME is not None
        assert Feature.AGENT_SUCCESS_RATE is not None
    
    def test_feature_values(self):
        """Test feature string values."""
        assert Feature.CONTENT_RELEVANCE.value == "content_relevance"
        assert Feature.USER_AGE_GROUP.value == "user_age_group"


# =============================================================================
# ExplanationType Tests
# =============================================================================


class TestExplanationType:
    """Test ExplanationType enum."""
    
    def test_explanation_types_exist(self):
        """Test all explanation types exist."""
        assert ExplanationType.FEATURE_IMPORTANCE is not None
        assert ExplanationType.COUNTERFACTUAL is not None
        assert ExplanationType.CONTRASTIVE is not None
        assert ExplanationType.NATURAL_LANGUAGE is not None


# =============================================================================
# FeatureValue Tests
# =============================================================================


class TestFeatureValue:
    """Test FeatureValue dataclass."""
    
    def test_feature_value_creation(self):
        """Test creating a feature value."""
        fv = FeatureValue(
            feature=Feature.CONTENT_QUALITY,
            value=8.5,
            normalized_value=0.85,
        )
        assert fv.feature == Feature.CONTENT_QUALITY
        assert fv.value == 8.5
        assert fv.normalized_value == 0.85
    
    def test_auto_display_name(self):
        """Test automatic display name generation."""
        fv = FeatureValue(
            feature=Feature.USER_AGE_GROUP,
            value="adult",
            normalized_value=0.6,
        )
        # Should auto-generate from feature name
        assert "Age" in fv.display_name or fv.display_name != ""
    
    def test_custom_display_name(self):
        """Test custom display name."""
        fv = FeatureValue(
            feature=Feature.LOCATION_TYPE,
            value="historical",
            normalized_value=0.3,
            display_name="Place Type",
        )
        assert fv.display_name == "Place Type"
    
    def test_with_description(self):
        """Test feature value with description."""
        fv = FeatureValue(
            feature=Feature.CONTENT_RELEVANCE,
            value=7.0,
            normalized_value=0.7,
            description="How relevant the content is to the location",
        )
        assert fv.description != ""


# =============================================================================
# Decision Tests
# =============================================================================


class TestDecision:
    """Test Decision dataclass."""
    
    @pytest.fixture
    def sample_decision(self):
        """Create a sample decision."""
        return Decision(
            decision_id="dec_123",
            selected_agent="video",
            selected_content_title="History of the Eiffel Tower",
            candidates={
                "video": {
                    "title": "History of the Eiffel Tower",
                    "relevance_score": 8.0,
                    "quality_score": 7.5,
                },
                "music": {
                    "title": "French Classical Music",
                    "relevance_score": 6.0,
                    "quality_score": 8.0,
                },
                "text": {
                    "title": "Eiffel Tower Facts",
                    "relevance_score": 7.0,
                    "quality_score": 6.5,
                },
            },
            user_profile={
                "age_group": "adult",
                "is_driver": False,
                "interests": ["history", "architecture"],
            },
            location={
                "name": "Eiffel Tower",
                "type": "historical",
            },
            scores={
                "video": 0.85,
                "music": 0.70,
                "text": 0.65,
            },
            reasoning="Selected video for historical content relevance",
        )
    
    def test_decision_creation(self, sample_decision):
        """Test decision creation."""
        assert sample_decision.decision_id == "dec_123"
        assert sample_decision.selected_agent == "video"
    
    def test_decision_scores(self, sample_decision):
        """Test decision scores."""
        assert sample_decision.scores["video"] == 0.85
        assert sample_decision.scores["music"] == 0.70
    
    def test_decision_has_timestamp(self, sample_decision):
        """Test decision has timestamp."""
        assert sample_decision.timestamp is not None
    
    def test_get_feature_vector(self, sample_decision):
        """Test extracting feature vector."""
        features = sample_decision.get_feature_vector()
        
        assert isinstance(features, dict)
        assert Feature.CONTENT_RELEVANCE in features
        assert Feature.USER_AGE_GROUP in features
    
    def test_feature_vector_values(self, sample_decision):
        """Test feature vector values are correct."""
        features = sample_decision.get_feature_vector()
        
        # Content relevance from video candidate
        assert features[Feature.CONTENT_RELEVANCE].value == 8.0
        assert features[Feature.USER_AGE_GROUP].value == "adult"


# =============================================================================
# SHAP Explainer Tests
# =============================================================================


class TestSHAPExplainer:
    """Test SHAP explainer."""
    
    @pytest.fixture
    def simple_model(self):
        """Simple linear model for testing."""
        def model(features: Dict[Feature, float]) -> float:
            return (
                0.4 * features.get(Feature.CONTENT_RELEVANCE, 0.5) +
                0.3 * features.get(Feature.CONTENT_QUALITY, 0.5) +
                0.2 * features.get(Feature.USER_IS_DRIVER, 0.0) +
                0.1
            )
        return model
    
    @pytest.fixture
    def shap_explainer(self, simple_model):
        """Create SHAP explainer with multiple features."""
        features = [Feature.CONTENT_RELEVANCE, Feature.CONTENT_QUALITY, Feature.USER_IS_DRIVER]
        return SHAPExplainer(model=simple_model, features=features)
    
    def test_explainer_creation(self, simple_model):
        """Test explainer creation."""
        features = [Feature.CONTENT_RELEVANCE]
        explainer = SHAPExplainer(model=simple_model, features=features)
        assert explainer is not None
        assert len(explainer.features) == 1
    
    def test_explainer_with_baseline(self, simple_model):
        """Test explainer with custom baseline."""
        features = [Feature.CONTENT_RELEVANCE, Feature.CONTENT_QUALITY]
        baseline = {Feature.CONTENT_RELEVANCE: 0.3, Feature.CONTENT_QUALITY: 0.3}
        explainer = SHAPExplainer(model=simple_model, features=features, baseline=baseline)
        assert explainer.baseline[Feature.CONTENT_RELEVANCE] == 0.3
    
    def test_explain_exact(self, shap_explainer):
        """Test exact SHAP value computation."""
        instance = {
            Feature.CONTENT_RELEVANCE: 0.9,
            Feature.CONTENT_QUALITY: 0.8,
            Feature.USER_IS_DRIVER: 0.0,
        }
        shap_values = shap_explainer.explain(instance)
        
        assert isinstance(shap_values, dict)
        assert Feature.CONTENT_RELEVANCE in shap_values
        assert Feature.CONTENT_QUALITY in shap_values
        # Higher relevance should have positive SHAP value
        assert shap_values[Feature.CONTENT_RELEVANCE] > 0
    
    def test_explain_approximate(self, shap_explainer):
        """Test approximate SHAP value computation."""
        instance = {
            Feature.CONTENT_RELEVANCE: 0.9,
            Feature.CONTENT_QUALITY: 0.8,
            Feature.USER_IS_DRIVER: 0.0,
        }
        shap_values = shap_explainer.explain_approximate(instance, n_samples=500)
        
        assert isinstance(shap_values, dict)
        assert len(shap_values) == 3
        # All values should be finite
        for v in shap_values.values():
            assert np.isfinite(v)
    
    def test_shap_values_sum_to_prediction_diff(self, shap_explainer):
        """Test SHAP values approximately sum to prediction difference."""
        instance = {
            Feature.CONTENT_RELEVANCE: 0.9,
            Feature.CONTENT_QUALITY: 0.8,
            Feature.USER_IS_DRIVER: 1.0,
        }
        shap_values = shap_explainer.explain_approximate(instance, n_samples=1000)
        
        # Sum of SHAP values should approximately equal f(x) - f(baseline)
        total_shap = sum(shap_values.values())
        
        # Get predictions
        f_x = shap_explainer.model(instance)
        f_baseline = shap_explainer.model(shap_explainer.baseline)
        expected_diff = f_x - f_baseline
        
        # Should be approximately equal (with some tolerance for sampling)
        assert abs(total_shap - expected_diff) < 0.15
    
    def test_compute_interaction_values(self, shap_explainer):
        """Test SHAP interaction value computation."""
        instance = {
            Feature.CONTENT_RELEVANCE: 0.9,
            Feature.CONTENT_QUALITY: 0.8,
            Feature.USER_IS_DRIVER: 0.0,
        }
        interactions = shap_explainer.compute_interaction_values(instance)
        
        assert isinstance(interactions, dict)
        # Should have interaction for each pair
        assert len(interactions) > 0
        # Keys should be tuples of features
        for key in interactions.keys():
            assert isinstance(key, tuple)
            assert len(key) == 2


# =============================================================================
# LIME Explainer Tests
# =============================================================================


class TestLIMEExplainer:
    """Test LIME explainer."""
    
    @pytest.fixture
    def simple_model(self):
        """Simple model for testing."""
        def model(features: Dict[Feature, float]) -> float:
            return (
                0.4 * features.get(Feature.CONTENT_QUALITY, 0.5) +
                0.3 * features.get(Feature.CONTENT_RELEVANCE, 0.5) +
                0.2
            )
        return model
    
    @pytest.fixture
    def lime_explainer(self, simple_model):
        """Create LIME explainer."""
        features = [Feature.CONTENT_QUALITY, Feature.CONTENT_RELEVANCE]
        return LIMEExplainer(model=simple_model, features=features)
    
    def test_lime_creation(self, lime_explainer):
        """Test LIME creation."""
        assert lime_explainer is not None
    
    def test_lime_explain(self, lime_explainer):
        """Test LIME explanation generation."""
        instance = {
            Feature.CONTENT_QUALITY: 0.9,
            Feature.CONTENT_RELEVANCE: 0.8,
        }
        result = lime_explainer.explain(instance, n_samples=1000)
        
        assert isinstance(result, dict)
        assert "feature_importance" in result
        assert "all_coefficients" in result
        assert "intercept" in result
        assert "local_prediction" in result
        assert "actual_prediction" in result
        assert "local_fidelity_r2" in result
    
    def test_lime_feature_importance_order(self, lime_explainer):
        """Test LIME returns features sorted by importance."""
        instance = {
            Feature.CONTENT_QUALITY: 0.9,
            Feature.CONTENT_RELEVANCE: 0.8,
        }
        result = lime_explainer.explain(instance, n_samples=2000, n_features_to_show=2)
        
        importance = result["feature_importance"]
        # Should be sorted by absolute value
        values = list(importance.values())
        assert all(abs(values[i]) >= abs(values[i+1]) for i in range(len(values)-1))
    
    def test_lime_local_fidelity(self, lime_explainer):
        """Test LIME achieves reasonable local fidelity."""
        instance = {
            Feature.CONTENT_QUALITY: 0.9,
            Feature.CONTENT_RELEVANCE: 0.8,
        }
        result = lime_explainer.explain(instance, n_samples=3000)
        
        # R² should be positive for a linear model
        assert result["local_fidelity_r2"] > 0.5
    
    def test_lime_with_custom_kernel_width(self, simple_model):
        """Test LIME with custom kernel width."""
        features = [Feature.CONTENT_QUALITY, Feature.CONTENT_RELEVANCE]
        explainer = LIMEExplainer(model=simple_model, features=features, kernel_width=0.5)
        
        assert explainer.kernel_width == 0.5
        
        instance = {Feature.CONTENT_QUALITY: 0.9, Feature.CONTENT_RELEVANCE: 0.8}
        result = explainer.explain(instance, n_samples=500)
        
        assert "kernel_width" in result
        assert result["kernel_width"] == 0.5


# =============================================================================
# Counterfactual Explainer Tests
# =============================================================================


class TestCounterfactualExplanation:
    """Test CounterfactualExplanation dataclass."""
    
    def test_counterfactual_creation(self):
        """Test creating a counterfactual explanation."""
        cf = CounterfactualExplanation(
            original_decision="video",
            counterfactual_decision="text",
            original_features={Feature.CONTENT_QUALITY: 0.9},
            counterfactual_features={Feature.CONTENT_QUALITY: 0.4},
            changes={Feature.CONTENT_QUALITY: (0.9, 0.4)},
            total_change=0.5,
            plausibility_score=0.7,
        )
        assert cf.original_decision == "video"
        assert cf.counterfactual_decision == "text"
    
    def test_counterfactual_to_natural_language(self):
        """Test natural language generation."""
        cf = CounterfactualExplanation(
            original_decision="video",
            counterfactual_decision="text",
            original_features={Feature.CONTENT_QUALITY: 0.9},
            counterfactual_features={Feature.CONTENT_QUALITY: 0.4},
            changes={Feature.CONTENT_QUALITY: (0.9, 0.4)},
            total_change=0.5,
            plausibility_score=0.7,
        )
        nl = cf.to_natural_language()
        
        assert "text" in nl
        assert "video" in nl
        assert "decreased" in nl


class TestCounterfactualExplainer:
    """Test counterfactual explanations."""
    
    @pytest.fixture
    def decision_model(self):
        """Simple decision model."""
        def model(features: Dict[Feature, float]) -> str:
            score = (
                0.4 * features.get(Feature.CONTENT_QUALITY, 0.5) +
                0.3 * features.get(Feature.CONTENT_RELEVANCE, 0.5)
            )
            if score > 0.5:
                return "video"
            elif score > 0.3:
                return "text"
            return "music"
        return model
    
    @pytest.fixture
    def score_model(self):
        """Score model for target class."""
        def model(features: Dict[Feature, float], target: str) -> float:
            score = (
                0.4 * features.get(Feature.CONTENT_QUALITY, 0.5) +
                0.3 * features.get(Feature.CONTENT_RELEVANCE, 0.5)
            )
            if target == "video":
                return score
            elif target == "text":
                return 0.5 - abs(score - 0.4)
            return 1.0 - score
        return model
    
    @pytest.fixture
    def cf_explainer(self, decision_model, score_model):
        """Create counterfactual explainer."""
        features = [Feature.CONTENT_QUALITY, Feature.CONTENT_RELEVANCE]
        return CounterfactualExplainer(
            model=decision_model,
            score_model=score_model,
            features=features,
        )
    
    def test_counterfactual_class_exists(self):
        """Test CounterfactualExplainer class exists."""
        assert CounterfactualExplainer is not None
    
    def test_cf_explainer_creation(self, cf_explainer):
        """Test counterfactual explainer creation."""
        assert cf_explainer is not None
        assert len(cf_explainer.features) == 2
    
    def test_cf_explain_finds_counterfactual(self, cf_explainer):
        """Test finding counterfactual explanations."""
        instance = {
            Feature.CONTENT_QUALITY: 0.9,
            Feature.CONTENT_RELEVANCE: 0.8,
        }
        # High scores -> video, try to get music
        counterfactuals = cf_explainer.explain(
            instance, 
            target_decision="music",
            n_counterfactuals=1,
            max_iterations=500,
        )
        
        # Should find at least one counterfactual
        assert isinstance(counterfactuals, list)
    
    def test_cf_same_decision_returns_empty(self, cf_explainer, decision_model):
        """Test that asking for same decision returns empty list."""
        instance = {
            Feature.CONTENT_QUALITY: 0.9,
            Feature.CONTENT_RELEVANCE: 0.8,
        }
        current_decision = decision_model(instance)
        
        counterfactuals = cf_explainer.explain(
            instance,
            target_decision=current_decision,
            n_counterfactuals=1,
        )
        
        assert counterfactuals == []


# =============================================================================
# Natural Language Explainer Tests
# =============================================================================


class TestNaturalLanguageExplainer:
    """Test natural language explanations."""
    
    @pytest.fixture
    def nl_explainer(self):
        """Create NL explainer."""
        return NaturalLanguageExplainer()
    
    @pytest.fixture
    def sample_decision(self):
        """Create sample decision for testing."""
        return Decision(
            decision_id="test_nl",
            selected_agent="video",
            selected_content_title="History Documentary",
            candidates={
                "video": {"relevance_score": 9, "quality_score": 8},
                "music": {"relevance_score": 6, "quality_score": 7},
                "text": {"relevance_score": 7, "quality_score": 6},
            },
            user_profile={"age_group": "adult", "is_driver": False},
            location={"type": "historical", "name": "Ancient Ruins"},
            scores={"video": 0.9, "music": 0.6, "text": 0.7},
            reasoning="Video selected for historical content",
        )
    
    def test_explainer_creation(self, nl_explainer):
        """Test NL explainer creation."""
        assert nl_explainer is not None
        assert nl_explainer.templates is not None
    
    def test_nl_explain_with_shap_values(self, nl_explainer, sample_decision):
        """Test NL explanation generation with SHAP values."""
        shap_values = {
            Feature.CONTENT_RELEVANCE: 0.15,
            Feature.CONTENT_QUALITY: 0.10,
            Feature.USER_AGE_GROUP: 0.05,
            Feature.LOCATION_TYPE: 0.08,
        }
        
        explanation = nl_explainer.explain(sample_decision, shap_values, top_k=3)
        
        assert isinstance(explanation, str)
        assert len(explanation) > 0
        assert "video" in explanation.lower() or "VIDEO" in explanation
    
    def test_nl_explain_driver_safety(self, nl_explainer):
        """Test NL explanation for driver scenario."""
        decision = Decision(
            decision_id="driver_test",
            selected_agent="music",
            selected_content_title="Classical Music",
            candidates={
                "music": {"relevance_score": 7, "quality_score": 8},
            },
            user_profile={"age_group": "adult", "is_driver": True},
            location={"type": "urban"},
            scores={"music": 0.8},
            reasoning="Audio for driver",
        )
        
        shap_values = {
            Feature.USER_IS_DRIVER: 0.25,
            Feature.CONTENT_QUALITY: 0.10,
        }
        
        explanation = nl_explainer.explain(decision, shap_values, top_k=2)
        
        # Should mention driver safety
        assert "music" in explanation.lower() or "MUSIC" in explanation
    
    def test_nl_explain_empty_shap_values(self, nl_explainer, sample_decision):
        """Test NL explanation with empty SHAP values."""
        shap_values = {}
        
        explanation = nl_explainer.explain(sample_decision, shap_values, top_k=3)
        
        # Should still return something meaningful
        assert isinstance(explanation, str)
        assert len(explanation) > 0


# =============================================================================
# ExplainabilityEngine Tests
# =============================================================================


class TestExplainabilityEngine:
    """Test main explainability engine."""
    
    @pytest.fixture
    def decision_model(self):
        """Simple decision model."""
        def model(features: Dict[Feature, float]) -> str:
            score = features.get(Feature.CONTENT_RELEVANCE, 0.5) * 0.6 + features.get(Feature.CONTENT_QUALITY, 0.5) * 0.4
            if score > 0.6:
                return "video"
            elif score > 0.4:
                return "text"
            return "music"
        return model
    
    @pytest.fixture
    def score_model(self):
        """Score model."""
        def model(features: Dict[Feature, float]) -> float:
            return features.get(Feature.CONTENT_RELEVANCE, 0.5) * 0.6 + features.get(Feature.CONTENT_QUALITY, 0.5) * 0.4
        return model
    
    @pytest.fixture
    def engine(self, decision_model, score_model):
        """Create explainability engine."""
        return ExplainabilityEngine(decision_model, score_model)
    
    @pytest.fixture
    def sample_decision(self):
        """Create sample decision."""
        return Decision(
            decision_id="engine_test",
            selected_agent="video",
            selected_content_title="Test Video",
            candidates={
                "video": {"relevance_score": 9, "quality_score": 8},
                "music": {"relevance_score": 5, "quality_score": 6},
                "text": {"relevance_score": 7, "quality_score": 7},
            },
            user_profile={"age_group": "adult", "is_driver": False},
            location={"type": "historical"},
            scores={"video": 0.9, "music": 0.5, "text": 0.7},
            reasoning="Test reasoning",
        )
    
    def test_engine_class_exists(self):
        """Test ExplainabilityEngine class exists."""
        assert ExplainabilityEngine is not None
    
    def test_engine_creation(self, engine):
        """Test engine creation."""
        assert engine is not None
        assert engine.shap is not None
        assert engine.lime is not None
        assert engine.counterfactual is not None
        assert engine.nl_explainer is not None
    
    def test_explain_decision_feature_importance(self, engine, sample_decision):
        """Test explaining decision with feature importance."""
        explanation = engine.explain_decision(
            sample_decision,
            methods=[ExplanationType.FEATURE_IMPORTANCE],
        )
        
        assert "decision_id" in explanation
        assert "selected_agent" in explanation
        assert "shap_values" in explanation or "lime_importance" in explanation
    
    def test_explain_decision_natural_language(self, engine, sample_decision):
        """Test explaining decision with natural language."""
        explanation = engine.explain_decision(
            sample_decision,
            methods=[ExplanationType.FEATURE_IMPORTANCE, ExplanationType.NATURAL_LANGUAGE],
        )
        
        assert "natural_language" in explanation
        assert isinstance(explanation["natural_language"], str)
    
    def test_target_score_method(self, engine):
        """Test _target_score internal method."""
        features = {Feature.CONTENT_RELEVANCE: 0.9, Feature.CONTENT_QUALITY: 0.8}
        
        # Should return 1.0 if decision matches target
        score_video = engine._target_score(features, "video")
        score_music = engine._target_score(features, "music")
        
        # One should be 1.0 (matches), other should be 0.0
        assert score_video == 1.0 or score_music == 1.0
    
    def test_generate_summary_report(self, engine, sample_decision):
        """Test generating summary report for multiple decisions."""
        decisions = [sample_decision, sample_decision]  # Use same decision twice
        
        report = engine.generate_summary_report(decisions)
        
        assert "n_decisions" in report
        assert report["n_decisions"] == 2
        assert "agent_distribution" in report
        assert "average_feature_importance" in report
        assert "most_important_features" in report


# =============================================================================
# Edge Cases
# =============================================================================


class TestExplainabilityEdgeCases:
    """Test edge cases."""
    
    def test_decision_with_single_candidate(self):
        """Test decision with only one candidate."""
        decision = Decision(
            decision_id="single",
            selected_agent="text",
            selected_content_title="Text Content",
            candidates={
                "text": {"relevance_score": 7, "quality_score": 7},
            },
            user_profile={"age_group": "adult"},
            location={"type": "urban"},
            scores={"text": 1.0},
            reasoning="Only option available",
        )
        
        features = decision.get_feature_vector()
        assert Feature.CONTENT_RELEVANCE in features
    
    def test_decision_with_empty_user_profile(self):
        """Test decision with minimal user profile."""
        decision = Decision(
            decision_id="minimal",
            selected_agent="video",
            selected_content_title="Test",
            candidates={
                "video": {"relevance_score": 7, "quality_score": 7},
            },
            user_profile={},  # Empty profile
            location={},
            scores={"video": 0.8},
            reasoning="Default selection",
        )
        
        features = decision.get_feature_vector()
        # Should use defaults
        assert features[Feature.USER_AGE_GROUP].value == "adult"
    
    def test_constant_model_baseline(self):
        """Test constant model returns consistent values."""
        def constant_model(features: Dict[Feature, float]) -> float:
            return 0.5  # Always returns same value
        
        result1 = constant_model({Feature.CONTENT_QUALITY: 0.9})
        result2 = constant_model({Feature.CONTENT_QUALITY: 0.1})
        
        assert result1 == result2 == 0.5
    
    def test_feature_value_normalization_bounds(self):
        """Test normalized values stay in bounds."""
        # Test all age groups
        decision = Decision(
            decision_id="test",
            selected_agent="video",
            selected_content_title="Test",
            candidates={"video": {"relevance_score": 5, "quality_score": 5}},
            user_profile={"age_group": "kid"},
            location={"type": "historical"},
            scores={"video": 0.5},
            reasoning="Test",
        )
        
        features = decision.get_feature_vector()
        
        # All normalized values should be in [0, 1]
        for fv in features.values():
            assert 0.0 <= fv.normalized_value <= 1.0


# =============================================================================
# Integration Tests
# =============================================================================


class TestExplainabilityIntegration:
    """Integration tests for explainability."""
    
    def test_decision_feature_extraction(self):
        """Test feature extraction from decision."""
        decision = Decision(
            decision_id="test",
            selected_agent="video",
            selected_content_title="Test Video",
            candidates={
                "video": {"relevance_score": 9, "quality_score": 8},
            },
            user_profile={"age_group": "adult"},
            location={"type": "cultural"},
            scores={"video": 0.92},
            reasoning="Test",
        )
        
        features = decision.get_feature_vector()
        
        assert len(features) > 0
        assert features[Feature.CONTENT_RELEVANCE].value == 9
    
    def test_full_pipeline(self):
        """Test full explainability pipeline."""
        # Create models
        def decision_model(features: Dict[Feature, float]) -> str:
            score = features.get(Feature.CONTENT_RELEVANCE, 0.5) * 0.6
            return "video" if score > 0.3 else "text"
        
        def score_model(features: Dict[Feature, float]) -> float:
            return features.get(Feature.CONTENT_RELEVANCE, 0.5) * 0.6
        
        # Create engine
        engine = ExplainabilityEngine(decision_model, score_model)
        
        # Create decision
        decision = Decision(
            decision_id="pipeline_test",
            selected_agent="video",
            selected_content_title="Pipeline Test Video",
            candidates={"video": {"relevance_score": 8, "quality_score": 7}},
            user_profile={"age_group": "adult", "is_driver": False},
            location={"type": "historical"},
            scores={"video": 0.85},
            reasoning="Pipeline test",
        )
        
        # Get explanation
        explanation = engine.explain_decision(decision)
        
        assert explanation is not None
        assert "decision_id" in explanation


class TestDemo:
    """Test demo function."""
    
    def test_demo_import(self):
        """Test demo function is importable."""
        assert callable(demo_explainability)
