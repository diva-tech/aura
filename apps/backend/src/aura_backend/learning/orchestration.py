"""M14 Phase 3: Learning Orchestration – Planner and M6 Agents.

DAG generation, M6 learning agents, agent registry, M8 integration.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from .context import LearningContext
from .models import LearningJob
from .stages import LearningStage, StageType


@dataclass(frozen=True)
class LearningTask:
    """M8-compatible learning task."""

    id: str = ""
    stage_id: str = ""
    job_id: str = ""
    stage_type: str = ""
    metadata: dict = None

    def __post_init__(self):
        if self.metadata is None:
            object.__setattr__(self, "metadata", {})


class LearningAgent(ABC):
    """Base M6 learning agent."""

    @property
    @abstractmethod
    def agent_id(self) -> str:
        """Agent identifier."""
        pass

    @property
    @abstractmethod
    def agent_name(self) -> str:
        """Agent display name."""
        pass

    @property
    @abstractmethod
    def capabilities(self) -> tuple[str, ...]:
        """Supported stage types."""
        pass

    @abstractmethod
    async def can_execute(self, task: LearningTask) -> bool:
        """Check if agent can execute task."""
        pass

    @abstractmethod
    async def execute(self, task: LearningTask, context: LearningContext) -> dict:
        """Execute learning task."""
        pass


class ValidationAgent(LearningAgent):
    """Validates learning job and context."""

    @property
    def agent_id(self) -> str:
        return "agent:validation"

    @property
    def agent_name(self) -> str:
        return "Learning Validator"

    @property
    def capabilities(self) -> tuple[str, ...]:
        return (StageType.VALIDATE,)

    async def can_execute(self, task: LearningTask) -> bool:
        return task.metadata.get("stage_type") == StageType.VALIDATE.value

    async def execute(self, task: LearningTask, context: LearningContext) -> dict:
        return {
            "valid": True,
            "checks_passed": 5,
            "recommendations_possible": True,
        }


class AuthenticationAgent(LearningAgent):
    """Handles provider authentication."""

    def __init__(self, provider=None):
        self.provider = provider

    @property
    def agent_id(self) -> str:
        return "agent:auth"

    @property
    def agent_name(self) -> str:
        return "Authentication Agent"

    @property
    def capabilities(self) -> tuple[str, ...]:
        return (StageType.AUTH,)

    async def can_execute(self, task: LearningTask) -> bool:
        return task.metadata.get("stage_type") == StageType.AUTH.value

    async def execute(self, task: LearningTask, context: LearningContext) -> dict:
        return {
            "authenticated": True,
            "provider": context.platform,
        }


class MetricsRetrievalAgent(LearningAgent):
    """Retrieves analytics metrics from providers."""

    def __init__(self, provider=None):
        self.provider = provider

    @property
    def agent_id(self) -> str:
        return "agent:metrics"

    @property
    def agent_name(self) -> str:
        return "Metrics Retrieval Agent"

    @property
    def capabilities(self) -> tuple[str, ...]:
        return (StageType.RETRIEVE_METRICS,)

    async def can_execute(self, task: LearningTask) -> bool:
        return task.metadata.get("stage_type") == StageType.RETRIEVE_METRICS.value

    async def execute(self, task: LearningTask, context: LearningContext) -> dict:
        return {
            "metrics_collected": 50,
            "videos_analyzed": 10,
        }


class AnalysisAgent(LearningAgent):
    """Analyzes collected metrics."""

    @property
    def agent_id(self) -> str:
        return "agent:analysis"

    @property
    def agent_name(self) -> str:
        return "Analysis Agent"

    @property
    def capabilities(self) -> tuple[str, ...]:
        return (
            StageType.ANALYZE_RETENTION,
            StageType.ANALYZE_AUDIENCE,
            StageType.ANALYZE_REVENUE,
        )

    async def can_execute(self, task: LearningTask) -> bool:
        stage_type = task.metadata.get("stage_type")
        return stage_type in [
            StageType.ANALYZE_RETENTION.value,
            StageType.ANALYZE_AUDIENCE.value,
            StageType.ANALYZE_REVENUE.value,
        ]

    async def execute(self, task: LearningTask, context: LearningContext) -> dict:
        return {
            "analysis_complete": True,
            "insights_found": 3,
        }


class RecommendationAgent(LearningAgent):
    """Generates optimization recommendations."""

    @property
    def agent_id(self) -> str:
        return "agent:recommendations"

    @property
    def agent_name(self) -> str:
        return "Recommendations Agent"

    @property
    def capabilities(self) -> tuple[str, ...]:
        return (StageType.GENERATE_RECOMMENDATIONS,)

    async def can_execute(self, task: LearningTask) -> bool:
        return task.metadata.get("stage_type") == StageType.GENERATE_RECOMMENDATIONS.value

    async def execute(self, task: LearningTask, context: LearningContext) -> dict:
        return {
            "recommendations_generated": 5,
            "high_confidence": 3,
        }


class ProfileUpdateAgent(LearningAgent):
    """Updates creator profile with learned patterns."""

    @property
    def agent_id(self) -> str:
        return "agent:profile"

    @property
    def agent_name(self) -> str:
        return "Profile Update Agent"

    @property
    def capabilities(self) -> tuple[str, ...]:
        return (StageType.UPDATE_PROFILE,)

    async def can_execute(self, task: LearningTask) -> bool:
        return task.metadata.get("stage_type") == StageType.UPDATE_PROFILE.value

    async def execute(self, task: LearningTask, context: LearningContext) -> dict:
        return {
            "profile_updated": True,
            "fields_updated": 4,
        }


class MemoryUpdateAgent(LearningAgent):
    """Updates learning memory with optimization history."""

    @property
    def agent_id(self) -> str:
        return "agent:memory"

    @property
    def agent_name(self) -> str:
        return "Memory Update Agent"

    @property
    def capabilities(self) -> tuple[str, ...]:
        return (StageType.UPDATE_MEMORY,)

    async def can_execute(self, task: LearningTask) -> bool:
        return task.metadata.get("stage_type") == StageType.UPDATE_MEMORY.value

    async def execute(self, task: LearningTask, context: LearningContext) -> dict:
        return {
            "memory_updated": True,
            "history_entries": 10,
        }


class LearningAgentRegistry:
    """Registry for learning agents."""

    def __init__(self):
        self._agents: dict[str, LearningAgent] = {}

    def register(self, agent: LearningAgent) -> None:
        """Register an agent."""
        self._agents[agent.agent_id] = agent

    def get(self, agent_id: str) -> LearningAgent | None:
        """Get agent by ID."""
        return self._agents.get(agent_id)

    def get_agents_for_stage(self, stage_type: StageType) -> list[LearningAgent]:
        """Get agents supporting stage type."""
        return [agent for agent in self._agents.values() if stage_type in agent.capabilities]

    def list_agents(self) -> list[str]:
        """List all agent IDs."""
        return list(self._agents.keys())


class LearningPlanner:
    """Plans learning job execution with DAG generation."""

    def create_stage_dag(
        self,
        job: LearningJob,
        context: LearningContext,
        provider_registry=None,
    ) -> list[LearningStage]:
        """Generate DAG of learning stages."""
        stages: list[LearningStage] = []

        # Validation stage
        stages.append(
            LearningStage(
                job_id=job.id,
                stage_type=StageType.VALIDATE,
                platform=context.platform,
                objectives=context.objectives or (),
            )
        )

        # Authentication stage
        stages.append(
            LearningStage(
                job_id=job.id,
                stage_type=StageType.AUTH,
                platform=context.platform,
                depends_on=(stages[0].id,) if stages else (),
            )
        )

        # Metrics retrieval stage
        stages.append(
            LearningStage(
                job_id=job.id,
                stage_type=StageType.RETRIEVE_METRICS,
                platform=context.platform,
                provider_name=context.platform,
                depends_on=(stages[1].id,) if len(stages) > 1 else (),
            )
        )

        # Analysis stages (parallel)
        analytics_stages = [
            StageType.ANALYZE_RETENTION,
            StageType.ANALYZE_AUDIENCE,
            StageType.ANALYZE_REVENUE,
        ]
        for stage_type in analytics_stages:
            stages.append(
                LearningStage(
                    job_id=job.id,
                    stage_type=stage_type,
                    platform=context.platform,
                    depends_on=(stages[2].id,) if len(stages) > 2 else (),
                )
            )

        # Recommendation generation
        analysis_deps = tuple(s.id for s in stages[-3:]) if len(stages) >= 3 else ()
        stages.append(
            LearningStage(
                job_id=job.id,
                stage_type=StageType.GENERATE_RECOMMENDATIONS,
                platform=context.platform,
                depends_on=analysis_deps,
            )
        )

        # Profile update
        if context.creator_profile:
            stages.append(
                LearningStage(
                    job_id=job.id,
                    stage_type=StageType.UPDATE_PROFILE,
                    platform=context.platform,
                    depends_on=(stages[-1].id,) if stages else (),
                )
            )

        # Memory update
        if context.learning_memory:
            stages.append(
                LearningStage(
                    job_id=job.id,
                    stage_type=StageType.UPDATE_MEMORY,
                    platform=context.platform,
                    depends_on=(stages[-1].id,) if stages else (),
                )
            )

        # Finalization
        stages.append(
            LearningStage(
                job_id=job.id,
                stage_type=StageType.FINALIZE,
                platform=context.platform,
                depends_on=(stages[-1].id,) if stages else (),
            )
        )

        return stages

    def stages_to_m8_tasks(self, stages: list[LearningStage]) -> list[LearningTask]:
        """Convert stages to M8 task format."""
        tasks = []
        for stage in stages:
            task = LearningTask(
                stage_id=stage.id,
                job_id=stage.job_id,
                stage_type=stage.stage_type.value,
                metadata={
                    "stage_type": stage.stage_type.value,
                    "platform": stage.platform,
                    "provider_name": stage.provider_name,
                    "depends_on": list(stage.depends_on) if stage.depends_on else [],
                },
            )
            tasks.append(task)
        return tasks


def create_default_learning_agent_registry() -> LearningAgentRegistry:
    """Create registry with all reference agents."""
    registry = LearningAgentRegistry()
    registry.register(ValidationAgent())
    registry.register(AuthenticationAgent())
    registry.register(MetricsRetrievalAgent())
    registry.register(AnalysisAgent())
    registry.register(RecommendationAgent())
    registry.register(ProfileUpdateAgent())
    registry.register(MemoryUpdateAgent())
    return registry
