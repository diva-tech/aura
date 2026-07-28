"""
Planning abstractions.

Defines interfaces for goal planning without implementation.
No AI logic included - contracts only.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


class ExecutionStrategy(str):
    """Execution strategy types"""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    ADAPTIVE = "adaptive"


@dataclass
class PlanStep:
    """Single step in a plan"""

    step_id: str
    description: str
    action: str
    parameters: Dict[str, Any] = None
    dependencies: List[str] = None
    retry_policy: Optional[Dict[str, Any]] = None
    timeout_seconds: Optional[float] = None
    expected_duration_ms: float = 0.0

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class Plan:
    """Execution plan for a goal"""

    plan_id: str
    goal_id: str
    steps: List[PlanStep]
    strategy: ExecutionStrategy
    total_estimated_time_ms: float
    created_at: datetime = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}

    @property
    def step_count(self) -> int:
        """Total steps in plan"""
        return len(self.steps)


@dataclass
class PlanResult:
    """Result of planning"""

    plan: Plan
    feasible: bool
    confidence: float
    reasoning: str
    alternatives: List[Plan] = None
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.alternatives is None:
            self.alternatives = []


class Planner(ABC):
    """
    Abstract planner interface.

    Converts goals into executable plans.
    No implementation - contracts only.
    """

    @abstractmethod
    async def plan(self, goal: Any, context: Any) -> PlanResult:
        """
        Create a plan for achieving the goal.

        Args:
            goal: Goal to plan for
            context: Execution context

        Returns:
            PlanResult with plan and feasibility assessment
        """
        pass

    @abstractmethod
    async def replan(self, goal: Any, context: Any, previous_plan: Plan) -> PlanResult:
        """
        Revise plan based on execution feedback.

        Args:
            goal: Original goal
            context: Execution context
            previous_plan: Previous plan to revise

        Returns:
            Revised PlanResult
        """
        pass

    @abstractmethod
    async def validate_plan(self, plan: Plan) -> Dict[str, Any]:
        """
        Validate a plan for feasibility.

        Args:
            plan: Plan to validate

        Returns:
            Validation result with errors/warnings
        """
        pass

    @abstractmethod
    async def health(self) -> Dict[str, Any]:
        """Get planner health status"""
        pass
