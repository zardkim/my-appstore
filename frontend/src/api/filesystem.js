import client from './client'

/**
 * 파일시스템 관련 API
 */
export const filesystemApi = {
  /**
   * 폴더 탐색
   * @param {string} path - 탐색할 경로
   */
  browse(path = '/library') {
    return client.get('filesystem/browse', {
      params: { path }
    })
  },

  /**
   * 디렉토리 생성
   * @param {string} path - 생성할 디렉토리 경로
   */
  createDirectory(path) {
    return client.post('filesystem/create-directory', null, {
      params: { path }
    })
  }
}
