# Windsong Blog

一个基于 Go + Vue 3 + PostgreSQL 的个人博客系统，支持 Docker 容器化部署和 GitHub Actions 自动化 CI/CD。

## 项目结构

```
Windsong-v2/
├── backend/              # Go 后端
│   ├── main.go           # 入口文件
│   ├── Dockerfile        # 后端镜像构建
│   ├── go.mod            # Go 模块依赖
│   └── .env.example      # 环境变量示例
├── frontend/             # Vue 3 前端
│   ├── src/
│   │   ├── api/          # API 封装
│   │   ├── router/       # 路由配置
│   │   ├── views/        # 页面组件
│   │   ├── components/   # 公共组件
│   │   └── style/        # 样式文件
│   ├── Dockerfile        # 前端镜像构建
│   ├── nginx.conf        # 前端 Nginx 配置
│   └── package.json
├── nginx/                # 主 Nginx 配置
│   ├── nginx.conf        # 主配置
│   └── conf.d/           # 站点配置
├── scripts/              # 部署脚本
│   └── deploy.sh         # 手动部署脚本
├── .github/workflows/    # GitHub Actions
│   └── deploy.yml        # CI/CD 工作流
├── docker-compose.yml    # 开发环境
├── docker-compose.prod.yml # 生产环境
└── .env.prod.example     # 生产环境变量
```

## 技术栈

### 后端

- Go 1.23
- Gin - Web 框架
- GORM - ORM 库
- PostgreSQL - 数据库

### 前端
- Vue 3
- Vite - 构建工具
- Vue Router - 路由
- Pinia - 状态管理
- Axios - HTTP 客户端

## 快速开始

### 1. 启动数据库

```bash
docker-compose up -d
```

### 2. 启动后端

```bash
cd backend

# 复制环境变量文件
cp .env.example .env

# 下载依赖
go mod download

# 运行
go run main.go
```

后端将运行在 http://localhost:8080

### 3. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将运行在 http://localhost:5173

## 生产部署

### 部署架构

```
                        ┌─────────────┐
                        │   Cloudflare
                        │     DNS     │
                        └──────┬──────┘
                               │
                        ┌──────▼──────┐
                        │   Nginx     │
                        │   :80/:443  │
                        └──────┬──────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
    ┌───────▼───────┐  ┌───────▼───────┐  ┌──────▼─────┐
    │   Frontend    │  │    Backend    │  │ PostgreSQL │
    │   (Vue SPA)   │  │   (Go API)    │  │             │
    │   :80         │  │   :8080       │  │   :5432     │
    └───────────────┘  └───────────────┘  └────────────┘
```

### 自动部署（GitHub Actions）

首次部署需要在 GitHub 仓库配置以下 Secrets：

| Secret 名称 | 说明 | 示例 |
|------------|------|------|
| `SERVER_HOST` | 服务器 IP 或域名 | `1.2.3.4` |
| `SERVER_USER` | SSH 用户名 | `root` |
| `SERVER_SSH_KEY` | SSH 私钥 | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `SERVER_PORT` | SSH 端口（可选） | `22` |

**配置步骤：**

1. 在服务器上生成 SSH 密钥对（如果没有）：
```bash
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions
```

2. 将公钥添加到服务器 authorized_keys：
```bash
cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys
```

3. 将私钥内容添加到 GitHub Secrets（`SERVER_SSH_KEY`）

4. 推送代码到 `develop` 分支，自动触发部署

### 手动部署

如果需要在服务器上手动部署：

```bash
# 1. 克隆或更新代码
cd /data/www/v2.windsong.top
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

- [ ] 用户认证系统
- [ ] 文章管理（增删改查）
- [ ] 评论系统
- [ ] 标签和分类
- [ ] 相册功能
- [ ] 搜索功能

## License

MIT
