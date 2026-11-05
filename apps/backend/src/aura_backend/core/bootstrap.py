"""
Runtime bootstrap and lifecycle management.

Provides:
- Application startup and shutdown
- Component initialization coordination
- Lifecycle event publishing
- Graceful degradation

The Runtime class is the single entry point for the entire AURA application.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

from aura_backend.config.logging import get_logger

from .agents import AgentRegistry
from .events import (
    ApplicationStarted,
    ApplicationStarting,
    ApplicationStopped,
    ApplicationStopping,
    EventBus,
    EventPublisher,
)
from .plugins import PluginRegistry
from .service_container import ServiceContainer

logger = get_logger(__name__)


class Runtime:
    """
    AURA Runtime - the single entry point for the application.

    The runtime coordinates:
    - Application startup and shutdown
    - Service container and dependency injection
    - Plugin lifecycle management
    - Agent lifecycle management
    - Event publishing and subscription
    - Health monitoring

    Usage:
        runtime = Runtime(version="0.2.0")
        runtime.register_services(...)
        runtime.register_plugins(...)
        runtime.register_agents(...)
        await runtime.startup()
        # ... do work ...
        await runtime.shutdown()
    """

    def __init__(self, version: str):
        self._version = version
        self._status = "uninitialized"
        self._health_status = "unknown"
        self._startup_errors: List[Dict[str, str]] = []
        self._start_time: Optional[datetime] = None
        self._end_time: Optional[datetime] = None

        # Core components
        self._event_bus = EventBus()
        self._event_publisher = EventPublisher(self._event_bus, source="runtime")
        self._service_container = ServiceContainer()
        self._plugin_registry = PluginRegistry()
        self._agent_registry = AgentRegistry()

        # Pre-register core services
        self._service_container.register_instance(EventBus, self._event_bus)
        self._service_container.register_instance(EventPublisher, self._event_publisher)
        self._service_container.register_instance(ServiceContainer, self._service_container)
        self._service_container.register_instance(PluginRegistry, self._plugin_registry)
        self._service_container.register_instance(AgentRegistry, self._agent_registry)

    @property
    def version(self) -> str:
        """Get runtime version"""
        return self._version

    @property
    def status(self) -> str:
        """Get runtime status"""
        return self._status

    @property
    def event_bus(self) -> EventBus:
        """Get event bus"""
        return self._event_bus

    @property
    def event_publisher(self) -> EventPublisher:
        """Get event publisher"""
        return self._event_publisher

    @property
    def services(self) -> ServiceContainer:
        """Get service container"""
        return self._service_container

    @property
    def plugins(self) -> PluginRegistry:
        """Get plugin registry"""
        return self._plugin_registry

    @property
    def agents(self) -> AgentRegistry:
        """Get agent registry"""
        return self._agent_registry

    def uptime_ms(self) -> float:
        """Get runtime uptime in milliseconds"""
        if self._start_time is None:
            return 0.0
        end = self._end_time or datetime.utcnow()
        return (end - self._start_time).total_seconds() * 1000

    async def startup(self) -> None:
        """
        Start the runtime with graceful degradation.

        Lifecycle:
        1. Publish ApplicationStarting event
        2. Initialize service container
        3. Initialize plugins (failures don't block)
        4. Initialize agents (failures don't block)
        5. Determine health status (Healthy/Degraded/Failed)
        6. Publish ApplicationStarted event
        """
        try:
            logger.info("runtime_startup_starting", extra={"version": self._version})
            self._status = "starting"
            self._start_time = datetime.utcnow()
            self._startup_errors = []

            # Publish starting event
            await self._event_publisher.publish(
                ApplicationStarting(version=self._version)
            )

            # Initialize plugins (graceful degradation)
            logger.info("runtime_initializing_plugins", extra={"count": self._plugin_registry.count()})
            try:
                await self._plugin_registry.initialize_all()
            except Exception as e:
                logger.warning("runtime_plugin_initialization_failed", extra={"error": str(e)})
                self._startup_errors.append({
                    "component": "plugins",
                    "error": str(e)
                })

            # Initialize agents (graceful degradation)
            logger.info("runtime_initializing_agents", extra={"count": self._agent_registry.count()})
            try:
                await self._agent_registry.initialize_all()
            except Exception as e:
                logger.warning("runtime_agent_initialization_failed", extra={"error": str(e)})
                self._startup_errors.append({
                    "component": "agents",
                    "error": str(e)
                })

            self._status = "running"

            # Determine health status
            if not self._startup_errors:
                self._health_status = "healthy"
            else:
                self._health_status = "degraded"

            startup_time = self.uptime_ms()

            # Publish started event
            await self._event_publisher.publish(
                ApplicationStarted(version=self._version, startup_time_ms=startup_time)
            )

            logger.info(
                "runtime_startup_complete",
                extra={
                    "version": self._version,
                    "startup_time_ms": startup_time,
                    "health": self._health_status,
                    "services": self._service_container.service_count(),
                    "plugins": self._plugin_registry.count(),
                    "agents": self._agent_registry.count(),
                    "startup_errors": len(self._startup_errors),
                },
            )
        except Exception as e:
            self._status = "error"
            self._health_status = "failed"
            logger.error("runtime_startup_failed", extra={"error": str(e)})
            raise RuntimeBootstrapError(f"Runtime startup failed: {str(e)}") from e

    async def shutdown(self, timeout_seconds: float = 30.0) -> None:
        """
        Shut down the runtime gracefully.

        Lifecycle:
        1. Verify running status
        2. Publish ApplicationStopping event
        3. Shut down agents with timeout
        4. Shut down plugins with timeout
        5. Publish ApplicationStopped event

        Args:
            timeout_seconds: Timeout for shutdown operations (default 30s)
        """
        if self._status not in ("running", "degraded"):
            logger.warning("runtime_shutdown_not_running", extra={"status": self._status})
            return

        try:
            logger.info("runtime_shutdown_starting", extra={"status": self._status})
            self._status = "stopping"

            # Publish stopping event
            await self._event_publisher.publish(ApplicationStopping())

            # Shut down agents with timeout
            logger.info("runtime_shutting_down_agents")
            try:
                await asyncio.wait_for(
                    self._agent_registry.shutdown_all(),
                    timeout=timeout_seconds
                )
            except asyncio.TimeoutError:
                logger.error("runtime_agent_shutdown_timeout", extra={"timeout_s": timeout_seconds})

            # Shut down plugins with timeout
            logger.info("runtime_shutting_down_plugins")
            try:
                await asyncio.wait_for(
                    self._plugin_registry.shutdown_all(),
                    timeout=timeout_seconds
                )
            except asyncio.TimeoutError:
                logger.error("runtime_plugin_shutdown_timeout", extra={"timeout_s": timeout_seconds})

            self._status = "stopped"
            self._end_time = datetime.utcnow()

            # Publish stopped event
            await self._event_publisher.publish(
                ApplicationStopped(uptime_ms=self.uptime_ms())
            )

            logger.info(
                "runtime_shutdown_complete",
                extra={"uptime_ms": self.uptime_ms()},
            )
        except Exception as e:
            self._status = "error"
            logger.error("runtime_shutdown_failed", extra={"error": str(e)})
            raise RuntimeBootstrapError(f"Runtime shutdown failed: {str(e)}") from e

    async def health(self) -> Dict[str, Any]:
        """
        Get runtime health status.

        Health levels:
        - Healthy: All components running
        - Degraded: Running but some components failed to initialize
        - Failed: Critical initialization failures, not running
        """
        health_level = self._health_status
        if self._status != "running":
            health_level = "failed" if self._status == "error" else self._status

        return {
            "status": self._status,
            "health": health_level,
            "version": self._version,
            "uptime_ms": self.uptime_ms(),
            "start_time": self._start_time.isoformat() if self._start_time else None,
            "startup_errors": self._startup_errors,
            "services": self._service_container.health(),
            "plugins": await self._plugin_registry.health_all(),
            "agents": await self._agent_registry.health_all(),
            "events": self._event_bus.health(),
        }

    def get_info(self) -> Dict[str, Any]:
        """Get runtime information"""
        return {
            "version": self._version,
            "status": self._status,
            "uptime_ms": self.uptime_ms(),
            "start_time": self._start_time.isoformat() if self._start_time else None,
            "services": self._service_container.get_info(),
            "plugins": self._plugin_registry.get_info(),
            "agents": self._agent_registry.get_info(),
            "events": {
                "event_count": self._event_bus.event_count(),
                "subscription_count": self._event_bus.subscription_count(),
            },
        }


class RuntimeBootstrapError(Exception):
    """Raised when runtime bootstrap fails"""

    pass
