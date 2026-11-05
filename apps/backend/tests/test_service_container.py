"""
Tests for service container and dependency injection.
"""

import pytest

from aura_backend.core.service_container import (
    ServiceContainer,
    ServiceLifetime,
    ServiceNotFoundError,
)


class DummyService:
    """Dummy service for testing"""

    def __init__(self):
        self.initialized = True


class AnotherService:
    """Another service for testing"""

    def __init__(self, dummy: DummyService):
        self.dummy = dummy


@pytest.fixture
def container():
    """Create a service container"""
    return ServiceContainer()


def test_container_creation(container):
    """Service container creates successfully"""
    assert container is not None


def test_container_register_type(container):
    """Container registers types"""
    container.register_type(DummyService, DummyService)
    assert container.resolve(DummyService) is not None


def test_container_register_instance(container):
    """Container registers instances"""
    instance = DummyService()
    container.register_instance(DummyService, instance)
    resolved = container.resolve(DummyService)
    assert resolved is instance


def test_container_singleton_lifetime(container):
    """Container honors singleton lifetime"""
    container.register_type(
        DummyService, DummyService, ServiceLifetime.SINGLETON
    )
    instance1 = container.resolve(DummyService)
    instance2 = container.resolve(DummyService)
    assert instance1 is instance2


def test_container_transient_lifetime(container):
    """Container honors transient lifetime"""
    container.register_type(
        DummyService, DummyService, ServiceLifetime.TRANSIENT
    )
    instance1 = container.resolve(DummyService)
    instance2 = container.resolve(DummyService)
    assert instance1 is not instance2


def test_container_factory(container):
    """Container resolves via factory"""
    def factory():
        return DummyService()

    container.register_factory(DummyService, factory)
    instance = container.resolve(DummyService)
    assert instance is not None


def test_container_list_services(container):
    """Container lists registered services"""
    container.register_type(DummyService, DummyService)
    container.register_type(AnotherService, AnotherService)
    services = container.list_services()
    assert len(services) == 2


def test_container_service_not_found(container):
    """Container raises error for unknown service"""
    with pytest.raises(ServiceNotFoundError):
        container.resolve(DummyService)


def test_container_health(container):
    """Container health status is correct"""
    container.register_type(DummyService, DummyService)
    health = container.health()
    assert health["status"] == "healthy"
    assert health["total_services"] == 1
