import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
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

// 响应拦截器
api.interceptors.response.use(
  response => response,
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

export default api
