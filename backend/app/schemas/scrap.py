from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ScrapBase(BaseModel):
    post_id: str
    post_title: Optional[str] = None


class ScrapCreate(ScrapBase):
    pass


class Scrap(ScrapBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
