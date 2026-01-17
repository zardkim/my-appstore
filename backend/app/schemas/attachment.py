from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AttachmentBase(BaseModel):
    note: Optional[str] = None
    type: str = "patch"  # manual, crack, patch, etc.


class AttachmentCreate(AttachmentBase):
    product_id: int
    file_path: str


class AttachmentUpdate(BaseModel):
    note: Optional[str] = None


class Attachment(AttachmentBase):
    id: int
    product_id: int
    file_path: str
    file_name: str
    file_size: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
