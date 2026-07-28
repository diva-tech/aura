"""
Goal domain models.

Goals represent the top-level intent for an agent execution.
All goal objects are immutable.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4


class GoalPriority(str, Enum):
    """Goal execution priority"""

    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class GoalStatus(str, Enum):
    """Goal execution status"""

    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class GoalMetadata:
    """Immutable goal metadata"""

    tags: tuple[str, ...] = ()
    category: str = ""
    owner: Optional[str] = None
    deadline: Optional[datetime] = None
    max_retries: int = 3
    timeout_seconds: Optional[float] = None
    custom_fields: Dict[str, Any] = field(default_factory=dict)

    def with_field(self, **kwargs) -> GoalMetadata:
        """Create new metadata with updated fields"""
        return replace(self, **kwargs)


@dataclass(frozen=True)
class Goal:
    """
    Immutable goal representation.

    Represents what an agent should accomplish.
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    description: str = ""
    objective: str = ""
    priority: GoalPriority = GoalPriority.NORMAL
    status: GoalStatus = GoalStatus.PENDING
    metadata: GoalMetadata = field(default_factory=GoalMetadata)

    # Tracking
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Constraints
    constraints: tuple[str, ...] = ()
    requirements: tuple[str, ...] = ()

    def with_status(self, status: GoalStatus) -> Goal:
        """Create new goal with updated status"""
        kwargs = {"status": status}
        if status == GoalStatus.ACTIVE and not self.started_at:
            kwargs["started_at"] = datetime.utcnow()
        elif status in (GoalStatus.COMPLETED, GoalStatus.FAILED, GoalStatus.CANCELLED):
            kwargs["completed_at"] = datetime.utcnow()
        return replace(self, **kwargs)

    def with_priority(self, priority: GoalPriority) -> Goal:
        """Create new goal with updated priority"""
        return replace(self, priority=priority)

    def with_metadata(self, **fields) -> Goal:
        """Create new goal with updated metadata"""
        new_metadata = self.metadata.with_field(**fields)
        return replace(self, metadata=new_metadata)

    def duration_ms(self) -> Optional[float]:
        """Get goal execution duration"""
        if not self.started_at:
            return None
        end = self.completed_at or datetime.utcnow()
        return (end - self.started_at).total_seconds() * 1000

    def is_expired(self) -> bool:
        """Check if goal has exceeded its deadline"""
        if not self.metadata.deadline:
            return False
        return datetime.utcnow() > self.metadata.deadline

    def to_dict(self) -> Dict[str, Any]:
        """Serialize goal for transmission/logging"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "objective": self.objective,
            "priority": self.priority.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_ms": self.duration_ms(),
            "constraints": self.constraints,
            "requirements": self.requirements,
            "tags": self.metadata.tags,
            "deadline": self.metadata.deadline.isoformat() if self.metadata.deadline else None,
        }


@dataclass(frozen=True)
class GoalResult:
    """
    Immutable result of goal execution.
    """

    goal_id: str
    status: GoalStatus
    success: bool = False
    result_data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0
    completed_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize result for transmission"""
        return {
            "goal_id": self.goal_id,
            "status": self.status.value,
            "success": self.success,
            "result_data": self.result_data,
            "error_message": self.error_message,
            "execution_time_ms": self.execution_time_ms,
            "completed_at": self.completed_at.isoformat(),
        }
