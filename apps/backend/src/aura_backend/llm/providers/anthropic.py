"""
Anthropic Claude Provider.

Implements the Provider interface for Anthropic's Claude models.

Maps:
- Universal LLMRequest → Claude Messages API format
- Claude API responses → Universal LLMResponse
- Streaming tokens → Universal StreamingToken
- Tool definitions → Claude tool_use format
- Vision/images → Claude image format
"""

from __future__ import annotations

import asyncio
from typing import Any, AsyncIterator, Dict, List, Optional
from datetime import datetime

try:
    from anthropic import Anthropic, AsyncAnthropic
    from anthropic.types import Message, ContentBlock, ToolUseBlock, TextBlock
except ImportError:
    raise ImportError("anthropic package required: pip install anthropic")

from aura_backend.llm.provider import (
    Provider,
    ProviderError,
    ProviderUnavailableError,
    ProviderAuthError,
)
from aura_backend.llm.models import (
    ModelMetadata,
    ModelCapability,
    LLMRequest,
    LLMResponse,
    ResponseContent,
    ToolCall,
    StreamingToken,
    RequestMessage,
)


class AnthropicProvider(Provider):
    """
    Anthropic Claude Provider.

    Supports Claude 3 family (Opus, Sonnet, Haiku).
    """

    # Model definitions (static - these are the models Anthropic exposes)
    MODELS = {
        "claude-3-opus-20240229": {
            "display_name": "Claude 3 Opus",
            "context_window": 200000,
            "max_output_tokens": 4096,
            "capabilities": {
                ModelCapability.VISION,
                ModelCapability.TOOL_CALLING,
                ModelCapability.STREAMING,
                ModelCapability.JSON_MODE,
                ModelCapability.REASONING,
            },
            "input_cost_per_million": 15.0,  # $15 per million input tokens
            "output_cost_per_million": 75.0,  # $75 per million output tokens
            "typical_latency_ms": 500,
        },
        "claude-3-sonnet-20240229": {
            "display_name": "Claude 3 Sonnet",
            "context_window": 200000,
            "max_output_tokens": 4096,
            "capabilities": {
                ModelCapability.VISION,
                ModelCapability.TOOL_CALLING,
                ModelCapability.STREAMING,
                ModelCapability.JSON_MODE,
            },
            "input_cost_per_million": 3.0,
            "output_cost_per_million": 15.0,
            "typical_latency_ms": 300,
        },
        "claude-3-haiku-20240307": {
            "display_name": "Claude 3 Haiku",
            "context_window": 200000,
            "max_output_tokens": 1024,
            "capabilities": {
                ModelCapability.VISION,
                ModelCapability.TOOL_CALLING,
                ModelCapability.STREAMING,
            },
            "input_cost_per_million": 0.80,
            "output_cost_per_million": 4.0,
            "typical_latency_ms": 200,
        },
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Anthropic provider.

        Args:
            config: Configuration dict with:
                - api_key: Anthropic API key (required)
                - timeout: Request timeout (optional)
        """
        super().__init__("anthropic", config)
        self.client: Optional[AsyncAnthropic] = None
        self.timeout = self.config.get("timeout", 30)

    async def initialize(self) -> None:
        """Initialize Anthropic client"""
        if self._initialized:
            return

        api_key = self.config.get("api_key")
        if not api_key:
            raise ProviderAuthError("anthropic api_key required in config")

        try:
            self.client = AsyncAnthropic(api_key=api_key, timeout=self.timeout)
            self._initialized = True
            self._health_status = "healthy"
            await self.health()  # Verify connectivity
        except Exception as e:
            self._health_status = "unavailable"
            raise ProviderAuthError(f"Failed to initialize Anthropic client: {str(e)}")

    async def shutdown(self) -> None:
        """Shutdown provider"""
        if self.client:
            await self.client.close()
        self._initialized = False
        self._health_status = "unknown"

    async def health(self) -> Dict[str, Any]:
        """Check provider health"""
        try:
            if not self.client:
                return {
                    "status": "unavailable",
                    "message": "Client not initialized",
                }

            # Quick health check via list models
            models = await self.list_models()
            self._health_status = "healthy"
            self._last_health_check = datetime.utcnow()

            return {
                "status": "healthy",
                "message": "Anthropic API responsive",
                "models_available": len(models),
            }
        except Exception as e:
            self._health_status = "unavailable"
            return {
                "status": "unavailable",
                "message": f"Health check failed: {str(e)}",
            }

    async def list_models(self) -> List[ModelMetadata]:
        """List available Claude models"""
        models = []
        for model_id, config in self.MODELS.items():
            models.append(
                ModelMetadata(
                    id=model_id,
                    provider="anthropic",
                    display_name=config["display_name"],
                    context_window=config["context_window"],
                    max_output_tokens=config["max_output_tokens"],
                    capabilities=config["capabilities"],
                    input_cost_per_million=config["input_cost_per_million"],
                    output_cost_per_million=config["output_cost_per_million"],
                    typical_latency_ms=config["typical_latency_ms"],
                    availability="available",
                )
            )
        return models

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Generate response from Claude.

        Maps universal LLMRequest to Anthropic API format.
        """
        if not self.client:
            raise ProviderError("Provider not initialized")

        model_id = request.model or "claude-3-sonnet-20240229"

        try:
            # Convert universal request to Anthropic format
            messages = self._map_messages(request.messages)
            kwargs = {
                "model": model_id,
                "messages": messages,
                "max_tokens": request.max_tokens or 2048,
            }

            # System prompt
            if request.system:
                kwargs["system"] = request.system

            # Temperature
            if 0 <= request.temperature <= 1:
                kwargs["temperature"] = request.temperature

            # Tool definitions
            if request.tools:
                kwargs["tools"] = self._map_tools(request.tools)

            # JSON mode - map to Anthropic's format
            if request.json_mode:
                if request.system:
                    kwargs["system"] += "\n\nRespond in valid JSON format."
                else:
                    kwargs["system"] = "Respond in valid JSON format."

            # Call Anthropic API
            response = await self.client.messages.create(**kwargs)

            # Normalize response
            return self._normalize_response(response, model_id, request)

        except Exception as e:
            if "401" in str(e) or "authentication" in str(e).lower():
                raise ProviderAuthError(f"Anthropic authentication failed: {str(e)}")
            elif "overloaded" in str(e).lower() or "rate_limit" in str(e).lower():
                raise ProviderUnavailableError(f"Anthropic rate limited: {str(e)}")
            else:
                raise ProviderError(f"Anthropic API error: {str(e)}")

    async def stream(self, request: LLMRequest) -> AsyncIterator[StreamingToken]:
        """
        Stream response tokens from Claude.

        Maps streaming response to universal StreamingToken format.
        """
        if not self.client:
            raise ProviderError("Provider not initialized")

        model_id = request.model or "claude-3-sonnet-20240229"

        try:
            # Prepare request (similar to generate)
            messages = self._map_messages(request.messages)
            kwargs = {
                "model": model_id,
                "messages": messages,
                "max_tokens": request.max_tokens or 2048,
                "stream": True,
            }

            if request.system:
                kwargs["system"] = request.system

            if 0 <= request.temperature <= 1:
                kwargs["temperature"] = request.temperature

            if request.tools:
                kwargs["tools"] = self._map_tools(request.tools)

            # Stream from Anthropic
            async with self.client.messages.stream(**kwargs) as stream:
                current_tool_use_id = None

                async for event in stream:
                    # Handle different event types
                    if event.type == "content_block_start":
                        if hasattr(event, "content_block"):
                            if hasattr(event.content_block, "id"):
                                current_tool_use_id = event.content_block.id

                    elif event.type == "content_block_delta":
                        if hasattr(event, "delta"):
                            if hasattr(event.delta, "text"):
                                # Text token
                                yield StreamingToken(
                                    token=event.delta.text,
                                    type="text",
                                )
                            elif hasattr(event.delta, "input"):
                                # Tool use input
                                yield StreamingToken(
                                    token=event.delta.input,
                                    type="tool_use_input",
                                    tool_call_id=current_tool_use_id,
                                )

                    elif event.type == "message_stop":
                        # Send finish reason
                        finish_reason = getattr(event, "message", {}).stop_reason or "stop"
                        yield StreamingToken(
                            token="",
                            type="text",
                            finish_reason=finish_reason,
                        )

        except Exception as e:
            raise ProviderError(f"Anthropic streaming error: {str(e)}")

    async def estimate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """Estimate cost for request"""
        if model not in self.MODELS:
            return 0.0

        config = self.MODELS[model]
        input_cost = (input_tokens / 1_000_000) * config["input_cost_per_million"]
        output_cost = (output_tokens / 1_000_000) * config["output_cost_per_million"]
        return input_cost + output_cost

    async def tokenize(self, model: str, text: str) -> List[int]:
        """
        Tokenize text using Anthropic's tokenizer.

        Note: Anthropic doesn't expose a tokenization API publicly.
        This is a placeholder that returns approximate token count.
        """
        # Rough approximation: ~4 chars per token
        approximate_tokens = len(text) // 4
        return list(range(approximate_tokens))

    # ========================================================================
    # PRIVATE METHODS - Mapping between universal and Anthropic formats
    # ========================================================================

    def _map_messages(self, messages: List[RequestMessage]) -> List[Dict[str, Any]]:
        """Map universal RequestMessage to Anthropic message format"""
        anthropic_messages = []

        for msg in messages:
            if msg.role == "system":
                # Anthropic doesn't support system role in messages array
                # System goes in the system parameter
                continue

            content = []

            # Text content
            if msg.content:
                content.append({"type": "text", "text": msg.content})

            # Images
            if msg.images:
                for img in msg.images:
                    if img.base64:
                        content.append(
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": img.media_type or "image/jpeg",
                                    "data": img.base64,
                                },
                            }
                        )
                    elif img.url:
                        content.append(
                            {
                                "type": "image",
                                "source": {
                                    "type": "url",
                                    "url": img.url,
                                },
                            }
                        )

            anthropic_messages.append(
                {
                    "role": msg.role,
                    "content": content,
                }
            )

        return anthropic_messages

    def _map_tools(self, tools: List[Any]) -> List[Dict[str, Any]]:
        """Map universal ToolDefinition to Anthropic tool format"""
        anthropic_tools = []

        for tool in tools:
            anthropic_tools.append(
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.input_schema,
                }
            )

        return anthropic_tools

    def _normalize_response(self, response: Message, model_id: str, request: LLMRequest) -> LLMResponse:
        """Normalize Anthropic Message response to universal LLMResponse"""
        # Extract text and tool calls from response
        text_content = ""
        tool_calls = []
        content_list = []

        for block in response.content:
            if isinstance(block, TextBlock):
                text_content = block.text
                content_list.append(
                    ResponseContent(
                        type="text",
                        text=block.text,
                    )
                )
            elif isinstance(block, ToolUseBlock):
                tool_calls.append(
                    ToolCall(
                        id=block.id,
                        name=block.name,
                        arguments=block.input,
                    )
                )
                content_list.append(
                    ResponseContent(
                        type="tool_use",
                        tool_calls=[
                            ToolCall(
                                id=block.id,
                                name=block.name,
                                arguments=block.input,
                            )
                        ],
                    )
                )

        # Calculate cost
        estimated_cost = await self.estimate_cost(
            model_id,
            response.usage.input_tokens,
            response.usage.output_tokens,
        )

        return LLMResponse(
            message=text_content,
            finish_reason=response.stop_reason or "stop",
            provider="anthropic",
            model=model_id,
            content=content_list,
            tool_calls=tool_calls,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            total_tokens=response.usage.input_tokens + response.usage.output_tokens,
            estimated_cost=estimated_cost,
        )
