"""
Comprehensive tests for AI Framework.

Tests all major components without implementation details.
"""

import pytest
from datetime import datetime
from typing import Any, Dict

from aura_backend.ai import (
    BaseAgent,
    AgentContext,
    Goal,
    GoalStatus,
    GoalPriority,
    AgentState,
    StateMachine,
    StateTransitionError,
    ToolRegistry,
    FilesystemTool,
    PythonTool,
    Session,
    SessionManager,
    SessionStatus,
    PromptTemplate,
    PromptLibrary,
    PromptVariables,
)
from aura_backend.ai.tools import (
    VisionTool,
    VideoTool,
    AudioTool,
    BrowserTool,
    ImageGenerationTool,
)


# ============================================================================
# CONTEXT TESTS
# ============================================================================

class TestAgentContext:
    """Test AgentContext"""

    def test_context_creation(self):
        """Context creates with defaults"""
        ctx = AgentContext()
        assert ctx.session_id
        assert ctx.correlation_id
        assert ctx.trace_id

    def test_working_memory(self):
        """Working memory operations"""
        ctx = AgentContext()
        ctx.update_memory("key1", "value1")
        assert ctx.get_memory("key1") == "value1"
        assert ctx.get_memory("missing") is None

    def test_cancellation(self):
        """Cancellation token works"""
        ctx = AgentContext()
        assert not ctx.is_cancelled()
        ctx.cancel()
        assert ctx.is_cancelled()

    def test_serialization(self):
        """Context serializes to dict"""
        ctx = AgentContext()
        ctx.goal = "test goal"
        data = ctx.to_dict()
        assert data["goal"] == "test goal"
        assert data["session_id"]


# ============================================================================
# GOAL TESTS
# ============================================================================

class TestGoal:
    """Test Goal domain models"""

    def test_goal_creation(self):
        """Goal creates with immutability"""
        goal = Goal(title="Test Goal", objective="Do something")
        assert goal.id
        assert goal.title == "Test Goal"
        assert goal.status == GoalStatus.PENDING

    def test_goal_transitions(self):
        """Goal status transitions"""
        goal = Goal(title="Test")
        assert goal.status == GoalStatus.PENDING

        active_goal = goal.with_status(GoalStatus.ACTIVE)
        assert active_goal.started_at is not None
        assert goal.started_at is None  # Original unchanged

        completed_goal = active_goal.with_status(GoalStatus.COMPLETED)
        assert completed_goal.completed_at is not None

    def test_goal_priority(self):
        """Goal priority changes"""
        goal = Goal(title="Test", priority=GoalPriority.NORMAL)
        high_priority = goal.with_priority(GoalPriority.HIGH)
        assert high_priority.priority == GoalPriority.HIGH
        assert goal.priority == GoalPriority.NORMAL

    def test_goal_duration(self):
        """Goal duration tracking"""
        goal = Goal(title="Test")
        active_goal = goal.with_status(GoalStatus.ACTIVE)
        # Duration only available after started
        assert active_goal.duration_ms() is not None


# ============================================================================
# STATE MACHINE TESTS
# ============================================================================

class TestStateMachine:
    """Test state machine with validation"""

    def test_initial_state(self):
        """State machine starts in IDLE"""
        sm = StateMachine()
        assert sm.current_state == AgentState.IDLE

    def test_valid_transitions(self):
        """Valid transitions work"""
        sm = StateMachine()
        sm.transition_to(AgentState.PLANNING)
        assert sm.current_state == AgentState.PLANNING

        sm.transition_to(AgentState.EXECUTING)
        assert sm.current_state == AgentState.EXECUTING

    def test_invalid_transitions(self):
        """Invalid transitions raise error"""
        sm = StateMachine()
        with pytest.raises(StateTransitionError):
            sm.transition_to(AgentState.REFLECTING)  # Can't go from IDLE to REFLECTING

    def test_transition_history(self):
        """Transition history tracked"""
        sm = StateMachine()
        sm.transition_to(AgentState.PLANNING)
        sm.transition_to(AgentState.EXECUTING)

        history = sm.history
        assert len(history) == 2
        assert history[0].from_state == AgentState.IDLE
        assert history[0].to_state == AgentState.PLANNING

    def test_valid_next_states(self):
        """Get valid next states"""
        sm = StateMachine()
        valid = sm.get_valid_next_states()
        assert AgentState.PLANNING in valid

    def test_state_duration(self):
        """Time in state calculation"""
        sm = StateMachine()
        sm.transition_to(AgentState.PLANNING)
        time_in_state = sm.time_in_state_ms()
        assert time_in_state >= 0


# ============================================================================
# TOOL FRAMEWORK TESTS
# ============================================================================

class TestToolFramework:
    """Test tool framework"""

    def test_tool_creation(self):
        """Tools create successfully"""
        tool = FilesystemTool()
        assert tool.id == "FilesystemTool"
        assert tool.get_name() == "Filesystem"

    def test_tool_capabilities(self):
        """Tools declare capabilities"""
        tool = VisionTool()
        capabilities = tool.get_capabilities()
        assert len(capabilities) > 0
        assert capabilities[0].name == "analyze-image"

    def test_tool_registry(self):
        """Tool registry manages tools"""
        registry = ToolRegistry()
        tool1 = FilesystemTool()
        tool2 = PythonTool()

        registry.register(tool1)
        registry.register(tool2)

        assert registry.count() == 2
        assert registry.get("FilesystemTool") is tool1
        assert len(registry.list()) == 2

    @pytest.mark.asyncio
    async def test_tool_health(self):
        """Tools report health"""
        tool = AudioTool()
        health = await tool.health()
        assert health["status"] == "placeholder"

    @pytest.mark.asyncio
    async def test_tool_info(self):
        """Tools provide complete info"""
        tool = BrowserTool()
        info = await tool.get_info()
        assert info["id"] == "BrowserTool"
        assert info["name"] == "Browser"
        assert len(info["capabilities"]) > 0


# ============================================================================
# SESSION MANAGEMENT TESTS
# ============================================================================

class TestSessionManagement:
    """Test session management"""

    def test_session_creation(self):
        """Sessions create with defaults"""
        session = Session(agent_id="agent1", goal_id="goal1")
        assert session.session_id
        assert session.status == SessionStatus.CREATED

    def test_session_lifecycle(self):
        """Session lifecycle works"""
        session = Session(agent_id="agent1", goal_id="goal1")

        session.start()
        assert session.status == SessionStatus.RUNNING
        assert session.started_at is not None

        session.complete()
        assert session.status == SessionStatus.COMPLETED
        assert session.completed_at is not None

    def test_session_manager(self):
        """Session manager tracks sessions"""
        mgr = SessionManager()

        session1 = mgr.create_session("agent1", "goal1")
        session2 = mgr.create_session("agent1", "goal2")
        session3 = mgr.create_session("agent2", "goal3")

        assert mgr.count_sessions() == 3
        assert mgr.count_sessions(agent_id="agent1") == 2

        sessions = mgr.list_sessions(agent_id="agent1")
        assert len(sessions) == 2

    def test_session_duration(self):
        """Session duration tracking"""
        session = Session(agent_id="agent1", goal_id="goal1")
        session.start()
        session.complete()

        duration = session.duration_ms()
        assert duration is not None
        assert duration >= 0


# ============================================================================
# PROMPT SYSTEM TESTS
# ============================================================================

class TestPromptSystem:
    """Test prompt system"""

    def test_prompt_template(self):
        """Prompt templates work"""
        template = PromptTemplate(
            id="template1",
            name="Test Template",
            template="Hello {name}",
            description="Test prompt",
        )
        assert template.id == "template1"
        assert "{name}" in template.template

    def test_prompt_variables(self):
        """Prompt variables work"""
        vars = PromptVariables()
        vars.set("key1", "value1")
        assert vars.get("key1") == "value1"
        assert vars.get("missing") is None

    def test_prompt_library(self):
        """Prompt library manages templates"""
        lib = PromptLibrary()

        template1 = PromptTemplate(
            id="t1",
            name="Template 1",
            template="Test 1",
            description="Test",
        )
        template2 = PromptTemplate(
            id="t2",
            name="Template 2",
            template="Test 2",
            description="Test",
        )

        lib.register_template(template1)
        lib.register_template(template2)

        assert lib.get_template("t1") is template1
        assert len(lib.list_templates()) == 2


# ============================================================================
# BASE AGENT TESTS
# ============================================================================

class TestBaseAgent:
    """Test BaseAgent lifecycle"""

    class SimpleAgent(BaseAgent):
        """Simple test agent"""

        async def _initialize_impl(self) -> None:
            pass

        async def _shutdown_impl(self) -> None:
            pass

    @pytest.mark.asyncio
    async def test_agent_lifecycle(self):
        """Agent lifecycle works"""
        agent = self.SimpleAgent()
        assert not agent.is_initialized

        await agent.initialize()
        assert agent.is_initialized

        await agent.shutdown()
        assert not agent.is_initialized

    @pytest.mark.asyncio
    async def test_agent_health(self):
        """Agent reports health"""
        agent = self.SimpleAgent()
        health = await agent.health()
        assert health["id"] == agent.id
        assert not health["initialized"]

    @pytest.mark.asyncio
    async def test_agent_info(self):
        """Agent provides complete info"""
        agent = self.SimpleAgent()
        await agent.initialize()

        info = await agent.get_info()
        assert info["id"] == agent.id
        assert info["initialized"]
        assert "health" in info


# ============================================================================
# DEPENDENCY INJECTION TESTS
# ============================================================================

class TestDependencyInjection:
    """Test that AI framework works with container"""

    def test_tool_registration_in_container(self):
        """Tools register in service container"""
        from aura_backend.core.service_container import ServiceContainer

        container = ServiceContainer()
        tool = FilesystemTool()

        container.register_instance(FilesystemTool, tool)
        resolved = container.resolve(FilesystemTool)

        assert resolved is tool

    @pytest.mark.asyncio
    async def test_agent_with_context(self):
        """Agent works with AgentContext"""
        agent = TestBaseAgent.SimpleAgent()
        ctx = AgentContext(goal="test")

        await agent.initialize()
        assert ctx.goal == "test"
