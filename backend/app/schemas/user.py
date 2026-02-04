from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str
    email: Optional[str] = None
    role: Optional[str] = "user"


class UserRegister(BaseModel):
    """Schema for public registration"""
    username: str
    password: str
    email: str


class UserResponse(UserBase):
    id: int
    email: Optional[str] = None
    role: str
    created_at: datetime

    class Config:
        from_attributes = True
