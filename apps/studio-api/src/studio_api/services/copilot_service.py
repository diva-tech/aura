"""AURA AI Copilot service orchestrating M9-M14."""

import json
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from studio_api.models.copilot import (
    CopilotAction,
    CopilotChat,
    CopilotMemory,
    CopilotRecommendation,
)
from studio_api.schemas.copilot import (
    CopilotActionCreate,
    CopilotChatCreate,
    CopilotMemoryCreate,
    CopilotRecommendationCreate,
)


class CopilotService:
    """Orchestrates M9-M14 AURA Engine modules."""

    async def save_chat_message(
        self,
        db: AsyncSession,
        project_id: str,
        role: str,
        message: str,
        context: Optional[dict] = None,
    ) -> CopilotChat:
        """Save chat message to history."""
        chat = CopilotChat(
            id=f"chat_{datetime.utcnow().timestamp()}",
            project_id=project_id,
            role=role,
            message=message,
            context=json.dumps(context) if context else None,
        )
        db.add(chat)
        await db.commit()
        await db.refresh(chat)
        return chat

    async def get_chat_history(
        self, db: AsyncSession, project_id: str, limit: int = 50
    ) -> list[CopilotChat]:
        """Get chat history for project."""
        from sqlalchemy import desc, select

        query = select(CopilotChat).where(
            CopilotChat.project_id == project_id
        ).order_by(desc(CopilotChat.created_at)).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def save_memory(
        self,
        db: AsyncSession,
        project_id: str,
        memory_type: str,
        key: str,
        value: dict,
    ) -> CopilotMemory:
        """Save user preference or memory."""
        memory = CopilotMemory(
            id=f"mem_{datetime.utcnow().timestamp()}",
            project_id=project_id,
            memory_type=memory_type,
            key=key,
            value=json.dumps(value),
        )
        db.add(memory)
        await db.commit()
        await db.refresh(memory)
        return memory

    async def get_memory(
        self,
        db: AsyncSession,
        project_id: str,
        memory_type: str,
        key: str,
    ) -> Optional[CopilotMemory]:
        """Get specific memory."""
        from sqlalchemy import and_, select

        query = select(CopilotMemory).where(
            and_(
                CopilotMemory.project_id == project_id,
                CopilotMemory.memory_type == memory_type,
                CopilotMemory.key == key,
            )
        )
        result = await db.execute(query)
        return result.scalar()

    async def create_recommendation(
        self,
        db: AsyncSession,
        project_id: str,
        rec_type: str,
        title: str,
        description: str,
        action: Optional[str] = None,
        priority: int = 5,
    ) -> CopilotRecommendation:
        """Create AI recommendation."""
        recommendation = CopilotRecommendation(
            id=f"rec_{datetime.utcnow().timestamp()}",
            project_id=project_id,
            recommendation_type=rec_type,
            title=title,
            description=description,
            action=action,
            priority=priority,
        )
        db.add(recommendation)
        await db.commit()
        await db.refresh(recommendation)
        return recommendation

    async def get_recommendations(
        self, db: AsyncSession, project_id: str, limit: int = 10
    ) -> list[CopilotRecommendation]:
        """Get active recommendations for project."""
        from sqlalchemy import desc, select

        query = select(CopilotRecommendation).where(
            CopilotRecommendation.project_id == project_id
        ).order_by(desc(CopilotRecommendation.priority)).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def create_action(
        self,
        db: AsyncSession,
        project_id: str,
        action_type: str,
        title: str,
        description: str,
        metadata: Optional[dict] = None,
    ) -> CopilotAction:
        """Create action item."""
        action = CopilotAction(
            id=f"act_{datetime.utcnow().timestamp()}",
            project_id=project_id,
            action_type=action_type,
            title=title,
            description=description,
            metadata=json.dumps(metadata) if metadata else None,
        )
        db.add(action)
        await db.commit()
        await db.refresh(action)
        return action

    async def get_pending_actions(
        self, db: AsyncSession, project_id: str
    ) -> list[CopilotAction]:
        """Get pending actions for project."""
        from sqlalchemy import select

        query = select(CopilotAction).where(
            CopilotAction.project_id == project_id,
            CopilotAction.completed == "pending",
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def complete_action(
        self, db: AsyncSession, action_id: str
    ) -> CopilotAction:
        """Mark action as completed."""
        from sqlalchemy import select

        query = select(CopilotAction).where(CopilotAction.id == action_id)
        result = await db.execute(query)
        action = result.scalar()
        if action:
            action.completed = "completed"
            await db.commit()
            await db.refresh(action)
        return action

    async def orchestrate_analysis(
        self, project_id: str, video_id: str
    ) -> dict:
        """Orchestrate M9 analysis module."""
        return {
            "type": "analysis",
            "video_id": video_id,
            "status": "queued",
            "message": "Starting AI video analysis...",
        }

    async def orchestrate_edit_plan(
        self, project_id: str, video_id: str, suggestions: list[str]
    ) -> dict:
        """Orchestrate edit plan generation from M9 suggestions."""
        return {
            "type": "edit_plan",
            "video_id": video_id,
            "suggestions": suggestions,
            "status": "generating",
            "message": "Creating optimized edit plan...",
        }

    async def orchestrate_render(
        self, project_id: str, edit_plan_id: str, settings: dict
    ) -> dict:
        """Orchestrate M12 rendering engine."""
        return {
            "type": "render",
            "edit_plan_id": edit_plan_id,
            "settings": settings,
            "status": "queued",
            "message": "Adding to render queue...",
        }

    async def orchestrate_publish(
        self, project_id: str, render_id: str, platforms: list[str]
    ) -> dict:
        """Orchestrate M13 publishing hub."""
        return {
            "type": "publish",
            "render_id": render_id,
            "platforms": platforms,
            "status": "queued",
            "message": f"Preparing to publish to {len(platforms)} platforms...",
        }

    async def orchestrate_learning(
        self, project_id: str, video_id: str
    ) -> dict:
        """Orchestrate M14 learning engine for insights."""
        return {
            "type": "learning",
            "video_id": video_id,
            "status": "analyzing",
            "message": "Extracting AI-learned insights...",
        }
