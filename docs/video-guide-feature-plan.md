# 설치안내 동영상 기능 구현 계획서 (v3)

> 작성일: 2026-03-01
> 버전: v1.4.22 이후 적용 예정
> 변경: 검색된 목록 분류에 "설치영상" 추가 + data/videos 통합 서빙

---

## 1. 개요

제품 상세페이지 **"설치방법" 탭 하단**에 동영상 섹션을 추가한다.
동영상은 두 가지 경로로 등록 가능하다:

1. **직접 업로드**: 관리자가 ProductDetail 페이지에서 로컬 파일 업로드
2. **검색된 목록 연동**: ScanList에서 분류를 "설치영상"으로 지정 후 제품에 등록

두 경로 모두 최종적으로 `data/videos/{product_id}/` 에 저장되고,
`/static/videos/` 엔드포인트로 Video.js가 스트리밍 재생한다.

---

## 2. 전체 흐름

### 경로 A: 직접 업로드

```
[ProductDetail - 설치방법 탭]
  관리자: 파일 선택 또는 드래그 앤 드롭
      ↓
  POST /api/product-videos/upload/{product_id}
      ↓
  data/videos/{product_id}/{timestamp}_{filename} 저장
      ↓
  product_videos DB 레코드 생성
      ↓
  /static/videos/{product_id}/{filename} 로 Video.js 재생
```

### 경로 B: 검색된 목록에서 등록

```
[ScanList - 검색된 목록]
  파일 분류 변경 → "설치영상" 선택
      ↓
  등록 다이얼로그 오픈
  제품 선택 + 영상 제목 입력 (선택)
      ↓
  POST /api/scan-items/{id}/register
       (classification == "installation_video")
      ↓  [백엔드 _register_as_video()]
  원본 파일 → data/videos/{product_id}/{filename} 복사
  product_videos DB 레코드 생성
  FilenameViolation.is_resolved = True
      ↓
  ProductDetail 설치방법 탭에서 Video.js 재생
```

### 통합 서빙 구조

```
data/videos/{product_id}/파일.mp4
         ↕ (FastAPI StaticFiles)
/static/videos/{product_id}/파일.mp4
         ↕ (Video.js HTTP Range Request 지원)
[브라우저 Video.js 플레이어]
```

---

## 3. "설치방법" 탭 최종 UI 구조

```
┌─────────────────────────────────────────────┐
│  설치방법 탭                                  │
│                                             │
│  ⚙️ 설치 가이드              [작성/편집/삭제] │  ← 기존 (변경 없음)
│  ─────────────────────────────────────────  │
│  TinyMCE HTML 뷰어 or 편집기                 │
│  (없으면: "아직 작성된 가이드 없음")           │
│                                             │
│  ━━━━━━━━━━━━ 구분선 ━━━━━━━━━━━━━━━━━━━━━  │
│                                             │
│  🎬 설치 안내 영상           [업로드] (관리)  │  ← 신규
│  ─────────────────────────────────────────  │
│  ┌────────────────────────────────────┐     │
│  │ ▶ Video.js 플레이어 (16:9)         │     │
│  │   영상 제목 / 설명 / 날짜 / 크기   │     │
│  │   [관리자] 편집 | 삭제             │     │
│  └────────────────────────────────────┘     │
│  ┌────────────────────────────────────┐     │
│  │ ▶ Video.js 플레이어 - 영상 2       │     │
│  └────────────────────────────────────┘     │
│  (영상 없으면: "등록된 영상이 없습니다")      │
└─────────────────────────────────────────────┘
```

---

## 4. 데이터베이스

### 신규 테이블: `product_videos`

```sql
CREATE TABLE product_videos (
    id          SERIAL PRIMARY KEY,
    product_id  INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    title       VARCHAR(200) NOT NULL DEFAULT '',
    description TEXT,
    file_path   VARCHAR NOT NULL,   -- data/videos/{pid}/{filename} 절대 경로
    file_name   VARCHAR NOT NULL,   -- 실제 저장 파일명
    file_size   BIGINT DEFAULT 0,
    mime_type   VARCHAR DEFAULT 'video/mp4',
    sort_order  INTEGER DEFAULT 0,
    source      VARCHAR DEFAULT 'upload',  -- 'upload' | 'scan'  (출처 구분)
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ix_product_videos_product_id ON product_videos(product_id);
```

> **source 컬럼**: 직접 업로드('upload')와 스캔 등록('scan') 구분.
> 삭제 시 'upload'는 파일도 삭제, 'scan'은 원본 보존을 위해 파일 삭제 여부 선택 가능.

### entrypoint.sh 자동 생성 (Alembic 미사용 환경)

```bash
python -c "
import psycopg2, os
conn = psycopg2.connect(os.environ['DATABASE_URL'])
cur = conn.cursor()
cur.execute('''
  CREATE TABLE IF NOT EXISTS product_videos (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL DEFAULT \\'\\',
    description TEXT,
    file_path VARCHAR NOT NULL,
    file_name VARCHAR NOT NULL,
    file_size BIGINT DEFAULT 0,
    mime_type VARCHAR DEFAULT \\'video/mp4\\',
    sort_order INTEGER DEFAULT 0,
    source VARCHAR DEFAULT \\'upload\\',
    created_at TIMESTAMPTZ DEFAULT NOW()
  );
  CREATE INDEX IF NOT EXISTS ix_product_videos_product_id
    ON product_videos(product_id);
''')
conn.commit(); cur.close(); conn.close()
print('[OK] product_videos table ready')
"
```

---

## 5. 백엔드 구현

### 5-1. 신규/수정 파일

| 파일 | 유형 | 내용 |
|---|---|---|
| `backend/app/models/product_video.py` | **신규** | SQLAlchemy 모델 |
| `backend/app/schemas/product_video.py` | **신규** | Pydantic 스키마 |
| `backend/app/api/product_videos.py` | **신규** | CRUD API 라우터 |
| `backend/app/config.py` | 수정 | `VIDEOS_DIR` 추가 |
| `backend/app/main.py` | 수정 | static 마운트 + 라우터 등록 |
| `backend/app/api/filename_violations.py` | 수정 | `installation_video` 분류 처리 추가 |
| `backend/entrypoint.sh` | 수정 | 테이블 자동 생성 추가 |

### 5-2. config.py

```python
VIDEOS_DIR: str = "/home/nuricom/project/myappStore/data/videos"
```

### 5-3. main.py

```python
# Static 마운트 추가
(settings.VIDEOS_DIR, "/static/videos", "videos"),

# 라우터 등록
from app.api import product_videos
app.include_router(product_videos.router, tags=["product-videos"])
```

### 5-4. product_videos.py API 엔드포인트

#### `GET /api/product-videos/{product_id}`
- 인증: 로그인 사용자
- 응답: `List[ProductVideoSchema]` (sort_order 오름차순)
- 각 항목에 `url: /static/videos/{product_id}/{file_name}` 포함

#### `POST /api/product-videos/upload/{product_id}`
- 인증: 관리자
- Body: `multipart/form-data`
  - `file`: 동영상 파일
  - `title`: 제목 (선택, 기본값: 파일명에서 확장자 제거)
  - `description`: 설명 (선택)
- 허용 MIME: `video/mp4`, `video/webm`, `video/ogg`, `video/quicktime`
- 허용 확장자: `.mp4`, `.webm`, `.ogg`, `.mov`
- 파일 크기 제한: **500MB**
- 저장: `data/videos/{product_id}/{timestamp}_{random}{ext}`
- source: `'upload'`

#### `PATCH /api/product-videos/{video_id}`
- 인증: 관리자
- Body: `{ "title"?, "description"?, "sort_order"? }` (partial)

#### `DELETE /api/product-videos/{video_id}`
- 인증: 관리자
- source == 'upload': 파일 삭제 + DB 삭제
- source == 'scan': DB 삭제만 (원본 파일 보존)

### 5-5. filename_violations.py 수정 — "설치영상" 등록 처리

**① VALID_CLASSIFICATIONS에 추가 (line 35)**
```python
# 기존
VALID_CLASSIFICATIONS = {"product", "patch", "language_pack", "manual", "update"}
# 변경
VALID_CLASSIFICATIONS = {"product", "patch", "language_pack", "manual", "update", "installation_video"}
```

**② register 엔드포인트에 분기 추가 (line 199 근처)**
```python
if item.classification == "product":
    return await _register_as_product(item, db)

# 신규: 설치영상 분기
if item.classification == "installation_video":
    if not request.product_id:
        raise HTTPException(status_code=400, detail="product_id가 필요합니다.")
    return await _register_as_video(item, request.product_id, request.note, db)

# 기존: 나머지 분류 (patch/language_pack/manual/update)
return await _register_as_attachment(item, request.product_id, request.note, db)
```

**③ _register_as_video() 함수 추가**
```python
async def _register_as_video(
    item: FilenameViolation,
    product_id: int,
    note: Optional[str],
    db: Session,
):
    """installation_video 분류 항목을 ProductVideo로 등록 (파일 복사)"""
    from app.models.product_video import ProductVideo
    from app.config import settings
    import shutil

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="제품을 찾을 수 없습니다.")

    src_path = Path(item.folder_path) / item.file_name
    if not src_path.exists():
        raise HTTPException(status_code=404, detail=f"파일을 찾을 수 없습니다: {src_path}")

    # 중복 확인
    existing = db.query(ProductVideo).filter(
        ProductVideo.product_id == product_id,
        ProductVideo.file_name == item.file_name,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="이 파일은 이미 해당 제품의 설치영상으로 등록되어 있습니다.")

    # data/videos/{product_id}/ 에 복사
    dest_dir = Path(settings.VIDEOS_DIR) / str(product_id)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / item.file_name

    # 파일명 충돌 처리
    counter = 1
    while dest_path.exists():
        stem, ext = os.path.splitext(item.file_name)
        dest_path = dest_dir / f"{stem}_{counter}{ext}"
        counter += 1

    shutil.copy2(str(src_path), str(dest_path))

    # MIME 타입 결정
    ext = Path(item.file_name).suffix.lower()
    mime_map = {'.mp4': 'video/mp4', '.webm': 'video/webm',
                '.ogg': 'video/ogg', '.mov': 'video/quicktime'}
    mime_type = mime_map.get(ext, 'video/mp4')

    title = note or Path(item.file_name).stem  # note를 제목으로 활용

    video = ProductVideo(
        product_id=product_id,
        title=title,
        file_path=str(dest_path),
        file_name=dest_path.name,
        file_size=dest_path.stat().st_size,
        mime_type=mime_type,
        source='scan',
    )
    db.add(video)

    item.is_resolved = True
    item.product_id = product_id
    item.violation_details = "설치영상 등록 완료"

    db.commit()
    db.refresh(video)

    return {
        "success": True,
        "message": "설치 안내 영상이 등록되었습니다.",
        "video_id": video.id,
        "product_id": product_id,
    }
```

---

## 6. 검색된 목록 (ScanList) 수정

### 6-1. 수정 파일

| 파일 | 내용 |
|---|---|
| `frontend/src/views/ScanList.vue` | classifications 배열에 "설치영상" 추가, 등록 다이얼로그 note 입력 필드를 영상 제목으로 활용 |
| `frontend/src/locales/ko.js` | `classification.installation_video` 텍스트 추가 |
| `frontend/src/locales/en.js` | 영문 텍스트 추가 |

### 6-2. ScanList.vue classifications 배열 추가

```javascript
const classifications = computed(() => [
  { key: 'product',             icon: '📦', label: t('scanList.classification.product'),            ... },
  { key: 'patch',               icon: '🔧', label: t('scanList.classification.patch'),              ... },
  { key: 'language_pack',       icon: '🌐', label: t('scanList.classification.language_pack'),      ... },
  { key: 'manual',              icon: '📖', label: t('scanList.classification.manual'),             ... },
  { key: 'update',              icon: '🔄', label: t('scanList.classification.update'),             ... },
  // ── 신규 ──
  { key: 'installation_video',  icon: '🎬', label: t('scanList.classification.installation_video'), ... },
])
```

### 6-3. 등록 다이얼로그에서 "설치영상" 처리

- 등록 다이얼로그는 기존 구조 그대로 사용 (제품 선택 + note 입력)
- `classification == 'installation_video'` 일 때:
  - note 입력 라벨을 **"영상 제목 (선택)"** 으로 변경 표시
  - note 값이 백엔드에서 ProductVideo.title 로 사용됨
  - 안내 문구 추가: "선택한 파일이 data/videos/ 에 복사되어 설치 안내 영상으로 등록됩니다"

### 6-4. submitRegister() 흐름 변경 없음

기존 `filenameViolationsApi.registerAsAttachment()` 호출 그대로 사용.
백엔드가 classification을 보고 `_register_as_video()` 또는 `_register_as_attachment()`로 분기 처리.

### 6-5. 통계 표시 (Stats)

- `stats.by_classification.installation_video` 카운트 표시
- 필터 탭에 "🎬 설치영상 (N)" 탭 추가

---

## 7. Video.js 로컬 설치

### 파일 배치

```
frontend/public/videojs/
├── video.min.js        ← Video.js 8.x 빌드 파일
├── video-js.min.css    ← Video.js 스타일
└── lang/
    └── ko.js           ← 한국어 UI (선택)
```

### 다운로드 방법

```bash
# GitHub Releases에서 video.js 최신 안정 버전 dist 다운로드
# https://github.com/videojs/video.js/releases
# → video.js-{ver}.zip → dist/video.min.js, dist/video-js.min.css 추출
# → frontend/public/videojs/ 에 배치
```

### 지원 포맷

| 확장자 | MIME | 브라우저 지원 |
|---|---|---|
| `.mp4` | `video/mp4` | 모든 브라우저 ✅ |
| `.webm` | `video/webm` | Chrome/Firefox ✅ |
| `.ogg` | `video/ogg` | Firefox ✅ |
| `.mov` | `video/quicktime` | Safari (제한적) |

---

## 8. 프론트엔드 구현

### 8-1. 신규/수정 파일

| 파일 | 유형 | 내용 |
|---|---|---|
| `frontend/src/api/productVideos.js` | **신규** | API 클라이언트 |
| `frontend/src/components/product/VideoGuideSection.vue` | **신규** | 영상 섹션 전체 컨테이너 |
| `frontend/src/components/product/VideoPlayer.vue` | **신규** | Video.js 개별 플레이어 |
| `frontend/src/views/ProductDetail.vue` | 수정 | 설치방법 탭 끝에 섹션 추가 |
| `frontend/src/views/ScanList.vue` | 수정 | classification 배열 + 다이얼로그 UI |
| `frontend/src/locales/ko.js` | 수정 | 신규 텍스트 추가 |
| `frontend/src/locales/en.js` | 수정 | 신규 텍스트 추가 |

### 8-2. API 클라이언트 (productVideos.js)

```javascript
import client from './client'

export const productVideosApi = {
  // 영상 목록 조회
  getVideos: (productId) =>
    client.get(`/product-videos/${productId}`),

  // 직접 업로드
  upload: (productId, formData, onProgress) =>
    client.post(`/product-videos/upload/${productId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => onProgress?.(Math.round(e.loaded * 100 / e.total)),
    }),

  // 영상 정보 수정 (제목/설명/순서)
  update: (videoId, data) =>
    client.patch(`/product-videos/${videoId}`, data),

  // 영상 삭제
  delete: (videoId) =>
    client.delete(`/product-videos/${videoId}`),
}
```

### 8-3. ProductDetail.vue 수정 위치

설치방법 탭 HTML 기존 끝부분 (line 971~972):
```html
<!-- 기존 마지막 줄 -->
<div v-else class="prose ... tinymce-content" v-html="product.installation_guide"></div>

<!-- ↓ 바로 아래 추가 (installation 탭 닫는 </div> 바로 앞) -->
<!-- 구분선 -->
<div class="border-t border-gray-200 dark:border-gray-700 mt-6 sm:mt-8 pt-6 sm:pt-8">
  <VideoGuideSection
    :product-id="product.id"
    :is-admin="authStore.user?.role === 'admin'"
  />
</div>
```

스크립트에 import 추가:
```javascript
import VideoGuideSection from '../components/product/VideoGuideSection.vue'
```

### 8-4. VideoGuideSection.vue 구조

```
상태:
  videos[]          ← API 로드
  uploading         ← 업로드 진행 중
  uploadProgress    ← 0~100
  isDragging        ← 드래그 중 강조

onMounted: loadVideos()

[관리자 영역]
  드래그 앤 드롭 존
    @drop → handleDrop()
    파일 선택 버튼
  업로드 진행바 (uploading 중)

[영상 목록]
  VideoPlayer v-for="video in videos"
    :video="video"
    :is-admin="isAdmin"
    @deleted="loadVideos"
    @updated="loadVideos"

[빈 상태]
  "등록된 설치 안내 영상이 없습니다"
  관리자: "위 영역에서 업로드하거나, 검색된 목록에서 설치영상으로 분류 후 등록하세요"
```

### 8-5. VideoPlayer.vue 구조

```
props: { video, isAdmin }
emits: ['deleted', 'updated']

onMounted:
  1. window.videojs 없으면 video.min.js + video-js.min.css 동적 로드
  2. videojs(`#vjs-${video.id}`, { fluid, controls, playbackRates, language })

onBeforeUnmount:
  player.dispose()

template:
  <div class="rounded-xl overflow-hidden bg-black">
    <video
      :id="`vjs-${video.id}`"
      class="video-js vjs-big-play-centered vjs-theme-city"
      controls
      preload="metadata"
    >
      <source :src="`/static/videos/${video.product_id}/${video.file_name}`"
              :type="video.mime_type" />
    </video>
  </div>

  <div class="mt-3 px-1">
    <!-- 제목 (인라인 편집) -->
    <!-- 설명 -->
    <!-- 날짜 / 파일크기 / source 뱃지 -->
    <!-- [관리자] 편집 / 삭제 버튼 -->
  </div>
```

### 8-6. i18n 추가

**ko.js**:
```javascript
// scanList.classification 에 추가
installation_video: '설치영상',

// product.installation 하위에 추가
videoGuide: {
  title: '설치 안내 영상',
  upload: '영상 업로드',
  dropzone: '동영상 파일을 드래그하거나 클릭하여 선택',
  formats: 'MP4, WebM, OGG 지원 · 최대 500MB',
  noVideos: '등록된 설치 안내 영상이 없습니다.',
  noVideosAdmin: '파일을 업로드하거나, 검색된 목록에서 "설치영상"으로 분류 후 등록하세요.',
  uploading: '업로드 중...',
  deleteConfirm: '이 영상을 삭제하시겠습니까?',
  deleteSuccess: '영상이 삭제되었습니다.',
  scanBadge: '스캔 등록',
  uploadBadge: '직접 업로드',
},

// ScanList 등록 다이얼로그 note 라벨 (분류별 분기)
noteForVideo: '영상 제목 (선택, 미입력 시 파일명 사용)',
videoGuideInfo: '파일이 data/videos/ 로 복사되어 설치 안내 영상으로 등록됩니다.',
```

---

## 9. 모바일 전체화면

Video.js 8.x 기본 내장. 추가 CSS (`ProductDetail.vue <style>` 하단):

```css
/* Video.js 반응형 */
:deep(.video-js) {
  width: 100%;
  border-radius: 0.75rem;
  overflow: hidden;
}

/* 재생 버튼 중앙 */
:deep(.video-js .vjs-big-play-button) {
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  margin: 0;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  line-height: 60px;
  border: none;
}

/* 전체화면 진입 시 라운드 제거 */
:deep(.video-js:-webkit-full-screen),
:deep(.video-js:fullscreen) {
  border-radius: 0;
}

@media (max-width: 640px) {
  :deep(.video-js) { border-radius: 0.5rem; }
  :deep(.video-js .vjs-big-play-button) {
    width: 48px; height: 48px; line-height: 48px;
  }
}
```

iOS Safari: `<video>` 에 `playsinline` 속성 미설정 → 기본 전체화면 재생

---

## 10. 파일 저장 구조

```
data/
└── videos/
    ├── 1/                               # product_id = 1
    │   ├── 20260301_120000_a1b2_install.mp4   (직접 업로드)
    │   └── setup_guide.mp4                     (스캔 등록 복사본)
    ├── 2/
    │   └── how_to_install.webm
    └── ...
```

Static 서빙:
```
/static/videos/1/20260301_120000_a1b2_install.mp4
→ data/videos/1/20260301_120000_a1b2_install.mp4
```

---

## 11. Nginx 설정 변경

`frontend/nginx.conf`:
```nginx
client_max_body_size 500m;  # 동영상 업로드 허용 크기
sendfile on;                 # 스트리밍 성능 향상
tcp_nopush on;
```

---

## 12. 구현 순서

### Phase 1: 백엔드
1. `models/product_video.py` 생성
2. `schemas/product_video.py` 생성
3. `api/product_videos.py` 생성 (upload / list / update / delete)
4. `config.py` → `VIDEOS_DIR` 추가
5. `main.py` → static 마운트 + 라우터 등록
6. `api/filename_violations.py` → `installation_video` 분류 처리 추가
   - `VALID_CLASSIFICATIONS` 에 추가
   - register 분기에 `_register_as_video()` 추가
7. `entrypoint.sh` → 테이블 자동 생성 코드 추가

### Phase 2: Video.js 준비
8. Video.js 8.x 다운로드 → `frontend/public/videojs/` 배치
9. `lang/ko.js` 추가

### Phase 3: 프론트엔드
10. `api/productVideos.js` 생성
11. `VideoPlayer.vue` 생성 (Video.js 초기화 + 플레이어 UI)
12. `VideoGuideSection.vue` 생성 (업로드 드롭존 + 플레이어 목록)
13. `ProductDetail.vue` → 설치방법 탭 끝에 구분선 + VideoGuideSection 삽입
14. `ScanList.vue` → classifications 배열에 `installation_video` 추가, 등록 다이얼로그 안내 문구 분기
15. `ko.js` / `en.js` i18n 추가

### Phase 4: Nginx + 빌드
16. `frontend/nginx.conf` → `client_max_body_size 500m` 추가
17. Docker 이미지 빌드 & 푸시
18. 테스트 (직접 업로드, 스캔 등록, 재생, 모바일 전체화면)
19. 버전 업 → GitHub 릴리즈

---

## 13. 고려사항 및 제약

| 항목 | 내용 |
|---|---|
| **파일 크기 제한** | Nginx + FastAPI 모두 500MB 설정 필요 |
| **HTTP Range 지원** | FastAPI StaticFiles 기본 지원 → Video.js seek 가능 |
| **스캔 파일 복사** | 원본 보존을 위해 복사본을 data/videos/에 저장 |
| **삭제 정책** | 직접 업로드: 파일+DB 삭제 / 스캔 등록: DB만 삭제 (복사본도 삭제 가능, source로 구분) |
| **썸네일** | Phase 1: Video.js 기본 (포스터 없음). 추후 ffmpeg로 자동 추출 가능 |
| **중복 방지** | 같은 product_id + file_name 조합 중복 등록 차단 |
| **Video.js 로드** | `window.videojs` 체크 후 1회만 동적 로드 (중복 스크립트 방지) |
| **다중 플레이어** | 각 플레이어를 `vjs-{video.id}` id로 구분, dispose() 누락 방지 |
| **스토리지** | data/ 볼륨 여유 공간 사전 확인 권장 |

---

*본 계획서는 구현 전 검토 및 수정 가능합니다.*
