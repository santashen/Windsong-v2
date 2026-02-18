# Windsong Blog

一个基于 Go + Vue 3 + Python + PostgreSQL 的个人博客系统，支持 Docker 容器化部署和 GitHub Actions 自动化 CI/CD。

## 功能特性

- 博客系统 - 基于 Git 仓库同步的 Markdown 文章，支持 LaTeX 公式渲染
- 相册管理 - 照片展览与后台管理
- 黄金分析 - AI 驱动的黄金市场分析
- 财经数据 - 股票/基金历史数据对比查看
- 实时监控 - 数据可视化监控面板
- 管理后台 - API Key 认证的后台管理系统

## 项目结构

```
Windsong-v2/
├── backend/              # Go 后端 API
│   ├── main.go           # 入口文件
│   ├── config/           # 环境配置
│   ├── database/         # 数据库连接
│   ├── models/           # 数据模型 (Post, Photo, GoldAnalysis)
│   ├── routes/           # 路由配置
│   ├── handlers/         # 请求处理器
│   ├── services/         # 业务逻辑
│   ├── middleware/       # 中间件 (AdminAuth)
│   └── Dockerfile
├── frontend/             # Vue 3 前端
│   ├── src/
│   │   ├── api/          # API 封装
│   │   ├── router/       # 路由配置
│   │   ├── stores/       # Pinia 状态管理
│   │   ├── views/        # 页面组件
│   │   ├── components/   # 公共组件
│   │   └── style/        # 样式文件
│   ├── nginx.conf        # 容器内 Nginx 配置
│   └── Dockerfile
├── ai-service/           # Python AI 服务
│   ├── main.py           # FastAPI 入口
│   ├── config.py         # 配置管理
│   ├── services/         # LLM / 财经数据服务
│   ├── prompts/          # AI 提示词
│   └── Dockerfile
├── db/migrations/        # Flyway 数据库迁移
├── nginx/                # 主 Nginx 反向代理配置
├── scripts/              # 部署脚本
├── .github/workflows/    # GitHub Actions CI/CD
├── docker-compose.yml    # 开发环境 (PostgreSQL + Flyway)
├── docker-compose.prod.yml # 生产环境
└── .env.prod.example     # 生产环境变量模板
```

## 技术栈

### 后端
- Go 1.23 + Gin Web 框架
- GORM - ORM 库
- PostgreSQL 16 + Flyway 数据库迁移
- frontmatter - Markdown 前置数据解析

### 前端
- Vue 3 + Composition API (`<script setup>`)
- Vite 5 - 构建工具
- Vue Router - 路由
- Pinia - 状态管理
- Axios - HTTP 客户端
- marked - Markdown 渲染
- KaTeX - LaTeX 公式渲染
- ECharts - 图表可视化
- Three.js - 3D 图形

### AI 服务
- Python 3.12 + FastAPI
- OpenAI 兼容 LLM API
- akshare - 财经数据获取

## 快速开始

### 1. 启动数据库

```bash
docker-compose up -d  # 启动 PostgreSQL + Flyway 自动迁移
```

### 2. 启动后端

```bash
cd backend
cp .env.example .env  # 配置环境变量
go mod download
go run main.go        # http://localhost:8080
```

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev           # http://localhost:5173
```

### 4. 启动 AI 服务（可选）

```bash
cd ai-service
pip install -r requirements.txt
cp .env.example .env  # 配置 LLM API 密钥
python main.py        # http://localhost:8000
```

## API 概览

### 后端 API (`/api`)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| POST | `/api/auth/verify` | 验证管理员 API Key |
| GET | `/api/posts` | 获取文章列表 |
| GET | `/api/posts/:slug` | 获取单篇文章 |
| POST | `/api/webhooks/sync` | 同步 Git 仓库文章 (管理员) |
| GET | `/api/photos` | 获取照片列表（分页） |
| GET | `/api/photos/:id` | 获取单张照片 |
| GET | `/api/photos/filters` | 获取筛选选项 |
| POST/PUT/DELETE | `/api/photos` | 照片管理 (管理员) |
| GET | `/api/gold/today` | 获取今日黄金分析 |

### AI 服务 API (`/ai-api` 代理)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/gold/analyze` | AI 黄金分析 |
| GET | `/api/finance/search` | 搜索股票/基金 |
| GET | `/api/finance/history` | 获取历史数据 |

## 生产部署

### 部署架构

```
                        ┌─────────────┐
                        │  Cloudflare  │
                        │     DNS      │
                        └──────┬───────┘
                               │
                        ┌──────▼───────┐
                        │    Nginx     │
                        │   :80/:443   │
                        └──────┬───────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
 ┌───────▼───────┐    ┌───────▼───────┐    ┌────────▼────────┐
 │   Frontend    │    │    Backend    │    │   AI Service    │
 │   (Vue SPA)   │    │   (Go API)    │    │   (FastAPI)     │
 │    :9081      │    │    :9080      │    │    :8000        │
 └───────────────┘    └───────┬───────┘    └─────────────────┘
                              │
                      ┌───────▼───────┐
                      │  PostgreSQL   │
                      │    :5432      │
                      │  (Flyway)     │
                      └───────────────┘
```

### 自动部署（GitHub Actions）

推送到 `develop` 分支自动触发部署流程：
1. 构建 backend、frontend、ai-service Docker 镜像
2. 推送镜像到 ghcr.io/santashen/
3. SSH 到服务器拉取最新镜像并重启服务

首次部署需要在 GitHub 仓库配置以下 Secrets：

| Secret 名称 | 说明 | 示例 |
|------------|------|------|
| `SERVER_HOST` | 服务器 IP 或域名 | `1.2.3.4` |
| `SERVER_USER` | SSH 用户名 | `root` |
| `SERVER_SSH_KEY` | SSH 私钥 | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `SERVER_PORT` | SSH 端口（可选） | `22` |

### 手动部署

```bash
# 1. 克隆或更新代码
cd /data/web-dockers/Windsong-v2
git fetch origin
git reset --hard origin/develop

# 2. 配置环境变量
cp .env.prod.example .env
# 编辑 .env 填写实际值

# 3. 登录 GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u <username> --password-stdin

# 4. 启动服务
docker-compose -f docker-compose.prod.yml up -d
```

## 开发计划

### API 规范化
- [ ] 统一响应格式 `{ code, message, data }`，统一错误码体系
- [ ] `swaggo/swag` 自动生成 OpenAPI 文档，Swagger UI 挂载到 `/swagger/`
- [ ] 请求参数校验：`go-playground/validator` + binding tags
- [ ] API 版本化：`/api/v1/`

### 测试体系
- [ ] 后端单元测试：`testing` + `testify`，覆盖 services 层核心逻辑
- [ ] 后端接口测试：`httptest` + Gin 测试模式，覆盖 handlers 层
- [ ] 测试数据库：`testcontainers-go` 启动临时 PostgreSQL
- [ ] 前端组件测试：Vitest + `@vue/test-utils`
- [ ] 前端 E2E 测试：Playwright 覆盖核心用户流程
- [ ] CI 集成：GitHub Actions 加入测试步骤，PR 必须测试通过
- [ ] 代码覆盖率报告

### 结构化日志
- [ ] 后端引入 `zerolog` 或 `zap`，JSON 格式输出
- [ ] 请求日志中间件：记录 request_id、method、path、status、latency
- [ ] 请求链路追踪：中间件注入 request_id 贯穿整个请求生命周期
- [ ] 分级日志：debug / info / warn / error
- [ ] AI Service (Python) 引入 `structlog` 保持日志格式一致

## License

MIT
