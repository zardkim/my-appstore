# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.15] - 2026-02-23

### Fixed
- **로그인 상태 유지 30일 미작동 수정**: `.env`의 `ACCESS_TOKEN_EXPIRE_MINUTES=30`(분)이 기본값(30일)을 덮어써 항상 30분 후 로그아웃되던 문제 수정. 백엔드 로그인에 `remember_me` 파라미터 추가 — 체크 시 30일, 미체크 시 설정값 토큰 발급
- **API 클라이언트 sessionStorage 토큰 누락 수정**: request interceptor가 `localStorage`만 확인하여 세션 미유지 사용자의 API 요청에 Authorization 헤더 누락. `sessionStorage` fallback 추가 및 401 시 양쪽 스토리지 동시 정리
- **스캔 예외 추가 실패 수정**: 소프트웨어 확장자 파일에 `*.ext` 와일드카드 패턴 시도 시 백엔드 차단 오류 발생. 항상 파일명 자체를 예외 패턴으로 등록하도록 수정
- **파일명 위반 목록 위반 유형 레이블 수정**: 검색된 목록에 "언더스코어 과다" 등 위반 유형 메시지 표시 → "스캔됨" 파란 뱃지로 통일
- **스크린샷 슬롯별 URL 추가 수정**: v-for 내 이벤트 핸들러 `idx` 클로저 캡처 문제로 항상 슬롯1에만 저장되던 문제 수정. `activeUrlSlot` ref 사용으로 교체

## [1.3.14] - 2026-02-23

### Added
- **스크린샷 슬롯별 URL 교체**: 제품 상세 → 스크린샷 탭에서 이미지가 채워진 슬롯에도 링크(URL) 아이콘 버튼 추가 (호버 시 슬롯 좌하단 표시). 빈 슬롯/채워진 슬롯 모두 URL로 추가/교체 가능
- **`POST /images/download-screenshot-slot/{id}?slot={slot}&url={url}`** 엔드포인트: 특정 슬롯에 URL 이미지를 다운로드하여 저장 (기존 슬롯 파일 자동 삭제 후 교체)
- **`imagesApi.downloadScreenshotBySlot(productId, url, slot)`**: 프론트엔드 API 클라이언트 메서드 추가

### Changed
- **Bing Image Search 기본값 OFF**: `bingImageSearch` 기본값을 `true` → `false`로 변경 (설정에서 명시적으로 활성화해야 사용 가능)

## [1.3.13] - 2026-02-23

### Fixed
- **config.py 어드민 판별 enum 버그 수정**: `current_user.role != "admin"` (enum vs 문자열 비교 → 항상 True) → `current_user.role.value != "admin"` 으로 수정. 이 버그로 인해 어드민 포함 모든 사용자가 항상 마스킹된 config를 받았고, 로그인 후 API 키 "저장됨" 표시가 정상 동작하지 않던 근본 원인

### Changed
- **Bing Image Search ON/OFF 토글**: Settings → Metadata에서 이미지 검색 기능 자체를 활성화/비활성화할 수 있는 토글 추가. 토글 OFF 시 API 키 입력 영역 숨김 및 검색 엔드포인트에서 비활성화 응답 반환
- **config.json 마이그레이션**: 서버 시작 시 `googleApiKey`, `googleSearchEngineId` 필드 자동 삭제 및 `bingImageSearch: true` 기본값 추가

## [1.3.12] - 2026-02-23

### Changed
- **이미지 검색 엔진 교체**: Google Custom Search API → **Bing Image Search API** (Azure Cognitive Services)
  - Google Programmable Search Engine의 "전체 웹 검색" 옵션 폐지로 실질적 검색 불가 문제 해결
  - Bing은 전체 웹 이미지 검색 지원, 월 1,000건 무료 (F0 티어)
  - `backend/app/core/bing_image_search.py` 신규 생성
  - `images.py`: `GoogleImageSearcher` → `BingImageSearcher`, `bingApiKey` config 읽기
  - `config.py`: `SENSITIVE_FIELDS`에 `bingApiKey` 추가, 기본값에서 Google 키 제거
  - `Settings.vue`: Google API 키 + Search Engine ID 섹션 → Bing API 키 단일 입력으로 교체
  - `ko.js` / `en.js`: 로케일 문자열 Bing 기준으로 업데이트

## [1.3.11] - 2026-02-23

### Fixed
- **Google Image Search Misconfiguration Detection**: When Google Programmable Search Engine returns `totalResults: "0"` (indicating it is NOT configured for "Search the entire web"), now raises a clear error instead of showing "검색 결과가 없습니다". New message guides user to: (1) visit https://programmablesearchengine.google.com, (2) enable "전체 웹 검색", (3) enable "이미지 검색" feature.
- **Image search error propagation**: `GOOGLE_SEARCH_ENGINE_MISCONFIGURED` sentinel exception propagates from `google_image_search.py` through `images.py` with actionable setup instructions.

## [1.3.10] - 2026-02-23

### Fixed
- **AI Metadata 400 Error (Root Fix)**: `/metadata/test` endpoint was receiving API key from frontend — but `GET /api/config/metadata` returns `***` (masked) for non-admin users, so `***` was sent to Gemini → "API key not valid". Fixed: backend now ALWAYS reads API key directly from `config.json` (same as `/scan/test-ai-api` which worked). Frontend no longer sends API keys — only sends `ai_provider` / `ai_model` / `custom_prompt`.
- **MetadataTestDialog / ViolationAISearchDialog**: Removed `geminiApiKey`/`openaiApiKey` refs and config reads for sensitive fields; server sources keys from config internally.

## [1.3.9] - 2026-02-22

### Fixed
- **AI Matching Always Blocked**: `filename_violations.py` and `scan.py` were checking `metadata_config.get('useAI', False)` — but config stores `scanMethod: 'ai'`, never `useAI: true` → always `False` → all AI matching blocked with "AI 비활성화" error. Fixed to `scanMethod == 'ai'`
- **API Key Never Saved (First Entry)**: Settings.vue `saveMetadataSettings` sent `geminiApiKey: editingGeminiKey ? value : ''` — when no key existed yet (`hasGeminiKey=false`), `editingGeminiKey` was also `false` → sent `''` → backend preserved existing `''` → key never written. Fixed: also sends value when `!hasGeminiKey` (first-time entry)
- **ViolationAISearchDialog Mobile**: Error action buttons now stack vertically on mobile (`grid grid-cols-1 sm:grid-cols-3`); save button expands to full width on mobile; modal height constrained with `max-height: 100dvh`

## [1.3.8] - 2026-02-22

### Fixed
- **API Key Not Persisting (Root Fix)**: Completely removed Fernet encryption from config.py — was the root cause of all API key issues since Docker restart regenerated the encryption key making stored ENC: values unreadable
- **API Key Overwrite Prevention**: `update_config_section` now preserves existing non-empty sensitive fields when incoming value is empty string — prevents accidental key overwrite when saving other settings
- **Legacy ENC: Cleanup**: `_migrate_config()` now detects and clears unreadable ENC:-prefixed values on load (user prompted to re-enter)

### Changed
- **API Key UX in Settings**: API key fields now show "저장됨 ✓" green badge instead of actual key value — click "수정" button to change, "취소" to cancel — key is never sent to frontend after save, preventing exposure and accidental overwrite

## [1.3.7] - 2026-02-22

### Fixed
- **AI Matching 400 Error (Critical)**: `products.py` and `scan.py` regenerate-metadata endpoints were creating `AIMetadataGenerator()` without `provider` parameter, defaulting to OpenAI even when Gemini is configured — Gemini API key was sent to OpenAI endpoint → 400 "API key not valid"
- **Wrong API Key Field**: `products.py` read `'apiKey'` (old legacy field) instead of `'openaiApiKey'`/`'geminiApiKey'`; now reads provider-specific key
- **Wrong Method Call**: `generate_metadata()` (non-existent) → `generate_detailed_metadata()` with proper field mapping (`developer`→`vendor`, `description_short`→`description`)
- **Google Image Search ENC: Values**: `images.py` read `config.json` directly, bypassing ENC: decryption; now uses `load_config()` which handles legacy encrypted values

## [1.3.6] - 2026-02-22

### Fixed
- **API Key Not Saving**: Removed Fernet encryption from config storage — encryption key file didn't persist across Docker restarts causing decryption failures; API keys are now stored as plaintext in config.json (personal NAS use)
- **API Key Field Name Mismatch**: Default config used `apiKey` but code saved/read `openaiApiKey`; added auto-migration on load (`apiKey` → `openaiApiKey`) and updated default config
- **AI 400 Error in FilenameViolations**: Added `apiKey` fallback when reading OpenAI key so legacy configs still work after migration
- **docker-compose.yml Version Tag**: Changed hardcoded `1.2.1` → `latest` so Synology Container Manager detects image updates automatically

### Changed
- **TinyMCE Mobile Optimization (TipsDetail)**: Responsive prose size (`prose-sm/base/lg`), reduced padding on mobile, added CSS for table overflow-scroll, image max-width, code word-wrap, heading size scaling
- **TinyMCE Mobile Optimization (ProductDetail Install)**: Added `.tinymce-content` CSS class with same mobile-responsive rules for installation guide tab

## [1.3.5] - 2026-02-21

### Added
- **사이드바 통합검색**: 데스크탑 사이드바 상단에 검색바 추가, 검색어 입력 후 Enter로 스토어 페이지 이동
- **모바일 검색**: 모바일 하단 네비에 검색 아이콘 추가, 탭 시 검색 오버레이 표시 후 스토어 이동
- **스토어 URL 검색 파라미터**: `/discover?search=키워드` URL로 검색 상태 전달 지원
- **로그인 30일 유지**: 로그인 페이지에 "로그인 상태 유지 (30일)" 체크박스 추가 — 체크 시 localStorage, 미체크 시 sessionStorage 사용
- **스토어 NEW 배지**: 등록 후 3일 이내 신규 제품에 카드 좌상단 NEW 배지 표시

### Changed
- **Scraps 모바일 최적화**: 모바일에서 카드뷰 표시 (router-link 기반), 데스크탑은 기존 테이블뷰 유지
- **스크린샷 URL 추가 슬롯별 적용**: 전역 "URL로 추가" 버튼 제거, 각 빈 슬롯(1~4)에 개별 URL 입력창 추가
- **팁&테크 모바일 클릭 수정**: 모바일 카드 `<div @click>` → `<router-link>` 변경으로 iOS 클릭 딜레이 해소
- **Discover 무한스크롤 모바일 수정**: IntersectionObserver root를 `.main-content-area` 스크롤 컨테이너로 지정

## [1.3.4] - 2026-02-21

### Fixed
- **i18n Missing Keys in Product Edit**: Added `featuresHint`, `featuresPlaceholder`, `addRequirement`, `formatsHint`, `formatsPlaceholder` keys to `ko.js` and `en.js`; product detail edit mode now shows properly translated placeholder/hint text instead of raw key strings
- **Rescan After Product Delete**: `cleanup_deleted_files()` API and `_cleanup_deleted_files()` scanner function now reset `FilenameViolation.is_resolved=False` before deleting products (previously only `delete_product()` did this); also fixed `_add_scanned_file()` to reset orphaned violations (is_resolved=True but product_id=NULL after CASCADE) so files always re-appear in detected list after product deletion

## [1.3.3] - 2026-02-21

### Fixed
- **Settings Navigation from AI Error**: `sections.some()` was called on a Vue computed ref (not an array) in `onMounted`, throwing a `TypeError` that caused the entire settings initialization to fail — fixing this also resolves the next two issues
- **URL Overwrite After AI Error**: Because `onMounted` threw early, `accessUrl` and `apiUrl` were never updated from `config.json`, staying at their `VITE_APP_URL`/`VITE_BACKEND_URL` ENV defaults (e.g., `https://app.nuripc.kr`); now fixed by the above
- **API Key Disappears After AI Error**: Same root cause — config was never loaded, so metadata settings (including API key) displayed empty; now fixed
- **AI Search Dialog Positioning**: Changed `md:inset-x-auto` → `md:inset-x-0` so the modal has proper left/right anchors; with `mx-auto` and `max-w-4xl`, the dialog now centers horizontally on desktop

## [1.3.2] - 2026-02-21

### Fixed
- **Attachment Upload in Docker**: `ATTACHMENTS_DIR` was hardcoded to dev path (`/home/nuricom/.../attachments`); fixed to use `settings.ATTACHMENTS_DIR` and added env var to `docker-compose.yml` (`/app/data/attachments`)
- **API Key Singleton**: `_get_fernet()` now uses a module-level singleton (`_fernet_instance`) so the same Fernet key is used throughout the process lifetime, preventing key mismatch when file persistence fails
- **Scan Exclusion Validation**: Software file extensions (`.exe`, `.iso`, `.zip` etc.) can no longer be added to file pattern exclusions; validated in both frontend and backend

## [1.3.1] - 2026-02-21

### Fixed
- **Scanner SQL Transaction**: Each file's DB operation now wrapped in savepoint (`begin_nested()`), preventing `InFailedSqlTransaction` when one file fails
- **API Key Persistence**: Encryption key now stored in `data/.encryption_key` file (volume-mounted), survives Docker rebuilds; legacy SECRET_KEY-encrypted values auto-migrate on next save
- **Mobile Home Spacing**: Increased bottom padding from `pb-20` to `pb-28` to prevent bottom nav overlap
- **Docker Image URL**: TinyMCE external images now saved with relative path `/static/eximage/...` instead of full `http://localhost:8110/...`, fixing broken image links in Docker/reverse proxy environments
- **Login Token Expiry**: Fixed `ACCESS_TOKEN_EXPIRE_MINUTES` default in `docker-compose.yml` to 43200 (30 days)

## [1.3.0] - 2026-02-21

### Added
- **Infinite Scroll**: Store(Discover) page replaced pagination with IntersectionObserver-based infinite scroll
- **Product Detail Edit**: Features, System Requirements, Supported Formats now editable in product detail edit mode
- **Screenshot URL Add**: Added URL input to add screenshots by URL in product detail page
- **Same-folder File Grouping**: Files in the same folder are now recognized as the same product during AI matching
- **Duplicate Detection Message**: AI matching now shows clear duplicate info when a similar product already exists
- **Login Persistence**: Token expiry extended to 30 days; frontend validates JWT `exp` claim on startup
- **Screenshot URL API**: `addScreenshotByUrl()` function connects to `downloadScreenshots` API endpoint

### Changed
- **AI Search Text**: Renamed "AI 매칭" → "AI 검색" throughout UI (ko/en locales, tooltips, messages)
- **Tips Attachment Limits**: Max file size 10MB → 500MB, max file count 5 → 20 (frontend + backend)
- **Filename Rule Check Removed**: Scanner no longer validates filename naming conventions; only scan exclusion rules apply
- **Favorites Layout**: Reduced card size (6-column grid, 48px icon, compact padding)
- **Scraps Layout**: Reduced table row height and font size; date column hidden on mobile
- **Home Mobile Spacing**: Added `pb-20` bottom padding on mobile to prevent content cutoff

### Fixed
- **TinyMCE Edit Mode**: Content now displayed correctly when editing Tips posts (added `setContent()` after API load)
- **External Image Save**: Fixed httpx client with `follow_redirects=True, verify=False`; use `get_backend_url()` instead of empty `BACKEND_URL`
- **Product Rescan After Delete**: `delete_product()` now resets `FilenameViolation.is_resolved` to `False` so files can be rescanned
- **AI Matching Duplicate Order**: `create-product` response now includes `is_duplicate`/`duplicate_reason` fields; frontend shows info dialog on duplicates
- **Same-folder AI Matching**: Both `create-product` and `create-product-with-metadata` endpoints now group and match all unresolved violations in the same folder together

## [1.2.0] - 2026-02-10

### Added
- **Version-Aware AI Matching**: AI auto-matcher now differentiates products by version (e.g., Office 2003/2007/2010 as separate products)
  - Added `extract_version_from_title()` for year/version extraction
  - Pre-check existing products before making AI API calls to reduce costs
- **PWA Scroll Containment**: Fixed mobile PWA scroll bounce issues
  - Added `overscroll-behavior: none` and `position: fixed` on html
  - Safe area support with `env(safe-area-inset-bottom)` for iPhone home indicator
  - `touch-action: pan-x` on bottom nav to prevent vertical gesture conflicts
- **Missing i18n Key**: Added `openaiPricingTitle` translation key for both Korean and English
- **Standard PWA Meta Tag**: Added `mobile-web-app-capable` alongside existing Apple-specific tag

### Changed
- **Mobile Optimization**: Comprehensive responsive improvements across multiple pages
  - Home/Favorites/Scraps: Scrollable headers on mobile (no longer fixed), reduced banner height
  - FilenameViolations: Split action buttons for mobile/desktop, compact stats cards
  - ChangePassword: Responsive padding, back button, mobile-friendly inputs
  - Discover: Separated search input from sort/cleanup buttons on mobile
  - Settings: Registration settings flex-col layout on mobile
  - ViolationAISearchDialog: Full-screen on mobile with always-visible apply button
  - ImageManager: Responsive padding and text sizes

### Fixed
- **Image Upload Display**: API now returns relative paths instead of full URLs for proper proxy routing
  - Logo upload/download endpoints return `/static/...` paths
  - Frontend `getIconUrl()`/`getScreenshotUrl()` extract relative paths from legacy full URLs
- **AI Matching Duplicates**: Existing product check moved before AI call to prevent waste
- **Apply Button Not Clickable**: ViolationAISearchDialog modal restructured with flex column layout
- **Debug Console Logs**: Removed 4 debug `console.log` statements from Settings.vue

## [1.2.2-beta] - 2026-01-19

### Added
- **Patch Links Feature**: Added ability to add up to 5 related links in product detail page patches/cracks section
  - Admin can add/edit/delete links with title and URL
  - Links are displayed for all users with click-to-open functionality
  - Added translation keys for link feature in Korean and English
  - Added database migration for `patch_links` JSON field in products table

### Fixed
- **Scrap Date Localization**: Fixed hardcoded 'ko-KR' locale in Scraps page date formatting
  - Date format now follows current language setting (localStorage or browser language)
- **Database Migration**: Added Alembic migration and field validators for patch_links feature
  - Fixed "Exception in ASGI application" error
  - Added conversion logic between PatchLink objects and database JSON storage

### Technical Changes
- `backend/app/models/product.py`: Added `patch_links` JSON column
- `backend/app/schemas/product.py`: Added `PatchLink` schema and field validator
- `backend/app/api/products.py`: Added validation for max 5 links and object-to-dict conversion
- `frontend/src/views/ProductDetail.vue`: Added link management UI (183+ lines)
- `frontend/src/views/Scraps.vue`: Dynamic locale support for date formatting

## [1.2.1-beta] - 2026-01-19

### Fixed
- **Category Label Display**: Fixed category labels to display from config.json instead of translation system
  - Settings - Category Management now shows Korean labels correctly
  - Changed `getCategoryLabel()` function to prioritize config.json labels
  - Updated "Source" category label from "소스" to "소스코드"
  - Synchronized default config across backend and config.json

### Technical Changes
- `frontend/src/views/Settings.vue`: Modified `getCategoryLabel()` to use config.json labels first
- `data/config.json`: Updated Source category label
- `backend/app/api/config.py`: Synced default config

## [1.2.0-beta] - 2026-01-03

### Added
- **Complete i18n Support**: Full internationalization with auto language detection
  - Korean and English language support
  - Automatic language detection from browser settings
  - Language switcher in UI
  - All UI elements translated (2000+ translation keys)

### Changed
- Enhanced filename parsing rules for better AI matching
- Improved documentation with parsing patterns analysis (1,836 files analyzed)
- Simplified CORS settings in documentation

## [1.0.0] - 2025-12-29

### Features

#### Phase 1 - MVP
- Implemented Docker environment (FastAPI + Vue + PostgreSQL)
- Added basic file scanning from configured folders to database
- Implemented login and download functionality
- Created basic list view UI
- Added JWT authentication with OAuth2PasswordBearer
- Implemented first-run setup page for admin account creation

#### Phase 2 - Metadata & AI Integration
- Enhanced filename parsing algorithms (FilenameParser with noise word filtering)
- Integrated OpenAI API (GPT-4o-mini) for automatic metadata generation
- Implemented icon crawling and local storage (IconCache with httpx)
- Added fallback mechanism when AI is unavailable
- Created admin page with AI toggle option

#### Phase 3 - Enhancement
- Implemented auto-scan scheduler (APScheduler with cron expressions)
- Added scheduler management UI (AdminScheduler.vue)
- Created ScanHistory tracking model
- Implemented advanced search and filtering (category, vendor, search)
- Added autocomplete suggestions
- Optimized download with X-Accel-Redirect headers
- Implemented category-based product grouping (Netflix-style)
- Added scheduler persistence via Settings table

#### Additional Features
- Implemented favorites and scraps functionality
- Added Tips & Tech board with TinyMCE editor
- Created folder browser for scan path configuration
- Implemented mobile responsive layout
- Added dark mode support
- Implemented internationalization (i18n) with Vue I18n
- Added user management and invitation system
- Implemented metadata testing dialog
- Added filename violation tracking
- Created unmatched items management system

### Infrastructure
- Set up version management system
- Implemented automatic versioning with standard-version
- Added version API endpoints
- Created CHANGELOG automation

---

**Note**: This is the first stable release (v1.0.0). Previous development was tracked in phases but not versioned.
