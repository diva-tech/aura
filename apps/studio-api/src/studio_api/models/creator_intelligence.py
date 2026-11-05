"""Creator Intelligence Platform models."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text

from studio_api.database.base import Base


class CreatorProfile(Base):
    """Creator profile with preferences and learning."""

    __tablename__ = "creator_profiles"

    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    preferred_editing_style = Column(String(50), nullable=True)
    preferred_upload_schedule = Column(String(50), nullable=True)
    preferred_platforms = Column(Text, nullable=True)  # JSON list
    typical_video_duration = Column(Integer, nullable=True)  # seconds
    audience_profile = Column(Text, nullable=True)  # JSON
    publishing_frequency = Column(String(50), nullable=True)
    favorite_thumbnail_style = Column(String(100), nullable=True)
    favorite_hook_style = Column(String(100), nullable=True)
    learning_confidence = Column(Float, default=0.5)  # 0-1
    accepted_suggestions = Column(Integer, default=0)
    rejected_suggestions = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class CreatorBrief(Base):
    """Daily creator brief with performance summary."""

    __tablename__ = "creator_briefs"

    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    brief_date = Column(DateTime, nullable=False)
    yesterday_views = Column(Integer, default=0)
    yesterday_views_change_pct = Column(Float, default=0.0)
    yesterday_subscribers = Column(Integer, default=0)
    yesterday_revenue = Column(Float, default=0.0)
    yesterday_watch_time_minutes = Column(Float, default=0.0)
    yesterday_retention_pct = Column(Float, default=0.0)
    yesterday_ctr_pct = Column(Float, default=0.0)
    best_performing_video_id = Column(String(36), nullable=True)
    worst_performing_video_id = Column(String(36), nullable=True)
    top_opportunity = Column(Text, nullable=True)  # JSON with title, score
    best_upload_time = Column(String(20), nullable=True)  # HH:MM format
    pending_tasks = Column(Text, nullable=True)  # JSON list
    risk_alerts = Column(Text, nullable=True)  # JSON list
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class CreatorInsight(Base):
    """AI-generated insights and learning."""

    __tablename__ = "creator_insights"

    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    insight_type = Column(String(50), nullable=False)  # performance, opportunity, trend
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    data_source = Column(String(100), nullable=True)  # M9, M10, M14, analytics
    confidence = Column(Float, default=0.8)  # 0-1
    actionable = Column(String(50), default="pending")  # pending, accepted, rejected
    metadata = Column(Text, nullable=True)  # JSON
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class AIExplanation(Base):
    """Explanation for any AI recommendation or action."""

    __tablename__ = "ai_explanations"

    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    subject_type = Column(String(50), nullable=False)  # edit, thumbnail, title, publish
    subject_id = Column(String(36), nullable=True)  # ID of the subject (video, plan, etc.)
    operation = Column(String(255), nullable=False)  # e.g., "Remove Intro"
    reason = Column(Text, nullable=False)
    confidence = Column(Float, default=0.8)  # 0-1
    expected_improvement = Column(Text, nullable=True)  # JSON with metrics
    data_sources = Column(Text, nullable=True)  # JSON list
    alternatives = Column(Text, nullable=True)  # JSON list of alternatives
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class PerformancePrediction(Base):
    """Predicted performance metrics for upcoming videos."""

    __tablename__ = "performance_predictions"

    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    video_id = Column(String(36), ForeignKey("videos.id"), nullable=True)
    predicted_views = Column(Integer, default=0)
    predicted_ctr_pct = Column(Float, default=0.0)
    predicted_watch_time_minutes = Column(Float, default=0.0)
    predicted_revenue = Column(Float, default=0.0)
    audience_match_pct = Column(Float, default=0.0)
    upload_score = Column(Float, default=0.0)  # 0-100
    confidence = Column(Float, default=0.7)  # 0-1
    reasoning = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class VideoHealthScore(Base):
    """Content quality assessment across multiple dimensions."""

    __tablename__ = "video_health_scores"

    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    video_id = Column(String(36), ForeignKey("videos.id"), nullable=True)
    overall_score = Column(Float, default=0.0)  # 0-100
    hook_score = Column(Float, default=0.0)
    retention_score = Column(Float, default=0.0)
    editing_score = Column(Float, default=0.0)
    captions_score = Column(Float, default=0.0)
    thumbnail_score = Column(Float, default=0.0)
    seo_score = Column(Float, default=0.0)
    cta_score = Column(Float, default=0.0)
    storytelling_score = Column(Float, default=0.0)
    pacing_score = Column(Float, default=0.0)
    brand_consistency_score = Column(Float, default=0.0)
    recommendations = Column(Text, nullable=True)  # JSON list
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class ContentOpportunity(Base):
    """Recommended content ideas and topics."""

    __tablename__ = "content_opportunities"

    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    opportunity_type = Column(String(50), nullable=False)  # trend, keyword, series, seasonal
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    demand_score = Column(Float, default=0.0)  # 0-100
    competition_level = Column(String(20), nullable=True)  # low, medium, high
    expected_views = Column(Integer, default=0)
    data_source = Column(String(100), nullable=True)  # M10, trending, audience_request
    metadata = Column(Text, nullable=True)  # JSON
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ThumbnailInsight(Base):
    """Thumbnail analysis and improvement suggestions."""

    __tablename__ = "thumbnail_insights"

    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    video_id = Column(String(36), ForeignKey("videos.id"), nullable=True)
    ctr_prediction = Column(Float, default=0.0)
    visual_complexity_score = Column(Float, default=0.0)
    text_contrast_score = Column(Float, default=0.0)
    face_detection = Column(String(20), nullable=True)  # present, absent
    emotion_score = Column(Float, default=0.0)
    brand_consistency_score = Column(Float, default=0.0)
    improvement_suggestions = Column(Text, nullable=True)  # JSON list
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
