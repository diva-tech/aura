"""Provider-agnostic LLM interfaces for content intelligence.

Abstracts Claude, OpenAI, Gemini, and local model implementations.
Every provider returns structured responses suitable for immutable object creation.
"""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class LLMModel(StrEnum):
    """Available LLM models"""

    CLAUDE_3_5_SONNET = "claude-3-5-sonnet"
    CLAUDE_3_OPUS = "claude-3-opus"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_4O = "gpt-4o"
    GEMINI_2_0_PRO = "gemini-2-0-pro"
    LOCAL_OLLAMA = "local-ollama"


@dataclass(frozen=True)
class LLMResponse:
    """Immutable LLM response"""

    model: str
    content: str
    stop_reason: str  # "stop_sequence", "max_tokens", "error"
    usage: dict[str, int]  # input_tokens, output_tokens
    error: str | None = None
    metadata: dict[str, Any] = None

    def is_success(self) -> bool:
        return self.stop_reason == "stop_sequence" and self.error is None

    def get_json(self) -> dict[str, Any] | None:
        """Extract JSON from response"""
        try:
            # Try direct JSON parsing
            return json.loads(self.content)
        except json.JSONDecodeError:
            # Try extracting JSON from markdown code blocks
            if "```json" in self.content:
                start = self.content.find("```json") + 7
                end = self.content.find("```", start)
                if end > start:
                    try:
                        return json.loads(self.content[start:end].strip())
                    except json.JSONDecodeError:
                        pass
            # Try extracting any JSON object/array
            for start in [self.content.find("{"), self.content.find("[")]:
                if start >= 0:
                    for end in range(len(self.content), start, -1):
                        try:
                            return json.loads(self.content[start:end])
                        except json.JSONDecodeError:
                            pass
        return None


class LLMProvider(ABC):
    """Base class for LLM providers"""

    @abstractmethod
    def generate(self, prompt: str, system: str | None = None, **kwargs) -> LLMResponse:
        """Generate text response"""
        pass

    @abstractmethod
    def generate_json(
        self, prompt: str, schema: dict[str, Any], system: str | None = None, **kwargs
    ) -> LLMResponse:
        """Generate JSON response matching schema"""
        pass

    @abstractmethod
    def supports_model(self, model: LLMModel) -> bool:
        """Check if provider supports model"""
        pass

    @abstractmethod
    def get_default_model(self) -> LLMModel:
        """Get default model for provider"""
        pass


# ============================================================================
# ANTHROPIC CLAUDE PROVIDER
# ============================================================================


class AnthropicProvider(LLMProvider):
    """Claude provider via Anthropic API"""

    def __init__(self, api_key: str | None = None, model: LLMModel = LLMModel.CLAUDE_3_5_SONNET):
        self.api_key = api_key
        self.model = model
        self._supported_models = [
            LLMModel.CLAUDE_3_5_SONNET,
            LLMModel.CLAUDE_3_OPUS,
        ]

    def supports_model(self, model: LLMModel) -> bool:
        return model in self._supported_models

    def get_default_model(self) -> LLMModel:
        return LLMModel.CLAUDE_3_5_SONNET

    def generate(self, prompt: str, system: str | None = None, **kwargs) -> LLMResponse:
        """
        Generate text via Claude.

        In production, this would call:
        client = Anthropic(api_key=self.api_key)
        response = client.messages.create(
            model=self.model.value,
            max_tokens=kwargs.get("max_tokens", 1024),
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )

        For now, return reference implementation response.
        """
        try:
            # Reference implementation
            if not self.api_key:
                return LLMResponse(
                    model=self.model.value,
                    content="",
                    stop_reason="error",
                    usage={"input_tokens": 0, "output_tokens": 0},
                    error="API key not configured",
                )

            # Simulated response
            return LLMResponse(
                model=self.model.value,
                content="[Claude response would be here]",
                stop_reason="stop_sequence",
                usage={"input_tokens": len(prompt.split()), "output_tokens": 10},
                metadata={"provider": "anthropic", "system_prompt": bool(system)},
            )
        except Exception as e:
            return LLMResponse(
                model=self.model.value,
                content="",
                stop_reason="error",
                usage={"input_tokens": 0, "output_tokens": 0},
                error=str(e),
            )

    def generate_json(
        self, prompt: str, schema: dict[str, Any], system: str | None = None, **kwargs
    ) -> LLMResponse:
        """Generate JSON-structured response"""
        json_schema_prompt = (
            f"{prompt}\n\nRespond with JSON matching this schema:\n{json.dumps(schema, indent=2)}"
        )

        return self.generate(
            json_schema_prompt,
            system=system
            or "You are a JSON generation expert. Always respond with valid JSON only.",
            **kwargs,
        )


# ============================================================================
# OPENAI PROVIDER
# ============================================================================


class OpenAIProvider(LLMProvider):
    """OpenAI provider for GPT models"""

    def __init__(self, api_key: str | None = None, model: LLMModel = LLMModel.GPT_4O):
        self.api_key = api_key
        self.model = model
        self._supported_models = [
            LLMModel.GPT_4_TURBO,
            LLMModel.GPT_4O,
        ]

    def supports_model(self, model: LLMModel) -> bool:
        return model in self._supported_models

    def get_default_model(self) -> LLMModel:
        return LLMModel.GPT_4O

    def generate(self, prompt: str, system: str | None = None, **kwargs) -> LLMResponse:
        """
        Generate text via OpenAI.

        In production:
        response = openai.ChatCompletion.create(
            model=self.model.value,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            max_tokens=kwargs.get("max_tokens", 1024),
        )
        """
        try:
            if not self.api_key:
                return LLMResponse(
                    model=self.model.value,
                    content="",
                    stop_reason="error",
                    usage={"input_tokens": 0, "output_tokens": 0},
                    error="API key not configured",
                )

            # Reference implementation
            return LLMResponse(
                model=self.model.value,
                content="[OpenAI response would be here]",
                stop_reason="stop_sequence",
                usage={"input_tokens": len(prompt.split()), "output_tokens": 10},
                metadata={"provider": "openai", "system_prompt": bool(system)},
            )
        except Exception as e:
            return LLMResponse(
                model=self.model.value,
                content="",
                stop_reason="error",
                usage={"input_tokens": 0, "output_tokens": 0},
                error=str(e),
            )

    def generate_json(
        self, prompt: str, schema: dict[str, Any], system: str | None = None, **kwargs
    ) -> LLMResponse:
        """Generate JSON response using OpenAI"""
        json_schema_prompt = (
            f"{prompt}\n\nRespond with JSON matching this schema:\n{json.dumps(schema, indent=2)}"
        )

        return self.generate(
            json_schema_prompt,
            system=system
            or "You are a JSON generation expert. Always respond with valid JSON only.",
            **kwargs,
        )


# ============================================================================
# GOOGLE GEMINI PROVIDER
# ============================================================================


class GeminiProvider(LLMProvider):
    """Google Gemini provider"""

    def __init__(self, api_key: str | None = None, model: LLMModel = LLMModel.GEMINI_2_0_PRO):
        self.api_key = api_key
        self.model = model
        self._supported_models = [
            LLMModel.GEMINI_2_0_PRO,
        ]

    def supports_model(self, model: LLMModel) -> bool:
        return model in self._supported_models

    def get_default_model(self) -> LLMModel:
        return LLMModel.GEMINI_2_0_PRO

    def generate(self, prompt: str, system: str | None = None, **kwargs) -> LLMResponse:
        """
        Generate text via Gemini.

        In production:
        client = genai.GenerativeModel(self.model.value)
        response = client.generate_content(
            prompt,
            system_instruction=system,
        )
        """
        try:
            if not self.api_key:
                return LLMResponse(
                    model=self.model.value,
                    content="",
                    stop_reason="error",
                    usage={"input_tokens": 0, "output_tokens": 0},
                    error="API key not configured",
                )

            # Reference implementation
            return LLMResponse(
                model=self.model.value,
                content="[Gemini response would be here]",
                stop_reason="stop_sequence",
                usage={"input_tokens": len(prompt.split()), "output_tokens": 10},
                metadata={"provider": "gemini", "system_prompt": bool(system)},
            )
        except Exception as e:
            return LLMResponse(
                model=self.model.value,
                content="",
                stop_reason="error",
                usage={"input_tokens": 0, "output_tokens": 0},
                error=str(e),
            )

    def generate_json(
        self, prompt: str, schema: dict[str, Any], system: str | None = None, **kwargs
    ) -> LLMResponse:
        """Generate JSON response using Gemini"""
        json_schema_prompt = (
            f"{prompt}\n\nRespond with JSON matching this schema:\n{json.dumps(schema, indent=2)}"
        )

        return self.generate(
            json_schema_prompt,
            system=system
            or "You are a JSON generation expert. Always respond with valid JSON only.",
            **kwargs,
        )


# ============================================================================
# LOCAL OLLAMA PROVIDER
# ============================================================================


class LocalOllamaProvider(LLMProvider):
    """Local Ollama model provider"""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "neural-chat"):
        self.base_url = base_url
        self.model_name = model
        self._supported_models = [LLMModel.LOCAL_OLLAMA]

    def supports_model(self, model: LLMModel) -> bool:
        return model == LLMModel.LOCAL_OLLAMA

    def get_default_model(self) -> LLMModel:
        return LLMModel.LOCAL_OLLAMA

    def generate(self, prompt: str, system: str | None = None, **kwargs) -> LLMResponse:
        """
        Generate text via Ollama.

        In production:
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model_name,
                "prompt": prompt,
                "system": system,
                "stream": False,
            },
        )
        """
        try:
            # Check if Ollama is available
            # For now, return reference implementation
            return LLMResponse(
                model=f"ollama:{self.model_name}",
                content="[Local Ollama response would be here]",
                stop_reason="stop_sequence",
                usage={"input_tokens": len(prompt.split()), "output_tokens": 10},
                metadata={"provider": "ollama", "base_url": self.base_url},
            )
        except Exception as e:
            return LLMResponse(
                model=f"ollama:{self.model_name}",
                content="",
                stop_reason="error",
                usage={"input_tokens": 0, "output_tokens": 0},
                error=f"Ollama unavailable: {str(e)}",
            )

    def generate_json(
        self, prompt: str, schema: dict[str, Any], system: str | None = None, **kwargs
    ) -> LLMResponse:
        """Generate JSON response via Ollama"""
        json_schema_prompt = (
            f"{prompt}\n\nRespond with JSON matching this schema:\n{json.dumps(schema, indent=2)}"
        )

        return self.generate(
            json_schema_prompt,
            system=system
            or "You are a JSON generation expert. Always respond with valid JSON only.",
            **kwargs,
        )


# ============================================================================
# PROVIDER REGISTRY AND FACTORY
# ============================================================================


class LLMProviderRegistry:
    """Registry for LLM providers"""

    def __init__(self):
        self._providers: dict[str, LLMProvider] = {}
        self._default_provider: str | None = None

    def register(self, name: str, provider: LLMProvider, is_default: bool = False):
        """Register LLM provider"""
        self._providers[name] = provider
        if is_default:
            self._default_provider = name

    def get(self, name: str) -> LLMProvider | None:
        """Get provider by name"""
        return self._providers.get(name)

    def get_default(self) -> LLMProvider | None:
        """Get default provider"""
        if self._default_provider:
            return self._providers.get(self._default_provider)
        return None

    def list_providers(self) -> list[str]:
        """List registered provider names"""
        return list(self._providers.keys())

    def get_by_model(self, model: LLMModel) -> LLMProvider | None:
        """Find provider supporting model"""
        for provider in self._providers.values():
            if provider.supports_model(model):
                return provider
        return None


def create_default_registry() -> LLMProviderRegistry:
    """Create registry with default providers"""
    registry = LLMProviderRegistry()

    # Register default implementations (with placeholder API keys for testing)
    registry.register("claude", AnthropicProvider(api_key="sk-test"), is_default=True)
    registry.register("openai", OpenAIProvider(api_key="sk-test"))
    registry.register("gemini", GeminiProvider(api_key="test"))
    registry.register("ollama", LocalOllamaProvider())

    return registry
