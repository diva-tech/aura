"""AURA Studio API main application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from studio_api.api import router
from studio_api.database.base import Base
from studio_api.database.config import engine

# Import models to register them with Base
from studio_api.models import Project, Video  # noqa: F401
from studio_api.models.analysis import (  # noqa: F401
    AnalysisReport,
    Scene,
    Suggestion,
    Transcript,
    VideoMetrics,
)
from studio_api.models.copilot import (  # noqa: F401
    CopilotChat,
    CopilotMemory,
    CopilotRecommendation,
    CopilotAction,
)
from studio_api.models.creator_intelligence import (  # noqa: F401
    CreatorProfile,
    CreatorBrief,
    CreatorInsight,
    AIExplanation,
    PerformancePrediction,
    VideoHealthScore,
    ContentOpportunity,
    ThumbnailInsight,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan."""
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="AURA Studio API",
    description="Project workspace and video management for AURA Studio",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)
