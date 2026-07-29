"""M11 Phase 3: Editing M6 Agents for M8 Orchestration.

All 10 editing engines wrapped as M6 agents (ExecutableAgent) for integration
with the M8 Task Orchestration runtime. Each agent is stateless and deterministic.
"""

from abc import ABC
from typing import Any, Dict, Optional, Set
from uuid import uuid4

from aura_backend.orchestration.models import Capability, ExecutionStatus, Skill, Task, TaskAttempt, ToolRequirement
from aura_backend.orchestration.registry import ExecutableAgent

from .engines import (
    BrollEngine,
    ClipEngine,
    CutEngine,
    EditingEngine,
    MusicEngine,
    OverlayEngine,
    SilenceEngine,
    SubtitleEngine,
    TimelineEngine,
    TransitionEngine,
    ZoomEngine,
)
from .models import Clip, Cut, Transition, SubtitleSegment, Overlay, ZoomAction, BrollSuggestion, MusicCue, SilenceRemoval, EditTimeline


class EditingAgentBase(ExecutableAgent, ABC):
    """Base class for all editing M6 agents.

    Wraps a deterministic editing engine and exposes it as an M8-compatible agent.
    All agents are stateless - the engine contains the pure logic.
    """

    def __init__(self, engine: EditingEngine, agent_name: str):
        """Initialize with engine and metadata."""
        self._id = str(uuid4())
        self._name = agent_name
        self._engine = engine

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def capabilities(self) -> Set[Capability]:
        return {Capability.ANALYSIS, Capability.DATA_PROCESSING}

    @property
    def skills(self) -> Set[Skill]:
        return {Skill.LLM_SYNTHESIS, Skill.FACT_EXTRACTION}

    @property
    def tool_requirements(self) -> Set[ToolRequirement]:
        return set()  # Editing engines are pure; no external tools needed

    async def can_execute(self, task: Task) -> bool:
        """All editing agents can execute if metadata matches."""
        engine_type = task.metadata.get("engine_type", "")
        return engine_type == self.name.lower().replace("agent", "")

    async def execute(self, task: Task) -> TaskAttempt:
        """Execute the editing engine and return attempt record."""
        try:
            # Extract inputs from task metadata
            inputs = task.metadata.get("inputs", {})

            # Call the engine's analyze method
            outputs = self._engine.analyze(**inputs)

            # Serialize results
            result = {
                "engine": self._engine.name,
                "output_count": len(outputs),
                "outputs": [o.to_dict() if hasattr(o, "to_dict") else str(o) for o in outputs],
            }

            return TaskAttempt(
                task_id=task.id,
                status=ExecutionStatus.COMPLETED,
                assigned_agent_id=self.id,
                result=str(result),
            )
        except Exception as e:
            return TaskAttempt(
                task_id=task.id,
                status=ExecutionStatus.FAILED,
                assigned_agent_id=self.id,
                error=str(e),
            )

    async def cancel(self, attempt_id: str) -> bool:
        """Editing engines are quick; no long-running tasks to cancel."""
        return True


# ============================================================================
# EDITING AGENTS (10 total)
# ============================================================================


class ClipAgent(EditingAgentBase):
    """M6 agent wrapping ClipEngine for M8 orchestration."""

    def __init__(self):
        super().__init__(ClipEngine(), "ClipAgent")


class TimelineAgent(EditingAgentBase):
    """M6 agent wrapping TimelineEngine for M8 orchestration."""

    def __init__(self):
        super().__init__(TimelineEngine(), "TimelineAgent")


class CutAgent(EditingAgentBase):
    """M6 agent wrapping CutEngine for M8 orchestration."""

    def __init__(self):
        super().__init__(CutEngine(), "CutAgent")


class TransitionAgent(EditingAgentBase):
    """M6 agent wrapping TransitionEngine for M8 orchestration."""

    def __init__(self):
        super().__init__(TransitionEngine(), "TransitionAgent")


class SubtitleAgent(EditingAgentBase):
    """M6 agent wrapping SubtitleEngine for M8 orchestration."""

    def __init__(self):
        super().__init__(SubtitleEngine(), "SubtitleAgent")


class OverlayAgent(EditingAgentBase):
    """M6 agent wrapping OverlayEngine for M8 orchestration."""

    def __init__(self):
        super().__init__(OverlayEngine(), "OverlayAgent")


class ZoomAgent(EditingAgentBase):
    """M6 agent wrapping ZoomEngine for M8 orchestration."""

    def __init__(self):
        super().__init__(ZoomEngine(), "ZoomAgent")


class BrollAgent(EditingAgentBase):
    """M6 agent wrapping BrollEngine for M8 orchestration."""

    def __init__(self):
        super().__init__(BrollEngine(), "BrollAgent")


class MusicAgent(EditingAgentBase):
    """M6 agent wrapping MusicEngine for M8 orchestration."""

    def __init__(self):
        super().__init__(MusicEngine(), "MusicAgent")


class SilenceAgent(EditingAgentBase):
    """M6 agent wrapping SilenceEngine for M8 orchestration."""

    def __init__(self):
        super().__init__(SilenceEngine(), "SilenceAgent")


# ============================================================================
# REVIEW AGENT
# ============================================================================


class ReviewAgent(EditingAgentBase):
    """M6 agent for reviewing and validating complete editing plans.

    Consumes all editing suggestions and produces quality metrics.
    """

    def __init__(self):
        self._id = str(uuid4())
        self._name = "ReviewAgent"
        self._engine = None  # No engine; pure review logic

    async def execute(self, task: Task) -> TaskAttempt:
        """Review the complete editing plan."""
        try:
            plan = task.metadata.get("edit_plan", {})

            # Validate structure
            findings = []
            if not plan.get("clips"):
                findings.append("No clips defined in plan")
            if not plan.get("timeline"):
                findings.append("No timeline sequencing")
            if not plan.get("transitions"):
                findings.append("No transitions defined")

            score = max(0.0, 1.0 - (len(findings) * 0.1))

            result = {
                "review_findings": findings,
                "quality_score": score,
                "is_valid": len(findings) == 0,
            }

            status = ExecutionStatus.COMPLETED if len(findings) == 0 else ExecutionStatus.COMPLETED
            return TaskAttempt(
                task_id=task.id,
                status=status,
                assigned_agent_id=self.id,
                result=str(result),
            )
        except Exception as e:
            return TaskAttempt(
                task_id=task.id,
                status=ExecutionStatus.FAILED,
                assigned_agent_id=self.id,
                error=str(e),
            )


# ============================================================================
# EDITING AGENT REGISTRY
# ============================================================================


def create_editing_agent_registry() -> Dict[str, ExecutableAgent]:
    """Create dictionary of all editing agents for M8 registration."""
    return {
        "clip": ClipAgent(),
        "timeline": TimelineAgent(),
        "cut": CutAgent(),
        "transition": TransitionAgent(),
        "subtitle": SubtitleAgent(),
        "overlay": OverlayAgent(),
        "zoom": ZoomAgent(),
        "broll": BrollAgent(),
        "music": MusicAgent(),
        "silence": SilenceAgent(),
        "review": ReviewAgent(),
    }


def register_editing_agents(registry: Any) -> None:
    """Register all editing agents with M8 AgentRegistry."""
    agents = create_editing_agent_registry()
    for agent in agents.values():
        registry.register(agent)
