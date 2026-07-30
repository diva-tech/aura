"""Edit plan service."""

import json
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from studio_api.models import (
    EditOperation,
    EditOperationType,
    EditPlan,
    EditPlanComment,
    EditPlanHistory,
    Suggestion,
    TimelineClip,
    TimelineTrack,
    TrackType,
    Transition,
)


class EditPlanService:
    """Edit plan service."""

    def __init__(self, session: AsyncSession):
        """Initialize service."""
        self.session = session

    async def generate_edit_plan(self, project_id: str) -> EditPlan:
        """Generate edit plan from accepted suggestions."""
        plan_id = str(uuid.uuid4())

        plan = EditPlan(
            id=plan_id,
            project_id=project_id,
            version=1,
            status="draft",
            approved=False,
            change_count=0,
        )
        self.session.add(plan)

        # Fetch accepted suggestions for this project
        query = select(Suggestion).where(
            Suggestion.report_id.in_(
                select(Suggestion.report_id).where(Suggestion.accepted)
            )
        )
        result = await self.session.execute(query)
        suggestions = result.scalars().all()

        # Create timeline tracks
        await self._create_timeline_tracks(plan_id)

        # Convert suggestions to edit operations
        await self._convert_suggestions_to_operations(plan_id, suggestions)

        # Record history
        await self._record_history(
            plan_id, 1, "ai_generate", "Initial edit plan generated from AI suggestions"
        )

        await self.session.commit()
        return plan

    async def _create_timeline_tracks(self, plan_id: str) -> None:
        """Create default timeline tracks."""
        track_types = [
            (TrackType.VIDEO, 0, "Video"),
            (TrackType.AUDIO, 1, "Audio"),
            (TrackType.CAPTION, 2, "Captions"),
            (TrackType.ZOOM, 3, "Zoom Effects"),
            (TrackType.OVERLAY, 4, "Overlays"),
            (TrackType.MUSIC, 5, "Music"),
            (TrackType.TRANSITION, 6, "Transitions"),
        ]

        for track_type, order, label in track_types:
            track = TimelineTrack(
                id=str(uuid.uuid4()),
                edit_plan_id=plan_id,
                track_type=track_type,
                order=order,
                label=label,
            )
            self.session.add(track)

    async def _convert_suggestions_to_operations(
        self, plan_id: str, suggestions: list[Suggestion]
    ) -> None:
        """Convert AI suggestions to edit operations."""
        for idx, suggestion in enumerate(suggestions):
            operation_type = self._map_suggestion_to_operation(suggestion.type)
            if not operation_type:
                continue

            operation = EditOperation(
                id=str(uuid.uuid4()),
                edit_plan_id=plan_id,
                operation_type=operation_type,
                start_time=suggestion.timestamp or 0,
                end_time=suggestion.timestamp or 1000,
                title=suggestion.title,
                description=suggestion.description,
                reason=suggestion.reason,
                suggestion_id=suggestion.id,
                enabled=True,
                applied=False,
                order=idx,
            )
            self.session.add(operation)

    def _map_suggestion_to_operation(self, suggestion_type: str) -> Optional[EditOperationType]:
        """Map suggestion type to operation type."""
        mapping = {
            "cut_intro": EditOperationType.CUT,
            "cut_outro": EditOperationType.CUT,
            "cut_silence": EditOperationType.CUT,
            "trim": EditOperationType.TRIM,
            "zoom": EditOperationType.ZOOM,
            "zoom_speaker": EditOperationType.ZOOM,
            "speed_up": EditOperationType.SPEED,
            "slow_down": EditOperationType.SPEED,
            "add_captions": EditOperationType.ZOOM,  # will have caption operations
            "remove_caption": EditOperationType.DELETE,
            "add_color": EditOperationType.COLOR,
            "add_music": EditOperationType.AUDIO,
            "remove_music": EditOperationType.AUDIO,
            "cta_overlay": EditOperationType.ZOOM,  # overlay operation
            "improve_audio": EditOperationType.AUDIO,
            "normalize_audio": EditOperationType.AUDIO,
        }
        return mapping.get(suggestion_type)

    async def update_operation(
        self, operation_id: str, **kwargs
    ) -> Optional[EditOperation]:
        """Update an edit operation."""
        query = select(EditOperation).where(EditOperation.id == operation_id)
        result = await self.session.execute(query)
        operation = result.scalar_one_or_none()

        if not operation:
            return None

        for key, value in kwargs.items():
            if hasattr(operation, key) and value is not None:
                setattr(operation, key, value)

        operation.updated_at = datetime.utcnow()
        await self.session.commit()
        return operation

    async def approve_edit_plan(self, edit_plan_id: str) -> Optional[EditPlan]:
        """Approve an edit plan."""
        query = select(EditPlan).where(EditPlan.id == edit_plan_id)
        result = await self.session.execute(query)
        plan = result.scalar_one_or_none()

        if not plan:
            return None

        plan.approved = True
        plan.status = "approved"
        plan.updated_at = datetime.utcnow()

        await self._record_history(
            edit_plan_id, plan.version, "approve", "Edit plan approved for rendering"
        )

        await self.session.commit()
        return plan

    async def regenerate_edit_plan(self, plan_id: str, prompt: str) -> Optional[EditPlan]:
        """Regenerate edit plan based on user prompt."""
        query = select(EditPlan).where(EditPlan.id == plan_id)
        result = await self.session.execute(query)
        plan = result.scalar_one_or_none()

        if not plan:
            return None

        # Increment version
        plan.version += 1
        plan.change_count += 1

        # Record history
        await self._record_history(
            plan_id, plan.version, "ai_regenerate", f"Regenerated: {prompt}"
        )

        await self.session.commit()
        return plan

    async def undo_edit_plan(self, plan_id: str) -> Optional[EditPlan]:
        """Undo last change to edit plan."""
        # Fetch current version
        query = select(EditPlan).where(EditPlan.id == plan_id)
        result = await self.session.execute(query)
        plan = result.scalar_one_or_none()

        if not plan or plan.version <= 1:
            return None

        # Fetch previous version from history
        query = select(EditPlanHistory).where(
            EditPlanHistory.edit_plan_id == plan_id,
            EditPlanHistory.version == plan.version - 1,
        )
        result = await self.session.execute(query)
        history = result.scalar_one_or_none()

        if not history:
            return None

        # Restore from history
        plan.version -= 1
        plan.updated_at = datetime.utcnow()

        await self._record_history(plan_id, plan.version, "undo", "Undone")

        await self.session.commit()
        return plan

    async def add_comment(
        self, plan_id: str, timestamp: int, text: str, author: Optional[str] = None
    ) -> Optional[EditPlanComment]:
        """Add comment to edit plan."""
        comment = EditPlanComment(
            id=str(uuid.uuid4()),
            edit_plan_id=plan_id,
            timestamp=timestamp,
            text=text,
            author=author,
        )
        self.session.add(comment)
        await self.session.commit()
        return comment

    async def get_edit_plan(self, plan_id: str) -> Optional[EditPlan]:
        """Get edit plan by ID."""
        query = select(EditPlan).where(EditPlan.id == plan_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_project_edit_plan(self, project_id: str) -> Optional[EditPlan]:
        """Get latest edit plan for project."""
        query = select(EditPlan).where(EditPlan.project_id == project_id).order_by(
            EditPlan.created_at.desc()
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def _record_history(
        self, plan_id: str, version: int, change_type: str, description: str
    ) -> None:
        """Record change history."""
        history = EditPlanHistory(
            id=str(uuid.uuid4()),
            edit_plan_id=plan_id,
            version=version,
            change_type=change_type,
            description=description,
        )
        self.session.add(history)
