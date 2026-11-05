"""M12 Phase 3: RenderStage and RenderFailure Domain Models.

Immutable models for rendering execution stages and failure handling.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4


class StageType(StrEnum):
    """Rendering pipeline stages"""
    CLIP_RENDER = "clip_render"
    TRANSITION = "transition"
    COMPOSITE = "composite"
    SUBTITLE = "subtitle"
    OVERLAY = "overlay"
    ZOOM = "zoom"
    BROLL = "broll"
    AUDIO = "audio"
    EXPORT = "export"
    VALIDATE = "validate"


class FailureSeverity(StrEnum):
    """Failure severity levels"""
    RECOVERABLE = "recoverable"
    DEGRADED = "degraded"
    FATAL = "fatal"


@dataclass(frozen=True)
class RenderStage:
    """Immutable rendering pipeline stage."""

    stage_id: str = field(default_factory=lambda: str(uuid4()))
    job_id: str = ""
    stage_type: StageType = StageType.CLIP_RENDER

    # Dependencies
    depends_on: List[str] = field(default_factory=list)  # Stage IDs
    input_assets: List[str] = field(default_factory=list)  # Asset IDs

    # Resources
    estimated_duration_seconds: float = 0.0
    estimated_memory_mb: int = 512
    estimated_disk_mb: int = 1024
    requires_gpu: bool = False

    # Provider selection
    preferred_provider: str = "mock"
    fallback_providers: List[str] = field(default_factory=list)
    provider_capabilities_required: Set[str] = field(default_factory=set)

    # Retry policy
    max_retries: int = 3
    retry_delay_seconds: float = 5.0
    retry_backoff_multiplier: float = 2.0

    # Output specification
    output_path: str = ""
    expected_size_mb: int = 0

    # Metadata
    priority: int = 50
    created_at: datetime = field(default_factory=datetime.utcnow)
    observation_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage_id": self.stage_id,
            "job_id": self.job_id,
            "stage_type": self.stage_type.value,
            "depends_on": len(self.depends_on),
            "max_retries": self.max_retries,
            "preferred_provider": self.preferred_provider,
            "estimated_duration_seconds": self.estimated_duration_seconds,
        }


@dataclass(frozen=True)
class RenderFailure:
    """Immutable rendering failure record."""

    failure_id: str = field(default_factory=lambda: str(uuid4()))
    stage_id: str = ""
    job_id: str = ""

    # Failure info
    stage_type: StageType = StageType.CLIP_RENDER
    provider_name: str = ""
    exception_type: str = ""
    error_message: str = ""
    severity: FailureSeverity = FailureSeverity.RECOVERABLE

    # Recovery info
    is_recoverable: bool = True
    retry_count: int = 0
    fallback_provider: Optional[str] = None
    can_use_fallback: bool = False

    # Diagnostics
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    stack_trace: str = ""

    # Metadata
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "failure_id": self.failure_id,
            "stage_id": self.stage_id,
            "stage_type": self.stage_type.value,
            "provider_name": self.provider_name,
            "exception_type": self.exception_type,
            "severity": self.severity.value,
            "is_recoverable": self.is_recoverable,
            "retry_count": self.retry_count,
            "timestamp": self.timestamp.isoformat(),
        }


# ============================================================================
# RENDERING EVENTS
# ============================================================================


@dataclass(frozen=True)
class RenderingEvent:
    """Base rendering lifecycle event"""

    event_id: str = field(default_factory=lambda: str(uuid4()))
    event_type: str = ""
    job_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "job_id": self.job_id,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True)
class RenderingStarted(RenderingEvent):
    """Fired when rendering job starts"""
    event_type: str = "rendering_started"
    stage_count: int = 0


@dataclass(frozen=True)
class StageStarted(RenderingEvent):
    """Fired when stage execution begins"""
    event_type: str = "stage_started"
    stage_type: str = ""
    provider: str = ""


@dataclass(frozen=True)
class StageCompleted(RenderingEvent):
    """Fired when stage completes successfully"""
    event_type: str = "stage_completed"
    stage_type: str = ""
    duration_seconds: float = 0.0
    output_size_mb: int = 0


@dataclass(frozen=True)
class StageFailed(RenderingEvent):
    """Fired when stage fails"""
    event_type: str = "stage_failed"
    stage_type: str = ""
    failure: Optional[RenderFailure] = None
    will_retry: bool = False


@dataclass(frozen=True)
class RenderingCompleted(RenderingEvent):
    """Fired when rendering job completes"""
    event_type: str = "rendering_completed"
    success: bool = True
    total_duration_seconds: float = 0.0
    total_stages: int = 0
    failed_stages: int = 0


# ============================================================================
# RENDERING METRICS
# ============================================================================


@dataclass(frozen=True)
class RenderingMetrics:
    """Immutable rendering performance metrics"""

    metrics_id: str = field(default_factory=lambda: str(uuid4()))
    job_id: str = ""

    # Timing
    total_duration_seconds: float = 0.0
    stages_completed: int = 0
    stages_failed: int = 0

    # Resources
    peak_memory_mb: int = 0
    peak_cpu_percent: float = 0.0
    peak_gpu_percent: float = 0.0
    total_disk_written_mb: int = 0

    # Quality
    validation_passed: bool = False
    validation_score: float = 0.0

    # Efficiency
    avg_stage_duration_seconds: float = 0.0
    successful_retries: int = 0
    failed_retries: int = 0

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metrics_id": self.metrics_id,
            "job_id": self.job_id,
            "total_duration_seconds": self.total_duration_seconds,
            "stages_completed": self.stages_completed,
            "peak_memory_mb": self.peak_memory_mb,
            "validation_score": self.validation_score,
        }
