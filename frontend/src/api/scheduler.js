import apiClient from './client'

export const schedulerApi = {
  async getStatus() {
    return apiClient.get('/scheduler/status')
  },

  async start(config) {
    return apiClient.post('/scheduler/start', config)
  },

  async stop() {
    return apiClient.post('/scheduler/stop')
  },

  async runNow() {
    return apiClient.post('/scheduler/run-now')
  },

  async getConfig() {
    return apiClient.get('/scheduler/config')
  }
}
