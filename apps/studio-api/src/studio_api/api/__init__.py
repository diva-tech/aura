"""API routes."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from studio_api.database.config import get_session
from studio_api.models import Video
from studio_api.models.analysis import (
    AnalysisReport,
    Scene,
    Suggestion,
    Transcript,
    VideoMetrics,
)
from studio_api.schemas import AnalysisResponse, ProjectCreate, ProjectResponse, VideoResponse
from studio_api.schemas.analysis import (
    AnalysisDetailResponse,
    AnalysisReportResponse,
    AnalysisStatusResponse,
    SceneResponse,
    SuggestionResponse,
    TranscriptResponse,
)
from studio_api.services import ProjectService, VideoService
from studio_api.services.analysis_service import AnalysisService
from studio_api.services.edit_plan_service import EditPlanService
from studio_api.services.preview_service import PreviewService
from studio_api.storage import StorageService
from studio_api.schemas.edit_plan import (
    EditPlanResponse,
    EditPlanCreateRequest,
    EditPlanUpdateRequest,
    EditPlanApproveRequest,
    EditPlanRegenerateRequest,
)
from studio_api.schemas.preview import (
    PreviewResponse,
    PreviewDetailResponse,
    RenderEstimateResponse,
    RenderSettingsResponse,
    GeneratePreviewRequest,
    PreviewSettingsUpdateRequest,
    ApprovePreviewRequest,
    PreviewCommentRequest,
)

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
@router.post("/projects/{project_id}/analyze", response_model=AnalysisStatusResponse)
async def analyze_project(
    project_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Start AI analysis for project."""
    # Verify project exists
    project_service = ProjectService(session)
    project = await project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # Get first video (for now, analyze the first uploaded video)
    result = await session.execute(
        select(Video).where(Video.project_id == project_id).limit(1)
    )
    video = result.scalars().first()
    if not video:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No videos to analyze")

    # Create analysis report
    analysis_service = AnalysisService(session)
    report = await analysis_service.create_analysis_report(project_id, video.id)

    # TODO: Queue analysis as async task (use Celery, RQ, or M8 orchestration)
    # For now, run synchronously
    try:
        await analysis_service.analyze_video(report.id, video.storage_path)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return AnalysisStatusResponse(status="completed", progress=100)


@router.get("/projects/{project_id}/analysis", response_model=AnalysisDetailResponse)
async def get_analysis(
    project_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Get analysis report for project."""
    # Get latest analysis
    result = await session.execute(
        select(AnalysisReport)
        .where(AnalysisReport.project_id == project_id)
        .order_by(AnalysisReport.created_at.desc())
        .limit(1)
    )
    report = result.scalars().first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No analysis found")

    # Get metrics
    metrics_result = await session.execute(
        select(VideoMetrics).where(VideoMetrics.report_id == report.id).limit(1)
    )
    metrics = metrics_result.scalars().first()

    # Get scenes
    scenes_result = await session.execute(
        select(Scene).where(Scene.report_id == report.id)
    )
    scenes = scenes_result.scalars().all()

    # Get transcript
    transcript_result = await session.execute(
        select(Transcript).where(Transcript.report_id == report.id)
    )
    transcript = transcript_result.scalars().all()

    # Get suggestions
    suggestions_result = await session.execute(
        select(Suggestion).where(Suggestion.report_id == report.id)
    )
    suggestions = suggestions_result.scalars().all()

    return AnalysisDetailResponse(
        report=AnalysisReportResponse.from_orm(report),
        metrics=metrics,
        scenes=[SceneResponse.from_orm(s) for s in scenes],
        transcript=[TranscriptResponse.from_orm(t) for t in transcript],
        suggestions=[SuggestionResponse.from_orm(s) for s in suggestions],
    )


@router.get("/projects/{project_id}/suggestions", response_model=list[SuggestionResponse])
async def get_suggestions(
    project_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Get suggestions for project."""
    # Get latest analysis
    result = await session.execute(
        select(AnalysisReport)
        .where(AnalysisReport.project_id == project_id)
        .order_by(AnalysisReport.created_at.desc())
        .limit(1)
    )
    report = result.scalars().first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No analysis found")

    # Get suggestions
    suggestions_result = await session.execute(
        select(Suggestion).where(Suggestion.report_id == report.id)
    )
    return suggestions_result.scalars().all()


@router.get("/projects/{project_id}/transcript", response_model=list[TranscriptResponse])
async def get_transcript(
    project_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Get transcript for project."""
    # Get latest analysis
    result = await session.execute(
        select(AnalysisReport)
        .where(AnalysisReport.project_id == project_id)
        .order_by(AnalysisReport.created_at.desc())
        .limit(1)
    )
    report = result.scalars().first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No analysis found")

    # Get transcript
    transcript_result = await session.execute(
        select(Transcript).where(Transcript.report_id == report.id)
    )
    return transcript_result.scalars().all()


@router.post("/projects/{project_id}/suggestions/{suggestion_id}/accept", status_code=status.HTTP_200_OK)
async def accept_suggestion(
    project_id: str,
    suggestion_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Accept a suggestion."""
    # Get suggestion
    suggestion_result = await session.execute(
        select(Suggestion).where(Suggestion.id == suggestion_id)
    )
    suggestion = suggestion_result.scalars().first()
    if not suggestion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suggestion not found")

    suggestion.accepted = True
    await session.commit()

    return {"status": "accepted"}


# Edit plan endpoints
@router.post(
    "/projects/{project_id}/edit-plan",
    response_model=EditPlanResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_edit_plan(
    project_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Generate edit plan from accepted suggestions."""
    # Verify project exists
    project_service = ProjectService(session)
    project = await project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    try:
        service = EditPlanService(session)
        plan = await service.generate_edit_plan(project_id)
        return plan
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/projects/{project_id}/edit-plan", response_model=EditPlanResponse)
async def get_edit_plan(
    project_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Get edit plan for project."""
    try:
        service = EditPlanService(session)
        plan = await service.get_project_edit_plan(project_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No edit plan found"
            )
        return plan
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/edit-plan/{plan_id}/approve", response_model=EditPlanResponse)
async def approve_edit_plan(
    plan_id: str,
    data: EditPlanApproveRequest,
    session: AsyncSession = Depends(get_session),
):
    """Approve an edit plan."""
    try:
        service = EditPlanService(session)
        plan = await service.approve_edit_plan(plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Edit plan not found"
            )
        return plan
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/edit-plan/{plan_id}/regenerate", response_model=EditPlanResponse)
async def regenerate_edit_plan(
    plan_id: str,
    data: EditPlanRegenerateRequest,
    session: AsyncSession = Depends(get_session),
):
    """Regenerate edit plan based on user prompt."""
    try:
        service = EditPlanService(session)
        plan = await service.regenerate_edit_plan(plan_id, data.prompt)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Edit plan not found"
            )
        return plan
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/edit-plan/{plan_id}/undo", response_model=EditPlanResponse)
async def undo_edit_plan(
    plan_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Undo last change to edit plan."""
    try:
        service = EditPlanService(session)
        plan = await service.undo_edit_plan(plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cannot undo. At initial version.",
            )
        return plan
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# Preview endpoints
@router.post(
    "/projects/{project_id}/preview",
    response_model=PreviewResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_preview(
    project_id: str,
    data: GeneratePreviewRequest,
    session: AsyncSession = Depends(get_session),
):
    """Generate preview from approved edit plan."""
    try:
        # Verify project exists
        project_service = ProjectService(session)
        project = await project_service.get_project(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )

        # Get latest edit plan
        edit_plan_service = EditPlanService(session)
        edit_plan = await edit_plan_service.get_project_edit_plan(project_id)
        if not edit_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No edit plan found"
            )

        if not edit_plan.approved:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Edit plan must be approved before preview",
            )

        service = PreviewService(session)
        preview = await service.generate_preview(
            project_id, edit_plan.id, data.quality
        )
        return preview
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/projects/{project_id}/preview", response_model=PreviewResponse)
async def get_preview(
    project_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Get latest preview for project."""
    try:
        service = PreviewService(session)
        preview = await service.get_project_preview(project_id)
        if not preview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No preview found"
            )
        return preview
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/preview/{preview_id}/approve", response_model=PreviewResponse)
async def approve_preview(
    preview_id: str,
    data: ApprovePreviewRequest,
    session: AsyncSession = Depends(get_session),
):
    """Approve preview for rendering."""
    try:
        service = PreviewService(session)
        preview = await service.approve_preview(preview_id)
        if not preview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Preview not found"
            )
        return preview
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get(
    "/projects/{project_id}/render-estimate", response_model=RenderEstimateResponse
)
async def get_render_estimate(
    project_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Get render estimate for project."""
    try:
        # Get latest edit plan
        edit_plan_service = EditPlanService(session)
        edit_plan = await edit_plan_service.get_project_edit_plan(project_id)
        if not edit_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No edit plan found"
            )

        service = PreviewService(session)
        estimate = await service.get_render_estimate(project_id, edit_plan.id)
        if not estimate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No render estimate found"
            )
        return estimate
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.put(
    "/projects/{project_id}/render-settings",
    response_model=RenderSettingsResponse,
)
async def update_render_settings(
    project_id: str,
    data: PreviewSettingsUpdateRequest,
    session: AsyncSession = Depends(get_session),
):
    """Update render settings for project."""
    try:
        service = PreviewService(session)
        settings = await service.update_render_settings(project_id, **data.dict(exclude_none=True))
        if not settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Settings not found"
            )
        return settings
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/preview/{preview_id}/comments")
async def add_preview_comment(
    preview_id: str,
    data: PreviewCommentRequest,
    session: AsyncSession = Depends(get_session),
):
    """Add comment to preview frame."""
    try:
        service = PreviewService(session)
        comment = await service.add_comment(
            preview_id, data.timestamp, data.text, data.author
        )
        return {"status": "created", "comment_id": comment.id if comment else None}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# Health check
@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
