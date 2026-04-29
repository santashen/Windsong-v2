<template>
  <div class="heat-page">
    <Header />

    <main class="heat-main">
      <section class="heat-head">
        <div>
          <p class="eyebrow">Thermal Workbench</p>
          <h1 class="page-title">流体换热计算</h1>
          <p class="page-subtitle">
            选择 CoolProp 工质，输入统一工况和单组温度，直接得到换热量。
          </p>
        </div>

        <router-link class="back-link" to="/services">返回服务目录</router-link>
      </section>

      <form class="workspace-shell" aria-label="换热计算工作区" @submit.prevent="calculateCurrent">
        <aside class="parameter-panel">
          <div class="panel-head">
            <p class="panel-title">统一工况</p>
            <p class="panel-note">同一批数据共用工质、压力和流量。</p>
          </div>

          <label class="field fluid-field">
            <span>工质</span>
            <input
              v-model.trim="fluidQuery"
              type="text"
              autocomplete="off"
              placeholder="Water"
              @focus="showFluidSuggestions = true"
              @blur="hideFluidSuggestionsSoon"
            />
            <div v-if="showFluidSuggestions && fluidSuggestions.length" class="fluid-menu">
              <button
                v-for="fluid in fluidSuggestions"
                :key="fluid.name"
                type="button"
                class="fluid-option"
                @click="selectFluid(fluid.name)"
              >
                {{ fluid.name }}
              </button>
            </div>
            <small v-if="selectedFluid">已选择 {{ selectedFluid }}</small>
          </label>

          <div class="field-row">
            <label class="field">
              <span>压力</span>
              <input v-model.number="form.pressureValue" type="number" min="0" step="any" />
            </label>
            <label class="field unit-field">
              <span>单位</span>
              <select v-model="form.pressureUnit">
                <option value="Pa">Pa</option>
                <option value="kPa">kPa</option>
                <option value="MPa">MPa</option>
                <option value="bar">bar</option>
              </select>
            </label>
          </div>

          <div class="field-row">
            <label class="field">
              <span>流量</span>
              <input v-model.number="form.flowValue" type="number" min="0" step="any" />
            </label>
            <label class="field unit-field">
              <span>单位</span>
              <select v-model="form.flowUnit">
                <option value="kg/s">kg/s</option>
                <option value="L/min">L/min</option>
                <option value="m³/h">m³/h</option>
              </select>
            </label>
          </div>
        </aside>

        <section class="input-panel">
          <div class="panel-head">
            <p class="panel-title">温度输入</p>
            <p class="panel-note">温度默认单位为 °C。</p>
          </div>

          <div class="mode-strip" aria-label="计算模式">
            <button
              class="mode-pill"
              :class="{ 'mode-pill--active': mode === 'single' }"
              type="button"
              @click="setMode('single')"
            >
              单组计算
            </button>
            <button
              class="mode-pill"
              :class="{ 'mode-pill--active': mode === 'batch' }"
              type="button"
              @click="setMode('batch')"
            >
              批量计算
            </button>
          </div>

          <div v-if="mode === 'single'" class="temperature-grid">
            <label class="field">
              <span>入口温度 Tin</span>
              <input v-model.number="form.tinC" type="number" step="any" />
            </label>
            <label class="field">
              <span>出口温度 Tout</span>
              <input v-model.number="form.toutC" type="number" step="any" />
            </label>
          </div>

          <div v-else class="batch-grid">
            <label class="field">
              <span>入口温度列</span>
              <textarea v-model="batchTinText" spellcheck="false" placeholder="25.1&#10;25.2&#10;25.3"></textarea>
            </label>
            <label class="field">
              <span>出口温度列</span>
              <textarea v-model="batchToutText" spellcheck="false" placeholder="30.1&#10;30.2&#10;30.3"></textarea>
            </label>
            <p class="row-count">
              Tin {{ parsedBatchInfo.tinCount }} 个，Tout {{ parsedBatchInfo.toutCount }} 个
            </p>
          </div>

          <button class="submit-button" type="submit" :disabled="isLoading">
            {{ isLoading ? '计算中...' : '计算' }}
          </button>

          <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
        </section>

        <aside class="result-panel">
          <div class="panel-head">
            <p class="panel-title">结果</p>
            <p class="panel-note">Q = m_dot × (h_out - h_in)</p>
          </div>

          <div class="result-value" :class="{ 'result-value--empty': !primaryResult }">
            <span>Q</span>
            <strong>{{ primaryResult?.qDisplay || '--' }}</strong>
          </div>

          <div v-if="mode === 'single'" class="result-meta">
            <div>
              <span>Tin</span>
              <strong>{{ primaryResult ? `${primaryResult.tinC} °C` : '--' }}</strong>
            </div>
            <div>
              <span>Tout</span>
              <strong>{{ primaryResult ? `${primaryResult.toutC} °C` : '--' }}</strong>
            </div>
            <div>
              <span>Q</span>
              <strong>{{ primaryResult ? `${formatNumber(primaryResult.qW)} W` : '--' }}</strong>
            </div>
          </div>

          <div v-else class="batch-result">
            <div class="batch-actions">
              <p class="batch-summary">
                {{ batchResults.length ? `${batchResults.length} 行结果` : '等待批量计算' }}
              </p>
              <div class="action-buttons">
                <button type="button" :disabled="!batchResults.length" @click="copyQColumn">复制 Q 列</button>
                <button type="button" :disabled="!batchResults.length" @click="exportCsv">导出 CSV</button>
              </div>
            </div>
            <p v-if="successMessage" class="success-message">{{ successMessage }}</p>
            <div v-if="batchResults.length" class="result-table-wrap">
              <table class="result-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Tin °C</th>
                    <th>Tout °C</th>
                    <th>Q W</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="row in batchResults" :key="row.index">
                    <td>{{ row.index }}</td>
                    <td>{{ formatNumber(row.tinC) }}</td>
                    <td>{{ formatNumber(row.toutC) }}</td>
                    <td>{{ formatNumber(row.qW) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </aside>
      </form>
    </main>

    <Footer />
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'

import { calculateHeatDissipation, searchHeatDissipationFluids } from '@/api/heatDissipation'
import Footer from '@/components/layout/Footer.vue'
import Header from '@/components/layout/Header.vue'

const fluidQuery = ref('Water')
const selectedFluid = ref('Water')
const fluidSuggestions = ref([])
const showFluidSuggestions = ref(false)
const isLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const singleResult = ref(null)
const batchResults = ref([])
const mode = ref('single')
const batchTinText = ref('25.1\n25.2\n25.3')
const batchToutText = ref('30.1\n30.2\n30.3')

const form = reactive({
  pressureValue: 101.325,
  pressureUnit: 'kPa',
  flowValue: 0.1,
  flowUnit: 'kg/s',
  tinC: 25,
  toutC: 35
})

let fluidSearchTimer = null
let isSelectingFluid = false

const primaryResult = computed(() => {
  if (mode.value === 'single') {
    return singleResult.value
  }
  return batchResults.value[0] || null
})

const parsedBatchInfo = computed(() => {
  const tin = parseNumberList(batchTinText.value)
  const tout = parseNumberList(batchToutText.value)
  return {
    tinCount: tin.values.length,
    toutCount: tout.values.length
  }
})

function isFiniteNumber(value) {
  return Number.isFinite(Number(value))
}

function formatNumber(value) {
  return Number(value).toLocaleString('zh-CN', {
    maximumFractionDigits: 4
  })
}

function getRequestErrorMessage(error) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') {
    return detail
  }
  if (detail?.message) {
    return detail.rowIndex ? `第 ${detail.rowIndex} 行：${detail.message}` : detail.message
  }
  return error?.message || '换热量计算失败，请稍后重试'
}

function setMode(nextMode) {
  mode.value = nextMode
  errorMessage.value = ''
  successMessage.value = ''
}

function parseNumberList(text) {
  const tokens = String(text || '')
    .split(/[\s,]+/)
    .map(token => token.trim())
    .filter(Boolean)
  const values = []

  for (let index = 0; index < tokens.length; index += 1) {
    const value = Number(tokens[index])
    if (!Number.isFinite(value)) {
      return {
        values,
        error: `第 ${index + 1} 行温度数据无法识别，请检查输入格式`
      }
    }
    values.push(value)
  }

  return { values, error: '' }
}

async function loadFluidSuggestions(query = fluidQuery.value) {
  try {
    const response = await searchHeatDissipationFluids(query, 20)
    fluidSuggestions.value = response.data?.items || []
  } catch (error) {
    fluidSuggestions.value = []
  }
}

function selectFluid(name) {
  isSelectingFluid = true
  selectedFluid.value = name
  fluidQuery.value = name
  showFluidSuggestions.value = false
  errorMessage.value = ''
  successMessage.value = ''
  window.clearTimeout(fluidSearchTimer)
  window.setTimeout(() => {
    isSelectingFluid = false
  }, 0)
}

function hideFluidSuggestionsSoon() {
  window.setTimeout(() => {
    if (!isSelectingFluid) {
      showFluidSuggestions.value = false
    }
  }, 120)
}

function validateSingleInput() {
  const commonError = validateCommonInput()
  if (commonError) {
    return commonError
  }
  if (!isFiniteNumber(form.tinC)) {
    return '入口温度数据无法识别，请检查输入格式'
  }
  if (!isFiniteNumber(form.toutC)) {
    return '出口温度数据无法识别，请检查输入格式'
  }
  return ''
}

function validateCommonInput() {
  if (!selectedFluid.value || fluidQuery.value !== selectedFluid.value) {
    return '请选择 CoolProp 支持的有效工质'
  }
  if (!isFiniteNumber(form.pressureValue) || Number(form.pressureValue) <= 0) {
    return '压力必须大于 0'
  }
  if (!isFiniteNumber(form.flowValue) || Number(form.flowValue) < 0) {
    return '流量不能为负数'
  }
  return ''
}

function buildCommonPayload(rows) {
  return {
    fluid: selectedFluid.value,
    pressure: {
      value: Number(form.pressureValue),
      unit: form.pressureUnit
    },
    flowRate: {
      value: Number(form.flowValue),
      unit: form.flowUnit
    },
    rows
  }
}

async function calculateCurrent() {
  if (mode.value === 'batch') {
    await calculateBatch()
    return
  }
  await calculateSingle()
}

async function calculateSingle() {
  errorMessage.value = ''
  successMessage.value = ''
  singleResult.value = null

  const validationError = validateSingleInput()
  if (validationError) {
    errorMessage.value = validationError
    return
  }

  isLoading.value = true
  try {
    const response = await calculateHeatDissipation(
      buildCommonPayload([
        {
          tinC: Number(form.tinC),
          toutC: Number(form.toutC)
        }
      ])
    )
    singleResult.value = response.data?.results?.[0] || null
  } catch (error) {
    errorMessage.value = getRequestErrorMessage(error)
  } finally {
    isLoading.value = false
  }
}

function buildBatchRows() {
  const commonError = validateCommonInput()
  if (commonError) {
    return { rows: [], error: commonError }
  }

  const tin = parseNumberList(batchTinText.value)
  if (tin.error) {
    return { rows: [], error: tin.error }
  }
  const tout = parseNumberList(batchToutText.value)
  if (tout.error) {
    return { rows: [], error: tout.error }
  }
  if (!tin.values.length || !tout.values.length) {
    return { rows: [], error: '请至少输入一组温度数据' }
  }
  if (tin.values.length !== tout.values.length) {
    return {
      rows: [],
      error: '入口温度和出口温度的数据数量不一致，请检查粘贴内容'
    }
  }

  return {
    rows: tin.values.map((tinC, index) => ({
      tinC,
      toutC: tout.values[index]
    })),
    error: ''
  }
}

async function calculateBatch() {
  errorMessage.value = ''
  successMessage.value = ''
  batchResults.value = []

  const { rows, error } = buildBatchRows()
  if (error) {
    errorMessage.value = error
    return
  }

  isLoading.value = true
  try {
    const response = await calculateHeatDissipation(buildCommonPayload(rows))
    batchResults.value = response.data?.results || []
  } catch (requestError) {
    errorMessage.value = getRequestErrorMessage(requestError)
  } finally {
    isLoading.value = false
  }
}

async function copyQColumn() {
  errorMessage.value = ''
  successMessage.value = ''
  if (!batchResults.value.length) {
    return
  }

  const text = batchResults.value.map(row => String(row.qW)).join('\n')
  try {
    await navigator.clipboard.writeText(text)
    successMessage.value = '已复制 Q 列'
  } catch (error) {
    errorMessage.value = '复制失败，请检查浏览器剪贴板权限'
  }
}

function escapeCsvCell(value) {
  const text = String(value ?? '')
  if (/[",\r\n]/.test(text)) {
    return `"${text.replace(/"/g, '""')}"`
  }
  return text
}

function exportCsv() {
  errorMessage.value = ''
  successMessage.value = ''
  if (!batchResults.value.length) {
    return
  }

  const header = ['index', 'Tin_C', 'Tout_C', 'Q_W']
  const lines = batchResults.value.map(row => [
    row.index,
    row.tinC,
    row.toutC,
    row.qW
  ].map(escapeCsvCell).join(','))
  const csv = [header.join(','), ...lines].join('\r\n')
  const blob = new Blob([`\uFEFF${csv}`], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `heat-dissipation-results-${new Date().toISOString().slice(0, 10)}.csv`
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
  successMessage.value = 'CSV 已导出'
}

watch(fluidQuery, value => {
  if (isSelectingFluid) {
    return
  }
  if (value !== selectedFluid.value) {
    selectedFluid.value = ''
  }
  showFluidSuggestions.value = true
  window.clearTimeout(fluidSearchTimer)
  fluidSearchTimer = window.setTimeout(() => {
    loadFluidSuggestions(value)
  }, 180)
})

onMounted(() => {
  loadFluidSuggestions()
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=VT323&family=Nunito:wght@400;600;700&display=swap');

.heat-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background:
    radial-gradient(circle at 14% 16%, rgba(255, 198, 233, 0.28), transparent 24%),
    radial-gradient(circle at 88% 10%, rgba(170, 226, 255, 0.28), transparent 26%),
    linear-gradient(180deg, #fbfcff 0%, #f8fbff 100%);
  color: #27334c;
  position: relative;
}

.heat-page::before {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  opacity: 0.16;
  background-image:
    linear-gradient(rgba(130, 150, 255, 0.08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(130, 150, 255, 0.08) 1px, transparent 1px);
  background-size: 24px 24px;
}

.heat-main {
  position: relative;
  z-index: 1;
  flex: 1;
  width: min(1260px, calc(100% - 32px));
  margin: 0 auto;
  padding: 2rem 0 4rem;
}

.heat-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.4rem;
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
  font-size: clamp(2.4rem, 5vw, 4rem);
  line-height: 0.95;
  letter-spacing: 0.05em;
  color: #283652;
}

.page-subtitle {
  margin: 0.9rem 0 0;
  max-width: 42ch;
  color: #64748e;
}

.back-link {
  min-height: 40px;
  display: inline-flex;
  align-items: center;
  padding: 0 0.9rem;
  border: 1px solid rgba(213, 220, 244, 0.95);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.72);
  color: #5060dc;
  font-weight: 700;
}

.workspace-shell {
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr) 280px;
  gap: 1rem;
  align-items: start;
}

.parameter-panel,
.input-panel,
.result-panel {
  padding: 1rem;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(222, 228, 255, 0.95);
  box-shadow: 0 14px 32px rgba(116, 132, 171, 0.08);
  backdrop-filter: blur(14px);
}

.panel-head {
  margin-bottom: 1rem;
}

.panel-title {
  margin: 0;
  font-family: 'VT323', monospace;
  font-size: 1.35rem;
  letter-spacing: 0.06em;
  color: #5f6de0;
}

.panel-note {
  margin: 0.2rem 0 0;
  color: #7a88a6;
  font-size: 0.9rem;
}

.field,
.field-row {
  display: grid;
  gap: 0.45rem;
}

.field-row {
  grid-template-columns: minmax(0, 1fr) 104px;
  margin-top: 0.8rem;
}

.field span {
  font-family: 'VT323', monospace;
  font-size: 1.05rem;
  color: #7b88a7;
  letter-spacing: 0.05em;
}

.field input,
.field select,
.field textarea {
  width: 100%;
  border: 1px solid rgba(213, 220, 244, 0.95);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.82);
  color: #2b3650;
  font-size: 0.95rem;
}

.field input,
.field select {
  height: 44px;
  padding: 0 0.8rem;
}

.field textarea {
  min-height: 170px;
  resize: vertical;
  padding: 0.75rem 0.8rem;
  line-height: 1.45;
  font-family: 'Nunito', sans-serif;
}

.field input:focus,
.field select:focus,
.field textarea:focus {
  outline: none;
  border-color: rgba(115, 131, 255, 0.72);
  box-shadow: 0 0 0 4px rgba(120, 136, 255, 0.12);
}

.field small {
  color: #2f9a70;
  font-size: 0.82rem;
}

.fluid-field {
  position: relative;
}

.fluid-menu {
  position: absolute;
  left: 0;
  right: 0;
  top: 70px;
  z-index: 5;
  max-height: 220px;
  overflow: auto;
  padding: 0.35rem;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(213, 220, 244, 0.95);
  box-shadow: 0 16px 34px rgba(116, 132, 171, 0.18);
}

.fluid-option {
  width: 100%;
  min-height: 34px;
  border: 0;
  border-radius: 6px;
  background: transparent;
  color: #394861;
  text-align: left;
  cursor: pointer;
  padding: 0 0.55rem;
}

.fluid-option:hover {
  background: #eef2ff;
  color: #4453d0;
}

.mode-strip {
  display: flex;
  gap: 0.7rem;
  margin-bottom: 1rem;
}

.mode-pill {
  min-height: 36px;
  display: inline-flex;
  align-items: center;
  padding: 0 0.9rem;
  border: 1px solid rgba(213, 220, 244, 0.95);
  border-radius: 8px;
  color: #61708d;
  background: rgba(255, 255, 255, 0.7);
}

.mode-pill--active {
  color: #4453d0;
  background: #eef2ff;
}

.mode-pill:disabled {
  opacity: 0.52;
}

.temperature-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.8rem;
}

.batch-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.8rem;
}

.row-count {
  grid-column: 1 / -1;
  margin: 0;
  color: #6f7f99;
  font-size: 0.9rem;
}

.submit-button {
  width: 100%;
  height: 46px;
  margin-top: 1rem;
  border: 0;
  border-radius: 8px;
  background: #5f6de0;
  color: #ffffff;
  font-family: 'VT323', monospace;
  font-size: 1.35rem;
  letter-spacing: 0.06em;
  cursor: pointer;
}

.submit-button:disabled {
  opacity: 0.68;
  cursor: wait;
}

.error-message {
  margin: 0.8rem 0 0;
  padding: 0.75rem 0.8rem;
  border-radius: 8px;
  background: rgba(255, 238, 244, 0.9);
  border: 1px solid rgba(255, 190, 210, 0.8);
  color: #ba345c;
}

.success-message {
  margin: 0;
  padding: 0.65rem 0.75rem;
  border-radius: 8px;
  background: rgba(226, 255, 241, 0.9);
  border: 1px solid rgba(174, 235, 207, 0.9);
  color: #24845f;
  font-size: 0.88rem;
}

.result-value {
  display: grid;
  gap: 0.35rem;
  place-items: center;
  min-height: 130px;
  margin-bottom: 1rem;
  border-radius: 8px;
  background: #f8faff;
  color: #5060dc;
  text-align: center;
}

.result-value span {
  font-family: 'VT323', monospace;
  font-size: 1.2rem;
  letter-spacing: 0.08em;
  color: #8794ad;
}

.result-value strong {
  font-family: 'VT323', monospace;
  font-size: 2.25rem;
  letter-spacing: 0.04em;
  color: #3d4ed1;
}

.result-value--empty strong {
  color: #9aa6bf;
}

.result-meta {
  display: grid;
  gap: 0.65rem;
}

.result-meta div {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.8rem;
  min-height: 42px;
  padding: 0 0.75rem;
  border-radius: 8px;
  background: rgba(248, 250, 255, 0.8);
}

.result-meta span {
  font-family: 'VT323', monospace;
  color: #7b88a7;
  font-size: 1.05rem;
}

.result-meta strong {
  color: #31405e;
  font-size: 0.9rem;
  text-align: right;
  word-break: break-word;
}

.batch-result {
  display: grid;
  gap: 0.75rem;
}

.batch-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.batch-summary {
  margin: 0;
  color: #6f7f99;
  font-size: 0.9rem;
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  justify-content: flex-end;
}

.action-buttons button {
  min-height: 34px;
  padding: 0 0.7rem;
  border-radius: 8px;
  border: 1px solid rgba(213, 220, 244, 0.95);
  background: rgba(255, 255, 255, 0.82);
  color: #5060dc;
  font-size: 0.86rem;
  font-weight: 700;
  cursor: pointer;
}

.action-buttons button:disabled {
  opacity: 0.48;
  cursor: not-allowed;
}

.result-table-wrap {
  max-height: 360px;
  overflow: auto;
  border: 1px solid rgba(222, 228, 255, 0.95);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.72);
}

.result-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 360px;
  font-size: 0.86rem;
}

.result-table th,
.result-table td {
  padding: 0.62rem 0.7rem;
  border-bottom: 1px solid rgba(226, 232, 248, 0.86);
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.result-table th:first-child,
.result-table td:first-child {
  text-align: left;
}

.result-table th {
  position: sticky;
  top: 0;
  z-index: 1;
  background: #f4f7ff;
  color: #657390;
  font-family: 'VT323', monospace;
  font-size: 1rem;
  letter-spacing: 0.04em;
}

.result-table tr:last-child td {
  border-bottom: 0;
}

@media (max-width: 1080px) {
  .workspace-shell {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .heat-main {
    width: min(100% - 24px, 1260px);
    padding: 1.4rem 0 3rem;
  }

  .heat-head {
    flex-direction: column;
  }

  .mode-strip {
    flex-wrap: wrap;
  }

  .temperature-grid,
  .batch-grid {
    grid-template-columns: 1fr;
  }

  .batch-actions {
    align-items: flex-start;
    flex-direction: column;
  }

  .action-buttons {
    justify-content: flex-start;
  }
}
</style>
