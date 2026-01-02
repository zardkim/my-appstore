from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class PostBase(BaseModel):
    category: str
    title: str
    content: str
    tags: Optional[str] = None
    is_notice: bool = False


class PostCreate(PostBase):
    images: Optional[List[str]] = None
    attachments: Optional[List[dict]] = None


class PostUpdate(BaseModel):
    category: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[str] = None
    is_notice: Optional[bool] = None
    images: Optional[List[str]] = None
    attachments: Optional[List[dict]] = None


class PostResponse(PostBase):
    id: int
    author_id: int
    author_username: str  # 작성자 이름
    views: int
    images: Optional[List[str]] = None
    attachments: Optional[List[dict]] = None
    comments_count: int = 0  # 댓글 수 (나중에 구현)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
