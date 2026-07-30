# ADR-009: Event Sourcing

**Date**: 2026-07-30  
**Status**: Accepted  
**Deciders**: Architecture Team  
**Affects**: M2, M6, M8-M14

## Context

Traditional state management has problems:

- Difficult to debug: what led to this state?
- No audit trail: which system modified it?
- Difficult to replay: can't recreate past states
- No undo/redo: hard to support rollback

Complex workflows need complete history:

- Understand execution flow
- Debug failures
- Audit for compliance
- Replay for testing
- Support time-travel debugging

## Decision

Use **Event Sourcing** as core architectural pattern.

### Event Model

Every state change is an immutable event:

```python
@dataclass(frozen=True)
class Event:
    """Immutable event"""
    event_id: str = ""
    job_id: str = ""
    timestamp: datetime = None
    event_type: str = ""  # Subclass name

    def to_dict(self) -> dict:
        """Serialize to dict"""
        pass
```

### Event Types

Throughout the system:

- **M2 Runtime**: PluginLoaded, RuntimeStarted, RuntimeStopped
- **M6 Agents**: StageStarted, StageCompleted, StageFailed
- **M8 Tasks**: TaskQueued, TaskStarted, TaskCompleted
- **M14 Learning**: LearningStarted, LearningCompleted, RecommendationGenerated

### Event Stream

Events form a complete history:

```
1. LearningStarted(job_id="job-1", stage_count=8)
2. StageStarted(stage_type="validate", ...)
3. StageCompleted(duration=100ms, ...)
4. StageStarted(stage_type="auth", ...)
5. StageCompleted(duration=200ms, ...)
...
N. LearningCompleted(is_success=true, recommendations=5)
```

### Replay

From event stream, can:

1. **Rebuild state**: Apply events in order to recreate state at any point
2. **Understand flow**: Trace execution through events
3. **Debug**: See exactly what happened
4. **Test**: Replay against modified logic

```python
def rebuild_state(events: list[Event]) -> State:
    """Replay events to rebuild state"""
    state = State()
    for event in events:
        state = state.apply(event)
    return state
```

### Event Storage

Events stored persistently (not in memory):

1. **Event log**: Append-only log of all events
2. **Snapshots**: Periodic snapshots for faster replay
3. **Indexing**: Index events by job_id, timestamp, etc.

```python
class EventStore:
    async def append(self, event: Event):
        """Append event to log"""

    async def get_events(self, job_id: str) -> list[Event]:
        """Get all events for job"""

    async def get_snapshot(self, job_id: str, time: datetime) -> Snapshot:
        """Get snapshot near time"""
```

### Event Versioning

Events may change over time:

```python
@dataclass(frozen=True)
class StageCompleted:
    version: int = 1  # Event version
    stage_type: str = ""
    duration_ms: float = 0.0

    @classmethod
    def from_v1(cls, data: dict) -> "StageCompleted":
        """Migrate from version 1"""
        return cls(
            version=1,
            stage_type=data["stage_type"],
            duration_ms=data["duration_ms"]
        )
```

## Benefits

✓ **Complete audit trail**: Every change is recorded
✓ **Debuggability**: Can trace exact execution flow
✓ **Replayability**: Can recreate past states
✓ **Compliance**: Natural audit log for regulations
✓ **Analytics**: Events are natural data source
✓ **Recovery**: Can recover from failures
✓ **Time-travel**: Debug at any historical point

## Consequences

**Positive:**

- Excellent for debugging and compliance
- Natural fit with immutable models
- Enables sophisticated analytics
- Supports regulatory requirements

**Negative:**

- Requires event storage infrastructure
- Events must be designed carefully (versioning needed)
- Replay can be slow for long histories
- More storage required
- Requires careful migration when events change

## Event Examples

### M6 Agent Events

```python
@dataclass(frozen=True)
class StageStarted(Event):
    stage_type: str = ""
    stage_id: str = ""
    platform: str = ""
    provider_name: str = ""

@dataclass(frozen=True)
class StageCompleted(Event):
    stage_type: str = ""
    duration_seconds: float = 0.0
    output_data: dict = None

@dataclass(frozen=True)
class StageFailed(Event):
    failure: Failure = None
    will_retry: bool = False
```

### M14 Learning Events

```python
@dataclass(frozen=True)
class LearningStarted(Event):
    stage_count: int = 0
    platforms: tuple[str, ...] = None

@dataclass(frozen=True)
class LearningCompleted(Event):
    is_success: bool = False
    successful_platforms: tuple[str, ...] = None
    recommendations_generated: int = 0
```

## Testing with Events

Events make testing easier:

```python
async def test_learning_recovery():
    """Test recovery from failure"""
    events = [
        LearningStarted(job_id="job-1", stage_count=8),
        StageStarted(stage_type="validate"),
        StageCompleted(duration=100),
        StageStarted(stage_type="auth"),
        StageFailed(failure=Failure(...)),  # Failure event
        StageStarted(stage_type="auth"),  # Retry
        StageCompleted(duration=200),  # Success on retry
    ]

    result = replay_events(events)
    assert result.success
```

## Future Evolution

- **CQRS**: Separate command and query sides using events
- **Event-driven microservices**: Coordinate via events
- **Temporal analytics**: Analyze event patterns over time
- **ML on events**: Predict failures from event patterns
- **Event compression**: Compress old event logs
- **Stream processing**: Real-time analytics on event stream

## See Also

- ADR-002: Immutable Domain Models (natural fit)
- ADR-006: Learning Feedback Loop (events feed learning)

## References

- M2 Runtime: Event bus (events are core infrastructure)
- M6 Agent Runtime: Lifecycle events
- M8 Task Orchestration: Task execution events
- M14 Learning: Learning lifecycle events
