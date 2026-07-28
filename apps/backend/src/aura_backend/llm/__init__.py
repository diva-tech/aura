"""
AURA LLM Runtime & Provider Platform.

Universal infrastructure for managing LLM providers.

Core components:
- Provider Registry: Dynamic provider registration
- Model Registry: Provider model metadata
- Capability Discovery: Request capabilities, runtime selects models
- Provider Interface: Abstract base for all providers
- Request Pipeline: Validation, policies, execution
- Routing Engine: Intelligent model selection
- Metrics & Events: Observability
"""

from aura_backend.llm.models import (
    ModelCapability,
    ModelMetadata,
    RequestMessage,
    RequestImage,
    RequestAudio,
    LLMRequest,
    ResponseContent,
    ToolCall,
    LLMResponse,
    StreamingToken,
)
from aura_backend.llm.registry import (
    ProviderRegistry,
    ModelRegistry,
    RegistryError,
)
from aura_backend.llm.provider import (
    Provider,
    ProviderError,
    ProviderUnavailableError,
)
from aura_backend.llm.routing import (
    CapabilitySet,
    RoutingPolicy,
    RoutingEngine,
    RoutingResult,
)
from aura_backend.llm.pipeline import (
    RequestPipeline,
    PipelineContext,
    PipelineError,
)
from aura_backend.llm.events import (
    RequestStartedEvent,
    RequestCompletedEvent,
    RequestFailedEvent,
    StreamingStartedEvent,
    StreamingCompletedEvent,
    ProviderUnavailableEvent,
    RoutingDecisionEvent,
)
from aura_backend.llm.metrics import (
    RequestMetrics,
    MetricsCollector,
)

__all__ = [
    # Models
    "ModelCapability",
    "ModelMetadata",
    "RequestMessage",
    "RequestImage",
    "RequestAudio",
    "LLMRequest",
    "ResponseContent",
    "ToolCall",
    "LLMResponse",
    "StreamingToken",
    # Registry
    "ProviderRegistry",
    "ModelRegistry",
    "RegistryError",
    # Provider
    "Provider",
    "ProviderError",
    "ProviderUnavailableError",
    # Routing
    "CapabilitySet",
    "RoutingPolicy",
    "RoutingEngine",
    "RoutingResult",
    # Pipeline
    "RequestPipeline",
    "PipelineContext",
    "PipelineError",
    # Events
    "RequestStartedEvent",
    "RequestCompletedEvent",
    "RequestFailedEvent",
    "StreamingStartedEvent",
    "StreamingCompletedEvent",
    "ProviderUnavailableEvent",
    "RoutingDecisionEvent",
    # Metrics
    "RequestMetrics",
    "MetricsCollector",
]
