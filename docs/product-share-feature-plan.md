# 제품 공유 기능 개발 계획서

## 1. 기능 개요

관리자 및 사용자가 특정 제품을 외부에 안전하게 공유할 수 있는 기능을 구현한다.

### 핵심 요구사항

| 항목 | 내용 |
|------|------|
| 공유 방식 | 1회성 (사용 후 자동 만료) |
| 기간 제한 | 최대 5일 (1~5일 사용자 선택) |
| 인증 방식 | 랜덤 비밀번호 자동 생성 |
| 공유 버튼 위치 | 제품 상세 페이지에만 노출 |
| 관리 페이지 | 사용자별 공유링크 관리 페이지 |

---

## 2. 데이터베이스 설계

### ShareLink 모델 (`backend/app/models/share_link.py`)

```python
class ShareLink(Base):
    __tablename__ = "share_links"

    id           = Column(Integer, primary_key=True, index=True)
    token        = Column(String(64), unique=True, nullable=False, index=True)  # URL 토큰 (UUID 기반)
    password     = Column(String(20), nullable=False)                           # 랜덤 비밀번호 (8자리)
    product_id   = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by   = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    expires_at   = Column(DateTime, nullable=False)                             # 만료 시각
    is_used      = Column(Boolean, default=False)                               # 1회성 사용 여부
    used_at      = Column(DateTime, nullable=True)                              # 사용 시각
    used_by_ip   = Column(String(45), nullable=True)                            # 사용자 IP
    created_at   = Column(DateTime, default=func.now())
    note         = Column(String(200), nullable=True)                           # 공유 메모 (선택)

    # Relationships
    product      = relationship("Product", foreign_keys=[product_id])
    creator      = relationship("User", foreign_keys=[created_by])
```

### 인덱스 전략
- `token`: UNIQUE 인덱스 (빠른 조회)
- `created_by`: 사용자별 목록 조회용
- `product_id`: 제품별 조회용
- `expires_at`: 만료 정리 스케줄러용

---

## 3. 백엔드 API 설계

### 파일 구조
```
backend/app/
├── models/
│   └── share_link.py          # ShareLink 모델
├── api/
│   └── share.py               # 공유 API 라우터
└── schemas/
    └── share.py               # Pydantic 스키마 (선택)
```

### API 엔드포인트

#### 3.1 공유링크 생성
```
POST /share/create
Authorization: Bearer {token}

Request Body:
{
  "product_id": 123,
  "expires_days": 3,      // 1~5 (기본값 1)
  "note": "팀 내부 공유"   // 선택사항
}

Response:
{
  "id": 1,
  "token": "a1b2c3d4e5f6...",   // 64자 UUID 기반
  "password": "Xk9#mP2q",       // 8자리 랜덤 비밀번호
  "share_url": "https://{host}/share/a1b2c3d4e5f6...",
  "expires_at": "2026-03-01T23:59:59",
  "product_title": "VMware Pro"
}
```

#### 3.2 공유링크 목록 조회 (내 링크)
```
GET /share/my-links?page=1&limit=20
Authorization: Bearer {token}

Response:
{
  "links": [
    {
      "id": 1,
      "token": "a1b2c3...",
      "product_id": 123,
      "product_title": "VMware Pro",
      "product_thumbnail": "...",
      "expires_at": "2026-03-01T23:59:59",
      "is_used": false,
      "is_expired": false,
      "created_at": "2026-02-25T10:00:00",
      "note": "팀 내부 공유"
    }
  ],
  "total": 5
}
```

#### 3.3 공유링크 삭제
```
DELETE /share/{link_id}
Authorization: Bearer {token}
```

#### 3.4 공유 페이지 접근 (비인증)
```
GET /share/view/{token}

Response:
{
  "product_title": "VMware Pro",
  "product_description": "...",
  "expires_at": "2026-03-01T23:59:59",
  "is_expired": false,
  "is_used": false,
  "requires_password": true
}
```

#### 3.5 공유 비밀번호 인증 및 다운로드
```
POST /share/access/{token}

Request Body:
{
  "password": "Xk9#mP2q"
}

Response (성공):
{
  "success": true,
  "product": { ... },    // 제품 상세 정보
  "versions": [ ... ],   // 버전 목록 (다운로드 링크 포함)
}

Response (실패):
{
  "success": false,
  "error": "invalid_password" | "expired" | "already_used"
}
```

#### 3.6 관리자 전체 링크 목록 (관리자 전용)
```
GET /share/admin/all?page=1&limit=20
Authorization: Bearer {token}  // admin 권한 필요
```

### 비밀번호 생성 규칙
- 8자리
- 대문자 + 소문자 + 숫자 조합
- 특수문자 제외 (복사-붙여넣기 편의성)
- 예: `Xk9mP2qR`

### 보안 처리
- 링크 사용 시 `is_used = True`, `used_at`, `used_by_ip` 기록
- 만료 확인: `expires_at < now()` → 접근 차단
- 1회 사용: `is_used = True` → 접근 차단
- 비밀번호 해싱 없이 저장 (단기 임시 링크 특성)
- 토큰: `secrets.token_urlsafe(32)` 사용

---

## 4. 프론트엔드 설계

### 파일 구조
```
frontend/src/
├── api/
│   └── share.js                  # 공유 API 호출 함수
├── components/
│   └── share/
│       ├── ShareDialog.vue        # 공유링크 생성 다이얼로그
│       └── ShareLinkItem.vue      # 공유링크 목록 아이템
├── views/
│   ├── ShareManage.vue            # 내 공유링크 관리 페이지
│   └── ShareView.vue              # 공유 접근 페이지 (비인증)
└── router/
    └── index.js                   # 라우터 추가
```

### 4.1 공유 버튼 (ProductDetail.vue)

제품 상세 페이지 상단 액션 버튼 영역에 공유 버튼 추가:

```html
<v-btn icon @click="openShareDialog" title="공유링크 생성">
  <v-icon>mdi-share-variant</v-icon>
</v-btn>
```

### 4.2 ShareDialog.vue - 공유링크 생성 다이얼로그

```
┌─────────────────────────────────────┐
│  📤 제품 공유링크 생성               │
│                                     │
│  제품: VMware Pro                    │
│                                     │
│  공유 기간                           │
│  [1일] [2일] [3일] [4일] [5일]      │
│                                     │
│  메모 (선택)                         │
│  [____________________________]     │
│                                     │
│  [취소]              [링크 생성]    │
└─────────────────────────────────────┘

→ 생성 후:

┌─────────────────────────────────────┐
│  ✅ 공유링크가 생성되었습니다          │
│                                     │
│  링크: https://...                  │
│  [복사]                             │
│                                     │
│  비밀번호: Xk9mP2qR                 │
│  [복사]                             │
│                                     │
│  만료: 2026-02-28 23:59             │
│  ⚠️ 이 비밀번호는 지금만 표시됩니다   │
│                                     │
│  [공유링크 관리 페이지로 이동] [닫기] │
└─────────────────────────────────────┘
```

### 4.3 ShareManage.vue - 공유링크 관리 페이지

라우트: `/my/share-links`

```
┌─────────────────────────────────────────────────────┐
│  내 공유링크 관리                                     │
│                                                     │
│  [활성] [만료됨] [사용됨]  (탭 필터)                │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │ 🖼️ VMware Pro                                │   │
│  │    만료: 2026-02-28  ●활성                   │   │
│  │    메모: 팀 내부 공유                         │   │
│  │    [링크복사] [삭제]                          │   │
│  └─────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────┐   │
│  │ 🖼️ Adobe Photoshop                           │   │
│  │    만료: 2026-02-20  ✗만료됨                 │   │
│  │    [삭제]                                    │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### 4.4 ShareView.vue - 공유 접근 페이지

라우트: `/share/:token`  (비인증 접근 가능)

```
┌─────────────────────────────────────┐
│  🔐 제품 공유 페이지                  │
│                                     │
│  VMware Pro                         │
│  만료: 2026-02-28                   │
│                                     │
│  비밀번호를 입력하세요                │
│  [________________]                 │
│                                     │
│  [확인]                             │
└─────────────────────────────────────┘

→ 인증 성공 후: 제품 정보 + 다운로드 버튼 표시
→ 이미 사용됨: "이 링크는 이미 사용되었습니다" 안내
→ 만료됨: "이 링크는 만료되었습니다" 안내
```

### 4.5 네비게이션 메뉴

사용자 프로필 드롭다운 또는 사이드 메뉴에 "공유링크 관리" 추가:
- 아이콘: `mdi-link-variant`
- 라우트: `/my/share-links`

---

## 5. 라우터 추가

```javascript
// router/index.js 추가
{
  path: '/share/:token',
  name: 'ShareView',
  component: () => import('@/views/ShareView.vue'),
  meta: { requiresAuth: false }  // 비인증 접근 가능
},
{
  path: '/my/share-links',
  name: 'ShareManage',
  component: () => import('@/views/ShareManage.vue'),
  meta: { requiresAuth: true }
}
```

---

## 6. 번역 키 추가

### ko.js / en.js
```javascript
share: {
  title: '공유링크 생성',
  createLink: '링크 생성',
  shareLink: '공유 링크',
  password: '비밀번호',
  expiresIn: '공유 기간',
  days: '{n}일',
  note: '메모 (선택)',
  notePlaceholder: '공유 목적이나 메모를 입력하세요',
  createdSuccess: '공유링크가 생성되었습니다',
  passwordWarning: '이 비밀번호는 지금만 표시됩니다. 반드시 복사하세요.',
  copyLink: '링크 복사',
  copyPassword: '비밀번호 복사',
  copied: '복사됨',
  manageLinks: '공유링크 관리',
  myLinks: '내 공유링크',
  noLinks: '생성된 공유링크가 없습니다',
  status: {
    active: '활성',
    expired: '만료됨',
    used: '사용됨',
  },
  deleteConfirm: '이 공유링크를 삭제하시겠습니까?',
  // ShareView
  enterPassword: '비밀번호를 입력하세요',
  accessProduct: '확인',
  alreadyUsed: '이 링크는 이미 사용되었습니다.',
  linkExpired: '이 링크는 만료되었습니다.',
  invalidPassword: '비밀번호가 올바르지 않습니다.',
  downloadNow: '지금 다운로드',
}
```

---

## 7. 스케줄러 (선택)

만료된 링크 자동 정리 (`backend/app/api/scheduler.py` 또는 별도 task):

```python
# 매일 자정 실행
def cleanup_expired_share_links():
    cutoff = datetime.now() - timedelta(days=30)  # 만료 후 30일 보관 후 삭제
    db.query(ShareLink).filter(ShareLink.expires_at < cutoff).delete()
```

---

## 8. 보안 고려사항

| 위협 | 대응 |
|------|------|
| 토큰 무차별 대입 | 64자리 URL-safe 토큰 (2^384 경우의 수) |
| 비밀번호 무차별 대입 | 5회 실패 시 해당 토큰 즉시 만료 처리 |
| 링크 무한 생성 | 사용자당 동시 활성 링크 최대 20개 제한 |
| 민감 제품 공유 | 공유 기능 관리자 설정으로 비활성화 가능 (옵션) |
| IP 추적 | `used_by_ip` 기록으로 감사 로그 유지 |

---

## 9. 구현 단계

### Phase 1 - 백엔드 (우선 구현)
1. `ShareLink` 모델 생성 및 DB 마이그레이션
2. `backend/app/api/share.py` API 구현
   - 생성 / 조회 / 삭제 / 접근 / 인증
3. `backend/app/main.py`에 라우터 등록
4. 단위 테스트

### Phase 2 - 프론트엔드 핵심
5. `frontend/src/api/share.js` API 클라이언트
6. `ShareDialog.vue` 생성 다이얼로그
7. `ProductDetail.vue`에 공유 버튼 추가
8. `ShareView.vue` 공유 접근 페이지

### Phase 3 - 관리 페이지
9. `ShareManage.vue` 공유링크 관리 페이지
10. 네비게이션 메뉴에 링크 추가
11. 번역 키 추가 (ko.js / en.js)

### Phase 4 - 마무리
12. 만료 링크 자동 정리 스케줄러 추가
13. E2E 테스트
14. 버전업 및 배포

---

## 10. 예상 버전

| 단계 | 버전 |
|------|------|
| Phase 1-2 완료 | v1.4.0 |
| Phase 3 완료 | v1.4.1 |
| Phase 4 완료 | v1.4.2 |

---

*작성일: 2026-02-25*
*작성자: Claude (AI Assistant)*
