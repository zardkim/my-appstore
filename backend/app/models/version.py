from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Version(Base):
    __tablename__ = "versions"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    version_name = Column(String)
    file_name = Column(String, nullable=False)
    file_path = Column(String, unique=True, nullable=False)
    file_size = Column(BigInteger)
    release_date = Column(DateTime(timezone=True), server_default=func.now())
    is_portable = Column(Boolean, default=False)  # 포터블 여부

    # Relationships
    product = relationship("Product", back_populates="versions")
