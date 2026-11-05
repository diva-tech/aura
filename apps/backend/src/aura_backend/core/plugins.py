"""
Plugin framework for AURA.

Provides:
- Plugin interface and lifecycle
- Plugin discovery and loading
- Plugin health monitoring
- Plugin isolation and management
- Thread-safe plugin management

Plugins extend AURA with new capabilities without modifying core code.
"""

from __future__ import annotations

import importlib
import inspect
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel, Field


class PluginStatus(str):
    """Status of a plugin"""

    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    INITIALIZED = "initialized"
    ERROR = "error"
    SHUTTING_DOWN = "shutting_down"
    SHUT_DOWN = "shut_down"


@dataclass
class PluginMetadata:
    """Metadata about a plugin"""

    id: str
    name: str
    version: str
    description: str
    author: Optional[str] = None
    license: Optional[str] = None
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class PluginCapability(BaseModel):
    """A capability provided by a plugin"""

    name: str = Field(...)
    description: str = Field(...)
    version: str = Field(default="1.0.0")


class BasePlugin(ABC):
    """
    Base class for all plugins.

    Plugins must implement:
    - get_metadata() - Return plugin metadata
    - initialize() - Initialize the plugin
    - shutdown() - Clean up resources
    - health() - Return health status
    """

    def __init__(self):
        self._status = PluginStatus.UNINITIALIZED
        self._initialized_at: Optional[datetime] = None
        self._error: Optional[str] = None

    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata"""
        pass

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the plugin"""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Shut down the plugin"""
        pass

    @abstractmethod
    async def health(self) -> Dict[str, Any]:
        """Return plugin health status"""
        pass

    def get_capabilities(self) -> List[PluginCapability]:
        """Return capabilities provided by this plugin"""
        return []

    @property
    def status(self) -> str:
        return self._status

    @property
    def error(self) -> Optional[str]:
        return self._error

    async def _set_status(self, status: str, error: Optional[str] = None) -> None:
        """Internal method to set plugin status"""
        self._status = status
        self._error = error
        if status == PluginStatus.INITIALIZED:
            self._initialized_at = datetime.utcnow()

    def get_status_info(self) -> Dict[str, Any]:
        """Get plugin status information"""
        return {
            "status": self._status,
            "initialized_at": self._initialized_at.isoformat() if self._initialized_at else None,
            "error": self._error,
        }


class PluginRegistry:
    """Registry for managing plugins with thread-safe operations"""

    def __init__(self):
        self._plugins: Dict[str, BasePlugin] = {}
        self._metadata: Dict[str, PluginMetadata] = {}
        self._registry_lock = threading.RLock()

    def register(self, plugin: BasePlugin) -> None:
        """Register a plugin"""
        metadata = plugin.get_metadata()

        with self._registry_lock:
            if metadata.id in self._plugins:
                raise PluginRegistrationError(f"Plugin {metadata.id} already registered")

            self._plugins[metadata.id] = plugin
            self._metadata[metadata.id] = metadata

    def unregister(self, plugin_id: str) -> bool:
        """Unregister a plugin"""
        with self._registry_lock:
            if plugin_id in self._plugins:
                del self._plugins[plugin_id]
                del self._metadata[plugin_id]
                return True
            return False

    def get(self, plugin_id: str) -> Optional[BasePlugin]:
        """Get a plugin by ID"""
        with self._registry_lock:
            return self._plugins.get(plugin_id)

    def list(self) -> List[PluginMetadata]:
        """List all registered plugins"""
        with self._registry_lock:
            return list(self._metadata.values())

    def find_by_name(self, name: str) -> Optional[BasePlugin]:
        """Find a plugin by name"""
        with self._registry_lock:
            for plugin in self._plugins.values():
                if plugin.get_metadata().name == name:
                    return plugin
            return None

    def find_by_tag(self, tag: str) -> List[BasePlugin]:
        """Find plugins by tag"""
        with self._registry_lock:
            return [
                plugin
                for plugin in self._plugins.values()
                if tag in plugin.get_metadata().tags
            ]

    def count(self) -> int:
        """Get count of registered plugins"""
        with self._registry_lock:
            return len(self._plugins)

    async def initialize_all(self) -> None:
        """Initialize all registered plugins with graceful degradation"""
        with self._registry_lock:
            plugins_to_init = list(self._plugins.values())

        failed_plugins = []
        for plugin in plugins_to_init:
            try:
                await plugin._set_status(PluginStatus.INITIALIZING)
                await plugin.initialize()
                await plugin._set_status(PluginStatus.INITIALIZED)
            except Exception as e:
                await plugin._set_status(PluginStatus.ERROR, str(e))
                failed_plugins.append((plugin.get_metadata().id, str(e)))

        if failed_plugins:
            error_msg = "; ".join(f"{pid}: {err}" for pid, err in failed_plugins)
            raise PluginInitializationError(f"Failed to initialize plugins: {error_msg}")

    async def shutdown_all(self) -> None:
        """Shut down all registered plugins in reverse order"""
        with self._registry_lock:
            plugins_to_shutdown = list(reversed(list(self._plugins.values())))

        for plugin in plugins_to_shutdown:
            try:
                await plugin._set_status(PluginStatus.SHUTTING_DOWN)
                await plugin.shutdown()
                await plugin._set_status(PluginStatus.SHUT_DOWN)
            except Exception as e:
                await plugin._set_status(PluginStatus.ERROR, str(e))

    async def health_all(self) -> Dict[str, Dict[str, Any]]:
        """Get health status for all plugins"""
        with self._registry_lock:
            plugins_items = list(self._plugins.items())

        health = {}
        for plugin_id, plugin in plugins_items:
            try:
                plugin_health = await plugin.health()
                health[plugin_id] = {
                    **plugin.get_status_info(),
                    **plugin_health,
                }
            except Exception as e:
                health[plugin_id] = {
                    **plugin.get_status_info(),
                    "error": str(e),
                }
        return health

    def get_info(self) -> Dict[str, Any]:
        """Get plugin registry information"""
        with self._registry_lock:
            plugin_list = [
                {
                    "id": meta.id,
                    "name": meta.name,
                    "version": meta.version,
                    "status": self._plugins[meta.id].status,
                }
                for meta in self._metadata.values()
            ]

        return {
            "plugin_count": len(plugin_list),
            "plugins": plugin_list,
        }


class PluginLoader:
    """Loads plugins from the filesystem"""

    @staticmethod
    def load_plugin(module_path: str, class_name: str) -> Type[BasePlugin]:
        """
        Load a plugin class from a module

        Args:
            module_path: Python module path (e.g., 'aura_backend.plugins.logging_plugin')
            class_name: Class name (e.g., 'LoggingPlugin')

        Returns:
            The plugin class
        """
        try:
            module = importlib.import_module(module_path)
            plugin_class = getattr(module, class_name)

            if not inspect.isclass(plugin_class) or not issubclass(plugin_class, BasePlugin):
                raise PluginLoadError(f"{class_name} is not a subclass of BasePlugin")

            return plugin_class
        except ImportError as e:
            raise PluginLoadError(f"Failed to load module {module_path}: {str(e)}") from e
        except AttributeError as e:
            raise PluginLoadError(f"Class {class_name} not found in {module_path}") from e

    @staticmethod
    def discover_plugins(plugin_dir: Path) -> Dict[str, Type[BasePlugin]]:
        """
        Auto-discover plugins in a directory

        Looks for Python files with classes inheriting from BasePlugin.

        Args:
            plugin_dir: Directory containing plugin modules

        Returns:
            Dictionary of {plugin_id: plugin_class}
        """
        plugins = {}

        if not plugin_dir.exists():
            return plugins

        for file_path in plugin_dir.glob("*.py"):
            if file_path.name.startswith("_"):
                continue

            module_name = file_path.stem
            module_path = f"aura_backend.plugins.{module_name}"

            try:
                module = importlib.import_module(module_path)

                for name, obj in inspect.getmembers(module):
                    if (
                        inspect.isclass(obj)
                        and issubclass(obj, BasePlugin)
                        and obj is not BasePlugin
                    ):
                        plugin = obj()
                        metadata = plugin.get_metadata()
                        plugins[metadata.id] = obj
            except Exception:
                continue

        return plugins


class PluginRegistrationError(Exception):
    """Raised when plugin registration fails"""

    pass


class PluginInitializationError(Exception):
    """Raised when plugin initialization fails"""

    pass


class PluginLoadError(Exception):
    """Raised when plugin loading fails"""

    pass
