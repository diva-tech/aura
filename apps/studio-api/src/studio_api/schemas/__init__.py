"""Request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    """Base project schema."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    target_platform: str = Field(..., description="YouTube, Instagram, TikTok, LinkedIn, Podcast")
    language: str = Field("en", max_length=10)
    aspect_ratio: str = Field("16:9", max_length=20)


class ProjectCreate(ProjectBase):
    """Create project schema."""

    pass


class ProjectUpdate(BaseModel):
    """Update project schema."""

    name: str | None = None
    description: str | None = None
    status: str | None = None


class ProjectResponse(ProjectBase):
    """Project response schema."""

    id: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VideoBase(BaseModel):
    """Base video schema."""

    filename: str = Field(..., min_length=1, max_length=255)


class VideoResponse(VideoBase):
    """Video response schema."""

    id: str
    project_id: str
    duration: int | None
    resolution: str | None
    codec: str | None
    fps: int | None
    size: int
    status: str
    storage_path: str
    thumbnail_path: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VideoMetadata(BaseModel):
    """Video metadata."""

    duration: int | None = None
    resolution: str | None = None
    codec: str | None = None
    fps: int | None = None


class AnalysisRequest(BaseModel):
    """Analysis request schema."""

    pass


class AnalysisResponse(BaseModel):
    """Analysis response schema."""

    status: str = "queued"
