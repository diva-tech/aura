"""M13 Phase 1: Publishing Foundation — Reporting Models.

Immutable reporting models tracking publishing status and results.
"""

from dataclasses import dataclass, field
from datetime import datetime

from .models import PlatformType, PublishingStatus


@dataclass(frozen=True)
class PublishingReport:
    """Immutable publishing report for a single task"""

    id: str = ""
    job_id: str = ""
    task_id: str = ""
    platform: PlatformType = PlatformType.YOUTUBE
    publish_status: PublishingStatus = PublishingStatus.PENDING
    scheduled_publish_time: datetime | None = None
    actual_publish_time: datetime | None = None
    platform_video_id: str = ""
    platform_url: str = ""
    thumbnail_uploaded: bool = False
    thumbnail_status: str = "pending"  # pending, uploaded, failed
    metadata_synced: bool = False
    metadata_status: str = "pending"  # pending, synced, failed
    processing_state: str = "pending"  # pending, processing, completed, failed
    duration_seconds: float = 0.0
    retry_count: int = 0
    last_error_message: str = ""
    is_draft: bool = True
    is_scheduled: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "job_id": self.job_id,
            "task_id": self.task_id,
            "platform": self.platform.value,
            "publish_status": self.publish_status.value,
            "scheduled_time": (
                self.scheduled_publish_time.isoformat() if self.scheduled_publish_time else None
            ),
            "actual_time": (
                self.actual_publish_time.isoformat() if self.actual_publish_time else None
            ),
            "platform_video_id": self.platform_video_id,
            "platform_url": self.platform_url,
            "thumbnail_status": self.thumbnail_status,
            "metadata_status": self.metadata_status,
            "processing_state": self.processing_state,
            "retry_count": self.retry_count,
            "duration_seconds": self.duration_seconds,
        }


@dataclass(frozen=True)
class TaskReport:
    """Immutable task-level report"""

    id: str = ""
    job_id: str = ""
    task_id: str = ""
    platform: PlatformType = PlatformType.YOUTUBE
    status: PublishingStatus = PublishingStatus.PENDING
    started_at: datetime | None = None
    completed_at: datetime | None = None
    total_attempts: int = 0
    successful_attempt: int = 0
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    platform_response_code: str = ""
    platform_response_time_ms: int = 0
    metadata_payload_size_bytes: int = 0
    media_size_bytes: int = 0
    thumbnail_size_bytes: int = 0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "job_id": self.job_id,
            "task_id": self.task_id,
            "platform": self.platform.value,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "total_attempts": self.total_attempts,
            "errors": self.errors,
            "warnings": self.warnings,
        }


@dataclass(frozen=True)
class JobReport:
    """Immutable job-level report"""

    id: str = ""
    job_id: str = ""
    total_tasks: int = 0
    completed_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    skipped_tasks: int = 0
    task_reports: tuple[PublishingReport, ...] = ()
    started_at: datetime | None = None
    completed_at: datetime | None = None
    total_duration_seconds: float = 0.0
    platforms_targeted: tuple[PlatformType, ...] = ()
    platforms_succeeded: tuple[PlatformType, ...] = ()
    platforms_failed: tuple[PlatformType, ...] = ()
    overall_status: PublishingStatus = PublishingStatus.PENDING
    summary_message: str = ""

    @property
    def success_rate(self) -> float:
        if self.total_tasks == 0:
            return 0.0
        return (self.successful_tasks / self.total_tasks) * 100.0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "job_id": self.job_id,
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "successful_tasks": self.successful_tasks,
            "failed_tasks": self.failed_tasks,
            "success_rate_percent": self.success_rate,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "total_duration_seconds": self.total_duration_seconds,
            "platforms_targeted": [p.value for p in self.platforms_targeted],
            "platforms_succeeded": [p.value for p in self.platforms_succeeded],
            "overall_status": self.overall_status.value,
        }


@dataclass(frozen=True)
class PublishingSummary:
    """Immutable summary of publishing results"""

    job_id: str = ""
    total_platforms: int = 0
    successful_platforms: int = 0
    failed_platforms: int = 0
    total_duration_seconds: float = 0.0
    avg_duration_per_platform_seconds: float = 0.0
    total_bytes_uploaded: int = 0
    error_summary: str = ""
    warning_summary: str = ""
    next_action_required: bool = False
    next_action_description: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def success_rate(self) -> float:
        if self.total_platforms == 0:
            return 0.0
        return (self.successful_platforms / self.total_platforms) * 100.0

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "total_platforms": self.total_platforms,
            "successful_platforms": self.successful_platforms,
            "failed_platforms": self.failed_platforms,
            "success_rate_percent": self.success_rate,
            "total_duration_seconds": self.total_duration_seconds,
            "avg_duration_per_platform_seconds": self.avg_duration_per_platform_seconds,
            "total_bytes_uploaded_mb": self.total_bytes_uploaded / (1024 * 1024),
            "next_action_required": self.next_action_required,
        }
