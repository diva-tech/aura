"""
Enhanced tool result models with observability support.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass
class ToolMetrics:
    """Tool execution metrics"""

    execution_time_ms: float
    memory_used_mb: Optional[float] = None
    cpu_percent: Optional[float] = None
    io_operations: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_time_ms": self.execution_time_ms,
            "memory_used_mb": self.memory_used_mb,
            "cpu_percent": self.cpu_percent,
            "io_operations": self.io_operations,
        }


@dataclass
class ToolArtifact:
    """Output artifact from tool execution"""

    name: str
    type: str
    path: Optional[str] = None
    size_bytes: Optional[int] = None
    mime_type: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "path": self.path,
            "size_bytes": self.size_bytes,
            "mime_type": self.mime_type,
        }


@dataclass
class ToolExecutionLog:
    """Tool execution log entry"""

    timestamp: datetime
    level: str  # DEBUG, INFO, WARNING, ERROR
    message: str
    context: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level,
            "message": self.message,
            "context": self.context or {},
        }


@dataclass
class ToolResult:
    """Enhanced result of tool execution"""

    success: bool
    data: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    duration: float = 0.0  # milliseconds
    logs: List[ToolExecutionLog] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    artifacts: List[ToolArtifact] = field(default_factory=list)
    metrics: Optional[ToolMetrics] = None

    # Backward compatibility
    @property
    def output(self) -> Any:
        return self.data

    @property
    def error(self) -> Optional[str]:
        return self.errors[0] if self.errors else None

    @property
    def execution_time_ms(self) -> float:
        return self.duration

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "metadata": self.metadata,
            "duration": self.duration,
            "logs": [log.to_dict() for log in self.logs],
            "warnings": self.warnings,
            "errors": self.errors,
            "artifacts": [artifact.to_dict() for artifact in self.artifacts],
            "metrics": self.metrics.to_dict() if self.metrics else None,
        }

    def add_log(self, level: str, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Add execution log entry"""
        self.logs.append(ToolExecutionLog(
            timestamp=datetime.utcnow(),
            level=level,
            message=message,
            context=context
        ))

    def add_warning(self, warning: str) -> None:
        """Add warning"""
        self.warnings.append(warning)

    def add_error(self, error: str) -> None:
        """Add error"""
        self.errors.append(error)

    def add_artifact(self, artifact: ToolArtifact) -> None:
        """Add artifact"""
        self.artifacts.append(artifact)
