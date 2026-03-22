import api from './index'
import { useAuthStore } from '@/stores/auth'

const PORTFOLIO_STORAGE_KEY = 'portfolio_access_password'

function getPortfolioPassword() {
  return sessionStorage.getItem(PORTFOLIO_STORAGE_KEY) || ''
}

function getPortfolioHeaders() {
  const password = getPortfolioPassword()
  return password ? { 'X-Portfolio-Password': password } : {}
}

function getAdminHeaders() {
  const authStore = useAuthStore()
  return {
    'X-API-Key': authStore.apiKey
  }
}

export const portfolioStorage = {
  key: PORTFOLIO_STORAGE_KEY,
  getPassword: getPortfolioPassword,
  setPassword(password) {
    sessionStorage.setItem(PORTFOLIO_STORAGE_KEY, password)
  },
  clearPassword() {
    sessionStorage.removeItem(PORTFOLIO_STORAGE_KEY)
  }
}

export const portfolioApi = {
  verifyAccess(password) {
    return api.post('/portfolio/access/verify', { password })
  },

  getLatestSnapshot() {
    return api.get('/portfolio/latest', {
      headers: getPortfolioHeaders()
    })
  }
}

export const adminPortfolioApi = {
  createSnapshot(data) {
    return api.post('/portfolio/snapshots', data, {
      headers: getAdminHeaders()
    })
  }
}
