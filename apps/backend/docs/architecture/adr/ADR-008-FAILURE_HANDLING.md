# ADR-008: Failure Handling

**Date**: 2026-07-30  
**Status**: Accepted  
**Deciders**: Architecture Team  
**Affects**: M6, M8-M14

## Context

Complex workflows fail in complex ways:

- Transient network errors (retry)
- Rate limiting (backoff)
- Provider failures (fallback)
- Resource exhaustion (queue)
- Configuration errors (skip)
- Permanent failures (propagate)

System needs sophisticated failure handling:

- Distinguish error types
- Apply appropriate recovery
- Track failure history
- Provide observability

## Decision

Implement **structured failure handling** with three layers:

### Layer 1: Typed Exceptions

Classify errors by type:

```python
class RecoverableError(Exception):
    """Transient, likely to succeed on retry"""
    pass

class TransientError(RecoverableError):
    """Network timeout, temporary unavailable"""
    pass

class RateLimitError(RecoverableError):
    """Provider rate limited, backoff needed"""
    pass

class PermanentError(Exception):
    """Not recoverable"""
    pass

class AuthenticationError(PermanentError):
    """Invalid credentials, won't succeed"""
    pass

class ConfigurationError(PermanentError):
    """Invalid configuration"""
    pass
```

### Layer 2: Structured Failure Record

```python
@dataclass(frozen=True)
class Failure:
    error_type: str  # Class name
    error_message: str
    is_recoverable: bool
    retry_count: int
    max_retries: int
    fallback_available: bool
    timestamp: datetime
    diagnostics: dict  # Additional context
```

### Layer 3: Recovery Strategy

Recovery depends on error type and context:

1. **Transient Errors**:
   - Retry with exponential backoff
   - Max retries: 3
   - Backoff: 1s, 2s, 4s (max 60s)

2. **Rate Limit Errors**:
   - Backoff longer (5s, 10s, 30s)
   - Respect rate limit headers
   - May queue for later

3. **Provider Failures**:
   - Try fallback provider if available
   - Degrade capabilities if needed
   - Skip stage if optional

4. **Permanent Errors**:
   - Log and propagate
   - Mark job as failed
   - Notify user

### Application in Orchestration

In M8 task execution:

```python
async def execute_task(task: Task) -> Result:
    try:
        result = await agent.execute(task, context)
        return Success(result)
    except RecoverableError as e:
        should_retry, backoff = retry_strategy(e, retry_count)
        if should_retry:
            await sleep(backoff)
            return execute_task(task)  # Retry
        else:
            return handle_fallback(task)  # Use fallback
    except PermanentError as e:
        record_failure(e)
        return Failure(e)
```

### Fallback Strategy

For provider failures:

1. **Primary provider fails**: Try fallback provider
2. **Fallback fails**: Degrade capabilities
3. **Degradation fails**: Skip optional stage
4. **Required stage fails**: Propagate failure

Each stage declares: fallback provider, optional/required, fallback strategy.

### Retry Optimization

Learn retry behavior from metrics:

```python
def get_retry_strategy(provider: str, success_rate: float) -> dict:
    """Tailor retry strategy based on provider reliability"""
    if success_rate >= 0.99:
        return {"max_retries": 1, "backoff_base": 1}
    elif success_rate >= 0.95:
        return {"max_retries": 2, "backoff_base": 2}
    else:
        return {"max_retries": 3, "backoff_base": 3}
```

## Benefits

✓ **Resilient**: System recovers from most failures automatically
✓ **Observable**: Failure tracking provides insights
✓ **Intelligent**: Different errors get different treatment
✓ **Maintainable**: Clear failure handling logic
✓ **Debuggable**: Structured failure records
✓ **Adaptive**: Learn from failures and adjust

## Consequences

**Positive:**

- High availability without manual intervention
- Clear error classification
- Natural integration with monitoring
- Supports graceful degradation

**Negative:**

- More error types to handle
- Retry logic adds latency
- Must carefully tune backoff times
- Requires monitoring to catch true problems

## Error Budget

System has error budget (rate of acceptable failures):

- **User errors**: Don't count against budget
- **Transient errors**: Counted if exceed threshold
- **Permanent errors**: Always count
- **Budget exceeded**: Page on-call engineer

```python
error_budget = ErrorBudget(
    transient_threshold=0.05,  # 5% transient error rate OK
    permanent_threshold=0.01,  # 1% permanent error rate
    window=timedelta(hours=1)
)
```

## Testing Failures

Test suite includes failure modes:

```python
async def test_provider_transient_failure():
    """Test retry on transient error"""
    provider = MockProvider(fail_count=2)  # Fail twice, then succeed
    result = await execute_with_retry(provider.get_metrics())
    assert result.success
    assert provider.call_count == 3

async def test_provider_permanent_failure():
    """Test propagation of permanent failure"""
    provider = MockProvider(permanent_failure=True)
    with pytest.raises(PermanentError):
        await execute_with_retry(provider.get_metrics())
```

## Future Evolution

- **Chaos engineering**: Inject failures to test recovery
- **Circuit breaker**: Disable failing provider temporarily
- **Adaptive backoff**: ML-based backoff time prediction
- **Error clustering**: Group similar errors
- **Automatic alerting**: Alert on error pattern changes

## See Also

- ADR-004: Provider Abstraction
- ADR-009: Event Sourcing (failures are events)

## References

- M6 Agent Runtime: Error handling in agents
- M8 Task Orchestration: Failure recovery in orchestrator
- M14 Phase 4: Production Readiness (retry optimization)
