"""M12 Phase 2: Render Context and Capability Models.

Immutable context carriers for rendering execution and provider capability tracking.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

from .models import ExportProfile


@dataclass(frozen=True)
class RenderCapability:
    """Immutable provider capability descriptor.

    Describes what features a rendering provider supports.
    """

    provider_name: str = ""
    version: str = ""

    # Hardware capabilities
    gpu_supported: bool = False
    gpu_required: bool = False
    hdr_supported: bool = False
    hdr_10_supported: bool = False
    max_resolution: str = "1920x1080"  # max supported resolution

    # Codec/format capabilities
    supported_codecs: Set[str] = field(default_factory=set)  # h264, h265, vp9, av1, etc.
    supported_audio_codecs: Set[str] = field(default_factory=set)  # aac, mp3, flac, etc.
    supported_containers: Set[str] = field(default_factory=set)  # mp4, webm, mov, etc.

    # Feature capabilities
    alpha_channel_supported: bool = False
    subtitle_support: bool = False
    subtitle_formats: Set[str] = field(default_factory=set)  # srt, vtt, ass, etc.
    audio_mixing_supported: bool = False
    max_audio_tracks: int = 2
    effects_supported: bool = False
    effect_types: Set[str] = field(default_factory=set)  # fade, dissolve, etc.

    # Performance capabilities
    batching_supported: bool = False
    streaming_supported: bool = False
    concurrent_jobs: int = 1
    estimated_speed: float = 1.0  # FPS relative to realtime

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider_name": self.provider_name,
            "version": self.version,
            "gpu_supported": self.gpu_supported,
            "hdr_supported": self.hdr_supported,
            "max_resolution": self.max_resolution,
            "supported_codecs": list(self.supported_codecs),
            "subtitle_support": self.subtitle_support,
            "audio_mixing_supported": self.audio_mixing_supported,
            "streaming_supported": self.streaming_supported,
            "concurrent_jobs": self.concurrent_jobs,
        }

    def supports_codec(self, codec: str) -> bool:
        """Check if codec is supported"""
        return codec in self.supported_codecs

    def supports_feature(self, feature: str) -> bool:
        """Check if feature is supported"""
        features = {
            "gpu": self.gpu_supported,
            "hdr": self.hdr_supported,
            "alpha": self.alpha_channel_supported,
            "subtitles": self.subtitle_support,
            "audio_mixing": self.audio_mixing_supported,
            "effects": self.effects_supported,
            "batching": self.batching_supported,
            "streaming": self.streaming_supported,
        }
        return features.get(feature, False)


@dataclass(frozen=True)
class RenderContext:
    """Immutable execution context for rendering.

    Carries all necessary context for rendering operations.
    """

    context_id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    video_id: str = ""
    job_id: str = ""

    # Provider configuration
    provider_name: str = "mock"
    provider_capability: Optional[RenderCapability] = None

    # Rendering parameters
    target_resolution: str = "1920x1080"
    target_fps: int = 30
    target_codec: str = "h264"
    target_bitrate: str = "5000k"
    target_audio_codec: str = "aac"
    target_audio_sample_rate: int = 48000

    # Export configuration
    export_profiles: List[ExportProfile] = field(default_factory=list)
    primary_export_profile: ExportProfile = ExportProfile.YOUTUBE_16_9

    # Paths
    working_directory: str = "/tmp/render"  # Where to write intermediate files
    output_directory: str = "/tmp/output"  # Where to write final artifacts
    cache_directory: str = "/tmp/cache"  # Where to cache assets

    # Rendering options
    use_gpu: bool = False
    use_hardware_acceleration: bool = False
    max_workers: int = 4  # Parallel workers
    retry_on_failure: bool = True
    max_retries: int = 3

    # Quality/performance tradeoff
    quality_preset: str = "medium"  # fast, medium, slow, lossless
    optimization_level: int = 2  # 0-3

    # Logging and debugging
    verbose: bool = False
    keep_intermediate_files: bool = False
    enable_profiling: bool = False

    # Timing information
    created_at: datetime = field(default_factory=datetime.utcnow)
    timeout_seconds: float = 3600.0  # 1 hour default timeout

    def to_dict(self) -> Dict[str, Any]:
        return {
            "context_id": self.context_id,
            "session_id": self.session_id,
            "job_id": self.job_id,
            "provider_name": self.provider_name,
            "target_resolution": self.target_resolution,
            "target_fps": self.target_fps,
            "working_directory": self.working_directory,
            "export_profiles": [p.value for p in self.export_profiles],
            "quality_preset": self.quality_preset,
            "timeout_seconds": self.timeout_seconds,
        }

    @property
    def working_path(self) -> Path:
        """Get working directory as Path"""
        return Path(self.working_directory)

    @property
    def output_path(self) -> Path:
        """Get output directory as Path"""
        return Path(self.output_directory)

    @property
    def cache_path(self) -> Path:
        """Get cache directory as Path"""
        return Path(self.cache_directory)

    def for_export_profile(self, profile: ExportProfile) -> "RenderContext":
        """Create context for specific export profile (immutable copy)"""
        # In Phase 2+, would adjust resolution, fps, codec based on profile
        return RenderContext(
            context_id=self.context_id,
            session_id=self.session_id,
            video_id=self.video_id,
            job_id=self.job_id,
            provider_name=self.provider_name,
            provider_capability=self.provider_capability,
            target_resolution=self.target_resolution,
            target_fps=self.target_fps,
            target_codec=self.target_codec,
            target_bitrate=self.target_bitrate,
            export_profiles=self.export_profiles,
            primary_export_profile=profile,
            working_directory=self.working_directory,
            output_directory=self.output_directory,
            cache_directory=self.cache_directory,
            use_gpu=self.use_gpu,
            max_workers=self.max_workers,
            quality_preset=self.quality_preset,
        )
