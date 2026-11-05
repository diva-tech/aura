"""M14 Phase 2 Tests: Analytics Providers.

Tests for context models, provider interface, implementations, and registry.
"""

import pytest

from aura_backend.learning import (
    AnalyticsCapability,
    AnalyticsProviderRegistry,
    InstagramAnalyticsProvider,
    LearningContext,
    LearningObjective,
    LinkedInAnalyticsProvider,
    MockAnalyticsProvider,
    PodcastAnalyticsProvider,
    TikTokAnalyticsProvider,
    YouTubeAnalyticsProvider,
    create_default_provider_registry,
)

# ============================================================================
# CONTEXT MODELS TESTS
# ============================================================================


class TestLearningContext:
    """Test learning context model."""

    def test_context_creation(self):
        """Create learning context."""
        context = LearningContext(
            job_id="job-1",
            creator_id="creator-1",
            platform="youtube",
            objectives=(LearningObjective(objective_type="increase_ctr"),),
        )

        assert context.job_id == "job-1"
        assert context.platform == "youtube"

    def test_context_immutable(self):
        """Context is immutable."""
        context = LearningContext()

        with pytest.raises(AttributeError):
            context.job_id = "new-job"

    def test_context_to_dict(self):
        """Serialize context."""
        context = LearningContext(
            job_id="job-1",
            creator_id="creator-1",
        )

        d = context.to_dict()

        assert d["job_id"] == "job-1"


# ============================================================================
# ANALYTICS CAPABILITY TESTS
# ============================================================================


class TestAnalyticsCapability:
    """Test analytics capability model."""

    def test_capability_creation(self):
        """Create capability."""
        cap = AnalyticsCapability(
            provider_name="youtube",
            supports_retention_analysis=True,
            supports_revenue_metrics=True,
            supports_ctr_metrics=True,
        )

        assert cap.provider_name == "youtube"
        assert cap.supports_retention_analysis is True

    def test_capability_supports_feature(self):
        """Check feature support."""
        cap = AnalyticsCapability(
            supports_retention_analysis=True,
            supports_revenue_metrics=False,
        )

        assert cap.supports_feature("retention") is True
        assert cap.supports_feature("revenue") is False

    def test_capability_supports_format(self):
        """Check format support."""
        cap = AnalyticsCapability(
            supported_formats=("json", "csv"),
        )

        assert cap.supports_format("json") is True
        assert cap.supports_format("xml") is False

    def test_capability_supports_platform(self):
        """Check platform support."""
        cap = AnalyticsCapability(
            supported_platforms=("youtube", "tiktok"),
        )

        assert cap.supports_platform("youtube") is True
        assert cap.supports_platform("instagram") is False

    def test_capability_can_negotiate(self):
        """Check capability negotiation."""
        cap = AnalyticsCapability(
            supports_retention_analysis=True,
            supports_revenue_metrics=True,
            supports_ctr_metrics=False,
        )

        assert cap.can_negotiate(("retention", "revenue")) is True
        assert cap.can_negotiate(("retention", "ctr")) is False

    def test_capability_immutable(self):
        """Capability is immutable."""
        cap = AnalyticsCapability()

        with pytest.raises(AttributeError):
            cap.provider_name = "youtube"


# ============================================================================
# PROVIDER INTERFACE TESTS
# ============================================================================


class TestProviderInterface:
    """Test provider interface compliance."""

    @pytest.mark.asyncio
    async def test_mock_provider_availability(self):
        """Mock provider is available."""
        provider = MockAnalyticsProvider()

        available = await provider.is_available()

        assert available is True

    @pytest.mark.asyncio
    async def test_mock_provider_authentication(self):
        """Mock provider authenticates."""
        provider = MockAnalyticsProvider()

        result = await provider.authenticate({})

        assert result.success is True

    @pytest.mark.asyncio
    async def test_youtube_provider_requires_credentials(self):
        """YouTube provider requires credentials."""
        provider = YouTubeAnalyticsProvider()

        result = await provider.authenticate({})

        assert result.success is False

    @pytest.mark.asyncio
    async def test_tiktok_provider_requires_credentials(self):
        """TikTok provider requires credentials."""
        provider = TikTokAnalyticsProvider()

        result = await provider.authenticate({})

        assert result.success is False


# ============================================================================
# METRICS RETRIEVAL TESTS
# ============================================================================


class TestMetricsRetrieval:
    """Test metrics retrieval."""

    @pytest.mark.asyncio
    async def test_mock_get_video_metrics(self):
        """Retrieve metrics from mock provider."""
        provider = MockAnalyticsProvider()
        context = LearningContext(creator_id="creator-1", platform="youtube")

        result = await provider.get_video_metrics(context, "video-1")

        assert result.success is True
        assert result.video_performance is not None
        assert result.video_performance.views == 50000

    @pytest.mark.asyncio
    async def test_youtube_get_video_metrics(self):
        """Retrieve metrics from YouTube provider."""
        provider = YouTubeAnalyticsProvider()
        context = LearningContext(creator_id="creator-1", platform="youtube")

        result = await provider.get_video_metrics(context, "video-1")

        assert result.success is True
        assert result.video_performance.views == 100000

    @pytest.mark.asyncio
    async def test_tiktok_get_video_metrics(self):
        """Retrieve metrics from TikTok provider."""
        provider = TikTokAnalyticsProvider()
        context = LearningContext(creator_id="creator-1", platform="tiktok")

        result = await provider.get_video_metrics(context, "video-1")

        assert result.success is True
        assert result.video_performance.views == 500000

    @pytest.mark.asyncio
    async def test_get_retention_curve(self):
        """Retrieve retention curve."""
        provider = YouTubeAnalyticsProvider()
        context = LearningContext(creator_id="creator-1", platform="youtube")

        curve = await provider.get_retention_curve(context, "video-1")

        assert curve is not None
        assert curve.completion_rate == 85.0

    @pytest.mark.asyncio
    async def test_tiktok_no_retention_curve(self):
        """TikTok provider doesn't support retention."""
        provider = TikTokAnalyticsProvider()
        context = LearningContext(creator_id="creator-1", platform="tiktok")

        curve = await provider.get_retention_curve(context, "video-1")

        assert curve is None


# ============================================================================
# AUDIENCE RETRIEVAL TESTS
# ============================================================================


class TestAudienceRetrieval:
    """Test audience data retrieval."""

    @pytest.mark.asyncio
    async def test_mock_get_audience_data(self):
        """Retrieve audience from mock provider."""
        provider = MockAnalyticsProvider()
        context = LearningContext(creator_id="creator-1")

        result = await provider.get_audience_data(context)

        assert result.success is True
        assert result.audience_profile is not None
        assert result.total_audience_size == 50000

    @pytest.mark.asyncio
    async def test_youtube_get_audience_data(self):
        """Retrieve audience from YouTube provider."""
        provider = YouTubeAnalyticsProvider()
        context = LearningContext(creator_id="creator-1")

        result = await provider.get_audience_data(context)

        assert result.success is True
        assert result.total_audience_size == 100000

    @pytest.mark.asyncio
    async def test_tiktok_get_audience_data(self):
        """Retrieve audience from TikTok provider."""
        provider = TikTokAnalyticsProvider()
        context = LearningContext(creator_id="creator-1")

        result = await provider.get_audience_data(context)

        assert result.success is True
        assert result.total_audience_size == 500000


# ============================================================================
# REVENUE RETRIEVAL TESTS
# ============================================================================


class TestRevenueRetrieval:
    """Test revenue data retrieval."""

    @pytest.mark.asyncio
    async def test_youtube_get_revenue(self):
        """Retrieve revenue from YouTube."""
        provider = YouTubeAnalyticsProvider()
        context = LearningContext(creator_id="creator-1")

        metrics = await provider.get_revenue_data(context, "video-1")

        assert metrics is not None
        assert metrics.revenue == 500.0

    @pytest.mark.asyncio
    async def test_tiktok_get_revenue(self):
        """Retrieve revenue from TikTok."""
        provider = TikTokAnalyticsProvider()
        context = LearningContext(creator_id="creator-1")

        metrics = await provider.get_revenue_data(context, "video-1")

        assert metrics is not None
        assert metrics.rpm == 0.2

    @pytest.mark.asyncio
    async def test_linkedin_no_revenue(self):
        """LinkedIn doesn't support revenue metrics."""
        provider = LinkedInAnalyticsProvider()
        context = LearningContext(creator_id="creator-1")

        metrics = await provider.get_revenue_data(context, "video-1")

        assert metrics is None


# ============================================================================
# CAPABILITY NEGOTIATION TESTS
# ============================================================================


class TestCapabilityNegotiation:
    """Test capability negotiation."""

    def test_mock_has_all_capabilities(self):
        """Mock provider has all capabilities."""
        provider = MockAnalyticsProvider()

        required = (
            "retention",
            "revenue",
            "ctr",
            "segmentation",
        )
        supports = provider.capabilities.can_negotiate(required)

        assert supports is True

    def test_tiktok_missing_retention(self):
        """TikTok doesn't support retention analysis."""
        provider = TikTokAnalyticsProvider()

        requires_retention = provider.capabilities.can_negotiate(("retention",))

        assert requires_retention is False

    def test_linkedin_missing_revenue(self):
        """LinkedIn doesn't support revenue metrics."""
        provider = LinkedInAnalyticsProvider()

        requires_revenue = provider.capabilities.can_negotiate(("revenue",))

        assert requires_revenue is False

    @pytest.mark.asyncio
    async def test_check_capability_support(self):
        """Check capability support via provider method."""
        provider = YouTubeAnalyticsProvider()

        supports_retention = await provider.check_capability_support(("retention",))

        assert supports_retention is True


# ============================================================================
# PROVIDER INTERCHANGEABILITY TESTS
# ============================================================================


class TestProviderInterchangeability:
    """Test provider interchangeability."""

    @pytest.mark.asyncio
    async def test_providers_have_same_interface(self):
        """All providers implement same interface."""
        providers = [
            MockAnalyticsProvider(),
            YouTubeAnalyticsProvider(),
            TikTokAnalyticsProvider(),
            InstagramAnalyticsProvider(),
            LinkedInAnalyticsProvider(),
            PodcastAnalyticsProvider(),
        ]

        for provider in providers:
            assert hasattr(provider, "provider_name")
            assert hasattr(provider, "capabilities")
            assert callable(provider.is_available)
            assert callable(provider.authenticate)
            assert callable(provider.get_video_metrics)
            assert callable(provider.get_audience_data)

    @pytest.mark.asyncio
    async def test_provider_swapping(self):
        """Swap providers without code changes."""
        context = LearningContext(creator_id="creator-1")

        for provider_class in [
            MockAnalyticsProvider,
            YouTubeAnalyticsProvider,
            TikTokAnalyticsProvider,
        ]:
            provider = provider_class()

            result = await provider.get_video_metrics(context, "video-1")

            assert result.success is True


# ============================================================================
# PROVIDER REGISTRY TESTS
# ============================================================================


class TestProviderRegistry:
    """Test provider registry."""

    def test_registry_creation(self):
        """Create registry."""
        registry = AnalyticsProviderRegistry()

        assert registry is not None

    def test_register_provider(self):
        """Register provider."""
        registry = AnalyticsProviderRegistry()
        provider = MockAnalyticsProvider()

        registry.register(provider)

        retrieved = registry.get("mock")

        assert retrieved is not None

    def test_list_providers(self):
        """List registered providers."""
        registry = AnalyticsProviderRegistry()
        registry.register(MockAnalyticsProvider())
        registry.register(YouTubeAnalyticsProvider())

        providers = registry.list_providers()

        assert len(providers) == 2
        assert "mock" in providers
        assert "youtube" in providers

    def test_filter_by_capability(self):
        """Filter providers by capability."""
        registry = AnalyticsProviderRegistry()
        registry.register(MockAnalyticsProvider())
        registry.register(TikTokAnalyticsProvider())
        registry.register(LinkedInAnalyticsProvider())

        providers_with_revenue = registry.filter_by_capability("revenue")

        assert "mock" in providers_with_revenue
        assert "tiktok" in providers_with_revenue
        assert "linkedin" not in providers_with_revenue

    def test_default_registry(self):
        """Create default registry."""
        registry = create_default_provider_registry()

        providers = registry.list_providers()

        assert len(providers) == 6
        assert "mock" in providers
        assert "youtube" in providers
        assert "tiktok" in providers
        assert "instagram" in providers
        assert "linkedin" in providers
        assert "podcast" in providers


# ============================================================================
# FAILURE HANDLING TESTS
# ============================================================================


class TestFailureHandling:
    """Test failure handling."""

    @pytest.mark.asyncio
    async def test_authentication_failure(self):
        """Authentication failure handling."""
        provider = YouTubeAnalyticsProvider()

        result = await provider.authenticate({})

        assert result.success is False
        assert result.error_code == "MISSING_CREDENTIALS"

    @pytest.mark.asyncio
    async def test_credential_validation(self):
        """Validate credentials."""
        provider = YouTubeAnalyticsProvider()

        valid = await provider.validate_credentials({"api_key": "test"})

        assert valid is True

        invalid = await provider.validate_credentials({})

        assert invalid is False

    @pytest.mark.asyncio
    async def test_unsupported_feature(self):
        """Handle unsupported features."""
        provider = TikTokAnalyticsProvider()

        curve = await provider.get_retention_curve(
            LearningContext(creator_id="creator-1"),
            "video-1",
        )

        assert curve is None

    @pytest.mark.asyncio
    async def test_export_format_support(self):
        """Test export format support."""
        provider = TikTokAnalyticsProvider()

        result = await provider.export_metrics(
            LearningContext(creator_id="creator-1"),
            ("video-1",),
            "json",
        )

        assert "error" in result or result.get("status") is not None
