"""
Universal tool framework.

Every future capability becomes a Tool.
Defines tool interface and production implementations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

# Import enhanced models
from aura_backend.ai.tools.models import (
    ToolResult,
    ToolMetrics,
    ToolArtifact,
    ToolExecutionLog,
)


class ToolStatus(str, Enum):
    """Tool health status"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


@dataclass
class ToolParameter:
    """Tool parameter definition"""

    name: str
    type: str
    description: str
    required: bool = True
    default: Optional[Any] = None
    options: Optional[List[Any]] = None


@dataclass
class ToolCapability:
    """Tool capability declaration"""

    name: str
    description: str
    version: str = "1.0.0"


class Tool(ABC):
    """
    Abstract base for all tools.

    Every capability that an agent can use becomes a Tool.
    """

    def __init__(self):
        self._id = f"{self.__class__.__name__}"
        self._created_at = datetime.utcnow()
        self._execution_count = 0
        self._total_execution_time_ms = 0.0

    @property
    def id(self) -> str:
        """Tool ID"""
        return self._id

    @abstractmethod
    def get_name(self) -> str:
        """Get tool name"""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Get tool description"""
        pass

    @abstractmethod
    def get_capabilities(self) -> List[ToolCapability]:
        """Get capabilities this tool provides"""
        pass

    @abstractmethod
    def get_parameters(self) -> List[ToolParameter]:
        """Get required parameters"""
        pass

    @abstractmethod
    async def validate(self, **kwargs) -> Dict[str, Any]:
        """
        Validate parameters.

        Returns validation result with errors/warnings.
        """
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """
        Execute the tool.

        Returns ToolResult with output or error.
        """
        pass

    @abstractmethod
    async def health(self) -> Dict[str, Any]:
        """Get tool health status"""
        pass

    @property
    def timeout_seconds(self) -> float:
        """Tool execution timeout"""
        return 300.0

    async def get_info(self) -> Dict[str, Any]:
        """Get complete tool information"""
        return {
            "id": self.id,
            "name": self.get_name(),
            "description": self.get_description(),
            "capabilities": [
                {
                    "name": cap.name,
                    "description": cap.description,
                    "version": cap.version,
                }
                for cap in self.get_capabilities()
            ],
            "parameters": [
                {
                    "name": param.name,
                    "type": param.type,
                    "description": param.description,
                    "required": param.required,
                }
                for param in self.get_parameters()
            ],
            "timeout_seconds": self.timeout_seconds,
            "execution_count": self._execution_count,
            "total_execution_time_ms": self._total_execution_time_ms,
        }


# Import production tool implementations
from aura_backend.ai.tools.filesystem import FilesystemTool as _FilesystemToolImpl
from aura_backend.ai.tools.python_executor import PythonExecutor as _PythonExecutorImpl
from aura_backend.ai.tools.browser import BrowserTool as _BrowserToolImpl

# Export production implementations
FilesystemTool = _FilesystemToolImpl
PythonTool = _PythonExecutorImpl
BrowserTool = _BrowserToolImpl


# Placeholder tool implementations (for Milestone 5+)

class VisionTool(Tool):
    """Placeholder vision analysis tool"""

    def get_name(self) -> str:
        return "Vision"

    def get_description(self) -> str:
        return "Image analysis and understanding"

    def get_capabilities(self) -> List[ToolCapability]:
        return [
            ToolCapability("analyze-image", "Analyze image content"),
            ToolCapability("detect-objects", "Detect objects in images"),
            ToolCapability("ocr", "Extract text from images"),
        ]

    def get_parameters(self) -> List[ToolParameter]:
        return []

    async def validate(self, **kwargs) -> Dict[str, Any]:
        return {"valid": True}

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(success=False, data=None, errors=["Not implemented in Milestone 4"])

    async def health(self) -> Dict[str, Any]:
        return {"status": "placeholder"}


class VideoTool(Tool):
    """Placeholder video processing tool"""

    def get_name(self) -> str:
        return "Video"

    def get_description(self) -> str:
        return "Video processing and analysis"

    def get_capabilities(self) -> List[ToolCapability]:
        return [
            ToolCapability("process-video", "Process video files"),
            ToolCapability("extract-frames", "Extract frames from video"),
            ToolCapability("analyze-video", "Analyze video content"),
        ]

    def get_parameters(self) -> List[ToolParameter]:
        return []

    async def validate(self, **kwargs) -> Dict[str, Any]:
        return {"valid": True}

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(success=False, data=None, errors=["Not implemented in Milestone 4"])

    async def health(self) -> Dict[str, Any]:
        return {"status": "placeholder"}


class AudioTool(Tool):
    """Placeholder audio processing tool"""

    def get_name(self) -> str:
        return "Audio"

    def get_description(self) -> str:
        return "Audio processing and analysis"

    def get_capabilities(self) -> List[ToolCapability]:
        return [
            ToolCapability("transcribe-audio", "Transcribe speech to text"),
            ToolCapability("analyze-audio", "Analyze audio content"),
        ]

    def get_parameters(self) -> List[ToolParameter]:
        return []

    async def validate(self, **kwargs) -> Dict[str, Any]:
        return {"valid": True}

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(success=False, data=None, errors=["Not implemented in Milestone 4"])

    async def health(self) -> Dict[str, Any]:
        return {"status": "placeholder"}


class ImageGenerationTool(Tool):
    """Placeholder image generation tool"""

    def get_name(self) -> str:
        return "ImageGeneration"

    def get_description(self) -> str:
        return "Image generation from prompts"

    def get_capabilities(self) -> List[ToolCapability]:
        return [
            ToolCapability("generate-image", "Generate images from text"),
            ToolCapability("edit-image", "Edit existing images"),
        ]

    def get_parameters(self) -> List[ToolParameter]:
        return []

    async def validate(self, **kwargs) -> Dict[str, Any]:
        return {"valid": True}

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(success=False, data=None, errors=["Not implemented in Milestone 4"])

    async def health(self) -> Dict[str, Any]:
        return {"status": "placeholder"}


class ToolRegistry:
    """Registry for tools with capability discovery (thread-safe)"""

    def __init__(self):
        import threading

        self._tools: Dict[str, Tool] = {}
        self._capabilities_index: Dict[str, List[str]] = {}
        self._metrics: Dict[str, Dict[str, Any]] = {}
        # CRITICAL FIX: Add thread-safe locking (same pattern as Runtime)
        self._registry_lock = threading.RLock()
        self._metrics_lock = threading.Lock()

    def register(self, tool: Tool) -> None:
        """Register a tool (thread-safe)"""
        with self._registry_lock:
            self._tools[tool.id] = tool

            with self._metrics_lock:
                self._metrics[tool.id] = {
                    "execution_count": 0,
                    "total_time_ms": 0.0,
                    "average_time_ms": 0.0,
                    "last_execution": None,
                }

            # Index capabilities
            for cap in tool.get_capabilities():
                if cap.name not in self._capabilities_index:
                    self._capabilities_index[cap.name] = []
                self._capabilities_index[cap.name].append(tool.id)

    def unregister(self, tool_id: str) -> None:
        """Unregister a tool (thread-safe)"""
        with self._registry_lock:
            if tool_id in self._tools:
                del self._tools[tool_id]
                # Clean up capability index
                for cap_tools in self._capabilities_index.values():
                    if tool_id in cap_tools:
                        cap_tools.remove(tool_id)

            with self._metrics_lock:
                if tool_id in self._metrics:
                    del self._metrics[tool_id]

    def get(self, tool_id: str) -> Optional[Tool]:
        """Get tool by ID (thread-safe)"""
        with self._registry_lock:
            return self._tools.get(tool_id)

    def list(self) -> List[Tool]:
        """List all registered tools (thread-safe)"""
        with self._registry_lock:
            return list(self._tools.values())

    def count(self) -> int:
        """Get number of registered tools"""
        return len(self._tools)

    def find_by_capability(self, capability_name: str) -> List[Tool]:
        """Find tools that support a capability"""
        tool_ids = self._capabilities_index.get(capability_name, [])
        return [self._tools[tid] for tid in tool_ids if tid in self._tools]

    def list_capabilities(self) -> Dict[str, List[str]]:
        """List all capabilities and tools that support them"""
        return {
            cap: [self._tools[tid].get_name() for tid in tool_ids if tid in self._tools]
            for cap, tool_ids in self._capabilities_index.items()
        }

    async def get_all_capabilities(self) -> Dict[str, List[Dict[str, str]]]:
        """Get all capabilities from all tools"""
        capabilities = {}
        for tool in self._tools.values():
            capabilities[tool.id] = [
                {"name": cap.name, "description": cap.description, "version": cap.version}
                for cap in tool.get_capabilities()
            ]
        return capabilities

    async def health(self) -> Dict[str, Any]:
        """Get health of all tools"""
        health = {}
        for tool in self._tools.values():
            try:
                health[tool.id] = await tool.health()
            except Exception as e:
                health[tool.id] = {"status": "error", "error": str(e)}
        return health

    async def health_all(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed health of all tools with metrics"""
        health = {}
        for tool_id, tool in self._tools.items():
            try:
                tool_health = await tool.health()
                tool_health.update(self._metrics.get(tool_id, {}))
                health[tool_id] = tool_health
            except Exception as e:
                health[tool_id] = {
                    "status": "error",
                    "error": str(e),
                    **self._metrics.get(tool_id, {})
                }
        return health

    def update_metrics(self, tool_id: str, execution_time_ms: float) -> None:
        """Update tool execution metrics (thread-safe)"""
        with self._metrics_lock:
            if tool_id not in self._metrics:
                self._metrics[tool_id] = {
                    "execution_count": 0,
                    "total_time_ms": 0.0,
                    "average_time_ms": 0.0,
                    "last_execution": None,
                }

            metrics = self._metrics[tool_id]
            metrics["execution_count"] += 1
            metrics["total_time_ms"] += execution_time_ms
            metrics["average_time_ms"] = metrics["total_time_ms"] / metrics["execution_count"]
            metrics["last_execution"] = datetime.utcnow().isoformat()

    def get_metrics(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Get metrics for a tool"""
        return self._metrics.get(tool_id)

    def get_tool_info(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Get complete tool information with metrics"""
        tool = self._tools.get(tool_id)
        if not tool:
            return None

        return {
            "id": tool.id,
            "name": tool.get_name(),
            "description": tool.get_description(),
            "capabilities": [
                {
                    "name": cap.name,
                    "description": cap.description,
                    "version": cap.version,
                }
                for cap in tool.get_capabilities()
            ],
            "metrics": self._metrics.get(tool_id, {}),
        }
