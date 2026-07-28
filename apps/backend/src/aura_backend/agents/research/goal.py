"""Goal model for ResearchAgent."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4


class GoalStatus(str, Enum):
    """Goal lifecycle status"""

    ACCEPTED = "accepted"
    PLANNING = "planning"
    EXECUTING = "executing"
    REFLECTING = "reflecting"
    REPLANNING = "replanning"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Goal:
    """Research goal"""

    description: str
    context: Optional[str] = None
    success_criteria: Optional[str] = None
    max_steps: int = 20
    max_reflections: int = 5
    timeout_seconds: int = 3600

    id: str = field(default_factory=lambda: str(uuid4()))
    status: GoalStatus = field(default=GoalStatus.ACCEPTED)
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

    def __post_init__(self):
        if not self.description:
            raise ValueError("Goal description required")

    def is_complete(self) -> bool:
        return self.status in {GoalStatus.COMPLETED, GoalStatus.FAILED, GoalStatus.CANCELLED}

    def is_active(self) -> bool:
        return not self.is_complete()
