from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    username = Column(String(100), nullable=True)
    action = Column(String(50), nullable=False, index=True)      # download, scan, ai_search, post_create, post_update, post_delete, product_create, product_update, product_delete, user_login
    resource_type = Column(String(50), nullable=True)            # product, post, scan_item, version
    resource_id = Column(Integer, nullable=True)
    resource_name = Column(String(500), nullable=True)
    ip_address = Column(String(50), nullable=True)
    details = Column(Text, nullable=True)                        # JSON 추가 정보
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
