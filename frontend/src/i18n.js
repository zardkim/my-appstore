/**
 * Vue I18n Configuration
 *
 * 다국어 지원 설정 파일
 * - Composition API 모드 사용 (legacy: false)
 * - localStorage에서 사용자 언어 설정 로드
 * - 기본 언어: 한국어 (ko)
 * - 폴백 언어: 한국어 (번역이 없을 경우)
 */

import { createI18n } from 'vue-i18n'
import messages from './locales'

// 브라우저 언어 감지 (선택적)
const getBrowserLocale = () => {
  const browserLocale = navigator.language || navigator.userLanguage
  // 'ko-KR' -> 'ko', 'en-US' -> 'en'
  return browserLocale.split('-')[0]
}

// 사용자 저장 언어 또는 브라우저 언어 또는 기본 언어
const savedLocale = localStorage.getItem('locale')
const browserLocale = getBrowserLocale()
const supportedLocales = Object.keys(messages)
const defaultLocale = 'ko'

// 지원하는 언어인지 확인
const getInitialLocale = () => {
  if (savedLocale && supportedLocales.includes(savedLocale)) {
    return savedLocale
  }
  if (supportedLocales.includes(browserLocale)) {
    return browserLocale
  }
  return defaultLocale
}

const i18n = createI18n({
  legacy: false, // Composition API 사용
  locale: getInitialLocale(),
  fallbackLocale: defaultLocale,
  messages,

  // 날짜/시간 포맷 (선택적)
  datetimeFormats: {
    ko: {
      short: {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      },
      long: {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        weekday: 'long'
      },
      time: {
        hour: '2-digit',
        minute: '2-digit'
      }
    },
    en: {
      short: {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      },
      long: {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        weekday: 'long'
      },
      time: {
        hour: '2-digit',
        minute: '2-digit'
      }
    }
  },

  // 숫자 포맷 (선택적)
  numberFormats: {
    ko: {
      currency: {
        style: 'currency',
        currency: 'KRW',
        currencyDisplay: 'symbol'
      },
      decimal: {
        style: 'decimal',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }
    },
    en: {
      currency: {
        style: 'currency',
        currency: 'USD',
        currencyDisplay: 'symbol'
      },
      decimal: {
        style: 'decimal',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }
    }
  }
})

export default i18n
