# ADR-005: Stateless Agents

**Date**: 2026-07-30  
**Status**: Accepted  
**Deciders**: Architecture Team  
**Affects**: M6, M8-M14

## Context

M6 agents execute work in orchestrated workflows. Key questions:

- Should agents maintain state between calls?
- Can agents run concurrently?
- How do agents communicate?
- What if an agent crashes mid-execution?

Previous designs had agents maintaining state, leading to:

- Race conditions when agents run in parallel
- Difficult recovery from crashes
- Hard to replay executions
- Dependency management between agents becomes complex

## Decision

**All M6 agents are stateless**.

### Pattern

```python
class LearningAgent(ABC):
    @abstractmethod
    async def execute(self, task: Task, context: Context) -> dict:
        """Execute task. No agent-local state."""
        pass
```

### Stateless Means

1. **No instance variables** holding execution state
2. **All state** passed through `context` parameter
3. **All results** returned as dict (or immutable result type)
4. **Idempotent** execution (same input → same output)

### Example: Validation Agent

```python
class ValidationAgent(LearningAgent):
    async def execute(self, task: Task, context: Context) -> dict:
        # All data from context
        job = context.job
        platform = context.platform

        # Do work
        errors = validate(job, platform)

        # Return results
        return {"valid": len(errors) == 0, "errors": errors}
        # No state stored in agent
```

## Benefits

✓ **Concurrent execution**: Multiple agents can run in parallel
✓ **Scalability**: Easy to scale (stateless agents are horizontally scalable)
✓ **Recovery**: If agent crashes, just re-run with same input
✓ **Testing**: No setup/teardown, deterministic behavior
✓ **Replay**: Can re-execute workflow by replaying task sequence
✓ **Debugging**: No hidden state, easier to trace

## Consequences

**Positive:**

- Supports massive parallelism
- Natural for distributed systems
- Easy to test and debug
- Natural fit with event sourcing

**Negative:**

- Must pass all state through context/parameters
- Context objects can become large
- Some patterns (e.g., maintaining statistics) require external storage
- Requires discipline (nothing prevents adding state, just convention)

## What CAN Be Stateful

Infrastructure components can be stateful:

- **Planners**: Can build DAGs (not running tasks)
- **Registries**: Can maintain registries of agents/providers
- **Caches**: Can maintain caches (with clear lifecycle)
- **Managers**: Can manage queues and scheduling

Key: Infrastructure state doesn't affect agent execution.

## Enforcement

1. **Code review**: Check agents have no `__init__` state
2. **Testing**: Stateless tests (no setup/teardown)
3. **Linting**: Can warn on instance variable assignments in agents
4. **Architecture review**: Verify agent dependencies go through context

## Coordination Pattern

How do agents coordinate without state?

Through **task results and context**:

```
Stage 1: Agent A executes, returns ResultA
           ↓
Stage 2: ResultA added to context
           ↓
Stage 3: Agent B executes with context including ResultA
           ↓
Stage 4: Agent B returns ResultB
```

Example from Learning Pipeline:

1. **ValidationAgent** → validates job → context.validation_result
2. **AuthenticationAgent** → authenticates → context.auth_result
3. **MetricsRetrievalAgent** → collects → context.metrics
4. **AnalysisAgent** → analyzes → context.analysis

## Future Evolution

- **Agent composition**: Combine agents without state sharing
- **Agent chaining**: Easy to build workflows from stateless agents
- **Distributed agents**: Agents can run on different machines
- **Horizontal scaling**: Add more agent instances without coordination
- **Agent migration**: Move agents between systems without state management

## See Also

- ADR-002: Immutable Domain Models (context is immutable)
- ADR-003: Planner → DAG → M8 → M6 → Provider Pattern

## References

- M6 Agent Runtime: Stateless agent execution
- M8 Task Orchestration: Coordinates stateless agents
- M9-M14: Examples of stateless agents
