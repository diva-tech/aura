"""Core orchestration models.

Immutable data structures for task execution, execution plans, and capability definitions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4


class ExecutionStatus(str, Enum):
    """Task execution status"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class Capability(str, Enum):
    """Agent capabilities - what an agent can fundamentally do"""
    RESEARCH = "research"
    ANALYSIS = "analysis"
    SUMMARIZATION = "summarization"
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    VIDEO_ANALYSIS = "video_analysis"
    SCRIPT_WRITING = "script_writing"
    VOICE_SYNTHESIS = "voice_synthesis"
    THUMBNAIL_GENERATION = "thumbnail_generation"
    SEO_OPTIMIZATION = "seo_optimization"
    CONTENT_PUBLISHING = "content_publishing"
    DATA_PROCESSING = "data_processing"
    PLANNING = "planning"
    REPORTING = "reporting"


class Skill(str, Enum):
    """Agent skills - specific methods or patterns an agent uses"""
    WEB_SEARCH = "web_search"
    DOCUMENT_ANALYSIS = "document_analysis"
    CODE_EXECUTION = "code_execution"
    LLM_SYNTHESIS = "llm_synthesis"
    FACT_EXTRACTION = "fact_extraction"
    COMPARISON = "comparison"
    RANKING = "ranking"
    VIDEO_TRANSCRIPTION = "video_transcription"
    SHOT_DETECTION = "shot_detection"
    SCENE_ANALYSIS = "scene_analysis"
    TEXT_GENERATION = "text_generation"
    MARKDOWN_FORMATTING = "markdown_formatting"
    SEO_ANALYSIS = "seo_analysis"
    METADATA_GENERATION = "metadata_generation"


class ToolRequirement(str, Enum):
    """Tool requirements - what external tools/APIs are needed"""
    GOOGLE_SEARCH = "google_search"
    CLAUDE_API = "claude_api"
    WEB_SCRAPING = "web_scraping"
    DATABASE = "database"
    FILE_STORAGE = "file_storage"
    VIDEO_PROCESSING = "video_processing"
    AUDIO_PROCESSING = "audio_processing"
    IMAGE_PROCESSING = "image_processing"


@dataclass(frozen=True)
class Task:
    """Immutable task definition in an execution plan.

    Represents a unit of work to be executed by an agent.
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    goal: str = ""
    description: str = ""
    priority: int = 0  # Higher = more important
    required_capabilities: Set[Capability] = field(default_factory=set)
    required_skills: Set[Skill] = field(default_factory=set)
    required_tools: Set[ToolRequirement] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "goal": self.goal,
            "description": self.description,
            "priority": self.priority,
            "required_capabilities": [c.value for c in self.required_capabilities],
            "required_skills": [s.value for s in self.required_skills],
            "required_tools": [t.value for t in self.required_tools],
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class TaskAttempt:
    """Immutable record of a single task execution attempt.

    Each retry creates a new attempt record, preserving full history.
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    task_id: str = ""
    attempt_number: int = 1
    status: ExecutionStatus = ExecutionStatus.PENDING
    assigned_agent_id: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration_seconds(self) -> Optional[float]:
        """Duration of execution in seconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "task_id": self.task_id,
            "attempt_number": self.attempt_number,
            "status": self.status.value,
            "assigned_agent_id": self.assigned_agent_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error,
            "duration_seconds": self.duration_seconds,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class ExecutionPlan:
    """Immutable plan for executing a goal.

    Separate from TaskGraph - represents the intended execution strategy.
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    goal_id: str = ""
    goal_description: str = ""
    tasks: List[Task] = field(default_factory=list)
    strategy: str = ""  # e.g., "sequential", "parallel", "dag"
    estimated_duration_seconds: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "goal_id": self.goal_id,
            "goal_description": self.goal_description,
            "task_count": len(self.tasks),
            "strategy": self.strategy,
            "estimated_duration_seconds": self.estimated_duration_seconds,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class TaskGraph:
    """Immutable directed acyclic graph of tasks.

    Represents task dependencies and execution order.
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    plan_id: str = ""
    nodes: Dict[str, Task] = field(default_factory=dict)  # task_id -> Task
    edges: Dict[str, List[str]] = field(default_factory=dict)  # task_id -> [dependent_ids]
    entry_nodes: List[str] = field(default_factory=list)  # tasks with no dependencies
    exit_nodes: List[str] = field(default_factory=list)  # tasks with no dependents
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def get_dependencies(self, task_id: str) -> List[str]:
        """Get tasks that must complete before task_id"""
        deps = []
        for source, targets in self.edges.items():
            if task_id in targets:
                deps.append(source)
        return deps

    def get_dependents(self, task_id: str) -> List[str]:
        """Get tasks that depend on task_id"""
        return self.edges.get(task_id, [])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "plan_id": self.plan_id,
            "node_count": len(self.nodes),
            "edge_count": sum(len(targets) for targets in self.edges.values()),
            "entry_nodes": self.entry_nodes,
            "exit_nodes": self.exit_nodes,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }
