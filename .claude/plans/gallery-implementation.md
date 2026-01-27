# Gallery Page Implementation Plan (相册页面实现方案)

## Overview
开发一个 Frutiger Aero 风格的相册页面，以卡片墙形式展示照片，支持过滤、分页和全屏查看功能。数据通过后端 API 获取。

---

## 1. File Structure (文件结构)

### Frontend
```
frontend/src/
├── views/
│   └── Gallery.vue                    # 主页面组件
├── components/
│   └── gallery/
│       ├── GalleryCard.vue            # 照片卡片组件
│       ├── GalleryFilter.vue          # 过滤控件
│       ├── GalleryPagination.vue      # 分页组件
│       └── GalleryLightbox.vue        # 全屏查看组件
├── stores/
│   └── gallery.js                     # Pinia 状态管理
├── api/
│   └── index.js                       # 添加 gallery API 调用
└── style/
    └── main.css                       # 添加 Aero 样式变量
```

### Backend (Go 项目规范结构)
```
backend/
├── main.go                            # 入口：初始化 + 启动服务器
├── config/
│   └── config.go                      # 配置管理（环境变量加载）
├── database/
│   └── database.go                    # 数据库连接和迁移
├── models/
│   └── photo.go                       # Photo 数据模型
├── handlers/
│   └── photo.go                       # Photo API 处理器
├── services/
│   └── photo.go                       # Photo 业务逻辑
├── routes/
│   └── routes.go                      # 路由注册
└── data/
    └── photos.json                    # 照片配置数据 (初始化导入)
```

---

## 2. Backend Architecture (后端架构设计)

### 2.1 Layer Responsibilities (各层职责)

| Layer | File | Responsibility |
|-------|------|----------------|
| Config | `config/config.go` | 加载环境变量，提供配置结构体 |
| Database | `database/database.go` | 数据库连接、迁移、提供 DB 实例 |
| Models | `models/photo.go` | Photo 数据模型定义 |
| Services | `services/photo.go` | 业务逻辑：过滤、分页计算、数据导入 |
| Handlers | `handlers/photo.go` | HTTP 请求处理、参数解析、响应 |
| Routes | `routes/routes.go` | 路由注册，中间件配置 |

### 2.2 Database Model (数据库模型)

**File: `models/photo.go`**

```go
type Photo struct {
    ID          uint      `gorm:"primaryKey" json:"id"`
    URL         string    `gorm:"not null" json:"url"`
    Thumbnail   string    `json:"thumbnail"`
    Title       string    `gorm:"not null" json:"title"`
    Description string    `json:"description"`
    Date        time.Time `gorm:"index" json:"date"`
    Location    string    `gorm:"index" json:"location"`
    City        string    `json:"city"`
    Country     string    `json:"country"`
    Tags        string    `json:"tags"`  // JSON array stored as string, e.g. ["nature","travel"]
    AspectRatio string    `json:"aspectRatio"`
    CreatedAt   time.Time `json:"createdAt"`
    UpdatedAt   time.Time `json:"updatedAt"`
}
```

### 2.3 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/photos` | 获取照片列表 (支持分页和过滤) |
| GET | `/api/photos/filters` | 获取可用过滤选项 (年份/地点/标签) |

### 2.4 Query Parameters for `/api/photos`

```
?page=1           # 页码，默认 1
&pageSize=20      # 每页数量，默认 20
&year=2024        # 按年份过滤
&location=Beijing # 按地点过滤
&tags=nature,travel # 按标签过滤 (逗号分隔)
```

### 2.5 Response Format

```json
{
  "photos": [...],
  "pagination": {
    "page": 1,
    "pageSize": 20,
    "total": 100,
    "totalPages": 5
  }
}
```

---

## 3. Data Schema (照片数据格式)

**File: `backend/data/photos.json`** (初始数据，可导入数据库)

```json
{
  "photos": [
    {
      "url": "https://image-host.com/photo.jpg",
      "thumbnail": "https://image-host.com/photo_thumb.jpg",
      "title": "Sunset at West Lake",
      "description": "A beautiful sunset captured at Hangzhou.",
      "date": "2023-10-15",
      "location": "Hangzhou, China",
      "city": "Hangzhou",
      "country": "China",
      "tags": ["nature", "sunset", "travel"],
      "aspectRatio": "landscape"
    }
  ]
}
```

---

## 4. Frontend Component Design (前端组件设计)

### 4.1 Gallery.vue - 主页面
- 引入 Header/Footer (参考 About.vue 模式)
- Frutiger Aero 背景 (云朵、气泡动画元素)
- 组合 Filter + Grid + Pagination + Lightbox 子组件
- 调用 API 获取数据

### 4.2 GalleryCard.vue - 照片卡片
- 毛玻璃效果卡片
- 显示: 图片、标题、日期、地点、标签
- 悬停动画 (上浮 + 光泽扫过)
- 图片懒加载
- 点击触发 Lightbox

### 4.3 GalleryFilter.vue - 过滤栏
- 年份下拉选择器
- 地点下拉选择器
- 标签多选 (Chip 样式)
- 清除过滤按钮

### 4.4 GalleryPagination.vue - 分页
- 上一页/下一页按钮
- 页码显示
- 每页20张

### 4.5 GalleryLightbox.vue - 全屏查看
- 全屏遮罩背景
- 居中显示大图
- 左右切换按钮
- 键盘导航 (左右箭头、ESC关闭)
- 显示照片信息 (标题、描述、日期、地点)
- 点击遮罩关闭

---

## 5. Frutiger Aero Style (样式要点)

### 5.1 新增 CSS 变量 (main.css)
```css
:root {
  --aero-glass-bg: rgba(255, 255, 255, 0.25);
  --aero-glass-border: rgba(255, 255, 255, 0.35);
  --aero-glass-shadow: 0 8px 32px rgba(31, 38, 135, 0.15);
  --aero-gradient-sky: linear-gradient(180deg, #87CEEB 0%, #E0F7FF 50%, #fff 100%);
  --aero-highlight: linear-gradient(180deg, rgba(255,255,255,0.8) 0%, rgba(255,255,255,0) 50%);
}
```

### 5.2 玻璃态卡片
```css
.aero-card {
  background: var(--aero-glass-bg);
  backdrop-filter: blur(10px);
  border: 1px solid var(--aero-glass-border);
  border-radius: 16px;
  box-shadow: var(--aero-glass-shadow), inset 0 1px 0 rgba(255,255,255,0.5);
}
```

### 5.3 背景元素
- 天空渐变背景
- 漂浮云朵动画
- 气泡/水滴装饰

---

## 6. State Management (Pinia Store)

**File: `frontend/src/stores/gallery.js`**

**State:**
- `photos` - 当前页照片
- `filters` - { year, location, tags[] }
- `pagination` - { page, pageSize, total, totalPages }
- `filterOptions` - { years[], locations[], tags[] }
- `selectedPhoto` - Lightbox 当前照片
- `isLoading` - 加载状态

**Actions:**
- `fetchPhotos()` - 调用 API 获取照片
- `fetchFilterOptions()` - 获取过滤选项
- `setFilter(type, value)` - 设置过滤条件
- `clearFilters()` - 清除过滤
- `setPage(page)` - 切换页码
- `openLightbox(photo)` / `closeLightbox()`
- `nextPhoto()` / `prevPhoto()` - Lightbox 导航

---

## 7. Implementation Steps (实现步骤)

### Phase 1: Backend Refactoring & API
- [ ] 创建 `config/config.go` - 提取配置管理逻辑
- [ ] 创建 `database/database.go` - 提取数据库连接逻辑
- [ ] 创建 `models/photo.go` - Photo 模型定义
- [ ] 创建 `services/photo.go` - 业务逻辑（过滤、分页、导入）
- [ ] 创建 `handlers/photo.go` - API 处理器
- [ ] 创建 `routes/routes.go` - 路由注册
- [ ] 重构 `main.go` - 简化为入口文件
- [ ] 创建 `data/photos.json` - 示例数据
- [ ] 实现数据导入功能

### Phase 2: Frontend Foundation
- [ ] 在 `router/index.js` 添加 `/gallery` 路由
- [ ] 在 `Header.vue` 添加导航链接
- [ ] 在 `api/index.js` 添加 gallery API 调用
- [ ] 创建 `gallery.js` Pinia store
- [ ] 在 `main.css` 添加 Aero CSS 变量

### Phase 3: Core Components
- [ ] 创建 `Gallery.vue` 页面框架
- [ ] 创建 `GalleryCard.vue` 卡片组件
- [ ] 实现 Frutiger Aero 背景和卡片样式

### Phase 4: Interactivity
- [ ] 创建 `GalleryFilter.vue` 过滤组件
- [ ] 创建 `GalleryPagination.vue` 分页组件
- [ ] 创建 `GalleryLightbox.vue` 全屏查看组件
- [ ] 连接组件与 Pinia store

### Phase 5: Polish
- [ ] 添加图片懒加载 (native `loading="lazy"`)
- [ ] 添加悬停动画效果
- [ ] 添加加载骨架屏
- [ ] Lightbox 键盘导航
- [ ] 响应式测试和调整

---

## 8. Critical Files to Modify/Create

### Backend (New Files)
| File | Description |
|------|-------------|
| `backend/config/config.go` | 配置管理 |
| `backend/database/database.go` | 数据库连接 |
| `backend/models/photo.go` | Photo 模型 |
| `backend/services/photo.go` | 业务逻辑 |
| `backend/handlers/photo.go` | API 处理器 |
| `backend/routes/routes.go` | 路由注册 |
| `backend/data/photos.json` | 示例数据 |

### Backend (Modify)
| File | Action |
|------|--------|
| `backend/main.go` | 重构为简洁入口，调用各模块 |

### Frontend (Modify)
| File | Action |
|------|--------|
| `frontend/src/router/index.js` | 添加 Gallery 路由 |
| `frontend/src/components/layout/Header.vue` | 添加导航链接 |
| `frontend/src/api/index.js` | 添加 gallery API 方法 |
| `frontend/src/style/main.css` | 添加 Aero CSS 变量 |

### Frontend (New Files)
| File | Description |
|------|-------------|
| `frontend/src/views/Gallery.vue` | 主页面组件 |
| `frontend/src/components/gallery/GalleryCard.vue` | 照片卡片 |
| `frontend/src/components/gallery/GalleryFilter.vue` | 过滤控件 |
| `frontend/src/components/gallery/GalleryPagination.vue` | 分页 |
| `frontend/src/components/gallery/GalleryLightbox.vue` | 全屏查看 |
| `frontend/src/stores/gallery.js` | Pinia store |

---

## 9. Verification (验证方式)

### Backend
1. 启动数据库: `docker-compose up -d`
2. 启动后端: `cd backend && go run main.go`
3. 测试 API:
   - `curl http://localhost:8080/api/photos`
   - `curl http://localhost:8080/api/photos?year=2024&page=1`
   - `curl http://localhost:8080/api/photos/filters`

### Frontend
1. 启动前端: `cd frontend && npm run dev`
2. 访问: http://localhost:5173/gallery
3. 功能验证:
   - 照片卡片正确显示
   - 过滤功能工作正常 (年份/地点/标签)
   - 分页功能工作正常
   - 点击卡片打开 Lightbox
   - Lightbox 左右切换、键盘导航、ESC关闭
   - 响应式布局在不同屏幕尺寸下正常
4. 构建测试: `npm run build` 无错误
