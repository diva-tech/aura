"""
Universal LLM request/response models.

These models are provider-agnostic and form the contract between
the runtime and individual providers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Literal, Union
from datetime import datetime
from enum import Enum


# ============================================================================
# CAPABILITY MODELS
# ============================================================================

class ModelCapability(str, Enum):
    """Supported model capabilities"""

    VISION = "vision"
    TOOL_CALLING = "tool_calling"
    STREAMING = "streaming"
    JSON_MODE = "json_mode"
    REASONING = "reasoning"
    EMBEDDINGS = "embeddings"
    AUDIO = "audio"
    IMAGES = "images"
    FUNCTION_CALLING = "function_calling"


@dataclass
class ModelMetadata:
    """Metadata for a single model"""

    id: str
    provider: str
    display_name: str
    description: str = ""
    context_window: int = 4096
    max_output_tokens: int = 2048
    capabilities: set[ModelCapability] = field(default_factory=set)
    input_cost_per_million: float = 0.0  # Cost per million tokens
    output_cost_per_million: float = 0.0
    typical_latency_ms: int = 0
    availability: Literal["available", "limited", "unavailable"] = "available"
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def supports_capability(self, capability: ModelCapability) -> bool:
        """Check if model supports capability"""
        return capability in self.capabilities

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict"""
        return {
            "id": self.id,
            "provider": self.provider,
            "display_name": self.display_name,
            "description": self.description,
            "context_window": self.context_window,
            "max_output_tokens": self.max_output_tokens,
            "capabilities": [cap.value for cap in self.capabilities],
            "input_cost_per_million": self.input_cost_per_million,
            "output_cost_per_million": self.output_cost_per_million,
            "typical_latency_ms": self.typical_latency_ms,
            "availability": self.availability,
            "metadata": self.metadata,
        }


# ============================================================================
# REQUEST MODELS
# ============================================================================

@dataclass
class RequestMessage:
    """Single message in conversation"""

    role: Literal["user", "assistant", "system"]
    content: str
    images: List[RequestImage] = field(default_factory=list)
    audio: Optional[RequestAudio] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RequestImage:
    """Image content in request"""

    url: Optional[str] = None
    base64: Optional[str] = None
    media_type: str = "image/jpeg"
    description: Optional[str] = None


@dataclass
class RequestAudio:
    """Audio content in request"""

    url: Optional[str] = None
    base64: Optional[str] = None
    media_type: str = "audio/wav"
    sample_rate: Optional[int] = None


@dataclass
class ToolDefinition:
    """Tool that model can call"""

    name: str
    description: str
    input_schema: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMRequest:
    """Universal LLM request"""

    messages: List[RequestMessage]
    model: Optional[str] = None  # Can be None for capability-based routing
    system: Optional[str] = None
    temperature: float = 0.7
    top_p: float = 1.0
    max_tokens: Optional[int] = None
    json_mode: bool = False
    tools: List[ToolDefinition] = field(default_factory=list)
    response_format: Optional[str] = None  # "text", "json", "xml", etc.

    # Metadata
    correlation_id: str = ""
    session_id: str = ""
    trace_id: str = ""

    # Routing preferences
    preferred_providers: List[str] = field(default_factory=list)
    required_capabilities: set[ModelCapability] = field(default_factory=set)
    max_latency_ms: Optional[int] = None
    prefer_cheaper: bool = False

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict"""
        return {
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "images": [
                        {
                            "url": img.url,
                            "base64": img.base64,
                            "media_type": img.media_type,
                            "description": img.description,
                        }
                        for img in msg.images
                    ],
                    "audio": {
                        "url": msg.audio.url,
                        "base64": msg.audio.base64,
                        "media_type": msg.audio.media_type,
                        "sample_rate": msg.audio.sample_rate,
                    } if msg.audio else None,
                    "metadata": msg.metadata,
                }
                for msg in self.messages
            ],
            "model": self.model,
            "system": self.system,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens,
            "json_mode": self.json_mode,
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.input_schema,
                }
                for tool in self.tools
            ],
            "response_format": self.response_format,
            "correlation_id": self.correlation_id,
            "session_id": self.session_id,
            "trace_id": self.trace_id,
        }


# ============================================================================
# RESPONSE MODELS
# ============================================================================

@dataclass
class ResponseContent:
    """Response content"""

    type: Literal["text", "tool_use", "json"]
    text: Optional[str] = None
    tool_calls: List[ToolCall] = field(default_factory=list)
    citations: List[str] = field(default_factory=list)


@dataclass
class ToolCall:
    """Tool call in response"""

    id: str
    name: str
    arguments: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMResponse:
    """Universal LLM response"""

    message: str
    finish_reason: Literal["stop", "max_tokens", "tool_use", "length"]
    provider: str
    model: str
    content: List[ResponseContent] = field(default_factory=list)
    tool_calls: List[ToolCall] = field(default_factory=list)
    citations: List[str] = field(default_factory=list)

    # Usage tracking
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0

    # Cost
    estimated_cost: float = 0.0

    # Performance
    latency_ms: int = 0
    time_to_first_token_ms: Optional[int] = None

    # Metadata
    correlation_id: str = ""
    session_id: str = ""
    trace_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict"""
        return {
            "message": self.message,
            "finish_reason": self.finish_reason,
            "provider": self.provider,
            "model": self.model,
            "content": [
                {
                    "type": c.type,
                    "text": c.text,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "name": tc.name,
                            "arguments": tc.arguments,
                        }
                        for tc in c.tool_calls
                    ],
                    "citations": c.citations,
                }
                for c in self.content
            ],
            "tool_calls": [
                {
                    "id": tc.id,
                    "name": tc.name,
                    "arguments": tc.arguments,
                }
                for tc in self.tool_calls
            ],
            "citations": self.citations,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "estimated_cost": self.estimated_cost,
            "latency_ms": self.latency_ms,
            "time_to_first_token_ms": self.time_to_first_token_ms,
            "correlation_id": self.correlation_id,
            "session_id": self.session_id,
            "trace_id": self.trace_id,
            "created_at": self.created_at.isoformat(),
        }


# ============================================================================
# STREAMING MODELS
# ============================================================================

@dataclass
class StreamingToken:
    """Single token in streaming response"""

    token: str
    type: Literal["text", "start_tool_use", "tool_use_input", "end_tool_use"]
    tool_call_id: Optional[str] = None
    finish_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
