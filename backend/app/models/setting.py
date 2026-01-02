from sqlalchemy import Column, Integer, String, Text
from app.database import Base


class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False, index=True)
    value = Column(Text)
    description = Column(String)

    # Common settings:
    # - scan_paths: JSON array of paths to scan
    # - ai_api_key: OpenAI API key
    # - cron_schedule: Cron expression for auto-scan
