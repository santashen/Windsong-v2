#!/usr/bin/env bash

set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
  trap - EXIT INT TERM
  echo
  echo "Stopping local development processes..."
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

cd "${ROOT_DIR}"

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
echo "Press Ctrl+C to stop the backend and frontend. PostgreSQL will remain running."

while kill -0 "${BACKEND_PID}" 2>/dev/null && kill -0 "${FRONTEND_PID}" 2>/dev/null; do
  sleep 1
done
