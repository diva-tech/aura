"""M12 Phase 1 Tests: Rendering Domain Models and Provider Interface.

Tests for:
1. Domain models (RenderJob, RenderTask, RenderedAsset, etc.)
2. Provider interface (RendererProvider)
3. Reference implementations (MockRendererProvider, FFmpegProvider)
4. Provider registry
"""

import pytest

from aura_backend.rendering import (
    # Models
    Artifact,
    ArtifactBundle,
    AssetMetadata,
    AssetType,
    ExportProfile,
    RenderedAsset,
    RenderGraph,
    RenderJob,
    RenderJobStatus,
    RenderManifest,
    RenderMetrics,
    RenderResult,
    RenderSegment,
    RenderTask,
    RenderTaskType,
    ValidationResult,
    ValidationStatus,
    # Provider
    ProviderRegistry,
    RendererProvider,
    # Implementations
    FFmpegProvider,
    MockRendererProvider,
    create_default_provider_registry,
)


# ============================================================================
# DOMAIN MODEL TESTS
# ============================================================================


class TestRenderJob:
    """Test RenderJob domain model"""

    def test_render_job_creation(self):
        """RenderJob can be created"""
        job = RenderJob(
            session_id="sess-1",
            video_id="v1",
            edit_plan_id="plan-1",
        )

        assert job.session_id == "sess-1"
        assert job.status == RenderJobStatus.PENDING

    def test_render_job_immutable(self):
        """RenderJob is immutable"""
        job = RenderJob()

        with pytest.raises(AttributeError):
            job.status = RenderJobStatus.RENDERING

    def test_render_job_to_dict(self):
        """RenderJob can serialize to dict"""
        job = RenderJob(
            session_id="sess-1",
            export_profiles=[ExportProfile.YOUTUBE_16_9],
        )

        d = job.to_dict()
        assert d["session_id"] == "sess-1"
        assert len(d["export_profiles"]) == 1


class TestRenderTask:
    """Test RenderTask domain model"""

    def test_render_task_creation(self):
        """RenderTask can be created"""
        task = RenderTask(
            job_id="job-1",
            task_type=RenderTaskType.CLIP_RENDER,
            source_path="/path/to/clip.mp4",
        )

        assert task.job_id == "job-1"
        assert task.task_type == RenderTaskType.CLIP_RENDER

    def test_render_task_dependencies(self):
        """RenderTask tracks dependencies"""
        task = RenderTask(
            depends_on=["task-1", "task-2"],
            input_assets=["asset-1"],
        )

        assert len(task.depends_on) == 2
        assert len(task.input_assets) == 1

    def test_render_task_immutable(self):
        """RenderTask is immutable"""
        task = RenderTask()

        with pytest.raises(AttributeError):
            task.source_path = "/new/path"


class TestAssetMetadata:
    """Test AssetMetadata domain model"""

    def test_asset_metadata_creation(self):
        """AssetMetadata can be created"""
        metadata = AssetMetadata(
            asset_type=AssetType.CLIP,
            file_path="/path/to/asset.mp4",
            duration_seconds=10.0,
        )

        assert metadata.asset_type == AssetType.CLIP
        assert metadata.duration_seconds == 10.0

    def test_asset_metadata_immutable(self):
        """AssetMetadata is immutable"""
        metadata = AssetMetadata()

        with pytest.raises(AttributeError):
            metadata.duration_seconds = 20.0

    def test_asset_metadata_to_dict(self):
        """AssetMetadata can serialize to dict"""
        metadata = AssetMetadata(
            asset_type=AssetType.FINAL_VIDEO,
            file_path="/path/to/video.mp4",
        )

        d = metadata.to_dict()
        assert d["asset_type"] == "final_video"


class TestRenderedAsset:
    """Test RenderedAsset domain model"""

    def test_rendered_asset_creation(self):
        """RenderedAsset can be created"""
        metadata = AssetMetadata(asset_type=AssetType.CLIP)
        asset = RenderedAsset(
            metadata=metadata,
            job_id="job-1",
        )

        assert asset.job_id == "job-1"
        assert asset.metadata.asset_type == AssetType.CLIP

    def test_rendered_asset_immutable(self):
        """RenderedAsset is immutable"""
        asset = RenderedAsset()

        with pytest.raises(AttributeError):
            asset.job_id = "new-job"

    def test_rendered_asset_to_dict(self):
        """RenderedAsset can serialize to dict"""
        metadata = AssetMetadata(asset_type=AssetType.CLIP)
        asset = RenderedAsset(metadata=metadata)

        d = asset.to_dict()
        assert d["asset_type"] == "clip"


class TestArtifact:
    """Test Artifact domain model"""

    def test_artifact_creation(self):
        """Artifact can be created"""
        artifact = Artifact(
            job_id="job-1",
            file_path="/path/to/final.mp4",
            export_profile=ExportProfile.YOUTUBE_16_9,
        )

        assert artifact.job_id == "job-1"
        assert artifact.export_profile == ExportProfile.YOUTUBE_16_9

    def test_artifact_immutable(self):
        """Artifact is immutable"""
        artifact = Artifact()

        with pytest.raises(AttributeError):
            artifact.validation_passed = True

    def test_artifact_to_dict(self):
        """Artifact can serialize to dict"""
        artifact = Artifact(
            job_id="job-1",
            resolution="1920x1080",
        )

        d = artifact.to_dict()
        assert d["resolution"] == "1920x1080"


class TestArtifactBundle:
    """Test ArtifactBundle domain model"""

    def test_artifact_bundle_creation(self):
        """ArtifactBundle can be created"""
        final_video = Artifact(job_id="job-1")
        bundle = ArtifactBundle(
            job_id="job-1",
            final_video=final_video,
        )

        assert bundle.final_video is not None
        assert bundle.job_id == "job-1"

    def test_artifact_bundle_with_exports(self):
        """ArtifactBundle can contain multiple exports"""
        exports = [
            Artifact(export_profile=ExportProfile.YOUTUBE_16_9),
            Artifact(export_profile=ExportProfile.TIKTOK),
        ]

        bundle = ArtifactBundle(exports=exports)

        assert len(bundle.exports) == 2

    def test_artifact_bundle_to_dict(self):
        """ArtifactBundle can serialize to dict"""
        bundle = ArtifactBundle(job_id="job-1")

        d = bundle.to_dict()
        assert d["job_id"] == "job-1"


class TestValidationResult:
    """Test ValidationResult domain model"""

    def test_validation_result_passed(self):
        """ValidationResult can represent passed validation"""
        result = ValidationResult(
            artifact_id="a1",
            status=ValidationStatus.PASSED,
            score=1.0,
        )

        assert result.status == ValidationStatus.PASSED
        assert result.score == 1.0

    def test_validation_result_with_issues(self):
        """ValidationResult can track issues"""
        result = ValidationResult(
            artifact_id="a1",
            status=ValidationStatus.FAILED,
            score=0.5,
            issues=["Resolution mismatch", "Duration incorrect"],
        )

        assert len(result.issues) == 2
        assert result.score == 0.5

    def test_validation_result_immutable(self):
        """ValidationResult is immutable"""
        result = ValidationResult()

        with pytest.raises(AttributeError):
            result.score = 0.8


class TestRenderMetrics:
    """Test RenderMetrics domain model"""

    def test_render_metrics_creation(self):
        """RenderMetrics can be created"""
        metrics = RenderMetrics(
            job_id="job-1",
            total_duration_seconds=120.0,
            frames_rendered=3600,
        )

        assert metrics.job_id == "job-1"
        assert metrics.frames_rendered == 3600

    def test_render_metrics_to_dict(self):
        """RenderMetrics can serialize to dict"""
        metrics = RenderMetrics(
            total_duration_seconds=120.0,
            peak_cpu_percent=75.5,
        )

        d = metrics.to_dict()
        assert d["total_duration_seconds"] == 120.0


# ============================================================================
# PROVIDER INTERFACE TESTS
# ============================================================================


class TestMockRendererProvider:
    """Test MockRendererProvider implementation"""

    @pytest.mark.asyncio
    async def test_mock_provider_available(self):
        """Mock provider is always available"""
        provider = MockRendererProvider()

        assert await provider.is_available()

    @pytest.mark.asyncio
    async def test_mock_provider_metadata(self):
        """Mock provider has correct metadata"""
        provider = MockRendererProvider()

        assert provider.name == "mock"
        assert provider.version == "1.0.0"
        assert "clip_rendering" in provider.capabilities

    @pytest.mark.asyncio
    async def test_mock_render_clip(self):
        """Mock provider can render clips"""
        provider = MockRendererProvider()

        asset = await provider.render_clip(
            source_path="/path/to/clip.mp4",
            start_seconds=0.0,
            end_seconds=5.0,
            output_path="/output/clip.mp4",
        )

        assert asset.metadata.duration_seconds == 5.0
        assert asset.metadata.is_valid

    @pytest.mark.asyncio
    async def test_mock_validate_output(self):
        """Mock provider can validate output"""
        provider = MockRendererProvider()

        result = await provider.validate_output(
            video_path="/output/video.mp4",
        )

        assert result.status == ValidationStatus.PASSED
        assert result.score == 1.0

    @pytest.mark.asyncio
    async def test_mock_get_video_info(self):
        """Mock provider can get video info"""
        provider = MockRendererProvider()

        info = await provider.get_video_info("/path/to/video.mp4")

        assert "duration_seconds" in info
        assert "resolution" in info

    @pytest.mark.asyncio
    async def test_mock_provider_to_dict(self):
        """Mock provider can serialize to dict"""
        provider = MockRendererProvider()

        d = provider.to_dict()
        assert d["name"] == "mock"


class TestFFmpegProvider:
    """Test FFmpegProvider implementation"""

    @pytest.mark.asyncio
    async def test_ffmpeg_provider_metadata(self):
        """FFmpeg provider has correct metadata"""
        provider = FFmpegProvider()

        assert provider.name == "ffmpeg"
        assert provider.version == "4.4.0"

    @pytest.mark.asyncio
    async def test_ffmpeg_capabilities(self):
        """FFmpeg provider declares capabilities"""
        provider = FFmpegProvider()

        capabilities = provider.capabilities
        assert capabilities["clip_rendering"]
        assert capabilities["subtitles"]
        assert not capabilities["transitions"]  # Requires complex filtering

    @pytest.mark.asyncio
    async def test_ffmpeg_available(self):
        """FFmpeg provider availability check"""
        provider = FFmpegProvider()

        # In Phase 1, just returns True
        assert await provider.is_available()

    @pytest.mark.asyncio
    async def test_ffmpeg_render_clip(self):
        """FFmpeg provider can render clips"""
        provider = FFmpegProvider()

        asset = await provider.render_clip(
            source_path="/path/to/clip.mp4",
            start_seconds=0.0,
            end_seconds=5.0,
            output_path="/output/clip.mp4",
        )

        assert asset.metadata.duration_seconds == 5.0

    @pytest.mark.asyncio
    async def test_ffmpeg_unsupported_features(self):
        """FFmpeg provider raises for unsupported features"""
        provider = FFmpegProvider()

        with pytest.raises(NotImplementedError):
            await provider.apply_transition(
                from_clip_path="clip1.mp4",
                to_clip_path="clip2.mp4",
                transition_type="fade",
                duration_seconds=1.0,
                output_path="/output/trans.mp4",
            )


# ============================================================================
# PROVIDER REGISTRY TESTS
# ============================================================================


class TestProviderRegistry:
    """Test ProviderRegistry"""

    def test_registry_creation(self):
        """Provider registry can be created"""
        registry = ProviderRegistry()

        assert registry is not None

    def test_registry_registration(self):
        """Provider can be registered"""
        registry = ProviderRegistry()
        provider = MockRendererProvider()

        registry.register(provider)
        retrieved = registry.get("mock")

        assert retrieved is not None
        assert retrieved.name == "mock"

    def test_registry_list_providers(self):
        """Registry can list providers"""
        registry = create_default_provider_registry()
        providers = registry.list_providers()

        assert "mock" in providers
        assert "ffmpeg" in providers

    def test_registry_get_provider_info(self):
        """Registry can get provider info"""
        registry = create_default_provider_registry()
        info = registry.get_provider_info()

        assert "mock" in info
        assert "ffmpeg" in info

    def test_default_registry_has_mock(self):
        """Default registry includes MockRendererProvider"""
        registry = create_default_provider_registry()

        mock = registry.get("mock")
        assert mock is not None
        assert isinstance(mock, MockRendererProvider)

    def test_default_registry_has_ffmpeg(self):
        """Default registry includes FFmpegProvider"""
        registry = create_default_provider_registry()

        ffmpeg = registry.get("ffmpeg")
        assert ffmpeg is not None
        assert isinstance(ffmpeg, FFmpegProvider)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestPhase1Integration:
    """Test Phase 1 components working together"""

    def test_render_job_to_task_workflow(self):
        """RenderJob creates RenderTasks"""
        job = RenderJob(session_id="s1", video_id="v1")
        task = RenderTask(
            job_id=job.job_id,
            task_type=RenderTaskType.CLIP_RENDER,
        )

        assert task.job_id == job.job_id

    def test_provider_asset_to_artifact_workflow(self):
        """Provider output becomes Artifact"""
        metadata = AssetMetadata(
            asset_type=AssetType.FINAL_VIDEO,
            file_path="/output/video.mp4",
            duration_seconds=300.0,
        )

        asset = RenderedAsset(metadata=metadata)

        artifact = Artifact(
            file_path=asset.metadata.file_path,
            duration_seconds=asset.metadata.duration_seconds,
        )

        assert artifact.duration_seconds == 300.0

    def test_artifact_bundle_creation_workflow(self):
        """Multiple artifacts can be bundled"""
        main = Artifact(
            export_profile=ExportProfile.YOUTUBE_16_9,
            file_path="/output/main.mp4",
        )

        exports = [
            Artifact(export_profile=ExportProfile.TIKTOK),
            Artifact(export_profile=ExportProfile.YOUTUBE_SHORTS),
        ]

        bundle = ArtifactBundle(
            job_id="job-1",
            final_video=main,
            exports=exports,
        )

        assert bundle.final_video is not None
        assert len(bundle.exports) == 2

    @pytest.mark.asyncio
    async def test_provider_swapping(self):
        """Providers are interchangeable"""
        mock_provider = MockRendererProvider()
        ffmpeg_provider = FFmpegProvider()

        # Both should implement same interface
        assert hasattr(mock_provider, "render_clip")
        assert hasattr(ffmpeg_provider, "render_clip")

        # Both can be registered
        registry = ProviderRegistry()
        registry.register(mock_provider)
        registry.register(ffmpeg_provider)

        assert registry.get("mock") == mock_provider
        assert registry.get("ffmpeg") == ffmpeg_provider


# ============================================================================
# EDGE CASE TESTS
# ============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_render_job_with_many_profiles(self):
        """RenderJob can have multiple export profiles"""
        profiles = [
            ExportProfile.YOUTUBE_16_9,
            ExportProfile.YOUTUBE_SHORTS,
            ExportProfile.TIKTOK,
            ExportProfile.INSTAGRAM_REEL,
            ExportProfile.LINKEDIN,
        ]

        job = RenderJob(export_profiles=profiles)

        assert len(job.export_profiles) == 5

    def test_render_task_deep_dependencies(self):
        """RenderTask can have complex dependency chain"""
        task = RenderTask(
            depends_on=[f"task-{i}" for i in range(10)],
        )

        assert len(task.depends_on) == 10

    def test_artifact_bundle_large_exports(self):
        """ArtifactBundle can have many exports"""
        exports = [
            Artifact(export_profile=ExportProfile.YOUTUBE_16_9),
            Artifact(export_profile=ExportProfile.YOUTUBE_SHORTS),
            Artifact(export_profile=ExportProfile.TIKTOK),
            Artifact(export_profile=ExportProfile.INSTAGRAM_REEL),
            Artifact(export_profile=ExportProfile.INSTAGRAM_FEED),
            Artifact(export_profile=ExportProfile.LINKEDIN),
            Artifact(export_profile=ExportProfile.PODCAST_AUDIO),
        ]

        bundle = ArtifactBundle(exports=exports)

        assert len(bundle.exports) == 7

    @pytest.mark.asyncio
    async def test_zero_duration_clip(self):
        """Provider handles zero-duration clips"""
        provider = MockRendererProvider()

        asset = await provider.render_clip(
            source_path="/path/to/clip.mp4",
            start_seconds=5.0,
            end_seconds=5.0,  # Zero duration
            output_path="/output/clip.mp4",
        )

        assert asset.metadata.duration_seconds == 0.0

    @pytest.mark.asyncio
    async def test_very_long_duration_clip(self):
        """Provider handles very long clips"""
        provider = MockRendererProvider()

        asset = await provider.render_clip(
            source_path="/path/to/long.mp4",
            start_seconds=0.0,
            end_seconds=36000.0,  # 10 hours
            output_path="/output/long.mp4",
        )

        assert asset.metadata.duration_seconds == 36000.0
