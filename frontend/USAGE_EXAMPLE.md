# 다국어 지원 사용 예시

이 문서는 다국어 지원을 실제 컴포넌트에 적용하는 방법을 보여줍니다.

## 🎯 빠른 적용 가이드

### 1. MainLayout.vue - 네비게이션 메뉴 번역

**변경 전:**
```vue
<template>
  <span class="mobile-nav-text">홈</span>
  <span class="mobile-nav-text">스토어</span>
  <span class="mobile-nav-text">팁&테크</span>
  <span class="mobile-nav-text">설정</span>
  <span class="mobile-nav-text">더보기</span>
</template>
```

**변경 후:**
```vue
<template>
  <span class="mobile-nav-text">{{ $t('nav.home') }}</span>
  <span class="mobile-nav-text">{{ $t('nav.discover') }}</span>
  <span class="mobile-nav-text">{{ $t('nav.tips') }}</span>
  <span class="mobile-nav-text">{{ $t('nav.settings') }}</span>
  <span class="mobile-nav-text">{{ $t('nav.more') }}</span>
</template>
```

### 2. Login.vue - 로그인 페이지

**변경 전:**
```vue
<template>
  <h1>로그인</h1>
  <input placeholder="사용자명" />
  <input placeholder="비밀번호" type="password" />
  <button>로그인</button>
</template>
```

**변경 후:**
```vue
<template>
  <h1>{{ $t('auth.login.title') }}</h1>
  <input :placeholder="$t('auth.login.username')" />
  <input :placeholder="$t('auth.login.password')" type="password" />
  <button>{{ $t('auth.login.submit') }}</button>
</template>
```

### 3. Settings.vue - 버튼 번역

**변경 전:**
```vue
<template>
  <button>저장</button>
  <button>취소</button>
  <button>사용자 추가</button>
</template>
```

**변경 후:**
```vue
<template>
  <button>{{ $t('common.button.save') }}</button>
  <button>{{ $t('common.button.cancel') }}</button>
  <button>{{ $t('settings.user.add') }}</button>
</template>
```

### 4. ProductCard.vue - 카테고리 번역

**변경 전:**
```vue
<script setup>
const getCategoryIcon = (category) => {
  return categoryIcons[category] || '📦'
}
</script>

<template>
  <span>{{ product.category }}</span>
</template>
```

**변경 후:**
```vue
<script setup>
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const getCategoryIcon = (category) => {
  return categoryIcons[category] || '📦'
}

const getCategoryLabel = (category) => {
  return t(`category.${category}`)
}
</script>

<template>
  <span>{{ getCategoryLabel(product.category) }}</span>
</template>
```

### 5. Admin.vue - 복잡한 텍스트 번역

**변경 전:**
```vue
<template>
  <h2>수동 파일 스캔</h2>
  <button :disabled="scanning">
    {{ scanning ? '스캔 중...' : '스캔 시작' }}
  </button>

  <div v-if="scanResult">
    <h3>✓ 스캔 완료</h3>
    <p>새로운 프로그램: {{ scanResult.new_products }}개</p>
  </div>
</template>
```

**변경 후:**
```vue
<template>
  <h2>{{ $t('admin.scan.title') }}</h2>
  <button :disabled="scanning">
    {{ scanning ? $t('admin.scan.scanning') : $t('admin.scan.start') }}
  </button>

  <div v-if="scanResult">
    <h3>{{ $t('admin.scan.completed') }}</h3>
    <p>{{ $t('admin.scan.newProducts') }}: {{ scanResult.new_products }}개</p>
  </div>
</template>
```

### 6. 날짜 포맷 적용

**변경 전:**
```vue
<template>
  <p>{{ new Date(user.created_at).toLocaleDateString() }}</p>
</template>
```

**변경 후:**
```vue
<template>
  <p>{{ $d(new Date(user.created_at), 'short') }}</p>
</template>
```

## 🎨 동적 번역 예시

### 변수를 포함한 메시지

**번역 파일 (ko.js):**
```javascript
{
  notification: {
    itemsAdded: '{count}개의 항목이 추가되었습니다',
    welcomeUser: '환영합니다, {name}님!'
  }
}
```

**컴포넌트:**
```vue
<template>
  <p>{{ $t('notification.itemsAdded', { count: 5 }) }}</p>
  <p>{{ $t('notification.welcomeUser', { name: username }) }}</p>
</template>
```

### 조건부 번역

```vue
<script setup>
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const status = 'active'

const getStatusText = (status) => {
  return t(`common.status.${status}`)
}
</script>

<template>
  <span>{{ getStatusText(status) }}</span>
</template>
```

## 📦 컴포넌트별 적용 체크리스트

### ✅ 네비게이션 & 레이아웃
- [ ] MainLayout.vue - 모바일 네비게이션
- [ ] Sidebar.vue - 데스크톱 사이드바
- [ ] Footer.vue - 푸터

### ✅ 인증
- [ ] Login.vue - 로그인 페이지
- [ ] Setup.vue - 초기 설정

### ✅ 주요 페이지
- [ ] Home.vue - 대시보드
- [ ] Discover.vue - 스토어 페이지
- [ ] ProductDetail.vue - 제품 상세
- [ ] Settings.vue - 설정 페이지
- [ ] Admin.vue - 관리자 페이지

### ✅ 컴포넌트
- [ ] ProductCard.vue - 제품 카드
- [ ] FolderBrowser.vue - 폴더 브라우저
- [ ] UnmatchedDetailDialog.vue - 불일치 항목 다이얼로그

### ✅ Tips & Board
- [ ] Tips.vue - 게시판 목록
- [ ] TipsDetail.vue - 게시글 상세
- [ ] TipsWrite.vue - 글 작성

## 🚀 빌드 및 배포

### 1. 번역 파일 작성 완료 확인
```bash
# 번역 파일 확인
cat frontend/src/locales/ko.js
cat frontend/src/locales/en.js
```

### 2. 개발 서버에서 테스트
```bash
cd frontend
npm run dev
```

### 3. 언어 전환 테스트
- 설정 페이지에서 언어를 변경
- 각 페이지 이동하며 번역 확인
- 브라우저 localStorage 확인: `localStorage.getItem('locale')`

### 4. 프로덕션 빌드
```bash
npm run build
```

## 💡 유지보수 팁

### 번역 누락 찾기

1. **브라우저 콘솔 확인**
   - 번역 키가 없으면 경고 메시지 표시

2. **영어로 전환 후 확인**
   - 한글로 표시되는 부분 = 번역 누락

3. **전역 검색**
   ```bash
   # 하드코딩된 한글 텍스트 찾기
   grep -r "홈\|설정\|저장" frontend/src/views/
   grep -r "로그인\|사용자" frontend/src/components/
   ```

### 일관성 유지

번역 작업 시 참고:
- 버튼: 동사 사용 (저장, Save)
- 제목: 명사 사용 (설정, Settings)
- 메시지: 완전한 문장 (저장되었습니다, Saved successfully)

## 🔗 다음 단계

1. **번역 파일 작성**
   - `src/locales/ko.js` 완성
   - `src/locales/en.js` 완성

2. **컴포넌트 적용**
   - 위 체크리스트 참고하여 순차 적용

3. **테스트**
   - 모든 페이지에서 언어 전환 테스트
   - 모바일/데스크톱 뷰 확인

4. **배포**
   - 프로덕션 빌드
   - Docker 이미지 재빌드

---

**참고:** 이 예시들은 가이드라인입니다. 실제 적용 시 프로젝트 구조에 맞게 조정하세요.
