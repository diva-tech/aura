"""M13 Phase 1: Publishing Foundation — Core Domain Models.

Immutable domain models for publishing jobs, tasks, platforms, and results.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import uuid4


class PublishingStatus(StrEnum):
    """Publishing job status"""

    PENDING = "pending"
    SCHEDULED = "scheduled"
    QUEUED = "queued"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"
    PARTIALLY_PUBLISHED = "partially_published"
    SCHEDULED_FOR_LATER = "scheduled_for_later"


class PublishingPriority(StrEnum):
    """Publishing priority level"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class PlatformType(StrEnum):
    """Supported publishing platforms"""

    YOUTUBE = "youtube"
    YOUTUBE_SHORTS = "youtube_shorts"
    TIKTOK = "tiktok"
    INSTAGRAM_REEL = "instagram_reel"
    INSTAGRAM_FEED = "instagram_feed"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    TWITCH = "twitch"
    PODCAST = "podcast"
    CUSTOM = "custom"


@dataclass(frozen=True)
class PublishingJob:
    """Immutable publishing job specification"""

    id: str = field(default_factory=lambda: str(uuid4()))
    artifact_bundle_id: str = ""
    session_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = ""
    status: PublishingStatus = PublishingStatus.PENDING
    priority: PublishingPriority = PublishingPriority.NORMAL
    title: str = ""
    description: str = ""
    tags: tuple[str, ...] = ()
    platforms: tuple[PlatformType, ...] = ()
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "artifact_bundle_id": self.artifact_bundle_id,
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "status": self.status.value,
            "priority": self.priority.value,
            "title": self.title,
            "platforms": [p.value for p in self.platforms],
            "progress": f"{self.completed_tasks}/{self.total_tasks}",
        }


@dataclass(frozen=True)
class PublishingTask:
    """Immutable publishing task for a single platform"""

    id: str = field(default_factory=lambda: str(uuid4()))
    job_id: str = ""
    platform: PlatformType = PlatformType.YOUTUBE
    status: PublishingStatus = PublishingStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    scheduled_publish_time: datetime | None = None
    platform_video_id: str = ""
    platform_url: str = ""
    is_draft: bool = True
    is_scheduled: bool = False
    retry_count: int = 0
    error_message: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "job_id": self.job_id,
            "platform": self.platform.value,
            "status": self.status.value,
            "platform_video_id": self.platform_video_id,
            "platform_url": self.platform_url,
            "is_draft": self.is_draft,
            "is_scheduled": self.is_scheduled,
            "retry_count": self.retry_count,
        }


@dataclass(frozen=True)
class PlatformAccount:
    """Immutable platform account credentials container"""

    id: str = field(default_factory=lambda: str(uuid4()))
    platform: PlatformType = PlatformType.YOUTUBE
    user_id: str = ""
    account_name: str = ""
    email: str = ""
    is_verified: bool = False
    is_active: bool = True
    last_used_at: datetime | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "platform": self.platform.value,
            "account_name": self.account_name,
            "email": self.email,
            "is_verified": self.is_verified,
            "is_active": self.is_active,
        }


@dataclass(frozen=True)
class PublishingMetadata:
    """Immutable publishing metadata"""

    title: str = ""
    description: str = ""
    tags: tuple[str, ...] = ()
    category: str = ""
    language: str = "en"
    is_made_for_kids: bool = False
    is_nsfw: bool = False
    allow_comments: bool = True
    allow_likes: bool = True
    allow_embedding: bool = True
    is_monetized: bool = False
    visibility: str = "public"  # public, unlisted, private
    license: str = "standard"  # standard, cc
    recording_date: datetime | None = None
    location: str = ""
    custom_metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "description": self.description,
            "tags": self.tags,
            "category": self.category,
            "language": self.language,
            "is_made_for_kids": self.is_made_for_kids,
            "visibility": self.visibility,
            "is_monetized": self.is_monetized,
        }


@dataclass(frozen=True)
class ThumbnailAsset:
    """Immutable thumbnail asset"""

    id: str = field(default_factory=lambda: str(uuid4()))
    job_id: str = ""
    file_path: str = ""
    file_size_bytes: int = 0
    width_pixels: int = 0
    height_pixels: int = 0
    format: str = "jpg"  # jpg, png, webp
    is_custom: bool = False
    is_auto_generated: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "file_path": self.file_path,
            "dimensions": f"{self.width_pixels}x{self.height_pixels}",
            "format": self.format,
            "is_custom": self.is_custom,
            "file_size_mb": self.file_size_bytes / (1024 * 1024),
        }


@dataclass(frozen=True)
class PublishedAsset:
    """Immutable published asset record"""

    id: str = field(default_factory=lambda: str(uuid4()))
    task_id: str = ""
    platform: PlatformType = PlatformType.YOUTUBE
    platform_video_id: str = ""
    platform_url: str = ""
    platform_thumbnail_url: str = ""
    duration_seconds: int = 0
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    published_at: datetime = field(default_factory=datetime.utcnow)
    metadata_status: str = "synced"  # synced, pending, failed
    thumbnail_status: str = "uploaded"  # uploaded, pending, failed
    is_live: bool = False
    is_monetized: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "platform": self.platform.value,
            "platform_video_id": self.platform_video_id,
            "platform_url": self.platform_url,
            "published_at": self.published_at.isoformat(),
            "view_count": self.view_count,
            "metadata_status": self.metadata_status,
        }


@dataclass(frozen=True)
class PublishingResult:
    """Immutable publishing task result"""

    id: str = field(default_factory=lambda: str(uuid4()))
    task_id: str = ""
    job_id: str = ""
    platform: PlatformType = PlatformType.YOUTUBE
    status: PublishingStatus = PublishingStatus.PENDING
    is_success: bool = False
    error_code: str = ""
    error_message: str = ""
    warning_messages: tuple[str, ...] = ()
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    duration_seconds: float = 0.0
    published_asset: PublishedAsset | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "platform": self.platform.value,
            "status": self.status.value,
            "is_success": self.is_success,
            "error_message": self.error_message,
            "duration_seconds": self.duration_seconds,
        }


@dataclass(frozen=True)
class PublishingMetrics:
    """Immutable publishing metrics"""

    job_id: str = ""
    total_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    skipped_tasks: int = 0
    total_duration_seconds: float = 0.0
    avg_task_duration_seconds: float = 0.0
    retry_count: int = 0
    total_retries: int = 0
    platforms_published: tuple[PlatformType, ...] = ()
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None

    @property
    def success_rate(self) -> float:
        if self.total_tasks == 0:
            return 0.0
        return (self.successful_tasks / self.total_tasks) * 100.0

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "total_tasks": self.total_tasks,
            "successful_tasks": self.successful_tasks,
            "failed_tasks": self.failed_tasks,
            "success_rate_percent": self.success_rate,
            "total_duration_seconds": self.total_duration_seconds,
            "platforms": [p.value for p in self.platforms_published],
        }
