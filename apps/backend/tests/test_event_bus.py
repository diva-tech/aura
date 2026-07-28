"""
Tests for event bus system.
"""

import asyncio
from datetime import datetime

import pytest

from aura_backend.core.events import (
    EventBus,
    BaseEvent,
    ApplicationStarting,
    ApplicationStarted,
)


@pytest.fixture
def event_bus():
    """Create an event bus instance"""
    return EventBus()


class TestEvent(BaseEvent):
    """Test event for testing"""

    def __init__(self, data: str):
        super().__init__()
        self.data = data


@pytest.mark.asyncio
async def test_event_bus_creation(event_bus):
    """Event bus creates successfully"""
    assert event_bus is not None
    assert event_bus.get_stats()["total_events_published"] == 0


@pytest.mark.asyncio
async def test_event_bus_publish_sync(event_bus):
    """Event bus publishes sync events"""
    received = []

    def handler(event: BaseEvent) -> None:
        received.append(event)

    event_bus.subscribe(TestEvent, handler)
    event = TestEvent("test")
    await event_bus.publish(event)

    assert len(received) == 1
    assert received[0].data == "test"


@pytest.mark.asyncio
async def test_event_bus_publish_async(event_bus):
    """Event bus publishes async events"""
    received = []

    async def handler(event: BaseEvent) -> None:
        received.append(event)

    event_bus.subscribe(TestEvent, handler)
    event = TestEvent("test")
    await event_bus.publish(event)

    assert len(received) == 1
    assert received[0].data == "test"


@pytest.mark.asyncio
async def test_event_bus_multiple_handlers(event_bus):
    """Event bus handles multiple subscribers"""
    received1 = []
    received2 = []

    def handler1(event: BaseEvent) -> None:
        received1.append(event)

    def handler2(event: BaseEvent) -> None:
        received2.append(event)

    event_bus.subscribe(TestEvent, handler1)
    event_bus.subscribe(TestEvent, handler2)
    event = TestEvent("test")
    await event_bus.publish(event)

    assert len(received1) == 1
    assert len(received2) == 1


@pytest.mark.asyncio
async def test_event_bus_unsubscribe(event_bus):
    """Event bus unsubscribes handlers"""
    received = []

    def handler(event: BaseEvent) -> None:
        received.append(event)

    subscription = event_bus.subscribe(TestEvent, handler)
    event_bus.unsubscribe(subscription)
    event = TestEvent("test")
    await event_bus.publish(event)

    assert len(received) == 0


@pytest.mark.asyncio
async def test_event_bus_lifecycle_events(event_bus):
    """Event bus publishes lifecycle events"""
    received = []

    def handler(event: BaseEvent) -> None:
        received.append(event)

    event_bus.subscribe(ApplicationStarting, handler)
    event = ApplicationStarting()
    await event_bus.publish(event)

    assert len(received) == 1
    assert isinstance(received[0], ApplicationStarting)


@pytest.mark.asyncio
async def test_event_bus_stats(event_bus):
    """Event bus tracks statistics"""
    received = []

    def handler(event: BaseEvent) -> None:
        received.append(event)

    event_bus.subscribe(TestEvent, handler)

    for i in range(5):
        await event_bus.publish(TestEvent(f"test{i}"))

    stats = event_bus.get_stats()
    assert stats["total_events_published"] == 5
    assert stats["active_subscribers"] == 1
