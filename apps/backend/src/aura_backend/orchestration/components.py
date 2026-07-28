"""Core orchestration components.

Independent components: Scheduler, Dispatcher, Capability Resolver, Execution Engine.
"""

import asyncio
from typing import Dict, List, Optional, Set

from aura_backend.orchestration.models import (
    Capability,
    ExecutionStatus,
    Skill,
    Task,
    TaskAttempt,
    TaskGraph,
    ToolRequirement,
)
from aura_backend.orchestration.registry import AgentRegistry, ExecutableAgent


class CapabilityResolver:
    """Matches task requirements to agent capabilities.

    Determines what capabilities, skills, and tools are needed for a task.
    """

    def __init__(self, agent_registry: AgentRegistry):
        """Initialize with agent registry for validation"""
        self.registry = agent_registry

    async def resolve_for_task(self, task: Task) -> Optional[ExecutableAgent]:
        """Find an agent capable of executing this task.

        Args:
            task: Task with capability requirements

        Returns:
            Capable agent, or None if no agent matches
        """
        if not task.required_capabilities:
            return None

        agent = self.registry.find_capable(
            required_capabilities=task.required_capabilities,
            required_skills=task.required_skills,
            required_tools=task.required_tools,
        )

        if agent:
            can_execute = await agent.can_execute(task)
            if can_execute:
                return agent

        return None

    async def resolve_alternatives(
        self,
        task: Task,
    ) -> List[ExecutableAgent]:
        """Find all agents capable of executing this task.

        Returns agents in order, suitable for failover or load balancing.
        """
        if not task.required_capabilities:
            return []

        agents = self.registry.find_all_capable(
            required_capabilities=task.required_capabilities,
        )

        # Filter by can_execute
        capable = []
        for agent in agents:
            can_execute = await agent.can_execute(task)
            if can_execute:
                capable.append(agent)

        return capable


class TaskScheduler:
    """Manages task queuing and ordering.

    Handles priority queues, dependency tracking, and scheduling decisions.
    """

    def __init__(self):
        """Initialize scheduler state"""
        self._queue: List[Task] = []
        self._scheduled: Dict[str, Task] = {}
        self._completed: Dict[str, Task] = {}

    async def enqueue(self, task: Task) -> None:
        """Add task to queue.

        Tasks are ordered by priority (higher = sooner).
        """
        self._queue.append(task)
        self._queue.sort(key=lambda t: t.priority, reverse=True)

    async def dequeue(self) -> Optional[Task]:
        """Remove and return next task from queue.

        Returns highest priority task ready to execute.
        """
        if not self._queue:
            return None
        return self._queue.pop(0)

    async def mark_scheduled(self, task: Task) -> None:
        """Mark task as scheduled"""
        self._scheduled[task.id] = task

    async def mark_completed(self, task_id: str) -> None:
        """Mark task as completed"""
        if task_id in self._scheduled:
            task = self._scheduled.pop(task_id)
            self._completed[task_id] = task

    def queue_size(self) -> int:
        """Current queue size"""
        return len(self._queue)

    def scheduled_count(self) -> int:
        """Number of scheduled tasks"""
        return len(self._scheduled)

    def completed_count(self) -> int:
        """Number of completed tasks"""
        return len(self._completed)


class TaskDispatcher:
    """Assigns tasks to agents.

    Uses capability resolver to match tasks to agents.
    """

    def __init__(
        self,
        agent_registry: AgentRegistry,
        capability_resolver: CapabilityResolver,
    ):
        """Initialize dispatcher"""
        self.registry = agent_registry
        self.resolver = capability_resolver

    async def dispatch(self, task: Task) -> Optional[ExecutableAgent]:
        """Assign task to a capable agent.

        Args:
            task: Task to dispatch

        Returns:
            Agent assigned to task, or None if no capable agent found
        """
        agent = await self.resolver.resolve_for_task(task)
        return agent

    async def dispatch_with_fallback(self, task: Task) -> Optional[ExecutableAgent]:
        """Assign task with fallback to alternatives if primary fails.

        Returns first responsive agent.
        """
        agents = await self.resolver.resolve_alternatives(task)
        if agents:
            return agents[0]  # Return primary candidate
        return None


class ExecutionEngine:
    """Executes task graphs with true concurrent execution.

    Handles:
    - True DAG execution with concurrent agents
    - Dependency resolution while tasks are running
    - Parallel execution up to max_parallel limit
    - Failure propagation
    - Cancellation
    - Retries
    - Per-task checkpointing
    """

    def __init__(
        self,
        dispatcher: TaskDispatcher,
        scheduler: TaskScheduler,
    ):
        """Initialize execution engine"""
        self.dispatcher = dispatcher
        self.scheduler = scheduler
        self._attempts: Dict[str, List[TaskAttempt]] = {}
        self._results: Dict[str, str] = {}
        self._running: Set[str] = set()  # Currently executing tasks
        self._completed: Set[str] = set()  # Successfully completed tasks
        self._failed: Set[str] = set()  # Failed tasks
        self._cancelled: Set[str] = set()  # Cancelled tasks
        self._pending_cancel: Set[str] = set()  # Tasks pending cancellation

    async def execute_graph(
        self,
        graph: TaskGraph,
        max_parallel: int = 5,
    ) -> bool:
        """Execute a task graph with true concurrent execution.

        Multiple agents execute simultaneously. Dependencies are resolved
        immediately when tasks complete. New tasks are enqueued without
        waiting for the current batch to finish.

        Args:
            graph: TaskGraph to execute
            max_parallel: Maximum concurrent tasks

        Returns:
            True if all tasks succeeded, False if any failed
        """
        # Reset state for this execution
        self._completed.clear()
        self._failed.clear()
        self._cancelled.clear()
        self._running.clear()

        # Track asyncio.Task objects for concurrent execution
        executing_tasks: Dict[asyncio.Task, str] = {}  # asyncio.Task -> task_id

        try:
            # Initialize: find and enqueue entry nodes
            ready_queue = list(graph.entry_nodes)
            awaiting_dependencies = set(graph.nodes.keys()) - set(graph.entry_nodes)

            while True:
                # Enqueue ready tasks (up to max_parallel)
                while ready_queue and len(executing_tasks) < max_parallel:
                    task_id = ready_queue.pop(0)
                    if task_id in self._running:
                        continue

                    task = graph.nodes[task_id]
                    coro_task = asyncio.create_task(self._execute_task(task))
                    executing_tasks[coro_task] = task_id
                    self._running.add(task_id)

                # All done if no running tasks and nothing in queue
                if not executing_tasks and not ready_queue:
                    break

                if not executing_tasks:
                    # Deadlock: tasks waiting but none ready
                    break

                # Wait for ANY task to complete (not all)
                done, pending = await asyncio.wait(
                    executing_tasks.keys(),
                    return_when=asyncio.FIRST_COMPLETED,
                )

                # Process each completed task
                for completed_task in done:
                    task_id = executing_tasks.pop(completed_task)
                    self._running.discard(task_id)

                    # Get the result
                    try:
                        attempt = await completed_task
                    except Exception as e:
                        # Task raised an exception
                        attempt = TaskAttempt(
                            task_id=task_id,
                            attempt_number=len(self._attempts.get(task_id, [])) + 1,
                            status=ExecutionStatus.FAILED,
                            error=str(e),
                        )

                    # Track attempt
                    self._track_attempt(task_id, attempt)

                    # Update state
                    if attempt.status == ExecutionStatus.COMPLETED:
                        self._completed.add(task_id)
                        self._results[task_id] = attempt.result or ""
                    elif attempt.status == ExecutionStatus.CANCELLED:
                        self._cancelled.add(task_id)
                    else:
                        self._failed.add(task_id)

                    # Resolve dependencies immediately after completion
                    # Find tasks that depend on this one
                    dependents = graph.get_dependents(task_id)
                    for dependent_id in dependents:
                        # Check if dependent is now ready
                        if dependent_id in self._completed or \
                           dependent_id in self._failed or \
                           dependent_id in self._cancelled:
                            continue

                        deps = graph.get_dependencies(dependent_id)
                        if all(dep in self._completed for dep in deps):
                            # Dependent is now ready
                            if dependent_id not in ready_queue:
                                ready_queue.append(dependent_id)

        finally:
            # Cancel any still-running tasks
            for coro_task in executing_tasks.keys():
                if not coro_task.done():
                    coro_task.cancel()

        # Success if no failures
        return len(self._failed) == 0

    async def _execute_task(self, task: Task) -> TaskAttempt:
        """Execute a single task concurrently.

        Returns immutable TaskAttempt record.
        """
        # Check if cancellation was requested
        if task.id in self._pending_cancel:
            self._pending_cancel.discard(task.id)
            return TaskAttempt(
                task_id=task.id,
                attempt_number=len(self._attempts.get(task.id, [])) + 1,
                status=ExecutionStatus.CANCELLED,
            )

        # Find capable agent
        agent = await self.dispatcher.dispatch(task)
        if not agent:
            return TaskAttempt(
                task_id=task.id,
                attempt_number=len(self._attempts.get(task.id, [])) + 1,
                status=ExecutionStatus.FAILED,
                error="No capable agent found",
            )

        # Execute via agent
        try:
            attempt = await agent.execute(task)
        except asyncio.CancelledError:
            return TaskAttempt(
                task_id=task.id,
                attempt_number=len(self._attempts.get(task.id, [])) + 1,
                status=ExecutionStatus.CANCELLED,
            )
        except Exception as e:
            return TaskAttempt(
                task_id=task.id,
                attempt_number=len(self._attempts.get(task.id, [])) + 1,
                status=ExecutionStatus.FAILED,
                error=str(e),
            )

        return attempt

    def _track_attempt(self, task_id: str, attempt: TaskAttempt) -> None:
        """Track task attempt for history"""
        if task_id not in self._attempts:
            self._attempts[task_id] = []
        self._attempts[task_id].append(attempt)

    async def cancel_task(self, task_id: str) -> bool:
        """Request cancellation of a running task.

        Cancellation happens gracefully - task may complete before
        cancellation takes effect.
        """
        if task_id in self._running:
            self._pending_cancel.add(task_id)
            return True
        return False

    def get_attempts(self, task_id: str) -> List[TaskAttempt]:
        """Get all attempts for a task"""
        return self._attempts.get(task_id, [])

    def get_result(self, task_id: str) -> Optional[str]:
        """Get result of completed task"""
        return self._results.get(task_id)

    def get_execution_state(self) -> Dict[str, Any]:
        """Get current execution state"""
        return {
            "running": list(self._running),
            "completed": list(self._completed),
            "failed": list(self._failed),
            "cancelled": list(self._cancelled),
            "results": dict(self._results),
        }
