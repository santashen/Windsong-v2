import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useMonitorStore = defineStore('monitor', () => {
  const chartConfigs = ref([])
  const isRunning = ref(false)
  let nextId = 1

  const hasConfigs = computed(() => chartConfigs.value.length > 0)

  function addConfig() {
    chartConfigs.value.push({
      id: nextId++,
      title: `Chart ${chartConfigs.value.length + 1}`,
      xAxisName: 'Time',
      yAxisName: 'Value',
      yMin: -1,
      yMax: 1,
      timeWindow: 10
    })
  }

  function removeConfig(id) {
    chartConfigs.value = chartConfigs.value.filter(c => c.id !== id)
  }

  function updateConfig(id, updates) {
    const config = chartConfigs.value.find(c => c.id === id)
    if (config) Object.assign(config, updates)
  }

  function startMonitoring() {
    if (chartConfigs.value.length > 0) isRunning.value = true
  }

  function stopMonitoring() {
    isRunning.value = false
  }

  return {
    chartConfigs,
    isRunning,
    hasConfigs,
    addConfig,
    removeConfig,
    updateConfig,
    startMonitoring,
    stopMonitoring
  }
})
