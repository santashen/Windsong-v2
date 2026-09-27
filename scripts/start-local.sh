#!/usr/bin/env bash

set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python}"
BACKEND_PID=""
PYTHON_PID=""
FRONTEND_PID=""

cleanup() {
  trap - EXIT INT TERM
  echo
  echo "Stopping local development processes..."
  [[ -z "${PYTHON_PID}" ]] || kill "${PYTHON_PID}" 2>/dev/null || true
  [[ -z "${BACKEND_PID}" ]] || kill "${BACKEND_PID}" 2>/dev/null || true
  [[ -z "${FRONTEND_PID}" ]] || kill "${FRONTEND_PID}" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

for command_name in docker go npm; do
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    echo "Missing required command: ${command_name}" >&2
    exit 1
  fi
done

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "Missing required command: ${PYTHON_BIN}" >&2
  echo "Activate the Conda environment first, for example: conda activate windsong" >&2
  exit 1
fi

cd "${ROOT_DIR}"

# Make the root .env available to all local child processes, including Python.
# The file is intended for local development and should contain shell-compatible
# KEY=VALUE entries.
if [[ -f "${ROOT_DIR}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${ROOT_DIR}/.env"
  set +a
fi

echo "Starting PostgreSQL..."
docker compose up -d postgres

echo "Waiting for PostgreSQL..."
for _ in {1..30}; do
  if docker compose exec -T postgres pg_isready \
    -U "${DB_USER:-windsong}" \
    -d "${DB_NAME:-windsong}" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

if ! docker compose exec -T postgres pg_isready \
  -U "${DB_USER:-windsong}" \
  -d "${DB_NAME:-windsong}" >/dev/null 2>&1; then
  echo "PostgreSQL did not become ready in time." >&2
  exit 1
fi

echo "Applying database migrations..."
docker compose run --rm flyway migrate

if [[ ! -d "frontend/node_modules" ]]; then
  echo "Installing frontend dependencies..."
  npm --prefix frontend install
fi

if ! "${PYTHON_BIN}" -c "import windsong_python" >/dev/null 2>&1; then
  echo "The Windsong Python package is not installed in the current environment." >&2
  echo "Run: cd python && ${PYTHON_BIN} -m pip install -e '.[dev]'" >&2
  exit 1
fi

echo "Starting Python services on http://localhost:8000..."
(
  cd python
  "${PYTHON_BIN}" -m uvicorn windsong_python.main:app --host 0.0.0.0 --port 8000
) &
PYTHON_PID=$!

echo "Starting Go backend on http://localhost:8080..."
(
  cd backend
  go run main.go
) &
BACKEND_PID=$!

echo "Starting Vue frontend on http://localhost:5173..."
(
  cd frontend
  npm run dev -- --host 0.0.0.0
) &
FRONTEND_PID=$!

echo
echo "Local development environment is ready."
echo "Python: http://localhost:8000"
echo "Go backend: http://localhost:8080"
echo "Vue frontend: http://localhost:5173"
echo "Press Ctrl+C to stop the Python service, backend, and frontend. PostgreSQL will remain running."

while kill -0 "${PYTHON_PID}" 2>/dev/null && kill -0 "${BACKEND_PID}" 2>/dev/null && kill -0 "${FRONTEND_PID}" 2>/dev/null; do
  sleep 1
done
