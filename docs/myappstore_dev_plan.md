멋진 아이디어입니다\! 개인용/팀용 NAS를 '나만의 앱스토어'처럼 꾸미고, 귀찮은 메타데이터 정리를 AI로 자동화한다는 점이 매우 실용적입니다.

요청하신 **MyApp Store** 개발을 위한 구체적인 **프로젝트 개발 계획서**를 작성해 드립니다.

-----

# 📝 MyApp Store 프로젝트 개발 계획서

## 1\. 프로젝트 개요

  * **프로젝트명:** MyApp Store
  * **목표:** NAS에 저장된 소프트웨어 파일들을 스캔하여 AI 기반으로 메타데이터(설명, 아이콘, 제조사 등)를 자동 생성하고, 웹진 형태의 직관적인 UI로 관리 및 다운로드 제공.
  * **핵심 가치:** "파일 이름만 있으면 앱스토어처럼 예쁘게 정리해주는 개인용 소프트웨어 라이브러리"

-----

## 2\. 기술 스택 (Tech Stack) 선정

NAS Docker 환경에서의 가벼운 구동과 AI/크롤링 연동의 용이성을 최우선으로 고려했습니다.

  * **Frontend (UI):** **Vue.js**
      * *이유:* 모바일 반응형 구현이 쉽고(Tailwind CSS 사용), 대시보드와 검색 기능의 UX가 매끄럽습니다.
  * **Backend (Server):** **Python (FastAPI)**
      * *이유:* 파일 시스템 제어, 웹 크롤링(BeautifulSoup/Selenium), AI 라이브러리(OpenAI/LangChain) 연동에 Python이 압도적으로 유리합니다. FastAPI는 비동기 처리를 지원해 스캔 속도가 빠릅니다.
  * **Database:** - **PostgreSQL**
      * *이유:* NAS Docker 환경에서는 파일 기반인 SQLite가 백업/관리가 가장 쉽습니다. (DB 파일 하나만 볼륨 매핑하면 끝)
  * **AI/Crawling:** **OpenAI API (GPT-4o-mini)** 또는 **Gemini**
      * *이유:* 단순히 크롤링만 하는 것보다, 파일명을 던져주면 GPT가 적절한 설명과 카테고리를 요약해주는 방식이 훨씬 정확합니다.
  * **Deployment:** **Docker Compose**

-----

## 3\. 데이터베이스 설계 (ERD 초안)

효율적인 버전 및 메타데이터 관리를 위해 관계형 DB 구조가 필요합니다.

1.  **Users (사용자):** `id`, `username`, `password_hash`, `role(admin/user)`, `created_at`
2.  **Products (프로그램):** `id`, `title`, `description`, `vendor`, `icon_url`, `category`, `folder_path`
3.  **Versions (버전/파일):** `id`, `product_id`, `version_name`, `file_name`, `file_path`, `file_size`, `release_date`
      * *Product와 1:N 관계 (하나의 프로그램에 여러 버전 존재)*
4.  **Attachments (추가 파일):** `id`, `product_id`, `file_path`, `note`, `type(manual/crack/etc)`
5.  **Settings (설정):** `scan_paths`(스캔 대상 폴더 목록), `ai_api_key`, `cron_schedule`

-----

## 4\. 핵심 기능별 개발 로직

### 4.1. 인증 및 사용자 관리

  * **최초 실행 감지:** DB에 사용자 테이블이 비어있으면 `/setup` 페이지로 리다이렉트하여 관리자 계정 생성 유도.
  * **관리자 페이지:** 일반 사용자를 CRUD(생성/조회/수정/삭제) 할 수 있는 테이블 뷰 제공.

### 4.2. 메타데이터 생성 엔진 (핵심)

이 앱의 핵심 기능인 **Auto-Tagging** 프로세스입니다.

1.  **파일명 파싱:** `Adobe_Photoshop_2024_v25.0.iso` -\> 키워드 추출 (`Adobe`, `Photoshop`, `2024`)
2.  **AI Query:**
      * *Prompt:* "이 소프트웨어('Adobe Photoshop 2024')에 대한 짧은 설명, 공식 제조사, 대표 카테고리, 공식 아이콘 이미지 URL을 검색해서 JSON으로 줘."
3.  **Fallback (크롤링):** AI가 정보를 못 찾으면 Google Search API나 DuckDuckGo 검색 결과를 긁어와서 요약.
4.  **저장:** DB에 메타데이터 저장 및 이미지는 로컬 캐싱(NAS에 저장하여 로딩 속도 향상).

### 4.3. 파일 스캔 및 모니터링

  * **경로 설정:** 관리자가 `/data/software` 같은 내부 경로를 설정.
  * **스캔 로직:** Python `os.walk`를 사용하여 폴더 구조 순회.
      * 새로운 폴더 발견 -\> **신규 프로그램**으로 등록 시도.
      * 기존 폴더 내 새로운 파일 발견 -\> **새 버전**으로 등록.
  * **스케줄러:** `APScheduler`를 사용하여 매일 밤 혹은 설정된 주기에 자동 스캔.

### 4.4. 다운로드 및 파일 서빙

  * **Nginx 활용:** NAS의 정적 파일을 효율적으로 서빙하기 위해 Backend에서 파일을 스트리밍하지 않고, **X-Accel-Redirect** 헤더를 사용하여 Nginx가 파일을 전송하도록 처리 (대용량 파일 전송 시 서버 부하 감소).

-----

## 5\. UI/UX 디자인 (화면 구성)

1.  **대시보드 (Home):**
      * 상단: "최근 추가된 앱" (Netflix 스타일의 가로 스크롤 카드)
      * 중단: 시스템 통계 (총 프로그램 수, 용량, 최근 스캔 시간)
2.  **탐색 (Discover):**
      * 왼쪽: 카테고리 필터 (그래픽, OS, 유틸리티 등)
      * 오른쪽: 그리드 형태의 앱 카드 (아이콘 + 제목 + 버전). 모바일에서는 1열 리스트로 변환.
3.  **상세 페이지 (Detail):**
      * 헤더: 큰 아이콘, 제목, 제조사, 최신 버전.
      * 탭 구성:
          * `정보`: AI가 작성한 설명, 태그.
          * `버전`: 다운로드 가능한 파일 목록 (버전별).
          * `자료실`: 사용자가 업로드한 추가 파일 및 노트(메모).
4.  **관리자 (Admin):**
      * 설정: 스캔 경로 추가/삭제, AI API 키 입력, 사용자 관리.

-----

## 6\. 개발 로드맵 (단계별 구현)

### 1단계: MVP (최소 기능 제품)

  * 도커 환경 구축 (FastAPI + React + DB).
  * 지정된 폴더의 파일 리스트를 DB로 가져오는 기본 스캔 기능.
  * 로그인 및 다운로드 기능 구현.
  * 기본 리스트 뷰 UI.

### 2단계: 메타데이터 & AI 연동

  * 파일명 파싱 알고리즘 고도화.
  * OpenAI API 연동하여 메타데이터 자동 채우기.
  * 이미지(아이콘) 크롤링 및 로컬 저장.

### 3단계: 디테일 & 확장

  * 대시보드 통계 및 웹진 스타일 UI 적용.
  * 추가 파일 업로드 및 노트 기능.
  * 자동 스캔 스케줄러 및 모바일 최적화.

-----

## 7\. Docker Compose 설정 예시

나스에 배포하기 위한 `docker-compose.yml` 구조입니다.

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    container_name: myapp-backend
    volumes:
      - ./data/db:/app/db  # DB 저장 경로
      - /volume1/Software:/mnt/software:ro # NAS의 실제 소프트웨어 폴더 (읽기 전용)
      - ./data/icons:/app/static/icons # 아이콘 저장 경로
    environment:
      - OPENAI_API_KEY=your_key
      - SECRET_KEY=your_secret
    ports:
      - "8100:8100"

  frontend:
    build: ./frontend
    container_name: myapp-frontend
    ports:
      - "5900:5900"
    depends_on:
      - backend
```

-----

## 8\. 개발 시 고려사항 (Tip)

1.  **AI 비용 관리:** 모든 파일에 대해 매번 AI를 호출하면 비용이 발생합니다. DB에 메타데이터가 없는 항목만 선별적으로 호출해야 합니다.
2.  **정확도:** "setup.exe" 처럼 파일명이 모호한 경우, 상위 폴더명을 기준으로 검색하는 로직이 필수입니다.
3.  **보안:** NAS 내부망에서 쓰더라도 관리자 계정 보안은 필수입니다. 다운로드 링크는 외부 유출 시 접근 불가능하도록 세션 체크를 해야 합니다.

-----

### 🚀 다음 단계 (Next Step)

이 계획서가 마음에 드시나요? 그렇다면 개발을 바로 시작하실 수 있도록 **"프로젝트 폴더 구조와 핵심 Backend 코드(FastAPI 초기 설정 및 파일 스캐너)"** 템플릿을 작성해 드릴까요?