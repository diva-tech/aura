"""M12 Phase 1: Renderer Provider Interface.

Abstract base class for all rendering providers.
Providers are interchangeable backends (FFmpeg, MoviePy, Remotion, etc.).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .models import (
    AssetMetadata,
    ExportProfile,
    RenderedAsset,
    RenderResult,
    ValidationResult,
)


class RendererProvider(ABC):
    """Abstract base class for all rendering providers.

    Providers handle the actual media manipulation (rendering, compositing,
    encoding, etc.). All providers are interchangeable and stateless.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name (e.g., 'ffmpeg', 'moviepy', 'remotion')"""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Provider version"""
        pass

    @property
    @abstractmethod
    def capabilities(self) -> Dict[str, bool]:
        """Provider capabilities (what features it supports)"""
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if provider is available (binary installed, etc.)"""
        pass

    # ========================================================================
    # RENDERING OPERATIONS
    # ========================================================================

    @abstractmethod
    async def render_clip(
        self,
        source_path: str,
        start_seconds: float,
        end_seconds: float,
        output_path: str,
        resolution: str = "1920x1080",
        fps: int = 30,
        codec: str = "h264",
        bitrate: str = "5000k",
    ) -> RenderedAsset:
        """Render a video clip from source.

        Args:
            source_path: Path to source video
            start_seconds: Start time in seconds
            end_seconds: End time in seconds
            output_path: Where to write rendered clip
            resolution: Target resolution (WxH)
            fps: Target frames per second
            codec: Video codec (h264, h265, etc.)
            bitrate: Target bitrate (e.g., '5000k')

        Returns:
            RenderedAsset with metadata
        """
        pass

    @abstractmethod
    async def apply_transition(
        self,
        from_clip_path: str,
        to_clip_path: str,
        transition_type: str,
        duration_seconds: float,
        output_path: str,
    ) -> RenderedAsset:
        """Apply transition between two clips.

        Args:
            from_clip_path: Path to first clip
            to_clip_path: Path to second clip
            transition_type: Type of transition (fade, dissolve, slide, etc.)
            duration_seconds: Transition duration
            output_path: Where to write result

        Returns:
            RenderedAsset with transition applied
        """
        pass

    @abstractmethod
    async def render_subtitles(
        self,
        video_path: str,
        subtitle_data: List[Dict[str, Any]],
        output_path: str,
        style: str = "default",
    ) -> RenderedAsset:
        """Burn subtitles into video.

        Args:
            video_path: Path to video
            subtitle_data: List of subtitle dicts with timing/text
            output_path: Where to write result
            style: Subtitle styling (color, size, position, etc.)

        Returns:
            RenderedAsset with subtitles burned
        """
        pass

    @abstractmethod
    async def render_overlay(
        self,
        video_path: str,
        overlay_type: str,
        content: Dict[str, Any],
        output_path: str,
    ) -> RenderedAsset:
        """Render overlay onto video.

        Args:
            video_path: Path to video
            overlay_type: Type of overlay (lower_third, statistic, etc.)
            content: Overlay content (text, position, size, etc.)
            output_path: Where to write result

        Returns:
            RenderedAsset with overlay applied
        """
        pass

    @abstractmethod
    async def apply_zoom(
        self,
        video_path: str,
        zoom_actions: List[Dict[str, Any]],
        output_path: str,
    ) -> RenderedAsset:
        """Apply zoom/pan effects to video.

        Args:
            video_path: Path to video
            zoom_actions: List of zoom action specs (timing, type, intensity)
            output_path: Where to write result

        Returns:
            RenderedAsset with zoom effects applied
        """
        pass

    @abstractmethod
    async def insert_broll(
        self,
        main_video_path: str,
        broll_path: str,
        start_time_seconds: float,
        duration_seconds: float,
        output_path: str,
    ) -> RenderedAsset:
        """Insert B-roll into main video.

        Args:
            main_video_path: Path to main video
            broll_path: Path to B-roll clip
            start_time_seconds: Where to insert B-roll
            duration_seconds: How long to show B-roll
            output_path: Where to write result

        Returns:
            RenderedAsset with B-roll inserted
        """
        pass

    @abstractmethod
    async def mix_audio(
        self,
        video_path: str,
        audio_tracks: List[Dict[str, Any]],
        output_path: str,
    ) -> RenderedAsset:
        """Mix audio tracks into video.

        Args:
            video_path: Path to video (video only or with audio)
            audio_tracks: List of audio specs (path, volume, fade, etc.)
            output_path: Where to write result

        Returns:
            RenderedAsset with audio mixed
        """
        pass

    @abstractmethod
    async def composite_video(
        self,
        clips: List[str],
        transitions: List[Dict[str, Any]],
        output_path: str,
    ) -> RenderedAsset:
        """Composite multiple clips with transitions into single video.

        Args:
            clips: List of clip paths
            transitions: Transition specs between clips
            output_path: Where to write result

        Returns:
            RenderedAsset with composited video
        """
        pass

    @abstractmethod
    async def export_video(
        self,
        video_path: str,
        export_profile: ExportProfile,
        output_path: str,
    ) -> RenderedAsset:
        """Export video in specific profile/format.

        Args:
            video_path: Path to video to export
            export_profile: Export profile (YouTube, TikTok, etc.)
            output_path: Where to write exported video

        Returns:
            RenderedAsset with exported video
        """
        pass

    # ========================================================================
    # VALIDATION
    # ========================================================================

    @abstractmethod
    async def validate_output(
        self,
        video_path: str,
        expected_duration_seconds: float = 0.0,
        expected_resolution: str = "1920x1080",
    ) -> ValidationResult:
        """Validate rendered video output.

        Args:
            video_path: Path to video to validate
            expected_duration_seconds: Expected duration (0 = skip check)
            expected_resolution: Expected resolution

        Returns:
            ValidationResult with all validation checks
        """
        pass

    @abstractmethod
    async def verify_checksum(
        self,
        file_path: str,
        expected_checksum: str,
    ) -> bool:
        """Verify file checksum.

        Args:
            file_path: Path to file
            expected_checksum: Expected checksum value

        Returns:
            True if checksum matches
        """
        pass

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    @abstractmethod
    async def get_video_info(
        self,
        video_path: str,
    ) -> Dict[str, Any]:
        """Get metadata about a video file.

        Returns:
            Dict with duration, resolution, fps, codec, etc.
        """
        pass

    @abstractmethod
    async def probe_file(
        self,
        file_path: str,
    ) -> Optional[AssetMetadata]:
        """Probe a file and return metadata.

        Returns:
            AssetMetadata or None if file invalid
        """
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Serialize provider info"""
        return {
            "name": self.name,
            "version": self.version,
            "capabilities": self.capabilities,
        }


# ============================================================================
# PROVIDER REGISTRY
# ============================================================================


class ProviderRegistry:
    """Registry of available rendering providers."""

    def __init__(self):
        self._providers: Dict[str, RendererProvider] = {}

    def register(self, provider: RendererProvider) -> None:
        """Register a rendering provider."""
        self._providers[provider.name] = provider

    def get(self, name: str) -> Optional[RendererProvider]:
        """Get provider by name."""
        return self._providers.get(name)

    def list_providers(self) -> List[str]:
        """List all registered providers."""
        return list(self._providers.keys())

    def get_provider_info(self) -> Dict[str, Dict[str, Any]]:
        """Get info about all providers."""
        return {name: provider.to_dict() for name, provider in self._providers.items()}
