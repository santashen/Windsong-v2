import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { authApi } from '@/api/auth'

const STORAGE_KEY = 'admin_api_key'

export const useAuthStore = defineStore('auth', () => {
  // State
  const apiKey = ref(localStorage.getItem(STORAGE_KEY) || null)
  const isAuthenticated = ref(false)
  const isLoading = ref(false)
  const error = ref(null)

  // Getters
  const hasStoredKey = computed(() => !!apiKey.value)

  // Actions
  async function initAuth() {
    if (!apiKey.value) {
      isAuthenticated.value = false
      return false
    }

    isLoading.value = true
    try {
      const response = await authApi.verify(apiKey.value)
      isAuthenticated.value = response.data.valid
      if (!isAuthenticated.value) {
        clearAuth()
      }
      return isAuthenticated.value
    } catch (err) {
      clearAuth()
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function login(key) {
    isLoading.value = true
    error.value = null

    try {
      const response = await authApi.verify(key)
      if (response.data.valid) {
        apiKey.value = key
        isAuthenticated.value = true
        localStorage.setItem(STORAGE_KEY, key)
        return true
      } else {
        error.value = response.data.message || 'Invalid API key'
        return false
      }
    } catch (err) {
      if (err.response?.status === 401) {
        error.value = err.response?.data?.message || 'Invalid API key'
      } else {
        error.value = 'Authentication failed. Please try again.'
      }
      return false
    } finally {
      isLoading.value = false
    }
  }

  function logout() {
    clearAuth()
  }

  function clearAuth() {
    apiKey.value = null
    isAuthenticated.value = false
    error.value = null
    localStorage.removeItem(STORAGE_KEY)
  }

  return {
    // State
    apiKey,
    isAuthenticated,
    isLoading,
    error,
    // Getters
    hasStoredKey,
    // Actions
    initAuth,
    login,
    logout,
    clearAuth
  }
})
