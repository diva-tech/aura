"""M13 Phase 3: Publishing Orchestration — Planner and M6 Agents.

DAG generation, M6 publishing agents, and M8 task integration.
"""

from abc import ABC, abstractmethod
from uuid import uuid4

from aura_backend.orchestration.models import Attempt, ExecutableAgent, Task

from .context import PublishingContext
from .models import PlatformType, PublishingJob
from .providers import ProviderRegistry, PublishingProvider
from .stages import PublishStage, StageType


class PublishingPlanner:
    """Converts PublishingJob → PublishStage DAG"""

    def create_stage_dag(
        self,
        job: PublishingJob,
        context: PublishingContext,
        provider_registry: ProviderRegistry,
    ) -> list[PublishStage]:
        """Create stage DAG from publishing job"""
        stages = []

        # 1. Validation stage (first, no dependencies)
        validate_stage = PublishStage(
            id=str(uuid4()),
            job_id=job.id,
            stage_type=StageType.VALIDATE,
            platform=list(job.platforms)[0] if job.platforms else PlatformType.YOUTUBE,
            depends_on=(),
        )
        stages.append(validate_stage)

        # For each platform, create platform-specific stages
        previous_stage_id = validate_stage.id
        for platform in job.platforms:
            # Authentication
            auth_stage = PublishStage(
                id=str(uuid4()),
                job_id=job.id,
                stage_type=StageType.AUTH,
                platform=platform,
                depends_on=(previous_stage_id,),
            )
            stages.append(auth_stage)
            previous_stage_id = auth_stage.id

            # Upload
            upload_stage = PublishStage(
                id=str(uuid4()),
                job_id=job.id,
                stage_type=StageType.UPLOAD,
                platform=platform,
                depends_on=(auth_stage.id,),
            )
            stages.append(upload_stage)

            # Thumbnail (optional)
            if context.create_thumbnail:
                thumbnail_stage = PublishStage(
                    id=str(uuid4()),
                    job_id=job.id,
                    stage_type=StageType.THUMBNAIL,
                    platform=platform,
                    depends_on=(upload_stage.id,),
                    is_optional=True,
                )
                stages.append(thumbnail_stage)
                previous_stage_id = thumbnail_stage.id
            else:
                previous_stage_id = upload_stage.id

            # Metadata
            metadata_stage = PublishStage(
                id=str(uuid4()),
                job_id=job.id,
                stage_type=StageType.METADATA,
                platform=platform,
                depends_on=(previous_stage_id,),
            )
            stages.append(metadata_stage)

            # Privacy
            privacy_stage = PublishStage(
                id=str(uuid4()),
                job_id=job.id,
                stage_type=StageType.PRIVACY,
                platform=platform,
                depends_on=(metadata_stage.id,),
            )
            stages.append(privacy_stage)

            # Scheduling (if needed)
            if context.publishing_schedule and not context.publishing_schedule.is_immediate():
                schedule_stage = PublishStage(
                    id=str(uuid4()),
                    job_id=job.id,
                    stage_type=StageType.SCHEDULE,
                    platform=platform,
                    depends_on=(privacy_stage.id,),
                    is_optional=True,
                )
                stages.append(schedule_stage)
                previous_stage_id = schedule_stage.id
            else:
                # Publish draft if not scheduling
                publish_stage = PublishStage(
                    id=str(uuid4()),
                    job_id=job.id,
                    stage_type=StageType.PUBLISH,
                    platform=platform,
                    depends_on=(privacy_stage.id,),
                )
                stages.append(publish_stage)
                previous_stage_id = publish_stage.id

            # Captions (optional)
            if context.generate_captions:
                captions_stage = PublishStage(
                    id=str(uuid4()),
                    job_id=job.id,
                    stage_type=StageType.CAPTIONS,
                    platform=platform,
                    depends_on=(previous_stage_id,),
                    is_optional=True,
                )
                stages.append(captions_stage)

        # Finalize stage (last, depends on all platform stages)
        finalize_stage = PublishStage(
            id=str(uuid4()),
            job_id=job.id,
            stage_type=StageType.FINALIZE,
            depends_on=(previous_stage_id,) if previous_stage_id else (),
        )
        stages.append(finalize_stage)

        return stages

    def stages_to_m8_tasks(self, stages: list[PublishStage]) -> list[Task]:
        """Convert stages to M8 tasks"""
        tasks = []
        for stage in stages:
            task = Task(
                id=stage.id,
                metadata={
                    "stage_id": stage.id,
                    "stage_type": stage.stage_type.value,
                    "platform": stage.platform.value,
                    "job_id": stage.job_id,
                },
            )
            tasks.append(task)
        return tasks


class PublishingAgent(ExecutableAgent, ABC):
    """Base publishing agent (M6)"""

    def __init__(self, provider: PublishingProvider | None = None, name: str = ""):
        super().__init__(id=str(uuid4()), name=name or self.__class__.__name__)
        self.provider = provider

    @property
    def capabilities(self) -> list[str]:
        if self.provider:
            return [
                "publish",
                "platform_" + self.provider.capabilities.platform.value,
            ]
        return ["publish"]

    @abstractmethod
    async def execute(self, task: Task) -> Attempt:
        """Execute publishing task"""


class AuthenticationAgent(PublishingAgent):
    """Authentication publishing agent"""

    async def can_execute(self, task: Task) -> bool:
        stage_type = task.metadata.get("stage_type")
        return stage_type == StageType.AUTH.value

    async def execute(self, task: Task) -> Attempt:
        attempt = Attempt(task_id=task.id, agent_id=self.id)
        if self.provider:
            try:
                context = PublishingContext(job_id=task.metadata.get("job_id", ""))
                result = await self.provider.authenticate(context)
                attempt.is_success = result
            except Exception as e:
                attempt.is_success = False
                attempt.error_message = str(e)
        return attempt


class UploadAgent(PublishingAgent):
    """Upload publishing agent"""

    async def can_execute(self, task: Task) -> bool:
        stage_type = task.metadata.get("stage_type")
        return stage_type == StageType.UPLOAD.value

    async def execute(self, task: Task) -> Attempt:
        attempt = Attempt(task_id=task.id, agent_id=self.id)
        if self.provider:
            try:
                context = PublishingContext(job_id=task.metadata.get("job_id", ""))
                response = await self.provider.upload_video(context)
                attempt.is_success = response.is_success
                attempt.output_data = {
                    "video_id": response.platform_video_id,
                    "url": response.platform_url,
                }
            except Exception as e:
                attempt.is_success = False
                attempt.error_message = str(e)
        return attempt


class MetadataAgent(PublishingAgent):
    """Metadata publishing agent"""

    async def can_execute(self, task: Task) -> bool:
        stage_type = task.metadata.get("stage_type")
        return stage_type == StageType.METADATA.value

    async def execute(self, task: Task) -> Attempt:
        attempt = Attempt(task_id=task.id, agent_id=self.id)
        if self.provider:
            try:
                context = PublishingContext(job_id=task.metadata.get("job_id", ""))
                result = await self.provider.set_metadata(context)
                attempt.is_success = result
            except Exception as e:
                attempt.is_success = False
                attempt.error_message = str(e)
        return attempt


class PublishAgent(PublishingAgent):
    """Publish publishing agent"""

    async def can_execute(self, task: Task) -> bool:
        stage_type = task.metadata.get("stage_type")
        return stage_type == StageType.PUBLISH.value

    async def execute(self, task: Task) -> Attempt:
        attempt = Attempt(task_id=task.id, agent_id=self.id)
        if self.provider:
            try:
                context = PublishingContext(job_id=task.metadata.get("job_id", ""))
                result = await self.provider.publish(context)
                attempt.is_success = result.is_success
            except Exception as e:
                attempt.is_success = False
                attempt.error_message = str(e)
        return attempt


class ThumbnailAgent(PublishingAgent):
    """Thumbnail publishing agent"""

    async def can_execute(self, task: Task) -> bool:
        stage_type = task.metadata.get("stage_type")
        return stage_type == StageType.THUMBNAIL.value

    async def execute(self, task: Task) -> Attempt:
        attempt = Attempt(task_id=task.id, agent_id=self.id)
        if self.provider:
            try:
                context = PublishingContext(job_id=task.metadata.get("job_id", ""))
                result = await self.provider.upload_thumbnail(context)
                attempt.is_success = result
            except Exception as e:
                attempt.is_success = False
                attempt.error_message = str(e)
        return attempt


class PrivacyAgent(PublishingAgent):
    """Privacy publishing agent"""

    async def can_execute(self, task: Task) -> bool:
        stage_type = task.metadata.get("stage_type")
        return stage_type == StageType.PRIVACY.value

    async def execute(self, task: Task) -> Attempt:
        attempt = Attempt(task_id=task.id, agent_id=self.id)
        if self.provider:
            try:
                context = PublishingContext(job_id=task.metadata.get("job_id", ""))
                result = await self.provider.set_privacy(context, "public")
                attempt.is_success = result
            except Exception as e:
                attempt.is_success = False
                attempt.error_message = str(e)
        return attempt


class ScheduleAgent(PublishingAgent):
    """Scheduling publishing agent"""

    async def can_execute(self, task: Task) -> bool:
        stage_type = task.metadata.get("stage_type")
        return stage_type == StageType.SCHEDULE.value

    async def execute(self, task: Task) -> Attempt:
        attempt = Attempt(task_id=task.id, agent_id=self.id)
        if self.provider:
            try:
                context = PublishingContext(job_id=task.metadata.get("job_id", ""))
                result = await self.provider.schedule_publish(context)
                attempt.is_success = result
            except Exception as e:
                attempt.is_success = False
                attempt.error_message = str(e)
        return attempt


class CaptionsAgent(PublishingAgent):
    """Captions publishing agent"""

    async def can_execute(self, task: Task) -> bool:
        stage_type = task.metadata.get("stage_type")
        return stage_type == StageType.CAPTIONS.value

    async def execute(self, task: Task) -> Attempt:
        attempt = Attempt(task_id=task.id, agent_id=self.id)
        if self.provider:
            try:
                context = PublishingContext(job_id=task.metadata.get("job_id", ""))
                result = await self.provider.generate_captions(context, "video_id")
                attempt.is_success = result
            except Exception as e:
                attempt.is_success = False
                attempt.error_message = str(e)
        return attempt


class PublishingAgentRegistry:
    """Registry for publishing M6 agents"""

    def __init__(self):
        self._agents: dict[str, PublishingAgent] = {}

    def register(self, name: str, agent: PublishingAgent) -> None:
        """Register an agent"""
        self._agents[name] = agent

    def get(self, name: str) -> PublishingAgent | None:
        """Get agent by name"""
        return self._agents.get(name)

    def list_agents(self) -> list[PublishingAgent]:
        """List all agents"""
        return list(self._agents.values())

    def get_agents_for_stage(self, stage_type: StageType) -> list[PublishingAgent]:
        """Get agents capable of executing stage type"""
        agents = []
        for agent in self._agents.values():
            if stage_type.value in agent.capabilities:
                agents.append(agent)
        return agents


def create_default_publishing_agent_registry(
    provider_registry: ProviderRegistry,
) -> PublishingAgentRegistry:
    """Create registry with built-in publishing agents"""
    registry = PublishingAgentRegistry()

    # Create agents for each provider
    for name, provider in provider_registry.list_providers().items():
        registry.register(f"auth_{name}", AuthenticationAgent(provider))
        registry.register(f"upload_{name}", UploadAgent(provider))
        registry.register(f"metadata_{name}", MetadataAgent(provider))
        registry.register(f"publish_{name}", PublishAgent(provider))
        registry.register(f"thumbnail_{name}", ThumbnailAgent(provider))
        registry.register(f"privacy_{name}", PrivacyAgent(provider))
        registry.register(f"schedule_{name}", ScheduleAgent(provider))
        registry.register(f"captions_{name}", CaptionsAgent(provider))

    return registry
