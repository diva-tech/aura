"""Analysis models."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text

from studio_api.database.base import Base


class AnalysisReport(Base):
    """Analysis report model."""

    __tablename__ = "analysis_reports"

    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    video_id = Column(String(36), ForeignKey("videos.id"), nullable=False, index=True)
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    overall_score = Column(Float, nullable=True)
    viral_score = Column(Float, nullable=True)
    engagement_score = Column(Float, nullable=True)
    hook_score = Column(Float, nullable=True)
    retention_score = Column(Float, nullable=True)
    clarity_score = Column(Float, nullable=True)
    audio_score = Column(Float, nullable=True)
    visual_score = Column(Float, nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Scene(Base):
    """Scene detection model."""

    __tablename__ = "scenes"

    id = Column(String(36), primary_key=True, index=True)
    report_id = Column(String(36), ForeignKey("analysis_reports.id"), nullable=False, index=True)
    start_time = Column(Integer, nullable=False)  # milliseconds
    end_time = Column(Integer, nullable=False)
    summary = Column(Text, nullable=True)
    emotion = Column(String(50), nullable=True)  # happy, sad, angry, etc.
    importance = Column(Float, nullable=True)  # 0-100
    objects = Column(Text, nullable=True)  # JSON array of detected objects
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Transcript(Base):
    """Transcript model."""

    __tablename__ = "transcripts"

    id = Column(String(36), primary_key=True, index=True)
    report_id = Column(String(36), ForeignKey("analysis_reports.id"), nullable=False, index=True)
    start_time = Column(Integer, nullable=False)  # milliseconds
    end_time = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    speaker = Column(String(100), nullable=True)
    confidence = Column(Float, nullable=True)  # 0-100
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Suggestion(Base):
    """AI suggestion model."""

    __tablename__ = "suggestions"

    id = Column(String(36), primary_key=True, index=True)
    report_id = Column(String(36), ForeignKey("analysis_reports.id"), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # cut_intro, remove_silence, zoom_speaker, etc.
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    reason = Column(Text, nullable=True)
    severity = Column(String(20), nullable=False)  # high, medium, low
    confidence = Column(Float, nullable=False)  # 0-100
    accepted = Column(Boolean, default=False)
    timestamp = Column(Integer, nullable=True)  # where suggestion applies (ms)
    estimated_impact = Column(Float, nullable=True)  # % improvement
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class VideoMetrics(Base):
    """Video metrics model."""

    __tablename__ = "video_metrics"

    id = Column(String(36), primary_key=True, index=True)
    report_id = Column(String(36), ForeignKey("analysis_reports.id"), nullable=False, index=True)
    duration = Column(Integer, nullable=True)  # seconds
    fps = Column(Integer, nullable=True)
    bitrate = Column(Integer, nullable=True)  # kbps
    resolution = Column(String(50), nullable=True)
    codec = Column(String(50), nullable=True)
    audio_level = Column(Float, nullable=True)  # dB
    silence_percentage = Column(Float, nullable=True)  # 0-100
    scene_count = Column(Integer, nullable=True)
    face_count = Column(Integer, nullable=True)
    speech_rate = Column(Float, nullable=True)  # words per minute
    text_coverage = Column(Float, nullable=True)  # % of video with text
    music_percentage = Column(Float, nullable=True)  # % with background music
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
