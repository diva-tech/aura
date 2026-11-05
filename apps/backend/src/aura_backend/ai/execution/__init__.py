"""
Execution engine abstractions.

Architecture for executing plans and tracking progress.
No execution logic - contracts only.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ExecutionPhase(str, Enum):
    """Execution phase"""

    PREPARING = "preparing"
    RUNNING = "running"
    MONITORING = "monitoring"
    COMPLETED = "completed"


class FailureReason(str, Enum):
    """Why execution failed"""

    TIMEOUT = "timeout"
    VALIDATION_ERROR = "validation_error"
    EXECUTION_ERROR = "execution_error"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


@dataclass
class Checkpoint:
    """Execution checkpoint for recovery"""

    checkpoint_id: str
    phase: ExecutionPhase
    timestamp: datetime
    state: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Progress:
    """Execution progress tracking"""

    completed_steps: int = 0
    total_steps: int = 0
    current_step_description: str = ""
    estimated_remaining_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def completion_percentage(self) -> float:
        """Progress as percentage"""
        if self.total_steps == 0:
            return 0.0
        return (self.completed_steps / self.total_steps) * 100


@dataclass
class ExecutionResult:
    """Result of execution"""

    success: bool
    output: Any = None
    error: Optional[str] = None
    failure_reason: Optional[FailureReason] = None
    execution_time_ms: float = 0.0
    checkpoints: List[Checkpoint] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class RetryPolicy(ABC):
    """Retry strategy for failed steps"""

    @abstractmethod
    def should_retry(self, attempt: int, error: str) -> bool:
        """Determine if should retry"""
        pass

    @abstractmethod
    def get_delay_ms(self, attempt: int) -> float:
        """Get delay before retry"""
        pass


class ExecutionPolicy(ABC):
    """Policy for execution behavior"""

    @abstractmethod
    def validate_execution_plan(self, plan: Any) -> Dict[str, Any]:
        """Validate a plan before execution"""
        pass

    @abstractmethod
    def handle_step_failure(self, step: Any, error: str) -> ExecutionPhase:
        """Determine next phase after step failure"""
        pass

    @abstractmethod
    def should_continue(self, progress: Progress) -> bool:
        """Determine if should continue execution"""
        pass


class ExecutionContext(ABC):
    """Context for a single execution"""

    @abstractmethod
    async def get_phase(self) -> ExecutionPhase:
        """Get current execution phase"""
        pass

    @abstractmethod
    async def set_phase(self, phase: ExecutionPhase) -> None:
        """Update execution phase"""
        pass

    @abstractmethod
    async def update_progress(self, progress: Progress) -> None:
        """Update progress tracking"""
        pass

    @abstractmethod
    async def create_checkpoint(self, state: Dict[str, Any]) -> Checkpoint:
        """Create recovery checkpoint"""
        pass

    @abstractmethod
    async def restore_checkpoint(self, checkpoint: Checkpoint) -> None:
        """Restore from checkpoint"""
        pass


class ExecutionPipeline(ABC):
    """Pipeline for executing plans"""

    @abstractmethod
    async def execute(
        self,
        plan: Any,
        context: Any,
        policy: ExecutionPolicy
    ) -> ExecutionResult:
        """Execute a plan"""
        pass

    @abstractmethod
    async def execute_step(
        self,
        step: Any,
        context: Any
    ) -> Dict[str, Any]:
        """Execute single step"""
        pass

    @abstractmethod
    async def cancel(self) -> None:
        """Cancel ongoing execution"""
        pass

    @abstractmethod
    async def health(self) -> Dict[str, Any]:
        """Get pipeline health"""
        pass
