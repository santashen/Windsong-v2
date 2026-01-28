# Markdown 博客系统实现计划

## 概述

添加一个 Markdown 博客系统，从外部 Git 仓库增量同步文章到 PostgreSQL，并提供 REST API 用于读取文章。

## 需要修改/创建的文件

| 文件 | 操作 | 用途 |
|------|------|------|
| `backend/config/config.go` | **修改** | 添加 `PostsRepoURL`, `PostsDir` 配置字段 |
| `backend/.env.example` | **修改** | 记录新的环境变量 |
| `backend/models/post.go` | **新建** | Post 模型、PostListItem、响应类型 |
| `backend/database/database.go` | **修改** | 添加 `Post` 到 AutoMigrate |
| `backend/services/post.go` | **新建** | PostService: 同步逻辑、git 操作、frontmatter 解析、CRUD |
| `backend/handlers/post.go` | **新建** | PostHandler: 3 个 API 端点的 HTTP 处理器 |
| `backend/routes/routes.go` | **修改** | 注册 post 路由 + webhook |
| `backend/go.mod` / `go.sum` | **修改** | 添加 `github.com/adrg/frontmatter`, `github.com/lib/pq` |

---

## 开发阶段

### 阶段 1: 配置和模型 (基础设施)
- 修改 `config/config.go` 添加新配置
- 修改 `.env.example` 记录环境变量
- 创建 `models/post.go` 定义数据模型
- 修改 `database/database.go` 添加自动迁移
- **测试点**: 启动后端，确认 `posts` 表自动创建

### 阶段 2: PostService 核心逻辑
- 创建 `services/post.go`
- 实现 Git 同步 (`gitSync`)
- 实现 Markdown 解析 (`parseMarkdownFile`)
- 实现增量同步 (`SyncPosts`)
- 实现查询方法 (`GetPosts`, `GetPostBySlug`)
- **测试点**: 需要你创建一个测试用的 posts Git 仓库

### 阶段 3: API 端点
- 创建 `handlers/post.go`
- 修改 `routes/routes.go` 注册路由
- **测试点**: 测试所有 API 端点

---

## 数据库模型

```go
type Post struct {
    ID          uint           `gorm:"primaryKey" json:"id"`
    Slug        string         `gorm:"uniqueIndex;not null" json:"slug"`
    Title       string         `gorm:"not null" json:"title"`
    Date        time.Time      `gorm:"index" json:"date"`
    Tags        pq.StringArray `gorm:"type:text[]" json:"tags"`
    Content     string         `gorm:"type:text" json:"content"`
    ContentHash string         `gorm:"size:64" json:"-"`
    IsPublished bool           `gorm:"default:true;index" json:"isPublished"`
    CreatedAt   time.Time      `json:"createdAt"`
    UpdatedAt   time.Time      `json:"updatedAt"`
}
```

---

## API 端点

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/webhooks/sync` | 触发同步 | 需要 ADMIN_API_KEY |
| GET | `/api/posts` | 文章列表(分页，不含content) | 公开 |
| GET | `/api/posts/:slug` | 文章详情(含content) | 公开 |

---

## Front Matter 格式

```yaml
---
title: "文章标题"
slug: "post-slug"
date: 2024-01-15
tags:
  - go
  - backend
published: true
---

Markdown 正文内容...
```

- 如果省略 `slug`，将从文件名推导 (如 `my-post.md` -> `my-post`)
- 如果省略 `published`，默认为 `true`

---

## 增量同步逻辑

```
对于每个 .md 文件:
    解析 front matter + 内容
    计算 SHA256(文件内容)
    根据 slug 查询数据库
    如果不存在         -> INSERT (created++)
    如果存在但 hash 不同 -> UPDATE (updated++)
    如果存在且 hash 相同 -> SKIP (skipped++)
    将 slug 加入 seenSlugs 集合

循环结束后:
    DELETE FROM posts WHERE slug NOT IN (seenSlugs) -> deleted++
```

---

## 验证步骤

1. **编译**: `cd backend && go build ./...`
2. **数据库**: 启动 PostgreSQL，运行后端，确认 `posts` 表自动创建
3. **同步测试**: 创建测试 Git 仓库，配置 `POSTS_REPO_URL`，调用同步 API
4. **列表 API**: `GET /api/posts` -> 验证分页响应，无 content 字段
5. **详情 API**: `GET /api/posts/:slug` -> 验证完整文章含 content
6. **增量更新**: 修改仓库中的文章，重新同步 -> 验证只有改动的文章被更新
7. **删除**: 从仓库删除 `.md` 文件，重新同步 -> 验证文章从数据库删除
