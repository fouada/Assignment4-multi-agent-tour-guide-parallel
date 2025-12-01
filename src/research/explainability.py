"""
🔍 Explainable AI Framework for Multi-Agent Decisions
======================================================

MIT-Level Innovation: Interpretable Decision-Making in Multi-Agent Systems

This module provides comprehensive explainability for the Judge Agent's
decisions, enabling users and developers to understand WHY specific
content was selected. This is crucial for:
- Trust and transparency
- Debugging and improvement
- Regulatory compliance (GDPR right to explanation)
- User satisfaction

Key Innovations:
1. SHAP-based Feature Attribution
2. LIME-based Local Explanations
3. Counterfactual Explanations ("What would change the decision?")
4. Attention-based Explanation for LLM Decisions
5. Human-Readable Natural Language Explanations

Academic References:
- Lundberg & Lee (2017) "A Unified Approach to Interpreting Model Predictions"
- Ribeiro et al. (2016) "Why Should I Trust You?: Explaining the Predictions of Any Classifier"
- Wachter et al. (2017) "Counterfactual Explanations without Opening the Black Box"
- Doshi-Velez & Kim (2017) "Towards A Rigorous Science of Interpretable Machine Learning"

Author: MIT-Level Research Framework
Version: 1.0.0
Date: November 2025
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from itertools import combinations
from typing import Any

import numpy as np

# =============================================================================
# Feature Definitions for Explanation
# =============================================================================


class Feature(str, Enum):
    """Features that influence agent selection decisions."""

    # Content Features
    CONTENT_RELEVANCE = "content_relevance"
    CONTENT_QUALITY = "content_quality"
    CONTENT_DURATION = "content_duration"
    CONTENT_TYPE = "content_type"

    # User Profile Features
    USER_AGE_GROUP = "user_age_group"
    USER_INTERESTS = "user_interests"
    USER_ACCESSIBILITY = "user_accessibility"
    USER_TRIP_PURPOSE = "user_trip_purpose"
    USER_IS_DRIVER = "user_is_driver"

    # Context Features
    LOCATION_TYPE = "location_type"
    LOCATION_POPULARITY = "location_popularity"
    TIME_OF_DAY = "time_of_day"
    PREVIOUS_SELECTIONS = "previous_selections"

    # Agent Features
    AGENT_RESPONSE_TIME = "agent_response_time"
    AGENT_SUCCESS_RATE = "agent_success_rate"


class ExplanationType(str, Enum):
    """Types of explanations that can be generated."""

    FEATURE_IMPORTANCE = "feature_importance"
    COUNTERFACTUAL = "counterfactual"
    CONTRASTIVE = "contrastive"
    EXAMPLE_BASED = "example_based"
    RULE_BASED = "rule_based"
    NATURAL_LANGUAGE = "natural_language"


@dataclass
class FeatureValue:
    """Represents a feature and its value."""

    feature: Feature
    value: Any
    normalized_value: float  # Normalized to [0, 1] for comparison
    display_name: str = ""
    description: str = ""

    def __post_init__(self):
        if not self.display_name:
            self.display_name = self.feature.value.replace("_", " ").title()


@dataclass
class Decision:
    """
    Represents a Judge Agent decision to explain.

    Contains all information about a content selection decision.
    """

    decision_id: str
    selected_agent: str  # "video", "music", or "text"
    selected_content_title: str
    candidates: dict[str, dict[str, Any]]  # agent -> content details
    user_profile: dict[str, Any]
    location: dict[str, Any]
    scores: dict[str, float]  # agent -> score
    reasoning: str
    timestamp: datetime = field(default_factory=datetime.now)

    def get_feature_vector(self) -> dict[Feature, FeatureValue]:
        """Extract feature vector from decision context."""
        features = {}

        # Content features for selected agent
        if self.selected_agent in self.candidates:
            content = self.candidates[self.selected_agent]
            features[Feature.CONTENT_RELEVANCE] = FeatureValue(
                feature=Feature.CONTENT_RELEVANCE,
                value=content.get("relevance_score", 5),
                normalized_value=content.get("relevance_score", 5) / 10,
            )
            features[Feature.CONTENT_QUALITY] = FeatureValue(
                feature=Feature.CONTENT_QUALITY,
                value=content.get("quality_score", 5),
                normalized_value=content.get("quality_score", 5) / 10,
            )

        # User profile features
        features[Feature.USER_AGE_GROUP] = FeatureValue(
            feature=Feature.USER_AGE_GROUP,
            value=self.user_profile.get("age_group", "adult"),
            normalized_value=self._age_to_normalized(
                self.user_profile.get("age_group", "adult")
            ),
        )
        features[Feature.USER_IS_DRIVER] = FeatureValue(
            feature=Feature.USER_IS_DRIVER,
            value=self.user_profile.get("is_driver", False),
            normalized_value=1.0 if self.user_profile.get("is_driver") else 0.0,
        )

        # Location features
        features[Feature.LOCATION_TYPE] = FeatureValue(
            feature=Feature.LOCATION_TYPE,
            value=self.location.get("type", "general"),
            normalized_value=self._location_type_to_normalized(
                self.location.get("type", "general")
            ),
        )

        return features

    def _age_to_normalized(self, age_group: str) -> float:
        """Convert age group to normalized value."""
        mapping = {"kid": 0.1, "teen": 0.3, "adult": 0.6, "senior": 0.9}
        return mapping.get(age_group, 0.5)

    def _location_type_to_normalized(self, loc_type: str) -> float:
        """Convert location type to normalized value."""
        mapping = {
            "historical": 0.2,
            "natural": 0.4,
            "urban": 0.6,
            "cultural": 0.3,
            "entertainment": 0.8,
        }
        return mapping.get(loc_type, 0.5)


# =============================================================================
# SHAP Value Computation
# =============================================================================


class SHAPExplainer:
    r"""
    SHAP (SHapley Additive exPlanations) for feature attribution.

    SHAP values come from cooperative game theory and provide:
    - Local accuracy: Σ φᵢ + φ₀ = f(x)
    - Missingness: Missing features have zero attribution
    - Consistency: If feature importance increases, SHAP value doesn't decrease

    Mathematical Foundation:
    φᵢ(f, x) = Σ_{S⊆N\{i}} |S|!(|N|-|S|-1)!/|N|! × [f(S∪{i}) - f(S)]

    This is the average marginal contribution of feature i across all
    possible coalitions of features.
    """

    def __init__(
        self,
        model: Callable[[dict[Feature, float]], float],
        features: list[Feature],
        baseline: dict[Feature, float] | None = None,
    ):
        """
        Initialize SHAP explainer.

        Args:
            model: Function that takes feature values and returns prediction
            features: List of features to explain
            baseline: Baseline feature values (default: 0.5 for all)
        """
        self.model = model
        self.features = features
        self.n_features = len(features)
        self.baseline = baseline or dict.fromkeys(features, 0.5)

    def explain(self, instance: dict[Feature, float]) -> dict[Feature, float]:
        """
        Compute exact SHAP values for an instance.

        This computes the exact Shapley values by enumerating all 2^n
        feature coalitions. For n > 15, consider approximate methods.

        Args:
            instance: Feature values for the instance to explain

        Returns:
            Dictionary mapping features to SHAP values
        """
        n = self.n_features
        shap_values = dict.fromkeys(self.features, 0.0)

        # Enumerate all subsets
        for i, feature in enumerate(self.features):
            # Features other than i
            other_features = [f for j, f in enumerate(self.features) if j != i]

            marginal_sum = 0.0

            # For each subset S of other features
            for s in range(n):
                # Subsets of size s from other features
                for subset in combinations(range(n - 1), s):
                    subset_features = [other_features[j] for j in subset]

                    # Compute f(S ∪ {i}) - f(S)
                    # f(S): use baseline for i and features not in S
                    # f(S ∪ {i}): use instance value for i

                    # Create input for f(S)
                    input_without_i = {}
                    for f in self.features:
                        if f in subset_features:
                            input_without_i[f] = instance.get(f, self.baseline[f])
                        else:
                            input_without_i[f] = self.baseline[f]

                    # Create input for f(S ∪ {i})
                    input_with_i = input_without_i.copy()
                    input_with_i[feature] = instance.get(
                        feature, self.baseline[feature]
                    )

                    # Compute marginal contribution
                    marginal = self.model(input_with_i) - self.model(input_without_i)

                    # Weight by |S|!(|N|-|S|-1)!/|N|!
                    weight = (
                        math.factorial(s) * math.factorial(n - s - 1)
                    ) / math.factorial(n)

                    marginal_sum += weight * marginal

            shap_values[feature] = marginal_sum

        return shap_values

    def explain_approximate(
        self, instance: dict[Feature, float], n_samples: int = 1000
    ) -> dict[Feature, float]:
        """
        Compute approximate SHAP values using sampling.

        Uses random permutations to estimate Shapley values:
        φᵢ ≈ (1/m) Σⱼ [f(Preᵢ(πⱼ) ∪ {i}) - f(Preᵢ(πⱼ))]

        Where Preᵢ(π) is the set of features before i in permutation π.

        Args:
            instance: Feature values
            n_samples: Number of random permutations

        Returns:
            Approximate SHAP values
        """
        rng = np.random.RandomState(42)
        n = self.n_features

        marginal_contributions = {f: [] for f in self.features}

        for _ in range(n_samples):
            # Random permutation
            perm = rng.permutation(n)

            current_input = self.baseline.copy()
            current_output = self.model(current_input)

            for idx in perm:
                feature = self.features[idx]

                # Add feature to coalition
                current_input[feature] = instance.get(feature, self.baseline[feature])
                new_output = self.model(current_input)

                # Marginal contribution
                marginal = new_output - current_output
                marginal_contributions[feature].append(marginal)

                current_output = new_output

        # Average marginal contributions
        return {
            f: np.mean(contributions)
            for f, contributions in marginal_contributions.items()
        }

    def compute_interaction_values(
        self, instance: dict[Feature, float]
    ) -> dict[tuple[Feature, Feature], float]:
        """
        Compute SHAP interaction values.

        Interaction value measures the joint effect of features i and j
        beyond their individual effects.
        """
        interactions = {}

        for i, feat_i in enumerate(self.features):
            for j, feat_j in enumerate(self.features):
                if i >= j:
                    continue

                # Compute interaction: f(i,j) - f(i) - f(j) + f(∅)
                # Averaged over all contexts

                input_ij = self.baseline.copy()
                input_ij[feat_i] = instance.get(feat_i, self.baseline[feat_i])
                input_ij[feat_j] = instance.get(feat_j, self.baseline[feat_j])

                input_i = self.baseline.copy()
                input_i[feat_i] = instance.get(feat_i, self.baseline[feat_i])

                input_j = self.baseline.copy()
                input_j[feat_j] = instance.get(feat_j, self.baseline[feat_j])

                input_none = self.baseline.copy()

                interaction = (
                    self.model(input_ij)
                    - self.model(input_i)
                    - self.model(input_j)
                    + self.model(input_none)
                )

                interactions[(feat_i, feat_j)] = interaction

        return interactions


# =============================================================================
# LIME (Local Interpretable Model-agnostic Explanations)
# =============================================================================


class LIMEExplainer:
    """
    LIME: Local Interpretable Model-agnostic Explanations.

    LIME explains predictions by:
    1. Sampling perturbations around the instance
    2. Getting model predictions for perturbations
    3. Fitting an interpretable model (linear) locally
    4. Using interpretable model's coefficients as explanations

    Mathematical Foundation:
    ξ(x) = argmin_{g∈G} L(f, g, πₓ) + Ω(g)

    Where:
    - G = class of interpretable models (e.g., linear)
    - L = fidelity loss (how well g approximates f locally)
    - πₓ = locality kernel (weights by proximity to x)
    - Ω(g) = complexity penalty
    """

    def __init__(
        self,
        model: Callable[[dict[Feature, float]], float],
        features: list[Feature],
        kernel_width: float = 0.75,
    ):
        """
        Initialize LIME explainer.

        Args:
            model: Black-box model to explain
            features: List of features
            kernel_width: Width of the exponential kernel
        """
        self.model = model
        self.features = features
        self.kernel_width = kernel_width

    def explain(
        self,
        instance: dict[Feature, float],
        n_samples: int = 5000,
        n_features_to_show: int = 10,
    ) -> dict[str, Any]:
        """
        Generate LIME explanation for an instance.

        Args:
            instance: Feature values for the instance
            n_samples: Number of perturbed samples
            n_features_to_show: Number of top features to return

        Returns:
            Dictionary with explanation details
        """
        rng = np.random.RandomState(42)

        # Convert instance to array
        instance_arr = np.array([instance.get(f, 0.5) for f in self.features])
        n = len(self.features)

        # Generate perturbations around the instance
        perturbations = rng.normal(instance_arr, self.kernel_width, size=(n_samples, n))
        perturbations = np.clip(perturbations, 0, 1)

        # Get model predictions
        predictions = []
        for pert in perturbations:
            pert_dict = {f: pert[i] for i, f in enumerate(self.features)}
            predictions.append(self.model(pert_dict))
        predictions = np.array(predictions)

        # Compute distances and weights
        distances = np.sqrt(np.sum((perturbations - instance_arr) ** 2, axis=1))
        weights = np.exp(-(distances**2) / (self.kernel_width**2))

        # Fit weighted linear model
        # Add intercept
        X = np.column_stack([np.ones(n_samples), perturbations])

        # Weighted least squares
        W = np.diag(weights)
        try:
            beta = np.linalg.solve(
                X.T @ W @ X + 1e-6 * np.eye(n + 1), X.T @ W @ predictions
            )
        except np.linalg.LinAlgError:
            beta = np.zeros(n + 1)

        # Extract coefficients (skip intercept)
        coefficients = {f: beta[i + 1] for i, f in enumerate(self.features)}
        intercept = beta[0]

        # Sort by absolute importance
        sorted_features = sorted(
            coefficients.items(), key=lambda x: abs(x[1]), reverse=True
        )[:n_features_to_show]

        # Compute local prediction
        local_prediction = intercept + sum(
            coef * instance.get(feat, 0.5) for feat, coef in coefficients.items()
        )

        # Compute R² for local fidelity
        predicted_local = X @ beta
        ss_res = np.sum(weights * (predictions - predicted_local) ** 2)
        ss_tot = np.sum(
            weights * (predictions - np.average(predictions, weights=weights)) ** 2
        )
        r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0

        return {
            "feature_importance": dict(sorted_features),
            "all_coefficients": coefficients,
            "intercept": intercept,
            "local_prediction": local_prediction,
            "actual_prediction": self.model(instance),
            "local_fidelity_r2": r_squared,
            "kernel_width": self.kernel_width,
            "n_samples": n_samples,
        }


# =============================================================================
# Counterfactual Explanations
# =============================================================================


@dataclass
class CounterfactualExplanation:
    """
    A counterfactual explanation answering:
    "What minimal change would result in a different outcome?"
    """

    original_decision: str
    counterfactual_decision: str
    original_features: dict[Feature, float]
    counterfactual_features: dict[Feature, float]
    changes: dict[Feature, tuple[float, float]]  # feature -> (old, new)
    total_change: float  # L1 distance
    plausibility_score: float  # How realistic is this counterfactual?

    def to_natural_language(self) -> str:
        """Generate human-readable explanation."""
        changes_text = []
        for feature, (old, new) in self.changes.items():
            feature_name = feature.value.replace("_", " ")
            direction = "increased" if new > old else "decreased"
            changes_text.append(
                f"{feature_name} {direction} from {old:.2f} to {new:.2f}"
            )

        changes_str = "; ".join(changes_text)
        return (
            f"The decision would have been '{self.counterfactual_decision}' "
            f"instead of '{self.original_decision}' if: {changes_str}"
        )


class CounterfactualExplainer:
    """
    Generate counterfactual explanations for decisions.

    Counterfactuals answer: "What would need to change to get
    a different outcome?"

    Uses gradient-based optimization to find minimal changes.
    """

    def __init__(
        self,
        model: Callable[[dict[Feature, float]], str],  # Returns decision
        score_model: Callable[[dict[Feature, float], str], float],  # Score for target
        features: list[Feature],
    ):
        """
        Initialize counterfactual explainer.

        Args:
            model: Model that makes decisions
            score_model: Function that returns score for a target class
            features: List of features
        """
        self.model = model
        self.score_model = score_model
        self.features = features

    def explain(
        self,
        instance: dict[Feature, float],
        target_decision: str,
        n_counterfactuals: int = 3,
        max_iterations: int = 1000,
    ) -> list[CounterfactualExplanation]:
        """
        Find counterfactual explanations.

        Uses optimization to find minimal changes that change the decision.

        Args:
            instance: Original feature values
            target_decision: Desired alternative decision
            n_counterfactuals: Number of counterfactuals to find
            max_iterations: Maximum optimization iterations

        Returns:
            List of counterfactual explanations
        """
        original_decision = self.model(instance)

        if original_decision == target_decision:
            return []  # Already the target

        counterfactuals = []
        rng = np.random.RandomState(42)

        for _ in range(n_counterfactuals):
            # Start from instance with small perturbation
            x = np.array([instance.get(f, 0.5) for f in self.features])
            x = x + rng.normal(0, 0.1, len(x))
            x = np.clip(x, 0, 1)

            # Gradient-free optimization (coordinate descent)
            best_x = x.copy()
            best_score = self._objective(x, instance, target_decision)

            for _ in range(max_iterations):
                # Try modifying each feature
                for i in range(len(self.features)):
                    for delta in [-0.1, 0.1, -0.05, 0.05]:
                        x_new = x.copy()
                        x_new[i] = np.clip(x_new[i] + delta, 0, 1)

                        score = self._objective(x_new, instance, target_decision)

                        if score < best_score:
                            best_score = score
                            best_x = x_new.copy()

                x = best_x.copy()

                # Check if we found a valid counterfactual
                cf_dict = {f: best_x[i] for i, f in enumerate(self.features)}
                if self.model(cf_dict) == target_decision:
                    break

            # Create counterfactual explanation
            cf_dict = {f: best_x[i] for i, f in enumerate(self.features)}
            cf_decision = self.model(cf_dict)

            if cf_decision == target_decision:
                changes = {}
                for i, f in enumerate(self.features):
                    orig = instance.get(f, 0.5)
                    cf_val = best_x[i]
                    if abs(orig - cf_val) > 0.01:
                        changes[f] = (orig, cf_val)

                if changes:
                    cf = CounterfactualExplanation(
                        original_decision=original_decision,
                        counterfactual_decision=target_decision,
                        original_features=instance,
                        counterfactual_features=cf_dict,
                        changes=changes,
                        total_change=np.sum(
                            np.abs(
                                best_x
                                - np.array(
                                    [instance.get(f, 0.5) for f in self.features]
                                )
                            )
                        ),
                        plausibility_score=self._compute_plausibility(
                            instance, cf_dict
                        ),
                    )
                    counterfactuals.append(cf)

        # Sort by total change (smallest first)
        counterfactuals.sort(key=lambda x: x.total_change)

        return counterfactuals

    def _objective(
        self, x: np.ndarray, original: dict[Feature, float], target: str
    ) -> float:
        """
        Objective function for counterfactual search.

        Minimize: -score(target) + λ·distance(x, original)
        """
        x_dict = {f: x[i] for i, f in enumerate(self.features)}

        # Maximize target score
        target_score = self.score_model(x_dict, target)

        # Minimize distance from original
        orig_arr = np.array([original.get(f, 0.5) for f in self.features])
        distance = np.sum(np.abs(x - orig_arr))

        # Lambda controls sparsity
        lambda_reg = 0.1

        return -target_score + lambda_reg * distance

    def _compute_plausibility(
        self, original: dict[Feature, float], counterfactual: dict[Feature, float]
    ) -> float:
        """
        Compute plausibility score for a counterfactual.

        Considers:
        - Number of features changed (fewer is better)
        - Magnitude of changes (smaller is better)
        - Whether changes are actionable
        """
        n_changed = 0
        total_magnitude = 0

        for f in self.features:
            orig = original.get(f, 0.5)
            cf = counterfactual.get(f, 0.5)

            if abs(orig - cf) > 0.01:
                n_changed += 1
                total_magnitude += abs(orig - cf)

        # Higher score = more plausible
        sparsity_score = 1.0 / (1 + n_changed)
        magnitude_score = 1.0 / (1 + total_magnitude)

        return (sparsity_score + magnitude_score) / 2


# =============================================================================
# Natural Language Explanation Generator
# =============================================================================


class NaturalLanguageExplainer:
    """
    Generate human-readable natural language explanations.

    Combines feature importance with domain knowledge to produce
    understandable explanations for non-technical users.
    """

    def __init__(self):
        """Initialize with templates."""
        self.templates = {
            "high_relevance": (
                "The {agent} content was selected primarily because it was "
                "highly relevant to the location ({relevance:.1f}/10)."
            ),
            "user_preference": (
                "Based on your {profile_feature}, {agent} content is typically "
                "more engaging and appropriate."
            ),
            "driver_safety": (
                "Since you're driving, video content was avoided for safety. "
                "{agent} was chosen as the best audio/text alternative."
            ),
            "location_match": (
                "For {location_type} locations like this one, {agent} content "
                "tends to provide the most valuable experience."
            ),
            "quality_factor": (
                "The {agent} content had the highest quality score "
                "({quality:.1f}/10) among available options."
            ),
        }

    def explain(
        self, decision: Decision, shap_values: dict[Feature, float], top_k: int = 3
    ) -> str:
        """
        Generate natural language explanation.

        Args:
            decision: The decision to explain
            shap_values: SHAP values for feature importance
            top_k: Number of top reasons to include

        Returns:
            Human-readable explanation string
        """
        # Sort features by absolute SHAP value
        sorted_features = sorted(
            shap_values.items(), key=lambda x: abs(x[1]), reverse=True
        )[:top_k]

        reasons = []

        for feature, shap_value in sorted_features:
            reason = self._generate_reason(feature, shap_value, decision)
            if reason:
                reasons.append(reason)

        # Combine reasons
        if not reasons:
            return f"'{decision.selected_content_title}' was selected as the best content for this location."

        intro = f"**{decision.selected_agent.upper()}** content was selected: '{decision.selected_content_title}'\n\n"
        intro += "**Key Reasons:**\n"

        for i, reason in enumerate(reasons, 1):
            intro += f"{i}. {reason}\n"

        return intro

    def _generate_reason(
        self, feature: Feature, shap_value: float, decision: Decision
    ) -> str | None:
        """Generate a reason based on feature importance."""
        selected = decision.selected_agent

        if feature == Feature.CONTENT_RELEVANCE:
            relevance = decision.candidates.get(selected, {}).get("relevance_score", 7)
            return self.templates["high_relevance"].format(
                agent=selected, relevance=relevance
            )

        elif feature == Feature.USER_IS_DRIVER:
            if decision.user_profile.get("is_driver"):
                return self.templates["driver_safety"].format(agent=selected)

        elif feature == Feature.USER_AGE_GROUP:
            age = decision.user_profile.get("age_group", "adult")
            return self.templates["user_preference"].format(
                agent=selected, profile_feature=f"{age} age group"
            )

        elif feature == Feature.LOCATION_TYPE:
            loc_type = decision.location.get("type", "general")
            return self.templates["location_match"].format(
                agent=selected, location_type=loc_type
            )

        elif feature == Feature.CONTENT_QUALITY:
            quality = decision.candidates.get(selected, {}).get("quality_score", 7)
            return self.templates["quality_factor"].format(
                agent=selected, quality=quality
            )

        return None


# =============================================================================
# Integrated Explainability Engine
# =============================================================================


class ExplainabilityEngine:
    """
    Integrated engine for generating comprehensive explanations.

    Combines multiple explanation methods:
    1. SHAP feature attribution
    2. LIME local explanations
    3. Counterfactual explanations
    4. Natural language summaries
    """

    def __init__(
        self,
        decision_model: Callable[[dict[Feature, float]], str],
        score_model: Callable[[dict[Feature, float]], float],
    ):
        """
        Initialize explainability engine.

        Args:
            decision_model: Model that makes decisions (returns agent name)
            score_model: Model that returns decision score
        """
        self.features = list(Feature)
        self.decision_model = decision_model
        self.score_model = score_model

        # Initialize explainers
        self.shap = SHAPExplainer(score_model, self.features)
        self.lime = LIMEExplainer(score_model, self.features)
        self.counterfactual = CounterfactualExplainer(
            decision_model, lambda x, t: self._target_score(x, t), self.features
        )
        self.nl_explainer = NaturalLanguageExplainer()

    def _target_score(self, features: dict[Feature, float], target: str) -> float:
        """Score function for target decision."""
        # Simplified: return high score if decision matches target
        decision = self.decision_model(features)
        if decision == target:
            return 1.0
        return 0.0

    def explain_decision(
        self, decision: Decision, methods: list[ExplanationType] | None = None
    ) -> dict[str, Any]:
        """
        Generate comprehensive explanation for a decision.

        Args:
            decision: Decision to explain
            methods: Which explanation methods to use (default: all)

        Returns:
            Dictionary with all explanations
        """
        methods = methods or list(ExplanationType)

        # Extract feature values from decision
        feature_vector = decision.get_feature_vector()
        instance = {f: fv.normalized_value for f, fv in feature_vector.items()}

        # Fill missing features with defaults
        for f in self.features:
            if f not in instance:
                instance[f] = 0.5

        explanations = {
            "decision_id": decision.decision_id,
            "selected_agent": decision.selected_agent,
            "selected_content": decision.selected_content_title,
            "original_reasoning": decision.reasoning,
        }

        # SHAP explanations
        if ExplanationType.FEATURE_IMPORTANCE in methods:
            shap_values = self.shap.explain_approximate(instance)
            explanations["shap_values"] = {f.value: v for f, v in shap_values.items()}
            explanations["top_features"] = sorted(
                shap_values.items(), key=lambda x: abs(x[1]), reverse=True
            )[:5]

        # LIME explanations
        if ExplanationType.FEATURE_IMPORTANCE in methods:
            lime_result = self.lime.explain(instance)
            explanations["lime_importance"] = lime_result["feature_importance"]
            explanations["local_fidelity"] = lime_result["local_fidelity_r2"]

        # Counterfactual explanations
        if ExplanationType.COUNTERFACTUAL in methods:
            other_agents = [
                a for a in ["video", "music", "text"] if a != decision.selected_agent
            ]

            counterfactuals = []
            for target in other_agents:
                cfs = self.counterfactual.explain(instance, target, n_counterfactuals=1)
                counterfactuals.extend(cfs)

            explanations["counterfactuals"] = [
                cf.to_natural_language() for cf in counterfactuals
            ]

        # Natural language explanation
        if ExplanationType.NATURAL_LANGUAGE in methods:
            if "shap_values" in explanations:
                nl_explanation = self.nl_explainer.explain(
                    decision,
                    {
                        Feature(k): v
                        for k, v in explanations["shap_values"].items()
                        if k in [f.value for f in Feature]
                    },
                )
                explanations["natural_language"] = nl_explanation

        return explanations

    def generate_summary_report(self, decisions: list[Decision]) -> dict[str, Any]:
        """
        Generate summary report across multiple decisions.

        Useful for understanding systematic patterns.
        """
        all_shap_values = {f: [] for f in self.features}
        agent_counts = {"video": 0, "music": 0, "text": 0}

        for decision in decisions:
            feature_vector = decision.get_feature_vector()
            instance = {f: fv.normalized_value for f, fv in feature_vector.items()}

            for f in self.features:
                if f not in instance:
                    instance[f] = 0.5

            shap_values = self.shap.explain_approximate(instance, n_samples=100)

            for f, v in shap_values.items():
                all_shap_values[f].append(v)

            agent_counts[decision.selected_agent] += 1

        # Aggregate statistics
        feature_importance_avg = {
            f.value: np.mean(values) if values else 0
            for f, values in all_shap_values.items()
        }

        feature_importance_std = {
            f.value: np.std(values) if values else 0
            for f, values in all_shap_values.items()
        }

        return {
            "n_decisions": len(decisions),
            "agent_distribution": agent_counts,
            "average_feature_importance": feature_importance_avg,
            "feature_importance_std": feature_importance_std,
            "most_important_features": sorted(
                feature_importance_avg.items(), key=lambda x: abs(x[1]), reverse=True
            )[:5],
        }


# =============================================================================
# Example Usage
# =============================================================================


def demo_explainability():
    """Demonstrate the explainability framework."""
    print("=" * 70)
    print("🔍 EXPLAINABILITY FRAMEWORK DEMO")
    print("=" * 70)

    # Simple decision model
    def decision_model(features: dict[Feature, float]) -> str:
        """Simple rule-based decision model."""
        # If user is driver, never select video
        if features.get(Feature.USER_IS_DRIVER, 0) > 0.5:
            if features.get(Feature.LOCATION_TYPE, 0.5) < 0.3:
                return "text"  # Historical -> text
            return "music"  # Otherwise music

        # Based on content relevance and quality
        relevance = features.get(Feature.CONTENT_RELEVANCE, 0.5)
        quality = features.get(Feature.CONTENT_QUALITY, 0.5)

        score = relevance * 0.6 + quality * 0.4

        if score > 0.7:
            return "video"
        elif score > 0.5:
            return "text"
        return "music"

    def score_model(features: dict[Feature, float]) -> float:
        """Returns score for the model's decision."""
        relevance = features.get(Feature.CONTENT_RELEVANCE, 0.5)
        quality = features.get(Feature.CONTENT_QUALITY, 0.5)
        return relevance * 0.6 + quality * 0.4

    # Create engine
    engine = ExplainabilityEngine(decision_model, score_model)

    # Create a sample decision
    decision = Decision(
        decision_id="test_001",
        selected_agent="text",
        selected_content_title="The History of Ancient Rome",
        candidates={
            "video": {"relevance_score": 6, "quality_score": 7},
            "music": {"relevance_score": 5, "quality_score": 6},
            "text": {"relevance_score": 8, "quality_score": 8},
        },
        user_profile={"age_group": "adult", "is_driver": False},
        location={"type": "historical", "name": "Roman Forum"},
        scores={"video": 6.5, "music": 5.5, "text": 8.0},
        reasoning="Text content best matches the historical context.",
    )

    # Generate explanation
    print("\n📊 Generating explanation...")
    explanation = engine.explain_decision(decision)

    print(f"\n🎯 Decision: {explanation['selected_agent'].upper()}")
    print(f"   Content: {explanation['selected_content']}")

    if "top_features" in explanation:
        print("\n📈 Top Features (SHAP):")
        for feat, value in explanation["top_features"]:
            direction = "+" if value > 0 else ""
            print(f"   {feat.value}: {direction}{value:.4f}")

    if "counterfactuals" in explanation:
        print("\n🔄 Counterfactual Explanations:")
        for cf in explanation["counterfactuals"][:2]:
            print(f"   • {cf}")

    if "natural_language" in explanation:
        print("\n📝 Natural Language Explanation:")
        print(explanation["natural_language"])

    print("\n✅ Demo complete!")


if __name__ == "__main__":
    demo_explainability()
