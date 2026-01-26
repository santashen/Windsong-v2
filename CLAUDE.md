# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Windsong is a personal blog system built with Go backend and Vue 3 frontend, using PostgreSQL for data storage. The project supports Docker containerization and GitHub Actions CI/CD.

## Development Commands

### Database
```bash
docker-compose up -d  # Start PostgreSQL
```

### Backend (Go)
```bash
cd backend
cp .env.example .env  # First time setup
go mod download
go run main.go        # Runs on http://localhost:8080
```

### Frontend (Vue)
```bash
cd frontend
npm install
npm run dev           # Runs on http://localhost:5173
npm run build         # Production build
```

### Docker Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Architecture

### Backend (`backend/`)
- Single `main.go` entry point using Gin web framework
- GORM for PostgreSQL database operations
- Routes under `/api` prefix, health check at `/health`
- Environment config via `.env` file (DATABASE_URL, PORT, ENV)
- In dev mode, CORS allows localhost:5173 and localhost:3000

### Frontend (`frontend/src/`)
- Vue 3 + Vite + Vue Router + Pinia
- `@` alias resolves to `src/` directory
- API requests go to `/api` (proxied to backend:8080 in dev via Vite config)
- Components: `components/layout/` for Header/Footer
- Views: `views/` for page components
- API layer: `api/index.js` wraps axios with interceptors

### Deployment
- GitHub Actions builds Docker images on push to main/develop
- Images pushed to ghcr.io/santashen/
- Auto-deploy to server on develop branch push
- Production uses Nginx reverse proxy for frontend static files
- Backend exposed internally on port 9080, frontend on 9081
