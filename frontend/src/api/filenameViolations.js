import client from './client'

export const filenameViolationsApi = {
  /**
   * 파일명 규칙 위반 목록 조회
   * @param {boolean} resolved - true면 해결된 항목만, false면 미해결 항목만
   */
  getViolations(resolved = false) {
    return client.get('/filename-violations/', { params: { resolved } })
  },

  /**
   * 파일명 규칙 위반 통계 조회
   */
  getStats() {
    return client.get('/filename-violations/stats')
  },

  /**
   * 위반 항목을 해결됨으로 표시
   * @param {number} violationId - Violation ID
   */
  resolveViolation(violationId) {
    return client.put(`/filename-violations/${violationId}/resolve`)
  },

  /**
   * 위반 항목 삭제
   * @param {number} violationId - Violation ID
   */
  deleteViolation(violationId) {
    return client.delete(`/filename-violations/${violationId}`)
  },

  /**
   * 위반 항목 일괄 삭제
   * @param {boolean} resolvedOnly - true면 해결된 항목만 삭제, false면 전체 삭제
   */
  clearViolations(resolvedOnly = true) {
    return client.delete('/filename-violations/', { params: { resolved_only: resolvedOnly } })
  },

  /**
   * 파일명 변경
   * @param {number} violationId - Violation ID
   * @param {string} newFilename - 새로운 파일명
   */
  renameFile(violationId, newFilename) {
    return client.put(`/filename-violations/${violationId}/rename`, {
      new_filename: newFilename
    })
  },

  /**
   * 제안된 파일명으로 일괄 변경
   * @param {number[]} violationIds - Violation ID 목록
   */
  batchRename(violationIds) {
    return client.post('/filename-violations/batch-rename', {
      violation_ids: violationIds
    })
  },

  /**
   * 스캔된 파일로부터 Product 생성 (AI 매칭)
   * @param {number} violationId - Violation ID
   */
  createProduct(violationId) {
    return client.post(`/filename-violations/${violationId}/create-product`)
  }
}
