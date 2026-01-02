from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    # 기본 정보 (AI 생성)
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    subtitle = Column(String)  # 부제목 (예: 한글명)
    description = Column(Text)  # 간단한 설명 (AI)
    vendor = Column(String)
    icon_url = Column(String)
    category = Column(String, index=True)
    folder_path = Column(String, unique=True, nullable=False)
    is_portable = Column(Boolean, default=False)  # 포터블 여부

    # 추가 기본 정보 (웹 크롤링)
    official_website = Column(String)  # 공식 웹사이트
    license_type = Column(String)  # 라이선스 종류 (Free, Trial, Commercial 등)
    platform = Column(String)  # 플랫폼 (Windows, macOS, Linux 등)

    # 상세 정보 (웹 크롤링)
    detailed_description = Column(Text)  # 상세 설명
    features = Column(JSON)  # 주요 기능 목록 ["기능1", "기능2", ...]
    system_requirements = Column(JSON)  # 시스템 요구사항 {"os": "...", "cpu": "...", "ram": "..."}
    supported_formats = Column(JSON)  # 지원 파일 포맷 {"images": ["jpg", "png"], "videos": [...]}

    # 릴리즈 정보
    release_notes = Column(Text)  # 릴리즈 노트
    release_date = Column(String)  # 릴리즈 날짜

    # 크롤링 메타데이터
    crawled_from = Column(JSON)  # 크롤링 소스 {"softpedia": true, "github": true, ...}
    last_crawled_at = Column(DateTime(timezone=True))  # 마지막 크롤링 시간
    screenshots = Column(JSON, nullable=True)  # 스크린샷 목록 [{"type": "local|external", "url": "..."}, ...]

    # 설치 방법 (사용자 작성)
    installation_guide = Column(Text)  # 설치 방법 (HTML 형식)

    # Relationships
    versions = relationship("Version", back_populates="product", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="product", cascade="all, delete-orphan")
