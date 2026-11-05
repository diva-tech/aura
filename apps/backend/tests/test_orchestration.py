"""Tests for Task Orchestration & Multi-Agent Runtime."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from aura_backend.orchestration import (
    Capability,
    ExecutableAgent,
    ExecutionPlan,
    ExecutionStatus,
    Skill,
    Task,
    TaskAttempt,
    TaskGraph,
    TaskOrchestrator,
    ToolRequirement,
    AgentRegistry,
    CapabilityResolver,
    TaskScheduler,
    TaskDispatcher,
    ExecutionEngine,
)


class MockAgent(ExecutableAgent):
    """Mock agent for testing"""

    def __init__(
        self,
        agent_id: str,
        capabilities: set = None,
        skills: set = None,
        tools: set = None,
    ):
        self._id = agent_id
        self._capabilities = capabilities or {Capability.RESEARCH}
        self._skills = skills or {Skill.WEB_SEARCH}
        self._tools = tools or {ToolRequirement.GOOGLE_SEARCH}

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return f"Agent-{self._id}"

    @property
    def capabilities(self) -> set:
        return self._capabilities

    @property
    def skills(self) -> set:
        return self._skills

    @property
    def tool_requirements(self) -> set:
        return self._tools

    async def can_execute(self, task: Task) -> bool:
        return self._capabilities >= task.required_capabilities

    async def execute(self, task: Task) -> TaskAttempt:
        return TaskAttempt(
            task_id=task.id,
            attempt_number=1,
            status=ExecutionStatus.COMPLETED,
            assigned_agent_id=self._id,
            result=f"Executed {task.goal}",
        )

    async def cancel(self, attempt_id: str) -> bool:
        return True


class TestModels:
    """Test core orchestration models"""

    def test_task_creation(self):
        """Test creating a task"""
        task = Task(
            goal="Research Python",
            priority=10,
            required_capabilities={Capability.RESEARCH},
        )

        assert task.goal == "Research Python"
        assert task.priority == 10
        assert Capability.RESEARCH in task.required_capabilities

    def test_task_immutability(self):
        """Test that tasks are immutable"""
        task = Task(goal="Test")
        with pytest.raises(AttributeError):
            task.goal = "Modified"

    def test_task_attempt_creation(self):
        """Test creating a task attempt"""
        attempt = TaskAttempt(
            task_id="task-1",
            status=ExecutionStatus.COMPLETED,
            result="Done",
        )

        assert attempt.task_id == "task-1"
        assert attempt.status == ExecutionStatus.COMPLETED
        assert attempt.result == "Done"

    def test_task_attempt_immutability(self):
        """Test that attempts are immutable"""
        attempt = TaskAttempt(task_id="task-1")
        with pytest.raises(AttributeError):
            attempt.status = ExecutionStatus.FAILED

    def test_execution_plan_creation(self):
        """Test creating an execution plan"""
        task1 = Task(goal="Research", priority=10)
        task2 = Task(goal="Summarize", priority=9)

        plan = ExecutionPlan(
            goal_description="Research and summarize",
            tasks=[task1, task2],
            strategy="sequential",
        )

        assert plan.goal_description == "Research and summarize"
        assert len(plan.tasks) == 2

    def test_task_graph_creation(self):
        """Test creating a task graph"""
        task1 = Task(id="t1", goal="Task 1")
        task2 = Task(id="t2", goal="Task 2")

        graph = TaskGraph(
            plan_id="plan-1",
            nodes={"t1": task1, "t2": task2},
            edges={"t1": ["t2"]},
            entry_nodes=["t1"],
            exit_nodes=["t2"],
        )

        assert len(graph.nodes) == 2
        assert graph.get_dependencies("t2") == ["t1"]
        assert graph.get_dependents("t1") == ["t2"]

    def test_capabilities_as_separate_concept(self):
        """Test that capabilities, skills, and tools are separate"""
        task = Task(
            goal="Video analysis",
            required_capabilities={Capability.VIDEO_ANALYSIS},
            required_skills={Skill.SCENE_ANALYSIS},
            required_tools={ToolRequirement.VIDEO_PROCESSING},
        )

        assert Capability.VIDEO_ANALYSIS in task.required_capabilities
        assert Skill.SCENE_ANALYSIS in task.required_skills
        assert ToolRequirement.VIDEO_PROCESSING in task.required_tools


class TestAgentRegistry:
    """Test agent registry and capability matching"""

    def test_agent_registration(self):
        """Test registering an agent"""
        registry = AgentRegistry()
        agent = MockAgent("agent-1")

        registry.register(agent)
        assert registry.count() == 1
        assert registry.get("agent-1") == agent

    def test_find_by_capability(self):
        """Test finding agents by capability"""
        registry = AgentRegistry()
        research_agent = MockAgent(
            "research",
            capabilities={Capability.RESEARCH},
        )
        summarize_agent = MockAgent(
            "summarize",
            capabilities={Capability.SUMMARIZATION},
        )

        registry.register(research_agent)
        registry.register(summarize_agent)

        found = registry.find_by_capability(Capability.RESEARCH)
        assert len(found) == 1
        assert found[0].id == "research"

    def test_find_capable_agent(self):
        """Test finding a capable agent"""
        registry = AgentRegistry()
        agent = MockAgent(
            "capable",
            capabilities={Capability.RESEARCH, Capability.ANALYSIS},
        )
        registry.register(agent)

        found = registry.find_capable({Capability.RESEARCH})
        assert found is not None
        assert found.id == "capable"

    def test_find_no_capable_agent(self):
        """Test when no agent is capable"""
        registry = AgentRegistry()
        agent = MockAgent("agent", capabilities={Capability.RESEARCH})
        registry.register(agent)

        found = registry.find_capable({Capability.VIDEO_ANALYSIS})
        assert found is None

    def test_agent_unregistration(self):
        """Test unregistering an agent"""
        registry = AgentRegistry()
        agent = MockAgent("agent-1")
        registry.register(agent)

        assert registry.count() == 1
        registry.unregister("agent-1")
        assert registry.count() == 0


class TestCapabilityResolver:
    """Test capability resolution"""

    @pytest.mark.asyncio
    async def test_resolve_task_to_agent(self):
        """Test resolving a task to a capable agent"""
        registry = AgentRegistry()
        agent = MockAgent("research", capabilities={Capability.RESEARCH})
        registry.register(agent)

        resolver = CapabilityResolver(registry)

        task = Task(
            goal="Research",
            required_capabilities={Capability.RESEARCH},
        )

        resolved = await resolver.resolve_for_task(task)
        assert resolved is not None
        assert resolved.id == "research"

    @pytest.mark.asyncio
    async def test_resolve_no_match(self):
        """Test resolution with no matching agent"""
        registry = AgentRegistry()
        resolver = CapabilityResolver(registry)

        task = Task(required_capabilities={Capability.VIDEO_ANALYSIS})
        resolved = await resolver.resolve_for_task(task)
        assert resolved is None


class TestTaskScheduler:
    """Test task scheduling"""

    @pytest.mark.asyncio
    async def test_enqueue_task(self):
        """Test enqueueing a task"""
        scheduler = TaskScheduler()
        task = Task(goal="Task 1", priority=5)

        await scheduler.enqueue(task)
        assert scheduler.queue_size() == 1

    @pytest.mark.asyncio
    async def test_priority_ordering(self):
        """Test tasks are ordered by priority"""
        scheduler = TaskScheduler()
        low = Task(id="low", priority=1)
        high = Task(id="high", priority=10)
        medium = Task(id="med", priority=5)

        await scheduler.enqueue(low)
        await scheduler.enqueue(high)
        await scheduler.enqueue(medium)

        # Should dequeue high priority first
        first = await scheduler.dequeue()
        assert first.id == "high"

    @pytest.mark.asyncio
    async def test_dequeue_empty(self):
        """Test dequeue on empty queue"""
        scheduler = TaskScheduler()
        task = await scheduler.dequeue()
        assert task is None


class TestTaskDispatcher:
    """Test task dispatching"""

    @pytest.mark.asyncio
    async def test_dispatch_task(self):
        """Test dispatching a task to an agent"""
        registry = AgentRegistry()
        agent = MockAgent("agent-1")
        registry.register(agent)

        resolver = CapabilityResolver(registry)
        dispatcher = TaskDispatcher(registry, resolver)

        task = Task(
            goal="Research",
            required_capabilities={Capability.RESEARCH},
        )

        assigned = await dispatcher.dispatch(task)
        assert assigned is not None
        assert assigned.id == "agent-1"


class TestExecutionEngine:
    """Test task execution engine"""

    @pytest.mark.asyncio
    async def test_execute_single_task(self):
        """Test executing a single task"""
        registry = AgentRegistry()
        agent = MockAgent("agent-1")
        registry.register(agent)

        resolver = CapabilityResolver(registry)
        dispatcher = TaskDispatcher(registry, resolver)
        scheduler = TaskScheduler()
        engine = ExecutionEngine(dispatcher, scheduler)

        task = Task(
            id="task-1",
            goal="Research",
            required_capabilities={Capability.RESEARCH},
        )
        graph = TaskGraph(
            nodes={"task-1": task},
            entry_nodes=["task-1"],
            exit_nodes=["task-1"],
        )

        success = await engine.execute_graph(graph)
        assert success is True

    @pytest.mark.asyncio
    async def test_execute_sequential_tasks(self):
        """Test executing sequential tasks"""
        registry = AgentRegistry()
        agent = MockAgent(
            "agent-1",
            capabilities={Capability.RESEARCH, Capability.SUMMARIZATION},
        )
        registry.register(agent)

        resolver = CapabilityResolver(registry)
        dispatcher = TaskDispatcher(registry, resolver)
        scheduler = TaskScheduler()
        engine = ExecutionEngine(dispatcher, scheduler)

        task1 = Task(
            id="t1",
            goal="Research",
            required_capabilities={Capability.RESEARCH},
            priority=10,
        )
        task2 = Task(
            id="t2",
            goal="Summarize",
            required_capabilities={Capability.SUMMARIZATION},
            priority=9,
        )

        graph = TaskGraph(
            nodes={"t1": task1, "t2": task2},
            edges={"t1": ["t2"]},
            entry_nodes=["t1"],
            exit_nodes=["t2"],
        )

        success = await engine.execute_graph(graph)
        assert success is True


class TestOrchestrator:
    """Test main orchestrator"""

    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self):
        """Test creating an orchestrator"""
        registry = AgentRegistry()
        memory = AsyncMock()

        orchestrator = TaskOrchestrator(registry, memory)
        assert orchestrator.registry == registry
        assert orchestrator.memory == memory

    @pytest.mark.asyncio
    async def test_orchestrator_metrics(self):
        """Test getting orchestrator metrics"""
        registry = AgentRegistry()
        agent = MockAgent("agent-1")
        registry.register(agent)

        memory = AsyncMock()
        orchestrator = TaskOrchestrator(registry, memory)

        metrics = orchestrator.get_metrics()
        assert metrics["registered_agents"] == 1

    @pytest.mark.asyncio
    async def test_capability_driven_selection(self):
        """Test that agents are selected by capability, not class"""
        registry = AgentRegistry()

        # Register agents with different capabilities
        research_agent = MockAgent(
            "research-agent",
            capabilities={Capability.RESEARCH},
        )
        video_agent = MockAgent(
            "video-agent",
            capabilities={Capability.VIDEO_ANALYSIS},
        )

        registry.register(research_agent)
        registry.register(video_agent)

        # Create a task requiring research
        task = Task(
            goal="Research",
            required_capabilities={Capability.RESEARCH},
        )

        # Orchestrator should select research agent without hardcoding
        resolver = CapabilityResolver(registry)
        agent = await resolver.resolve_for_task(task)

        assert agent.id == "research-agent"
        assert Capability.RESEARCH in agent.capabilities

    @pytest.mark.asyncio
    async def test_task_attempt_immutability(self):
        """Test that task attempts are immutable"""
        attempt = TaskAttempt(task_id="t1", status=ExecutionStatus.PENDING)

        # Verify immutability
        with pytest.raises(AttributeError):
            attempt.status = ExecutionStatus.RUNNING

    @pytest.mark.asyncio
    async def test_execution_plan_vs_task_graph(self):
        """Test distinction between execution plan and task graph"""
        # ExecutionPlan: what needs to be done (from AI Framework)
        plan = ExecutionPlan(
            goal_description="Research and summarize Python async",
            strategy="sequential",
        )
        assert plan.goal_description is not None

        # TaskGraph: how to execute it (dependencies, order)
        task1 = Task(id="research", goal="Research")
        task2 = Task(id="summarize", goal="Summarize")

        graph = TaskGraph(
            plan_id=plan.id,
            nodes={"research": task1, "summarize": task2},
            edges={"research": ["summarize"]},
        )

        # They're distinct but related
        assert graph.plan_id == plan.id
        assert len(plan.tasks) != len(graph.nodes)


class TestFutureExtensibility:
    """Test that architecture supports future agents without changes"""

    @pytest.mark.asyncio
    async def test_new_agent_type_fits_architecture(self):
        """Test that new agent types (Video, Script, Thumbnail) fit without changes"""

        # Simulate future VideoAnalysisAgent
        class VideoAnalysisAgent(ExecutableAgent):
            @property
            def id(self) -> str:
                return "video-analyst"

            @property
            def name(self) -> str:
                return "Video Analysis Agent"

            @property
            def capabilities(self) -> set:
                return {Capability.VIDEO_ANALYSIS}

            @property
            def skills(self) -> set:
                return {Skill.SCENE_ANALYSIS, Skill.SHOT_DETECTION}

            @property
            def tool_requirements(self) -> set:
                return {ToolRequirement.VIDEO_PROCESSING}

            async def can_execute(self, task: Task) -> bool:
                return Capability.VIDEO_ANALYSIS in task.required_capabilities

            async def execute(self, task: Task) -> TaskAttempt:
                return TaskAttempt(
                    task_id=task.id,
                    status=ExecutionStatus.COMPLETED,
                    result="Video analyzed",
                )

            async def cancel(self, attempt_id: str) -> bool:
                return True

        # Register it - no orchestration code changes needed
        registry = AgentRegistry()
        video_agent = VideoAnalysisAgent()
        registry.register(video_agent)

        # Can immediately create tasks for it
        task = Task(
            goal="Analyze video",
            required_capabilities={Capability.VIDEO_ANALYSIS},
        )

        resolver = CapabilityResolver(registry)
        agent = await resolver.resolve_for_task(task)
        assert agent is not None
        assert agent.id == "video-analyst"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
