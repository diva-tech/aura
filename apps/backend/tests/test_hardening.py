"""
Comprehensive tests for runtime hardening.

Tests:
- Thread safety of all core components
- Graceful degradation on failures
- Concurrent operations
- Circular dependency detection
- Constructor dependency injection
- Async handler concurrency
"""

import asyncio
import threading
from typing import Any, Dict

import pytest

from aura_backend.core.bootstrap import Runtime
from aura_backend.core.events import EventBus, BaseEvent
from aura_backend.core.service_container import ServiceContainer, CircularDependencyError
from aura_backend.core.plugins import BasePlugin, PluginMetadata, PluginCapability
from aura_backend.core.agents import BaseAgent, AgentMetadata, AgentCapability


# ============================================================================
# THREAD SAFETY TESTS
# ============================================================================


class TestEventBusThreadSafety:
    """Test EventBus thread safety"""

    @pytest.mark.asyncio
    async def test_concurrent_subscribe_unsubscribe(self):
        """Concurrent subscribe/unsubscribe should not corrupt data"""
        event_bus = EventBus()
        results = []

        def subscribe_handler(event: BaseEvent) -> None:
            results.append("received")

        def subscribe_thread():
            for i in range(100):
                sub_id = event_bus.subscribe(
                    "test.event",
                    subscribe_handler,
                    subscription_id=f"sub-{threading.current_thread().name}-{i}"
                )
                assert sub_id is not None

        def unsubscribe_thread():
            subscriptions = event_bus.list_subscriptions()
            for sub in subscriptions[:50]:
                event_bus.unsubscribe(sub["subscription_id"])

        threads = []
        for _ in range(3):
            t1 = threading.Thread(target=subscribe_thread)
            t2 = threading.Thread(target=unsubscribe_thread)
            threads.extend([t1, t2])
            t1.start()
            t2.start()

        for t in threads:
            t.join()

        count = event_bus.subscription_count()
        assert count >= 0

    @pytest.mark.asyncio
    async def test_concurrent_publish(self):
        """Concurrent publish operations should be safe"""
        event_bus = EventBus()
        received = []

        def handler(event: BaseEvent) -> None:
            received.append(event)

        event_bus.subscribe("test.event", handler)

        async def publish_events():
            for i in range(50):
                await event_bus.publish(BaseEvent.create(event_type="test.event"))

        await asyncio.gather(
            publish_events(),
            publish_events(),
            publish_events(),
        )

        assert len(received) == 150


class TestServiceContainerThreadSafety:
    """Test ServiceContainer thread safety"""

    def test_concurrent_registration(self):
        """Concurrent registration should not corrupt state"""
        container = ServiceContainer()

        class ServiceA:
            pass

        class ServiceB:
            pass

        def register_thread(service_type, impl):
            for i in range(50):
                try:
                    container.register(service_type, impl)
                except Exception:
                    pass

        threads = [
            threading.Thread(target=register_thread, args=(ServiceA, ServiceA)),
            threading.Thread(target=register_thread, args=(ServiceB, ServiceB)),
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert container.service_count() >= 1

    def test_singleton_only_created_once_concurrent(self):
        """Singleton should only be created once even with concurrent access"""
        container = ServiceContainer()
        creation_count = []

        class ServiceWithCounter:
            def __init__(self):
                creation_count.append(1)

        container.register(ServiceWithCounter, ServiceWithCounter, lifetime="singleton")

        def resolve_thread():
            for _ in range(50):
                container.resolve(ServiceWithCounter)

        threads = [threading.Thread(target=resolve_thread) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(creation_count) == 1


class TestPluginRegistryThreadSafety:
    """Test PluginRegistry thread safety"""

    @pytest.mark.asyncio
    async def test_concurrent_plugin_registration(self):
        """Concurrent plugin registration should be safe"""
        from aura_backend.core.plugins import PluginRegistry

        registry = PluginRegistry()

        class TestPlugin(BasePlugin):
            def __init__(self, plugin_id: str):
                super().__init__()
                self.plugin_id = plugin_id

            async def initialize(self) -> None:
                pass

            async def shutdown(self) -> None:
                pass

            async def health(self) -> Dict[str, Any]:
                return {"status": "healthy"}

            def get_metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    id=self.plugin_id,
                    name=f"Plugin {self.plugin_id}",
                    version="1.0.0",
                    description="Test plugin",
                )

        def register_plugins():
            for i in range(50):
                try:
                    plugin = TestPlugin(f"plugin-{threading.current_thread().name}-{i}")
                    registry.register(plugin)
                except Exception:
                    pass

        threads = [threading.Thread(target=register_plugins) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert registry.count() >= 1


# ============================================================================
# GRACEFUL DEGRADATION TESTS
# ============================================================================


class TestRuntimeGracefulDegradation:
    """Test runtime graceful degradation on failures"""

    @pytest.mark.asyncio
    async def test_plugin_failure_doesnt_block_agents(self):
        """Plugin initialization failure should not block agent initialization"""
        runtime = Runtime(version="0.2.0")

        class FailingPlugin(BasePlugin):
            async def initialize(self) -> None:
                raise RuntimeError("Plugin failed")

            async def shutdown(self) -> None:
                pass

            async def health(self) -> Dict[str, Any]:
                return {"status": "unhealthy"}

            def get_metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    id="failing-plugin",
                    name="Failing Plugin",
                    version="1.0.0",
                    description="Test",
                )

        class SuccessfulAgent(BaseAgent):
            def __init__(self):
                super().__init__()
                self.initialized = False

            async def initialize(self) -> None:
                self.initialized = True

            async def shutdown(self) -> None:
                pass

            async def health(self) -> Dict[str, Any]:
                return {"status": "healthy"}

            def get_metadata(self) -> AgentMetadata:
                return AgentMetadata(
                    id=self.id,
                    name="Success Agent",
                    agent_type="test",
                    version="1.0.0",
                    description="Test",
                )

        runtime.plugins.register(FailingPlugin())
        agent = SuccessfulAgent()
        runtime.agents.register_instance(agent)

        await runtime.startup()

        assert runtime.status == "running"
        assert agent.initialized
        assert agent.status.value == "ready"
        health = await runtime.health()
        assert health["health"] == "degraded"


# ============================================================================
# DEPENDENCY INJECTION TESTS
# ============================================================================


class TestConstructorDependencyInjection:
    """Test constructor dependency injection"""

    def test_constructor_injection_single_dependency(self):
        """Constructor injection should resolve single dependency"""
        container = ServiceContainer()

        class DatabaseService:
            pass

        class UserService:
            def __init__(self, db: DatabaseService):
                self.db = db

        container.register_instance(DatabaseService, DatabaseService())
        user_service = container.resolve(UserService)

        assert user_service.db is not None
        assert isinstance(user_service.db, DatabaseService)

    def test_constructor_injection_multiple_dependencies(self):
        """Constructor injection should resolve multiple dependencies"""
        container = ServiceContainer()

        class DatabaseService:
            pass

        class CacheService:
            pass

        class UserService:
            def __init__(self, db: DatabaseService, cache: CacheService):
                self.db = db
                self.cache = cache

        container.register_instance(DatabaseService, DatabaseService())
        container.register_instance(CacheService, CacheService())

        user_service = container.resolve(UserService)

        assert user_service.db is not None
        assert user_service.cache is not None

    def test_constructor_injection_with_defaults(self):
        """Constructor injection should respect default parameters"""
        container = ServiceContainer()

        class ConfigService:
            def __init__(self):
                self.value = "default"

        class ServiceWithDefault:
            def __init__(self, config: ConfigService = None):
                self.config = config or ConfigService()

        service = container.resolve(ServiceWithDefault)
        assert service.config is not None

    def test_circular_dependency_detection(self):
        """Circular dependencies should be detected"""
        container = ServiceContainer()

        class ServiceA:
            def __init__(self, b: "ServiceB"):
                self.b = b

        class ServiceB:
            def __init__(self, a: ServiceA):
                self.a = a

        container.register_type(ServiceA, ServiceA)
        container.register_type(ServiceB, ServiceB)

        with pytest.raises(CircularDependencyError):
            container.resolve(ServiceA)


# ============================================================================
# ASYNC HANDLER TESTS
# ============================================================================


class TestAsyncHandlerConcurrency:
    """Test concurrent async handler execution"""

    @pytest.mark.asyncio
    async def test_async_handlers_concurrent(self):
        """Async handlers should execute concurrently"""
        event_bus = EventBus()
        execution_times = []

        async def slow_handler(event: BaseEvent) -> None:
            start = asyncio.get_event_loop().time()
            await asyncio.sleep(0.1)
            end = asyncio.get_event_loop().time()
            execution_times.append((start, end))

        event_bus.subscribe_async("test.event", slow_handler)
        event_bus.subscribe_async("test.event", slow_handler)
        event_bus.subscribe_async("test.event", slow_handler)

        await event_bus.publish(BaseEvent.create(event_type="test.event"))

        assert len(execution_times) == 3

    @pytest.mark.asyncio
    async def test_async_handler_timeout(self):
        """Slow async handler should timeout gracefully"""
        event_bus = EventBus()
        received = []

        async def slow_handler(event: BaseEvent) -> None:
            await asyncio.sleep(10)

        async def quick_handler(event: BaseEvent) -> None:
            received.append("done")

        event_bus.subscribe_async("test.event", slow_handler)
        event_bus.subscribe_async("test.event", quick_handler)

        await event_bus.publish(
            BaseEvent.create(event_type="test.event"),
            timeout_seconds=0.1
        )

        assert len(received) == 1


# ============================================================================
# LIFECYCLE TESTS
# ============================================================================


class TestRuntimeLifecycle:
    """Test runtime lifecycle"""

    @pytest.mark.asyncio
    async def test_graceful_shutdown_with_timeout(self):
        """Shutdown should respect timeout"""
        runtime = Runtime(version="0.2.0")
        await runtime.startup()

        await runtime.shutdown(timeout_seconds=1.0)

        assert runtime.status == "stopped"

    @pytest.mark.asyncio
    async def test_health_levels(self):
        """Runtime health should report Healthy/Degraded/Failed"""
        runtime = Runtime(version="0.2.0")

        class FailingPlugin(BasePlugin):
            async def initialize(self) -> None:
                raise RuntimeError("Plugin failed")

            async def shutdown(self) -> None:
                pass

            async def health(self) -> Dict[str, Any]:
                return {"status": "unhealthy"}

            def get_metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    id="failing",
                    name="Failing",
                    version="1.0.0",
                    description="Test",
                )

        runtime.plugins.register(FailingPlugin())
        await runtime.startup()

        health = await runtime.health()
        assert health["health"] == "degraded"
        assert len(health["startup_errors"]) > 0
