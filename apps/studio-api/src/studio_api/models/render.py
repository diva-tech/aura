"""Render models."""

from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text

from studio_api.database.base import Base


class RenderStatus(str, Enum):
    """Render status."""

    PENDING = "pending"
    QUEUED = "queued"
    PREPARING = "preparing"
    RENDERING = "rendering"
    ENCODING = "encoding"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class RenderStage(str, Enum):
    """Render pipeline stages."""

    PREPARING_ASSETS = "preparing_assets"
    CUTTING = "cutting"
    CAPTIONS = "captions"
    OVERLAYS = "overlays"
    TRANSITIONS = "transitions"
    EFFECTS = "effects"
    AUDIO_MIX = "audio_mix"
    COLOR_GRADING = "color_grading"
    ENCODING = "encoding"
    THUMBNAIL = "thumbnail"
    FINALIZING = "finalizing"


class RenderQuality(str, Enum):
    """Render quality presets."""

    DRAFT = "draft"
    STANDARD = "standard"
    HIGH = "high"
    ULTRA = "ultra"


class Render(Base):
    """Render job model."""

    __tablename__ = "renders"

    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    preview_id = Column(String(36), ForeignKey("previews.id"), nullable=False, index=True)
    edit_plan_id = Column(String(36), ForeignKey("edit_plans.id"), nullable=False, index=True)
    status = Column(String(50), default="pending")  # pending, queued, rendering, completed, failed
    quality = Column(String(20), default="standard")  # draft, standard, high, ultra
    platform = Column(String(50), nullable=True)  # youtube, shorts, instagram, tiktok, etc.
    priority = Column(Integer, default=5)  # 1-10, higher = more important
    output_path = Column(String(500), nullable=True)
    output_size = Column(Integer, nullable=True)  # bytes
    duration = Column(Integer, nullable=True)  # milliseconds
    fps = Column(Integer, nullable=True)
    resolution = Column(String(50), nullable=True)
    codec = Column(String(50), nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    estimated_time = Column(Integer, nullable=True)  # seconds
    elapsed_time = Column(Integer, default=0)  # seconds
    progress_percent = Column(Float, default=0.0)  # 0-100
    current_stage = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class RenderLog(Base):
    """Render progress log entry."""

    __tablename__ = "render_logs"

    id = Column(String(36), primary_key=True, index=True)
    render_id = Column(String(36), ForeignKey("renders.id"), nullable=False, index=True)
    stage = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)  # started, completed, error
    message = Column(Text, nullable=True)
    progress_percent = Column(Float, nullable=True)
    duration = Column(Integer, nullable=True)  # milliseconds
    error_code = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)


class RenderAsset(Base):
    """Rendered asset file."""

    __tablename__ = "render_assets"

    id = Column(String(36), primary_key=True, index=True)
    render_id = Column(String(36), ForeignKey("renders.id"), nullable=False, index=True)
    asset_type = Column(String(50), nullable=False)  # video, thumbnail, captions, metadata
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)  # bytes
    file_format = Column(String(50), nullable=True)  # mp4, vtt, jpg, json
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class RenderMetadata(Base):
    """Render metadata and statistics."""

    __tablename__ = "render_metadata"

    id = Column(String(36), primary_key=True, index=True)
    render_id = Column(String(36), ForeignKey("renders.id"), nullable=False, index=True)
    total_frames = Column(Integer, nullable=True)
    frames_processed = Column(Integer, default=0)
    gpu_usage_peak = Column(Float, nullable=True)  # 0-100
    cpu_usage_peak = Column(Float, nullable=True)  # 0-100
    memory_usage_peak = Column(Integer, nullable=True)  # MB
    bitrate_actual = Column(String(50), nullable=True)
    actual_fps = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
