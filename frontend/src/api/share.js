import apiClient from './client'
import axios from 'axios'

function getApiBaseUrl() {
  const envUrl = import.meta.env.VITE_API_BASE_URL
  if (envUrl && (envUrl.startsWith('http://') || envUrl.startsWith('https://'))) return envUrl
  if (envUrl && envUrl.startsWith('/')) return envUrl
  return '/api'
}

// 비인증 axios 인스턴스 (공유 페이지 접근용)
const publicClient = axios.create({
  baseURL: getApiBaseUrl(),
  headers: { 'Content-Type': 'application/json' },
})

export const shareApi = {
  // 공유링크 생성 (인증 필요)
  async create(productId, expiresDays, note = '') {
    return apiClient.post('/share/create', {
      product_id: productId,
      expires_days: expiresDays,
      note,
    })
  },

  // 내 공유링크 목록 (인증 필요)
  async getMyLinks(page = 1, limit = 20, statusFilter = null) {
    const params = { page, limit }
    if (statusFilter) params.status_filter = statusFilter
    return apiClient.get('/share/my-links', { params })
  },

  // 공유링크 삭제 (인증 필요)
  async deleteLink(linkId) {
    return apiClient.delete(`/share/${linkId}`)
  },

  // 공유 페이지 정보 조회 (비인증)
  async viewShare(token) {
    return publicClient.get(`/share/view/${token}`)
  },

  // 공유링크 비밀번호 인증 및 제품 정보 반환 (비인증)
  async accessShare(token, password) {
    return publicClient.post(`/share/access/${token}`, { password })
  },

  // 관리자 전체 목록 (인증 필요)
  async adminGetAll(page = 1, limit = 20) {
    return apiClient.get('/share/admin/all', { params: { page, limit } })
  },
}
