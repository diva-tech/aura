# ADR-003: Planner → DAG → M8 → M6 → Provider Pattern

**Date**: 2026-07-30  
**Status**: Accepted  
**Deciders**: Architecture Team  
**Affects**: M6, M8, M9-M14

## Context

Complex workflows require coordination of multiple agents and providers:

- Video rendering needs multiple analysis passes
- Publishing requires provider-specific formatting
- Learning optimization needs multi-stage analytics collection

Traditional sequential execution is too rigid. Pure agent networks can deadlock or have unclear execution order.

## Decision

Establish a **standardized execution pattern**:

```
Domain Logic
    ↓
Planner (creates plan)
    ↓
DAG (explicit dependencies)
    ↓
M8 Task Graph (orchestration)
    ↓
M6 Agents (execution)
    ↓
Providers (actual work)
```

### Stage 1: Planner

**Responsibility**: Create execution plan

```python
planner = VideoAnalysisPlan()
stages = planner.create_stage_dag(video, context, provider_registry)
# Returns: List[Stage] with dependencies
```

**Example**: Learning Planner

```
- Validate job
- Authenticate providers
- Collect metrics (parallel)
- Analyze retention, audience, revenue (parallel)
- Generate recommendations
- Update profiles
- Finalize
```

### Stage 2: DAG

**Responsibility**: Explicit dependency graph

```python
@dataclass(frozen=True)
class Stage:
    depends_on: tuple[str, ...] = ()  # Upstream stage IDs
    stage_type: StageType = StageType.VALIDATE
```

**Benefits**:

- Clear which stages can run in parallel
- Easy to visualize workflow
- Natural for failure handling (skip downstream if upstream fails)

### Stage 3: M8 Task Graph

**Responsibility**: Convert to orchestration format

```python
tasks = planner.stages_to_m8_tasks(stages)
# Each task has metadata, dependency information
# M8 handles actual scheduling and orchestration
```

### Stage 4: M6 Agents

**Responsibility**: Execute individual stages

```python
@dataclass(frozen=True)
class LearningTask:
    metadata: dict  # Contains stage_type, platform, etc

async def execute(task: LearningTask, context) -> dict:
    stage_type = task.metadata["stage_type"]
    # Execute appropriate logic
```

**Key property**: Agents are **stateless**

- No agent-local state
- All state passed through task and context
- Agents are safely concurrent

### Stage 5: Providers

**Responsibility**: Do actual work

```python
provider = registry.get_provider(platform)
metrics = await provider.get_video_metrics(video_id)
```

## Benefits

✓ **Clear execution flow**: Easy to understand what happens when
✓ **Parallelization**: DAG makes concurrency explicit
✓ **Failure handling**: Can skip stages or use fallbacks
✓ **Testing**: Each stage testable independently
✓ **Debugging**: Can trace through explicit stages
✓ **Monitoring**: Easy to track stage execution times
✓ **Extensions**: New stages can be added without changing others

## Consequences

**Positive:**

- Complex workflows become manageable
- Team can reason about execution
- Easy to add observability
- Natural fit with M8 task graph

**Negative:**

- More classes and indirection
- DAG generation logic needs to be correct
- Stage interdependencies can be complex
- Requires understanding of both DAG and M8

## Alternatives Considered

### A. Direct Agent-to-Agent Messaging

Would create implicit dependencies, hard to reason about.

### B. Manual Task Submission

Error-prone, requires explicit coordination.

### C. Reactive Streams

Would add complexity without clear benefit for our use case.

### D. Hierarchical State Machines

More complex than needed, DAG is simpler.

## Application Across Milestones

- **M9 Video Intelligence**: VideoAnalysisPlan creates DAG for video analysis
- **M10 Content Intelligence**: ContentAnalysisPlan for content understanding
- **M11 Intelligent Editing**: EditingPlan for transformation workflows
- **M12 Rendering**: RenderingPlan for render passes
- **M13 Publishing**: PublishingPlan for multi-provider publishing
- **M14 Learning**: LearningPlanner for analytics and recommendations

Each planner follows same pattern: create DAG, convert to M8 tasks, agents execute.

## Future Evolution

The pattern supports:

- **Conditional stages**: If-then-else logic in DAG
- **Loop stages**: Retry or repeat stages with backoff
- **Dynamic DAGs**: DAG generated at runtime based on results
- **Distributed execution**: M8 can distribute tasks across machines
- **Stage caching**: Results of expensive stages cached
- **Partial re-execution**: Re-run from failure point

## See Also

- ADR-001: Layered Architecture (M8 as orchestration layer)
- ADR-004: Provider Abstraction
- ADR-005: Stateless Agents

## References

- M6 Agent Runtime: Stateless agent execution
- M8 Task Orchestration: DAG scheduling
- M9-M14: Examples of planners using this pattern
