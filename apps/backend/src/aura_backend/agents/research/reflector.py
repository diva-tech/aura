"""Reflection logic for ResearchAgent using LLM Runtime."""

import time
from enum import Enum
from typing import Optional

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
from aura_backend.agents.research.plan import Plan, PlanStep
from aura_backend.agents.research.context import ExecutionContext


class ReflectionDecision(str, Enum):
    """Decision from reflection"""

    CONTINUE = "continue"
    RETRY = "retry"
    SKIP = "skip"
    INSERT_STEP = "insert_step"
    REPLAN = "replan"
    COMPLETE = "complete"
    FAIL = "fail"


class Reflector:
    """Reflection using LLM Runtime"""

    def __init__(
        self,
        provider_registry: ProviderRegistry,
        model_registry: ModelRegistry,
    ):
        self.provider_registry = provider_registry
        self.model_registry = model_registry
        self.routing_engine = RoutingEngine(model_registry)

    async def reflect(
        self,
        step: PlanStep,
        plan: Plan,
        context: ExecutionContext,
    ) -> ReflectionDecision:
        """Reflect on step execution and decide next action"""
        start_time = time.time()

        try:
            provider = self.provider_registry.get("anthropic")
            if not provider:
                return ReflectionDecision.CONTINUE

            # Route to best model
            routing_result = await self.routing_engine.route(
                required_capabilities={ModelCapability.REASONING},
                policy=RoutingPolicy(strategy=RoutingStrategy.BALANCED),
            )

            # Create reflection prompt
            reflection_prompt = self._create_reflection_prompt(step, plan, context)

            # Call LLM for reflection
            request = LLMRequest(
                messages=[RequestMessage(role="user", content=reflection_prompt)],
                model=routing_result.model.id,
                temperature=0.7,
                max_tokens=512,
            )

            response = await provider.generate(request)

            # Parse decision
            decision = self._parse_decision(response.message)

            # Update context
            context.reflection_count += 1
            context.total_tokens_used += response.input_tokens + response.output_tokens
            context.total_cost += response.estimated_cost or 0.0
            context.reflection_time_ms = (time.time() - start_time) * 1000
            context.add_llm_response({"role": "reflection", "content": response.message})

            return decision

        except Exception as e:
            # On error, continue execution
            return ReflectionDecision.CONTINUE

    def _create_reflection_prompt(
        self,
        step: PlanStep,
        plan: Plan,
        context: ExecutionContext,
    ) -> str:
        """Create reflection prompt"""
        status = "SUCCESSFUL" if step.status.value == "completed" else "FAILED"
        output = str(step.result.get("output", "No output")) if step.result else "No result"

        prompt = f"""You are an autonomous research agent reflecting on execution.

CURRENT STEP:
- Description: {step.description}
- Status: {status}
- Tool Used: {step.tool_used or "None"}
- Output: {output[:200]}
- Error: {step.error or "None"}

PLAN PROGRESS:
- Total Steps: {len(plan.steps)}
- Completed Steps: {len(plan.completed_steps)}
- Current Index: {plan.current_step_index}
- Success Rate: {plan.success_rate():.1f}%

CONTEXT:
- Goal: {context.goal_description}
- Steps Completed: {len(context.completed_steps)}
- Reflections: {context.reflection_count}
- Replans: {context.replan_count}

DECISION CRITERIA:
1. Was the step successful and did it provide useful information?
2. Have we gathered enough information to answer the goal?
3. Should we retry the step, skip it, or continue?
4. Do we need to modify the plan?
5. Should execution stop (success or failure)?

Respond with ONE decision:
- CONTINUE: Next step in plan
- RETRY: Retry current step
- SKIP: Skip current step and continue
- INSERT_STEP: Need new step before continuing
- REPLAN: Current plan not working, need new plan
- COMPLETE: Goal achieved successfully
- FAIL: Cannot achieve goal, stop execution

DECISION:"""
        return prompt

    def _parse_decision(self, response: str) -> ReflectionDecision:
        """Parse LLM response into decision"""
        text = response.upper()

        if "COMPLETE" in text:
            return ReflectionDecision.COMPLETE
        elif "FAIL" in text:
            return ReflectionDecision.FAIL
        elif "REPLAN" in text:
            return ReflectionDecision.REPLAN
        elif "RETRY" in text:
            return ReflectionDecision.RETRY
        elif "SKIP" in text:
            return ReflectionDecision.SKIP
        elif "INSERT" in text or "INSERT_STEP" in text:
            return ReflectionDecision.INSERT_STEP
        else:
            return ReflectionDecision.CONTINUE
