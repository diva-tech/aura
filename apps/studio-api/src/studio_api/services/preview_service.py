"""Preview service."""

import json
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from studio_api.models import (
    Preview,
    PreviewFrameComment,
    PreviewStatus,
    PreviewValidation,
    RenderEstimate,
    RenderSettings,
)


class PreviewService:
    """Preview service for generating and managing previews."""

    def __init__(self, session: AsyncSession):
        """Initialize service."""
        self.session = session

    async def generate_preview(
        self, project_id: str, edit_plan_id: str, quality: str = "medium"
    ) -> Preview:
        """Generate preview from edit plan."""
        preview_id = str(uuid.uuid4())

        preview = Preview(
            id=preview_id,
            project_id=project_id,
            edit_plan_id=edit_plan_id,
            version=1,
            status="processing",
            quality=quality,
            approved=False,
        )
        self.session.add(preview)

        # Create default render settings if not exists
        settings = await self.get_or_create_render_settings(project_id)

        # Generate estimate
        estimate = await self.calculate_render_estimate(project_id, edit_plan_id)

        # Validate preview
        validation = await self.validate_preview(preview_id, edit_plan_id)

        # Simulate preview generation (would call M12 Rendering Engine)
        # For now, mark as completed
        preview.status = "completed"
        preview.file_path = f"previews/{preview_id}/preview.mp4"
        preview.duration = 180000  # Mock duration
        preview.filesize = 52428800  # Mock size (50MB)
        preview.estimated_render_time = estimate.estimated_render_time
        preview.estimated_output_size = estimate.estimated_output_size

        await self.session.commit()
        return preview

    async def get_or_create_render_settings(
        self, project_id: str
    ) -> RenderSettings:
        """Get or create render settings for project."""
        query = select(RenderSettings).where(
            RenderSettings.project_id == project_id
        )
        result = await self.session.execute(query)
        settings = result.scalar_one_or_none()

        if not settings:
            settings = RenderSettings(
                id=str(uuid.uuid4()),
                project_id=project_id,
                resolution="1080p",
                fps=30,
                codec="h264",
                bitrate="5mbps",
                quality_level=85,
            )
            self.session.add(settings)
            await self.session.commit()

        return settings

    async def calculate_render_estimate(
        self, project_id: str, edit_plan_id: str
    ) -> RenderEstimate:
        """Calculate render time and cost estimate."""
        estimate_id = str(uuid.uuid4())

        # Mock calculation - in reality, this would analyze the edit plan
        estimate = RenderEstimate(
            id=estimate_id,
            project_id=project_id,
            edit_plan_id=edit_plan_id,
            estimated_duration=180000,  # 3 minutes
            estimated_render_time=120,  # 2 minutes render time
            estimated_output_size=104857600,  # 100MB
            gpu_usage_percent=75.0,
            cpu_usage_percent=45.0,
            operations_count=8,
            effects_count=3,
            captions_count=5,
            transitions_count=2,
        )
        self.session.add(estimate)
        await self.session.commit()

        return estimate

    async def validate_preview(
        self, preview_id: str, edit_plan_id: str
    ) -> PreviewValidation:
        """Validate preview for rendering issues."""
        validation_id = str(uuid.uuid4())

        errors = []
        warnings = []

        # Mock validation checks
        validation = PreviewValidation(
            id=validation_id,
            preview_id=preview_id,
            is_valid=True,
            errors=json.dumps(errors),
            warnings=json.dumps(warnings),
            checked_assets=True,
            checked_operations=True,
            checked_audio=True,
            checked_fonts=True,
            checked_overlays=True,
        )
        self.session.add(validation)
        await self.session.commit()

        return validation

    async def update_render_settings(
        self, project_id: str, **kwargs
    ) -> Optional[RenderSettings]:
        """Update render settings."""
        query = select(RenderSettings).where(
            RenderSettings.project_id == project_id
        )
        result = await self.session.execute(query)
        settings = result.scalar_one_or_none()

        if not settings:
            return None

        for key, value in kwargs.items():
            if hasattr(settings, key) and value is not None:
                setattr(settings, key, value)

        settings.updated_at = datetime.utcnow()
        await self.session.commit()
        return settings

    async def approve_preview(self, preview_id: str) -> Optional[Preview]:
        """Approve preview for rendering."""
        query = select(Preview).where(Preview.id == preview_id)
        result = await self.session.execute(query)
        preview = result.scalar_one_or_none()

        if not preview:
            return None

        preview.approved = True
        preview.updated_at = datetime.utcnow()
        await self.session.commit()
        return preview

    async def get_preview(self, preview_id: str) -> Optional[Preview]:
        """Get preview by ID."""
        query = select(Preview).where(Preview.id == preview_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_project_preview(self, project_id: str) -> Optional[Preview]:
        """Get latest preview for project."""
        query = (
            select(Preview)
            .where(Preview.project_id == project_id)
            .order_by(Preview.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def add_comment(
        self,
        preview_id: str,
        timestamp: int,
        text: str,
        author: Optional[str] = None,
    ) -> Optional[PreviewFrameComment]:
        """Add comment to preview frame."""
        comment = PreviewFrameComment(
            id=str(uuid.uuid4()),
            preview_id=preview_id,
            timestamp=timestamp,
            text=text,
            author=author,
        )
        self.session.add(comment)
        await self.session.commit()
        return comment

    async def get_preview_comments(
        self, preview_id: str
    ) -> list[PreviewFrameComment]:
        """Get all comments for preview."""
        query = select(PreviewFrameComment).where(
            PreviewFrameComment.preview_id == preview_id
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_render_estimate(
        self, project_id: str, edit_plan_id: str
    ) -> Optional[RenderEstimate]:
        """Get render estimate for project."""
        query = (
            select(RenderEstimate)
            .where(RenderEstimate.project_id == project_id)
            .order_by(RenderEstimate.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
