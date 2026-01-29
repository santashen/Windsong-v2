# 黄金分析服务实现计划

## 概述

开发一个与大模型相关的 Python 后台服务，第一个功能是黄金分析服务。系统架构：
- **Python 服务**：无状态服务，仅提供 LLM 调用接口，不存储数据
- **Go 后端**：提供 API，优先返回数据库缓存，无缓存时调用 Python 服务并存储结果
- **Vue 前端**：展示今日黄金分析结果

## LLM API 配置

- **API 基础 URL**：`https://api.vveai.com`（可通过环境变量配置）
- **认证方式**：Bearer Token（`Authorization: Bearer {API_KEY}`）
- **API 格式**：兼容 OpenAI `/v1/chat/completions`
- **推荐模型**：`gpt-4o-search-preview`（支持联网搜索获取实时金价数据）

## 新增文件结构

```
Windsong-v2/
├── ai-service/                    # 新增: Python AI 服务（无状态）
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                    # FastAPI 入口
│   ├── config.py                  # 配置管理
│   ├── prompts/
│   │   └── gold.md                # 黄金分析 prompt (从根目录复制)
│   └── services/
│       ├── __init__.py
│       ├── base_llm.py            # LLM 基类（方便后期扩展）
│       └── gold_analysis.py       # 黄金分析服务
│
├── backend/
│   ├── models/gold_analysis.go    # 新增: GORM 模型
│   ├── services/gold_analysis.go  # 新增: 业务逻辑（含调用 Python 服务）
│   ├── handlers/gold_analysis.go  # 新增: HTTP 处理程序
│   ├── routes/routes.go           # 修改: 添加路由
│   ├── config/config.go           # 修改: 添加 AI_SERVICE_URL
│   └── database/database.go       # 修改: 添加迁移
│
├── frontend/src/
│   ├── api/index.js               # 修改: 添加 goldApi
│   ├── stores/gold.js             # 新增: Pinia store
│   ├── router/index.js            # 修改: 添加路由
│   ├── views/GoldAnalysis.vue     # 新增: 页面组件
│   └── components/layout/Header.vue # 修改: 添加导航
│
├── docker-compose.prod.yml        # 修改: 添加 ai-service
└── .github/workflows/deploy.yml   # 修改: 添加构建
```

## 数据库模型

**表名**: `gold_analyses`

| 字段 | 类型 | 说明 |
|-----|------|------|
| id | uint | 主键 |
| analysis_date | timestamp | 分析日期 (唯一索引) |
| content | text | Markdown 分析内容 |
| model_used | varchar(50) | 使用的模型 |
| prompt_hash | varchar(64) | Prompt hash |
| created_at | timestamp | 创建时间 |
| updated_at | timestamp | 更新时间 |

## API 设计

### Python AI Service (端口 8000，无状态)

| 端点 | 方法 | 说明 |
|-----|------|------|
| `/health` | GET | 健康检查 |
| `/api/gold/analyze` | GET | 调用 LLM 生成黄金分析（实时） |

### Go Backend (端口 8080)

| 端点 | 方法 | 说明 |
|-----|------|------|
| `/api/gold/today` | GET | 获取今日分析（优先缓存，无缓存则调用 Python） |

## 核心流程

```
用户访问 /gold 页面
       ↓
Vue 调用 GET /api/gold/today
       ↓
Go 检查数据库：今天是否有分析？
       ↓
  ┌────┴────┐
  有         没有
  ↓           ↓
返回缓存    调用 Python /api/gold/analyze
              ↓
          Python 调用 LLM API
              ↓
          返回分析结果给 Go
              ↓
          Go 存储到数据库
              ↓
          返回给前端
```

## 实现步骤

### Phase 1: Python AI Service

1. 创建 `ai-service/` 目录结构
2. 实现 `config.py` - 环境变量配置（LLM_API_URL, LLM_API_KEY, LLM_MODEL）
3. 实现 `services/base_llm.py` - LLM 抽象基类（方便后期扩展其他 AI 服务）
4. 实现 `services/gold_analysis.py` - 黄金分析服务
5. 实现 `main.py` - FastAPI 入口，提供 `/api/gold/analyze` 端点
6. 复制 `gold.md` 到 `prompts/` 目录
7. 创建 `Dockerfile` 和 `requirements.txt`

### Phase 2: Go Backend

1. 创建 `models/gold_analysis.go` - GORM 模型
2. 修改 `database/database.go` - 添加 AutoMigrate
3. 修改 `config/config.go` - 添加 AI_SERVICE_URL 配置
4. 创建 `services/gold_analysis.go` - 业务逻辑（缓存检查 + 调用 Python）
5. 创建 `handlers/gold_analysis.go` - HTTP 处理程序
6. 修改 `routes/routes.go` - 注册 `/api/gold/today` 路由

### Phase 3: Vue Frontend

1. 修改 `api/index.js` - 添加 goldApi.getTodayAnalysis()
2. 创建 `stores/gold.js` - Pinia store（Setup Store 风格）
3. 创建 `views/GoldAnalysis.vue` - 页面组件（像素风格，金色主题）
4. 修改 `router/index.js` - 添加 `/gold` 路由
5. 修改 `components/layout/Header.vue` - 添加导航链接

### Phase 4: Docker & CI/CD

1. 修改 `docker-compose.prod.yml` - 添加 ai-service 服务
2. 修改 `.github/workflows/deploy.yml` - 添加 ai-service 镜像构建和部署

## 环境变量

### Python AI Service
```
LLM_API_URL=https://api.vveai.com        # LLM API 基础 URL
LLM_API_KEY=sk-xxx                        # LLM API Key
LLM_MODEL=gpt-4o-search-preview           # 使用的模型（需支持联网搜索）
```

### Go Backend
```
AI_SERVICE_URL=http://ai-service:8000     # Python 服务地址（Docker 内部）
```

## 验证方案

1. **本地测试 Python 服务**:
   ```bash
   cd ai-service
   pip install -r requirements.txt
   LLM_API_URL=https://api.vveai.com LLM_API_KEY=xxx python main.py
   curl http://localhost:8000/api/gold/analyze
   ```

2. **本地测试 Go 后端**:
   ```bash
   cd backend
   AI_SERVICE_URL=http://localhost:8000 go run main.go
   curl http://localhost:8080/api/gold/today
   ```

3. **前端测试**:
   ```bash
   cd frontend
   npm run dev
   # 访问 http://localhost:5173/gold
   ```

## 关键文件路径

| 文件 | 用途 |
|-----|------|
| `backend/routes/routes.go` | 路由注册参考 |
| `backend/services/post.go` | Go 服务层实现参考 |
| `frontend/src/stores/blog.js` | Pinia Setup Store 参考 |
| `frontend/src/views/BlogList.vue` | 像素风格页面参考 |
| `docker-compose.prod.yml` | Docker 配置参考 |
