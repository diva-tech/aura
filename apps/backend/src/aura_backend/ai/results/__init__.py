"""
Execution results and outcome tracking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class StepResult:
    """Result of executing a single step"""

    step_id: str
    success: bool
    output: Any = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionOutcome:
    """Complete outcome of goal execution"""

    session_id: str
    goal_id: str
    success: bool

    completed_steps: int = 0
    total_steps: int = 0
    step_results: List[StepResult] = field(default_factory=list)

    final_output: Any = None
    error_message: Optional[str] = None

    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime = field(default_factory=datetime.utcnow)

    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def execution_time_ms(self) -> float:
        """Total execution time"""
        return (self.completed_at - self.started_at).total_seconds() * 1000

    @property
    def success_rate(self) -> float:
        """Percentage of successful steps"""
        if self.total_steps == 0:
            return 0.0
        successful = sum(1 for r in self.step_results if r.success)
        return (successful / self.total_steps) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Serialize outcome"""
        return {
            "session_id": self.session_id,
            "goal_id": self.goal_id,
            "success": self.success,
            "completed_steps": self.completed_steps,
            "total_steps": self.total_steps,
            "execution_time_ms": self.execution_time_ms,
            "success_rate": self.success_rate,
            "error_message": self.error_message,
        }
