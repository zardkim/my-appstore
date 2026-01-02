import apiClient from './client'

export const favoritesApi = {
  // 내 즐겨찾기 목록 조회
  async getMyFavorites() {
    return apiClient.get('favorites/')
  },

  // 즐겨찾기 추가
  async addFavorite(productId) {
    return apiClient.post(`favorites/${productId}`)
  },

  // 즐겨찾기 제거
  async removeFavorite(productId) {
    return apiClient.delete(`favorites/${productId}`)
  },

  // 즐겨찾기 여부 확인
  async checkFavorite(productId) {
    return apiClient.get(`favorites/check/${productId}`)
  }
}
