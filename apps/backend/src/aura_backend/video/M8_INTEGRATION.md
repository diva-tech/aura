# Milestone 9: M8 Task Orchestration Integration

**Status: COMPLETE** ✅

This document describes the integration of Video Intelligence Runtime with M8 Task Orchestration Runtime, enabling scalable distributed video analysis.

---

## Architecture: From Direct Invocation to Task Graph Orchestration

### Before Refactoring (Phase 2)
```
VideoIngestionPipeline
  ├─ Directly invokes scene_agent.analyze()
  ├─ Directly invokes speech_agent.analyze()
  ├─ Directly invokes ocr_agent.analyze()
  ├─ Directly invokes vision_agent.analyze()
  └─ Directly invokes knowledge_builder.build_knowledge_graph()
  
(Sequential execution, single-process, tight coupling)
```

### After Refactoring (M8 Integration)
```
VideoIngestionPipeline
  │
  ├─→ AnalysisPlanner.plan_analysis()
  │   ↓
  │   Creates TaskGraph (DAG)
  │   ├─ Frame extraction task
  │   ├─ Audio extraction task
  │   ├─ Scene analysis task (depends on frames)
  │   ├─ Speech analysis task (depends on audio)
  │   ├─ OCR analysis task (depends on frames)
  │   ├─ Vision analysis task (depends on frames)
  │   └─ Knowledge building task (depends on all analysis)
  │
  ├─→ M8.ExecutionEngine.execute_graph(task_graph)
  │   │
  │   ├─→ M8.Scheduler (determines execution order)
  │   ├─→ M8.Dispatcher (routes tasks to agents)
  │   ├─→ M8.CapabilityResolver (matches tasks to ExecutableAgent implementations)
  │   │
  │   └─→ ExecutableAgent implementations execute tasks
  │       ├─ scene_analysis_agent
  │       ├─ speech_analysis_agent
  │       ├─ ocr_analysis_agent
  │       ├─ vision_analysis_agent
  │       └─ knowledge_building_agent
  │
  ├─→ Pipeline collects task outputs
  │   ↓
  │   _collect_observations_from_graph()
  │   ↓
  │   All outputs → immutable Observation objects
  │   (Append-only collection)
  │
  └─→ persist_session_to_memory()
      ↓
      Memory Runtime (M7)
```

---

## Component Breakdown

### 1. AnalysisPlanner

**File**: `analysis_planner.py`

**Purpose**: Convert AnalysisSession into executable Task Graph

**Key Classes**:

#### TaskType (Enum)
```python
class TaskType(str, Enum):
    SCENE_ANALYSIS = "scene_analysis"
    SPEECH_ANALYSIS = "speech_analysis"
    OCR_ANALYSIS = "ocr_analysis"
    VISION_ANALYSIS = "vision_analysis"
    KNOWLEDGE_BUILDING = "knowledge_building"
```

#### TaskStatus (Enum)
```python
class TaskStatus(str, Enum):
    PENDING = "pending"          # Ready for submission
    SUBMITTED = "submitted"      # Sent to M8
    EXECUTING = "executing"      # Running in executor
    COMPLETED = "completed"      # Finished successfully
    FAILED = "failed"             # Execution failed
```

#### Task (Immutable Frozen Dataclass)
```python
@dataclass(frozen=True)
class Task:
    id: str                          # Unique task ID
    task_type: TaskType              # What kind of analysis
    agent_name: str                  # ExecutableAgent registry name
    session_id: str                  # AnalysisSession reference
    video_id: str                    # Video reference
    
    input_data: Dict[str, Any]       # Task-specific inputs
    depends_on: List[str]            # Task IDs (dependencies)
    status: TaskStatus               # Current state
    output_data: Optional[Dict]      # Results after execution
    error_message: Optional[str]     # Failure reason
```

#### TaskGraph (Immutable Frozen Dataclass)
```python
@dataclass(frozen=True)
class TaskGraph:
    id: str                          # Graph ID
    session_id: str                  # AnalysisSession reference
    video_id: str                    # Video reference
    
    tasks: Dict[str, Task]           # All tasks (task_id → Task)
    task_order: List[str]            # Topologically sorted task IDs
    
    # Stages
    extraction_tasks: List[str]      # Frame/audio extraction
    analysis_tasks: List[str]        # Scene/speech/OCR/vision
    aggregation_tasks: List[str]     # Knowledge building
```

#### AnalysisPlanner
```python
class AnalysisPlanner:
    async def plan_analysis(
        session_id: str,
        video_id: str,
        video_metadata: Dict,
        has_frames: bool = True,
        has_audio: bool = True,
        enabled_agents: Optional[List[str]] = None,
    ) -> TaskGraph:
        """Create executable task graph for video analysis."""
```

**Task Graph Structure** (with dependencies):
```
frame_extract → scene_analysis ─┐
                ocr_analysis ────┤→ knowledge_building
                vision_analysis ─┘

audio_extract → speech_analysis ─┘
```

**Validation Features**:
- Cycle detection (prevents infinite loops)
- Dependency validation (all dependencies must exist)
- Topological sorting (execution order hints)

### 2. Refactored VideoIngestionPipeline

**Changes**:
1. Removed direct agent references (`scene_agent`, `speech_agent`, etc.)
2. Added `AnalysisPlanner` for task graph creation
3. Added reference to M8 `ExecutionEngine`
4. Refactored `extract_and_analyze()` to create TaskGraph and submit to M8

**Public API Signature Changes**:
```python
# Before
def __init__(
    self,
    provider_registry: ProviderRegistry,
    scene_agent: Optional[SceneAnalysisAgent] = None,
    speech_agent: Optional[SpeechAnalysisAgent] = None,
    # ... other agents
    memory_manager=None,
)

# After
def __init__(
    self,
    provider_registry: ProviderRegistry,
    execution_engine=None,  # M8 ExecutionEngine
    analysis_planner: Optional[AnalysisPlanner] = None,
    memory_manager=None,  # M7 MemoryManager
)
```

**Method Behavior**:
```python
# Same public API, different implementation
async def extract_and_analyze(
    self,
    video: Video,
    timeline: Timeline,
    session: AnalysisSession,
) -> Tuple[Timeline, AnalysisSession]:
    """
    NEW: Creates TaskGraph via AnalysisPlanner
    NEW: Submits to M8.ExecutionEngine for distributed execution
    NEW: Collects results and converts to Observations
    SAME: Returns (updated_timeline, updated_session)
    """
```

### 3. Task Collection and Conversion

**Method**: `_collect_observations_from_graph()`

**Process**:
1. Iterate over completed tasks in task graph
2. Extract output_data from each task
3. Extract observation list from output_data
4. Reconstruct immutable Observation objects
5. Return append-only observation list

**Key Feature**: All observations are created fresh from task outputs (append-only pattern).

---

## Execution Flow

### 1. Analysis Planning
```python
planner = AnalysisPlanner()
task_graph = await planner.plan_analysis(
    session_id="session-1",
    video_id="vid-1",
    video_metadata=video.metadata.to_dict(),
)
```

**Output**: TaskGraph with 7 tasks
- 2 extraction tasks (frames, audio)
- 4 analysis tasks (scene, speech, OCR, vision)
- 1 aggregation task (knowledge building)

### 2. Graph Validation
```python
errors = planner.validate_graph(task_graph)
# Returns: [] (empty list means valid)
```

**Checks**:
- No cycles in task dependencies
- All dependencies refer to existing tasks
- All tasks have unique IDs

### 3. M8 Submission
```python
completed_graph = await execution_engine.execute_graph(
    task_graph.to_dict(),
    context={"session_id": session.id, "video_id": video.id},
)
```

**M8 Responsibilities**:
1. **Scheduler**: Determines execution order based on dependencies
2. **Dispatcher**: Routes tasks to appropriate workers/processes
3. **CapabilityResolver**: Matches task requirements to ExecutableAgent implementations

### 4. Result Collection
```python
observations = await pipeline._collect_observations_from_graph(
    completed_graph, video.id
)
```

**Process**:
1. Iterate task outputs
2. Extract observation lists
3. Reconstruct Observation objects
4. Return append-only collection

### 5. Knowledge Building (As Agent)
```python
knowledge_nodes, session = await pipeline.build_knowledge_graph(
    video.id, observations, session
)
```

**Implementation**:
- If M8 available: Submits KnowledgeBuilder as registered agent task
- Otherwise: Executes locally (backward compatibility)

### 6. Persistence
```python
await pipeline.persist_session_to_memory(
    session, video, timeline, knowledge_nodes
)
```

**CRITICAL**: Only entry point to Memory Runtime

---

## Agent Registration (Prerequisite)

For M8 to execute tasks, all analysis agents must be registered with the ExecutableAgent registry:

```python
# Pseudocode - agents must be registered with M6/M8
agent_registry = ExecutableAgentRegistry()

agent_registry.register(
    "scene_analysis_agent",
    SceneAnalysisAgent(OpenCVSceneProvider())
)

agent_registry.register(
    "speech_analysis_agent",
    SpeechAnalysisAgent(WhisperSpeechProvider())
)

agent_registry.register(
    "ocr_analysis_agent",
    OCRAnalysisAgent(TesseractOCRProvider())
)

agent_registry.register(
    "vision_analysis_agent",
    VisionAnalysisAgent(OpenCVVisionProvider())
)

agent_registry.register(
    "knowledge_building_agent",
    KnowledgeBuilderAgent()  # Wrapper around KnowledgeBuilder
)

# Pass registry to M8 Dispatcher for CapabilityResolver
```

**Agent Contract**:
```python
class ExecutableAgent:
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input: task dict with input_data
        Output: dict with observations list
        """
        observations = [...]  # Generate observations
        return {
            "observations": [obs.to_dict() for obs in observations],
            "status": "completed",
        }
```

---

## Append-Only Observation Semantics

**Principle**: Observations are immutable and collected in order without modification.

**Implementation**:
```python
# Start with existing observations
existing = list(timeline.observations)  # e.g., []

# Collect from M8 execution
new_obs = await _collect_observations_from_graph(graph, video.id)  # e.g., [obs1, obs2, obs3]

# Append (never modify existing)
all_obs = existing + new_obs  # [obs1, obs2, obs3]

# Create new timeline with appended observations
timeline = Timeline(
    id=timeline.id,
    observations=all_obs,  # Appended, not modified
    # ...
)
```

**Benefits**:
- Immutability preserves correctness
- Append-only enables audit trail
- No risk of overwriting discoveries
- Supports multiple analysis runs on same video

---

## Backward Compatibility

### Without M8 (Local Fallback)
If ExecutionEngine is not configured:
```python
pipeline = VideoIngestionPipeline(
    provider_registry=registry,
    execution_engine=None,  # M8 not available
)

# extract_and_analyze() raises error
# build_knowledge_graph() falls back to local execution
```

### With M8
```python
pipeline = VideoIngestionPipeline(
    provider_registry=registry,
    execution_engine=m8_engine,  # M8 available
)

# extract_and_analyze() submits TaskGraph to M8
# build_knowledge_graph() submits agent task to M8
```

---

## Architectural Principles Maintained

✅ **Provider Statelesness**
- Providers still have no session/persistence knowledge
- Agents wrap providers, execute via M8

✅ **Observation Universality**
- All results still become Observation objects
- Collected append-only from M8 output

✅ **Single Persistence Entry Point**
- Only `persist_session_to_memory()` writes to M7
- M8 results never touch Memory Runtime directly

✅ **AnalysisSession as Root Aggregate**
- TaskGraph references session_id
- All results associated with session
- Session finalized before persistence

✅ **No M1-M8 Changes**
- Completely separate integration layer
- M8 untouched (uses existing ExecutionEngine)
- M6 agent registry used (no changes)
- M7 persistence unchanged

---

## Task Graph Example

For a video analysis with all agents enabled:

```python
TaskGraph(
    id="graph_vid-1_1722192000.123",
    session_id="session-1",
    video_id="vid-1",
    tasks={
        # Extraction (stage 1)
        "frame_extract_vid-1": Task(
            id="frame_extract_vid-1",
            task_type=TaskType.SCENE_ANALYSIS,  # Marker
            agent_name="frame_extraction_service",
            input_data={"fps": 30.0, "duration_seconds": 60.0},
            depends_on=[],
        ),
        "audio_extract_vid-1": Task(
            id="audio_extract_vid-1",
            task_type=TaskType.SPEECH_ANALYSIS,  # Marker
            agent_name="audio_extraction_service",
            input_data={"duration_seconds": 60.0},
            depends_on=[],
        ),
        
        # Analysis (stage 2)
        "scene_analysis_vid-1": Task(
            id="scene_analysis_vid-1",
            task_type=TaskType.SCENE_ANALYSIS,
            agent_name="scene_analysis_agent",
            input_data={"frames_task_id": "frame_extract_vid-1"},
            depends_on=["frame_extract_vid-1"],
        ),
        "speech_analysis_vid-1": Task(
            id="speech_analysis_vid-1",
            task_type=TaskType.SPEECH_ANALYSIS,
            agent_name="speech_analysis_agent",
            input_data={"audio_task_id": "audio_extract_vid-1"},
            depends_on=["audio_extract_vid-1"],
        ),
        # ... OCR and Vision tasks similarly
        
        # Aggregation (stage 3)
        "knowledge_build_vid-1_1722192000.123": Task(
            id="knowledge_build_vid-1_1722192000.123",
            task_type=TaskType.KNOWLEDGE_BUILDING,
            agent_name="knowledge_building_agent",
            input_data={
                "analysis_task_ids": [
                    "scene_analysis_vid-1",
                    "speech_analysis_vid-1",
                    # ... OCR, Vision
                ]
            },
            depends_on=[
                "scene_analysis_vid-1",
                "speech_analysis_vid-1",
                # ... OCR, Vision
            ],
        ),
    },
    task_order=[
        # Extraction stage
        "frame_extract_vid-1",
        "audio_extract_vid-1",
        # Analysis stage
        "scene_analysis_vid-1",
        "speech_analysis_vid-1",
        # ... OCR, Vision
        # Aggregation stage
        "knowledge_build_vid-1_1722192000.123",
    ],
    extraction_tasks=["frame_extract_vid-1", "audio_extract_vid-1"],
    analysis_tasks=["scene_analysis_vid-1", "speech_analysis_vid-1", ...],
    aggregation_tasks=["knowledge_build_vid-1_1722192000.123"],
)
```

---

## Benefits of M8 Integration

1. **Scalability**: Analysis tasks run on distributed workers
2. **Concurrency**: Independent tasks execute in parallel
3. **Isolation**: Failed tasks don't block others
4. **Monitoring**: M8 provides execution tracking
5. **Routing**: Dispatcher matches tasks to capable agents
6. **Extensibility**: New analysis agents plug into M8 registry
7. **Separation**: Planning (AnalysisPlanner) separate from execution (M8)

---

## Summary

**M8 Integration Complete** ✅

The Video Intelligence Runtime now uses M8 Task Orchestration for all analysis work:
- ✅ AnalysisPlanner creates executable TaskGraph
- ✅ Graph validation prevents cycles
- ✅ M8 ExecutionEngine handles scheduling/dispatching/resolution
- ✅ Results collected and converted to append-only Observations
- ✅ Single persistence entry point maintained
- ✅ AnalysisSession as root aggregate preserved
- ✅ M1-M8 untouched
- ✅ Public APIs maintained
- ✅ Backward compatibility (local fallback)

Ready for distributed, scalable video analysis.
