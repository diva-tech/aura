"""
Storage plugin - Example plugin for file and data storage management.

This plugin demonstrates the plugin framework and lifecycle management.
No actual business logic is implemented - it's a placeholder for Milestone 2+.
"""

from typing import Any, Dict

from aura_backend.config.logging import get_logger
from aura_backend.core.plugins import BasePlugin, PluginMetadata, PluginCapability

logger = get_logger(__name__)


class StoragePlugin(BasePlugin):
    """
    Storage plugin for AURA runtime.

    Provides file and data storage capabilities.
    """

    async def initialize(self) -> None:
        """Initialize the storage plugin"""
        logger.info("storage_plugin_initializing")

    async def shutdown(self) -> None:
        """Shut down the storage plugin"""
        logger.info("storage_plugin_shutting_down")

    async def health(self) -> Dict[str, Any]:
        """Return plugin health status"""
        return {
            "status": "healthy",
            "storage_backend": "local",
            "available_space_mb": 1000,
        }

    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata"""
        return PluginMetadata(
            id="storage-plugin",
            name="Storage Plugin",
            version="0.1.0",
            description="File and data storage management for AURA",
            author="AURA Team",
            tags=["storage", "persistence"],
        )

    def get_capabilities(self) -> list[PluginCapability]:
        """Return plugin capabilities"""
        return [
            PluginCapability(
                name="file-storage",
                description="Stores and retrieves files from persistent storage",
            ),
            PluginCapability(
                name="data-persistence",
                description="Persists application data",
            ),
        ]
