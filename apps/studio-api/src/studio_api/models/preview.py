"""Preview models."""

from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text

from studio_api.database.base import Base


class PreviewQuality(str, Enum):
    """Preview quality levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PreviewStatus(str, Enum):
    """Preview status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Preview(Base):
    """Preview model."""

    __tablename__ = "previews"

    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    edit_plan_id = Column(String(36), ForeignKey("edit_plans.id"), nullable=False, index=True)
    version = Column(Integer, default=1, nullable=False)
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    quality = Column(String(20), default="medium")  # low, medium, high
    approved = Column(Boolean, default=False)
    file_path = Column(String(500), nullable=True)
    duration = Column(Integer, nullable=True)  # milliseconds
    filesize = Column(Integer, nullable=True)  # bytes
    estimated_render_time = Column(Integer, nullable=True)  # seconds
    estimated_output_size = Column(Integer, nullable=True)  # bytes
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class RenderSettings(Base):
    """Render settings for preview/final render."""

    __tablename__ = "render_settings"

    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    resolution = Column(String(50), default="1080p")  # 720p, 1080p, 2k, 4k
    fps = Column(Integer, default=30)  # 24, 30, 60
    codec = Column(String(50), default="h264")  # h264, h265, av1
    bitrate = Column(String(50), default="5mbps")  # variable bitrate
    platform = Column(String(50), nullable=True)  # youtube, shorts, tiktok, instagram
    audio_bitrate = Column(String(50), default="128kbps")
    audio_codec = Column(String(50), default="aac")  # aac, mp3, opus
    quality_level = Column(Integer, default=85)  # 0-100
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class RenderEstimate(Base):
    """Render cost and time estimation."""

    __tablename__ = "render_estimates"

    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    edit_plan_id = Column(String(36), ForeignKey("edit_plans.id"), nullable=False, index=True)
    estimated_duration = Column(Integer, nullable=True)  # milliseconds
    estimated_render_time = Column(Integer, nullable=True)  # seconds
    estimated_output_size = Column(Integer, nullable=True)  # bytes
    gpu_usage_percent = Column(Float, nullable=True)  # 0-100
    cpu_usage_percent = Column(Float, nullable=True)  # 0-100
    operations_count = Column(Integer, default=0)
    effects_count = Column(Integer, default=0)
    captions_count = Column(Integer, default=0)
    transitions_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class PreviewValidation(Base):
    """Preview validation results."""

    __tablename__ = "preview_validations"

    id = Column(String(36), primary_key=True, index=True)
    preview_id = Column(String(36), ForeignKey("previews.id"), nullable=False, index=True)
    is_valid = Column(Boolean, default=True)
    errors = Column(Text, nullable=True)  # JSON array of error objects
    warnings = Column(Text, nullable=True)  # JSON array of warning objects
    checked_assets = Column(Boolean, default=False)
    checked_operations = Column(Boolean, default=False)
    checked_audio = Column(Boolean, default=False)
    checked_fonts = Column(Boolean, default=False)
    checked_overlays = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class PreviewFrameComment(Base):
    """Comment on a preview frame."""

    __tablename__ = "preview_frame_comments"

    id = Column(String(36), primary_key=True, index=True)
    preview_id = Column(String(36), ForeignKey("previews.id"), nullable=False, index=True)
    timestamp = Column(Integer, nullable=False)  # milliseconds
    text = Column(Text, nullable=False)
    author = Column(String(255), nullable=True)
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
