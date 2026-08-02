# AI 메타데이터 고도화 계획

> 기반 문서: `AI_METADATA_TEST_SAMPLES.md` (파일명 10개 실측 테스트에서 발견한 파서/AI 메타데이터 문제)
> 작성일: 2026-08-02

## 배경

`AI_METADATA_TEST_SAMPLES.md`에서 실제 검색된 목록 파일명 10개를 테스트한 결과, 사용자가 지적한 3가지 방향으로 개선이 필요함을 확인했다.

1. **공식적으로 알려진 프로그램**은 "제조사 / 프로그램명 / 연도 / 연도별 버전 / 지원 OS"라는 일관된 구조로 정리될 수 있는데, 현재는 이 5개 필드가 파일명 파싱 단계에서부터 서로 뒤섞이거나 소실됨 (예: `software_name`에 vendor·OS가 중복으로 남거나, `v2026`처럼 연도가 문자에 바로 붙으면 연도 자체가 소실됨).
2. **`patch`, `fix`, `with keygen`, `include ...`** 같은 문구는 "이 파일이 곧 패치다"가 아니라 **"메인 프로그램에 패치/크랙/키젠이 함께 포함되어 있다"**는 의미인데, 현재 분류 로직(`classify_file`)은 이를 구분하지 못하고 파일 전체를 `patch`로 오분류할 수 있음.
3. **낮은 신뢰도 항목(개인 개발자가 블로그/커뮤니티에 공유한 프로그램)**은 파일명만으로는 정확한 메타데이터를 만들 수 없으므로, **사용자가 블로그 URL이나 설명 파일을 제공하면 그 내용을 근거로 AI가 메타데이터를 생성**하는 별도 경로가 필요함.

아래는 이 3가지를 Phase로 나눈 구현 계획이다. 코드는 아직 변경하지 않았다.

---

## 현재 구조 확인 (계획 근거)

- `FilenameParser` (`backend/app/core/parser.py`): 파일명 → `software_name/version/vendor/year/is_portable` 추출. `NOISE_WORDS`에 `fix`가 없고, `_extract_year`가 `\b(20\d{2})\b`를 써서 `v2026`/`_2024_`처럼 연도가 단어문자(문자/숫자/`_`)에 바로 붙으면 매칭 실패 (재현 확인됨).
- `classify_file` (`backend/app/core/classifier.py`): 파일 1개를 `product/patch/language_pack/manual/update` 중 하나로 분류. `_PATCH_KEYWORDS`에 `fix`가 이미 포함되어 있어서, **"Autodesk Maya v2026 + Fix (macOS).zip"처럼 메인 설치파일 안에 fix가 포함된 케이스도 파일 전체가 `patch`로 분류됨** (규칙 2가 무조건 우선 적용, 재현 확인).
- `Product` 모델(`backend/app/models/product.py`): `vendor`, `platform`(문자열), `patch_links`(JSON, 최대 5개, "패치/크랙 관련 링크" 용도로 이미 존재) 필드는 있지만, **연도를 담는 전용 컬럼은 없음** — 현재는 `title` 문자열 안에 연도가 섞여 들어가 있음.
- `AIMetadataGeneratorV2` (`backend/app/core/ai_metadata.py`): `generate_detailed_metadata(filename, parent_folder, custom_prompt)` — 파일명 기반 컨텍스트만 프롬프트에 넣음. **외부 텍스트(URL/파일 본문)를 근거로 메타데이터를 생성하는 경로는 없음.** 신뢰도(confidence) 필드도 없음 — AI가 모든 필드를 "REQUIRED"로 강제 응답하게 되어 있어 모르는 항목도 그럴듯하게 채워 넣을 위험이 있음.
- `MetadataCache` 모델에는 `confidence_score` 필드가 있지만, 이건 현재 라우터에 마운트되지 않은 죽은 코드(`app/api/unmatched.py`, `main.py`에 `include_router` 없음)에서만 쓰이는 필드라 **실제로 살아있는 매칭 경로(`auto_matcher.py`, `filename_violations.py`)에는 신뢰도 개념이 아예 없음.**
- 현재 라이브 설정(`data/scan_exclusions.txt`, 직접 확인함)에 `*.txt`, `*.nfo`, `*.md` 등이 이미 제외 패턴으로 등록되어 있어 **스캔 대상에서 완전히 제외됨** — 그런데 이런 파일이 오히려 저신뢰도 프로그램의 설명 파일(readme, nfo)일 가능성이 높아, 현재는 유용할 수 있는 소스를 스캔 단계에서 이미 버리고 있음.

---

## Phase 1 — 표준 필드 구조화 (제조사 / 프로그램명 / 연도 / 버전 / 지원 OS)

**목적**: 공식적으로 알려진 프로그램은 5개 필드가 항상 명확히 분리되어 저장되도록 한다.

### 1-1. 파서 정규식 버그 수정 (`parser.py`)
- `_extract_year`를 `\b(20\d{2})\b` 대신 **숫자가 아닌 문자 경계**를 보는 방식으로 교체 (예: `(?<!\d)(19|20)\d{2}(?!\d)` — 앞뒤에 다른 숫자만 없으면 매칭, `v`/`_`에 바로 붙어도 인식). `_extract_version`의 `v(\d+)` 계열 패턴도 동일하게 점검.
- `NOISE_WORDS`에 `macos`, `dlm` 추가. `vendor`를 `software_name`에서 중복 제거하는 후처리 추가 (현재 vendor 필드는 정확히 뽑히는데 name에도 남아있는 문제, `AI_METADATA_TEST_SAMPLES.md` ②③ 참고).
- `KNOWN_VENDORS`에 없는 경우 첫 단어를 vendor로 추정하는 폴백 제거 — 모르면 `null` (briss 케이스처럼, 잘못된 추정보다 안전).

### 1-2. `year`를 Product의 정식 컬럼으로 승격
- 현재 연도는 `title` 문자열에만 섞여 있어서, 검색/정렬/버전 구분(지난 세션에서 고친 AutoCAD 2026 vs 2027 이슈)이 전부 문자열 정규식에 의존하고 있음. `products` 테이블에 `release_year` (nullable Integer) 컬럼 추가를 제안.
  - alembic 마이그레이션 1개 추가, 기존 `title`에서 backfill 가능한 행은 마이그레이션 스크립트에서 채움.
  - `find_similar_product`(auto_matcher.py)의 버전 분리 가드가 문자열 정규식 대신 이 컬럼을 직접 비교하도록 변경 → 지난 세션에 발견한 "폴백 정규식도 같은 버그를 공유한다"는 리스크가 구조적으로 해소됨.
  - 목록/상세 API 응답, 검색 필터(`category`처럼 `release_year` 필터 추가 가능)에도 활용.
- `platform`은 이미 컬럼이 있으니 AI 프롬프트가 항상 `"Windows" | "macOS" | "Linux" | "Cross-platform"` 중 하나로만 답하도록 enum성 지침을 프롬프트에 명시(현재도 비슷하게 되어 있으나 자유 텍스트 허용 폭이 넓음).

### 1-3. AI 프롬프트 재정비 (`ai_metadata.py`)
- `title`에는 "제조사/버전/OS를 빼고 프로그램명 + (필요시 연도)만" 넣도록 더 명확히 지시 (현재 title 지침이 "연도를 포함하라"만 있고 vendor/OS를 빼라는 지침은 없어서 AI가 `"Autodesk AutoCAD macOS"` 같은 답을 줄 수 있음 — 파서 버그와 같은 실수를 AI도 할 수 있으므로 프롬프트에서 명시적으로 분리 요청).
- `developer`(vendor), `platform`, 그리고 새 `release_year` 필드를 스키마에 명시적으로 분리해서 요청.

---

## Phase 2 — "포함됨" 문구와 "그 자체가 패치임"을 구분

**목적**: `+ Fix`, `with Keygen`, `Incl. Patch`, `include Crack` 같은 문구가 나오면 **메인 제품 설치파일에 패치/크랙/키젠이 동봉되어 있다는 태그**로 처리하고, 파일 자체를 patch로 오분류하지 않는다.

### 2-1. "연결어 + 패치키워드" 패턴을 별도로 인식 (`classifier.py`)
- 현재 규칙 2("패치 키워드가 combined 문자열 어디에든 있으면 patch")를 다음처럼 세분화:
  1. 패치 키워드 앞에 **연결어**(`+`, `with`, `incl`, `include`, `included`, `bundled`)가 붙어 있는 경우 (예: `... v2026 + Fix`, `... with Keygen`) → **규칙 2(patch 분류)만 건너뛰고, 다른 규칙(1/3/4/5/6)은 그대로 평가**해서 원래대로라면 나왔을 분류를 따르게 함. 동시에 "포함된 부가요소" 태그는 별도로 기록.
  2. 연결어 없이 패치 키워드가 파일명의 핵심인 경우 (예: `AutoCAD_2024_Patch.exe`, `Keygen.exe`, `Crack_Only.zip`, `Maya_2026_Patch.exe`) → 기존대로 `patch` 분류.
- 정규식 초안: `r'(?:\+|with|incl\.?|include[sd]?|bundled)[\s_]+(fix|crack|keygen|patch|serial)'` (공백뿐 아니라 언더스코어 구분자도 커버해야 함 — `AutoCAD_2024_with_Keygen.exe`처럼 실제로 밑줄로 이어지는 경우가 많음).
- **테스트셋으로 두 분기를 모두 확인함**: `Autodesk Maya v2026 + Fix (macOS).zip` / `Autodesk AutoCAD v2026 + Fix (macOS).zip` → 연결어 매칭됨(제품으로 유지되어야 함). `Maya_2026_Patch.exe`, `Keygen.exe`, `Crack_Only.zip` → 연결어 없이 매칭 안 됨(기존대로 patch 유지, 회귀 없음).
- **규칙 1(메뉴얼 확장자)과의 상호작용 확인**: `설치법 with crack.pdf` 같은 경우 연결어 패턴에도 걸림 — 이런 `.pdf`/`.doc` 파일은 "제품"이 아니라 매뉴얼/가이드 성격이 강하므로, 연결어 예외는 **규칙 2만 건너뛰게 하고 규칙 1(메뉴얼 판정)은 그대로 먼저 평가되도록 순서를 유지**해야 함 (연결어 예외를 이유로 무조건 `product`로 강제하면 안 됨). 이 상호작용은 구현 시 별도 테스트 케이스로 반드시 검증.

### 2-2. "포함된 부가요소" 저장 위치
- `Version`(또는 `FilenameViolation`)에 가벼운 컬럼 추가: `bundled_extras` (JSON 배열, 예: `["crack"]`, `["keygen"]`) — 또는 최소 침습적으로 기존 `Product.patch_links`(이미 "패치/크랙 관련 링크" 용도로 존재)에 `{"title": "포함된 크랙", "url": null, "note": "파일명에서 자동 감지됨"}` 형태로 넣는 방법도 검토 가능. **DB 마이그레이션 최소화를 위해 우선 후자(기존 `patch_links` 재사용)로 시작하고, 필요해지면 전용 컬럼으로 분리하는 순서를 제안.**
- 상세 페이지에서 "이 버전은 패치/크랙이 포함되어 있습니다" 배지로 노출 가능 (프론트 작업은 별도 범위).

### 2-3. `parser.py`의 `NOISE_WORDS`와 `classifier.py`의 `_PATCH_KEYWORDS` 통합
- 현재 두 파일이 "fix" 같은 키워드를 각자 따로 관리하고 있어(하나는 없고 하나는 있음) 서로 어긋남. 공용 키워드 사전 모듈(`app/core/keywords.py` 등)로 통합해 두 로직이 같은 소스를 참조하도록 정리. (부가요소 키워드가 `software_name`에서도 항상 제거되도록 보장하는 효과도 있음.)

---

## Phase 3 — 저신뢰도 프로그램: URL/설명파일 기반 메타데이터 생성

**목적**: 개인 개발자가 블로그/커뮤니티에 공유한, 웹 검색만으로는 AI가 답을 낼 수 없는 프로그램에 대해 **사용자가 근거 자료(URL 또는 파일)를 제공하면 그 내용을 근거로 메타데이터를 생성**한다.

### 3-1. 신뢰도를 먼저 정의해야 함 (선행 과제)
- 지금 시스템엔 "낮은 신뢰도"를 판별할 방법이 없음 (앞서 확인한 대로 `confidence_score`는 죽은 코드에만 존재).
- **AI 자체 신뢰도 자기보고는 신호로 쓰지 않는다.** `AI_METADATA_TEST_SAMPLES.md` §4에서 이미 지적했듯, 현재 프롬프트는 모든 필드를 "REQUIRED"로 강제해 AI가 근거 없이 답을 지어내는 구조인데, **그 지어낸 답을 만든 같은 호출에게 "이거 확실해?"라고 물어봐야 응답의 신뢰도를 스스로 검증할 근거가 없음** — `OSH_v25.10_by_Remiz_64bit.iso`처럼 애초에 존재하지 않는 제품을 그럴듯하게 지어냈다면, `confidence: high`라고도 똑같이 그럴듯하게 답할 위험이 큼.
- 대신 **파이프라인이 이미 관찰할 수 있는 신호**로 신뢰도를 계산한다 (AI 호출과 독립적):
  - `vendor`가 `KNOWN_VENDORS`(또는 Phase 1에서 AI가 반환한 `developer`)와 매칭되는가
  - `release_year`(1-2) 추출에 성공했는가
  - `MetadataCache`에 이미 동일 제품명으로 hit가 있는가 (재확인된 이력)
  - 정규화된 제품명 길이가 너무 짧거나(`briss`처럼 3자 이하 등) 일반명사에 가까운가
  - 테스트셋 검증: ②③④⑤⑥(Autodesk 계열)은 vendor 매칭 + year 추출 성공 → 신호상 high. ①⑦⑨⑩(E.Z.Subtitles/PDF-Pro/BluePDF/OSH)은 vendor 미매칭 + (수정 전 기준) year 추출 실패 → 신호상 low. 실제 정답표(§2 요약표)의 신뢰도 판정과 정확히 일치함 — 즉 자기보고가 아니라 이 규칙 기반 스코어를 low/high 판별의 1차 기준으로 삼는다.
  - AI의 자체 신뢰도 필드는 참고용 보조 신호로만 프롬프트에 추가하고(있으면 도움은 되므로), **URL-소스 흐름을 노출할지 말지의 최종 판단은 위 규칙 기반 스코어로 한다.**

### 3-2. 새 백엔드 엔드포인트: 소스 기반 메타데이터 생성
- `POST /api/scan-items/{scan_item_id}/generate-metadata-from-source`
  - body: `{ "url": "https://..." }` 또는 `multipart/form-data` 파일 업로드 (txt/md/pdf 등) — 하나만 필수, 관리자 전용.
  - URL인 경우: `httpx`로 GET → HTML에서 본문 텍스트만 추출 (신규 의존성 필요, 아래 3-4 참고) → 5,000~8,000자로 트렁케이트.
  - 파일인 경우: 확장자별로 텍스트 추출 (`.txt/.md`는 그대로, `.pdf`는 신규 의존성 필요).
  - 추출한 텍스트 + 원본 파일명을 새 함수 `AIMetadataGeneratorV2.generate_metadata_from_source(source_text, filename_hint)`에 전달.
  - 응답은 기존 `generate_detailed_metadata`와 동일한 JSON 스키마 → 기존 `create-product-with-metadata` 플로우에 그대로 재사용 가능 (프론트에서 "생성된 메타데이터 미리보기 → 확인 후 등록" 동선 재사용).

### 3-3. AI 프롬프트: "제공된 원문에서만 답하라"
- `generate_metadata_from_source`용 프롬프트는 기존 프롬프트와 달리 **"아래 제공된 텍스트에 명시된 내용만 사용하고, 텍스트에 없는 정보는 추측하지 말고 빈 값으로 남겨라"**를 명시해야 함 — 그렇지 않으면 AI가 여전히 사전 지식으로 답을 지어내 소스 제공의 의미가 없어짐. 이게 Phase 3에서 가장 중요한 프롬프트 설계 포인트.

### 3-4. 신규 의존성 (requirements.txt)
- 현재 HTML 파싱/PDF 텍스트 추출 라이브러리가 전혀 없음 (`httpx`만 존재, `CLAUDE.md`가 설명하는 "9개 소스 우선순위 크롤링"은 실제로는 구현되어 있지 않고 `metadata_enricher.py`는 "웹 크롤링 없이 AI만 사용"이라고 명시되어 있음 — 문서와 실제 코드가 어긋나 있다는 점도 참고).
  - HTML → 본문 텍스트: `trafilatura` (본문만 잘 뽑아내는 가벼운 라이브러리) 또는 `beautifulsoup4` + 간단한 태그 제거.
  - PDF → 텍스트: `pypdf`.
- 둘 다 순수 텍스트 추출용으로 가볍고, 이미지 렌더링 등은 불필요.

### 3-5. 스캔 폴더에 이미 있는 설명 파일 재활용 (연계 개선)
- 현재 라이브 설정에서 `*.txt`, `*.nfo`가 스캔 대상에서 제외되고 있는데, 이 파일들이야말로 3-2의 "설명 파일"로 바로 쓸 수 있는 소스임. 스캔 시 이 파일들을 등록 대상에서는 제외하되, **"이 폴더에 readme.txt/설명.nfo가 있습니다 → 이 파일로 메타데이터 생성" 버튼을 자동으로 보여주는 방식**을 제안 (사용자가 파일을 새로 준비/업로드할 필요 없이 원클릭으로 3-2 경로를 탈 수 있음). 파일 시스템 접근이므로 `SCAN_BASE_PATH`/등록된 스캔 폴더 하위로 제한(v1.4.63에서 도입한 `_ensure_within_scan_base`와 동일한 원칙 재사용).

### 3-6. 보안 참고사항
- URL fetch는 관리자 전용이라도 SSRF 여지가 있음 (`http://169.254.169.254/...` 같은 내부 메타데이터 엔드포인트 등). `httpx` 요청 전에 사설 IP 대역(`127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.0.0/16`)으로 리졸브되는 호스트는 차단하는 기본적인 검증을 넣을 것을 권장.
- 응답 크기 제한(예: 5MB) 및 타임아웃 설정 필수 (기존 `icon_cache.py`의 httpx 사용 패턴 참고).

---

## 제안 실행 순서

| 순서 | Phase | 작업량 | 리스크 | 근거 |
|---|---|---|---|---|
| 1 | 1-1 파서 정규식 버그 수정 | 작음 (정규식 몇 개) | 낮음 — 순수 버그 수정, 기존 동작 개선만 함 | `AI_METADATA_TEST_SAMPLES.md` 우선순위 1번 버그, 지난 세션 버전분리 수정과 직결 |
| 2 | 2-1/2-3 패치 오분류 수정 | 중간 | 낮음 — `classify_file` 규칙 순서만 변경 | 사용자가 이번에 직접 지적한 항목 |
| 3 | 1-2 `release_year` 컬럼 추가 | 중간 (마이그레이션 + auto_matcher 수정) | 중간 — 기존 문자열 기반 버전분리 로직을 대체하므로 회귀 테스트 필요 | 구조적으로 반복되는 연도 관련 버그의 근본 해결 |
| 4 | 1-3 AI 프롬프트 재정비 | 작음 | 낮음 | Phase 1 마무리 |
| 5 | 3-1 규칙 기반 신뢰도 스코어링 + UI 배지 | 작음 (AI 호출과 무관한 후처리 로직) | 낮음 | Phase 3 진입 조건 |
| 6 | 3-2~3-4 소스 기반 생성 엔드포인트 | 큼 (신규 API + 신규 의존성 + 신규 AI 함수) | 중간 — 외부 URL fetch 보안 검토 필요(3-6) | 이번 요청의 핵심 |
| 7 | 3-5 폴더 내 설명파일 자동 감지 | 작음~중간 | 낮음 | 사용성 개선, 6번에 종속 |

1~4번은 지난 세션에 발견한 버그들과 직접 연결되어 있어 먼저 처리하는 걸 권장하고, 5~7번(소스 기반 생성)은 신규 기능이라 별도 브랜치/커밋으로 분리해 진행하는 게 안전해 보입니다.
