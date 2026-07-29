"""Milestone 12: Rendering Engine.

Phase 1: Domain models, provider interface, reference implementations
Phase 2: Rendering engines, context models, validation
Phase 3: M6 agents, task orchestration, events, metrics
Phase 4: Tests, documentation, review
"""

# Context Models (Phase 2)
from .context import (
    RenderCapability,
    RenderContext,
)

# Rendering Engines (Phase 2)
from .engines import (
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
)

# Models (Phase 1)
from .models import (
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
)

# Provider Interface (Phase 1)
from .providers import (
    ProviderRegistry,
    RendererProvider,
)

# Reference Implementations (Phase 1)
from .backend import (
    FFmpegProvider,
    MockRendererProvider,
    create_default_provider_registry,
)

__all__ = [
    # Context (Phase 2)
    "RenderCapability",
    "RenderContext",
    # Rendering Engines (Phase 2)
    "AudioRenderer",
    "BrollRenderer",
    "ClipRenderer",
    "CompositeRenderer",
    "ExportRenderer",
    "OverlayRenderer",
    "RenderingEngine",
    "RendererRegistry",
    "SubtitleRenderer",
    "TransitionRenderer",
    "ValidationEngine",
    "ZoomRenderer",
    "create_renderer_registry",
    # Models (Phase 1)
    "Artifact",
    "ArtifactBundle",
    "AssetMetadata",
    "AssetType",
    "ExportProfile",
    "RenderedAsset",
    "RenderGraph",
    "RenderJob",
    "RenderJobStatus",
    "RenderManifest",
    "RenderMetrics",
    "RenderResult",
    "RenderSegment",
    "RenderTask",
    "RenderTaskType",
    "ValidationResult",
    "ValidationStatus",
    # Provider Interface (Phase 1)
    "ProviderRegistry",
    "RendererProvider",
    # Reference Implementations (Phase 1)
    "FFmpegProvider",
    "MockRendererProvider",
    "create_default_provider_registry",
]
