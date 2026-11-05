"""Report generation for ResearchAgent."""

from datetime import datetime
from typing import Any, Dict, List

from aura_backend.agents.research.goal import Goal
from aura_backend.agents.research.plan import Plan, PlanStep
from aura_backend.agents.research.context import ExecutionContext


class Reporter:
    """Generates markdown reports from execution"""

    @staticmethod
    def generate_report(
        goal: Goal,
        plan: Plan,
        context: ExecutionContext,
    ) -> str:
        """Generate comprehensive markdown report"""
        lines = []

        # Header
        lines.append(f"# Research Report: {goal.description}\n")
        lines.append(f"**Date**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
        lines.append(f"**Goal ID**: `{goal.id}`\n")
        lines.append(f"**Status**: `{goal.status.value.upper()}`\n\n")

        # Executive Summary
        lines.append("## Executive Summary\n")
        lines.append(f"- **Goal**: {goal.description}\n")
        lines.append(f"- **Success Criteria**: {goal.success_criteria or 'Provide comprehensive information'}\n")
        lines.append(f"- **Status**: {goal.status.value}\n")
        if goal.error:
            lines.append(f"- **Error**: {goal.error}\n")
        lines.append("\n")

        # Execution Timeline
        lines.append("## Execution Timeline\n")
        if goal.started_at:
            start_time = goal.started_at.timestamp()
            end_time = (goal.completed_at or datetime.utcnow()).timestamp()
            duration_seconds = end_time - start_time
            lines.append(f"- **Started**: {goal.started_at.isoformat()}\n")
            if goal.completed_at:
                lines.append(f"- **Completed**: {goal.completed_at.isoformat()}\n")
            lines.append(f"- **Duration**: {duration_seconds:.1f}s ({duration_seconds/60:.1f}m)\n")
        lines.append(f"- **Planning Time**: {context.planning_time_ms/1000:.1f}s\n")
        lines.append(f"- **Execution Time**: {context.execution_time_ms/1000:.1f}s\n")
        lines.append(f"- **Reflection Time**: {context.reflection_time_ms/1000:.1f}s\n")
        lines.append("\n")

        # Plan Overview
        lines.append("## Plan Overview\n")
        lines.append(f"- **Total Steps**: {len(plan.steps)}\n")
        lines.append(f"- **Completed**: {len([s for s in plan.steps if s.status.value == 'completed'])}\n")
        lines.append(f"- **Failed**: {len([s for s in plan.steps if s.status.value == 'failed'])}\n")
        lines.append(f"- **Skipped**: {len([s for s in plan.steps if s.status.value == 'skipped'])}\n")
        lines.append(f"- **Success Rate**: {plan.success_rate():.1f}%\n")
        lines.append("\n")

        # Step Details
        lines.append("## Execution Steps\n\n")
        for i, step in enumerate(plan.steps, 1):
            lines.extend(Reporter._format_step(step, i))

        # Tool Usage Summary
        lines.append("## Tool Usage Summary\n")
        tool_usage: Dict[str, int] = {}
        for step in plan.steps:
            if step.tool_used:
                tool_usage[step.tool_used] = tool_usage.get(step.tool_used, 0) + 1

        for tool, count in sorted(tool_usage.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"- **{tool}**: {count} times\n")
        lines.append(f"\n**Total Tool Calls**: {context.tool_call_count}\n\n")

        # LLM Usage
        lines.append("## LLM Usage\n")
        lines.append(f"- **Total Tokens**: {context.total_tokens_used}\n")
        lines.append(f"- **Estimated Cost**: ${context.total_cost:.6f}\n")
        lines.append(f"- **LLM Calls**: {len(context.llm_responses)}\n")
        lines.append(f"- **Reflections**: {context.reflection_count}\n")
        lines.append(f"- **Replans**: {context.replan_count}\n\n")

        # Key Findings
        if context.working_memory:
            lines.append("## Key Findings\n")
            for key, value in context.working_memory.items():
                if not key.startswith("_"):
                    lines.append(f"### {key}\n")
                    lines.append(f"```\n{value}\n```\n\n")

        # Conclusion
        lines.append("## Conclusion\n")
        if goal.status.value == "completed":
            lines.append("✅ Goal completed successfully.\n\n")
        elif goal.status.value == "failed":
            lines.append(f"❌ Goal failed: {goal.error}\n\n")
        else:
            lines.append(f"⚠️ Goal status: {goal.status.value}\n\n")

        return "".join(lines)

    @staticmethod
    def _format_step(step: PlanStep, index: int) -> List[str]:
        """Format a single step as markdown"""
        lines = []

        status_icon = {
            "completed": "✅",
            "failed": "❌",
            "skipped": "⊘",
            "pending": "⏳",
            "running": "▶️",
        }.get(step.status.value, "•")

        lines.append(f"### Step {index}: {status_icon} {step.description}\n")
        lines.append(f"**Reason**: {step.reason}\n\n")
        lines.append(f"**Status**: `{step.status.value}`\n")
        if step.tool_used:
            lines.append(f"**Tool Used**: {step.tool_used}\n")
        if step.duration_ms() is not None:
            lines.append(f"**Duration**: {step.duration_ms():.0f}ms\n")
        if step.retry_count > 0:
            lines.append(f"**Retries**: {step.retry_count}\n")

        if step.error:
            lines.append(f"**Error**: {step.error}\n")

        if step.result:
            output = step.result.get("output", "")
            if output:
                output_str = str(output)[:500]
                lines.append(f"\n**Output**:\n```\n{output_str}\n```\n")

        lines.append("\n")
        return lines

    @staticmethod
    def generate_summary(
        goal: Goal,
        plan: Plan,
        context: ExecutionContext,
    ) -> Dict[str, Any]:
        """Generate structured summary"""
        return {
            "goal_id": goal.id,
            "goal": goal.description,
            "status": goal.status.value,
            "duration_seconds": (
                (goal.completed_at or datetime.utcnow()).timestamp() - goal.started_at.timestamp()
                if goal.started_at
                else 0
            ),
            "steps": {
                "total": len(plan.steps),
                "completed": len([s for s in plan.steps if s.status.value == "completed"]),
                "failed": len([s for s in plan.steps if s.status.value == "failed"]),
                "skipped": len([s for s in plan.steps if s.status.value == "skipped"]),
            },
            "llm": {
                "total_tokens": context.total_tokens_used,
                "estimated_cost": context.total_cost,
                "calls": len(context.llm_responses),
            },
            "tools": {
                "calls": context.tool_call_count,
            },
            "reflections": context.reflection_count,
            "replans": context.replan_count,
        }
