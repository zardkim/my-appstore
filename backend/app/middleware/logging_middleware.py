"""
HTTP 요청/응답 로깅 미들웨어
"""
import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import uuid

logger = logging.getLogger("access")


class LoggingMiddleware(BaseHTTPMiddleware):
    """모든 HTTP 요청/응답 로깅"""

    # 로깅에서 제외할 경로
    EXCLUDE_PATHS = [
        "/docs",
        "/redoc",
        "/openapi.json",
        "/favicon.ico",
    ]

    async def dispatch(self, request: Request, call_next):
        # 제외 경로 체크
        if any(request.url.path.startswith(path) for path in self.EXCLUDE_PATHS):
            return await call_next(request)

        # 요청 ID 생성
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # 시작 시간
        start_time = time.time()

        # 요청 정보 추출
        client_host = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        # 요청 로깅
        logger.info(
            f"Incoming request: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "ip_address": client_host,
                "user_agent": user_agent,
            }
        )

        # 요청 처리
        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            # 응답 로깅
            log_level = logging.INFO if response.status_code < 400 else logging.ERROR
            logger.log(
                log_level,
                f"Request completed: {request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "process_time": f"{process_time:.3f}s",
                    "process_time_ms": int(process_time * 1000),
                }
            )

            # 응답 헤더에 request_id 추가
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            process_time = time.time() - start_time

            logger.error(
                f"Request failed: {request.method} {request.url.path} - {str(e)}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                    "path": request.url.path,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "process_time": f"{process_time:.3f}s",
                },
                exc_info=True
            )
            raise
