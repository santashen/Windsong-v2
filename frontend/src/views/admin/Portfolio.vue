<template>
  <div class="portfolio-admin-page">
    <div class="page-header">
      <div>
        <p class="header-eyebrow">Investment Management</p>
        <h1>新增投资快照</h1>
        <p class="header-text">
          每次提交都会写入一条新的历史记录，前台家庭页面始终只读取最新一期。
        </p>
      </div>
      <button class="secondary-btn" type="button" @click="resetForm">重置表单</button>
    </div>

    <form class="snapshot-form" @submit.prevent="handleSubmit">
      <section class="form-card">
        <div class="section-heading">
          <h2>本期概览</h2>
        </div>
        <div class="form-grid">
          <label class="field">
            <span>记录日期</span>
            <input v-model="form.recordDate" type="date" required />
          </label>
          <label class="field">
            <span>总本金</span>
            <input v-model.number="form.totalPrincipal" type="number" min="0" step="0.01" required />
          </label>
          <label class="field">
            <span>当前总市值</span>
            <input v-model.number="form.totalMarketValue" type="number" min="0" step="0.01" required />
          </label>
          <label class="field">
            <span>预期年度总股息</span>
            <input v-model.number="form.expectedAnnualDividends" type="number" min="0" step="0.01" required />
          </label>
          <label class="field">
            <span>整体持仓股息率 (%)</span>
            <input v-model.number="form.portfolioDividendYieldPct" type="number" min="0" step="0.01" required />
          </label>
          <label class="field">
            <span>当前市值股息率 (%)</span>
            <input v-model.number="form.marketValueDividendYieldPct" type="number" min="0" step="0.01" required />
          </label>
        </div>
        <label class="field field-full">
          <span>主理人留言</span>
          <textarea
            v-model="form.managerComment"
            rows="5"
            placeholder="写给家人的本期说明，例如资产配置逻辑、关注的现金流质量、对估值的判断边界。"
          ></textarea>
        </label>
      </section>

      <section class="form-card">
        <div class="section-heading">
          <div>
            <h2>区块 A: 宽基 / 行业 ETF</h2>
            <p>围绕 预期年分红 = 持有份数 × 每份派息 录入 ETF 持仓，强调份额积累与现金流产出。</p>
          </div>
          <button class="secondary-btn" type="button" @click="addEtf">添加 ETF</button>
        </div>

        <div class="rows-stack">
          <div v-for="(etf, index) in form.holdings.etfs" :key="`etf-${index}`" class="holding-row">
            <div class="company-block">
              <div class="ownership-note">
                预期年分红 = 持有份数 × 每份派息，持仓股息率 = 每份派息 ÷ 平均买入成本
              </div>

              <div class="row-grid etf-grid etf-grid--top">
                <label class="field">
                  <span>标的名称</span>
                  <input v-model.trim="etf.name" type="text" required />
                </label>
                <label class="field">
                  <span>持仓占比 (%)</span>
                  <input v-model.number="etf.weightPct" type="number" min="0" max="100" step="0.01" required />
                </label>
                <label class="field">
                  <span>当前参考价格</span>
                  <input v-model.number="etf.currentReferencePrice" type="number" min="0" step="0.01" required />
                </label>
              </div>

              <div class="divider"></div>

              <div class="row-grid etf-grid etf-grid--formula">
                <label class="field">
                  <span>持有份数</span>
                  <input v-model.number="etf.shares" type="number" min="0" step="1" required />
                </label>
                <label class="field">
                  <span>平均买入成本</span>
                  <input v-model.number="etf.averageCost" type="number" min="0" step="0.01" required />
                </label>
                <label class="field">
                  <span>每份派息</span>
                  <input v-model.number="etf.dividendPerShare" type="number" min="0" step="0.01" required />
                </label>
                <label class="field">
                  <span>预期年分红</span>
                  <input :value="formatNumber(etfAnnualDividend(etf))" type="number" step="0.01" readonly />
                </label>
                <label class="field">
                  <span>持仓股息率 (%)</span>
                  <input :value="formatNumber(etfYieldOnCost(etf))" type="number" step="0.01" readonly />
                </label>
              </div>
            </div>
            <button
              class="danger-btn"
              type="button"
              @click="removeEtf(index)"
              :disabled="form.holdings.etfs.length === 1"
            >
              删除
            </button>
          </div>
        </div>
      </section>

      <section class="form-card">
        <div class="section-heading">
          <div>
            <h2>区块 B: 优秀企业</h2>
            <p>围绕 分红 = 股数 × EPS × 派息率 录入和展示企业分红能力与我们的所有权。</p>
          </div>
          <button class="secondary-btn" type="button" @click="addCompany">添加企业</button>
        </div>

        <div class="rows-stack">
          <div v-for="(company, index) in form.holdings.companies" :key="`company-${index}`" class="holding-row">
            <div class="company-block">
              <div class="row-grid company-grid company-grid--top">
                <label class="field">
                  <span>企业名称</span>
                  <input v-model.trim="company.name" type="text" required />
                </label>
                <label class="field">
                  <span>估值状态</span>
                  <select v-model="company.valuationStatus" required>
                    <option value="undervalued">低估</option>
                    <option value="fair">合理</option>
                    <option value="overvalued">高估</option>
                  </select>
                </label>
                <label class="field">
                  <span>当前股价</span>
                  <input v-model.number="company.currentPrice" type="number" min="0" step="0.01" required />
                </label>
              </div>

              <div class="divider"></div>

              <div class="ownership-note">
                分红 = 持有股数 × 每股收益(EPS) × 派息率
              </div>

              <div class="row-grid company-grid company-grid--formula">
                <label class="field">
                  <span>持有股数</span>
                  <input v-model.number="company.shares" type="number" min="0" step="1" required />
                </label>
                <label class="field">
                  <span>每股收益 EPS</span>
                  <input v-model.number="company.eps" type="number" min="0" step="0.01" required />
                </label>
                <label class="field">
                  <span>派息率 (%)</span>
                  <input v-model.number="company.payoutRatio" type="number" min="0" max="100" step="0.01" required />
                </label>
                <label class="field">
                  <span>每股分红 DPS</span>
                  <input :value="formatNumber(companyDps(company))" type="number" step="0.01" readonly />
                </label>
                <label class="field">
                  <span>预期年分红</span>
                  <input :value="formatNumber(companyAnnualDividend(company))" type="number" step="0.01" readonly />
                </label>
              </div>

              <div class="divider"></div>

              <div class="row-grid company-grid company-grid--quality">
                <label class="field">
                  <span>平均持仓成本</span>
                  <input v-model.number="company.averageCost" type="number" min="0" step="0.01" required />
                </label>
                <label class="field">
                  <span>当前股价</span>
                  <input v-model.number="company.currentPrice" type="number" min="0" step="0.01" required />
                </label>
                <label class="field">
                  <span>持仓股息率 (%)</span>
                  <input v-model.number="company.holdingDividendYieldPct" type="number" min="0" step="0.01" required />
                </label>
                <label class="field">
                  <span>当前股息率 (%)</span>
                  <input v-model.number="company.currentDividendYieldPct" type="number" min="0" step="0.01" required />
                </label>
              </div>
            </div>

            <button
              class="danger-btn"
              type="button"
              @click="removeCompany(index)"
              :disabled="form.holdings.companies.length === 1"
            >
              删除
            </button>
          </div>
        </div>
      </section>

      <section class="form-actions">
        <button class="primary-btn" type="submit" :disabled="isSubmitting">
          {{ isSubmitting ? '提交中...' : '保存为新一期快照' }}
        </button>
        <p v-if="submitMessage" class="submit-message success">{{ submitMessage }}</p>
        <p v-if="submitError" class="submit-message error">{{ submitError }}</p>
      </section>
    </form>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { adminPortfolioApi } from '@/api/portfolio'

function createEtf() {
  return {
    name: '',
    weightPct: 0,
    shares: 0,
    averageCost: 0,
    dividendPerShare: 0,
    currentReferencePrice: 0
  }
}

function createCompany() {
  return {
    name: '',
    valuationStatus: 'fair',
    shares: 0,
    eps: 0,
    payoutRatio: 0,
    averageCost: 0,
    currentPrice: 0,
    holdingDividendYieldPct: 0,
    currentDividendYieldPct: 0
  }
}

function createInitialForm() {
  return {
    recordDate: new Date().toISOString().slice(0, 10),
    totalPrincipal: 0,
    totalMarketValue: 0,
    expectedAnnualDividends: 0,
    portfolioDividendYieldPct: 0,
    marketValueDividendYieldPct: 0,
    managerComment: '',
    holdings: {
      etfs: [createEtf()],
      companies: [createCompany()]
    }
  }
}

const form = reactive(createInitialForm())
const isSubmitting = ref(false)
const submitMessage = ref('')
const submitError = ref('')

function resetForm() {
  Object.assign(form, createInitialForm())
  submitMessage.value = ''
  submitError.value = ''
}

function addEtf() {
  form.holdings.etfs.push(createEtf())
}

function removeEtf(index) {
  if (form.holdings.etfs.length === 1) return
  form.holdings.etfs.splice(index, 1)
}

function addCompany() {
  form.holdings.companies.push(createCompany())
}

function removeCompany(index) {
  if (form.holdings.companies.length === 1) return
  form.holdings.companies.splice(index, 1)
}

function roundToTwo(value) {
  return Number((Number(value || 0)).toFixed(2))
}

function companyDps(company) {
  return roundToTwo((Number(company.eps || 0) * Number(company.payoutRatio || 0)) / 100)
}

function companyAnnualDividend(company) {
  return roundToTwo(Number(company.shares || 0) * companyDps(company))
}

function etfAnnualDividend(etf) {
  return roundToTwo(Number(etf.shares || 0) * Number(etf.dividendPerShare || 0))
}

function etfYieldOnCost(etf) {
  const averageCost = Number(etf.averageCost || 0)
  if (!averageCost) return 0
  return roundToTwo((Number(etf.dividendPerShare || 0) / averageCost) * 100)
}

function formatNumber(value) {
  return Number(value || 0).toFixed(2)
}

function buildPayload() {
  return {
    recordDate: form.recordDate,
    totalPrincipal: Number(form.totalPrincipal),
    totalMarketValue: Number(form.totalMarketValue),
    expectedAnnualDividends: Number(form.expectedAnnualDividends),
    portfolioDividendYieldPct: Number(form.portfolioDividendYieldPct),
    marketValueDividendYieldPct: Number(form.marketValueDividendYieldPct),
    managerComment: form.managerComment.trim(),
    holdings: {
      etfs: form.holdings.etfs.map(item => ({
        name: item.name.trim(),
        weightPct: Number(item.weightPct),
        shares: Number(item.shares),
        averageCost: Number(item.averageCost),
        dividendPerShare: roundToTwo(item.dividendPerShare),
        expectedAnnualDividend: etfAnnualDividend(item),
        yieldOnCost: etfYieldOnCost(item),
        currentReferencePrice: Number(item.currentReferencePrice)
      })),
      companies: form.holdings.companies.map(item => ({
        name: item.name.trim(),
        valuationStatus: item.valuationStatus,
        shares: Number(item.shares),
        eps: roundToTwo(item.eps),
        payoutRatio: Number(item.payoutRatio),
        dps: companyDps(item),
        expectedAnnualDividend: companyAnnualDividend(item),
        averageCost: Number(item.averageCost),
        currentPrice: Number(item.currentPrice),
        holdingDividendYieldPct: Number(item.holdingDividendYieldPct),
        currentDividendYieldPct: Number(item.currentDividendYieldPct)
      }))
    }
  }
}

async function handleSubmit() {
  isSubmitting.value = true
  submitMessage.value = ''
  submitError.value = ''

  try {
    await adminPortfolioApi.createSnapshot(buildPayload())
    resetForm()
    submitMessage.value = '新一期投资快照已保存。'
  } catch (error) {
    submitError.value = error.message || '保存失败，请稍后重试。'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.portfolio-admin-page {
  max-width: 1280px;
}

.page-header,
.form-card,
.holding-row {
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 16px;
}

.page-header {
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.header-eyebrow {
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-text-secondary);
  margin-bottom: 0.5rem;
}

.page-header h1 {
  font-size: 1.9rem;
  color: var(--color-text);
  margin-bottom: 0.35rem;
}

.header-text {
  color: var(--color-text-secondary);
  max-width: 52rem;
}

.snapshot-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-card {
  padding: 1.5rem;
}

.section-heading {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1rem;
}

.section-heading h2 {
  font-size: 1.2rem;
  margin-bottom: 0.25rem;
}

.section-heading p {
  color: var(--color-text-secondary);
  font-size: 0.92rem;
}

.form-grid,
.row-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
}

.company-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.etf-grid--formula {
  grid-template-columns: repeat(5, minmax(0, 1fr));
}

.company-grid--formula {
  grid-template-columns: repeat(5, minmax(0, 1fr));
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.field span {
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.field input,
.field textarea,
.field select {
  width: 100%;
  padding: 0.82rem 0.95rem;
  border: 1px solid var(--color-border);
  border-radius: 10px;
  background: var(--color-bg);
  color: var(--color-text);
  font-size: 0.95rem;
}

.field input:focus,
.field textarea:focus,
.field select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.12);
}

.field input[readonly] {
  background: var(--color-bg-secondary);
  color: var(--color-text);
  font-weight: 700;
}

.field-full {
  margin-top: 1rem;
}

.rows-stack {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.holding-row {
  padding: 1rem;
}

.company-block {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.divider {
  height: 1px;
  background: var(--color-border);
}

.ownership-note {
  font-size: 0.88rem;
  color: var(--color-primary);
  font-weight: 600;
}

.secondary-btn,
.danger-btn,
.primary-btn {
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
}

.secondary-btn {
  padding: 0.8rem 1rem;
  background: var(--color-bg-secondary);
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.danger-btn {
  margin-top: 0.9rem;
  padding: 0.65rem 0.95rem;
  background: rgba(239, 68, 68, 0.08);
  color: var(--color-danger);
}

.danger-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.form-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.primary-btn {
  padding: 0.9rem 1.4rem;
  background: var(--color-primary);
  color: #fff;
}

.primary-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.submit-message {
  font-size: 0.95rem;
}

.submit-message.success {
  color: var(--color-success);
}

.submit-message.error {
  color: var(--color-danger);
}

@media (max-width: 1200px) {
  .etf-grid--formula,
  .company-grid--formula {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 1024px) {
  .form-grid,
  .row-grid,
  .company-grid,
  .etf-grid--formula,
  .company-grid--formula {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .page-header,
  .section-heading,
  .form-actions {
    flex-direction: column;
    align-items: flex-start;
  }

  .form-grid,
  .row-grid,
  .company-grid,
  .etf-grid--formula,
  .company-grid--formula {
    grid-template-columns: 1fr;
  }
}
</style>
