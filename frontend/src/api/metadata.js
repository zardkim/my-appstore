import client from './client'

export const metadataApi = {
  /**
   * 메타데이터 생성 테스트
   * @param {string} softwareName - 소프트웨어 이름
   * @param {Object} settings - 메타데이터 설정 (aiProvider, aiModel만 사용; 키는 서버가 config에서 직접 읽음)
   * @returns {Promise}
   */
  async testGeneration(softwareName, settings = null) {
    const requestData = {
      software_name: softwareName
    }

    // provider/model만 전달 (API 키는 보안상 서버가 config에서 직접 읽음)
    if (settings) {
      if (settings.aiProvider) requestData.ai_provider = settings.aiProvider
      if (settings.aiModel) requestData.ai_model = settings.aiModel
      if (settings.useCustomPrompt) requestData.use_custom_prompt = settings.useCustomPrompt
      if (settings.customPrompt) requestData.custom_prompt = settings.customPrompt
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
