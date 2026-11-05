# AnalysisSession: Grouping Complete Analysis Runs

**Added After Phase 1 Approval**  
**Status**: Integrated into Phase 1

## Overview

`AnalysisSession` is a lightweight domain object that groups one complete video analysis run. It provides essential tracking and context for all results produced during analysis.

## Why AnalysisSession?

Before sessions:
```
Video → Timeline → Observations → Memory Runtime
(No grouping of related analysis)
```

After sessions:
```
AnalysisSession
├── video_id (which video)
├── session_type (initial/refinement/comparison)
├── status (pending/in_progress/completed/failed)
├── started_at, completed_at (when)
├── duration_seconds (how long)
├── timeline_id (points to Timeline)
├── observation_ids (all discoveries)
├── knowledge_node_ids (semantic graph)
└── metrics (analysis stats)
```

**Benefits:**
1. **Traceability**: Know exactly which video, when, and what was analyzed
2. **Grouping**: All results from one run stay together
3. **Tracking**: Monitor analysis progress and performance
4. **Retrieval**: Query "give me all observations from session X"
5. **Comparison**: Support refinement and comparison sessions

## Definition

```python
@dataclass(frozen=True)
class AnalysisSession:
    """Immutable analysis session - groups one complete analysis run."""
    id: str                              # Unique session ID
    video_id: str                        # Which video
    session_type: str                    # "initial", "refinement", etc.
    status: str                          # pending, in_progress, completed, failed
    started_at: datetime                 # When started
    completed_at: Optional[datetime]     # When finished
    timeline_id: Optional[str]           # Reference to Timeline
    observation_ids: List[str]           # All observation IDs found
    knowledge_node_ids: List[str]        # Knowledge graph nodes
    metrics: Dict[str, Any]              # Analysis metrics
    metadata: Dict[str, Any]             # Extensibility
    
    # Properties
    duration_seconds: Optional[float]    # computed from started/completed
    is_active: bool                      # status == "in_progress"
    is_complete: bool                    # status == "completed"
```

## Session Types

```python
"initial"        # First complete analysis of video
"refinement"     # Re-analysis with improved models
"comparison"     # Side-by-side analysis with different parameters
"partial"        # Focused analysis on time range
```

## Session Status Flow

```
pending → in_progress → completed
             ↓
           failed
```

- **pending**: Created, not yet started
- **in_progress**: Currently analyzing
- **completed**: Finished successfully
- **failed**: Encountered error

## Usage in Pipeline

### 1. Create Session

```python
session = await pipeline.create_analysis_session(
    video_id="vid-1",
    session_type="initial",
)
# Returns: session with status="pending"
```

### 2. Ingest Video

```python
video, timeline, session = await pipeline.ingest_video(
    file_path="video.mp4",
    session=session,  # Optional, creates if None
)
# Returns: (video, timeline, session with status="in_progress")
```

### 3. Add Observations (Phase 2)

```python
# After analysis agents produce observations
session, timeline = await pipeline.add_observations_to_session(
    session=session,
    observations=[obs1, obs2, obs3],
    timeline=timeline,
)
# Updates session.observation_ids and timeline.observations
```

### 4. Complete Session

```python
session = await pipeline.complete_session(
    session=session,
    metrics={
        "duration_seconds": 45.2,
        "observation_count": 42,
        "speech_segments": 8,
        "objects_detected": 12,
    },
)
# Returns: session with status="completed" and metrics set
```

### 5. Persist to Memory Runtime

```python
await pipeline.persist_session_to_memory(
    session=session,
    video=video,
    timeline=timeline,
)
# Stores: video, session, timeline, all observations, all events
# IMPORTANT: Only entry point for Memory Runtime persistence
```

## Complete Flow Example

```python
from aura_backend.video import (
    VideoIngestionPipeline, ProviderRegistry, FFmpegVideoProvider
)

# Setup
registry = ProviderRegistry()
registry.register_video_provider("ffmpeg", FFmpegVideoProvider())
pipeline = VideoIngestionPipeline(registry, memory_manager=m7_memory)

# 1. Create session
session = await pipeline.create_analysis_session(
    video_id="vid-1",
    session_type="initial",
)

# 2. Ingest video
video, timeline, session = await pipeline.ingest_video(
    "path/to/video.mp4",
    session=session,
)

# 3. Coordinate analysis agents (Phase 2)
# Agents produce observations via providers + mappers
observations = []
for agent in [speech_agent, ocr_agent, vision_agent]:
    obs = await agent.analyze(frames, context)
    observations.extend(obs)

# 4. Add observations to session
session, timeline = await pipeline.add_observations_to_session(
    session=session,
    observations=observations,
    timeline=timeline,
)

# 5. Complete session
session = await pipeline.complete_session(
    session=session,
    metrics={"observation_count": len(observations)},
)

# 6. Persist (ONLY via pipeline)
await pipeline.persist_session_to_memory(session, video, timeline)

# Result: Complete analysis session persisted to Memory Runtime
# Ready for retrieval: "show me all observations from session X"
```

## Provider Independence

**Critical Design Principle**: Providers are **stateless**

❌ Wrong:
```python
provider = WhisperSpeechProvider()
provider.session = session  # Don't do this!
results = provider.transcribe(audio)
```

✅ Right:
```python
provider = WhisperSpeechProvider()  # Stateless
results = provider.transcribe(audio)  # Just input → output

# Pipeline handles session association
observations = SpeechMapper.from_results(session.video_id, results)
session, timeline = await pipeline.add_observations_to_session(
    session, observations, timeline
)
```

**Why**: 
- Providers are simple, reusable, testable
- Sessions are pipeline's responsibility
- Clear separation of concerns
- Providers can be swapped without session logic changes

## Querying Sessions

Phase 4 (Memory Runtime integration) will enable queries like:

```python
# Get all sessions for a video
sessions = await memory.query(
    memory_type="episodic",
    object_type="AnalysisSession",
    video_id="vid-1",
)

# Get all observations from a session
observations = await memory.query(
    memory_type="episodic",
    object_type="Observation",
    session_id="session-xyz",
)

# Get completed sessions in time range
completed = await memory.query(
    object_type="AnalysisSession",
    status="completed",
    started_at_after=datetime(2026, 7, 1),
)
```

## Metrics Examples

Sessions track analysis performance:

```python
metrics = {
    "duration_seconds": 45.2,
    "observation_count": 42,
    "observation_breakdown": {
        "speech": 8,
        "ocr": 5,
        "objects": 12,
        "faces": 3,
        "scenes": 14,
    },
    "confidence_stats": {
        "min": 0.72,
        "max": 0.99,
        "avg": 0.91,
    },
    "frame_count": 1800,
    "agents_used": ["speech_agent", "ocr_agent", "vision_agent"],
    "providers_used": ["whisper", "tesseract", "yolo"],
}
```

## Session Immutability

Sessions are frozen dataclasses. To update a session:

```python
# Don't mutate
session.status = "completed"  # ❌ Raises FrozenInstanceError

# Create new session with updated fields
session = AnalysisSession(
    id=session.id,
    video_id=session.video_id,
    session_type=session.session_type,
    status="completed",  # ← Updated
    started_at=session.started_at,
    completed_at=datetime.utcnow(),  # ← Updated
    # ... copy other fields unchanged
)
```

This pattern ensures auditability and prevents accidental state corruption.

## Integration with Phase 2

### Frame Extraction
```python
TimelineEvent(
    event_type=TimelineEventType.FRAMES_EXTRACTED,
    data={"frame_count": 1800, "session_id": session.id},
)
```

### Agent Execution
```python
# Each agent tracks which session it's analyzing
for frame in frames:
    obs = await agent.analyze(frame, context={"session_id": session.id})
    # Agent doesn't modify session (stays stateless)
    # Pipeline adds observations to session
```

### Concurrent Analysis
```python
# M8 ExecutionEngine knows about session context
dag = {
    "frames": extracted_frames,
    "speech": {"depends_on": ["frames"]},
    "ocr": {"depends_on": ["frames"]},
    "vision": {"depends_on": ["frames"]},
    "session_context": {"session_id": session.id},  # Tracked
}
```

## Testing Sessions

```python
def test_session_lifecycle():
    # Create
    session = AnalysisSession(video_id="v1", session_type="initial")
    assert session.status == "pending"
    
    # Progress
    session = AnalysisSession(
        id=session.id, video_id=session.video_id,
        status="in_progress", started_at=datetime.utcnow()
    )
    assert session.is_active
    
    # Complete
    session = AnalysisSession(
        id=session.id, video_id=session.video_id,
        status="completed", completed_at=datetime.utcnow()
    )
    assert session.is_complete
    assert session.duration_seconds is not None
```

## Summary

- **Lightweight**: Single focused domain object
- **Immutable**: Frozen dataclass prevents mutations
- **Stateless Providers**: Providers do work, pipeline manages sessions
- **Single Persistence Entry Point**: All Memory Runtime writes via pipeline
- **Extensible**: Metadata field for future session-specific data
- **Ready for Phase 2**: Agents produce observations, pipeline adds to session

This design maintains clean separation of concerns while providing essential tracking for complete analysis runs.
