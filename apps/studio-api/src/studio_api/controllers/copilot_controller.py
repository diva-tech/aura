"""AURA AI Copilot API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from studio_api.database import get_db
from studio_api.schemas.copilot import (
    CopilotActionCreate,
    CopilotActionResponse,
    CopilotChatRequest,
    CopilotChatResponse,
    CopilotChatResponseWrapper,
    CopilotMemoryCreate,
    CopilotMemoryResponse,
    CopilotRecommendationCreate,
    CopilotRecommendationResponse,
)
from studio_api.services.copilot_service import CopilotService

router = APIRouter(prefix="/copilot", tags=["copilot"])
service = CopilotService()


@router.post("/{project_id}/chat", response_model=CopilotChatResponseWrapper)
async def chat(
    project_id: str,
    request: CopilotChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """Process copilot chat message."""
    user_message = await service.save_chat_message(
        db, project_id, "user", request.message, request.context
    )

    # Simulate AI response based on user message
    response_text = "I'm analyzing your request..."
    if "edit plan" in request.message.lower():
        response_text = (
            "I can generate a new edit plan. Which video would you like "
            "me to optimize? I can improve pacing, add engaging cuts, "
            "or restructure based on your audience insights."
        )
    elif "analyze" in request.message.lower():
        response_text = (
            "Starting AI analysis of your video. I'll examine retention, "
            "engagement patterns, and provide optimization suggestions."
        )
    elif "publish" in request.message.lower():
        response_text = (
            "I can help you publish to multiple platforms. Which platforms "
            "are you targeting? I'll optimize metadata for each one."
        )
    elif "performance" in request.message.lower():
        response_text = (
            "Your videos are performing well! I've identified that "
            "8-12 minute lengths with strong hooks work best for your "
            "audience. Want me to apply these insights?"
        )
    else:
        response_text = (
            "I can help with video analysis, editing, optimization, "
            "publishing, and channel strategy. What would you like to "
            "work on?"
        )

    assistant_message = await service.save_chat_message(
        db, project_id, "assistant", response_text
    )

    return CopilotChatResponseWrapper(
        user_message=user_message,
        assistant_message=assistant_message,
        orchestration_context={
            "modules": ["analysis", "edit_plan", "render", "publish", "learning"]
        },
    )


@router.get("/{project_id}/history", response_model=list[CopilotChatResponse])
async def get_history(
    project_id: str,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """Get chat history for project."""
    return await service.get_chat_history(db, project_id, limit)


@router.post("/{project_id}/memory", response_model=CopilotMemoryResponse)
async def save_memory(
    project_id: str,
    request: CopilotMemoryCreate,
    db: AsyncSession = Depends(get_db),
):
    """Save user preference or memory."""
    return await service.save_memory(
        db, project_id, request.memory_type, request.key, request.value
    )


@router.get("/{project_id}/memory/{memory_type}/{key}")
async def get_memory(
    project_id: str,
    memory_type: str,
    key: str,
    db: AsyncSession = Depends(get_db),
):
    """Get specific memory."""
    memory = await service.get_memory(db, project_id, memory_type, key)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory


@router.post(
    "/{project_id}/recommendations",
    response_model=CopilotRecommendationResponse,
)
async def create_recommendation(
    project_id: str,
    request: CopilotRecommendationCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create AI recommendation."""
    return await service.create_recommendation(
        db,
        project_id,
        request.recommendation_type,
        request.title,
        request.description,
        request.action,
        request.priority,
    )


@router.get(
    "/{project_id}/recommendations",
    response_model=list[CopilotRecommendationResponse],
)
async def get_recommendations(
    project_id: str,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """Get active recommendations."""
    return await service.get_recommendations(db, project_id, limit)


@router.post("/{project_id}/actions", response_model=CopilotActionResponse)
async def create_action(
    project_id: str,
    request: CopilotActionCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create action item."""
    return await service.create_action(
        db,
        project_id,
        request.action_type,
        request.title,
        request.description,
        request.metadata,
    )


@router.get(
    "/{project_id}/actions/pending",
    response_model=list[CopilotActionResponse],
)
async def get_pending_actions(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get pending actions."""
    return await service.get_pending_actions(db, project_id)


@router.post("/{project_id}/actions/{action_id}/complete")
async def complete_action(
    project_id: str,
    action_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Mark action as completed."""
    return await service.complete_action(db, action_id)


@router.post("/{project_id}/orchestrate/analyze")
async def orchestrate_analyze(
    project_id: str,
    video_id: str,
):
    """Orchestrate M9 analysis module."""
    return await service.orchestrate_analysis(project_id, video_id)


@router.post("/{project_id}/orchestrate/edit-plan")
async def orchestrate_edit_plan(
    project_id: str,
    video_id: str,
    suggestions: list[str],
):
    """Orchestrate edit plan generation."""
    return await service.orchestrate_edit_plan(project_id, video_id, suggestions)


@router.post("/{project_id}/orchestrate/render")
async def orchestrate_render(
    project_id: str,
    edit_plan_id: str,
    settings: dict,
):
    """Orchestrate M12 rendering."""
    return await service.orchestrate_render(project_id, edit_plan_id, settings)


@router.post("/{project_id}/orchestrate/publish")
async def orchestrate_publish(
    project_id: str,
    render_id: str,
    platforms: list[str],
):
    """Orchestrate M13 publishing."""
    return await service.orchestrate_publish(project_id, render_id, platforms)


@router.post("/{project_id}/orchestrate/learning")
async def orchestrate_learning(
    project_id: str,
    video_id: str,
):
    """Orchestrate M14 learning insights."""
    return await service.orchestrate_learning(project_id, video_id)
