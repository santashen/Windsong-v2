import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const familyPortfolioApi = axios.create({
  baseURL: '/ai-api/family-portfolio',
  timeout: 20000,
  headers: {
    'Content-Type': 'application/json'
  }
})

function getAuthHeaders() {
  const authStore = useAuthStore()
  return authStore.apiKey
    ? {
        'X-API-Key': authStore.apiKey
      }
    : {}
}

export const portfolioApi = {
  listPortfolios() {
    return familyPortfolioApi.get('/portfolios')
  },
  getPortfolioDetail(portfolioId) {
    return familyPortfolioApi.get(`/portfolios/${portfolioId}`)
  },
  listAssets() {
    return familyPortfolioApi.get('/assets')
  }
}

export const adminPortfolioApi = {
  listPortfolios() {
    return familyPortfolioApi.get('/portfolios')
  },
  getPortfolioDetail(id) {
    return familyPortfolioApi.get(`/portfolios/${id}`)
  },
  createPortfolio(data) {
    return familyPortfolioApi.post('/portfolios', data, { headers: getAuthHeaders() })
  },
  updatePortfolio(id, data) {
    return familyPortfolioApi.put(`/portfolios/${id}`, data, { headers: getAuthHeaders() })
  },
  deletePortfolio(id) {
    return familyPortfolioApi.delete(`/portfolios/${id}`, { headers: getAuthHeaders() })
  },
  listAssets() {
    return familyPortfolioApi.get('/assets')
  },
  createAsset(data) {
    return familyPortfolioApi.post('/assets', data, { headers: getAuthHeaders() })
  },
  updateAsset(id, data) {
    return familyPortfolioApi.put(`/assets/${id}`, data, { headers: getAuthHeaders() })
  },
  deleteAsset(id) {
    return familyPortfolioApi.delete(`/assets/${id}`, { headers: getAuthHeaders() })
  },
  createHolding(data) {
    return familyPortfolioApi.post('/holdings', data, { headers: getAuthHeaders() })
  },
  updateHolding(id, data) {
    return familyPortfolioApi.put(`/holdings/${id}`, data, { headers: getAuthHeaders() })
  },
  deleteHolding(id) {
    return familyPortfolioApi.delete(`/holdings/${id}`, { headers: getAuthHeaders() })
  },
  createInvestmentThesis(data) {
    return familyPortfolioApi.post('/investment-theses', data, { headers: getAuthHeaders() })
  },
  updateInvestmentThesis(id, data) {
    return familyPortfolioApi.put(`/investment-theses/${id}`, data, { headers: getAuthHeaders() })
  },
  deleteInvestmentThesis(id) {
    return familyPortfolioApi.delete(`/investment-theses/${id}`, { headers: getAuthHeaders() })
  },
  createPerformanceHistory(data) {
    return familyPortfolioApi.post('/performance-history', data, { headers: getAuthHeaders() })
  },
  updatePerformanceHistory(id, data) {
    return familyPortfolioApi.put(`/performance-history/${id}`, data, { headers: getAuthHeaders() })
  },
  deletePerformanceHistory(id) {
    return familyPortfolioApi.delete(`/performance-history/${id}`, { headers: getAuthHeaders() })
  }
}
