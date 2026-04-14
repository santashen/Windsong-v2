import axios from 'axios'

const valuationApi = axios.create({
  baseURL: '/ai-api',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json'
  }
})

export function getValuationBacktest(params) {
  return valuationApi.get('/valuation-backtest', { params })
}
