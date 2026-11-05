"""
Request Pipeline.

Validates and processes LLM requests through middleware/hooks.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, List, Optional, Dict
from datetime import datetime

from aura_backend.llm.models import LLMRequest, LLMResponse
from aura_backend.llm.provider import Provider
from aura_backend.core.events import BaseEventBus


class PipelineError(Exception):
    """Pipeline execution error"""

    pass


@dataclass
class PipelineContext:
    """Context for pipeline execution"""

    request: LLMRequest
    provider: Optional[Provider] = None
    selected_model: Optional[str] = None
    response: Optional[LLMResponse] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class RequestPipeline:
    """
    Request pipeline with hooks.

    Stages:
    1. Validation hook
    2. Policy hook
    3. Caching hook (placeholder)
    4. Routing (select provider/model)
    5. Retry hook (placeholder)
    6. Rate limiting hook (placeholder)
    7. Provider execution
    8. Response normalization
    9. Metrics hook
    """

    def __init__(self, event_bus: Optional[BaseEventBus] = None):
        self.event_bus = event_bus
        self._validation_hooks: List[Callable[[LLMRequest], None]] = []
        self._policy_hooks: List[Callable[[PipelineContext], None]] = []
        self._caching_hooks: List[Callable[[PipelineContext], Optional[LLMResponse]]] = []
        self._retry_hooks: List[Callable[[PipelineContext], int]] = []  # Returns max retries
        self._rate_limit_hooks: List[Callable[[PipelineContext], None]] = []
        self._metrics_hooks: List[Callable[[PipelineContext], None]] = []

    def add_validation_hook(self, hook: Callable[[LLMRequest], None]) -> None:
        """Add validation hook"""
        self._validation_hooks.append(hook)

    def add_policy_hook(self, hook: Callable[[PipelineContext], None]) -> None:
        """Add policy hook"""
        self._policy_hooks.append(hook)

    def add_caching_hook(self, hook: Callable[[PipelineContext], Optional[LLMResponse]]) -> None:
        """Add caching hook"""
        self._caching_hooks.append(hook)

    def add_retry_hook(self, hook: Callable[[PipelineContext], int]) -> None:
        """Add retry hook"""
        self._retry_hooks.append(hook)

    def add_rate_limit_hook(self, hook: Callable[[PipelineContext], None]) -> None:
        """Add rate limit hook"""
        self._rate_limit_hooks.append(hook)

    def add_metrics_hook(self, hook: Callable[[PipelineContext], None]) -> None:
        """Add metrics hook"""
        self._metrics_hooks.append(hook)

    async def execute(self, context: PipelineContext) -> LLMResponse:
        """
        Execute pipeline.

        Args:
            context: Pipeline context with request

        Returns:
            LLMResponse

        Raises:
            PipelineError: On pipeline failure
        """
        # Validation
        for hook in self._validation_hooks:
            hook(context.request)

        # Policy
        for hook in self._policy_hooks:
            hook(context)

        # Caching (placeholder)
        for hook in self._caching_hooks:
            cached = hook(context)
            if cached:
                return cached

        # Rate limiting (placeholder)
        for hook in self._rate_limit_hooks:
            hook(context)

        # Retry logic (placeholder)
        max_retries = 1
        for hook in self._retry_hooks:
            max_retries = max(max_retries, hook(context))

        # Execute with retries
        last_error = None
        for attempt in range(max_retries):
            try:
                if not context.provider:
                    raise PipelineError("No provider selected")

                # Execute provider
                response = await context.provider.generate(context.request)
                context.response = response

                # Metrics (placeholder)
                for hook in self._metrics_hooks:
                    hook(context)

                return response

            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise PipelineError(f"Pipeline failed after {max_retries} retries: {str(e)}")

        raise PipelineError(f"Pipeline failed: {str(last_error)}")


import asyncio
