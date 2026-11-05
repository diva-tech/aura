"""M13 Phase 2: Publishing Providers — Reference Implementations.

Mock and platform-specific provider implementations.
"""

from datetime import datetime

from .context import PublishCapability, PublishingContext
from .models import PlatformType, PublishingResult, PublishingStatus
from .providers import ProviderRegistry, PublishingProvider, UploadResponse


class MockPublishingProvider(PublishingProvider):
    """Mock provider for testing (always succeeds)"""

    @property
    def provider_name(self) -> str:
        return "mock"

    @property
    def capabilities(self) -> PublishCapability:
        return PublishCapability(
            provider_name="mock",
            platform=PlatformType.CUSTOM,
            supports_upload=True,
            supports_scheduling=True,
            supports_thumbnails=True,
            supports_playlists=True,
            supports_auto_captions=True,
            supports_auto_translation=True,
            supports_premiere=True,
            supports_live=True,
            supports_shorts=True,
            supports_monetization=True,
            supports_analytics=True,
            supports_comments=True,
            supports_embedding=True,
            supports_privacy_levels=("public", "unlisted", "private"),
            supported_codecs=("h264", "h265", "vp9", "av1"),
            supported_resolutions=(
                "4320p",
                "2160p",
                "1440p",
                "1080p",
                "720p",
                "480p",
                "360p",
                "240p",
            ),
            supported_aspect_ratios=("16:9", "9:16", "1:1", "4:5"),
            max_upload_size_mb=1000000,
            max_duration_seconds=24 * 60 * 60,
            requires_authentication=False,
            rate_limit_requests_per_hour=10000,
            concurrent_uploads_supported=10,
        )

    async def is_available(self) -> bool:
        return True

    async def authenticate(self, context: PublishingContext) -> bool:
        return True

    async def validate_credentials(self, context: PublishingContext) -> bool:
        return True

    async def upload_video(self, context: PublishingContext) -> UploadResponse:
        return UploadResponse(
            is_success=True,
            platform_video_id=f"mock_video_{context.job_id}",
            platform_url="https://mock.example.com/watch?v=test",
            metadata_synced=True,
            thumbnail_uploaded=True,
        )

    async def upload_thumbnail(self, context: PublishingContext) -> bool:
        return True

    async def set_metadata(self, context: PublishingContext) -> bool:
        return True

    async def set_privacy(self, context: PublishingContext, privacy_level: str) -> bool:
        return True

    async def schedule_publish(self, context: PublishingContext) -> bool:
        return True

    async def publish_draft(self, context: PublishingContext, video_id: str) -> bool:
        return True

    async def get_video_status(self, context: PublishingContext, video_id: str) -> dict:
        return {
            "video_id": video_id,
            "status": "ready",
            "processing_percent": 100,
        }

    async def add_to_playlist(
        self, context: PublishingContext, video_id: str, playlist_id: str
    ) -> bool:
        return True

    async def generate_captions(self, context: PublishingContext, video_id: str) -> bool:
        return True

    async def publish(self, context: PublishingContext) -> PublishingResult:
        response = await self.upload_video(context)
        return PublishingResult(
            task_id="",
            job_id=context.job_id,
            platform=PlatformType.CUSTOM,
            status=PublishingStatus.PUBLISHED,
            is_success=response.is_success,
            error_message=response.error_message,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
        )


class YouTubeProvider(PublishingProvider):
    """YouTube provider (reference implementation with declared capabilities)"""

    @property
    def provider_name(self) -> str:
        return "youtube"

    @property
    def capabilities(self) -> PublishCapability:
        return PublishCapability(
            provider_name="youtube",
            platform=PlatformType.YOUTUBE,
            supports_upload=True,
            supports_scheduling=True,
            supports_thumbnails=True,
            supports_playlists=True,
            supports_auto_captions=True,
            supports_auto_translation=True,
            supports_premiere=True,
            supports_live=False,  # Separate service
            supports_shorts=False,  # YouTube Shorts separate
            supports_monetization=True,
            supports_analytics=True,
            supports_comments=True,
            supports_embedding=True,
            supports_privacy_levels=("public", "unlisted", "private"),
            supported_codecs=("h264", "h265", "vp9", "av1"),
            supported_resolutions=(
                "4320p",
                "2160p",
                "1440p",
                "1080p",
                "720p",
                "480p",
                "360p",
                "240p",
            ),
            supported_aspect_ratios=("16:9",),
            max_upload_size_mb=256000,
            max_duration_seconds=12 * 60 * 60,
            requires_authentication=True,
            authentication_type="oauth2",
            rate_limit_requests_per_hour=10000,
            concurrent_uploads_supported=1,
        )

    async def is_available(self) -> bool:
        # In Phase 2, this is a stub; Phase 3+ will implement API calls
        return True

    async def authenticate(self, context: PublishingContext) -> bool:
        # Stub: In Phase 3+, implement OAuth2 flow
        return context.platform_account is not None

    async def validate_credentials(self, context: PublishingContext) -> bool:
        # Stub: In Phase 3+, validate OAuth token
        return context.platform_account is not None and context.platform_account.is_verified

    async def upload_video(self, context: PublishingContext) -> UploadResponse:
        # Stub: In Phase 3+, implement YouTube API call
        return UploadResponse(
            is_success=True,
            platform_video_id="youtube_stub",
            platform_url="https://youtube.com/watch?v=stub",
        )

    async def upload_thumbnail(self, context: PublishingContext) -> bool:
        # Stub: In Phase 3+, implement YouTube API call
        return True

    async def set_metadata(self, context: PublishingContext) -> bool:
        # Stub: In Phase 3+, implement YouTube API call
        return True

    async def set_privacy(self, context: PublishingContext, privacy_level: str) -> bool:
        # Stub: In Phase 3+, implement YouTube API call
        return True

    async def schedule_publish(self, context: PublishingContext) -> bool:
        # Stub: In Phase 3+, implement YouTube API call
        return True

    async def publish_draft(self, context: PublishingContext, video_id: str) -> bool:
        # Stub: In Phase 3+, implement YouTube API call
        return True

    async def get_video_status(self, context: PublishingContext, video_id: str) -> dict:
        # Stub: In Phase 3+, implement YouTube API call
        return {"status": "processing", "processing_percent": 0}

    async def add_to_playlist(
        self, context: PublishingContext, video_id: str, playlist_id: str
    ) -> bool:
        # Stub: In Phase 3+, implement YouTube API call
        return True

    async def generate_captions(self, context: PublishingContext, video_id: str) -> bool:
        # Stub: In Phase 3+, implement YouTube API call
        return True

    async def publish(self, context: PublishingContext) -> PublishingResult:
        # Stub implementation
        return PublishingResult(
            job_id=context.job_id,
            platform=PlatformType.YOUTUBE,
            status=PublishingStatus.PENDING,
            is_success=False,
            error_message="YouTube provider Phase 3+ implementation required",
        )


class TikTokProvider(PublishingProvider):
    """TikTok provider (reference implementation)"""

    @property
    def provider_name(self) -> str:
        return "tiktok"

    @property
    def capabilities(self) -> PublishCapability:
        return PublishCapability(
            provider_name="tiktok",
            platform=PlatformType.TIKTOK,
            supports_upload=True,
            supports_scheduling=True,
            supports_thumbnails=False,  # Auto-generated
            supports_playlists=False,
            supports_auto_captions=True,
            supports_auto_translation=False,
            supports_premiere=False,
            supports_live=False,
            supports_shorts=True,
            supports_monetization=True,
            supports_analytics=True,
            supports_comments=True,
            supports_embedding=False,
            supports_privacy_levels=("public",),
            supported_codecs=("h264", "h265"),
            supported_resolutions=("1080p", "720p", "480p"),
            supported_aspect_ratios=("9:16", "16:9", "1:1"),
            max_upload_size_mb=287,
            max_duration_seconds=10 * 60,
            requires_authentication=True,
            authentication_type="oauth2",
            rate_limit_requests_per_hour=3600,
            concurrent_uploads_supported=1,
        )

    async def is_available(self) -> bool:
        return True

    async def authenticate(self, context: PublishingContext) -> bool:
        return context.platform_account is not None

    async def validate_credentials(self, context: PublishingContext) -> bool:
        return context.platform_account is not None and context.platform_account.is_verified

    async def upload_video(self, context: PublishingContext) -> UploadResponse:
        return UploadResponse(is_success=True, platform_video_id="tiktok_stub")

    async def upload_thumbnail(self, context: PublishingContext) -> bool:
        return False  # TikTok doesn't support custom thumbnails

    async def set_metadata(self, context: PublishingContext) -> bool:
        return True

    async def set_privacy(self, context: PublishingContext, privacy_level: str) -> bool:
        return privacy_level == "public"

    async def schedule_publish(self, context: PublishingContext) -> bool:
        return True

    async def publish_draft(self, context: PublishingContext, video_id: str) -> bool:
        return True

    async def get_video_status(self, context: PublishingContext, video_id: str) -> dict:
        return {"status": "processing"}

    async def add_to_playlist(
        self, context: PublishingContext, video_id: str, playlist_id: str
    ) -> bool:
        return False

    async def generate_captions(self, context: PublishingContext, video_id: str) -> bool:
        return True

    async def publish(self, context: PublishingContext) -> PublishingResult:
        return PublishingResult(
            job_id=context.job_id,
            platform=PlatformType.TIKTOK,
            status=PublishingStatus.PENDING,
            is_success=False,
            error_message="TikTok provider Phase 3+ implementation required",
        )


class InstagramProvider(PublishingProvider):
    """Instagram provider (reference implementation)"""

    @property
    def provider_name(self) -> str:
        return "instagram"

    @property
    def capabilities(self) -> PublishCapability:
        return PublishCapability(
            provider_name="instagram",
            platform=PlatformType.INSTAGRAM_REEL,
            supports_upload=True,
            supports_scheduling=True,
            supports_thumbnails=True,
            supports_playlists=False,
            supports_auto_captions=True,
            supports_auto_translation=False,
            supports_premiere=False,
            supports_live=False,
            supports_shorts=True,
            supports_monetization=True,
            supports_analytics=True,
            supports_comments=True,
            supports_embedding=False,
            supports_privacy_levels=("public", "private"),
            supported_codecs=("h264", "h265"),
            supported_resolutions=("1080p", "720p", "480p"),
            supported_aspect_ratios=("9:16", "1:1", "4:5"),
            max_upload_size_mb=100,
            max_duration_seconds=90,
            requires_authentication=True,
            authentication_type="oauth2",
            rate_limit_requests_per_hour=200,
            concurrent_uploads_supported=1,
        )

    async def is_available(self) -> bool:
        return True

    async def authenticate(self, context: PublishingContext) -> bool:
        return context.platform_account is not None

    async def validate_credentials(self, context: PublishingContext) -> bool:
        return context.platform_account is not None and context.platform_account.is_verified

    async def upload_video(self, context: PublishingContext) -> UploadResponse:
        return UploadResponse(is_success=True, platform_video_id="instagram_stub")

    async def upload_thumbnail(self, context: PublishingContext) -> bool:
        return True

    async def set_metadata(self, context: PublishingContext) -> bool:
        return True

    async def set_privacy(self, context: PublishingContext, privacy_level: str) -> bool:
        return privacy_level in ("public", "private")

    async def schedule_publish(self, context: PublishingContext) -> bool:
        return True

    async def publish_draft(self, context: PublishingContext, video_id: str) -> bool:
        return True

    async def get_video_status(self, context: PublishingContext, video_id: str) -> dict:
        return {"status": "ready"}

    async def add_to_playlist(
        self, context: PublishingContext, video_id: str, playlist_id: str
    ) -> bool:
        return False

    async def generate_captions(self, context: PublishingContext, video_id: str) -> bool:
        return True

    async def publish(self, context: PublishingContext) -> PublishingResult:
        return PublishingResult(
            job_id=context.job_id,
            platform=PlatformType.INSTAGRAM_REEL,
            status=PublishingStatus.PENDING,
            is_success=False,
            error_message="Instagram provider Phase 3+ implementation required",
        )


class LinkedInProvider(PublishingProvider):
    """LinkedIn provider (reference implementation)"""

    @property
    def provider_name(self) -> str:
        return "linkedin"

    @property
    def capabilities(self) -> PublishCapability:
        return PublishCapability(
            provider_name="linkedin",
            platform=PlatformType.LINKEDIN,
            supports_upload=True,
            supports_scheduling=True,
            supports_thumbnails=False,
            supports_playlists=False,
            supports_auto_captions=False,
            supports_auto_translation=False,
            supports_premiere=False,
            supports_live=False,
            supports_shorts=False,
            supports_monetization=False,
            supports_analytics=True,
            supports_comments=True,
            supports_embedding=False,
            supports_privacy_levels=("public", "private"),
            supported_codecs=("h264",),
            supported_resolutions=("1080p", "720p"),
            supported_aspect_ratios=("16:9", "1:1", "9:16"),
            max_upload_size_mb=200,
            max_duration_seconds=10 * 60,
            requires_authentication=True,
            authentication_type="oauth2",
            rate_limit_requests_per_hour=500,
            concurrent_uploads_supported=1,
        )

    async def is_available(self) -> bool:
        return True

    async def authenticate(self, context: PublishingContext) -> bool:
        return context.platform_account is not None

    async def validate_credentials(self, context: PublishingContext) -> bool:
        return context.platform_account is not None and context.platform_account.is_verified

    async def upload_video(self, context: PublishingContext) -> UploadResponse:
        return UploadResponse(is_success=True, platform_video_id="linkedin_stub")

    async def upload_thumbnail(self, context: PublishingContext) -> bool:
        return False

    async def set_metadata(self, context: PublishingContext) -> bool:
        return True

    async def set_privacy(self, context: PublishingContext, privacy_level: str) -> bool:
        return privacy_level in ("public", "private")

    async def schedule_publish(self, context: PublishingContext) -> bool:
        return True

    async def publish_draft(self, context: PublishingContext, video_id: str) -> bool:
        return True

    async def get_video_status(self, context: PublishingContext, video_id: str) -> dict:
        return {"status": "published"}

    async def add_to_playlist(
        self, context: PublishingContext, video_id: str, playlist_id: str
    ) -> bool:
        return False

    async def generate_captions(self, context: PublishingContext, video_id: str) -> bool:
        return False

    async def publish(self, context: PublishingContext) -> PublishingResult:
        return PublishingResult(
            job_id=context.job_id,
            platform=PlatformType.LINKEDIN,
            status=PublishingStatus.PENDING,
            is_success=False,
            error_message="LinkedIn provider Phase 3+ implementation required",
        )


class PodcastProvider(PublishingProvider):
    """Podcast provider (reference implementation)"""

    @property
    def provider_name(self) -> str:
        return "podcast"

    @property
    def capabilities(self) -> PublishCapability:
        return PublishCapability(
            provider_name="podcast",
            platform=PlatformType.PODCAST,
            supports_upload=True,
            supports_scheduling=True,
            supports_thumbnails=True,
            supports_playlists=True,
            supports_auto_captions=False,
            supports_auto_translation=False,
            supports_premiere=False,
            supports_live=False,
            supports_shorts=False,
            supports_monetization=True,
            supports_analytics=True,
            supports_comments=False,
            supports_embedding=False,
            supports_privacy_levels=("public",),
            supported_codecs=("aac", "mp3", "opus"),
            supported_resolutions=(),  # Audio-only
            supported_aspect_ratios=(),
            max_upload_size_mb=5000,
            max_duration_seconds=12 * 60 * 60,
            requires_authentication=True,
            authentication_type="api_key",
            rate_limit_requests_per_hour=1000,
            concurrent_uploads_supported=2,
        )

    async def is_available(self) -> bool:
        return True

    async def authenticate(self, context: PublishingContext) -> bool:
        return context.platform_account is not None

    async def validate_credentials(self, context: PublishingContext) -> bool:
        return context.platform_account is not None and context.platform_account.is_verified

    async def upload_video(self, context: PublishingContext) -> UploadResponse:
        return UploadResponse(is_success=True, platform_video_id="podcast_stub")

    async def upload_thumbnail(self, context: PublishingContext) -> bool:
        return True

    async def set_metadata(self, context: PublishingContext) -> bool:
        return True

    async def set_privacy(self, context: PublishingContext, privacy_level: str) -> bool:
        return privacy_level == "public"

    async def schedule_publish(self, context: PublishingContext) -> bool:
        return True

    async def publish_draft(self, context: PublishingContext, video_id: str) -> bool:
        return True

    async def get_video_status(self, context: PublishingContext, video_id: str) -> dict:
        return {"status": "live"}

    async def add_to_playlist(
        self, context: PublishingContext, video_id: str, playlist_id: str
    ) -> bool:
        return True

    async def generate_captions(self, context: PublishingContext, video_id: str) -> bool:
        return False

    async def publish(self, context: PublishingContext) -> PublishingResult:
        return PublishingResult(
            job_id=context.job_id,
            platform=PlatformType.PODCAST,
            status=PublishingStatus.PENDING,
            is_success=False,
            error_message="Podcast provider Phase 3+ implementation required",
        )


def create_default_provider_registry() -> ProviderRegistry:
    """Create registry with built-in providers"""
    registry = ProviderRegistry()
    registry.register("mock", MockPublishingProvider())
    registry.register("youtube", YouTubeProvider())
    registry.register("tiktok", TikTokProvider())
    registry.register("instagram", InstagramProvider())
    registry.register("linkedin", LinkedInProvider())
    registry.register("podcast", PodcastProvider())
    return registry
