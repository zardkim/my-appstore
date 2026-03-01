import client from './client'

export const productVideosApi = {
  getVideos: (productId) =>
    client.get(`/product-videos/${productId}`),

  upload: (productId, formData, onProgress) =>
    client.post(`/product-videos/upload/${productId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => {
        if (onProgress && e.total) {
          onProgress(Math.round((e.loaded * 100) / e.total))
        }
      },
    }),

  update: (videoId, data) =>
    client.patch(`/product-videos/${videoId}`, data),

  delete: (videoId) =>
    client.delete(`/product-videos/${videoId}`),
}
