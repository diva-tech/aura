"""Video Intelligence Runtime.

Analyzes videos and converts findings into structured knowledge.

Does NOT edit, render, or generate videos.
Does analyze, understand, and extract knowledge from videos.

Architecture:
- Provider-agnostic analysis (speech, OCR, vision pluggable)
- Immutable observation model (universal for all discoveries)
- Timeline-first execution (all findings become timeline events)
- M6 agent integration (analysis via Task Orchestration)
- M7 memory integration (knowledge storage)
"""

from aura_backend.video.models import (
    Observation,
    ObservationType,
    Scene,
    Timeline,
    TimelineEvent,
    TimelineEventType,
    Video,
    VideoMetadata,
    Frame,
    AudioSegment,
    TranscriptSegment,
    KnowledgeNode,
    AnalysisSession,
    VideoCodec,
    AudioCodec,
)
from aura_backend.video.providers import (
    VideoProvider,
    SpeechProvider,
    OCRProvider,
    VisionProvider,
    FFmpegVideoProvider,
    WhisperSpeechProvider,
    TesseractOCRProvider,
    OpenCVVisionProvider,
    ProviderRegistry,
)
from aura_backend.video.mappers import (
    SpeechMapper,
    OCRMapper,
    VisionMapper,
)
from aura_backend.video.extraction import (
    FrameExtractionService,
    AudioExtractionService,
    ExtractedFrame,
    ExtractedAudioSegment,
)
from aura_backend.video.scene_analysis import (
    SceneProvider,
    OpenCVSceneProvider,
    SceneDetection,
    SceneMapper,
)
from aura_backend.video.analysis_agents import (
    SceneAnalysisAgent,
    SpeechAnalysisAgent,
    OCRAnalysisAgent,
    VisionAnalysisAgent,
)
from aura_backend.video.knowledge_builder import KnowledgeBuilder
from aura_backend.video.analysis_planner import (
    AnalysisPlanner,
    TaskGraph,
    Task,
    TaskType,
    TaskStatus,
)
from aura_backend.video.ingestion import VideoIngestionPipeline

__all__ = [
    # Models
    "Video",
    "VideoMetadata",
    "Frame",
    "Scene",
    "AudioSegment",
    "TranscriptSegment",
    "Observation",
    "ObservationType",
    "Timeline",
    "TimelineEvent",
    "TimelineEventType",
    "KnowledgeNode",
    "AnalysisSession",
    "VideoCodec",
    "AudioCodec",
    # Providers (interfaces)
    "VideoProvider",
    "SpeechProvider",
    "OCRProvider",
    "VisionProvider",
    # Reference implementations
    "FFmpegVideoProvider",
    "WhisperSpeechProvider",
    "TesseractOCRProvider",
    "OpenCVVisionProvider",
    "ProviderRegistry",
    # Mappers
    "SpeechMapper",
    "OCRMapper",
    "VisionMapper",
    # Extraction services
    "FrameExtractionService",
    "AudioExtractionService",
    "ExtractedFrame",
    "ExtractedAudioSegment",
    # Scene analysis
    "SceneProvider",
    "OpenCVSceneProvider",
    "SceneDetection",
    "SceneMapper",
    # Analysis agents
    "SceneAnalysisAgent",
    "SpeechAnalysisAgent",
    "OCRAnalysisAgent",
    "VisionAnalysisAgent",
    # Knowledge builder
    "KnowledgeBuilder",
    # Analysis planning (M8 integration)
    "AnalysisPlanner",
    "TaskGraph",
    "Task",
    "TaskType",
    "TaskStatus",
    # Pipeline
    "VideoIngestionPipeline",
]
