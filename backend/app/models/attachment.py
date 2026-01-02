from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    file_path = Column(String, nullable=False)
    note = Column(Text)
    type = Column(String)  # manual, crack, patch, etc.

    # Relationships
    product = relationship("Product", back_populates="attachments")
