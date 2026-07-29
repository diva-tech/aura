"""Milestone 13: Publishing & Distribution Platform.

Phase 1: Publishing Foundation
- Domain models, profiles, scheduling, reporting, retry policies

Phase 2: Publishing Providers
- Context, capability models, abstract provider interface, reference implementations

Phase 3: Publishing Orchestration
- Stages, failures, events, planner, M6 agents, M8 integration
"""

# Provider Backends (Phase 2)
from .backends import (
    InstagramProvider,
    LinkedInProvider,
    MockPublishingProvider,
    PodcastProvider,
    TikTokProvider,
    YouTubeProvider,
    create_default_provider_registry,
)

# Context & Capability (Phase 2)
from .context import (
    PublishCapability,
    PublishingContext,
)

# Events (Phase 3)
from .events import (
    PublishingCompleted,
    PublishingEvent,
    PublishingMetricsEvent,
    PublishingStarted,
    StageCompleted,
    StageFailed,
    StageStarted,
)

# Manifest
from .manifest import PublishingManifest

# Models
from .models import (
    PlatformAccount,
    PlatformType,
    PublishedAsset,
    PublishingJob,
    PublishingMetadata,
    PublishingMetrics,
    PublishingPriority,
    PublishingResult,
    PublishingStatus,
    PublishingTask,
    ThumbnailAsset,
)

# Orchestration (Phase 3)
from .orchestration import (
    AuthenticationAgent,
    CaptionsAgent,
    MetadataAgent,
    PrivacyAgent,
    PublishAgent,
    PublishingAgent,
    PublishingAgentRegistry,
    PublishingPlanner,
    ScheduleAgent,
    ThumbnailAgent,
    UploadAgent,
    create_default_publishing_agent_registry,
)

# Profiles
from .profiles import (
    CUSTOM_PROFILE,
    INSTAGRAM_FEED_PROFILE,
    INSTAGRAM_REEL_PROFILE,
    LINKEDIN_PROFILE,
    PODCAST_PROFILE,
    TIKTOK_PROFILE,
    YOUTUBE_PROFILE,
    YOUTUBE_SHORTS_PROFILE,
    PublishingProfile,
    get_all_profiles,
    get_profile,
)

# Providers (Phase 2)
from .providers import (
    ProviderRegistry,
    PublishingProvider,
    UploadResponse,
)

# Reporting
from .reports import (
    JobReport,
    PublishingReport,
    PublishingSummary,
    TaskReport,
)

# Retry
from .retry import (
    AGGRESSIVE_RETRY_POLICY,
    CONSERVATIVE_RETRY_POLICY,
    DEFAULT_RETRY_POLICY,
    NO_RETRY_POLICY,
    RATE_LIMIT_RETRY_POLICY,
    RetryableError,
    RetryPolicy,
    RetryStrategy,
)

# Scheduling
from .schedule import (
    ImmediateSchedule,
    PublishSchedule,
    RecurrencePattern,
    RecurringPublish,
    ScheduledPublish,
    ScheduleType,
    WeekDay,
)

# Stages & Failures (Phase 3)
from .stages import (
    PublishingFailure,
    PublishingStageStatus,
    PublishStage,
    StageType,
)

__all__ = [
    # Stages & Failures (Phase 3)
    "PublishingFailure",
    "PublishStage",
    "PublishingStageStatus",
    "StageType",
    # Events (Phase 3)
    "PublishingCompleted",
    "PublishingEvent",
    "PublishingMetricsEvent",
    "PublishingStarted",
    "StageCompleted",
    "StageFailed",
    "StageStarted",
    # Orchestration (Phase 3)
    "AuthenticationAgent",
    "CaptionsAgent",
    "MetadataAgent",
    "PrivacyAgent",
    "PublishAgent",
    "PublishingAgent",
    "PublishingAgentRegistry",
    "PublishingPlanner",
    "ScheduleAgent",
    "ThumbnailAgent",
    "UploadAgent",
    "create_default_publishing_agent_registry",
    # Context & Capability (Phase 2)
    "PublishCapability",
    "PublishingContext",
    # Providers (Phase 2)
    "PublishingProvider",
    "ProviderRegistry",
    "UploadResponse",
    # Provider Backends (Phase 2)
    "InstagramProvider",
    "LinkedInProvider",
    "MockPublishingProvider",
    "PodcastProvider",
    "TikTokProvider",
    "YouTubeProvider",
    "create_default_provider_registry",
    # Models
    "PlatformAccount",
    "PlatformType",
    "PublishingJob",
    "PublishingMetadata",
    "PublishingMetrics",
    "PublishingPriority",
    "PublishingResult",
    "PublishedAsset",
    "PublishingStatus",
    "PublishingTask",
    "ThumbnailAsset",
    # Profiles
    "CUSTOM_PROFILE",
    "INSTAGRAM_FEED_PROFILE",
    "INSTAGRAM_REEL_PROFILE",
    "LINKEDIN_PROFILE",
    "PODCAST_PROFILE",
    "TIKTOK_PROFILE",
    "YOUTUBE_PROFILE",
    "YOUTUBE_SHORTS_PROFILE",
    "PublishingProfile",
    "get_all_profiles",
    "get_profile",
    # Scheduling
    "ImmediateSchedule",
    "PublishSchedule",
    "RecurringPublish",
    "RecurrencePattern",
    "ScheduledPublish",
    "ScheduleType",
    "WeekDay",
    # Reporting
    "JobReport",
    "PublishingSummary",
    "PublishingReport",
    "TaskReport",
    # Manifest
    "PublishingManifest",
    # Retry
    "AGGRESSIVE_RETRY_POLICY",
    "CONSERVATIVE_RETRY_POLICY",
    "DEFAULT_RETRY_POLICY",
    "NO_RETRY_POLICY",
    "RATE_LIMIT_RETRY_POLICY",
    "RetryPolicy",
    "RetryStrategy",
    "RetryableError",
]
