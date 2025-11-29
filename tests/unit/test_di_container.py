"""
Unit tests for Dependency Injection Container.

Tests cover:
- Lifetime enum
- Container registration
- Container resolution
- Singleton, Transient, Scoped lifetimes
- Factory registration
- Instance registration
- Error handling

MIT Level Testing - 85%+ Coverage Target
"""

from unittest.mock import Mock

import pytest

from src.core.di.container import (
    CircularDependencyError,
    Container,
    DependencyNotFoundError,
    Lifetime,
    Registration,
)


class TestLifetime:
    """Tests for Lifetime enum."""

    def test_lifetime_values(self):
        """Test all lifetime values exist."""
        assert Lifetime.SINGLETON is not None
        assert Lifetime.TRANSIENT is not None
        assert Lifetime.SCOPED is not None

    def test_lifetime_unique_values(self):
        """Test lifetime values are unique."""
        values = [Lifetime.SINGLETON, Lifetime.TRANSIENT, Lifetime.SCOPED]
        assert len(set(values)) == 3


class TestRegistration:
    """Tests for Registration dataclass."""

    def test_basic_registration(self):
        """Test basic registration creation."""
        reg = Registration(
            service_type=str,
            implementation=str,
            lifetime=Lifetime.TRANSIENT,
        )
        assert reg.service_type is str
        assert reg.implementation is str
        assert reg.lifetime == Lifetime.TRANSIENT

    def test_registration_with_factory(self):
        """Test registration with factory."""
        factory = Mock()
        reg = Registration(
            service_type=str,
            implementation=str,
            lifetime=Lifetime.SINGLETON,
            factory=factory,
        )
        assert reg.factory == factory

    def test_registration_with_instance(self):
        """Test registration with instance."""
        instance = "test_instance"
        reg = Registration(
            service_type=str,
            implementation=str,
            lifetime=Lifetime.SINGLETON,
            instance=instance,
        )
        assert reg.instance == instance

    def test_registration_with_tags(self):
        """Test registration with tags."""
        reg = Registration(
            service_type=str,
            implementation=str,
            lifetime=Lifetime.TRANSIENT,
            tags={"tag1", "tag2"},
        )
        assert "tag1" in reg.tags
        assert "tag2" in reg.tags


class TestContainerBasics:
    """Tests for Container basic operations."""

    def test_create_container(self):
        """Test container creation."""
        container = Container()
        assert container is not None

    def test_container_with_parent(self):
        """Test container with parent."""
        parent = Container()
        child = Container(parent=parent)
        assert child._parent == parent

    def test_register_concrete_type(self):
        """Test registering concrete type."""
        container = Container()

        class MyService:
            pass

        container.register(MyService)
        assert MyService in container._registrations

    def test_register_with_implementation(self):
        """Test registering interface with implementation."""
        container = Container()

        class IService:
            pass

        class ServiceImpl(IService):
            pass

        container.register(IService, ServiceImpl)
        assert IService in container._registrations

    def test_register_with_lifetime(self):
        """Test registering with specific lifetime."""
        container = Container()

        class MyService:
            pass

        container.register(MyService, lifetime=Lifetime.SINGLETON)
        reg = container._registrations[MyService]
        assert reg.lifetime == Lifetime.SINGLETON


class TestContainerResolution:
    """Tests for Container resolution."""

    def test_resolve_simple_type(self):
        """Test resolving simple type."""
        container = Container()

        class SimpleService:
            pass

        container.register(SimpleService)
        service = container.resolve(SimpleService)
        assert isinstance(service, SimpleService)

    def test_resolve_singleton(self):
        """Test singleton returns same instance."""
        container = Container()

        class SingletonService:
            pass

        container.register(SingletonService, lifetime=Lifetime.SINGLETON)
        service1 = container.resolve(SingletonService)
        service2 = container.resolve(SingletonService)
        assert service1 is service2

    def test_resolve_transient(self):
        """Test transient returns new instance each time."""
        container = Container()

        class TransientService:
            pass

        container.register(TransientService, lifetime=Lifetime.TRANSIENT)
        service1 = container.resolve(TransientService)
        service2 = container.resolve(TransientService)
        assert service1 is not service2

    def test_resolve_not_registered(self):
        """Test resolving unregistered type raises error."""
        container = Container()

        class UnregisteredService:
            pass

        with pytest.raises(DependencyNotFoundError):
            container.resolve(UnregisteredService)


class TestContainerFactory:
    """Tests for factory registration."""

    def test_register_factory(self):
        """Test registering factory function."""
        container = Container()
        factory = Mock(return_value="factory_result")

        container.register_factory(str, factory)
        result = container.resolve(str)

        assert result == "factory_result"
        factory.assert_called_once()

    def test_factory_called_each_time_transient(self):
        """Test factory called each time for transient."""
        container = Container()
        call_count = 0

        def factory():
            nonlocal call_count
            call_count += 1
            return f"instance_{call_count}"

        container.register_factory(str, factory, lifetime=Lifetime.TRANSIENT)
        r1 = container.resolve(str)
        r2 = container.resolve(str)

        assert r1 == "instance_1"
        assert r2 == "instance_2"

    def test_factory_singleton(self):
        """Test factory called once for singleton."""
        container = Container()
        call_count = 0

        def factory():
            nonlocal call_count
            call_count += 1
            return f"instance_{call_count}"

        container.register_factory(str, factory, lifetime=Lifetime.SINGLETON)
        r1 = container.resolve(str)
        r2 = container.resolve(str)

        assert r1 == "instance_1"
        assert r2 == "instance_1"
        assert call_count == 1


class TestContainerInstance:
    """Tests for instance registration."""

    def test_register_instance(self):
        """Test registering pre-created instance."""
        container = Container()
        instance = {"key": "value"}

        container.register_instance(dict, instance)
        resolved = container.resolve(dict)

        assert resolved is instance

    def test_instance_always_same(self):
        """Test instance always returns same object."""
        container = Container()
        instance = [1, 2, 3]

        container.register_instance(list, instance)
        r1 = container.resolve(list)
        r2 = container.resolve(list)

        assert r1 is r2
        assert r1 is instance


class TestContainerExceptions:
    """Tests for container exceptions."""

    def test_circular_dependency_error(self):
        """Test CircularDependencyError."""
        error = CircularDependencyError("Circular dep A -> B -> A")
        assert "Circular" in str(error)

    def test_dependency_not_found_error(self):
        """Test DependencyNotFoundError."""
        error = DependencyNotFoundError("Service not found")
        assert "not found" in str(error)


class TestContainerIsRegistered:
    """Tests for is_registered method."""

    def test_is_registered_true(self):
        """Test is_registered returns true for registered."""
        container = Container()

        class MyService:
            pass

        container.register(MyService)
        assert container.is_registered(MyService)

    def test_is_registered_false(self):
        """Test is_registered returns false for unregistered."""
        container = Container()

        class MyService:
            pass

        assert not container.is_registered(MyService)


class TestContainerParentLookup:
    """Tests for parent container lookup."""

    def test_resolve_from_parent(self):
        """Test resolving from parent container."""
        parent = Container()
        child = Container(parent=parent)

        class ParentService:
            pass

        parent.register(ParentService, lifetime=Lifetime.SINGLETON)
        service = child.resolve(ParentService)

        assert isinstance(service, ParentService)

    def test_child_overrides_parent(self):
        """Test child registration overrides parent."""
        parent = Container()
        child = Container(parent=parent)

        class Service:
            pass

        class ChildServiceImpl(Service):
            pass

        parent.register(Service, lifetime=Lifetime.SINGLETON)
        child.register(Service, ChildServiceImpl, lifetime=Lifetime.SINGLETON)

        child_service = child.resolve(Service)
        assert isinstance(child_service, ChildServiceImpl)

