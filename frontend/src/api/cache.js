import client from './client'

export const cacheApi = {
  // 캐쉬 통계 조회
  getStats() {
    return client.get('/cache/stats')
  },

  // 캐쉬 키 목록 조회
  getKeys(pattern = '*', limit = 100) {
    return client.get('/cache/keys', {
      params: { pattern, limit }
    })
  },

  // 캐쉬 삭제
  clearCache(pattern = '*') {
    return client.post('/cache/clear', { pattern })
  }
}
