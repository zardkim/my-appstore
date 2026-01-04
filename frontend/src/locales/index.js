import { createI18n } from 'vue-i18n'
import ko from './ko'
import en from './en'

// 브라우저 언어 감지 또는 localStorage에서 저장된 언어 가져오기
const savedLocale = localStorage.getItem('locale')
const browserLocale = navigator.language.split('-')[0]
const defaultLocale = savedLocale || (browserLocale === 'ko' ? 'ko' : 'en')

const i18n = createI18n({
  legacy: false, // Composition API 모드 사용
  locale: defaultLocale,
  fallbackLocale: 'en',
  messages: {
    ko,
    en
  }
})

export default i18n
