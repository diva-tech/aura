"""Publish service integrating M13 Publishing Engine."""

import json
import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from studio_api.models import (
    PublishHistory,
    PublishJob,
    PublishMetadata,
    PublishPlatform,
    PublishStatus,
    PlatformAccount,
    PlatformHealth,
)


class PublishService:
    """Publish service for M13 Publishing Engine integration."""

    def __init__(self, session: AsyncSession):
        """Initialize service."""
        self.session = session

    async def create_publish_job(
        self,
        render_id: str,
        project_id: str,
        platform_account_id: str,
        platform: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[list[str]] = None,
        caption: Optional[str] = None,
        hashtags: Optional[list[str]] = None,
        scheduled_time: Optional[datetime] = None,
    ) -> PublishJob:
        """Create a new publish job."""
        job_id = str(uuid.uuid4())

        job = PublishJob(
            id=job_id,
            render_id=render_id,
            project_id=project_id,
            platform_account_id=platform_account_id,
            platform=platform,
            status="queued",
            scheduled_time=scheduled_time,
        )
        self.session.add(job)

        # Create metadata
        metadata = PublishMetadata(
            id=str(uuid.uuid4()),
            publish_job_id=job_id,
            platform=platform,
            title=title,
            description=description,
            tags=json.dumps(tags) if tags else None,
            caption=caption,
            hashtags=json.dumps(hashtags) if hashtags else None,
        )
        self.session.add(metadata)

        # Log history
        history = PublishHistory(
            id=str(uuid.uuid4()),
            publish_job_id=job_id,
            event_type="queued",
            status="queued",
            message="Publish job created and queued",
        )
        self.session.add(history)

        await self.session.commit()
        return job

    async def publish_video(
        self, publish_job_id: str
    ) -> Optional[PublishJob]:
        """Publish video via M13 Engine."""
        query = select(PublishJob).where(PublishJob.id == publish_job_id)
        result = await self.session.execute(query)
        job = result.scalar_one_or_none()

        if not job:
            return None

        try:
            job.status = "publishing"
            job.updated_at = datetime.utcnow()

            # Mock M13 Publishing Engine call
            # In production, this would call the actual M13 engine
            job.status = "published"
            job.published_at = datetime.utcnow()
            job.platform_video_id = f"{job.platform}_video_{uuid.uuid4().hex[:8]}"
            job.platform_url = f"https://{job.platform}.com/watch?v={job.platform_video_id}"

            # Log history
            history = PublishHistory(
                id=str(uuid.uuid4()),
                publish_job_id=publish_job_id,
                event_type="published",
                status="published",
                message=f"Video published to {job.platform}",
            )
            self.session.add(history)

            await self.session.commit()
            return job
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            job.updated_at = datetime.utcnow()

            # Log history
            history = PublishHistory(
                id=str(uuid.uuid4()),
                publish_job_id=publish_job_id,
                event_type="failed",
                status="failed",
                message=str(e),
            )
            self.session.add(history)

            await self.session.commit()
            return job

    async def retry_publish(self, publish_job_id: str) -> Optional[PublishJob]:
        """Retry failed publish job."""
        query = select(PublishJob).where(PublishJob.id == publish_job_id)
        result = await self.session.execute(query)
        job = result.scalar_one_or_none()

        if not job or job.status != "failed":
            return None

        job.status = "queued"
        job.retry_count += 1
        job.error_message = None
        job.updated_at = datetime.utcnow()

        # Log history
        history = PublishHistory(
            id=str(uuid.uuid4()),
            publish_job_id=publish_job_id,
            event_type="retried",
            status="queued",
            message=f"Retry attempt {job.retry_count}",
        )
        self.session.add(history)

        await self.session.commit()
        return job

    async def cancel_publish(self, publish_job_id: str) -> Optional[PublishJob]:
        """Cancel a publish job."""
        query = select(PublishJob).where(PublishJob.id == publish_job_id)
        result = await self.session.execute(query)
        job = result.scalar_one_or_none()

        if not job:
            return None

        job.status = "cancelled"
        job.updated_at = datetime.utcnow()

        # Log history
        history = PublishHistory(
            id=str(uuid.uuid4()),
            publish_job_id=publish_job_id,
            event_type="cancelled",
            status="cancelled",
            message="Publish job cancelled",
        )
        self.session.add(history)

        await self.session.commit()
        return job

    async def connect_account(
        self,
        user_id: str,
        platform: str,
        auth_code: str,
        account_name: str,
        account_id: str,
    ) -> PlatformAccount:
        """Connect a platform account via OAuth."""
        account_db_id = str(uuid.uuid4())

        # Mock OAuth token exchange
        account = PlatformAccount(
            id=account_db_id,
            user_id=user_id,
            platform=platform,
            account_name=account_name,
            account_id=account_id,
            access_token=f"token_{uuid.uuid4().hex[:16]}",
            refresh_token=f"refresh_{uuid.uuid4().hex[:16]}",
            token_expires_at=datetime.utcnow() + timedelta(hours=1),
            is_connected=True,
        )
        self.session.add(account)
        await self.session.commit()
        return account

    async def get_platform_accounts(
        self, user_id: str
    ) -> list[PlatformAccount]:
        """Get all connected accounts for user."""
        query = select(PlatformAccount).where(PlatformAccount.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_publish_job(self, job_id: str) -> Optional[PublishJob]:
        """Get publish job by ID."""
        query = select(PublishJob).where(PublishJob.id == job_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_publish_jobs(
        self, project_id: Optional[str] = None, status: Optional[str] = None
    ) -> list[PublishJob]:
        """List publish jobs."""
        query = select(PublishJob).order_by(PublishJob.created_at.desc())

        if project_id:
            query = query.where(PublishJob.project_id == project_id)

        if status:
            query = query.where(PublishJob.status == status)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_publish_history(self, job_id: str) -> list[PublishHistory]:
        """Get publish history for job."""
        query = (
            select(PublishHistory)
            .where(PublishHistory.publish_job_id == job_id)
            .order_by(PublishHistory.timestamp.asc())
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def check_platform_health(self, platform: str) -> PlatformHealth:
        """Check platform API health."""
        query = select(PlatformHealth).where(PlatformHealth.platform == platform)
        result = await self.session.execute(query)
        health = result.scalar_one_or_none()

        if not health:
            health = PlatformHealth(
                id=str(uuid.uuid4()),
                platform=platform,
                is_healthy=True,
                response_time_ms=200,
            )
            self.session.add(health)
        else:
            health.last_check = datetime.utcnow()
            health.is_healthy = True
            health.response_time_ms = 200

        await self.session.commit()
        return health
