# Development Guide

## Principles

- SOLID design
- Clean architecture boundaries
- Repository pattern for persistence access
- Dependency injection through explicit composition
- CQRS for command/query-heavy modules when domain complexity grows
- Strict typing in both Python and TypeScript
- Shared infrastructure clients created at application startup, not per request
- Sanitized operational responses that avoid leaking raw dependency errors

## Backend Layout

- `api/`: transport layer and route contracts
- `controllers/`: request orchestration
- `services/`: application services
- `repositories/`: infrastructure data access
- `models/`: persistence models
- `database/`: engine and session management
- `middleware/`: cross-cutting request behavior
- `core/`: runtime state, request context, and infrastructure client composition
- `events/`, `jobs/`, `websocket/`: async and realtime boundaries

## Frontend Layout

- `app/`: composition root
- `components/`: reusable UI primitives and layout
- `features/`: bounded dashboard modules
- `config/`: renderer runtime configuration
- `lib/`: helpers
- `styles/`: global styling and theme tokens

## Quality Gates

- Python: `pytest`, `ruff`, `mypy`
- Desktop: `vitest`, `playwright`, `eslint`, `tsc`
- Containers: `docker compose config`
- Repository: `pnpm verify`
