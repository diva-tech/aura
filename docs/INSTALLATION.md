# Installation Guide

## Prerequisites

- Python 3.12
- Node.js 22+
- pnpm 9+
- Docker and Docker Compose

## Local Setup

1. Copy environment templates as needed and update placeholder values.
2. Install JavaScript dependencies with `pnpm install`.
3. Create a virtual environment and install backend dependencies with `pip install -e ./apps/backend[dev]`.
4. Start infrastructure with `docker compose up -d postgres redis rabbitmq ollama`.
5. Run the backend with `./scripts/dev-backend.sh`.
6. Run the desktop shell with `./scripts/dev-desktop.sh`.

## Full Stack via Docker

Run `docker compose up --build`.

Note:

- The `desktop` container exposes a production renderer preview on port `4173` for headless environments.
- The native Electron shell is still run locally during development.
