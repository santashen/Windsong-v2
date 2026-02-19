# Windsong 测试体系实现计划

## Context

项目当前零测试、零测试依赖。后端所有依赖都是具体类型（无接口），无法 mock，必须先做接口提取重构才能编写单元测试。前端同样没有任何测试工具链。CI 流水线中没有测试步骤，代码直接构建部署。

本计划实现 README 中列出的全部测试体系目标，使项目具备：后端单元测试 + 集成测试、前端组件测试 + E2E 测试、CI 门禁 + 覆盖率报告。

---

## Phase 1: 后端接口提取（使代码可测试）

### 1A. Handler 层接口 — 创建 `backend/handlers/interfaces.go`

定义三个接口，对应三个 service 的公开方法：

```go
type PostServiceInterface interface {
    SyncPosts() (*services.SyncResult, error)
    GetPosts(query services.PostQuery) (*models.PostListResponse, error)
    GetPostBySlug(slug string) (*models.Post, error)
}

type PhotoServiceInterface interface {
    GetPhotos(query services.PhotoQuery) (*models.PhotoResponse, error)
    GetFilterOptions() (*models.FilterOptions, error)
    GetPhotoByID(id uint) (*models.Photo, error)
    CreatePhoto(photo *models.Photo) error
    UpdatePhoto(id uint, photo *models.Photo) error
    DeletePhoto(id uint) error
}

type GoldAnalysisServiceInterface interface {
    GetTodayAnalysis() (*models.GoldAnalysis, error)
}
```

**修改 3 个 handler 文件**，将字段类型从 `*services.XxxService` 改为对应接口：
- `backend/handlers/post.go`
- `backend/handlers/photo.go`
- `backend/handlers/gold_analysis.go`

Go 结构体类型自动满足接口，`routes/routes.go` 无需改动。

### 1B. Service 内部依赖接口 — 创建 `backend/services/interfaces.go`

```go
type HTTPClient interface {
    Do(req *http.Request) (*http.Response, error)
}

type GitSyncer interface {
    Sync(repoURL, postsDir string) error
}
```

**修改 `backend/services/gold_analysis.go`**：
- 添加 `httpClient HTTPClient` 字段
- 构造函数接受可选 `HTTPClient`，nil 时用默认 `&http.Client{Timeout: 180s}`
- `fetchFromAIService()` 使用 `s.httpClient.Do(req)`

**修改 `backend/services/post.go`**：
- 添加 `gitSyncer GitSyncer` 字段
- 将现有 `gitSync()` 中的 `os/exec` 逻辑提取到 `defaultGitSyncer` 结构体
- 构造函数接受可选 `GitSyncer`，nil 时用 `&defaultGitSyncer{}`

---

## Phase 2: 后端单元测试

### 依赖
```bash
cd backend && go get github.com/stretchr/testify
```

### 2A. Handler 测试（mock service 接口）

创建 `backend/handlers/testutil_test.go` — Gin TestMode 设置 + `performRequest` 辅助函数。

每个 handler 一个测试文件，使用函数式 mock（`mockPostService` 等内嵌函数字段）：

| 测试文件 | 关键用例 |
|---------|---------|
| `handlers/auth_test.go` | 正确/错误 key、dev mode 绕过、缺失 key |
| `handlers/post_test.go` | GetPosts 成功/失败、GetPost 成功/404、SyncPosts |
| `handlers/photo_test.go` | CRUD 全流程、参数校验、过滤查询 |
| `handlers/gold_analysis_test.go` | 成功/500 |

### 2B. Middleware 测试

创建 `backend/middleware/auth_test.go`：
- dev mode 放行、X-API-Key 正确/错误、Bearer Token 正确/错误

### 2C. Service 纯函数测试

`backend/services/post_test.go`：
- `parseMarkdownFile` — 各种 frontmatter 格式、空文件、无 frontmatter

---

## Phase 3: 后端集成测试（testcontainers-go）

### 依赖
```bash
cd backend
go get github.com/testcontainers/testcontainers-go
go get github.com/testcontainers/testcontainers-go/modules/postgres
```

### 3A. 测试数据库辅助 — 创建 `backend/testutil/testdb.go`

- 启动 PostgreSQL 16 容器
- 用 `WithInitScripts` 直接执行 `db/migrations/V1__initial_schema.sql`（比单独跑 Flyway 更快）
- 返回 `*gorm.DB` + cleanup 函数

### 3B. 集成测试文件（`//go:build integration` 标签）

| 测试文件 | 关键用例 |
|---------|---------|
| `services/photo_integration_test.go` | CRUD 全流程、分页、过滤、FilterOptions、ImportFromJSON |
| `services/post_integration_test.go` | GetPosts 分页+tag过滤、GetPostBySlug、SyncPosts（mock GitSyncer + 临时 .md 文件 + 真实 DB） |
| `services/gold_analysis_integration_test.go` | 缓存命中（预插入当日记录）、缓存未命中（mock HTTP + 验证 DB 写入） |

运行方式：
- 仅单元测试：`go test ./...`
- 含集成测试：`go test -tags integration ./...`

---

## Phase 4: 前端组件测试（Vitest）

### 依赖
```bash
cd frontend && npm install -D vitest @vue/test-utils @pinia/testing happy-dom @vitest/coverage-v8
```

### 4A. 配置

**`frontend/vite.config.js`** 添加 `test` 块：
```js
test: {
  environment: 'happy-dom',
  globals: true,
  setupFiles: ['./src/test/setup.js'],
}
```

**`frontend/package.json`** 添加脚本：
```json
"test": "vitest run",
"test:watch": "vitest",
"test:coverage": "vitest run --coverage"
```

**创建 `frontend/src/test/setup.js`** — 全局 mock axios。

### 4B. Store 测试（最高优先级）

| 测试文件 | 关键用例 |
|---------|---------|
| `stores/__tests__/blog.test.js` | fetchPosts、setTagFilter/clearFilter、setPage、collectTags |
| `stores/__tests__/gallery.test.js` | fetchPhotos+过滤、lightbox 导航、activeFilterCount |
| `stores/__tests__/auth.test.js` | login/logout、initAuth（localStorage）、hasStoredKey |

### 4C. 组件测试（第二优先级）

| 测试文件 | 关键用例 |
|---------|---------|
| `components/blog/__tests__/BlogCard.test.js` | 渲染标题/日期/标签、click 事件 |
| `components/blog/__tests__/BlogPagination.test.js` | 页码渲染、页面切换事件 |
| `components/layout/__tests__/Header.test.js` | 导航链接渲染 |

---

## Phase 5: 前端 E2E 测试（Playwright）

### 依赖
```bash
cd frontend && npm install -D @playwright/test && npx playwright install
```

### 5A. 配置 — 创建 `frontend/playwright.config.js`

使用 Playwright `route` API 拦截 `/api/*` 请求进行 mock，不依赖真实后端。

### 5B. E2E 测试文件

| 测试文件 | 覆盖流程 |
|---------|---------|
| `e2e/navigation.spec.js` | 首页加载、导航切换 |
| `e2e/blog.spec.js` | 文章列表加载、点击进入详情、标签过滤、分页 |
| `e2e/gallery.spec.js` | 照片加载、过滤、灯箱 |
| `e2e/admin.spec.js` | 登录/登出、未认证重定向 |

---

## Phase 6: CI 集成

### 修改 `.github/workflows/deploy.yml`

新增两个 job（在 `build` 之前）：

**`test-backend`**：
1. Setup Go 1.23
2. `go test -v -race -coverprofile=coverage.out ./...`（单元测试）
3. `go test -v -race -tags integration -coverprofile=coverage-integration.out ./...`（集成测试）
4. `go tool cover -func=coverage.out`（打印覆盖率摘要）
5. Upload coverage artifact

**`test-frontend`**：
1. Setup Node 20
2. `npm ci`
3. `npm run test -- --coverage`（Vitest）
4. `npx playwright test`（E2E，API mock 模式）
5. Upload coverage artifact

**`build`** job 加 `needs: [test-backend, test-frontend]`，测试不通过则不构建。

### 覆盖率

- 后端：`go tool cover -func` 输出到 CI 日志
- 前端：`@vitest/coverage-v8` 生成 `frontend/coverage/`
- 两者都作为 artifact 上传

### .gitignore 补充
```
backend/coverage*.out
frontend/coverage/
```

---

## 执行顺序

```
Phase 1A + 1B （接口提取，后续所有后端测试的前提）
      │
      ├── Phase 2（后端单元测试）──┐
      │                           ├── Phase 3（后端集成测试）
      │                           │
      └── Phase 4（前端 Vitest）───┤
                                  ├── Phase 5（Playwright E2E）
                                  │
                                  └── Phase 6（CI 集成）
```

Phase 1 → Phase 2/4 可并行 → Phase 3/5 → Phase 6

---

## 验证方式

1. **后端单元测试**：`cd backend && go test -v -race ./...` 全部通过
2. **后端集成测试**：`cd backend && go test -v -race -tags integration ./...` 全部通过（需要 Docker）
3. **前端组件测试**：`cd frontend && npm test` 全部通过
4. **前端 E2E**：`cd frontend && npx playwright test` 全部通过
5. **CI**：推送到 PR 分支，验证 GitHub Actions 中 test-backend 和 test-frontend job 全部绿色，build job 在测试之后执行
6. **覆盖率**：CI 日志中可见覆盖率百分比，artifacts 中可下载详细报告
