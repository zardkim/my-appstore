/**
 * Locale Files Index
 *
 * 새로운 언어를 추가하려면:
 * 1. locales/[언어코드].js 파일 생성 (예: ja.js, zh.js)
 * 2. 아래에 import 추가
 * 3. export default 객체에 추가
 */

import ko from './ko'
import en from './en'

export default {
  ko,
  en
  // 여기에 더 많은 언어 추가 가능
  // ja, // 일본어
  // zh, // 중국어
  // etc.
}
