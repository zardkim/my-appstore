import client from './client'

export const commentsApi = {
  // 댓글 목록 조회
  getComments(postId) {
    return client.get(`/posts/${postId}/comments`)
  },

  // 댓글 작성
  createComment(postId, content) {
    return client.post(`/posts/${postId}/comments`, { content })
  },

  // 댓글 수정
  updateComment(commentId, content) {
    return client.put(`/posts/comments/${commentId}`, { content })
  },

  // 댓글 삭제
  deleteComment(commentId) {
    return client.delete(`/posts/comments/${commentId}`)
  }
}
