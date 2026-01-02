import client from './client'

export const unmatchedApi = {
  /**
   * 불일치 항목 목록 조회
   * @param {string} status - 상태 필터 (pending, approved, manual, ignored)
   * @param {number} skip - 건너뛸 항목 수
   * @param {number} limit - 조회할 최대 항목 수
   * @returns {Promise}
   */
  async getList(status = null, skip = 0, limit = 50) {
    const params = { skip, limit }
    if (status) {
      params.status = status
    }
    return client.get('/unmatched/', { params })
  },

  /**
   * 불일치 항목 상세 조회
   * @param {number} id - 항목 ID
   * @returns {Promise}
   */
  async getDetail(id) {
    return client.get(`/unmatched/${id}`)
  },

  /**
   * AI 제안 승인
   * @param {number} id - 항목 ID
   * @returns {Promise}
   */
  async approve(id) {
    return client.post(`/unmatched/${id}/approve`)
  },

  /**
   * 수동 메타데이터 입력
   * @param {number} id - 항목 ID
   * @param {object} metadata - 메타데이터
   * @returns {Promise}
   */
  async saveManual(id, metadata) {
    return client.post(`/unmatched/${id}/manual`, metadata)
  },

  /**
   * 수동 검색 (AI 재쿼리)
   * @param {number} id - 항목 ID
   * @param {string} softwareName - 소프트웨어 이름
   * @param {boolean} collectExtended - 확장 메타데이터 수집 여부
   * @returns {Promise}
   */
  async search(id, softwareName, collectExtended = true) {
    return client.post(`/unmatched/${id}/search`, {
      software_name: softwareName,
      collect_extended: collectExtended
    })
  },

  /**
   * 항목 무시
   * @param {number} id - 항목 ID
   * @returns {Promise}
   */
  async ignore(id) {
    return client.delete(`/unmatched/${id}`)
  },

  /**
   * 통계 조회
   * @returns {Promise}
   */
  async getStats() {
    return client.get('/unmatched/stats/summary')
  }
}
