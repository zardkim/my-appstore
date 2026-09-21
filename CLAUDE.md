# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🔴 이 프로젝트의 Git / 레지스트리 정책 (2026-09-21 확정)

**이 프로젝트는 GitHub와 Docker Hub만 사용한다. Harbor와 Gitea는 사용하지 않는다.**

| 용도 | 사용처 |
|---|---|
| Git 저장소 | **GitHub** — `github.com/zardkim/my-appstore` (정본, 유일) |
| 컨테이너 이미지 | **Docker Hub** — `zardkim/myappstore-backend`, `zardkim/myappstore-frontend` |
| 이미지 빌드/푸시 | **GitHub Actions** (`.github/workflows/docker-build.yml`) — `v*` 태그 push로 트리거 |
| 운영 배포 | 시놀로지 Container Manager가 Docker Hub `:latest`를 pull |

### 하지 말 것

- ❌ Harbor(`harbor.nurilab.pe.kr`)에 푸시하지 않는다. `docker-compose*.yml`의 이미지 주소도 Docker Hub를 유지한다
- ❌ Gitea(`gitea.nurilab.pe.kr`)에 미러/리모트를 추가하지 않는다. 정본을 두 곳에 두지 않는다
- ❌ `build.sh`에 레지스트리 푸시 로직을 추가하지 않는다 — 빌드/푸시는 CI 한 곳에서만 한다

> **참고**: 사용자 전역 규칙(`~/.claude/CLAUDE.md`)은 Harbor를 기본 레지스트리로 지정하지만,
> 이 프로젝트는 공개 Docker Hub 이미지를 배포하므로 **의도적인 예외**다.
> 2026-09-14 ~ 09-21에 Harbor를 백업본으로 병행 운영해 봤으나, 같은 태그에 서로 다른 빌드가
> 올라가는 사고(1.4.69)가 발생해 단일화하기로 결정했다.
> Harbor에 남아 있는 과거 이미지(~1.4.74)는 참고용일 뿐 **신뢰하지 말 것.**

---

## Project Overview

**MyApp Store** is a NAS-based personal software library management system that scans software files and uses AI to automatically generate metadata (descriptions, icons, vendors, categories), presenting them in an app store-like web UI.

**Core Value**: "Transform a folder of files into a beautiful app store just from filenames"

## Technology Stack

- **Frontend**: Vue.js with Tailwind CSS (mobile responsive)
- **Backend**: Python FastAPI (async support for fast scanning, easy AI/crawling integration)
- **Database**: PostgreSQL (note: dev plan mentions SQLite initially but final choice is PostgreSQL)
- **Cache**: Redis (API response caching, statistics caching)
- **AI**: OpenAI API (GPT-4o-mini), Gemini, Claude (Anthropic), or Azure OpenAI for metadata generation
- **Deployment**: Docker Compose for NAS environments

## Database Schema

### Core Tables
1. **Users**: `id`, `username`, `password_hash`, `role(admin/user)`, `created_at`
2. **Products**: `id`, `title`, `description`, `vendor`, `icon_url`, `category`, `folder_path`
3. **Versions**: `id`, `product_id`, `version_name`, `file_name`, `file_path`, `file_size`, `release_date`
   - 1:N relationship with Products (one program can have multiple versions)
4. **Attachments**: `id`, `product_id`, `file_path`, `note`, `type(manual/crack/etc)`
5. **Settings**: `id`, `key`, `value`, `description` (stores: scan_paths, cron_schedule, use_ai)
6. **ScanHistory** (Phase 3): `id`, `scan_type`, `scan_paths`, `started_at`, `completed_at`, `new_products`, `new_versions`, `updated_products`, `ai_generated`, `icons_cached`, `errors`

## Architecture & Core Features

### Metadata Generation Engine (Auto-Tagging Pipeline)
This is the core feature of the application:

1. **Filename Parsing**: Extract keywords from files (e.g., `Adobe_Photoshop_2024_v25.0.iso` → `Adobe`, `Photoshop`, `2024`)
2. **AI Query**: Prompt example: "이 소프트웨어('Adobe Photoshop 2024')에 대한 짧은 설명, 공식 제조사, 대표 카테고리, 공식 아이콘 이미지 URL을 검색해서 JSON으로 줘."
3. **Web Crawling**: 구현하지 않음 (2026-09-21 폐기 확정)
   - 과거 문서에는 9개 소스(Softpedia / GitHub / Archive.org / FileHippo / SourceForge /
     GitLab / DuckDuckGo / Bing / AlternativeTo)를 병렬 검색해 우선순위로 병합한다는
     설계가 상세히 기술되어 있었으나 **코드로 구현된 적이 없다.**
     `backend/app` 전체 검색 결과 해당 키워드는 0건이다.
   - 실제 메타데이터 보강 경로는 다음 두 가지뿐이다:
     - AI 생성 (`core/ai_metadata.py`, `core/metadata_enricher.py`)
     - 이미지 검색 (`core/google_image_search.py` — Google CSE, 설정에서 on/off)
   - `products.crawled_from` 컬럼은 이 설계의 잔재다. 값을 쓰는 코드가 없다.

4. **Local Caching**: 아이콘/스크린샷을 NAS 로컬에 캐시 (`/data/icons`, `/data/screenshots`)

**Critical**: For ambiguous filenames like `setup.exe`, use the parent folder name as search context.

### Caching Strategy ✅ IMPLEMENTED (2계층)

> **정정 (2026-09-21)**: 이전 문서는 "3계층 ✅ IMPLEMENTED"라며 2계층으로
> `metadata_cache` DB 캐시를 기술했으나, **그 계층은 존재하지 않는다.**
> `MetadataCache` 모델은 `app/api`·`app/core` 어디에서도 참조되지 않는다
> (`models/__init__.py`의 export 한 줄뿐). v1.4.64의 죽은 코드 정리에서
> 사용처가 제거되었고 모델만 남았다. 테이블 정리 여부는 보류 중이다.

1. **File Cache (Images)**: `/data/icons`, `/data/screenshots`
   - 제품 아이콘·스크린샷을 로컬에 캐시 (`core/icon_cache.py`)
   - 외부 API 의존도 감소, 영구 보관

2. **Redis Cache (API Responses)**: 포트 6379
   - 제품 목록/검색/통계 응답
   - TTL 기반 만료 (60~600초)
   - 데이터 변경 시 스마트 무효화 — `KEYS` 대신 `SCAN` 사용 (대규모 캐시에서 Redis 블로킹 방지)
   - Redis 연결 실패 시 예외를 삼키고 캐시 없이 동작 (graceful degradation)

**Cache Management**:
- Admin API: `GET /api/cache/stats`, `POST /api/cache/clear`
- 자동 무효화: 제품 수정, 스캔, AI 매칭 시
- 키 패턴: `{prefix}:{params_hash}`

### File Scanning & Monitoring
- Use Python `os.walk` to traverse configured folder paths
- New folder detected → register as new program
- New file in existing folder → register as new version
- Use `APScheduler` for scheduled automatic scans (e.g., nightly)

### File Serving Strategy
Use Nginx **X-Accel-Redirect** headers instead of streaming through backend to reduce server load for large file downloads.

### Authentication & First-Run Setup
- Detect empty Users table → redirect to `/setup` page for admin account creation
- Admin page provides user CRUD operations

## UI Structure

1. **Dashboard (Home)**: Netflix-style horizontal scroll cards for recently added apps, system statistics
2. **Discover**: Category filters (left sidebar), grid of app cards (responsive to 1-column on mobile)
3. **Detail Page**: Large icon/title/vendor header with tabs:
   - 정보 (Info): AI-generated description and tags
   - 버전 (Versions): Downloadable file list by version
   - 자료실 (Resources): User-uploaded additional files and notes
4. **Admin**: Scan path management, AI API key configuration, user management

## Development Roadmap

### Phase 1: MVP ✅ COMPLETED
- Docker environment (FastAPI + Vue + PostgreSQL)
- Basic file scanning from configured folders to DB
- Login and download functionality
- Basic list view UI
- JWT authentication with OAuth2PasswordBearer
- First-run setup page for admin account creation

### Phase 2: Metadata & AI Integration ✅ COMPLETED
- Enhanced filename parsing algorithms (FilenameParser with noise word filtering)
- OpenAI API integration (GPT-4o-mini) for automatic metadata
- Icon crawling and local storage (IconCache with httpx)
- Fallback mechanism when AI is unavailable
- Admin page with AI toggle option

### Phase 3: Enhancement ✅ COMPLETED
- Auto-scan scheduler (APScheduler with cron expressions)
- Scheduler management UI (AdminScheduler.vue)
- ScanHistory tracking model
- Advanced search and filtering (category, vendor, search)
- Autocomplete suggestions
- Download optimization with X-Accel-Redirect headers
- Category-based product grouping (Netflix-style)
- Scheduler persistence via Settings table

## Docker Configuration Notes

When implementing docker-compose.yml:
- **Library folder**: `./data/library` mounted to `/library` in container (main storage)
- Optional: Mount NAS software folder as **read-only** at `/library/NAS` (e.g., `/volume1/Software:/library/NAS:ro`)
- Separate volumes for: DB storage (`./data/db`), Redis data (`./data/redis`), icon cache (`./data/icons`), library (`./data/library`)
- Required environment variables: `OPENAI_API_KEY`, `SECRET_KEY`, `REDIS_URL`, `SCAN_BASE_PATH=/library`
- Ports: Backend 8110, Frontend 5900, Redis 6379
- Services: PostgreSQL (db), Redis (redis), FastAPI (backend), Vite (frontend)

## Critical Development Considerations

1. **AI Cost Management**: Only call AI for items without existing metadata in DB (check before querying)
2. **Filename Ambiguity Handling**: For generic filenames, use parent folder name as primary search context
3. **Security**: Implement session-based download link validation even for internal NAS usage to prevent unauthorized access if links leak

## Current Implementation Status (v1.4.76, 2026-09-21 실측)

> 이전 문서는 "v3.0.0 / 백엔드 30개 파일 / 프론트 17개 파일 / 모델 6개"로 적혀 있었다.
> 아래는 코드에서 직접 센 값이다. 규모가 바뀌면 여기도 함께 고칠 것.

| 항목 | 실측 |
|---|---|
| 버전 | **1.4.76** |
| 백엔드 | **81개 `.py` / 15,276줄** |
| API 라우터 | **24개** |
| SQLAlchemy 모델 | **15개** |
| 프론트엔드 뷰 | **21개 `.vue`** |
| Alembic 마이그레이션 | **27개** (정본) |
| 로케일 | ko / en |

### 백엔드 구조

```
backend/app/
├── main.py            FastAPI 앱, 스케줄러 자동 시작
│                      (스키마 DDL 없음 - entrypoint.sh 의 Alembic 이 담당)
├── config.py          Pydantic Settings
├── database.py        SQLAlchemy engine + SessionLocal
├── dependencies.py    get_current_user, get_current_admin_user
├── models/            15개 모델
├── schemas/           Pydantic 스키마
├── api/               24개 라우터 (아래 표)
├── core/              스캐너·파서·분류기·AI·매처·캐시·스케줄러·알림
└── middleware/        요청 로깅
backend/alembic/       마이그레이션 27개 (스키마 정본)
backend/entrypoint.sh  DB 대기 -> Alembic 모드 판정 -> upgrade/stamp -> 앱 기동
```

### API 라우터

| 모듈 | prefix |
|---|---|
| `auth` | `/api/auth"` |
| `products` | `/api/products"` |
| `users` | `/api/users"` |
| `invitations` | `/api/invitations"` |
| `scan` | `/api/scan"` |
| `download` | `/api/download"` |
| `scheduler` | `/api/scheduler"` |
| `filesystem` | `/api/filesystem"` |
| `favorites` | `/api/favorites"` |
| `scraps` | `/api/scraps"` |
| `config` | `/api/config"` |
| `metadata` | `/api/metadata"` |
| `posts` | `/api/posts"` |
| `comments` | `/api/posts"` |
| `images` | `/api/images"` |
| `version` | `/api"` |
| `cache` | `/api/cache"` |
| `notifications` | `/api/notifications"` |
| `share` | `/api/share"` |
| `backup` | `/api/backup"` |
| `activity_log` | `/api"` |

### 프론트엔드 구조

```
frontend/src/
├── main.js, App.vue
├── router/index.js    네비게이션 가드 + 청크 로드 실패 자가 복구
├── store/             Pinia (auth, locale)
├── api/               Axios 클라이언트
├── components/        admin · common · dialog · layout · product · violation
├── locales/           ko.js / en.js
└── views/             21개 화면
```

### 스키마 관리 (2026-09-21 통일 완료)

정본은 `backend/alembic/versions/` **하나**다. 바꾸려면:

```bash
# 1. 모델 수정 후
alembic revision --autogenerate -m "설명"
# 2. 생성된 파일을 반드시 검토 (손수 만든 GIN 인덱스를 drop 하려 들 수 있다)
```

- `entrypoint.sh` 가 DB 상태를 보고 `upgrade` / `stamp` / 중단을 자동 판정한다
- CI 의 `schema-check` 잡이 `alembic check` 로 드리프트를 막는다 — 어긋나면 이미지가 빌드되지 않는다
- ❌ `entrypoint.sh` 나 `main.py` 에 DDL 을 다시 넣지 말 것
- 의도적 예외(손수 만든 GIN 인덱스, 보류 중인 죽은 테이블/컬럼)는 `alembic/env.py` 의 `include_object` 에서 제외한다

### 릴리스

```bash
./build.sh [patch|minor|major]   # 버전 bump + 커밋 + 태그 + push
```
이미지 빌드/푸시는 **GitHub Actions 만** 수행한다. `build.sh` 는 빌드하지 않는다.

# GitNexus — Code Intelligence

This project is indexed by GitNexus as **my-appstore** (6425 symbols, 12485 relationships, 300 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> Index stale? Run `node .gitnexus/run.cjs analyze` from the project root — it auto-selects an available runner. No `.gitnexus/run.cjs` yet? `npx gitnexus analyze` (npm 11 crash → `npm i -g gitnexus`; #1939).

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows. For regression review, compare against the default branch: `detect_changes({scope: "compare", base_ref: "main"})`.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `query({search_query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `context({name: "symbolName"})`.
- For security review, `explain({target: "fileOrSymbol"})` lists taint findings (source→sink flows; needs `analyze --pdg`).

## Never Do

- NEVER edit a function, class, or method without first running `impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `rename` which understands the call graph.
- NEVER commit changes without running `detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/my-appstore/context` | Codebase overview, check index freshness |
| `gitnexus://repo/my-appstore/clusters` | All functional areas |
| `gitnexus://repo/my-appstore/processes` | All execution flows |
| `gitnexus://repo/my-appstore/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
