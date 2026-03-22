<template>
  <div class="portfolio-page">
    <Header />

    <main class="portfolio-main">
      <div class="portfolio-container">
        <div class="portfolio-topbar">
          <div class="brand-copy">
            <p class="eyebrow">Family Portfolio</p>
            <h1 class="page-title">家庭投资组合</h1>
            <p class="page-subtitle">基于企业经营质量、股东现金流与估值纪律的长期资产快照。</p>
          </div>
          <div class="page-links">
            <router-link to="/services">Services</router-link>
            <span>/</span>
            <span>Portfolio</span>
          </div>
        </div>

        <section v-if="!isAuthorized" class="auth-card">
          <div class="auth-panel">
            <div class="auth-content">
              <p class="section-kicker">Access</p>
              <h2>查看最新一期家庭资产快照</h2>
              <p class="auth-description">
                页面只展示最新一期数据，不显示短期涨跌、不展示分时走势，也不放大市场情绪。
              </p>
              <ul class="auth-points">
                <li>关注企业质量与股东回报</li>
                <li>以分红现金流理解资产生产力</li>
                <li>以估值区间辅助决策，不追逐噪音</li>
              </ul>
            </div>

            <form class="auth-form" @submit.prevent="handleUnlock">
              <label class="field-label" for="portfolio-password">访问密码</label>
              <input
                id="portfolio-password"
                v-model="password"
                class="password-input"
                type="password"
                autocomplete="current-password"
                placeholder="请输入访问密码"
              />
              <button class="primary-btn" type="submit" :disabled="isVerifying">
                {{ isVerifying ? '验证中...' : '进入查看' }}
              </button>
              <p v-if="authError" class="form-error">{{ authError }}</p>
            </form>
          </div>
        </section>

        <template v-else>
          <section class="hero-card">
            <div class="hero-main">
              <div class="hero-head">
                <div>
                  <p class="section-kicker">Latest Snapshot</p>
                  <h2>我们持有的是企业，而不是价格曲线</h2>
                </div>
                <div class="hero-date-block">
                  <span class="hero-date-label">最后更新</span>
                  <strong>{{ formatDate(snapshot.recordDate) }}</strong>
                </div>
              </div>

              <p class="hero-message">{{ snapshot.managerComment || '本期未填写主理人留言。' }}</p>
            </div>

            <div class="hero-actions">
              <button class="secondary-btn" @click="lockPage">重新上锁</button>
            </div>
          </section>

          <section class="overview-section">
            <div class="section-header">
              <div>
                <p class="section-kicker">Overview</p>
                <h2>资产概览</h2>
              </div>
            </div>

            <div class="overview-grid">
              <article class="metric-card metric-card--primary">
                <p class="metric-label">投入本金</p>
                <p class="metric-value">{{ formatCurrency(snapshot.totalPrincipal) }}</p>
              </article>
              <article class="metric-card">
                <p class="metric-label">当前总市值</p>
                <p class="metric-value">{{ formatCurrency(snapshot.totalMarketValue) }}</p>
              </article>
              <article class="metric-card">
                <p class="metric-label">预期年度总股息</p>
                <p class="metric-value">{{ formatCurrency(snapshot.expectedAnnualDividends) }}</p>
              </article>
              <article class="metric-card">
                <p class="metric-label">整体持仓股息率</p>
                <p class="metric-value">{{ formatPercent(snapshot.portfolioDividendYieldPct) }}</p>
              </article>
              <article class="metric-card">
                <p class="metric-label">当前市值股息率</p>
                <p class="metric-value">{{ formatPercent(snapshot.marketValueDividendYieldPct) }}</p>
              </article>
            </div>
          </section>

          <section class="detail-section">
            <div class="section-header">
              <div>
                <p class="section-kicker">Section A</p>
                <h2>宽基 / 行业 ETF</h2>
              </div>
            </div>

            <div class="etf-stack">
              <article
                v-for="item in snapshot.holdings.etfs"
                :key="`etf-${item.name}`"
                class="etf-card"
              >
                <div class="etf-identity">
                  <p class="mini-label">标的与配置</p>
                  <div class="etf-name-block">
                    <h3>{{ item.name }}</h3>
                    <p>用更稳定的份额积累，换取长期可预期的现金流。</p>
                  </div>
                </div>

                <div class="etf-core">
                  <p class="mini-label">我们的所有权</p>
                  <dl class="ownership-grid etf-ownership-grid">
                    <div class="ownership-card">
                      <dt>持有份数</dt>
                      <dd>{{ formatShares(item.shares) }}</dd>
                    </div>
                    <div class="ownership-card ownership-card--accent">
                      <dt>预期年分红</dt>
                      <dd>{{ formatCurrency(etfExpectedAnnualDividend(item)) }}</dd>
                      <p class="ownership-footnote">
                        基于过去12个月每份派息 {{ formatCurrency(etfDividendPerShare(item)) }} 计算
                      </p>
                    </div>
                  </dl>
                </div>

                <div class="etf-compare">
                  <p class="mini-label">成本与回报</p>
                  <dl class="company-metrics">
                    <div>
                      <dt>平均买入成本</dt>
                      <dd>{{ formatCurrency(item.averageCost) }}</dd>
                    </div>
                    <div>
                      <dt>持仓股息率</dt>
                      <dd>{{ formatPercent(etfYieldOnCost(item)) }}</dd>
                    </div>
                    <div>
                      <dt>现价</dt>
                      <dd>{{ formatCurrency(item.currentReferencePrice) }}</dd>
                    </div>
                    <div>
                      <dt>目前股息率</dt>
                      <dd>{{ formatPercent(etfCurrentYield(item)) }}</dd>
                    </div>
                  </dl>
                </div>
              </article>

              <article v-if="!snapshot.holdings.etfs.length" class="company-card empty-card">
                <p>本期未配置 ETF 持仓。</p>
              </article>
            </div>
          </section>

          <section class="detail-section">
            <div class="section-header">
              <div>
                <p class="section-kicker">Section B</p>
                <h2>优秀企业</h2>
              </div>
            </div>

            <div class="company-grid">
              <article
                v-for="company in snapshot.holdings.companies"
                :key="`company-${company.name}`"
                class="company-card"
              >
                <div class="company-topline">
                  <div>
                    <h3>{{ company.name }}</h3>
                    <p class="company-subtitle">以经营质量、分红能力与所有权数量理解长期回报</p>
                  </div>
                  <span class="valuation-chip" :class="company.valuationStatus">
                    {{ valuationText(company.valuationStatus) }}
                  </span>
                </div>

                <div class="card-section">
                  <p class="mini-label">企业能力</p>
                  <dl class="company-metrics company-metrics--three">
                    <div>
                      <dt>EPS</dt>
                      <dd>{{ formatCurrency(company.eps) }}</dd>
                    </div>
                    <div>
                      <dt>派息率</dt>
                      <dd>{{ formatPercent(company.payoutRatio) }}</dd>
                    </div>
                    <div>
                      <dt>每股分红</dt>
                      <dd>{{ formatCurrency(company.dps) }}</dd>
                    </div>
                  </dl>
                </div>

                <div class="card-divider"></div>

                <div class="card-section ownership-section">
                  <p class="mini-label">我们的所有权</p>
                  <dl class="ownership-grid ownership-grid--expanded">
                    <div class="ownership-card">
                      <dt>持有股数</dt>
                      <dd>{{ formatShares(company.shares) }}</dd>
                    </div>
                    <div class="ownership-card ownership-card--accent">
                      <dt>预期年分红</dt>
                      <dd>{{ formatCurrency(company.expectedAnnualDividend) }}</dd>
                    </div>
                    <div class="ownership-card">
                      <dt>持仓总金额</dt>
                      <dd>{{ formatCurrency(companyHoldingAmount(company)) }}</dd>
                    </div>
                    <div class="ownership-card">
                      <dt>持仓占比</dt>
                      <dd>{{ formatPercent(companyHoldingWeight(company)) }}</dd>
                    </div>
                  </dl>
                </div>

                <div class="card-divider"></div>

                <div class="card-section">
                  <p class="mini-label">质量与成本</p>
                  <dl class="company-metrics">
                    <div>
                      <dt>平均持仓成本</dt>
                      <dd>{{ formatCurrency(company.averageCost) }}</dd>
                    </div>
                    <div>
                      <dt>当前股价</dt>
                      <dd>{{ formatCurrency(company.currentPrice) }}</dd>
                    </div>
                    <div>
                      <dt>持仓股息率</dt>
                      <dd>{{ formatPercent(company.holdingDividendYieldPct) }}</dd>
                    </div>
                    <div>
                      <dt>当前股息率</dt>
                      <dd>{{ formatPercent(company.currentDividendYieldPct) }}</dd>
                    </div>
                  </dl>
                </div>
              </article>

              <article v-if="!snapshot.holdings.companies.length" class="company-card empty-card">
                <p>本期未配置企业持仓。</p>
              </article>
            </div>
          </section>
        </template>

        <section v-if="loadError" class="error-card">
          <p>{{ loadError }}</p>
        </section>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import { portfolioApi, portfolioStorage } from '@/api/portfolio'

const password = ref('')
const isAuthorized = ref(false)
const isVerifying = ref(false)
const authError = ref('')
const loadError = ref('')

const snapshot = reactive({
  recordDate: '',
  totalPrincipal: 0,
  totalMarketValue: 0,
  expectedAnnualDividends: 0,
  portfolioDividendYieldPct: 0,
  marketValueDividendYieldPct: 0,
  managerComment: '',
  holdings: {
    etfs: [],
    companies: []
  }
})

async function handleUnlock() {
  if (!password.value.trim()) {
    authError.value = '请输入访问密码。'
    return
  }

  isVerifying.value = true
  authError.value = ''
  loadError.value = ''

  try {
    await portfolioApi.verifyAccess(password.value)
    portfolioStorage.setPassword(password.value)
    isAuthorized.value = true
    await fetchLatestSnapshot()
  } catch (error) {
    authError.value = error.message || '密码验证失败。'
    portfolioStorage.clearPassword()
    isAuthorized.value = false
  } finally {
    isVerifying.value = false
  }
}

async function fetchLatestSnapshot() {
  try {
    const response = await portfolioApi.getLatestSnapshot()
    const data = response.data
    Object.assign(snapshot, {
      ...data,
      holdings: {
        etfs: data.holdings?.etfs || [],
        companies: data.holdings?.companies || []
      }
    })
  } catch (error) {
    loadError.value = error.message || '读取最新投资快照失败。'
    if (error.code === 40100) {
      portfolioStorage.clearPassword()
      isAuthorized.value = false
    }
  }
}

function lockPage() {
  portfolioStorage.clearPassword()
  isAuthorized.value = false
  password.value = ''
}

function formatCurrency(value) {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY',
    maximumFractionDigits: 2
  }).format(Number(value || 0))
}

function formatPercent(value) {
  return `${Number(value || 0).toFixed(2)}%`
}

function formatShares(value) {
  return new Intl.NumberFormat('zh-CN', {
    maximumFractionDigits: 0
  }).format(Number(value || 0))
}

function companyHoldingAmount(company) {
  return Number(company.shares || 0) * Number(company.averageCost || 0)
}

function companyHoldingWeight(company) {
  const totalPrincipal = Number(snapshot.totalPrincipal || 0)
  if (!totalPrincipal) return 0
  return (companyHoldingAmount(company) / totalPrincipal) * 100
}

function etfDividendPerShare(item) {
  return Number(item.dividendPerShare || 0)
}

function etfExpectedAnnualDividend(item) {
  if (item.expectedAnnualDividend !== undefined && item.expectedAnnualDividend !== null) {
    return Number(item.expectedAnnualDividend || 0)
  }
  return Number(item.shares || 0) * etfDividendPerShare(item)
}

function etfYieldOnCost(item) {
  if (item.yieldOnCost !== undefined && item.yieldOnCost !== null) {
    return Number(item.yieldOnCost || 0)
  }
  const averageCost = Number(item.averageCost || 0)
  if (!averageCost) return 0
  return (etfDividendPerShare(item) / averageCost) * 100
}

function etfCurrentYield(item) {
  const currentPrice = Number(item.currentReferencePrice || 0)
  if (!currentPrice) return 0
  return (etfDividendPerShare(item) / currentPrice) * 100
}

function formatDate(value) {
  if (!value) return '--'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }).format(date)
}

function valuationText(status) {
  const map = {
    undervalued: '低估',
    fair: '合理',
    overvalued: '高估'
  }
  return map[status] || status
}

onMounted(async () => {
  const storedPassword = portfolioStorage.getPassword()
  if (!storedPassword) return

  password.value = storedPassword
  isAuthorized.value = true
  await fetchLatestSnapshot()
})
</script>

<style scoped>
.portfolio-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background:
    linear-gradient(180deg, #f7f9fc 0%, #ffffff 240px, #ffffff 100%);
}

.portfolio-main {
  flex: 1;
  padding: 2.25rem 1rem 4rem;
}

.portfolio-container {
  max-width: 1080px;
  margin: 0 auto;
}

.portfolio-topbar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.75rem;
}

.eyebrow,
.section-kicker {
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #4f76b7;
  margin-bottom: 0.55rem;
}

.page-title {
  font-size: 2.7rem;
  line-height: 1.05;
  color: #0f172a;
  margin: 0 0 0.5rem;
}

.page-subtitle {
  color: #64748b;
  font-size: 1rem;
  margin: 0;
  max-width: 40rem;
}

.page-links {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  color: #64748b;
  font-size: 0.92rem;
  white-space: nowrap;
}

.page-links a {
  color: #2563eb;
}

.auth-card,
.hero-card,
.error-card,
.company-card,
.etf-card,
.metric-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  box-shadow: 0 10px 32px rgba(15, 23, 42, 0.05);
}

.auth-card,
.hero-card,
.detail-section,
.overview-section,
.error-card {
  margin-bottom: 1.5rem;
}

.auth-panel {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
}

.auth-content {
  padding: 2rem;
  border-right: 1px solid #e2e8f0;
  background:
    linear-gradient(135deg, rgba(37, 99, 235, 0.06), rgba(59, 130, 246, 0.02));
}

.auth-content h2 {
  font-size: 1.8rem;
  color: #0f172a;
  margin: 0 0 0.85rem;
}

.auth-description {
  color: #64748b;
  line-height: 1.7;
  margin-bottom: 1rem;
}

.auth-points {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.7rem;
}

.auth-points li {
  color: #1e293b;
  font-size: 0.95rem;
  padding-left: 1rem;
  position: relative;
}

.auth-points li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0.48rem;
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: #3b82f6;
}

.auth-form {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.field-label {
  display: block;
  margin-bottom: 0.55rem;
  color: #475569;
  font-size: 0.92rem;
  font-weight: 600;
}

.password-input {
  width: 100%;
  margin-bottom: 0.9rem;
  padding: 0.92rem 1rem;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
  background: #fff;
  color: #0f172a;
  font-size: 0.96rem;
}

.password-input:focus {
  outline: none;
  border-color: #60a5fa;
  box-shadow: 0 0 0 4px rgba(96, 165, 250, 0.14);
}

.primary-btn,
.secondary-btn {
  border-radius: 12px;
  font-size: 0.94rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.primary-btn {
  border: none;
  padding: 0.92rem 1.1rem;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  color: #fff;
}

.primary-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 10px 20px rgba(37, 99, 235, 0.2);
}

.primary-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.secondary-btn {
  border: 1px solid #dbe3ee;
  background: #f8fafc;
  color: #1e293b;
  padding: 0.8rem 1rem;
}

.secondary-btn:hover {
  background: #f1f5f9;
}

.form-error,
.error-card {
  color: #dc2626;
}

.form-error {
  margin-top: 0.85rem;
}

.hero-card {
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: stretch;
}

.hero-main {
  flex: 1;
}

.hero-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1rem;
}

.hero-head h2 {
  font-size: 1.7rem;
  color: #0f172a;
  line-height: 1.15;
  margin: 0;
  max-width: 34rem;
}

.hero-date-block {
  min-width: 140px;
  padding: 0.9rem 1rem;
  border-radius: 14px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
}

.hero-date-label {
  display: block;
  font-size: 0.78rem;
  color: #64748b;
  margin-bottom: 0.25rem;
}

.hero-date-block strong {
  color: #0f172a;
  font-size: 0.95rem;
}

.hero-message {
  margin: 0;
  color: #475569;
  line-height: 1.8;
  white-space: pre-wrap;
}

.hero-actions {
  display: flex;
  align-items: flex-start;
}

.section-header {
  margin-bottom: 1rem;
}

.section-header h2 {
  font-size: 1.35rem;
  color: #0f172a;
  margin: 0;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 1rem;
}

.metric-card {
  padding: 1.2rem;
}

.metric-card--primary {
  background: linear-gradient(180deg, #f8fbff 0%, #eef5ff 100%);
  border-color: #cfe0fb;
}

.metric-label {
  color: #64748b;
  font-size: 0.88rem;
  margin-bottom: 0.65rem;
}

.metric-value {
  color: #0f172a;
  font-size: 1.28rem;
  line-height: 1.2;
  font-weight: 700;
  margin: 0;
}

.etf-stack {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.etf-card {
  display: grid;
  grid-template-columns: minmax(0, 0.95fr) minmax(0, 1.3fr) minmax(0, 1fr);
  gap: 1.25rem;
  padding: 1.3rem;
}

.etf-identity,
.etf-core,
.etf-compare {
  min-width: 0;
}

.etf-name-block h3 {
  margin: 0 0 0.3rem;
  color: #0f172a;
  font-size: 1.12rem;
}

.etf-name-block p {
  margin: 0;
  color: #64748b;
  font-size: 0.86rem;
  line-height: 1.55;
}

.etf-ownership-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.company-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.company-card {
  padding: 1.3rem;
}

.company-topline {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1rem;
}

.company-topline h3 {
  margin: 0 0 0.3rem;
  color: #0f172a;
  font-size: 1.12rem;
}

.company-subtitle {
  margin: 0;
  color: #64748b;
  font-size: 0.86rem;
  line-height: 1.5;
}

.card-section {
  padding: 0.15rem 0;
}

.mini-label {
  margin: 0 0 0.75rem;
  color: #64748b;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.card-divider {
  height: 1px;
  background: #e2e8f0;
  margin: 1rem 0;
}

.valuation-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 4.25rem;
  padding: 0.35rem 0.7rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 700;
  border: 1px solid transparent;
}

.valuation-chip.undervalued {
  color: #15803d;
  background: #f0fdf4;
  border-color: #bbf7d0;
}

.valuation-chip.fair {
  color: #334155;
  background: #f8fafc;
  border-color: #dbe3ee;
}

.valuation-chip.overvalued {
  color: #c2410c;
  background: #fff7ed;
  border-color: #fdba74;
}

.company-metrics {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.85rem 1rem;
}

.company-metrics--three {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.ownership-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.9rem;
}

.ownership-grid--expanded {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.ownership-card {
  padding: 1rem;
  border-radius: 14px;
  border: 1px solid #dbe3ee;
  background: #f8fafc;
}

.ownership-card--accent {
  background: linear-gradient(180deg, #f8fbff 0%, #eef5ff 100%);
  border-color: #cfe0fb;
}

.ownership-card dt {
  color: #64748b;
  font-size: 0.82rem;
  margin-bottom: 0.3rem;
}

.ownership-card dd {
  color: #0f172a;
  font-size: 1.28rem;
  font-weight: 800;
  line-height: 1.2;
}

.ownership-footnote {
  margin: 0.55rem 0 0;
  color: #64748b;
  font-size: 0.78rem;
  line-height: 1.5;
}

.company-metrics dt {
  color: #64748b;
  font-size: 0.82rem;
  margin-bottom: 0.25rem;
}

.company-metrics dd {
  color: #0f172a;
  font-size: 0.98rem;
  font-weight: 700;
}

.empty-card {
  text-align: center;
  color: #64748b;
}

.error-card {
  padding: 1rem 1.2rem;
  background: #fff7f7;
  border-color: #fecaca;
  box-shadow: none;
}

@media (max-width: 1080px) {
  .overview-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .etf-card {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 860px) {
  .auth-panel,
  .company-grid,
  .overview-grid {
    grid-template-columns: 1fr;
  }

  .auth-content {
    border-right: none;
    border-bottom: 1px solid #e2e8f0;
  }

  .hero-card,
  .hero-head,
  .portfolio-topbar {
    flex-direction: column;
  }

  .hero-date-block {
    width: 100%;
  }

  .hero-actions {
    width: 100%;
  }
}

@media (max-width: 640px) {
  .portfolio-main {
    padding: 1.5rem 0.85rem 3rem;
  }

  .page-title {
    font-size: 2.15rem;
  }

  .hero-card,
  .auth-content,
  .auth-form,
  .company-card,
  .etf-card {
    padding: 1rem;
  }

  .company-metrics {
    grid-template-columns: 1fr;
  }

  .company-metrics--three,
  .etf-ownership-grid,
  .ownership-grid {
    grid-template-columns: 1fr;
  }

  .secondary-btn {
    width: 100%;
  }
}
</style>
