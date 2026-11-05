"""Tests for ResearchAgent implementation."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from aura_backend.agents.research import (
    ResearchAgent,
    Goal,
    GoalStatus,
    Plan,
    PlanStep,
    StepStatus,
    ExecutionContext,
    AgentState,
    ResearchAgentState,
)
from aura_backend.ai.tools import ToolRegistry
from aura_backend.llm import ProviderRegistry, ModelRegistry


class TestGoalModel:
    """Test Goal model"""

    def test_goal_creation(self):
        """Test creating a goal"""
        goal = Goal(
            description="Research Java 21 features",
            context="Need to understand new Java 21 capabilities",
            success_criteria="Comprehensive list of Java 21 features",
        )

        assert goal.description == "Research Java 21 features"
        assert goal.status == GoalStatus.ACCEPTED
        assert not goal.is_complete()
        assert goal.is_active()

    def test_goal_status_transitions(self):
        """Test goal status transitions"""
        goal = Goal(description="Test")

        assert goal.status == GoalStatus.ACCEPTED
        goal.status = GoalStatus.PLANNING
        assert goal.status == GoalStatus.PLANNING
        assert goal.is_active()

        goal.status = GoalStatus.COMPLETED
        assert goal.is_complete()

    def test_goal_requires_description(self):
        """Test that goal requires description"""
        with pytest.raises(ValueError):
            Goal(description="")


class TestPlanModel:
    """Test Plan model"""

    def test_plan_creation(self):
        """Test creating a plan"""
        plan = Plan()
        assert len(plan.steps) == 0
        assert plan.current_step_index == 0
        assert plan.is_complete()

    def test_plan_add_step(self):
        """Test adding steps to plan"""
        plan = Plan()
        step = PlanStep(description="Step 1", reason="Test")

        plan.add_step(step)
        assert len(plan.steps) == 1
        assert plan.current_step() == step

    def test_plan_advance(self):
        """Test advancing through plan"""
        plan = Plan()
        step1 = PlanStep(description="Step 1", reason="Test 1")
        step2 = PlanStep(description="Step 2", reason="Test 2")

        plan.add_step(step1)
        plan.add_step(step2)

        assert plan.current_step_index == 0
        plan.advance()
        assert plan.current_step_index == 1
        assert plan.current_step() == step2

    def test_plan_success_rate(self):
        """Test plan success rate calculation"""
        plan = Plan()
        step1 = PlanStep(description="Step 1", reason="Test 1")
        step2 = PlanStep(description="Step 2", reason="Test 2")

        step1.status = StepStatus.COMPLETED
        step2.status = StepStatus.FAILED

        plan.add_step(step1)
        plan.add_step(step2)

        assert plan.success_rate() == 50.0


class TestExecutionContext:
    """Test ExecutionContext model"""

    def test_context_creation(self):
        """Test creating execution context"""
        context = ExecutionContext(
            goal_id="goal-1",
            goal_description="Test goal",
        )

        assert context.goal_id == "goal-1"
        assert context.total_tokens_used == 0
        assert len(context.working_memory) == 0

    def test_context_memory_operations(self):
        """Test memory operations"""
        context = ExecutionContext(
            goal_id="goal-1",
            goal_description="Test",
        )

        context.update_memory("key1", "value1")
        assert context.get_memory("key1") == "value1"
        assert context.get_memory("key2", "default") == "default"

    def test_context_tool_output(self):
        """Test adding tool outputs"""
        context = ExecutionContext(
            goal_id="goal-1",
            goal_description="Test",
        )

        context.add_tool_output("BrowserTool", {"url": "example.com", "content": "..."})
        assert "BrowserTool_0" in context.tool_outputs

    def test_context_llm_response(self):
        """Test adding LLM responses"""
        context = ExecutionContext(
            goal_id="goal-1",
            goal_description="Test",
        )

        response = {"model": "claude-3-opus", "content": "Response"}
        context.add_llm_response(response)
        assert len(context.llm_responses) == 1


class TestStateMachine:
    """Test state machine"""

    def test_state_machine_initialization(self):
        """Test state machine init"""
        state = ResearchAgentState()
        assert state.current_state == AgentState.IDLE
        assert not state.is_terminal()

    def test_valid_transitions(self):
        """Test valid state transitions"""
        state = ResearchAgentState()

        # IDLE -> PLANNING
        assert state.transition(AgentState.PLANNING)
        assert state.current_state == AgentState.PLANNING

        # PLANNING -> EXECUTING
        assert state.transition(AgentState.EXECUTING)
        assert state.current_state == AgentState.EXECUTING

    def test_invalid_transitions(self):
        """Test invalid state transitions"""
        state = ResearchAgentState()

        # IDLE -> COMPLETED not allowed
        assert not state.transition(AgentState.COMPLETED)
        assert state.current_state == AgentState.IDLE

    def test_terminal_states(self):
        """Test terminal state detection"""
        state = ResearchAgentState()
        assert not state.is_terminal()

        state.current_state = AgentState.COMPLETED
        assert state.is_terminal()

        state.current_state = AgentState.FAILED
        assert state.is_terminal()


class TestResearchAgent:
    """Test ResearchAgent"""

    @pytest.fixture
    def agent_setup(self):
        """Setup agent and mocks"""
        tool_registry = ToolRegistry()
        provider_registry = ProviderRegistry()
        model_registry = ModelRegistry()

        agent = ResearchAgent(
            tool_registry=tool_registry,
            provider_registry=provider_registry,
            model_registry=model_registry,
        )

        return {
            "agent": agent,
            "tool_registry": tool_registry,
            "provider_registry": provider_registry,
            "model_registry": model_registry,
        }

    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent_setup):
        """Test agent initialization"""
        agent = agent_setup["agent"]

        await agent.initialize()
        assert agent.state.current_state == AgentState.IDLE

    @pytest.mark.asyncio
    async def test_goal_acceptance(self, agent_setup):
        """Test accepting a goal"""
        agent = agent_setup["agent"]

        goal = Goal(description="Test research")
        await agent.accept_goal(goal)

        assert agent.current_goal == goal
        assert goal.status == GoalStatus.PLANNING
        assert agent.state.current_state == AgentState.PLANNING

    @pytest.mark.asyncio
    async def test_state_transitions_during_execution(self, agent_setup):
        """Test state transitions"""
        agent = agent_setup["agent"]

        goal = Goal(description="Test")
        await agent.accept_goal(goal)

        # Should be in PLANNING
        assert agent.state.current_state == AgentState.PLANNING


class TestPlanStep:
    """Test PlanStep model"""

    def test_step_creation(self):
        """Test creating a step"""
        step = PlanStep(
            description="Search for Java 21",
            reason="Gather information",
            expected_output="List of Java 21 features",
        )

        assert step.description == "Search for Java 21"
        assert step.status == StepStatus.PENDING
        assert not step.is_complete()

    def test_step_duration(self):
        """Test step duration calculation"""
        step = PlanStep(description="Test", reason="Test")

        step.started_at = datetime(2026, 7, 28, 10, 0, 0)
        step.completed_at = datetime(2026, 7, 28, 10, 0, 5)

        duration = step.duration_ms()
        assert duration == 5000.0

    def test_step_retry_logic(self):
        """Test step retry logic"""
        step = PlanStep(description="Test", reason="Test", max_retries=2)

        step.status = StepStatus.FAILED
        assert step.can_retry()

        step.retry_count = 2
        assert not step.can_retry()


class TestPlannerIntegration:
    """Test Planner with mocks"""

    @pytest.mark.asyncio
    async def test_planning_with_llm(self):
        """Test planning with LLM"""
        from aura_backend.agents.research.planner import Planner

        provider_registry = MagicMock()
        model_registry = MagicMock()

        planner = Planner(provider_registry, model_registry)

        goal = Goal(description="Research Java 21")
        context = ExecutionContext(goal_id="goal-1", goal_description="Research Java 21")

        # Mock LLM response
        mock_provider = AsyncMock()
        mock_response = MagicMock()
        mock_response.message = """
        STEP 1:
        DESCRIPTION: Search for Java 21 features
        REASON: Gather initial information
        EXPECTED_OUTPUT: List of features
        TOOLS: browser
        PRIORITY: 10

        STEP 2:
        DESCRIPTION: Analyze documentation
        REASON: Understand details
        EXPECTED_OUTPUT: Detailed analysis
        TOOLS: python
        PRIORITY: 8
        """
        mock_response.input_tokens = 100
        mock_response.output_tokens = 200
        mock_response.estimated_cost = 0.01

        mock_provider.generate = AsyncMock(return_value=mock_response)
        provider_registry.get.return_value = mock_provider
        model_registry.find_by_capabilities.return_value = []

        # Mock routing engine
        with patch("aura_backend.agents.research.planner.RoutingEngine") as mock_routing:
            mock_routing_instance = MagicMock()
            mock_routing_result = MagicMock()
            mock_routing_result.model.id = "claude-3-opus"
            mock_routing_instance.route = AsyncMock(return_value=mock_routing_result)
            mock_routing.return_value = mock_routing_instance

            plan = await planner.create_plan(goal, context)

            assert len(plan.steps) >= 1
            assert context.planning_time_ms > 0


class TestExecutorIntegration:
    """Test Executor with mocks"""

    @pytest.mark.asyncio
    async def test_step_execution(self):
        """Test step execution"""
        from aura_backend.agents.research.executor import StepExecutor

        tool_registry = ToolRegistry()
        executor = StepExecutor(tool_registry)

        step = PlanStep(description="Test step", reason="Testing")
        context = ExecutionContext(goal_id="goal-1", goal_description="Test")

        # No tools registered, execution should fail
        result = await executor.execute_step(step, context)
        assert not result or step.status == StepStatus.FAILED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
