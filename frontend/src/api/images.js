import client from './client'

export const imagesApi = {
  /**
   * Google Custom Search API로 로고 검색
   * @param {string} query - 검색어
   * @param {number} limit - 최대 결과 개수
   * @param {number} offset - 시작 위치 (0부터 시작)
   */
  searchLogo(query, limit = 5, offset = 0) {
    return client.post('/images/search-logo', { query, limit, offset })
  },

  /**
   * Google Custom Search API로 스크린샷 검색
   * @param {string} query - 검색어
   * @param {number} limit - 최대 결과 개수
   * @param {number} offset - 시작 위치 (0부터 시작)
   */
  searchScreenshots(query, limit = 10, offset = 0) {
    return client.post('/images/search-screenshots', { query, limit, offset })
  },

  /**
   * 제품 로고 업로드
   * @param {number} productId - 제품 ID
   * @param {File} file - 업로드할 이미지 파일
   */
  uploadLogo(productId, file) {
    const formData = new FormData()
    formData.append('file', file)
    return client.post(`/images/upload-logo/${productId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  /**
   * 제품 스크린샷 업로드 (최대 10개)
   * @param {number} productId - 제품 ID
   * @param {File[]} files - 업로드할 이미지 파일 배열
   */
  uploadScreenshots(productId, files) {
    const formData = new FormData()
    files.forEach(file => formData.append('files', file))
    return client.post(`/images/upload-screenshots/${productId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  /**
   * URL에서 로고 다운로드 후 저장
   * @param {number} productId - 제품 ID
   * @param {string} url - 다운로드할 이미지 URL
   */
  downloadLogo(productId, url) {
    return client.post(`/images/download-logo/${productId}?url=${encodeURIComponent(url)}`)
  },

  /**
   * URL에서 스크린샷 다운로드 후 저장
   * @param {number} productId - 제품 ID
   * @param {string[]} urls - 다운로드할 이미지 URL 배열
   */
  downloadScreenshots(productId, urls) {
    const urlParams = urls.map(url => `urls=${encodeURIComponent(url)}`).join('&')
    return client.post(`/images/download-screenshots/${productId}?${urlParams}`)
  },

  /**
   * 제품 이미지 삭제
   * @param {number} productId - 제품 ID
   * @param {string} imageType - 'logo', 'screenshots', 'all'
   */
  deleteImages(productId, imageType = 'all') {
    return client.delete(`/images/${productId}?image_type=${imageType}`)
  },

  /**
   * 게시글 내용에서 외부 이미지를 찾아 로컬로 다운로드하고 URL 교체
   * @param {string} content - HTML 형식의 게시글 내용
   * @returns {Promise<{content: string, images: string[]}>}
   */
  processPostContent(content) {
    return client.post('/images/process-post-content', { content })
  }
}
