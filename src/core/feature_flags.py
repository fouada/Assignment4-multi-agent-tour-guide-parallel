"""
Feature Flags System
===================

Production-grade feature flag system for runtime feature toggles,
A/B testing, gradual rollouts, and experimentation.

Design Patterns:
    - Strategy Pattern: Different evaluation strategies
    - Observer Pattern: Flag change notifications
    - Decorator Pattern: @feature_flag decorator

Academic Reference:
    - Fowler, "Feature Toggles" (martinfowler.com/articles/feature-toggles.html)
    - Rahman & Williams, "Feature Toggle Patterns" (IEEE Software, 2016)

Example:
    # Define flags
    flags = FeatureFlagManager()
    flags.create_flag(
        "new_recommendation_algorithm",
        enabled=True,
        rollout_percentage=50,  # 50% of users
        targeting_rules={
            "user_type": ["premium", "beta_tester"]
        }
    )

    # Check flag
    if flags.is_enabled("new_recommendation_algorithm", user_context):
        use_new_algorithm()
    else:
        use_old_algorithm()

    # Or use decorator
    @feature_flag("new_recommendation_algorithm")
    def recommend_content(user):
        return new_recommendation_engine.run(user)
"""

from __future__ import annotations

import hashlib
import logging
import threading
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from functools import wraps
from typing import Any, TypeVar

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)

T = TypeVar("T")


class FlagType(Enum):
    """Types of feature flags."""

    RELEASE = auto()  # Release toggles (temporary, removed after rollout)
    EXPERIMENT = auto()  # A/B tests (data-driven decisions)
    OPS = auto()  # Operational toggles (circuit breakers, maintenance mode)
    PERMISSION = auto()  # Permission toggles (premium features)


class RolloutStrategy(Enum):
    """How to roll out a feature."""

    ALL_USERS = "all"  # All users get the feature
    PERCENTAGE = "percentage"  # Gradual rollout by percentage
    WHITELIST = "whitelist"  # Specific users/groups
    TARGETING = "targeting"  # Rule-based targeting
    RANDOM = "random"  # Random assignment (for experiments)


class TargetingRule(BaseModel):
    """Rule for targeting specific users."""

    attribute: str  # e.g., "user_type", "region", "version"
    operator: str = Field(default="in")  # in, not_in, equals, greater_than, etc.
    values: list[Any]  # e.g., ["premium", "beta_tester"]

    def evaluate(self, context: dict[str, Any]) -> bool:
        """Evaluate if context matches this rule."""
        if self.attribute not in context:
            return False

        value = context[self.attribute]

        if self.operator == "in":
            return value in self.values
        elif self.operator == "not_in":
            return value not in self.values
        elif self.operator == "equals":
            return value == self.values[0] if self.values else False
        elif self.operator == "not_equals":
            return value != self.values[0] if self.values else True
        elif self.operator == "greater_than":
            return value > self.values[0] if self.values else False
        elif self.operator == "less_than":
            return value < self.values[0] if self.values else False
        else:
            logger.warning(f"Unknown operator: {self.operator}")
            return False


class FeatureFlag(BaseModel):
    """
    A feature flag configuration.

    Attributes:
        name: Unique flag identifier
        enabled: Whether flag is globally enabled
        flag_type: Type of flag (release, experiment, etc.)
        rollout_strategy: How to roll out the feature
        rollout_percentage: Percentage of users (0-100) for gradual rollout
        whitelist: List of user IDs to always enable
        blacklist: List of user IDs to always disable
        targeting_rules: Complex targeting rules
        created_at: When flag was created
        updated_at: Last modification time
        expires_at: Optional expiration (for temporary flags)
        description: Human-readable description
        tags: Categorization tags
    """

    name: str = Field(..., min_length=1, max_length=100)
    enabled: bool = Field(default=True)
    flag_type: FlagType = Field(default=FlagType.RELEASE)
    rollout_strategy: RolloutStrategy = Field(default=RolloutStrategy.ALL_USERS)

    # Rollout config
    rollout_percentage: int = Field(default=100, ge=0, le=100)
    whitelist: list[str] = Field(default_factory=list)
    blacklist: list[str] = Field(default_factory=list)
    targeting_rules: list[TargetingRule] = Field(default_factory=list)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    expires_at: datetime | None = None
    description: str = Field(default="")
    tags: list[str] = Field(default_factory=list)

    # A/B testing
    variant: str | None = None  # For multivariate experiments
    variants: dict[str, int] = Field(default_factory=dict)  # {variant: weight}

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate flag name format."""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Flag name must be alphanumeric with _/-")
        return v

    def is_expired(self) -> bool:
        """Check if flag has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at


@dataclass
class FlagEvaluation:
    """Result of flag evaluation."""

    flag_name: str
    enabled: bool
    reason: str  # Why flag was enabled/disabled
    variant: str | None = None  # For A/B tests
    evaluation_time: datetime = field(default_factory=datetime.now)


class FeatureFlagManager:
    """
    Central manager for feature flags.

    Provides:
    - Flag registration and configuration
    - Context-aware flag evaluation
    - Rollout strategies (percentage, whitelist, targeting)
    - A/B testing support
    - Flag change notifications
    - Metrics and analytics

    Example:
        manager = FeatureFlagManager()

        # Create flags
        manager.create_flag(
            "new_ui",
            enabled=True,
            rollout_percentage=25,
        )

        # Evaluate
        if manager.is_enabled("new_ui", {"user_id": "123"}):
            show_new_ui()

        # Get variant for A/B test
        variant = manager.get_variant(
            "pricing_page",
            {"user_id": "123"},
            default="control"
        )
    """

    def __init__(self):
        """Initialize feature flag manager."""
        self._flags: dict[str, FeatureFlag] = {}
        self._lock = threading.RLock()

        # Observers for flag changes
        self._observers: list[Callable[[str, bool], None]] = []

        # Metrics
        self._evaluation_counts: dict[str, int] = defaultdict(int)
        self._enabled_counts: dict[str, int] = defaultdict(int)

    def create_flag(
        self,
        name: str,
        enabled: bool = True,
        flag_type: FlagType = FlagType.RELEASE,
        rollout_strategy: RolloutStrategy = RolloutStrategy.ALL_USERS,
        rollout_percentage: int = 100,
        whitelist: list[str] | None = None,
        targeting_rules: list[TargetingRule] | None = None,
        description: str = "",
        tags: list[str] | None = None,
        expires_at: datetime | None = None,
    ) -> FeatureFlag:
        """
        Create a new feature flag.

        Args:
            name: Unique flag identifier
            enabled: Whether flag is globally enabled
            flag_type: Type of flag
            rollout_strategy: Rollout strategy
            rollout_percentage: Percentage for gradual rollout
            whitelist: Always-enabled users
            targeting_rules: Complex targeting rules
            description: Description
            tags: Tags for categorization
            expires_at: Optional expiration

        Returns:
            Created feature flag
        """
        flag = FeatureFlag(
            name=name,
            enabled=enabled,
            flag_type=flag_type,
            rollout_strategy=rollout_strategy,
            rollout_percentage=rollout_percentage,
            whitelist=whitelist or [],
            targeting_rules=targeting_rules or [],
            description=description,
            tags=tags or [],
            expires_at=expires_at,
        )

        with self._lock:
            self._flags[name] = flag

        logger.info(f"Created feature flag: {name} (enabled={enabled})")
        return flag

    def update_flag(
        self,
        name: str,
        **kwargs: Any,
    ) -> FeatureFlag:
        """
        Update an existing flag.

        Args:
            name: Flag name
            **kwargs: Fields to update

        Returns:
            Updated flag
        """
        with self._lock:
            if name not in self._flags:
                raise ValueError(f"Flag not found: {name}")

            flag = self._flags[name]
            old_enabled = flag.enabled

            # Update fields
            for key, value in kwargs.items():
                if hasattr(flag, key):
                    setattr(flag, key, value)

            flag.updated_at = datetime.now()

            # Notify observers if enabled state changed
            if old_enabled != flag.enabled:
                self._notify_observers(name, flag.enabled)

        logger.info(f"Updated feature flag: {name}")
        return flag

    def delete_flag(self, name: str) -> None:
        """Delete a feature flag."""
        with self._lock:
            if name in self._flags:
                del self._flags[name]
                logger.info(f"Deleted feature flag: {name}")

    def get_flag(self, name: str) -> FeatureFlag | None:
        """Get flag configuration."""
        with self._lock:
            return self._flags.get(name)

    def list_flags(
        self,
        flag_type: FlagType | None = None,
        tags: list[str] | None = None,
    ) -> list[FeatureFlag]:
        """
        List all flags, optionally filtered.

        Args:
            flag_type: Filter by type
            tags: Filter by tags (must have all tags)

        Returns:
            List of flags
        """
        with self._lock:
            flags = list(self._flags.values())

            if flag_type:
                flags = [f for f in flags if f.flag_type == flag_type]

            if tags:
                flags = [f for f in flags if all(t in f.tags for t in tags)]

            return flags

    def is_enabled(
        self,
        name: str,
        context: dict[str, Any] | None = None,
    ) -> bool:
        """
        Check if a feature flag is enabled.

        Args:
            name: Flag name
            context: Evaluation context (user_id, attributes, etc.)

        Returns:
            True if flag is enabled for this context
        """
        evaluation = self.evaluate(name, context or {})
        return evaluation.enabled

    def evaluate(
        self,
        name: str,
        context: dict[str, Any],
    ) -> FlagEvaluation:
        """
        Evaluate a feature flag with full context.

        Args:
            name: Flag name
            context: Evaluation context

        Returns:
            Evaluation result with reason
        """
        with self._lock:
            # Track evaluation
            self._evaluation_counts[name] += 1

            # Flag not found - default to disabled
            if name not in self._flags:
                logger.debug(f"Flag not found: {name}, defaulting to disabled")
                return FlagEvaluation(
                    flag_name=name,
                    enabled=False,
                    reason="flag_not_found",
                )

            flag = self._flags[name]

            # Flag expired
            if flag.is_expired():
                logger.debug(f"Flag expired: {name}")
                return FlagEvaluation(
                    flag_name=name,
                    enabled=False,
                    reason="expired",
                )

            # Flag globally disabled
            if not flag.enabled:
                return FlagEvaluation(
                    flag_name=name,
                    enabled=False,
                    reason="globally_disabled",
                )

            user_id = context.get("user_id")

            # Check blacklist
            if user_id and user_id in flag.blacklist:
                return FlagEvaluation(
                    flag_name=name,
                    enabled=False,
                    reason="blacklisted",
                )

            # Check whitelist
            if user_id and user_id in flag.whitelist:
                self._enabled_counts[name] += 1
                return FlagEvaluation(
                    flag_name=name,
                    enabled=True,
                    reason="whitelisted",
                )

            # Evaluate based on strategy
            if flag.rollout_strategy == RolloutStrategy.ALL_USERS:
                self._enabled_counts[name] += 1
                return FlagEvaluation(
                    flag_name=name,
                    enabled=True,
                    reason="all_users",
                )

            elif flag.rollout_strategy == RolloutStrategy.PERCENTAGE:
                enabled = self._evaluate_percentage(
                    name,
                    user_id or "",
                    flag.rollout_percentage,
                )
                if enabled:
                    self._enabled_counts[name] += 1
                return FlagEvaluation(
                    flag_name=name,
                    enabled=enabled,
                    reason=f"percentage_rollout_{flag.rollout_percentage}%",
                )

            elif flag.rollout_strategy == RolloutStrategy.TARGETING:
                enabled = self._evaluate_targeting(flag.targeting_rules, context)
                if enabled:
                    self._enabled_counts[name] += 1
                return FlagEvaluation(
                    flag_name=name,
                    enabled=enabled,
                    reason="targeting_rules",
                )

            # Default: disabled
            return FlagEvaluation(
                flag_name=name,
                enabled=False,
                reason="default_disabled",
            )

    def _evaluate_percentage(
        self,
        flag_name: str,
        user_id: str,
        percentage: int,
    ) -> bool:
        """
        Evaluate percentage-based rollout.

        Uses consistent hashing to ensure same user always gets same result.
        """
        if percentage == 0:
            return False
        if percentage == 100:
            return True

        # Consistent hash
        hash_input = f"{flag_name}:{user_id}".encode()
        hash_value = int(hashlib.md5(hash_input).hexdigest(), 16)
        bucket = hash_value % 100

        return bucket < percentage

    def _evaluate_targeting(
        self,
        rules: list[TargetingRule],
        context: dict[str, Any],
    ) -> bool:
        """
        Evaluate targeting rules.

        All rules must match (AND logic).
        """
        if not rules:
            return True

        return all(rule.evaluate(context) for rule in rules)

    def get_variant(
        self,
        name: str,
        context: dict[str, Any],
        default: str = "control",
    ) -> str:
        """
        Get variant for A/B testing.

        Args:
            name: Flag name
            context: Evaluation context
            default: Default variant if flag disabled

        Returns:
            Variant name
        """
        evaluation = self.evaluate(name, context)

        if not evaluation.enabled:
            return default

        flag = self._flags.get(name)
        if not flag or not flag.variants:
            return default

        # Use consistent hashing for variant assignment
        user_id = context.get("user_id", "")
        return self._select_variant(name, user_id, flag.variants)

    def _select_variant(
        self,
        flag_name: str,
        user_id: str,
        variants: dict[str, int],
    ) -> str:
        """
        Select variant based on weights.

        Uses consistent hashing.
        """
        if not variants:
            return "control"

        # Normalize weights
        total_weight = sum(variants.values())
        if total_weight == 0:
            return list(variants.keys())[0]

        # Hash to bucket
        hash_input = f"{flag_name}:variant:{user_id}".encode()
        hash_value = int(hashlib.md5(hash_input).hexdigest(), 16)
        bucket = hash_value % total_weight

        # Select variant
        cumulative = 0
        for variant, weight in variants.items():
            cumulative += weight
            if bucket < cumulative:
                return variant

        return list(variants.keys())[0]

    def register_observer(
        self,
        callback: Callable[[str, bool], None],
    ) -> None:
        """
        Register observer for flag changes.

        Args:
            callback: Function called with (flag_name, enabled)
        """
        with self._lock:
            self._observers.append(callback)

    def _notify_observers(self, flag_name: str, enabled: bool) -> None:
        """Notify all observers of flag change."""
        for observer in self._observers:
            try:
                observer(flag_name, enabled)
            except Exception as e:
                logger.error(f"Observer error: {e}")

    def get_stats(self) -> dict[str, Any]:
        """Get feature flag statistics."""
        with self._lock:
            total_flags = len(self._flags)
            enabled_flags = sum(1 for f in self._flags.values() if f.enabled)

            return {
                "total_flags": total_flags,
                "enabled_flags": enabled_flags,
                "disabled_flags": total_flags - enabled_flags,
                "evaluation_counts": dict(self._evaluation_counts),
                "enabled_counts": dict(self._enabled_counts),
                "flags_by_type": self._get_flags_by_type(),
            }

    def _get_flags_by_type(self) -> dict[str, int]:
        """Count flags by type."""
        counts: dict[str, int] = defaultdict(int)
        for flag in self._flags.values():
            counts[flag.flag_type.name] += 1
        return dict(counts)

    def export_config(self) -> dict[str, Any]:
        """Export all flag configurations."""
        with self._lock:
            return {name: flag.model_dump() for name, flag in self._flags.items()}

    def import_config(self, config: dict[str, Any]) -> None:
        """Import flag configurations."""
        with self._lock:
            for name, flag_data in config.items():
                flag = FeatureFlag(**flag_data)
                self._flags[name] = flag
        logger.info(f"Imported {len(config)} feature flags")


# ============== Global Manager ==============

_manager: FeatureFlagManager | None = None
_manager_lock = threading.Lock()


def get_feature_flags() -> FeatureFlagManager:
    """Get the global feature flag manager."""
    global _manager
    with _manager_lock:
        if _manager is None:
            _manager = FeatureFlagManager()
        return _manager


# ============== Decorator ==============


def feature_flag(
    name: str,
    default: bool = False,
    fallback_value: Any = None,
) -> Callable:
    """
    Decorator to guard function with feature flag.

    If flag is disabled, returns fallback_value or raises NotImplementedError.

    Args:
        name: Feature flag name
        default: Default if flag not found
        fallback_value: Value to return if disabled

    Example:
        @feature_flag("new_algorithm", fallback_value=[])
        def get_recommendations(user):
            return new_recommendation_engine.run(user)
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            manager = get_feature_flags()

            # Try to extract user context from args/kwargs
            context: dict[str, Any] = {}
            if "user_id" in kwargs:
                context["user_id"] = kwargs["user_id"]
            elif "context" in kwargs:
                context = kwargs["context"]

            # Check flag
            if manager.is_enabled(name, context):
                return func(*args, **kwargs)

            # Flag disabled
            logger.debug(f"Feature flag '{name}' disabled, using fallback")

            if fallback_value is not None:
                return fallback_value

            raise NotImplementedError(f"Feature '{name}' is disabled")

        return wrapper

    return decorator


def flag_variant(
    name: str,
    variants: dict[str, Callable],
    default: str = "control",
) -> Callable:
    """
    Decorator for A/B testing with multiple variants.

    Args:
        name: Flag name
        variants: Map of variant name to implementation function
        default: Default variant

    Example:
        @flag_variant(
            "checkout_flow",
            variants={
                "control": old_checkout,
                "variant_a": new_checkout_v1,
                "variant_b": new_checkout_v2,
            }
        )
        def checkout(user):
            pass  # Implementation determined by variant
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            manager = get_feature_flags()

            # Extract context
            context: dict[str, Any] = {}
            if "user_id" in kwargs:
                context["user_id"] = kwargs["user_id"]

            # Get variant
            variant = manager.get_variant(name, context, default)

            # Execute variant
            if variant in variants:
                return variants[variant](*args, **kwargs)

            # Fallback to original function
            return func(*args, **kwargs)

        return wrapper

    return decorator
