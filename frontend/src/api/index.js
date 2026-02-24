import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => config,
  error => Promise.reject(error)
)

// 响应拦截器 - 解包统一响应信封 { code, message, data }
api.interceptors.response.use(
  response => {
    const res = response.data
    if (res && typeof res === 'object' && 'code' in res) {
      if (res.code === 0) {
        response.data = res.data
        return response
      }
      const err = new Error(res.message || 'Request failed')
      err.code = res.code
      err.response = response
      return Promise.reject(err)
    }
    return response
  },
  error => Promise.reject(error)
)

// Gallery API
export const galleryApi = {
  // Get photos with pagination and filters
  getPhotos(params = {}) {
    return api.get('/photos', { params })
  },

  // Get single photo by ID
  getPhoto(id) {
    return api.get(`/photos/${id}`)
  },

  // Get filter options (years, locations, tags)
  getFilterOptions() {
    return api.get('/photos/filters')
  }
}

// Posts API
export const postsApi = {
  // Get posts with pagination and tag filter
  getPosts(params = {}) {
    return api.get('/posts', { params })
  },

  // Get single post by slug
  getPost(slug) {
    return api.get(`/posts/${slug}`)
  }
}

// Gold Analysis API
export const goldApi = {
  // Get today's gold analysis
  getTodayAnalysis() {
    return api.get('/gold/today', { timeout: 180000 }) // 3 min timeout for LLM
  }
}

// AI Service API (direct to Python ai-service)
const aiApi = axios.create({
  baseURL: '/ai-api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
})

// 响应拦截器 - 解包统一响应信封 { code, message, data }
aiApi.interceptors.response.use(
  response => {
    const res = response.data
    if (res && typeof res === 'object' && 'code' in res) {
      if (res.code === 0) {
        response.data = res.data
        return response
      }
      const err = new Error(res.message || 'Request failed')
      err.code = res.code
      err.response = response
      return Promise.reject(err)
    }
    return response
  },
  error => Promise.reject(error)
)

// Finance Data API
export const financeApi = {
  search(keyword) {
    return aiApi.get('/finance/search', { params: { keyword } })
  },
  getHistory(params) {
    return aiApi.get('/finance/history', { params })
  }
}

export default api
