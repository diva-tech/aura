# Milestone 9: Video Intelligence Runtime
## Phase 1 Architecture & Implementation

**Status: COMPLETE** ✅

Phase 1 establishes the foundation for video analysis: immutable domain models, provider-agnostic architecture, and mappers that convert third-party results to a unified observation model.

---

## Architecture Overview

The video intelligence runtime is structured around an **end-to-end ingestion pipeline**:

```
VideoFile
    ↓
[VideoProvider] (extracts metadata via FFmpeg)
    ↓
[Video + Timeline] (immutable objects created)
    ↓
[Analysis Agents] (via M8 Task Orchestration)
    ├─ Speech Analysis (Whisper)
    ├─ OCR Analysis (Tesseract)
    └─ Vision Analysis (OpenCV)
    ↓
[Mappers] (convert results to Observations)
    ├─ SpeechMapper
    ├─ OCRMapper
    └─ VisionMapper
    ↓
[Observation] (universal model - single format for all discoveries)
    ↓
[Timeline + Memory Runtime] (storage via M7)
```

### Core Design Principles

1. **Provider Abstraction**: All external libraries (FFmpeg, Whisper, Tesseract, OpenCV) are isolated behind provider interfaces. No third-party objects leak into the domain layer.

2. **Observation Universality**: Every discovery—whether from speech, OCR, vision, or other sources—becomes a single immutable `Observation` object. This is the universal language of the runtime.

3. **Timeline-First Execution**: Everything discovered becomes a timeline event. The Timeline is the canonical source of truth for video analysis state.

4. **Immutability**: All domain objects are frozen dataclasses with complete type hints. Immutability ensures thread safety and prevents accidental mutations.

5. **Separation of Concerns**: 
   - Models → Domain structure
   - Providers → External library isolation
   - Mappers → Results to domain conversion
   - Pipeline → Orchestration

---

## Component Breakdown

### 1. Domain Models (`models.py`)

#### Enums
- **VideoCodec**: H264, H265, VP9, AV1, UNKNOWN
- **AudioCodec**: AAC, MP3, OPUS, VORBIS, UNKNOWN
- **ObservationType**: 14 types covering all discoveries
  - SCENE_BOUNDARY, SCENE_CONTENT
  - SPEECH, SILENCE, MUSIC, SOUND_EFFECT
  - OCR, FACE, OBJECT, LOGO, TEXT, ACTIVITY
- **TimelineEventType**: 9 types for pipeline stages
  - VIDEO_IMPORTED, FRAMES_EXTRACTED, SCENE_DETECTED
  - AUDIO_EXTRACTED, TRANSCRIPT_GENERATED, OCR_COMPLETED
  - FACE_DETECTED, OBJECT_DETECTED, OBSERVATION_CREATED

#### Core Objects (all frozen dataclasses)

**VideoMetadata** (immutable)
- Duration, FPS, resolution, codecs, bitrate, frame count
- Audio/subtitle streams, file format, size
- Fully serializable via `to_dict()`

**Video** (immutable)
- Unique ID (UUID4), file path, metadata reference, import timestamp
- No modification after creation

**Frame** (immutable)
- Reference to video, frame number, timestamp
- Keyframe flag for extraction hints

**Observation** (THE UNIVERSAL MODEL)
- Single structure for all discoveries
- Fields:
  - `id`: Unique observation ID
  - `video_id`: Reference to source video
  - `observation_type`: What was discovered (enum)
  - `source_agent`: Which agent made the discovery
  - `start_timestamp`, `end_timestamp`: When in video
  - `confidence`: Quality metric (0.0-1.0)
  - `payload`: Discovery-specific data (text, bbox, class, etc.)
  - `metadata`: Source provider, segment ID, etc.
  - `created_at`: Creation timestamp

**Timeline** (immutable, query-capable)
- Canonical execution model for video analysis
- Fields:
  - `id`: Timeline ID
  - `video_id`: Reference to video
  - `events`: List of TimelineEvent
  - `observations`: List of Observation
  - `created_at`, `updated_at`: Timestamps
- Query methods:
  - `get_events_by_type(TimelineEventType)`: Filter events
  - `get_observations_by_type(ObservationType)`: Filter observations
  - `get_observations_in_range(start, end)`: Time-based queries

**Other Models**
- Scene, AudioSegment, TranscriptSegment, KnowledgeNode
- All immutable, all have `to_dict()` for serialization

---

### 2. Provider Interfaces & Reference Implementations (`providers.py`)

#### Abstract Interfaces (contracts)

**VideoProvider**
```python
async def extract_metadata(file_path: str) -> VideoMetadata
async def is_supported(file_path: str) -> bool
```

**SpeechProvider**
```python
async def transcribe(audio_data: bytes, language: str) -> List[TranscriptSegment]
async def supports_language(language: str) -> bool
```

**OCRProvider**
```python
async def detect_text(image_data: bytes) -> List[Dict[str, Any]]
async def supports_language(language: str) -> bool
```

**VisionProvider**
```python
async def detect_objects(image_data: bytes) -> List[Dict[str, Any]]
async def detect_faces(image_data: bytes) -> List[Dict[str, Any]]
```

#### Reference Implementations

**FFmpegVideoProvider**
- Supports: .mp4, .mov, .mkv, .avi, .webm
- Returns: VideoMetadata with realistic stub values
- Production note: Would call ffprobe subprocess and parse JSON

**WhisperSpeechProvider**
- Supports: 99+ languages
- Returns: List[TranscriptSegment] with timestamps and confidence
- Production note: Would load Whisper model and process audio bytes

**TesseractOCRProvider**
- Supports: 100+ languages
- Returns: List of dicts with text, confidence, bbox
- Production note: Would call Tesseract OCR engine

**OpenCVVisionProvider**
- Supports: Object detection (YOLO) and face detection (cascade/DNN)
- Returns: Lists of dicts with class/confidence and bounding boxes
- Production note: Would run inference on image bytes

#### ProviderRegistry
```python
class ProviderRegistry:
    def register_video_provider(name: str, provider: VideoProvider)
    def get_video_provider(name: str) -> Optional[VideoProvider]
    # Similar for speech, ocr, vision providers
```

Purpose: Centralized provider management and lookup

---

### 3. Mappers: Provider Results → Observations (`mappers.py`)

Mappers are the **critical boundary** where third-party library results are converted to immutable domain objects. No provider objects leak outside.

**SpeechMapper**
```python
@staticmethod
def from_transcript_segments(
    video_id: str,
    segments: List[TranscriptSegment],
) -> List[Observation]:
```
- Converts each TranscriptSegment → Observation
- observation_type = SPEECH
- source_agent = "SpeechAgent"
- payload = {text, speaker, language}
- metadata = {source_provider: "whisper", segment_id}

**OCRMapper**
```python
@staticmethod
def from_detections(
    video_id: str,
    start_timestamp: float,
    end_timestamp: float,
    detections: List[Dict],
) -> List[Observation]:
```
- Converts detection dicts → Observation list
- observation_type = OCR
- source_agent = "OCRAgent"
- payload = {text, bbox}
- metadata = {source_provider: "tesseract"}

**VisionMapper**
```python
@staticmethod
def from_object_detections(...) -> List[Observation]
@staticmethod
def from_face_detections(...) -> List[Observation]
```
- Object: observation_type = OBJECT, source_agent = "ObjectAnalysisAgent"
- Face: observation_type = FACE, source_agent = "FaceAnalysisAgent"
- Payloads include bbox and classification confidence

---

### 4. Ingestion Pipeline (`ingestion.py`)

**VideoIngestionPipeline**

Orchestrates the complete ingestion flow:

```python
class VideoIngestionPipeline:
    def __init__(
        self,
        provider_registry: ProviderRegistry,
        memory_manager=None,  # M7 integration point
    )
    
    async def ingest_video(
        self,
        file_path: str,
        video_provider_name: str = "ffmpeg",
    ) -> tuple[Video, Timeline]:
```

**Flow:**
1. Get VideoProvider from registry
2. Validate file support (is_supported)
3. Extract metadata (extract_metadata)
4. Create immutable Video object
5. Create Timeline with VIDEO_IMPORTED event
6. Store in Memory Runtime (if available)
7. Return (Video, Timeline) tuple

**State captured:**
- Resolution, duration, codec, bitrate, file size
- All facts about the video immediately available
- Timeline event records the import with full metadata

---

## Integration with Other Milestones

### M1-M5: Event Bus, Plugins, LLM Runtime
- **No changes required**
- M9 is independent and builds on top

### M6: Agent Orchestration
- **Phase 2 will implement analysis agents as ExecutableAgent subclasses**
- Agents registered in ExecutableAgent registry
- Each agent: takes observations/frames as input, produces observations as output

### M7: Memory Runtime
- **Phase 4 will integrate knowledge storage**
- Observations stored in episodic memory
- KnowledgeNode objects bridge observations to semantic graph

### M8: Task Orchestration
- **Phase 2 will use ExecutionEngine for parallel analysis**
- DAG: [frames] → [Speech/OCR/Vision agents] → [Observations]
- Concurrent execution of independent analysis tasks

---

## Extensibility Points

### Adding a New Analysis Provider

1. **Create provider interface** (already exists for Video/Speech/OCR/Vision)
2. **Implement reference provider**:
   ```python
   class MyCustomProvider(VideoProvider):
       async def extract_metadata(self, file_path: str) -> VideoMetadata:
           # Implementation
       
       async def is_supported(self, file_path: str) -> bool:
           # Check format
   ```
3. **Register with ProviderRegistry**:
   ```python
   registry.register_video_provider("my_custom", MyCustomProvider())
   ```
4. **Use in ingestion pipeline**:
   ```python
   video, timeline = pipeline.ingest_video("file.mp4", "my_custom")
   ```

### Adding a New Observation Type

1. **Add to ObservationType enum**:
   ```python
   class ObservationType(str, Enum):
       NEW_TYPE = "new_type"
   ```
2. **Create mapper method** (if provider-based):
   ```python
   class MyMapper:
       @staticmethod
       def from_raw_data(video_id, data) -> List[Observation]:
           # Convert to observations
   ```
3. **Use in agents** to produce observations
4. **Query in Timeline**:
   ```python
   timeline.get_observations_by_type(ObservationType.NEW_TYPE)
   ```

---

## Testing Strategy

**test_phase1_integration.py** covers:

1. **Model Immutability**: Verify frozen dataclasses
2. **Provider Interfaces**: Verify abstract methods exist
3. **Provider Registry**: Register and retrieve providers
4. **Mappers**: Convert provider outputs to Observations
5. **Ingestion Pipeline**: End-to-end flow
6. **Timeline Queries**: get_observations_by_type, get_observations_in_range
7. **Serialization**: All objects to_dict() for storage/API

---

## File Structure

```
aura_backend/video/
├── __init__.py                    # Package exports
├── models.py                      # Domain models (frozen dataclasses)
├── providers.py                   # Provider interfaces + reference implementations
├── mappers.py                     # Provider results → Observations
├── ingestion.py                   # End-to-end ingestion orchestrator
└── PHASE1_ARCHITECTURE.md         # This file

tests/video/
├── __init__.py
└── test_phase1_integration.py     # Comprehensive tests
```

---

## Phase 2: Core Infrastructure

What Phase 2 will implement:

1. **Frame Extraction**
   - Extract keyframes/interval frames from video
   - Store Frame objects in Timeline
   - Emit FRAMES_EXTRACTED event

2. **Analysis Agent Implementation**
   - SpeechAnalysisAgent (ExecutableAgent)
   - OCRAnalysisAgent (ExecutableAgent)
   - VisionAnalysisAgent (ExecutableAgent)
   - Each produces Observations via mappers

3. **Task Orchestration**
   - Build DAG: [frames] → [agents] → [observations]
   - Use M8 ExecutionEngine for concurrent execution
   - Orchestrate speech, OCR, vision in parallel

4. **Timeline Enrichment**
   - Add frame extraction events
   - Add agent execution events
   - Add observation creation events

5. **Memory Integration**
   - Store Video in M7 episodic memory
   - Store Observations in M7 episodic memory
   - Build KnowledgeNodes from observations

---

## Key Architectural Decisions

1. **Single Observation Model**
   - Rather than separate SpeechResult, OCRResult, VisionResult classes
   - All discoveries use Observation with different observation_type values
   - Simplifies storage, querying, and analysis agent input/output contracts

2. **Timeline as Execution Model**
   - Rather than separate processing queues or state machines
   - Everything becomes a timeline event
   - Single canonical source of truth for analysis state

3. **Frozen Dataclasses for All Domain Objects**
   - Rather than mutable classes with validators
   - Immutability provides thread safety and prevents bugs
   - Full type hints enable IDE support and static analysis

4. **Provider Registry for Dynamic Composition**
   - Rather than hardcoding provider implementations
   - Registry allows runtime selection of providers
   - Enables testing with mock providers and production provider swaps

5. **Mapper Boundary at Third-Party Library Transition**
   - Rather than exposing FFmpeg/Whisper/Tesseract objects directly
   - Mappers convert to domain objects
   - Prevents library-specific code from spreading throughout domain layer

---

## References

- [M6 Agent Orchestration](../agents/ARCHITECTURE.md)
- [M7 Memory Runtime](../memory/ARCHITECTURE.md)
- [M8 Task Orchestration](../orchestration/ARCHITECTURE.md)
