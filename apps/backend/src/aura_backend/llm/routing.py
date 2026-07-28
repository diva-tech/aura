"""
Routing Engine.

Intelligent model selection based on capabilities, cost, latency, availability.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List
from enum import Enum

from aura_backend.llm.models import ModelCapability, ModelMetadata
from aura_backend.llm.registry import ModelRegistry


class RoutingStrategy(str, Enum):
    """Routing strategy"""

    CHEAPEST = "cheapest"
    FASTEST = "fastest"
    BALANCED = "balanced"  # Balance cost and speed
    PREFERRED = "preferred"  # Use preferred provider
    CAPABLE = "capable"  # Any model with capabilities


@dataclass
class CapabilitySet:
    """Set of required capabilities"""

    vision: bool = False
    tool_calling: bool = False
    streaming: bool = False
    json_mode: bool = False
    reasoning: bool = False
    embeddings: bool = False
    audio: bool = False
    images: bool = False

    def to_model_capabilities(self) -> set[ModelCapability]:
        """Convert to ModelCapability set"""
        caps = set()
        if self.vision:
            caps.add(ModelCapability.VISION)
        if self.tool_calling:
            caps.add(ModelCapability.TOOL_CALLING)
        if self.streaming:
            caps.add(ModelCapability.STREAMING)
        if self.json_mode:
            caps.add(ModelCapability.JSON_MODE)
        if self.reasoning:
            caps.add(ModelCapability.REASONING)
        if self.embeddings:
            caps.add(ModelCapability.EMBEDDINGS)
        if self.audio:
            caps.add(ModelCapability.AUDIO)
        if self.images:
            caps.add(ModelCapability.IMAGES)
        return caps


@dataclass
class RoutingPolicy:
    """Routing policy configuration"""

    strategy: RoutingStrategy = RoutingStrategy.BALANCED
    preferred_providers: List[str] = None
    max_latency_ms: Optional[int] = None
    prefer_cheaper: bool = False
    min_availability: str = "available"

    def __post_init__(self):
        if self.preferred_providers is None:
            self.preferred_providers = []


@dataclass
class RoutingResult:
    """Result of routing decision"""

    model: ModelMetadata
    reason: str
    score: float
    alternatives: List[ModelMetadata]


class RoutingEngine:
    """
    Route requests to appropriate models.

    Selects models based on:
    - Required capabilities
    - Cost preference
    - Latency preference
    - Provider availability
    - Context window requirement
    """

    def __init__(self, registry: ModelRegistry):
        self.registry = registry

    async def route(
        self,
        required_capabilities: set[ModelCapability],
        policy: RoutingPolicy = None,
        context_length: Optional[int] = None,
    ) -> RoutingResult:
        """
        Route to best model.

        Args:
            required_capabilities: Required capabilities
            policy: Routing policy
            context_length: Minimum context window

        Returns:
            RoutingResult with selected model
        """
        policy = policy or RoutingPolicy()

        # Find candidates with required capabilities
        candidates = self.registry.find_by_capabilities(required_capabilities)

        # Filter by context length
        if context_length:
            candidates = [m for m in candidates if m.context_window >= context_length]

        # Filter by availability
        candidates = [m for m in candidates if m.availability == policy.min_availability]

        # Filter by latency
        if policy.max_latency_ms:
            candidates = [m for m in candidates if m.typical_latency_ms <= policy.max_latency_ms]

        if not candidates:
            raise ValueError("No models available with required capabilities")

        # Score candidates based on strategy
        if policy.strategy == RoutingStrategy.CHEAPEST:
            selected = self._score_cheapest(candidates)
        elif policy.strategy == RoutingStrategy.FASTEST:
            selected = self._score_fastest(candidates)
        elif policy.strategy == RoutingStrategy.BALANCED:
            selected = self._score_balanced(candidates)
        elif policy.strategy == RoutingStrategy.PREFERRED:
            selected = self._score_preferred(candidates, policy.preferred_providers)
        else:
            selected = self._score_capable(candidates)

        return RoutingResult(
            model=selected,
            reason=f"Selected via {policy.strategy.value} strategy",
            score=1.0,
            alternatives=candidates[:5],  # Top 5 alternatives
        )

    def _score_cheapest(self, candidates: List[ModelMetadata]) -> ModelMetadata:
        """Score models by cost"""
        return min(
            candidates,
            key=lambda m: m.input_cost_per_million + m.output_cost_per_million,
        )

    def _score_fastest(self, candidates: List[ModelMetadata]) -> ModelMetadata:
        """Score models by latency"""
        return min(candidates, key=lambda m: m.typical_latency_ms)

    def _score_balanced(self, candidates: List[ModelMetadata]) -> ModelMetadata:
        """Score models by balanced cost/latency"""
        # Normalize scores (cost + latency weighted equally)
        max_cost = max(m.input_cost_per_million + m.output_cost_per_million for m in candidates)
        max_latency = max(m.typical_latency_ms for m in candidates) or 1

        def score(m: ModelMetadata) -> float:
            cost_score = (m.input_cost_per_million + m.output_cost_per_million) / max_cost
            latency_score = m.typical_latency_ms / max_latency
            return cost_score * 0.5 + latency_score * 0.5

        return min(candidates, key=score)

    def _score_preferred(self, candidates: List[ModelMetadata], preferred: List[str]) -> ModelMetadata:
        """Score models by provider preference"""
        # Preferred providers first
        for provider in preferred:
            for m in candidates:
                if m.provider == provider:
                    return m
        # Fall back to first available
        return candidates[0]

    def _score_capable(self, candidates: List[ModelMetadata]) -> ModelMetadata:
        """Just pick first capable model"""
        return candidates[0]
