"""Deterministic creator intelligence engines for Phase 3.

Consume Phase 2 semantic artifacts and produce platform-agnostic
creator opportunities, strategies, and content bundles.
All engines are stateless and deterministic.
"""

from typing import Any, Dict, List, Optional

from .creator import (
    ContentAsset,
    ContentBundle,
    ContentFormat,
    ContentOpportunity,
    CreatorGoal,
    CreatorStrategy,
    DistributionStrategy,
    EngagementMetrics,
    OpportunityType,
    PlatformType,
)
from .evidence import ContentEvidence
from .models import (
    Chapter,
    Highlight,
    Hook,
    Quote,
    Recommendation,
    Story,
    Topic,
)
from .scoring import ScoringDimension, ScoringPipeline, ScoringRegistry


class CreatorEngine:
    """Base class for creator intelligence engines."""

    def __init__(self, scoring_registry: Optional[ScoringRegistry] = None):
        self.scoring_pipeline = ScoringPipeline(scoring_registry or ScoringRegistry())

    def _create_evidence(
        self,
        opportunity_type: str,
        opportunity_id: str,
        phase2_ids: List[str],
        summary: str,
    ) -> ContentEvidence:
        """Create evidence linking creator output to Phase 2 artifacts"""
        return ContentEvidence(
            discovery_type=opportunity_type,
            discovery_id=opportunity_id,
            observation_ids=phase2_ids,
            evidence_quality=0.85,
            summary=summary,
            reasoning=f"Identified from {len(phase2_ids)} Phase 2 artifacts",
            analysis_method=self.__class__.__name__,
        )


# ============================================================================
# CONTENT OPPORTUNITY ENGINE
# ============================================================================


class ContentOpportunityEngine(CreatorEngine):
    """Identifies content opportunities from Phase 2 artifacts.

    Finds clips, moments, and angles that can be repurposed across platforms.
    """

    def analyze(
        self,
        story: Optional[Story] = None,
        highlights: Optional[List[Highlight]] = None,
        hooks: Optional[List[Hook]] = None,
        recommendations: Optional[List[Recommendation]] = None,
        topics: Optional[List[Topic]] = None,
    ) -> List[ContentOpportunity]:
        """Identify content opportunities from Phase 2 outputs"""
        if not highlights:
            return []

        opportunities = []

        # Opportunity 1: Top highlights as clips
        for highlight in highlights[:5]:
            platform_fit = {
                PlatformType.YOUTUBE: 0.9,  # YouTube Shorts
                PlatformType.TIKTOK: 0.95,
                PlatformType.INSTAGRAM: 0.9,
                PlatformType.LINKEDIN: 0.7,
            }

            engagement = EngagementMetrics(
                estimated_reach=100000,
                engagement_rate=0.08,
                share_likelihood=0.15,
                comment_potential=0.12,
                conversion_potential=0.05,
                virality_score=0.7,
            )

            opportunity = ContentOpportunity(
                opportunity_type=OpportunityType.CLIP_EXTRACTION,
                title=f"Clip: {highlight.title}",
                description=f"High-impact moment: {highlight.description}",
                highlight_ids=[highlight.id],
                start_timestamp=highlight.start_timestamp,
                end_timestamp=highlight.end_timestamp,
                platform_fit=platform_fit,
                recommended_format=ContentFormat.SHORT_FORM,
                engagement_metrics=engagement,
                reasoning="Peak engagement and emotional intensity",
                potential_goals=[
                    CreatorGoal.GROW_AUDIENCE,
                    CreatorGoal.INCREASE_ENGAGEMENT,
                ],
                opportunity_score=0.85,
                confidence=0.9,
                observation_ids=highlight.observation_ids,
            )

            opportunities.append(opportunity)

        # Opportunity 2: Opening hooks for engagement
        if hooks:
            for hook in hooks[:2]:
                platform_fit = {
                    PlatformType.YOUTUBE: 0.85,
                    PlatformType.TIKTOK: 0.9,
                    PlatformType.INSTAGRAM: 0.8,
                    PlatformType.LINKEDIN: 0.75,
                }

                engagement = EngagementMetrics(
                    estimated_reach=80000,
                    engagement_rate=0.12,
                    share_likelihood=0.18,
                    comment_potential=0.15,
                    conversion_potential=0.08,
                    virality_score=0.8,
                )

                opportunity = ContentOpportunity(
                    opportunity_type=OpportunityType.ENGAGEMENT_HOOK,
                    title=f"Hook: {hook.title}",
                    description=f"Attention-grabber using {hook.hook_type.value}",
                    hook_ids=[hook.id],
                    start_timestamp=hook.start_timestamp,
                    end_timestamp=hook.end_timestamp,
                    platform_fit=platform_fit,
                    recommended_format=ContentFormat.SHORT_FORM,
                    engagement_metrics=engagement,
                    reasoning=f"Strong {hook.hook_type.value} hook for audience engagement",
                    potential_goals=[CreatorGoal.GROW_AUDIENCE],
                    opportunity_score=0.8,
                    confidence=0.88,
                    observation_ids=hook.observation_ids,
                )

                opportunities.append(opportunity)

        # Opportunity 3: Topic-based educational content
        if topics:
            for topic in topics[:3]:
                platform_fit = {
                    PlatformType.YOUTUBE: 0.85,
                    PlatformType.LINKEDIN: 0.95,
                    PlatformType.BLOG: 0.9,
                    PlatformType.NEWSLETTER: 0.85,
                }

                engagement = EngagementMetrics(
                    estimated_reach=50000,
                    engagement_rate=0.06,
                    share_likelihood=0.22,
                    comment_potential=0.18,
                    conversion_potential=0.12,
                    virality_score=0.5,
                )

                opportunity = ContentOpportunity(
                    opportunity_type=OpportunityType.EDUCATIONAL,
                    title=f"Deep Dive: {topic.label}",
                    description=f"Educational content around {topic.label}",
                    topic_ids=[topic.id],
                    platform_fit=platform_fit,
                    recommended_format=ContentFormat.MEDIUM_FORM,
                    engagement_metrics=engagement,
                    reasoning=f"Topic '{topic.label}' has strong discussion potential",
                    potential_goals=[
                        CreatorGoal.ESTABLISH_AUTHORITY,
                        CreatorGoal.BUILD_COMMUNITY,
                    ],
                    opportunity_score=0.75,
                    confidence=0.82,
                    observation_ids=topic.observation_ids,
                )

                opportunities.append(opportunity)

        return opportunities


# ============================================================================
# CREATOR STRATEGY ENGINE
# ============================================================================


class CreatorStrategyEngine(CreatorEngine):
    """Builds creator strategy from opportunities."""

    def analyze(
        self,
        story: Optional[Story] = None,
        opportunities: Optional[List[ContentOpportunity]] = None,
        creator_goals: Optional[List[CreatorGoal]] = None,
    ) -> List[CreatorStrategy]:
        """Build strategy from opportunities"""
        if not opportunities:
            return []

        strategies = []

        # Strategy 1: Growth-focused (multi-platform)
        growth_opportunities = [o for o in opportunities if CreatorGoal.GROW_AUDIENCE in o.potential_goals]

        if growth_opportunities:
            distribution = DistributionStrategy(
                primary_platform=PlatformType.TIKTOK,
                secondary_platforms=[PlatformType.YOUTUBE, PlatformType.INSTAGRAM],
                publish_immediately=True,
                platform_customizations={
                    PlatformType.TIKTOK: {"max_length": "60s", "style": "trending"},
                    PlatformType.YOUTUBE: {"max_length": "90s", "style": "edited"},
                    PlatformType.INSTAGRAM: {"format": "reel", "aspect_ratio": "9:16"},
                },
            )

            strategy = CreatorStrategy(
                creator_goals=[CreatorGoal.GROW_AUDIENCE, CreatorGoal.INCREASE_ENGAGEMENT],
                opportunity_ids=[o.id for o in growth_opportunities],
                opportunity_count=len(growth_opportunities),
                primary_narrative=story.title if story else "Engaging narrative",
                key_themes=["engagement", "virality", "audience_growth"],
                distribution_strategy=distribution,
                platform_priorities={
                    PlatformType.TIKTOK: 1.0,
                    PlatformType.YOUTUBE: 0.8,
                    PlatformType.INSTAGRAM: 0.8,
                    PlatformType.LINKEDIN: 0.5,
                },
                content_calendar_weeks=4,
                strategy_score=0.85,
                confidence=0.88,
                reasoning="Multi-platform short-form strategy maximizes audience reach",
                expected_outcomes="Expected 300-500% increase in impressions over 4 weeks",
                observation_ids=[obs for opp in growth_opportunities for obs in opp.observation_ids],
            )

            strategies.append(strategy)

        # Strategy 2: Authority-focused (long-form, educational)
        authority_opportunities = [
            o for o in opportunities if CreatorGoal.ESTABLISH_AUTHORITY in o.potential_goals
        ]

        if authority_opportunities:
            distribution = DistributionStrategy(
                primary_platform=PlatformType.LINKEDIN,
                secondary_platforms=[PlatformType.BLOG, PlatformType.NEWSLETTER],
                publish_immediately=False,
                publish_delays_hours=[24, 48, 72],
            )

            strategy = CreatorStrategy(
                creator_goals=[CreatorGoal.ESTABLISH_AUTHORITY, CreatorGoal.BUILD_COMMUNITY],
                opportunity_ids=[o.id for o in authority_opportunities],
                opportunity_count=len(authority_opportunities),
                primary_narrative="Thought leadership and expert insights",
                key_themes=["expertise", "education", "community"],
                distribution_strategy=distribution,
                platform_priorities={
                    PlatformType.LINKEDIN: 1.0,
                    PlatformType.BLOG: 0.9,
                    PlatformType.NEWSLETTER: 0.8,
                },
                content_calendar_weeks=8,
                strategy_score=0.8,
                confidence=0.85,
                reasoning="Long-form educational strategy builds authority and trust",
                expected_outcomes="Expected 50% increase in thought leadership positioning",
                observation_ids=[obs for opp in authority_opportunities for obs in opp.observation_ids],
            )

            strategies.append(strategy)

        return strategies


# ============================================================================
# CONTENT BUNDLE ENGINE
# ============================================================================


class ContentBundleEngine(CreatorEngine):
    """Creates actionable content bundles for creators."""

    def analyze(
        self,
        opportunities: Optional[List[ContentOpportunity]] = None,
        strategy: Optional[CreatorStrategy] = None,
        highlights: Optional[List[Highlight]] = None,
        quotes: Optional[List[Quote]] = None,
    ) -> List[ContentBundle]:
        """Create content bundles from opportunities and strategy"""
        if not opportunities:
            return []

        bundles = []

        # Bundle 1: 4-week content calendar
        assets = []

        # Week 1: Top highlights as clips
        for i, highlight in enumerate((highlights or [])[:2]):
            asset = ContentAsset(
                title=f"Week 1 Clip {i + 1}: {highlight.title}",
                description=highlight.description,
                format=ContentFormat.SHORT_FORM,
                start_timestamp=highlight.start_timestamp,
                end_timestamp=highlight.end_timestamp,
                platform=PlatformType.TIKTOK,
                production_notes="Extract and edit this segment. Add trending music.",
                hashtags=["#content", "#trending", "#mustsee"],
                cta="Follow for more insights",
                observation_ids=highlight.observation_ids,
            )
            assets.append(asset)

        # Week 2-3: Quote graphics
        for i, quote in enumerate((quotes or [])[:2]):
            asset = ContentAsset(
                title=f"Quote Graphic {i + 1}: {quote.text[:30]}...",
                description=f"Memorable quote: '{quote.text}'",
                format=ContentFormat.QUOTE_GRAPHIC,
                start_timestamp=quote.start_timestamp,
                end_timestamp=quote.end_timestamp,
                platform=PlatformType.INSTAGRAM,
                production_notes=f"Create branded quote graphic with text: '{quote.text}'",
                hashtags=["#quote", "#wisdom", "#inspiration"],
                observation_ids=quote.observation_ids,
            )
            assets.append(asset)

        # Week 4: Recommendations
        for i, asset_opportunity in enumerate(opportunities[:2]):
            asset = ContentAsset(
                title=f"Recommendation {i + 1}: {asset_opportunity.title}",
                description=asset_opportunity.description,
                format=asset_opportunity.recommended_format,
                start_timestamp=asset_opportunity.start_timestamp,
                end_timestamp=asset_opportunity.end_timestamp,
                platform=asset_opportunity.primary_platform,
                production_notes=asset_opportunity.reasoning,
                cta="Watch the full video for more",
                observation_ids=asset_opportunity.observation_ids,
            )
            assets.append(asset)

        # Distribute assets across 4 weeks
        week_1 = [a.id for a in assets[0:1]]
        week_2 = [a.id for a in assets[1:3]]
        week_3 = [a.id for a in assets[3:4]]
        week_4 = [a.id for a in assets[4:]]

        bundle = ContentBundle(
            title="4-Week Content Campaign",
            description="Complete content bundle with clips, quotes, and recommendations",
            theme=strategy.primary_narrative if strategy else "Compelling content series",
            assets=assets,
            opportunity_ids=[o.id for o in opportunities[:5]],
            target_platforms=[PlatformType.TIKTOK, PlatformType.INSTAGRAM, PlatformType.YOUTUBE],
            creator_goals=strategy.creator_goals if strategy else [CreatorGoal.GROW_AUDIENCE],
            week_1_posts=week_1,
            week_2_posts=week_2,
            week_3_posts=week_3,
            week_4_posts=week_4,
            bundle_score=0.85,
            completeness=0.9,
            consistency=0.85,
            confidence=0.88,
            reasoning="Curated bundle balances short-form clips, quotes, and recommendations",
            implementation_guide="Post Week 1 content immediately, then one asset per platform per week",
            observation_ids=[obs for opp in opportunities for obs in opp.observation_ids],
            strategy_id=strategy.id if strategy else None,
        )

        bundles.append(bundle)

        return bundles


# ============================================================================
# CREATOR ENGINE REGISTRY
# ============================================================================


class CreatorEngineRegistry:
    """Registry for creator intelligence engines"""

    def __init__(self, scoring_registry: Optional[ScoringRegistry] = None):
        self.scoring_registry = scoring_registry or ScoringRegistry()
        self.engines: Dict[str, CreatorEngine] = {}
        self._register_defaults()

    def _register_defaults(self):
        """Register default engines"""
        self.engines["opportunities"] = ContentOpportunityEngine(self.scoring_registry)
        self.engines["strategy"] = CreatorStrategyEngine(self.scoring_registry)
        self.engines["bundles"] = ContentBundleEngine(self.scoring_registry)

    def get(self, engine_name: str) -> Optional[CreatorEngine]:
        """Get engine by name"""
        return self.engines.get(engine_name)

    def list_engines(self) -> List[str]:
        """List engine names"""
        return list(self.engines.keys())


def create_default_creator_registry(
    scoring_registry: Optional[ScoringRegistry] = None,
) -> CreatorEngineRegistry:
    """Factory for default creator engine registry"""
    return CreatorEngineRegistry(scoring_registry)
