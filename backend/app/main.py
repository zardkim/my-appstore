from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
from pathlib import Path
import logging

from app.database import engine, Base
from app.api import auth, products, users, scan, download, scheduler, filesystem, favorites, scraps, config, metadata, posts, invitations, images, filename_violations, version, comments, cache, attachments, share, product_videos, backup, activity_log
from app.core.scheduler import scan_scheduler
from app.config import settings

# 로깅 시스템 초기화 (FastAPI app 생성 전에 실행)
from app.core.logger import setup_logging
setup_logging()

# 로거 인스턴스 생성
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# ── 레거시 배포 호환: classification 컬럼이 없으면 직접 추가 ──────────
# Alembic 마이그레이션 실패 또는 구 create_all() 배포 환경에서
# classification 컬럼이 누락될 수 있으므로 앱 시작 시 직접 보장
try:
    from sqlalchemy import text as _text
    with engine.connect() as _conn:
        _conn.execute(_text(
            "ALTER TABLE filename_violations "
            "ADD COLUMN IF NOT EXISTS classification VARCHAR(20) NOT NULL DEFAULT 'product'"
        ))
        _conn.execute(_text(
            "ALTER TABLE filename_violations "
            "ADD COLUMN IF NOT EXISTS classification_auto BOOLEAN NOT NULL DEFAULT true"
        ))
        _conn.commit()
except Exception:
    pass  # 테이블이 아직 없거나 이미 컬럼이 있으면 무시

# ── users.email 컬럼 보장 (ALTER TABLE은 별도 트랜잭션으로 커밋) ────────
try:
    from sqlalchemy import text as _text2
    with engine.connect() as _conn2:
        _conn2.execute(_text2(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR"
        ))
        _conn2.commit()
    logger.info("✓ users.email column verified")
except Exception as _e2:
    logger.info(f"users.email column: {_e2}")

# UNIQUE 제약조건은 별도 트랜잭션 (실패해도 위 컬럼 추가는 유지)
try:
    from sqlalchemy import text as _text3
    with engine.connect() as _conn3:
        _conn3.execute(_text3("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint
                    WHERE conname = 'users_email_key' AND conrelid = 'users'::regclass
                ) THEN
                    ALTER TABLE users ADD CONSTRAINT users_email_key UNIQUE (email);
                END IF;
            END $$;
        """))
        _conn3.commit()
except Exception:
    pass

# Ensure required directories exist before app initialization
required_directories = [
    settings.ICON_CACHE_DIR,
    settings.SCREENSHOT_CACHE_DIR,
    settings.EXIMAGE_DIR,
    settings.PATCHES_DIR,
    settings.CONFIG_DATA_DIR,
    settings.SCAN_BASE_PATH
]

for directory in required_directories:
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"✓ Directory ensured: {directory}")
    except Exception as e:
        logger.error(f"Failed to create directory {directory}: {e}", exc_info=True)

from app.version import get_version

# API 문서용 태그 메타데이터
tags_metadata = [
    {
        "name": "Authentication",
        "description": "사용자 인증 및 계정 관리 (로그인, 회원가입, 비밀번호 변경)",
    },
    {
        "name": "Products",
        "description": "제품(소프트웨어) 관리 - 목록 조회, 상세 정보, 검색, 통계",
    },
    {
        "name": "Users",
        "description": "사용자 관리 (관리자 전용)",
    },
    {
        "name": "Invitations",
        "description": "초대 코드 관리 (관리자 전용)",
    },
    {
        "name": "Scan",
        "description": "파일 시스템 스캔 및 메타데이터 생성",
    },
    {
        "name": "Download",
        "description": "파일 다운로드",
    },
    {
        "name": "Scheduler",
        "description": "자동 스캔 스케줄러 관리",
    },
    {
        "name": "Filesystem",
        "description": "파일 시스템 탐색기",
    },
    {
        "name": "Favorites",
        "description": "즐겨찾기 관리",
    },
    {
        "name": "Scraps",
        "description": "스크랩(북마크) 관리",
    },
    {
        "name": "Config",
        "description": "설정 관리",
    },
    {
        "name": "Metadata",
        "description": "AI 메타데이터 생성 및 관리",
    },
    {
        "name": "Unmatched",
        "description": "매칭되지 않은 파일 관리",
    },
    {
        "name": "Posts",
        "description": "게시판(팁&테크) 게시글 관리",
    },
    {
        "name": "Comments",
        "description": "댓글 관리",
    },
    {
        "name": "Images",
        "description": "이미지 검색 및 업로드",
    },
    {
        "name": "Filename Violations",
        "description": "파일명 규칙 위반 관리",
    },
    {
        "name": "Version",
        "description": "버전 정보",
    },
    {
        "name": "Cache",
        "description": "캐시 관리 (Redis)",
    },
    {
        "name": "Attachments",
        "description": "패치/크랙 파일 관리 (업로드, 다운로드, 삭제)",
    },
    {
        "name": "Share",
        "description": "제품 공유링크 생성 및 관리 (1회성, 기간 제한, 랜덤 비밀번호)",
    },
]

from fastapi import Request
from fastapi.responses import JSONResponse
import traceback

app = FastAPI(
    title="MyApp Store API",
    description="""
# MyApp Store API

NAS 기반 개인 소프트웨어 라이브러리 관리 시스템

## 주요 기능

* **AI 메타데이터 생성**: OpenAI GPT-4o-mini, Google Gemini를 활용한 자동 메타데이터 생성
* **파일 스캔**: 폴더 구조 기반 자동 소프트웨어 감지 및 버전 관리
* **사용자 인증**: JWT 기반 인증 시스템
* **게시판**: 팁&테크 공유 게시판
* **즐겨찾기/스크랩**: 개인화된 소프트웨어 관리
* **스케줄러**: 자동 스캔 스케줄링 (Cron 표현식 지원)
* **Redis 캐싱**: 빠른 응답을 위한 캐시 시스템

## 기술 스택

* FastAPI (Python 3.11+)
* PostgreSQL
* Redis
* SQLAlchemy ORM
* Alembic (마이그레이션)
* JWT 인증
* OpenAI & Google Gemini API

## 인증

대부분의 API는 JWT 토큰 기반 인증이 필요합니다.

1. `/api/auth/login`으로 로그인
2. 받은 `access_token`을 `Authorization: Bearer <token>` 헤더에 포함

## 바로가기

* [API 상태 페이지](/api-status)
* [Health Check](/health)
* [버전 정보](/api/version)
    """,
    version=get_version(),
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url=None,  # 커스텀 ReDoc 사용
    openapi_url="/openapi.json",
    contact={
        "name": "MyApp Store",
        "url": "https://github.com/zardkim/my-appstore",
    },
    license_info={
        "name": "MIT License",
    },
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    tb = traceback.format_exc()
    logger.error(f"Unhandled exception on {request.url}: {tb}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "traceback": tb, "type": type(exc).__name__}
    )

# CORS configuration - 환경변수에서 동적 로드
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging middleware
from app.middleware.logging_middleware import LoggingMiddleware
app.add_middleware(LoggingMiddleware)

# 정적 파일 디렉토리 생성 및 마운트 (디렉토리가 없으면 자동 생성)
for dir_path, mount_path, name in [
    (settings.ICON_CACHE_DIR, "/static/icons", "icons"),
    (settings.SCREENSHOT_CACHE_DIR, "/static/screenshots", "screenshots"),
    (settings.EXIMAGE_DIR, "/static/eximage", "eximage"),
    (settings.VIDEOS_DIR, "/static/videos", "videos"),
]:
    os.makedirs(dir_path, exist_ok=True)
    app.mount(mount_path, StaticFiles(directory=dir_path), name=name)
    logger.info(f"✓ {name} mounted: {mount_path} -> {dir_path}")

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(invitations.router, prefix="/api/invitations", tags=["Invitations"])
app.include_router(scan.router, prefix="/api/scan", tags=["Scan"])
app.include_router(download.router, prefix="/api/download", tags=["Download"])
app.include_router(scheduler.router, prefix="/api/scheduler", tags=["Scheduler"])
app.include_router(filesystem.router, prefix="/api/filesystem", tags=["Filesystem"])
app.include_router(favorites.router, prefix="/api/favorites", tags=["Favorites"])
app.include_router(scraps.router, prefix="/api/scraps", tags=["Scraps"])
app.include_router(config.router, prefix="/api/config", tags=["Config"])
app.include_router(metadata.router, prefix="/api/metadata", tags=["Metadata"])
app.include_router(posts.router, prefix="/api/posts", tags=["Posts"])
app.include_router(comments.router, prefix="/api/posts", tags=["Comments"])
app.include_router(images.router, prefix="/api/images", tags=["Images"])
app.include_router(filename_violations.router, tags=["Filename Violations"])
app.include_router(version.router, prefix="/api", tags=["Version"])
app.include_router(cache.router, prefix="/api/cache", tags=["Cache"])
app.include_router(attachments.router, tags=["Attachments"])
app.include_router(share.router, prefix="/api/share", tags=["Share"])
app.include_router(product_videos.router, tags=["product-videos"])
app.include_router(backup.router, prefix="/api/backup", tags=["Backup"])
app.include_router(activity_log.router, prefix="/api", tags=["Activity Log"])


@app.on_event("startup")
async def startup_event():
    """
    애플리케이션 시작 시 실행
    """
    logger.info("=" * 50)
    logger.info("MyApp Store API Starting...")
    logger.info("=" * 50)
    logger.debug(f"ICON_CACHE_DIR = {settings.ICON_CACHE_DIR}")
    logger.debug(f"SCREENSHOT_CACHE_DIR = {settings.SCREENSHOT_CACHE_DIR}")
    logger.debug(f"EXIMAGE_DIR = {settings.EXIMAGE_DIR}")
    logger.debug(f"SCAN_BASE_PATH = {settings.SCAN_BASE_PATH}")
    logger.debug(f"CONFIG_DATA_DIR = {settings.CONFIG_DATA_DIR}")
    logger.debug(f"CORS_ORIGINS = {settings.get_cors_origins()}")
    logger.debug(f"REDIS_URL = {settings.REDIS_URL}")

    # Redis 캐시 초기화 테스트
    from app.core.redis_cache import redis_cache
    if redis_cache.enabled:
        logger.info("✓ Redis cache connected successfully")
    else:
        logger.warning("Redis cache disabled (will run without caching)")

    # 데이터베이스에서 스케줄러 설정 로드
    try:
        scan_scheduler.load_settings_from_db()

        # 스캔 경로가 설정되어 있으면 스케줄러 자동 시작
        if scan_scheduler.scan_paths:
            scan_scheduler.start()
            logger.info("✓ Auto-scan scheduler initialized")
        else:
            logger.warning("Scheduler not started (no scan paths configured)")

    except Exception as e:
        logger.error(f"Failed to initialize scheduler: {e}", exc_info=True)

    logger.info("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    """
    애플리케이션 종료 시 실행
    """
    logger.info("Shutting down MyApp Store API...")
    scan_scheduler.stop()
    logger.info("✓ Scheduler stopped")


@app.get("/")
async def root():
    """API 루트 엔드포인트"""
    return {
        "message": "MyApp Store API",
        "version": get_version(),
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
        "health": "/health"
    }

@app.get("/api")
async def api_info():
    """API 정보 엔드포인트"""
    return {
        "name": "MyApp Store API",
        "version": get_version(),
        "description": "NAS 기반 개인 소프트웨어 라이브러리 관리 시스템",
        "documentation": {
            "swagger": f"{settings.get_backend_url()}/docs",
            "redoc": f"{settings.get_backend_url()}/redoc",
            "openapi_schema": f"{settings.get_backend_url()}/openapi.json"
        },
        "endpoints": {
            "authentication": "/api/auth",
            "products": "/api/products",
            "users": "/api/users",
            "scan": "/api/scan",
            "download": "/api/download",
            "scheduler": "/api/scheduler",
            "filesystem": "/api/filesystem",
            "favorites": "/api/favorites",
            "scraps": "/api/scraps",
            "config": "/api/config",
            "metadata": "/api/metadata",
            "posts": "/api/posts",
            "images": "/api/images",
            "cache": "/api/cache",
            "version": "/api/version"
        },
        "features": [
            "AI 메타데이터 생성 (OpenAI GPT-4o-mini, Google Gemini)",
            "파일 시스템 자동 스캔",
            "JWT 기반 인증",
            "게시판 (팁&테크)",
            "즐겨찾기/스크랩",
            "자동 스캔 스케줄러",
            "Redis 캐싱"
        ],
        "contact": {
            "github": "https://github.com/zardkim/my-appstore"
        }
    }

@app.get("/debug-cors")
async def debug_cors():
    return {
        "configured_origins": settings.get_cors_origins(),
        "message": "Current CORS origins from environment variables"
    }


@app.get("/redoc", response_class=HTMLResponse)
async def redoc_html():
    """커스텀 ReDoc 문서 페이지"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>MyApp Store API - ReDoc</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
        <link rel="shortcut icon" href="https://fastapi.tiangolo.com/img/favicon.png">
        <style>
            body {{
                margin: 0;
                padding: 0;
            }}
        </style>
    </head>
    <body>
        <redoc spec-url="/openapi.json"></redoc>
        <script src="https://cdn.jsdelivr.net/npm/redoc@2.1.3/bundles/redoc.standalone.js"></script>
    </body>
    </html>
    """


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "scheduler": {
            "running": scan_scheduler.is_running,
            "next_run": scan_scheduler.get_status().get("next_run_time")
        }
    }

@app.get("/api-status")
async def api_status():
    """API 상태 확인 페이지 (HTML)"""
    from fastapi.responses import HTMLResponse
    import socket

    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>MyApp Store - API 상태</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }}
            .card {{
                background: white;
                padding: 20px;
                margin: 20px 0;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            h1 {{ color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
            h2 {{ color: #666; margin-top: 0; }}
            .status {{
                display: inline-block;
                padding: 5px 15px;
                border-radius: 20px;
                font-weight: bold;
            }}
            .success {{ background: #4CAF50; color: white; }}
            .error {{ background: #f44336; color: white; }}
            .info {{ background: #2196F3; color: white; }}
            button {{
                padding: 10px 20px;
                margin: 5px;
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
            }}
            button:hover {{ background: #45a049; }}
            #result {{
                margin-top: 20px;
                padding: 15px;
                background: #f9f9f9;
                border-left: 4px solid #4CAF50;
                white-space: pre-wrap;
                font-family: monospace;
                font-size: 12px;
            }}
            .endpoint {{
                background: #f0f0f0;
                padding: 5px 10px;
                border-radius: 4px;
                font-family: monospace;
                display: inline-block;
                margin: 5px 0;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }}
            th, td {{
                padding: 10px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{ background: #4CAF50; color: white; }}
        </style>
    </head>
    <body>
        <h1>🚀 MyApp Store API 상태</h1>

        <div class="card">
            <h2>서버 정보</h2>
            <table>
                <tr><th>항목</th><th>값</th></tr>
                <tr><td>서버 상태</td><td><span class="status success">정상 작동</span></td></tr>
                <tr><td>호스트명</td><td>{hostname}</td></tr>
                <tr><td>내부 IP</td><td>{local_ip}</td></tr>
                <tr><td>백엔드 포트</td><td>8110</td></tr>
                <tr><td>프론트엔드 포트</td><td>5900</td></tr>
                <tr><td>CORS 설정</td><td>{settings.CORS_ORIGINS}</td></tr>
            </table>
        </div>

        <div class="card">
            <h2>접속 URL</h2>
            <p><strong>로컬 접속:</strong></p>
            <div class="endpoint">http://localhost:5900</div>
            <p><strong>내부 네트워크 접속:</strong></p>
            <div class="endpoint">http://{local_ip}:5900</div>
            <div class="endpoint">http://192.168.0.8:5900</div>
        </div>

        <div class="card">
            <h2>API 엔드포인트 테스트</h2>
            <button onclick="testEndpoint('/health', 'GET')">Health Check</button>
            <button onclick="testEndpoint('/api/auth/check-setup', 'GET')">Setup Check</button>
            <button onclick="testEndpoint('/api/products/stats/overview', 'GET', true)">Products Stats (인증 필요)</button>
            <button onclick="testLogin()">로그인 테스트</button>
            <button onclick="clearResult()">결과 지우기</button>
            <div style="margin-top: 10px;">
                <label style="font-size: 14px;">사용자명: </label>
                <input type="text" id="username" value="nuricom" style="padding: 5px; border: 1px solid #ccc; border-radius: 4px;">
                <label style="font-size: 14px; margin-left: 10px;">비밀번호: </label>
                <input type="password" id="password" value="" placeholder="비밀번호 입력" style="padding: 5px; border: 1px solid #ccc; border-radius: 4px;">
            </div>
            <div id="result"></div>
        </div>

        <div class="card">
            <h2>주요 API 엔드포인트</h2>
            <table>
                <tr><th>엔드포인트</th><th>설명</th><th>인증</th></tr>
                <tr><td>/health</td><td>서버 상태 확인</td><td>불필요</td></tr>
                <tr><td>/api/auth/login</td><td>로그인</td><td>불필요</td></tr>
                <tr><td>/api/auth/check-setup</td><td>초기 설정 확인</td><td>불필요</td></tr>
                <tr><td>/api/products/</td><td>제품 목록</td><td>필요</td></tr>
                <tr><td>/api/posts/</td><td>게시글 목록</td><td>불필요</td></tr>
                <tr><td>/docs</td><td>API 문서 (Swagger)</td><td>불필요</td></tr>
            </table>
        </div>

        <script>
            let authToken = null;

            function showResult(message, isError = false) {{
                const resultDiv = document.getElementById('result');
                resultDiv.textContent = message;
                resultDiv.style.borderLeftColor = isError ? '#f44336' : '#4CAF50';
                resultDiv.style.background = isError ? '#ffebee' : '#e8f5e9';
            }}

            function clearResult() {{
                document.getElementById('result').textContent = '';
                document.getElementById('result').style.background = '#f9f9f9';
            }}

            async function testEndpoint(endpoint, method = 'GET', needsAuth = false) {{
                try {{
                    showResult('테스트 중...');

                    const headers = {{}};
                    if (needsAuth && authToken) {{
                        headers['Authorization'] = `Bearer ${{authToken}}`;
                    }}

                    const response = await fetch(endpoint, {{
                        method: method,
                        headers: headers
                    }});

                    const data = await response.json();

                    const result = `
✅ 성공!

URL: ${{endpoint}}
Method: ${{method}}
Status: ${{response.status}} ${{response.statusText}}

Response:
${{JSON.stringify(data, null, 2)}}
                    `;

                    showResult(result);
                }} catch (error) {{
                    showResult(`❌ 실패!\\n\\nURL: ${{endpoint}}\\nError: ${{error.message}}`, true);
                }}
            }}

            async function testLogin() {{
                try {{
                    showResult('로그인 테스트 중...');

                    const username = document.getElementById('username').value;
                    const password = document.getElementById('password').value;

                    if (!username || !password) {{
                        showResult('❌ 사용자명과 비밀번호를 입력하세요.', true);
                        return;
                    }}

                    const formData = new FormData();
                    formData.append('username', username);
                    formData.append('password', password);

                    const response = await fetch('/api/auth/login', {{
                        method: 'POST',
                        body: formData
                    }});

                    const data = await response.json();

                    if (response.ok) {{
                        authToken = data.access_token;
                        const result = `
✅ 로그인 성공!

Status: ${{response.status}}
Token Type: ${{data.token_type}}
Access Token: ${{data.access_token.substring(0, 50)}}...

* 토큰이 저장되었습니다. 이제 인증이 필요한 API를 테스트할 수 있습니다.
                        `;
                        showResult(result);
                    }} else {{
                        showResult(`❌ 로그인 실패!\\n\\nStatus: ${{response.status}}\\n\\nResponse:\\n${{JSON.stringify(data, null, 2)}}`, true);
                    }}
                }} catch (error) {{
                    showResult(`❌ 로그인 실패!\\n\\nError: ${{error.message}}`, true);
                }}
            }}
        </script>
    </body>
    </html>
    """

    return HTMLResponse(content=html_content)
