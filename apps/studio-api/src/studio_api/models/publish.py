"""Publish models."""

from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text

from studio_api.database.base import Base


class PublishPlatform(str, Enum):
    """Supported publishing platforms."""

    YOUTUBE = "youtube"
    YOUTUBE_SHORTS = "youtube_shorts"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    LINKEDIN = "linkedin"
    PODCAST = "podcast"


class PublishStatus(str, Enum):
    """Publish job status."""

    PENDING = "pending"
    QUEUED = "queued"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PlatformAccount(Base):
    """Connected platform account."""

    __tablename__ = "platform_accounts"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), nullable=False, index=True)  # Project owner
    platform = Column(String(50), nullable=False)
    account_name = Column(String(255), nullable=False)
    account_id = Column(String(255), nullable=False)
    access_token = Column(Text, nullable=False)  # Encrypted in production
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    is_connected = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class PublishJob(Base):
    """Publish job to a platform."""

    __tablename__ = "publish_jobs"

    id = Column(String(36), primary_key=True, index=True)
    render_id = Column(String(36), ForeignKey("renders.id"), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    platform_account_id = Column(String(36), ForeignKey("platform_accounts.id"), nullable=False)
    platform = Column(String(50), nullable=False)
    status = Column(String(50), default="pending")
    scheduled_time = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)
    platform_video_id = Column(String(255), nullable=True)
    platform_url = Column(String(500), nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    metadata = Column(Text, nullable=True)  # JSON with platform-specific data
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class PublishMetadata(Base):
    """Platform-specific publish metadata."""

    __tablename__ = "publish_metadata"

    id = Column(String(36), primary_key=True, index=True)
    publish_job_id = Column(String(36), ForeignKey("publish_jobs.id"), nullable=False, index=True)
    platform = Column(String(50), nullable=False)
    # YouTube/YouTube Shorts
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)  # JSON array
    playlist_id = Column(String(255), nullable=True)
    visibility = Column(String(50), nullable=True)  # public, unlisted, private
    # Instagram/TikTok
    caption = Column(Text, nullable=True)
    hashtags = Column(Text, nullable=True)  # JSON array
    # TikTok
    privacy_level = Column(String(50), nullable=True)  # public, friends, private
    # LinkedIn
    share_with = Column(String(50), nullable=True)  # connections, public
    # Podcast
    episode_title = Column(String(255), nullable=True)
    episode_description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class PublishHistory(Base):
    """Complete publish history for analytics."""

    __tablename__ = "publish_history"

    id = Column(String(36), primary_key=True, index=True)
    publish_job_id = Column(String(36), ForeignKey("publish_jobs.id"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)  # queued, publishing, published, failed, retried
    status = Column(String(50), nullable=False)
    message = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)


class PlatformHealth(Base):
    """Platform API health status."""

    __tablename__ = "platform_health"

    id = Column(String(36), primary_key=True, index=True)
    platform = Column(String(50), nullable=False, index=True)
    is_healthy = Column(Boolean, default=True)
    last_check = Column(DateTime, default=datetime.utcnow, nullable=False)
    response_time_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
