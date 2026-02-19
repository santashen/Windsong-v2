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
- Routes under `/api/v1` prefix, health check at `/health`, Swagger UI at `/swagger/`
- In dev mode, CORS allows localhost:5173 and localhost:3000

## API 规范

开发新接口时必须遵循以下规范。

### 统一响应格式

所有接口使用 `handlers.Response` 信封，通过辅助函数返回响应：

```go
// 成功 (200)
handlers.Success(c, data)

// 创建成功 (201)
handlers.SuccessCreated(c, data)

// 业务错误
handlers.Error(c, http.StatusNotFound, handlers.CodeNotFound, "Resource not found")

// 参数校验失败（自动解析 validator.ValidationErrors）
handlers.ValidationError(c, err)
```

响应体结构：`{"code": 0, "message": "success", "data": {...}}`，错误时 `data` 省略。

### 错误码

| 常量 | 值 | 含义 |
|------|------|------|
| `CodeSuccess` | 0 | 成功 |
| `CodeBadRequest` | 40000 | 请求参数错误 |
| `CodeValidationError` | 40001 | 参数校验失败 |
| `CodeUnauthorized` | 40100 | 未认证 |
| `CodeNotFound` | 40400 | 资源不存在 |
| `CodeInternalError` | 50000 | 服务器内部错误 |
| `CodeExternalService` | 50200 | 外部服务调用失败 |

新增错误码遵循 `HTTP状态码 × 100 + 子码` 的命名规则，定义在 `handlers/response.go`。

### 请求参数校验

- JSON body 使用 `binding` tag + `c.ShouldBindJSON()`，错误交给 `ValidationError(c, err)`
- Query 参数定义 struct 使用 `form` + `binding` tag + `c.ShouldBindQuery()`
- 不要手动 `strconv.Atoi` 解析分页参数，用 query struct 代替
- 分页参数默认值：`Page=1, PageSize=20`，在 handler 中用 `if == 0` 赋默认值

### Swagger 注释

每个 handler 方法必须添加 swaggo 注释，新增接口后执行 `cd backend && swag init` 重新生成文档：

```go
// GetResource godoc
// @Summary      简要描述
// @Description  详细描述
// @Tags         分组名
// @Accept       json
// @Produce      json
// @Security     ApiKeyAuth           // 需要认证时添加
// @Param        id   path   int    true  "Resource ID"
// @Param        body body   Input  true  "Request body"
// @Success      200  {object}  handlers.Response{data=models.Resource}
// @Failure      400  {object}  handlers.Response
// @Router       /resource/{id} [get]
```

### 前端对接

- 后端 API baseURL 为 `/api/v1`（`frontend/src/api/index.js`）
- 响应拦截器自动解包信封：`response.data` 已经是内层 `data` 字段
- 业务错误（code ≠ 0）自动 reject，store 中通过 `err.message` 获取错误信息
- AI 服务的 `aiApi` 实例不经过信封解包，保持原样

### Frontend (`frontend/src/`)
- Vue 3 + Vite + Vue Router + Pinia
- **Prefer Vue 3 Composition API style**:
  - Components: Use `<script setup>` syntax
  - Pinia stores: Use Setup Store syntax (function with `ref`, `computed`, return object)
  - Avoid Options API unless necessary for compatibility
- `@` alias resolves to `src/` directory
- API requests: `/api/v1` proxied to backend:8080, `/ai-api` proxied to ai-service:8000 (in dev via Vite config)
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
