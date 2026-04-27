<template>
  <div class="portfolio-admin">
    <section class="admin-hero">
      <div>
        <p class="hero-kicker">Family Portfolio Admin</p>
        <h1>家庭投资组合管理</h1>
        <p>维护组合、资产、持仓、投资逻辑和历史净值。写操作使用当前登录的 ADMIN API KEY。</p>
      </div>
      <button class="refresh-btn" @click="loadAll" :disabled="loading">{{ loading ? '刷新中...' : '刷新数据' }}</button>
    </section>

    <section v-if="error" class="admin-error">{{ error }}</section>

    <section class="admin-layout-grid">
      <div class="admin-column">
        <article class="admin-card">
          <div class="card-head">
            <h2>组合</h2>
            <button v-if="editingPortfolioId" class="ghost-btn" @click="resetPortfolioForm">取消编辑</button>
          </div>
          <form class="form-grid" @submit.prevent="submitPortfolio">
            <label><span>组合名称</span><input v-model.trim="portfolioForm.name" type="text" required /></label>
            <label><span>累计本金</span><input v-model="portfolioForm.total_principal" type="number" step="0.0001" min="0" required /></label>
            <label><span>币种</span><input v-model.trim="portfolioForm.currency" type="text" maxlength="10" required /></label>
            <button class="submit-btn" type="submit">{{ editingPortfolioId ? '更新组合' : '新增组合' }}</button>
          </form>
          <div class="list-shell">
            <button v-for="portfolio in portfolios" :key="portfolio.id" class="list-row" @click="editPortfolio(portfolio)">
              <div><strong>{{ portfolio.name }}</strong><span>{{ formatCurrency(portfolio.total_principal) }}</span></div>
              <span class="row-actions" @click.stop="deletePortfolio(portfolio.id)">删除</span>
            </button>
          </div>
        </article>

        <article class="admin-card">
          <div class="card-head">
            <h2>资产</h2>
            <button v-if="editingAssetId" class="ghost-btn" @click="resetAssetForm">取消编辑</button>
          </div>
          <form class="form-grid" @submit.prevent="submitAsset">
            <label><span>代码</span><input v-model.trim="assetForm.ticker_code" type="text" required /></label>
            <label><span>名称</span><input v-model.trim="assetForm.name" type="text" required /></label>
            <label><span>行业</span><input v-model.trim="assetForm.sector" type="text" /></label>
            <label>
              <span>类型</span>
              <select v-model="assetForm.asset_type">
                <option value="stock">stock</option>
                <option value="etf">etf</option>
                <option value="fund">fund</option>
                <option value="bond">bond</option>
                <option value="cash">cash</option>
                <option value="other">other</option>
              </select>
            </label>
            <label><span>图标名</span><input v-model.trim="assetForm.icon_name" type="text" /></label>
            <label><span>当前价格</span><input v-model="assetForm.current_price" type="number" step="0.0001" min="0" /></label>
            <button class="submit-btn" type="submit">{{ editingAssetId ? '更新资产' : '新增资产' }}</button>
          </form>
          <div class="list-shell">
            <button v-for="asset in assets" :key="asset.id" class="list-row" @click="editAsset(asset)">
              <div><strong>{{ asset.name }}</strong><span>{{ asset.ticker_code }} · {{ asset.asset_type }}</span></div>
              <span class="row-actions" @click.stop="deleteAsset(asset.id)">删除</span>
            </button>
          </div>
        </article>
      </div>

      <div class="admin-column admin-column--wide">
        <article class="admin-card">
          <div class="card-head">
            <h2>持仓 / 论点 / 曲线</h2>
            <select v-model="selectedPortfolioId" class="inline-select">
              <option :value="null">选择组合</option>
              <option v-for="portfolio in portfolios" :key="portfolio.id" :value="portfolio.id">{{ portfolio.name }}</option>
            </select>
          </div>

          <div v-if="selectedPortfolioDetail" class="detail-stack">
            <section class="data-preview">
              <h3>当前组合快照</h3>
              <p>{{ selectedPortfolioDetail.portfolio.name }} · {{ selectedPortfolioDetail.holdings.length }} 项持仓 · {{ selectedPortfolioDetail.performance_history.length }} 条净值记录</p>
            </section>

            <div class="sub-grid">
              <form class="form-grid soft-panel" @submit.prevent="submitHolding">
                <div class="sub-head">
                  <h3>持仓</h3>
                  <button v-if="editingHoldingId" class="ghost-btn" type="button" @click="resetHoldingForm">取消编辑</button>
                </div>
                <label>
                  <span>资产</span>
                  <select v-model.number="holdingForm.asset_id" required @change="handleHoldingAssetChange">
                    <option value="">选择资产</option>
                    <option v-for="asset in assets" :key="asset.id" :value="asset.id">{{ asset.name }}</option>
                  </select>
                </label>
                <label><span>投入金额</span><input v-model="holdingForm.invested_amount" type="number" step="0.0001" min="0" required /></label>
                <label><span>份额</span><input v-model="holdingForm.share_count" type="number" step="0.0001" min="0" required /></label>
                <label><span>平均成本</span><input v-model="holdingForm.average_cost" type="number" step="0.0001" min="0" required /></label>
                <label><span>权重 (%)</span><input v-model="holdingForm.weight_percentage" type="number" step="0.0001" min="0" max="100" required /></label>
                <button class="submit-btn" type="submit">{{ editingHoldingId ? '更新持仓' : '新增持仓' }}</button>
              </form>

              <form class="form-grid soft-panel" @submit.prevent="submitPerformance">
                <div class="sub-head">
                  <h3>净值曲线</h3>
                  <button v-if="editingPerformanceId" class="ghost-btn" type="button" @click="resetPerformanceForm">取消编辑</button>
                </div>
                <label><span>日期</span><input v-model="performanceForm.record_date" type="date" required /></label>
                <label><span>组合净值</span><input v-model="performanceForm.portfolio_nav" type="number" step="0.0001" min="0" required /></label>
                <label><span>比较基准</span><input v-model="performanceForm.benchmark_nav" type="number" step="0.0001" min="0" /></label>
                <button class="submit-btn" type="submit">{{ editingPerformanceId ? '更新记录' : '新增记录' }}</button>
              </form>
            </div>

            <form class="form-grid soft-panel" @submit.prevent="submitThesis">
              <div class="sub-head">
                <h3>投资逻辑</h3>
                <button v-if="editingThesisId" class="ghost-btn" type="button" @click="resetThesisForm">取消编辑</button>
              </div>
              <label>
                <span>资产</span>
                <select v-model.number="thesisForm.asset_id" required @change="handleThesisAssetChange">
                  <option value="">选择资产</option>
                  <option v-for="asset in assets" :key="asset.id" :value="asset.id">{{ asset.name }}</option>
                </select>
              </label>
              <label><span>策略标签</span><input v-model.trim="thesisForm.strategy_tag" type="text" /></label>
              <label><span>预期股息率</span><input v-model="thesisForm.expected_dividend_yield" type="number" step="0.0001" min="0" /></label>
              <label><span>安全边际</span><input v-model="thesisForm.margin_of_safety" type="number" step="0.0001" min="0" /></label>
              <label><span>估值方法</span><input v-model.trim="thesisForm.valuation_metric_name" type="text" /></label>
              <label><span>分位值</span><input v-model="thesisForm.percentile_value" type="number" min="0" max="100" /></label>
              <label class="field-span"><span>短摘要</span><input v-model.trim="thesisForm.short_description" type="text" maxlength="500" /></label>
              <label class="field-span"><span>Markdown 详情</span><textarea v-model="thesisForm.markdown_details" rows="8"></textarea></label>
              <button class="submit-btn" type="submit">{{ editingThesisId ? '更新逻辑' : '新增逻辑' }}</button>
            </form>

            <div class="sub-grid">
              <article class="soft-panel">
                <div class="sub-head"><h3>当前持仓</h3></div>
                <div class="table-mini">
                  <button v-for="item in selectedPortfolioDetail.holdings" :key="item.holding.id" class="table-row" @click="editHolding(item)">
                    <div><strong>{{ item.asset.name }}</strong><span>{{ item.asset.ticker_code }} · {{ item.holding.weight_percentage }}%</span></div>
                    <span class="row-actions" @click.stop="deleteHolding(item.holding.id)">删除</span>
                  </button>
                </div>
              </article>

              <article class="soft-panel">
                <div class="sub-head"><h3>历史净值</h3></div>
                <div class="table-mini">
                  <button v-for="entry in selectedPortfolioDetail.performance_history" :key="entry.id" class="table-row" @click="editPerformance(entry)">
                    <div><strong>{{ entry.record_date }}</strong><span>组合 {{ entry.portfolio_nav }} · 基准 {{ entry.benchmark_nav || '--' }}</span></div>
                    <span class="row-actions" @click.stop="deletePerformance(entry.id)">删除</span>
                  </button>
                </div>
              </article>
            </div>

            <article class="soft-panel">
              <div class="sub-head"><h3>投资逻辑列表</h3></div>
              <div class="table-mini">
                <button
                  v-for="item in holdingsWithThesis"
                  :key="`logic-${item.holding.id}`"
                  class="table-row"
                  @click="editThesis(item.investment_thesis)"
                >
                  <div><strong>{{ item.asset.name }}</strong><span>{{ item.investment_thesis?.strategy_tag || '暂无策略标签' }}</span></div>
                  <span class="row-actions" @click.stop="deleteThesis(item.investment_thesis.id)">删除</span>
                </button>
              </div>
            </article>
          </div>

          <div v-else class="empty-admin">选择一个组合后开始维护持仓和净值。</div>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { adminPortfolioApi } from '@/api/familyPortfolio'

const loading = ref(false)
const error = ref('')
const portfolios = ref([])
const assets = ref([])
const selectedPortfolioId = ref(null)
const selectedPortfolioDetail = ref(null)

const editingPortfolioId = ref(null)
const editingAssetId = ref(null)
const editingHoldingId = ref(null)
const editingThesisId = ref(null)
const editingPerformanceId = ref(null)

const portfolioForm = ref({ name: '', total_principal: '0', currency: 'CNY' })
const assetForm = ref({
  ticker_code: '',
  name: '',
  sector: '',
  asset_type: 'stock',
  icon_name: '',
  current_price: '0'
})
const holdingForm = ref({
  asset_id: '',
  invested_amount: '0',
  share_count: '0',
  average_cost: '0',
  weight_percentage: '0'
})
const thesisForm = ref({
  asset_id: '',
  strategy_tag: '',
  expected_dividend_yield: '',
  margin_of_safety: '',
  valuation_metric_name: '',
  percentile_value: '',
  short_description: '',
  markdown_details: ''
})
const performanceForm = ref({
  record_date: '',
  portfolio_nav: '1',
  benchmark_nav: ''
})

const holdingsWithThesis = computed(() =>
  (selectedPortfolioDetail.value?.holdings || []).filter(item => item.investment_thesis)
)

function getHoldingAssetId(item) {
  const rawAssetId = item?.holding?.asset_id ?? item?.asset?.id ?? null
  return rawAssetId === null || rawAssetId === undefined ? null : Number(rawAssetId)
}

function findHoldingByAssetId(assetId) {
  if (!assetId) {
    return null
  }
  const normalizedAssetId = Number(assetId)
  return (
    (selectedPortfolioDetail.value?.holdings || []).find(
      item => getHoldingAssetId(item) === normalizedAssetId
    ) || null
  )
}

function findThesisByAssetId(assetId) {
  if (!assetId) {
    return null
  }
  const normalizedAssetId = Number(assetId)
  return (
    holdingsWithThesis.value.find(item => Number(item.investment_thesis?.asset_id) === normalizedAssetId)
      ?.investment_thesis || null
  )
}

function formatCurrency(value) {
  return Number(value || 0).toLocaleString('zh-CN', {
    style: 'currency',
    currency: 'CNY',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

function normalizeNullableNumber(value) {
  return value === '' || value === null || value === undefined ? null : value
}

function resetPortfolioForm() {
  editingPortfolioId.value = null
  portfolioForm.value = { name: '', total_principal: '0', currency: 'CNY' }
}

function resetAssetForm() {
  editingAssetId.value = null
  assetForm.value = {
    ticker_code: '',
    name: '',
    sector: '',
    asset_type: 'stock',
    icon_name: '',
    current_price: '0'
  }
}

function resetHoldingForm() {
  editingHoldingId.value = null
  holdingForm.value = {
    asset_id: '',
    invested_amount: '0',
    share_count: '0',
    average_cost: '0',
    weight_percentage: '0'
  }
}

function syncHoldingFormByAsset(assetId) {
  if (!assetId) {
    resetHoldingForm()
    return
  }

  const existingHolding = findHoldingByAssetId(assetId)
  if (existingHolding) {
    editingHoldingId.value = existingHolding.holding.id
    holdingForm.value = {
      asset_id: getHoldingAssetId(existingHolding),
      invested_amount: existingHolding.holding.invested_amount,
      share_count: existingHolding.holding.share_count,
      average_cost: existingHolding.holding.average_cost,
      weight_percentage: existingHolding.holding.weight_percentage
    }
    return
  }

  editingHoldingId.value = null
  holdingForm.value = {
    asset_id: Number(assetId),
    invested_amount: '0',
    share_count: '0',
    average_cost: '0',
    weight_percentage: '0'
  }
}

function resetThesisForm() {
  editingThesisId.value = null
  thesisForm.value = {
    asset_id: '',
    strategy_tag: '',
    expected_dividend_yield: '',
    margin_of_safety: '',
    valuation_metric_name: '',
    percentile_value: '',
    short_description: '',
    markdown_details: ''
  }
}

function syncThesisFormByAsset(assetId) {
  if (!assetId) {
    resetThesisForm()
    return
  }

  const existingThesis = findThesisByAssetId(assetId)
  if (existingThesis) {
    editThesis(existingThesis)
    return
  }

  editingThesisId.value = null
  thesisForm.value = {
    asset_id: Number(assetId),
    strategy_tag: '',
    expected_dividend_yield: '',
    margin_of_safety: '',
    valuation_metric_name: '',
    percentile_value: '',
    short_description: '',
    markdown_details: ''
  }
}

function handleHoldingAssetChange() {
  syncHoldingFormByAsset(holdingForm.value.asset_id)
}

function handleThesisAssetChange() {
  syncThesisFormByAsset(thesisForm.value.asset_id)
}

function resetPerformanceForm() {
  editingPerformanceId.value = null
  performanceForm.value = {
    record_date: '',
    portfolio_nav: '1',
    benchmark_nav: ''
  }
}

async function loadAll() {
  loading.value = true
  error.value = ''
  try {
    const [portfolioResponse, assetResponse] = await Promise.all([
      adminPortfolioApi.listPortfolios(),
      adminPortfolioApi.listAssets()
    ])
    portfolios.value = portfolioResponse.data?.items || []
    assets.value = assetResponse.data?.items || []

    if (!selectedPortfolioId.value && portfolios.value.length) {
      selectedPortfolioId.value = portfolios.value[0].id
    }
    if (selectedPortfolioId.value) {
      await loadPortfolioDetail(selectedPortfolioId.value)
    }
  } catch (requestError) {
    error.value = requestError?.response?.data?.detail || requestError?.message || '请求失败'
  } finally {
    loading.value = false
  }
}

async function loadPortfolioDetail(id) {
  if (!id) {
    selectedPortfolioDetail.value = null
    return
  }
  const response = await adminPortfolioApi.getPortfolioDetail(id)
  selectedPortfolioDetail.value = response.data
}

async function submitPortfolio() {
  if (editingPortfolioId.value) {
    await adminPortfolioApi.updatePortfolio(editingPortfolioId.value, { ...portfolioForm.value })
  } else {
    await adminPortfolioApi.createPortfolio({ ...portfolioForm.value })
  }
  resetPortfolioForm()
  await loadAll()
}

async function submitAsset() {
  const payload = { ...assetForm.value, current_price: normalizeNullableNumber(assetForm.value.current_price) }
  if (editingAssetId.value) {
    await adminPortfolioApi.updateAsset(editingAssetId.value, payload)
  } else {
    await adminPortfolioApi.createAsset(payload)
  }
  resetAssetForm()
  await loadAll()
}

async function submitHolding() {
  const payload = {
    portfolio_id: selectedPortfolioId.value,
    asset_id: Number(holdingForm.value.asset_id),
    invested_amount: holdingForm.value.invested_amount,
    share_count: holdingForm.value.share_count,
    average_cost: holdingForm.value.average_cost,
    weight_percentage: holdingForm.value.weight_percentage
  }
  if (editingHoldingId.value) {
    await adminPortfolioApi.updateHolding(editingHoldingId.value, payload)
  } else {
    await adminPortfolioApi.createHolding(payload)
  }
  resetHoldingForm()
  await loadPortfolioDetail(selectedPortfolioId.value)
}

async function submitThesis() {
  const payload = {
    asset_id: Number(thesisForm.value.asset_id),
    strategy_tag: thesisForm.value.strategy_tag || null,
    expected_dividend_yield: normalizeNullableNumber(thesisForm.value.expected_dividend_yield),
    margin_of_safety: normalizeNullableNumber(thesisForm.value.margin_of_safety),
    valuation_metric_name: thesisForm.value.valuation_metric_name || null,
    percentile_value: normalizeNullableNumber(thesisForm.value.percentile_value),
    short_description: thesisForm.value.short_description || null,
    markdown_details: thesisForm.value.markdown_details || null
  }
  if (editingThesisId.value) {
    await adminPortfolioApi.updateInvestmentThesis(editingThesisId.value, payload)
  } else {
    await adminPortfolioApi.createInvestmentThesis(payload)
  }
  resetThesisForm()
  await loadPortfolioDetail(selectedPortfolioId.value)
}

async function submitPerformance() {
  const payload = {
    portfolio_id: selectedPortfolioId.value,
    record_date: performanceForm.value.record_date,
    portfolio_nav: performanceForm.value.portfolio_nav,
    benchmark_nav: normalizeNullableNumber(performanceForm.value.benchmark_nav)
  }
  if (editingPerformanceId.value) {
    await adminPortfolioApi.updatePerformanceHistory(editingPerformanceId.value, payload)
  } else {
    await adminPortfolioApi.createPerformanceHistory(payload)
  }
  resetPerformanceForm()
  await loadPortfolioDetail(selectedPortfolioId.value)
}

function editPortfolio(portfolio) {
  editingPortfolioId.value = portfolio.id
  portfolioForm.value = {
    name: portfolio.name,
    total_principal: portfolio.total_principal,
    currency: portfolio.currency
  }
}

function editAsset(asset) {
  editingAssetId.value = asset.id
  assetForm.value = {
    ticker_code: asset.ticker_code,
    name: asset.name,
    sector: asset.sector || '',
    asset_type: asset.asset_type,
    icon_name: asset.icon_name || '',
    current_price: asset.current_price || '0'
  }
}

function editHolding(item) {
  editingHoldingId.value = item.holding.id
  holdingForm.value = {
    asset_id: item.holding.asset_id,
    invested_amount: item.holding.invested_amount,
    share_count: item.holding.share_count,
    average_cost: item.holding.average_cost,
    weight_percentage: item.holding.weight_percentage
  }
}

function editThesis(thesis) {
  if (!thesis) {
    return
  }
  editingThesisId.value = thesis.id
  thesisForm.value = {
    asset_id: thesis.asset_id,
    strategy_tag: thesis.strategy_tag || '',
    expected_dividend_yield: thesis.expected_dividend_yield || '',
    margin_of_safety: thesis.margin_of_safety || '',
    valuation_metric_name: thesis.valuation_metric_name || '',
    percentile_value: thesis.percentile_value || '',
    short_description: thesis.short_description || '',
    markdown_details: thesis.markdown_details || ''
  }
}

function editPerformance(entry) {
  editingPerformanceId.value = entry.id
  performanceForm.value = {
    record_date: entry.record_date,
    portfolio_nav: entry.portfolio_nav,
    benchmark_nav: entry.benchmark_nav || ''
  }
}

async function deletePortfolio(id) {
  await adminPortfolioApi.deletePortfolio(id)
  if (selectedPortfolioId.value === id) {
    selectedPortfolioId.value = null
    selectedPortfolioDetail.value = null
  }
  await loadAll()
}

async function deleteAsset(id) {
  await adminPortfolioApi.deleteAsset(id)
  await loadAll()
}

async function deleteHolding(id) {
  await adminPortfolioApi.deleteHolding(id)
  await loadPortfolioDetail(selectedPortfolioId.value)
}

async function deleteThesis(id) {
  await adminPortfolioApi.deleteInvestmentThesis(id)
  await loadPortfolioDetail(selectedPortfolioId.value)
}

async function deletePerformance(id) {
  await adminPortfolioApi.deletePerformanceHistory(id)
  await loadPortfolioDetail(selectedPortfolioId.value)
}

watch(selectedPortfolioId, async value => {
  if (!value) {
    selectedPortfolioDetail.value = null
    return
  }
  await loadPortfolioDetail(value)
  resetHoldingForm()
  resetThesisForm()
  resetPerformanceForm()
})

watch(
  holdingsWithThesis,
  () => {
    if (!thesisForm.value.asset_id) {
      return
    }
    syncThesisFormByAsset(thesisForm.value.asset_id)
  },
  { deep: true }
)

watch(
  () => selectedPortfolioDetail.value?.holdings,
  () => {
    if (!holdingForm.value.asset_id) {
      return
    }
    syncHoldingFormByAsset(holdingForm.value.asset_id)
  },
  { deep: true }
)

onMounted(loadAll)
</script>

<style scoped>
.portfolio-admin {
  max-width: 1520px;
}

.admin-hero,
.admin-card,
.soft-panel,
.admin-error {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
}

.admin-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.hero-kicker {
  font-size: 0.75rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #64748b;
  font-weight: 700;
}

.admin-hero h1,
.card-head h2,
.sub-head h3 {
  font-family: 'Manrope', sans-serif;
  color: #0f172a;
}

.admin-hero p:last-child {
  max-width: 58ch;
  color: #475569;
  margin-top: 0.45rem;
}

.refresh-btn,
.submit-btn,
.ghost-btn {
  height: 40px;
  border-radius: 10px;
  padding: 0 0.95rem;
  cursor: pointer;
}

.refresh-btn,
.submit-btn {
  border: 1px solid #0f172a;
  background: #0f172a;
  color: #ffffff;
  font-weight: 600;
}

.ghost-btn {
  border: 1px solid #cbd5e1;
  background: #ffffff;
  color: #475569;
}

.admin-error {
  margin-bottom: 1rem;
  padding: 1rem 1.25rem;
  color: #b91c1c;
}

.admin-layout-grid {
  display: grid;
  grid-template-columns: 380px minmax(0, 1fr);
  gap: 1.5rem;
}

.admin-column {
  display: grid;
  gap: 1.5rem;
  align-content: start;
}

.admin-card {
  padding: 1.25rem;
}

.card-head,
.sub-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-grid {
  display: grid;
  gap: 0.85rem;
}

.sub-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

label {
  display: grid;
  gap: 0.35rem;
}

label span {
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #64748b;
  font-weight: 700;
}

input,
select,
textarea {
  width: 100%;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  background: #ffffff;
  color: #0f172a;
  padding: 0.75rem 0.85rem;
  font: inherit;
}

textarea {
  resize: vertical;
}

.field-span {
  grid-column: 1 / -1;
}

.list-shell,
.table-mini {
  display: grid;
  gap: 0.65rem;
  margin-top: 1rem;
}

.list-row,
.table-row {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  width: 100%;
  padding: 0.9rem 1rem;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  text-align: left;
  cursor: pointer;
}

.list-row strong,
.table-row strong {
  display: block;
  color: #0f172a;
}

.list-row span,
.table-row span,
.data-preview p,
.empty-admin {
  color: #64748b;
}

.row-actions {
  color: #b91c1c;
  font-size: 0.85rem;
}

.soft-panel {
  padding: 1rem;
}

.detail-stack {
  display: grid;
  gap: 1rem;
}

.data-preview {
  padding: 0.95rem 1rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
}

.inline-select {
  min-width: 180px;
}

.empty-admin {
  padding: 1.5rem 0;
}

@media (max-width: 1120px) {
  .admin-layout-grid,
  .sub-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .admin-hero {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
