"""
불일치 항목 모델

정확도 90% 미만인 메타데이터를 별도 관리하여 수동 검토
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from datetime import datetime
from app.database import Base


class UnmatchedItem(Base):
    """불일치 항목 (정확도 < 90%)"""
    __tablename__ = "unmatched_items"

    id = Column(Integer, primary_key=True, index=True)

    # 파일 정보
    file_path = Column(String, unique=True, nullable=False)
    file_name = Column(String, nullable=False)
    folder_path = Column(String, nullable=False)

    # 파싱된 정보
    parsed_name = Column(String, nullable=True)
    parsed_version = Column(String, nullable=True)
    parsed_vendor = Column(String, nullable=True)

    # AI가 제안한 메타데이터 (참고용)
    suggested_metadata = Column(JSON, nullable=True)

    # 정확도 점수
    confidence_score = Column(Float, nullable=False, default=0.0)

    # 상태: pending (대기), approved (승인), manual (수동입력), ignored (무시)
    status = Column(String, default="pending", nullable=False, index=True)

    # 수동으로 입력된 메타데이터
    manual_metadata = Column(JSON, nullable=True)

    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    reviewed_at = Column(DateTime, nullable=True)

    # 검토자
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    def __repr__(self):
        return f"<UnmatchedItem(file='{self.file_name}', score={self.confidence_score}, status='{self.status}')>"
