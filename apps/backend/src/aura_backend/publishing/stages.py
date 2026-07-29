"""M13 Phase 3: Publishing Orchestration — Stages and Failures.

Immutable stage models and failure tracking for publishing execution.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from .models import PlatformType
from .retry import RetryPolicy


class StageType(StrEnum):
    """Publishing stage types"""

    VALIDATE = "validate"  # Validate artifact and metadata
    AUTH = "auth"  # Authenticate with platform
    UPLOAD = "upload"  # Upload video to platform
    THUMBNAIL = "thumbnail"  # Upload thumbnail
    METADATA = "metadata"  # Set metadata (title, description, tags)
    PRIVACY = "privacy"  # Set privacy level
    SCHEDULE = "schedule"  # Schedule for later publishing
    PUBLISH = "publish"  # Publish draft
    PLAYLIST = "playlist"  # Add to playlist
    CAPTIONS = "captions"  # Generate captions
    FINALIZE = "finalize"  # Finalize publishing


class PublishingStageStatus(StrEnum):
    """Stage execution status"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class PublishStage:
    """Immutable publishing pipeline stage"""

    id: str = field(default_factory=lambda: str(uuid4()))
    job_id: str = ""
    stage_type: StageType = StageType.VALIDATE
    status: PublishingStageStatus = PublishingStageStatus.PENDING
    platform: PlatformType = PlatformType.YOUTUBE
    provider_name: str = ""
    preferred_provider: str = ""
    depends_on: tuple[str, ...] = ()
    retry_policy: RetryPolicy | None = None
    schedule_metadata: dict = field(default_factory=dict)
    stage_inputs: dict = field(default_factory=dict)
    stage_outputs: dict = field(default_factory=dict)
    is_optional: bool = False
    skip_if_error: bool = False
    estimated_duration_seconds: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    retry_count: int = 0
    error_message: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "job_id": self.job_id,
            "stage_type": self.stage_type.value,
            "status": self.status.value,
            "platform": self.platform.value,
            "provider": self.provider_name,
            "depends_on": self.depends_on,
            "is_optional": self.is_optional,
            "retry_count": self.retry_count,
            "estimated_duration_seconds": self.estimated_duration_seconds,
        }


@dataclass(frozen=True)
class PublishingFailure:
    """Immutable publishing failure record"""

    id: str = field(default_factory=lambda: str(uuid4()))
    job_id: str = ""
    stage_id: str = ""
    stage_type: StageType = StageType.VALIDATE
    platform: PlatformType = PlatformType.YOUTUBE
    provider_name: str = ""
    error_code: str = ""
    error_message: str = ""
    exception_type: str = ""
    is_recoverable: bool = True
    retry_count: int = 0
    max_retries: int = 3
    fallback_provider: str | None = None
    can_use_fallback: bool = False
    diagnostics: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "job_id": self.job_id,
            "stage_id": self.stage_id,
            "stage_type": self.stage_type.value,
            "platform": self.platform.value,
            "provider": self.provider_name,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "is_recoverable": self.is_recoverable,
            "retry_count": self.retry_count,
            "fallback_provider": self.fallback_provider,
            "timestamp": self.timestamp.isoformat(),
        }
