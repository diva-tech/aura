"""Events published by ResearchAgent."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class ResearchAgentEvent:
    """Base event for ResearchAgent"""

    goal_id: str
    agent_id: str
    timestamp: datetime
    metadata: Dict[str, Any]


@dataclass
class GoalAcceptedEvent(ResearchAgentEvent):
    """Goal has been accepted for execution"""

    goal_description: str = ""


@dataclass
class PlanningStartedEvent(ResearchAgentEvent):
    """Planning phase has started"""

    pass


@dataclass
class PlanningCompletedEvent(ResearchAgentEvent):
    """Planning phase completed"""

    step_count: int = 0
    planning_time_ms: float = 0.0
    tokens_used: int = 0


@dataclass
class StepStartedEvent(ResearchAgentEvent):
    """Step execution started"""

    step_id: str = ""
    step_description: str = ""
    step_index: int = 0


@dataclass
class StepCompletedEvent(ResearchAgentEvent):
    """Step execution completed"""

    step_id: str = ""
    step_status: str = "completed"
    execution_time_ms: float = 0.0
    tool_used: Optional[str] = None
    tokens_used: int = 0


@dataclass
class ReflectionStartedEvent(ResearchAgentEvent):
    """Reflection phase started"""

    reflection_count: int = 0


@dataclass
class ReflectionCompletedEvent(ResearchAgentEvent):
    """Reflection phase completed"""

    decision: str = ""
    reflection_time_ms: float = 0.0
    tokens_used: int = 0


@dataclass
class ReplanningStartedEvent(ResearchAgentEvent):
    """Replanning phase started"""

    reason: str = ""


@dataclass
class GoalCompletedEvent(ResearchAgentEvent):
    """Goal completed successfully"""

    total_time_ms: float = 0.0
    steps_executed: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0


@dataclass
class GoalFailedEvent(ResearchAgentEvent):
    """Goal failed"""

    error: str = ""
    total_time_ms: float = 0.0
    steps_executed: int = 0
    total_tokens: int = 0
