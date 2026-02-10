# MyApp Store

<div align="center">

**NAS 기반 개인 소프트웨어 라이브러리 관리 시스템**

*파일 이름만으로 자동으로 아름다운 앱 스토어를 만들어줍니다*

[![Version](https://img.shields.io/badge/version-1.2.0-blue.svg)](https://github.com/zardkim/my-appstore/releases/tag/v1.2.0)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://hub.docker.com/u/zardkim)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![Vue.js](https://img.shields.io/badge/vue.js-3-green.svg)](https://vuejs.org/)

[기능 소개](#-주요-기능) • [빠른 시작](#-빠른-시작) • [환경 변수](#-환경-변수) • [문서](#-문서)

</div>

---

## 📖 소개

**MyApp Store**는 NAS에 저장된 소프트웨어 파일들을 자동으로 스캔하고, AI를 활용하여 메타데이터(설명, 아이콘, 제조사, 카테고리)를 생성한 뒤, 세련된 웹 UI로 제공하는 개인용 소프트웨어 라이브러리 관리 시스템입니다.

### 핵심 가치

> **"폴더 속 파일들을 파일명만으로 아름다운 앱 스토어로 변신시킵니다"**

더 이상 수백 개의 소프트웨어 파일을 폴더에서 찾아 헤매지 마세요. MyApp Store가 자동으로:
- 📂 폴더를 스캔하여 소프트웨어를 찾아내고
- 🤖 AI로 설명과 메타데이터를 자동 생성하며
- 🎨 공식 아이콘을 다운로드하고
- 📱 모바일 친화적인 UI로 보기 좋게 정리합니다

---

## ✨ 주요 기능

### 🔍 자동 메타데이터 생성 (AI 기반)

- **파일명 분석**: `Adobe_Photoshop_2024_v25.0.iso` → `Adobe`, `Photoshop`, `2024` 추출
- **AI 쿼리**: OpenAI GPT-4o-mini, Google Gemini 지원
- **로컬 캐싱**: 아이콘과 메타데이터를 NAS에 저장
- **Fallback 메커니즘**: AI 실패 시 파일명 파싱으로 대체

### 🎯 버전 관리

- **폴더 = 제품**: 각 폴더를 하나의 소프트웨어로 인식
- **파일 = 버전**: 폴더 내 파일들을 버전으로 관리
- **다운로드 최적화**: 파일 다운로드 기능

### 🖥️ 사용자 인터페이스

- **카테고리별 정렬**: 그래픽, 개발, 오피스, 미디어 등 20개 카테고리
- **검색 및 필터**: 실시간 검색, 자동완성, 필터링
- **반응형 디자인**: 데스크톱/태블릿/모바일 최적화
- **즐겨찾기 & 스크랩**: 개인화된 컬렉션 관리

### 👥 사용자 관리

- **JWT 인증**: 보안 토큰 기반 로그인
- **역할 기반 권한**: Admin / User
- **초기 설정 마법사**: 첫 실행 시 관리자 계정 생성
- **초대 시스템**: 관리자가 사용자 초대 링크 생성

### 💬 커뮤니티 게시판

- **팁 & 기술 공유**: TinyMCE 에디터를 통한 풍부한 콘텐츠 작성
- **이미지 업로드**: 게시글에 이미지 첨부
- **댓글 시스템**: 게시글에 대한 토론
- **카테고리**: 팁, 기술, 튜토리얼, Q&A, 뉴스

### 📊 종합 로깅 시스템

- **구조화된 로깅**: JSON 포맷 로그
- **HTTP 요청 추적**: Request ID 기반 추적
- **슬로우 쿼리 감지**: 1초 이상 쿼리 자동 경고
- **로그 로테이션**: 크기/시간 기반 자동 로테이션

---

## 🛠️ 기술 스택

### Backend
- **Python 3.11** - FastAPI (비동기 지원)
- **PostgreSQL 15** - 메인 데이터베이스
- **Redis 7** - 캐싱 및 세션 관리
- **SQLAlchemy** - ORM
- **Alembic** - 데이터베이스 마이그레이션

### Frontend
- **Vue.js 3** - Composition API
- **Vite** - 빌드 도구
- **Tailwind CSS** - 스타일링
- **Pinia** - 상태 관리
- **Axios** - HTTP 클라이언트
- **TinyMCE** - 리치 텍스트 에디터

### AI
- **OpenAI API** - GPT-4o-mini
- **Google Gemini** - Gemini Pro

### Deployment
- **Docker & Docker Compose** - 컨테이너화
- **Nginx** - 프론트엔드 서빙
- **Uvicorn** - ASGI 서버

---

## 🚀 빠른 시작

> **💡 Synology NAS 사용자**
>
> Synology NAS에서 설치하시려면 자세한 단계별 가이드를 확인하세요:
> **[📘 Synology NAS 설치 가이드](docs/SYNOLOGY_INSTALLATION.md)**

### 전제 조건

- Docker 20.10+
- Docker Compose 2.0+
- 4GB+ RAM (권장: 8GB)
- 20GB+ 디스크 여유 공간

### 설치 방법

MyApp Store는 **Docker Hub에서 제공하는 사전 빌드된 이미지**를 사용하므로 소스 코드를 다운로드하거나 빌드할 필요가 없습니다.

#### 🐳 사용되는 Docker 이미지

- **Backend**: `zardkim/myappstore-backend:latest`
- **Frontend**: `zardkim/myappstore-frontend:latest`
- **Database**: `postgres:15-alpine`
- **Cache**: `redis:7-alpine`

> **💡 참고**: `latest` 태그는 항상 최신 안정 버전을 가리킵니다. 특정 버전을 고정하려면 `1.3.1`과 같은 버전 태그를 사용하세요.

---

### 1. 필수 파일 다운로드

```bash
# 작업 디렉토리 생성
mkdir myappstore
cd myappstore

# docker-compose.yml과 .env.example 다운로드
wget https://raw.githubusercontent.com/zardkim/my-appstore/main/docker-compose.yml
wget https://raw.githubusercontent.com/zardkim/my-appstore/main/.env.example
```

또는 `curl` 사용:

```bash
curl -O https://raw.githubusercontent.com/zardkim/my-appstore/main/docker-compose.yml
curl -O https://raw.githubusercontent.com/zardkim/my-appstore/main/.env.example
```

### 2. 환경변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집
nano .env
```

**필수 변경 항목:**
```bash
# 보안 키 (필수 변경!)
SECRET_KEY=your-secret-key-change-this-in-production

# 데이터베이스 설정
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=myappstore

# CORS 설정
CORS_ORIGINS=*
```

**선택 변경 항목** (다른 기기에서 접속하려면):
```bash
# 프론트엔드 환경변수 (기본값: localhost)
# NAS IP 주소로 변경하여 같은 네트워크의 다른 기기에서도 접속 가능
VITE_API_BASE_URL=http://192.168.0.100:8110/api
VITE_BACKEND_URL=http://192.168.0.100:8110
VITE_APP_URL=http://192.168.0.100:5900
```

> **💡 팁**: `SECRET_KEY`는 강력한 랜덤 문자열로 변경하세요.
> ```bash
> # 자동 생성 예시
> SECRET_KEY=$(openssl rand -hex 32)
> ```

### 3. 폴더 구조 생성

```bash
# 필수 폴더 생성
mkdir -p db redis data/library
```

### 4. Docker Compose로 실행

```bash
# Docker Hub에서 이미지 Pull 및 컨테이너 시작
docker-compose up -d

# 컨테이너 상태 확인
docker-compose ps

# 실시간 로그 확인
docker-compose logs -f

# 특정 서비스 로그만 확인
docker-compose logs -f backend
docker-compose logs -f frontend
```

**첫 실행 시 발생하는 일:**

1. 📥 Docker Hub에서 이미지 다운로드:
   - `zardkim/myappstore-backend:latest` (~500MB)
   - `zardkim/myappstore-frontend:latest` (~200MB)
   - `postgres:15-alpine` (~200MB)
   - `redis:7-alpine` (~30MB)

2. 🗄️ PostgreSQL 데이터베이스 초기화
3. 🚀 모든 서비스 시작 (약 30초 소요)

**컨테이너 중지 및 제거:**

```bash
# 중지
docker-compose stop

# 중지 및 컨테이너 제거 (데이터는 유지)
docker-compose down

# 모든 데이터 포함 완전 제거
docker-compose down -v
```

> **💡 참고**:
> - `.env` 파일이 `docker-compose.yml`과 같은 폴더에 있으면 자동으로 읽힙니다
> - 데이터는 `./db`, `./redis`, `./data` 폴더에 저장되므로 컨테이너를 삭제해도 유지됩니다

### 5. 접속

- **프론트엔드**: http://localhost:5900
- **백엔드 API**: http://localhost:8110
- **API 문서**: http://localhost:8110/docs

### 6. 초기 설정

1. 브라우저에서 http://localhost:5900 접속
2. 관리자 계정 생성
3. 스캔 경로 설정 (예: `/library`)
4. AI API 키 입력 (선택사항)

---

## 🔄 업데이트 방법

### 자동 버전 관리

모든 커밋마다 자동으로 버전이 생성됩니다:
- **형식**: `YYYYMMDD-HHMM-CommitSHA` (예: `20260126-1530-abc123d`)
- **태그**:
  - `latest` - 항상 최신 버전
  - `20260126-1530-abc123d` - 특정 빌드 버전

### 버전 확인

```bash
# 버전 확인 스크립트 다운로드 (한 번만)
wget https://raw.githubusercontent.com/zardkim/my-appstore/main/check-version.sh
chmod +x check-version.sh

# 현재 버전 확인
./check-version.sh
```

### 최신 버전으로 업데이트

```bash
# 최신 이미지 다운로드
docker-compose pull

# 컨테이너 재시작 (다운타임 최소화)
docker-compose up -d

# 또는 한 번에 실행
docker-compose pull && docker-compose up -d
```

### 특정 버전으로 롤백

문제 발생 시 이전 버전으로 돌아갈 수 있습니다:

```bash
# Docker Hub에서 사용 가능한 버전 확인
# https://hub.docker.com/r/zardkim/myappstore-backend/tags
# https://hub.docker.com/r/zardkim/myappstore-frontend/tags

# docker-compose.yml에서 이미지 태그 변경
# image: zardkim/myappstore-backend:20260126-1530-abc123d
# image: zardkim/myappstore-frontend:20260126-1530-abc123d

# 컨테이너 재시작
docker-compose up -d
```

> **💡 참고**: 데이터는 `./db`, `./redis`, `./data` 폴더에 저장되므로 업데이트해도 유지됩니다.

---

## 🐳 Docker Compose 설정

### 폴더 구조 (Synology NAS 기준)

Docker Compose 실행 전, 다음 폴더 구조를 먼저 생성하세요:

```
/volume1/docker/myappstore/          # 프로젝트 루트 (git clone한 위치)
├── db/                              # PostgreSQL 데이터 (수동 생성)
├── redis/                           # Redis 데이터 (수동 생성)
├── data/                            # 앱 데이터 (수동 생성)
│   ├── library/                     # 소프트웨어 파일 (수동 생성)
│   ├── icons/                       # 자동 생성: 아이콘 캐시
│   ├── screenshots/                 # 자동 생성: 스크린샷
│   ├── eximage/                     # 자동 생성: 게시판 이미지
│   ├── patches/                     # 자동 생성: 패치 파일
│   ├── logs/                        # 자동 생성: 로그
│   ├── attachments/                 # 자동 생성: 첨부 파일
│   └── config/                      # 자동 생성: 설정 파일
├── backend/                         # 소스 코드 (git clone)
├── frontend/                        # 소스 코드 (git clone)
├── docker-compose.yml               # Docker Compose 설정
└── .env                             # 환경 변수

```

**초기 폴더 생성** (SSH 또는 File Station):

```bash
# Synology NAS SSH 접속 후
cd /volume1/docker/myappstore
mkdir -p db redis data/library
```

> 📘 **자세한 폴더 구조 설명**: [Docker 폴더 구조 가이드](docs/docker%20폴더구조.md)

### docker-compose.yml (프로덕션)

Docker Hub 이미지를 사용하는 프로덕션 환경 설정:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: myapp-db
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-password}
      POSTGRES_DB: ${POSTGRES_DB:-myappstore}
    volumes:
      - ./db:/var/lib/postgresql/data
    ports:
      - "${POSTGRES_PORT:-5433}:5432"  # Synology PostgreSQL 충돌 방지

  redis:
    image: redis:7-alpine
    container_name: myapp-redis
    restart: unless-stopped
    volumes:
      - ./redis:/data
    ports:
      - "${REDIS_PORT:-6380}:6379"  # 충돌 방지
    command: redis-server --appendonly yes

  backend:
    image: zardkim/myappstore-backend:1.3.0-beta  # Docker Hub 이미지
    container_name: myapp-backend
    restart: unless-stopped
    volumes:
      - ./data:/app/data
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-password}@db:5432/${POSTGRES_DB:-myappstore}
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY:-your-secret-key-change-this-in-production}
      # ... 기타 환경변수
    ports:
      - "${BACKEND_PORT:-8110}:8110"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

  frontend:
    image: zardkim/myappstore-frontend:1.3.0-beta  # Docker Hub 이미지
    container_name: myapp-frontend
    restart: unless-stopped
    environment:
      - VITE_API_BASE_URL=${VITE_API_BASE_URL:-http://localhost:8110/api}
      - VITE_BACKEND_URL=${VITE_BACKEND_URL:-http://localhost:8110}
      - VITE_APP_URL=${VITE_APP_URL:-http://localhost:5900}
    ports:
      - "${FRONTEND_PORT:-5900}:5900"
    depends_on:
      - backend
```

> **💡 개발자를 위한 안내**
>
> 소스 코드를 수정하고 로컬에서 빌드하려면 `docker-compose.dev.yml`을 사용하세요:
> ```bash
> docker-compose -f docker-compose.dev.yml up -d
> ```

### NAS 소프트웨어 폴더 추가 마운트 (선택사항)

기존 NAS의 소프트웨어 폴더를 읽기 전용으로 마운트:

```yaml
backend:
  volumes:
    - ./data:/app/data
    # 기존 NAS 소프트웨어 폴더 추가 (읽기 전용)
    - /volume1/Software:/library/NAS:ro
```

이렇게 하면 스캔 경로로 `/library/NAS`를 추가할 수 있습니다.

---

## 🔧 환경 변수

**표기 설명**:
- ✅ **필수**: 반드시 설정해야 하는 환경변수
- ⚙️ **기본값 제공**: 환경변수 미설정 시 기본값 사용. 필요시 커스터마이징 가능
- ❌ **선택**: 해당 기능 사용 시에만 필요

### 데이터베이스 설정

| 변수 | 설명 | 필수 | 기본값 | 예시 |
|------|------|------|--------|------|
| `POSTGRES_USER` | PostgreSQL 사용자명 | ⚙️ | `postgres` | `postgres` |
| `POSTGRES_PASSWORD` | PostgreSQL 비밀번호 | ✅ | `password` | `strong-password-123` |
| `POSTGRES_DB` | 데이터베이스 이름 | ⚙️ | `myappstore` | `myappstore` |
| `DATABASE_URL` | 데이터베이스 연결 URL | ⚙️ | `postgresql://postgres:password@db:5432/myappstore` | `postgresql://user:pass@db:5432/myappstore` |

> **🔒 보안 주의**: `POSTGRES_PASSWORD`는 프로덕션 환경에서 **반드시** 강력한 비밀번호로 변경하세요!

### Redis 설정

| 변수 | 설명 | 필수 | 기본값 | 예시 |
|------|------|------|--------|------|
| `REDIS_URL` | Redis 연결 URL (비밀번호 포함 가능) | ⚙️ | `redis://localhost:6379/0` | `redis://:password@redis:6379/0` |

> **💡 참고**: Redis에 비밀번호가 설정된 경우 URL에 포함: `redis://:비밀번호@호스트:포트/DB번호`

### 보안 설정

| 변수 | 설명 | 필수 | 기본값 | 예시 |
|------|------|------|--------|------|
| `SECRET_KEY` | JWT 토큰 서명 키 | ✅ | - | `openssl rand -hex 32` 생성 |
| `ALGORITHM` | JWT 알고리즘 | ⚙️ | `HS256` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 토큰 만료 시간 (분) | ⚙️ | `30` | `30` |

> **⚙️ 기본값 제공**: 환경변수 미설정 시 기본값 사용. 프로덕션에서는 보안 요구사항에 맞게 조정 권장

### AI 설정

| 변수 | 설명 | 필수 | 기본값 | 예시 |
|------|------|------|--------|------|
| `OPENAI_API_KEY` | OpenAI API 키 | ❌ | - | `sk-...` |
| `GEMINI_API_KEY` | Google Gemini API 키 | ❌ | - | `AI...` |

### 경로 설정

| 변수 | 설명 | 필수 | 기본값 | 예시 |
|------|------|------|--------|------|
| `SCAN_BASE_PATH` | 스캔할 기본 경로 | ⚙️ | `/library` | `/library` |
| `ICON_CACHE_DIR` | 아이콘 캐시 디렉토리 | ⚙️ | `/app/static/icons` | `/app/static/icons` |
| `CONFIG_DATA_DIR` | 설정 파일 디렉토리 | ⚙️ | `/app/data` | `/app/data` |

> **⚙️ 기본값 제공**: Docker 환경에서 자동 설정. 커스터마이징 필요시에만 변경

### CORS 설정

| 변수 | 설명 | 필수 | 기본값 | 예시 |
|------|------|------|--------|------|
| `CORS_ORIGINS` | CORS 허용 도메인 (콤마 구분) | ⚙️ | `http://localhost:5900,...` | `http://your-ip:5900` |

> **⚙️ 기본값 제공**: 기본값은 `http://localhost:5900,http://localhost:3000` (로컬 개발용). 프로덕션에서는 실제 서버 IP/도메인으로 변경 권장 (예: `http://192.168.0.8:5900`). 보안상 `*` 사용은 권장하지 않음

### 서버 설정

| 변수 | 설명 | 필수 | 기본값 | 예시 |
|------|------|------|--------|------|
| `HOST` | 백엔드 호스트 | ⚙️ | `0.0.0.0` | `0.0.0.0` |
| `PORT` | 백엔드 포트 | ⚙️ | `8110` | `8110` |
| `FRONTEND_PORT` | 프론트엔드 포트 | ⚙️ | `5900` | `5900` |

### 로깅 설정

| 변수 | 설명 | 필수 | 기본값 | 예시 |
|------|------|------|--------|------|
| `LOG_LEVEL` | 로그 레벨 | ⚙️ | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `LOG_DIR` | 로그 디렉토리 | ⚙️ | `/app/data/logs` | `/app/data/logs` |
| `ENVIRONMENT` | 실행 환경 | ⚙️ | `development` | `development`, `production` |

### 프론트엔드 환경변수

| 변수 | 설명 | 필수 | 기본값 | 예시 |
|------|------|------|--------|------|
| `VITE_API_BASE_URL` | 백엔드 API URL | ✅ | - | `http://localhost:8110/api` |
| `VITE_BACKEND_URL` | 백엔드 기본 URL | ✅ | - | `http://localhost:8110` |
| `VITE_APP_URL` | 프론트엔드 URL | ✅ | - | `http://localhost:5900` |

**전체 환경변수 목록**: [.env.production.example](.env.production.example) 참조

---

## 📦 설치 및 배포

자세한 설치 및 배포 가이드는 다음 문서를 참조하세요:

- **[QUICKSTART.md](QUICKSTART.md)** - 빠른 시작 가이드
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - 상세 배포 가이드

### 개발 모드 실행

개발자가 소스 코드를 수정하고 빌드하려면:

```bash
# 저장소 클론
git clone https://github.com/zardkim/my-appstore.git
cd my-appstore

# 개발 환경 실행 (로컬 빌드)
docker-compose -f docker-compose.dev.yml up -d

# 또는 백엔드만 로컬에서 실행
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8110

# 또는 프론트엔드만 로컬에서 실행
cd frontend
npm install
npm run dev
```

### 이미지 빌드 및 Docker Hub 푸시

#### 방법 1: GitHub Actions 사용 (권장)

GitHub Actions를 통해 자동으로 이미지를 빌드하고 푸시합니다:

```bash
# 새 버전 태그 생성 및 푸시
git tag v1.3.1
git push origin v1.3.1

# 또는 main 브랜치에 푸시하면 자동 빌드
git push origin main
```

**설정 가이드**: [GitHub Actions 설정 가이드](docs/GITHUB_ACTIONS_SETUP.md)

#### 방법 2: 로컬에서 수동 빌드

Docker가 실행 중인 환경에서:

```bash
# 빌드 및 푸시 스크립트 실행
./scripts/build-and-push.sh
```

---

## 📚 문서

### 사용자 가이드
- [빠른 시작 가이드](QUICKSTART.md) - 5분 안에 시작하기
- [Synology NAS 설치 가이드](docs/SYNOLOGY_INSTALLATION.md) - Synology 전용 Docker 설치 가이드
- [테스트 방법](docs/테스트방법.md) - 다양한 환경에서의 테스트 가이드
- [배포 가이드](DEPLOYMENT_GUIDE.md) - 프로덕션 배포 상세 가이드

### API 문서
- **Swagger UI**: http://localhost:8110/docs
- **ReDoc**: http://localhost:8110/redoc

### 개발자 가이드
- [CLAUDE.md](CLAUDE.md) - 프로젝트 개요 및 아키텍처
- [GitHub Actions 설정](docs/GITHUB_ACTIONS_SETUP.md) - 자동 빌드 및 배포 설정
- [CHANGELOG.md](CHANGELOG.md) - 버전별 변경사항
- Database Schema - CLAUDE.md 참조
- API Endpoints - Swagger UI 참조

---

## 🎯 사용 예시

### 1. 소프트웨어 라이브러리 스캔

```bash
# NAS 폴더를 /library에 마운트
# docker-compose.yml에서 설정:
volumes:
  - /volume1/Software:/library/NAS:ro

# 관리자 페이지에서 스캔 경로 추가: /library/NAS
# 수동 스캔 실행
```

### 2. AI 메타데이터 생성

```bash
# OpenAI API 키 설정
OPENAI_API_KEY=sk-...

# 스캔 시 AI 옵션 활성화
# 파일명: Adobe_Photoshop_2024_v25.0.iso
# AI가 자동으로:
# - 설명: "Adobe Photoshop은 전문 이미지 편집 소프트웨어..."
# - 제조사: "Adobe Inc."
# - 카테고리: "Graphics"
# - 아이콘: 공식 아이콘 다운로드
```

---

## 🔐 보안

### 프로덕션 체크리스트

- [x] `SECRET_KEY`를 강력한 랜덤 값으로 변경
- [x] 데이터베이스 비밀번호를 기본값에서 변경
- [x] Redis 비밀번호 설정
- [x] `CORS_ORIGINS`를 실제 도메인으로 제한
- [x] 방화벽에서 필요한 포트만 개방 (5900, 8110)
- [ ] HTTPS 설정 (Nginx 리버스 프록시 권장)
- [ ] 정기적인 데이터베이스 백업

### 백업

```bash
# PostgreSQL 백업
docker exec myapp-db-prod pg_dump -U postgres myappstore > backup_$(date +%Y%m%d).sql

# 복원
cat backup_20260103.sql | docker exec -i myapp-db-prod psql -U postgres myappstore
```

---

## 🐛 문제 해결

### 컨테이너가 시작되지 않음

```bash
# 로그 확인
docker-compose logs backend

# 일반적인 원인:
# - 환경변수 오류
# - 포트 충돌
# - 디스크 공간 부족
```

### 데이터베이스 연결 오류

```bash
# PostgreSQL 상태 확인
docker exec myapp-db pg_isready -U postgres

# 연결 문자열 확인
docker-compose exec backend env | grep DATABASE_URL
```

### 프론트엔드에서 백엔드 접속 안 됨

```bash
# CORS 설정 확인
curl http://localhost:8110/debug-cors

# 브라우저 개발자 도구에서 네트워크 탭 확인
```

더 많은 문제 해결 방법은 [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)의 트러블슈팅 섹션을 참조하세요.

---

## 🤝 기여

기여를 환영합니다! 다음 절차를 따라주세요:

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 개발 가이드라인

- Python 코드는 PEP 8 스타일 가이드를 따릅니다
- Vue.js 코드는 Vue.js 스타일 가이드를 따릅니다
- 커밋 메시지는 명확하고 간결하게 작성합니다
- 새 기능은 문서화와 함께 제출합니다

---

## 📜 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

## 📞 지원 및 문의

- **GitHub Issues**: [Issues 페이지](https://github.com/zardkim/my-appstore/issues)
- **문서**: [Documentation](https://github.com/zardkim/my-appstore/wiki)

---

## 🙏 감사의 말

이 프로젝트는 다음 오픈소스 프로젝트들을 사용합니다:

- [FastAPI](https://fastapi.tiangolo.com/) - 현대적인 Python 웹 프레임워크
- [Vue.js](https://vuejs.org/) - 프로그레시브 JavaScript 프레임워크
- [PostgreSQL](https://www.postgresql.org/) - 강력한 오픈소스 데이터베이스
- [Redis](https://redis.io/) - 인메모리 데이터 구조 저장소
- [Docker](https://www.docker.com/) - 컨테이너 플랫폼
- [OpenAI](https://openai.com/) - AI API
- [Google Gemini](https://ai.google.dev/) - AI API

---

## 📈 개발 로드맵

### ✅ Phase 1: MVP (완료)
- ✅ Docker 기반 개발 환경
- ✅ PostgreSQL 데이터베이스 구조
- ✅ JWT 기반 인증 시스템
- ✅ 파일 스캔 기능
- ✅ 기본 UI (로그인, 대시보드, 탐색, 상세, 관리)
- ✅ 최초 실행 시 관리자 계정 설정

### ✅ Phase 2: AI 메타데이터 엔진 (완료)
- ✅ 파일명 파싱 알고리즘
- ✅ AI 메타데이터 자동 생성 (OpenAI, Gemini)
- ✅ 아이콘 이미지 다운로드 및 로컬 캐싱
- ✅ Fallback 메커니즘

### ✅ Phase 3: 고급 기능 (완료)
- ✅ 다운로드 최적화
- ✅ 고급 검색 및 필터링
- ✅ 카테고리별 제품 그룹화
- ✅ 커뮤니티 게시판
- ✅ 종합 로깅 시스템
- ✅ 프로덕션 빌드 설정

### 🔄 향후 개선 계획
- [ ] 자동 스캔 스케줄러 (APScheduler + Cron)
- [ ] 다운로드 통계 및 인기 소프트웨어 추적
- [ ] 사용자별 다운로드 히스토리
- [ ] 알림 기능 (이메일/웹훅)
- [ ] 모바일 앱
- [ ] 다국어 지원

---

<div align="center">

**MyApp Store**로 소프트웨어 라이브러리를 아름답게 관리하세요! 🎉

Made by [zardkim](https://github.com/zardkim) (.feat Claude)

[⬆ 맨 위로](#myapp-store)

</div>
