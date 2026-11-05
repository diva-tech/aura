"""
Provider and Model Registry.

Manages dynamic provider registration and model discovery.
"""

from __future__ import annotations

import threading
from typing import Any, Dict, List, Optional
from datetime import datetime

from aura_backend.llm.provider import Provider
from aura_backend.llm.models import ModelMetadata, ModelCapability


class RegistryError(Exception):
    """Base registry error"""

    pass


class ProviderRegistry:
    """
    Registry for LLM providers.

    Thread-safe provider registration and discovery.
    """

    def __init__(self):
        self._providers: Dict[str, Provider] = {}
        self._lock = threading.RLock()

    def register(self, provider: Provider) -> None:
        """
        Register a provider.

        Args:
            provider: Provider instance

        Raises:
            RegistryError: If provider name already registered
        """
        with self._lock:
            if provider.name in self._providers:
                raise RegistryError(f"Provider '{provider.name}' already registered")
            self._providers[provider.name] = provider

    def unregister(self, provider_name: str) -> None:
        """
        Unregister a provider.

        Args:
            provider_name: Name of provider to unregister
        """
        with self._lock:
            if provider_name in self._providers:
                del self._providers[provider_name]

    def get(self, provider_name: str) -> Optional[Provider]:
        """
        Get provider by name.

        Args:
            provider_name: Name of provider

        Returns:
            Provider instance or None if not found
        """
        with self._lock:
            return self._providers.get(provider_name)

    def list(self) -> List[Provider]:
        """
        List all registered providers.

        Returns:
            List of Provider instances
        """
        with self._lock:
            return list(self._providers.values())

    def count(self) -> int:
        """Get number of registered providers"""
        with self._lock:
            return len(self._providers)

    async def health(self) -> Dict[str, Dict[str, Any]]:
        """
        Get health status of all providers.

        Returns:
            Dict mapping provider name to health info
        """
        with self._lock:
            providers = list(self._providers.values())

        health_status = {}
        for provider in providers:
            try:
                health_status[provider.name] = await provider.health()
            except Exception as e:
                health_status[provider.name] = {
                    "status": "error",
                    "error": str(e),
                }

        return health_status


class ModelRegistry:
    """
    Registry for LLM models.

    Maintains metadata for all models across all providers.
    Thread-safe discovery by capabilities, cost, latency, etc.
    """

    def __init__(self):
        self._models: Dict[str, ModelMetadata] = {}  # model_id -> metadata
        self._by_provider: Dict[str, List[str]] = {}  # provider -> [model_ids]
        self._by_capability: Dict[ModelCapability, List[str]] = {}  # capability -> [model_ids]
        self._lock = threading.RLock()

    def register(self, model: ModelMetadata) -> None:
        """
        Register model metadata.

        Args:
            model: ModelMetadata instance
        """
        with self._lock:
            self._models[model.id] = model

            # Index by provider
            if model.provider not in self._by_provider:
                self._by_provider[model.provider] = []
            self._by_provider[model.provider].append(model.id)

            # Index by capabilities
            for capability in model.capabilities:
                if capability not in self._by_capability:
                    self._by_capability[capability] = []
                self._by_capability[capability].append(model.id)

    def unregister(self, model_id: str) -> None:
        """
        Unregister model.

        Args:
            model_id: ID of model to unregister
        """
        with self._lock:
            if model_id not in self._models:
                return

            model = self._models[model_id]
            del self._models[model_id]

            # Clean up indices
            if model.provider in self._by_provider:
                self._by_provider[model.provider].remove(model_id)

            for capability in model.capabilities:
                if capability in self._by_capability:
                    self._by_capability[capability].remove(model_id)

    def get(self, model_id: str) -> Optional[ModelMetadata]:
        """
        Get model metadata by ID.

        Args:
            model_id: ID of model

        Returns:
            ModelMetadata or None if not found
        """
        with self._lock:
            return self._models.get(model_id)

    def list(self, provider: Optional[str] = None) -> List[ModelMetadata]:
        """
        List models.

        Args:
            provider: Optional provider name to filter by

        Returns:
            List of ModelMetadata objects
        """
        with self._lock:
            if provider:
                model_ids = self._by_provider.get(provider, [])
                return [self._models[mid] for mid in model_ids if mid in self._models]
            return list(self._models.values())

    def find_by_capabilities(
        self,
        capabilities: set[ModelCapability],
        provider: Optional[str] = None,
    ) -> List[ModelMetadata]:
        """
        Find models supporting all specified capabilities.

        Args:
            capabilities: Required capabilities
            provider: Optional provider filter

        Returns:
            List of matching ModelMetadata objects
        """
        with self._lock:
            # Get models with all capabilities
            if not capabilities:
                candidates = set(self._models.keys())
            else:
                candidates = None
                for cap in capabilities:
                    cap_models = set(self._by_capability.get(cap, []))
                    if candidates is None:
                        candidates = cap_models
                    else:
                        candidates &= cap_models

                if candidates is None:
                    candidates = set()

            # Filter by provider if specified
            if provider:
                provider_models = set(self._by_provider.get(provider, []))
                candidates &= provider_models

            return [self._models[mid] for mid in candidates if mid in self._models]

    def find_cheapest(
        self,
        capabilities: set[ModelCapability] = None,
    ) -> Optional[ModelMetadata]:
        """
        Find cheapest model supporting capabilities.

        Args:
            capabilities: Required capabilities

        Returns:
            Cheapest ModelMetadata or None
        """
        candidates = self.find_by_capabilities(capabilities or set())
        if not candidates:
            return None

        # Sort by combined input/output cost (rough estimate)
        return min(candidates, key=lambda m: m.input_cost_per_million + m.output_cost_per_million)

    def find_fastest(
        self,
        capabilities: set[ModelCapability] = None,
    ) -> Optional[ModelMetadata]:
        """
        Find fastest model supporting capabilities.

        Args:
            capabilities: Required capabilities

        Returns:
            Fastest ModelMetadata or None
        """
        candidates = self.find_by_capabilities(capabilities or set())
        if not candidates:
            return None

        return min(candidates, key=lambda m: m.typical_latency_ms)

    def find_by_context_length(
        self,
        min_context: int,
        capabilities: set[ModelCapability] = None,
    ) -> List[ModelMetadata]:
        """
        Find models with minimum context window.

        Args:
            min_context: Minimum context window required
            capabilities: Optional required capabilities

        Returns:
            List of matching ModelMetadata objects
        """
        candidates = self.find_by_capabilities(capabilities or set())
        return [m for m in candidates if m.context_window >= min_context]

    def count(self, provider: Optional[str] = None) -> int:
        """
        Count models.

        Args:
            provider: Optional provider filter

        Returns:
            Number of models
        """
        with self._lock:
            if provider:
                return len(self._by_provider.get(provider, []))
            return len(self._models)

    def update(self, model: ModelMetadata) -> None:
        """
        Update model metadata.

        Args:
            model: Updated ModelMetadata
        """
        with self._lock:
            if model.id in self._models:
                # Keep existing registration
                old_model = self._models[model.id]
                model.metadata.update(old_model.metadata)
            self._models[model.id] = model
            model.updated_at = datetime.utcnow()
