"""M13 Phase 2: Publishing Providers — Context and Capability Models.

Immutable execution context and capability declaration for publishers.
"""

from dataclasses import dataclass, field

from .models import (
    PlatformAccount,
    PlatformType,
    PublishingMetadata,
)
from .profiles import PublishingProfile
from .retry import RetryPolicy
from .schedule import PublishSchedule


@dataclass(frozen=True)
class PublishCapability:
    """Immutable provider capability declaration"""

    provider_name: str = ""
    platform: PlatformType = PlatformType.YOUTUBE
    supports_upload: bool = True
    supports_scheduling: bool = True
    supports_thumbnails: bool = True
    supports_playlists: bool = False
    supports_auto_captions: bool = False
    supports_auto_translation: bool = False
    supports_premiere: bool = False
    supports_live: bool = False
    supports_shorts: bool = False
    supports_monetization: bool = False
    supports_analytics: bool = False
    supports_comments: bool = True
    supports_embedding: bool = True
    supports_privacy_levels: tuple[str, ...] = ()  # public, unlisted, private
    supported_codecs: tuple[str, ...] = ()
    supported_resolutions: tuple[str, ...] = ()
    supported_aspect_ratios: tuple[str, ...] = ()
    max_upload_size_mb: int = 0
    max_duration_seconds: int = 0
    requires_authentication: bool = True
    authentication_type: str = ""  # oauth2, api_key, etc.
    rate_limit_requests_per_hour: int = 0
    concurrent_uploads_supported: int = 1

    def supports_feature(self, feature: str) -> bool:
        """Check if provider supports a feature"""
        feature_map = {
            "upload": self.supports_upload,
            "scheduling": self.supports_scheduling,
            "thumbnails": self.supports_thumbnails,
            "playlists": self.supports_playlists,
            "auto_captions": self.supports_auto_captions,
            "auto_translation": self.supports_auto_translation,
            "premiere": self.supports_premiere,
            "live": self.supports_live,
            "shorts": self.supports_shorts,
            "monetization": self.supports_monetization,
            "analytics": self.supports_analytics,
            "comments": self.supports_comments,
            "embedding": self.supports_embedding,
        }
        return feature_map.get(feature, False)

    def supports_codec(self, codec: str) -> bool:
        """Check if provider supports codec"""
        return codec in self.supported_codecs

    def supports_resolution(self, resolution: str) -> bool:
        """Check if provider supports resolution"""
        return resolution in self.supported_resolutions

    def supports_aspect_ratio(self, aspect_ratio: str) -> bool:
        """Check if provider supports aspect ratio"""
        return aspect_ratio in self.supported_aspect_ratios

    def to_dict(self) -> dict:
        return {
            "provider_name": self.provider_name,
            "platform": self.platform.value,
            "supports_upload": self.supports_upload,
            "supports_scheduling": self.supports_scheduling,
            "supports_thumbnails": self.supports_thumbnails,
            "supports_monetization": self.supports_monetization,
            "supports_analytics": self.supports_analytics,
            "max_upload_size_mb": self.max_upload_size_mb,
            "max_duration_seconds": self.max_duration_seconds,
            "concurrent_uploads": self.concurrent_uploads_supported,
        }


@dataclass(frozen=True)
class PublishingContext:
    """Immutable publishing execution context"""

    job_id: str = ""
    artifact_bundle_id: str = ""
    session_id: str = ""
    platform_account: PlatformAccount | None = None
    publishing_profile: PublishingProfile | None = None
    publishing_schedule: PublishSchedule | None = None
    publishing_metadata: PublishingMetadata | None = None
    retry_policy: RetryPolicy | None = None
    artifact_directory: str = ""
    output_directory: str = ""
    thumbnail_path: str = ""
    video_file_path: str = ""
    is_draft: bool = True
    create_thumbnail: bool = False
    generate_captions: bool = False
    translate_metadata: bool = False
    enable_monetization: bool = False
    enable_analytics: bool = False
    custom_options: dict = field(default_factory=dict)
    timeout_seconds: int = 3600
    max_retries: int = 3

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "artifact_bundle_id": self.artifact_bundle_id,
            "session_id": self.session_id,
            "platform": self.publishing_profile.platform.value if self.publishing_profile else None,
            "is_draft": self.is_draft,
            "create_thumbnail": self.create_thumbnail,
            "generate_captions": self.generate_captions,
            "enable_monetization": self.enable_monetization,
            "timeout_seconds": self.timeout_seconds,
        }
