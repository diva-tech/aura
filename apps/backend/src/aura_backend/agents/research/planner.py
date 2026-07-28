"""Planning logic for ResearchAgent using LLM Runtime."""

import time
from typing import List

from aura_backend.llm import (
    LLMRequest,
    RequestMessage,
    ModelCapability,
    ProviderRegistry,
    ModelRegistry,
    RoutingEngine,
    RoutingPolicy,
    RoutingStrategy,
)
from aura_backend.agents.research.goal import Goal
from aura_backend.agents.research.plan import Plan, PlanStep, StepToolType
from aura_backend.agents.research.context import ExecutionContext


class Planner:
    """Planning using LLM Runtime"""

    def __init__(
        self,
        provider_registry: ProviderRegistry,
        model_registry: ModelRegistry,
    ):
        self.provider_registry = provider_registry
        self.model_registry = model_registry
        self.routing_engine = RoutingEngine(model_registry)

    async def create_plan(self, goal: Goal, context: ExecutionContext) -> Plan:
        """Create execution plan using LLM"""
        start_time = time.time()

        try:
            # Get provider for planning
            provider = self.provider_registry.get("anthropic")
            if not provider:
                raise ValueError("No LLM provider available for planning")

            # Route to best model
            routing_result = await self.routing_engine.route(
                required_capabilities={ModelCapability.REASONING},
                policy=RoutingPolicy(strategy=RoutingStrategy.BALANCED),
            )

            # Create planning prompt
            planning_prompt = self._create_planning_prompt(goal, context)

            # Call LLM for planning
            request = LLMRequest(
                messages=[RequestMessage(role="user", content=planning_prompt)],
                model=routing_result.model.id,
                temperature=0.5,
                max_tokens=2048,
            )

            response = await provider.generate(request)

            # Parse response into steps
            plan = self._parse_plan(response.message, goal)

            # Update context with tokens
            context.total_tokens_used += response.input_tokens + response.output_tokens
            context.total_cost += response.estimated_cost or 0.0

            context.planning_time_ms = (time.time() - start_time) * 1000
            context.add_llm_response({"role": "planning", "content": response.message})

            return plan

        except Exception as e:
            raise RuntimeError(f"Planning failed: {str(e)}")

    def _create_planning_prompt(self, goal: Goal, context: ExecutionContext) -> str:
        """Create planning prompt for LLM"""
        prompt = f"""You are an autonomous research agent. Create a detailed execution plan.

GOAL: {goal.description}

CONTEXT: {goal.context or "No additional context"}

SUCCESS CRITERIA: {goal.success_criteria or "Provide comprehensive information"}

CONSTRAINTS:
- Maximum {goal.max_steps} steps
- Each step must be specific and actionable
- Steps should use: Browser (web search/browsing), Filesystem (file operations), Python (computation/analysis)
- Steps should be sequential

OUTPUT FORMAT:
Create exactly {min(5, goal.max_steps)} steps with this format for each:
STEP N:
DESCRIPTION: [what to do]
REASON: [why it matters for the goal]
CAPABILITIES: [required capabilities from: vision, search, analysis, computation]
EXPECTED_OUTPUT: [what should result]
TOOLS: [hints: browser, filesystem, python]
PRIORITY: [1-10]

Now create the plan:"""
        return prompt

    def _parse_plan(self, response: str, goal: Goal) -> Plan:
        """Parse LLM response into Plan"""
        plan = Plan()

        lines = response.split("\n")
        step_lines = []
        current_step = None

        for line in lines:
            if line.startswith("STEP"):
                if current_step:
                    step_lines.append(current_step)
                current_step = [line]
            elif current_step is not None:
                current_step.append(line)

        if current_step:
            step_lines.append(current_step)

        # Parse each step
        for step_text in step_lines:
            try:
                step = self._parse_step(step_text)
                if step:
                    plan.add_step(step)
            except Exception:
                pass

        # Ensure at least one step
        if not plan.steps:
            step = PlanStep(
                description=f"Research: {goal.description}",
                reason="Default step to gather information",
                expected_output="Research findings",
                tool_hints=[StepToolType.BROWSER],
            )
            plan.add_step(step)

        return plan

    def _parse_step(self, step_text) -> PlanStep:
        """Parse a single step from LLM response"""
        text = "\n".join(step_text)

        description = self._extract_value(text, "DESCRIPTION:")
        reason = self._extract_value(text, "REASON:")
        expected_output = self._extract_value(text, "EXPECTED_OUTPUT:")
        tools = self._extract_value(text, "TOOLS:")
        priority_str = self._extract_value(text, "PRIORITY:")

        priority = int(priority_str) if priority_str else 5

        # Map tools
        tool_hints = []
        if tools:
            if "browser" in tools.lower():
                tool_hints.append(StepToolType.BROWSER)
            if "filesystem" in tools.lower():
                tool_hints.append(StepToolType.FILESYSTEM)
            if "python" in tools.lower():
                tool_hints.append(StepToolType.PYTHON)

        if not tool_hints:
            tool_hints = [StepToolType.ANY]

        return PlanStep(
            description=description,
            reason=reason,
            expected_output=expected_output,
            tool_hints=tool_hints,
            priority=priority,
        )

    def _extract_value(self, text: str, key: str) -> str:
        """Extract value after key in text"""
        if key not in text:
            return ""
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if key in line:
                value = line.split(key, 1)[-1].strip()
                return value
        return ""
