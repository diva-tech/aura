"""Database models."""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from studio_api.database.base import Base
from studio_api.models import analysis, edit_plan, preview, render  # noqa: F401


class Project(Base):
    """Project model."""

    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    target_platform = Column(String(50), nullable=False)
    language = Column(String(10), default="en")
    aspect_ratio = Column(String(20), default="16:9")
    status = Column(String(50), default="draft")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Video(Base):
    """Video model."""

    __tablename__ = "videos"

    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    duration = Column(Integer, nullable=True)  # in seconds
    resolution = Column(String(50), nullable=True)  # e.g., "1920x1080"
    codec = Column(String(50), nullable=True)
    fps = Column(Integer, nullable=True)
    size = Column(Integer, nullable=False)  # in bytes
    status = Column(String(50), default="uploaded")
    storage_path = Column(String(500), nullable=False)
    thumbnail_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


__all__ = ["Base", "Project", "Video"]
