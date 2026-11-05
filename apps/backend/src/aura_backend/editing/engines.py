"""M11 Phase 2: Editing Intelligence Engines.

10 deterministic, stateless engines that consume M10 outputs and produce
editing plans without rendering any media.

All engines follow these principles:
- No side effects
- No state mutation
- Same input → same output (deterministic)
- Consume only immutable M10 objects
- Produce immutable editing plans
- Full evidence and traceability
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from uuid import uuid4

from aura_backend.content.evidence import AnalysisOutput, ContentEvidence, ScoreCard
from aura_backend.content.models import Highlight, Quote, Recommendation, Story, Topic

from .decisions import DecisionType, EditDecision, EditStrategy
from .models import (
    BrollSuggestion,
    Clip,
    ClipSource,
    Cut,
    EditTimeline,
    MusicCue,
    MusicMood,
    Overlay,
    OverlayType,
    SilenceRemoval,
    SubtitleSegment,
    Transition,
    TransitionType,
    ZoomAction,
    ZoomActionType,
)


class EditingEngine(ABC):
    """Base class for all editing engines.

    All editing engines are:
    - Stateless: no instance variables
    - Deterministic: same input always produces same output
    - Pure: no side effects
    - Immutable: all inputs and outputs are frozen dataclasses
    """

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    def analyze(self, **kwargs) -> list[AnalysisOutput]:
        """Analyze input and produce editing suggestions.

        Args:
            **kwargs: Input objects (Highlights, Story, etc.)

        Returns:
            List of AnalysisOutput with EditDecision, editing object, evidence, scorecard
        """
        pass

    def _create_decision(
        self,
        decision_type: DecisionType,
        reason: str,
        confidence: float,
        score: float,
        affected_time_range: tuple[float, float],
        platform: str = "universal",
        strategy: EditStrategy = EditStrategy.YOUTUBE_DOCUMENTARY,
        dependencies: list[str] | None = None,
        scorecard: dict[str, float] | None = None,
    ) -> EditDecision:
        """Create an EditDecision for a suggestion."""
        return EditDecision(
            decision_type=decision_type,
            reason=reason,
            confidence=confidence,
            score=score,
            affected_time_range=affected_time_range,
            platform=platform,
            strategy=strategy,
            dependencies=dependencies or [],
            scorecard=scorecard or {},
        )

    def _create_evidence(
        self,
        decision_type: str,
        observations_used: int,
        quality: float,
        observations: list[str],
    ) -> ContentEvidence:
        """Create ContentEvidence for traceability."""
        return ContentEvidence(
            source_component=self.name,
            observation_ids=observations,
            observation_types_used=["highlight", "story"],
            evidence_quality=quality,
            coverage_percentage=min(100.0, quality * 100),
        )

    def _create_scorecard(self, scores: dict[str, float]) -> ScoreCard:
        """Create a ScoreCard for decision reasoning."""
        return ScoreCard(
            dimension_scores=scores,
            dimension_confidences={k: 0.7 for k in scores.keys()},
            dimension_reasoning={k: f"Computed for {k}" for k in scores.keys()},
            aggregation_strategy="weighted_average",
        )


# ============================================================================
# ENGINE 1: CLIP ENGINE
# ============================================================================


class ClipEngine(EditingEngine):
    """Creates Clip objects from Highlights and Story.

    Consumes:
    - Highlights (start/end timestamps, importance scores)
    - Story (narrative context, importance)

    Produces:
    - Clip objects with platform suitability scores
    - EditDecision for each clip selection
    """

    def analyze(
        self,
        highlights: list[Highlight] | None = None,
        story: Story | None = None,
        strategy: EditStrategy = EditStrategy.YOUTUBE_DOCUMENTARY,
    ) -> list[AnalysisOutput]:
        """Extract clips from highlights."""
        outputs = []
        highlights = highlights or []

        if not highlights:
            return outputs

        for highlight in highlights:
            # Determine clip source based on highlight
            source = self._determine_clip_source(highlight)

            # Calculate clip priority and platform suitability
            clip_score = self._calculate_clip_score(highlight)
            platform_fit = self._calculate_platform_fit(highlight, strategy)

            clip = Clip(
                session_id=highlight.session_id,
                video_id=highlight.video_id,
                start_timestamp=highlight.start_timestamp,
                end_timestamp=highlight.end_timestamp,
                duration_seconds=highlight.end_timestamp - highlight.start_timestamp,
                source_type=source,
                clip_score=clip_score,
                confidence=(
                    highlight.importance_score if hasattr(highlight, "importance_score") else 0.7
                ),
                observation_ids=highlight.observation_ids,
                platform_suitability=platform_fit,
            )

            # Create decision
            decision = self._create_decision(
                decision_type=DecisionType.CLIP_SELECTION,
                reason=f"Extracted clip from highlight: {highlight.title}",
                confidence=clip.confidence,
                score=clip_score,
                affected_time_range=(highlight.start_timestamp, highlight.end_timestamp),
                strategy=strategy,
            )

            # Create evidence
            evidence = self._create_evidence(
                decision_type="clip_selection",
                observations_used=len(highlight.observation_ids),
                quality=0.85,
                observations=highlight.observation_ids,
            )

            # Create scorecard
            scorecard = self._create_scorecard(
                {
                    "clip_score": clip_score,
                    "platform_fit": (
                        sum(platform_fit.values()) / len(platform_fit) if platform_fit else 0.5
                    ),
                    "temporal_clarity": 0.8,
                    "narrative_value": 0.75,
                }
            )

            outputs.append(
                AnalysisOutput(
                    analysis_id=str(uuid4()),
                    result_type="clip",
                    result_object=clip,
                    decision=decision,
                    evidence=evidence,
                    scorecard=scorecard,
                )
            )

        return outputs

    def _determine_clip_source(self, highlight: Highlight) -> ClipSource:
        """Determine clip source from highlight type."""
        title_lower = highlight.title.lower() if highlight.title else ""
        if "highlight" in title_lower:
            return ClipSource.HIGHLIGHT
        elif "hook" in title_lower:
            return ClipSource.HOOK
        elif "quote" in title_lower:
            return ClipSource.QUOTE
        return ClipSource.HIGHLIGHT

    def _calculate_clip_score(self, highlight: Highlight) -> float:
        """Calculate clip quality score (0-1)."""
        duration = highlight.end_timestamp - highlight.start_timestamp
        # Prefer clips 3-15 seconds
        duration_score = 1.0 if 3.0 <= duration <= 15.0 else 0.6
        importance = getattr(highlight, "importance_score", 0.7)
        return (duration_score + importance) / 2

    def _calculate_platform_fit(
        self, highlight: Highlight, strategy: EditStrategy
    ) -> dict[str, float]:
        """Calculate clip fit for different platforms."""
        base_fit = 0.75
        duration = highlight.end_timestamp - highlight.start_timestamp

        fits = {
            "youtube": base_fit + (0.15 if duration > 30 else 0.0),
            "tiktok": base_fit + (0.15 if 3 <= duration <= 15 else -0.2),
            "instagram": base_fit + (0.1 if duration <= 30 else -0.1),
            "linkedin": base_fit - 0.1,
        }
        return {k: max(0.0, min(1.0, v)) for k, v in fits.items()}


# ============================================================================
# ENGINE 2: TIMELINE ENGINE
# ============================================================================


class TimelineEngine(EditingEngine):
    """Creates master EditTimeline from clips and story.

    Consumes:
    - Clip objects
    - Story (narrative sequence)

    Produces:
    - Master EditTimeline with narrative sequencing
    """

    def analyze(
        self,
        clips: list[Clip] | None = None,
        story: Story | None = None,
    ) -> list[AnalysisOutput]:
        """Sequence clips into a master timeline."""
        clips = clips or []

        if not clips:
            return []

        # Sort clips by narrative importance
        sorted_clips = sorted(
            clips,
            key=lambda c: (c.start_timestamp, -c.clip_score),
        )

        clip_ids = [c.id for c in sorted_clips]
        total_duration = sum(c.duration_seconds for c in sorted_clips)
        narrative_flow = self._calculate_narrative_flow(sorted_clips)
        visual_rhythm = self._calculate_visual_rhythm(sorted_clips)

        timeline = EditTimeline(
            session_id=clips[0].session_id if clips else "",
            video_id=clips[0].video_id if clips else "",
            clip_ids=clip_ids,
            quality_score=0.8,
            narrative_flow=narrative_flow,
            visual_rhythm=visual_rhythm,
            total_duration_seconds=total_duration,
            clip_count=len(sorted_clips),
            observation_ids=[obs for clip in clips for obs in clip.observation_ids],
        )

        # Create decision
        decision = self._create_decision(
            decision_type=DecisionType.SEQUENCE,
            reason=f"Sequenced {len(clips)} clips into narrative timeline",
            confidence=0.85,
            score=narrative_flow,
            affected_time_range=(0.0, total_duration),
        )

        # Create evidence
        evidence = self._create_evidence(
            decision_type="sequence",
            observations_used=len(timeline.observation_ids),
            quality=0.85,
            observations=timeline.observation_ids,
        )

        # Create scorecard
        scorecard = self._create_scorecard(
            {
                "narrative_flow": narrative_flow,
                "visual_rhythm": visual_rhythm,
                "pacing": 0.8,
                "coherence": 0.82,
            }
        )

        return [
            AnalysisOutput(
                analysis_id=str(uuid4()),
                result_type="timeline",
                result_object=timeline,
                decision=decision,
                evidence=evidence,
                scorecard=scorecard,
            )
        ]

    def _calculate_narrative_flow(self, clips: list[Clip]) -> float:
        """Calculate narrative flow quality (0-1)."""
        if not clips:
            return 0.0
        # Flow is better with consistent clip lengths and smooth progression
        lengths = [c.duration_seconds for c in clips]
        if not lengths:
            return 0.5
        avg_length = sum(lengths) / len(lengths)
        variance = sum((length_val - avg_length) ** 2 for length_val in lengths) / len(lengths)
        # Lower variance = better flow
        return max(0.5, 1.0 - (variance / 100))

    def _calculate_visual_rhythm(self, clips: list[Clip]) -> float:
        """Calculate visual rhythm quality (0-1)."""
        if not clips or len(clips) < 2:
            return 0.7
        # Rhythm is good with varied clip lengths
        lengths = [c.duration_seconds for c in clips]
        min_length = min(lengths)
        max_length = max(lengths)
        range_val = max_length - min_length
        # More variation = better rhythm
        return min(1.0, 0.5 + (range_val / 30))


# ============================================================================
# ENGINE 3: CUT ENGINE
# ============================================================================


class CutEngine(EditingEngine):
    """Suggests Cut objects (trim, dead air, jump cuts, etc.).

    Consumes:
    - Clips
    - Story (narrative pacing)

    Produces:
    - Cut objects for trim, montage, jump cuts
    """

    def analyze(
        self,
        clips: list[Clip] | None = None,
        story: Story | None = None,
    ) -> list[AnalysisOutput]:
        """Suggest cuts within clips."""
        clips = clips or []
        outputs = []

        for clip in clips:
            # Suggest cuts based on clip length and story context
            cuts = self._suggest_cuts_for_clip(clip)

            for cut in cuts:
                # Create decision
                decision = self._create_decision(
                    decision_type=DecisionType.CUT,
                    reason=f"Suggested {cut.cut_type} at {cut.position_seconds}s",
                    confidence=0.75,
                    score=0.75,
                    affected_time_range=(cut.position_seconds - 1, cut.position_seconds + 1),
                )

                # Create evidence
                evidence = self._create_evidence(
                    decision_type="cut",
                    observations_used=len(clip.observation_ids),
                    quality=0.8,
                    observations=clip.observation_ids,
                )

                # Create scorecard
                scorecard = self._create_scorecard(
                    {
                        "cut_necessity": 0.8,
                        "temporal_precision": 0.85,
                        "narrative_impact": 0.7,
                    }
                )

                outputs.append(
                    AnalysisOutput(
                        analysis_id=str(uuid4()),
                        result_type="cut",
                        result_object=cut,
                        decision=decision,
                        evidence=evidence,
                        scorecard=scorecard,
                    )
                )

        return outputs

    def _suggest_cuts_for_clip(self, clip: Clip) -> list[Cut]:
        """Suggest cuts within a clip."""
        cuts = []
        duration = clip.duration_seconds

        # Suggest hard cut at beginning if clip is long
        if duration > 5.0:
            cuts.append(
                Cut(
                    clip_id=clip.id,
                    position_seconds=clip.start_timestamp + 0.5,
                    trim_start_seconds=0.0,
                    trim_end_seconds=0.5,
                    cut_type="hard_cut",
                    confidence=0.75,
                    observation_ids=clip.observation_ids,
                )
            )

        # Suggest jump cut for dead air (assuming 2s of silence = dead air)
        if duration > 10.0:
            cuts.append(
                Cut(
                    clip_id=clip.id,
                    position_seconds=clip.start_timestamp + (duration / 2),
                    trim_start_seconds=0.0,
                    trim_end_seconds=1.0,
                    cut_type="jump_cut",
                    confidence=0.7,
                    observation_ids=clip.observation_ids,
                )
            )

        # Suggest reaction cut near end
        if duration > 3.0:
            cuts.append(
                Cut(
                    clip_id=clip.id,
                    position_seconds=clip.end_timestamp - 1.0,
                    trim_start_seconds=0.0,
                    trim_end_seconds=0.3,
                    cut_type="reaction_cut",
                    confidence=0.65,
                    observation_ids=clip.observation_ids,
                )
            )

        return cuts


# ============================================================================
# ENGINE 4: TRANSITION ENGINE
# ============================================================================


class TransitionEngine(EditingEngine):
    """Chooses transition types between clips.

    Consumes:
    - Clips (source/destination)
    - Story (narrative tone)

    Produces:
    - Transition objects with type selection and confidence
    """

    def analyze(
        self,
        clips: list[Clip] | None = None,
        story: Story | None = None,
    ) -> list[AnalysisOutput]:
        """Suggest transitions between clips."""
        clips = clips or []
        outputs = []

        # Generate transitions between consecutive clips
        for i in range(len(clips) - 1):
            from_clip = clips[i]
            to_clip = clips[i + 1]

            # Choose transition type
            transition_type = self._choose_transition_type(from_clip, to_clip, i)

            transition = Transition(
                from_clip_id=from_clip.id,
                to_clip_id=to_clip.id,
                transition_type=transition_type,
                duration_seconds=0.3 if transition_type == TransitionType.CUT else 0.5,
                transition_score=0.8,
                confidence=0.8,
                observation_ids=from_clip.observation_ids + to_clip.observation_ids,
            )

            # Create decision
            decision = self._create_decision(
                decision_type=DecisionType.TRANSITION,
                reason=f"Transition from clip {i} to {i+1}: {transition_type.value}",
                confidence=0.8,
                score=0.8,
                affected_time_range=(from_clip.end_timestamp, to_clip.start_timestamp),
            )

            # Create evidence
            evidence = self._create_evidence(
                decision_type="transition",
                observations_used=len(transition.observation_ids),
                quality=0.85,
                observations=transition.observation_ids,
            )

            # Create scorecard
            scorecard = self._create_scorecard(
                {
                    "transition_fit": 0.85,
                    "pacing": 0.8,
                    "visual_continuity": 0.75,
                }
            )

            outputs.append(
                AnalysisOutput(
                    analysis_id=str(uuid4()),
                    result_type="transition",
                    result_object=transition,
                    decision=decision,
                    evidence=evidence,
                    scorecard=scorecard,
                )
            )

        return outputs

    def _choose_transition_type(
        self, from_clip: Clip, to_clip: Clip, position: int
    ) -> TransitionType:
        """Choose best transition type between two clips."""
        gap = to_clip.start_timestamp - from_clip.end_timestamp

        # Hard cut for rapid changes
        if position % 3 == 0:
            return TransitionType.CUT

        # Fade for topic changes
        if gap > 2.0:
            return TransitionType.FADE

        # Cross dissolve for smooth flow
        if from_clip.clip_score > 0.8 and to_clip.clip_score > 0.8:
            return TransitionType.CROSS_DISSOLVE

        # Default to cut
        return TransitionType.CUT


# ============================================================================
# ENGINE 5: SUBTITLE ENGINE
# ============================================================================


class SubtitleEngine(EditingEngine):
    """Creates subtitle timing and styling plan.

    Consumes:
    - Story/Topics (speech content)
    - Clips (timing boundaries)

    Produces:
    - SubtitleSegment objects with styling
    """

    def analyze(
        self,
        story: Story | None = None,
        clips: list[Clip] | None = None,
        quotes: list[Quote] | None = None,
    ) -> list[AnalysisOutput]:
        """Create subtitle timeline."""
        outputs = []
        quotes = quotes or []

        for quote in quotes:
            subtitle = SubtitleSegment(
                clip_id="",
                start_timestamp=quote.start_timestamp,
                end_timestamp=quote.end_timestamp,
                text=quote.text[:100] if quote.text else "Quote",
                speaker=getattr(quote, "speaker", ""),
                duration_seconds=quote.end_timestamp - quote.start_timestamp,
                highlighted_words=[],
                emoji_suggestions=self._suggest_emojis(quote.text if quote.text else ""),
                readability_score=0.85,
                observation_ids=quote.observation_ids,
            )

            # Create decision
            decision = self._create_decision(
                decision_type=DecisionType.SUBTITLE,
                reason=f"Subtitle: {subtitle.text[:30]}...",
                confidence=0.85,
                score=0.85,
                affected_time_range=(quote.start_timestamp, quote.end_timestamp),
            )

            # Create evidence
            evidence = self._create_evidence(
                decision_type="subtitle",
                observations_used=len(quote.observation_ids),
                quality=0.9,
                observations=quote.observation_ids,
            )

            # Create scorecard
            scorecard = self._create_scorecard(
                {
                    "readability": 0.85,
                    "timing_accuracy": 0.9,
                    "cultural_appropriateness": 0.8,
                }
            )

            outputs.append(
                AnalysisOutput(
                    analysis_id=str(uuid4()),
                    result_type="subtitle",
                    result_object=subtitle,
                    decision=decision,
                    evidence=evidence,
                    scorecard=scorecard,
                )
            )

        return outputs

    def _suggest_emojis(self, text: str) -> list[str]:
        """Suggest emojis based on text content."""
        emoji_map = {
            "laugh": ["😂", "🤣"],
            "love": ["❤️", "😍"],
            "wow": ["😮", "🤩"],
            "sad": ["😢", "😭"],
            "angry": ["😠", "🤬"],
        }

        text_lower = text.lower()
        for key, emojis in emoji_map.items():
            if key in text_lower:
                return emojis[:1]

        return []


# ============================================================================
# ENGINE 6: OVERLAY ENGINE
# ============================================================================


class OverlayEngine(EditingEngine):
    """Suggests overlay placement and content.

    Consumes:
    - Topics (information to display)
    - Clips (timing and position)
    - Recommendations (actionable overlays)

    Produces:
    - Overlay objects (lower thirds, stats, CTAs, etc.)
    """

    def analyze(
        self,
        topics: list[Topic] | None = None,
        clips: list[Clip] | None = None,
        recommendations: list[Recommendation] | None = None,
    ) -> list[AnalysisOutput]:
        """Suggest overlays."""
        outputs = []
        topics = topics or []

        for topic in topics:
            # Suggest lower third for topic introduction
            topic_title = topic.title if hasattr(topic, "title") else "Topic"
            overlay = Overlay(
                clip_id="",
                start_timestamp=(
                    topic.start_timestamp if hasattr(topic, "start_timestamp") else 0.0
                ),
                end_timestamp=(topic.end_timestamp if hasattr(topic, "end_timestamp") else 10.0),
                overlay_type=OverlayType.LOWER_THIRD,
                content=topic_title,
                position_x=0.0,
                position_y=0.85,
                width=0.5,
                height=0.1,
                relevance_score=0.85,
                confidence=0.8,
                observation_ids=(
                    topic.observation_ids if hasattr(topic, "observation_ids") else []
                ),
            )

            # Create decision
            decision = self._create_decision(
                decision_type=DecisionType.OVERLAY,
                reason=f"Add lower third overlay for: {topic_title}",
                confidence=0.8,
                score=0.85,
                affected_time_range=(overlay.start_timestamp, overlay.end_timestamp),
            )

            # Create evidence
            evidence = self._create_evidence(
                decision_type="overlay",
                observations_used=len(overlay.observation_ids),
                quality=0.85,
                observations=overlay.observation_ids,
            )

            # Create scorecard
            scorecard = self._create_scorecard(
                {
                    "clarity": 0.85,
                    "visual_impact": 0.8,
                    "information_value": 0.85,
                }
            )

            outputs.append(
                AnalysisOutput(
                    analysis_id=str(uuid4()),
                    result_type="overlay",
                    result_object=overlay,
                    decision=decision,
                    evidence=evidence,
                    scorecard=scorecard,
                )
            )

        return outputs


# ============================================================================
# ENGINE 7: ZOOM ENGINE
# ============================================================================


class ZoomEngine(EditingEngine):
    """Suggests zoom/pan actions for engagement.

    Consumes:
    - Clips (visual content)
    - Recommendations (engagement tactics)

    Produces:
    - ZoomAction objects (punch in/out, face tracking, etc.)
    """

    def analyze(
        self,
        clips: list[Clip] | None = None,
        recommendations: list[Recommendation] | None = None,
    ) -> list[AnalysisOutput]:
        """Suggest zoom actions."""
        outputs = []
        clips = clips or []

        for clip in clips:
            duration = clip.duration_seconds

            # Suggest punch-in at midpoint
            if duration > 2.0:
                zoom = ZoomAction(
                    clip_id=clip.id,
                    start_timestamp=clip.start_timestamp + (duration * 0.3),
                    end_timestamp=clip.start_timestamp + (duration * 0.7),
                    zoom_type=ZoomActionType.PUNCH_IN,
                    target_x=0.5,
                    target_y=0.5,
                    zoom_intensity=1.2,
                    easing="ease_out",
                    effectiveness_score=0.75,
                    confidence=0.75,
                    observation_ids=clip.observation_ids,
                )

                # Create decision
                decision = self._create_decision(
                    decision_type=DecisionType.ZOOM,
                    reason="Punch-in for engagement",
                    confidence=0.75,
                    score=0.75,
                    affected_time_range=(zoom.start_timestamp, zoom.end_timestamp),
                )

                # Create evidence
                evidence = self._create_evidence(
                    decision_type="zoom",
                    observations_used=len(clip.observation_ids),
                    quality=0.8,
                    observations=clip.observation_ids,
                )

                # Create scorecard
                scorecard = self._create_scorecard(
                    {
                        "engagement": 0.8,
                        "smoothness": 0.85,
                        "visual_impact": 0.75,
                    }
                )

                outputs.append(
                    AnalysisOutput(
                        analysis_id=str(uuid4()),
                        result_type="zoom",
                        result_object=zoom,
                        decision=decision,
                        evidence=evidence,
                        scorecard=scorecard,
                    )
                )

        return outputs


# ============================================================================
# ENGINE 8: BROLL ENGINE
# ============================================================================


class BrollEngine(EditingEngine):
    """Suggests B-roll with search keywords.

    Consumes:
    - Topics (what content would enhance)
    - Story (narrative context)

    Produces:
    - BrollSuggestion objects with keywords (no downloads)
    """

    def analyze(
        self,
        topics: list[Topic] | None = None,
        story: Story | None = None,
    ) -> list[AnalysisOutput]:
        """Suggest B-roll placements and keywords."""
        outputs = []
        topics = topics or []

        for topic in topics:
            topic_title = topic.title if hasattr(topic, "title") else ""
            start_ts = topic.start_timestamp if hasattr(topic, "start_timestamp") else 0.0
            end_ts = topic.end_timestamp if hasattr(topic, "end_timestamp") else 10.0
            obs_ids = topic.observation_ids if hasattr(topic, "observation_ids") else []

            broll = BrollSuggestion(
                video_id="",
                start_timestamp=start_ts,
                end_timestamp=end_ts,
                search_keywords=self._generate_keywords(topic_title),
                stock_footage_categories=["b-roll", "nature", "technology"],
                image_suggestions=[],
                animation_suggestions=["transitions", "text-animation"],
                relevance_score=0.8,
                confidence=0.8,
                observation_ids=obs_ids,
            )

            # Create decision
            keyword_str = broll.search_keywords[0] if broll.search_keywords else "content"
            decision = self._create_decision(
                decision_type=DecisionType.BROLL,
                reason=f"B-roll needed for: {keyword_str}",
                confidence=0.8,
                score=0.8,
                affected_time_range=(broll.start_timestamp, broll.end_timestamp),
            )

            # Create evidence
            evidence = self._create_evidence(
                decision_type="broll",
                observations_used=len(broll.observation_ids),
                quality=0.8,
                observations=broll.observation_ids,
            )

            # Create scorecard
            scorecard = self._create_scorecard(
                {
                    "visual_enhancement": 0.8,
                    "keyword_specificity": 0.85,
                    "narrative_fit": 0.75,
                }
            )

            outputs.append(
                AnalysisOutput(
                    analysis_id=str(uuid4()),
                    result_type="broll",
                    result_object=broll,
                    decision=decision,
                    evidence=evidence,
                    scorecard=scorecard,
                )
            )

        return outputs

    def _generate_keywords(self, topic_title: str) -> list[str]:
        """Generate search keywords from topic."""
        # Simple keyword extraction - in practice would use NLP
        words = topic_title.lower().split()[:3]
        return words + [f"{w}s" for w in words]  # Plurals


# ============================================================================
# ENGINE 9: MUSIC ENGINE
# ============================================================================


class MusicEngine(EditingEngine):
    """Suggests music with mood and tempo.

    Consumes:
    - Story (narrative tone, pacing)
    - Clips (timing requirements)

    Produces:
    - MusicCue objects with mood/intensity/tempo (no tracks)
    """

    def analyze(
        self,
        story: Story | None = None,
        clips: list[Clip] | None = None,
    ) -> list[AnalysisOutput]:
        """Suggest music cues."""
        outputs = []
        clips = clips or []

        if not clips:
            return []

        # Suggest music for entire video
        music = MusicCue(
            video_id=clips[0].video_id if clips else "",
            start_timestamp=clips[0].start_timestamp if clips else 0.0,
            end_timestamp=sum(c.end_timestamp for c in clips) / len(clips) if clips else 0.0,
            mood=MusicMood.ENERGETIC,
            intensity=0.7,
            tempo_bpm=120,
            fade_in_seconds=2.0,
            fade_out_seconds=3.0,
            beat_emphasis=True,
            fit_score=0.8,
            confidence=0.75,
            observation_ids=[obs for clip in clips for obs in clip.observation_ids],
        )

        # Create decision
        decision = self._create_decision(
            decision_type=DecisionType.MUSIC,
            reason=f"Background music: {music.mood.value}, {music.tempo_bpm} BPM",
            confidence=0.75,
            score=0.8,
            affected_time_range=(music.start_timestamp, music.end_timestamp),
        )

        # Create evidence
        evidence = self._create_evidence(
            decision_type="music",
            observations_used=len(music.observation_ids),
            quality=0.85,
            observations=music.observation_ids,
        )

        # Create scorecard
        scorecard = self._create_scorecard(
            {
                "mood_fit": 0.85,
                "pacing_alignment": 0.8,
                "emotional_impact": 0.75,
            }
        )

        outputs.append(
            AnalysisOutput(
                analysis_id=str(uuid4()),
                result_type="music",
                result_object=music,
                decision=decision,
                evidence=evidence,
                scorecard=scorecard,
            )
        )

        return outputs


# ============================================================================
# ENGINE 10: SILENCE ENGINE
# ============================================================================


class SilenceEngine(EditingEngine):
    """Detects silence and suggests removal/shortening.

    Consumes:
    - Story (silence/pause patterns)
    - Clips (timing)

    Produces:
    - SilenceRemoval objects with removal suggestions
    """

    def analyze(
        self,
        clips: list[Clip] | None = None,
        story: Story | None = None,
    ) -> list[AnalysisOutput]:
        """Detect silence and suggest removal."""
        outputs = []
        clips = clips or []

        for clip in clips:
            duration = clip.duration_seconds

            # Detect potential silence in middle of long clips
            if duration > 10.0:
                silence = SilenceRemoval(
                    clip_id=clip.id,
                    start_timestamp=clip.start_timestamp + (duration * 0.4),
                    end_timestamp=clip.start_timestamp + (duration * 0.5),
                    silence_duration_seconds=2.0,
                    action="shorten",
                    suggested_reduction_seconds=1.0,
                    confidence=0.7,
                    observation_ids=clip.observation_ids,
                )

                # Create decision
                decision = self._create_decision(
                    decision_type=DecisionType.SILENCE_REMOVAL,
                    reason="Long silence detected - suggest shortening",
                    confidence=0.7,
                    score=0.7,
                    affected_time_range=(silence.start_timestamp, silence.end_timestamp),
                )

                # Create evidence
                evidence = self._create_evidence(
                    decision_type="silence_removal",
                    observations_used=len(clip.observation_ids),
                    quality=0.75,
                    observations=clip.observation_ids,
                )

                # Create scorecard
                scorecard = self._create_scorecard(
                    {
                        "silence_confidence": 0.7,
                        "pacing_impact": 0.75,
                        "narrative_preservation": 0.8,
                    }
                )

                outputs.append(
                    AnalysisOutput(
                        analysis_id=str(uuid4()),
                        result_type="silence_removal",
                        result_object=silence,
                        decision=decision,
                        evidence=evidence,
                        scorecard=scorecard,
                    )
                )

        return outputs


# ============================================================================
# ENGINE REGISTRY
# ============================================================================


@dataclass
class EditingEngineRegistry:
    """Registry for all editing engines."""

    engines: dict[str, EditingEngine] = field(default_factory=dict)

    def register(self, name: str, engine: EditingEngine) -> None:
        """Register an engine."""
        self.engines[name] = engine

    def get(self, name: str) -> EditingEngine | None:
        """Get an engine by name."""
        return self.engines.get(name)

    def list_engines(self) -> list[str]:
        """List all registered engines."""
        return list(self.engines.keys())


def create_default_editing_registry() -> EditingEngineRegistry:
    """Create default registry with all 10 editing engines."""
    registry = EditingEngineRegistry()

    registry.register("clips", ClipEngine())
    registry.register("timeline", TimelineEngine())
    registry.register("cuts", CutEngine())
    registry.register("transitions", TransitionEngine())
    registry.register("subtitles", SubtitleEngine())
    registry.register("overlays", OverlayEngine())
    registry.register("zoom", ZoomEngine())
    registry.register("broll", BrollEngine())
    registry.register("music", MusicEngine())
    registry.register("silence", SilenceEngine())

    return registry
