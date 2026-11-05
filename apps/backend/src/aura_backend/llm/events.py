"""
LLM Runtime Events.

Events published by the LLM runtime for observability.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional
from datetime import datetime

from aura_backend.core.events import BaseEvent


@dataclass
class RequestStartedEvent(BaseEvent):
    """Request started"""

    event_type: str = "llm:request_started"
    model: str = ""
    provider: str = ""
    message_count: int = 0
    request_tokens: Optional[int] = None


@dataclass
class RequestCompletedEvent(BaseEvent):
    """Request completed successfully"""

    event_type: str = "llm:request_completed"
    model: str = ""
    provider: str = ""
    finish_reason: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int = 0
    estimated_cost: float = 0.0


@dataclass
class RequestFailedEvent(BaseEvent):
    """Request failed"""

    event_type: str = "llm:request_failed"
    model: str = ""
    provider: str = ""
    error_message: str = ""
    error_type: str = ""
    latency_ms: int = 0


@dataclass
class StreamingStartedEvent(BaseEvent):
    """Streaming started"""

    event_type: str = "llm:streaming_started"
    model: str = ""
    provider: str = ""


@dataclass
class StreamingCompletedEvent(BaseEvent):
    """Streaming completed"""

    event_type: str = "llm:streaming_completed"
    model: str = ""
    provider: str = ""
    tokens_streamed: int = 0
    total_latency_ms: int = 0
    time_to_first_token_ms: Optional[int] = None


@dataclass
class ProviderUnavailableEvent(BaseEvent):
    """Provider became unavailable"""

    event_type: str = "llm:provider_unavailable"
    provider: str = ""
    reason: str = ""


@dataclass
class RoutingDecisionEvent(BaseEvent):
    """Routing decision made"""

    event_type: str = "llm:routing_decision"
    selected_model: str = ""
    selected_provider: str = ""
    strategy: str = ""
    candidates_count: int = 0
