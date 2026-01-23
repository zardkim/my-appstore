# 메타데이터 관리 기능 구현 계획

## 목차
1. [개요](#개요)
2. [메타데이터 항목 정의](#메타데이터-항목-정의)
3. [현재 시스템 분석](#현재-시스템-분석)
4. [구현 계획](#구현-계획)
5. [UI/UX 설계](#uiux-설계)
6. [백엔드 API 설계](#백엔드-api-설계)
7. [구현 단계](#구현-단계)

---

## 개요

### 목적
라이브러리에 프로그램이 추가될 때 AI가 자동으로 생성한 메타데이터를 사용자에게 표시하고, 메타데이터가 부정확한 경우 관리자가 수동으로 수정할 수 있는 기능을 제공합니다.

### 핵심 기능
1. **AI 스캔 진행 상황 표시**: 스캔 중 생성되는 메타데이터를 실시간으로 표시
2. **메타데이터 표시**: 각 제품의 메타데이터를 명확하게 표시
3. **메타데이터 수정**: 관리자가 부정확한 메타데이터를 수정할 수 있는 인터페이스 제공
4. **수정 이력 추적** (선택사항): 메타데이터 변경 이력 기록

---

## 메타데이터 항목 정의

### Product 레벨 메타데이터
AI가 자동으로 생성하는 제품(Product) 관련 메타데이터:

| 필드명 | 타입 | 설명 | AI 생성 | 수정 가능 | 필수 |
|--------|------|------|---------|-----------|------|
| `title` | String | 정확한 공식 제품명 (예: "Adobe Photoshop") | ✓ | ✓ | ✓ |
| `description` | Text | 50-100자 이내의 제품 설명 | ✓ | ✓ | ✗ |
| `vendor` | String | 제조사/개발사 (예: "Adobe", "Microsoft") | ✓ | ✓ | ✗ |
| `category` | String | 카테고리 (Graphics, Office, Development 등) | ✓ | ✓ | ✓ |
| `icon_url` | String | 아이콘 이미지 URL 또는 로컬 경로 | ✓ | ✓ | ✗ |
| `folder_path` | String | 파일 시스템 폴더 경로 | ✗ | ✗ | ✓ |

### Version 레벨 메타데이터
파일 시스템에서 자동으로 수집하는 버전(Version) 관련 메타데이터:

| 필드명 | 타입 | 설명 | AI 생성 | 수정 가능 | 필수 |
|--------|------|------|---------|-----------|------|
| `version_name` | String | 버전 번호 (예: "2024", "v1.0") | ✓ | ✓ | ✗ |
| `file_name` | String | 파일명 | ✗ | ✗ | ✓ |
| `file_path` | String | 파일 전체 경로 | ✗ | ✗ | ✓ |
| `file_size` | BigInteger | 파일 크기 (바이트) | ✗ | ✗ | ✗ |
| `release_date` | DateTime | 릴리즈 날짜 (파일 생성 날짜) | ✗ | ✓ | ✓ |

### 카테고리 목록 (20개)
```
Graphics, Office, Development, Utility, Media, OS, Security,
Network, Mac, Mobile, Patch, Driver, Source, Backup, Portable,
Business, Engineering, Theme, Hardware, Uncategorized
```

---

## 현재 시스템 분석

### 기존 AI 메타데이터 생성 흐름
```
[파일/폴더 발견]
    ↓
[FilenameParser: 파일명 파싱]
    ↓
[AIMetadataGenerator: OpenAI API 호출]
    ↓
[메타데이터 정제 및 검증]
    ↓
[IconCache: 아이콘 다운로드 및 캐싱]
    ↓
[Database: Product/Version 저장]
```

### 현재 스캔 방식
1. **수동 스캔** (`/api/scan/start`)
   - Admin 페이지에서 관리자가 수동으로 실행
   - 완료 후 결과 요약만 표시 (new_products, new_versions 등)
   - 개별 메타데이터는 표시하지 않음

2. **자동 스캔** (스케줄러)
   - Cron 표현식에 따라 자동 실행
   - 백그라운드에서 실행되며 결과는 ScanHistory에 기록
   - 진행 상황 실시간 표시 없음

### 현재 제한사항
- ❌ 스캔 중 생성되는 메타데이터를 실시간으로 확인할 수 없음
- ❌ AI가 생성한 메타데이터가 부정확해도 수정 방법이 없음
- ❌ 메타데이터 품질을 검증할 UI가 없음
- ❌ 제품 수정 API가 존재하지 않음

---

## 구현 계획

### Phase 1: 제품 편집 기능 (기본)
**목표**: 기존 제품의 메타데이터를 수정할 수 있는 기본 기능 제공

#### 1.1 백엔드 API
- `PUT /api/products/{id}` - 제품 메타데이터 업데이트 (관리자 전용)
- `PUT /api/products/{id}/versions/{version_id}` - 버전 정보 업데이트 (관리자 전용)

#### 1.2 프론트엔드 UI
- **제품 상세 페이지 (ProductDetail.vue)** 수정
  - 관리자에게만 "편집" 버튼 표시
  - 클릭 시 편집 모달 열기
  - 모든 메타데이터 필드를 폼으로 제공
  - 카테고리는 드롭다운 선택
  - 아이콘은 URL 입력 또는 파일 업로드

- **제품 목록 페이지 (Discover.vue)** 개선
  - 각 카드에 메타데이터 상태 표시 (AI 생성 뱃지)
  - 관리자용 퀵 편집 버튼 (선택사항)

### Phase 2: 스캔 진행 상황 표시 (고급)
**목표**: 스캔 중 메타데이터 생성 과정을 실시간으로 표시

#### 2.1 백엔드 개선
- WebSocket 또는 Server-Sent Events (SSE) 추가
- 스캔 진행 상황을 실시간으로 클라이언트에 전송
- 각 제품별 메타데이터 생성 결과 스트리밍

#### 2.2 프론트엔드 UI
- **Admin 페이지 - 수동 스캔 탭** 개선
  - 스캔 진행 중 실시간 로그 표시
  - 각 제품/버전별 생성된 메타데이터 미리보기
  - 스캔 완료 후 "검토" 버튼으로 메타데이터 수정 페이지 이동

### Phase 3: 일괄 메타데이터 관리 (선택사항)
**목표**: 여러 제품의 메타데이터를 한 번에 관리

#### 3.1 백엔드 API
- `GET /api/products/metadata-review` - 검토가 필요한 제품 목록
- `PUT /api/products/bulk-update` - 여러 제품 일괄 업데이트

#### 3.2 프론트엔드 UI
- **새 페이지: MetadataReview.vue**
  - AI 생성 메타데이터 품질 검토 대시보드
  - 테이블 형식으로 여러 제품 표시
  - 인라인 편집 기능
  - "승인", "수정 필요" 플래그 설정

---

## UI/UX 설계

### 1. 제품 상세 페이지 편집 모달

#### 레이아웃 구성
```
┌─────────────────────────────────────────┐
│  제품 편집                     [X]       │
├─────────────────────────────────────────┤
│                                          │
│  [아이콘 프리뷰]                         │
│                                          │
│  제품명 *                                │
│  ┌────────────────────────────────────┐ │
│  │ Adobe Photoshop                    │ │
│  └────────────────────────────────────┘ │
│                                          │
│  설명                                    │
│  ┌────────────────────────────────────┐ │
│  │ 전문가용 사진 편집 및 그래픽 디자인 │ │
│  │ 소프트웨어                          │ │
│  └────────────────────────────────────┘ │
│                                          │
│  제조사                                  │
│  ┌────────────────────────────────────┐ │
│  │ Adobe                              │ │
│  └────────────────────────────────────┘ │
│                                          │
│  카테고리 *                              │
│  ┌────────────────────────────────────┐ │
│  │ Graphics          ▼                │ │
│  └────────────────────────────────────┘ │
│                                          │
│  아이콘 URL                              │
│  ┌────────────────────────────────────┐ │
│  │ /static/icons/adobe-photoshop.png  │ │
│  └────────────────────────────────────┘ │
│  또는 [파일 선택]                        │
│                                          │
│  ┌──────────────────┐ ┌──────────────┐ │
│  │   취소           │ │  저장        │ │
│  └──────────────────┘ └──────────────┘ │
└─────────────────────────────────────────┘
```

#### 주요 기능
- **유효성 검증**: 필수 필드 입력 확인
- **변경 사항 표시**: 원래 값과 다르면 하이라이트
- **아이콘 업로드**: 로컬 파일 업로드 시 자동으로 `/static/icons/` 저장
- **카테고리 도움말**: 각 카테고리 설명 툴팁 제공

### 2. 스캔 진행 상황 표시 (Phase 2)

#### 실시간 로그 뷰
```
┌──────────────────────────────────────────────────┐
│  스캔 진행 중... (15/42)                         │
├──────────────────────────────────────────────────┤
│                                                   │
│  ✓ /library/Adobe/Photoshop_2024                │
│    - 제품: Adobe Photoshop                       │
│    - 카테고리: Graphics                          │
│    - 제조사: Adobe                               │
│    - 아이콘: ✓ 다운로드 완료                     │
│                                                   │
│  ✓ /library/Microsoft/Office_365                │
│    - 제품: Microsoft Office 365                  │
│    - 카테고리: Office                            │
│    - 제조사: Microsoft                           │
│    - 아이콘: ✓ 다운로드 완료                     │
│                                                   │
│  ⏳ /library/AutoCAD/AutoCAD_2024                │
│    - AI 메타데이터 생성 중...                    │
│                                                   │
│  ⚠ /library/Unknown/setup.exe                   │
│    - 경고: 제조사를 확인할 수 없음               │
│    - Fallback: Uncategorized                     │
│                                                   │
└──────────────────────────────────────────────────┘
```

### 3. 메타데이터 상태 표시

#### 제품 카드 뱃지
```
┌─────────────────────────┐
│  [아이콘]              │
│                         │
│  Adobe Photoshop        │
│  Adobe                  │
│                         │
│  [AI 생성] [검토 완료]  │  ← 상태 뱃지
└─────────────────────────┘
```

**뱃지 종류**:
- 🤖 **AI 생성**: AI가 자동으로 생성한 메타데이터 (파란색)
- ✓ **검토 완료**: 관리자가 확인/수정한 메타데이터 (초록색)
- ⚠ **수동 입력**: AI 없이 Fallback으로 생성된 메타데이터 (노란색)

---

## 백엔드 API 설계

### 1. 제품 업데이트 API

#### `PUT /api/products/{product_id}`
제품 메타데이터 업데이트 (관리자 전용)

**Request Body**:
```json
{
  "title": "Adobe Photoshop 2024",
  "description": "전문가용 사진 편집 및 그래픽 디자인 소프트웨어",
  "vendor": "Adobe",
  "category": "Graphics",
  "icon_url": "/static/icons/adobe-photoshop.png"
}
```

**Response**:
```json
{
  "message": "Product updated successfully",
  "product": {
    "id": 1,
    "title": "Adobe Photoshop 2024",
    "description": "전문가용 사진 편집 및 그래픽 디자인 소프트웨어",
    "vendor": "Adobe",
    "category": "Graphics",
    "icon_url": "/static/icons/adobe-photoshop.png",
    "folder_path": "/library/Adobe/Photoshop_2024"
  }
}
```

**권한**: Admin only (`get_current_admin_user`)

### 2. 버전 업데이트 API

#### `PUT /api/products/{product_id}/versions/{version_id}`
버전 메타데이터 업데이트 (관리자 전용)

**Request Body**:
```json
{
  "version_name": "2024.1",
  "release_date": "2024-01-15T00:00:00Z"
}
```

**Response**:
```json
{
  "message": "Version updated successfully",
  "version": {
    "id": 1,
    "product_id": 1,
    "version_name": "2024.1",
    "file_name": "photoshop_2024.dmg",
    "file_path": "/library/Adobe/Photoshop_2024/photoshop_2024.dmg",
    "file_size": 3221225472,
    "release_date": "2024-01-15T00:00:00Z"
  }
}
```

### 3. 아이콘 업로드 API (선택사항)

#### `POST /api/products/{product_id}/upload-icon`
제품 아이콘 이미지 업로드

**Request**: `multipart/form-data`
- `file`: 이미지 파일 (PNG, JPG, SVG)

**Response**:
```json
{
  "message": "Icon uploaded successfully",
  "icon_url": "/static/icons/custom-product-123.png"
}
```

### 4. 스캔 진행 상황 API (Phase 2)

#### `GET /api/scan/status` (SSE)
Server-Sent Events를 통한 실시간 스캔 진행 상황 스트리밍

**Event Types**:
```json
// 스캔 시작
{"type": "scan_started", "total_items": 42}

// 제품 발견
{"type": "product_found", "path": "/library/Adobe/Photoshop_2024"}

// 메타데이터 생성 중
{"type": "metadata_generating", "path": "/library/Adobe/Photoshop_2024"}

// 메타데이터 생성 완료
{
  "type": "metadata_generated",
  "product": {
    "title": "Adobe Photoshop 2024",
    "category": "Graphics",
    "vendor": "Adobe",
    "icon_cached": true
  }
}

// 에러 발생
{"type": "error", "path": "/library/Unknown/setup.exe", "error": "Could not determine vendor"}

// 스캔 완료
{
  "type": "scan_completed",
  "summary": {
    "new_products": 5,
    "new_versions": 12,
    "ai_generated": 15,
    "icons_cached": 14,
    "errors": 2
  }
}
```

---

## 구현 단계

### Step 1: 백엔드 API 구현
**예상 시간**: 2-3시간

1. `backend/app/api/products.py`에 다음 엔드포인트 추가:
   - `PUT /api/products/{product_id}`
   - `PUT /api/products/{product_id}/versions/{version_id}`

2. `backend/app/schemas/product.py`에 다음 스키마 추가:
   - `ProductUpdateRequest`
   - `VersionUpdateRequest`

3. 유효성 검증 로직:
   - 카테고리가 허용된 목록에 있는지 확인
   - 필수 필드(title, category) 체크
   - 파일 경로는 수정 불가능하도록 제한

4. 테스트:
   - FastAPI Swagger UI (`/docs`)에서 API 테스트
   - 권한 검증 (일반 사용자는 403 에러)

### Step 2: 프론트엔드 API 클라이언트
**예상 시간**: 30분

1. `frontend/src/api/products.js`에 함수 추가:
   ```javascript
   updateProduct: (id, data) => client.put(`/products/${id}`, data)
   updateVersion: (productId, versionId, data) => client.put(`/products/${productId}/versions/${versionId}`, data)
   ```

### Step 3: 제품 편집 모달 UI
**예상 시간**: 3-4시간

1. `frontend/src/components/ProductEditModal.vue` 생성:
   - 제품 메타데이터 편집 폼
   - 카테고리 드롭다운 (설정에서 불러오기)
   - 유효성 검증
   - 저장/취소 버튼

2. `ProductDetail.vue` 수정:
   - 관리자에게만 "편집" 버튼 표시 (`authStore.user.role === 'admin'`)
   - 편집 모달 통합
   - 저장 후 데이터 새로고침

3. 스타일링:
   - 다크 모드 지원
   - 반응형 디자인
   - 에러/성공 메시지 표시

### Step 4: 버전 편집 기능 (선택사항)
**예상 시간**: 2시간

1. `ProductDetail.vue`의 "버전" 탭 개선:
   - 각 버전에 편집 아이콘 추가
   - 버전 편집 인라인 폼 또는 모달
   - `version_name`, `release_date` 수정 가능

### Step 5: 메타데이터 상태 뱃지
**예상 시간**: 1-2시간

1. Product 모델에 `metadata_source` 필드 추가 (선택사항):
   - 마이그레이션 생성
   - `ai_generated`, `manual`, `reviewed` 상태 추적

2. `Discover.vue` 카드에 뱃지 표시:
   - AI 생성 뱃지
   - 수동 입력 뱃지

3. `ProductDetail.vue`에도 뱃지 표시

### Step 6: 스캔 진행 상황 표시 (Phase 2, 선택사항)
**예상 시간**: 4-6시간

1. 백엔드에 SSE 엔드포인트 추가:
   - `backend/app/api/scan.py`에 `/scan/status` 추가
   - `FileScanner`를 수정하여 진행 상황 이벤트 발생

2. 프론트엔드에 EventSource 통합:
   - `Admin.vue`에 실시간 로그 컴포넌트 추가
   - 스캔 시작 시 SSE 연결
   - 진행 상황 표시

---

## 추가 고려사항

### 1. 아이콘 관리
- **업로드 기능**: 사용자가 직접 아이콘 업로드 가능
- **아이콘 저장소**: `/app/static/icons/` 또는 별도 스토리지
- **파일명 규칙**: `{vendor}-{title}.png` (소문자, 공백은 하이픈)

### 2. 메타데이터 품질 검증
- **AI 신뢰도 점수** (선택사항): AI 응답에 confidence score 추가
- **자동 플래그**: 신뢰도가 낮으면 "검토 필요" 플래그
- **사용자 피드백**: "이 메타데이터가 정확한가요?" 버튼

### 3. 성능 최적화
- **일괄 업데이트**: 여러 제품을 한 번에 수정할 때 트랜잭션 사용
- **캐싱**: 카테고리 목록, 제조사 목록 캐싱
- **이미지 최적화**: 아이콘 자동 리사이징 (예: 256x256px)

### 4. 보안
- **권한 검증**: 모든 수정 API는 관리자 전용
- **입력 검증**: XSS 방지를 위한 HTML 이스케이프
- **파일 업로드 제한**: 이미지 파일만 허용, 크기 제한 (1MB)

### 5. 사용성
- **변경 이력** (선택사항): 누가 언제 무엇을 수정했는지 로그
- **되돌리기** (선택사항): 이전 메타데이터로 복원
- **일괄 작업** (선택사항): 여러 제품의 카테고리 한 번에 변경

---

## 예상 일정

### Phase 1: 기본 편집 기능 (권장 우선순위)
- **Step 1-3**: 1-2일
- **목표**: 관리자가 제품 메타데이터를 수정할 수 있는 기본 기능 완성

### Phase 2: 스캔 진행 표시 (선택사항)
- **Step 6**: 1일
- **목표**: 스캔 중 메타데이터 생성 과정 실시간 확인

### Phase 3: 고급 기능 (선택사항)
- **메타데이터 품질 대시보드**: 1-2일
- **일괄 편집 기능**: 1일

---

## 데이터베이스 변경 (선택사항)

### 메타데이터 출처 추적
```python
# backend/app/models/product.py
class Product(Base):
    __tablename__ = "products"

    # 기존 필드들...

    # 새 필드 추가
    metadata_source = Column(String, default="ai")  # ai, manual, reviewed
    last_edited_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    last_edited_at = Column(DateTime(timezone=True), nullable=True)
```

### 마이그레이션
```bash
# Alembic 마이그레이션 생성
alembic revision -m "add metadata tracking fields"

# 마이그레이션 적용
alembic upgrade head
```

---

## 참고 자료

### 관련 파일
- Backend:
  - `backend/app/models/product.py` - Product 모델
  - `backend/app/models/version.py` - Version 모델
  - `backend/app/api/products.py` - Product API
  - `backend/app/core/ai_metadata.py` - AI 메타데이터 생성기
  - `backend/app/core/scanner.py` - 파일 스캐너

- Frontend:
  - `frontend/src/views/ProductDetail.vue` - 제품 상세 페이지
  - `frontend/src/views/Discover.vue` - 제품 목록 페이지
  - `frontend/src/views/Admin.vue` - 관리자 페이지
  - `frontend/src/api/products.js` - Product API 클라이언트

### 현재 카테고리 목록
```javascript
const categories = [
  { name: 'Graphics', label: '그래픽', icon: '🎨' },
  { name: 'Office', label: '오피스', icon: '📊' },
  { name: 'Development', label: '개발', icon: '💻' },
  { name: 'Utility', label: '유틸리티', icon: '🛠️' },
  { name: 'Media', label: '미디어', icon: '🎬' },
  { name: 'OS', label: '운영체제', icon: '💿' },
  { name: 'Security', label: '보안', icon: '🔒' },
  { name: 'Network', label: '네트워크', icon: '🌐' },
  { name: 'Mac', label: '맥', icon: '🍎' },
  { name: 'Mobile', label: '모바일', icon: '📱' },
  { name: 'Patch', label: '패치', icon: '🔧' },
  { name: 'Driver', label: '드라이버', icon: '⚙️' },
  { name: 'Source', label: '소스', icon: '📦' },
  { name: 'Backup', label: '백업&복구', icon: '💾' },
  { name: 'Portable', label: '포터블', icon: '🎒' },
  { name: 'Business', label: '업무용', icon: '💼' },
  { name: 'Engineering', label: '공학용', icon: '📐' },
  { name: 'Theme', label: '테마&스킨', icon: '🎭' },
  { name: 'Hardware', label: '하드웨어', icon: '🔌' },
  { name: 'Uncategorized', label: '미분류', icon: '📂' }
]
```

---

## 결론

이 계획서는 메타데이터 관리 기능을 단계적으로 구현할 수 있도록 설계되었습니다.

**권장 구현 순서**:
1. **Phase 1** (필수): 기본 편집 기능 - 가장 중요하고 즉시 활용 가능
2. **Phase 2** (선택): 스캔 진행 표시 - 사용자 경험 개선
3. **Phase 3** (선택): 고급 기능 - 대규모 라이브러리 관리 시 유용

각 단계는 독립적으로 구현 가능하며, Phase 1만으로도 충분한 가치를 제공합니다.
