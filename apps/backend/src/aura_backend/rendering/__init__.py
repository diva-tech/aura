"""Milestone 12: Rendering Engine.

Phase 1: Domain models, provider interface, reference implementations
Phase 2: Rendering engines, validation, export profiles
Phase 3: M6 agents, task orchestration, events, metrics
Phase 4: Tests, documentation, review
"""

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
    # Models
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
    # Provider Interface
    "ProviderRegistry",
    "RendererProvider",
    # Reference Implementations
    "FFmpegProvider",
    "MockRendererProvider",
    "create_default_provider_registry",
]
