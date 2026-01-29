# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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
3. **Multi-Source Web Crawling**: Uses 9 sources in parallel with priority-based result merging:

   **Priority 1 (Core - Highest Trust)**: Softpedia, GitHub, Archive.org
   - Most reliable and detailed metadata

   **Priority 2 (Support)**: FileHippo, SourceForge, GitLab
   - Additional info and download links

   **Priority 3 (Search Engines)**: DuckDuckGo, Bing
   - General search and official site links

   **Priority 4 (Other)**: AlternativeTo
   - Software alternatives info

   **Merge Strategy**:
   - All sources searched in parallel for performance
   - Results merged with priority: 1 → 2 → 3 → 4
   - Official website: Priority 1 sources preferred
   - Download URL: GitHub/SourceForge releases prioritized
   - Descriptions: All sources combined (priority order)
4. **Local Caching**: Store metadata in DB and cache images locally on NAS

**Critical**: For ambiguous filenames like `setup.exe`, use the parent folder name as search context.

### Hybrid Caching Strategy ✅ IMPLEMENTED
Three-layer caching approach for optimal performance:

1. **File Cache (Images)**: `/data/icons`, `/data/screenshots`
   - Product icons and screenshots cached locally
   - Reduces external API dependency
   - Permanent storage

2. **Database Cache (Metadata)**: `metadata_cache` table
   - AI-generated metadata cached in PostgreSQL
   - Prevents duplicate AI API calls
   - Tracks hit count and confidence score
   - Source tracking: ai/manual/web

3. **Redis Cache (API Responses)**: Port 6379
   - Product lists, searches, statistics
   - TTL-based automatic expiration (60-600 seconds)
   - Smart invalidation on data changes
   - 40-60x performance improvement
   - Graceful degradation if Redis unavailable

**Cache Management**:
- Admin API: `GET /api/cache/stats`, `POST /api/cache/clear`
- Automatic invalidation on: product updates, scans, AI matching
- Key pattern: `{prefix}:{params_hash}`

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

## Current Implementation Status (v3.0.0)

### Backend Structure (30 files)
```
backend/app/
├── main.py                    # FastAPI app with scheduler auto-start
├── config.py                  # Pydantic Settings (ICON_CACHE_DIR hardcoded to dev path)
├── database.py                # SQLAlchemy engine + SessionLocal
├── dependencies.py            # get_current_user, get_current_admin_user
├── models/                    # 6 SQLAlchemy models
│   ├── user.py
│   ├── product.py
│   ├── version.py
│   ├── attachment.py
│   ├── setting.py
│   └── scan_history.py
├── schemas/                   # 4 Pydantic schemas
├── api/                       # 7 API routers
│   ├── auth.py               # /login, /setup, /check-setup
│   ├── users.py
│   ├── products.py           # Enhanced with search, filters, stats
│   ├── scan.py               # Manual scan with AI toggle
│   ├── download.py           # X-Accel-Redirect
│   ├── scheduler.py          # /start, /stop, /run-now, /status
│   └── filesystem.py         # Folder browser API
└── core/                      # 6 core modules
    ├── security.py           # JWT + Bcrypt
    ├── parser.py             # FilenameParser
    ├── ai_metadata.py        # AIMetadataGenerator (OpenAI)
    ├── icon_cache.py         # IconCache (httpx)
    ├── scanner.py            # FileScanner (async/sync)
    └── scheduler.py          # ScanScheduler (APScheduler)
```

### Frontend Structure (17 files)
```
frontend/src/
├── main.js
├── App.vue
├── router/index.js           # Navigation guards
├── store/auth.js             # Pinia auth state
├── api/                      # 7 API clients
│   ├── client.js            # Axios with interceptors
│   ├── auth.js
│   ├── products.js
│   ├── scan.js
│   ├── scheduler.js
│   └── filesystem.js        # Folder browser API
├── components/              # Reusable components
│   ├── FolderBrowser.vue    # Folder selection modal
│   └── ...
└── views/                    # 10 views
    ├── Login.vue
    ├── Setup.vue
    ├── Home.vue             # Dashboard with stats
    ├── Discover.vue         # Product browsing
    ├── ProductDetail.vue    # Product details with tabs
    ├── Settings.vue         # Settings with folder browser integration
    ├── Admin.vue            # 3 tabs: manual scan, scheduler, info
    ├── Tips.vue             # Tips & Tech board list
    ├── TipsDetail.vue       # Tips post detail view
    └── TipsWrite.vue        # Tips post editor with TinyMCE
```

### Key Implementation Details

**AI Metadata Generation**:
- Model: GPT-4o-mini
- Prompt: Korean language, JSON-only response
- Categories: Graphics, Office, Development, Utility, Media, OS, Security, Network, Mac, Mobile, Patch, Driver, Source, Backup, Portable, Business, Engineering, Theme, Hardware, Uncategorized
- Fallback: Parser-based metadata if API fails or unavailable

**Scheduler**:
- Global instance: `scan_scheduler` in `core/scheduler.py`
- Auto-start on app startup if settings exist in DB
- Cron expressions supported (default: "0 2 * * *")
- Settings persisted in Settings table (scan_paths, cron_schedule, use_ai)

**Authentication**:
- JWT tokens with HS256 algorithm
- OAuth2PasswordBearer scheme
- Token stored in localStorage on frontend
- 401 responses trigger automatic logout

**File Scanning Logic**:
- Folder = Product (identified by folder_path)
- File in folder = Version (identified by file_path)
- Duplicate detection via DB unique constraints
- Both sync and async scan methods available

### Folder Browser Feature (v3.1.0)

**Backend** (`app/api/filesystem.py`):
- `GET /api/filesystem/browse?path={path}` - Browse directory contents
  - Returns: current_path, parent_path, items (name, path, is_dir, is_readable)
  - Default path: `/library`
  - Admin-only access
- `POST /api/filesystem/create-directory?path={path}` - Create new directory
  - Admin-only access

**Frontend** (`components/FolderBrowser.vue`):
- Modal-based folder selection UI
- Breadcrumb navigation
- Visual folder tree with readable/unreadable indicators
- Double-click to navigate, single-click to select
- Direct path input support
- Integrated into Settings.vue for scan folder configuration

**Default Library Folder**:
- Base path: `/library` (mounted from `./data/library`)
- Used as default starting point for folder browser
- NAS folders can be mounted as subdirectories (e.g., `/library/NAS`)

### Known Hardcoded Values (Need Attention)

1. **config.py**: `ICON_CACHE_DIR = "/home/nuricom/project/myappStore/data/icons"`
   - Should use environment variable for Docker compatibility

2. **Settings.vue**: Default folder is now `/library` (updated from `/tmp/myappstore_scan_test`)

3. **docker-compose.yml**: Library folder configured
   - `./data/library:/library` (main storage)
   - Optional NAS mount: `- /volume1/Software:/library/NAS:ro`

4. **main.py**: `Base.metadata.create_all(bind=engine)` commented out
   - Using Alembic migrations recommended

### Production Deployment Checklist

- [ ] Set up Alembic migrations
- [ ] Add Nginx service to docker-compose.yml for X-Accel-Redirect
- [ ] Configure NAS volume mounts
- [ ] Change ICON_CACHE_DIR to environment variable
- [ ] Build frontend for production (Vite build)
- [ ] Set up logging (replace print() statements)
- [ ] Add health check endpoints
- [ ] Configure CORS for production domains
- [ ] Generate strong SECRET_KEY
- [ ] (Optional) Add API rate limiting
- [ ] (Optional) Add test suite

### API Endpoints Reference

**Auth**:
- POST `/api/auth/login` - Login
- GET `/api/auth/check-setup` - Check if setup needed
- POST `/api/auth/setup` - Create admin account

**Products**:
- GET `/api/products/` - List with filters (category, vendor, search, sort)
- GET `/api/products/recent` - Recent products
- GET `/api/products/by-category` - Netflix-style grouping
- GET `/api/products/search/suggestions` - Autocomplete
- GET `/api/products/{id}` - Product details
- GET `/api/products/stats/overview` - System stats
- GET `/api/products/stats/categories` - Category stats

**Scan**:
- POST `/api/scan/start` - Manual scan (body: {scan_path, use_ai})

**Scheduler**:
- GET `/api/scheduler/status` - Scheduler status
- POST `/api/scheduler/start` - Start scheduler (body: {cron_schedule, scan_paths, use_ai})
- POST `/api/scheduler/stop` - Stop scheduler
- POST `/api/scheduler/run-now` - Immediate scan
- GET `/api/scheduler/config` - Get saved config

**Download**:
- GET `/api/download/{version_id}` - Download file (returns X-Accel-Redirect header)

**Filesystem** (Admin-only):
- GET `/api/filesystem/browse?path={path}` - Browse directory
- POST `/api/filesystem/create-directory?path={path}` - Create directory

All authenticated endpoints require `Authorization: Bearer <token>` header.
Admin-only endpoints: all under `/api/scheduler`, `/api/scan`, `/api/users`, `/api/filesystem`.
