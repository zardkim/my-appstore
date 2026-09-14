import client from './client'

export const notificationsApi = {
  /**
   * 디스코드 웹훅 테스트 메시지 전송 (관리자 전용)
   * 서버에 저장된 웹훅 URL을 사용하므로 별도 인자가 없다.
   */
  testDiscord: () => client.post('/notifications/discord/test'),

  /**
   * 디스코드 알림 설정 상태 조회 (관리자 전용)
   */
  getDiscordStatus: () => client.get('/notifications/discord/status')
}
