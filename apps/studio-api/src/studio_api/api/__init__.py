"""API routes."""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from studio_api.database.config import get_session
from studio_api.schemas import AnalysisResponse, ProjectCreate, ProjectResponse, VideoResponse
from studio_api.services import ProjectService, VideoService
from studio_api.storage import StorageService

router = APIRouter(prefix="/api", tags=["api"])


# Project endpoints
@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    session: AsyncSession = Depends(get_session),
):
    """Create a new project."""
    service = ProjectService(session)
    project = await service.create_project(data)
    return project


@router.get("/projects", response_model=list[ProjectResponse])
async def list_projects(
    session: AsyncSession = Depends(get_session),
):
    """List all projects."""
    service = ProjectService(session)
    projects = await service.list_projects()
    return projects


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Get project by ID."""
    service = ProjectService(session)
    project = await service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Delete project."""
    service = ProjectService(session)
    success = await service.delete_project(project_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return None


# Video endpoints
@router.post("/projects/{project_id}/upload", response_model=VideoResponse, status_code=status.HTTP_201_CREATED)
async def upload_video(
    project_id: str,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
):
    """Upload video to project."""
    # Verify project exists
    project_service = ProjectService(session)
    project = await project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # Read file
    try:
        file_content = await file.read()
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to read file")

    # Save file
    try:
        storage_path, size = await StorageService.save_video(project_id, file_content, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # Extract metadata
    metadata = StorageService.get_video_metadata(storage_path)

    # Generate thumbnail
    thumbnail_path = None
    if metadata.get("duration"):
        thumb_filename = f"{project_id}_{file.filename.split('.')[0]}_thumb.jpg"
        thumb_storage_path = f"{storage_path.rsplit('.', 1)[0]}_thumb.jpg"
        thumbnail_result = await StorageService.generate_thumbnail(storage_path, thumb_storage_path)
        if thumbnail_result:
            thumbnail_path = thumbnail_result

    # Create video record
    video_service = VideoService(session)
    video = await video_service.create_video(
        project_id=project_id,
        filename=file.filename,
        size=size,
        storage_path=storage_path,
        thumbnail_path=thumbnail_path,
        metadata=metadata,
    )

    return video


@router.get("/videos/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Get video by ID."""
    service = VideoService(session)
    video = await service.get_video(video_id)
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    return video


@router.get("/projects/{project_id}/videos", response_model=list[VideoResponse])
async def list_project_videos(
    project_id: str,
    session: AsyncSession = Depends(get_session),
):
    """List videos for a project."""
    # Verify project exists
    project_service = ProjectService(session)
    project = await project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    service = VideoService(session)
    videos = await service.list_project_videos(project_id)
    return videos


@router.delete("/videos/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video(
    video_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Delete video."""
    service = VideoService(session)
    video = await service.get_video(video_id)
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")

    # Delete files
    await StorageService.delete_video(video.storage_path)
    if video.thumbnail_path:
        await StorageService.delete_thumbnail(video.thumbnail_path)

    success = await service.delete_video(video_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete video")
    return None


# Analysis endpoints
@router.post("/projects/{project_id}/analyze", response_model=AnalysisResponse)
async def analyze_project(
    project_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Queue project for AI analysis (placeholder)."""
    # Verify project exists
    service = ProjectService(session)
    project = await service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # TODO: Integrate with M9-M14 engine
    return AnalysisResponse(status="queued")


# Health check
@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
