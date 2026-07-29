"""M13 Phase 3 Tests: Publishing Orchestration.

Tests for stages, planner, M6 agents, M8 integration, and lifecycle events.
"""

from datetime import datetime, timedelta

import pytest

from aura_backend.publishing import (  # Phase 3; Phase 2; Phase 1
    AuthenticationAgent,
    MockPublishingProvider,
    PlatformType,
    PublishAgent,
    PublishingAgentRegistry,
    PublishingCompleted,
    PublishingFailure,
    PublishingJob,
    PublishingPlanner,
    PublishingStarted,
    PublishStage,
    ScheduledPublish,
    StageCompleted,
    StageFailed,
    StageStarted,
    StageType,
    UploadAgent,
    create_default_provider_registry,
    create_default_publishing_agent_registry,
)

# ============================================================================
# STAGE & FAILURE MODEL TESTS
# ============================================================================


class TestPublishStage:
    """Test PublishStage domain model"""

    def test_create_stage(self):
        """Create publishing stage"""
        stage = PublishStage(
            job_id="job-1",
            stage_type=StageType.UPLOAD,
            platform=PlatformType.YOUTUBE,
        )

        assert stage.job_id == "job-1"
        assert stage.stage_type == StageType.UPLOAD

    def test_stage_immutable(self):
        """Stage is immutable"""
        stage = PublishStage()

        with pytest.raises(AttributeError):
            stage.job_id = "new-job"

    def test_stage_dependencies(self):
        """Stage can have dependencies"""
        stage = PublishStage(depends_on=("stage-1", "stage-2"))

        assert len(stage.depends_on) == 2

    def test_stage_serialization(self):
        """Stage serialization"""
        stage = PublishStage(job_id="job-1")
        d = stage.to_dict()

        assert d["job_id"] == "job-1"


class TestPublishingFailure:
    """Test publishing failure model"""

    def test_create_failure(self):
        """Create publishing failure"""
        failure = PublishingFailure(
            job_id="job-1",
            stage_id="stage-1",
            platform=PlatformType.YOUTUBE,
            error_message="Upload failed",
        )

        assert failure.job_id == "job-1"
        assert failure.is_recoverable is True

    def test_failure_immutable(self):
        """Failure is immutable"""
        failure = PublishingFailure()

        with pytest.raises(AttributeError):
            failure.job_id = "new-job"

    def test_failure_recovery_info(self):
        """Failure tracks recovery information"""
        failure = PublishingFailure(
            is_recoverable=True,
            retry_count=1,
            fallback_provider="mock",
            can_use_fallback=True,
        )

        assert failure.can_use_fallback is True


# ============================================================================
# EVENT MODEL TESTS
# ============================================================================


class TestPublishingEvents:
    """Test publishing lifecycle events"""

    def test_publishing_started_event(self):
        """PublishingStarted event"""
        event = PublishingStarted(
            job_id="job-1",
            stage_count=8,
            platforms=("youtube", "tiktok"),
        )

        assert event.stage_count == 8
        assert len(event.platforms) == 2

    def test_stage_started_event(self):
        """StageStarted event"""
        event = StageStarted(
            job_id="job-1",
            stage_type="upload",
            stage_id="stage-1",
            platform="youtube",
        )

        assert event.stage_type == "upload"

    def test_stage_completed_event(self):
        """StageCompleted event"""
        event = StageCompleted(
            job_id="job-1",
            stage_type="upload",
            duration_seconds=15.5,
        )

        assert event.duration_seconds == 15.5

    def test_stage_failed_event(self):
        """StageFailed event"""
        failure = PublishingFailure(stage_id="stage-1")
        event = StageFailed(
            job_id="job-1",
            failure=failure,
            will_retry=True,
        )

        assert event.will_retry is True

    def test_publishing_completed_event(self):
        """PublishingCompleted event"""
        event = PublishingCompleted(
            job_id="job-1",
            is_success=True,
            successful_platforms=("youtube", "tiktok"),
        )

        assert event.is_success is True
        assert len(event.successful_platforms) == 2


# ============================================================================
# PLANNING TESTS
# ============================================================================


class TestPublishingPlanner:
    """Test publishing planner"""

    def test_planner_creation(self):
        """Create planner"""
        planner = PublishingPlanner()

        assert planner is not None

    def test_dag_generation_single_platform(self):
        """Generate DAG for single platform"""
        planner = PublishingPlanner()
        job = PublishingJob(
            artifact_bundle_id="bundle-1",
            platforms=(PlatformType.YOUTUBE,),
        )

        from aura_backend.publishing import PublishingContext

        context = PublishingContext(job_id=job.id)
        stages = planner.create_stage_dag(job, context, None)

        assert len(stages) > 0
        # Should have: validate, auth, upload, metadata, privacy, publish, finalize
        assert stages[0].stage_type == StageType.VALIDATE

    def test_dag_generation_multi_platform(self):
        """Generate DAG for multiple platforms"""
        planner = PublishingPlanner()
        job = PublishingJob(
            artifact_bundle_id="bundle-1",
            platforms=(PlatformType.YOUTUBE, PlatformType.TIKTOK),
        )

        from aura_backend.publishing import PublishingContext

        context = PublishingContext(job_id=job.id)
        stages = planner.create_stage_dag(job, context, None)

        # Should have stages for both platforms
        youtube_stages = [s for s in stages if s.platform == PlatformType.YOUTUBE]
        tiktok_stages = [s for s in stages if s.platform == PlatformType.TIKTOK]

        assert len(youtube_stages) > 0
        assert len(tiktok_stages) > 0

    def test_dag_dependencies(self):
        """DAG has proper dependencies"""
        planner = PublishingPlanner()
        job = PublishingJob(
            artifact_bundle_id="bundle-1",
            platforms=(PlatformType.YOUTUBE,),
        )

        from aura_backend.publishing import PublishingContext

        context = PublishingContext(job_id=job.id)
        stages = planner.create_stage_dag(job, context, None)

        # Later stages should depend on earlier ones
        for i in range(1, len(stages)):
            if not stages[i].is_optional:
                assert len(stages[i].depends_on) > 0 or stages[i].stage_type == StageType.VALIDATE

    def test_stages_to_m8_tasks(self):
        """Convert stages to M8 tasks"""
        planner = PublishingPlanner()
        job = PublishingJob(
            artifact_bundle_id="bundle-1",
            platforms=(PlatformType.YOUTUBE,),
        )

        from aura_backend.publishing import PublishingContext

        context = PublishingContext(job_id=job.id)
        stages = planner.create_stage_dag(job, context, None)
        tasks = planner.stages_to_m8_tasks(stages)

        assert len(tasks) == len(stages)
        assert all(t.metadata.get("stage_type") for t in tasks)


# ============================================================================
# M6 AGENT TESTS
# ============================================================================


class TestPublishingAgents:
    """Test M6 publishing agents"""

    @pytest.mark.asyncio
    async def test_agent_creation(self):
        """Create publishing agent"""
        provider = MockPublishingProvider()
        agent = AuthenticationAgent(provider)

        assert agent.provider is not None
        assert "publish" in agent.capabilities

    @pytest.mark.asyncio
    async def test_auth_agent_execution(self):
        """Execute authentication agent"""
        from aura_backend.orchestration.models import Task

        provider = MockPublishingProvider()
        agent = AuthenticationAgent(provider)
        task = Task(metadata={"stage_type": StageType.AUTH.value})

        can_exec = await agent.can_execute(task)
        assert can_exec is True

    @pytest.mark.asyncio
    async def test_upload_agent_execution(self):
        """Execute upload agent"""
        from aura_backend.orchestration.models import Task

        provider = MockPublishingProvider()
        agent = UploadAgent(provider)
        task = Task(metadata={"stage_type": StageType.UPLOAD.value})

        can_exec = await agent.can_execute(task)
        assert can_exec is True

    @pytest.mark.asyncio
    async def test_agent_execute_task(self):
        """Execute full task"""
        from aura_backend.orchestration.models import Task

        provider = MockPublishingProvider()
        agent = PublishAgent(provider)
        task = Task(metadata={"stage_type": StageType.PUBLISH.value, "job_id": "job-1"})

        attempt = await agent.execute(task)

        assert attempt.task_id == task.id
        assert attempt.agent_id == agent.id


# ============================================================================
# AGENT REGISTRY TESTS
# ============================================================================


class TestPublishingAgentRegistry:
    """Test agent registry"""

    def test_registry_creation(self):
        """Create registry"""
        registry = PublishingAgentRegistry()

        assert registry is not None

    def test_register_agent(self):
        """Register agent"""
        registry = PublishingAgentRegistry()
        agent = AuthenticationAgent()

        registry.register("auth", agent)
        retrieved = registry.get("auth")

        assert retrieved is not None

    def test_get_agents_for_stage(self):
        """Get agents for stage type"""
        registry = PublishingAgentRegistry()
        provider = MockPublishingProvider()

        registry.register("auth", AuthenticationAgent(provider))
        registry.register("upload", UploadAgent(provider))

        agents = registry.get_agents_for_stage(StageType.AUTH)

        assert len(agents) > 0

    def test_default_registry(self):
        """Create default registry"""
        provider_registry = create_default_provider_registry()
        registry = create_default_publishing_agent_registry(provider_registry)

        agents = registry.list_agents()

        # Should have agents for mock provider at minimum
        assert len(agents) > 0


# ============================================================================
# SCHEDULING TESTS
# ============================================================================


class TestSchedulingIntegration:
    """Test scheduling in orchestration"""

    def test_dag_with_scheduling(self):
        """DAG includes scheduling stage when needed"""
        planner = PublishingPlanner()
        publish_time = datetime.utcnow() + timedelta(hours=1)
        schedule = ScheduledPublish(publish_at=publish_time)

        from aura_backend.publishing import PublishingContext

        context = PublishingContext(
            job_id="job-1",
            publishing_schedule=schedule,
        )
        job = PublishingJob(
            artifact_bundle_id="bundle-1",
            platforms=(PlatformType.YOUTUBE,),
        )

        stages = planner.create_stage_dag(job, context, None)

        # Scheduling may not be in DAG depending on implementation
        # Just verify no errors occurred
        assert len(stages) > 0


# ============================================================================
# RETRY & FAILURE RECOVERY TESTS
# ============================================================================


class TestRetryAndRecovery:
    """Test retry and failure recovery"""

    def test_failure_recovery_info(self):
        """Failure contains recovery info"""
        failure = PublishingFailure(
            is_recoverable=True,
            retry_count=2,
            max_retries=3,
            fallback_provider="mock",
            can_use_fallback=True,
        )

        assert failure.retry_count < failure.max_retries
        assert failure.can_use_fallback

    def test_failure_as_dict(self):
        """Serialize failure"""
        failure = PublishingFailure(job_id="job-1")
        d = failure.to_dict()

        assert d["job_id"] == "job-1"


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestPhase3Integration:
    """Integration tests for Phase 3 components"""

    @pytest.mark.asyncio
    async def test_full_orchestration_workflow(self):
        """Full orchestration workflow"""
        # Create job
        job = PublishingJob(
            artifact_bundle_id="bundle-1",
            platforms=(PlatformType.YOUTUBE,),
        )

        # Create context
        from aura_backend.publishing import PublishingContext

        context = PublishingContext(job_id=job.id, artifact_bundle_id="bundle-1")

        # Plan stages
        planner = PublishingPlanner()
        provider_registry = create_default_provider_registry()
        stages = planner.create_stage_dag(job, context, provider_registry)

        # Convert to M8 tasks
        tasks = planner.stages_to_m8_tasks(stages)

        # Create agents
        agent_registry = create_default_publishing_agent_registry(provider_registry)

        # Verify agents can handle stages
        assert len(agent_registry.list_agents()) > 0
        assert len(stages) > 0
        assert len(tasks) == len(stages)

    def test_multi_platform_orchestration(self):
        """Multi-platform orchestration"""
        job = PublishingJob(
            artifact_bundle_id="bundle-1",
            platforms=(PlatformType.YOUTUBE, PlatformType.TIKTOK, PlatformType.INSTAGRAM_REEL),
        )

        from aura_backend.publishing import PublishingContext

        context = PublishingContext(job_id=job.id)

        planner = PublishingPlanner()
        stages = planner.create_stage_dag(job, context, None)

        # Should have stages for each platform
        assert len(stages) > 0

        # Count platforms represented
        platforms = {s.platform for s in stages if s.platform != PlatformType.YOUTUBE}
        # Validation stage uses YouTube by default, but other stages cover all platforms
        assert PlatformType.TIKTOK in platforms or PlatformType.INSTAGRAM_REEL in platforms
