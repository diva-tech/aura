# ADR-007: Capability Negotiation

**Date**: 2026-07-30  
**Status**: Accepted  
**Deciders**: Architecture Team  
**Affects**: M4-M5, M9-M14

## Context

Different providers support different capabilities:

- **YouTube**: Video metrics, retention, revenue (365 days)
- **TikTok**: Revenue, audience (30 days)
- **Instagram**: Revenue, audience (90 days)
- **LinkedIn**: Audience only

Planner cannot assume all providers have same capabilities. System must:

- Discover what each provider supports
- Select provider based on required capabilities
- Degrade gracefully when capabilities unavailable
- Select between multiple capable providers

## Decision

Implement **capability negotiation** system.

### Capability Model

```python
@dataclass(frozen=True)
class Capability:
    """Single capability that a provider supports"""
    name: str  # "video_metrics", "retention_curve", etc
    lookback_days: int = 365
    rate_limit_per_hour: int = 10000

@dataclass(frozen=True)
class ProviderCapabilities:
    """All capabilities a provider declares"""
    provider_name: str
    supported_features: tuple[Capability, ...]

    def has_capability(self, name: str) -> bool:
        return any(c.name == name for c in self.supported_features)

    def get_capability(self, name: str) -> Optional[Capability]:
        return next((c for c in self.supported_features if c.name == name), None)
```

### Provider Declaration

Each provider declares capabilities:

```python
class YouTubeAnalyticsProvider(AnalyticsProvider):
    def get_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            provider_name="youtube",
            supported_features=(
                Capability("video_metrics", lookback_days=365),
                Capability("retention_curve", lookback_days=365),
                Capability("audience_data", lookback_days=365),
                Capability("revenue_data", lookback_days=365),
                Capability("ctr_metrics", lookback_days=365),
            )
        )
```

### Selection Strategy

Planner selects provider based on:

1. **Required capabilities**: Which capabilities are needed
2. **Capability match**: Does provider support all?
3. **Rate limits**: Can provider handle volume?
4. **Lookback period**: Does provider have data?
5. **Latency**: Provider latency acceptable?
6. **Fallback**: Alternative provider available?

```python
def select_provider(
    required_capabilities: list[str],
    providers: dict[str, AnalyticsProvider]
) -> ProviderSelection:
    candidates = []

    for name, provider in providers.items():
        caps = provider.get_capabilities()

        # Check if provider supports all required capabilities
        if all(caps.has_capability(c) for c in required_capabilities):
            candidates.append((name, caps))

    if not candidates:
        # No provider has all capabilities, degrade
        return ProviderSelection(
            primary=None,
            fallback=None,
            mode="degraded",
            missing_capabilities=required_capabilities
        )

    # Select best candidate (highest rate limit, lowest latency, etc)
    candidates.sort(key=lambda x: x[1].rate_limit_per_hour, reverse=True)
    return ProviderSelection(
        primary=candidates[0][0],
        fallback=candidates[1][0] if len(candidates) > 1 else None,
        mode="optimized"
    )
```

### Graceful Degradation

When capabilities unavailable:

1. **Skip stage**: If optional, skip analysis stage
2. **Use default**: Use platform-wide defaults
3. **Fallback**: Try alternative provider
4. **Partial results**: Use subset of available data
5. **Quality reduction**: Lower quality results with available data

## Benefits

✓ **Flexibility**: Works with any provider combination
✓ **Graceful degradation**: System works even with partial capabilities
✓ **Provider independence**: Not locked to specific provider
✓ **Quality optimization**: Selects best available provider
✓ **Extensibility**: New providers can declare capabilities
✓ **Testability**: Can test with mock capabilities

## Consequences

**Positive:**

- Robust to provider changes
- Clear provider contracts
- Easy to reason about what's available

**Negative:**

- Requires capabilities declared accurately
- Selection logic can be complex
- Provider must implement introspection
- Capabilities may change (versioning needed)

## Capability Versioning

Capabilities may evolve:

```python
@dataclass(frozen=True)
class Capability:
    name: str
    version: str = "1.0"  # Semantic versioning
    lookback_days: int = 365
```

Selection can prefer specific versions if needed.

## Testing

Mock provider declares test capabilities:

```python
class MockAnalyticsProvider(AnalyticsProvider):
    def get_capabilities(self) -> ProviderCapabilities:
        # All capabilities available in test
        return ProviderCapabilities(
            provider_name="mock",
            supported_features=(
                Capability("video_metrics"),
                Capability("retention_curve"),
                Capability("audience_data"),
                Capability("revenue_data"),
                Capability("ctr_metrics"),
            )
        )
```

## Future Evolution

- **Dynamic capabilities**: Capabilities change based on runtime state
- **Capability composability**: Combine capabilities from multiple providers
- **Performance SLAs**: Declare latency guarantees
- **Cost information**: Declare cost per API call
- **Quota management**: Share rate limits across jobs
- **Capability prediction**: ML-based prediction of which provider works best

## See Also

- ADR-004: Provider Abstraction
- ADR-008: Failure Handling

## References

- M14 Learning Engine: AnalyticsCapability model
- M14 Phase 2: Analytics Providers implementation
- M14 Phase 4: Production readiness (capability negotiation in optimizer)
