"""Main orchestrator - coordinates all components for task execution.

Facade that uses independent components: Scheduler, Dispatcher, Planner, etc.
"""

from typing import Any, Dict, List, Optional

from aura_backend.memory import MemoryManager
from aura_backend.orchestration.checkpointing import CheckpointManager
from aura_backend.orchestration.components import (
    CapabilityResolver,
    ExecutionEngine,
    TaskDispatcher,
    TaskScheduler,
)
from aura_backend.orchestration.events import OrchestrationEvent, TaskCreatedEvent
from aura_backend.orchestration.models import ExecutionPlan, TaskGraph
from aura_backend.orchestration.planner import TaskPlanner
from aura_backend.orchestration.registry import AgentRegistry


class TaskOrchestrator:
    """Coordinates task execution across multiple agents.

    Uses capability-driven agent selection and immutable task attempts.
    Manages execution plans, task graphs, scheduling, and recovery.
    """

    def __init__(
        self,
        agent_registry: AgentRegistry,
        memory_manager: MemoryManager,
    ):
        """Initialize orchestrator with registry and memory"""
        self.registry = agent_registry
        self.memory = memory_manager

        # Initialize independent components
        self.capability_resolver = CapabilityResolver(agent_registry)
        self.scheduler = TaskScheduler()
        self.dispatcher = TaskDispatcher(agent_registry, self.capability_resolver)
        self.execution_engine = ExecutionEngine(self.dispatcher, self.scheduler)
        self.planner = TaskPlanner()
        self.checkpoint_manager = CheckpointManager(memory_manager)

        # Events
        self._events: List[OrchestrationEvent] = []

    async def execute_goal(
        self,
        goal_description: str,
        goal_id: str = "",
        max_parallel: int = 5,
    ) -> bool:
        """Execute a goal by orchestrating agents.

        End-to-end flow:
        1. Create execution plan from goal
        2. Create task graph from plan
        3. Schedule tasks
        4. Execute with agents
        5. Checkpoint state

        Args:
            goal_description: What to accomplish
            goal_id: Optional goal ID from M3 Framework
            max_parallel: Max parallel task execution

        Returns:
            True if execution succeeded, False if any task failed
        """
        # Step 1: Create execution plan
        plan = await self.planner.create_execution_plan(goal_description, goal_id)

        # Step 2: Create task graph
        graph = await self.planner.create_task_graph(plan)

        # Step 3: Publish task creation events
        for task in plan.tasks:
            event = TaskCreatedEvent(
                task_id=task.id,
                goal=task.goal,
                priority=task.priority,
            )
            self._events.append(event)

        # Step 4: Enqueue tasks
        for task in plan.tasks:
            await self.scheduler.enqueue(task)

        # Step 5: Execute task graph
        success = await self.execution_engine.execute_graph(graph, max_parallel)

        # Step 6: Create checkpoint of final state
        if success:
            await self.checkpoint_manager.create_checkpoint(
                task_graph=graph,
                completed_tasks=self.execution_engine._results,
                failed_tasks={},
                running_tasks=set(),
                checkpoint_id=f"final-{plan.id}",
            )

        return success

    async def execute_plan(
        self,
        plan: ExecutionPlan,
        max_parallel: int = 5,
    ) -> bool:
        """Execute an execution plan.

        Args:
            plan: ExecutionPlan with tasks
            max_parallel: Max parallel execution

        Returns:
            True if all tasks succeeded
        """
        # Create task graph from plan
        graph = await self.planner.create_task_graph(plan)

        # Execute graph
        return await self.execution_engine.execute_graph(graph, max_parallel)

    async def execute_graph(
        self,
        graph: TaskGraph,
        max_parallel: int = 5,
    ) -> bool:
        """Execute a task graph directly.

        Args:
            graph: TaskGraph with dependencies
            max_parallel: Max parallel execution

        Returns:
            True if all tasks succeeded
        """
        return await self.execution_engine.execute_graph(graph, max_parallel)

    async def resume_from_checkpoint(
        self,
        checkpoint_id: str,
        max_parallel: int = 5,
    ) -> bool:
        """Resume execution from a checkpoint.

        Restores state and continues execution.
        """
        checkpoint = await self.checkpoint_manager.restore_checkpoint(checkpoint_id)
        if not checkpoint:
            return False

        # Continue execution from checkpoint state
        # In production, would skip completed tasks
        return await self.execution_engine.execute_graph(
            checkpoint.task_graph,
            max_parallel,
        )

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        return await self.execution_engine.cancel_task(task_id)

    def get_attempt_history(self, task_id: str) -> List[Any]:
        """Get all attempts for a task"""
        return self.execution_engine.get_attempts(task_id)

    def get_events(self) -> List[OrchestrationEvent]:
        """Get all events from this execution"""
        return self._events

    def get_metrics(self) -> Dict[str, Any]:
        """Get execution metrics"""
        return {
            "queued_tasks": self.scheduler.queue_size(),
            "scheduled_tasks": self.scheduler.scheduled_count(),
            "completed_tasks": self.scheduler.completed_count(),
            "registered_agents": self.registry.count(),
            "events": len(self._events),
        }
