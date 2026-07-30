"""
Event-driven architecture foundation for AURA.

Provides:
- Type-safe event publishing and subscription
- Async event handling
- Correlation and trace IDs
- Structured logging
- Transport-agnostic event bus

Future transports (RabbitMQ, Kafka, Redis Streams, NATS) can implement
the same EventBus interface without changing application code.
"""

from __future__ import annotations

import asyncio
import threading
import uuid
from collections.abc import Awaitable, Callable
from datetime import datetime
from enum import StrEnum
from typing import Any, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T", bound="BaseEvent")


class EventPriority(StrEnum):
    """Event processing priority"""

    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class BaseEvent(BaseModel):
    """Base class for all events in the system"""

    event_type: str = Field(...)
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = Field(default="aura")
    priority: EventPriority = Field(default=EventPriority.NORMAL)
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = True

    @classmethod
    def create(
        cls,
        **kwargs,
    ) -> BaseEvent:
        """Create an event with auto-generated IDs if not provided"""
        if "event_type" not in kwargs:
            kwargs["event_type"] = cls.__name__
        return cls(**kwargs)


# Lifecycle Events
class ApplicationStarting(BaseEvent):
    """Fired when application is starting"""

    event_type: str = "application.starting"
    version: str = ""


class ApplicationStarted(BaseEvent):
    """Fired when application has started"""

    event_type: str = "application.started"
    version: str = ""
    startup_time_ms: float = 0.0


class ApplicationStopping(BaseEvent):
    """Fired when application is stopping"""

    event_type: str = "application.stopping"


class ApplicationStopped(BaseEvent):
    """Fired when application has stopped"""

    event_type: str = "application.stopped"
    uptime_ms: float = 0.0


class PluginLoaded(BaseEvent):
    """Fired when a plugin is loaded"""

    event_type: str = "plugin.loaded"
    plugin_id: str = ""
    plugin_name: str = ""
    plugin_version: str = ""


class PluginUnloaded(BaseEvent):
    """Fired when a plugin is unloaded"""

    event_type: str = "plugin.unloaded"
    plugin_id: str = ""
    plugin_name: str = ""


class AgentRegistered(BaseEvent):
    """Fired when an agent is registered"""

    event_type: str = "agent.registered"
    agent_id: str = ""
    agent_name: str = ""
    agent_type: str = ""


class HealthChanged(BaseEvent):
    """Fired when system health status changes"""

    event_type: str = "health.changed"
    status: str = ""
    message: str = ""


# Type aliases
EventHandler = Callable[[BaseEvent], Any]
AsyncEventHandler = Callable[[BaseEvent], Awaitable[None]]


class EventSubscription:
    """Represents a subscription to events"""

    def __init__(
        self,
        subscription_id: str,
        event_type: str,
        handler: EventHandler | AsyncEventHandler,
        is_async: bool = False,
    ):
        self.subscription_id = subscription_id
        self.event_type = event_type
        self.handler = handler
        self.is_async = is_async
        self.created_at = datetime.utcnow()
        self.event_count = 0

    async def handle(self, event: BaseEvent) -> None:
        """Handle an event"""
        try:
            if self.is_async:
                await self.handler(event)
            else:
                self.handler(event)
            self.event_count += 1
        except Exception as e:
            raise EventHandlerError(f"Error handling {event.event_type}: {str(e)}") from e


class EventBus:
    """
    In-memory event bus for publish-subscribe pattern.

    Features:
    - Type-safe event publishing
    - Async and sync handlers
    - Multiple listeners per event type
    - Event correlation and tracing
    - Structured logging
    - Transport-agnostic (can be replaced with RabbitMQ, Kafka, etc.)
    - Thread-safe subscription management
    """

    def __init__(self):
        self._subscriptions: dict[str, list[EventSubscription]] = {}
        self._subscriptions_by_id: dict[str, tuple[str, EventSubscription]] = {}
        self._all_subscriptions: list[EventSubscription] = []
        self._subscriptions_lock = threading.RLock()
        self._event_count = 0
        self._event_count_lock = threading.Lock()
        self._start_time = datetime.utcnow()

    def subscribe(
        self,
        event_type: str,
        handler: EventHandler,
        subscription_id: str | None = None,
    ) -> str:
        """
        Subscribe to an event type with a sync handler

        Args:
            event_type: The event type to subscribe to (e.g., 'application.started')
            handler: Sync function to call when event is published
            subscription_id: Optional subscription ID (auto-generated if not provided)

        Returns:
            The subscription ID
        """
        sub_id = subscription_id or str(uuid.uuid4())
        subscription = EventSubscription(sub_id, event_type, handler, is_async=False)

        with self._subscriptions_lock:
            if event_type not in self._subscriptions:
                self._subscriptions[event_type] = []

            self._subscriptions[event_type].append(subscription)
            self._all_subscriptions.append(subscription)
            self._subscriptions_by_id[sub_id] = (event_type, subscription)

        return sub_id

    def subscribe_async(
        self,
        event_type: str,
        handler: AsyncEventHandler,
        subscription_id: str | None = None,
    ) -> str:
        """
        Subscribe to an event type with an async handler

        Args:
            event_type: The event type to subscribe to
            handler: Async function to call when event is published
            subscription_id: Optional subscription ID (auto-generated if not provided)

        Returns:
            The subscription ID
        """
        sub_id = subscription_id or str(uuid.uuid4())
        subscription = EventSubscription(sub_id, event_type, handler, is_async=True)

        with self._subscriptions_lock:
            if event_type not in self._subscriptions:
                self._subscriptions[event_type] = []

            self._subscriptions[event_type].append(subscription)
            self._all_subscriptions.append(subscription)
            self._subscriptions_by_id[sub_id] = (event_type, subscription)

        return sub_id

    def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from an event

        Args:
            subscription_id: The subscription ID to remove

        Returns:
            True if unsubscribed, False if subscription not found
        """
        with self._subscriptions_lock:
            if subscription_id not in self._subscriptions_by_id:
                return False

            event_type, subscription = self._subscriptions_by_id.pop(subscription_id)

            if event_type in self._subscriptions:
                self._subscriptions[event_type] = [
                    s
                    for s in self._subscriptions[event_type]
                    if s.subscription_id != subscription_id
                ]

            self._all_subscriptions = [
                s for s in self._all_subscriptions if s.subscription_id != subscription_id
            ]

            return True

    async def publish(self, event: BaseEvent, timeout_seconds: float = 30.0) -> None:
        """
        Publish an event to all subscribers

        Args:
            event: The event to publish
            timeout_seconds: Timeout for all handlers to complete (default 30s)
        """
        with self._event_count_lock:
            self._event_count += 1

        with self._subscriptions_lock:
            subscriptions = list(self._subscriptions.get(event.event_type, []))

        if not subscriptions:
            return

        sync_tasks = []
        async_tasks = []

        for subscription in subscriptions:
            if subscription.is_async:
                async_tasks.append(self._handle_with_timeout(subscription, event, timeout_seconds))
            else:
                sync_tasks.append((subscription, event))

        for subscription, evt in sync_tasks:
            try:
                await subscription.handle(evt)
            except EventHandlerError:
                pass

        if async_tasks:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*async_tasks, return_exceptions=True), timeout=timeout_seconds
                )
            except TimeoutError:
                pass

    async def _handle_with_timeout(
        self, subscription: EventSubscription, event: BaseEvent, timeout_seconds: float
    ) -> None:
        """Handle an event with timeout protection"""
        try:
            await asyncio.wait_for(subscription.handle(event), timeout=timeout_seconds)
        except TimeoutError:
            pass
        except EventHandlerError:
            pass

    def list_subscriptions(self) -> list[dict[str, Any]]:
        """List all active subscriptions"""
        with self._subscriptions_lock:
            return [
                {
                    "subscription_id": sub.subscription_id,
                    "event_type": sub.event_type,
                    "is_async": sub.is_async,
                    "event_count": sub.event_count,
                    "created_at": sub.created_at.isoformat(),
                }
                for sub in self._all_subscriptions
            ]

    def subscription_count(self, event_type: str | None = None) -> int:
        """Get count of subscriptions for an event type or total"""
        with self._subscriptions_lock:
            if event_type:
                return len(self._subscriptions.get(event_type, []))
            return len(self._all_subscriptions)

    def event_count(self) -> int:
        """Get total events published"""
        with self._event_count_lock:
            return self._event_count

    def uptime_ms(self) -> float:
        """Get bus uptime in milliseconds"""
        return (datetime.utcnow() - self._start_time).total_seconds() * 1000

    def health(self) -> dict[str, Any]:
        """Get bus health status"""
        with self._event_count_lock:
            event_count = self._event_count
        return {
            "status": "healthy",
            "event_count": event_count,
            "subscription_count": self.subscription_count(),
            "uptime_ms": self.uptime_ms(),
        }


class EventPublisher:
    """Publishes events to the event bus"""

    def __init__(self, event_bus: EventBus, source: str = "aura"):
        self._bus = event_bus
        self._source = source

    async def publish(self, event: BaseEvent) -> None:
        """Publish an event"""
        if not event.source:
            event.source = self._source
        await self._bus.publish(event)


class EventSubscriber:
    """Subscribes to events from the event bus"""

    def __init__(self, event_bus: EventBus):
        self._bus = event_bus
        self._subscriptions: set[str] = set()

    def subscribe(
        self,
        event_type: str,
        handler: EventHandler,
        subscription_id: str | None = None,
    ) -> str:
        """Subscribe to an event type"""
        sub_id = self._bus.subscribe(event_type, handler, subscription_id)
        self._subscriptions.add(sub_id)
        return sub_id

    def subscribe_async(
        self,
        event_type: str,
        handler: AsyncEventHandler,
        subscription_id: str | None = None,
    ) -> str:
        """Subscribe to an event type with async handler"""
        sub_id = self._bus.subscribe_async(event_type, handler, subscription_id)
        self._subscriptions.add(sub_id)
        return sub_id

    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from an event"""
        success = self._bus.unsubscribe(subscription_id)
        if success:
            self._subscriptions.discard(subscription_id)
        return success

    def unsubscribe_all(self) -> int:
        """Unsubscribe from all events"""
        count = 0
        for sub_id in list(self._subscriptions):
            if self.unsubscribe(sub_id):
                count += 1
        return count


class EventHandlerError(Exception):
    """Raised when an event handler fails"""

    pass


# Alias for compatibility with existing imports
BaseEventBus = EventBus
