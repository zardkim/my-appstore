from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel
import logging
import json
from pathlib import Path
import re
logger = logging.getLogger(__name__)


from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserResponse, UserRegister
from app.core.security import verify_password, create_access_token, get_password_hash
from app.dependencies import get_current_user
from app.config import settings

router = APIRouter()


def get_registration_status() -> bool:
    """Check if registration is open from config.json"""
    try:
        config_file = Path(settings.CONFIG_DATA_DIR) / "config.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('general', {}).get('registrationOpen', False)
    except Exception as e:
        logger.error(f"Error reading config: {e}")
    return False


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


@router.get("/registration-status")
async def check_registration_status():
    """
    Check if registration is open
    """
    return {"registration_open": get_registration_status()}


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Public registration endpoint
    Only works if registration is open in config
    """
    # Check if registration is open
    if not get_registration_status():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registration is currently closed"
        )

    # Validate username (alphanumeric, 3-20 chars)
    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be 3-20 characters, alphanumeric and underscore only"
        )

    # Validate password length
    if len(user_data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )

    # Validate email format
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )

    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        role=UserRole.user
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
