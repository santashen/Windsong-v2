# Stock/Fund Data Viewer Feature

## Context
Services.vue 目前有两个服务卡片（Gold Analysis、Real-time Monitor），需要新增第三个服务：股票/基金数据查看器。用户可以搜索股票/基金，选择时间范围和展示属性，支持多选对比，使用折线图展示。

## Architecture
- **Data source**: akshare (免费，无需注册)
- **Backend**: Python ai-service (FastAPI, port 8000)
- **Frontend → Backend**: Vite 新增 `/ai-api` 代理直连 ai-service，不经过 Go
- **Chart**: echarts (已安装) 折线图

## Implementation Plan

### 1. Backend: ai-service 新增股票数据 API
**File: `ai-service/services/finance_data.py`** (new)
- 使用 akshare 获取数据，封装为 `FinanceDataService` 类
- 支持的数据类型：
  - A股股票历史数据 (akshare `stock_zh_a_hist`)
  - 基金净值数据 (akshare `fund_open_fund_info_em`)
- 搜索接口：根据关键字搜索股票/基金名称和代码
  - 股票搜索: `stock_info_a_code_name` 获取列表后本地过滤
  - 基金搜索: `fund_name_em` 获取列表后本地过滤
- 历史数据接口：根据代码、时间范围返回数据
  - 返回字段根据类型不同：股票返回 OHLCV，基金返回净值/累计净值/日增长率

**File: `ai-service/main.py`** (modify)
- 新增路由：
  - `GET /api/finance/search?keyword=xxx` — 搜索股票/基金
  - `GET /api/finance/history?code=xxx&type=stock|fund&start=2024-01-01&end=2025-01-01&fields=close,volume` — 获取历史数据
  - 支持 `codes` 参数传多个代码（逗号分隔），方便批量查询

**File: `ai-service/requirements.txt`** (modify)
- 添加 `akshare>=1.14.0`

### 2. Frontend: Vite proxy 配置
**File: `frontend/vite.config.js`** (modify)
- 新增 `/ai-api` 代理到 `http://localhost:8000`，重写路径为 `/api`

### 3. Frontend: API 层
**File: `frontend/src/api/index.js`** (modify)
- 新增 `financeApi` 对象，使用独立的 axios 实例 (baseURL: `/ai-api`)
  - `search(keyword)` → `/ai-api/finance/search`
  - `getHistory(params)` → `/ai-api/finance/history`

### 4. Frontend: Pinia Store
**File: `frontend/src/stores/finance.js`** (new)
- Setup store 风格 (与 gold.js 一致)
- State: `searchResults`, `selectedItems[]`, `chartData`, `timeRange`, `selectedFields[]`, `isLoading`, `error`
- Actions: `searchSymbol(keyword)`, `addItem(item)`, `removeItem(code)`, `fetchHistory()`, `setTimeRange()`, `toggleField()`
- 默认时间范围: 近 1 年
- 预设时间快捷选项: 1月、3月、6月、1年、3年、全部

### 5. Frontend: 页面组件
**File: `frontend/src/views/FinanceView.vue`** (new)
- 页面布局参考 Monitor.vue（breadcrumb + header + 内容区）
- 分区：
  1. **搜索区**: 输入框 + 搜索结果下拉列表，点击添加到已选列表
  2. **已选列表**: 已选股票/基金 chips，可删除
  3. **配置区**: 时间范围选择（快捷按钮 + 自定义日期），属性选择（checkbox）
  4. **图表区**: echarts 折线图，多个标的叠加显示
- 属性选项根据类型动态变化：
  - 股票: 收盘价、开盘价、最高价、最低价、成交量、换手率
  - 基金: 单位净值、累计净值、日增长率

### 6. Frontend: 路由 & Services 卡片
**File: `frontend/src/router/index.js`** (modify)
- 新增 `/finance` 路由指向 `FinanceView`

**File: `frontend/src/views/Services.vue`** (modify)
- 在 services-grid 中新增第三张卡片，链接到 `/finance`

## Key Design Decisions
- 搜索使用防抖 (300ms)，避免频繁请求
- akshare 的股票/基金列表可在 ai-service 启动时缓存到内存，加速搜索
- 多标的数据在同一图表中使用不同颜色的折线
- 如果标的的数据量级差异大（如不同股价），使用百分比变化模式方便对比

## Verification
1. 启动 ai-service: `cd ai-service && pip install -r requirements.txt && python main.py`
2. 测试搜索: `curl http://localhost:8000/api/finance/search?keyword=贵州茅台`
3. 测试历史数据: `curl "http://localhost:8000/api/finance/history?code=600519&type=stock&start=2024-01-01&end=2025-01-01"`
4. 启动前端: `cd frontend && npm run dev`
5. 访问 `/services` 确认新卡片显示
6. 访问 `/finance`，搜索添加股票，选择时间范围和属性，确认图表正常渲染
