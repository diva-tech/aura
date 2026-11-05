"""
Tests for runtime bootstrap and lifecycle management.
"""

import pytest

from aura_backend.core.bootstrap import Runtime, RuntimeBootstrapError


@pytest.fixture
def runtime():
    """Create a runtime instance"""
    return Runtime(version="0.2.0")


@pytest.mark.asyncio
async def test_runtime_initialization(runtime):
    """Runtime initializes with correct state"""
    assert runtime.version == "0.2.0"
    assert runtime.status == "uninitialized"
    assert runtime.uptime_ms() == 0.0


@pytest.mark.asyncio
async def test_runtime_startup(runtime):
    """Runtime starts up successfully"""
    await runtime.startup()
    assert runtime.status == "running"
    assert runtime.uptime_ms() > 0


@pytest.mark.asyncio
async def test_runtime_shutdown(runtime):
    """Runtime shuts down successfully"""
    await runtime.startup()
    await runtime.shutdown()
    assert runtime.status == "stopped"


@pytest.mark.asyncio
async def test_runtime_provides_services(runtime):
    """Runtime provides core services"""
    assert runtime.services is not None
    assert runtime.plugins is not None
    assert runtime.agents is not None
    assert runtime.event_bus is not None
    assert runtime.event_publisher is not None


@pytest.mark.asyncio
async def test_runtime_health(runtime):
    """Runtime health status is correct"""
    await runtime.startup()
    health = await runtime.health()

    assert health["status"] == "running"
    assert health["version"] == "0.2.0"
    assert health["uptime_ms"] > 0
    assert "services" in health
    assert "plugins" in health
    assert "agents" in health
    assert "events" in health


@pytest.mark.asyncio
async def test_runtime_info(runtime):
    """Runtime info contains expected data"""
    await runtime.startup()
    info = runtime.get_info()

    assert info["version"] == "0.2.0"
    assert info["status"] == "running"
    assert "services" in info
    assert "plugins" in info
    assert "agents" in info
    assert "events" in info
