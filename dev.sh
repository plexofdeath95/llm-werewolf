#!/usr/bin/env bash
# Start the backend (FastAPI on :8000) and the frontend (Vite on :5173) together. macOS / Linux.
# Uses uv when it is installed, otherwise the active Python (e.g. a venv made with pip).
# No --reload: restart this script after backend changes (it also ends live games).
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONUTF8=1
if command -v uv >/dev/null 2>&1; then PY=(uv run python); else PY=(python3); fi
"${PY[@]}" -m uvicorn aiplays.main:app --port 8000 --timeout-graceful-shutdown 3 &
API=$!
trap 'kill "$API" 2>/dev/null || true' EXIT INT TERM
cd frontend
[ -d node_modules ] || npm install
npm run dev
