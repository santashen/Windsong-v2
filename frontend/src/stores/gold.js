import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { goldApi } from '@/api'

export const useGoldStore = defineStore('gold', () => {
  // State
  const analysis = ref(null)
  const isLoading = ref(false)
  const error = ref(null)

  // Getters
  const hasAnalysis = computed(() => analysis.value !== null)
  const analysisDate = computed(() => {
    if (!analysis.value?.analysisDate) return ''
    return new Date(analysis.value.analysisDate).toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  })

  // Actions
  async function fetchTodayAnalysis() {
    isLoading.value = true
    error.value = null

    try {
      const response = await goldApi.getTodayAnalysis()
      analysis.value = response.data
    } catch (err) {
      error.value = err.message || 'Failed to fetch analysis'
      console.error('Error fetching gold analysis:', err)
    } finally {
      isLoading.value = false
    }
  }

  function clearError() {
    error.value = null
  }

  return {
    // State
    analysis,
    isLoading,
    error,
    // Getters
    hasAnalysis,
    analysisDate,
    // Actions
    fetchTodayAnalysis,
    clearError
  }
})
