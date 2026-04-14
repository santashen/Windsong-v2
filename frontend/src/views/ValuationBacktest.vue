<template>
  <div class="valuation-page">
    <Header />

    <main class="valuation-main">
      <section class="hero-section">
        <div class="hero-copy">
          <p class="eyebrow">Valuation Terminal</p>
          <h1 class="page-title">老唐估值回测</h1>
          <p class="page-subtitle">
            用利润、利率与历史股本变化，观察价格和价值在时间里如何错位。
          </p>

          <div class="formula-ribbon">
            <span>三年后合理估值 = 第三年预计归母净利润 × (1 / 无风险收益率)</span>
            <span>无风险收益率最低按 2% 计</span>
          </div>
        </div>

        <div class="hero-pixels" aria-hidden="true">
          <span v-for="n in 24" :key="n"></span>
        </div>
      </section>

      <section class="workspace-shell">
        <section class="query-panel">
          <div class="panel-head">
            <p class="panel-title">Backtest Query</p>
            <p class="panel-note">只在点击按钮后发起回测。</p>
          </div>

          <form class="query-grid" @submit.prevent="loadBacktest">
            <label class="field">
              <span>股票代码</span>
              <input v-model.trim="form.symbol" type="text" inputmode="numeric" maxlength="6" placeholder="600519" />
            </label>

            <label class="field">
              <span>开始日期</span>
              <input v-model="form.startDate" type="date" />
            </label>

            <label class="field">
              <span>结束日期</span>
              <input v-model="form.endDate" type="date" />
            </label>

            <button class="submit-button" type="submit" :disabled="loading">
              {{ loading ? '回测中...' : '开始回测' }}
            </button>
          </form>
        </section>

        <section class="chart-panel">
          <div class="chart-head">
            <div>
              <p class="panel-title">Price / Value</p>
              <p class="chart-caption">黑线收盘价，蓝线内在价值，绿线买点，红线卖点。</p>
            </div>
            <p v-if="dataPoints.length" class="chart-range">
              {{ dataPoints[0]?.date }} - {{ dataPoints[dataPoints.length - 1]?.date }}
            </p>
          </div>

          <div v-if="error" class="status-card status-card--error">{{ error }}</div>
          <div v-else-if="loading" class="status-card">正在请求历史行情、财报与利率...</div>
          <div v-else-if="!hasQueried" class="status-card">输入参数后点击“开始回测”。</div>
          <div v-else-if="!dataPoints.length" class="status-card">当前条件下没有可展示的数据。</div>
          <div v-show="dataPoints.length" ref="chartRef" class="chart"></div>
        </section>

        <aside class="insight-panel">
          <div class="metric-card">
            <span class="metric-label">样本天数</span>
            <strong class="metric-value">{{ dataPoints.length || '--' }}</strong>
          </div>

          <div class="metric-card">
            <span class="metric-label">买点触发</span>
            <strong class="metric-value">{{ buySignals.length || '--' }}</strong>
          </div>

          <div class="metric-card">
            <span class="metric-label">卖点触发</span>
            <strong class="metric-value">{{ sellSignals.length || '--' }}</strong>
          </div>

          <div class="metric-card">
            <span class="metric-label">最近收盘价</span>
            <strong class="metric-value">{{ latestPoint ? formatNumber(latestPoint.price) : '--' }}</strong>
          </div>

          <div class="info-card">
            <p class="info-title">Method Notes</p>
            <ul class="info-list">
              <li>季度归母净利润先转换为 TTM，再线性插值到日频。</li>
              <li>十年期国债月度数据按日期线性插值，并设置 2% 下限。</li>
              <li>历史每股估值按股本变更记录动态换算。</li>
            </ul>
          </div>
        </aside>
      </section>
    </main>

    <Footer />
  </div>
</template>

<script setup>
import * as echarts from 'echarts'
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'

import { getValuationBacktest } from '@/api/valuation'
import Footer from '@/components/layout/Footer.vue'
import Header from '@/components/layout/Header.vue'

const today = new Date().toISOString().slice(0, 10)
const chartRef = ref(null)
const loading = ref(false)
const error = ref('')
const hasQueried = ref(false)
const dataPoints = ref([])

const form = reactive({
  symbol: '600519',
  startDate: '2010-01-01',
  endDate: today
})

let chartInstance = null
let resizeHandler = null

const latestPoint = computed(() => dataPoints.value[dataPoints.value.length - 1] || null)

const buySignals = computed(() => {
  const signals = []
  const rows = dataPoints.value
  for (let index = 1; index < rows.length; index += 1) {
    const previous = rows[index - 1]
    const current = rows[index]
    if (previous.price > previous.buy_line && current.price <= current.buy_line) {
      signals.push({ date: current.date, price: current.price, label: '买' })
    }
  }
  return signals
})

const sellSignals = computed(() => {
  const signals = []
  const rows = dataPoints.value
  for (let index = 1; index < rows.length; index += 1) {
    const previous = rows[index - 1]
    const current = rows[index]
    if (previous.price < previous.sell_line && current.price >= current.sell_line) {
      signals.push({ date: current.date, price: current.price, label: '卖' })
    }
  }
  return signals
})

function formatNumber(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return '--'
  }
  return Number(value).toLocaleString('zh-CN', {
    maximumFractionDigits: 2
  })
}

function buildMarkPoints() {
  const buyMarks = buySignals.value.map(item => ({
    name: '买点',
    coord: [item.date, item.price],
    value: item.label,
    itemStyle: { color: '#2dbd8d' },
    label: { color: '#ffffff' }
  }))

  const sellMarks = sellSignals.value.map(item => ({
    name: '卖点',
    coord: [item.date, item.price],
    value: item.label,
    itemStyle: { color: '#ff5f7a' },
    label: { color: '#ffffff' }
  }))

  return [...buyMarks, ...sellMarks]
}

function renderChart() {
  if (!chartRef.value || !dataPoints.value.length) {
    return
  }

  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }

  chartInstance.setOption({
    animationDuration: 700,
    backgroundColor: 'transparent',
    color: ['#20263f', '#6287ff', '#2dbd8d', '#ff5f7a'],
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255,255,255,0.9)',
      borderColor: 'rgba(215, 224, 255, 0.95)',
      textStyle: { color: '#334155' },
      valueFormatter: value => formatNumber(value)
    },
    legend: {
      top: 0,
      textStyle: { color: '#5f6d89' }
    },
    grid: {
      left: 58,
      right: 24,
      top: 56,
      bottom: 40
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dataPoints.value.map(item => item.date),
      axisLine: { lineStyle: { color: 'rgba(143, 157, 196, 0.4)' } },
      axisLabel: { color: '#7a86a8' }
    },
    yAxis: {
      type: 'value',
      scale: true,
      axisLine: { show: false },
      axisLabel: {
        color: '#7a86a8',
        formatter: value => formatNumber(value)
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(172, 184, 220, 0.18)'
        }
      }
    },
    dataZoom: [
      {
        type: 'inside',
        start: 70,
        end: 100
      },
      {
        type: 'slider',
        height: 26,
        bottom: 0,
        borderColor: 'rgba(214, 223, 255, 0.7)',
        fillerColor: 'rgba(136, 160, 255, 0.18)',
        backgroundColor: 'rgba(255, 255, 255, 0.5)'
      }
    ],
    series: [
      {
        name: '收盘价',
        type: 'line',
        showSymbol: false,
        lineStyle: { width: 2.2 },
        data: dataPoints.value.map(item => item.price),
        markPoint: {
          symbolSize: 34,
          data: buildMarkPoints()
        }
      },
      {
        name: '内在价值',
        type: 'line',
        showSymbol: false,
        lineStyle: { width: 2 },
        data: dataPoints.value.map(item => item.intrinsic_value)
      },
      {
        name: '理想买点',
        type: 'line',
        showSymbol: false,
        lineStyle: { width: 1.7, type: 'dashed' },
        data: dataPoints.value.map(item => item.buy_line)
      },
      {
        name: '理想卖点',
        type: 'line',
        showSymbol: false,
        lineStyle: { width: 1.7, type: 'dashed' },
        data: dataPoints.value.map(item => item.sell_line)
      }
    ]
  }, true)
}

async function loadBacktest() {
  loading.value = true
  error.value = ''
  hasQueried.value = true

  try {
    const response = await getValuationBacktest({
      symbol: form.symbol,
      start_date: form.startDate,
      end_date: form.endDate
    })
    dataPoints.value = response.data?.data || []
    await nextTick()
    if (dataPoints.value.length) {
      renderChart()
      chartInstance?.resize()
    } else {
      chartInstance?.clear()
    }
  } catch (requestError) {
    dataPoints.value = []
    chartInstance?.clear()
    error.value = requestError?.response?.data?.detail || requestError?.message || '回测请求失败'
  } finally {
    loading.value = false
  }
}

watch(dataPoints, async points => {
  if (!points.length) {
    return
  }
  await nextTick()
  renderChart()
})

onMounted(() => {
  resizeHandler = () => chartInstance?.resize()
  window.addEventListener('resize', resizeHandler)
})

onBeforeUnmount(() => {
  if (resizeHandler) {
    window.removeEventListener('resize', resizeHandler)
  }
  chartInstance?.dispose()
  chartInstance = null
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=VT323&family=Nunito:wght@400;600;700&display=swap');

.valuation-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background:
    radial-gradient(circle at 12% 14%, rgba(255, 198, 233, 0.34), transparent 24%),
    radial-gradient(circle at 88% 12%, rgba(170, 226, 255, 0.3), transparent 26%),
    radial-gradient(circle at 56% 82%, rgba(188, 179, 255, 0.2), transparent 22%),
    linear-gradient(180deg, #fbfcff 0%, #f9f7ff 48%, #f6fbff 100%);
  position: relative;
  overflow: hidden;
}

.valuation-page::before {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  opacity: 0.18;
  background-image:
    linear-gradient(rgba(130, 150, 255, 0.08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(130, 150, 255, 0.08) 1px, transparent 1px);
  background-size: 24px 24px;
  mask-image: linear-gradient(180deg, rgba(255,255,255,0.9), transparent 90%);
}

.valuation-page::after {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  opacity: 0.12;
  background:
    radial-gradient(circle at 14% 22%, #fff 0 1px, transparent 1.6px),
    radial-gradient(circle at 77% 34%, #fff 0 1px, transparent 1.6px),
    radial-gradient(circle at 48% 72%, #fff 0 1px, transparent 1.6px);
  background-size: 180px 180px;
  animation: shimmer 12s linear infinite;
}

.valuation-main {
  position: relative;
  z-index: 1;
  flex: 1;
  width: min(1260px, calc(100% - 32px));
  margin: 0 auto;
  padding: 2rem 0 4rem;
}

.hero-section {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 260px;
  gap: 1.4rem;
  align-items: end;
  margin-bottom: 1.4rem;
}

.hero-copy {
  animation: drift-in 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}

.eyebrow {
  margin: 0 0 0.6rem;
  font-family: 'VT323', monospace;
  font-size: 1.35rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #6471dc;
}

.page-title {
  margin: 0;
  font-family: 'VT323', monospace;
  font-size: clamp(2.5rem, 5vw, 4.2rem);
  line-height: 0.92;
  letter-spacing: 0.05em;
  color: #283652;
}

.page-subtitle {
  margin: 0.9rem 0 0;
  max-width: 36ch;
  color: #64748e;
  font-size: 1rem;
}

.formula-ribbon {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
  margin-top: 1.1rem;
}

.formula-ribbon span {
  display: inline-flex;
  align-items: center;
  min-height: 32px;
  padding: 0 0.8rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.62);
  border: 1px solid rgba(222, 228, 255, 0.95);
  color: #5f6f8b;
  font-size: 0.88rem;
  box-shadow: 0 8px 20px rgba(120, 136, 178, 0.08);
  backdrop-filter: blur(8px);
}

.hero-pixels {
  display: grid;
  grid-template-columns: repeat(6, 16px);
  gap: 8px;
  justify-content: end;
  align-content: start;
  padding-bottom: 0.4rem;
}

.hero-pixels span {
  width: 16px;
  height: 16px;
  border-radius: 3px;
  background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(162,191,255,0.8));
  box-shadow: 0 0 14px rgba(134, 160, 255, 0.22);
  animation: blink 4s ease-in-out infinite;
}

.hero-pixels span:nth-child(3n) {
  animation-delay: 0.45s;
}

.hero-pixels span:nth-child(4n) {
  animation-delay: 0.9s;
}

.workspace-shell {
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr) 280px;
  gap: 1rem;
  align-items: start;
}

.query-panel,
.chart-panel,
.insight-panel {
  border-radius: 22px;
  background:
    linear-gradient(180deg, rgba(255,255,255,0.84), rgba(255,255,255,0.7)),
    linear-gradient(135deg, rgba(208, 219, 255, 0.12), rgba(255, 214, 233, 0.1));
  border: 1px solid rgba(255, 255, 255, 0.94);
  box-shadow:
    0 18px 36px rgba(116, 132, 171, 0.1),
    inset 0 1px 0 rgba(255,255,255,0.88);
  backdrop-filter: blur(16px);
}

.query-panel,
.chart-panel {
  padding: 1rem;
}

.insight-panel {
  display: grid;
  gap: 0.8rem;
  padding: 0.9rem;
}

.panel-head,
.chart-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.9rem;
}

.panel-title {
  margin: 0;
  font-family: 'VT323', monospace;
  font-size: 1.35rem;
  letter-spacing: 0.06em;
  color: #5f6de0;
}

.panel-note,
.chart-caption,
.chart-range {
  margin: 0.18rem 0 0;
  color: #7a88a6;
  font-size: 0.9rem;
}

.query-grid {
  display: grid;
  gap: 0.8rem;
}

.field {
  display: grid;
  gap: 0.35rem;
}

.field span {
  font-family: 'VT323', monospace;
  font-size: 1.05rem;
  color: #7b88a7;
  letter-spacing: 0.05em;
}

.field input {
  height: 46px;
  padding: 0 0.85rem;
  border: 1px solid rgba(213, 220, 244, 0.95);
  border-radius: 14px;
  background: rgba(255,255,255,0.78);
  color: #2b3650;
  font-size: 0.95rem;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}

.field input:focus {
  outline: none;
  border-color: rgba(115, 131, 255, 0.72);
  box-shadow: 0 0 0 4px rgba(120, 136, 255, 0.12);
  transform: translateY(-1px);
}

.submit-button {
  height: 48px;
  border: none;
  border-radius: 16px;
  background: linear-gradient(135deg, #6173ff 0%, #7d56f1 100%);
  color: #fff;
  font-family: 'VT323', monospace;
  font-size: 1.35rem;
  letter-spacing: 0.06em;
  cursor: pointer;
  box-shadow: 0 14px 28px rgba(104, 103, 245, 0.22);
  transition: transform 0.2s ease, box-shadow 0.2s ease, opacity 0.2s ease;
}

.submit-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 18px 34px rgba(104, 103, 245, 0.28);
}

.submit-button:disabled {
  opacity: 0.72;
  cursor: wait;
}

.chart {
  height: 560px;
}

.status-card {
  min-height: 560px;
  display: grid;
  place-items: center;
  padding: 1.4rem;
  border-radius: 18px;
  background: rgba(252, 252, 255, 0.76);
  border: 1px dashed rgba(208, 217, 246, 0.9);
  color: #70809b;
  text-align: center;
}

.status-card--error {
  color: #c24168;
}

.metric-card,
.info-card {
  border-radius: 16px;
  padding: 0.9rem;
  background: rgba(255,255,255,0.72);
  border: 1px solid rgba(227, 232, 248, 0.95);
}

.metric-card {
  display: grid;
  gap: 0.2rem;
}

.metric-label {
  font-family: 'VT323', monospace;
  font-size: 1.05rem;
  color: #8a97b1;
}

.metric-value {
  color: #2c3752;
  font-size: 1.65rem;
  line-height: 1.05;
}

.info-title {
  margin: 0;
  font-family: 'VT323', monospace;
  font-size: 1.2rem;
  color: #6170df;
}

.info-list {
  margin: 0.65rem 0 0;
  padding-left: 1rem;
  color: #6c7b95;
  line-height: 1.6;
}

.info-list li + li {
  margin-top: 0.45rem;
}

@keyframes drift-in {
  from {
    opacity: 0;
    transform: translateY(14px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes blink {
  0%, 100% {
    opacity: 0.48;
    transform: translateY(0);
  }
  50% {
    opacity: 1;
    transform: translateY(-1px);
  }
}

@keyframes shimmer {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}

@media (max-width: 1120px) {
  .workspace-shell {
    grid-template-columns: 1fr;
  }

  .insight-panel {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .valuation-main {
    width: min(100% - 24px, 1260px);
    padding: 1.4rem 0 3rem;
  }

  .hero-section {
    grid-template-columns: 1fr;
  }

  .hero-pixels {
    justify-content: start;
    grid-template-columns: repeat(8, 14px);
  }

  .chart,
  .status-card {
    height: 430px;
    min-height: 430px;
  }

  .insight-panel {
    grid-template-columns: 1fr;
  }
}
</style>
