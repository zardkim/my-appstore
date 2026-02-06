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

  async saveScanExclusions(data) {
    return apiClient.post('scan/exclusions', data)
  },

  async addScanExclusion(pattern, type) {
    return apiClient.post('scan/exclusions/add', { pattern, type })
  },

  async getScanInfo() {
    return apiClient.get('scan/scan-info')
  },

  async previewScan(path, limit = 100) {
    return apiClient.get('scan/preview', { params: { path, limit } })
  },

  async testAiApi() {
    return apiClient.get('scan/test-api')
  }
}
