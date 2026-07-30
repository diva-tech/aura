# ADR-010: Memory Separation

**Date**: 2026-07-30  
**Status**: Accepted  
**Deciders**: Architecture Team  
**Affects**: M7, M14

## Context

Agents need to access memory for context, but different types of memory serve different purposes:

- **Short-term**: Current job context, working memory
- **Medium-term**: Session context, user preferences
- **Long-term**: Historical learning, optimization history
- **External**: File storage, database, caches

Monolithic memory design would create:

- Performance issues (scanning all history for recent data)
- Consistency problems (updating while querying)
- Security issues (mixing privileged and unprivileged data)
- Coupling issues (can't replace storage independently)

## Decision

Separate memory into **distinct layers** with clear responsibilities.

### Memory Layers

#### 1. Context Memory (Working Memory)

**Scope**: Current execution

```python
@dataclass(frozen=True)
class LearningContext:
    """Current execution context"""
    job_id: str
    creator_id: str
    platform: str
    # ...current job data
```

**Lifecycle**: Created for job, discarded after completion
**Storage**: In-memory (Python objects)
**Access**: Passed to all agents
**Mutability**: Immutable

#### 2. Session Memory

**Scope**: User session (current learning session)

```python
@dataclass(frozen=True)
class SessionState:
    """Session-level data"""
    creator_id: str
    platforms: list[str]
    job_count: int
    total_recommendations: int
    # ...session aggregate data
```

**Lifecycle**: Persists across multiple jobs in session
**Storage**: In-memory or Redis
**Access**: Queried by planners and agents
**Mutability**: Mutable (track session statistics)

#### 3. Creator Memory (Medium-term)

**Scope**: Creator's historical data

```python
@dataclass(frozen=True)
class CreatorProfile:
    """Creator's preferences and strategy"""
    creator_id: str
    learning_version: str
    preferred_platforms: list[str]
    tone_of_voice: str
    editing_style: str
    # ...creator's profile
```

**Lifecycle**: Persists indefinitely, updated over time
**Storage**: Database (Postgres)
**Access**: Loaded at job start, updated at job end
**Mutability**: Updates create new versions

#### 4. Learning Memory (Long-term)

**Scope**: What system learned about creator

```python
@dataclass(frozen=True)
class LearningMemory:
    """Historical learning data"""
    creator_id: str
    experiments: list[ExperimentRecord]
    recommendations_seen: list[RecommendationAcceptance]
    optimization_history: list[OptimizationHistory]
    feature_importance: dict[str, float]
    # ...learning history
```

**Lifecycle**: Persists indefinitely
**Storage**: Database with tiered access (hot/cold)
**Access**: Loaded for learning, analyzed for insights
**Mutability**: Append-only (add new experiments, not modify)

#### 5. External Memory

**Scope**: External resources

**Types**:

- **File storage**: Generated content, embeddings
- **Cache**: Recommendation cache, provider responses
- **Search index**: Query historical data
- **Data warehouse**: Analytics and reporting

**Access**: Through provider abstraction
**Mutability**: Depends on resource type

### Memory Access Patterns

Different patterns for different layers:

```
Agent execution:
  1. Load Context (passed as parameter)
  2. Load CreatorProfile (query by creator_id)
  3. Query LearningMemory (search by pattern)
  4. Access external caches if needed
  5. Return results
```

```
Learning update:
  1. Analyze learning results
  2. Update CreatorProfile (new version)
  3. Append to LearningMemory (new records)
  4. Invalidate related caches
```

### Separation Benefits

1. **Performance**: Query only relevant memory layer
2. **Scalability**: Different layers scale differently
3. **Consistency**: Clear consistency boundaries
4. **Testing**: Can mock different memory layers
5. **Evolution**: Can change storage backend per layer
6. **Privacy**: Different access controls per layer

## Benefits

✓ **Clear responsibilities**: Each layer has specific purpose
✓ **Performance**: Optimized for access patterns
✓ **Scalability**: Layers can scale independently
✓ **Evolution**: Can upgrade storage independently
✓ **Testing**: Mock different memory layers easily

## Consequences

**Positive:**

- Flexible storage choices per layer
- Natural performance optimization
- Easy to reason about memory management
- Supports multi-node deployments

**Negative:**

- More complex memory management
- Consistency issues between layers
- Requires careful cache invalidation
- Data duplication between layers
- Harder to have complete view of memory

## Consistency Strategy

Handle consistency between layers:

1. **Context is authoritative**: Agents trust context
2. **CreatorProfile is authoritative**: Profile updates override learning suggestions
3. **LearningMemory is append-only**: Never modify, only append
4. **Caches are derivable**: Can be invalidated and rebuilt
5. **External memory is eventual**: May lag but eventually consistent

### Cache Invalidation

When to invalidate caches:

```python
def update_creator_profile(creator_id, new_profile):
    # Update profile
    save_profile(new_profile)

    # Invalidate dependent caches
    invalidate_recommendation_cache(creator_id)
    invalidate_analysis_cache(creator_id)
    # But don't invalidate LearningMemory (it's append-only)
```

## Storage Implementation

Example storage per layer:

| Layer    | Primary      | Backup        | Cache         |
| -------- | ------------ | ------------- | ------------- |
| Context  | Python dict  | None          | N/A           |
| Session  | Redis        | Postgres      | In-memory     |
| Creator  | Postgres     | Backup DB     | Redis         |
| Learning | Postgres     | S3 (archival) | Elasticsearch |
| External | Per provider | Per provider  | Redis         |

## Testing Memory

Mock different layers:

```python
def test_learning_with_rich_history():
    """Test with populated learning memory"""
    memory = LearningMemory(
        creator_id="creator-1",
        experiments=[...100 experiments...],
        recommendations_seen=[...1000 recommendations...],
    )

    result = generate_recommendations(memory)
    assert len(result) > 0

def test_learning_cold_start():
    """Test new creator with no history"""
    memory = LearningMemory(
        creator_id="creator-new",
        experiments=[],
        recommendations_seen=[],
    )

    result = generate_recommendations(memory)
    # Should use defaults
    assert len(result) > 0
```

## Future Evolution

- **Distributed memory**: Replicate memory across nodes
- **Sharded memory**: Split learning memory by creator
- **Memory compression**: Archive old learning data
- **Adaptive caching**: Cache based on access patterns
- **Memory fusion**: Combine insights from multiple creators
- **Streaming memory**: Stream large memory datasets

## See Also

- ADR-002: Immutable Domain Models (memory uses immutable models)
- ADR-006: Learning Feedback Loop (learning memory stores feedback)

## References

- M7 Memory Platform: Memory abstractions
- M14 Learning: LearningMemory, CreatorProfile implementations
- M14 Phase 1: Learning Foundation models
- M14 Phase 4: Production readiness (memory statistics, dashboard)
