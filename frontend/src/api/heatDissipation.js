import axios from 'axios'

const heatDissipationApi = axios.create({
  baseURL: '/ai-api',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json'
  }
})

export function searchHeatDissipationFluids(query = '', limit = 20) {
  return heatDissipationApi.get('/heat-dissipation/fluids', {
    params: { query, limit }
  })
}

export function calculateHeatDissipation(payload) {
  return heatDissipationApi.post('/heat-dissipation/calculate', payload)
}
