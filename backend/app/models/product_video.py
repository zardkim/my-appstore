from sqlalchemy import Column, Integer, String, Text, BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class ProductVideo(Base):
    __tablename__ = "product_videos"

    id          = Column(Integer, primary_key=True, index=True)
    product_id  = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    title       = Column(String(200), nullable=False, default='')
    description = Column(Text, nullable=True)
    file_path   = Column(String, nullable=False)
    file_name   = Column(String, nullable=False)
    file_size   = Column(BigInteger, default=0)
    mime_type   = Column(String, default='video/mp4')
    sort_order  = Column(Integer, default=0)
    source      = Column(String, default='upload')   # 'upload' | 'scan'
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="videos")
