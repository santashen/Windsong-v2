import api from './index'

export const authApi = {
  // Verify API key
  verify(apiKey) {
    return api.post('/auth/verify', { apiKey })
  }
}
