from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
import logging
import time

logger = logging.getLogger(__name__)

# 슬로우 쿼리 임계값 (초)
SLOW_QUERY_THRESHOLD = 1.0

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=False,  # SQLAlchemy 기본 echo 비활성화 (우리가 직접 로깅)
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# ==================== SQLAlchemy 이벤트 리스너 ====================

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """쿼리 실행 전: 시작 시간 기록"""
    conn.info.setdefault('query_start_time', []).append(time.time())

    # 쿼리 로깅 (DEBUG 레벨)
    logger.debug(f"SQL Query: {statement[:200]}...")


@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """쿼리 실행 후: 실행 시간 측정 및 슬로우 쿼리 감지"""
    total_time = time.time() - conn.info['query_start_time'].pop(-1)

    if total_time > SLOW_QUERY_THRESHOLD:
        # 슬로우 쿼리 경고
        logger.warning(
            f"SLOW QUERY detected ({total_time:.3f}s): {statement}",
            extra={
                "query": statement,
                "parameters": parameters,
                "execution_time": total_time,
                "threshold": SLOW_QUERY_THRESHOLD
            }
        )
    else:
        # 정상 쿼리 디버그 로그
        logger.debug(f"Query completed in {total_time:.3f}s")


@event.listens_for(Engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """커넥션 풀: 새 연결 생성"""
    logger.debug("Database connection established")


@event.listens_for(Engine, "close")
def receive_close(dbapi_conn, connection_record):
    """커넥션 풀: 연결 종료"""
    logger.debug("Database connection closed")


@event.listens_for(Engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """커넥션 풀: 체크아웃"""
    logger.debug("Connection checked out from pool")


@event.listens_for(Engine, "checkin")
def receive_checkin(dbapi_conn, connection_record):
    """커넥션 풀: 체크인"""
    logger.debug("Connection returned to pool")


# 초기화 로그
logger.info(f"Database engine initialized: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'localhost'}")
logger.info(f"Connection pool: size={engine.pool.size()}, max_overflow={engine.pool._max_overflow}")
logger.info(f"Slow query threshold: {SLOW_QUERY_THRESHOLD}s")


def get_db():
    """Database dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
