#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../apps/backend"
uvicorn aura_backend.main:app --reload --app-dir src --host 0.0.0.0 --port 8000
