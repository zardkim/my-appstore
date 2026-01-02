from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), nullable=False)  # tip, tech, tutorial, qna, news, notice
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(String(500), nullable=True)  # comma-separated
    is_notice = Column(Boolean, default=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    views = Column(Integer, default=0)
    images = Column(JSON, nullable=True)  # List of image paths in /static/eximage/
    attachments = Column(JSON, nullable=True)  # List of attachment file info
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    author = relationship("User", backref="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
