# ADR-002: Immutable Domain Models

**Date**: 2026-07-30  
**Status**: Accepted  
**Deciders**: Architecture Team  
**Affects**: M1, M3-M14

## Context

Domain models flow through multiple systems (agents, providers, orchestrators, memory). State mutations during this flow create several problems:

- Difficult to debug: which system modified the state?
- Race conditions: concurrent modifications without locking
- Unexpected side effects: modifications in unexpected places
- Memory sharing bugs: aliasing and mutation surprises
- Thread safety: requires explicit synchronization

The system needs strong guarantees about state immutability to support:

- Autonomous agents running in parallel
- Long-running workflows with state snapshots
- Event sourcing and replay
- Testing and debugging

## Decision

**All domain models are immutable** using Python's `frozen=True` dataclasses.

### Examples

```python
@dataclass(frozen=True)
class LearningJob:
    id: str = ""
    creator_id: str = ""
    # Cannot modify: LearningJob.creator_id = "new" raises AttributeError
```

### Immutability Pattern

1. **Use `frozen=True`**: Prevents attribute assignment
2. **Tuple types**: Use `tuple` instead of `list` for sequences
3. **Value semantics**: Pass copies, not references
4. ****post_init** for defaults**: Initialize mutable defaults properly
5. **Use `object.__setattr__`**: Only way to set frozen attributes

### Non-Domain State

Non-domain classes (managers, registries, caches) CAN be mutable:

- LearningPlanner: stateless planner
- LearningAgentRegistry: mutable agent registry
- RecommendationCacheManager: mutable cache
- QueueOptimizer: mutable queue tracking

Clear separation: domain models frozen, infrastructure classes mutable.

## Benefits

✓ **Thread safety**: No explicit synchronization needed
✓ **Debugging**: State chain is immutable, easier to trace
✓ **Parallelism**: Agents can safely share models across threads
✓ **Event sourcing**: Natural fit for immutable state transitions
✓ **Testing**: No setup/teardown for mutable state
✓ **Concurrency**: No race conditions on model attributes

## Consequences

**Positive:**

- Natural fit with event sourcing and audit trails
- Easier concurrent programming
- Better debugging experience
- Natural for functional programming patterns

**Negative:**

- Cannot update state in-place (must create new object)
- Slightly higher memory usage (not sharing modified objects)
- Learning curve for teams used to mutable OOP
- Some patterns (e.g., builder pattern) require rework

## Alternatives Considered

### A. Mutable Models with Locking

Would require explicit synchronization everywhere, error-prone and hard to debug.

### B. Copy-on-Write

Adds complexity without clear benefits for our domain.

### C. Mixed (Frozen and Mutable)

Tried in initial design, led to subtle bugs when developers forgot to freeze critical models.

### D. Functional Data Structures

Would require external library and higher learning curve.

## Enforcement

1. **Code review**: Check for `frozen=True` on all models
2. **Type checking**: Mypy catches assignment attempts
3. **Tests**: Immutability tests verify frozen behavior
4. **Linting**: Pylint warns on missing frozen

## Future Evolution

As the system scales, immutability will simplify:

- Distributed tracing (state doesn't change unexpectedly)
- Caching strategies (frozen objects are naturally cacheable)
- Replication (no synchronization needed)
- Time-travel debugging (snapshot all state at each step)

## See Also

- ADR-009: Event Sourcing (natural fit for immutable models)
- M1 Foundation: Core model definitions
- M3-M14: All domain models

## References

- Python dataclasses: https://docs.python.org/3/library/dataclasses.html
- Frozen dataclasses: https://docs.python.org/3/library/dataclasses.html#frozen-instances
