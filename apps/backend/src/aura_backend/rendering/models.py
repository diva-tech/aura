"""M12 Phase 1: Rendering Domain Models.

Immutable data structures for rendering jobs, tasks, assets, and validation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4


class RenderJobStatus(StrEnum):
    """Status of a rendering job"""
    PENDING = "pending"
    QUEUED = "queued"
    RENDERING = "rendering"
    VALIDATING = "validating"
    EXPORTING = "exporting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RenderTaskType(StrEnum):
    """Types of rendering tasks"""
    CLIP_RENDER = "clip_render"
    TRANSITION_APPLY = "transition_apply"
    SUBTITLE_BURN = "subtitle_burn"
    OVERLAY_APPLY = "overlay_apply"
    ZOOM_APPLY = "zoom_apply"
    BROLL_INSERT = "broll_insert"
    AUDIO_MIX = "audio_mix"
    COMPOSITE = "composite"
    EXPORT = "export"
    VALIDATE = "validate"


class AssetType(StrEnum):
    """Types of rendered assets"""
    CLIP = "clip"
    TRANSITION = "transition"
    COMPOSITE = "composite"
    INTERMEDIATE = "intermediate"
    FINAL_VIDEO = "final_video"
    THUMBNAIL = "thumbnail"
    MANIFEST = "manifest"


class ExportProfile(StrEnum):
    """Export profiles for different platforms"""
    YOUTUBE_16_9 = "youtube_16_9"  # 1920x1080, 30fps
    YOUTUBE_SHORTS = "youtube_shorts"  # 1080x1920, 30fps
    TIKTOK = "tiktok"  # 1080x1920, 30fps
    INSTAGRAM_REEL = "instagram_reel"  # 1080x1920, 30fps
    INSTAGRAM_FEED = "instagram_feed"  # 1080x1080, 30fps
    LINKEDIN = "linkedin"  # 1200x675, 24fps
    PODCAST_AUDIO = "podcast_audio"  # Audio only, 44.1kHz stereo
    CUSTOM = "custom"


class ValidationStatus(StrEnum):
    """Validation result status"""
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"


@dataclass(frozen=True)
class RenderJob:
    """Immutable rendering job definition."""

    job_id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    video_id: str = ""
    edit_plan_id: str = ""

    # Job metadata
    status: RenderJobStatus = RenderJobStatus.PENDING
    priority: int = 50  # 1-100
    provider: str = "ffmpeg"  # ffmpeg, moviepy, remotion, mock

    # Configuration
    target_resolution: str = "1920x1080"
    target_fps: int = 30
    target_codec: str = "h264"
    target_bitrate: str = "5000k"

    # Export profiles
    export_profiles: List[ExportProfile] = field(default_factory=list)

    # Tracking
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

    # Metadata
    observation_ids: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "session_id": self.session_id,
            "video_id": self.video_id,
            "status": self.status.value,
            "provider": self.provider,
            "target_resolution": self.target_resolution,
            "target_fps": self.target_fps,
            "export_profiles": [p.value for p in self.export_profiles],
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class RenderTask:
    """Immutable rendering task (executed by M6 agent)."""

    task_id: str = field(default_factory=lambda: str(uuid4()))
    job_id: str = ""
    task_type: RenderTaskType = RenderTaskType.CLIP_RENDER

    # Input specification
    source_path: str = ""  # Path to source media
    clip_start_seconds: float = 0.0
    clip_end_seconds: float = 0.0

    # Rendering parameters
    parameters: Dict[str, Any] = field(default_factory=dict)

    # Dependencies
    depends_on: List[str] = field(default_factory=list)  # Task IDs this depends on
    input_assets: List[str] = field(default_factory=list)  # Asset IDs needed

    # Output specification
    output_path: str = ""
    expected_duration_seconds: float = 0.0

    # Metadata
    priority: int = 50
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "job_id": self.job_id,
            "task_type": self.task_type.value,
            "source_path": self.source_path,
            "output_path": self.output_path,
            "depends_on": len(self.depends_on),
            "expected_duration_seconds": self.expected_duration_seconds,
        }


@dataclass(frozen=True)
class RenderSegment:
    """Immutable rendering segment (part of a clip or composite)."""

    segment_id: str = field(default_factory=lambda: str(uuid4()))
    clip_id: str = ""
    segment_index: int = 0

    # Timing
    start_time_seconds: float = 0.0
    end_time_seconds: float = 0.0
    duration_seconds: float = 0.0

    # Content
    content_type: str = ""  # "clip", "transition", "overlay", etc.
    source_path: str = ""

    # Effects to apply (in order)
    effects: List[Dict[str, Any]] = field(default_factory=list)

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "segment_id": self.segment_id,
            "clip_id": self.clip_id,
            "segment_index": self.segment_index,
            "start_time_seconds": self.start_time_seconds,
            "duration_seconds": self.duration_seconds,
            "content_type": self.content_type,
        }


@dataclass(frozen=True)
class AssetMetadata:
    """Immutable metadata for rendered assets."""

    asset_id: str = field(default_factory=lambda: str(uuid4()))
    job_id: str = ""
    asset_type: AssetType = AssetType.CLIP

    # File information
    file_path: str = ""
    file_size_bytes: int = 0
    checksum: str = ""

    # Media information
    duration_seconds: float = 0.0
    resolution: str = "1920x1080"
    fps: int = 30
    codec: str = "h264"
    bitrate: str = "5000k"
    audio_sample_rate: int = 48000

    # Validation
    is_valid: bool = False
    validation_passed: bool = False

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "asset_type": self.asset_type.value,
            "file_path": self.file_path,
            "file_size_bytes": self.file_size_bytes,
            "duration_seconds": self.duration_seconds,
            "resolution": self.resolution,
            "fps": self.fps,
            "codec": self.codec,
            "is_valid": self.is_valid,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class RenderedAsset:
    """Immutable rendered asset with metadata."""

    asset_id: str = field(default_factory=lambda: str(uuid4()))
    metadata: AssetMetadata = field(default_factory=AssetMetadata)
    content_hash: str = ""  # SHA256 of content

    # Asset reference
    job_id: str = ""
    parent_asset_id: Optional[str] = None

    # Lifecycle
    created_at: datetime = field(default_factory=datetime.utcnow)
    archived_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "asset_type": self.metadata.asset_type.value,
            "file_path": self.metadata.file_path,
            "content_hash": self.content_hash,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class Artifact:
    """Immutable artifact (final output of rendering job)."""

    artifact_id: str = field(default_factory=lambda: str(uuid4()))
    job_id: str = ""
    session_id: str = ""
    video_id: str = ""

    # File information
    file_path: str = ""
    file_size_bytes: int = 0
    checksum: str = ""

    # Media specifications
    duration_seconds: float = 0.0
    resolution: str = "1920x1080"
    fps: int = 30
    codec: str = "h264"
    bitrate: str = "5000k"
    audio_sample_rate: int = 48000

    # Export profile
    export_profile: ExportProfile = ExportProfile.CUSTOM

    # Validation
    validation_passed: bool = False
    validation_score: float = 0.0

    # Lifecycle
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "job_id": self.job_id,
            "file_path": self.file_path,
            "file_size_bytes": self.file_size_bytes,
            "duration_seconds": self.duration_seconds,
            "resolution": self.resolution,
            "export_profile": self.export_profile.value,
            "validation_passed": self.validation_passed,
            "validation_score": self.validation_score,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class ArtifactBundle:
    """Immutable bundle of all artifacts from a render job."""

    bundle_id: str = field(default_factory=lambda: str(uuid4()))
    job_id: str = ""
    session_id: str = ""
    video_id: str = ""

    # Artifacts
    final_video: Optional[Artifact] = None
    thumbnails: List[Artifact] = field(default_factory=list)
    exports: List[Artifact] = field(default_factory=list)
    intermediate_assets: List[RenderedAsset] = field(default_factory=list)

    # Metadata
    total_size_bytes: int = 0
    creation_timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bundle_id": self.bundle_id,
            "job_id": self.job_id,
            "final_video": self.final_video.to_dict() if self.final_video else None,
            "export_count": len(self.exports),
            "thumbnail_count": len(self.thumbnails),
            "total_size_bytes": self.total_size_bytes,
            "creation_timestamp": self.creation_timestamp.isoformat(),
        }


@dataclass(frozen=True)
class RenderResult:
    """Immutable result of a rendering operation."""

    result_id: str = field(default_factory=lambda: str(uuid4()))
    job_id: str = ""

    # Success/failure
    success: bool = False
    error_message: Optional[str] = None

    # Artifacts produced
    artifact_bundle: Optional[ArtifactBundle] = None

    # Timing
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime = field(default_factory=datetime.utcnow)

    # Metadata
    observation_ids: List[str] = field(default_factory=list)

    @property
    def duration_seconds(self) -> float:
        return (self.completed_at - self.started_at).total_seconds()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "result_id": self.result_id,
            "job_id": self.job_id,
            "success": self.success,
            "duration_seconds": self.duration_seconds,
            "artifacts": (
                self.artifact_bundle.to_dict() if self.artifact_bundle else None
            ),
            "error_message": self.error_message,
        }


@dataclass(frozen=True)
class RenderMetrics:
    """Immutable metrics from a rendering job."""

    metrics_id: str = field(default_factory=lambda: str(uuid4()))
    job_id: str = ""

    # Timing metrics
    total_duration_seconds: float = 0.0
    encoding_time_seconds: float = 0.0
    export_time_seconds: float = 0.0
    validation_time_seconds: float = 0.0

    # Resource usage
    peak_cpu_percent: float = 0.0
    peak_memory_mb: float = 0.0
    peak_gpu_percent: float = 0.0

    # Output metrics
    frames_rendered: int = 0
    output_file_size_bytes: int = 0
    encoding_speed: float = 0.0  # FPS

    # Quality
    validation_score: float = 0.0
    artifacts_created: int = 0

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metrics_id": self.metrics_id,
            "job_id": self.job_id,
            "total_duration_seconds": self.total_duration_seconds,
            "peak_cpu_percent": self.peak_cpu_percent,
            "peak_memory_mb": self.peak_memory_mb,
            "frames_rendered": self.frames_rendered,
            "encoding_speed": self.encoding_speed,
            "validation_score": self.validation_score,
        }


@dataclass(frozen=True)
class ValidationResult:
    """Immutable validation result for rendered output."""

    validation_id: str = field(default_factory=lambda: str(uuid4()))
    artifact_id: str = ""

    # Overall result
    status: ValidationStatus = ValidationStatus.PASSED
    score: float = 1.0  # 0-1

    # Validation checks
    resolution_valid: bool = True
    duration_valid: bool = True
    fps_valid: bool = True
    audio_sync_valid: bool = True
    subtitle_sync_valid: bool = True
    frames_intact: bool = True
    checksum_valid: bool = True

    # Issues found
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "validation_id": self.validation_id,
            "artifact_id": self.artifact_id,
            "status": self.status.value,
            "score": self.score,
            "resolution_valid": self.resolution_valid,
            "duration_valid": self.duration_valid,
            "issues": len(self.issues),
            "warnings": len(self.warnings),
        }


@dataclass(frozen=True)
class RenderManifest:
    """Immutable manifest of all rendering work."""

    manifest_id: str = field(default_factory=lambda: str(uuid4()))
    job_id: str = ""
    session_id: str = ""
    video_id: str = ""

    # Tasks
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0

    # Artifacts
    artifacts_created: List[Artifact] = field(default_factory=list)
    asset_count: int = 0

    # Metrics
    render_metrics: Optional[RenderMetrics] = None

    # Validation
    validation_results: List[ValidationResult] = field(default_factory=list)

    # Timestamps
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "manifest_id": self.manifest_id,
            "job_id": self.job_id,
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "artifacts_count": len(self.artifacts_created),
            "validation_count": len(self.validation_results),
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat(),
        }


@dataclass(frozen=True)
class RenderGraph:
    """Immutable rendering dependency graph."""

    graph_id: str = field(default_factory=lambda: str(uuid4()))
    job_id: str = ""

    # Task nodes
    tasks: List[RenderTask] = field(default_factory=list)

    # Edges (dependencies)
    edges: Dict[str, List[str]] = field(default_factory=dict)  # task_id -> [depends_on]

    # Execution order
    execution_order: List[str] = field(default_factory=list)  # Topologically sorted task IDs

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "job_id": self.job_id,
            "task_count": len(self.tasks),
            "edge_count": len(self.edges),
            "execution_order_length": len(self.execution_order),
        }
