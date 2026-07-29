"""M12 Phase 3: Rendering Orchestration - Planner and M6 Agents.

RenderingPlanner converts EditPlan to RenderStage DAG.
M6 agents wrap each rendering engine for M8 execution.
"""

from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

from aura_backend.editing import EditPlan
from aura_backend.orchestration.models import Capability, Skill, Task, TaskAttempt, ExecutionStatus, ToolRequirement
from aura_backend.orchestration.registry import ExecutableAgent

from .context import RenderContext, RenderCapability
from .engines import RenderingEngine
from .stages import RenderStage, StageType


# ============================================================================
# RENDERING PLANNER
# ============================================================================


class RenderingPlanner:
    """Converts EditPlan into RenderStage DAG for M8 execution."""

    def create_stage_dag(
        self,
        edit_plan: EditPlan,
        context: RenderContext,
        job_id: str = "",
    ) -> List[RenderStage]:
        """Convert EditPlan to ordered RenderStage list.

        Creates stages with proper dependencies.
        """
        stages = []
        job_id = job_id or str(uuid4())

        # Stage 1: Render clips (parallel if multiple)
        if edit_plan.clips:
            clip_stage = RenderStage(
                job_id=job_id,
                stage_type=StageType.CLIP_RENDER,
                estimated_duration_seconds=len(edit_plan.clips) * 2.0,
                priority=100,
                output_path=f"{context.working_path}/clips",
                preferred_provider=context.provider_name,
            )
            stages.append(clip_stage)

        # Stage 2: Composite (depends on clips)
        if edit_plan.clips and edit_plan.timeline:
            composite_stage = RenderStage(
                job_id=job_id,
                stage_type=StageType.COMPOSITE,
                depends_on=[stages[-1].stage_id] if stages else [],
                estimated_duration_seconds=5.0,
                priority=90,
                output_path=f"{context.working_path}/composited.mp4",
                preferred_provider=context.provider_name,
            )
            stages.append(composite_stage)

        # Parallel stages after composite
        prev_stage_id = stages[-1].stage_id if stages else ""

        if edit_plan.subtitles:
            sub_stage = RenderStage(
                job_id=job_id,
                stage_type=StageType.SUBTITLE,
                depends_on=[prev_stage_id] if prev_stage_id else [],
                estimated_duration_seconds=3.0,
                priority=80,
                output_path=f"{context.working_path}/subtitled.mp4",
                preferred_provider=context.provider_name,
            )
            stages.append(sub_stage)

        if edit_plan.overlays:
            overlay_stage = RenderStage(
                job_id=job_id,
                stage_type=StageType.OVERLAY,
                depends_on=[prev_stage_id] if prev_stage_id else [],
                estimated_duration_seconds=2.0,
                priority=75,
                output_path=f"{context.working_path}/overlaid.mp4",
                preferred_provider=context.provider_name,
            )
            stages.append(overlay_stage)

        if edit_plan.zoom_actions:
            zoom_stage = RenderStage(
                job_id=job_id,
                stage_type=StageType.ZOOM,
                depends_on=[prev_stage_id] if prev_stage_id else [],
                estimated_duration_seconds=2.0,
                priority=75,
                output_path=f"{context.working_path}/zoomed.mp4",
                preferred_provider=context.provider_name,
            )
            stages.append(zoom_stage)

        if edit_plan.broll_suggestions:
            broll_stage = RenderStage(
                job_id=job_id,
                stage_type=StageType.BROLL,
                depends_on=[prev_stage_id] if prev_stage_id else [],
                estimated_duration_seconds=3.0,
                priority=70,
                output_path=f"{context.working_path}/broll_inserted.mp4",
                preferred_provider=context.provider_name,
            )
            stages.append(broll_stage)

        if edit_plan.music_suggestions:
            audio_stage = RenderStage(
                job_id=job_id,
                stage_type=StageType.AUDIO,
                depends_on=[prev_stage_id] if prev_stage_id else [],
                estimated_duration_seconds=2.0,
                priority=70,
                output_path=f"{context.working_path}/with_audio.mp4",
                preferred_provider=context.provider_name,
            )
            stages.append(audio_stage)

        # Export (depends on final video)
        final_stage_id = stages[-1].stage_id if stages else ""
        export_stage = RenderStage(
            job_id=job_id,
            stage_type=StageType.EXPORT,
            depends_on=[final_stage_id] if final_stage_id else [],
            estimated_duration_seconds=3.0,
            priority=50,
            output_path=f"{context.output_path}/video.mp4",
            preferred_provider=context.provider_name,
        )
        stages.append(export_stage)

        # Validation (depends on export)
        validate_stage = RenderStage(
            job_id=job_id,
            stage_type=StageType.VALIDATE,
            depends_on=[export_stage.stage_id],
            estimated_duration_seconds=1.0,
            priority=40,
            preferred_provider=context.provider_name,
        )
        stages.append(validate_stage)

        return stages

    def stages_to_m8_tasks(
        self,
        stages: List[RenderStage],
    ) -> List[Task]:
        """Convert RenderStages to M8 Task objects."""
        tasks = []

        for stage in stages:
            task = Task(
                goal=f"Execute {stage.stage_type.value}",
                description=f"Rendering stage: {stage.stage_type.value}",
                priority=stage.priority,
                required_capabilities={Capability.ANALYSIS},
                metadata={
                    "stage_id": stage.stage_id,
                    "stage_type": stage.stage_type.value,
                    "preferred_provider": stage.preferred_provider,
                    "depends_on": stage.depends_on,
                },
            )
            tasks.append(task)

        return tasks


# ============================================================================
# M6 RENDERING AGENTS
# ============================================================================


class RenderingAgentBase(ExecutableAgent):
    """Base class for M6 rendering agents."""

    def __init__(self, engine: RenderingEngine, agent_name: str):
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
        return {Capability.ANALYSIS}

    @property
    def skills(self) -> Set[Skill]:
        return {Skill.CODE_EXECUTION}

    @property
    def tool_requirements(self) -> Set[ToolRequirement]:
        return set()

    async def can_execute(self, task: Task) -> bool:
        """Check if agent can execute task"""
        engine_type = task.metadata.get("stage_type", "").lower()
        agent_type = self.name.lower().replace("agent", "").replace("rendering", "")
        return engine_type.startswith(agent_type) or agent_type in engine_type

    async def execute(self, task: Task) -> TaskAttempt:
        """Execute rendering task (stub)"""
        try:
            return TaskAttempt(
                task_id=task.id,
                status=ExecutionStatus.COMPLETED,
                assigned_agent_id=self.id,
                result=f"Rendered {task.metadata.get('stage_type')}",
            )
        except Exception as e:
            return TaskAttempt(
                task_id=task.id,
                status=ExecutionStatus.FAILED,
                assigned_agent_id=self.id,
                error=str(e),
            )

    async def cancel(self, attempt_id: str) -> bool:
        return True


class ClipRenderingAgent(RenderingAgentBase):
    """M6 agent for ClipRenderer"""
    pass


class TransitionRenderingAgent(RenderingAgentBase):
    """M6 agent for TransitionRenderer"""
    pass


class SubtitleRenderingAgent(RenderingAgentBase):
    """M6 agent for SubtitleRenderer"""
    pass


class OverlayRenderingAgent(RenderingAgentBase):
    """M6 agent for OverlayRenderer"""
    pass


class ZoomRenderingAgent(RenderingAgentBase):
    """M6 agent for ZoomRenderer"""
    pass


class BrollRenderingAgent(RenderingAgentBase):
    """M6 agent for BrollRenderer"""
    pass


class AudioRenderingAgent(RenderingAgentBase):
    """M6 agent for AudioRenderer"""
    pass


class CompositeRenderingAgent(RenderingAgentBase):
    """M6 agent for CompositeRenderer"""
    pass


class ExportRenderingAgent(RenderingAgentBase):
    """M6 agent for ExportRenderer"""
    pass


class ValidationAgent(RenderingAgentBase):
    """M6 agent for ValidationEngine"""
    pass


# ============================================================================
# AGENT REGISTRY
# ============================================================================


class RenderingAgentRegistry:
    """Registry of M6 rendering agents for M8."""

    def __init__(self):
        self._agents: Dict[str, ExecutableAgent] = {}

    def register(self, name: str, agent: ExecutableAgent) -> None:
        """Register an agent"""
        self._agents[name] = agent

    def get(self, name: str) -> Optional[ExecutableAgent]:
        """Get agent by name"""
        return self._agents.get(name)

    def list_agents(self) -> List[str]:
        """List all registered agents"""
        return list(self._agents.keys())


def create_default_rendering_agent_registry(
    engines: Dict[str, RenderingEngine]
) -> RenderingAgentRegistry:
    """Factory for creating default agent registry"""
    registry = RenderingAgentRegistry()

    # Create agents for each engine
    if "clips" in engines:
        registry.register("clip", ClipRenderingAgent(engines["clips"], "ClipRenderingAgent"))
    if "transitions" in engines:
        registry.register("transition", TransitionRenderingAgent(engines["transitions"], "TransitionRenderingAgent"))
    if "subtitles" in engines:
        registry.register("subtitle", SubtitleRenderingAgent(engines["subtitles"], "SubtitleRenderingAgent"))
    if "overlays" in engines:
        registry.register("overlay", OverlayRenderingAgent(engines["overlays"], "OverlayRenderingAgent"))
    if "zoom" in engines:
        registry.register("zoom", ZoomRenderingAgent(engines["zoom"], "ZoomRenderingAgent"))
    if "broll" in engines:
        registry.register("broll", BrollRenderingAgent(engines["broll"], "BrollRenderingAgent"))
    if "audio" in engines:
        registry.register("audio", AudioRenderingAgent(engines["audio"], "AudioRenderingAgent"))
    if "composite" in engines:
        registry.register("composite", CompositeRenderingAgent(engines["composite"], "CompositeRenderingAgent"))
    if "export" in engines:
        registry.register("export", ExportRenderingAgent(engines["export"], "ExportRenderingAgent"))
    if "validation" in engines:
        registry.register("validation", ValidationAgent(engines["validation"], "ValidationAgent"))

    return registry
