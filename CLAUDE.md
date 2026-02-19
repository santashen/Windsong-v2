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
- `logger/` - zerolog structured logger (`logger.Log` global instance)
- `middleware/` - RequestID, Logger, Recovery, AdminAuth
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

## Logging Conventions

项目使用结构化日志。开发环境输出彩色可读格式，生产环境输出 JSON。新增接口或服务时必须遵循以下规范。

### Go 后端（zerolog）

**Handler 层** — 通过 `middleware.GetLogger(c)` 获取携带 request_id 的 logger：
```go
// 错误分支必须记录日志，级别按语义选择
middleware.GetLogger(c).Error().Err(err).Msg("failed to create photo")
middleware.GetLogger(c).Warn().Err(err).Str("slug", slug).Msg("post not found")
```

**Service 层** — 无 gin.Context 时使用全局 `logger.Log`：
```go
import "windsong/logger"

logger.Log.Info().Str("dir", dir).Msg("cloning repository")
logger.Log.Error().Err(err).Str("url", url).Msg("failed to save photo")
```

**规则：**
- 不要使用 stdlib `log` 包，全部使用 `logger.Log` 或 `middleware.GetLogger(c)`
- 日志消息用小写英文，描述"发生了什么"（如 `"failed to fetch posts"`），不要包含变量值——变量通过 `.Str()` / `.Int()` / `.Err()` 等链式方法传入
- Handler 中 4xx 用 Warn，5xx 用 Error；正常流程不需要在 handler 层打日志
- Service 中关键操作（外部调用、数据同步等）记录 Info，失败记录 Error
- 不要在循环内打 Info/Warn 级别日志，避免日志洪泛

### Python AI 服务（structlog）

**获取 logger：**
```python
import structlog
logger = structlog.get_logger()
```

**记录日志：**
```python
# 使用关键字参数传递上下文，不要用 f-string
logger.info("gold analysis started", model=model_name)
logger.error("failed to fetch stock history", code=code, error=str(e))
logger.debug("cumulative NAV not available", code=code, error=str(e))
```

**规则：**
- 不要使用 stdlib `logging`，全部使用 `structlog.get_logger()`
- request_id 通过中间件自动注入（`structlog.contextvars`），service 层无需手动传递
- 日志消息用小写英文静态字符串，变量通过关键字参数传入，不要用 f-string 拼接
- 外部 API 调用（LLM、akshare 等）的开始/完成/失败应记录日志
- `except Exception: pass` 是禁止的——至少用 `logger.debug` 记录
