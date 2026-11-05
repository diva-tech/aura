# AURA Studio API

FastAPI-based backend for AURA Studio - project workspace and video management.

## Features

- Project management (create, list, update, delete)
- Video upload with drag & drop support
- Automatic metadata extraction (duration, resolution, codec, FPS)
- Thumbnail generation
- RESTful API
- PostgreSQL storage
- Redis caching
- CORS enabled
- OpenAPI documentation

## Setup

```bash
# Install dependencies
pip install -e .

# Set environment variables
export DATABASE_URL=postgresql+asyncpg://aura:aura@localhost:5432/aura_studio

# Run server
uvicorn studio_api.main:app --reload --port 8001
```

## API Endpoints

### Projects

- `POST /api/projects` - Create project
- `GET /api/projects` - List all projects
- `GET /api/projects/{id}` - Get project
- `DELETE /api/projects/{id}` - Delete project

### Videos

- `POST /api/projects/{id}/upload` - Upload video
- `GET /api/videos/{id}` - Get video info
- `GET /api/projects/{id}/videos` - List project videos
- `DELETE /api/videos/{id}` - Delete video

### Analysis

- `POST /api/projects/{id}/analyze` - Queue for analysis (placeholder)

### Health

- `GET /api/health` - Health check

## Database

Requires PostgreSQL 16+. Creates tables automatically on startup.

## Storage

Videos stored in `/storage/uploads/{project_id}/`
Thumbnails stored alongside videos with `_thumb.jpg` suffix

## Requirements

- Python 3.12+
- PostgreSQL 16+
- ffmpeg (for video processing)
