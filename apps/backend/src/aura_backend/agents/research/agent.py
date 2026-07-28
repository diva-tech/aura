"""ResearchAgent: Autonomous research agent using platform APIs."""

import time
from datetime import datetime
from typing import Any, Dict, Optional

from aura_backend.ai.tools import ToolRegistry
from aura_backend.core.events import EventBus
from aura_backend.llm import ProviderRegistry, ModelRegistry

from aura_backend.agents.research.goal import Goal, GoalStatus
from aura_backend.agents.research.plan import Plan, PlanStep, StepStatus
from aura_backend.agents.research.context import ExecutionContext
from aura_backend.agents.research.state import AgentState, ResearchAgentState
from aura_backend.agents.research.planner import Planner
from aura_backend.agents.research.executor import StepExecutor
from aura_backend.agents.research.reflector import Reflector, ReflectionDecision
from aura_backend.agents.research.reporter import Reporter
from aura_backend.agents.research.events import (
    GoalAcceptedEvent,
    PlanningStartedEvent,
    PlanningCompletedEvent,
    StepStartedEvent,
    StepCompletedEvent,
    ReflectionStartedEvent,
    ReflectionCompletedEvent,
    ReplanningStartedEvent,
    GoalCompletedEvent,
    GoalFailedEvent,
)


class ResearchAgent:
    """Autonomous research agent using platform APIs"""

    def __init__(
        self,
        tool_registry: ToolRegistry,
        provider_registry: ProviderRegistry,
        model_registry: ModelRegistry,
        event_bus: Optional[EventBus] = None,
    ):
        self.tool_registry = tool_registry
        self.provider_registry = provider_registry
        self.model_registry = model_registry
        self.event_bus = event_bus

        self.agent_id = "research-agent-v1"
        self.state = ResearchAgentState(initial_state=AgentState.IDLE)

        self.planner = Planner(provider_registry, model_registry)
        self.executor = StepExecutor(tool_registry)
        self.reflector = Reflector(provider_registry, model_registry)

        self.current_goal: Optional[Goal] = None
        self.current_plan: Optional[Plan] = None
        self.context: Optional[ExecutionContext] = None

    async def initialize(self) -> None:
        """Initialize agent"""
        self.state.transition(AgentState.IDLE)

    async def shutdown(self) -> None:
        """Shutdown agent"""
        pass

    async def accept_goal(self, goal: Goal) -> None:
        """Accept a research goal"""
        if not self.state.transition(AgentState.PLANNING):
            raise RuntimeError(f"Cannot accept goal in state {self.state.current_state}")

        self.current_goal = goal
        goal.status = GoalStatus.PLANNING
        goal.started_at = datetime.utcnow()

        self.context = ExecutionContext(
            goal_id=goal.id,
            goal_description=goal.description,
        )

        self._publish_event(
            GoalAcceptedEvent(
                goal_id=goal.id,
                agent_id=self.agent_id,
                timestamp=datetime.utcnow(),
                metadata={"goal": goal.description},
                goal_description=goal.description,
            )
        )

    async def execute(self) -> Dict[str, Any]:
        """Execute the goal to completion"""
        if not self.current_goal or not self.context:
            raise RuntimeError("No goal accepted")

        try:
            # Phase 1: Planning
            await self._plan()

            # Phase 2-4: Execute, Reflect, Replan cycle
            while self.state.can_continue() and self.current_goal.is_active():
                await self._execute_step()

                if self.state.current_state == AgentState.EXECUTING:
                    await self._reflect()

                if self.state.current_state == AgentState.REFLECTING:
                    await self._check_replan()

            # Generate report
            report = Reporter.generate_report(
                self.current_goal,
                self.current_plan,
                self.context,
            )

            return {
                "success": self.current_goal.status == GoalStatus.COMPLETED,
                "status": self.current_goal.status.value,
                "report": report,
                "summary": Reporter.generate_summary(
                    self.current_goal,
                    self.current_plan,
                    self.context,
                ),
            }

        except Exception as e:
            self.current_goal.status = GoalStatus.FAILED
            self.current_goal.error = str(e)
            self.current_goal.completed_at = datetime.utcnow()
            self.state.transition(AgentState.FAILED)

            self._publish_event(
                GoalFailedEvent(
                    goal_id=self.current_goal.id,
                    agent_id=self.agent_id,
                    timestamp=datetime.utcnow(),
                    metadata={},
                    error=str(e),
                    total_time_ms=(
                        (self.current_goal.completed_at.timestamp() - self.current_goal.started_at.timestamp())
                        * 1000
                        if self.current_goal.started_at
                        else 0
                    ),
                )
            )

            raise

    async def _plan(self) -> None:
        """Plan execution"""
        self._publish_event(
            PlanningStartedEvent(
                goal_id=self.current_goal.id,
                agent_id=self.agent_id,
                timestamp=datetime.utcnow(),
                metadata={},
            )
        )

        self.current_plan = await self.planner.create_plan(
            self.current_goal,
            self.context,
        )

        self._publish_event(
            PlanningCompletedEvent(
                goal_id=self.current_goal.id,
                agent_id=self.agent_id,
                timestamp=datetime.utcnow(),
                metadata={},
                step_count=len(self.current_plan.steps),
                planning_time_ms=self.context.planning_time_ms,
                tokens_used=self.context.total_tokens_used,
            )
        )

        self.state.transition(AgentState.EXECUTING)

    async def _execute_step(self) -> None:
        """Execute current step"""
        step = self.current_plan.current_step()
        if not step:
            self.state.transition(AgentState.COMPLETED)
            self.current_goal.status = GoalStatus.COMPLETED
            self.current_goal.completed_at = datetime.utcnow()
            return

        self._publish_event(
            StepStartedEvent(
                goal_id=self.current_goal.id,
                agent_id=self.agent_id,
                timestamp=datetime.utcnow(),
                metadata={},
                step_id=step.id,
                step_description=step.description,
                step_index=self.current_plan.current_step_index,
            )
        )

        success = await self.executor.execute_step(step, self.context)

        self._publish_event(
            StepCompletedEvent(
                goal_id=self.current_goal.id,
                agent_id=self.agent_id,
                timestamp=datetime.utcnow(),
                metadata={},
                step_id=step.id,
                step_status=step.status.value,
                execution_time_ms=step.duration_ms() or 0.0,
                tool_used=step.tool_used,
            )
        )

        if success:
            self.context.completed_steps.append(step.id)
            self.current_plan.advance()
        else:
            # Failed step - go to reflection
            self.state.transition(AgentState.REFLECTING)

    async def _reflect(self) -> None:
        """Reflect on execution"""
        step = self.current_plan.steps[self.current_plan.current_step_index - 1]

        self._publish_event(
            ReflectionStartedEvent(
                goal_id=self.current_goal.id,
                agent_id=self.agent_id,
                timestamp=datetime.utcnow(),
                metadata={},
                reflection_count=self.context.reflection_count,
            )
        )

        decision = await self.reflector.reflect(
            step,
            self.current_plan,
            self.context,
        )

        self._publish_event(
            ReflectionCompletedEvent(
                goal_id=self.current_goal.id,
                agent_id=self.agent_id,
                timestamp=datetime.utcnow(),
                metadata={},
                decision=decision.value,
                reflection_time_ms=self.context.reflection_time_ms,
            )
        )

        # Apply decision
        if decision == ReflectionDecision.CONTINUE:
            self.state.transition(AgentState.EXECUTING)
        elif decision == ReflectionDecision.RETRY:
            if step.can_retry():
                await self.executor.retry_step(step, self.context)
                self.state.transition(AgentState.EXECUTING)
            else:
                step.status = StepStatus.FAILED
                self.state.transition(AgentState.REFLECTING)
        elif decision == ReflectionDecision.SKIP:
            self.current_plan.skip_current()
            self.state.transition(AgentState.EXECUTING)
        elif decision == ReflectionDecision.REPLAN:
            self.state.transition(AgentState.REPLANNING)
        elif decision == ReflectionDecision.COMPLETE:
            self.current_goal.status = GoalStatus.COMPLETED
            self.current_goal.completed_at = datetime.utcnow()
            self.state.transition(AgentState.COMPLETED)
        elif decision == ReflectionDecision.FAIL:
            self.current_goal.status = GoalStatus.FAILED
            self.current_goal.error = "Reflection determined goal cannot be achieved"
            self.current_goal.completed_at = datetime.utcnow()
            self.state.transition(AgentState.FAILED)
        else:
            self.state.transition(AgentState.EXECUTING)

    async def _check_replan(self) -> None:
        """Check if replanning is needed"""
        if self.state.current_state != AgentState.REFLECTING:
            return

        # Replanning triggered by reflection
        if self.context.replan_count >= self.current_goal.max_reflections:
            self.current_goal.status = GoalStatus.FAILED
            self.current_goal.error = "Max replans exceeded"
            self.state.transition(AgentState.FAILED)
            return

        self._publish_event(
            ReplanningStartedEvent(
                goal_id=self.current_goal.id,
                agent_id=self.agent_id,
                timestamp=datetime.utcnow(),
                metadata={},
                reason="Reflection indicated plan needs adjustment",
            )
        )

        self.context.replan_count += 1
        self.current_plan = await self.planner.create_plan(
            self.current_goal,
            self.context,
        )

        self.state.transition(AgentState.EXECUTING)

    def _publish_event(self, event: Any) -> None:
        """Publish event to event bus"""
        if self.event_bus:
            self.event_bus.publish(event)
