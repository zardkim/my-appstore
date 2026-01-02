from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean
from sqlalchemy.sql import func
from app.database import Base


class ScanHistory(Base):
    """
    스캔 이력 추적
    """
    __tablename__ = "scan_history"

    id = Column(Integer, primary_key=True, index=True)
    scan_type = Column(String, nullable=False)  # 'manual' or 'scheduled'
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, nullable=False)  # 'running', 'completed', 'failed'

    # 스캔 결과
    new_products = Column(Integer, default=0)
    new_versions = Column(Integer, default=0)
    updated_products = Column(Integer, default=0)
    ai_generated = Column(Integer, default=0)
    icons_cached = Column(Integer, default=0)

    # 스캔 경로 및 설정
    scanned_paths = Column(JSON)  # List of paths
    use_ai = Column(Boolean, default=True)

    # 에러 정보
    errors = Column(JSON)  # List of error messages
    error_message = Column(String, nullable=True)  # 전체 실패 시 에러 메시지
