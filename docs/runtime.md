# AURA Runtime Documentation

## Overview

The AURA Runtime is a production-grade, extensible application framework built on Clean Architecture, SOLID principles, and Domain-Driven Design. It provides a foundation for building loosely-coupled, testable, and maintainable applications with sophisticated lifecycle management, event-driven architecture, and plugin extensibility.

## Architecture

### Core Components

The runtime consists of five primary systems:

1. **Event Bus** — Transport-agnostic event system for inter-component communication
2. **Service Container** — Dependency injection container with lifetime management
3. **Plugin Registry** — Dynamic plugin loading, lifecycle management, and capability declaration
4. **Agent Registry** — Managed agent instances with execution tracking and health monitoring
5. **Runtime Bootstrap** — Single entry point coordinating startup/shutdown sequences

### Design Principles

- **Event-Driven**: Components communicate through events; no direct dependencies between plugins or agents
- **Transport-Agnostic**: Event bus can be swapped (in-memory → RabbitMQ/Kafka/Redis) without application changes
- **Type-Safe**: Full type annotations with TypeVar, Generic, and Protocol support
- **Extensible**: Plugins and agents declare capabilities; system is self-documenting
- **Observable**: Structured logging, correlation IDs, trace IDs, and health monitoring
- **Graceful**: Coordinated startup/shutdown with proper ordering and error handling

## Component Responsibilities

### Event Bus

Provides pub/sub event distribution to enable loose coupling between components.

**Key Methods:**
- `subscribe(event_type, handler)` — Register handler for event type
- `publish(event)` — Publish event to all subscribers
- `unsubscribe(subscription)` — Remove subscription

**Event Lifecycle:**
1. Event published with unique event_id, correlation_id, trace_id
2. All sync handlers executed immediately
3. Async handlers executed concurrently
4. Statistics tracked for monitoring

**Built-in Events:**
- `ApplicationStarting` — Before plugins/agents initialize
- `ApplicationStarted` — After all startup complete
- `ApplicationStopping` — Before shutdown begins
- `ApplicationStopped` — After all shutdown complete
- `PluginLoaded` — When plugin initializes
- `PluginUnloaded` — When plugin shuts down
- `AgentRegistered` — When agent registers
- `HealthChanged` — When component health changes

### Service Container

Provides dependency injection with support for singletons, transients, type-based registration, factory functions, and instance registration.

**Registration Patterns:**
```python
# Type-based (creates new instance each time)
container.register_type(IService, ServiceImpl)

# Factory (callable returns instance)
container.register_factory(IService, lambda: ServiceImpl())

# Instance (always returns same object)
container.register_instance(IService, ServiceImpl())
```

**Lifetimes:**
- `SINGLETON` — One instance per container
- `TRANSIENT` — New instance per resolution

### Plugin Registry

Manages plugin lifecycle: registration, initialization, health monitoring, unloading.

**Plugin Requirements:**
- Inherit from `BasePlugin`
- Implement `initialize()`, `shutdown()`, `health()`
- Provide `get_metadata()` and `get_capabilities()`

**Plugin States:**
- UNINITIALIZED → INITIALIZING → INITIALIZED → [ERROR] → SHUTTING_DOWN → SHUT_DOWN

### Agent Registry

Manages agent registration, instantiation, and execution tracking.

**Agent Requirements:**
- Inherit from `BaseAgent`
- Implement `initialize()`, `shutdown()`, `health()`
- Provide `get_metadata()` and `get_capabilities()`

**Agent States:**
- UNINITIALIZED → INITIALIZING → READY → EXECUTING → [ERROR] → SHUTTING_DOWN → SHUT_DOWN

### Runtime Bootstrap

Single entry point coordinating entire application lifecycle.

**Startup Sequence:**
1. Emit ApplicationStarting event
2. Initialize all plugins (in registration order)
3. Initialize all agents (in registration order)
4. Emit ApplicationStarted event

**Shutdown Sequence:**
1. Emit ApplicationStopping event
2. Shutdown all agents (in reverse registration order)
3. Shutdown all plugins (in reverse registration order)
4. Emit ApplicationStopped event

## Lifecycle

### Application Startup

```python
from aura_backend.core.bootstrap import Runtime

runtime = Runtime(version="0.2.0")
await runtime.startup()

# Access components
services = runtime.services
plugins = runtime.plugins
agents = runtime.agents
event_bus = runtime.event_bus
```

### Component Initialization

Each plugin and agent goes through a controlled initialization:

1. **UNINITIALIZED** → **INITIALIZING** (status changes)
2. Execute `initialize()` method asynchronously
3. **INITIALIZING** → **INITIALIZED** (on success)
4. Emit lifecycle event (PluginLoaded/AgentRegistered)

### Application Shutdown

```python
await runtime.shutdown()
# All plugins and agents shut down in proper order
```

## Extension Guide

### Creating a Plugin

```python
from typing import Any, Dict
from aura_backend.core.plugins import (
    BasePlugin, PluginMetadata, PluginCapability
)

class MyPlugin(BasePlugin):
    async def initialize(self) -> None:
        logger.info("MyPlugin initializing")
        # Setup code here

    async def shutdown(self) -> None:
        logger.info("MyPlugin shutting down")
        # Cleanup code here

    async def health(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "component": "my-plugin",
        }

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id="my-plugin",
            name="My Plugin",
            version="1.0.0",
            description="Description of plugin",
            author="Author Name",
            tags=["tag1", "tag2"],
        )

    def get_capabilities(self) -> list[PluginCapability]:
        return [
            PluginCapability(
                name="capability-1",
                description="Does something useful",
            ),
        ]
```

### Registering a Plugin

```python
from aura_backend.core.bootstrap import Runtime
from myapp.plugins import MyPlugin

runtime = Runtime(version="0.2.0")
plugin = MyPlugin()
runtime.plugins.register(plugin)
await runtime.startup()
```

### Creating an Agent

```python
from typing import Any, Dict
from aura_backend.core.agents import (
    BaseAgent, AgentMetadata, AgentCapability
)

class MyAgent(BaseAgent):
    async def initialize(self) -> None:
        logger.info(f"MyAgent {self.id} initializing")

    async def shutdown(self) -> None:
        logger.info(f"MyAgent {self.id} shutting down")

    async def health(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "processing_capacity": 10,
        }

    def get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            id=self.id,
            name="My Agent",
            agent_type="my-type",
            version="1.0.0",
            description="Description of agent",
            author="Author Name",
            tags=["tag1", "tag2"],
        )

    def get_capabilities(self) -> list[AgentCapability]:
        return [
            AgentCapability(
                name="capability-1",
                description="Does something useful",
            ),
        ]
```

### Registering an Agent

```python
from aura_backend.core.bootstrap import Runtime
from myapp.agents import MyAgent

runtime = Runtime(version="0.2.0")
agent = MyAgent()
runtime.agents.register_instance(agent)
await runtime.startup()
```

### Subscribing to Events

```python
from aura_backend.core.events import ApplicationStarted

async def on_app_started(event: ApplicationStarted) -> None:
    logger.info("Application started!")

runtime.event_bus.subscribe(ApplicationStarted, on_app_started)
await runtime.startup()  # Handler will be called
```

### Accessing Services

```python
from myapp.services import UserService

# Register service
runtime.services.register_type(UserService, UserService)

# Resolve service
user_service = runtime.services.resolve(UserService)
await user_service.get_user(123)
```

## Plugin Examples

### Logging Plugin

```python
class LoggingPlugin(BasePlugin):
    """Provides structured logging capabilities"""
    
    async def initialize(self) -> None:
        logger.info("logging_plugin_initializing")
    
    async def shutdown(self) -> None:
        logger.info("logging_plugin_shutting_down")
    
    async def health(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "log_level": "INFO",
        }
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id="logging-plugin",
            name="Logging Plugin",
            version="0.1.0",
            description="Structured logging for AURA",
            author="AURA Team",
            tags=["logging", "observability"],
        )
    
    def get_capabilities(self) -> list[PluginCapability]:
        return [
            PluginCapability(
                name="structured-logging",
                description="JSON logging for components",
            ),
        ]
```

### Storage Plugin

```python
class StoragePlugin(BasePlugin):
    """Provides file storage and data persistence"""
    
    async def initialize(self) -> None:
        logger.info("storage_plugin_initializing")
    
    async def shutdown(self) -> None:
        logger.info("storage_plugin_shutting_down")
    
    async def health(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "storage_backend": "s3",
            "available_space_mb": 5000,
        }
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id="storage-plugin",
            name="Storage Plugin",
            version="0.1.0",
            description="File storage for AURA",
            author="AURA Team",
            tags=["storage", "persistence"],
        )
    
    def get_capabilities(self) -> list[PluginCapability]:
        return [
            PluginCapability(
                name="file-storage",
                description="Stores files persistently",
            ),
        ]
```

## Agent Examples

### Editor Agent

```python
class EditorAgent(BaseAgent):
    """AI-powered video editing agent"""
    
    async def initialize(self) -> None:
        logger.info(f"editor_agent_initializing {self.id}")
    
    async def shutdown(self) -> None:
        logger.info(f"editor_agent_shutting_down {self.id}")
    
    async def health(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "processing_capacity": 10,
            "current_load": 0,
        }
    
    def get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            id=self.id,
            name="Editor Agent",
            agent_type="editor",
            version="0.1.0",
            description="AI video editing",
            author="AURA Team",
            tags=["video", "editing", "ai"],
        )
    
    def get_capabilities(self) -> list[AgentCapability]:
        return [
            AgentCapability(
                name="video-editing",
                description="Edits video intelligently",
            ),
        ]
```

### SEO Agent

```python
class SEOAgent(BaseAgent):
    """AI-powered SEO optimization agent"""
    
    async def initialize(self) -> None:
        logger.info(f"seo_agent_initializing {self.id}")
    
    async def shutdown(self) -> None:
        logger.info(f"seo_agent_shutting_down {self.id}")
    
    async def health(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "processing_capacity": 20,
            "current_load": 0,
        }
    
    def get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            id=self.id,
            name="SEO Agent",
            agent_type="seo",
            version="0.1.0",
            description="SEO optimization",
            author="AURA Team",
            tags=["seo", "metadata", "ai"],
        )
    
    def get_capabilities(self) -> list[AgentCapability]:
        return [
            AgentCapability(
                name="seo-optimization",
                description="Optimizes for search engines",
            ),
        ]
```

## Health Monitoring

Each component reports health status:

```python
# Check runtime health
health = await runtime.health()
# {
#   "status": "running",
#   "version": "0.2.0",
#   "uptime_ms": 1234,
#   "services": {...},
#   "plugins": {...},
#   "agents": {...},
#   "events": {...}
# }

# Check component health
plugin_health = await plugin.health()
agent_health = await agent.health()
service_health = container.health()
event_bus_health = event_bus.get_stats()
```

## Observability

### Logging

All components log initialization/shutdown:

```
logger.info("runtime_starting")
logger.info("plugin_initializing", extra={"plugin_id": "my-plugin"})
logger.info("agent_ready", extra={"agent_id": "abc-123"})
logger.info("runtime_started")
```

### Correlation IDs

Events carry correlation IDs for tracing:

```python
event = BaseEvent()
print(event.correlation_id)  # Unique ID for request
print(event.trace_id)         # Trace ID for distributed tracing
```

### Statistics

Event bus and services track metrics:

```python
event_bus_stats = event_bus.get_stats()
# {
#   "total_events_published": 42,
#   "active_subscribers": 5,
#   "uptime_ms": 1234
# }

container_stats = container.get_stats()
# {
#   "total_services": 10,
#   "resolve_counts": {"Service1": 5, "Service2": 3}
# }
```

## Error Handling

Custom exceptions for debugging:

```python
from aura_backend.core.bootstrap import RuntimeBootstrapError
from aura_backend.core.plugins import (
    PluginRegistrationError,
    PluginInitializationError,
)
from aura_backend.core.agents import AgentRegistrationError
from aura_backend.core.service_container import ServiceNotFoundError
from aura_backend.core.events import EventHandlerError

try:
    await runtime.startup()
except RuntimeBootstrapError as e:
    logger.error(f"Runtime startup failed: {e}")
```

## Testing

The runtime supports comprehensive testing:

```python
@pytest.mark.asyncio
async def test_my_plugin():
    runtime = Runtime(version="0.2.0")
    plugin = MyPlugin()
    runtime.plugins.register(plugin)
    
    await runtime.startup()
    health = await plugin.health()
    assert health["status"] == "healthy"
    
    await runtime.shutdown()
    assert plugin.status == "shut_down"
```

## Thread Safety Guarantees

**All core runtime components are thread-safe:**

- **EventBus**: Subscription management is protected by RLock
- **ServiceContainer**: Registration and singleton resolution are protected by locks
- **PluginRegistry**: Plugin registration/unregistration are protected by locks
- **AgentRegistry**: Agent registration/unregistration are protected by locks

**Guidelines:**

- Concurrent registration is safe: multiple threads can register plugins/agents simultaneously
- Concurrent event publishing is safe: multiple threads can publish events simultaneously
- Concurrent service resolution is safe: singleton pattern guaranteed even under load
- Event subscription/unsubscription is O(1) via index-based lookup

**Not Thread-Safe:**

- BasePlugin and BaseAgent implementations should be thread-safe themselves
- Event handlers should be thread-safe if accessing shared state

## Constructor Dependency Injection

The ServiceContainer supports automatic constructor injection:

```python
class DatabaseService:
    pass

class UserService:
    def __init__(self, db: DatabaseService):
        self.db = db

# Register services
container.register_instance(DatabaseService, DatabaseService())

# Resolve with automatic injection
user_service = container.resolve(UserService)
# user_service.db is automatically injected
```

**How it works:**

1. Resolver inspects constructor parameters via `inspect.signature()`
2. For each parameter with a type annotation:
   - If service is registered, it's automatically resolved and injected
   - If service is not registered and parameter has default, default is used
   - Otherwise, parameter is skipped
3. Service is instantiated with resolved dependencies

**Circular Dependency Detection:**

Circular dependencies are detected and throw `CircularDependencyError`:

```python
# This will raise CircularDependencyError
class ServiceA:
    def __init__(self, b: ServiceB):
        self.b = b

class ServiceB:
    def __init__(self, a: ServiceA):
        self.a = a

container.register_type(ServiceA, ServiceA)
container.register_type(ServiceB, ServiceB)
container.resolve(ServiceA)  # Raises CircularDependencyError
```

## Graceful Degradation

The runtime supports graceful startup degradation:

**Behavior:**

- If a plugin fails to initialize, failure is logged but startup continues
- If an agent fails to initialize, failure is logged but startup continues
- Runtime status becomes "running" with health level "degraded"
- Successful components are fully operational
- Failed components are marked unhealthy in status reports

**Health Levels:**

- **Healthy**: All components initialized successfully
- **Degraded**: Running but some components failed to initialize
- **Failed**: Critical failures, runtime not running

**Example:**

```python
runtime = Runtime(version="0.2.0")
runtime.plugins.register(FailingPlugin())  # Will fail to initialize
runtime.agents.register_instance(GoodAgent())

await runtime.startup()
# Runtime is still running despite plugin failure

health = await runtime.health()
print(health["health"])  # "degraded"
print(health["startup_errors"])  # [{"component": "plugins", "error": "..."}]
```

## Async Event Handler Concurrency

Async event handlers execute concurrently using `asyncio.gather()`:

```python
event_bus = EventBus()

async def handler1(event):
    await asyncio.sleep(1)

async def handler2(event):
    await asyncio.sleep(1)

event_bus.subscribe_async("test", handler1)
event_bus.subscribe_async("test", handler2)

# Both handlers run concurrently, total time ~1s not 2s
await event_bus.publish(event)
```

**Handler Timeout:**

Each handler has a default 30-second timeout. Long-running handlers are cancelled if they exceed the timeout:

```python
# Timeout for this event's handlers
await event_bus.publish(event, timeout_seconds=60.0)
```

**Failure Isolation:**

One failing handler does not affect others:

```python
async def failing_handler(event):
    raise RuntimeError("Handler failed")

async def good_handler(event):
    print("Still executed despite failing_handler")

event_bus.subscribe_async("test", failing_handler)
event_bus.subscribe_async("test", good_handler)

await event_bus.publish(event)  # Good handler still runs
```

## Lifecycle Guarantees

**Startup Sequence (with timeouts):**

1. ApplicationStarting event published
2. Plugin initialization (graceful degradation)
3. Agent initialization (graceful degradation)
4. ApplicationStarted event published
5. Runtime status: "running" with health: "healthy"/"degraded"

**Shutdown Sequence (with timeouts):**

1. ApplicationStopping event published
2. Agent shutdown (reverse order, 30s timeout default)
3. Plugin shutdown (reverse order, 30s timeout default)
4. ApplicationStopped event published
5. Runtime status: "stopped"

**Graceful Shutdown Example:**

```python
# Custom shutdown timeout
await runtime.shutdown(timeout_seconds=60.0)

# If agents take too long, shutdown continues anyway after timeout
# Shutdown failures are logged but don't block
```

## Performance Optimization

**O(1) Operations:**

- Subscribe/unsubscribe events: O(1) via index-based lookup
- Find agents by type: O(1) via type index
- Find agents by tag: O(1) via tag index
- Singleton resolution: O(1) via singleton cache

**Statistics Tracking:**

All components track statistics for monitoring:

- EventBus: `event_count`, `subscription_count`, `uptime_ms`
- ServiceContainer: `service_count`, `resolve_count` per service
- PluginRegistry: `plugin_count`, initialization time
- AgentRegistry: `agent_count`, `execution_count` per agent

## Production Considerations

- Runtime startup/shutdown are async — use proper async/await patterns
- All component lifecycle methods are async — implement graceful degradation
- All core components are thread-safe for concurrent access
- Service container supports automatic constructor dependency injection
- Event handlers should complete quickly; long operations should run async
- Health checks should complete within 1 second
- Monitor event bus queue depth if adding many async handlers
- Use correlation IDs in logs for distributed tracing
- Configure shutdown timeout based on your workload (default 30s)

## Migration Path

The event bus design allows future transport upgrades without code changes:

1. Current: In-memory event bus (EventBus class) with thread-safe locking
2. Future: RabbitMQ transport (RabbitMQEventBus extends EventBus)
3. Future: Kafka transport (KafkaEventBus extends EventBus)

Applications use interface (event_bus: EventPublisher) — transport is swappable.
