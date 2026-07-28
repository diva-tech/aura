"""Planning models for ResearchAgent."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4


class StepStatus(str, Enum):
    """Execution step status"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


class StepToolType(str, Enum):
    """Tool type hints for step execution"""

    BROWSER = "browser"
    FILESYSTEM = "filesystem"
    PYTHON = "python"
    ANY = "any"


@dataclass
class PlanStep:
    """Executable planning step"""

    description: str
    reason: str
    required_capabilities: Set[str] = field(default_factory=set)
    expected_output: str = ""
    tool_hints: List[StepToolType] = field(default_factory=lambda: [StepToolType.ANY])
    priority: int = 0  # Higher = more important

    id: str = field(default_factory=lambda: str(uuid4()))
    status: StepStatus = field(default=StepStatus.PENDING)
    tool_used: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 2
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def is_complete(self) -> bool:
        return self.status in {StepStatus.COMPLETED, StepStatus.FAILED, StepStatus.SKIPPED}

    def can_retry(self) -> bool:
        return self.retry_count < self.max_retries and self.status == StepStatus.FAILED

    def duration_ms(self) -> Optional[float]:
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds() * 1000
        return None


@dataclass
class Plan:
    """Agent execution plan"""

    steps: List[PlanStep] = field(default_factory=list)
    strategy: str = "sequential"
    created_at: datetime = field(default_factory=datetime.utcnow)

    current_step_index: int = 0
    completed_steps: List[str] = field(default_factory=list)

    def add_step(self, step: PlanStep) -> None:
        self.steps.append(step)

    def current_step(self) -> Optional[PlanStep]:
        if self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None

    def advance(self) -> bool:
        if self.current_step_index < len(self.steps) - 1:
            self.current_step_index += 1
            return True
        return False

    def insert_step(self, index: int, step: PlanStep) -> None:
        self.steps.insert(index, step)

    def skip_current(self) -> None:
        step = self.current_step()
        if step:
            step.status = StepStatus.SKIPPED
            self.advance()

    def is_complete(self) -> bool:
        return self.current_step_index >= len(self.steps) or all(s.is_complete() for s in self.steps)

    def success_rate(self) -> float:
        if not self.steps:
            return 0.0
        completed = sum(1 for s in self.steps if s.status == StepStatus.COMPLETED)
        return completed / len(self.steps) * 100
