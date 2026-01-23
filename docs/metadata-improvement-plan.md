# 메타데이터 수집 개선 계획

> 기반 문서: `/스캔 및 메타데이터 설명.md`
> 작성일: 2025-12-16

## 📋 현재 구현 상태 분석

### ✅ 구현 완료
- [x] FilenameParser를 통한 파일명/폴더명 파싱
- [x] OpenAI API를 통한 AI 메타데이터 생성
- [x] 웹 크롤링 (DuckDuckGo 검색, 공식 사이트 크롤링)
- [x] YouTube 영상 검색
- [x] 확장 메타데이터 수집 (system_requirements, supported_os, tags 등)
- [x] 설정 페이지에서 API 키 관리

### ❌ 미구현 (개선 필요)
- [ ] 메타데이터 캐시 정책 (중복 수집 방지)
- [ ] 정확도 측정 및 자동 분류 (90% 기준)
- [ ] 불일치 목록 관리 페이지
- [ ] 수동 메타데이터 검색/입력 기능
- [ ] 예외 목록 설정 (스캔 제외 파일/폴더)
- [ ] 스크린샷 개수 제한 (현재 5개 → 3개로)
- [ ] YouTube 영상 제거 또는 옵션화 (요구사항: 불필요)

---

## 🎯 개선 항목 상세 계획

### 1. 메타데이터 캐시 정책 구현

**목적**: 동일한 소프트웨어에 대해 반복적으로 AI API를 호출하지 않도록 캐싱

**구현 방안**:
```python
# backend/app/models/metadata_cache.py (신규)
class MetadataCache(Base):
    __tablename__ = "metadata_cache"

    id = Column(Integer, primary_key=True)
    software_name = Column(String, unique=True, index=True)  # 정규화된 이름
    metadata_json = Column(JSON)  # 캐시된 메타데이터
    confidence_score = Column(Float)  # 정확도 점수 (0.0 ~ 1.0)
    source = Column(String)  # "ai", "manual", "web"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    hit_count = Column(Integer, default=0)  # 재사용 횟수
```

**적용 로직**:
1. 파일 스캔 시 정규화된 이름으로 캐시 조회
2. 캐시 존재 + 정확도 90% 이상 → 재사용
3. 캐시 없음 또는 낮은 정확도 → AI/웹 크롤링 수행 후 캐시 저장

**장점**:
- API 비용 절감 (동일 프로그램 중복 수집 방지)
- 스캔 속도 향상
- 사용자가 수동으로 수정한 메타데이터도 캐시 가능

---

### 2. 정확도 측정 및 자동 분류

**목적**: AI가 생성한 메타데이터의 신뢰도를 측정하여 90% 이상만 자동 적용

**정확도 계산 방법**:
```python
def calculate_confidence_score(metadata: Dict, parsed_info: Dict) -> float:
    """
    메타데이터 정확도 점수 계산 (0.0 ~ 1.0)

    점수 기준:
    - title이 parsed_name과 유사도 (0.3)
    - vendor 존재 여부 (0.15)
    - description 길이 적정성 (0.15)
    - category가 "Uncategorized"가 아닌지 (0.15)
    - icon_url 존재 여부 (0.1)
    - official_website 존재 여부 (0.15)
    """
    score = 0.0

    # 1. 제목 유사도 (Levenshtein distance 또는 fuzzywuzzy)
    from difflib import SequenceMatcher
    title_similarity = SequenceMatcher(None,
        metadata.get('title', '').lower(),
        parsed_info.get('software_name', '').lower()
    ).ratio()
    score += title_similarity * 0.3

    # 2. Vendor 존재
    if metadata.get('vendor') and metadata['vendor'] != 'Unknown':
        score += 0.15

    # 3. Description 적정성 (100~500자)
    desc_len = len(metadata.get('description', ''))
    if 100 <= desc_len <= 500:
        score += 0.15

    # 4. Category 유효성
    if metadata.get('category') and metadata['category'] != 'Uncategorized':
        score += 0.15

    # 5. Icon URL 존재
    if metadata.get('icon_url'):
        score += 0.1

    # 6. Official website 존재
    if metadata.get('official_website'):
        score += 0.15

    return score
```

**적용 흐름**:
```
파일 스캔
  ↓
메타데이터 생성 (AI + 웹 크롤링)
  ↓
정확도 점수 계산
  ↓
┌─────────────┬─────────────┐
│ ≥ 90%       │ < 90%       │
├─────────────┼─────────────┤
│ 자동 등록   │ 불일치 목록 │
│ (Products)  │ 저장        │
└─────────────┴─────────────┘
```

---

### 3. 불일치 목록 관리 페이지

**목적**: 정확도 90% 미만인 항목을 별도 관리하고 수동 처리 지원

**데이터베이스 모델**:
```python
# backend/app/models/unmatched_item.py (신규)
class UnmatchedItem(Base):
    __tablename__ = "unmatched_items"

    id = Column(Integer, primary_key=True)
    file_path = Column(String, unique=True)
    file_name = Column(String)
    folder_path = Column(String)

    # 파싱 정보
    parsed_name = Column(String)
    parsed_version = Column(String)
    parsed_vendor = Column(String)

    # AI 생성 메타데이터 (참고용)
    suggested_metadata = Column(JSON)
    confidence_score = Column(Float)

    # 상태
    status = Column(String, default="pending")  # pending, reviewed, ignored

    # 수동 입력 메타데이터
    manual_metadata = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
```

**API 엔드포인트**:
```python
# GET /api/unmatched - 불일치 목록 조회
# GET /api/unmatched/{id} - 상세 조회
# POST /api/unmatched/{id}/approve - AI 제안 승인
# POST /api/unmatched/{id}/manual - 수동 메타데이터 입력
# POST /api/unmatched/{id}/search - 수동 검색 (AI 재쿼리)
# DELETE /api/unmatched/{id} - 무시
```

**프론트엔드 페이지**:
```
/admin/unmatched
├── 필터: 전체/대기중/검토완료/무시
├── 테이블:
│   ├── 파일명
│   ├── 파싱된 이름
│   ├── 정확도
│   ├── AI 제안 (미리보기)
│   └── 액션 (승인/수정/재검색/무시)
└── 상세 다이얼로그:
    ├── 원본 정보 (파일명, 경로)
    ├── 파싱 결과
    ├── AI 제안 메타데이터 (편집 가능)
    ├── 수동 검색 버튼
    └── 저장/무시 버튼
```

---

### 4. 수동 메타데이터 검색/입력 기능

**목적**: 불일치 항목에 대해 관리자가 직접 검색하거나 입력

**기능 구성**:

1. **수동 검색**:
   - 소프트웨어 이름 입력 → AI 재쿼리
   - 여러 후보 제시 (top 3)
   - 관리자가 선택

2. **수동 입력 폼**:
   ```
   [ 제목       ] ___________________
   [ 제조사     ] ___________________
   [ 카테고리   ] [드롭다운]
   [ 설명       ]
   ┌────────────────────────────────┐
   │                                │
   │  (텍스트 에리어)               │
   └────────────────────────────────┘
   [ 공식 사이트 ] ___________________
   [ 아이콘 URL  ] ___________________

   [저장] [취소]
   ```

3. **외부 검색 링크**:
   - Google 검색 바로가기
   - 공식 사이트 찾기 도우미

---

### 5. 예외 목록 설정

**목적**: 특정 파일/폴더를 스캔에서 제외

**설정 UI** (Settings.vue에 추가):
```vue
<div class="exception-settings">
  <h3>🚫 스캔 예외 목록</h3>

  <!-- 파일명 패턴 -->
  <div class="exception-patterns">
    <label>제외할 파일명 패턴 (한 줄에 하나씩)</label>
    <textarea v-model="exceptionPatterns" rows="5">
      *.txt
      *.log
      Thumbs.db
      .DS_Store
      desktop.ini
    </textarea>
  </div>

  <!-- 폴더명 패턴 -->
  <div class="exception-folders">
    <label>제외할 폴더명</label>
    <textarea v-model="exceptionFolders" rows="5">
      .git
      node_modules
      __MACOSX
      $RECYCLE.BIN
    </textarea>
  </div>

  <!-- 특정 경로 -->
  <div class="exception-paths">
    <label>제외할 전체 경로</label>
    <div v-for="(path, idx) in exceptionPaths" :key="idx">
      <input v-model="exceptionPaths[idx]" />
      <button @click="removeExceptionPath(idx)">삭제</button>
    </div>
    <button @click="addExceptionPath">경로 추가</button>
  </div>
</div>
```

**백엔드 적용**:
```python
# backend/app/core/scanner.py
class FileScanner:
    def should_exclude(self, file_path: str, config: Dict) -> bool:
        """파일이 예외 목록에 포함되는지 확인"""
        import fnmatch

        # 패턴 매칭
        for pattern in config.get('exception_patterns', []):
            if fnmatch.fnmatch(os.path.basename(file_path), pattern):
                return True

        # 폴더명 체크
        path_parts = file_path.split(os.sep)
        for folder in config.get('exception_folders', []):
            if folder in path_parts:
                return True

        # 전체 경로 체크
        for exc_path in config.get('exception_paths', []):
            if file_path.startswith(exc_path):
                return True

        return False
```

---

### 6. 스크린샷 개수 제한 (5개 → 3개)

**간단한 수정**:

```python
# backend/app/core/web_crawler.py
def _extract_image_urls(self, html: str, base_url: str) -> List[str]:
    # ...

    # 우선순위 이미지가 있으면 그것을 먼저, 없으면 일반 이미지
    if priority_screenshots:
        return priority_screenshots[:3]  # 5 → 3

    return screenshots[:3]  # 5 → 3
```

```python
# backend/app/api/metadata.py
metadata['screenshots'] = crawl_data.get('screenshots', [])[:3]
```

---

### 7. YouTube 영상 처리

**요구사항**: 유튜브 영상은 필요없음

**옵션 1: 완전 제거**
- `search_youtube_video()` 메서드 제거
- 관련 코드 삭제

**옵션 2: 설정으로 옵션화** (권장)
```python
# config.json
{
  "metadata": {
    "extendedFields": {
      "video_url": false  // 기본값 false로 변경
    }
  }
}
```

- 기본적으로 비활성화
- 필요시 설정에서 활성화 가능
- 테스트 다이얼로그에서는 체크박스로 제어

**→ 옵션 2 추천** (유연성 유지)

---

## 📅 구현 우선순위

### Phase 1: 핵심 기능 (즉시)
1. **스크린샷 3개 제한** - 5분
2. **YouTube 기본 비활성화** - 10분
3. **메타데이터 캐시 모델 추가** - 30분
4. **정확도 계산 로직 구현** - 1시간

### Phase 2: 불일치 관리 (1주)
1. **UnmatchedItem 모델 추가** - 30분
2. **불일치 API 엔드포인트** - 2시간
3. **불일치 관리 페이지 UI** - 4시간
4. **수동 검색/입력 기능** - 3시간

### Phase 3: 예외 관리 (3일)
1. **예외 목록 설정 UI** - 2시간
2. **스캐너 예외 로직 적용** - 1시간
3. **테스트 및 검증** - 2시간

---

## 🔄 수정된 전체 워크플로우

```
┌─────────────────────────────────────────────────────────┐
│ 1. 파일 스캔                                            │
│    - 설정된 library 폴더 탐색                          │
│    - 예외 목록 필터링 (*.txt, .git 등)                 │
│    - 지원 확장자만 수집 (zip, 7z, rar, iso, dmg)       │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 2. 메타데이터 캐시 조회                                │
│    - 정규화된 이름으로 캐시 검색                       │
│    - 캐시 존재 + 정확도 ≥ 90% → 재사용 (종료)         │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 3. 파일명 파싱 (FilenameParser)                        │
│    - 파일명에서 소프트웨어 이름, 버전, 제조사 추출     │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 4. AI 메타데이터 생성 (OpenAI API)                     │
│    - 프로그램명, 버전, 공식사이트, 지원사양           │
│    - 설명, 카테고리 자동 분류                          │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 5. 웹 크롤링 (선택적)                                  │
│    - 스크린샷 3개 수집                                 │
│    - 다운로드 링크 추출                                │
│    - (YouTube는 기본 비활성화)                         │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 6. 정확도 점수 계산                                    │
│    - 제목 유사도, vendor 존재, 카테고리 유효성 등     │
│    - 점수: 0.0 ~ 1.0                                   │
└─────────────────────────────────────────────────────────┘
                        ↓
        ┌───────────────┴───────────────┐
        │                               │
    ≥ 90%                           < 90%
        │                               │
        ↓                               ↓
┌──────────────────┐        ┌────────────────────────┐
│ 7a. 자동 등록    │        │ 7b. 불일치 목록 저장   │
│  - Products 저장 │        │  - UnmatchedItems 저장 │
│  - 캐시 저장     │        │  - 관리자 검토 대기    │
└──────────────────┘        └────────────────────────┘
                                        ↓
                            ┌────────────────────────┐
                            │ 8. 관리자 수동 처리    │
                            │  - 제안 승인           │
                            │  - 재검색              │
                            │  - 수동 입력           │
                            │  - 무시                │
                            └────────────────────────┘
                                        ↓
                            ┌────────────────────────┐
                            │ 9. Products 등록       │
                            │    + 캐시 저장         │
                            └────────────────────────┘
```

---

## 💾 데이터베이스 스키마 추가

```sql
-- 메타데이터 캐시 테이블
CREATE TABLE metadata_cache (
    id SERIAL PRIMARY KEY,
    software_name VARCHAR(255) UNIQUE NOT NULL,
    metadata_json JSONB NOT NULL,
    confidence_score FLOAT NOT NULL,
    source VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    hit_count INTEGER DEFAULT 0
);

CREATE INDEX idx_metadata_cache_name ON metadata_cache(software_name);
CREATE INDEX idx_metadata_cache_score ON metadata_cache(confidence_score);

-- 불일치 항목 테이블
CREATE TABLE unmatched_items (
    id SERIAL PRIMARY KEY,
    file_path VARCHAR(500) UNIQUE NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    folder_path VARCHAR(500) NOT NULL,

    parsed_name VARCHAR(255),
    parsed_version VARCHAR(100),
    parsed_vendor VARCHAR(255),

    suggested_metadata JSONB,
    confidence_score FLOAT,

    status VARCHAR(50) DEFAULT 'pending',
    manual_metadata JSONB,

    created_at TIMESTAMP DEFAULT NOW(),
    reviewed_at TIMESTAMP,
    reviewed_by INTEGER REFERENCES users(id)
);

CREATE INDEX idx_unmatched_status ON unmatched_items(status);
CREATE INDEX idx_unmatched_created ON unmatched_items(created_at);

-- 설정 테이블에 예외 목록 추가
INSERT INTO settings (key, value, description) VALUES
('scan_exception_patterns', '["*.txt", "*.log", "Thumbs.db", ".DS_Store"]', '스캔 제외 파일 패턴'),
('scan_exception_folders', '[".git", "node_modules", "__MACOSX"]', '스캔 제외 폴더명'),
('scan_exception_paths', '[]', '스캔 제외 전체 경로');
```

---

## 🎨 UI 개선 사항

### 관리자 페이지 탭 추가
```
현재: [수동 스캔] [스케줄러] [정보]
추가: [수동 스캔] [스케줄러] [불일치 목록] [예외 설정] [정보]
```

### 스캔 결과 요약 개선
```
스캔 완료!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 자동 등록: 45개 (정확도 ≥ 90%)
⚠️  검토 필요: 12개 (정확도 < 90%)
📦 캐시 재사용: 23개
🚫 제외됨: 8개
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[불일치 목록 보기] 버튼 추가
```

---

## ⚙️ 설정 페이지 구성 (개선)

```
메타데이터 설정
├─ AI 모델 설정
│  ├─ API 키
│  ├─ 모델 선택
│  └─ 정확도 임계값 (90% 기본)
│
├─ 수집 항목
│  ├─ 기본 메타데이터 (항상)
│  │  ├─ 프로그램명
│  │  ├─ 버전
│  │  ├─ 설명
│  │  └─ 카테고리
│  └─ 확장 메타데이터 (선택)
│     ├─ ✅ 공식 사이트
│     ├─ ✅ 지원 사양
│     ├─ ✅ 스크린샷 (3개)
│     └─ ☐ YouTube 영상 (기본 비활성화)
│
├─ 예외 목록
│  ├─ 파일 패턴
│  ├─ 폴더명
│  └─ 전체 경로
│
└─ 캐시 관리
   ├─ 캐시 통계 (항목 수, 적중률)
   └─ [캐시 초기화] 버튼
```

---

## 📊 예상 효과

1. **API 비용 절감**: 캐시 정책으로 50~70% 절감 예상
2. **정확도 향상**: 불일치 항목 수동 관리로 최종 정확도 95% 이상
3. **스캔 속도**: 캐시 재사용으로 2~3배 빠른 스캔
4. **유지보수성**: 예외 목록으로 불필요한 파일 제외
5. **사용자 경험**: 자동/수동 하이브리드 방식으로 편의성 ↑

---

## 🚀 다음 단계

1. Phase 1 즉시 구현 (스크린샷 제한, YouTube 비활성화)
2. MetadataCache, UnmatchedItem 모델 추가
3. Alembic 마이그레이션 생성
4. API 엔드포인트 구현
5. 프론트엔드 UI 개발
6. 통합 테스트

이 계획을 승인하시면 즉시 Phase 1부터 구현을 시작하겠습니다.
