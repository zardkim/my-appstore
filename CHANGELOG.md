# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
