from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import secrets
import string


class ShareLink(Base):
    __tablename__ = "share_links"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(64), unique=True, nullable=False, index=True)
    password = Column(String(20), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    used_by_ip = Column(String(45), nullable=True)
    password_fail_count = Column(Integer, default=0)
    note = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    product = relationship("Product", foreign_keys=[product_id])
    creator = relationship("User", foreign_keys=[created_by])

    @staticmethod
    def generate_token():
        """Generate a secure random URL token (64 chars)"""
        return secrets.token_urlsafe(48)

    @staticmethod
    def generate_password(length=8):
        """Generate a random password (uppercase + lowercase + digits, no special chars)"""
        alphabet = string.ascii_letters + string.digits
        while True:
            password = ''.join(secrets.choice(alphabet) for _ in range(length))
            # Ensure at least one uppercase, one lowercase, one digit
            has_upper = any(c.isupper() for c in password)
            has_lower = any(c.islower() for c in password)
            has_digit = any(c.isdigit() for c in password)
            if has_upper and has_lower and has_digit:
                return password
