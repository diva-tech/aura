"""
Tests for plugin registry and lifecycle.
"""

from typing import Any, Dict

import pytest

from aura_backend.core.plugins import (
    BasePlugin,
    PluginRegistry,
    PluginMetadata,
    PluginCapability,
    PluginRegistrationError,
)


class TestPlugin(BasePlugin):
    """Test plugin implementation"""

    async def initialize(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    async def health(self) -> Dict[str, Any]:
        return {"status": "healthy"}

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id="test-plugin",
            name="Test Plugin",
            version="0.1.0",
            description="A test plugin",
            author="Test Author",
        )

    def get_capabilities(self) -> list[PluginCapability]:
        return [
            PluginCapability(
                name="test-capability",
                description="A test capability",
            )
        ]


@pytest.fixture
def registry():
    """Create a plugin registry"""
    return PluginRegistry()


@pytest.mark.asyncio
async def test_registry_creation(registry):
    """Plugin registry creates successfully"""
    assert registry is not None


@pytest.mark.asyncio
async def test_registry_register_plugin(registry):
    """Registry registers plugins"""
    plugin = TestPlugin()
    registry.register(plugin)
    assert registry.get(plugin.id) is plugin


@pytest.mark.asyncio
async def test_registry_unregister_plugin(registry):
    """Registry unregisters plugins"""
    plugin = TestPlugin()
    registry.register(plugin)
    registry.unregister(plugin.id)

    with pytest.raises(KeyError):
        registry.get(plugin.id)


@pytest.mark.asyncio
async def test_registry_list_plugins(registry):
    """Registry lists plugins"""
    plugin = TestPlugin()
    registry.register(plugin)
    plugins = registry.list()
    assert len(plugins) == 1


@pytest.mark.asyncio
async def test_registry_find_by_name(registry):
    """Registry finds plugins by name"""
    plugin = TestPlugin()
    registry.register(plugin)
    found = registry.find_by_name("Test Plugin")
    assert found is plugin


@pytest.mark.asyncio
async def test_registry_initialize_plugins(registry):
    """Registry initializes all plugins"""
    plugin = TestPlugin()
    registry.register(plugin)
    await registry.initialize_all()
    assert plugin.status == "initialized"


@pytest.mark.asyncio
async def test_registry_shutdown_plugins(registry):
    """Registry shuts down all plugins"""
    plugin = TestPlugin()
    registry.register(plugin)
    await registry.initialize_all()
    await registry.shutdown_all()
    assert plugin.status == "shut_down"


@pytest.mark.asyncio
async def test_registry_health(registry):
    """Registry reports health"""
    plugin = TestPlugin()
    registry.register(plugin)
    await registry.initialize_all()
    health = registry.health()
    assert health["total_plugins"] == 1
