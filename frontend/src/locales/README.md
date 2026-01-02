# 🌍 다국어 지원 가이드 (i18n)

MyApp Store의 다국어 지원 시스템 사용 가이드입니다.

## 📁 파일 구조

```
frontend/src/
├── i18n.js                    # i18n 설정
├── locales/
│   ├── README.md             # 이 문서
│   ├── index.js              # 번역 파일 통합
│   ├── ko.js                 # 한국어 번역
│   └── en.js                 # 영어 번역
└── store/
    └── locale.js             # 언어 상태 관리
```

## 🚀 빠른 시작

### 1. 번역 파일 작성

`ko.js`와 `en.js` 파일에 번역을 추가하세요.

**ko.js 예시:**
```javascript
export default {
  common: {
    button: {
      save: '저장',
      cancel: '취소'
    }
  },
  nav: {
    home: '홈',
    settings: '설정'
  }
}
```

**en.js 예시:**
```javascript
export default {
  common: {
    button: {
      save: 'Save',
      cancel: 'Cancel'
    }
  },
  nav: {
    home: 'Home',
    settings: 'Settings'
  }
}
```

### 2. 컴포넌트에서 사용

#### 템플릿에서 사용
```vue
<template>
  <h1>{{ $t('nav.home') }}</h1>
  <button>{{ $t('common.button.save') }}</button>
</template>
```

#### Script에서 사용
```vue
<script setup>
import { useI18n } from 'vue-i18n'

const { t, locale } = useI18n()

// 번역 텍스트 가져오기
const title = t('nav.home')

// 현재 언어 확인
console.log(locale.value) // 'ko' 또는 'en'
</script>
```

### 3. 변수 포함 번역

#### 번역 파일:
```javascript
{
  welcome: {
    message: '환영합니다, {name}님!'
  }
}
```

#### 컴포넌트:
```vue
<template>
  <p>{{ $t('welcome.message', { name: username }) }}</p>
</template>
```

### 4. 복수형 처리

#### 번역 파일:
```javascript
{
  items: {
    count: '아이템 없음 | {n}개의 아이템 | {n}개의 아이템들'
  }
}
```

#### 컴포넌트:
```vue
<template>
  <p>{{ $t('items.count', count) }}</p>
</template>
```

### 5. 날짜/시간 포맷

```vue
<template>
  <p>{{ $d(new Date(), 'short') }}</p>
  <p>{{ $d(new Date(), 'long') }}</p>
</template>
```

## 🔧 언어 변경

### Locale Store 사용

```vue
<script setup>
import { useLocaleStore } from '@/store/locale'

const localeStore = useLocaleStore()

// 언어 변경
const changeLanguage = (lang) => {
  localeStore.setLocale(lang) // 'ko' 또는 'en'
}

// 현재 언어 확인
const currentLanguage = localeStore.locale
</script>
```

### v-model로 언어 선택

```vue
<template>
  <select v-model="language">
    <option value="ko">한국어</option>
    <option value="en">English</option>
  </select>
</template>

<script setup>
import { computed } from 'vue'
import { useLocaleStore } from '@/store/locale'

const localeStore = useLocaleStore()

const language = computed({
  get: () => localeStore.locale,
  set: (value) => localeStore.setLocale(value)
})
</script>
```

## ✨ 새로운 언어 추가하기

### 1. 번역 파일 생성

`locales/ja.js` 파일 생성 (일본어 예시):

```javascript
export default {
  common: {
    button: {
      save: '保存',
      cancel: 'キャンセル'
    }
  }
  // ...
}
```

### 2. locales/index.js에 추가

```javascript
import ko from './ko'
import en from './en'
import ja from './ja' // 추가

export default {
  ko,
  en,
  ja // 추가
}
```

### 3. store/locale.js에 등록

```javascript
supportedLocales: [
  { code: 'ko', name: '한국어', nativeName: '한국어' },
  { code: 'en', name: 'English', nativeName: 'English' },
  { code: 'ja', name: 'Japanese', nativeName: '日本語' } // 추가
]
```

### 4. i18n.js에 날짜/시간 포맷 추가 (선택)

```javascript
datetimeFormats: {
  // ...
  ja: {
    short: { year: 'numeric', month: '2-digit', day: '2-digit' },
    long: { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }
  }
}
```

## 📝 번역 키 네이밍 규칙

✅ **좋은 예:**
- `common.button.save`
- `settings.users.addButton`
- `product.detail.description`

❌ **나쁜 예:**
- `btn_save` (언더스코어 사용)
- `SaveButton` (PascalCase)
- `s.u.a` (의미 불명확)

### 권장 구조:
```
카테고리.영역.항목
```

## 🎯 번역 우선순위

1. **필수 (Phase 1):**
   - 네비게이션 메뉴
   - 공통 버튼 (저장, 취소, 삭제 등)
   - 로그인/인증 페이지

2. **중요 (Phase 2):**
   - 주요 페이지 제목 및 설명
   - 폼 레이블
   - 설정 페이지

3. **선택 (Phase 3):**
   - 도움말 텍스트
   - 에러 메시지 상세
   - 툴팁

## 🔍 번역 누락 확인

번역이 누락된 경우 기본 언어(한국어)가 표시됩니다.

### 개발 모드에서 확인:
브라우저 콘솔에서 누락된 번역 키를 확인할 수 있습니다.

## 💡 팁

### 1. 번역 키 자동완성
VS Code를 사용하는 경우, JS 파일로 작성하면 자동완성이 지원됩니다.

### 2. 긴 텍스트 처리
긴 텍스트는 백틱(`)을 사용하여 여러 줄로 작성:

```javascript
{
  longText: `
    첫 번째 줄
    두 번째 줄
    세 번째 줄
  `
}
```

### 3. HTML 포함
HTML을 포함해야 하는 경우 `v-html` 사용:

```vue
<template>
  <div v-html="$t('content.html')"></div>
</template>
```

번역 파일:
```javascript
{
  content: {
    html: '<strong>굵은 텍스트</strong>와 일반 텍스트'
  }
}
```

## 🐛 문제 해결

### 번역이 표시되지 않는 경우:

1. **번역 키 확인**
   - 오타가 없는지 확인
   - 대소문자가 정확한지 확인

2. **파일 저장 확인**
   - 번역 파일을 저장했는지 확인
   - `npm run dev` 재시작

3. **콘솔 확인**
   - 브라우저 개발자 도구에서 에러 확인

4. **언어 코드 확인**
   - localStorage의 'locale' 값 확인
   - 지원하는 언어 코드인지 확인

## 📚 참고 자료

- [Vue I18n 공식 문서](https://vue-i18n.intlify.dev/)
- [Composition API 가이드](https://vue-i18n.intlify.dev/guide/advanced/composition.html)
- [날짜/시간 포맷](https://vue-i18n.intlify.dev/guide/essentials/datetime.html)

## 🤝 기여하기

번역을 추가하거나 개선하고 싶으신가요?

1. 해당 언어 파일 (`ko.js` 또는 `en.js`) 편집
2. 누락된 번역 추가
3. 저장 후 빌드/배포

---

**문의사항이 있으시면 Issues에 등록해주세요!**
