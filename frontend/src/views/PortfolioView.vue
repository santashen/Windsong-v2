<template>
  <div class="portfolio-page">
    <div class="portfolio-shell">
      <section v-if="!isAuthorized" class="access-panel">
        <div class="access-copy">
          <p class="eyebrow">Family Portfolio</p>
          <h1>把我们视作企业的长期共同所有者</h1>
          <p class="lead">
            这里不展示短期波动，不展示闪烁的价格情绪，只呈现最新一期的经营性资产快照。
          </p>
        </div>

        <form class="access-form" @submit.prevent="handleUnlock">
          <label class="field-label" for="portfolio-password">访问密码</label>
          <input
            id="portfolio-password"
            v-model="password"
            class="password-input"
            type="password"
            autocomplete="current-password"
            placeholder="请输入访问密码"
          />
          <button class="unlock-button" type="submit" :disabled="isVerifying">
            {{ isVerifying ? '验证中...' : '进入查看' }}
          </button>
          <p v-if="authError" class="form-error">{{ authError }}</p>
        </form>
      </section>

      <section v-else class="portfolio-content">
        <header class="hero-card">
          <div>
            <p class="eyebrow">Latest Snapshot</p>
            <h1>家庭投资组合</h1>
            <p class="hero-meta">更新日期 {{ formatDate(snapshot.recordDate) }}</p>
          </div>
          <button class="text-button" @click="lockPage">重新上锁</button>
        </header>

        <section class="message-card">
          <p class="section-kicker">主理人留言</p>
          <p class="manager-message">{{ snapshot.managerComment || '本期未填写主理人留言。' }}</p>
        </section>

        <section class="overview-grid">
          <article class="metric-card">
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
        </section>

        <section class="holdings-section">
          <div class="section-header">
            <div>
              <p class="section-kicker">区块 A</p>
              <h2>宽基 / 行业 ETF</h2>
            </div>
          </div>
          <div class="table-shell">
            <table class="holdings-table">
              <thead>
                <tr>
                  <th>标的名称</th>
                  <th>持仓占比</th>
                  <th>平均买入成本</th>
                  <th>当前参考价格</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in snapshot.holdings.etfs" :key="`etf-${item.name}`">
                  <td>{{ item.name }}</td>
                  <td>{{ formatPercent(item.weightPct) }}</td>
                  <td>{{ formatCurrency(item.averageCost) }}</td>
                  <td>{{ formatCurrency(item.currentReferencePrice) }}</td>
                </tr>
                <tr v-if="!snapshot.holdings.etfs.length">
                  <td colspan="4" class="empty-cell">本期未配置 ETF 持仓。</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section class="holdings-section">
          <div class="section-header">
            <div>
              <p class="section-kicker">区块 B</p>
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
                <h3>{{ company.name }}</h3>
                <span class="valuation-chip" :class="company.valuationStatus">
                  {{ valuationText(company.valuationStatus) }}
                </span>
              </div>
              <dl class="company-metrics">
                <div>
                  <dt>ROE</dt>
                  <dd>{{ formatPercent(company.roePct) }}</dd>
                </div>
                <div>
                  <dt>平均持仓成本</dt>
                  <dd>{{ formatCurrency(company.averageCost) }}</dd>
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
            </article>
            <article v-if="!snapshot.holdings.companies.length" class="company-card empty-card">
              <p>本期未配置企业持仓。</p>
            </article>
          </div>
        </section>
      </section>

      <section v-if="loadError" class="error-panel">
        <p>{{ loadError }}</p>
      </section>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
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
  background:
    radial-gradient(circle at top left, rgba(107, 142, 184, 0.22), transparent 28%),
    radial-gradient(circle at bottom right, rgba(163, 177, 198, 0.18), transparent 32%),
    linear-gradient(180deg, #0d1b2a 0%, #132238 42%, #e8edf2 42%, #eef3f7 100%);
  padding: 2rem 1rem 4rem;
}

.portfolio-shell {
  max-width: 1120px;
  margin: 0 auto;
}

.access-panel,
.portfolio-content,
.error-panel {
  background: rgba(248, 251, 255, 0.94);
  border: 1px solid rgba(144, 162, 184, 0.2);
  box-shadow: 0 24px 80px rgba(9, 18, 33, 0.18);
  border-radius: 28px;
  overflow: hidden;
}

.access-panel {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
}

.access-copy {
  padding: 4rem;
  background: linear-gradient(160deg, #132238 0%, #18314f 100%);
  color: #f3f7fb;
}

.eyebrow,
.section-kicker {
  letter-spacing: 0.16em;
  text-transform: uppercase;
  font-size: 0.76rem;
  color: #7f95af;
  margin-bottom: 0.85rem;
}

.access-copy .eyebrow {
  color: #9db2ca;
}

.access-copy h1 {
  font-size: clamp(2rem, 3vw, 3.4rem);
  line-height: 1.1;
  margin-bottom: 1rem;
  font-family: Georgia, 'Times New Roman', serif;
}

.lead {
  max-width: 36rem;
  color: rgba(243, 247, 251, 0.82);
  font-size: 1rem;
}

.access-form {
  padding: 4rem 3rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 1rem;
  background: linear-gradient(180deg, #f6f9fc 0%, #eef3f7 100%);
}

.field-label {
  font-size: 0.9rem;
  color: #41546b;
  font-weight: 600;
}

.password-input,
.text-button,
.unlock-button {
  border-radius: 14px;
}

.password-input {
  width: 100%;
  border: 1px solid #c8d3de;
  background: #fff;
  padding: 0.95rem 1rem;
  font-size: 1rem;
  color: #112033;
}

.password-input:focus {
  outline: none;
  border-color: #3e5c76;
  box-shadow: 0 0 0 3px rgba(62, 92, 118, 0.12);
}

.unlock-button,
.text-button {
  border: none;
  cursor: pointer;
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.unlock-button {
  padding: 0.95rem 1.2rem;
  background: linear-gradient(135deg, #284b63 0%, #3e5c76 100%);
  color: #f8fbff;
  font-weight: 600;
}

.unlock-button:hover:not(:disabled),
.text-button:hover {
  transform: translateY(-1px);
}

.unlock-button:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.form-error,
.error-panel {
  color: #8d2636;
}

.portfolio-content {
  padding: 1.5rem;
}

.hero-card,
.message-card,
.metric-card,
.holdings-section {
  border-radius: 24px;
}

.hero-card,
.message-card,
.holdings-section {
  background: linear-gradient(180deg, #f8fbff 0%, #edf3f8 100%);
  border: 1px solid #d7e0e8;
}

.hero-card {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 2rem;
  margin-bottom: 1rem;
}

.hero-card h1,
.holdings-section h2 {
  font-family: Georgia, 'Times New Roman', serif;
}

.hero-card h1 {
  font-size: clamp(2rem, 3vw, 3rem);
  color: #10243a;
}

.hero-meta {
  color: #5c7288;
}

.text-button {
  background: rgba(16, 36, 58, 0.06);
  color: #18314f;
  padding: 0.8rem 1rem;
}

.message-card {
  padding: 1.5rem 2rem;
  margin-bottom: 1rem;
}

.manager-message {
  font-size: 1rem;
  color: #22374d;
  white-space: pre-wrap;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.metric-card {
  padding: 1.25rem;
  background: linear-gradient(180deg, #fdfefe 0%, #eef4f8 100%);
  border: 1px solid #dbe4ec;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.7);
}

.metric-label {
  color: #60758a;
  font-size: 0.9rem;
  margin-bottom: 0.7rem;
}

.metric-value {
  color: #132238;
  font-size: 1.4rem;
  font-weight: 700;
  line-height: 1.2;
}

.holdings-section {
  padding: 1.5rem;
  margin-bottom: 1rem;
}

.section-header {
  margin-bottom: 1rem;
}

.table-shell {
  overflow-x: auto;
}

.holdings-table {
  width: 100%;
  border-collapse: collapse;
}

.holdings-table th,
.holdings-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #d7e0e8;
}

.holdings-table th {
  color: #5a7187;
  font-size: 0.82rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.holdings-table td {
  color: #14263a;
}

.company-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.company-card {
  padding: 1.35rem;
  border: 1px solid #d7e0e8;
  border-radius: 18px;
  background: #fdfefe;
}

.company-topline {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.company-topline h3 {
  font-size: 1.15rem;
  color: #10243a;
}

.valuation-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 4.5rem;
  padding: 0.35rem 0.7rem;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 600;
}

.valuation-chip.undervalued {
  background: #e2f1e8;
  color: #275d41;
}

.valuation-chip.fair {
  background: #e6edf4;
  color: #37526d;
}

.valuation-chip.overvalued {
  background: #f4e7df;
  color: #7a4b2c;
}

.company-metrics {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.8rem 1rem;
}

.company-metrics dt {
  color: #70859a;
  font-size: 0.82rem;
  margin-bottom: 0.3rem;
}

.company-metrics dd {
  color: #10243a;
  font-size: 1rem;
  font-weight: 600;
}

.empty-cell,
.empty-card {
  text-align: center;
  color: #70859a;
}

.error-panel {
  margin-top: 1rem;
  padding: 1rem 1.25rem;
  background: rgba(252, 243, 244, 0.96);
}

@media (max-width: 1080px) {
  .overview-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 820px) {
  .access-panel {
    grid-template-columns: 1fr;
  }

  .access-copy,
  .access-form {
    padding: 2rem;
  }

  .company-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .portfolio-page {
    padding: 1rem 0.75rem 3rem;
  }

  .portfolio-content {
    padding: 1rem;
  }

  .hero-card {
    padding: 1.4rem;
    flex-direction: column;
  }

  .message-card,
  .holdings-section {
    padding: 1rem;
  }

  .overview-grid,
  .company-metrics {
    grid-template-columns: 1fr;
  }
}
</style>
