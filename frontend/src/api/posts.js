import apiClient from './client'

export const postsApi = {
  // 게시글 목록 조회
  getPosts(params = {}) {
    return apiClient.get('/posts/', { params })
  },

  // 게시글 상세 조회
  getPost(id) {
    return apiClient.get(`/posts/${id}`)
  },

  // 게시글 작성
  createPost(data) {
    return apiClient.post('/posts/', data)
  },

  // 게시글 수정
  updatePost(id, data) {
    return apiClient.put(`/posts/${id}`, data)
  },

  // 게시글 삭제
  deletePost(id) {
    return apiClient.delete(`/posts/${id}`)
  },

  // 첨부파일 업로드
  uploadAttachment(file) {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.post('/posts/upload-attachment', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 첨부파일 다운로드 URL
  getAttachmentUrl(filename) {
    return `${apiClient.defaults.baseURL}/posts/download-attachment/${filename}`
  }
}
