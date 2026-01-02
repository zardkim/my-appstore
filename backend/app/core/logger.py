"""
중앙화된 로깅 설정
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
import json
from typing import Optional

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


class ColoredFormatter(logging.Formatter):
    """컬러 출력을 위한 포맷터 (개발 환경용)"""

    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']

        record.levelname_colored = f"{log_color}{record.levelname}{reset}"
        record.name_colored = f"\033[34m{record.name}{reset}"  # Blue

        return super().format(record)


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

        # 컬러 포맷터 사용
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name_colored)s - %(levelname_colored)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    else:
        # 프로덕션 환경에서는 간단한 포맷
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
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

    # 외부 라이브러리 로그 레벨 조정 (노이즈 감소)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    # 초기화 완료 로그
    root_logger.info("=" * 50)
    root_logger.info("Logging system initialized")
    root_logger.info(f"Log directory: {log_dir}")
    root_logger.info(f"Log level: {settings.LOG_LEVEL}")
    root_logger.info(f"Environment: {settings.ENVIRONMENT}")
    root_logger.info("=" * 50)


def get_logger(name: str) -> logging.Logger:
    """
    로거 인스턴스 가져오기

    Args:
        name: 로거 이름 (일반적으로 __name__ 사용)

    Returns:
        logging.Logger: 로거 인스턴스

    Example:
        logger = get_logger(__name__)
        logger.info("Hello, World!")
    """
    return logging.getLogger(name)


def log_with_context(
    logger: logging.Logger,
    level: int,
    message: str,
    user_id: Optional[int] = None,
    request_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    **kwargs
):
    """
    컨텍스트 정보와 함께 로그 기록

    Args:
        logger: 로거 인스턴스
        level: 로그 레벨
        message: 로그 메시지
        user_id: 사용자 ID
        request_id: 요청 ID
        ip_address: IP 주소
        **kwargs: 추가 컨텍스트
    """
    extra = {}
    if user_id is not None:
        extra['user_id'] = user_id
    if request_id is not None:
        extra['request_id'] = request_id
    if ip_address is not None:
        extra['ip_address'] = ip_address

    extra.update(kwargs)

    logger.log(level, message, extra=extra)
