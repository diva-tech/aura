"""Execution logic for ResearchAgent using Tool Platform."""

import time
from typing import Any, Dict, Optional

from aura_backend.ai.tools import ToolRegistry
from aura_backend.agents.research.plan import PlanStep, StepStatus, StepToolType
from aura_backend.agents.research.context import ExecutionContext


class StepExecutor:
    """Executes individual plan steps using available tools"""

    def __init__(self, tool_registry: ToolRegistry):
        self.tool_registry = tool_registry

    async def execute_step(
        self,
        step: PlanStep,
        context: ExecutionContext,
    ) -> bool:
        """Execute a single step"""
        start_time = time.time()
        step.started_at = time.time()
        step.status = StepStatus.RUNNING

        try:
            # Select tool based on hints
            tool = self._select_tool(step)
            if not tool:
                step.status = StepStatus.FAILED
                step.error = "No suitable tool found"
                return False

            # Prepare tool invocation
            tool_input = self._prepare_tool_input(step, context)

            # Execute tool
            result = await tool.execute(**tool_input)

            # Record result
            if result.success:
                step.status = StepStatus.COMPLETED
                step.result = {"output": result.data, "artifacts": result.artifacts}
                step.tool_used = tool.get_name()

                # Add to context
                context.add_tool_output(tool.get_name(), result.data)
                context.tool_call_count += 1

                # Update memory
                context.update_memory(f"step_{step.id}_output", result.data)

                elapsed_ms = (time.time() - start_time) * 1000
                step.completed_at = time.time()
                context.execution_time_ms += elapsed_ms

                return True
            else:
                step.status = StepStatus.FAILED
                step.error = ", ".join(result.errors) if result.errors else "Tool execution failed"
                return False

        except Exception as e:
            step.status = StepStatus.FAILED
            step.error = str(e)
            return False
        finally:
            if step.completed_at is None:
                step.completed_at = time.time()

    def _select_tool(self, step: PlanStep):
        """Select best tool for step"""
        tools = self.tool_registry.list()

        # Filter by tool hints
        for hint in step.tool_hints:
            if hint == StepToolType.BROWSER:
                for tool in tools:
                    if tool.get_name() == "BrowserTool":
                        return tool
            elif hint == StepToolType.FILESYSTEM:
                for tool in tools:
                    if tool.get_name() == "FilesystemTool":
                        return tool
            elif hint == StepToolType.PYTHON:
                for tool in tools:
                    if tool.get_name() == "PythonTool":
                        return tool

        # Return first tool if no specific hint
        return tools[0] if tools else None

    def _prepare_tool_input(self, step: PlanStep, context: ExecutionContext) -> Dict[str, Any]:
        """Prepare input for tool invocation"""
        tool_name = self._select_tool(step).get_name() if self._select_tool(step) else "unknown"

        if tool_name == "BrowserTool":
            return {
                "url": context.get_memory("search_query", f"Search: {step.description}"),
            }
        elif tool_name == "FilesystemTool":
            return {
                "path": context.get_memory("file_path", "./research_data"),
                "operation": "read",
            }
        elif tool_name == "PythonTool":
            return {
                "code": f"# {step.description}\n# TODO: Implement analysis",
            }
        else:
            return {}

    async def retry_step(self, step: PlanStep, context: ExecutionContext) -> bool:
        """Retry a failed step"""
        if not step.can_retry():
            return False

        step.retry_count += 1
        step.status = StepStatus.RETRYING

        return await self.execute_step(step, context)
