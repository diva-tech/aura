"""Creator Intelligence Platform schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CreatorProfileResponse(BaseModel):
    """Creator profile response."""

    id: str
    project_id: str
    preferred_editing_style: Optional[str] = None
    preferred_upload_schedule: Optional[str] = None
    preferred_platforms: Optional[str] = None
    typical_video_duration: Optional[int] = None
    audience_profile: Optional[str] = None
    publishing_frequency: Optional[str] = None
    favorite_thumbnail_style: Optional[str] = None
    favorite_hook_style: Optional[str] = None
    learning_confidence: float
    accepted_suggestions: int
    rejected_suggestions: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CreatorBriefResponse(BaseModel):
    """Creator brief response."""

    id: str
    project_id: str
    brief_date: datetime
    yesterday_views: int
    yesterday_views_change_pct: float
    yesterday_subscribers: int
    yesterday_revenue: float
    yesterday_watch_time_minutes: float
    yesterday_retention_pct: float
    yesterday_ctr_pct: float
    best_performing_video_id: Optional[str] = None
    worst_performing_video_id: Optional[str] = None
    top_opportunity: Optional[str] = None
    best_upload_time: Optional[str] = None
    pending_tasks: Optional[str] = None
    risk_alerts: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CreatorInsightResponse(BaseModel):
    """Creator insight response."""

    id: str
    project_id: str
    insight_type: str
    title: str
    description: str
    data_source: Optional[str] = None
    confidence: float
    actionable: str
    metadata: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AIExplanationResponse(BaseModel):
    """AI explanation response."""

    id: str
    project_id: str
    subject_type: str
    subject_id: Optional[str] = None
    operation: str
    reason: str
    confidence: float
    expected_improvement: Optional[str] = None
    data_sources: Optional[str] = None
    alternatives: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PerformancePredictionResponse(BaseModel):
    """Performance prediction response."""

    id: str
    project_id: str
    video_id: Optional[str] = None
    predicted_views: int
    predicted_ctr_pct: float
    predicted_watch_time_minutes: float
    predicted_revenue: float
    audience_match_pct: float
    upload_score: float
    confidence: float
    reasoning: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class VideoHealthScoreResponse(BaseModel):
    """Video health score response."""

    id: str
    project_id: str
    video_id: Optional[str] = None
    overall_score: float
    hook_score: float
    retention_score: float
    editing_score: float
    captions_score: float
    thumbnail_score: float
    seo_score: float
    cta_score: float
    storytelling_score: float
    pacing_score: float
    brand_consistency_score: float
    recommendations: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContentOpportunityResponse(BaseModel):
    """Content opportunity response."""

    id: str
    project_id: str
    opportunity_type: str
    title: str
    description: str
    demand_score: float
    competition_level: Optional[str] = None
    expected_views: int
    data_source: Optional[str] = None
    metadata: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ThumbnailInsightResponse(BaseModel):
    """Thumbnail insight response."""

    id: str
    project_id: str
    video_id: Optional[str] = None
    ctr_prediction: float
    visual_complexity_score: float
    text_contrast_score: float
    face_detection: Optional[str] = None
    emotion_score: float
    brand_consistency_score: float
    improvement_suggestions: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
