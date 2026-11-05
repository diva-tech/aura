"""M12 Phase 2: Rendering Execution Engines.

10 stateless, deterministic rendering components that execute EditPlan operations.
All components are provider-agnostic via the RendererProvider interface.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from aura_backend.editing import (
    Clip,
    Cut,
    EditPlan,
    Overlay,
    SilenceRemoval,
    SubtitleSegment,
    Transition,
    ZoomAction,
)

from .context import RenderContext
from .models import AnalysisOutput, RenderedAsset, ValidationResult
from .providers import RendererProvider


class RenderingEngine(ABC):
    """Base class for all rendering engines.

    All rendering engines are:
    - Stateless: no instance variables
    - Deterministic: same input always produces same output
    - Pure: no side effects
    - Immutable: all inputs and outputs are frozen dataclasses
    - Provider-agnostic: work with any RendererProvider
    """

    def __init__(self, provider: RendererProvider):
        """Initialize with a rendering provider"""
        self._provider = provider

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @property
    def provider(self) -> RendererProvider:
        return self._provider

    @abstractmethod
    async def render(
        self,
        edit_plan: EditPlan,
        context: RenderContext,
    ) -> RenderedAsset:
        """Execute rendering operation.

        Args:
            edit_plan: EditPlan with rendering specifications
            context: RenderContext with execution parameters

        Returns:
            RenderedAsset with rendered output
        """
        pass


# ============================================================================
# RENDERER 1: CLIP RENDERER
# ============================================================================


class ClipRenderer(RenderingEngine):
    """Renders individual video clips from EditPlan."""

    async def render(
        self,
        edit_plan: EditPlan,
        context: RenderContext,
    ) -> RenderedAsset:
        """Render clips from edit plan.

        Processes each clip in the edit plan through the provider.
        """
        if not edit_plan.clips:
            raise ValueError("EditPlan has no clips to render")

        # Render first clip as example (Phase 2 would batch)
        clip = edit_plan.clips[0]

        asset = await self.provider.render_clip(
            source_path=f"{context.cache_path}/{clip.id}.mp4",
            start_seconds=clip.start_timestamp,
            end_seconds=clip.end_timestamp,
            output_path=f"{context.working_path}/clip_{clip.id}.mp4",
            resolution=context.target_resolution,
            fps=context.target_fps,
            codec=context.target_codec,
            bitrate=context.target_bitrate,
        )

        return asset


# ============================================================================
# RENDERER 2: TRANSITION RENDERER
# ============================================================================


class TransitionRenderer(RenderingEngine):
    """Renders transitions between clips."""

    async def render(
        self,
        edit_plan: EditPlan,
        context: RenderContext,
    ) -> RenderedAsset:
        """Render transitions.

        Applies transitions between consecutive clips.
        """
        if not edit_plan.transitions:
            raise ValueError("EditPlan has no transitions to render")

        # Render first transition (Phase 2 would batch)
        transition = edit_plan.transitions[0]

        asset = await self.provider.apply_transition(
            from_clip_path=f"{context.working_path}/clip_{transition.from_clip_id}.mp4",
            to_clip_path=f"{context.working_path}/clip_{transition.to_clip_id}.mp4",
            transition_type=transition.transition_type.value,
            duration_seconds=transition.duration_seconds,
            output_path=f"{context.working_path}/transition_{transition.id}.mp4",
        )

        return asset


# ============================================================================
# RENDERER 3: SUBTITLE RENDERER
# ============================================================================


class SubtitleRenderer(RenderingEngine):
    """Renders/burns subtitles into video."""

    async def render(
        self,
        edit_plan: EditPlan,
        context: RenderContext,
    ) -> RenderedAsset:
        """Render subtitles.

        Burns subtitle segments into the video.
        """
        if not edit_plan.subtitles:
            raise ValueError("EditPlan has no subtitles to render")

        # Convert subtitles to provider format
        subtitle_data = [
            {
                "start": sub.start_timestamp,
                "end": sub.end_timestamp,
                "text": sub.text,
                "speaker": sub.speaker,
            }
            for sub in edit_plan.subtitles
        ]

        asset = await self.provider.render_subtitles(
            video_path=f"{context.working_path}/composited.mp4",
            subtitle_data=subtitle_data,
            output_path=f"{context.working_path}/with_subtitles.mp4",
            style="default",
        )

        return asset


# ============================================================================
# RENDERER 4: OVERLAY RENDERER
# ============================================================================


class OverlayRenderer(RenderingEngine):
    """Renders overlays onto video."""

    async def render(
        self,
        edit_plan: EditPlan,
        context: RenderContext,
    ) -> RenderedAsset:
        """Render overlays.

        Applies all overlays to the video.
        """
        if not edit_plan.overlays:
            raise ValueError("EditPlan has no overlays to render")

        # Render overlays onto video
        asset = await self.provider.render_overlay(
            video_path=f"{context.working_path}/with_subtitles.mp4",
            overlay_type="composite",
            content={
                "overlays": [
                    {
                        "type": overlay.overlay_type.value,
                        "position": (overlay.position_x, overlay.position_y),
                        "size": (overlay.width, overlay.height),
                        "content": overlay.content,
                    }
                    for overlay in edit_plan.overlays
                ]
            },
            output_path=f"{context.working_path}/with_overlays.mp4",
        )

        return asset


# ============================================================================
# RENDERER 5: ZOOM RENDERER
# ============================================================================


class ZoomRenderer(RenderingEngine):
    """Renders zoom/pan effects."""

    async def render(
        self,
        edit_plan: EditPlan,
        context: RenderContext,
    ) -> RenderedAsset:
        """Render zoom actions.

        Applies zoom and pan effects to video.
        """
        if not edit_plan.zoom_actions:
            raise ValueError("EditPlan has no zoom actions to render")

        # Convert zoom actions to provider format
        zoom_data = [
            {
                "start": zoom.start_timestamp,
                "end": zoom.end_timestamp,
                "type": zoom.zoom_type.value,
                "target_x": zoom.target_x,
                "target_y": zoom.target_y,
                "intensity": zoom.zoom_intensity,
                "easing": zoom.easing,
            }
            for zoom in edit_plan.zoom_actions
        ]

        asset = await self.provider.apply_zoom(
            video_path=f"{context.working_path}/with_overlays.mp4",
            zoom_actions=zoom_data,
            output_path=f"{context.working_path}/with_zoom.mp4",
        )

        return asset


# ============================================================================
# RENDERER 6: BROLL RENDERER
# ============================================================================


class BrollRenderer(RenderingEngine):
    """Inserts B-roll into video."""

    async def render(
        self,
        edit_plan: EditPlan,
        context: RenderContext,
    ) -> RenderedAsset:
        """Render B-roll.

        Inserts B-roll clips into the main video.
        """
        if not edit_plan.broll_suggestions:
            raise ValueError("EditPlan has no B-roll to render")

        # Render first B-roll suggestion (Phase 2 would batch)
        broll = edit_plan.broll_suggestions[0]

        asset = await self.provider.insert_broll(
            main_video_path=f"{context.working_path}/with_zoom.mp4",
            broll_path=f"{context.cache_path}/broll_{broll.id}.mp4",
            start_time_seconds=broll.start_timestamp,
            duration_seconds=broll.end_timestamp - broll.start_timestamp,
            output_path=f"{context.working_path}/with_broll.mp4",
        )

        return asset


# ============================================================================
# RENDERER 7: AUDIO RENDERER
# ============================================================================


class AudioRenderer(RenderingEngine):
    """Mixes audio tracks."""

    async def render(
        self,
        edit_plan: EditPlan,
        context: RenderContext,
    ) -> RenderedAsset:
        """Render audio.

        Mixes music and audio tracks into video.
        """
        if not edit_plan.music_suggestions:
            raise ValueError("EditPlan has no audio to render")

        # Convert music cues to audio format
        audio_tracks = [
            {
                "path": f"{context.cache_path}/music_{music.id}.mp3",
                "start": music.start_timestamp,
                "end": music.end_timestamp,
                "volume": 0.8,
                "fade_in": music.fade_in_seconds,
                "fade_out": music.fade_out_seconds,
            }
            for music in edit_plan.music_suggestions
        ]

        asset = await self.provider.mix_audio(
            video_path=f"{context.working_path}/with_broll.mp4",
            audio_tracks=audio_tracks,
            output_path=f"{context.working_path}/with_audio.mp4",
        )

        return asset


# ============================================================================
# RENDERER 8: COMPOSITE RENDERER
# ============================================================================


class CompositeRenderer(RenderingEngine):
    """Composites all clips and effects into single video."""

    async def render(
        self,
        edit_plan: EditPlan,
        context: RenderContext,
    ) -> RenderedAsset:
        """Composite video.

        Combines all clips with transitions into a single video.
        """
        if not edit_plan.clips or not edit_plan.timeline:
            raise ValueError("EditPlan missing clips or timeline for compositing")

        # Get list of clip IDs in timeline order
        clip_ids = edit_plan.timeline.clip_ids
        clip_paths = [f"{context.working_path}/clip_{cid}.mp4" for cid in clip_ids]

        # Convert transitions to provider format
        transitions_data = [
            {
                "from": t.from_clip_id,
                "to": t.to_clip_id,
                "type": t.transition_type.value,
                "duration": t.duration_seconds,
            }
            for t in edit_plan.transitions
        ]

        asset = await self.provider.composite_video(
            clips=clip_paths,
            transitions=transitions_data,
            output_path=f"{context.working_path}/composited.mp4",
        )

        return asset


# ============================================================================
# RENDERER 9: EXPORT RENDERER
# ============================================================================


class ExportRenderer(RenderingEngine):
    """Exports video in multiple profiles."""

    async def render(
        self,
        edit_plan: EditPlan,
        context: RenderContext,
    ) -> RenderedAsset:
        """Export video.

        Exports video in target export profile format.
        """
        source_path = f"{context.working_path}/with_audio.mp4"
        profile = context.primary_export_profile

        asset = await self.provider.export_video(
            video_path=source_path,
            export_profile=profile,
            output_path=f"{context.output_path}/video_{profile.value}.mp4",
        )

        return asset


# ============================================================================
# RENDERER 10: VALIDATION ENGINE
# ============================================================================


class ValidationEngine(RenderingEngine):
    """Validates rendered output."""

    async def render(
        self,
        edit_plan: EditPlan,
        context: RenderContext,
    ) -> ValidationResult:
        """Validate output.

        Validates the rendered video against EditPlan specifications.
        """
        video_path = f"{context.output_path}/video_{context.primary_export_profile.value}.mp4"

        # Validate output
        result = await self.provider.validate_output(
            video_path=video_path,
            expected_duration_seconds=edit_plan.timeline.total_duration_seconds
            if edit_plan.timeline
            else 0.0,
            expected_resolution=context.target_resolution,
        )

        return result


# ============================================================================
# RENDERER REGISTRY
# ============================================================================


class RendererRegistry:
    """Registry of rendering components."""

    def __init__(self, provider: RendererProvider):
        """Initialize with provider"""
        self._provider = provider
        self._renderers = {
            "clips": ClipRenderer(provider),
            "transitions": TransitionRenderer(provider),
            "subtitles": SubtitleRenderer(provider),
            "overlays": OverlayRenderer(provider),
            "zoom": ZoomRenderer(provider),
            "broll": BrollRenderer(provider),
            "audio": AudioRenderer(provider),
            "composite": CompositeRenderer(provider),
            "export": ExportRenderer(provider),
            "validation": ValidationEngine(provider),
        }

    def get(self, name: str) -> Optional[RenderingEngine]:
        """Get renderer by name"""
        return self._renderers.get(name)

    def list_renderers(self) -> List[str]:
        """List all renderers"""
        return list(self._renderers.keys())

    async def render_all(
        self,
        edit_plan: EditPlan,
        context: RenderContext,
    ) -> Dict[str, Any]:
        """Execute full rendering pipeline.

        Runs all rendering components in sequence.
        """
        results = {}

        # Execute pipeline
        try:
            results["clips"] = await self._renderers["clips"].render(edit_plan, context)
            results["transitions"] = await self._renderers["transitions"].render(
                edit_plan, context
            )
            results["composite"] = await self._renderers["composite"].render(
                edit_plan, context
            )

            if edit_plan.subtitles:
                results["subtitles"] = await self._renderers["subtitles"].render(
                    edit_plan, context
                )

            if edit_plan.overlays:
                results["overlays"] = await self._renderers["overlays"].render(
                    edit_plan, context
                )

            if edit_plan.zoom_actions:
                results["zoom"] = await self._renderers["zoom"].render(edit_plan, context)

            if edit_plan.broll_suggestions:
                results["broll"] = await self._renderers["broll"].render(
                    edit_plan, context
                )

            if edit_plan.music_suggestions:
                results["audio"] = await self._renderers["audio"].render(edit_plan, context)

            results["export"] = await self._renderers["export"].render(edit_plan, context)
            results["validation"] = await self._renderers["validation"].render(
                edit_plan, context
            )

        except Exception as e:
            results["error"] = str(e)

        return results


def create_renderer_registry(provider: RendererProvider) -> RendererRegistry:
    """Factory for creating renderer registry"""
    return RendererRegistry(provider)
