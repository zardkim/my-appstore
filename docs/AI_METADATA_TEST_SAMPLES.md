# AI 메타데이터 생성 테스트 샘플

AI 메타데이터 생성/자동 매칭 로직을 개선하기 전, 실제 등록 대기 중인(검색된 목록) 파일명 10개를 테스트 케이스로 삼아 다음을 정리한다.

1. 파일명만 보고 실제로 어떤 프로그램인지 식별 (정답/ground truth, 신뢰도 표기)
2. 현재 `FilenameParser` (`backend/app/core/parser.py`)가 이 파일명에서 실제로 무엇을 추출하는지 (`parser.parse(filename)` 직접 실행 결과)
3. 정답과 파서 출력의 차이 — AI 프롬프트/파서가 개선되어야 할 지점

파서 출력은 2026-08-02 기준 `python3 -c "from app.core.parser import FilenameParser; FilenameParser().parse(...)"` 로 직접 실행해 확인한 실측값이다 (추정 아님).

---

## 1. 파일별 식별 결과

### ① `E.Z.Subtitles.v4.exe`
- **식별**: 자막 제작/편집 소프트웨어로 추정되나 **낮은 신뢰도**. "E.Z."가 어떤 브랜드의 약어인지 확정할 근거가 부족함 (알려진 "EZTitles"와는 표기가 다름 — EZTitles는 "EZTitles"로 붙여 쓰며 "E.Z.Subtitles"라는 정식 명칭은 확인되지 않음).
- **파서 출력**: `software_name: "Subtitles"`, `version: "4"`, `vendor: "Subtitles"`, `year: null`
- **문제점**: "E.Z." 부분이 통째로 소실되어 제품명이 "Subtitles"라는 일반명사로 축약됨 — 브랜드 식별력을 잃음. `vendor`도 `software_name`과 동일한 값으로 중복 추정되어 의미 없음.
- **개선 포인트**: 점(`.`)으로 구분된 이니셜(`E`, `Z`)이 노이즈로 오인되어 제거됨. 실제 웹 검색 없이는 정확한 제품 식별이 불가능한 대표적 **모호 케이스** — AI가 확신 없이 답을 지어내지 않고 "확인 필요"로 표시하거나 부모 폴더명 컨텍스트를 요구해야 하는 케이스로 남겨두는 게 맞음.

### ② `Autodesk AutoCAD 2027 macOS.zip`
- **식별**: **Autodesk AutoCAD 2027**, macOS 빌드. CAD/설계 소프트웨어. (신뢰도 높음 — Autodesk는 매년 신버전을 출시하며 2027 버전 네이밍은 출시 주기상 실존 가능)
- **파서 출력**: `software_name: "Autodesk AutoCAD macOS"`, `version: "2027"`, `vendor: "Autodesk"`, `year: "2027"`
- **문제점**: `software_name`에 제조사(`Autodesk`)와 플랫폼(`macOS`)이 그대로 남아 있음. `vendor`는 별도 필드로 이미 정확히 추출됐는데 `software_name`에서 중복 제거가 안 됨. `NOISE_WORDS`에 `mac`은 있지만 `macos`가 없어서 "macOS" 토큰이 그대로 통과함.

### ③ `Autodesk AutoCAD LT 2027 macOS.zip`
- **식별**: **Autodesk AutoCAD LT 2027** — AutoCAD의 2D 전용 경량판(LT = "LT" 에디션, 3D 모델링 미지원, 정가도 AutoCAD 풀버전보다 저렴). macOS 빌드.
- **파서 출력**: `software_name: "Autodesk AutoCAD LT macOS"`, `version: "2027"`, `vendor: "Autodesk"`, `year: "2027"`
- **문제점**: ②와 동일 (vendor/macOS 중복). 다만 "LT" 에디션 구분자는 정상적으로 유지됨 — 이 부분은 잘 동작. **AutoCAD와 AutoCAD LT는 실제로 다른 제품(다른 가격/기능)이므로, 자동 매칭 로직이 "AutoCAD"와 "AutoCAD LT"를 같은 제품으로 합치지 않는지 별도 검증 필요.**

### ④ `Autodesk Maya v2026 + Fix (macOS).zip`
- **식별**: **Autodesk Maya 2026**, macOS. 3D 애니메이션/VFX 제작 소프트웨어. "+ Fix"는 정품 인증 우회용 패치/크랙이 포함되어 있음을 뜻하는 배포자 표기.
- **파서 출력**: `software_name: "Autodesk Maya Fix macOS"`, `version: "2026"`, `vendor: "Autodesk"`, **`year: null`**
- **문제점 (중요)**:
  - `"Fix"`가 `NOISE_WORDS`에 없어서 제품명에 그대로 남음 (`crack`, `patch`, `keygen` 등은 필터링되지만 `fix`는 누락).
  - **`year`가 `null`로 나옴 — "v2026"처럼 버전 접두사 `v` 바로 뒤에 연도가 붙으면 연도 추출이 실패함.** 원인: `_extract_year`의 정규식 `\b(20\d{2})\b`는 `\b`(단어 경계)를 요구하는데, `v`와 `2`는 둘 다 단어 문자(`\w`)라서 그 사이에 경계가 생기지 않음. 실제로 `re.search(r'\b(20\d{2})\b', "v2026")` → `None` 을 직접 확인함 (반면 `"AutoCAD 2026"`처럼 공백 뒤에 오면 정상 매칭).
  - **연쇄 영향**: `auto_matcher.py`의 `find_similar_product` 버전 분리 가드(v1.4.63에서 수정)는 `year`가 없으면 폴더명에서 연도를 재추출하는 폴백을 쓰는데, 그 폴백 정규식도 동일한 `\b(20\d{2})\b` 계열이라 **"v2026"/"v2027" 형태의 폴더명에는 여전히 동일한 버그가 재현될 수 있음.** 즉 `Autodesk Maya v2026 + Fix (macOS)` 폴더와 `Autodesk Maya v2027 + Fix (macOS)` 폴더가 다시 같은 제품으로 오인 매칭될 위험이 남아 있음 — 후속 수정 필요 항목으로 별도 기록.

### ⑤ `Autodesk AutoCAD v2026 + Fix (macOS).zip`
- **식별**: **Autodesk AutoCAD 2026**, macOS, 패치/크랙 포함.
- **파서 출력**: `software_name: "Autodesk AutoCAD Fix macOS"`, `version: "2026"`, `vendor: "Autodesk"`, **`year: null`**
- **문제점**: ④와 완전히 동일한 두 가지 버그(`Fix` 노이즈 미필터링, `v+연도` 연도 추출 실패)가 재현됨. **④의 AutoCAD Maya 2026판과 ②의 AutoCAD 2027판(연도 표기 방식이 다름: `2027` vs `v2026`)이 같은 스캔 배치에 섞여 있다는 것 자체가, 연도 표기 방식이 파일마다 제각각이라 파서가 일관되게 처리하지 못한다는 걸 보여주는 실제 사례.**

### ⑥ `AutoCAD_2024_Korean_Win_64bit_dlm.7z`
- **식별**: **Autodesk AutoCAD 2024**, 한국어, Windows 64bit. 파일명 끝의 `dlm`은 Autodesk 공식 웹사이트의 다운로드 매니저(Download Manager)가 생성하는 설치 패키지 표기 관행과 일치함 — 즉 리패커가 임의로 붙인 태그가 아니라 **Autodesk 공식 다운로드 산출물일 가능성이 높은 특징적 단서.**
- **파서 출력**: `software_name: "AutoCAD Korean dlm"`, `version: null`, `vendor: "AutoCAD"`, **`year: null`**
- **문제점 (가장 심각)**:
  - "2024"가 완전히 소실됨 (`version`도 `year`도 모두 `null`) — ④⑤의 `v2026` 버그와 **동일한 근본 원인**임을 확인함: Python 정규식에서 언더스코어(`_`)는 단어 문자(`\w`)로 취급되므로, `\b(20\d{2})\b`는 `_2024_`에서도 앞뒤 모두 경계가 생기지 않아 매칭에 실패함 (`re.search(r'\b(20\d{2})\b', "AutoCAD_2024_Korean_Win_64bit_dlm")` → `None`, `"AutoCAD 2024 Korean"`처럼 공백이면 정상 매칭되는 것으로 직접 확인). 즉 **`v2026`이든 `_2024_`든, 연도 앞뒤가 공백/하이픈 등 진짜 비-단어문자가 아니면 전부 놓치는 구조적 버그.**
  - `vendor`가 `"AutoCAD"`로 잘못 추정됨 — `AutoCAD`는 제품명이지 제조사(Autodesk)가 아님. `KNOWN_VENDORS`에 `autodesk`는 있지만, 파일명이 `Autodesk`로 시작하지 않고 `AutoCAD`로 시작하기 때문에 매칭되지 않고, 대신 "알려지지 않은 경우 첫 단어를 vendor로 사용" 폴백이 잘못된 값을 만들어냄.
  - `Win`, `64bit`는 정상적으로 필터링됨 (이 부분은 잘 동작).
  - **이 케이스는 폴더/AI 매칭이 실패하기 가장 쉬운 케이스** — 연도가 빠지면 ②~⑤의 AutoCAD 2026/2027과 구분 없이 뒤섞일 위험이 가장 큼.

### ⑦ `PDF-Pro_5-setup.exe`
- **식별**: **"PDF Pro" 5버전**으로 추정되나, "PDF Pro"라는 이름을 쓰는 제품이 여러 업체(PDF Pro Inc./pdfpro.co, 그 외 군소 PDF 편집기들)에 존재해 **어느 회사의 제품인지는 낮은 신뢰도**. PDF 편집/변환 유틸리티인 것은 확실.
- **파서 출력**: `software_name: "PDF Pro"`, `version: null`, `vendor: "PDF"`, `year: null`
- **문제점**: `setup`은 정상적으로 제거됐지만 `5`(버전)도 함께 사라짐 — `version` 추출 정규식이 언더스코어/하이픈으로 분리된 단독 한 자리 숫자(`_5-`)를 버전으로 인식하지 못함. `vendor: "PDF"`는 사실상 제품명 앞부분을 그대로 가져온 것이라 신뢰할 수 없는 추정값.

### ⑧ `briss-0.9.zip`
- **식별**: **briss** — PDF 여백을 잘라내는(crop) 오픈소스 Java 유틸리티 (briss.sourceforge.net). 버전 `0.9`. **신뢰도 높음** — 이름이 흔한 단어가 아니라 고유 프로젝트명이라 식별이 명확한 대조군 케이스.
- **파서 출력**: `software_name: "briss"`, `version: null`, `vendor: null`
- **문제점**: 제품명 자체는 정확히 추출됐으나, 하이픈 뒤 버전(`0.9`)이 `version` 필드로 못 들어감 — `_extract_version`의 패턴들이 `단어-숫자.숫자` 형태(구분자 없이 붙어있는 `briss-0.9`)를 포착하지 못함. `vendor: null`은 이 경우 오히려 정직한 결과 (briss는 개인 개발자의 단일 프로젝트라 별도 vendor가 없는 게 맞음) — **모르면 null을 두는 게 잘못된 추정보다 낫다는 걸 보여주는 좋은 대조 사례.**

### ⑨ `BluePDF_v1.2.zip`
- **식별**: **BluePDF** — PDF 변환/생성 관련 유틸리티로 추정되나 **낮은 신뢰도** (지명도가 낮아 정확한 제조사/기능 확인 어려움). 버전 `1.2`.
- **파서 출력**: `software_name: "BluePDF v1"`, `version: "1.2"`, `vendor: "BluePDF"`
- **문제점**: `version`은 `1.2`로 올바르게 추출됐는데, **`software_name`에 `"v1"`이 중복으로 남아 있음** — `_extract_software_name`이 버전 문자열(`1.2`)을 공백 기준으로 쪼개(`"1"`, `"2"`) 각각 제거를 시도하면서 `v1.2`의 `v1` 토큰 자체는 지우지 못하는 케이스로 보임. `software_name`에 버전 잔여물이 남는 전형적 버그 사례.

### ⑩ `OSH_v25.10_by_Remiz_64bit.iso`
- **식별**: **식별 불가 (모호)**. "OSH"가 어떤 소프트웨어의 정식 약어인지 확정할 수 없음. `by_Remiz`는 제품명이 아니라 **리패커/배포자 태그**로 보임 ("Remiz"는 CAD/엔지니어링 소프트웨어를 주로 리패키징해 공유하는 배포자 닉네임으로 알려져 있으며, 이 테스트셋의 다른 항목들도 CAD 계열이 많다는 점과 정황상 부합). 즉 이 파일명만으로는 정답을 낼 수 없고, **웹 검색 또는 상위 폴더명 컨텍스트가 반드시 필요한 케이스.**
- **파서 출력**: `software_name: "OSH v25 by Remiz 64bit"`, `version: "25.10"`, `vendor: "OSH"`
- **문제점**: `by Remiz` 패턴이 전혀 제거되지 않음 — `parser.py`에 `re.sub(r'\bby\s+\w+', '', ...)` 로직이 있는데도 남아있는 걸 보면(코드 81번째 줄) **정규식이 처리 순서상 언더스코어(`_`)가 아직 공백으로 치환되기 전에 실행되어 `by_Remiz`(언더스코어로 붙어있음)를 `\bby\s+\w+`(공백 요구)가 못 잡는 것으로 보임** — 순서 의존적 버그. `vendor: "OSH"`도 근거 없는 추정.
- **의의**: **AI/파서가 "모른다"를 정직하게 표현해야 하는 대표 케이스로 의도적으로 포함.** 현재 AI 프롬프트는 모든 필드를 "REQUIRED"로 요구하는데(`ai_metadata.py`), 이런 케이스에서 AI가 그럴듯하지만 근거 없는 답을 지어낼(hallucination) 위험이 가장 큰 항목.

---

## 2. 요약 표

| # | 파일명 | 식별(정답) | 신뢰도 | 파서 `software_name` | 파서 `version` | 파서 `year` |
|---|---|---|---|---|---|---|
| ① | E.Z.Subtitles.v4.exe | (자막 SW, 브랜드 불명) | 낮음 | Subtitles | 4 | – |
| ② | Autodesk AutoCAD 2027 macOS.zip | Autodesk AutoCAD 2027 (macOS) | 높음 | Autodesk AutoCAD macOS | 2027 | 2027 |
| ③ | Autodesk AutoCAD LT 2027 macOS.zip | Autodesk AutoCAD LT 2027 (macOS) | 높음 | Autodesk AutoCAD LT macOS | 2027 | 2027 |
| ④ | Autodesk Maya v2026 + Fix (macOS).zip | Autodesk Maya 2026 (macOS, 크랙 포함) | 높음 | Autodesk Maya Fix macOS | 2026 | **null ⚠️** |
| ⑤ | Autodesk AutoCAD v2026 + Fix (macOS).zip | Autodesk AutoCAD 2026 (macOS, 크랙 포함) | 높음 | Autodesk AutoCAD Fix macOS | 2026 | **null ⚠️** |
| ⑥ | AutoCAD_2024_Korean_Win_64bit_dlm.7z | Autodesk AutoCAD 2024 (한국어, Win64) | 높음 | AutoCAD Korean dlm | **null ⚠️** | **null ⚠️** |
| ⑦ | PDF-Pro_5-setup.exe | "PDF Pro" 5 (제조사 불명) | 낮음 | PDF Pro | **null ⚠️** | – |
| ⑧ | briss-0.9.zip | briss (PDF 크롭 유틸) | 높음 | briss | **null** (버그) | – |
| ⑨ | BluePDF_v1.2.zip | BluePDF (제조사 불명) | 낮음 | BluePDF v1 (잔여물) | 1.2 | – |
| ⑩ | OSH_v25.10_by_Remiz_64bit.iso | **식별 불가** | 없음 | OSH v25 by Remiz 64bit | 25.10 | – |

---

## 3. 발견된 파서 버그 (우선순위순)

1. **연도가 `\w` 문자(문자/숫자/언더스코어)에 바로 붙어 있으면 인식 실패** (④⑤⑥): `_extract_year`의 `\b(20\d{2})\b`는 Python 정규식에서 `_`도 단어 문자로 취급되기 때문에 `v2026`, `_2024_`처럼 연도 앞뒤가 공백/하이픈 등 진짜 비-단어문자가 아니면 전부 매칭에 실패함 (직접 재현 확인). **`auto_matcher.py`의 버전 분리 가드도 동일 정규식 계열을 재사용하므로, "AutoCAD v2026" vs "AutoCAD v2027" 같은 폴더명 조합에서 이전에 고친 버전 오인 매칭 버그가 재발할 수 있음.** 가장 우선순위 높음.
2. **`by_이름` (언더스코어로 붙은 배포자 태그) 미제거** (⑩): noise 제거 정규식이 언더스코어 치환 전에 실행되어 공백 기준 패턴이 안 맞음.
3. **`Fix` 미필터링** (④⑤): `NOISE_WORDS`에 `crack/patch/keygen`은 있지만 `fix`가 없음.
4. **`macos` 미필터링** (②③): `NOISE_WORDS`에 `mac`은 있지만 `macos`가 없어 "macOS" 토큰이 그대로 통과.
5. **`vendor` 잘못된 추정** (①⑥⑦⑨⑩): `KNOWN_VENDORS`에 없는 경우 첫 단어를 그대로 vendor로 사용하는 폴백이 신뢰할 수 없는 값을 만듦. `null`을 두는 것(⑧)이 오히려 안전.
6. **`제품명-단독숫자.숫자` 버전 미인식** (⑦⑧): `PDF-Pro_5`, `briss-0.9`처럼 구분자로 붙은 짧은 버전이 `version` 필드로 못 들어감.
7. **`software_name`에 버전 잔여물 남음** (⑨): `BluePDF v1.2` → `software_name: "BluePDF v1"`.
8. **`vendor`가 `software_name`에서 중복 제거되지 않음** (②③): vendor 필드는 정확한데 software_name에 그대로 남아 지저분함.

## 4. AI 프롬프트 관점에서의 시사점

- ①⑦⑨⑩ 처럼 신뢰도가 낮은 케이스에서, 현재 `ai_metadata.py` 프롬프트는 모든 필드를 "ALL fields are REQUIRED"로 강제하고 있어 AI가 불확실한 항목도 그럴듯하게 채워 넣을 유인이 있음. confidence/신뢰도 필드를 추가하거나, 근거 부족 시 명시적으로 "확인 필요"를 표시하게 하는 방향을 검토할 필요가 있음 (⑩이 가장 극단적 사례).
- ④⑤⑥처럼 **연도가 파서 단계에서 이미 소실된 채로 AI에 전달되면**, AI가 파일명만 보고 연도를 되살릴 수도 있지만 보장할 수 없음 — 파서 버그(#1)를 먼저 고치는 게 AI 프롬프트를 아무리 다듬어도 얻지 못하는 안정성을 준다.
- ⑧처럼 파서가 잘 처리한 케이스도 있으므로, 전면 재작성보다는 위에 정리된 구체적 버그들을 targeted하게 고치는 접근이 적절해 보임.
