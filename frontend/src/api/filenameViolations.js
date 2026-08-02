import client from './client'

export const filenameViolationsApi = {
  /**
   * 스캔 항목 목록 조회 (신규 API)
   */
  getScanItems(params = {}) {
    return client.get('/scan-items/', { params })
  },

  /**
   * 스캔 항목 통계 (신규 API)
   */
  getScanStats() {
    return client.get('/scan-items/stats')
  },

  /**
   * 분류 수동 변경 (신규 API)
   * @param {number} id - Scan item ID
   * @param {string} classification - product|patch|language_pack|manual|update
   */
  classifyItem(id, classification) {
    return client.patch(`/scan-items/${id}/classify`, { classification })
  },

  /**
   * 스캔 항목 등록 (신규 API)
   * - product 분류: AI 매칭으로 제품 등록
   * - 나머지: 지정 제품의 Attachment로 등록 (product_id 필수)
   * @param {number} id - Scan item ID
   * @param {object} data - { product_id?: number, note?: string }
   */
  registerScanItem(id, data = {}) {
    return client.post(`/scan-items/${id}/register`, data)
  },

  /**
   * 첨부파일로 등록 (patch/language_pack/manual/update)
   * @param {number} id - Scan item ID
   * @param {number} productId - 연결할 제품 ID
   * @param {string} classification - 분류 (현재 item.classification 값 사용)
   * @param {string} note - 메모 (선택)
   */
  registerAsAttachment(id, productId, classification, note = '') {
    return client.post(`/scan-items/${id}/register`, {
      product_id: productId,
      note: note || undefined
    })
  },

  /**
   * 스캔 항목 삭제
   */
  deleteViolation(violationId) {
    return client.delete(`/filename-violations/${violationId}`)
  },

  /**
   * 파일명 변경
   */
  renameFile(violationId, newFilename) {
    return client.put(`/filename-violations/${violationId}/rename`, {
      new_filename: newFilename
    })
  },

  /**
   * 제안된 파일명으로 일괄 변경
   */
  batchRename(violationIds) {
    return client.post('/filename-violations/batch-rename', {
      violation_ids: violationIds
    })
  },

  /**
   * 선택한 항목들을 일괄 삭제
   */
  batchDelete(violationIds) {
    return client.post('/filename-violations/batch-delete', {
      violation_ids: violationIds
    })
  },

  /**
   * 스캔된 파일로부터 Product 생성 (AI 매칭)
   */
  createProduct(violationId) {
    return client.post(`/filename-violations/${violationId}/create-product`)
  },

  /**
   * 스캔된 파일로부터 AI 메타데이터와 함께 Product 생성
   */
  createProductWithMetadata(violationId, metadata) {
    return client.post(`/filename-violations/${violationId}/create-product-with-metadata`, {
      metadata: metadata
    })
  },

  /**
   * 스캔된 파일을 기존 제품의 버전으로 추가
   */
  addToProduct(violationId, productId) {
    return client.post(`/filename-violations/${violationId}/add-to-product`, {
      product_id: productId
    })
  },

  /**
   * AI 검색 전 중복 제품 검사 (백엔드 매칭 로직 동일)
   * @param {number} violationId - Scan item ID
   */
  findSimilarProducts(violationId) {
    return client.get(`/scan-items/${violationId}/find-similar`)
  },

  /**
   * 스캔 항목 폴더에서 재활용 가능한 설명 파일(readme.txt, *.nfo, *.md 등) 조회
   * @param {number} violationId - Scan item ID
   */
  getDescriptionFiles(violationId) {
    return client.get(`/scan-items/${violationId}/description-files`)
  },

  /**
   * URL/업로드 파일/스캔 폴더 내 설명 파일의 원문만 근거로 메타데이터 생성
   * @param {number} violationId - Scan item ID
   * @param {object} source - { url?: string, file?: File, descriptionFilePath?: string } 중 하나만
   */
  generateMetadataFromSource(violationId, source) {
    const formData = new FormData()
    if (source.url) formData.append('url', source.url)
    if (source.file) formData.append('file', source.file)
    if (source.descriptionFilePath) formData.append('description_file_path', source.descriptionFilePath)
    return client.post(`/scan-items/${violationId}/generate-metadata-from-source`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}
