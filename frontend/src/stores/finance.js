import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { financeApi } from '@/api'

export const useFinanceStore = defineStore('finance', () => {
  // State
  const searchResults = ref([])
  const selectedItems = ref([])
  const chartData = ref([])
  const isSearching = ref(false)
  const isLoading = ref(false)
  const error = ref(null)
  const timeRange = ref('1y')
  const selectedFields = ref(['close'])

  // Time range presets
  const timeRangeOptions = [
    { label: '1月', value: '1m' },
    { label: '3月', value: '3m' },
    { label: '6月', value: '6m' },
    { label: '1年', value: '1y' },
    { label: '3年', value: '3y' },
    { label: '全部', value: 'all' },
  ]

  // Field options by type
  const stockFields = [
    { key: 'close', label: '收盘价' },
    { key: 'open', label: '开盘价' },
    { key: 'high', label: '最高价' },
    { key: 'low', label: '最低价' },
    { key: 'volume', label: '成交量' },
    { key: 'turnover_rate', label: '换手率' },
  ]

  const fundFields = [
    { key: 'nav', label: '单位净值' },
    { key: 'cum_nav', label: '累计净值' },
    { key: 'daily_return', label: '日增长率(%)' },
  ]

  // Getters
  const hasSelection = computed(() => selectedItems.value.length > 0)
  const hasChartData = computed(() => chartData.value.length > 0)
  const hasMultipleTypes = computed(() => {
    const types = new Set(selectedItems.value.map(i => i.type))
    return types.size > 1
  })
  const availableFields = computed(() => {
    const types = new Set(selectedItems.value.map(i => i.type))
    if (types.has('stock') && types.has('fund')) {
      return [...stockFields, ...fundFields]
    }
    if (types.has('fund')) return fundFields
    return stockFields
  })

  // Actions
  function getDateRange() {
    const end = new Date()
    const start = new Date()
    switch (timeRange.value) {
      case '1m': start.setMonth(start.getMonth() - 1); break
      case '3m': start.setMonth(start.getMonth() - 3); break
      case '6m': start.setMonth(start.getMonth() - 6); break
      case '1y': start.setFullYear(start.getFullYear() - 1); break
      case '3y': start.setFullYear(start.getFullYear() - 3); break
      case 'all': start.setFullYear(2000); break
    }
    return {
      start: start.toISOString().slice(0, 10),
      end: end.toISOString().slice(0, 10),
    }
  }

  async function searchSymbol(keyword) {
    if (!keyword || keyword.trim().length === 0) {
      searchResults.value = []
      return
    }
    isSearching.value = true
    try {
      const res = await financeApi.search(keyword)
      searchResults.value = res.data.results || []
    } catch (err) {
      console.error('Search failed:', err)
      searchResults.value = []
    } finally {
      isSearching.value = false
    }
  }

  function addItem(item) {
    if (selectedItems.value.some(i => i.code === item.code && i.type === item.type)) return
    selectedItems.value.push({ ...item })
    searchResults.value = []

    // Reset fields to defaults for the current type mix
    const types = new Set(selectedItems.value.map(i => i.type))
    if (types.size === 1) {
      const firstType = [...types][0]
      selectedFields.value = [firstType === 'fund' ? 'nav' : 'close']
    }
  }

  function removeItem(code) {
    selectedItems.value = selectedItems.value.filter(i => i.code !== code)
    if (selectedItems.value.length === 0) {
      chartData.value = []
      selectedFields.value = ['close']
    }
  }

  function setTimeRange(range) {
    timeRange.value = range
  }

  function toggleField(field) {
    const idx = selectedFields.value.indexOf(field)
    if (idx >= 0) {
      if (selectedFields.value.length > 1) {
        selectedFields.value.splice(idx, 1)
      }
    } else {
      selectedFields.value.push(field)
    }
  }

  async function fetchHistory() {
    if (!hasSelection.value) return

    isLoading.value = true
    error.value = null

    try {
      const { start, end } = getDateRange()

      // Group by type and fetch
      const stockCodes = selectedItems.value.filter(i => i.type === 'stock').map(i => i.code)
      const fundCodes = selectedItems.value.filter(i => i.type === 'fund').map(i => i.code)

      const requests = []
      if (stockCodes.length) {
        requests.push(financeApi.getHistory({
          codes: stockCodes.join(','),
          type: 'stock',
          start,
          end,
        }))
      }
      if (fundCodes.length) {
        requests.push(financeApi.getHistory({
          codes: fundCodes.join(','),
          type: 'fund',
          start,
          end,
        }))
      }

      const responses = await Promise.all(requests)
      const allResults = responses.flatMap(r => r.data.results || [])

      // Attach name from selectedItems
      chartData.value = allResults.map(d => {
        const item = selectedItems.value.find(i => i.code === d.code)
        return { ...d, name: item?.name || d.code }
      })
    } catch (err) {
      error.value = err.message || 'Failed to fetch data'
      console.error('Fetch history error:', err)
    } finally {
      isLoading.value = false
    }
  }

  return {
    // State
    searchResults,
    selectedItems,
    chartData,
    isSearching,
    isLoading,
    error,
    timeRange,
    selectedFields,
    // Constants
    timeRangeOptions,
    stockFields,
    fundFields,
    // Getters
    hasSelection,
    hasChartData,
    hasMultipleTypes,
    availableFields,
    // Actions
    searchSymbol,
    addItem,
    removeItem,
    setTimeRange,
    toggleField,
    fetchHistory,
  }
})
