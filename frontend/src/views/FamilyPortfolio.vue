<template>
  <div class="portfolio-page">
    <Header />

    <main class="portfolio-shell">
      <div class="portfolio-main">



        <section v-if="error" class="empty-shell">
          <h2>数据读取失败</h2>
          <p>{{ error }}</p>
        </section>

        <section v-else-if="loading" class="empty-shell">
          <h2>正在整理组合报告</h2>
          <p>正在从 AI service 读取持仓、论点和历史净值。</p>
        </section>

        <template v-else-if="portfolioDetail">
          <section class="summary-strip">
            <article class="summary-panel">
              <div>
                <p class="summary-label">总资产净值</p>
                <div class="summary-row">
                  <strong>{{ formatCurrency(totalMarketValue) }}</strong>
                  <span :class="['summary-delta', totalReturnValue >= 0 ? 'up' : 'down']">
                    {{ totalReturnRate >= 0 ? '+' : '' }}{{ totalReturnRate.toFixed(2) }}%
                  </span>
                </div>
              </div>

              <div class="summary-split">
                <p class="summary-label">累计投入本金</p>
                <strong class="summary-muted">{{ formatCurrency(portfolioPrincipal) }}</strong>
              </div>

              <div class="summary-split">
                <p class="summary-label">盈利情况</p>
                <strong :class="['summary-profit', totalReturnValue >= 0 ? 'up' : 'down']">
                  {{ totalReturnValue >= 0 ? '+' : '' }}{{ formatCurrency(totalReturnValue) }}
                </strong>
              </div>
            </article>
          </section>

          <section class="holdings-shell">
            <div class="section-head">
              <div>
                <h2>核心组合持仓</h2>
              </div>
              <span class="section-stamp">{{ lastUpdatedLabel }}</span>
            </div>

            <div class="table-wrap">
              <table class="holdings-table">
                <thead>
                  <tr>
                    <th>资产名称</th>
                    <th class="align-right">代码</th>
                    <th class="align-right">投入金额</th>
                    <th class="align-right">当前市值</th>
                    <th class="align-right">权重 (%)</th>
                    <th class="align-right">现价</th>
                    <th class="align-right">盈亏</th>
                    <th class="align-right">收益率 (%)</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in enrichedHoldings" :key="item.holding.id" @click="openThesis(item)">
                    <td>
                      <div class="asset-cell">
                        <strong>{{ item.asset.name }}</strong>
                        <span>{{ item.asset.sector || item.asset.asset_type }}</span>
                      </div>
                    </td>
                    <td class="align-right mono">{{ item.asset.ticker_code }}</td>
                    <td class="align-right mono">{{ formatCurrency(item.investedAmount) }}</td>
                    <td class="align-right mono strong">{{ formatCurrency(item.marketValue) }}</td>
                    <td class="align-right mono">{{ formatPercent(item.weightPercentage) }}</td>
                    <td class="align-right mono">{{ formatCurrency(item.currentPrice) }}</td>
                    <td class="align-right mono" :class="item.gainValue >= 0 ? 'up' : 'down'">
                      {{ item.gainValue >= 0 ? '+' : '' }}{{ formatCurrency(item.gainValue) }}
                    </td>
                    <td class="align-right mono strong" :class="item.gainRate >= 0 ? 'up' : 'down'">
                      {{ item.gainRate >= 0 ? '+' : '' }}{{ item.gainRate.toFixed(2) }}%
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          <section class="analysis-grid">
            <article
              v-for="item in enrichedHoldings"
              :key="`thesis-${item.holding.id}`"
              class="thesis-card"
              @click="openThesis(item)"
            >
              <div class="thesis-topline">
                <span class="thesis-badge">
                  {{ item.investment_thesis?.strategy_tag || typeLabel(item.asset.asset_type) }}
                </span>
                <span class="material-symbols-outlined thesis-icon">{{ item.asset.icon_name || 'insights' }}</span>
              </div>

              <h3>{{ item.asset.name }}</h3>

              <div class="metric-stack">
                <div class="metric-row">
                  <span>预期股息率</span>
                  <strong :class="rateClass(item.investment_thesis?.expected_dividend_yield)">
                    {{ percentOrDash(item.investment_thesis?.expected_dividend_yield) }}
                  </strong>
                </div>

                <template v-if="item.investment_thesis?.margin_of_safety !== null && item.investment_thesis?.margin_of_safety !== undefined">
                  <div class="metric-row">
                    <span>安全边际</span>
                    <strong class="up">{{ percentOrDash(item.investment_thesis.margin_of_safety) }}</strong>
                  </div>
                  <div class="metric-bar">
                    <span :style="{ width: `${Math.min(Number(item.investment_thesis.margin_of_safety), 100)}%` }"></span>
                  </div>
                </template>
              </div>

              <p>
                {{ item.investment_thesis?.short_description || thesisPreview(item.investment_thesis?.markdown_details) || '点击查看完整投资逻辑与 Markdown 分析。' }}
              </p>
            </article>
          </section>

          <section class="chart-shell">
            <div class="section-head">
              <div>
                <h2>历史价值增长曲线</h2>
                <p>组合净值与沪深300指数的长期表现对照。</p>
              </div>
              <div class="legend-row">
                <span><i class="legend-dot legend-dot--primary"></i>家庭投资组合</span>
                <span><i class="legend-dot legend-dot--secondary"></i>沪深300指数</span>
              </div>
            </div>

            <div v-if="performanceHistory.length" ref="chartRef" class="chart-panel"></div>
            <div v-else class="chart-empty">尚未录入历史净值数据。</div>
          </section>
        </template>

        <section v-else class="empty-shell">
          <h2>暂无投资组合</h2>
          <p>请先在后台管理页创建一个家庭投资组合。</p>
        </section>
      </div>
    </main>

    <transition name="fade">
      <div v-if="activeThesis" class="detail-overlay" @click.self="activeThesis = null">
        <article class="detail-modal">
          <div class="detail-head">
            <div>
              <p class="detail-kicker">{{ activeThesis.asset.ticker_code }}</p>
              <h3>{{ activeThesis.asset.name }}</h3>
            </div>
            <button type="button" class="detail-close" @click="activeThesis = null">关闭</button>
          </div>

          <div class="detail-grid">
            <div class="detail-metric">
              <span>当前权重</span>
              <strong>{{ formatPercent(activeThesis.holding.weight_percentage) }}</strong>
            </div>
            <div class="detail-metric">
              <span>持仓成本</span>
              <strong>{{ formatCurrency(activeThesis.holding.average_cost) }}</strong>
            </div>
            <div class="detail-metric">
              <span>当前价格</span>
              <strong>{{ formatCurrency(activeThesis.asset.current_price) }}</strong>
            </div>
            <div class="detail-metric">
              <span>安全边际</span>
              <strong>{{ percentOrDash(activeThesis.investment_thesis?.margin_of_safety) }}</strong>
            </div>
          </div>

          <div class="markdown-body" v-html="activeThesisHtml"></div>
        </article>
      </div>
    </transition>

    <section class="report-footer-band">
      <div class="report-footer__inner">
        <p>“我认为，格雷厄姆有三个基本的思想，这足以作为你投资智慧的根本：（1）把股票视作企业所有权的一部分；（2）把市场波动当作朋友而不是敌人；（3）在买入价格上留有充足的安全边际。我认为这些思想，从现在起直至百年后，都将会被看作正确投资的基石。” —— 沃伦·巴菲特</p>
      </div>
    </section>

    <Footer />
  </div>
</template>

<script setup>
import * as echarts from 'echarts'
import { marked } from 'marked'
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

import { portfolioApi } from '@/api/familyPortfolio'
import Footer from '@/components/layout/Footer.vue'
import Header from '@/components/layout/Header.vue'

const loading = ref(true)
const error = ref('')
const portfolioOptions = ref([])
const selectedPortfolioId = ref(null)
const portfolioDetail = ref(null)
const activeThesis = ref(null)
const chartRef = ref(null)

let chartInstance = null
let resizeHandler = null

const portfolioPrincipal = computed(() => Number(portfolioDetail.value?.portfolio?.total_principal || 0))
const performanceHistory = computed(() => portfolioDetail.value?.performance_history || [])

const enrichedHoldings = computed(() =>
  (portfolioDetail.value?.holdings || []).map(item => {
    const investedAmount = Number(item.holding.invested_amount || 0)
    const shareCount = Number(item.holding.share_count || 0)
    const currentPrice = Number(item.asset.current_price || 0)
    const marketValue = shareCount * currentPrice
    const gainValue = marketValue - investedAmount
    const gainRate = investedAmount > 0 ? (gainValue / investedAmount) * 100 : 0

    return {
      ...item,
      investedAmount,
      currentPrice,
      marketValue,
      gainValue,
      gainRate,
      weightPercentage: Number(item.holding.weight_percentage || 0)
    }
  })
)

const totalMarketValue = computed(() =>
  enrichedHoldings.value.reduce((sum, item) => sum + item.marketValue, 0)
)

const totalReturnValue = computed(() => totalMarketValue.value - portfolioPrincipal.value)
const totalReturnRate = computed(() =>
  portfolioPrincipal.value > 0 ? (totalReturnValue.value / portfolioPrincipal.value) * 100 : 0
)
const lastUpdatedLabel = computed(() => {
  const values = [
    portfolioDetail.value?.portfolio?.updated_at,
    ...(portfolioDetail.value?.holdings || []).flatMap(item => [
      item.holding?.updated_at,
      item.asset?.updated_at,
      item.investment_thesis?.updated_at
    ]),
    ...(portfolioDetail.value?.performance_history || []).map(item => item.updated_at)
  ]
    .filter(Boolean)
    .map(value => new Date(value))
    .filter(value => !Number.isNaN(value.getTime()))
    .sort((a, b) => b.getTime() - a.getTime())

  if (!values.length) {
    return '暂无更新时间'
  }

  const latest = values[0]
  return `更新于 ${latest.getFullYear()}-${String(latest.getMonth() + 1).padStart(2, '0')}-${String(latest.getDate()).padStart(2, '0')}`
})

const activeThesisHtml = computed(() => {
  const source = activeThesis.value?.investment_thesis?.markdown_details
  if (!source) {
    return '<p>暂无详细投资逻辑。</p>'
  }
  return marked.parse(source)
})

function formatCurrency(value) {
  return Number(value || 0).toLocaleString('zh-CN', {
    style: 'currency',
    currency: 'CNY',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

function formatPercent(value) {
  return `${Number(value || 0).toFixed(2)}%`
}

function percentOrDash(value) {
  if (value === null || value === undefined || value === '') {
    return '--'
  }
  return `${Number(value).toFixed(2)}%`
}

function thesisPreview(markdown) {
  if (!markdown) {
    return ''
  }
  return markdown.replace(/[#>*`-]/g, '').replace(/\s+/g, ' ').trim().slice(0, 88)
}

function typeLabel(assetType) {
  const map = {
    stock: '个股策略',
    etf: 'ETF策略',
    fund: '基金策略',
    bond: '债券策略',
    cash: '现金头寸',
    other: '资产配置'
  }
  return map[assetType] || '资产配置'
}

function rateClass(value) {
  return Number(value || 0) >= 0 ? 'up' : 'down'
}

function openThesis(item) {
  activeThesis.value = item
}

async function fetchPortfolios() {
  const response = await portfolioApi.listPortfolios()
  portfolioOptions.value = [...(response.data?.items || [])].sort((a, b) => b.id - a.id)
  if (!portfolioOptions.value.length) {
    portfolioDetail.value = null
    return
  }
  if (!selectedPortfolioId.value) {
    selectedPortfolioId.value = portfolioOptions.value[0].id
  }
  await fetchPortfolioDetail(selectedPortfolioId.value)
}

async function fetchPortfolioDetail(portfolioId) {
  if (!portfolioId) {
    portfolioDetail.value = null
    return
  }
  const response = await portfolioApi.getPortfolioDetail(portfolioId)
  portfolioDetail.value = response.data
  await nextTick()
  renderChart()
}

function renderChart() {
  if (!chartRef.value || !performanceHistory.value.length) {
    chartInstance?.clear()
    return
  }

  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }

  chartInstance.setOption(
    {
      animationDuration: 700,
      grid: { left: 48, right: 20, top: 24, bottom: 34 },
      tooltip: {
        trigger: 'axis',
        valueFormatter: value => Number(value).toFixed(4)
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: performanceHistory.value.map(item => item.record_date),
        axisLine: { lineStyle: { color: '#cbd5e1' } },
        axisLabel: { color: '#64748b' }
      },
      yAxis: {
        type: 'value',
        scale: true,
        axisLabel: { color: '#64748b' },
        splitLine: { lineStyle: { color: '#e2e8f0' } }
      },
      series: [
        {
          name: '组合净值',
          type: 'line',
          smooth: true,
          showSymbol: false,
          lineStyle: { width: 3, color: '#0f172a' },
          data: performanceHistory.value.map(item => Number(item.portfolio_nav))
        },
        {
          name: '比较基准',
          type: 'line',
          smooth: true,
          showSymbol: false,
          lineStyle: { width: 2, type: 'dashed', color: '#94a3b8' },
          data: performanceHistory.value.map(item => Number(item.benchmark_nav || 0))
        }
      ]
    },
    true
  )
}

async function loadPage() {
  loading.value = true
  error.value = ''
  try {
    await fetchPortfolios()
  } catch (requestError) {
    error.value = requestError?.response?.data?.detail || requestError?.message || '请求失败'
  } finally {
    loading.value = false
  }
}

watch(selectedPortfolioId, async value => {
  if (!value) {
    return
  }
  try {
    await fetchPortfolioDetail(value)
  } catch (requestError) {
    error.value = requestError?.response?.data?.detail || requestError?.message || '请求失败'
  }
})

onMounted(() => {
  loadPage()
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
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

.portfolio-page {
  min-height: 100vh;
  background: #f7f9fb;
  color: #191c1e;
  font-family: 'Inter', sans-serif;
}

.portfolio-shell {
  min-height: calc(100vh - 140px);
}

.portfolio-main,
.report-footer__inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.portfolio-main {
  padding-top: 1.75rem;
  padding-bottom: 3rem;
}

.report-masthead {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding: 1rem 1.25rem;
  border: 1px solid #e2e8f0;
  background: #ffffff;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
  border-radius: 8px;
}

.report-masthead__brand {
  font-family: 'Manrope', sans-serif;
  font-size: 1.25rem;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.02em;
}

.manage-link,
.detail-close {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 40px;
  padding: 0 1rem;
  border-radius: 8px;
  border: 1px solid #0f172a;
  background: #0f172a;
  color: #ffffff;
  font-size: 0.875rem;
  font-weight: 700;
  text-decoration: none;
}

.page-intro {
  margin-bottom: 2rem;
}

.page-kicker,
.summary-label,
.section-stamp,
.thesis-badge,
.detail-kicker {
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #64748b;
}

.page-intro h1 {
  margin: 0.25rem 0 0.55rem;
  font-family: 'Manrope', sans-serif;
  font-size: clamp(2.2rem, 4vw, 3rem);
  line-height: 1.08;
  color: #0f172a;
}

.page-intro p:last-child {
  max-width: 42ch;
  color: #475569;
}

.summary-panel,
.holdings-shell,
.thesis-card,
.chart-shell,
.detail-modal,
.report-footer-band {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
}

.summary-strip {
  margin-bottom: 1.5rem;
}

.summary-panel {
  display: flex;
  gap: 3rem;
  max-width: 920px;
  padding: 1.5rem;
  border-radius: 8px;
}

.summary-row {
  display: flex;
  align-items: baseline;
  gap: 0.65rem;
  margin-top: 0.5rem;
}

.summary-row strong,
.summary-muted,
.summary-profit {
  font-family: 'Manrope', sans-serif;
  font-size: clamp(1.35rem, 2vw, 1.8rem);
  line-height: 1.05;
  word-break: break-word;
}

.summary-muted {
  color: #94a3b8;
}

.summary-split {
  padding-left: 2.5rem;
  border-left: 1px solid #f1f5f9;
}

.summary-delta.up,
.up {
  color: #dc2626;
}

.summary-delta.down,
.down {
  color: #16a34a;
}

.holdings-shell,
.chart-shell {
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  border-radius: 8px;
}

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.2rem;
}

.section-head h2 {
  font-family: 'Manrope', sans-serif;
  font-size: 1.125rem;
  color: #0f172a;
}

.section-head p {
  margin-top: 0.25rem;
  color: #64748b;
  font-size: 0.875rem;
}

.section-stamp {
  padding: 0.35rem 0.7rem;
  border-radius: 999px;
  background: #f1f5f9;
}

.table-wrap {
  overflow-x: auto;
}

.holdings-table {
  width: 100%;
  border-collapse: collapse;
}

.holdings-table th,
.holdings-table td {
  padding: 1.1rem 0.95rem;
  border-bottom: 1px solid #f1f5f9;
}

.holdings-table th {
  background: rgba(248, 250, 252, 0.7);
  font-size: 0.75rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.holdings-table tbody tr {
  cursor: pointer;
  transition: background 0.18s ease;
}

.holdings-table tbody tr:hover {
  background: rgba(248, 250, 252, 0.7);
}

.asset-cell {
  display: flex;
  flex-direction: column;
  gap: 0.18rem;
}

.asset-cell strong,
.strong {
  color: #0f172a;
  font-weight: 700;
}

.holdings-table td.up,
.holdings-table td.strong.up {
  color: #dc2626;
}

.holdings-table td.down,
.holdings-table td.strong.down {
  color: #16a34a;
}

.asset-cell span {
  font-size: 0.75rem;
  color: #94a3b8;
}

.align-right {
  text-align: right;
}

.mono {
  font-variant-numeric: tabular-nums;
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.thesis-card {
  padding: 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.thesis-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
}

.thesis-topline,
.metric-row,
.legend-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.thesis-badge {
  padding: 0.3rem 0.5rem;
  border-radius: 4px;
  background: #dbeafe;
  color: #1e3a8a;
}

.thesis-icon {
  color: #94a3b8;
  font-size: 1.3rem;
  line-height: 1;
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}

.thesis-card h3 {
  margin: 1rem 0 1.1rem;
  font-family: 'Manrope', sans-serif;
  font-size: 1.125rem;
  color: #0f172a;
}

.metric-stack {
  display: grid;
  gap: 0.85rem;
  margin-bottom: 1rem;
}

.metric-row span,
.thesis-card p,
.legend-row span,
.chart-empty,
.empty-shell p {
  color: #475569;
}

.metric-bar {
  height: 6px;
  border-radius: 999px;
  overflow: hidden;
  background: #e2e8f0;
}

.metric-bar span {
  display: block;
  height: 100%;
  background: #0f172a;
}

.chart-panel {
  height: 320px;
}

.legend-row {
  gap: 1rem;
  flex-wrap: wrap;
}

.legend-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 999px;
  margin-right: 0.4rem;
}

.legend-dot--primary {
  background: #0f172a;
}

.legend-dot--secondary {
  background: #94a3b8;
}

.chart-empty,
.empty-shell {
  display: grid;
  place-items: center;
  min-height: 240px;
  text-align: center;
  padding: 2rem;
}

.empty-shell h2 {
  margin-bottom: 0.5rem;
  font-family: 'Manrope', sans-serif;
}

.detail-overlay {
  position: fixed;
  inset: 0;
  z-index: 20;
  background: rgba(15, 23, 42, 0.42);
  display: grid;
  place-items: center;
  padding: 1.5rem;
}

.detail-modal {
  width: min(920px, 100%);
  max-height: calc(100vh - 3rem);
  overflow: auto;
  padding: 1.5rem;
  border-radius: 8px;
}

.detail-head {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
  margin-bottom: 1.25rem;
}

.detail-head h3 {
  margin-top: 0.25rem;
  font-family: 'Manrope', sans-serif;
  font-size: 2rem;
  color: #0f172a;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.8rem;
  margin-bottom: 1.4rem;
}

.detail-metric {
  padding: 0.95rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
}

.detail-metric span {
  display: block;
  font-size: 0.78rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.detail-metric strong {
  display: block;
  margin-top: 0.4rem;
  color: #0f172a;
  font-size: 1.1rem;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3) {
  margin: 1.2rem 0 0.6rem;
  font-family: 'Manrope', sans-serif;
  color: #0f172a;
}

.markdown-body :deep(p),
.markdown-body :deep(li) {
  color: #334155;
  line-height: 1.75;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  padding-left: 1.2rem;
}

.report-footer-band {
  margin: 0 auto 1.5rem;
  max-width: 1200px;
  border-radius: 8px;
}

.report-footer__inner {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  color: #64748b;
  font-size: 0.9rem;
  padding-top: 1.4rem;
  padding-bottom: 1.4rem;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 980px) {
  .analysis-grid,
  .detail-grid,
  .summary-panel,
  .report-footer__inner {
    grid-template-columns: 1fr;
    flex-direction: column;
    align-items: flex-start;
  }

  .summary-split {
    padding-left: 0;
    border-left: 0;
    border-top: 1px solid #f1f5f9;
    padding-top: 1.25rem;
  }
}

@media (max-width: 720px) {
  .portfolio-main,
  .report-footer__inner {
    padding-left: 1rem;
    padding-right: 1rem;
  }

  .report-masthead {
    padding: 1rem;
  }

  .page-intro h1 {
    font-size: 1.8rem;
  }

  .section-head,
  .detail-head {
    flex-direction: column;
  }
}
</style>
