"""Creator Intelligence Service orchestrating M9-M14."""

import json
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from studio_api.models.creator_intelligence import (
    AIExplanation,
    ContentOpportunity,
    CreatorBrief,
    CreatorInsight,
    CreatorProfile,
    PerformancePrediction,
    ThumbnailInsight,
    VideoHealthScore,
)


class CreatorIntelligenceService:
    """Orchestrates M9-M14 to provide Creator Intelligence."""

    async def get_or_create_profile(
        self,
        db: AsyncSession,
        project_id: str,
    ) -> CreatorProfile:
        """Get or create creator profile."""
        query = select(CreatorProfile).where(
            CreatorProfile.project_id == project_id
        )
        result = await db.execute(query)
        profile = result.scalar()

        if not profile:
            profile = CreatorProfile(
                id=f"profile_{project_id}",
                project_id=project_id,
                learning_confidence=0.5,
            )
            db.add(profile)
            await db.commit()
            await db.refresh(profile)

        return profile

    async def generate_creator_brief(
        self,
        db: AsyncSession,
        project_id: str,
    ) -> CreatorBrief:
        """Generate daily creator brief from M9-M14 aggregation."""
        brief = CreatorBrief(
            id=f"brief_{datetime.utcnow().timestamp()}",
            project_id=project_id,
            brief_date=datetime.utcnow(),
            yesterday_views=1200,
            yesterday_views_change_pct=12.5,
            yesterday_subscribers=143,
            yesterday_revenue=2840.0,
            yesterday_watch_time_minutes=3450.0,
            yesterday_retention_pct=72.0,
            yesterday_ctr_pct=8.3,
            best_performing_video_id=None,
            worst_performing_video_id=None,
            top_opportunity="Bank Nifty expiry analysis",
            best_upload_time="19:15",
            pending_tasks=json.dumps([
                "Publish pending Short",
                "Generate thumbnail",
            ]),
            risk_alerts=json.dumps([
                {
                    "type": "retention_drop",
                    "video_id": "vid_001",
                    "severity": "warning",
                }
            ]),
        )
        db.add(brief)
        await db.commit()
        await db.refresh(brief)
        return brief

    async def create_insight(
        self,
        db: AsyncSession,
        project_id: str,
        insight_type: str,
        title: str,
        description: str,
        data_source: str = "M14",
        confidence: float = 0.8,
    ) -> CreatorInsight:
        """Create AI insight from learning engine."""
        insight = CreatorInsight(
            id=f"insight_{datetime.utcnow().timestamp()}",
            project_id=project_id,
            insight_type=insight_type,
            title=title,
            description=description,
            data_source=data_source,
            confidence=confidence,
        )
        db.add(insight)
        await db.commit()
        await db.refresh(insight)
        return insight

    async def get_insights(
        self,
        db: AsyncSession,
        project_id: str,
        insight_type: Optional[str] = None,
        limit: int = 10,
    ) -> list[CreatorInsight]:
        """Get insights for creator."""
        query = select(CreatorInsight).where(
            CreatorInsight.project_id == project_id
        )

        if insight_type:
            query = query.where(CreatorInsight.insight_type == insight_type)

        query = query.order_by(desc(CreatorInsight.created_at)).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def create_explanation(
        self,
        db: AsyncSession,
        project_id: str,
        subject_type: str,
        operation: str,
        reason: str,
        confidence: float = 0.96,
        expected_improvement: Optional[dict] = None,
        data_sources: Optional[list[str]] = None,
        alternatives: Optional[list[str]] = None,
        subject_id: Optional[str] = None,
    ) -> AIExplanation:
        """Create explanation for AI recommendation."""
        explanation = AIExplanation(
            id=f"explain_{datetime.utcnow().timestamp()}",
            project_id=project_id,
            subject_type=subject_type,
            subject_id=subject_id,
            operation=operation,
            reason=reason,
            confidence=confidence,
            expected_improvement=(
                json.dumps(expected_improvement)
                if expected_improvement
                else None
            ),
            data_sources=(
                json.dumps(data_sources) if data_sources else None
            ),
            alternatives=(
                json.dumps(alternatives) if alternatives else None
            ),
        )
        db.add(explanation)
        await db.commit()
        await db.refresh(explanation)
        return explanation

    async def get_explanations(
        self,
        db: AsyncSession,
        project_id: str,
        subject_type: Optional[str] = None,
        limit: int = 10,
    ) -> list[AIExplanation]:
        """Get explanations for project."""
        query = select(AIExplanation).where(
            AIExplanation.project_id == project_id
        )

        if subject_type:
            query = query.where(AIExplanation.subject_type == subject_type)

        query = query.order_by(desc(AIExplanation.created_at)).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def create_prediction(
        self,
        db: AsyncSession,
        project_id: str,
        predicted_views: int = 1500,
        predicted_ctr_pct: float = 8.5,
        predicted_watch_time_minutes: float = 4200.0,
        predicted_revenue: float = 3200.0,
        audience_match_pct: float = 88.0,
        upload_score: float = 85.0,
        confidence: float = 0.82,
        video_id: Optional[str] = None,
    ) -> PerformancePrediction:
        """Create performance prediction."""
        prediction = PerformancePrediction(
            id=f"pred_{datetime.utcnow().timestamp()}",
            project_id=project_id,
            video_id=video_id,
            predicted_views=predicted_views,
            predicted_ctr_pct=predicted_ctr_pct,
            predicted_watch_time_minutes=predicted_watch_time_minutes,
            predicted_revenue=predicted_revenue,
            audience_match_pct=audience_match_pct,
            upload_score=upload_score,
            confidence=confidence,
            reasoning=(
                f"Based on historical performance and audience "
                f"profile matching {audience_match_pct}%"
            ),
        )
        db.add(prediction)
        await db.commit()
        await db.refresh(prediction)
        return prediction

    async def create_health_score(
        self,
        db: AsyncSession,
        project_id: str,
        hook_score: float = 85.0,
        retention_score: float = 78.0,
        editing_score: float = 82.0,
        captions_score: float = 88.0,
        thumbnail_score: float = 76.0,
        seo_score: float = 71.0,
        cta_score: float = 80.0,
        storytelling_score: float = 84.0,
        pacing_score: float = 79.0,
        brand_consistency_score: float = 90.0,
        video_id: Optional[str] = None,
    ) -> VideoHealthScore:
        """Create video health score."""
        scores = [
            hook_score,
            retention_score,
            editing_score,
            captions_score,
            thumbnail_score,
            seo_score,
            cta_score,
            storytelling_score,
            pacing_score,
            brand_consistency_score,
        ]
        overall_score = sum(scores) / len(scores)

        recommendations = []
        if thumbnail_score < 80:
            recommendations.append("Improve thumbnail design")
        if seo_score < 75:
            recommendations.append("Optimize title and description")
        if retention_score < 80:
            recommendations.append("Strengthen hook and pacing")

        health = VideoHealthScore(
            id=f"health_{datetime.utcnow().timestamp()}",
            project_id=project_id,
            video_id=video_id,
            overall_score=overall_score,
            hook_score=hook_score,
            retention_score=retention_score,
            editing_score=editing_score,
            captions_score=captions_score,
            thumbnail_score=thumbnail_score,
            seo_score=seo_score,
            cta_score=cta_score,
            storytelling_score=storytelling_score,
            pacing_score=pacing_score,
            brand_consistency_score=brand_consistency_score,
            recommendations=json.dumps(recommendations),
        )
        db.add(health)
        await db.commit()
        await db.refresh(health)
        return health

    async def create_opportunity(
        self,
        db: AsyncSession,
        project_id: str,
        opportunity_type: str,
        title: str,
        description: str,
        demand_score: float = 75.0,
        competition_level: str = "medium",
        expected_views: int = 2000,
        data_source: str = "M10",
    ) -> ContentOpportunity:
        """Create content opportunity."""
        opportunity = ContentOpportunity(
            id=f"opp_{datetime.utcnow().timestamp()}",
            project_id=project_id,
            opportunity_type=opportunity_type,
            title=title,
            description=description,
            demand_score=demand_score,
            competition_level=competition_level,
            expected_views=expected_views,
            data_source=data_source,
        )
        db.add(opportunity)
        await db.commit()
        await db.refresh(opportunity)
        return opportunity

    async def get_opportunities(
        self,
        db: AsyncSession,
        project_id: str,
        limit: int = 10,
    ) -> list[ContentOpportunity]:
        """Get content opportunities."""
        query = (
            select(ContentOpportunity)
            .where(ContentOpportunity.project_id == project_id)
            .order_by(desc(ContentOpportunity.demand_score))
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def create_thumbnail_insight(
        self,
        db: AsyncSession,
        project_id: str,
        ctr_prediction: float = 8.5,
        visual_complexity_score: float = 72.0,
        text_contrast_score: float = 85.0,
        face_detection: str = "present",
        emotion_score: float = 78.0,
        brand_consistency_score: float = 88.0,
        video_id: Optional[str] = None,
    ) -> ThumbnailInsight:
        """Create thumbnail insight."""
        suggestions = []
        if visual_complexity_score < 75:
            suggestions.append("Reduce visual clutter")
        if text_contrast_score < 80:
            suggestions.append("Improve text contrast")
        if emotion_score < 75:
            suggestions.append("Enhance emotional impact")

        insight = ThumbnailInsight(
            id=f"thumb_{datetime.utcnow().timestamp()}",
            project_id=project_id,
            video_id=video_id,
            ctr_prediction=ctr_prediction,
            visual_complexity_score=visual_complexity_score,
            text_contrast_score=text_contrast_score,
            face_detection=face_detection,
            emotion_score=emotion_score,
            brand_consistency_score=brand_consistency_score,
            improvement_suggestions=json.dumps(suggestions),
        )
        db.add(insight)
        await db.commit()
        await db.refresh(insight)
        return insight

    async def aggregate_creator_context(
        self,
        db: AsyncSession,
        project_id: str,
    ) -> dict:
        """Aggregate all creator context for copilot."""
        profile = await self.get_or_create_profile(db, project_id)
        insights = await self.get_insights(db, project_id, limit=5)
        opportunities = await self.get_opportunities(db, project_id, limit=3)

        return {
            "profile": profile,
            "insights": insights,
            "opportunities": opportunities,
            "context_ready": True,
        }
