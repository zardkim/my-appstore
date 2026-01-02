from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserCreate
from app.dependencies import get_current_admin_user
from app.core.security import get_password_hash

router = APIRouter()


class PasswordChange(BaseModel):
    new_password: str


class UserStatusToggle(BaseModel):
    is_active: bool


@router.get("/", response_model=List[UserResponse])
async def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get all users (admin only)"""
    users = db.query(User).all()
    return users


@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create new user (admin only)"""
    # Validate password length
    if len(user_data.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")

    # Check if username already exists
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.patch("/{user_id}/password")
async def change_user_password(
    user_id: int,
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Change user password (admin only)"""
    # Validate password length
    if len(password_data.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role == "admin" and user.id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot change other admin's password")

    user.password_hash = get_password_hash(password_data.new_password)
    db.commit()

    return {"message": "Password changed successfully"}


@router.patch("/{user_id}/status")
async def toggle_user_status(
    user_id: int,
    status_data: UserStatusToggle,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Toggle user active status (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role == "admin":
        raise HTTPException(status_code=403, detail="Cannot change admin status")

    user.is_active = status_data.is_active
    db.commit()

    return {"message": "User status updated successfully", "is_active": user.is_active}


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}
