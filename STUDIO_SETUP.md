# AURA Studio v1 Setup Guide

## Quick Start

```bash
# 1. Install backend dependencies
cd apps/studio-api
pip install -e .

# 2. Install frontend dependencies
cd ../studio-web
npm install

# 3. Run with docker-compose
cd ../..
docker-compose -f docker-compose.studio.yml up --build

# 4. Open browser
# Frontend: http://localhost:3000
# API Docs: http://localhost:8001/docs
```

## Architecture

### Backend (studio-api)

- FastAPI framework
- SQLAlchemy ORM
- PostgreSQL database
- Redis cache
- Video storage and thumbnail generation

### Frontend (studio-web)

- Next.js 15 with React 19
- TypeScript
- Tailwind CSS
- React Query for data fetching
- Zustand for state management
- React Hook Form for forms
- React Dropzone for file uploads
- React Player for video preview

## Database Schema

### projects table

- id (UUID)
- name (string)
- description (text)
- target_platform (string)
- language (string)
- aspect_ratio (string)
- status (string)
- created_at (timestamp)
- updated_at (timestamp)

### videos table

- id (UUID)
- project_id (UUID, FK)
- filename (string)
- duration (int)
- resolution (string)
- codec (string)
- fps (int)
- size (int)
- status (string)
- storage_path (string)
- thumbnail_path (string)
- created_at (timestamp)
- updated_at (timestamp)

## API Endpoints

### Projects

- `POST /api/projects` - Create project
- `GET /api/projects` - List projects
- `GET /api/projects/{id}` - Get project
- `DELETE /api/projects/{id}` - Delete project

### Videos

- `POST /api/projects/{id}/upload` - Upload video
- `GET /api/videos/{id}` - Get video
- `GET /api/projects/{id}/videos` - List project videos
- `DELETE /api/videos/{id}` - Delete video

### Analysis

- `POST /api/projects/{id}/analyze` - Queue for analysis (placeholder)

## Features Implemented

✅ Project creation dialog
✅ Video upload with drag & drop
✅ Video preview with thumbnails
✅ Project dashboard
✅ Storage management
✅ Metadata extraction
✅ Thumbnail generation
✅ API endpoints
✅ Database models
✅ Service layer
✅ Repository pattern
✅ Dark theme UI
✅ Loading states
✅ Error handling
✅ Placeholder AI analysis

## File Structure

```
apps/
  studio-api/
    src/studio_api/
      __init__.py
      main.py
      api/              # API routes
      models/           # Database models
      schemas/          # Pydantic schemas
      services/         # Business logic
      database/         # Database config & repos
      storage/          # File storage service
    pyproject.toml
    Dockerfile

  studio-web/
    src/
      app/
        layout.tsx
        page.tsx
        project/
          [id]/
            page.tsx
      components/       # React components
      lib/
        api.ts          # API client
        store.ts        # Zustand store
    package.json
    next.config.js
    Dockerfile

storage/
  uploads/              # Video files
  projects/             # Project data
```

## Next Steps

1. ✅ Create project dialog
2. ✅ Video upload component
3. ✅ Video preview
4. ✅ Project dashboard
5. ⏳ Connect to M9-M14 engine for actual AI analysis
6. ⏳ Add project templates
7. ⏳ Add rendering pipeline
8. ⏳ Add publishing pipeline
9. ⏳ Add collaboration features
10. ⏳ Add asset management

## Development

### Backend development

```bash
cd apps/studio-api
uvicorn studio_api.main:app --reload --port 8001
```

### Frontend development

```bash
cd apps/studio-web
npm run dev
```

### Run tests

```bash
# Backend
cd apps/studio-api
pytest

# Frontend
cd apps/studio-web
npm test
```
