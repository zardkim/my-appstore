# Gemini + Google Custom Search API 통합 메타데이터 생성 계획서

## 📋 개요

**목표**: Gemini AI와 Google Custom Search API를 통합하여 소프트웨어 메타데이터를 자동으로 생성하고, 공식 이미지(로고, 스크린샷)를 수집하는 시스템 구축

**현재 상태**: Gemini API만 사용하여 텍스트 메타데이터(제목, 설명, 카테고리 등) 생성
**개선 목표**: Google Custom Search API를 추가하여 공식 이미지 자동 수집 및 검증

---

## 🎯 통합 전략

### Phase 1: Gemini API 기반 메타데이터 생성 (✅ 현재 구현됨)

**역할**: 텍스트 메타데이터 생성
- 소프트웨어 이름 파싱
- 설명(description) 생성
- 카테고리 분류
- 제조사(vendor) 추출
- 시스템 요구사항 정보
- 주요 기능(features) 목록

**API 엔드포인트**:
```
https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
```

**지원 모델**:
- `gemini-3.0-flash-exp` (최신)
- `gemini-2.5-flash-exp` (추천, 기본값)
- `gemini-2.5-pro-exp`

**현재 구현**:
- `app/core/ai_metadata.py` - AIMetadataGenerator 클래스
- Gemini API 호출 및 JSON 응답 파싱
- 오류 처리 및 Fallback 메커니즘

---

### Phase 2: Google Custom Search API 통합 (🔜 구현 예정)

**역할**: 이미지 검색 및 검증
- 공식 로고 이미지 URL 수집
- 소프트웨어 스크린샷 수집
- 공식 웹사이트 URL 검증
- 이미지 출처 URL 저장 (저작권 안전)

**필요 구성요소**:
1. **API Key**: Google Cloud Console에서 발급
2. **Search Engine ID (cx)**: Programmable Search Engine 생성

**API 엔드포인트**:
```
https://www.googleapis.com/customsearch/v1
```

**요청 파라미터**:
```json
{
  "key": "API_KEY",
  "cx": "SEARCH_ENGINE_ID",
  "q": "SolidWorks 2024 official logo",
  "searchType": "image",
  "num": 5
}
```

---

## 🔧 구현 계획

### 1단계: Google Custom Search API 설정

#### 1.1 API 키 발급
```bash
# Google Cloud Console 접속
https://console.cloud.google.com/

# 프로젝트 생성
프로젝트 이름: myappstore-metadata-search

# Custom Search JSON API 활성화
API 및 서비스 → 라이브러리 → "Custom Search JSON API" 검색 → 사용 설정

# API 키 생성
API 및 서비스 → 사용자 인증 정보 → API 키 만들기

# 보안 설정
- API 제한: Custom Search JSON API만 허용
- HTTP referrer 또는 IP 주소 제한 설정
```

#### 1.2 Programmable Search Engine 생성
```bash
# PSE 콘솔 접속
https://programmablesearchengine.google.com/

# 검색엔진 생성
- 검색할 사이트: * (전체 웹 검색)
- 검색엔진 이름: SoftwareMetadataSearch
- 이미지 검색: ON (중요!)

# Search Engine ID (cx) 확인
cx=xxxxxxxxxxxxxxxxx
```

---

### 2단계: 백엔드 구현

#### 2.1 새로운 모듈 생성: `app/core/google_image_search.py`

```python
"""
Google Custom Search API를 사용한 이미지 검색 모듈
"""
import httpx
from typing import List, Dict, Optional
from app.config import settings

class GoogleImageSearcher:
    def __init__(self, api_key: str, cx: str):
        """
        Args:
            api_key: Google API Key
            cx: Custom Search Engine ID
        """
        self.api_key = api_key
        self.cx = cx
        self.base_url = "https://www.googleapis.com/customsearch/v1"

    async def search_logo(self, software_name: str, num_results: int = 3) -> List[Dict]:
        """
        공식 로고 이미지 검색

        Args:
            software_name: 소프트웨어 이름 (예: "Adobe Photoshop 2024")
            num_results: 반환할 결과 수 (기본값: 3)

        Returns:
            이미지 정보 리스트 [{"url": "...", "thumbnail": "...", "source": "..."}]
        """
        query = f"{software_name} official logo"
        return await self._search_images(query, num_results)

    async def search_screenshots(self, software_name: str, num_results: int = 4) -> List[Dict]:
        """
        소프트웨어 스크린샷 검색

        Args:
            software_name: 소프트웨어 이름
            num_results: 반환할 결과 수 (기본값: 4)

        Returns:
            스크린샷 정보 리스트
        """
        query = f"{software_name} software screenshot interface"
        return await self._search_images(query, num_results)

    async def _search_images(self, query: str, num: int) -> List[Dict]:
        """
        실제 이미지 검색 수행
        """
        params = {
            "key": self.api_key,
            "cx": self.cx,
            "q": query,
            "searchType": "image",
            "num": min(num, 10),  # 최대 10개
            "safe": "active"
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.base_url, params=params)

                if response.status_code == 200:
                    data = response.json()
                    items = data.get("items", [])

                    return [
                        {
                            "url": item.get("link"),
                            "thumbnail": item.get("image", {}).get("thumbnailLink"),
                            "source": item.get("displayLink"),
                            "title": item.get("title")
                        }
                        for item in items
                    ]
                else:
                    print(f"Google Image Search Error: {response.status_code}")
                    return []

        except Exception as e:
            print(f"Google Image Search Exception: {e}")
            return []

    def get_quota_info(self) -> Dict:
        """
        할당량 정보 반환
        """
        return {
            "free_daily_quota": 100,
            "cost_per_1000": "$5 USD",
            "note": "이미지 검색 1회 = 1 쿼리로 계산"
        }
```

#### 2.2 설정 파일 업데이트: `app/config.py`

```python
class Settings(BaseSettings):
    # 기존 설정...

    # Google Custom Search API 설정
    GOOGLE_API_KEY: Optional[str] = None
    GOOGLE_CX: Optional[str] = None  # Custom Search Engine ID

    class Config:
        env_file = ".env"
```

#### 2.3 메타데이터 생성 통합: `app/core/ai_metadata.py` 수정

```python
from app.core.google_image_search import GoogleImageSearcher

class AIMetadataGenerator:
    def __init__(self, provider: str, api_key: str, model: str,
                 google_api_key: Optional[str] = None,
                 google_cx: Optional[str] = None):
        # 기존 초기화...

        # Google Image Search 초기화 (선택적)
        self.image_searcher = None
        if google_api_key and google_cx:
            self.image_searcher = GoogleImageSearcher(google_api_key, google_cx)

    async def generate_metadata(self, software_name: str) -> dict:
        """
        Gemini로 텍스트 메타데이터 생성 +
        Google Custom Search로 이미지 수집
        """
        # 1. Gemini API로 텍스트 메타데이터 생성
        metadata = await self._generate_text_metadata(software_name)

        # 2. Google Image Search로 이미지 URL 수집 (optional)
        if self.image_searcher:
            try:
                # 공식 로고 검색
                logo_results = await self.image_searcher.search_logo(software_name, num_results=1)
                if logo_results:
                    metadata["icon_url"] = logo_results[0]["url"]
                    metadata["icon_source"] = logo_results[0]["source"]

                # 스크린샷 검색
                screenshot_results = await self.image_searcher.search_screenshots(software_name, num_results=4)
                metadata["screenshots"] = [img["url"] for img in screenshot_results]
                metadata["screenshot_sources"] = [img["source"] for img in screenshot_results]

            except Exception as e:
                print(f"Image search failed, using Gemini fallback: {e}")
                # Gemini가 제공한 기본 이미지 URL 사용

        return metadata
```

---

### 3단계: 프론트엔드 설정 UI 추가

#### 3.1 Settings.vue 확장

```vue
<!-- Google Custom Search API 설정 섹션 -->
<div class="mt-6 border-t border-gray-200 dark:border-gray-600 pt-6">
  <h3 class="text-lg font-semibold mb-4">🔍 Google 이미지 검색 (선택사항)</h3>
  <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
    공식 로고 및 스크린샷 자동 수집을 위해 Google Custom Search API를 설정할 수 있습니다.
    (하루 100회 무료)
  </p>

  <!-- Google API Key -->
  <div class="mb-4">
    <label class="block text-sm font-medium mb-2">Google API Key</label>
    <input
      v-model="googleApiKey"
      type="password"
      placeholder="AIzaSy..."
      class="w-full px-4 py-2 border rounded-xl"
    />
    <p class="text-xs text-gray-500 mt-2">
      발급: https://console.cloud.google.com/
    </p>
  </div>

  <!-- Google CX (Search Engine ID) -->
  <div class="mb-4">
    <label class="block text-sm font-medium mb-2">Search Engine ID (cx)</label>
    <input
      v-model="googleCx"
      type="text"
      placeholder="xxxxxxxxx:yyyyy"
      class="w-full px-4 py-2 border rounded-xl"
    />
    <p class="text-xs text-gray-500 mt-2">
      발급: https://programmablesearchengine.google.com/
    </p>
  </div>

  <!-- 이미지 검색 활성화 토글 -->
  <div class="flex items-center">
    <input
      v-model="enableImageSearch"
      type="checkbox"
      id="enableImageSearch"
      class="mr-2"
    />
    <label for="enableImageSearch" class="text-sm">
      이미지 자동 검색 활성화
    </label>
  </div>
</div>
```

---

### 4단계: 데이터베이스 확장 (선택사항)

#### 4.1 Products 테이블 확장

```python
# app/models/product.py에 컬럼 추가

class Product(Base):
    # 기존 컬럼...

    # 이미지 출처 정보 (저작권 안전)
    icon_source = Column(String)  # 로고 이미지 출처 URL
    screenshot_sources = Column(JSON)  # 스크린샷 출처 URL 목록
```

#### 4.2 Migration 생성

```bash
cd backend
alembic revision -m "add_image_source_tracking"
alembic upgrade head
```

---

## 📊 통합 워크플로우

```
[사용자 파일 업로드]
        ↓
[파일명 파싱] → "Adobe_Photoshop_2024.zip"
        ↓
[Gemini API 호출]
    ↓
┌───────────────────────────┐
│ 텍스트 메타데이터 생성      │
│ - title: "Adobe Photoshop" │
│ - vendor: "Adobe"          │
│ - category: "Graphics"     │
│ - description: "..."       │
└───────────────────────────┘
        ↓
[Google Custom Search API 호출] (선택적)
    ↓
┌───────────────────────────┐
│ 이미지 URL 수집            │
│ - 로고: 1개                │
│ - 스크린샷: 4개            │
│ - 출처 URL 저장            │
└───────────────────────────┘
        ↓
[데이터베이스 저장]
        ↓
[사용자에게 표시]
```

---

## 💰 비용 분석

### Gemini API
- **무료 할당량**: 분당 15 RPM (Requests Per Minute)
- **가격**: 무료 티어 충분 (Flash 모델)
- **사용 시나리오**: 모든 소프트웨어 메타데이터 생성

### Google Custom Search API
- **무료 할당량**: 하루 100회 검색
- **유료**: $5 / 1,000회
- **사용 시나리오**:
  - 이미지가 없는 경우만 검색 (선택적)
  - 사용자가 이미지 갱신 요청 시
  - 주요 소프트웨어만 자동 검색

**비용 절감 전략**:
1. Gemini가 제공한 `icon_url`이 있으면 Google Search 생략
2. 사용자가 수동으로 이미지 검색 요청한 경우만 API 호출
3. 로컬 캐싱: 한 번 검색한 이미지는 재검색하지 않음
4. 일별 할당량 모니터링 (100회 제한)

---

## 🔒 보안 고려사항

### API 키 관리
```python
# .env 파일
GEMINI_API_KEY=AIzaSy...
GOOGLE_API_KEY=AIzaSy...
GOOGLE_CX=xxxxxxxxx:yyyyy

# Docker Compose
services:
  backend:
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - GOOGLE_CX=${GOOGLE_CX}
```

### API 제한 설정
1. Google Cloud Console에서 API 키 제한
   - HTTP referrer 제한
   - IP 주소 제한
2. Rate Limiting 구현 (백엔드)
   ```python
   # 일별 할당량 추적
   daily_quota_tracker = {
       "google_search": {"used": 0, "limit": 100}
   }
   ```

---

## 🧪 테스트 계획

### 1. 단위 테스트
```python
# tests/test_google_image_search.py

async def test_logo_search():
    searcher = GoogleImageSearcher(api_key="...", cx="...")
    results = await searcher.search_logo("Adobe Photoshop")

    assert len(results) > 0
    assert "url" in results[0]
    assert "thumbnail" in results[0]

async def test_quota_exceeded():
    # 할당량 초과 시 빈 리스트 반환 테스트
    pass
```

### 2. 통합 테스트
```python
# tests/test_metadata_integration.py

async def test_full_metadata_generation():
    generator = AIMetadataGenerator(
        provider="gemini",
        api_key=gemini_key,
        model="gemini-2.5-flash-exp",
        google_api_key=google_key,
        google_cx=cx
    )

    metadata = await generator.generate_metadata("SolidWorks 2024")

    assert "title" in metadata
    assert "description" in metadata
    assert "icon_url" in metadata  # Google Search 결과
    assert "screenshots" in metadata
```

---

## 📈 모니터링 및 로깅

### API 사용량 추적
```python
# app/core/api_usage_tracker.py

class APIUsageTracker:
    def __init__(self):
        self.usage = {
            "gemini": {"total": 0, "success": 0, "error": 0},
            "google_search": {"total": 0, "success": 0, "error": 0, "quota_used": 0}
        }

    def log_gemini_call(self, success: bool):
        self.usage["gemini"]["total"] += 1
        if success:
            self.usage["gemini"]["success"] += 1
        else:
            self.usage["gemini"]["error"] += 1

    def log_google_search(self, success: bool):
        self.usage["google_search"]["total"] += 1
        self.usage["google_search"]["quota_used"] += 1

        if success:
            self.usage["google_search"]["success"] += 1
        else:
            self.usage["google_search"]["error"] += 1

    def get_daily_report(self) -> dict:
        return {
            "date": datetime.now().date().isoformat(),
            "usage": self.usage,
            "google_quota_remaining": 100 - self.usage["google_search"]["quota_used"]
        }
```

---

## 🚀 배포 체크리스트

- [ ] Google Cloud 프로젝트 생성
- [ ] Custom Search JSON API 활성화
- [ ] API Key 발급 및 제한 설정
- [ ] Programmable Search Engine 생성 (이미지 검색 ON)
- [ ] cx 값 확보
- [ ] `GoogleImageSearcher` 클래스 구현
- [ ] `AIMetadataGenerator` 통합
- [ ] Settings UI에 Google API 설정 추가
- [ ] 환경변수 설정 (.env, docker-compose.yml)
- [ ] 데이터베이스 마이그레이션
- [ ] 단위 테스트 작성
- [ ] 통합 테스트 실행
- [ ] API 사용량 모니터링 구현
- [ ] 프로덕션 배포

---

## 📝 결론

**Gemini + Google Custom Search API 통합 시스템**은 다음과 같은 장점을 제공합니다:

1. **정확한 텍스트 메타데이터**: Gemini의 강력한 언어 이해 능력
2. **검증된 이미지 소스**: Google Search를 통한 공식 이미지 수집
3. **비용 효율성**: 무료 할당량 최대 활용 (Gemini 무제한, Google 100회/일)
4. **저작권 안전**: 이미지 출처 URL 자동 기록
5. **확장성**: 필요시 Google Search를 선택적으로 활성화/비활성화

**권장 사용 패턴**:
- 기본: Gemini만 사용 (빠르고 무료)
- 고급: Gemini + Google Search (더 정확한 이미지)
- 검증: 사용자가 수동으로 이미지 갱신 요청

이 통합 시스템을 통해 **완전 자동화된 소프트웨어 카탈로그 생성**이 가능합니다.
