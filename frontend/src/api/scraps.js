import apiClient from './client'

export const scrapsApi = {
  // 내 스크랩 목록 조회
  async getMyScraps() {
    return apiClient.get('scraps/')
  },

  // 스크랩 추가
  async addScrap(postId, postTitle = null) {
    return apiClient.post(`scraps/${postId}`, null, {
      params: { post_title: postTitle }
    })
  },

  // 스크랩 제거
  async removeScrap(postId) {
    return apiClient.delete(`scraps/${postId}`)
  },

  // 스크랩 여부 확인
  async checkScrap(postId) {
    return apiClient.get(`scraps/check/${postId}`)
  }
}
