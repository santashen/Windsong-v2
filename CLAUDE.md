# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Windsong is a personal blog system with Go backend, Vue 3 frontend, and Python AI service, using PostgreSQL for data storage. Features include blog posts (git-synced markdown), photo gallery, gold analysis (AI-powered), finance data viewer, and real-time monitoring. The project supports Docker containerization and GitHub Actions CI/CD.

## Development Commands

### Database
```bash
docker-compose up -d  # Start PostgreSQL + Flyway migrations
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

### AI Service (Python)
```bash
cd ai-service
pip install -r requirements.txt
cp .env.example .env  # Configure LLM API keys
python main.py        # Runs on http://localhost:8000
```

### Docker Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Architecture

### Backend (`backend/`)
- Entry point: `main.go` using Gin web framework
- Layered structure: `routes/` -> `handlers/` -> `services/` -> `models/`
- `config/` - Environment config (DATABASE_URL, PORT, ENV, ADMIN_API_KEY, POSTS_REPO_URL, AI_SERVICE_URL)
- `database/` - GORM PostgreSQL connection
- `models/` - Post, Photo, GoldAnalysis
- `handlers/` - auth, post, photo, gold_analysis
- `services/` - post (git sync + markdown parsing), photo (CRUD + import), gold_analysis (AI service calls)
- `middleware/` - AdminAuth (API key verification)
- Routes under `/api` prefix, health check at `/health`
- In dev mode, CORS allows localhost:5173 and localhost:3000

### Frontend (`frontend/src/`)
- Vue 3 + Vite + Vue Router + Pinia
- **Prefer Vue 3 Composition API style**:
  - Components: Use `<script setup>` syntax
  - Pinia stores: Use Setup Store syntax (function with `ref`, `computed`, return object)
  - Avoid Options API unless necessary for compatibility
- `@` alias resolves to `src/` directory
- API requests: `/api` proxied to backend:8080, `/ai-api` proxied to ai-service:8000 (in dev via Vite config)
- Views: Home, Gallery, BlogList, BlogPost, About, Services, GoldAnalysis, Monitor, FinanceView, Admin (Login/Photos)
- Components: `layout/` (Header/Footer), `blog/`, `gallery/`, `monitor/`, `admin/`, `icons/`
- Stores: auth, blog, gallery, gold, monitor, finance
- API layer: `api/index.js` wraps axios; `api/admin/photos.js` for admin; `api/auth.js` for auth
- Markdown rendering with `marked`, LaTeX with `katex`, charts with `echarts`, 3D with `three.js`

### AI Service (`ai-service/`)
- Python 3.12 + FastAPI
- OpenAI-compatible LLM integration (configurable provider)
- Services: gold analysis (LLM-powered), finance data (stocks/funds via akshare)
- Endpoints: `/api/gold/analyze`, `/api/finance/search`, `/api/finance/history`

### Database (`db/migrations/`)
- PostgreSQL 16 with Flyway for schema migrations
- Tables: posts, photos, gold_analyses
- Migration files in `db/migrations/` following Flyway naming convention (V1__, V2__, etc.)

### Deployment
- GitHub Actions builds Docker images for backend, frontend, and ai-service on push to main/develop
- Images pushed to ghcr.io/santashen/
- Auto-deploy to server on develop branch push (deploy path: `/data/web-dockers/Windsong-v2`)
- Production uses Nginx reverse proxy: `/api/` -> backend:9080, `/` -> frontend:9081
- Services on `windsong-network` Docker bridge
