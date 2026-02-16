<template>
  <div class="finance-page">
    <Header />

    <main class="finance-main">
      <div class="finance-container">
        <!-- Breadcrumb -->
        <div class="breadcrumb">
          <router-link to="/services">Services</router-link>
          <span class="separator">/</span>
          <span class="current">Finance</span>
        </div>

        <!-- Page Header -->
        <div class="page-header">
          <h1 class="page-title">Finance Data</h1>
          <p class="page-subtitle">Search and compare stocks & funds</p>
        </div>

        <!-- Search Section -->
        <div class="search-section">
          <div class="search-wrapper">
            <input
              v-model="searchKeyword"
              type="text"
              class="search-input"
              placeholder="Search by stock/fund name or code..."
              @input="onSearchInput"
              @focus="showDropdown = true"
            />
            <span v-if="store.isSearching" class="search-spinner"></span>
          </div>

          <!-- Search Results Dropdown -->
          <div v-if="showDropdown && store.searchResults.length" class="search-dropdown" ref="dropdownRef">
            <div
              v-for="item in store.searchResults"
              :key="item.code + item.type"
              class="dropdown-item"
              @mousedown.prevent="selectItem(item)"
            >
              <span class="item-code">{{ item.code }}</span>
              <span class="item-name">{{ item.name }}</span>
              <span class="item-type" :class="item.type">{{ item.type === 'stock' ? 'Stock' : 'Fund' }}</span>
            </div>
          </div>
        </div>

        <!-- Selected Items -->
        <div v-if="store.hasSelection" class="selected-section">
          <div class="section-label">Selected</div>
          <div class="chips">
            <span
              v-for="item in store.selectedItems"
              :key="item.code"
              class="chip"
              :class="item.type"
            >
              {{ item.name }} ({{ item.code }})
              <button class="chip-remove" @click="store.removeItem(item.code)">x</button>
            </span>
          </div>
        </div>

        <!-- Config Section -->
        <div v-if="store.hasSelection" class="config-section">
          <!-- Time Range -->
          <div class="config-group">
            <div class="section-label">Time Range</div>
            <div class="range-buttons">
              <button
                v-for="opt in store.timeRangeOptions"
                :key="opt.value"
                class="range-btn"
                :class="{ active: store.timeRange === opt.value }"
                @click="store.setTimeRange(opt.value)"
              >
                {{ opt.label }}
              </button>
            </div>
          </div>

          <!-- Fields -->
          <div class="config-group">
            <div class="section-label">Attributes</div>
            <div class="field-checks">
              <label
                v-for="field in store.availableFields"
                :key="field.key"
                class="field-label"
              >
                <input
                  type="checkbox"
                  :checked="store.selectedFields.includes(field.key)"
                  @change="store.toggleField(field.key)"
                />
                {{ field.label }}
              </label>
            </div>
          </div>

          <!-- Fetch Button -->
          <div class="config-actions">
            <button class="btn btn-primary" :disabled="store.isLoading" @click="store.fetchHistory()">
              {{ store.isLoading ? 'Loading...' : 'Query' }}
            </button>
          </div>
        </div>

        <!-- Error -->
        <div v-if="store.error" class="error-state">
          <p class="error-text">{{ store.error }}</p>
        </div>

        <!-- Chart -->
        <div v-if="store.hasChartData" class="chart-section">
          <div ref="chartRef" class="chart-container"></div>
        </div>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import { useFinanceStore } from '@/stores/finance'

const store = useFinanceStore()

const searchKeyword = ref('')
const showDropdown = ref(false)
const chartRef = ref(null)
const dropdownRef = ref(null)
let searchTimer = null
let chartInstance = null

const COLORS = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4', '#f97316']

function onSearchInput() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    store.searchSymbol(searchKeyword.value)
  }, 300)
}

function selectItem(item) {
  store.addItem(item)
  searchKeyword.value = ''
  showDropdown.value = false
}

// Close dropdown on outside click
function handleClickOutside(e) {
  if (dropdownRef.value && !dropdownRef.value.contains(e.target)) {
    showDropdown.value = false
  }
}

if (typeof document !== 'undefined') {
  document.addEventListener('click', handleClickOutside)
}

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})

// Watch chartData and selectedFields to render chart
watch(
  () => [store.chartData, store.selectedFields],
  () => {
    if (store.hasChartData) {
      nextTick(renderChart)
    }
  },
  { deep: true }
)

function renderChart() {
  if (!chartRef.value) return

  if (chartInstance) {
    chartInstance.dispose()
  }
  chartInstance = echarts.init(chartRef.value)

  const series = []
  const legendData = []
  let colorIdx = 0

  for (const item of store.chartData) {
    if (item.error) continue

    for (const field of store.selectedFields) {
      const values = item.data?.[field]
      if (!values || values.length === 0) continue

      const seriesName = store.chartData.length > 1
        ? `${item.name} - ${getFieldLabel(field, item.type)}`
        : getFieldLabel(field, item.type)

      legendData.push(seriesName)
      series.push({
        name: seriesName,
        type: 'line',
        data: item.dates.map((d, i) => [d, values[i]]),
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 2, color: COLORS[colorIdx % COLORS.length] },
        itemStyle: { color: COLORS[colorIdx % COLORS.length] },
      })
      colorIdx++
    }
  }

  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(0,0,0,0.75)',
      textStyle: { color: '#fff', fontSize: 12 },
    },
    legend: {
      data: legendData,
      bottom: 0,
      textStyle: { color: '#888' },
    },
    grid: {
      left: '3%',
      right: '3%',
      top: '5%',
      bottom: legendData.length > 3 ? '15%' : '10%',
      containLabel: true,
    },
    xAxis: {
      type: 'time',
      axisLine: { lineStyle: { color: '#ddd' } },
      axisLabel: { color: '#888' },
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      axisLabel: { color: '#888' },
      splitLine: { lineStyle: { color: '#eee' } },
    },
    series,
  }

  chartInstance.setOption(option)

  // Resize handler
  const resizeObserver = new ResizeObserver(() => {
    chartInstance?.resize()
  })
  resizeObserver.observe(chartRef.value)
}

function getFieldLabel(key, type) {
  const allFields = [...store.stockFields, ...store.fundFields]
  const found = allFields.find(f => f.key === key)
  return found ? found.label : key
}
</script>

<style scoped>
.finance-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-bg);
}

.finance-main {
  flex: 1;
  padding: 2rem 1rem 4rem;
}

.finance-container {
  max-width: 900px;
  margin: 0 auto;
}

/* Breadcrumb */
.breadcrumb {
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
}

.breadcrumb a {
  color: var(--color-primary);
  text-decoration: none;
}

.breadcrumb a:hover {
  text-decoration: underline;
}

.breadcrumb .separator {
  margin: 0 0.5rem;
  color: var(--color-text-secondary);
}

.breadcrumb .current {
  color: var(--color-text);
}

/* Page Header */
.page-header {
  text-align: center;
  margin-bottom: 2rem;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--color-text);
  margin: 0 0 0.5rem 0;
}

.page-subtitle {
  font-size: 1rem;
  color: var(--color-text-secondary);
  margin: 0;
}

/* Search */
.search-section {
  position: relative;
  margin-bottom: 1.5rem;
}

.search-wrapper {
  position: relative;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem;
  font-size: 1rem;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-bg);
  color: var(--color-text);
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.search-input:focus {
  border-color: var(--color-primary);
}

.search-spinner {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: translateY(-50%) rotate(360deg); }
}

.search-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  max-height: 300px;
  overflow-y: auto;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  margin-top: 4px;
  z-index: 100;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 1rem;
  cursor: pointer;
  transition: background 0.15s;
}

.dropdown-item:hover {
  background: var(--color-bg-secondary);
}

.item-code {
  font-weight: 600;
  color: var(--color-text);
  min-width: 70px;
}

.item-name {
  flex: 1;
  color: var(--color-text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-type {
  font-size: 0.75rem;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-weight: 600;
}

.item-type.stock {
  background: #dbeafe;
  color: #2563eb;
}

.item-type.fund {
  background: #d1fae5;
  color: #059669;
}

/* Selected Chips */
.selected-section {
  margin-bottom: 1.5rem;
}

.section-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin-bottom: 0.5rem;
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

.chip.stock {
  background: #dbeafe;
  color: #1d4ed8;
}

.chip.fund {
  background: #d1fae5;
  color: #047857;
}

.chip-remove {
  border: none;
  background: none;
  cursor: pointer;
  font-size: 0.8rem;
  color: inherit;
  opacity: 0.6;
  padding: 0;
  line-height: 1;
}

.chip-remove:hover {
  opacity: 1;
}

/* Config */
.config-section {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.config-group {
  margin-bottom: 1.25rem;
}

.config-group:last-of-type {
  margin-bottom: 0;
}

.range-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.range-btn {
  padding: 0.4rem 0.9rem;
  font-size: 0.85rem;
  font-weight: 500;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-bg);
  color: var(--color-text);
  cursor: pointer;
  transition: all 0.15s;
}

.range-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.range-btn.active {
  background: var(--color-primary);
  color: #fff;
  border-color: var(--color-primary);
}

.field-checks {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem 1.25rem;
}

.field-label {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.9rem;
  color: var(--color-text);
  cursor: pointer;
}

.config-actions {
  margin-top: 1.25rem;
  display: flex;
  justify-content: center;
}

/* Buttons */
.btn {
  padding: 0.6rem 1.5rem;
  font-size: 0.95rem;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  color: #fff;
  background: var(--color-primary);
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

/* Error */
.error-state {
  text-align: center;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
}

.error-text {
  color: #ef4444;
  margin: 0;
}

/* Chart */
.chart-section {
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 1.5rem;
}

.chart-container {
  width: 100%;
  height: 450px;
}

/* Responsive */
@media (max-width: 768px) {
  .page-title {
    font-size: 2rem;
  }

  .chart-container {
    height: 300px;
  }

  .range-buttons {
    gap: 0.35rem;
  }

  .range-btn {
    padding: 0.35rem 0.65rem;
    font-size: 0.8rem;
  }
}
</style>
