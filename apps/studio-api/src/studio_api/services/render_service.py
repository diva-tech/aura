"""Render service integrating M12 Rendering Engine."""

import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from studio_api.models import (
    Render,
    RenderAsset,
    RenderLog,
    RenderMetadata,
    RenderStatus,
    RenderStage,
)


class RenderService:
    """Render service for M12 Rendering Engine integration."""

    def __init__(self, session: AsyncSession):
        """Initialize service."""
        self.session = session

    async def start_render(
        self,
        project_id: str,
        preview_id: str,
        edit_plan_id: str,
        quality: str = "standard",
        platform: Optional[str] = None,
        priority: int = 5,
    ) -> Render:
        """Start a render job."""
        render_id = str(uuid.uuid4())

        render = Render(
            id=render_id,
            project_id=project_id,
            preview_id=preview_id,
            edit_plan_id=edit_plan_id,
            status="queued",
            quality=quality,
            platform=platform,
            priority=priority,
            estimated_time=120,  # Mock: 2 minutes
        )
        self.session.add(render)

        # Create initial metadata
        metadata = RenderMetadata(
            id=str(uuid.uuid4()),
            render_id=render_id,
            total_frames=5400,  # Mock: 3 min @ 30fps
        )
        self.session.add(metadata)

        # Log initial stage
        log = RenderLog(
            id=str(uuid.uuid4()),
            render_id=render_id,
            stage=RenderStage.PREPARING_ASSETS.value,
            status="started",
            message="Preparing render assets",
        )
        self.session.add(log)

        await self.session.commit()
        return render

    async def update_render_progress(
        self, render_id: str, stage: str, progress: float, message: Optional[str] = None
    ) -> Optional[Render]:
        """Update render progress."""
        query = select(Render).where(Render.id == render_id)
        result = await self.session.execute(query)
        render = result.scalar_one_or_none()

        if not render:
            return None

        render.current_stage = stage
        render.progress_percent = progress
        render.elapsed_time = int((datetime.utcnow() - render.created_at).total_seconds())
        render.status = "rendering"
        render.updated_at = datetime.utcnow()

        # Log progress
        log = RenderLog(
            id=str(uuid.uuid4()),
            render_id=render_id,
            stage=stage,
            status="progress",
            message=message,
            progress_percent=progress,
        )
        self.session.add(log)
        await self.session.commit()
        return render

    async def complete_render(
        self,
        render_id: str,
        output_path: str,
        output_size: int,
        fps: int,
        resolution: str,
        codec: str,
    ) -> Optional[Render]:
        """Mark render as completed."""
        query = select(Render).where(Render.id == render_id)
        result = await self.session.execute(query)
        render = result.scalar_one_or_none()

        if not render:
            return None

        render.status = "completed"
        render.output_path = output_path
        render.output_size = output_size
        render.fps = fps
        render.resolution = resolution
        render.codec = codec
        render.completed_at = datetime.utcnow()
        render.progress_percent = 100.0
        render.updated_at = datetime.utcnow()

        # Add rendered asset
        asset = RenderAsset(
            id=str(uuid.uuid4()),
            render_id=render_id,
            asset_type="video",
            file_path=output_path,
            file_size=output_size,
            file_format="mp4",
        )
        self.session.add(asset)

        # Log completion
        log = RenderLog(
            id=str(uuid.uuid4()),
            render_id=render_id,
            stage=RenderStage.FINALIZING.value,
            status="completed",
            message="Render completed successfully",
            progress_percent=100.0,
        )
        self.session.add(log)

        await self.session.commit()
        return render

    async def fail_render(
        self, render_id: str, error_message: str, error_code: Optional[str] = None
    ) -> Optional[Render]:
        """Mark render as failed."""
        query = select(Render).where(Render.id == render_id)
        result = await self.session.execute(query)
        render = result.scalar_one_or_none()

        if not render:
            return None

        render.status = "failed"
        render.error_message = error_message
        render.updated_at = datetime.utcnow()

        # Log error
        log = RenderLog(
            id=str(uuid.uuid4()),
            render_id=render_id,
            stage=render.current_stage or "unknown",
            status="error",
            message=error_message,
            error_code=error_code,
        )
        self.session.add(log)

        await self.session.commit()
        return render

    async def cancel_render(self, render_id: str) -> Optional[Render]:
        """Cancel a render job."""
        query = select(Render).where(Render.id == render_id)
        result = await self.session.execute(query)
        render = result.scalar_one_or_none()

        if not render:
            return None

        render.status = "cancelled"
        render.updated_at = datetime.utcnow()

        # Log cancellation
        log = RenderLog(
            id=str(uuid.uuid4()),
            render_id=render_id,
            stage=render.current_stage or "unknown",
            status="cancelled",
            message="Render cancelled by user",
        )
        self.session.add(log)

        await self.session.commit()
        return render

    async def retry_render(self, render_id: str) -> Optional[Render]:
        """Retry a failed render."""
        query = select(Render).where(Render.id == render_id)
        result = await self.session.execute(query)
        render = result.scalar_one_or_none()

        if not render or render.status != "failed":
            return None

        render.status = "queued"
        render.retry_count += 1
        render.progress_percent = 0.0
        render.current_stage = RenderStage.PREPARING_ASSETS.value
        render.error_message = None
        render.updated_at = datetime.utcnow()

        # Log retry
        log = RenderLog(
            id=str(uuid.uuid4()),
            render_id=render_id,
            stage=RenderStage.PREPARING_ASSETS.value,
            status="started",
            message=f"Retry attempt {render.retry_count}",
        )
        self.session.add(log)

        await self.session.commit()
        return render

    async def get_render(self, render_id: str) -> Optional[Render]:
        """Get render by ID."""
        query = select(Render).where(Render.id == render_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_renders(
        self, project_id: Optional[str] = None, status: Optional[str] = None
    ) -> list[Render]:
        """List renders."""
        query = select(Render).order_by(Render.created_at.desc())

        if project_id:
            query = query.where(Render.project_id == project_id)

        if status:
            query = query.where(Render.status == status)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_render_logs(self, render_id: str) -> list[RenderLog]:
        """Get render logs."""
        query = (
            select(RenderLog)
            .where(RenderLog.render_id == render_id)
            .order_by(RenderLog.timestamp.asc())
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_render_metadata(self, render_id: str) -> Optional[RenderMetadata]:
        """Get render metadata."""
        query = select(RenderMetadata).where(RenderMetadata.render_id == render_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_render_assets(self, render_id: str) -> list[RenderAsset]:
        """Get render assets."""
        query = select(RenderAsset).where(RenderAsset.render_id == render_id)
        result = await self.session.execute(query)
        return result.scalars().all()
