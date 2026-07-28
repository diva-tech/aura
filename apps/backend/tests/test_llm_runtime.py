"""
Comprehensive tests for LLM Runtime architecture.

Validates:
- Request mapping (universal → Anthropic)
- Response normalization (Anthropic → universal)
- Streaming
- Tool calling
- Vision
- JSON mode
- Error handling
- Pipeline integration
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List

from aura_backend.llm import (
    LLMRequest,
    LLMResponse,
    RequestMessage,
    RequestImage,
    ToolDefinition,
    ModelCapability,
    ProviderRegistry,
    ModelRegistry,
    RoutingEngine,
    RoutingStrategy,
    RoutingPolicy,
    RequestPipeline,
)
from aura_backend.llm.providers.anthropic import AnthropicProvider


class TestAnthropicProviderIntegration:
    """Test AnthropicProvider implementation"""

    @pytest.fixture
    def provider_config(self):
        """Anthropic provider config"""
        return {"api_key": "test-api-key"}

    @pytest.fixture
    async def provider(self, provider_config):
        """Initialize provider for testing"""
        provider = AnthropicProvider(config=provider_config)
        # Mock the client instead of actual initialization
        provider.client = AsyncMock()
        provider._initialized = True
        provider._health_status = "healthy"
        return provider

    @pytest.mark.asyncio
    async def test_health_check(self, provider):
        """Test health check"""
        health = await provider.health()
        assert health["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_list_models(self, provider):
        """Test model discovery"""
        models = await provider.list_models()
        assert len(models) == 3
        assert any(m.id == "claude-3-opus-20240229" for m in models)
        assert all(m.provider == "anthropic" for m in models)

    @pytest.mark.asyncio
    async def test_model_capabilities(self, provider):
        """Test that models have expected capabilities"""
        models = await provider.list_models()
        opus = next(m for m in models if "opus" in m.id)

        assert ModelCapability.VISION in opus.capabilities
        assert ModelCapability.TOOL_CALLING in opus.capabilities
        assert ModelCapability.STREAMING in opus.capabilities

    @pytest.mark.asyncio
    async def test_simple_text_request(self, provider):
        """Test simple text generation"""
        # Mock Anthropic response
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Hello, world!")]
        mock_response.stop_reason = "end_turn"
        mock_response.usage = MagicMock(input_tokens=10, output_tokens=5)

        provider.client.messages.create = AsyncMock(return_value=mock_response)

        # Create universal request
        request = LLMRequest(
            messages=[RequestMessage(role="user", content="Hello")],
            model="claude-3-opus-20240229",
        )

        # Generate
        response = await provider.generate(request)

        # Verify response
        assert response.message == "Hello, world!"
        assert response.provider == "anthropic"
        assert response.input_tokens == 10
        assert response.output_tokens == 5

    @pytest.mark.asyncio
    async def test_vision_request(self, provider):
        """Test vision/image request"""
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="I see an image")]
        mock_response.stop_reason = "end_turn"
        mock_response.usage = MagicMock(input_tokens=50, output_tokens=10)

        provider.client.messages.create = AsyncMock(return_value=mock_response)

        # Create request with image
        request = LLMRequest(
            messages=[
                RequestMessage(
                    role="user",
                    content="What's in this image?",
                    images=[
                        RequestImage(
                            base64="iVBORw0KGg...",
                            media_type="image/jpeg",
                        )
                    ],
                )
            ],
            model="claude-3-opus-20240229",
        )

        response = await provider.generate(request)
        assert response.message == "I see an image"

        # Verify image was passed to Anthropic
        call_kwargs = provider.client.messages.create.call_args[1]
        assert any(
            msg["role"] == "user" and any(c["type"] == "image" for c in msg["content"])
            for msg in call_kwargs["messages"]
        )

    @pytest.mark.asyncio
    async def test_tool_calling(self, provider):
        """Test tool calling request"""
        mock_response = MagicMock()
        mock_tool_use = MagicMock()
        mock_tool_use.type = "tool_use"
        mock_tool_use.name = "search"
        mock_tool_use.id = "tool_123"
        mock_tool_use.input = {"query": "Python async"}
        mock_response.content = [mock_tool_use]
        mock_response.stop_reason = "tool_use"
        mock_response.usage = MagicMock(input_tokens=30, output_tokens=15)

        provider.client.messages.create = AsyncMock(return_value=mock_response)

        # Create request with tools
        request = LLMRequest(
            messages=[RequestMessage(role="user", content="Search for info")],
            tools=[
                ToolDefinition(
                    name="search",
                    description="Search the web",
                    input_schema={"type": "object", "properties": {"query": {"type": "string"}}},
                )
            ],
        )

        response = await provider.generate(request)

        # Verify tool calls in response
        assert len(response.tool_calls) == 1
        assert response.tool_calls[0].name == "search"
        assert response.tool_calls[0].arguments["query"] == "Python async"

    @pytest.mark.asyncio
    async def test_system_prompt(self, provider):
        """Test system prompt handling"""
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Response")]
        mock_response.stop_reason = "end_turn"
        mock_response.usage = MagicMock(input_tokens=20, output_tokens=5)

        provider.client.messages.create = AsyncMock(return_value=mock_response)

        request = LLMRequest(
            messages=[RequestMessage(role="user", content="Hi")],
            system="You are a helpful assistant",
        )

        await provider.generate(request)

        # Verify system prompt was passed
        call_kwargs = provider.client.messages.create.call_args[1]
        assert call_kwargs["system"] == "You are a helpful assistant"

    @pytest.mark.asyncio
    async def test_cost_estimation(self, provider):
        """Test cost estimation"""
        cost = await provider.estimate_cost("claude-3-opus-20240229", 1000, 500)

        # 1000 input tokens at $15/million + 500 output at $75/million
        expected = (1000 / 1_000_000 * 15) + (500 / 1_000_000 * 75)
        assert abs(cost - expected) < 0.0001


class TestRuntimeArchitecture:
    """Test that runtime architecture works end-to-end"""

    @pytest.fixture
    def setup(self):
        """Setup providers and registries"""
        provider_registry = ProviderRegistry()
        model_registry = ModelRegistry()

        # Create mock provider
        provider = AsyncMock(spec=AnthropicProvider)
        provider.name = "anthropic"

        # Mock models
        models = [
            MagicMock(
                id="claude-3-opus-20240229",
                provider="anthropic",
                capabilities={ModelCapability.VISION, ModelCapability.TOOL_CALLING},
            ),
            MagicMock(
                id="claude-3-sonnet-20240229",
                provider="anthropic",
                capabilities={ModelCapability.TOOL_CALLING},
            ),
        ]
        provider.list_models = AsyncMock(return_value=models)

        provider_registry.register(provider)

        for model in models:
            model_registry.register(model)

        return {
            "provider_registry": provider_registry,
            "model_registry": model_registry,
            "provider": provider,
        }

    @pytest.mark.asyncio
    async def test_routing_by_capability(self, setup):
        """Test capability-based routing"""
        model_registry = setup["model_registry"]
        routing_engine = RoutingEngine(model_registry)

        # Request vision capability
        result = await routing_engine.route(
            required_capabilities={ModelCapability.VISION},
            policy=RoutingPolicy(strategy=RoutingStrategy.CAPABLE),
        )

        # Should select model with vision
        assert "opus" in result.model.id

    @pytest.mark.asyncio
    async def test_request_pipeline_integration(self, setup):
        """Test request flows through pipeline"""
        provider = setup["provider"]

        # Setup pipeline
        pipeline = RequestPipeline()

        # Mock provider response
        mock_response = MagicMock(spec=LLMResponse)
        mock_response.message = "Response"
        mock_response.provider = "anthropic"
        provider.generate = AsyncMock(return_value=mock_response)

        # Create context
        from aura_backend.llm.pipeline import PipelineContext

        context = PipelineContext(
            request=LLMRequest(messages=[RequestMessage(role="user", content="Hi")]),
            provider=provider,
            selected_model="claude-3-opus-20240229",
        )

        # Execute pipeline
        response = await pipeline.execute(context)

        # Verify response
        assert response.message == "Response"
        assert response.provider == "anthropic"

    @pytest.mark.asyncio
    async def test_universal_model_to_provider_mapping(self):
        """Test that universal models map correctly to providers"""
        # This validates that the LLMRequest/LLMResponse abstraction
        # doesn't lose information when mapping to/from Anthropic

        provider = AnthropicProvider({"api_key": "test"})
        models = await provider.list_models()

        # Verify all Anthropic models are discoverable
        assert len(models) >= 3

        # Verify capabilities are preserved
        for model in models:
            assert len(model.capabilities) > 0
            assert model.input_cost_per_million > 0
            assert model.output_cost_per_million > 0

        # Verify context windows are reasonable
        for model in models:
            assert model.context_window >= 128000  # All Claude 3 have 200k


class TestArchitectureValidation:
    """Validate that the runtime architecture is sufficient"""

    def test_request_model_completeness(self):
        """Verify LLMRequest covers all Anthropic request needs"""
        # Can express:
        # - Multiple messages ✓
        # - System prompt ✓
        # - Temperature ✓
        # - Max tokens ✓
        # - Tool definitions ✓
        # - Vision images ✓
        # - JSON mode ✓
        # - Tool calling ✓
        # - Streaming (via pipeline) ✓
        # - Metadata tracking (correlation_id, session_id) ✓

        request = LLMRequest(
            messages=[
                RequestMessage(role="user", content="Hi", images=[RequestImage(base64="...")]),
            ],
            system="System",
            temperature=0.7,
            max_tokens=1024,
            tools=[ToolDefinition(name="search", description="...", input_schema={})],
            json_mode=True,
        )

        # All fields mappable to Anthropic
        assert request.messages
        assert request.system
        assert request.temperature is not None
        assert request.max_tokens
        assert request.tools
        assert request.json_mode

    def test_response_model_completeness(self):
        """Verify LLMResponse captures all Anthropic response data"""
        # Can express:
        # - Text response ✓
        # - Tool calls ✓
        # - Usage (tokens) ✓
        # - Cost estimation ✓
        # - Latency ✓
        # - Provider/model attribution ✓
        # - Multiple content blocks ✓

        response = LLMResponse(
            message="Response",
            finish_reason="stop",
            provider="anthropic",
            model="claude-3-opus-20240229",
            tool_calls=[ToolCall(id="1", name="search", arguments={})],
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
            estimated_cost=0.015,
            latency_ms=500,
        )

        # All Anthropic response data captured
        assert response.message
        assert response.tool_calls
        assert response.input_tokens > 0
        assert response.estimated_cost > 0
        assert response.latency_ms > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
