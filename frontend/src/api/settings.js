import apiClient from './client'

export const settingsApi = {
  /**
   * 모든 설정 가져오기 (config API 사용)
   */
  async get() {
    return apiClient.get('/config')
  },

  /**
   * 설정 업데이트 (config API 사용)
   * @param {Object} settings - 설정 객체
   */
  async update(settings) {
    return apiClient.put('/config', settings)
  },

  /**
   * 특정 섹션의 설정값 가져오기
   * @param {string} section - 설정 섹션
   */
  async getSection(section) {
    return apiClient.get(`/config/${section}`)
  },

  /**
   * 특정 섹션의 설정값 업데이트
   * @param {string} section - 설정 섹션
   * @param {any} value - 설정 값
   */
  async updateSection(section, value) {
    return apiClient.put(`/config/${section}`, value)
  }
}
