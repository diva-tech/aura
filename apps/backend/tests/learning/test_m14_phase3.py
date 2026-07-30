"""M14 Phase 3 Tests: Learning Orchestration.

Tests for stages, failures, DAG generation, agents, and events.
"""


import pytest

from aura_backend.learning import (
    AnalysisAgent,
    AuthenticationAgent,
    LearningAgentRegistry,
    LearningCompleted,
    LearningContext,
    LearningFailure,
    LearningJob,
    LearningPlanner,
    LearningStage,
    LearningStarted,
    M8LearningTask,
    MetricsRetrievalAgent,
    StageCompleted,
    StageFailed,
    StageStarted,
    StageType,
    ValidationAgent,
    create_default_learning_agent_registry,
)

# ============================================================================
# LEARNING STAGE TESTS
# ============================================================================


class TestLearningStage:
    """Test learning stage model."""

    def test_stage_creation(self):
        """Create learning stage."""
        stage = LearningStage(
            job_id="job-1",
            stage_type=StageType.VALIDATE,
            platform="youtube",
        )

        assert stage.job_id == "job-1"
        assert stage.stage_type == StageType.VALIDATE
        assert stage.id is not None

    def test_stage_immutable(self):
        """Stage is immutable."""
        stage = LearningStage()

        with pytest.raises(AttributeError):
            stage.job_id = "new-job"

    def test_stage_with_dependencies(self):
        """Stage can have dependencies."""
        stage = LearningStage(
            depends_on=("stage-1", "stage-2"),
        )

        assert len(stage.depends_on) == 2

    def test_stage_serialization(self):
        """Serialize stage."""
        stage = LearningStage(
            job_id="job-1",
            stage_type=StageType.AUTH,
        )

        d = stage.to_dict()

        assert d["job_id"] == "job-1"
        assert d["stage_type"] == "authenticate"


# ============================================================================
# LEARNING FAILURE TESTS
# ============================================================================


class TestLearningFailure:
    """Test learning failure model."""

    def test_failure_creation(self):
        """Create learning failure."""
        failure = LearningFailure(
            job_id="job-1",
            stage_id="stage-1",
            stage_type=StageType.RETRIEVE_METRICS,
            platform="youtube",
            error_message="Failed to retrieve metrics",
        )

        assert failure.job_id == "job-1"
        assert failure.is_recoverable is False

    def test_failure_with_recovery_info(self):
        """Failure with recovery information."""
        failure = LearningFailure(
            is_recoverable=True,
            retry_count=1,
            max_retries=3,
            fallback_provider="mock",
            can_use_fallback=True,
        )

        assert failure.retry_count < failure.max_retries
        assert failure.can_use_fallback is True


# ============================================================================
# LEARNING EVENT TESTS
# ============================================================================


class TestLearningEvents:
    """Test learning lifecycle events."""

    def test_learning_started_event(self):
        """LearningStarted event."""
        event = LearningStarted(
            job_id="job-1",
            stage_count=8,
            platforms=("youtube", "tiktok"),
        )

        assert event.stage_count == 8
        assert len(event.platforms) == 2

    def test_stage_started_event(self):
        """StageStarted event."""
        event = StageStarted(
            job_id="job-1",
            stage_type=StageType.VALIDATE,
            stage_id="stage-1",
            platform="youtube",
        )

        assert event.stage_type == StageType.VALIDATE

    def test_stage_completed_event(self):
        """StageCompleted event."""
        event = StageCompleted(
            job_id="job-1",
            stage_type=StageType.RETRIEVE_METRICS,
            duration_seconds=15.5,
        )

        assert event.duration_seconds == 15.5

    def test_stage_failed_event(self):
        """StageFailed event."""
        failure = LearningFailure(stage_id="stage-1")
        event = StageFailed(
            job_id="job-1",
            failure=failure,
            will_retry=True,
        )

        assert event.will_retry is True

    def test_learning_completed_event(self):
        """LearningCompleted event."""
        event = LearningCompleted(
            job_id="job-1",
            is_success=True,
            successful_platforms=("youtube", "tiktok"),
            recommendations_generated=5,
        )

        assert event.is_success is True
        assert len(event.successful_platforms) == 2


# ============================================================================
# DAG GENERATION TESTS
# ============================================================================


class TestDAGGeneration:
    """Test DAG generation."""

    def test_planner_creation(self):
        """Create planner."""
        planner = LearningPlanner()

        assert planner is not None

    def test_dag_single_platform(self):
        """Generate DAG for single platform."""
        planner = LearningPlanner()
        job = LearningJob(
            creator_id="creator-1",
        )
        context = LearningContext(
            job_id=job.id,
            creator_id="creator-1",
            platform="youtube",
        )

        stages = planner.create_stage_dag(job, context, None)

        assert len(stages) > 0
        assert stages[0].stage_type == StageType.VALIDATE

    def test_dag_dependencies(self):
        """DAG has proper dependencies."""
        planner = LearningPlanner()
        job = LearningJob(creator_id="creator-1")
        context = LearningContext(
            job_id=job.id,
            platform="youtube",
        )

        stages = planner.create_stage_dag(job, context, None)

        # Later stages should depend on earlier ones
        for i in range(1, len(stages)):
            if not stages[i].is_optional:
                assert len(stages[i].depends_on) > 0 or stages[i].stage_type == StageType.VALIDATE

    def test_stages_to_m8_tasks(self):
        """Convert stages to M8 tasks."""
        planner = LearningPlanner()
        job = LearningJob(creator_id="creator-1")
        context = LearningContext(job_id=job.id, platform="youtube")

        stages = planner.create_stage_dag(job, context, None)
        tasks = planner.stages_to_m8_tasks(stages)

        assert len(tasks) == len(stages)
        assert all(t.metadata.get("stage_type") for t in tasks)


# ============================================================================
# M6 AGENT TESTS
# ============================================================================


class TestLearningAgents:
    """Test M6 learning agents."""

    def test_agent_properties(self):
        """Agent has required properties."""
        agent = ValidationAgent()

        assert agent.agent_id is not None
        assert agent.agent_name is not None
        assert len(agent.capabilities) > 0

    @pytest.mark.asyncio
    async def test_validation_agent(self):
        """Validation agent execution."""
        agent = ValidationAgent()
        task = M8LearningTask(metadata={"stage_type": StageType.VALIDATE.value})

        can_exec = await agent.can_execute(task)
        assert can_exec is True

        result = await agent.execute(task, LearningContext())
        assert result["valid"] is True

    @pytest.mark.asyncio
    async def test_auth_agent(self):
        """Authentication agent execution."""
        agent = AuthenticationAgent()
        task = M8LearningTask(metadata={"stage_type": StageType.AUTH.value})

        can_exec = await agent.can_execute(task)
        assert can_exec is True

    @pytest.mark.asyncio
    async def test_metrics_agent(self):
        """Metrics retrieval agent execution."""
        agent = MetricsRetrievalAgent()
        task = M8LearningTask(metadata={"stage_type": StageType.RETRIEVE_METRICS.value})

        can_exec = await agent.can_execute(task)
        assert can_exec is True

    @pytest.mark.asyncio
    async def test_analysis_agent(self):
        """Analysis agent handles multiple stage types."""
        agent = AnalysisAgent()

        for stage_type in [
            StageType.ANALYZE_RETENTION.value,
            StageType.ANALYZE_AUDIENCE.value,
            StageType.ANALYZE_REVENUE.value,
        ]:
            task = M8LearningTask(metadata={"stage_type": stage_type})
            can_exec = await agent.can_execute(task)
            assert can_exec is True


# ============================================================================
# AGENT REGISTRY TESTS
# ============================================================================


class TestAgentRegistry:
    """Test learning agent registry."""

    def test_registry_creation(self):
        """Create registry."""
        registry = LearningAgentRegistry()

        assert registry is not None

    def test_register_agent(self):
        """Register agent."""
        registry = LearningAgentRegistry()
        agent = ValidationAgent()

        registry.register(agent)

        retrieved = registry.get("agent:validation")

        assert retrieved is not None

    def test_get_agents_for_stage(self):
        """Get agents for stage type."""
        registry = LearningAgentRegistry()
        registry.register(ValidationAgent())
        registry.register(AuthenticationAgent())

        agents = registry.get_agents_for_stage(StageType.VALIDATE)

        assert len(agents) > 0

    def test_list_agents(self):
        """List all agents."""
        registry = LearningAgentRegistry()
        registry.register(ValidationAgent())
        registry.register(MetricsRetrievalAgent())

        agents = registry.list_agents()

        assert len(agents) == 2

    def test_default_registry(self):
        """Create default registry."""
        registry = create_default_learning_agent_registry()

        agents = registry.list_agents()

        # Should have agents for all key stages
        assert len(agents) >= 7


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestPhase3Integration:
    """Integration tests for Phase 3."""

    def test_full_orchestration_flow(self):
        """Full orchestration flow."""
        planner = LearningPlanner()
        job = LearningJob(creator_id="creator-1")
        context = LearningContext(
            job_id=job.id,
            creator_id="creator-1",
            platform="youtube",
        )

        stages = planner.create_stage_dag(job, context, None)
        tasks = planner.stages_to_m8_tasks(stages)

        assert len(stages) > 0
        assert len(tasks) == len(stages)

    def test_multi_platform_orchestration(self):
        """Multi-platform orchestration."""
        planner = LearningPlanner()
        job = LearningJob(creator_id="creator-1")

        for platform in ["youtube", "tiktok", "instagram"]:
            context = LearningContext(
                job_id=job.id,
                platform=platform,
            )

            stages = planner.create_stage_dag(job, context, None)

            assert len(stages) > 0

    @pytest.mark.asyncio
    async def test_agent_execution_flow(self):
        """Agent execution flow."""
        registry = create_default_learning_agent_registry()

        for stage_type in [StageType.VALIDATE, StageType.AUTH]:
            agents = registry.get_agents_for_stage(stage_type)

            assert len(agents) > 0

            for agent in agents:
                task = M8LearningTask(metadata={"stage_type": stage_type.value})

                can_execute = await agent.can_execute(task)

                if can_execute:
                    result = await agent.execute(task, LearningContext())
                    assert result is not None
