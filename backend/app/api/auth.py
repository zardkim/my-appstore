from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel
import logging
logger = logging.getLogger(__name__)


from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserResponse
from app.core.security import verify_password, create_access_token, get_password_hash
from app.dependencies import get_current_user
from app.config import settings

router = APIRouter()


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """User login endpoint"""
    logger.debug(f"LOGIN] 로그인 시도 - Username: {form_data.username}")

    user = db.query(User).filter(User.username == form_data.username).first()

    if not user:
        logger.debug(f"LOGIN] 사용자를 찾을 수 없음: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.debug(f"LOGIN] 사용자 찾음: {user.username}, Role: {user.role.value}")

    password_valid = verify_password(form_data.password, user.password_hash)
    logger.debug(f"LOGIN] 비밀번호 검증 결과: {password_valid}")

    if not password_valid:
        logger.debug(f"LOGIN] 비밀번호 불일치")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/check-setup")
async def check_setup(db: Session = Depends(get_db)):
    """
    Check if initial setup is needed
    Returns True if no users exist in the system
    """
    user_count = db.query(User).count()
    return {"needs_setup": user_count == 0}


@router.post("/setup", response_model=UserResponse)
async def setup(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Initial setup endpoint - creates first admin user
    Only works if no users exist
    """
    user_count = db.query(User).count()
    if user_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Setup already completed"
        )

    # Validate password length
    if len(user_data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )

    # Create admin user
    new_user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        role=UserRole.admin
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password
    Requires authentication
    """
    # Validate new password length
    if len(request.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )

    # Verify current password
    if not verify_password(request.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )

    # Update password
    current_user.password_hash = get_password_hash(request.new_password)
    db.commit()

    return {"message": "Password changed successfully"}
