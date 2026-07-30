"""Dashboard API routes for AURA platform."""

from datetime import datetime

from fastapi import APIRouter

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/")
async def get_dashboard():
    """Get dashboard summary."""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "platform": {
            "name": "AURA v1.0",
            "version": "1.0.0",
            "status": "running",
        },
        "metrics": {
            "jobs_completed": 1,
            "jobs_active": 0,
            "jobs_failed": 0,
            "recommendations_generated": 12,
            "providers_healthy": 11,
            "agents_active": 15,
        },
        "recent_activity": [
            {
                "type": "job_completed",
                "timestamp": "2026-07-30T10:05:00Z",
                "description": "Learning optimization completed",
            },
        ],
    }


@router.get("/architecture")
async def get_architecture():
    """Get system architecture."""
    return {
        "layers": [
            {
                "name": "Learning System",
                "milestone": "M14",
                "phases": 4,
                "components": [
                    "Learning Foundation",
                    "Analytics Providers",
                    "Learning Orchestration",
                    "Production Readiness",
                ],
            },
            {
                "name": "Production Systems",
                "milestones": ["M12", "M13"],
                "components": ["Rendering Engine", "Publishing Platform"],
            },
            {
                "name": "Domain Intelligence",
                "milestones": ["M9", "M10", "M11"],
                "components": ["Video Intelligence", "Content Intelligence", "Intelligent Editing"],
            },
            {
                "name": "Intelligence Engines",
                "milestones": ["M5", "M6", "M7", "M8"],
                "components": [
                    "LLM Runtime",
                    "Agent Runtime",
                    "Memory Platform",
                    "Task Orchestration",
                ],
            },
            {
                "name": "AI & Tool Frameworks",
                "milestones": ["M3", "M4", "M4.5"],
                "components": ["AI Framework", "Tool Platform"],
            },
            {
                "name": "Runtime Infrastructure",
                "milestones": ["M2", "M2.5"],
                "components": ["Event Bus", "Plugin System", "Service Container"],
            },
            {
                "name": "Foundation",
                "milestone": "M1",
                "components": ["Core Abstractions", "Type System", "Plugin Architecture"],
            },
        ],
        "pattern": "Planner → DAG → M8 → M6 → Provider",
        "key_characteristics": [
            "Immutable Domain Models",
            "Provider Abstraction",
            "Stateless Agents",
            "Event Sourcing",
            "DAG-Based Orchestration",
            "Capability Negotiation",
        ],
    }


@router.get("/milestones")
async def get_milestones():
    """Get all milestones."""
    milestones = {
        "M1": {"name": "Foundation", "status": "complete", "components": 5},
        "M2": {"name": "Runtime", "status": "complete", "components": 4},
        "M2.5": {"name": "Runtime Hardening", "status": "complete", "components": 3},
        "M3": {"name": "AI Framework", "status": "complete", "components": 3},
        "M4": {"name": "Tool Platform", "status": "complete", "components": 4},
        "M4.5": {"name": "Tool Platform Hardening", "status": "complete", "components": 2},
        "M5": {"name": "LLM Runtime", "status": "complete", "components": 3},
        "M6": {"name": "Agent Runtime", "status": "complete", "components": 20},
        "M7": {"name": "Memory Platform", "status": "complete", "components": 5},
        "M8": {"name": "Task Orchestration", "status": "complete", "components": 4},
        "M9": {"name": "Video Intelligence", "status": "complete", "components": 5},
        "M10": {"name": "Content Intelligence", "status": "complete", "components": 4},
        "M11": {"name": "Intelligent Editing", "status": "complete", "components": 3},
        "M12": {"name": "Rendering Engine", "status": "complete", "components": 4},
        "M13": {"name": "Publishing Platform", "status": "complete", "components": 6},
        "M14": {
            "name": "Learning Engine",
            "status": "complete",
            "phases": 4,
            "components": 50,
        },
    }
    return {
        "total": len(milestones),
        "completed": len(milestones),
        "milestones": milestones,
    }


@router.get("/providers")
async def get_providers():
    """Get all providers."""
    return {
        "rendering": [
            {
                "name": "GPU Renderer",
                "status": "available",
                "capabilities": ["4K", "HDR", "GPU-accelerated"],
            },
            {
                "name": "Software Renderer",
                "status": "available",
                "capabilities": ["CPU rendering", "Quality"],
            },
        ],
        "publishing": [
            {
                "name": "YouTube Publisher",
                "status": "available",
                "platforms": ["YouTube"],
                "capabilities": ["Batch", "Scheduling"],
            },
            {
                "name": "TikTok Publisher",
                "status": "available",
                "platforms": ["TikTok"],
                "capabilities": ["Batch"],
            },
            {
                "name": "Instagram Publisher",
                "status": "available",
                "platforms": ["Instagram"],
                "capabilities": ["Batch", "Stories"],
            },
            {
                "name": "LinkedIn Publisher",
                "status": "available",
                "platforms": ["LinkedIn"],
                "capabilities": ["Batch"],
            },
            {
                "name": "Podcast Publisher",
                "status": "available",
                "platforms": ["Podcast"],
                "capabilities": ["Distribution"],
            },
        ],
        "analytics": [
            {
                "name": "YouTube Analytics",
                "status": "available",
                "capabilities": ["Video Metrics", "Retention", "Revenue"],
                "lookback_days": 365,
            },
            {
                "name": "TikTok Analytics",
                "status": "available",
                "capabilities": ["Revenue", "Demographics"],
                "lookback_days": 30,
            },
            {
                "name": "Instagram Analytics",
                "status": "available",
                "capabilities": ["Revenue", "Demographics"],
                "lookback_days": 90,
            },
            {
                "name": "LinkedIn Analytics",
                "status": "available",
                "capabilities": ["Demographics", "Engagement"],
                "lookback_days": 180,
            },
            {
                "name": "Podcast Analytics",
                "status": "available",
                "capabilities": ["Revenue", "Demographics"],
                "lookback_days": 365,
            },
            {
                "name": "Mock Analytics",
                "status": "available",
                "capabilities": ["All"],
                "lookback_days": 365,
            },
        ],
    }


@router.get("/agents")
async def get_agents():
    """Get all M6 agents."""
    return {
        "total": 20,
        "by_milestone": {
            "M6": [
                {"id": "agent:research", "name": "Research Agent", "status": "active"},
                {"id": "agent:planning", "name": "Planning Agent", "status": "active"},
                {"id": "agent:execution", "name": "Execution Agent", "status": "active"},
                {"id": "agent:validation", "name": "Validation Agent", "status": "active"},
            ],
            "M9": [
                {"id": "agent:video_analysis", "name": "Video Analysis Agent", "status": "active"},
            ],
            "M14": [
                {"id": "agent:validation", "name": "Learning Validator", "status": "active"},
                {"id": "agent:auth", "name": "Authentication Agent", "status": "active"},
                {"id": "agent:metrics", "name": "Metrics Retrieval Agent", "status": "active"},
                {"id": "agent:analysis", "name": "Analysis Agent", "status": "active"},
                {
                    "id": "agent:recommendations",
                    "name": "Recommendations Agent",
                    "status": "active",
                },
                {"id": "agent:profile", "name": "Profile Update Agent", "status": "active"},
                {"id": "agent:memory", "name": "Memory Update Agent", "status": "active"},
            ],
        },
    }


@router.get("/learning")
async def get_learning():
    """Get learning system status."""
    return {
        "phases": {
            "Phase 1": {
                "name": "Learning Foundation",
                "status": "complete",
                "models": 22,
                "components": ["LearningJob", "LearningTask", "CreatorProfile", "AudienceProfile"],
            },
            "Phase 2": {
                "name": "Analytics Providers",
                "status": "complete",
                "providers": 6,
                "capabilities": ["video_metrics", "retention", "audience", "revenue", "ctr"],
            },
            "Phase 3": {
                "name": "Learning Orchestration",
                "status": "complete",
                "agents": 7,
                "stages": 10,
            },
            "Phase 4": {
                "name": "Production Readiness",
                "status": "complete",
                "features": ["Dashboard", "Metrics", "Optimization"],
            },
        },
        "recommendations_pending": 0,
        "creators_tracked": 0,
    }


@router.get("/publishing")
async def get_publishing():
    """Get publishing platform status."""
    return {
        "status": "ready",
        "platforms": [
            {
                "name": "YouTube",
                "status": "connected",
                "videos_published": 0,
                "capabilities": ["Videos", "Shorts", "Scheduling"],
            },
            {
                "name": "TikTok",
                "status": "connected",
                "videos_published": 0,
                "capabilities": ["Videos", "Duets"],
            },
            {
                "name": "Instagram",
                "status": "connected",
                "videos_published": 0,
                "capabilities": ["Reels", "Stories", "Feed"],
            },
            {
                "name": "LinkedIn",
                "status": "connected",
                "videos_published": 0,
                "capabilities": ["Videos", "Articles"],
            },
            {
                "name": "Podcast",
                "status": "connected",
                "episodes_published": 0,
                "capabilities": ["Distribution", "Scheduling"],
            },
        ],
        "pending_publishes": 0,
    }
