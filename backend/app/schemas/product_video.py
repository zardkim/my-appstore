from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProductVideoBase(BaseModel):
    title: str = ''
    description: Optional[str] = None
    sort_order: int = 0


class ProductVideoCreate(ProductVideoBase):
    product_id: int
    file_path: str
    file_name: str
    file_size: int = 0
    mime_type: str = 'video/mp4'
    source: str = 'upload'


class ProductVideoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None


class ProductVideo(ProductVideoBase):
    id: int
    product_id: int
    file_path: str
    file_name: str
    file_size: int
    mime_type: str
    source: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
