/**
 * Locale Store (Pinia)
 *
 * 언어 설정 상태 관리
 * - localStorage와 동기화
 * - 선택적으로 백엔드 API와 동기화 가능
 */

import { defineStore } from 'pinia'
import i18n from '../locales'

export const useLocaleStore = defineStore('locale', {
  state: () => ({
    // 현재 선택된 언어
    locale: localStorage.getItem('locale') || 'ko',
    // 지원하는 언어 목록
    supportedLocales: [
      { code: 'ko', name: '한국어', nativeName: '한국어' },
      { code: 'en', name: 'English', nativeName: 'English' }
      // 여기에 더 많은 언어 추가 가능
      // { code: 'ja', name: 'Japanese', nativeName: '日本語' },
      // { code: 'zh', name: 'Chinese', nativeName: '中文' }
    ]
  }),

  getters: {
    /**
     * 현재 언어 정보 반환
     */
    currentLocale: (state) => {
      return state.supportedLocales.find(l => l.code === state.locale) || state.supportedLocales[0]
    },

    /**
     * 현재 언어 코드
     */
    currentLocaleCode: (state) => state.locale
  },

  actions: {
    /**
     * 언어 변경
     * @param {string} newLocale - 새로운 언어 코드 (예: 'ko', 'en')
     */
    async setLocale(newLocale) {
      // 지원하는 언어인지 확인
      const supported = this.supportedLocales.find(l => l.code === newLocale)
      if (!supported) {
        console.warn(`Locale '${newLocale}' is not supported. Using default locale.`)
        return
      }

      // 상태 업데이트
      this.locale = newLocale

      // localStorage에 저장
      localStorage.setItem('locale', newLocale)

      // vue-i18n 글로벌 locale 변경 (즉시 적용)
      i18n.global.locale.value = newLocale

      // 선택적: 백엔드 API에 저장
      // try {
      //   await settingsApi.updateLocale(newLocale)
      // } catch (error) {
      //   console.error('Failed to save locale to backend:', error)
      // }

      console.log(`Locale changed to: ${newLocale}`)
    },

    /**
     * 브라우저 기본 언어로 변경
     */
    setBrowserLocale() {
      const browserLocale = navigator.language || navigator.userLanguage
      const localeCode = browserLocale.split('-')[0]
      const supported = this.supportedLocales.find(l => l.code === localeCode)

      if (supported) {
        this.setLocale(localeCode)
      } else {
        console.log(`Browser locale '${localeCode}' not supported. Using current locale.`)
      }
    }
  }
})
