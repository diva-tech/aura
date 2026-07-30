# ADR-004: Provider Abstraction

**Date**: 2026-07-30  
**Status**: Accepted  
**Deciders**: Architecture Team  
**Affects**: M4-M5, M9-M14

## Context

AURA depends on external services:

- **Rendering**: GPU providers, rendering APIs
- **Publishing**: YouTube, TikTok, Instagram APIs
- **Analytics**: YouTube Analytics, TikTok Analytics, etc.
- **AI Models**: OpenAI, Claude, local models

System cannot be coupled to specific implementations. Providers may change, be swapped, or run in different deployments.

## Decision

**Implement Provider Abstraction**:

Every external dependency goes through an abstract provider interface.

### Pattern

```python
class RendererProvider(ABC):
    """Abstract renderer interface"""

    @abstractmethod
    async def render(self, job: RenderJob, context) -> RenderResult:
        pass

class GPURendererProvider(RendererProvider):
    """GPU-based implementation"""

class SoftwareRendererProvider(RendererProvider):
    """CPU-based implementation"""
```

### Key Principles

1. **Single Responsibility**: Each provider does one thing well
2. **Interchangeability**: Any provider can replace another (same interface)
3. **Discovery**: Providers registered in ProviderRegistry
4. **Capability Negotiation**: Providers declare what they support
5. **Reference Implementations**: At least one reference implementation per interface

### Provider Types in AURA

| Type                   | Purpose               | Examples                   |
| ---------------------- | --------------------- | -------------------------- |
| **RendererProvider**   | Rendering output      | GPU, Software              |
| **PublishingProvider** | Platform publishing   | YouTube, TikTok, Instagram |
| **AnalyticsProvider**  | Analytics collection  | YouTube, TikTok, Mock      |
| **LLMProvider**        | Model inference       | OpenAI, Claude, Local      |
| **EmbeddingProvider**  | Embeddings            | OpenAI, Local              |
| **PlannerProvider**    | Custom planning logic | Custom implementations     |
| **MemoryProvider**     | Long-term storage     | In-Memory, Postgres, Redis |

### Capability Model

Each provider declares capabilities:

```python
@dataclass(frozen=True)
class AnalyticsCapability:
    supported_features: tuple[str, ...]  # ["video_metrics", "retention", ...]
    rate_limit_per_hour: int = 10000
    lookback_days: int = 365
```

### Selection Strategy

Planner selects provider based on:

1. Required capabilities
2. Rate limit availability
3. Latency requirements
4. Cost (if applicable)
5. Fallback availability

## Benefits

✓ **Flexibility**: Swap implementations without changing code
✓ **Testing**: Use mock providers for testing
✓ **Deployment flexibility**: Different providers per environment
✓ **Vendor independence**: Not locked to single provider
✓ **Extensibility**: Easy to add new provider implementations
✓ **Failure handling**: Fallback to alternative providers

## Consequences

**Positive:**

- System is vendor-agnostic
- Easy to test with mocks
- Clear interfaces for extensions
- Natural separation of concerns

**Negative:**

- More abstraction layers
- Requires implementing interface for each provider
- May have feature gaps (interface is lowest common denominator)
- Performance overhead from indirection

## Alternatives Considered

### A. Direct Integration

Would couple system to specific services, brittle and hard to test.

### B. Configuration-based Selection

Less flexible than provider abstraction, harder to implement complex selection logic.

### C. Service Locator Pattern

Less type-safe than dependency injection.

## Provider Lifecycle

1. **Registration**: Provider registered in ProviderRegistry
2. **Discovery**: Planner queries registry for available providers
3. **Selection**: Planner selects best provider for job
4. **Authentication**: Provider authenticates if needed
5. **Execution**: Agent invokes provider method
6. **Error Handling**: Fallback to alternative if provider fails

## Reference Implementations

Every provider type has at least one reference implementation:

- **AnalyticsProvider**: MockAnalyticsProvider (always available)
- **RendererProvider**: SoftwareRenderer (CPU-based fallback)
- **PublishingProvider**: MockPublishingProvider (for testing)
- **LLMProvider**: MockLLMProvider (for testing)

## Future Evolution

- **Provider composition**: Combine multiple providers (e.g., hybrid rendering)
- **Adaptive provider selection**: Choose based on load and latency
- **Provider health tracking**: Monitor and fallback automatically
- **Provider-specific optimizations**: Leverage provider-specific capabilities
- **Cost optimization**: Select based on cost/performance tradeoff

## See Also

- ADR-007: Capability Negotiation
- ADR-008: Failure Handling

## References

- M4 Tool Platform: ToolProvider abstraction
- M5 LLM Runtime: LLMProvider implementations
- M9-M13: Domain-specific provider implementations
- M14 Learning: AnalyticsProvider implementations
