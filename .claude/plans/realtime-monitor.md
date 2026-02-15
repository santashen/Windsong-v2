# Real-time Monitoring Simulation Feature

## Context

Services 页面目前有一个 "Coming Soon" 占位卡片。需要将其替换为一个新的 "Real-time Monitor" 功能卡片，点击后进入监控模拟页面。该页面支持 DSL 式配置：用户先配置多个图表组件（标题、轴名、范围、时间窗口），然后启动后生成 mock 数据进行实时可视化。

## Implementation Plan

### Step 1: Install ECharts

```bash
cd frontend && npm install echarts
```

### Step 2: Create Pinia Store — `frontend/src/stores/monitor.js`

- Setup store 风格（同 `stores/gold.js` 的模式）
- State: `chartConfigs` (配置数组), `isRunning` (运行状态)
- Actions: `addConfig`, `removeConfig`, `updateConfig`, `startMonitoring`, `stopMonitoring`
- 每个 config 对象: `{ id, title, xAxisName, yAxisName, yMin, yMax, timeWindow }`

### Step 3: Create Chart Config Form — `frontend/src/components/monitor/ChartConfigForm.vue`

- Props: `config` 对象
- Emits: `remove`
- 表单字段: 标题、X轴名、Y轴名、Y轴最小/最大值、时间窗口(秒)
- 两列 grid 布局，移动端单列
- 样式复用现有 CSS 变量

### Step 4: Create ECharts Wrapper — `frontend/src/components/monitor/RealtimeChart.vue`

- Props: `config` 对象
- `onMounted` 初始化 ECharts 实例，设置图表选项（标题、轴名、范围）
- `setInterval` (100ms / 10Hz) 生成 mock 数据：正弦波 + 随机噪声
- 数据滑动窗口：只保留 `timeWindow` 秒内的数据点
- `animation: false` 提升高频更新性能
- `onBeforeUnmount` 清理 timer + `dispose()` ECharts 实例
- `ResizeObserver` 处理容器尺寸变化

### Step 5: Create Monitor Page — `frontend/src/views/Monitor.vue`

- 页面结构同 GoldAnalysis.vue: Header + main + Footer
- 面包屑: Services / Monitor
- **配置阶段** (`v-if="!store.isRunning"`):
  - `v-for` 渲染 ChartConfigForm 列表
  - "Add Chart" 按钮 + "Start Monitoring" 按钮
- **运行阶段** (`v-else`):
  - Live 指示器（绿色脉冲圆点）+ Stop 按钮
  - `grid: repeat(auto-fill, minmax(400px, 1fr))` 布局渲染 RealtimeChart 列表

### Step 6: Add Route — modify `frontend/src/router/index.js`

- Import `Monitor` from `@/views/Monitor.vue`
- 添加路由 `{ path: '/monitor', name: 'Monitor', component: Monitor }`

### Step 7: Update Services Page — modify `frontend/src/views/Services.vue`

- 将第 30-39 行的 "Coming Soon" div 替换为 `<router-link to="/monitor">` 卡片
- 图标: 📡, 标题: "Real-time Monitor", tag: "📈 Simulation"
- 删除 `.coming-soon` 相关 CSS

## Files Summary

| Action | File |
|--------|------|
| New | `frontend/src/stores/monitor.js` |
| New | `frontend/src/components/monitor/ChartConfigForm.vue` |
| New | `frontend/src/components/monitor/RealtimeChart.vue` |
| New | `frontend/src/views/Monitor.vue` |
| Modify | `frontend/src/router/index.js` |
| Modify | `frontend/src/views/Services.vue` |
| Modify | `frontend/package.json` (npm install echarts) |

## Verification

1. `cd frontend && npm run dev` 启动开发服务器
2. 访问 `/services`，确认 Monitor 卡片显示且可点击
3. 进入 `/monitor`，添加 2-3 个图表配置，修改参数
4. 点击 Start，确认所有图表实时更新、时间窗口滑动正确
5. 点击 Stop，确认回到配置界面、timer 已清理
6. 调整浏览器窗口，确认图表响应式 resize
