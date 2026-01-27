import api from '../index'
import { useAuthStore } from '@/stores/auth'

// Helper to get auth headers
const getAuthHeaders = () => {
  const authStore = useAuthStore()
  return {
    'X-API-Key': authStore.apiKey
  }
}

export const adminPhotoApi = {
  // Get photos with pagination
  getPhotos(params = {}) {
    return api.get('/photos', {
      params,
      headers: getAuthHeaders()
    })
  },

  // Get single photo
  getPhoto(id) {
    return api.get(`/photos/${id}`, {
      headers: getAuthHeaders()
    })
  },

  // Create photo
  createPhoto(data) {
    return api.post('/photos', data, {
      headers: getAuthHeaders()
    })
  },

  // Update photo
  updatePhoto(id, data) {
    return api.put(`/photos/${id}`, data, {
      headers: getAuthHeaders()
    })
  },

  // Delete photo
  deletePhoto(id) {
    return api.delete(`/photos/${id}`, {
      headers: getAuthHeaders()
    })
  },

  // Get filter options
  getFilterOptions() {
    return api.get('/photos/filters', {
      headers: getAuthHeaders()
    })
  }
}
