# Video Intelligence Runtime: Quick Reference

## Imports

```python
from aura_backend.video import (
    # Core models
    Video, VideoMetadata, Observation, Timeline, TimelineEvent,
    AnalysisSession,  # NEW: Groups complete analysis runs
    ObservationType, TimelineEventType, VideoCodec, AudioCodec,
    
    # Providers
    VideoProvider, SpeechProvider, OCRProvider, VisionProvider,
    FFmpegVideoProvider, WhisperSpeechProvider, TesseractOCRProvider, OpenCVVisionProvider,
    ProviderRegistry,
    
    # Mappers
    SpeechMapper, OCRMapper, VisionMapper,
    
    # Pipeline
    VideoIngestionPipeline,
)
```

## Analysis Sessions

```python
# Create session to group complete analysis run
session = AnalysisSession(
    video_id="vid-1",
    session_type="initial",  # initial, refinement, comparison
    status="pending",         # pending, in_progress, completed, failed
)

# Mark session in progress
session = AnalysisSession(
    id=session.id,
    video_id=session.video_id,
    session_type=session.session_type,
    status="in_progress",
    started_at=datetime.utcnow(),
)

# Add observations to session (accumulates IDs)
observation_ids = session.observation_ids + [obs1.id, obs2.id]
session = AnalysisSession(
    id=session.id,
    video_id=session.video_id,
    session_type=session.session_type,
    status=session.status,
    started_at=session.started_at,
    observation_ids=observation_ids,
)

# Complete session with metrics
session = AnalysisSession(
    id=session.id,
    video_id=session.video_id,
    session_type=session.session_type,
    status="completed",
    started_at=session.started_at,
    completed_at=datetime.utcnow(),
    observation_ids=observation_ids,
    metrics={"observation_count": len(observation_ids)},
)

# Check session state
print(f"Duration: {session.duration_seconds} seconds")
print(f"Is active: {session.is_active}")
print(f"Is complete: {session.is_complete}")
```

## Creating Observations

```python
# Speech observation
obs = Observation(
    video_id="vid-1",
    observation_type=ObservationType.SPEECH,
    source_agent="SpeechAgent",
    start_timestamp=0.0,
    end_timestamp=3.0,
    confidence=0.95,
    payload={"text": "Hello", "speaker": "Alice", "language": "en"},
    metadata={"source_provider": "whisper"},
)

# Object detection observation
obs = Observation(
    video_id="vid-1",
    observation_type=ObservationType.OBJECT,
    source_agent="ObjectAnalysisAgent",
    start_timestamp=5.0,
    end_timestamp=6.0,
    confidence=0.87,
    payload={"class": "person", "bbox": {"x": 100, "y": 150, "w": 200, "h": 400}},
    metadata={"source_provider": "yolo"},
)
```

## Working with Timeline

```python
# Create timeline with events and observations
timeline = Timeline(
    video_id="vid-1",
    events=[
        TimelineEvent(
            video_id="vid-1",
            event_type=TimelineEventType.VIDEO_IMPORTED,
            data={"file_path": "video.mp4", "duration_seconds": 60.0},
            source="VideoIngestionPipeline",
        )
    ],
    observations=[obs1, obs2, obs3],
)

# Query by observation type
speech_obs = timeline.get_observations_by_type(ObservationType.SPEECH)
object_obs = timeline.get_observations_by_type(ObservationType.OBJECT)

# Query by timestamp range
obs_in_range = timeline.get_observations_in_range(start_timestamp=5.0, end_timestamp=10.0)

# Query events by type
import_events = timeline.get_events_by_type(TimelineEventType.VIDEO_IMPORTED)
```

## Using Mappers

```python
from aura_backend.video import TranscriptSegment, SpeechMapper, OCRMapper, VisionMapper

# Map speech transcription
segments = [
    TranscriptSegment(
        video_id="vid-1",
        start_timestamp=0.0,
        end_timestamp=3.0,
        text="Hello world",
        speaker="Alice",
        confidence=0.95,
        language="en",
    )
]
speech_obs = SpeechMapper.from_transcript_segments("vid-1", segments)

# Map OCR results
ocr_detections = [
    {"text": "SIGN", "confidence": 0.92, "bbox": {"x": 100, "y": 50, "w": 200, "h": 60}}
]
ocr_obs = OCRMapper.from_detections(
    video_id="vid-1",
    start_timestamp=5.0,
    end_timestamp=6.0,
    detections=ocr_detections,
)

# Map object detections
object_detections = [
    {"class": "person", "confidence": 0.95, "bbox": {"x": 100, "y": 150, "w": 200, "h": 400}}
]
vision_obs = VisionMapper.from_object_detections(
    video_id="vid-1",
    start_timestamp=10.0,
    end_timestamp=11.0,
    detections=object_detections,
)

# Map face detections
face_detections = [
    {"confidence": 0.99, "bbox": {"x": 150, "y": 200, "w": 100, "h": 120}}
]
face_obs = VisionMapper.from_face_detections(
    video_id="vid-1",
    start_timestamp=15.0,
    end_timestamp=16.0,
    detections=face_detections,
)
```

## Provider Registry

```python
from aura_backend.video import ProviderRegistry, FFmpegVideoProvider

registry = ProviderRegistry()

# Register providers
registry.register_video_provider("ffmpeg", FFmpegVideoProvider())
registry.register_speech_provider("whisper", WhisperSpeechProvider())
registry.register_ocr_provider("tesseract", TesseractOCRProvider())
registry.register_vision_provider("opencv", OpenCVVisionProvider())

# Retrieve providers
video_provider = registry.get_video_provider("ffmpeg")
speech_provider = registry.get_speech_provider("whisper")
ocr_provider = registry.get_ocr_provider("tesseract")
vision_provider = registry.get_vision_provider("opencv")
```

## Video Ingestion Pipeline (with Sessions)

```python
from aura_backend.video import VideoIngestionPipeline, ProviderRegistry, AnalysisSession

registry = ProviderRegistry()
registry.register_video_provider("ffmpeg", FFmpegVideoProvider())

pipeline = VideoIngestionPipeline(registry, memory_manager=m7_memory)

# 1. Create analysis session to group results
session = await pipeline.create_analysis_session(
    video_id="vid-1",
    session_type="initial",
)

# 2. Ingest video (returns updated session)
video, timeline, session = await pipeline.ingest_video(
    "path/to/video.mp4",
    session=session,
)

# 3. Add observations to session (Phase 2)
observations = [obs1, obs2, obs3]  # From analysis agents
session, timeline = await pipeline.add_observations_to_session(
    session=session,
    observations=observations,
    timeline=timeline,
)

# 4. Complete session
session = await pipeline.complete_session(
    session=session,
    metrics={"observation_count": len(observations)},
)

# 5. Persist to Memory Runtime (ONLY entry point)
await pipeline.persist_session_to_memory(session, video, timeline)

# Results
print(f"Session ID: {session.id}")
print(f"Video ID: {video.id}")
print(f"Status: {session.status}")
print(f"Duration: {session.duration_seconds} seconds")
print(f"Observations: {len(session.observation_ids)}")
```

## Observation Types (Enum)

```python
# Available observation types
ObservationType.SCENE_BOUNDARY      # Scene transitions
ObservationType.SCENE_CONTENT       # Scene descriptions
ObservationType.SPEECH              # Transcribed speech
ObservationType.SILENCE             # Silent segments
ObservationType.MUSIC               # Music detection
ObservationType.SOUND_EFFECT        # Sound effects
ObservationType.OCR                 # Text in images
ObservationType.FACE                # Face detection
ObservationType.OBJECT              # Object detection
ObservationType.LOGO                # Logo detection
ObservationType.TEXT                # Text observations
ObservationType.ACTIVITY            # Activity detection
```

## Timeline Event Types (Enum)

```python
# Available event types
TimelineEventType.VIDEO_IMPORTED         # Video file ingested
TimelineEventType.FRAMES_EXTRACTED       # Frames extracted
TimelineEventType.SCENE_DETECTED         # Scenes detected
TimelineEventType.AUDIO_EXTRACTED        # Audio extracted
TimelineEventType.TRANSCRIPT_GENERATED   # Speech transcribed
TimelineEventType.OCR_COMPLETED          # Text extracted
TimelineEventType.FACE_DETECTED          # Faces detected
TimelineEventType.OBJECT_DETECTED        # Objects detected
TimelineEventType.OBSERVATION_CREATED    # Observation stored
```

## Serialization

```python
# All objects can be serialized to dict
obs_dict = observation.to_dict()
video_dict = video.to_dict()
metadata_dict = video.metadata.to_dict()
timeline_dict = timeline.to_dict()

# Serialize for storage/API response
import json
json_str = json.dumps(obs_dict)
```

## Phase 2 Integration Points

### Adding an Analysis Agent

```python
from aura_backend.orchestration import ExecutableAgent

class MyAnalysisAgent(ExecutableAgent):
    async def execute(self, frames, context):
        # Process frames
        results = ...
        
        # Convert to observations via mapper
        observations = MyMapper.from_results(video_id, results)
        
        # Return observations
        return observations

# Register with M6 agent registry
agent_registry.register("my_agent", MyAnalysisAgent())
```

### Orchestrating Analysis via M8

```python
from aura_backend.orchestration import ExecutionEngine

# Build DAG
dag = {
    "frames": ...,
    "speech_agent": {"depends_on": ["frames"]},
    "ocr_agent": {"depends_on": ["frames"]},
    "vision_agent": {"depends_on": ["frames"]},
}

# Execute with M8 engine
engine = ExecutionEngine(agent_registry)
results = await engine.execute_graph(dag, context)

# Results contain observations from all agents
all_observations = results["speech_agent"] + results["ocr_agent"] + results["vision_agent"]

# Create/update timeline
timeline = Timeline(video_id=video.id, observations=all_observations)
```

### Storing in M7 Memory

```python
from aura_backend.memory import MemoryManager

memory = MemoryManager()

# Store video
await memory.store_episodic(video.to_dict(), node_type="video", video_id=video.id)

# Store observations
for obs in all_observations:
    await memory.store_episodic(obs.to_dict(), node_type="observation", video_id=video.id)

# Build knowledge graph
for obs in all_observations:
    node = KnowledgeNode(
        video_id=video.id,
        node_type=obs.observation_type.value,
        label=str(obs.payload),
        observations=[obs.id],
    )
    await memory.store_semantic(node.to_dict())
```

## Common Patterns

### Single Video Analysis Flow
```python
# 1. Ingest
video, timeline = await pipeline.ingest_video("video.mp4")

# 2. Analyze (Phase 2)
frames = extract_frames(video)
agents_results = await engine.execute_analysis_dag(frames)

# 3. Map to observations
all_observations = []
for agent_name, results in agents_results.items():
    mapper = get_mapper_for_agent(agent_name)
    observations = mapper.convert(video.id, results)
    all_observations.extend(observations)

# 4. Update timeline
timeline = Timeline(video_id=video.id, observations=all_observations)

# 5. Store (Phase 4)
await memory.store(video, timeline)
```

### Query Analysis Results
```python
# Find all speech in video
speech_obs = timeline.get_observations_by_type(ObservationType.SPEECH)
for obs in speech_obs:
    print(f"{obs.start_timestamp}s: {obs.payload['text']}")

# Find all objects detected between 10-20 seconds
objects_in_range = timeline.get_observations_in_range(10.0, 20.0)
objects = [o for o in objects_in_range if o.observation_type == ObservationType.OBJECT]
```

## Testing

```python
import pytest
from aura_backend.video import Observation, ObservationType, Timeline

def test_observation_creation():
    obs = Observation(
        video_id="test",
        observation_type=ObservationType.SPEECH,
        source_agent="SpeechAgent",
    )
    assert obs.observation_type == ObservationType.SPEECH

def test_timeline_queries():
    obs1 = Observation(video_id="v1", observation_type=ObservationType.SPEECH)
    obs2 = Observation(video_id="v1", observation_type=ObservationType.OBJECT)
    
    timeline = Timeline(video_id="v1", observations=[obs1, obs2])
    
    speech = timeline.get_observations_by_type(ObservationType.SPEECH)
    assert len(speech) == 1
```

Run all Phase 1 tests:
```bash
PYTHONPATH=src pytest tests/video/test_phase1_integration.py -v
```

## Debug/Troubleshooting

### Check Observation Creation
```python
obs = Observation(...)
print(f"ID: {obs.id}")
print(f"Type: {obs.observation_type}")
print(f"Payload: {obs.payload}")
print(f"Metadata: {obs.metadata}")
```

### Verify Timeline Consistency
```python
timeline = Timeline(video_id="v1", observations=obs_list)
print(f"Observation count: {len(timeline.observations)}")
print(f"Event count: {len(timeline.events)}")
print(f"By type: {timeline.get_observations_by_type(ObservationType.SPEECH)}")
```

### Check Provider Registry
```python
registry = ProviderRegistry()
print(f"Video providers: {registry._video_providers.keys()}")
print(f"Speech providers: {registry._speech_providers.keys()}")
provider = registry.get_video_provider("ffmpeg")
print(f"Provider class: {type(provider).__name__}")
```

## References

- **models.py**: Core data structures
- **providers.py**: External library interfaces
- **mappers.py**: Result conversion logic
- **ingestion.py**: Pipeline orchestration
- **README.md**: User guide
- **PHASE1_ARCHITECTURE.md**: Detailed architecture
- **test_phase1_integration.py**: Usage examples and tests
