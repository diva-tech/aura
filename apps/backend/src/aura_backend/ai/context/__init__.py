"""
Agent execution context.

Flows through every agent execution, carrying:
- Session and correlation information
- Current goal and step
- Working memory state
- Execution history
- Configuration
- Runtime references
- Cancellation signal
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4


@dataclass
class ExecutionStep:
    """Record of a single execution step"""

    step_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    step_type: str = ""
    description: str = ""
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentContext:
    """
    Complete execution context for an agent.

    Carries all necessary state through the execution lifecycle.
    """

    # Identity
    session_id: str = field(default_factory=lambda: str(uuid4()))
    correlation_id: str = field(default_factory=lambda: str(uuid4()))
    trace_id: str = field(default_factory=lambda: str(uuid4()))

    # Execution target
    goal: str = ""
    goal_id: Optional[str] = None
    current_step: int = 0
    total_steps: Optional[int] = None

    # State
    working_memory: Dict[str, Any] = field(default_factory=dict)
    execution_history: list[ExecutionStep] = field(default_factory=list)

    # Configuration
    metadata: Dict[str, Any] = field(default_factory=dict)
    configuration: Dict[str, Any] = field(default_factory=dict)

    # Runtime references
    event_publisher: Optional[Any] = None
    runtime: Optional[Any] = None
    service_container: Optional[Any] = None

    # Lifecycle
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Cancellation
    _cancel_requested: bool = field(default=False, init=False)
    _cancel_lock: threading.Lock = field(default_factory=threading.Lock, init=False)

    def add_step(self, step: ExecutionStep) -> None:
        """Record an execution step"""
        self.execution_history.append(step)

    def cancel(self) -> None:
        """Request cancellation"""
        with self._cancel_lock:
            self._cancel_requested = True

    def is_cancelled(self) -> bool:
        """Check if cancellation was requested"""
        with self._cancel_lock:
            return self._cancel_requested

    def update_memory(self, key: str, value: Any) -> None:
        """Update working memory"""
        self.working_memory[key] = value

    def get_memory(self, key: str, default: Any = None) -> Any:
        """Retrieve from working memory"""
        return self.working_memory.get(key, default)

    def duration_ms(self) -> float:
        """Get execution duration"""
        if not self.started_at:
            return 0.0
        end = self.completed_at or datetime.utcnow()
        return (end - self.started_at).total_seconds() * 1000

    def to_dict(self) -> Dict[str, Any]:
        """Serialize context for logging/transmission"""
        return {
            "session_id": self.session_id,
            "correlation_id": self.correlation_id,
            "trace_id": self.trace_id,
            "goal": self.goal,
            "goal_id": self.goal_id,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "working_memory_size": len(self.working_memory),
            "execution_history_size": len(self.execution_history),
            "duration_ms": self.duration_ms(),
            "cancelled": self.is_cancelled(),
        }
