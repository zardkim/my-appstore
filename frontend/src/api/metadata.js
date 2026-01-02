import client from './client'

export const metadataApi = {
  /**
   * 메타데이터 생성 테스트
   * @param {string} softwareName - 소프트웨어 이름
   * @param {Object} settings - 메타데이터 설정 (aiProvider, aiModel, geminiApiKey, openaiApiKey)
   * @returns {Promise}
   */
  async testGeneration(softwareName, settings = null) {
    const requestData = {
      software_name: softwareName
    }

    // 설정이 제공된 경우 추가
    if (settings) {
      if (settings.aiProvider) requestData.ai_provider = settings.aiProvider
      if (settings.aiModel) requestData.ai_model = settings.aiModel
      if (settings.geminiApiKey) requestData.gemini_api_key = settings.geminiApiKey
      if (settings.openaiApiKey) requestData.openai_api_key = settings.openaiApiKey
    }

    return client.post('/metadata/test', requestData)
  },

  /**
   * 선택된 메타데이터로 Product 등록
   * @param {Object} metadata - 메타데이터 객체
   * @returns {Promise}
   */
  async register(metadata) {
    return client.post('/metadata/register', {
      metadata: metadata
    })
  }
}
