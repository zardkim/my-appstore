from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class FilenameViolation(Base):
    """파일명 규칙 위반 항목"""
    __tablename__ = "filename_violations"

    id = Column(Integer, primary_key=True, index=True)
    folder_path = Column(String(500), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    violation_type = Column(String(50), nullable=False)  # underscore_overuse, bracket_usage, version_format, etc.
    violation_details = Column(Text, nullable=True)
    suggestion = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())
    is_resolved = Column(Boolean, default=False)

    # 매칭된 Product/Version 정보 (재스캔 시 중복 방지용)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True)
    version_id = Column(Integer, ForeignKey("versions.id", ondelete="SET NULL"), nullable=True, index=True)

    # Relationships
    product = relationship("Product", foreign_keys=[product_id])
    version = relationship("Version", foreign_keys=[version_id])
