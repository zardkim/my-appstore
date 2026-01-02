from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path
import logging

from app.database import engine, Base
from app.api import auth, products, users, scan, download, scheduler, filesystem, favorites, scraps, config, metadata, unmatched, posts, invitations, images, filename_violations, version, comments, cache
from app.core.scheduler import scan_scheduler
from app.config import settings

# 로깅 시스템 초기화 (FastAPI app 생성 전에 실행)
from app.core.logger import setup_logging
setup_logging()

# 로거 인스턴스 생성
logger = logging.getLogger(__name__)

# Create database tables
# Base.metadata.create_all(bind=engine)

# Ensure required directories exist before app initialization
required_directories = [
    settings.ICON_CACHE_DIR,
    settings.SCREENSHOT_CACHE_DIR,
    settings.EXIMAGE_DIR,
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

app = FastAPI(
    title="MyApp Store API",
    description="NAS-based personal software library management system",
    version=get_version()
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

# Mount static files directory for icons
static_parent = os.path.dirname(settings.ICON_CACHE_DIR)
if os.path.exists(static_parent):
    app.mount("/static/icons", StaticFiles(directory=settings.ICON_CACHE_DIR), name="icons")
    logger.info(f"✓ Icons mounted: /static/icons -> {settings.ICON_CACHE_DIR}")
else:
    logger.warning(f"Icons directory does not exist: {settings.ICON_CACHE_DIR}")

# Mount static files directory for screenshots
if os.path.exists(settings.SCREENSHOT_CACHE_DIR):
    app.mount("/static/screenshots", StaticFiles(directory=settings.SCREENSHOT_CACHE_DIR), name="screenshots")
    logger.info(f"✓ Screenshots mounted: /static/screenshots -> {settings.SCREENSHOT_CACHE_DIR}")
else:
    logger.warning(f"Screenshots directory does not exist: {settings.SCREENSHOT_CACHE_DIR}")

# Mount static files directory for external images (post content images)
if os.path.exists(settings.EXIMAGE_DIR):
    app.mount("/static/eximage", StaticFiles(directory=settings.EXIMAGE_DIR), name="eximage")
    logger.info(f"✓ External images mounted: /static/eximage -> {settings.EXIMAGE_DIR}")
else:
    logger.warning(f"External images directory does not exist: {settings.EXIMAGE_DIR}")

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
app.include_router(unmatched.router, prefix="/api/unmatched", tags=["Unmatched"])
app.include_router(posts.router, prefix="/api/posts", tags=["Posts"])
app.include_router(comments.router, prefix="/api/posts", tags=["Comments"])
app.include_router(images.router, prefix="/api/images", tags=["Images"])
app.include_router(filename_violations.router, tags=["Filename Violations"])
app.include_router(version.router, prefix="/api", tags=["Version"])
app.include_router(cache.router, prefix="/api/cache", tags=["Cache"])


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
    return {
        "message": "MyApp Store API",
        "version": "3.0.0",
        "phase": "Phase 3 - Advanced Features",
        "docs": "/docs"
    }

@app.get("/debug-cors")
async def debug_cors():
    return {
        "configured_origins": settings.get_cors_origins(),
        "message": "Current CORS origins from environment variables"
    }


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
                <tr><td>백엔드 포트</td><td>8100</td></tr>
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
