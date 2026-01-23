# Windsong Blog

一个基于 Go + Vue 3 + PostgreSQL 的个人博客系统。

## 项目结构

```
Windsong-v2/
├── backend/          # Go 后端
│   ├── main.go       # 入口文件
│   ├── go.mod        # Go 模块依赖
│   └── .env.example  # 环境变量示例
├── frontend/         # Vue 3 前端
│   ├── src/
│   │   ├── api/      # API 封装
│   │   ├── router/   # 路由配置
│   │   ├── views/    # 页面组件
│   │   ├── components/ # 公共组件
│   │   └── style/    # 样式文件
│   └── package.json
└── docker-compose.yml # PostgreSQL 数据库
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

## 开发计划

- [ ] 用户认证系统
- [ ] 文章管理（增删改查）
- [ ] 评论系统
- [ ] 标签和分类
- [ ] 相册功能
- [ ] 搜索功能

## License

MIT
