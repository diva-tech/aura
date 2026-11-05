"""
Service container for dependency injection.

Provides:
- Service registration and resolution
- Singleton and transient lifetimes
- Service health monitoring
- Service discovery
- Thread-safe registration and resolution
"""

from __future__ import annotations

import threading
import inspect
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Generic
from dataclasses import dataclass
from datetime import datetime

T = TypeVar("T")


class ServiceLifetime:
    """Service lifetime options"""

    SINGLETON = "singleton"
    TRANSIENT = "transient"


@dataclass
class ServiceDescriptor(Generic[T]):
    """Describes a registered service"""

    service_type: Type[T]
    implementation_type: Optional[Type[T]] = None
    factory: Optional[Callable[..., T]] = None
    instance: Optional[T] = None
    lifetime: str = ServiceLifetime.TRANSIENT
    registered_at: datetime = None

    def __post_init__(self):
        if self.registered_at is None:
            self.registered_at = datetime.utcnow()


class ServiceContainer:
    """
    Dependency injection container.

    Supports:
    - Service registration with interfaces
    - Singleton and transient lifetimes
    - Factory pattern
    - Service discovery
    - Thread-safe registration and resolution
    - Constructor dependency injection
    - Circular dependency detection
    """

    def __init__(self):
        self._descriptors: Dict[Type, ServiceDescriptor] = {}
        self._singletons: Dict[Type, Any] = {}
        self._service_stats: Dict[Type, Dict[str, Any]] = {}
        self._registration_lock = threading.RLock()
        self._singleton_lock = threading.RLock()
        self._resolution_stack: Dict[int, List[Type]] = {}

    def register(
        self,
        service_type: Type[T],
        implementation_type: Optional[Type[T]] = None,
        lifetime: str = ServiceLifetime.TRANSIENT,
    ) -> ServiceContainer:
        """
        Register a service with an implementation type

        Args:
            service_type: The interface type
            implementation_type: The implementation type (defaults to service_type)
            lifetime: SINGLETON or TRANSIENT

        Returns:
            Self for chaining
        """
        impl_type = implementation_type or service_type

        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation_type=impl_type,
            lifetime=lifetime,
        )

        with self._registration_lock:
            self._descriptors[service_type] = descriptor
            self._service_stats[service_type] = {
                "registered_at": descriptor.registered_at.isoformat(),
                "lifetime": lifetime,
                "resolve_count": 0,
            }

        return self

    def register_factory(
        self,
        service_type: Type[T],
        factory: Callable[..., T],
        lifetime: str = ServiceLifetime.TRANSIENT,
    ) -> ServiceContainer:
        """
        Register a service using a factory function

        Args:
            service_type: The interface type
            factory: Factory function to create instances
            lifetime: SINGLETON or TRANSIENT

        Returns:
            Self for chaining
        """
        descriptor = ServiceDescriptor(
            service_type=service_type,
            factory=factory,
            lifetime=lifetime,
        )

        with self._registration_lock:
            self._descriptors[service_type] = descriptor
            self._service_stats[service_type] = {
                "registered_at": descriptor.registered_at.isoformat(),
                "lifetime": lifetime,
                "resolve_count": 0,
            }

        return self

    def register_instance(
        self,
        service_type: Type[T],
        instance: T,
    ) -> ServiceContainer:
        """
        Register a singleton instance

        Args:
            service_type: The interface type
            instance: The instance to register

        Returns:
            Self for chaining
        """
        descriptor = ServiceDescriptor(
            service_type=service_type,
            instance=instance,
            lifetime=ServiceLifetime.SINGLETON,
        )

        with self._registration_lock:
            self._descriptors[service_type] = descriptor
            self._singletons[service_type] = instance
            self._service_stats[service_type] = {
                "registered_at": descriptor.registered_at.isoformat(),
                "lifetime": ServiceLifetime.SINGLETON,
                "resolve_count": 0,
            }

        return self

    def resolve(self, service_type: Type[T]) -> T:
        """
        Resolve a service instance

        Args:
            service_type: The interface type to resolve

        Returns:
            An instance of the service

        Raises:
            ServiceNotFoundError: If service not registered
            ServiceResolutionError: If resolution fails
            CircularDependencyError: If circular dependency detected
        """
        thread_id = threading.get_ident()
        if thread_id not in self._resolution_stack:
            self._resolution_stack[thread_id] = []

        return self._resolve_internal(service_type, self._resolution_stack[thread_id])

    def _resolve_internal(self, service_type: Type[T], resolution_stack: List[Type]) -> T:
        """Internal resolve with circular dependency detection"""
        if service_type in resolution_stack:
            cycle = " -> ".join(t.__name__ for t in resolution_stack + [service_type])
            raise CircularDependencyError(f"Circular dependency detected: {cycle}")

        with self._registration_lock:
            if service_type not in self._descriptors:
                raise ServiceNotFoundError(f"Service {service_type.__name__} not registered")
            descriptor = self._descriptors[service_type]

        resolution_stack.append(service_type)

        try:
            if descriptor.lifetime == ServiceLifetime.SINGLETON:
                with self._singleton_lock:
                    if service_type in self._singletons:
                        instance = self._singletons[service_type]
                    else:
                        instance = self._create_instance(descriptor, resolution_stack)
                        self._singletons[service_type] = instance
            else:
                instance = self._create_instance(descriptor, resolution_stack)

            with self._registration_lock:
                if service_type in self._service_stats:
                    self._service_stats[service_type]["resolve_count"] += 1

            return instance
        finally:
            resolution_stack.pop()

    def _create_instance(self, descriptor: ServiceDescriptor, resolution_stack: List[Type]) -> Any:
        """Create a service instance with constructor dependency injection"""
        try:
            if descriptor.instance is not None:
                return descriptor.instance

            if descriptor.factory is not None:
                return descriptor.factory()

            impl_type = descriptor.implementation_type or descriptor.service_type
            sig = inspect.signature(impl_type.__init__)
            params = {}

            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue

                param_type = param.annotation
                if param_type == inspect.Parameter.empty:
                    continue

                if self.is_registered(param_type):
                    params[param_name] = self._resolve_internal(param_type, resolution_stack)
                elif param.default != inspect.Parameter.empty:
                    params[param_name] = param.default

            return impl_type(**params)
        except Exception as e:
            raise ServiceResolutionError(
                f"Failed to resolve {descriptor.service_type.__name__}: {str(e)}"
            ) from e

    def list_services(self) -> List[Dict[str, Any]]:
        """List all registered services"""
        return [
            {
                "type": descriptor.service_type.__name__,
                "implementation": descriptor.implementation_type.__name__
                if descriptor.implementation_type
                else None,
                "lifetime": descriptor.lifetime,
                "registered_at": descriptor.registered_at.isoformat(),
            }
            for descriptor in self._descriptors.values()
        ]

    def service_count(self) -> int:
        """Get count of registered services"""
        return len(self._descriptors)

    def is_registered(self, service_type: Type) -> bool:
        """Check if a service is registered"""
        return service_type in self._descriptors

    def get_stats(self) -> Dict[str, Any]:
        """Get container statistics"""
        return {
            "service_count": self.service_count(),
            "singleton_count": len(self._singletons),
            "services": self._service_stats,
        }

    def health(self) -> Dict[str, Any]:
        """Get container health status"""
        return {
            "status": "healthy",
            "service_count": self.service_count(),
            "singleton_count": len(self._singletons),
        }


class ServiceNotFoundError(Exception):
    """Raised when a service is not registered"""

    pass


class ServiceResolutionError(Exception):
    """Raised when service resolution fails"""

    pass


class CircularDependencyError(Exception):
    """Raised when circular dependency is detected"""

    pass
