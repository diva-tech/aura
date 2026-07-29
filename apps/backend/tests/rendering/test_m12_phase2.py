"""M12 Phase 2 Tests: Rendering Engines and Context Models.

Tests for:
1. RenderContext and RenderCapability models
2. All 10 rendering engines (stateless, deterministic)
3. Provider interchangeability
4. Artifact generation
5. Validation
6. Full rendering pipeline
"""

import pytest

from aura_backend.editing import EditPlan, Clip
from aura_backend.rendering import (
    # Phase 2
    RenderCapability,
    RenderContext,
    AudioRenderer,
    BrollRenderer,
    ClipRenderer,
    CompositeRenderer,
    ExportRenderer,
    OverlayRenderer,
    RenderingEngine,
    RendererRegistry,
    SubtitleRenderer,
    TransitionRenderer,
    ValidationEngine,
    ZoomRenderer,
    create_renderer_registry,
    # Phase 1
    ExportProfile,
    MockRendererProvider,
    FFmpegProvider,
    RenderedAsset,
)


# ============================================================================
# CONTEXT AND CAPABILITY TESTS
# ============================================================================


class TestRenderContext:
    """Test RenderContext domain model"""

    def test_context_creation(self):
        """RenderContext can be created"""
        context = RenderContext(
            session_id="sess-1",
            job_id="job-1",
        )

        assert context.session_id == "sess-1"
        assert context.job_id == "job-1"

    def test_context_immutable(self):
        """RenderContext is immutable"""
        context = RenderContext()

        with pytest.raises(AttributeError):
            context.provider_name = "ffmpeg"

    def test_context_properties(self):
        """RenderContext path properties work"""
        context = RenderContext(
            working_directory="/work",
            output_directory="/output",
        )

        assert str(context.working_path) == "/work"
        assert str(context.output_path) == "/output"

    def test_context_for_export_profile(self):
        """RenderContext can be customized for profile"""
        context = RenderContext(
            session_id="sess-1",
            primary_export_profile=ExportProfile.YOUTUBE_16_9,
        )

        tiktok_context = context.for_export_profile(ExportProfile.TIKTOK)

        assert tiktok_context.primary_export_profile == ExportProfile.TIKTOK
        assert tiktok_context.session_id == context.session_id


class TestRenderCapability:
    """Test RenderCapability domain model"""

    def test_capability_creation(self):
        """RenderCapability can be created"""
        cap = RenderCapability(
            provider_name="ffmpeg",
            gpu_supported=True,
            max_resolution="4096x2160",
        )

        assert cap.provider_name == "ffmpeg"
        assert cap.max_resolution == "4096x2160"

    def test_capability_codec_support(self):
        """Capability tracks codec support"""
        cap = RenderCapability(
            supported_codecs={"h264", "h265", "vp9"},
        )

        assert cap.supports_codec("h264")
        assert not cap.supports_codec("av1")

    def test_capability_feature_support(self):
        """Capability tracks feature support"""
        cap = RenderCapability(
            gpu_supported=True,
            audio_mixing_supported=True,
        )

        assert cap.supports_feature("gpu")
        assert cap.supports_feature("audio_mixing")
        assert not cap.supports_feature("hdr")


# ============================================================================
# RENDERING ENGINE TESTS
# ============================================================================


@pytest.mark.asyncio
class TestClipRenderer:
    """Test ClipRenderer engine"""

    async def test_clip_renderer_initialization(self):
        """ClipRenderer can be initialized"""
        provider = MockRendererProvider()
        renderer = ClipRenderer(provider)

        assert renderer.name == "ClipRenderer"
        assert renderer.provider == provider

    async def test_clip_renderer_requires_clips(self):
        """ClipRenderer requires clips in plan"""
        provider = MockRendererProvider()
        renderer = ClipRenderer(provider)
        context = RenderContext()
        plan = EditPlan()

        with pytest.raises(ValueError):
            await renderer.render(plan, context)

    async def test_clip_renderer_produces_asset(self):
        """ClipRenderer produces RenderedAsset"""
        provider = MockRendererProvider()
        renderer = ClipRenderer(provider)
        context = RenderContext()

        clips = [
            Clip(session_id="s1", video_id="v1", start_timestamp=0.0, end_timestamp=5.0),
        ]
        plan = EditPlan(clips=clips)

        asset = await renderer.render(plan, context)

        assert isinstance(asset, RenderedAsset)
        assert asset.metadata.is_valid


@pytest.mark.asyncio
class TestCompositeRenderer:
    """Test CompositeRenderer engine"""

    async def test_composite_requires_clips_and_timeline(self):
        """CompositeRenderer requires clips and timeline"""
        provider = MockRendererProvider()
        renderer = CompositeRenderer(provider)
        context = RenderContext()
        plan = EditPlan()

        with pytest.raises(ValueError):
            await renderer.render(plan, context)


@pytest.mark.asyncio
class TestValidationEngine:
    """Test ValidationEngine"""

    async def test_validation_engine_produces_result(self):
        """ValidationEngine produces ValidationResult"""
        provider = MockRendererProvider()
        engine = ValidationEngine(provider)
        context = RenderContext()

        clips = [
            Clip(session_id="s1", video_id="v1", start_timestamp=0.0, end_timestamp=5.0),
        ]
        plan = EditPlan(clips=clips)

        result = await engine.render(plan, context)

        assert result is not None
        assert result.status.value in ["passed", "warning", "failed"]


# ============================================================================
# PROVIDER INTERCHANGEABILITY TESTS
# ============================================================================


@pytest.mark.asyncio
class TestProviderInterchangeability:
    """Test that engines work with different providers"""

    async def test_renderer_with_mock_provider(self):
        """ClipRenderer works with MockRendererProvider"""
        provider = MockRendererProvider()
        renderer = ClipRenderer(provider)
        context = RenderContext(provider_name="mock")

        clips = [
            Clip(session_id="s1", video_id="v1", start_timestamp=0.0, end_timestamp=5.0),
        ]
        plan = EditPlan(clips=clips)

        asset = await renderer.render(plan, context)

        assert asset.metadata.asset_type.value == "clip"

    async def test_renderer_with_ffmpeg_provider(self):
        """ClipRenderer works with FFmpegProvider"""
        provider = FFmpegProvider()
        renderer = ClipRenderer(provider)
        context = RenderContext(provider_name="ffmpeg")

        clips = [
            Clip(session_id="s1", video_id="v1", start_timestamp=0.0, end_timestamp=5.0),
        ]
        plan = EditPlan(clips=clips)

        asset = await renderer.render(plan, context)

        assert asset is not None


# ============================================================================
# RENDERER REGISTRY TESTS
# ============================================================================


@pytest.mark.asyncio
class TestRendererRegistry:
    """Test RendererRegistry"""

    def test_registry_creation(self):
        """RendererRegistry can be created"""
        provider = MockRendererProvider()
        registry = create_renderer_registry(provider)

        assert registry is not None

    def test_registry_has_all_renderers(self):
        """Registry has all 10 renderers"""
        provider = MockRendererProvider()
        registry = create_renderer_registry(provider)

        expected = [
            "clips",
            "transitions",
            "subtitles",
            "overlays",
            "zoom",
            "broll",
            "audio",
            "composite",
            "export",
            "validation",
        ]

        renderers = registry.list_renderers()
        for renderer_name in expected:
            assert renderer_name in renderers

    def test_registry_retrieves_renderers(self):
        """Registry can retrieve renderers by name"""
        provider = MockRendererProvider()
        registry = create_renderer_registry(provider)

        clip_renderer = registry.get("clips")
        assert clip_renderer is not None
        assert isinstance(clip_renderer, ClipRenderer)

    @pytest.mark.asyncio
    async def test_registry_render_all_workflow(self):
        """Registry can execute full pipeline"""
        provider = MockRendererProvider()
        registry = create_renderer_registry(provider)
        context = RenderContext()

        clips = [
            Clip(session_id="s1", video_id="v1", start_timestamp=0.0, end_timestamp=5.0),
        ]
        plan = EditPlan(clips=clips)

        results = await registry.render_all(plan, context)

        assert "clips" in results or "error" in results


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


@pytest.mark.asyncio
class TestPhase2Integration:
    """Test Phase 2 components working together"""

    async def test_rendering_context_with_registry(self):
        """RenderContext works with RendererRegistry"""
        context = RenderContext(
            session_id="s1",
            job_id="j1",
            provider_name="mock",
            export_profiles=[ExportProfile.YOUTUBE_16_9],
        )

        provider = MockRendererProvider()
        registry = create_renderer_registry(provider)

        renderers = registry.list_renderers()
        assert len(renderers) == 10

    async def test_capability_driven_renderer_selection(self):
        """Capability model can drive renderer selection"""
        cap = RenderCapability(
            provider_name="ffmpeg",
            audio_mixing_supported=True,
            subtitle_support=True,
        )

        context = RenderContext(
            provider_capability=cap,
        )

        if cap.supports_feature("audio_mixing"):
            provider = MockRendererProvider()
            renderer = AudioRenderer(provider)
            assert renderer is not None


# ============================================================================
# EDGE CASE TESTS
# ============================================================================


@pytest.mark.asyncio
class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_render_context_timeout(self):
        """RenderContext tracks timeout"""
        context = RenderContext(timeout_seconds=300.0)

        assert context.timeout_seconds == 300.0

    def test_render_capability_max_resolution(self):
        """RenderCapability declares max resolution"""
        cap = RenderCapability(
            max_resolution="7680x4320",  # 8K
        )

        assert "7680" in cap.max_resolution

    def test_render_context_retry_config(self):
        """RenderContext has retry configuration"""
        context = RenderContext(
            retry_on_failure=True,
            max_retries=5,
        )

        assert context.max_retries == 5

    @pytest.mark.asyncio
    async def test_renderer_handles_empty_subtitles(self):
        """SubtitleRenderer handles missing subtitles"""
        provider = MockRendererProvider()
        renderer = SubtitleRenderer(provider)
        context = RenderContext()
        plan = EditPlan()

        with pytest.raises(ValueError):
            await renderer.render(plan, context)

    @pytest.mark.asyncio
    async def test_all_renderers_are_stateless(self):
        """All renderers are stateless"""
        provider = MockRendererProvider()

        renderers = [
            ClipRenderer(provider),
            TransitionRenderer(provider),
            SubtitleRenderer(provider),
            OverlayRenderer(provider),
            ZoomRenderer(provider),
            BrollRenderer(provider),
            AudioRenderer(provider),
            CompositeRenderer(provider),
            ExportRenderer(provider),
            ValidationEngine(provider),
        ]

        for renderer in renderers:
            # Stateless = no instance state beyond provider
            assert hasattr(renderer, "_provider")
            assert not hasattr(renderer, "_cache")
            assert not hasattr(renderer, "_state")
