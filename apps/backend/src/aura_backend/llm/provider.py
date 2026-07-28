"""
Abstract Provider interface.

Every LLM provider must implement this interface.
No provider-specific code in this module.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, List, Optional
from datetime import datetime

from aura_backend.llm.models import (
    ModelMetadata,
    LLMRequest,
    LLMResponse,
    StreamingToken,
)


class ProviderError(Exception):
    """Base provider error"""

    pass


class ProviderUnavailableError(ProviderError):
    """Provider is unavailable"""

    pass


class ProviderAuthError(ProviderError):
    """Authentication failed"""

    pass


class ProviderQuotaError(ProviderError):
    """Quota exceeded"""

    pass


class Provider(ABC):
    """
    Abstract base for all LLM providers.

    Every provider (OpenAI, Anthropic, Gemini, etc.) implements this interface.
    """

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize provider.

        Args:
            name: Provider identifier (e.g., "anthropic", "openai")
            config: Provider configuration (API keys, endpoints, etc.)
        """
        self.name = name
        self.config = config or {}
        self._initialized = False
        self._health_status = "unknown"
        self._last_health_check = None

    @property
    def is_initialized(self) -> bool:
        """Check if provider is initialized"""
        return self._initialized

    @property
    def health_status(self) -> str:
        """Get current health status"""
        return self._health_status

    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialize provider.

        Perform any setup needed (API key validation, client initialization, etc.)
        """
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown provider and cleanup resources"""
        pass

    @abstractmethod
    async def health(self) -> Dict[str, Any]:
        """
        Check provider health.

        Returns dict with:
        - status: "healthy", "degraded", "unavailable"
        - message: Health status message
        - last_check: Timestamp
        - models_available: Number of available models
        """
        pass

    @abstractmethod
    async def list_models(self) -> List[ModelMetadata]:
        """
        List all available models from this provider.

        Returns:
            List of ModelMetadata objects
        """
        pass

    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Generate response from LLM.

        Args:
            request: LLMRequest with normalized parameters

        Returns:
            LLMResponse with provider/model set

        Raises:
            ProviderError: On any error
            ProviderUnavailableError: Provider is down
            ProviderAuthError: Authentication failed
            ProviderQuotaError: Quota exceeded
        """
        pass

    @abstractmethod
    async def stream(
        self, request: LLMRequest
    ) -> AsyncIterator[StreamingToken]:
        """
        Stream response tokens.

        Args:
            request: LLMRequest with streaming enabled

        Yields:
            StreamingToken for each token

        Raises:
            ProviderError: On any error
        """
        pass

    @abstractmethod
    async def estimate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """
        Estimate cost for a request.

        Args:
            model: Model ID
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Estimated cost in USD
        """
        pass

    @abstractmethod
    async def tokenize(self, model: str, text: str) -> List[int]:
        """
        Tokenize text using model's tokenizer.

        Args:
            model: Model ID
            text: Text to tokenize

        Returns:
            List of token IDs
        """
        pass

    async def embed(self, model: str, texts: List[str]) -> List[List[float]]:
        """
        Embed texts (optional capability).

        Args:
            model: Embedding model ID
            texts: Texts to embed

        Returns:
            List of embeddings (one per text)

        Raises:
            NotImplementedError: Provider doesn't support embeddings
        """
        raise NotImplementedError(f"{self.name} does not support embeddings")

    def get_info(self) -> Dict[str, Any]:
        """Get provider information"""
        return {
            "name": self.name,
            "initialized": self._initialized,
            "health_status": self._health_status,
            "last_health_check": self._last_health_check.isoformat()
            if self._last_health_check
            else None,
        }
