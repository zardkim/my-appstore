import client from './client'

/**
 * 패치 파일 업로드
 * @param {number} productId - 제품 ID
 * @param {File} file - 업로드할 파일
 * @param {string} note - 파일 설명 (선택)
 * @param {string} type - 파일 타입 (patch, crack, manual 등)
 */
export const uploadAttachment = async (productId, file, note = '', type = 'patch') => {
  const formData = new FormData()
  formData.append('product_id', productId)
  formData.append('file', file)
  if (note) formData.append('note', note)
  formData.append('type', type)

  const response = await client.post('/attachments/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  return response.data
}

/**
 * 제품의 패치 파일 목록 조회
 * @param {number} productId - 제품 ID
 * @param {string} type - 파일 타입 필터 (선택)
 */
export const getProductAttachments = async (productId, type = null) => {
  const params = type ? { type } : {}
  const response = await client.get(`/attachments/product/${productId}`, { params })
  return response.data
}

/**
 * 패치 파일 다운로드
 * @param {number} attachmentId - 첨부파일 ID
 */
export const downloadAttachment = async (attachmentId) => {
  const response = await client.get(`/attachments/download/${attachmentId}`, {
    responseType: 'blob'
  })
  return response
}

/**
 * 패치 파일 정보 수정 (노트만)
 * @param {number} attachmentId - 첨부파일 ID
 * @param {string} note - 수정할 노트
 */
export const updateAttachment = async (attachmentId, note) => {
  const response = await client.patch(`/attachments/${attachmentId}`, { note })
  return response.data
}

/**
 * 패치 파일 삭제
 * @param {number} attachmentId - 첨부파일 ID
 */
export const deleteAttachment = async (attachmentId) => {
  const response = await client.delete(`/attachments/${attachmentId}`)
  return response.data
}

export default {
  uploadAttachment,
  getProductAttachments,
  downloadAttachment,
  updateAttachment,
  deleteAttachment
}
