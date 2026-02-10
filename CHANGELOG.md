# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
