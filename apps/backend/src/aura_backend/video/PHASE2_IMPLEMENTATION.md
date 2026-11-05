# Milestone 9: Video Intelligence Runtime
## Phase 2 Implementation Guide

**Status: COMPLETE** ✅

Phase 2 builds the complete analysis pipeline on top of Phase 1's foundation. It implements frame extraction, audio extraction, and four analysis agents that produce observations, which are then aggregated into a knowledge graph.

---

## Architecture Overview

### Complete Pipeline Flow

```
Video File
  ↓
VideoProvider.extract_metadata() → VideoMetadata
  ↓
Video + Timeline created, AnalysisSession started
  ↓
┌─────────────────────────────────────────────────────┐
│ Parallel Analysis                                    │
│                                                      │
│ FrameExtractionService ──→ ExtractedFrame[]        │
│   ↓                                                  │
│   SceneAnalysisAgent ──→ Observation(SCENE)         │
│   OCRAnalysisAgent ──→ Observation(OCR)             │
│   VisionAnalysisAgent ──→ Observation(OBJECT/FACE)  │
│                                                      │
│ AudioExtractionService ──→ ExtractedAudioSegment[]  │
│   ↓                                                  │
│   SpeechAnalysisAgent ──→ Observation(SPEECH)       │
│                                                      │
└─────────────────────────────────────────────────────┘
  ↓
Observation[] collected
  ↓
KnowledgeBuilder → KnowledgeNode[]
  ↓
Timeline updated with all events and observations
AnalysisSession finalized with metrics
  ↓
VideoIngestionPipeline.persist_session_to_memory() ←─ ONLY entry point
  ↓
Memory Runtime (M7)
```

---

## Component Breakdown

### 1. Extraction Services

#### FrameExtractionService
- **Responsibility**: Extract frames from video at regular intervals
- **Input**: Video file path, FPS, duration
- **Output**: List[ExtractedFrame]
- **Features**: 
  - Extract keyframes
  - Extract interval frames (e.g., 1 FPS)
  - Provide frame image data (PNG/JPEG encoded)
  - Include frame metadata (number, timestamp, keyframe flag)

```python
frame = ExtractedFrame(
    frame_number=0,
    timestamp_seconds=0.0,
    is_keyframe=True,
    image_data=b"PNG data",  # Encoded image
    width=1920,
    height=1080,
)
```

#### AudioExtractionService
- **Responsibility**: Extract audio from video
- **Input**: Video file path, sample rate, channels
- **Output**: List[ExtractedAudioSegment]
- **Features**:
  - Extract audio data (PCM or compressed)
  - Maintain sample rate and channel info
  - Create time-bounded segments

```python
audio = ExtractedAudioSegment(
    start_timestamp=0.0,
    end_timestamp=60.0,
    audio_data=b"PCM audio data",
    sample_rate=16000,
    channels=1,
)
```

### 2. Analysis Agents

All agents are **provider-aware** but **observation-focused**:
- They use providers (stateless)
- They use mappers (provider result → Observation)
- They return only Observation objects
- They never access Memory Runtime directly

#### SceneAnalysisAgent
- **Consumes**: ExtractedFrame[] (with image data)
- **Uses**: SceneProvider (detects scene boundaries)
- **Produces**: Observation(SCENE_CONTENT)
- **Uses Mapper**: SceneMapper

```python
agent = SceneAnalysisAgent(scene_provider)
observations = await agent.analyze(
    video_id="vid-1",
    frames=frames,
    video_metadata=metadata,
)
```

#### SpeechAnalysisAgent
- **Consumes**: ExtractedAudioSegment[] (audio data)
- **Uses**: SpeechProvider (Whisper)
- **Produces**: Observation(SPEECH)
- **Uses Mapper**: SpeechMapper

```python
agent = SpeechAnalysisAgent(speech_provider)
observations = await agent.analyze(
    video_id="vid-1",
    audio_segments=audio_segments,
    language="en",
)
```

#### OCRAnalysisAgent
- **Consumes**: ExtractedFrame[] (with image data)
- **Uses**: OCRProvider (Tesseract)
- **Produces**: Observation(OCR)
- **Uses Mapper**: OCRMapper

```python
agent = OCRAnalysisAgent(ocr_provider)
observations = await agent.analyze(
    video_id="vid-1",
    frames=frames,
    language="en",
)
```

#### VisionAnalysisAgent
- **Consumes**: ExtractedFrame[] (with image data)
- **Uses**: VisionProvider (OpenCV/YOLO)
- **Produces**: Observation(OBJECT), Observation(FACE)
- **Uses Mapper**: VisionMapper

```python
agent = VisionAnalysisAgent(vision_provider)
observations = await agent.analyze(
    video_id="vid-1",
    frames=frames,
)
```

### 3. Knowledge Builder

**Critical**: KnowledgeBuilder consumes **ONLY** Observation objects. It has NO access to:
- Providers
- Memory Runtime
- AnalysisSession
- Any raw data

```python
builder = KnowledgeBuilder()
knowledge_nodes = await builder.build_knowledge_graph(
    video_id="vid-1",
    observations=observation_list,
)
```

**Process**:
1. Extract entities from observations
   - Speakers from SPEECH observations
   - Objects from OBJECT observations
   - Faces from FACE observations
   - Locations/scenes from SCENE observations
2. Group related observations by entity
3. Create KnowledgeNode for each entity
4. Build relationships between observations

**Entities Extracted**:
- `person`: From speaker names in speech
- `object`: From detected object classes
- `face`: From face detections
- `brand`: From logo detections
- `scene`: From scene content
- `activity`: From activity observations
- `language`: From speech language

### 4. Enhanced VideoIngestionPipeline

Pipeline is the **sole orchestrator** and **sole access point** to Memory Runtime.

#### Key Methods

```python
# Session management
session = await pipeline.create_analysis_session(video_id, session_type)

# Video import
video, timeline, session = await pipeline.ingest_video(
    file_path,
    session=session,
)

# Analysis (Phase 2)
timeline, session = await pipeline.extract_and_analyze(
    video, timeline, session
)

# Knowledge graph (Phase 2)
knowledge_nodes, session = await pipeline.build_knowledge_graph(
    video_id, observations, session
)

# Finalization
session = await pipeline.complete_session(session, timeline)

# Persistence (ONLY entry point)
await pipeline.persist_session_to_memory(session, video, timeline, knowledge_nodes)
```

#### extract_and_analyze Method

Orchestrates complete analysis:
1. Extract frames (via FrameExtractionService)
2. Extract audio (via AudioExtractionService)
3. Run scene analysis agent (if available)
4. Run speech analysis agent (if available)
5. Run OCR analysis agent (if available)
6. Run vision analysis agent (if available)
7. Accumulate all observations
8. Create timeline events for each stage
9. Update timeline and session

#### build_knowledge_graph Method

1. Create KnowledgeBuilder
2. Build knowledge graph from observations
3. Extract entities and relationships
4. Create KnowledgeNode objects
5. Update session with knowledge node IDs

#### persist_session_to_memory Method

**CRITICAL**: This is the ONLY place where data is written to Memory Runtime.

Persists in order:
1. Video object
2. AnalysisSession object
3. Timeline object
4. Each Observation
5. Each TimelineEvent
6. Each KnowledgeNode (semantic memory)

---

## Architectural Principles Maintained

### 1. Provider Statelesness
```python
# ✅ CORRECT: Provider is pure function
provider = WhisperSpeechProvider()
results = await provider.transcribe(audio_bytes)
# Provider has no session, timeline, or persistence knowledge

# ❌ WRONG: Provider with state
provider.session = session
provider.memory = memory
```

### 2. Observation Universality
Every discovery, regardless of source, becomes an Observation:
```python
# Speech
Observation(observation_type=SPEECH, source_agent="SpeechAgent", ...)

# OCR
Observation(observation_type=OCR, source_agent="OCRAgent", ...)

# Objects
Observation(observation_type=OBJECT, source_agent="VisionAgent", ...)

# Scenes
Observation(observation_type=SCENE_CONTENT, source_agent="SceneAnalysisAgent", ...)
```

### 3. Single Persistence Entry Point
```python
# ✅ CORRECT
await pipeline.persist_session_to_memory(session, video, timeline, nodes)

# ❌ WRONG
await memory.store(observation)  # Direct access bypassed
await agent.persist()  # Agent has no persistence
```

### 4. AnalysisSession as Root Aggregate
Every result is associated with exactly one AnalysisSession:
```
AnalysisSession
├─ video_id
├─ timeline_id → Timeline
│  ├─ events → TimelineEvent[]
│  └─ observations → Observation[]
├─ observation_ids
├─ knowledge_node_ids → KnowledgeNode[]
└─ metrics
```

### 5. KnowledgeBuilder Observation Isolation
```python
# ✅ KnowledgeBuilder consumes ONLY observations
builder = KnowledgeBuilder()
nodes = await builder.build_knowledge_graph(video_id, observations)

# ❌ KnowledgeBuilder cannot access
# - Providers
# - Memory Runtime
# - Video metadata
# - Raw frames or audio
```

---

## Integration Points

### With M6 Agent Orchestration
Agents can be integrated with ExecutableAgent registry:
```python
# Phase 3: Register with M6 agent registry
agent_registry.register("scene_analysis", scene_agent)
agent_registry.register("speech_analysis", speech_agent)
agent_registry.register("ocr_analysis", ocr_agent)
agent_registry.register("vision_analysis", vision_agent)
```

### With M8 Task Orchestration
Analysis can be parallelized via Task Orchestration:
```python
# Phase 3: Build DAG for concurrent execution
dag = {
    "frames": extract_frames(video),
    "audio": extract_audio(video),
    "scene": {"depends_on": ["frames"]},
    "speech": {"depends_on": ["audio"]},
    "ocr": {"depends_on": ["frames"]},
    "vision": {"depends_on": ["frames"]},
}
results = await orchestration_engine.execute_graph(dag)
```

### With M7 Memory Runtime
AnalysisSession enables session-scoped queries:
```python
# Phase 4: Query by session
observations = await memory.query(
    object_type="Observation",
    session_id="session-xyz",
)

knowledge_nodes = await memory.query(
    object_type="KnowledgeNode",
    session_id="session-xyz",
)
```

---

## Complete Analysis Flow Example

```python
from aura_backend.video import (
    VideoIngestionPipeline,
    ProviderRegistry,
    FFmpegVideoProvider,
    WhisperSpeechProvider,
    TesseractOCRProvider,
    OpenCVVisionProvider,
    OpenCVSceneProvider,
    SceneAnalysisAgent,
    SpeechAnalysisAgent,
    OCRAnalysisAgent,
    VisionAnalysisAgent,
)

# Setup
registry = ProviderRegistry()
registry.register_video_provider("ffmpeg", FFmpegVideoProvider())
registry.register_speech_provider("whisper", WhisperSpeechProvider())
registry.register_ocr_provider("tesseract", TesseractOCRProvider())
registry.register_vision_provider("opencv", OpenCVVisionProvider())

scene_agent = SceneAnalysisAgent(OpenCVSceneProvider())
speech_agent = SpeechAnalysisAgent(WhisperSpeechProvider())
ocr_agent = OCRAnalysisAgent(TesseractOCRProvider())
vision_agent = VisionAnalysisAgent(OpenCVVisionProvider())

pipeline = VideoIngestionPipeline(
    provider_registry=registry,
    scene_agent=scene_agent,
    speech_agent=speech_agent,
    ocr_agent=ocr_agent,
    vision_agent=vision_agent,
    memory_manager=m7_memory,
)

# Execution
# 1. Create session
session = await pipeline.create_analysis_session(
    video_id="vid-1",
    session_type="initial",
)

# 2. Import video
video, timeline, session = await pipeline.ingest_video(
    "path/to/video.mp4",
    session=session,
)

# 3. Extract and analyze
timeline, session = await pipeline.extract_and_analyze(video, timeline, session)

# 4. Build knowledge graph
knowledge_nodes, session = await pipeline.build_knowledge_graph(
    video_id=video.id,
    observations=timeline.observations,
    session=session,
)

# 5. Complete session
session = await pipeline.complete_session(session, timeline)

# 6. Persist (ONLY entry point)
await pipeline.persist_session_to_memory(
    session, video, timeline, knowledge_nodes
)
```

---

## Files

### New Files (Phase 2)
- `extraction.py` — Frame and audio extraction services
- `scene_analysis.py` — Scene detection provider and mapper
- `analysis_agents.py` — Scene, speech, OCR, vision agents
- `knowledge_builder.py` — Knowledge graph construction
- `PHASE2_IMPLEMENTATION.md` — This file

### Modified Files (Phase 2)
- `ingestion.py` — Complete refactor for Phase 2
- `__init__.py` — Exports for new components
- `models.py` — No changes (fully backward compatible)
- `providers.py` — No changes (Phase 1 implementations sufficient)
- `mappers.py` — No changes (Phase 1 implementations sufficient)

---

## Testing

Phase 2 test file: `tests/video/test_phase2_analysis.py`

Tests cover:
- Frame extraction
- Audio extraction
- Scene analysis agent
- Speech analysis agent
- OCR analysis agent
- Vision analysis agent
- Knowledge builder
- Pipeline with agents
- AnalysisSession integration
- End-to-end flow
- Provider statelesness verification
- Observation immutability
- Single persistence entry point

---

## Performance Considerations

### Parallel Analysis
With M8 orchestration, these can run in parallel:
- Scene detection on frames
- OCR on frames
- Vision detection on frames
- Speech transcription on audio

Sequential:
- Frame extraction (must happen first)
- Audio extraction (must happen first)
- Knowledge graph building (needs all observations)

### Memory Usage
- Extracted frames stored in memory (image data)
- Extracted audio stored in memory
- All observations kept in timeline
- Knowledge nodes created after analysis

---

## Next: Phase 3

Phase 3 will implement:
1. **M6 Integration** — Register agents with ExecutableAgent
2. **M8 Integration** — Concurrent execution via DAG orchestration
3. **Production Provider Implementations** — Real FFmpeg, Whisper, Tesseract, OpenCV
4. **Streaming Architecture** — Process frames/audio as they arrive
5. **Error Handling** — Retry logic, failure modes, recovery

---

## Summary

**Phase 2 Complete** ✅

The complete analysis pipeline is implemented:
- ✅ Frame extraction
- ✅ Audio extraction
- ✅ Scene analysis (boundaries and content)
- ✅ Speech transcription
- ✅ Text detection (OCR)
- ✅ Object and face detection (Vision)
- ✅ Knowledge graph building from observations
- ✅ Complete orchestration via VideoIngestionPipeline
- ✅ Single persistence entry point to Memory Runtime
- ✅ AnalysisSession as root aggregate

All architectural principles maintained:
- ✅ Providers remain stateless
- ✅ Every result becomes an Observation
- ✅ KnowledgeBuilder consumes only observations
- ✅ Only pipeline accesses Memory Runtime
- ✅ AnalysisSession groups complete analysis run

Ready for Phase 3: Agent and Orchestration Integration
