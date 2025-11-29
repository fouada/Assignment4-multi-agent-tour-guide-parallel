"""
Unit tests for DI Scope module.

Tests cover:
- ScopeContext: storing and retrieving scoped instances
- Scope: context manager for scoped dependencies
- scoped decorator

MIT Level Testing - 85%+ Coverage Target
"""

from unittest.mock import Mock

from src.core.di.scope import (
    Scope,
    ScopeContext,
    scoped,
)


class TestScopeContext:
    """Tests for ScopeContext dataclass."""

    def test_initialization(self):
        """Test scope context initialization."""
        ctx = ScopeContext(name="test")
        assert ctx.name == "test"
        assert ctx.instances == {}
        assert ctx.parent is None

    def test_get_returns_none_for_missing(self):
        """Test get returns None for missing type."""
        ctx = ScopeContext(name="test")
        result = ctx.get(str)
        assert result is None

    def test_set_and_get(self):
        """Test set and get instance."""
        ctx = ScopeContext(name="test")
        ctx.set(str, "test_value")
        result = ctx.get(str)
        assert result == "test_value"

    def test_get_from_parent(self):
        """Test get falls back to parent."""
        parent = ScopeContext(name="parent")
        parent.set(str, "parent_value")

        child = ScopeContext(name="child", parent=parent)
        result = child.get(str)
        assert result == "parent_value"

    def test_child_overrides_parent(self):
        """Test child overrides parent value."""
        parent = ScopeContext(name="parent")
        parent.set(str, "parent_value")

        child = ScopeContext(name="child", parent=parent)
        child.set(str, "child_value")

        assert child.get(str) == "child_value"
        assert parent.get(str) == "parent_value"

    def test_dispose_calls_dispose_on_instances(self):
        """Test dispose calls dispose on instances."""
        instance = Mock()
        ctx = ScopeContext(name="test")
        ctx.set(Mock, instance)

        ctx.dispose()
        instance.dispose.assert_called_once()

    def test_dispose_calls_close_if_no_dispose(self):
        """Test dispose calls close if no dispose."""
        instance = Mock(spec=["close"])
        ctx = ScopeContext(name="test")
        ctx.set(Mock, instance)

        ctx.dispose()
        instance.close.assert_called_once()

    def test_dispose_clears_instances(self):
        """Test dispose clears instances dict."""
        ctx = ScopeContext(name="test")
        ctx.set(str, "value")
        ctx.dispose()
        assert ctx.instances == {}

    def test_dispose_handles_errors(self):
        """Test dispose handles errors gracefully."""
        instance = Mock()
        instance.dispose.side_effect = Exception("Dispose failed")
        ctx = ScopeContext(name="test")
        ctx.set(Mock, instance)

        # Should not raise
        ctx.dispose()


class TestScope:
    """Tests for Scope context manager."""

    def test_context_manager_enter_exit(self):
        """Test scope as context manager."""
        with Scope("test_scope") as scope:
            assert scope.name == "test_scope"
            assert scope._context is not None

    def test_nested_scopes(self):
        """Test nested scopes have parent."""
        with Scope("parent"):
            with Scope("child") as child_scope:
                # Child should have parent
                assert child_scope._context.parent is not None

    def test_scope_disposes_on_exit(self):
        """Test scope disposes instances on exit."""
        instance = Mock()

        with Scope("test") as scope:
            scope._context.set(Mock, instance)

        instance.dispose.assert_called_once()

    def test_resolve_returns_scoped_instance(self):
        """Test resolve returns scoped instance."""
        with Scope("test") as scope:
            scope._context.set(str, "scoped_value")
            result = scope.resolve(str)
            assert result == "scoped_value"

    def test_active_scopes_registry(self):
        """Test scope is tracked in active scopes."""
        with Scope("test_registry"):
            # Scope should be tracked while active
            assert "test_registry" in Scope._active_scopes


class TestScopedDecorator:
    """Tests for scoped decorator."""

    def test_scoped_decorator(self):
        """Test scoped decorator wraps function."""

        @scoped
        def my_func():
            return "result"

        # Should work outside scope too
        result = my_func()
        assert result == "result"

    def test_scoped_preserves_metadata(self):
        """Test scoped preserves function metadata."""

        @scoped
        def my_func():
            """My docstring."""
            return "result"

        assert my_func.__name__ == "my_func"
        assert my_func.__doc__ == "My docstring."
