"""
Logging plugin - Example plugin that provides structured logging capabilities.

This plugin demonstrates the plugin framework and lifecycle management.
No actual business logic is implemented - it's a placeholder for Milestone 2+.
"""

from typing import Any, Dict

from aura_backend.config.logging import get_logger
from aura_backend.core.plugins import BasePlugin, PluginMetadata, PluginCapability

logger = get_logger(__name__)


class LoggingPlugin(BasePlugin):
    """
    Logging plugin for AURA runtime.

    Provides structured logging capabilities and log configuration management.
    """

    async def initialize(self) -> None:
        """Initialize the logging plugin"""
        logger.info("logging_plugin_initializing")

    async def shutdown(self) -> None:
        """Shut down the logging plugin"""
        logger.info("logging_plugin_shutting_down")

    async def health(self) -> Dict[str, Any]:
        """Return plugin health status"""
        return {
            "status": "healthy",
            "log_level": "INFO",
        }

    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata"""
        return PluginMetadata(
            id="logging-plugin",
            name="Logging Plugin",
            version="0.1.0",
            description="Structured logging and log management for AURA",
            author="AURA Team",
            tags=["logging", "observability"],
        )

    def get_capabilities(self) -> list[PluginCapability]:
        """Return plugin capabilities"""
        return [
            PluginCapability(
                name="structured-logging",
                description="Provides structured JSON logging for all components",
            ),
            PluginCapability(
                name="log-configuration",
                description="Manages logging configuration and levels",
            ),
        ]
