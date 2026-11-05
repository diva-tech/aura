"""Business logic services."""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from studio_api.database.repositories import ProjectRepository, VideoRepository
from studio_api.models import Project, Video
from studio_api.schemas import ProjectCreate, VideoMetadata


class ProjectService:
    """Project service."""

    def __init__(self, session: AsyncSession):
        self.repository = ProjectRepository(session)

    async def create_project(self, data: ProjectCreate) -> Project:
        """Create a new project."""
        return await self.repository.create(
            name=data.name,
            description=data.description,
            target_platform=data.target_platform,
            language=data.language,
            aspect_ratio=data.aspect_ratio,
        )

    async def get_project(self, project_id: str) -> Optional[Project]:
        """Get project by ID."""
        return await self.repository.get_by_id(project_id)

    async def list_projects(self) -> list[Project]:
        """List all projects."""
        return await self.repository.get_all()

    async def update_project(self, project_id: str, name: Optional[str] = None, description: Optional[str] = None, status: Optional[str] = None) -> Optional[Project]:
        """Update project."""
        return await self.repository.update(project_id, name, description, status)

    async def delete_project(self, project_id: str) -> bool:
        """Delete project."""
        return await self.repository.delete(project_id)


class VideoService:
    """Video service."""

    def __init__(self, session: AsyncSession):
        self.repository = VideoRepository(session)

    async def create_video(self, project_id: str, filename: str, size: int, storage_path: str, thumbnail_path: Optional[str] = None, metadata: Optional[VideoMetadata] = None) -> Video:
        """Create a new video."""
        meta_dict = metadata.model_dump(exclude_none=True) if metadata else {}
        return await self.repository.create(
            project_id=project_id,
            filename=filename,
            size=size,
            storage_path=storage_path,
            thumbnail_path=thumbnail_path,
            **meta_dict,
        )

    async def get_video(self, video_id: str) -> Optional[Video]:
        """Get video by ID."""
        return await self.repository.get_by_id(video_id)

    async def list_project_videos(self, project_id: str) -> list[Video]:
        """List videos for a project."""
        return await self.repository.get_by_project(project_id)

    async def delete_video(self, video_id: str) -> bool:
        """Delete video."""
        return await self.repository.delete(video_id)
