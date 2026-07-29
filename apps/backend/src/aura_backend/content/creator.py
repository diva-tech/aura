"""Creator Intelligence Layer: Platform-agnostic content opportunities and strategies.

Consumes Phase 2 semantic artifacts (Story, Highlights, etc.) and produces
ContentOpportunity, CreatorStrategy, and ContentBundle models for creators.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4


class PlatformType(StrEnum):
    """Supported creator platforms"""

    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    TWITCH = "twitch"
    PODCAST = "podcast"
    NEWSLETTER = "newsletter"
    BLOG = "blog"


class OpportunityType(StrEnum):
    """Types of content opportunities"""

    CLIP_EXTRACTION = "clip_extraction"  # Extract segment for short-form
    SERIES_POTENTIAL = "series_potential"  # Multi-part content series
    REPURPOSING = "repurposing"  # Adapt for different platform
    CROSS_PROMOTION = "cross_promotion"  # Use on multiple platforms
    ENGAGEMENT_HOOK = "engagement_hook"  # High engagement moment to feature
    EDUCATIONAL = "educational"  # Educational/tutorial extract
    ENTERTAINMENT = "entertainment"  # Entertainment-focused moment
    THOUGHT_LEADERSHIP = "thought_leadership"  # Expert commentary
    COMMUNITY_MOMENT = "community_moment"  # Shareable audience moment


class CreatorGoal(StrEnum):
    """Creator objectives"""

    GROW_AUDIENCE = "grow_audience"
    INCREASE_ENGAGEMENT = "increase_engagement"
    ESTABLISH_AUTHORITY = "establish_authority"
    DRIVE_CONVERSIONS = "drive_conversions"
    BUILD_COMMUNITY = "build_community"
    DIVERSIFY_PLATFORMS = "diversify_platforms"
    TEST_NEW_FORMAT = "test_new_format"


class ContentFormat(StrEnum):
    """Content format types"""

    SHORT_FORM = "short_form"  # <60 seconds
    MEDIUM_FORM = "medium_form"  # 1-15 minutes
    LONG_FORM = "long_form"  # >15 minutes
    CAROUSEL = "carousel"  # Multi-slide/image
    QUOTE_GRAPHIC = "quote_graphic"  # Quote + image
    ARTICLE = "article"  # Written content
    TRANSCRIPT = "transcript"  # Full text transcript
    INFOGRAPHIC = "infographic"  # Data visualization


@dataclass(frozen=True)
class EngagementMetrics:
    """Predicted engagement metrics for opportunity"""

    estimated_reach: int = 0  # Estimated audience reach
    engagement_rate: float = 0.5  # Predicted engagement (0-1)
    share_likelihood: float = 0.5  # Likelihood of shares/reposts
    comment_potential: float = 0.5  # Likelihood of comments
    conversion_potential: float = 0.5  # Potential to convert

    virality_score: float = 0.5  # Viral potential (0-1)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "estimated_reach": self.estimated_reach,
            "engagement_rate": self.engagement_rate,
            "share_likelihood": self.share_likelihood,
            "comment_potential": self.comment_potential,
            "conversion_potential": self.conversion_potential,
            "virality_score": self.virality_score,
        }


@dataclass(frozen=True)
class ContentOpportunity:
    """Immutable content opportunity discovered for creator.

    Identifies specific moments/angles from video that can be repurposed
    or featured to achieve creator goals.
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    video_id: str = ""

    opportunity_type: OpportunityType = OpportunityType.CLIP_EXTRACTION
    title: str = ""
    description: str = ""

    # What this opportunity uses from Phase 2
    highlight_ids: List[str] = field(default_factory=list)
    quote_ids: List[str] = field(default_factory=list)
    topic_ids: List[str] = field(default_factory=list)
    chapter_ids: List[str] = field(default_factory=list)

    # Timing
    start_timestamp: float = 0.0
    end_timestamp: float = 0.0

    # Platform fit
    platform_fit: Dict[PlatformType, float] = field(default_factory=dict)  # Platform → 0-1 fit score
    recommended_format: ContentFormat = ContentFormat.SHORT_FORM

    # Engagement prediction
    engagement_metrics: Optional[EngagementMetrics] = None

    # Rationale
    reasoning: str = ""  # Why this is an opportunity
    potential_goals: List[CreatorGoal] = field(default_factory=list)

    # Quality
    opportunity_score: float = 0.5  # 0-1: overall opportunity quality
    confidence: float = 0.5

    # Traceability
    observation_ids: List[str] = field(default_factory=list)  # M9 observations used
    metadata: Dict[str, Any] = field(default_factory=dict)

    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "video_id": self.video_id,
            "opportunity_type": self.opportunity_type.value,
            "title": self.title,
            "description": self.description,
            "highlight_count": len(self.highlight_ids),
            "quote_count": len(self.quote_ids),
            "topic_count": len(self.topic_ids),
            "start_timestamp": self.start_timestamp,
            "end_timestamp": self.end_timestamp,
            "recommended_format": self.recommended_format.value,
            "best_platform": max(self.platform_fit, key=self.platform_fit.get)
            if self.platform_fit
            else None,
            "opportunity_score": self.opportunity_score,
            "confidence": self.confidence,
            "engagement_metrics": self.engagement_metrics.to_dict()
            if self.engagement_metrics
            else None,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class DistributionStrategy:
    """Strategy for distributing content across platforms"""

    primary_platform: PlatformType = PlatformType.YOUTUBE
    secondary_platforms: List[PlatformType] = field(default_factory=list)

    # Timing
    publish_immediately: bool = True
    publish_sequence: List[PlatformType] = field(default_factory=list)  # Order of posting
    publish_delays_hours: List[int] = field(default_factory=list)  # Delays between posts

    # Customization per platform
    platform_customizations: Dict[PlatformType, Dict[str, str]] = field(default_factory=dict)

    # Engagement strategy
    engagement_hooks_per_platform: Dict[PlatformType, str] = field(default_factory=dict)
    hashtags_per_platform: Dict[PlatformType, List[str]] = field(default_factory=dict)

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary_platform": self.primary_platform.value,
            "secondary_platforms": [p.value for p in self.secondary_platforms],
            "publish_immediately": self.publish_immediately,
            "platform_count": len(self.secondary_platforms) + 1,
        }


@dataclass(frozen=True)
class CreatorStrategy:
    """Immutable strategy for content creation/repurposing.

    Synthesizes opportunities into coherent creator strategy with goals,
    timeline, and cross-platform distribution plan.
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    video_id: str = ""

    # Creator context
    creator_goals: List[CreatorGoal] = field(default_factory=list)
    target_audience: str = ""  # Description of audience

    # Opportunities included
    opportunity_ids: List[str] = field(default_factory=list)
    opportunity_count: int = 0

    # Strategy details
    primary_narrative: str = ""  # Core story/message to emphasize
    key_themes: List[str] = field(default_factory=list)  # Themes to highlight

    # Distribution
    distribution_strategy: Optional[DistributionStrategy] = None

    # Platform focus
    platform_priorities: Dict[PlatformType, float] = field(default_factory=dict)  # Platform → priority (0-1)

    # Timeline
    content_calendar_weeks: int = 4  # How many weeks to plan for

    # Quality
    strategy_score: float = 0.5  # 0-1: overall strategy quality
    confidence: float = 0.5

    # Rationale
    reasoning: str = ""  # Why this strategy makes sense
    expected_outcomes: str = ""  # What results to expect

    # Traceability
    observation_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "video_id": self.video_id,
            "creator_goals": [g.value for g in self.creator_goals],
            "opportunity_count": self.opportunity_count,
            "theme_count": len(self.key_themes),
            "platform_count": len(self.platform_priorities),
            "content_calendar_weeks": self.content_calendar_weeks,
            "strategy_score": self.strategy_score,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class ContentAsset:
    """Individual content asset within a bundle"""

    id: str = field(default_factory=lambda: str(uuid4()))

    # Content
    title: str = ""
    description: str = ""
    format: ContentFormat = ContentFormat.SHORT_FORM

    # Timing
    start_timestamp: float = 0.0
    end_timestamp: float = 0.0

    # Platform-specific
    platform: PlatformType = PlatformType.YOUTUBE
    platform_specific_metadata: Dict[str, str] = field(default_factory=dict)

    # What it includes
    highlight_ids: List[str] = field(default_factory=list)
    quote_ids: List[str] = field(default_factory=list)

    # Production notes
    production_notes: str = ""  # What creator should know
    hashtags: List[str] = field(default_factory=list)
    cta: Optional[str] = None  # Call to action

    # Tracking
    observation_ids: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "format": self.format.value,
            "platform": self.platform.value,
            "start_timestamp": self.start_timestamp,
            "end_timestamp": self.end_timestamp,
            "production_notes": self.production_notes,
        }


@dataclass(frozen=True)
class ContentBundle:
    """Immutable bundle of curated content for creator.

    Groups opportunities and assets into actionable content package
    optimized for specific platforms and creator goals.
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    video_id: str = ""

    # Bundle metadata
    title: str = ""
    description: str = ""
    theme: str = ""

    # What's included
    assets: List[ContentAsset] = field(default_factory=list)
    opportunity_ids: List[str] = field(default_factory=list)

    # Creator context
    target_platforms: List[PlatformType] = field(default_factory=list)
    creator_goals: List[CreatorGoal] = field(default_factory=list)

    # Content calendar
    week_1_posts: List[str] = field(default_factory=list)  # Asset IDs
    week_2_posts: List[str] = field(default_factory=list)
    week_3_posts: List[str] = field(default_factory=list)
    week_4_posts: List[str] = field(default_factory=list)

    # Quality
    bundle_score: float = 0.5  # 0-1: overall bundle quality
    completeness: float = 0.5  # How complete is this bundle (0-1)
    consistency: float = 0.5  # Thematic consistency (0-1)
    confidence: float = 0.5

    # Rationale
    reasoning: str = ""  # Why these assets together
    implementation_guide: str = ""  # How to use this bundle

    # Traceability
    observation_ids: List[str] = field(default_factory=list)
    strategy_id: Optional[str] = None  # CreatorStrategy this came from
    metadata: Dict[str, Any] = field(default_factory=dict)

    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "video_id": self.video_id,
            "title": self.title,
            "theme": self.theme,
            "asset_count": len(self.assets),
            "opportunity_count": len(self.opportunity_ids),
            "platform_count": len(self.target_platforms),
            "bundle_score": self.bundle_score,
            "completeness": self.completeness,
            "consistency": self.consistency,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
        }
