"""Analysis Planner: Convert AnalysisSession into executable Task Graph.

Transforms a video analysis session into a directed acyclic graph (DAG) of tasks
that can be submitted to M8 Task Orchestration Runtime for distributed execution.

The planner:
1. Takes AnalysisSession, Video, extracted frames/audio
2. Creates Task objects for each analysis stage
3. Defines dependencies between tasks
4. Returns ready-to-execute TaskGraph

This enables:
- Concurrent execution of independent analysis tasks
- Scalable analysis via M8 dispatcher
- Separation of planning from execution
- Clear task boundaries and dependencies
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set
from enum import Enum
from datetime import datetime


class TaskType(str, Enum):
    """Types of analysis tasks"""
    SCENE_ANALYSIS = "scene_analysis"
    SPEECH_ANALYSIS = "speech_analysis"
    OCR_ANALYSIS = "ocr_analysis"
    VISION_ANALYSIS = "vision_analysis"
    KNOWLEDGE_BUILDING = "knowledge_building"


class TaskStatus(str, Enum):
    """Task lifecycle states"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class Task:
    """Immutable task in analysis workflow.

    Represents a single analysis operation to be executed by M8.
    """
    id: str
    task_type: TaskType
    agent_name: str  # ExecutableAgent registry name
    session_id: str  # Which AnalysisSession this belongs to
    video_id: str

    # Input data
    input_data: Dict[str, Any] = field(default_factory=dict)

    # Dependencies
    depends_on: List[str] = field(default_factory=list)  # Task IDs

    # Execution context
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)

    # Output tracking
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize task for M8 submission"""
        return {
            "id": self.id,
            "task_type": self.task_type.value,
            "agent_name": self.agent_name,
            "session_id": self.session_id,
            "video_id": self.video_id,
            "input_data": self.input_data,
            "depends_on": self.depends_on,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class TaskGraph:
    """Immutable executable task graph (DAG).

    Ready for submission to M8 Task Orchestration Runtime.
    Scheduler/Dispatcher will execute based on dependencies.
    """
    id: str
    session_id: str
    video_id: str

    # All tasks in the graph
    tasks: Dict[str, Task] = field(default_factory=dict)  # task_id → Task

    # Execution order hints
    task_order: List[str] = field(default_factory=list)  # Topologically sorted IDs

    # Stage groupings
    extraction_tasks: List[str] = field(default_factory=list)  # Frame/audio extract
    analysis_tasks: List[str] = field(default_factory=list)  # Scene/speech/OCR/vision
    aggregation_tasks: List[str] = field(default_factory=list)  # Knowledge building

    created_at: datetime = field(default_factory=datetime.utcnow)

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        return self.tasks.get(task_id)

    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get all tasks with given status"""
        return [t for t in self.tasks.values() if t.status == status]

    def get_ready_tasks(self) -> List[Task]:
        """Get tasks ready to execute (all dependencies complete)"""
        completed_ids = set(
            t.id for t in self.get_tasks_by_status(TaskStatus.COMPLETED)
        )

        ready = []
        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING:
                # Check if all dependencies are complete
                if all(dep_id in completed_ids for dep_id in task.depends_on):
                    ready.append(task)

        return ready

    def is_complete(self) -> bool:
        """Whether all tasks are complete or failed"""
        for task in self.tasks.values():
            if task.status not in (TaskStatus.COMPLETED, TaskStatus.FAILED):
                return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Serialize graph for M8 submission"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "video_id": self.video_id,
            "tasks": {tid: t.to_dict() for tid, t in self.tasks.items()},
            "task_order": self.task_order,
            "extraction_tasks": self.extraction_tasks,
            "analysis_tasks": self.analysis_tasks,
            "aggregation_tasks": self.aggregation_tasks,
            "created_at": self.created_at.isoformat(),
        }


class AnalysisPlanner:
    """Convert AnalysisSession into executable Task Graph.

    The planner creates a DAG representing the analysis workflow:
    1. Extract frames (no dependencies)
    2. Extract audio (no dependencies)
    3. Scene analysis (depends on frame extraction)
    4. Speech analysis (depends on audio extraction)
    5. OCR analysis (depends on frame extraction)
    6. Vision analysis (depends on frame extraction)
    7. Knowledge building (depends on all analysis tasks)

    All tasks are independent except for stage dependencies.
    """

    def __init__(self, execution_engine=None):
        """Initialize planner with optional reference to M8 ExecutionEngine"""
        self.execution_engine = execution_engine

    async def plan_analysis(
        self,
        session_id: str,
        video_id: str,
        video_metadata: Dict[str, Any],
        has_frames: bool = True,
        has_audio: bool = True,
        enabled_agents: Optional[List[str]] = None,
    ) -> TaskGraph:
        """Create executable task graph for video analysis.

        Args:
            session_id: AnalysisSession ID
            video_id: Video ID
            video_metadata: Video metadata (fps, duration, etc.)
            has_frames: Whether frames are available
            has_audio: Whether audio is available
            enabled_agents: List of agent names to enable
                          (defaults to all: scene, speech, ocr, vision, knowledge)

        Returns:
            TaskGraph ready for M8 submission
        """
        if enabled_agents is None:
            enabled_agents = [
                "scene_analysis_agent",
                "speech_analysis_agent",
                "ocr_analysis_agent",
                "vision_analysis_agent",
                "knowledge_building_agent",
            ]

        tasks: Dict[str, Task] = {}
        extraction_tasks: List[str] = []
        analysis_tasks: List[str] = []
        aggregation_tasks: List[str] = []

        # Frame extraction task (always created if frames available)
        frame_task_id = None
        if has_frames:
            frame_task_id = f"frame_extract_{video_id}"
            frame_task = Task(
                id=frame_task_id,
                task_type=TaskType.SCENE_ANALYSIS,  # Marker only
                agent_name="frame_extraction_service",
                session_id=session_id,
                video_id=video_id,
                input_data={
                    "file_path": video_metadata.get("file_path", ""),
                    "fps": video_metadata.get("fps", 30.0),
                    "duration_seconds": video_metadata.get("duration_seconds", 60.0),
                },
                depends_on=[],
            )
            tasks[frame_task_id] = frame_task
            extraction_tasks.append(frame_task_id)

        # Audio extraction task
        audio_task_id = None
        if has_audio:
            audio_task_id = f"audio_extract_{video_id}"
            audio_task = Task(
                id=audio_task_id,
                task_type=TaskType.SPEECH_ANALYSIS,  # Marker only
                agent_name="audio_extraction_service",
                session_id=session_id,
                video_id=video_id,
                input_data={
                    "file_path": video_metadata.get("file_path", ""),
                    "duration_seconds": video_metadata.get("duration_seconds", 60.0),
                },
                depends_on=[],
            )
            tasks[audio_task_id] = audio_task
            extraction_tasks.append(audio_task_id)

        # Analysis tasks (depend on extraction tasks)
        if "scene_analysis_agent" in enabled_agents and frame_task_id:
            scene_task_id = f"scene_analysis_{video_id}"
            scene_task = Task(
                id=scene_task_id,
                task_type=TaskType.SCENE_ANALYSIS,
                agent_name="scene_analysis_agent",
                session_id=session_id,
                video_id=video_id,
                input_data={
                    "frames_task_id": frame_task_id,
                    "metadata": video_metadata,
                },
                depends_on=[frame_task_id],
            )
            tasks[scene_task_id] = scene_task
            analysis_tasks.append(scene_task_id)

        if "speech_analysis_agent" in enabled_agents and audio_task_id:
            speech_task_id = f"speech_analysis_{video_id}"
            speech_task = Task(
                id=speech_task_id,
                task_type=TaskType.SPEECH_ANALYSIS,
                agent_name="speech_analysis_agent",
                session_id=session_id,
                video_id=video_id,
                input_data={
                    "audio_task_id": audio_task_id,
                    "language": "en",
                },
                depends_on=[audio_task_id],
            )
            tasks[speech_task_id] = speech_task
            analysis_tasks.append(speech_task_id)

        if "ocr_analysis_agent" in enabled_agents and frame_task_id:
            ocr_task_id = f"ocr_analysis_{video_id}"
            ocr_task = Task(
                id=ocr_task_id,
                task_type=TaskType.OCR_ANALYSIS,
                agent_name="ocr_analysis_agent",
                session_id=session_id,
                video_id=video_id,
                input_data={
                    "frames_task_id": frame_task_id,
                    "language": "en",
                },
                depends_on=[frame_task_id],
            )
            tasks[ocr_task_id] = ocr_task
            analysis_tasks.append(ocr_task_id)

        if "vision_analysis_agent" in enabled_agents and frame_task_id:
            vision_task_id = f"vision_analysis_{video_id}"
            vision_task = Task(
                id=vision_task_id,
                task_type=TaskType.VISION_ANALYSIS,
                agent_name="vision_analysis_agent",
                session_id=session_id,
                video_id=video_id,
                input_data={
                    "frames_task_id": frame_task_id,
                },
                depends_on=[frame_task_id],
            )
            tasks[vision_task_id] = vision_task
            analysis_tasks.append(vision_task_id)

        # Knowledge building task (depends on all analysis tasks)
        if "knowledge_building_agent" in enabled_agents and analysis_tasks:
            knowledge_task_id = f"knowledge_build_{video_id}"
            knowledge_task = Task(
                id=knowledge_task_id,
                task_type=TaskType.KNOWLEDGE_BUILDING,
                agent_name="knowledge_building_agent",
                session_id=session_id,
                video_id=video_id,
                input_data={
                    "analysis_task_ids": analysis_tasks,
                },
                depends_on=analysis_tasks,
            )
            tasks[knowledge_task_id] = knowledge_task
            aggregation_tasks.append(knowledge_task_id)

        # Topological sort (simplified: extraction → analysis → aggregation)
        task_order = extraction_tasks + analysis_tasks + aggregation_tasks

        graph = TaskGraph(
            id=f"graph_{video_id}_{datetime.utcnow().timestamp()}",
            session_id=session_id,
            video_id=video_id,
            tasks=tasks,
            task_order=task_order,
            extraction_tasks=extraction_tasks,
            analysis_tasks=analysis_tasks,
            aggregation_tasks=aggregation_tasks,
            created_at=datetime.utcnow(),
        )

        return graph

    def get_task_dependencies(self, graph: TaskGraph) -> Dict[str, List[str]]:
        """Get dependency map for graph visualization or debugging"""
        return {
            task_id: task.depends_on
            for task_id, task in graph.tasks.items()
        }

    def validate_graph(self, graph: TaskGraph) -> List[str]:
        """Validate graph structure, return list of errors (empty if valid)"""
        errors = []
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        # Check for cycles using DFS
        def has_cycle(task_id: str) -> bool:
            visited.add(task_id)
            rec_stack.add(task_id)

            task = graph.get_task(task_id)
            if not task:
                errors.append(f"Task {task_id} not found in graph")
                return True

            for dep_id in task.depends_on:
                if dep_id not in visited:
                    if has_cycle(dep_id):
                        return True
                elif dep_id in rec_stack:
                    errors.append(f"Cycle detected: {task_id} depends on {dep_id}")
                    return True

            rec_stack.remove(task_id)
            return False

        # Check all tasks for cycles
        for task_id in graph.tasks.keys():
            if task_id not in visited:
                has_cycle(task_id)

        # Check all dependencies exist
        for task_id, task in graph.tasks.items():
            for dep_id in task.depends_on:
                if dep_id not in graph.tasks:
                    errors.append(f"Task {task_id} depends on non-existent task {dep_id}")

        return errors
