"""
Comprehensive Unit Tests for Feature Flags System
=================================================

Tests cover:
- Flag types and strategies
- Targeting rules evaluation
- Feature flag CRUD operations
- Context-aware evaluation
- Rollout strategies (percentage, whitelist, targeting)
- A/B testing and variants
- Observer pattern for flag changes
- Metrics and analytics
- Decorator patterns
- Edge cases and error handling

MIT Level Testing - 90%+ Coverage Target for feature_flags.py
"""

import threading
import time
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from src.core.feature_flags import (
    FeatureFlag,
    FeatureFlagManager,
    FlagEvaluation,
    FlagType,
    RolloutStrategy,
    TargetingRule,
    feature_flag,
    flag_variant,
    get_feature_flags,
)


class TestFlagType:
    """Tests for FlagType enum."""

    def test_all_flag_types_exist(self):
        """Test all flag types are defined."""
        assert FlagType.RELEASE is not None
        assert FlagType.EXPERIMENT is not None
        assert FlagType.OPS is not None
        assert FlagType.PERMISSION is not None

    def test_flag_type_count(self):
        """Test number of flag types."""
        assert len(FlagType) == 4


class TestRolloutStrategy:
    """Tests for RolloutStrategy enum."""

    def test_all_strategies_exist(self):
        """Test all rollout strategies are defined."""
        assert RolloutStrategy.ALL_USERS.value == "all"
        assert RolloutStrategy.PERCENTAGE.value == "percentage"
        assert RolloutStrategy.WHITELIST.value == "whitelist"
        assert RolloutStrategy.TARGETING.value == "targeting"
        assert RolloutStrategy.RANDOM.value == "random"

    def test_strategy_count(self):
        """Test number of strategies."""
        assert len(RolloutStrategy) == 5


class TestTargetingRule:
    """Tests for TargetingRule evaluation."""

    def test_rule_creation(self):
        """Test creating a targeting rule."""
        rule = TargetingRule(
            attribute="user_type", operator="in", values=["premium", "beta_tester"]
        )

        assert rule.attribute == "user_type"
        assert rule.operator == "in"
        assert rule.values == ["premium", "beta_tester"]

    def test_in_operator_match(self):
        """Test 'in' operator with matching value."""
        rule = TargetingRule(
            attribute="user_type", operator="in", values=["premium", "beta"]
        )

        context = {"user_type": "premium"}
        assert rule.evaluate(context) is True

    def test_in_operator_no_match(self):
        """Test 'in' operator with non-matching value."""
        rule = TargetingRule(
            attribute="user_type", operator="in", values=["premium", "beta"]
        )

        context = {"user_type": "free"}
        assert rule.evaluate(context) is False

    def test_not_in_operator(self):
        """Test 'not_in' operator."""
        rule = TargetingRule(
            attribute="user_type", operator="not_in", values=["blocked", "suspended"]
        )

        assert rule.evaluate({"user_type": "premium"}) is True
        assert rule.evaluate({"user_type": "blocked"}) is False

    def test_equals_operator(self):
        """Test 'equals' operator."""
        rule = TargetingRule(attribute="region", operator="equals", values=["US"])

        assert rule.evaluate({"region": "US"}) is True
        assert rule.evaluate({"region": "EU"}) is False

    def test_not_equals_operator(self):
        """Test 'not_equals' operator."""
        rule = TargetingRule(attribute="version", operator="not_equals", values=["1.0"])

        assert rule.evaluate({"version": "2.0"}) is True
        assert rule.evaluate({"version": "1.0"}) is False

    def test_greater_than_operator(self):
        """Test 'greater_than' operator."""
        rule = TargetingRule(attribute="age", operator="greater_than", values=[18])

        assert rule.evaluate({"age": 25}) is True
        assert rule.evaluate({"age": 15}) is False

    def test_less_than_operator(self):
        """Test 'less_than' operator."""
        rule = TargetingRule(attribute="age", operator="less_than", values=[65])

        assert rule.evaluate({"age": 30}) is True
        assert rule.evaluate({"age": 70}) is False

    def test_missing_attribute(self):
        """Test evaluation with missing attribute."""
        rule = TargetingRule(attribute="missing_attr", operator="in", values=["value"])

        assert rule.evaluate({"other_attr": "value"}) is False

    def test_unknown_operator(self):
        """Test evaluation with unknown operator logs warning."""
        rule = TargetingRule(attribute="test", operator="unknown_op", values=["value"])

        assert rule.evaluate({"test": "value"}) is False

    def test_empty_values_list(self):
        """Test evaluation with empty values list."""
        rule = TargetingRule(attribute="test", operator="equals", values=[])

        assert rule.evaluate({"test": "value"}) is False


class TestFeatureFlag:
    """Tests for FeatureFlag model."""

    def test_minimal_flag_creation(self):
        """Test creating flag with minimal parameters."""
        flag = FeatureFlag(name="test_flag")

        assert flag.name == "test_flag"
        assert flag.enabled is True
        assert flag.flag_type == FlagType.RELEASE
        assert flag.rollout_strategy == RolloutStrategy.ALL_USERS
        assert flag.rollout_percentage == 100
        assert flag.whitelist == []
        assert flag.blacklist == []

    def test_full_flag_creation(self):
        """Test creating flag with all parameters."""
        expires = datetime.now() + timedelta(days=7)
        flag = FeatureFlag(
            name="full_flag",
            enabled=True,
            flag_type=FlagType.EXPERIMENT,
            rollout_strategy=RolloutStrategy.PERCENTAGE,
            rollout_percentage=50,
            whitelist=["user_1", "user_2"],
            blacklist=["user_3"],
            description="Test flag",
            tags=["test", "experiment"],
            expires_at=expires,
        )

        assert flag.name == "full_flag"
        assert flag.flag_type == FlagType.EXPERIMENT
        assert flag.rollout_percentage == 50
        assert len(flag.whitelist) == 2
        assert flag.expires_at == expires

    def test_flag_name_validation(self):
        """Test flag name validation."""
        # Valid names
        FeatureFlag(name="valid_name")
        FeatureFlag(name="valid-name")
        FeatureFlag(name="valid_name_123")

        # Invalid names should raise ValueError
        with pytest.raises(ValueError):
            FeatureFlag(name="invalid name!")  # Space and special char

    def test_is_expired_not_set(self):
        """Test is_expired when expires_at is None."""
        flag = FeatureFlag(name="test")
        assert flag.is_expired() is False

    def test_is_expired_future(self):
        """Test is_expired with future expiration."""
        flag = FeatureFlag(name="test", expires_at=datetime.now() + timedelta(days=1))
        assert flag.is_expired() is False

    def test_is_expired_past(self):
        """Test is_expired with past expiration."""
        flag = FeatureFlag(name="test", expires_at=datetime.now() - timedelta(days=1))
        assert flag.is_expired() is True

    def test_flag_with_targeting_rules(self):
        """Test flag with targeting rules."""
        rule = TargetingRule(attribute="user_type", operator="in", values=["premium"])
        flag = FeatureFlag(name="premium_feature", targeting_rules=[rule])

        assert len(flag.targeting_rules) == 1
        assert flag.targeting_rules[0].attribute == "user_type"

    def test_flag_with_variants(self):
        """Test flag with A/B test variants."""
        flag = FeatureFlag(
            name="ab_test", variants={"control": 50, "variant_a": 30, "variant_b": 20}
        )

        assert len(flag.variants) == 3
        assert flag.variants["control"] == 50


class TestFlagEvaluation:
    """Tests for FlagEvaluation result."""

    def test_evaluation_creation(self):
        """Test creating flag evaluation result."""
        eval_result = FlagEvaluation(
            flag_name="test_flag", enabled=True, reason="whitelisted"
        )

        assert eval_result.flag_name == "test_flag"
        assert eval_result.enabled is True
        assert eval_result.reason == "whitelisted"
        assert eval_result.variant is None

    def test_evaluation_with_variant(self):
        """Test evaluation with A/B test variant."""
        eval_result = FlagEvaluation(
            flag_name="ab_test",
            enabled=True,
            reason="targeting_rules",
            variant="variant_a",
        )

        assert eval_result.variant == "variant_a"


class TestFeatureFlagManager:
    """Tests for FeatureFlagManager."""

    @pytest.fixture
    def manager(self):
        """Create a fresh flag manager for each test."""
        return FeatureFlagManager()

    def test_manager_initialization(self):
        """Test manager initialization."""
        manager = FeatureFlagManager()
        assert manager is not None
        assert manager._flags == {}

    def test_create_flag(self, manager):
        """Test creating a flag."""
        flag = manager.create_flag("test_flag", enabled=True)

        assert flag.name == "test_flag"
        assert flag.enabled is True
        assert "test_flag" in manager._flags

    def test_create_flag_with_options(self, manager):
        """Test creating flag with options."""
        rule = TargetingRule(attribute="user_type", operator="in", values=["premium"])
        flag = manager.create_flag(
            name="premium_feature",
            enabled=True,
            flag_type=FlagType.PERMISSION,
            rollout_strategy=RolloutStrategy.TARGETING,
            rollout_percentage=100,
            whitelist=["vip_user"],
            targeting_rules=[rule],
            description="Premium only feature",
            tags=["premium", "paid"],
        )

        assert flag.flag_type == FlagType.PERMISSION
        assert flag.rollout_strategy == RolloutStrategy.TARGETING
        assert len(flag.whitelist) == 1
        assert len(flag.targeting_rules) == 1
        assert "premium" in flag.tags

    def test_get_flag(self, manager):
        """Test getting a flag."""
        manager.create_flag("test_flag")
        flag = manager.get_flag("test_flag")

        assert flag is not None
        assert flag.name == "test_flag"

    def test_get_nonexistent_flag(self, manager):
        """Test getting nonexistent flag returns None."""
        flag = manager.get_flag("nonexistent")
        assert flag is None

    def test_update_flag(self, manager):
        """Test updating a flag."""
        manager.create_flag("test_flag", enabled=True)
        updated = manager.update_flag("test_flag", enabled=False, rollout_percentage=50)

        assert updated.enabled is False
        assert updated.rollout_percentage == 50

    def test_update_nonexistent_flag_raises_error(self, manager):
        """Test updating nonexistent flag raises ValueError."""
        with pytest.raises(ValueError, match="Flag not found"):
            manager.update_flag("nonexistent", enabled=False)

    def test_delete_flag(self, manager):
        """Test deleting a flag."""
        manager.create_flag("test_flag")
        assert manager.get_flag("test_flag") is not None

        manager.delete_flag("test_flag")
        assert manager.get_flag("test_flag") is None

    def test_delete_nonexistent_flag(self, manager):
        """Test deleting nonexistent flag does nothing."""
        manager.delete_flag("nonexistent")  # Should not raise

    def test_list_all_flags(self, manager):
        """Test listing all flags."""
        manager.create_flag("flag1")
        manager.create_flag("flag2")
        manager.create_flag("flag3")

        flags = manager.list_flags()
        assert len(flags) == 3

    def test_list_flags_by_type(self, manager):
        """Test listing flags filtered by type."""
        manager.create_flag("release1", flag_type=FlagType.RELEASE)
        manager.create_flag("experiment1", flag_type=FlagType.EXPERIMENT)
        manager.create_flag("release2", flag_type=FlagType.RELEASE)

        release_flags = manager.list_flags(flag_type=FlagType.RELEASE)
        assert len(release_flags) == 2

    def test_list_flags_by_tags(self, manager):
        """Test listing flags filtered by tags."""
        manager.create_flag("flag1", tags=["frontend", "beta"])
        manager.create_flag("flag2", tags=["backend", "beta"])
        manager.create_flag("flag3", tags=["frontend", "stable"])

        beta_flags = manager.list_flags(tags=["beta"])
        assert len(beta_flags) == 2

        frontend_beta_flags = manager.list_flags(tags=["frontend", "beta"])
        assert len(frontend_beta_flags) == 1

    def test_is_enabled_flag_not_found(self, manager):
        """Test is_enabled returns False for nonexistent flag."""
        assert manager.is_enabled("nonexistent") is False

    def test_is_enabled_globally_disabled(self, manager):
        """Test is_enabled returns False for disabled flag."""
        manager.create_flag("disabled_flag", enabled=False)
        assert manager.is_enabled("disabled_flag") is False

    def test_is_enabled_all_users_strategy(self, manager):
        """Test is_enabled with ALL_USERS strategy."""
        manager.create_flag(
            "all_users_flag", rollout_strategy=RolloutStrategy.ALL_USERS
        )
        assert manager.is_enabled("all_users_flag") is True

    def test_is_enabled_with_whitelist(self, manager):
        """Test is_enabled with whitelisted user."""
        manager.create_flag("whitelist_flag", whitelist=["user_123", "user_456"])

        context = {"user_id": "user_123"}
        assert manager.is_enabled("whitelist_flag", context) is True

        context = {"user_id": "user_999"}
        assert (
            manager.is_enabled("whitelist_flag", context) is True
        )  # ALL_USERS by default

    def test_is_enabled_with_blacklist(self, manager):
        """Test is_enabled with blacklisted user."""
        manager.create_flag("blacklist_flag")
        manager.update_flag("blacklist_flag", blacklist=["banned_user"])

        context = {"user_id": "banned_user"}
        assert manager.is_enabled("blacklist_flag", context) is False

        context = {"user_id": "normal_user"}
        assert manager.is_enabled("blacklist_flag", context) is True

    def test_is_enabled_expired_flag(self, manager):
        """Test is_enabled returns False for expired flag."""
        manager.create_flag(
            "expired_flag", expires_at=datetime.now() - timedelta(days=1)
        )
        assert manager.is_enabled("expired_flag") is False

    def test_percentage_rollout_consistency(self, manager):
        """Test percentage rollout is consistent for same user."""
        manager.create_flag(
            "percentage_flag",
            rollout_strategy=RolloutStrategy.PERCENTAGE,
            rollout_percentage=50,
        )

        context = {"user_id": "consistent_user"}
        result1 = manager.is_enabled("percentage_flag", context)
        result2 = manager.is_enabled("percentage_flag", context)
        result3 = manager.is_enabled("percentage_flag", context)

        # Should be consistent across multiple evaluations
        assert result1 == result2 == result3

    def test_percentage_rollout_distribution(self, manager):
        """Test percentage rollout approximates desired percentage."""
        manager.create_flag(
            "50percent_flag",
            rollout_strategy=RolloutStrategy.PERCENTAGE,
            rollout_percentage=50,
        )

        enabled_count = 0
        total_users = 1000

        for i in range(total_users):
            context = {"user_id": f"user_{i}"}
            if manager.is_enabled("50percent_flag", context):
                enabled_count += 1

        # Should be approximately 50% (within 10% margin)
        ratio = enabled_count / total_users
        assert 0.40 <= ratio <= 0.60

    def test_percentage_rollout_0_percent(self, manager):
        """Test 0% rollout disables for all users."""
        manager.create_flag(
            "0percent_flag",
            rollout_strategy=RolloutStrategy.PERCENTAGE,
            rollout_percentage=0,
        )

        for i in range(100):
            context = {"user_id": f"user_{i}"}
            assert manager.is_enabled("0percent_flag", context) is False

    def test_percentage_rollout_100_percent(self, manager):
        """Test 100% rollout enables for all users."""
        manager.create_flag(
            "100percent_flag",
            rollout_strategy=RolloutStrategy.PERCENTAGE,
            rollout_percentage=100,
        )

        for i in range(100):
            context = {"user_id": f"user_{i}"}
            assert manager.is_enabled("100percent_flag", context) is True

    def test_targeting_rules_single_rule(self, manager):
        """Test targeting with single rule."""
        rule = TargetingRule(attribute="user_type", operator="in", values=["premium"])
        manager.create_flag(
            "targeting_flag",
            rollout_strategy=RolloutStrategy.TARGETING,
            targeting_rules=[rule],
        )

        assert manager.is_enabled("targeting_flag", {"user_type": "premium"}) is True
        assert manager.is_enabled("targeting_flag", {"user_type": "free"}) is False

    def test_targeting_rules_multiple_rules_and_logic(self, manager):
        """Test targeting with multiple rules (AND logic)."""
        rule1 = TargetingRule(attribute="user_type", operator="in", values=["premium"])
        rule2 = TargetingRule(attribute="region", operator="equals", values=["US"])
        manager.create_flag(
            "multi_rule_flag",
            rollout_strategy=RolloutStrategy.TARGETING,
            targeting_rules=[rule1, rule2],
        )

        # Both rules must match
        assert (
            manager.is_enabled(
                "multi_rule_flag", {"user_type": "premium", "region": "US"}
            )
            is True
        )
        assert (
            manager.is_enabled(
                "multi_rule_flag", {"user_type": "premium", "region": "EU"}
            )
            is False
        )
        assert (
            manager.is_enabled("multi_rule_flag", {"user_type": "free", "region": "US"})
            is False
        )

    def test_evaluate_returns_evaluation_object(self, manager):
        """Test evaluate returns full evaluation object."""
        manager.create_flag("test_flag")
        evaluation = manager.evaluate("test_flag", {})

        assert isinstance(evaluation, FlagEvaluation)
        assert evaluation.flag_name == "test_flag"
        assert evaluation.enabled is True
        assert evaluation.reason == "all_users"

    def test_evaluate_with_whitelist_reason(self, manager):
        """Test evaluate returns correct reason for whitelisted user."""
        manager.create_flag("whitelist_flag", whitelist=["vip"])
        evaluation = manager.evaluate("whitelist_flag", {"user_id": "vip"})

        assert evaluation.enabled is True
        assert evaluation.reason == "whitelisted"

    def test_evaluate_with_percentage_reason(self, manager):
        """Test evaluate returns percentage reason."""
        manager.create_flag(
            "percentage_flag",
            rollout_strategy=RolloutStrategy.PERCENTAGE,
            rollout_percentage=75,
        )
        evaluation = manager.evaluate("percentage_flag", {"user_id": "test"})

        assert "percentage_rollout" in evaluation.reason

    def test_get_variant_flag_disabled(self, manager):
        """Test get_variant returns default when flag disabled."""
        manager.create_flag("ab_test", enabled=False)
        variant = manager.get_variant("ab_test", {}, default="control")

        assert variant == "control"

    def test_get_variant_no_variants_defined(self, manager):
        """Test get_variant returns default when no variants defined."""
        manager.create_flag("simple_flag")
        variant = manager.get_variant("simple_flag", {}, default="control")

        assert variant == "control"

    def test_get_variant_with_variants(self, manager):
        """Test get_variant selects variant consistently."""
        manager.create_flag("ab_test")
        manager.update_flag(
            "ab_test", variants={"control": 50, "variant_a": 30, "variant_b": 20}
        )

        context = {"user_id": "user_123"}
        variant1 = manager.get_variant("ab_test", context)
        variant2 = manager.get_variant("ab_test", context)

        # Should be consistent
        assert variant1 == variant2
        assert variant1 in ["control", "variant_a", "variant_b"]

    def test_get_variant_distribution(self, manager):
        """Test variant distribution approximates weights."""
        manager.create_flag("ab_test")
        manager.update_flag("ab_test", variants={"control": 50, "variant_a": 50})

        variant_counts = {"control": 0, "variant_a": 0}
        total_users = 1000

        for i in range(total_users):
            context = {"user_id": f"user_{i}"}
            variant = manager.get_variant("ab_test", context)
            variant_counts[variant] += 1

        # Should be approximately 50/50 (within 10% margin)
        ratio = variant_counts["control"] / total_users
        assert 0.40 <= ratio <= 0.60

    def test_observer_notification(self, manager):
        """Test observers are notified of flag changes."""
        notifications = []

        def callback(flag_name, enabled):
            notifications.append((flag_name, enabled))

        manager.register_observer(callback)
        manager.create_flag("test_flag", enabled=True)

        # Update flag to trigger notification
        manager.update_flag("test_flag", enabled=False)

        assert len(notifications) == 1
        assert notifications[0] == ("test_flag", False)

    def test_multiple_observers(self, manager):
        """Test multiple observers are notified."""
        notifications1 = []
        notifications2 = []

        def callback1(flag_name, enabled):
            notifications1.append((flag_name, enabled))

        def callback2(flag_name, enabled):
            notifications2.append((flag_name, enabled))

        manager.register_observer(callback1)
        manager.register_observer(callback2)

        manager.create_flag("test_flag")
        manager.update_flag("test_flag", enabled=False)

        assert len(notifications1) == 1
        assert len(notifications2) == 1

    def test_observer_error_handling(self, manager):
        """Test observer errors don't break other observers."""
        notifications = []

        def failing_callback(flag_name, enabled):
            raise Exception("Observer error")

        def working_callback(flag_name, enabled):
            notifications.append((flag_name, enabled))

        manager.register_observer(failing_callback)
        manager.register_observer(working_callback)

        manager.create_flag("test_flag")
        manager.update_flag("test_flag", enabled=False)

        # Working callback should still be notified
        assert len(notifications) == 1

    def test_get_stats(self, manager):
        """Test getting flag statistics."""
        manager.create_flag("flag1", enabled=True)
        manager.create_flag("flag2", enabled=False)
        manager.create_flag("flag3", enabled=True, flag_type=FlagType.EXPERIMENT)

        # Make some evaluations
        manager.is_enabled("flag1")
        manager.is_enabled("flag1")
        manager.is_enabled("flag2")

        stats = manager.get_stats()

        assert stats["total_flags"] == 3
        assert stats["enabled_flags"] == 2
        assert stats["disabled_flags"] == 1
        assert stats["evaluation_counts"]["flag1"] == 2
        assert stats["evaluation_counts"]["flag2"] == 1
        assert "flags_by_type" in stats

    def test_export_config(self, manager):
        """Test exporting flag configurations."""
        manager.create_flag("flag1", enabled=True, description="Test flag")
        manager.create_flag("flag2", enabled=False)

        config = manager.export_config()

        assert len(config) == 2
        assert "flag1" in config
        assert "flag2" in config
        assert config["flag1"]["enabled"] is True
        assert config["flag1"]["description"] == "Test flag"

    def test_import_config(self, manager):
        """Test importing flag configurations."""
        # Export a flag first to get correct format
        manager.create_flag(
            "flag1", enabled=True, description="Imported flag", tags=["imported"]
        )
        config = manager.export_config()

        # Clear manager
        manager._flags.clear()

        # Import it back
        manager.import_config(config)

        flag = manager.get_flag("flag1")
        assert flag is not None
        assert flag.enabled is True
        assert flag.description == "Imported flag"

    def test_thread_safety(self, manager):
        """Test manager is thread-safe."""

        def create_flags(start_idx):
            for i in range(start_idx, start_idx + 10):
                manager.create_flag(f"flag_{i}")

        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_flags, args=(i * 10,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        flags = manager.list_flags()
        assert len(flags) == 50


class TestGlobalManager:
    """Tests for global feature flag manager singleton."""

    def test_get_global_manager(self):
        """Test getting global manager."""
        manager = get_feature_flags()
        assert manager is not None
        assert isinstance(manager, FeatureFlagManager)

    def test_global_manager_singleton(self):
        """Test global manager is singleton."""
        manager1 = get_feature_flags()
        manager2 = get_feature_flags()

        assert manager1 is manager2


class TestFeatureFlagDecorator:
    """Tests for @feature_flag decorator."""

    def test_decorator_enabled_flag(self):
        """Test decorator allows function execution when flag enabled."""
        manager = FeatureFlagManager()
        manager.create_flag("test_feature", enabled=True)

        # Mock the global manager
        with patch("src.core.feature_flags.get_feature_flags", return_value=manager):

            @feature_flag("test_feature")
            def my_function():
                return "success"

            result = my_function()
            assert result == "success"

    def test_decorator_disabled_flag_with_fallback(self):
        """Test decorator returns fallback when flag disabled."""
        manager = FeatureFlagManager()
        manager.create_flag("test_feature", enabled=False)

        with patch("src.core.feature_flags.get_feature_flags", return_value=manager):

            @feature_flag("test_feature", fallback_value="fallback")
            def my_function():
                return "success"

            result = my_function()
            assert result == "fallback"

    def test_decorator_disabled_flag_no_fallback_raises(self):
        """Test decorator raises NotImplementedError when disabled without fallback."""
        manager = FeatureFlagManager()
        manager.create_flag("test_feature", enabled=False)

        with patch("src.core.feature_flags.get_feature_flags", return_value=manager):

            @feature_flag("test_feature")
            def my_function():
                return "success"

            with pytest.raises(
                NotImplementedError, match="Feature 'test_feature' is disabled"
            ):
                my_function()

    def test_decorator_extracts_user_id_from_kwargs(self):
        """Test decorator extracts user_id from kwargs for context."""
        manager = FeatureFlagManager()
        manager.create_flag("premium_feature", whitelist=["vip_user"])

        with patch("src.core.feature_flags.get_feature_flags", return_value=manager):

            @feature_flag("premium_feature")
            def premium_function(user_id=None):
                return "premium content"

            # Should work for whitelisted user even if global flag uses whitelist
            result = premium_function(user_id="vip_user")
            assert result == "premium content"

    def test_decorator_preserves_function_metadata(self):
        """Test decorator preserves original function metadata."""
        manager = FeatureFlagManager()
        manager.create_flag("test_feature", enabled=True)

        with patch("src.core.feature_flags.get_feature_flags", return_value=manager):

            @feature_flag("test_feature")
            def documented_function():
                """This is documentation."""
                return "result"

            assert documented_function.__name__ == "documented_function"
            assert "documentation" in documented_function.__doc__


class TestFlagVariantDecorator:
    """Tests for @flag_variant decorator."""

    def test_variant_decorator_selects_variant(self):
        """Test variant decorator selects correct implementation."""
        manager = FeatureFlagManager()
        manager.create_flag("checkout_flow")
        manager.update_flag("checkout_flow", variants={"control": 50, "variant_a": 50})

        def control_impl(user_id=None):
            return "control"

        def variant_a_impl(user_id=None):
            return "variant_a"

        with patch("src.core.feature_flags.get_feature_flags", return_value=manager):

            @flag_variant(
                "checkout_flow",
                variants={"control": control_impl, "variant_a": variant_a_impl},
            )
            def checkout(user_id=None):
                return "default"

            # Should return variant result, not default
            result = checkout(user_id="test_user")
            assert result in ["control", "variant_a"]

    def test_variant_decorator_falls_back_to_original(self):
        """Test variant decorator falls back to original function for unknown variant."""
        manager = FeatureFlagManager()
        manager.create_flag("test_variants")

        def variant_impl(user_id=None):
            return "variant"

        with patch("src.core.feature_flags.get_feature_flags", return_value=manager):
            # Mock get_variant to return unknown variant
            with patch.object(manager, "get_variant", return_value="unknown_variant"):

                @flag_variant("test_variants", variants={"known": variant_impl})
                def my_function(user_id=None):
                    return "default"

                result = my_function(user_id="test")
                assert result == "default"


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_percentage_with_empty_user_id(self):
        """Test percentage rollout with empty user_id."""
        manager = FeatureFlagManager()
        manager.create_flag(
            "test_flag",
            rollout_strategy=RolloutStrategy.PERCENTAGE,
            rollout_percentage=50,
        )

        # Should handle empty string user_id
        result = manager.is_enabled("test_flag", {"user_id": ""})
        assert isinstance(result, bool)

    def test_targeting_with_empty_rules(self):
        """Test targeting with empty rules list."""
        manager = FeatureFlagManager()
        manager.create_flag(
            "test_flag", rollout_strategy=RolloutStrategy.TARGETING, targeting_rules=[]
        )

        # Empty rules should enable for all
        assert manager.is_enabled("test_flag", {}) is True

    def test_concurrent_flag_creation(self):
        """Test concurrent flag creation doesn't cause issues."""
        manager = FeatureFlagManager()
        errors = []
        counter = [0]
        lock = threading.Lock()

        def create_many_flags():
            try:
                for _ in range(100):
                    with lock:
                        idx = counter[0]
                        counter[0] += 1
                    manager.create_flag(f"flag_{idx}")
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=create_many_flags) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0

    def test_evaluation_metrics_tracking(self):
        """Test that evaluation and enabled counts are tracked correctly."""
        manager = FeatureFlagManager()
        manager.create_flag("tracked_flag", rollout_percentage=100)

        # Make several evaluations
        for _ in range(5):
            manager.is_enabled("tracked_flag", {"user_id": "test"})

        stats = manager.get_stats()
        assert stats["evaluation_counts"]["tracked_flag"] == 5
        assert stats["enabled_counts"]["tracked_flag"] == 5

    def test_whitelist_blacklist_precedence(self):
        """Test blacklist takes precedence over rollout strategy."""
        manager = FeatureFlagManager()
        manager.create_flag("test_flag", rollout_strategy=RolloutStrategy.ALL_USERS)
        manager.update_flag("test_flag", blacklist=["banned_user"])

        assert manager.is_enabled("test_flag", {"user_id": "normal_user"}) is True
        assert manager.is_enabled("test_flag", {"user_id": "banned_user"}) is False

    def test_whitelist_precedence_over_percentage(self):
        """Test whitelist takes precedence over percentage rollout."""
        manager = FeatureFlagManager()
        manager.create_flag(
            "test_flag",
            rollout_strategy=RolloutStrategy.PERCENTAGE,
            rollout_percentage=0,  # 0% rollout
            whitelist=["vip_user"],
        )

        # VIP should be enabled despite 0% rollout
        assert manager.is_enabled("test_flag", {"user_id": "vip_user"}) is True

        # Regular users should be disabled
        assert manager.is_enabled("test_flag", {"user_id": "regular_user"}) is False

    def test_variant_with_zero_weights(self):
        """Test variant selection with all zero weights."""
        manager = FeatureFlagManager()
        manager.create_flag("zero_weight_test")
        manager.update_flag("zero_weight_test", variants={"control": 0, "variant_a": 0})

        variant = manager.get_variant("zero_weight_test", {"user_id": "test"})
        # Should return first variant when all weights are zero
        assert variant in ["control", "variant_a"]

    def test_flag_update_updates_timestamp(self):
        """Test that updating a flag updates the updated_at timestamp."""
        manager = FeatureFlagManager()
        flag = manager.create_flag("test_flag")

        original_time = flag.updated_at
        time.sleep(0.01)  # Small delay to ensure timestamp difference

        manager.update_flag("test_flag", rollout_percentage=75)
        updated_flag = manager.get_flag("test_flag")

        assert updated_flag.updated_at > original_time
