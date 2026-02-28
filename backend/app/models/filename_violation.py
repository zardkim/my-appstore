from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class FilenameViolation(Base):
    """스캔된 파일 항목 (= ScanItem)

    파일 스캔 시 생성되며, 각 파일을 5가지 분류 중 하나로 자동 분류한다.
      - product       : 소프트웨어 설치 본체 (기본값)
      - patch         : 패치, 크랙, 키젠 등
      - language_pack : 언어팩, 번역팩
      - manual        : 메뉴얼, 설명서, 가이드
      - update        : 업데이트, 서비스팩
    """
    __tablename__ = "filename_violations"

    id = Column(Integer, primary_key=True, index=True)
    folder_path = Column(String(500), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)

    # 기존 스캔 관련 필드 (하위 호환 유지)
    violation_type = Column(String(50), nullable=False, default="scanned")
    violation_details = Column(Text, nullable=True)
    suggestion = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())
    is_resolved = Column(Boolean, default=False)

    # 분류 필드 (새로 추가)
    classification = Column(
        String(20),
        nullable=False,
        default="product",
        server_default="product"
    )
    # True: 자동 분류, False: 사용자가 수동으로 변경한 분류
    classification_auto = Column(Boolean, nullable=False, default=True, server_default="true")

    # 매칭된 Product/Version 정보 (재스캔 시 중복 방지용)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True)
    version_id = Column(Integer, ForeignKey("versions.id", ondelete="SET NULL"), nullable=True, index=True)

    # Relationships
    product = relationship("Product", foreign_keys=[product_id])
    version = relationship("Version", foreign_keys=[version_id])
