"""Task planner - converts goals to execution plans and task graphs.

Reuses existing AI Framework (M3) Goal and Plan interfaces.
"""

from typing import Dict, List, Optional, Set

from aura_backend.orchestration.models import (
    Capability,
    ExecutionPlan,
    Skill,
    Task,
    TaskGraph,
    ToolRequirement,
)


class TaskPlanner:
    """Converts high-level goals to execution plans and task graphs.

    Uses AI Framework to generate task decomposition.
    """

    def __init__(self):
        """Initialize planner"""
        pass

    async def create_execution_plan(
        self,
        goal_description: str,
        goal_id: str = "",
    ) -> ExecutionPlan:
        """Create an execution plan from a goal.

        Args:
            goal_description: What needs to be accomplished
            goal_id: Optional goal ID from M3 Framework

        Returns:
            ExecutionPlan with ordered tasks
        """
        # In a real implementation, this would use M3 AI Framework
        # to generate a plan via an LLM call.
        # For now, we create a simple plan structure.

        tasks = await self._decompose_goal(goal_description)

        plan = ExecutionPlan(
            goal_id=goal_id,
            goal_description=goal_description,
            tasks=tasks,
            strategy="sequential",
        )

        return plan

    async def create_task_graph(
        self,
        plan: ExecutionPlan,
    ) -> TaskGraph:
        """Create a task graph from an execution plan.

        Determines dependencies and execution order.

        Args:
            plan: ExecutionPlan with tasks

        Returns:
            TaskGraph with dependency edges
        """
        nodes = {task.id: task for task in plan.tasks}
        edges: Dict[str, List[str]] = {}

        # For sequential execution: each task depends on previous
        for i, task in enumerate(plan.tasks):
            edges[task.id] = []
            if i > 0:
                # Current task depends on previous
                prev_task = plan.tasks[i - 1]
                # Find who depends on previous
                if prev_task.id not in edges:
                    edges[prev_task.id] = []
                edges[prev_task.id].append(task.id)

        # Entry nodes: tasks with no dependencies
        entry_nodes = [task.id for task in plan.tasks if i == 0 for i in range(1)]
        if plan.tasks:
            entry_nodes = [plan.tasks[0].id]

        # Exit nodes: tasks with no dependents
        exit_nodes = []
        for task_id, dependents in edges.items():
            if not dependents:
                exit_nodes.append(task_id)
        if not exit_nodes and plan.tasks:
            exit_nodes = [plan.tasks[-1].id]

        graph = TaskGraph(
            plan_id=plan.id,
            nodes=nodes,
            edges=edges,
            entry_nodes=entry_nodes,
            exit_nodes=exit_nodes,
        )

        return graph

    async def _decompose_goal(self, goal: str) -> List[Task]:
        """Decompose a goal into tasks.

        In production, this would use M3 AI Framework (LLM-based planning).
        For now, simple heuristic-based decomposition.
        """
        # This is a placeholder implementation.
        # Real implementation would:
        # 1. Call M3 AI Framework
        # 2. Generate structured plan via LLM
        # 3. Extract tasks with capabilities/skills/tools

        # Example: "Research Python async and summarize"
        tasks = [
            Task(
                goal="Research Python async patterns",
                description="Search for and analyze Python async/await patterns",
                priority=10,
                required_capabilities={Capability.RESEARCH, Capability.ANALYSIS},
                required_skills={Skill.WEB_SEARCH, Skill.DOCUMENT_ANALYSIS},
                required_tools={ToolRequirement.GOOGLE_SEARCH, ToolRequirement.CLAUDE_API},
            ),
            Task(
                goal="Summarize findings",
                description="Create a concise summary of research findings",
                priority=9,
                required_capabilities={Capability.SUMMARIZATION},
                required_skills={Skill.LLM_SYNTHESIS},
                required_tools={ToolRequirement.CLAUDE_API},
            ),
        ]

        return tasks
