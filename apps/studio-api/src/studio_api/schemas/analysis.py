"""Analysis schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class VideoMetricsResponse(BaseModel):
    """Video metrics response."""

    duration: int | None = None
    fps: int | None = None
    bitrate: int | None = None
    resolution: str | None = None
    codec: str | None = None
    audio_level: float | None = None
    silence_percentage: float | None = None
    scene_count: int | None = None
    face_count: int | None = None
    speech_rate: float | None = None

    class Config:
        from_attributes = True


class SceneResponse(BaseModel):
    """Scene response."""

    id: str
    start_time: int
    end_time: int
    summary: str | None = None
    emotion: str | None = None
    importance: float | None = None
    objects: str | None = None

    class Config:
        from_attributes = True


class TranscriptResponse(BaseModel):
    """Transcript response."""

    id: str
    start_time: int
    end_time: int
    text: str
    speaker: str | None = None
    confidence: float | None = None

    class Config:
        from_attributes = True


class SuggestionResponse(BaseModel):
    """Suggestion response."""

    id: str
    type: str
    title: str
    description: str
    reason: str | None = None
    severity: str
    confidence: float
    accepted: bool = False
    timestamp: int | None = None
    estimated_impact: float | None = None

    class Config:
        from_attributes = True


class AnalysisReportResponse(BaseModel):
    """Analysis report response."""

    id: str
    project_id: str
    video_id: str
    status: str
    overall_score: float | None = None
    viral_score: float | None = None
    engagement_score: float | None = None
    hook_score: float | None = None
    retention_score: float | None = None
    clarity_score: float | None = None
    audio_score: float | None = None
    visual_score: float | None = None
    summary: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AnalysisDetailResponse(BaseModel):
    """Complete analysis with all details."""

    report: AnalysisReportResponse
    metrics: VideoMetricsResponse | None = None
    scenes: list[SceneResponse] = Field(default_factory=list)
    transcript: list[TranscriptResponse] = Field(default_factory=list)
    suggestions: list[SuggestionResponse] = Field(default_factory=list)


class AnalysisStatusResponse(BaseModel):
    """Analysis status response."""

    status: str
    progress: int = 0  # 0-100
    current_stage: str | None = None
