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

### Testing

#### Backend 测试约定

**依赖注入模式：** Handler 通过接口持有 service，service 通过接口持有外部依赖。新增代码必须遵循此模式。

- Handler 层接口定义在 `handlers/interfaces.go`，handler struct 字段使用接口类型而非具体 service 指针
- Service 层外部依赖接口定义在 `services/interfaces.go`（如 `HTTPClient`、`GitSyncer`），通过构造函数可选参数注入，默认使用真实实现

**新增 handler 时：**
1. 在 `handlers/interfaces.go` 添加对应的 service 接口
2. handler struct 字段类型使用该接口
3. 创建 `handlers/<name>_test.go`，用函数式 mock 测试（参考现有 handler 测试）
4. 使用 `handlers/testutil_test.go` 中的 `performRequest` 辅助函数

**新增 service 时：**
1. 若依赖外部服务（HTTP API、命令行工具等），在 `services/interfaces.go` 定义接口，构造函数用 `...Interface` 可变参数注入
2. 纯函数（解析、转换等）直接写单元测试：`services/<name>_test.go`
3. 涉及数据库的逻辑写集成测试：`services/<name>_integration_test.go`，加 `//go:build integration` 标签，使用 `testutil/testdb.go` 启动临时 PostgreSQL

**运行测试：**
```bash
cd backend
go test ./...                          # 单元测试
go test -tags integration ./...        # 含集成测试（需要 Docker）
go test -v -race -coverprofile=c.out ./...  # 带竞态检测和覆盖率
```

#### Frontend 测试约定

- 组件测试：Vitest + `@vue/test-utils`，配置在 `vite.config.js` 的 `test` 块
- Store 测试放 `stores/__tests__/`，组件测试放 `components/<module>/__tests__/`
- E2E 测试：Playwright，配置在 `playwright.config.js`，测试文件放 `e2e/`

**运行测试：**
```bash
cd frontend
npm test                # Vitest 单元/组件测试
npx playwright test     # E2E 测试
```

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
