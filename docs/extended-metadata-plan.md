# 확장 메타데이터 수집 기능 설계서

## 목차
1. [개요](#개요)
2. [확장 메타데이터 항목](#확장-메타데이터-항목)
3. [데이터베이스 스키마 확장](#데이터베이스-스키마-확장)
4. [설정 기반 수집 전략](#설정-기반-수집-전략)
5. [AI 프롬프트 개선](#ai-프롬프트-개선)
6. [웹 크롤링 전략](#웹-크롤링-전략)
7. [구현 계획](#구현-계획)
8. [테스트 시나리오](#테스트-시나리오)

---

## 개요

### 목적
기본 메타데이터(제목, 설명, 제조사, 카테고리, 아이콘)에서 확장하여 더 풍부한 제품 정보를 자동으로 수집합니다.

### 핵심 가치
"단순히 파일 이름만 있어도, 공식 사이트처럼 상세한 제품 정보를 자동으로 채워주는 스마트 라이브러리"

### 수집 방법
1. **AI 기반 수집** (OpenAI GPT-4o-mini): 일반적인 정보, 요약, 카테고리
2. **웹 크롤링** (선택사항): 공식 사이트에서 상세 정보 추출
3. **설정 기반 선택**: 사용자가 원하는 정보만 수집

---

## 확장 메타데이터 항목

### 기본 메타데이터 (현재 구현됨)
- ✅ `title`: 제품명
- ✅ `description`: 간단한 설명
- ✅ `vendor`: 제조사
- ✅ `category`: 카테고리
- ✅ `icon_url`: 아이콘 이미지

### 확장 메타데이터 (신규)

| 필드명 | 타입 | 설명 | AI 수집 | 크롤링 | 우선순위 |
|--------|------|------|---------|--------|----------|
| `official_website` | String | 공식 웹사이트 URL | ✓ | ✓ | 높음 |
| `system_requirements` | JSON | 시스템 요구사항 | ✓ | ✓ | 높음 |
| `supported_os` | Array | 지원 운영체제 | ✓ | ✓ | 높음 |
| `screenshots` | Array | 스크린샷 URL 목록 | ✗ | ✓ | 중간 |
| `video_url` | String | 유튜브 또는 공식 영상 | ✓ | ✓ | 중간 |
| `license_type` | String | 라이선스 타입 (Free, Trial, Paid) | ✓ | ✓ | 중간 |
| `latest_version` | String | 최신 버전 번호 | ✓ | ✓ | 낮음 |
| `release_date` | Date | 최초 릴리즈 날짜 | ✓ | ✗ | 낮음 |
| `tags` | Array | 검색용 태그/키워드 | ✓ | ✗ | 낮음 |
| `download_url` | String | 공식 다운로드 링크 | ✗ | ✓ | 낮음 |

### system_requirements 구조 (JSON)
```json
{
  "minimum": {
    "os": "Windows 10 64-bit",
    "processor": "Intel Core i5",
    "memory": "8 GB RAM",
    "graphics": "NVIDIA GTX 1050",
    "storage": "20 GB available space"
  },
  "recommended": {
    "os": "Windows 11 64-bit",
    "processor": "Intel Core i7",
    "memory": "16 GB RAM",
    "graphics": "NVIDIA RTX 3060",
    "storage": "50 GB available space"
  }
}
```

### supported_os 예시
```json
["Windows 10", "Windows 11", "macOS 12+", "Linux (Ubuntu 20.04+)"]
```

---

## 데이터베이스 스키마 확장

### Product 모델 변경 (추가 필드)

```python
# backend/app/models/product.py

from sqlalchemy import Column, Integer, String, Text, JSON, ARRAY
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY

class Product(Base):
    __tablename__ = "products"

    # 기존 필드
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text)
    vendor = Column(String)
    icon_url = Column(String)
    category = Column(String, index=True)
    folder_path = Column(String, unique=True, nullable=False)

    # 확장 필드 (신규)
    official_website = Column(String, nullable=True)
    system_requirements = Column(JSON, nullable=True)
    supported_os = Column(PG_ARRAY(String), nullable=True)  # PostgreSQL ARRAY
    screenshots = Column(PG_ARRAY(String), nullable=True)   # URL 목록
    video_url = Column(String, nullable=True)
    license_type = Column(String, nullable=True)  # Free, Trial, Paid, Open Source
    latest_version = Column(String, nullable=True)
    release_date = Column(DateTime(timezone=True), nullable=True)
    tags = Column(PG_ARRAY(String), nullable=True)
    download_url = Column(String, nullable=True)

    # 메타데이터 추적
    metadata_completeness = Column(Integer, default=0)  # 0-100 점수
    last_metadata_update = Column(DateTime(timezone=True), nullable=True)
```

### Alembic 마이그레이션
```bash
# 마이그레이션 생성
alembic revision -m "add extended metadata fields to products"

# 마이그레이션 적용
alembic upgrade head
```

---

## 설정 기반 수집 전략

### 메타데이터 설정 구조 (config.json)

```json
{
  "metadata": {
    "scanMethod": "ai",  // "ai", "manual", "hybrid"
    "aiProvider": "openai",
    "aiModel": "gpt-4o-mini",
    "apiKey": "sk-...",

    // 수집할 메타데이터 선택
    "collectExtended": true,
    "extendedFields": {
      "official_website": true,
      "system_requirements": true,
      "supported_os": true,
      "screenshots": false,  // 비활성화 (트래픽/저장공간 고려)
      "video_url": true,
      "license_type": true,
      "latest_version": false,
      "release_date": false,
      "tags": true,
      "download_url": false
    },

    // 웹 크롤링 설정
    "enableWebCrawling": false,  // 기본값: 비활성화
    "crawlingTimeout": 10,  // 초
    "maxScreenshots": 5
  }
}
```

### UI: 설정 페이지 개선

**Settings.vue - 메타데이터 설정 섹션**:
```vue
<!-- 기본 메타데이터 수집 -->
<div>
  <label>스캔 방법</label>
  <select v-model="scanMethod">
    <option value="ai">AI 자동 수집 (권장)</option>
    <option value="manual">수동 입력만</option>
    <option value="hybrid">AI + 수동 보완</option>
  </select>
</div>

<!-- 확장 메타데이터 수집 -->
<div>
  <label class="flex items-center">
    <input type="checkbox" v-model="collectExtended" />
    <span>확장 메타데이터 수집 활성화</span>
  </label>
</div>

<!-- 수집할 항목 선택 -->
<div v-if="collectExtended" class="ml-6 space-y-2">
  <label class="flex items-center">
    <input type="checkbox" v-model="extendedFields.official_website" />
    <span>공식 웹사이트</span>
  </label>
  <label class="flex items-center">
    <input type="checkbox" v-model="extendedFields.system_requirements" />
    <span>시스템 요구사항</span>
  </label>
  <label class="flex items-center">
    <input type="checkbox" v-model="extendedFields.supported_os" />
    <span>지원 운영체제</span>
  </label>
  <label class="flex items-center">
    <input type="checkbox" v-model="extendedFields.video_url" />
    <span>소개 영상 (YouTube)</span>
  </label>
  <label class="flex items-center">
    <input type="checkbox" v-model="extendedFields.screenshots" />
    <span>스크린샷 (저장공간 필요)</span>
  </label>
  <!-- ... 기타 항목 -->
</div>

<!-- 웹 크롤링 옵션 -->
<div>
  <label class="flex items-center">
    <input type="checkbox" v-model="enableWebCrawling" />
    <span>웹 크롤링 활성화 (느릴 수 있음)</span>
  </label>
  <p class="text-xs text-gray-500">
    AI만으로 충분하지 않을 때 공식 사이트에서 직접 정보를 가져옵니다.
  </p>
</div>
```

---

## AI 프롬프트 개선

### 확장된 AI 프롬프트

```python
# backend/app/core/ai_metadata.py

async def generate_extended_metadata(self, filename: str, options: dict) -> dict:
    """
    확장 메타데이터 생성

    Args:
        filename: 소프트웨어 이름
        options: 수집할 필드 옵션 (설정에서 가져옴)
    """

    # 수집할 필드 목록 생성
    requested_fields = []
    if options.get('official_website'):
        requested_fields.append("official_website: 공식 웹사이트 URL")
    if options.get('system_requirements'):
        requested_fields.append("system_requirements: 시스템 요구사항 (minimum, recommended)")
    if options.get('supported_os'):
        requested_fields.append("supported_os: 지원 운영체제 배열")
    if options.get('video_url'):
        requested_fields.append("video_url: 공식 소개 영상 (YouTube 등)")
    if options.get('license_type'):
        requested_fields.append("license_type: 라이선스 (Free, Trial, Paid, Open Source)")
    if options.get('tags'):
        requested_fields.append("tags: 검색용 태그 배열 (최대 5개)")

    fields_list = "\n".join([f"  - {field}" for field in requested_fields])

    prompt = f"""다음 소프트웨어에 대한 상세 정보를 JSON 형식으로 제공해주세요:

소프트웨어: {filename}

기본 정보:
  - title: 정확한 공식 제품명
  - description: 100-200자 이내의 상세 설명
  - vendor: 공식 제조사/개발사
  - category: 카테고리 (Graphics, Office, Development 등)
  - icon_url: 공식 아이콘 이미지 URL

확장 정보:
{fields_list}

중요 사항:
1. 응답은 반드시 유효한 JSON만 작성
2. 확실하지 않은 정보는 null 또는 빈 배열 사용
3. system_requirements는 다음 형식 사용:
   {{
     "minimum": {{"os": "...", "processor": "...", "memory": "...", "graphics": "...", "storage": "..."}},
     "recommended": {{"os": "...", "processor": "...", "memory": "...", "graphics": "...", "storage": "..."}}
   }}
4. supported_os는 배열로: ["Windows 10", "macOS 12+", "Linux"]
5. tags는 핵심 키워드만 5개 이내
6. video_url은 공식 YouTube 링크 우선

예시:
{{
  "title": "Adobe Photoshop 2024",
  "description": "전문가용 이미지 편집 및 그래픽 디자인 소프트웨어. 사진 보정, 합성, 디지털 페인팅 등 다양한 기능 제공",
  "vendor": "Adobe Inc.",
  "category": "Graphics",
  "icon_url": "https://...",
  "official_website": "https://www.adobe.com/products/photoshop.html",
  "system_requirements": {{
    "minimum": {{
      "os": "Windows 10 64-bit",
      "processor": "Intel or AMD processor with 64-bit support",
      "memory": "8 GB RAM",
      "graphics": "GPU with DirectX 12 support",
      "storage": "4 GB available space"
    }},
    "recommended": {{
      "os": "Windows 11 64-bit",
      "processor": "Intel Core i7 or AMD Ryzen 7",
      "memory": "16 GB RAM",
      "graphics": "NVIDIA GeForce RTX 3060 or AMD Radeon RX 6700 XT",
      "storage": "20 GB available space on SSD"
    }}
  }},
  "supported_os": ["Windows 10", "Windows 11", "macOS 12 Monterey", "macOS 13 Ventura"],
  "video_url": "https://www.youtube.com/watch?v=...",
  "license_type": "Paid",
  "tags": ["이미지편집", "그래픽디자인", "사진보정", "레이어", "포토샵"]
}}"""

    # OpenAI API 호출
    # ... (기존 코드와 유사하지만 더 많은 토큰 할당)
```

---

## 웹 크롤링 전략

### 크롤링 대상 선정
1. **공식 웹사이트**: AI가 제공한 official_website에서 정보 추출
2. **YouTube 검색**: "{제품명} official trailer" 검색
3. **스크린샷**: 공식 사이트의 갤러리/스크린샷 섹션

### 크롤링 도구
```python
# backend/app/core/web_crawler.py

import httpx
from bs4 import BeautifulSoup
from typing import List, Optional

class WebCrawler:
    """
    공식 웹사이트에서 추가 정보 크롤링
    """

    async def crawl_official_site(self, url: str) -> dict:
        """
        공식 사이트에서 정보 추출
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, follow_redirects=True)

                if response.status_code != 200:
                    return {}

                soup = BeautifulSoup(response.text, 'html.parser')

                return {
                    'screenshots': self._extract_screenshots(soup),
                    'download_url': self._extract_download_link(soup),
                    'system_requirements': self._extract_system_requirements(soup)
                }
        except Exception as e:
            print(f"Crawling error: {e}")
            return {}

    def _extract_screenshots(self, soup) -> List[str]:
        """스크린샷 이미지 URL 추출"""
        screenshots = []

        # 일반적인 이미지 갤러리 선택자
        selectors = [
            'img[class*="screenshot"]',
            'img[class*="gallery"]',
            'div[class*="screenshots"] img',
            'div[class*="gallery"] img'
        ]

        for selector in selectors:
            images = soup.select(selector)
            for img in images[:5]:  # 최대 5개
                src = img.get('src') or img.get('data-src')
                if src and src.startswith('http'):
                    screenshots.append(src)

        return screenshots[:5]

    def _extract_download_link(self, soup) -> Optional[str]:
        """다운로드 링크 추출"""
        # "Download", "Get Started" 등의 버튼 찾기
        download_links = soup.select('a[href*="download"]')
        if download_links:
            return download_links[0].get('href')
        return None

    def _extract_system_requirements(self, soup) -> Optional[dict]:
        """시스템 요구사항 추출 (텍스트 파싱)"""
        # "System Requirements" 섹션 찾기
        req_section = soup.find(text=lambda t: t and 'system requirements' in t.lower())

        if req_section:
            # 섹션 내용 파싱 (구현 필요)
            pass

        return None

    async def search_youtube_video(self, product_name: str) -> Optional[str]:
        """
        YouTube에서 공식 영상 검색
        """
        # YouTube Data API 사용 (API 키 필요)
        # 또는 간단한 검색 URL 생성
        search_query = f"{product_name} official trailer"
        # YouTube API 호출 로직...
        return None
```

### 크롤링 주의사항
- **로봇 규칙 준수**: robots.txt 확인
- **요청 제한**: 과도한 요청 방지 (rate limiting)
- **에러 처리**: 크롤링 실패 시 AI 결과만 사용
- **저작권**: 스크린샷은 공식 사이트에서만 수집

---

## 구현 계획

### Phase 1: 데이터베이스 및 AI 확장 (1-2일)
1. ✅ Product 모델에 확장 필드 추가
2. ✅ Alembic 마이그레이션 작성 및 적용
3. ✅ AI 프롬프트 개선 (확장 정보 요청)
4. ✅ 설정 config.json에 extendedFields 추가

### Phase 2: 설정 UI 개선 (1일)
1. ✅ Settings.vue에 확장 메타데이터 옵션 추가
2. ✅ 체크박스로 수집할 필드 선택
3. ✅ 웹 크롤링 활성화 옵션

### Phase 3: 웹 크롤링 구현 (선택사항, 2-3일)
1. ✅ WebCrawler 클래스 생성
2. ✅ 스크린샷 추출 로직
3. ✅ YouTube 영상 검색 통합
4. ✅ 에러 처리 및 fallback

### Phase 4: UI 표시 개선 (1-2일)
1. ✅ ProductDetail.vue에 확장 정보 표시
   - 시스템 요구사항 섹션
   - 지원 OS 뱃지
   - 스크린샷 갤러리
   - 유튜브 영상 임베드
2. ✅ 메타데이터 완성도 표시 (진행률 바)

---

## 테스트 시나리오

### 테스트 케이스 1: 한컴오피스 2024
```bash
폴더: /library/한컴오피스 2024
파일: 한컴 오피스 2024.zip

예상 AI 응답:
{
  "title": "한컴 오피스 2024",
  "description": "한글 워드프로세서를 포함한 국산 오피스 통합 소프트웨어",
  "vendor": "한글과컴퓨터",
  "category": "Office",
  "official_website": "https://www.hancom.com/",
  "system_requirements": {
    "minimum": {
      "os": "Windows 10 이상",
      "processor": "Intel Pentium 4 이상",
      "memory": "2 GB RAM",
      "storage": "5 GB 여유 공간"
    },
    "recommended": {
      "os": "Windows 11",
      "processor": "Intel Core i5 이상",
      "memory": "4 GB RAM",
      "storage": "10 GB 여유 공간"
    }
  },
  "supported_os": ["Windows 10", "Windows 11"],
  "video_url": "https://www.youtube.com/watch?v=...",
  "license_type": "Paid",
  "tags": ["오피스", "한글", "워드프로세서", "문서작성", "국산소프트웨어"]
}
```

### 테스트 스크립트 작성

```python
# backend/tests/test_extended_metadata.py

import asyncio
from app.core.ai_metadata import AIMetadataGenerator

async def test_extended_metadata():
    """확장 메타데이터 테스트"""

    generator = AIMetadataGenerator()

    test_cases = [
        "한컴 오피스 2024",
        "Adobe Photoshop 2024",
        "Microsoft Office 365",
        "Visual Studio Code",
        "AutoCAD 2024"
    ]

    options = {
        'official_website': True,
        'system_requirements': True,
        'supported_os': True,
        'video_url': True,
        'license_type': True,
        'tags': True
    }

    for software_name in test_cases:
        print(f"\n{'='*60}")
        print(f"테스트: {software_name}")
        print('='*60)

        metadata = await generator.generate_extended_metadata(
            software_name,
            options
        )

        print(f"\n제목: {metadata.get('title')}")
        print(f"제조사: {metadata.get('vendor')}")
        print(f"카테고리: {metadata.get('category')}")
        print(f"공식 사이트: {metadata.get('official_website')}")
        print(f"지원 OS: {metadata.get('supported_os')}")
        print(f"라이선스: {metadata.get('license_type')}")
        print(f"태그: {metadata.get('tags')}")

        if metadata.get('system_requirements'):
            print("\n시스템 요구사항:")
            print(f"  최소: {metadata['system_requirements'].get('minimum')}")
            print(f"  권장: {metadata['system_requirements'].get('recommended')}")

        print(f"\n비디오: {metadata.get('video_url')}")

if __name__ == "__main__":
    asyncio.run(test_extended_metadata())
```

### 실행 방법
```bash
cd backend
python -m tests.test_extended_metadata
```

---

## 메타데이터 완성도 점수 계산

```python
def calculate_completeness(product: Product) -> int:
    """
    메타데이터 완성도 계산 (0-100)
    """
    score = 0
    total_fields = 15

    # 필수 필드 (각 10점)
    if product.title: score += 10
    if product.description: score += 10
    if product.vendor: score += 10
    if product.category: score += 10
    if product.icon_url: score += 10

    # 확장 필드 (각 5점)
    if product.official_website: score += 5
    if product.system_requirements: score += 5
    if product.supported_os: score += 5
    if product.screenshots: score += 5
    if product.video_url: score += 5
    if product.license_type: score += 5
    if product.latest_version: score += 5
    if product.tags: score += 5

    return min(100, score)
```

---

## UI 표시 예시

### 제품 상세 페이지 - 확장 정보 탭

```vue
<!-- 시스템 요구사항 섹션 -->
<div v-if="product.system_requirements" class="mt-6">
  <h3 class="text-lg font-bold mb-4">💻 시스템 요구사항</h3>
  <div class="grid grid-cols-2 gap-4">
    <div class="border rounded-lg p-4">
      <h4 class="font-semibold mb-2">최소 사양</h4>
      <ul class="text-sm space-y-1">
        <li><strong>OS:</strong> {{ product.system_requirements.minimum.os }}</li>
        <li><strong>프로세서:</strong> {{ product.system_requirements.minimum.processor }}</li>
        <li><strong>메모리:</strong> {{ product.system_requirements.minimum.memory }}</li>
        <li><strong>그래픽:</strong> {{ product.system_requirements.minimum.graphics }}</li>
        <li><strong>저장공간:</strong> {{ product.system_requirements.minimum.storage }}</li>
      </ul>
    </div>
    <div class="border rounded-lg p-4 bg-blue-50">
      <h4 class="font-semibold mb-2">권장 사양</h4>
      <ul class="text-sm space-y-1">
        <li><strong>OS:</strong> {{ product.system_requirements.recommended.os }}</li>
        <li><strong>프로세서:</strong> {{ product.system_requirements.recommended.processor }}</li>
        <li><strong>메모리:</strong> {{ product.system_requirements.recommended.memory }}</li>
        <li><strong>그래픽:</strong> {{ product.system_requirements.recommended.graphics }}</li>
        <li><strong>저장공간:</strong> {{ product.system_requirements.recommended.storage }}</li>
      </ul>
    </div>
  </div>
</div>

<!-- 지원 OS -->
<div v-if="product.supported_os" class="mt-6">
  <h3 class="text-lg font-bold mb-4">🖥️ 지원 운영체제</h3>
  <div class="flex flex-wrap gap-2">
    <span
      v-for="os in product.supported_os"
      :key="os"
      class="px-3 py-1 bg-gray-100 rounded-full text-sm"
    >
      {{ os }}
    </span>
  </div>
</div>

<!-- 스크린샷 갤러리 -->
<div v-if="product.screenshots?.length" class="mt-6">
  <h3 class="text-lg font-bold mb-4">📸 스크린샷</h3>
  <div class="grid grid-cols-3 gap-4">
    <img
      v-for="(screenshot, index) in product.screenshots"
      :key="index"
      :src="screenshot"
      class="rounded-lg cursor-pointer hover:opacity-80"
      @click="openScreenshot(screenshot)"
    />
  </div>
</div>

<!-- 유튜브 영상 -->
<div v-if="product.video_url" class="mt-6">
  <h3 class="text-lg font-bold mb-4">🎬 소개 영상</h3>
  <div class="aspect-video">
    <iframe
      :src="getYouTubeEmbedUrl(product.video_url)"
      class="w-full h-full rounded-lg"
      frameborder="0"
      allowfullscreen
    ></iframe>
  </div>
</div>

<!-- 태그 -->
<div v-if="product.tags?.length" class="mt-6">
  <h3 class="text-lg font-bold mb-4">🏷️ 태그</h3>
  <div class="flex flex-wrap gap-2">
    <span
      v-for="tag in product.tags"
      :key="tag"
      class="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm"
    >
      #{{ tag }}
    </span>
  </div>
</div>
```

---

## 비용 및 성능 고려사항

### AI API 비용
- **GPT-4o-mini**: ~$0.15 / 1M input tokens, ~$0.60 / 1M output tokens
- **확장 메타데이터**: 토큰 사용량 약 2-3배 증가
- **예상 비용**: 제품당 약 $0.001 - $0.002 (매우 저렴)

### 성능
- **AI 호출 시간**: 2-5초
- **웹 크롤링 추가**: +5-10초 (선택사항)
- **권장**: 기본적으로 AI만 사용, 필요시 크롤링 활성화

### 저장 공간
- **스크린샷 수집**: 제품당 약 1-5 MB 추가
- **권장**: 스크린샷 수집은 선택적으로 활성화

---

## 다음 단계

1. **즉시 구현 가능**: AI 프롬프트 확장 및 테스트
2. **데이터베이스 마이그레이션**: 확장 필드 추가
3. **설정 UI 추가**: 수집할 필드 선택
4. **테스트 및 검증**: 실제 소프트웨어로 정확도 확인
5. **선택적 구현**: 웹 크롤링 기능

이 설계서를 바탕으로 단계적으로 구현하면 풍부한 메타데이터를 자동으로 수집하는 스마트 라이브러리를 구축할 수 있습니다.
