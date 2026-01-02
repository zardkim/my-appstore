import apiClient from './client'

export const scanApi = {
  async startScan(path, useAI = true) {
    return apiClient.post('scan/start', { path, use_ai: useAI })
  },

  async regenerateMetadata(productId) {
    return apiClient.post(`scan/regenerate-metadata/${productId}`)
  },

  async getScanExclusions() {
    return apiClient.get('scan/exclusions')
  },

  async saveScanExclusions(exclusions) {
    return apiClient.post('scan/exclusions', { exclusions })
  }
}
