"""Analytics and learning models."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text

from studio_api.database.base import Base


class DailyAnalytics(Base):
    """Daily performance analytics."""

    __tablename__ = "daily_analytics"

    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    views = Column(Integer, default=0)
    subscribers = Column(Integer, default=0)
    watch_time_minutes = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)
    retention_percent = Column(Float, nullable=True)
    ctr_percent = Column(Float, nullable=True)
    publishing_streak = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class AiLearning(Base):
    """AI learning insights from M14."""

    __tablename__ = "ai_learning"

    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    insight_type = Column(String(50), nullable=False)  # audience_preference, upload_time, video_length, etc.
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    value = Column(String(255), nullable=False)  # e.g., "9 PM", "8-12 minutes", "bright colors"
    confidence = Column(Float, nullable=True)  # 0-100
    impact_score = Column(Float, nullable=True)  # 0-100
    is_actionable = Column(String(50), default="high")  # high, medium, low
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class VideoComparison(Base):
    """Video comparison analysis."""

    __tablename__ = "video_comparisons"

    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    video_a_id = Column(String(36), nullable=False)
    video_b_id = Column(String(36), nullable=False)
    metric_name = Column(String(100), nullable=False)  # views, watch_time, ctr, etc.
    video_a_value = Column(Float, nullable=True)
    video_b_value = Column(Float, nullable=True)
    difference_percent = Column(Float, nullable=True)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Forecast(Base):
    """Performance forecast."""

    __tablename__ = "forecasts"

    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    forecast_type = Column(String(50), nullable=False)  # views, ctr, watch_time, revenue
    predicted_value = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=True)  # 0-100
    forecast_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ContentRecommendation(Base):
    """AI-generated content recommendations."""

    __tablename__ = "content_recommendations"

    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)  # trending, improvement, opportunity
    priority = Column(Integer, default=5)  # 1-10, higher = more important
    estimated_impact_percent = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class LearningData(Base):
    """M14 Learning Engine output."""

    __tablename__ = "learning_data"

    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    learning_category = Column(String(50), nullable=False)
    data = Column(Text, nullable=False)  # JSON with M14 insights
    accuracy = Column(Float, nullable=True)  # 0-100
    last_updated = Column(DateTime, default=datetime.utcnow, nullable=False)
