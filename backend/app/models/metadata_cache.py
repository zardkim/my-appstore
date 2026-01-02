"""
메타데이터 캐시 모델

동일한 소프트웨어에 대한 메타데이터를 캐시하여 중복 AI API 호출 방지
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from datetime import datetime
from app.database import Base


class MetadataCache(Base):
    """메타데이터 캐시"""
    __tablename__ = "metadata_cache"

    id = Column(Integer, primary_key=True, index=True)

    # 정규화된 소프트웨어 이름 (검색 키)
    software_name = Column(String, unique=True, index=True, nullable=False)

    # 캐시된 메타데이터 (JSON)
    metadata_json = Column(JSON, nullable=False)

    # 정확도 점수 (0.0 ~ 1.0)
    confidence_score = Column(Float, nullable=False, default=0.0)

    # 메타데이터 출처 ("ai", "manual", "web")
    source = Column(String, nullable=False, default="ai")

    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 재사용 횟수 (캐시 히트 카운트)
    hit_count = Column(Integer, default=0, nullable=False)

    def __repr__(self):
        return f"<MetadataCache(name='{self.software_name}', score={self.confidence_score}, hits={self.hit_count})>"
