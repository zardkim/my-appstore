# 로깅 시스템 구현 계획

## 📋 목차

1. [현재 상태 분석](#현재-상태-분석)
2. [로깅 시스템 아키텍처](#로깅-시스템-아키텍처)
3. [백엔드 로깅 구현](#백엔드-로깅-구현)
4. [프론트엔드 로깅 구현](#프론트엔드-로깅-구현)
5. [데이터베이스 로깅 구현](#데이터베이스-로깅-구현)
6. [로그 관리 UI 구현](#로그-관리-ui-구현)
7. [구현 로드맵](#구현-로드맵)
8. [예상 효과](#예상-효과)

---

## 현재 상태 분석

### 백엔드
```
✗ print() 문 사용: 228개 (15개 파일)
✓ logging 모듈 사용: 1개 (email_sender.py)
✗ 로그 파일 없음
✗ 로그 레벨 구분 없음
✗ 구조화된 로깅 없음
```

**문제점:**
- print()는 로그 레벨, 타임스탬프, 파일 정보 없음
- 로그 파일로 저장되지 않아 디버깅 어려움
- 에러와 정보성 로그 구분 불가
- 프로덕션 환경에서 로그 추적 불가능

### 프론트엔드
```
✓ console.log() 사용 중
✗ 에러 추적 시스템 없음
✗ 사용자 액션 로깅 없음
✗ 프로덕션 로그 수집 없음
```

**문제점:**
- 사용자 환경에서 발생한 에러 파악 불가
- 디버깅 정보가 브라우저에만 남음
- 성능 모니터링 어려움

### 데이터베이스
```
✗ 슬로우 쿼리 로깅 없음
✗ 트랜잭션 로깅 없음
✗ 커넥션 풀 모니터링 없음
```

**문제점:**
- 성능 병목 지점 파악 어려움
- 데이터베이스 관련 에러 추적 불가
- 쿼리 최적화 근거 없음

---

## 로깅 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                     로깅 계층 구조                      │
└─────────────────────────────────────────────────────────┘

┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   프론트엔드     │    │    백엔드        │    │   데이터베이스   │
│                  │    │                  │    │                  │
│  • 콘솔 로그     │    │  • Python        │    │  • 슬로우 쿼리   │
│  • 에러 추적     │    │    logging       │    │  • 커넥션 로그   │
│  • 사용자 액션   │    │  • 파일 로그     │    │  • 에러 로그     │
│  • API 호출 로그 │    │  • 구조화 로그   │    │                  │
└────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘
         │                       │                       │
         │                       ▼                       │
         │              ┌──────────────────┐             │
         └─────────────▶│   로그 수집기    │◀────────────┘
                        │   (Optional)     │
                        │  • Logstash      │
                        │  • Fluentd       │
                        │  • Vector        │
                        └────────┬─────────┘
                                 ▼
                        ┌──────────────────┐
                        │   로그 저장소    │
                        │                  │
                        │  • 파일 시스템   │
                        │  • 데이터베이스  │
                        │  • Elasticsearch │
                        └────────┬─────────┘
                                 ▼
                        ┌──────────────────┐
                        │   로그 뷰어 UI   │
                        │  (관리자 전용)   │
                        │                  │
                        │  • 실시간 조회   │
                        │  • 검색/필터링   │
                        │  • 다운로드      │
                        └──────────────────┘
```

---

## 백엔드 로깅 구현

### 1. Python Logging 설정

#### 1.1 로깅 설정 모듈 (`app/core/logger.py`)

```python
"""
중앙화된 로깅 설정
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
import json

from app.config import settings


class JSONFormatter(logging.Formatter):
    """구조화된 JSON 로그 포맷터"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 예외 정보 추가
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # 추가 컨텍스트 정보
        if hasattr(record, 'user_id'):
            log_data["user_id"] = record.user_id
        if hasattr(record, 'request_id'):
            log_data["request_id"] = record.request_id
        if hasattr(record, 'ip_address'):
            log_data["ip_address"] = record.ip_address

        return json.dumps(log_data, ensure_ascii=False)


def setup_logging():
    """로깅 시스템 초기화"""

    # 로그 디렉토리 생성
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)

    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

    # 기존 핸들러 제거 (중복 방지)
    root_logger.handlers.clear()

    # 콘솔 핸들러 (개발 환경)
    if settings.ENVIRONMENT == "development":
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    # 일반 로그 파일 핸들러 (INFO 이상)
    info_file_handler = RotatingFileHandler(
        filename=log_dir / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    info_file_handler.setLevel(logging.INFO)
    info_file_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(info_file_handler)

    # 에러 로그 파일 핸들러 (ERROR 이상)
    error_file_handler = RotatingFileHandler(
        filename=log_dir / "error.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(error_file_handler)

    # 접근 로그 핸들러 (일별 로테이션)
    access_file_handler = TimedRotatingFileHandler(
        filename=log_dir / "access.log",
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    access_file_handler.setLevel(logging.INFO)
    access_file_handler.setFormatter(JSONFormatter())

    # 별도 access 로거 생성
    access_logger = logging.getLogger("access")
    access_logger.addHandler(access_file_handler)
    access_logger.setLevel(logging.INFO)
    access_logger.propagate = False

    # 외부 라이브러리 로그 레벨 조정
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    logging.info("Logging system initialized")


# 편의 함수
def get_logger(name: str) -> logging.Logger:
    """로거 인스턴스 가져오기"""
    return logging.getLogger(name)
```

#### 1.2 설정 추가 (`app/config.py`)

```python
class Settings(BaseSettings):
    # ... 기존 설정 ...

    # Logging
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_DIR: str = "/home/nuricom/project/myappStore/data/logs"
    ENVIRONMENT: str = "development"  # development, production
```

#### 1.3 미들웨어 추가 (`app/middleware/logging_middleware.py`)

```python
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

    async def dispatch(self, request: Request, call_next):
        # 요청 ID 생성
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # 시작 시간
        start_time = time.time()

        # 요청 정보
        logger.info(
            "Incoming request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "ip_address": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            }
        )

        # 요청 처리
        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            # 응답 로깅
            logger.info(
                "Request completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                    "status_code": response.status_code,
                    "process_time": f"{process_time:.3f}s",
                }
            )

            # 응답 헤더에 request_id 추가
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            process_time = time.time() - start_time

            logger.error(
                "Request failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                    "error": str(e),
                    "process_time": f"{process_time:.3f}s",
                },
                exc_info=True
            )
            raise
```

### 2. 기존 print() 문 변경

#### 2.1 변경 예시

**Before:**
```python
print(f"[RedisCache] Connected to Redis: {settings.REDIS_URL}")
print(f"[RedisCache] Failed to connect to Redis: {e}")
```

**After:**
```python
import logging
logger = logging.getLogger(__name__)

logger.info(f"Connected to Redis: {settings.REDIS_URL}")
logger.error(f"Failed to connect to Redis: {e}", exc_info=True)
```

#### 2.2 로그 레벨 가이드

| 레벨 | 용도 | 예시 |
|------|------|------|
| **DEBUG** | 디버깅 정보 | 변수값, 내부 상태 |
| **INFO** | 일반 정보 | 스캔 시작/완료, 캐쉬 히트/미스 |
| **WARNING** | 경고 (처리 가능) | API 재시도, 캐쉬 미스 |
| **ERROR** | 에러 (기능 실패) | 파일 읽기 실패, API 호출 실패 |
| **CRITICAL** | 치명적 에러 | DB 연결 실패, 서버 시작 실패 |

### 3. 로그 모델 추가 (`app/models/log.py`)

```python
"""
로그 데이터베이스 모델 (선택사항)
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from datetime import datetime
import enum

from app.database import Base


class LogLevel(str, enum.Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Log(Base):
    """시스템 로그 테이블"""
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    level = Column(Enum(LogLevel), index=True)
    logger = Column(String(255), index=True)
    message = Column(Text)
    module = Column(String(255))
    function = Column(String(255))
    line = Column(Integer)

    # 추가 컨텍스트
    user_id = Column(Integer, nullable=True, index=True)
    request_id = Column(String(36), nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)
    exception = Column(Text, nullable=True)

    # 메타데이터
    extra = Column(Text, nullable=True)  # JSON 형식
```

---

## 프론트엔드 로깅 구현

### 1. 로거 유틸리티 (`src/utils/logger.js`)

```javascript
/**
 * 프론트엔드 로깅 유틸리티
 */

class Logger {
  constructor() {
    this.isDevelopment = import.meta.env.MODE === 'development'
    this.logBuffer = []
    this.maxBufferSize = 100
  }

  /**
   * 로그 포맷팅
   */
  formatLog(level, message, context = {}) {
    return {
      timestamp: new Date().toISOString(),
      level,
      message,
      url: window.location.href,
      userAgent: navigator.userAgent,
      ...context
    }
  }

  /**
   * DEBUG 로그
   */
  debug(message, context) {
    if (this.isDevelopment) {
      console.debug(`[DEBUG] ${message}`, context)
    }
    this.addToBuffer('DEBUG', message, context)
  }

  /**
   * INFO 로그
   */
  info(message, context) {
    if (this.isDevelopment) {
      console.info(`[INFO] ${message}`, context)
    }
    this.addToBuffer('INFO', message, context)
  }

  /**
   * WARNING 로그
   */
  warn(message, context) {
    console.warn(`[WARN] ${message}`, context)
    this.addToBuffer('WARNING', message, context)
  }

  /**
   * ERROR 로그
   */
  error(message, error, context) {
    console.error(`[ERROR] ${message}`, error, context)

    const logEntry = this.formatLog('ERROR', message, {
      ...context,
      error: {
        name: error?.name,
        message: error?.message,
        stack: error?.stack
      }
    })

    this.addToBuffer('ERROR', message, logEntry)

    // 에러는 즉시 서버로 전송
    this.sendToServer([logEntry])
  }

  /**
   * 로그 버퍼에 추가
   */
  addToBuffer(level, message, context) {
    const logEntry = this.formatLog(level, message, context)
    this.logBuffer.push(logEntry)

    // 버퍼 크기 제한
    if (this.logBuffer.length > this.maxBufferSize) {
      this.logBuffer.shift()
    }
  }

  /**
   * 서버로 로그 전송
   */
  async sendToServer(logs) {
    if (!logs || logs.length === 0) return

    try {
      await fetch('/api/logs/frontend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ logs })
      })
    } catch (err) {
      // 로그 전송 실패 시 콘솔에만 표시
      console.error('Failed to send logs to server:', err)
    }
  }

  /**
   * 주기적으로 버퍼 플러시
   */
  startAutoFlush(intervalMs = 60000) {
    setInterval(() => {
      if (this.logBuffer.length > 0) {
        this.sendToServer([...this.logBuffer])
        this.logBuffer = []
      }
    }, intervalMs)
  }

  /**
   * 사용자 액션 로깅
   */
  logAction(action, details = {}) {
    this.info(`User action: ${action}`, {
      action,
      ...details,
      userId: localStorage.getItem('userId')
    })
  }

  /**
   * API 호출 로깅
   */
  logApiCall(method, url, status, duration) {
    const level = status >= 400 ? 'ERROR' : 'INFO'
    this[level.toLowerCase()](`API ${method} ${url}`, {
      method,
      url,
      status,
      duration: `${duration}ms`
    })
  }
}

// 싱글톤 인스턴스
export const logger = new Logger()

// 전역 에러 핸들러
window.addEventListener('error', (event) => {
  logger.error('Unhandled error', event.error, {
    filename: event.filename,
    lineno: event.lineno,
    colno: event.colno
  })
})

// Promise rejection 핸들러
window.addEventListener('unhandledrejection', (event) => {
  logger.error('Unhandled promise rejection', event.reason)
})
```

### 2. API 인터셉터에 로깅 추가 (`src/api/client.js`)

```javascript
import axios from 'axios'
import { logger } from '@/utils/logger'

// 요청 인터셉터
client.interceptors.request.use(
  (config) => {
    config.metadata = { startTime: new Date() }
    logger.debug(`API Request: ${config.method.toUpperCase()} ${config.url}`, {
      params: config.params,
      data: config.data
    })
    return config
  },
  (error) => {
    logger.error('API Request failed', error)
    return Promise.reject(error)
  }
)

// 응답 인터셉터
client.interceptors.response.use(
  (response) => {
    const duration = new Date() - response.config.metadata.startTime
    logger.logApiCall(
      response.config.method.toUpperCase(),
      response.config.url,
      response.status,
      duration
    )
    return response
  },
  (error) => {
    const duration = error.config?.metadata?.startTime
      ? new Date() - error.config.metadata.startTime
      : 0

    logger.logApiCall(
      error.config?.method?.toUpperCase() || 'UNKNOWN',
      error.config?.url || 'UNKNOWN',
      error.response?.status || 0,
      duration
    )

    return Promise.reject(error)
  }
)
```

### 3. Vue 에러 핸들러 (`src/main.js`)

```javascript
import { logger } from './utils/logger'

const app = createApp(App)

// Vue 에러 핸들러
app.config.errorHandler = (err, instance, info) => {
  logger.error('Vue error', err, {
    component: instance?.$options?.name,
    info
  })
}

// 경고 핸들러
app.config.warnHandler = (msg, instance, trace) => {
  logger.warn('Vue warning', {
    message: msg,
    component: instance?.$options?.name,
    trace
  })
}

// 로그 자동 플러시 시작
logger.startAutoFlush()
```

---

## 데이터베이스 로깅 구현

### 1. SQLAlchemy 로깅 설정

#### 1.1 엔진 설정 (`app/database.py`)

```python
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
import logging
import time

logger = logging.getLogger("sqlalchemy.engine")

# 슬로우 쿼리 임계값 (초)
SLOW_QUERY_THRESHOLD = 1.0


@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """쿼리 실행 전 시간 기록"""
    conn.info.setdefault('query_start_time', []).append(time.time())
    logger.debug(f"Query started: {statement[:100]}...")


@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """쿼리 실행 후 시간 측정"""
    total_time = time.time() - conn.info['query_start_time'].pop(-1)

    if total_time > SLOW_QUERY_THRESHOLD:
        logger.warning(
            f"Slow query detected ({total_time:.3f}s): {statement}",
            extra={
                "query": statement,
                "parameters": parameters,
                "execution_time": total_time
            }
        )
    else:
        logger.debug(f"Query completed in {total_time:.3f}s")


# 엔진 생성 시 로깅 활성화
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",  # 개발 환경에서만 쿼리 출력
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)
```

### 2. 커넥션 풀 모니터링

```python
@event.listens_for(Engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """커넥션 풀 연결 로깅"""
    logger.info("Database connection established")


@event.listens_for(Engine, "close")
def receive_close(dbapi_conn, connection_record):
    """커넥션 풀 해제 로깅"""
    logger.info("Database connection closed")


@event.listens_for(Engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """커넥션 체크아웃 로깅"""
    logger.debug("Connection checked out from pool")


@event.listens_for(Engine, "checkin")
def receive_checkin(dbapi_conn, connection_record):
    """커넥션 체크인 로깅"""
    logger.debug("Connection returned to pool")
```

### 3. PostgreSQL 로깅 설정

#### 3.1 `docker-compose.yml` 수정

```yaml
db:
  image: postgres:15
  environment:
    # ... 기존 설정 ...

    # 로깅 설정
    POSTGRES_INITDB_ARGS: "-c log_statement=all -c log_duration=on"
  command:
    - "postgres"
    - "-c"
    - "log_statement=all"              # 모든 SQL 문 로깅
    - "-c"
    - "log_duration=on"                # 쿼리 실행 시간 로깅
    - "-c"
    - "log_min_duration_statement=1000" # 1초 이상 쿼리만 로깅
    - "-c"
    - "log_line_prefix=%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h " # 로그 포맷
  volumes:
    - ./data/db:/var/lib/postgresql/data
    - ./data/logs/postgresql:/var/log/postgresql  # 로그 저장
```

---

## 로그 관리 UI 구현

### 1. 백엔드 API (`app/api/logs.py`)

```python
"""
로그 관리 API (Admin only)
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import json
from pathlib import Path

from app.dependencies import get_current_admin_user
from app.config import settings

router = APIRouter()


class LogEntry(BaseModel):
    """로그 항목"""
    timestamp: str
    level: str
    logger: str
    message: str
    module: Optional[str] = None
    function: Optional[str] = None
    line: Optional[int] = None
    exception: Optional[str] = None


class LogListResponse(BaseModel):
    """로그 목록 응답"""
    total: int
    logs: List[LogEntry]
    has_more: bool


@router.get("/", response_model=LogListResponse)
async def get_logs(
    log_type: str = Query("app", enum=["app", "error", "access"]),
    level: Optional[str] = Query(None, enum=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    search: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(100, le=1000),
    offset: int = 0,
    current_user = Depends(get_current_admin_user)
):
    """
    로그 목록 조회 (Admin only)

    Args:
        log_type: 로그 타입 (app, error, access)
        level: 로그 레벨 필터
        search: 검색 키워드
        start_date: 시작 날짜
        end_date: 종료 날짜
        limit: 최대 반환 개수
        offset: 오프셋
    """
    log_file_map = {
        "app": "app.log",
        "error": "error.log",
        "access": "access.log"
    }

    log_file = Path(settings.LOG_DIR) / log_file_map[log_type]

    if not log_file.exists():
        return {
            "total": 0,
            "logs": [],
            "has_more": False
        }

    try:
        logs = []
        total = 0

        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    log_entry = json.loads(line.strip())

                    # 레벨 필터
                    if level and log_entry.get('level') != level:
                        continue

                    # 검색 필터
                    if search and search.lower() not in log_entry.get('message', '').lower():
                        continue

                    # 날짜 필터
                    log_time = datetime.fromisoformat(log_entry['timestamp'].replace('Z', '+00:00'))
                    if start_date and log_time < start_date:
                        continue
                    if end_date and log_time > end_date:
                        continue

                    total += 1

                    # 오프셋 및 리미트 적용
                    if total > offset and len(logs) < limit:
                        logs.append(LogEntry(**log_entry))

                except json.JSONDecodeError:
                    continue

        return {
            "total": total,
            "logs": logs[:limit],
            "has_more": total > (offset + limit)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"로그 조회 실패: {str(e)}")


@router.get("/download/{log_type}")
async def download_log(
    log_type: str,
    current_user = Depends(get_current_admin_user)
):
    """
    로그 파일 다운로드 (Admin only)
    """
    from fastapi.responses import FileResponse

    log_file_map = {
        "app": "app.log",
        "error": "error.log",
        "access": "access.log"
    }

    if log_type not in log_file_map:
        raise HTTPException(status_code=400, detail="잘못된 로그 타입")

    log_file = Path(settings.LOG_DIR) / log_file_map[log_type]

    if not log_file.exists():
        raise HTTPException(status_code=404, detail="로그 파일을 찾을 수 없습니다")

    return FileResponse(
        path=log_file,
        filename=f"{log_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
        media_type="text/plain"
    )


@router.delete("/clear/{log_type}")
async def clear_log(
    log_type: str,
    current_user = Depends(get_current_admin_user)
):
    """
    로그 파일 삭제 (Admin only)
    """
    log_file_map = {
        "app": "app.log",
        "error": "error.log",
        "access": "access.log"
    }

    if log_type not in log_file_map:
        raise HTTPException(status_code=400, detail="잘못된 로그 타입")

    log_file = Path(settings.LOG_DIR) / log_file_map[log_type]

    if log_file.exists():
        log_file.unlink()

    return {"success": True, "message": f"{log_type} 로그가 삭제되었습니다"}


@router.post("/frontend")
async def log_frontend(
    logs: List[dict]
):
    """
    프론트엔드 로그 수신

    인증 없이도 로그를 받을 수 있도록 설정
    (에러 추적용)
    """
    import logging
    frontend_logger = logging.getLogger("frontend")

    for log in logs:
        level = log.get('level', 'INFO')
        message = log.get('message', '')

        log_method = getattr(frontend_logger, level.lower(), frontend_logger.info)
        log_method(message, extra=log)

    return {"success": True, "count": len(logs)}
```

### 2. 프론트엔드 UI (`src/views/Logs.vue`)

```vue
<template>
  <div class="logs-viewer">
    <div class="header">
      <h1>시스템 로그</h1>

      <!-- 필터 -->
      <div class="filters">
        <select v-model="logType">
          <option value="app">애플리케이션</option>
          <option value="error">에러</option>
          <option value="access">접근 로그</option>
        </select>

        <select v-model="logLevel">
          <option value="">모든 레벨</option>
          <option value="DEBUG">DEBUG</option>
          <option value="INFO">INFO</option>
          <option value="WARNING">WARNING</option>
          <option value="ERROR">ERROR</option>
          <option value="CRITICAL">CRITICAL</option>
        </select>

        <input
          v-model="searchQuery"
          placeholder="검색..."
          @input="debounceSearch"
        />

        <button @click="downloadLogs">다운로드</button>
        <button @click="clearLogs" class="danger">삭제</button>
      </div>
    </div>

    <!-- 로그 목록 -->
    <div class="log-list">
      <div
        v-for="log in logs"
        :key="log.timestamp"
        :class="['log-entry', `level-${log.level.toLowerCase()}`]"
      >
        <div class="log-header">
          <span class="timestamp">{{ formatTime(log.timestamp) }}</span>
          <span class="level">{{ log.level }}</span>
          <span class="logger">{{ log.logger }}</span>
        </div>
        <div class="log-message">{{ log.message }}</div>
        <div v-if="log.exception" class="log-exception">
          <pre>{{ log.exception }}</pre>
        </div>
      </div>

      <!-- 로딩 -->
      <div v-if="loading" class="loading">로딩 중...</div>

      <!-- 더 불러오기 -->
      <button
        v-if="hasMore && !loading"
        @click="loadMore"
        class="load-more"
      >
        더 보기
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { logsApi } from '@/api/logs'

const logType = ref('app')
const logLevel = ref('')
const searchQuery = ref('')
const logs = ref([])
const loading = ref(false)
const hasMore = ref(false)
const offset = ref(0)

const loadLogs = async (reset = false) => {
  if (reset) {
    offset.value = 0
    logs.value = []
  }

  loading.value = true

  try {
    const response = await logsApi.getLogs({
      log_type: logType.value,
      level: logLevel.value || undefined,
      search: searchQuery.value || undefined,
      limit: 100,
      offset: offset.value
    })

    if (reset) {
      logs.value = response.data.logs
    } else {
      logs.value.push(...response.data.logs)
    }

    hasMore.value = response.data.has_more
  } catch (error) {
    console.error('로그 로드 실패:', error)
  } finally {
    loading.value = false
  }
}

const loadMore = () => {
  offset.value += 100
  loadLogs(false)
}

const downloadLogs = async () => {
  window.open(`/api/logs/download/${logType.value}`, '_blank')
}

const clearLogs = async () => {
  if (!confirm('로그를 삭제하시겠습니까?')) return

  try {
    await logsApi.clearLogs(logType.value)
    loadLogs(true)
  } catch (error) {
    console.error('로그 삭제 실패:', error)
  }
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleString('ko-KR')
}

// 디바운스 검색
let searchTimeout
const debounceSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadLogs(true)
  }, 500)
}

// 필터 변경 시 재로드
watch([logType, logLevel], () => {
  loadLogs(true)
})

// 초기 로드
loadLogs(true)
</script>

<style scoped>
.log-entry {
  border-left: 4px solid;
  padding: 12px;
  margin-bottom: 8px;
  background: white;
  border-radius: 4px;
}

.level-debug { border-color: #6c757d; }
.level-info { border-color: #0d6efd; }
.level-warning { border-color: #ffc107; }
.level-error { border-color: #dc3545; }
.level-critical { border-color: #dc3545; background: #fff5f5; }

.log-exception {
  margin-top: 8px;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 4px;
  font-family: monospace;
  font-size: 12px;
  overflow-x: auto;
}
</style>
```

### 3. API 클라이언트 (`src/api/logs.js`)

```javascript
import client from './client'

export const logsApi = {
  getLogs(params) {
    return client.get('/logs/', { params })
  },

  downloadLogs(logType) {
    return client.get(`/logs/download/${logType}`, {
      responseType: 'blob'
    })
  },

  clearLogs(logType) {
    return client.delete(`/logs/clear/${logType}`)
  }
}
```

---

## 구현 로드맵

### Phase 1: 백엔드 로깅 기반 구축 (1주)

**목표:** 체계적인 로깅 시스템 구축

- [ ] `app/core/logger.py` 구현
- [ ] `app/config.py`에 로깅 설정 추가
- [ ] `app/middleware/logging_middleware.py` 구현
- [ ] `app/main.py`에 로깅 초기화 추가
- [ ] 로그 디렉토리 생성 (`/data/logs/`)
- [ ] 환경변수 추가 (`.env`)

**검증:**
```bash
# 로그 파일 생성 확인
ls -lh /home/nuricom/project/myappStore/data/logs/
# app.log, error.log, access.log 존재 확인

# 로그 내용 확인
tail -f /home/nuricom/project/myappStore/data/logs/app.log
```

### Phase 2: print() → logging 변환 (2주)

**목표:** 모든 print() 문을 logging으로 변경

**우선순위 파일:**
1. `app/core/redis_cache.py` (13개)
2. `app/core/scheduler.py` (15개)
3. `app/core/icon_cache.py` (26개)
4. `app/main.py` (26개)
5. `app/core/scanner.py` (많음)
6. 나머지 파일들...

**변환 가이드라인:**
```python
# Before
print(f"[Info] Something happened: {value}")

# After
logger.info(f"Something happened: {value}")

# Before
print(f"[Error] Failed: {e}")

# After
logger.error(f"Failed: {str(e)}", exc_info=True)
```

**검증:**
```bash
# print() 문 검색 (0개여야 함)
grep -r "print(" backend/app/ --include="*.py" | grep -v "venv" | wc -l
```

### Phase 3: 데이터베이스 로깅 (3일)

**목표:** DB 쿼리 모니터링

- [ ] `app/database.py`에 SQLAlchemy 이벤트 리스너 추가
- [ ] 슬로우 쿼리 로깅 활성화
- [ ] `docker-compose.yml` PostgreSQL 로깅 설정
- [ ] 로그 모델 추가 (선택사항)

**검증:**
```bash
# PostgreSQL 로그 확인
docker logs myapp-postgres | grep "duration:"

# 슬로우 쿼리 확인
grep "Slow query" data/logs/app.log
```

### Phase 4: 프론트엔드 로깅 (1주)

**목표:** 프론트엔드 에러 추적

- [ ] `src/utils/logger.js` 구현
- [ ] `src/api/client.js`에 로깅 인터셉터 추가
- [ ] `src/main.js`에 에러 핸들러 추가
- [ ] 백엔드 `/api/logs/frontend` 엔드포인트 구현
- [ ] 주요 컴포넌트에 액션 로깅 추가

**검증:**
```javascript
// 브라우저 콘솔에서
logger.info('Test log')
logger.error('Test error', new Error('Test'))

// 서버 로그 확인
tail -f data/logs/app.log | grep "frontend"
```

### Phase 5: 로그 뷰어 UI (1주)

**목표:** 관리자 로그 조회 기능

- [ ] `app/api/logs.py` 구현
- [ ] `src/api/logs.js` 클라이언트 구현
- [ ] `src/views/Logs.vue` 뷰어 UI 구현
- [ ] 라우터에 `/logs` 경로 추가
- [ ] Settings.vue에 "로그" 메뉴 추가

**검증:**
- 관리자 로그인 후 `/logs` 접속
- 로그 타입별 조회 테스트
- 검색/필터링 테스트
- 다운로드 기능 테스트

### Phase 6: 고도화 (선택사항)

**추가 기능:**
- [ ] 실시간 로그 스트리밍 (WebSocket)
- [ ] 로그 분석 대시보드
- [ ] 알림 시스템 (Critical 에러 발생 시)
- [ ] Elasticsearch 통합 (대용량)
- [ ] Grafana 통합 (시각화)

---

## 예상 효과

### 1. 운영 효율성 향상

**Before:**
```
사용자: "제품 목록이 안 보여요"
개발자: "음... 서버 로그를 봐야 하는데... print()로 출력한 게 어디 갔지?"
→ 디버깅 시간: 2-4시간
```

**After:**
```
사용자: "제품 목록이 안 보여요"
개발자: 로그 뷰어에서 검색 → 1분 내 원인 파악
→ 디버깅 시간: 5-10분
```

**절감 효과:** 디버깅 시간 80% 단축

### 2. 성능 최적화 근거 확보

**슬로우 쿼리 자동 감지:**
```
[WARNING] Slow query detected (2.341s):
SELECT * FROM products WHERE category = 'Graphics' ORDER BY created_at DESC
```

→ 인덱스 추가, 쿼리 최적화 결정 근거

### 3. 사용자 행동 분석

**액션 로그 수집:**
```json
{
  "action": "download_version",
  "product_id": 123,
  "version_id": 456,
  "user_id": 1,
  "timestamp": "2026-01-03T10:30:00Z"
}
```

→ 인기 소프트웨어 파악, UI/UX 개선 인사이트

### 4. 보안 감사 추적

**접근 로그:**
```json
{
  "method": "POST",
  "url": "/api/products/123",
  "user_id": 5,
  "ip_address": "192.168.1.100",
  "status_code": 403
}
```

→ 비정상 접근 패턴 감지

### 5. 정량적 효과

| 항목 | Before | After | 개선율 |
|------|--------|-------|--------|
| 디버깅 시간 | 2-4시간 | 5-10분 | **80%↓** |
| 에러 발견 | 사용자 신고 후 | 실시간 감지 | **100%↑** |
| 성능 병목 파악 | 추측 | 데이터 기반 | **정량화** |
| 로그 보관 | 없음 | 30일 | **+30일** |
| 로그 검색 | 불가능 | 1초 이내 | **즉시** |

---

## 예상 비용

### 저장 공간

**일일 로그 예상 크기:**
- 애플리케이션 로그: ~50MB/일
- 에러 로그: ~10MB/일
- 접근 로그: ~100MB/일
- PostgreSQL 로그: ~20MB/일

**총계:** ~180MB/일 × 30일 = **5.4GB/월**

### 추가 의존성

```
# requirements.txt (이미 있음)
# logging은 Python 표준 라이브러리이므로 추가 설치 불필요
```

---

## 참고 자료

### Python Logging
- [Python Logging HOWTO](https://docs.python.org/3/howto/logging.html)
- [FastAPI Logging](https://fastapi.tiangolo.com/tutorial/handling-errors/#custom-exception-handlers)

### SQLAlchemy Logging
- [SQLAlchemy Engine Events](https://docs.sqlalchemy.org/en/20/core/events.html#sqlalchemy.events.PoolEvents)

### PostgreSQL Logging
- [PostgreSQL Logging Documentation](https://www.postgresql.org/docs/current/runtime-config-logging.html)

### Frontend Logging
- [Sentry.io](https://sentry.io/) - 프로덕션 에러 추적
- [LogRocket](https://logrocket.com/) - 세션 리플레이

---

## 결론

**로깅 시스템은 애플리케이션의 "블랙박스"입니다.**

현재 MyApp Store는 228개의 print() 문으로 임시 로깅을 하고 있지만, 체계적인 로깅 시스템 구축으로:

✅ **디버깅 시간 80% 단축**
✅ **에러 실시간 감지**
✅ **성능 최적화 근거 확보**
✅ **보안 감사 추적 가능**
✅ **운영 효율성 대폭 향상**

**6주 로드맵으로 완벽한 로깅 시스템을 구축할 수 있습니다!** 🚀
