"""
AI framework events.

Extends the runtime EventBus with AI-specific events.
"""

from __future__ import annotations

from aura_backend.core.events import BaseEvent


# Goal Events

class GoalCreated(BaseEvent):
    """Fired when a new goal is created"""

    event_type: str = "goal.created"
    goal_id: str = ""
    goal_title: str = ""
    priority: str = "normal"


class GoalUpdated(BaseEvent):
    """Fired when a goal is updated"""

    event_type: str = "goal.updated"
    goal_id: str = ""
    status: str = ""


class GoalCompleted(BaseEvent):
    """Fired when a goal is completed"""

    event_type: str = "goal.completed"
    goal_id: str = ""
    success: bool = False


class GoalFailed(BaseEvent):
    """Fired when a goal fails"""

    event_type: str = "goal.failed"
    goal_id: str = ""
    error: str = ""


class GoalCancelled(BaseEvent):
    """Fired when a goal is cancelled"""

    event_type: str = "goal.cancelled"
    goal_id: str = ""


# Planning Events

class PlanningStarted(BaseEvent):
    """Fired when planning begins"""

    event_type: str = "planning.started"
    goal_id: str = ""


class PlanningCompleted(BaseEvent):
    """Fired when planning completes"""

    event_type: str = "planning.completed"
    goal_id: str = ""
    plan_id: str = ""
    step_count: int = 0


class PlanningFailed(BaseEvent):
    """Fired when planning fails"""

    event_type: str = "planning.failed"
    goal_id: str = ""
    error: str = ""


# Execution Events

class ExecutionStarted(BaseEvent):
    """Fired when execution begins"""

    event_type: str = "execution.started"
    session_id: str = ""
    goal_id: str = ""
    plan_id: str = ""


class ExecutionCompleted(BaseEvent):
    """Fired when execution completes"""

    event_type: str = "execution.completed"
    session_id: str = ""
    success: bool = False
    execution_time_ms: float = 0.0


class ExecutionFailed(BaseEvent):
    """Fired when execution fails"""

    event_type: str = "execution.failed"
    session_id: str = ""
    error: str = ""


class ExecutionCancelled(BaseEvent):
    """Fired when execution is cancelled"""

    event_type: str = "execution.cancelled"
    session_id: str = ""


# Step Events

class StepStarted(BaseEvent):
    """Fired when a step begins"""

    event_type: str = "step.started"
    session_id: str = ""
    step_id: str = ""
    step_description: str = ""


class StepCompleted(BaseEvent):
    """Fired when a step completes"""

    event_type: str = "step.completed"
    session_id: str = ""
    step_id: str = ""
    success: bool = False


class StepFailed(BaseEvent):
    """Fired when a step fails"""

    event_type: str = "step.failed"
    session_id: str = ""
    step_id: str = ""
    error: str = ""


# Tool Events

class ToolExecuted(BaseEvent):
    """Fired when a tool is executed"""

    event_type: str = "tool.executed"
    session_id: str = ""
    tool_id: str = ""
    tool_name: str = ""
    success: bool = False
    execution_time_ms: float = 0.0


class ToolFailed(BaseEvent):
    """Fired when tool execution fails"""

    event_type: str = "tool.failed"
    session_id: str = ""
    tool_id: str = ""
    error: str = ""


# Observation Events

class ObservationRecorded(BaseEvent):
    """Fired when an observation is recorded"""

    event_type: str = "observation.recorded"
    session_id: str = ""
    observation_type: str = ""
    content: str = ""


# Reflection Events

class ReflectionStarted(BaseEvent):
    """Fired when reflection begins"""

    event_type: str = "reflection.started"
    session_id: str = ""


class ReflectionCompleted(BaseEvent):
    """Fired when reflection completes"""

    event_type: str = "reflection.completed"
    session_id: str = ""
    insights: str = ""


# Memory Events

class MemoryUpdated(BaseEvent):
    """Fired when memory is updated"""

    event_type: str = "memory.updated"
    session_id: str = ""
    memory_type: str = ""
    operation: str = ""


class MemoryRetrieved(BaseEvent):
    """Fired when memory is retrieved"""

    event_type: str = "memory.retrieved"
    session_id: str = ""
    memory_type: str = ""
    item_count: int = 0


# Agent Events

class AgentStateChanged(BaseEvent):
    """Fired when agent state changes"""

    event_type: str = "agent.state_changed"
    agent_id: str = ""
    from_state: str = ""
    to_state: str = ""


class AgentFailed(BaseEvent):
    """Fired when agent encounters a fatal error"""

    event_type: str = "agent.failed"
    agent_id: str = ""
    error: str = ""


class AgentRecovered(BaseEvent):
    """Fired when agent recovers from error"""

    event_type: str = "agent.recovered"
    agent_id: str = ""
    recovery_method: str = ""


# Framework Health Events

class FrameworkHealthChanged(BaseEvent):
    """Fired when AI framework health changes"""

    event_type: str = "framework.health_changed"
    health_status: str = ""
    affected_components: list[str] = None

    def __post_init__(self):
        if self.affected_components is None:
            self.affected_components = []
