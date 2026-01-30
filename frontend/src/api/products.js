import apiClient from './client'

export const productsApi = {
  async getAll(params = {}) {
    return apiClient.get('/products/', { params })
  },

  async getRecent(limit = 10) {
    return apiClient.get('/products/recent', { params: { limit } })
  },

  async getById(id) {
    return apiClient.get(`/products/${id}`)
  },

  async getStats() {
    return apiClient.get('/products/stats/overview')
  },

  async getByCategory() {
    return apiClient.get('/products/by-category')
  },

  async search(query) {
    return apiClient.get('/products/', { params: { search: query } })
  },

  async getSearchSuggestions(query) {
    return apiClient.get('/products/search/suggestions', { params: { q: query } })
  },

  async getCategoryStats() {
    return apiClient.get('/products/stats/categories')
  },

  async updateProduct(id, data) {
    return apiClient.put(`/products/${id}`, data)
  },

  async updateVersion(productId, versionId, data) {
    return apiClient.put(`/products/${productId}/versions/${versionId}`, data)
  },

  async regenerateMetadata(productId) {
    return apiClient.post(`/products/${productId}/regenerate-metadata`)
  },

  async cleanupDeleted() {
    return apiClient.post('/products/cleanup-deleted')
  },

  async deleteProduct(id) {
    return apiClient.delete(`/products/${id}`)
  }
}
