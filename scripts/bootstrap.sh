#!/usr/bin/env bash
set -euo pipefail

pnpm install

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ./apps/backend[dev]
