"""M12 Phase 3 Tests: Rendering Orchestration, Planner, and M6 Agents.

Tests for:
1. RenderStage and RenderFailure domain models
2. RenderingPlanner and DAG generation
3. M6 rendering agents
4. Agent registry
5. Rendering events and metrics
6. Retry handling and failure recovery
"""

import pytest

from aura_backend.editing import EditPlan, Clip
from aura_backend.rendering import (
    # Phase 3
    RenderingPlanner,
    RenderingAgentRegistry,
    ClipRenderingAgent,
    CompositeRenderingAgent,
    ExportRenderingAgent,
    ValidationAgent,
    # Domain models
    RenderContext,
    MockRendererProvider,
)
from aura_backend.rendering.stages import (
    RenderStage,
    RenderFailure,
    StageType,
    FailureSeverity,
    RenderingStarted,
    StageCompleted,
    StageFailed,
    RenderingMetrics,
)


# ============================================================================
# DOMAIN MODEL TESTS
# ============================================================================


class TestRenderStage:
    """Test RenderStage domain model"""

    def test_render_stage_creation(self):
        """RenderStage can be created"""
        stage = RenderStage(
            job_id="job-1",
            stage_type=StageType.CLIP_RENDER,
        )

        assert stage.job_id == "job-1"
        assert stage.stage_type == StageType.CLIP_RENDER

    def test_render_stage_immutable(self):
        """RenderStage is immutable"""
        stage = RenderStage()

        with pytest.raises(AttributeError):
            stage.job_id = "new-job"

    def test_render_stage_dependencies(self):
        """RenderStage tracks dependencies"""
        stage = RenderStage(
            depends_on=["stage-1", "stage-2"],
        )

        assert len(stage.depends_on) == 2

    def test_render_stage_to_dict(self):
        """RenderStage can serialize"""
        stage = RenderStage(
            job_id="job-1",
            stage_type=StageType.EXPORT,
        )

        d = stage.to_dict()
        assert d["job_id"] == "job-1"
        assert d["stage_type"] == "export"


class TestRenderFailure:
    """Test RenderFailure domain model"""

    def test_render_failure_creation(self):
        """RenderFailure can be created"""
        failure = RenderFailure(
            stage_id="stage-1",
            stage_type=StageType.EXPORT,
            provider_name="ffmpeg",
            error_message="Export failed",
        )

        assert failure.stage_id == "stage-1"
        assert failure.is_recoverable

    def test_render_failure_immutable(self):
        """RenderFailure is immutable"""
        failure = RenderFailure()

        with pytest.raises(AttributeError):
            failure.retry_count = 5

    def test_render_failure_retry_handling(self):
        """RenderFailure tracks retry state"""
        failure = RenderFailure(
            stage_id="stage-1",
            retry_count=2,
            fallback_provider="mock",
            can_use_fallback=True,
        )

        assert failure.retry_count == 2
        assert failure.can_use_fallback


# ============================================================================
# RENDERING PLANNER TESTS
# ============================================================================


class TestRenderingPlanner:
    """Test RenderingPlanner"""

    def test_planner_initialization(self):
        """RenderingPlanner can be initialized"""
        planner = RenderingPlanner()

        assert planner is not None

    def test_planner_creates_stage_dag_simple(self):
        """Planner creates stage DAG from EditPlan"""
        planner = RenderingPlanner()
        context = RenderContext()

        clips = [
            Clip(session_id="s1", video_id="v1", start_timestamp=0.0, end_timestamp=5.0),
        ]
        plan = EditPlan(clips=clips)

        stages = planner.create_stage_dag(plan, context)

        assert len(stages) > 0
        assert stages[0].stage_type == StageType.CLIP_RENDER

    def test_planner_creates_dependencies(self):
        """Planner creates proper stage dependencies"""
        planner = RenderingPlanner()
        context = RenderContext()

        clips = [
            Clip(session_id="s1", video_id="v1", start_timestamp=0.0, end_timestamp=5.0),
        ]
        plan = EditPlan(clips=clips)

        stages = planner.create_stage_dag(plan, context)

        # Later stages should depend on earlier ones
        if len(stages) > 1:
            for i in range(1, len(stages)):
                assert len(stages[i].depends_on) > 0 or stages[i].stage_type == StageType.CLIP_RENDER

    def test_planner_respects_edit_plan_content(self):
        """Planner only creates stages for content in EditPlan"""
        planner = RenderingPlanner()
        context = RenderContext()

        # Plan with only clips
        clips = [
            Clip(session_id="s1", video_id="v1", start_timestamp=0.0, end_timestamp=5.0),
        ]
        plan_clips_only = EditPlan(clips=clips)
        stages_clips = planner.create_stage_dag(plan_clips_only, context)

        # Plan with clips and subtitles
        from aura_backend.editing import SubtitleSegment
        subtitles = [
            SubtitleSegment(
                session_id="s1",
                video_id="v1",
                start_timestamp=0.0,
                end_timestamp=2.0,
                text="Test",
            ),
        ]
        plan_with_subs = EditPlan(clips=clips, subtitles=subtitles)
        stages_subs = planner.create_stage_dag(plan_with_subs, context)

        # Plan with subtitles should have more stages
        assert len(stages_subs) > len(stages_clips)

    def test_planner_stages_to_m8_tasks(self):
        """Planner converts stages to M8 tasks"""
        planner = RenderingPlanner()
        context = RenderContext()

        clips = [
            Clip(session_id="s1", video_id="v1", start_timestamp=0.0, end_timestamp=5.0),
        ]
        plan = EditPlan(clips=clips)

        stages = planner.create_stage_dag(plan, context)
        tasks = planner.stages_to_m8_tasks(stages)

        assert len(tasks) == len(stages)
        assert all(t.metadata.get("stage_type") for t in tasks)


# ============================================================================
# M6 AGENT TESTS
# ============================================================================


class TestRenderingAgents:
    """Test M6 rendering agents"""

    def test_agent_initialization(self):
        """Rendering agents can be initialized"""
        provider = MockRendererProvider()
        from aura_backend.rendering.engines import ClipRenderer

        engine = ClipRenderer(provider)
        agent = ClipRenderingAgent(engine, "ClipRenderingAgent")

        assert agent.id is not None
        assert agent.name == "ClipRenderingAgent"

    def test_agent_capabilities(self):
        """Agents declare capabilities"""
        provider = MockRendererProvider()
        from aura_backend.rendering.engines import ClipRenderer

        engine = ClipRenderer(provider)
        agent = ClipRenderingAgent(engine, "ClipRenderingAgent")

        assert len(agent.capabilities) > 0

    @pytest.mark.asyncio
    async def test_agent_can_execute(self):
        """Agents can check task executability"""
        from aura_backend.orchestration.models import Task

        provider = MockRendererProvider()
        from aura_backend.rendering.engines import ClipRenderer

        engine = ClipRenderer(provider)
        agent = ClipRenderingAgent(engine, "ClipRenderingAgent")

        task = Task(
            metadata={"stage_type": "clip_render"},
        )

        result = await agent.can_execute(task)
        assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_agent_executes_task(self):
        """Agents can execute tasks"""
        from aura_backend.orchestration.models import Task

        provider = MockRendererProvider()
        from aura_backend.rendering.engines import ClipRenderer

        engine = ClipRenderer(provider)
        agent = ClipRenderingAgent(engine, "ClipRenderingAgent")

        task = Task(
            metadata={"stage_type": "clip_render"},
        )

        attempt = await agent.execute(task)

        assert attempt is not None
        assert attempt.task_id == task.id


# ============================================================================
# AGENT REGISTRY TESTS
# ============================================================================


class TestRenderingAgentRegistry:
    """Test RenderingAgentRegistry"""

    def test_registry_creation(self):
        """Registry can be created"""
        registry = RenderingAgentRegistry()

        assert registry is not None

    def test_registry_registration(self):
        """Agents can be registered"""
        provider = MockRendererProvider()
        from aura_backend.rendering.engines import ClipRenderer

        engine = ClipRenderer(provider)
        agent = ClipRenderingAgent(engine, "ClipRenderingAgent")

        registry = RenderingAgentRegistry()
        registry.register("clip", agent)

        retrieved = registry.get("clip")
        assert retrieved is not None

    def test_registry_list_agents(self):
        """Registry can list agents"""
        registry = RenderingAgentRegistry()
        provider = MockRendererProvider()
        from aura_backend.rendering.engines import (
            ClipRenderer,
            CompositeRenderer,
            ExportRenderer,
            ValidationEngine,
        )

        registry.register("clip", ClipRenderingAgent(ClipRenderer(provider), "Clip"))
        registry.register("composite", CompositeRenderingAgent(CompositeRenderer(provider), "Composite"))
        registry.register("export", ExportRenderingAgent(ExportRenderer(provider), "Export"))
        registry.register("validation", ValidationAgent(ValidationEngine(provider), "Validation"))

        agents = registry.list_agents()
        assert len(agents) == 4


# ============================================================================
# EVENT TESTS
# ============================================================================


class TestRenderingEvents:
    """Test rendering lifecycle events"""

    def test_rendering_started_event(self):
        """RenderingStarted event can be created"""
        event = RenderingStarted(
            job_id="job-1",
            stage_count=5,
        )

        assert event.event_type == "rendering_started"
        assert event.stage_count == 5

    def test_stage_completed_event(self):
        """StageCompleted event can be created"""
        event = StageCompleted(
            job_id="job-1",
            stage_type="clip_render",
            duration_seconds=10.5,
        )

        assert event.event_type == "stage_completed"
        assert event.duration_seconds == 10.5

    def test_stage_failed_event(self):
        """StageFailed event can be created with failure"""
        failure = RenderFailure(
            stage_id="s1",
            error_message="Export failed",
        )

        event = StageFailed(
            job_id="job-1",
            stage_type="export",
            failure=failure,
            will_retry=True,
        )

        assert event.event_type == "stage_failed"
        assert event.will_retry


# ============================================================================
# METRICS TESTS
# ============================================================================


class TestRenderingMetrics:
    """Test rendering metrics"""

    def test_metrics_creation(self):
        """RenderingMetrics can be created"""
        metrics = RenderingMetrics(
            job_id="job-1",
            total_duration_seconds=120.0,
            stages_completed=8,
            validation_passed=True,
        )

        assert metrics.job_id == "job-1"
        assert metrics.validation_passed

    def test_metrics_immutable(self):
        """RenderingMetrics is immutable"""
        metrics = RenderingMetrics()

        with pytest.raises(AttributeError):
            metrics.total_duration_seconds = 200.0


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestPhase3Integration:
    """Test Phase 3 components working together"""

    def test_planner_to_agent_workflow(self):
        """Planner output works with agent registry"""
        planner = RenderingPlanner()
        context = RenderContext()

        clips = [
            Clip(session_id="s1", video_id="v1", start_timestamp=0.0, end_timestamp=5.0),
        ]
        plan = EditPlan(clips=clips)

        stages = planner.create_stage_dag(plan, context)
        tasks = planner.stages_to_m8_tasks(stages)

        assert len(tasks) == len(stages)
        assert all(t.metadata.get("stage_type") for t in tasks)

    def test_events_and_metrics_tracking(self):
        """Events and metrics can be created together"""
        start_event = RenderingStarted(job_id="job-1", stage_count=5)
        complete_event = StageCompleted(
            job_id="job-1",
            stage_type="export",
            duration_seconds=15.0,
        )
        metrics = RenderingMetrics(
            job_id="job-1",
            total_duration_seconds=45.0,
            stages_completed=5,
        )

        assert start_event.job_id == metrics.job_id
        assert complete_event.job_id == metrics.job_id


# ============================================================================
# FAILURE RECOVERY TESTS
# ============================================================================


class TestFailureRecovery:
    """Test failure handling and recovery"""

    def test_failure_is_recoverable(self):
        """Failure can be marked as recoverable"""
        failure = RenderFailure(
            stage_id="s1",
            is_recoverable=True,
            retry_count=1,
            max_retries=3,
            fallback_provider="mock",
            can_use_fallback=True,
        )

        assert failure.is_recoverable
        assert failure.retry_count < 3  # Can retry
        assert failure.can_use_fallback

    def test_failure_fallback_provider(self):
        """Failure tracks fallback provider"""
        failure = RenderFailure(
            stage_id="s1",
            provider_name="ffmpeg",
            fallback_provider="moviepy",
            can_use_fallback=True,
        )

        assert failure.fallback_provider == "moviepy"
        assert failure.can_use_fallback
