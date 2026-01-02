from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Scrap(Base):
    __tablename__ = "scraps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(String, nullable=False)  # 팁&테크 게시글 ID (현재는 임시 ID)
    post_title = Column(String, nullable=True)  # 게시글 제목 저장 (빠른 조회용)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="scraps")
