"""M13 Phase 2 Tests: Publishing Providers.

Tests for context models, capabilities, provider interface, and implementations.
"""

from datetime import datetime, timedelta

import pytest

from aura_backend.publishing import (  # Phase 2; Phase 1
    YOUTUBE_PROFILE,
    InstagramProvider,
    LinkedInProvider,
    MockPublishingProvider,
    PlatformAccount,
    PlatformType,
    PodcastProvider,
    ProviderRegistry,
    PublishCapability,
    PublishingContext,
    PublishingJob,
    ScheduledPublish,
    TikTokProvider,
    UploadResponse,
    YouTubeProvider,
    create_default_provider_registry,
)

# ============================================================================
# CONTEXT & CAPABILITY TESTS
# ============================================================================


class TestPublishCapability:
    """Test PublishCapability"""

    def test_create_capability(self):
        """Create capability"""
        cap = PublishCapability(
            provider_name="youtube",
            platform=PlatformType.YOUTUBE,
            supports_upload=True,
            supports_scheduling=True,
        )

        assert cap.provider_name == "youtube"
        assert cap.supports_upload is True

    def test_capability_feature_support(self):
        """Check feature support"""
        cap = PublishCapability(
            supports_upload=True,
            supports_scheduling=True,
            supports_monetization=False,
        )

        assert cap.supports_feature("upload") is True
        assert cap.supports_feature("scheduling") is True
        assert cap.supports_feature("monetization") is False
        assert cap.supports_feature("unknown") is False

    def test_capability_codec_support(self):
        """Check codec support"""
        cap = PublishCapability(
            supported_codecs=("h264", "h265", "vp9"),
        )

        assert cap.supports_codec("h264") is True
        assert cap.supports_codec("h265") is True
        assert cap.supports_codec("av1") is False

    def test_capability_resolution_support(self):
        """Check resolution support"""
        cap = PublishCapability(
            supported_resolutions=("1080p", "720p", "480p"),
        )

        assert cap.supports_resolution("1080p") is True
        assert cap.supports_resolution("4320p") is False

    def test_capability_aspect_ratio_support(self):
        """Check aspect ratio support"""
        cap = PublishCapability(
            supported_aspect_ratios=("16:9", "9:16"),
        )

        assert cap.supports_aspect_ratio("16:9") is True
        assert cap.supports_aspect_ratio("1:1") is False

    def test_capability_immutable(self):
        """Capability is immutable"""
        cap = PublishCapability()

        with pytest.raises(AttributeError):
            cap.provider_name = "new"


class TestPublishingContext:
    """Test PublishingContext"""

    def test_create_context(self):
        """Create context"""
        account = PlatformAccount(
            platform=PlatformType.YOUTUBE,
            account_name="test",
        )
        context = PublishingContext(
            job_id="job-1",
            artifact_bundle_id="bundle-1",
            platform_account=account,
        )

        assert context.job_id == "job-1"
        assert context.platform_account is not None

    def test_context_with_profile_and_schedule(self):
        """Context with profile and schedule"""
        publish_time = datetime.utcnow() + timedelta(hours=1)
        schedule = ScheduledPublish(publish_at=publish_time)

        context = PublishingContext(
            job_id="job-1",
            publishing_profile=YOUTUBE_PROFILE,
            publishing_schedule=schedule,
        )

        assert context.publishing_profile is not None
        assert context.publishing_schedule is not None

    def test_context_immutable(self):
        """Context is immutable"""
        context = PublishingContext()

        with pytest.raises(AttributeError):
            context.job_id = "new-job"

    def test_context_serialization(self):
        """Context serialization"""
        context = PublishingContext(
            job_id="job-1",
            is_draft=True,
        )
        d = context.to_dict()

        assert d["job_id"] == "job-1"
        assert d["is_draft"] is True


# ============================================================================
# PROVIDER INTERFACE TESTS
# ============================================================================


class TestProviderInterface:
    """Test provider interface compliance"""

    @pytest.mark.asyncio
    async def test_mock_provider_interface(self):
        """Mock provider implements interface"""
        provider = MockPublishingProvider()

        assert provider.provider_name == "mock"
        assert provider.capabilities is not None
        assert await provider.is_available() is True

    @pytest.mark.asyncio
    async def test_youtube_provider_interface(self):
        """YouTube provider implements interface"""
        provider = YouTubeProvider()

        assert provider.provider_name == "youtube"
        assert provider.capabilities.platform == PlatformType.YOUTUBE
        assert await provider.is_available() is True

    @pytest.mark.asyncio
    async def test_tiktok_provider_interface(self):
        """TikTok provider implements interface"""
        provider = TikTokProvider()

        assert provider.provider_name == "tiktok"
        assert provider.capabilities.platform == PlatformType.TIKTOK

    @pytest.mark.asyncio
    async def test_instagram_provider_interface(self):
        """Instagram provider implements interface"""
        provider = InstagramProvider()

        assert provider.provider_name == "instagram"
        assert provider.capabilities.platform == PlatformType.INSTAGRAM_REEL

    @pytest.mark.asyncio
    async def test_linkedin_provider_interface(self):
        """LinkedIn provider implements interface"""
        provider = LinkedInProvider()

        assert provider.provider_name == "linkedin"
        assert provider.capabilities.platform == PlatformType.LINKEDIN

    @pytest.mark.asyncio
    async def test_podcast_provider_interface(self):
        """Podcast provider implements interface"""
        provider = PodcastProvider()

        assert provider.provider_name == "podcast"
        assert provider.capabilities.platform == PlatformType.PODCAST


# ============================================================================
# PROVIDER INTERCHANGEABILITY TESTS
# ============================================================================


class TestProviderInterchangeability:
    """Test provider swappability"""

    @pytest.mark.asyncio
    async def test_providers_same_interface(self):
        """All providers implement same interface"""
        providers = [
            MockPublishingProvider(),
            YouTubeProvider(),
            TikTokProvider(),
            InstagramProvider(),
            LinkedInProvider(),
            PodcastProvider(),
        ]

        for provider in providers:
            # All have these methods
            assert hasattr(provider, "provider_name")
            assert hasattr(provider, "capabilities")
            assert hasattr(provider, "is_available")
            assert hasattr(provider, "authenticate")
            assert hasattr(provider, "upload_video")
            assert hasattr(provider, "set_metadata")
            assert hasattr(provider, "publish")

    @pytest.mark.asyncio
    async def test_provider_swapping(self):
        """Providers can be swapped"""
        providers = {
            "mock": MockPublishingProvider(),
            "youtube": YouTubeProvider(),
            "tiktok": TikTokProvider(),
        }

        for name, provider in providers.items():
            assert provider.provider_name == name
            # All support same core methods
            assert await provider.is_available()


# ============================================================================
# AUTHENTICATION TESTS
# ============================================================================


class TestAuthentication:
    """Test authentication flow"""

    @pytest.mark.asyncio
    async def test_mock_authentication(self):
        """Mock provider authentication"""
        provider = MockPublishingProvider()
        context = PublishingContext(job_id="job-1")

        result = await provider.authenticate(context)
        assert result is True

    @pytest.mark.asyncio
    async def test_youtube_authentication_requires_account(self):
        """YouTube requires account"""
        provider = YouTubeProvider()
        context = PublishingContext(job_id="job-1", platform_account=None)

        result = await provider.authenticate(context)
        assert result is False

    @pytest.mark.asyncio
    async def test_youtube_authentication_with_account(self):
        """YouTube authentication with account"""
        provider = YouTubeProvider()
        account = PlatformAccount(platform=PlatformType.YOUTUBE)
        context = PublishingContext(job_id="job-1", platform_account=account)

        result = await provider.authenticate(context)
        assert result is True

    @pytest.mark.asyncio
    async def test_credential_validation(self):
        """Validate credentials"""
        provider = YouTubeProvider()
        account = PlatformAccount(
            platform=PlatformType.YOUTUBE,
            is_verified=True,
        )
        context = PublishingContext(job_id="job-1", platform_account=account)

        result = await provider.validate_credentials(context)
        assert result is True


# ============================================================================
# UPLOAD FLOW TESTS
# ============================================================================


class TestUploadFlow:
    """Test upload flow"""

    @pytest.mark.asyncio
    async def test_mock_upload(self):
        """Mock upload succeeds"""
        provider = MockPublishingProvider()
        context = PublishingContext(job_id="job-1")

        response = await provider.upload_video(context)

        assert response.is_success is True
        assert response.platform_video_id is not None
        assert response.error_message == ""

    @pytest.mark.asyncio
    async def test_upload_response_immutable(self):
        """UploadResponse is immutable"""
        response = UploadResponse()

        with pytest.raises(AttributeError):
            response.platform_video_id = "new_id"

    @pytest.mark.asyncio
    async def test_metadata_setting(self):
        """Set metadata"""
        provider = MockPublishingProvider()
        context = PublishingContext(job_id="job-1")

        result = await provider.set_metadata(context)
        assert result is True

    @pytest.mark.asyncio
    async def test_thumbnail_upload(self):
        """Upload thumbnail"""
        provider = MockPublishingProvider()
        context = PublishingContext(job_id="job-1")

        result = await provider.upload_thumbnail(context)
        assert result is True

    @pytest.mark.asyncio
    async def test_tiktok_no_custom_thumbnail(self):
        """TikTok doesn't support custom thumbnails"""
        provider = TikTokProvider()
        context = PublishingContext(job_id="job-1")

        result = await provider.upload_thumbnail(context)
        assert result is False


# ============================================================================
# SCHEDULING TESTS
# ============================================================================


class TestScheduling:
    """Test scheduling support"""

    @pytest.mark.asyncio
    async def test_youtube_scheduling(self):
        """YouTube supports scheduling"""
        provider = YouTubeProvider()
        context = PublishingContext(job_id="job-1")

        result = await provider.schedule_publish(context)
        assert result is True

    @pytest.mark.asyncio
    async def test_tiktok_scheduling(self):
        """TikTok supports scheduling"""
        provider = TikTokProvider()
        context = PublishingContext(job_id="job-1")

        result = await provider.schedule_publish(context)
        assert result is True

    @pytest.mark.asyncio
    async def test_instagram_scheduling(self):
        """Instagram supports scheduling"""
        provider = InstagramProvider()
        context = PublishingContext(job_id="job-1")

        result = await provider.schedule_publish(context)
        assert result is True


# ============================================================================
# METADATA HANDLING TESTS
# ============================================================================


class TestMetadataHandling:
    """Test metadata handling"""

    @pytest.mark.asyncio
    async def test_set_metadata(self):
        """Set metadata on video"""
        providers = [
            YouTubeProvider(),
            TikTokProvider(),
            InstagramProvider(),
        ]

        context = PublishingContext(job_id="job-1")

        for provider in providers:
            result = await provider.set_metadata(context)
            assert result is True

    @pytest.mark.asyncio
    async def test_privacy_levels(self):
        """Handle privacy levels"""
        provider = YouTubeProvider()

        # YouTube supports these
        assert await provider.set_privacy(PublishingContext(job_id="job-1"), "public") is True
        assert await provider.set_privacy(PublishingContext(job_id="job-1"), "private") is True

    @pytest.mark.asyncio
    async def test_tiktok_privacy_public_only(self):
        """TikTok only supports public"""
        provider = TikTokProvider()

        # TikTok public only
        assert await provider.set_privacy(PublishingContext(job_id="job-1"), "public") is True
        assert await provider.set_privacy(PublishingContext(job_id="job-1"), "private") is False


# ============================================================================
# CAPABILITY NEGOTIATION TESTS
# ============================================================================


class TestCapabilityNegotiation:
    """Test capability negotiation"""

    def test_youtube_capabilities(self):
        """YouTube capabilities"""
        provider = YouTubeProvider()
        cap = provider.capabilities

        assert cap.supports_feature("upload") is True
        assert cap.supports_feature("scheduling") is True
        assert cap.supports_feature("monetization") is True
        assert cap.supports_feature("shorts") is False  # YouTube Shorts separate

    def test_tiktok_capabilities(self):
        """TikTok capabilities"""
        provider = TikTokProvider()
        cap = provider.capabilities

        assert cap.supports_feature("shorts") is True
        assert cap.supports_feature("monetization") is True
        assert cap.supports_feature("playlists") is False

    def test_instagram_capabilities(self):
        """Instagram capabilities"""
        provider = InstagramProvider()
        cap = provider.capabilities

        assert cap.max_duration_seconds == 90  # Instagram Reel limit
        assert cap.supports_feature("scheduling") is True

    def test_linkedin_capabilities(self):
        """LinkedIn capabilities"""
        provider = LinkedInProvider()
        cap = provider.capabilities

        assert cap.supports_feature("monetization") is False
        assert cap.supports_feature("analytics") is True

    def test_podcast_capabilities(self):
        """Podcast capabilities"""
        provider = PodcastProvider()
        cap = provider.capabilities

        assert cap.platform == PlatformType.PODCAST
        assert cap.supports_feature("playlists") is True
        assert cap.supported_codecs == ("aac", "mp3", "opus")


# ============================================================================
# FAILURE HANDLING TESTS
# ============================================================================


class TestFailureHandling:
    """Test failure handling"""

    @pytest.mark.asyncio
    async def test_provider_status_check(self):
        """Check provider availability"""
        provider = MockPublishingProvider()

        # Mock always available
        assert await provider.is_available() is True

    @pytest.mark.asyncio
    async def test_video_status_retrieval(self):
        """Get video processing status"""
        provider = MockPublishingProvider()
        context = PublishingContext(job_id="job-1")

        status = await provider.get_video_status(context, "video-123")

        assert "status" in status
        assert status["status"] is not None

    @pytest.mark.asyncio
    async def test_draft_publishing(self):
        """Publish draft"""
        provider = MockPublishingProvider()
        context = PublishingContext(job_id="job-1")

        result = await provider.publish_draft(context, "video-123")
        assert result is True


# ============================================================================
# PROVIDER REGISTRY TESTS
# ============================================================================


class TestProviderRegistry:
    """Test provider registry"""

    def test_registry_creation(self):
        """Create registry"""
        registry = ProviderRegistry()

        assert registry is not None

    def test_provider_registration(self):
        """Register provider"""
        registry = ProviderRegistry()
        provider = MockPublishingProvider()

        registry.register("mock", provider)

        retrieved = registry.get("mock")
        assert retrieved is not None
        assert retrieved.provider_name == "mock"

    def test_get_by_platform(self):
        """Get provider by platform"""
        registry = ProviderRegistry()
        registry.register("youtube", YouTubeProvider())

        provider = registry.get_by_platform("youtube")

        assert provider is not None
        assert provider.provider_name == "youtube"

    def test_list_providers(self):
        """List all providers"""
        registry = ProviderRegistry()
        registry.register("mock", MockPublishingProvider())
        registry.register("youtube", YouTubeProvider())

        providers = registry.list_providers()

        assert len(providers) == 2
        assert "mock" in providers
        assert "youtube" in providers

    def test_default_registry(self):
        """Create default registry with all providers"""
        registry = create_default_provider_registry()

        assert registry.get("mock") is not None
        assert registry.get("youtube") is not None
        assert registry.get("tiktok") is not None
        assert registry.get("instagram") is not None
        assert registry.get("linkedin") is not None
        assert registry.get("podcast") is not None


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestPhase2Integration:
    """Integration tests for Phase 2 components"""

    @pytest.mark.asyncio
    async def test_full_publish_workflow_mock(self):
        """Full workflow with mock provider"""
        provider = MockPublishingProvider()
        account = PlatformAccount(platform=PlatformType.CUSTOM)
        context = PublishingContext(
            job_id="job-1",
            artifact_bundle_id="bundle-1",
            platform_account=account,
        )

        # Authenticate
        assert await provider.authenticate(context) is True

        # Upload
        response = await provider.upload_video(context)
        assert response.is_success is True

        # Set metadata
        assert await provider.set_metadata(context) is True

        # Publish
        result = await provider.publish(context)
        assert result.job_id == "job-1"

    @pytest.mark.asyncio
    async def test_multi_platform_publishing(self):
        """Test with multiple providers"""
        platforms = {
            "youtube": YouTubeProvider(),
            "tiktok": TikTokProvider(),
            "instagram": InstagramProvider(),
        }

        job = PublishingJob(
            artifact_bundle_id="bundle-1",
            platforms=(
                PlatformType.YOUTUBE,
                PlatformType.TIKTOK,
                PlatformType.INSTAGRAM_REEL,
            ),
        )

        # Verify each platform has matching provider
        for platform_type in job.platforms:
            found = False
            for provider in platforms.values():
                if provider.capabilities.platform == platform_type:
                    found = True
                    break
            assert found, f"No provider for {platform_type}"
