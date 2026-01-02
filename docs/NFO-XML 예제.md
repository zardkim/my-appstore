좋은 예제라서 실제로 바로 써먹을 수 있는 형태로 만들어볼게요.
아래는 같은 정보를 기준으로 한 NFO + XML 한 쌍입니다.

📄 example.nfo (사람 + AI용)
===============================================================================
                             SolidWorks 2022 SP3
===============================================================================

Type        : CAD / Engineering Software
Platform    : Windows x64
Release     : 2022 SP3
Language    : Korean
Vendor      : Dassault Systèmes
Crack       : Included
Patch       : Included
LanguagePack: Included

-------------------------------------------------------------------------------
Description
-------------------------------------------------------------------------------
SolidWorks 2022 is a professional 3D CAD software used for mechanical design,
simulation, and product development.

This release includes Service Pack 3 and a Korean language pack.
A license bypass method is included for offline activation.

-------------------------------------------------------------------------------
System Requirements
-------------------------------------------------------------------------------
OS          : Windows 10 / 11 (64-bit)
CPU         : Intel or AMD 64-bit
RAM         : 16 GB recommended
GPU         : OpenGL 4.5 compatible
Disk Space  : 20 GB free space

-------------------------------------------------------------------------------
Installation
-------------------------------------------------------------------------------
1. Mount the ISO file.
2. Run setup.exe as Administrator.
3. Apply patch after installation.
4. Copy crack files to installation directory.
5. Block software in firewall (recommended).

-------------------------------------------------------------------------------
Notes
-------------------------------------------------------------------------------
- Tested on Windows 11 23H2
- Antivirus may detect crack as false positive
- Internet connection not required after activation

-------------------------------------------------------------------------------
Files
-------------------------------------------------------------------------------
- SolidWorks_2022_SP3.iso
- Crack/
- Patch/
- Korean_Language_Pack/

-------------------------------------------------------------------------------
Release Group
-------------------------------------------------------------------------------
Example-TEAM

===============================================================================
✅ 특징

사람이 읽기 편함

AI 요약 / 키워드 추출 최적

크랙·패치·언어팩 같은 비정형 정보 표현에 강함

📄 example.xml (시스템 / DB / 미디어 서버용)
<?xml version="1.0" encoding="UTF-8"?>
<software>
  <title>SolidWorks</title>
  <version>2022 SP3</version>
  <category>CAD</category>
  <vendor>Dassault Systèmes</vendor>

  <platform>
    <os>windows</os>
    <architecture>x64</architecture>
  </platform>

  <language>
    <primary>ko</primary>
    <available>
      <lang>en</lang>
      <lang>ko</lang>
    </available>
  </language>

  <release>
    <group>Example-TEAM</group>
    <type>scene</type>
  </release>

  <components>
    <crack>true</crack>
    <patch>true</patch>
    <languagePack>true</languagePack>
  </components>

  <requirements>
    <os>Windows 10/11 64-bit</os>
    <cpu>Intel/AMD 64-bit</cpu>
    <ram unit="GB">16</ram>
    <gpu>OpenGL 4.5 compatible</gpu>
    <disk unit="GB">20</disk>
  </requirements>

  <files>
    <file>SolidWorks_2022_SP3.iso</file>
    <file>Crack/</file>
    <file>Patch/</file>
    <file>Korean_Language_Pack/</file>
  </files>

  <notes>
    <note>Tested on Windows 11 23H2</note>
    <note>Antivirus may report false positives</note>
    <note>No internet required after activation</note>
  </notes>
</software>
✅ 특징

DB 매핑 100% 안정

Jellyfin/Kodi/Plex 변형 구조로 쉽게 전환 가능

API / 검색 / 필터링에 최적

🔄 실제 운영 시 추천 규칙
NFO

원본 그대로 보존

사람이 수정 가능

AI 입력용 소스

XML

언제든 재생성 가능

DB 저장 기준

시스템 연동 기준


## 추가정보

그러면 웹 크롤링보다 ai로 메타데이터를 생성하는게 더 나아보이네.
프로그램 로고이미지와 스크린샷은 구글 검색 api를 이용하면 되나?
ChatGPT의 말:
결론부터 말하면 👇
네, 지금 상황에서는 “웹 크롤링 최소화 + AI 중심 생성”이 훨씬 현실적이고 안정적인 선택이고,
로고/스크린샷은 Google 검색 API 계열을 쓰는 게 맞습니다.
다만 아무 Google API나 쓰면 되는 건 아니고, 역할 분담을 잘 해야 합니다.

아래를 보시면 왜 그런지 명확해질 거예요.

1️⃣ 웹 크롤링 vs AI 메타데이터 생성 (현실 비교)
❌ 웹 크롤링의 문제점 (이미 체감하신 부분)
robots.txt / ToS / IP 차단

사이트 구조 변경 시 파서 전부 수정

법적 리스크 애매

유지보수 비용 큼

✅ AI 중심 생성의 장점
파일명 / 폴더명 / 버전 문자열만 있어도 생성 가능

크랙/패치/언어팩 같은 비정형 정보에 강함

사이트 정책 변화 영향 없음

NFO 생성에 최적

👉 당신이 만드는 “프로그램 자료실 + 메타데이터 시스템”에는 AI 쪽이 정답에 가깝습니다.

2️⃣ 추천 전체 구조 (지금 기준 최적)
[파일명 / 폴더명 / 내부 파일]
        ↓
     AI 분석
        ↓
   NFO 생성 (텍스트)
        ↓
  정규화 → XML / DB
        ↓
이미지 수집 (검색 API)
👉 텍스트는 AI, 이미지는 검색 API
이 조합이 제일 안정적입니다.

3️⃣ 프로그램 로고 / 스크린샷 수집 방법
❓ Google 검색 API를 써도 되나?
👉 “Google 공식 API”를 써야 합니다.

✅ 사용 가능한 것
① Google Custom Search JSON API
공식

합법

안정적

이미지 검색 지원

📌 추천 용도:

프로그램 로고

대표 스크린샷 1~3장

❌ 권장하지 않는 것
일반 Google 이미지 검색 HTML 크롤링 ❌

headless chrome으로 구글 긁기 ❌
→ 100% 차단 대상

4️⃣ Google Custom Search API로 가능한 것
✔ 검색 쿼리 예시
"SolidWorks 2022" official logo
"SolidWorks 2022" software screenshot
✔ 응답에서 얻는 것
이미지 URL

썸네일

출처 페이지

이미지 크기

5️⃣ 이미지 유형별 추천 전략
이미지	방법	비고
로고	Google CSE	투명 PNG 우선
메인 스크린샷	Google CSE	공식 사이트 우선
UI 예시	Google CSE	해상도 필터
아이콘	(보조) Bing Image API	대안
6️⃣ ⚠️ 반드시 고려해야 할 저작권 포인트 (중요)
❗ 이미지 “수집”과 “보관”은 다름
URL 링크 → 상대적으로 안전

이미지 파일 저장 → 저작권 이슈 가능

✔ 안전한 전략
이미지 URL만 저장

또는

캐시용 썸네일만 저장

출처 URL 항상 기록

{
  "image_type": "logo",
  "url": "...",
  "source": "softpedia.com"
}
7️⃣ NFO에 이미지 메타데이터 넣는 예시
Images:
- Logo      : https://example.com/logo.png
- Screenshot: https://example.com/screen1.jpg
- Source    : Google Custom Search
또는 XML:

<images>
  <logo url="..." />
  <screenshot url="..." />
</images>
8️⃣ AI + 이미지 자동화 실전 팁 (핵심)
🔹 AI 프롬프트에 이미지 검색 키워드도 포함
Generate search keywords for official logo and UI screenshots.
🔹 AI → 검색어 생성 → Google API 호출
👉 사람 개입 없이 자동화 가능

9️⃣ 한 줄 결론 (아주 중요)
텍스트 메타데이터 = AI가 제일 잘함
이미지 메타데이터 = 공식 검색 API가 제일 안전함
웹 크롤링은 “보조 수단”으로만 유지

