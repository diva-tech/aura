"""Data access repositories."""

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from studio_api.models import Project, Video


class ProjectRepository:
    """Project repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, name: str, description: Optional[str], target_platform: str, language: str, aspect_ratio: str) -> Project:
        """Create project."""
        project = Project(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            target_platform=target_platform,
            language=language,
            aspect_ratio=aspect_ratio,
        )
        self.session.add(project)
        await self.session.commit()
        await self.session.refresh(project)
        return project

    async def get_by_id(self, project_id: str) -> Optional[Project]:
        """Get project by ID."""
        result = await self.session.execute(select(Project).where(Project.id == project_id))
        return result.scalars().first()

    async def get_all(self) -> list[Project]:
        """Get all projects."""
        result = await self.session.execute(select(Project).order_by(Project.created_at.desc()))
        return result.scalars().all()

    async def update(self, project_id: str, name: Optional[str] = None, description: Optional[str] = None, status: Optional[str] = None) -> Optional[Project]:
        """Update project."""
        project = await self.get_by_id(project_id)
        if not project:
            return None

        if name:
            project.name = name
        if description is not None:
            project.description = description
        if status:
            project.status = status

        await self.session.commit()
        await self.session.refresh(project)
        return project

    async def delete(self, project_id: str) -> bool:
        """Delete project."""
        project = await self.get_by_id(project_id)
        if not project:
            return False

        await self.session.delete(project)
        await self.session.commit()
        return True


class VideoRepository:
    """Video repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, project_id: str, filename: str, size: int, storage_path: str, thumbnail_path: Optional[str] = None, **metadata) -> Video:
        """Create video."""
        video = Video(
            id=str(uuid.uuid4()),
            project_id=project_id,
            filename=filename,
            size=size,
            storage_path=storage_path,
            thumbnail_path=thumbnail_path,
            duration=metadata.get("duration"),
            resolution=metadata.get("resolution"),
            codec=metadata.get("codec"),
            fps=metadata.get("fps"),
        )
        self.session.add(video)
        await self.session.commit()
        await self.session.refresh(video)
        return video

    async def get_by_id(self, video_id: str) -> Optional[Video]:
        """Get video by ID."""
        result = await self.session.execute(select(Video).where(Video.id == video_id))
        return result.scalars().first()

    async def get_by_project(self, project_id: str) -> list[Video]:
        """Get videos by project ID."""
        result = await self.session.execute(select(Video).where(Video.project_id == project_id).order_by(Video.created_at.desc()))
        return result.scalars().all()

    async def delete(self, video_id: str) -> bool:
        """Delete video."""
        video = await self.get_by_id(video_id)
        if not video:
            return False

        await self.session.delete(video)
        await self.session.commit()
        return True
