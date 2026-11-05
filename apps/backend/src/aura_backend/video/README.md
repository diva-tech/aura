# Video Intelligence Runtime

Analyzes videos and converts findings into structured knowledge.

**Does NOT**: edit, render, or generate videos  
**Does**: analyze, understand, and extract knowledge from videos

## Quick Start

### Basic Usage

```python
from aura_backend.video import (
    VideoIngestionPipeline,
    ProviderRegistry,
    FFmpegVideoProvider,
)

# Create registry and register providers
registry = ProviderRegistry()
registry.register_video_provider("ffmpeg", FFmpegVideoProvider())

# Create pipeline
pipeline = VideoIngestionPipeline(registry)

# Ingest video (Phase 2)
video, timeline = await pipeline.ingest_video("path/to/video.mp4")

# Analyze video (Phase 2-3)
# Pipeline will coordinate speech, OCR, and vision analysis
# All discoveries become Observation objects in timeline

# Query results
speech_observations = timeline.get_observations_by_type(ObservationType.SPEECH)
object_observations = timeline.get_observations_by_type(ObservationType.OBJECT)
```

### Analysis Sessions

Sessions group complete analysis runs for tracking and traceability:

```python
from aura_backend.video import AnalysisSession

# Create session
session = await pipeline.create_analysis_session(
    video_id="vid-1",
    session_type="initial",  # initial, refinement, comparison
)

# Ingest video with session
video, timeline, session = await pipeline.ingest_video(
    "path/to/video.mp4",
    session=session,
)

# Add observations to session (Phase 2)
session, timeline = await pipeline.add_observations_to_session(
    session=session,
    observations=[obs1, obs2, obs3],
    timeline=timeline,
)

# Complete session with metrics
session = await pipeline.complete_session(
    session=session,
    metrics={"observation_count": 3},
)

# Persist to Memory Runtime (ONLY entry point)
await pipeline.persist_session_to_memory(session, video, timeline)
```

**Key Principles:**
- Sessions group one complete analysis run
- Providers remain stateless (input → output only)
- Only pipeline persists to Memory Runtime
- Sessions support initial/refinement/comparison analysis types

See [ANALYSIS_SESSION.md](./ANALYSIS_SESSION.md) for detailed guide.

### Understanding the Model

Everything discovered in a video becomes an **Observation** — the universal model:

```python
from aura_backend.video import Observation, ObservationType

# Speech discovery
speech_obs = Observation(
    video_id="vid-1",
    observation_type=ObservationType.SPEECH,
    source_agent="SpeechAgent",
    start_timestamp=0.0,
    end_timestamp=3.0,
    confidence=0.95,
    payload={
        "text": "Hello world",
        "speaker": "Alice",
        "language": "en",
    },
    metadata={
        "source_provider": "whisper",
        "segment_id": "seg-123",
    },
)

# Object detection discovery
object_obs = Observation(
    video_id="vid-1",
    observation_type=ObservationType.OBJECT,
    source_agent="ObjectAnalysisAgent",
    start_timestamp=5.0,
    end_timestamp=6.0,
    confidence=0.87,
    payload={
        "class": "person",
        "bbox": {"x": 100, "y": 150, "w": 200, "h": 400},
    },
    metadata={
        "source_provider": "yolo",
    },
)
```

The **Timeline** is the canonical execution model:

```python
from aura_backend.video import Timeline, TimelineEvent, TimelineEventType

# Timeline tracks all events and observations
timeline = Timeline(
    video_id="vid-1",
    events=[
        TimelineEvent(
            event_type=TimelineEventType.VIDEO_IMPORTED,
            data={"file_path": "video.mp4", "duration_seconds": 60.0},
        ),
        TimelineEvent(
            event_type=TimelineEventType.FRAMES_EXTRACTED,
            data={"frame_count": 1800},
        ),
        # More events...
    ],
    observations=[speech_obs, object_obs, ...],
)

# Query by type
timeline.get_observations_by_type(ObservationType.SPEECH)
timeline.get_observations_by_type(ObservationType.OBJECT)

# Query by timestamp range
timeline.get_observations_in_range(start_timestamp=5.0, end_timestamp=10.0)
```

## Architecture

### Core Components

1. **Models** (`models.py`)
   - Immutable domain objects (frozen dataclasses)
   - Observation: universal model for all discoveries
   - Timeline: canonical execution model
   - VideoMetadata: video file information

2. **Providers** (`providers.py`)
   - Abstract interfaces for external libraries
   - Reference implementations (FFmpeg, Whisper, Tesseract, OpenCV)
   - ProviderRegistry for dynamic composition

3. **Mappers** (`mappers.py`)
   - Convert provider results to Observation objects
   - Critical boundary preventing library leakage
   - SpeechMapper, OCRMapper, VisionMapper

4. **Pipeline** (`ingestion.py`)
   - End-to-end orchestrator
   - Coordinates metadata extraction, analysis, and storage

### Provider Abstraction

All external libraries are isolated behind provider interfaces:

```
FFmpeg
  ↓
[VideoProvider interface]
  ↓
VideoIngestionPipeline
```

```
Whisper
  ↓
[SpeechProvider interface]
  ↓
[SpeechMapper]
  ↓
Observation
```

This ensures:
- No third-party objects leak into domain layer
- Easy to swap providers (e.g., different speech models)
- Testable with mock providers

### Integration with AURA Milestones

- **M1-M5**: Independent; no changes required
- **M6**: Analysis agents as ExecutableAgent subclasses (Phase 2)
- **M7**: Memory runtime integration for storage (Phase 4)
- **M8**: Task orchestration for parallel analysis (Phase 2)

## Implementation Phases

### Phase 1: ✅ COMPLETE
Foundation layer with models, providers, mappers, and pipeline

- Immutable domain models
- Provider interfaces and reference implementations
- Mapper conversions to Observation
- Ingestion pipeline structure

### Phase 2: In Progress
Core infrastructure with frame extraction and analysis agents

- Frame extraction from video
- SpeechAnalysisAgent, OCRAnalysisAgent, VisionAnalysisAgent
- Concurrent execution via M8 ExecutionEngine
- Timeline enrichment with events

### Phase 3: Not Started
Agent implementations that produce Observations

- Full agent logic for each analysis type
- Integration with ML models
- Confidence scoring and quality metrics

### Phase 4: Not Started
Knowledge graph and Memory Runtime integration

- Store observations in M7 episodic memory
- Build KnowledgeNodes from observations
- Create semantic graph of discovered entities
- Search and retrieval APIs

### Phase 5: Not Started
Observability and monitoring

- Event tracking
- Performance metrics
- Dashboard and visualization

### Phase 6: Not Started
Tests and documentation

- Comprehensive test coverage
- User guides
- API documentation

## Module Exports

```python
from aura_backend.video import (
    # Domain models
    Video,
    VideoMetadata,
    VideoCodec,
    AudioCodec,
    Observation,
    ObservationType,
    Timeline,
    TimelineEvent,
    TimelineEventType,
    AnalysisSession,  # NEW: Groups complete analysis runs
    Frame,
    Scene,
    AudioSegment,
    TranscriptSegment,
    KnowledgeNode,
    
    # Provider interfaces
    VideoProvider,
    SpeechProvider,
    OCRProvider,
    VisionProvider,
    
    # Reference implementations
    FFmpegVideoProvider,
    WhisperSpeechProvider,
    TesseractOCRProvider,
    OpenCVVisionProvider,
    ProviderRegistry,
    
    # Mappers
    SpeechMapper,
    OCRMapper,
    VisionMapper,
    
    # Pipeline
    VideoIngestionPipeline,
)
```

## Observation Types

All discoveries are categorized by observation type:

- `SCENE_BOUNDARY`: Scene transitions
- `SCENE_CONTENT`: Scene descriptions
- `SPEECH`: Transcribed speech
- `SILENCE`: Silent segments
- `MUSIC`: Music detection
- `SOUND_EFFECT`: Sound effect detection
- `OCR`: Text in images
- `FACE`: Face detection
- `OBJECT`: Object detection
- `LOGO`: Logo detection
- `TEXT`: Text-specific observations
- `ACTIVITY`: Action/activity detection

## Timeline Event Types

Events track pipeline execution:

- `VIDEO_IMPORTED`: Video file ingested
- `FRAMES_EXTRACTED`: Frames extracted from video
- `SCENE_DETECTED`: Scene boundaries detected
- `AUDIO_EXTRACTED`: Audio extracted
- `TRANSCRIPT_GENERATED`: Speech transcribed
- `OCR_COMPLETED`: Text extracted
- `FACE_DETECTED`: Faces detected
- `OBJECT_DETECTED`: Objects detected
- `OBSERVATION_CREATED`: Observation stored

## Testing

Run Phase 1 integration tests:

```bash
PYTHONPATH=src pytest tests/video/test_phase1_integration.py -v
```

Tests cover:
- Model immutability
- Provider interfaces
- Provider registry
- Mapper conversions
- Ingestion pipeline
- Timeline queries
- Serialization

## Architecture Documentation

See [PHASE1_ARCHITECTURE.md](./PHASE1_ARCHITECTURE.md) for detailed architecture, design decisions, and extensibility points.

## Design Principles

1. **Provider Abstraction**: External libraries isolated behind interfaces
2. **Observation Universality**: Single model for all discoveries
3. **Timeline-First**: Everything becomes a timeline event
4. **Immutability**: All domain objects frozen
5. **Separation of Concerns**: Models → Providers → Mappers → Pipeline

## Key Decisions

- **Single Observation model** instead of result-type-specific classes
- **Timeline as execution model** instead of state machines
- **Frozen dataclasses** for immutability and thread safety
- **ProviderRegistry** for dynamic composition
- **Mapper boundary** preventing library leakage

## Performance Characteristics

- **Video import**: O(1) filesystem check + metadata extraction (FFmpeg subprocess)
- **Observation lookup**: O(n) list filtering; indexed queries in Phase 4
- **Timeline queries**: O(n) linear search; batch lookups supported
- **Mapper conversion**: O(n) in detection count; stateless and parallelizable

## Future Enhancements

- **Indexed timeline queries** (by timestamp, type, agent)
- **Streaming frame extraction** (Phase 2)
- **Batch observation insertion** (optimization)
- **Caching layer** for frequent queries
- **Distributed analysis** via M8 task orchestration
- **Hierarchical observations** (temporal relationships)

## License & Ownership

Part of AURA (Autonomous Understanding & Reasoning Agent) Platform  
Lead: AI Platform Engineering  
Milestones: M1-M8 FROZEN (no changes); M9 Video Intelligence Runtime

---

**Phase 1 Status**: ✅ Complete  
**Last Updated**: 2026-07-28  
**Next Phase**: Phase 2 (Core Infrastructure)
