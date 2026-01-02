# ✅ 다국어 지원 (i18n) 설정 완료

MyApp Store 프로젝트에 **vue-i18n**을 사용한 다국어 지원 기능이 설정되었습니다.

## 📋 완료된 작업

### ✅ 1. 패키지 설치
- `vue-i18n@9` 설치 완료

### ✅ 2. 파일 구조 생성
```
frontend/src/
├── i18n.js                    # vue-i18n 설정 파일
├── locales/
│   ├── README.md             # 사용 가이드
│   ├── index.js              # 번역 파일 통합
│   ├── ko.js                 # 한국어 번역 (샘플 포함)
│   └── en.js                 # 영어 번역 (샘플 포함)
├── store/
│   └── locale.js             # 언어 상태 관리 (Pinia)
└── main.js                    # i18n 등록 완료
```

### ✅ 3. Settings 페이지 연동
- 언어 선택 드롭다운이 locale store와 연결됨
- 언어 변경 시 자동으로 localStorage에 저장
- 새로고침 후에도 선택한 언어 유지

### ✅ 4. 문서 작성
- `src/locales/README.md` - 상세 사용 가이드
- `USAGE_EXAMPLE.md` - 컴포넌트별 적용 예시

### ✅ 5. 빌드 테스트
- 프로덕션 빌드 성공 확인

## 🎯 다음 단계: 번역 파일 작성

### 1. 번역 파일 편집

**한국어 (`src/locales/ko.js`):**
```javascript
export default {
  common: {
    button: {
      save: '저장',
      cancel: '취소'
      // ... 더 많은 번역 추가
    }
  },
  nav: {
    home: '홈',
    settings: '설정'
    // ... 더 많은 번역 추가
  }
  // ... 섹션별로 번역 추가
}
```

**영어 (`src/locales/en.js`):**
```javascript
export default {
  common: {
    button: {
      save: 'Save',
      cancel: 'Cancel'
      // ... 더 많은 번역 추가
    }
  },
  nav: {
    home: 'Home',
    settings: 'Settings'
    // ... 더 많은 번역 추가
  }
  // ... 섹션별로 번역 추가
}
```

### 2. 컴포넌트에 적용

**기본 사용법:**
```vue
<template>
  <!-- 하드코딩된 텍스트 -->
  <h1>홈</h1>
  <button>저장</button>

  <!-- 번역 키로 변경 -->
  <h1>{{ $t('nav.home') }}</h1>
  <button>{{ $t('common.button.save') }}</button>
</template>
```

**Script에서 사용:**
```vue
<script setup>
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const message = t('common.message.success')
</script>
```

### 3. 적용 우선순위

**Phase 1 (필수):**
1. 네비게이션 메뉴 (MainLayout.vue, Sidebar.vue)
2. 공통 버튼 (저장, 취소, 삭제 등)
3. 로그인/인증 페이지 (Login.vue, Setup.vue)

**Phase 2 (중요):**
4. 주요 페이지 (Home.vue, Discover.vue, ProductDetail.vue)
5. 설정 페이지 (Settings.vue, Admin.vue)
6. 폼 레이블 및 플레이스홀더

**Phase 3 (선택):**
7. 에러 메시지 및 알림
8. 도움말 텍스트
9. 카테고리 이름

### 4. 테스트

**개발 서버 실행:**
```bash
cd frontend
npm run dev
```

**언어 전환 테스트:**
1. Settings 페이지 접속
2. 언어 드롭다운에서 English 선택
3. 각 페이지를 이동하며 번역 확인
4. 한국어로 다시 전환 확인

**빌드 테스트:**
```bash
npm run build
```

## 📚 참고 문서

1. **상세 사용 가이드:**
   - `src/locales/README.md`

2. **컴포넌트별 적용 예시:**
   - `USAGE_EXAMPLE.md`

3. **Vue I18n 공식 문서:**
   - https://vue-i18n.intlify.dev/

## 🔧 현재 동작 방식

### 언어 선택 프로세스:
1. 사용자가 Settings에서 언어 선택
2. `locale.js` store의 `setLocale()` 호출
3. localStorage에 저장 (`locale` 키)
4. vue-i18n의 전역 locale 변경
5. 모든 `$t()` 함수가 새 언어로 렌더링

### 초기 언어 설정:
1. localStorage에 저장된 언어 확인
2. 없으면 브라우저 언어 확인
3. 지원하지 않으면 기본 언어(한국어) 사용

### 번역 폴백:
- 번역 키가 없으면 한국어(fallbackLocale) 사용
- 한국어에도 없으면 번역 키 자체 표시

## ⚠️ 주의사항

1. **번역 키 네이밍:**
   - 소문자와 점(.)으로 구분
   - 명확하고 설명적인 이름 사용
   - 예: `settings.users.addButton`

2. **일관성:**
   - 같은 의미의 텍스트는 같은 번역 키 사용
   - 버튼: 동사 (저장, Save)
   - 제목: 명사 (설정, Settings)

3. **HTML 포함:**
   - HTML이 필요한 경우 `v-html` 사용
   - XSS 취약점 주의

4. **동적 콘텐츠:**
   - 변수는 `{ }` 사용: `$t('msg', { name: '홍길동' })`

## 🚀 배포

번역 파일 작성 후:

```bash
# 프로덕션 빌드
npm run build

# Docker 이미지 재빌드 (필요시)
docker-compose build frontend
docker-compose up -d
```

## ✨ 향후 확장 가능성

- 🌏 추가 언어 지원 (일본어, 중국어 등)
- 🔄 번역 파일 자동 동기화
- 📊 번역 커버리지 체크
- 🌐 백엔드 API 메시지 다국어화

---

**준비 완료!** 이제 번역 파일만 작성하면 자동으로 적용됩니다.

상세한 사용법은 `src/locales/README.md`와 `USAGE_EXAMPLE.md`를 참조하세요.
