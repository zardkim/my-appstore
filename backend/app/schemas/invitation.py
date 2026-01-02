from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class InvitationCreate(BaseModel):
    email: EmailStr


class InvitationResponse(BaseModel):
    id: int
    email: str
    code: str
    expires_at: datetime
    used: bool
    used_at: Optional[datetime]
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True


class InvitationRegister(BaseModel):
    code: str
    username: str
    password: str


class InvitationVerify(BaseModel):
    email: str
    is_valid: bool
    expires_at: Optional[datetime]
