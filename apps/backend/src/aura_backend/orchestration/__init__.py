"""Task Orchestration & Multi-Agent Runtime.

Coordinates autonomous agents to execute complex tasks through:
- Capability-driven agent selection
- Immutable task attempts
- Separate scheduler, dispatcher, and capability resolver
- Common Executable interface
- Execution plans distinct from task graphs
"""

from aura_backend.orchestration.checkpointing import (
    CheckpointManager,
    ExecutionCheckpoint,
)
from aura_backend.orchestration.components import (
    CapabilityResolver,
    ExecutionEngine,
    TaskDispatcher,
    TaskScheduler,
)
from aura_backend.orchestration.models import (
    Capability,
    ExecutionPlan,
    ExecutionStatus,
    Skill,
    Task,
    TaskAttempt,
    TaskGraph,
    ToolRequirement,
)
from aura_backend.orchestration.orchestrator import TaskOrchestrator
from aura_backend.orchestration.planner import TaskPlanner
from aura_backend.orchestration.registry import (
    AgentRegistry,
    ExecutableAgent,
)

__all__ = [
    # Models
    "Task",
    "TaskAttempt",
    "TaskGraph",
    "ExecutionPlan",
    "Capability",
    "Skill",
    "ToolRequirement",
    "ExecutionStatus",
    # Registry
    "AgentRegistry",
    "ExecutableAgent",
    # Components
    "CapabilityResolver",
    "TaskScheduler",
    "TaskDispatcher",
    "ExecutionEngine",
    # Planner
    "TaskPlanner",
    # Checkpointing
    "CheckpointManager",
    "ExecutionCheckpoint",
    # Orchestrator
    "TaskOrchestrator",
]
