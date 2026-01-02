from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User
from app.models.invitation import Invitation
from app.schemas.invitation import (
    InvitationCreate,
    InvitationResponse,
    InvitationRegister,
    InvitationVerify
)
from app.dependencies import get_current_admin_user
from app.core.security import get_password_hash
from app.core.email_sender import email_sender

router = APIRouter()


@router.post("/send", response_model=InvitationResponse)
async def send_invitation(
    invitation_data: InvitationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Send invitation email (admin only)"""
    # Check if email already has an active invitation
    existing = db.query(Invitation).filter(
        Invitation.email == invitation_data.email,
        Invitation.used == False,
        Invitation.expires_at > datetime.utcnow()
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="이미 활성화된 초대장이 있습니다."
        )

    # Check if user with this email already exists (using email as username)
    existing_user = db.query(User).filter(User.username == invitation_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="이미 등록된 이메일입니다."
        )

    # Create invitation
    code = Invitation.generate_code()
    expires_at = datetime.utcnow() + timedelta(days=7)

    new_invitation = Invitation(
        email=invitation_data.email,
        code=code,
        expires_at=expires_at,
        created_by=current_user.id
    )

    db.add(new_invitation)
    db.commit()
    db.refresh(new_invitation)

    # Send email
    email_sent = email_sender.send_invitation_email(invitation_data.email, code)

    if not email_sent:
        # Email failed but invitation is created
        # Admin can still manually share the code
        pass

    return new_invitation


@router.get("/verify/{code}", response_model=InvitationVerify)
async def verify_invitation(
    code: str,
    db: Session = Depends(get_db)
):
    """Verify invitation code"""
    invitation = db.query(Invitation).filter(Invitation.code == code).first()

    if not invitation:
        return InvitationVerify(
            email="",
            is_valid=False,
            expires_at=None
        )

    # Check if already used
    if invitation.used:
        return InvitationVerify(
            email=invitation.email,
            is_valid=False,
            expires_at=invitation.expires_at
        )

    # Check if expired
    if invitation.expires_at < datetime.utcnow():
        return InvitationVerify(
            email=invitation.email,
            is_valid=False,
            expires_at=invitation.expires_at
        )

    return InvitationVerify(
        email=invitation.email,
        is_valid=True,
        expires_at=invitation.expires_at
    )


@router.post("/register")
async def register_with_invitation(
    register_data: InvitationRegister,
    db: Session = Depends(get_db)
):
    """Register new user with invitation code"""
    # Validate password length
    if len(register_data.password) < 8:
        raise HTTPException(status_code=400, detail="비밀번호는 최소 8자 이상이어야 합니다.")

    # Find invitation
    invitation = db.query(Invitation).filter(Invitation.code == register_data.code).first()

    if not invitation:
        raise HTTPException(status_code=404, detail="초대 코드가 유효하지 않습니다.")

    # Check if already used
    if invitation.used:
        raise HTTPException(status_code=400, detail="이미 사용된 초대 코드입니다.")

    # Check if expired
    if invitation.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="만료된 초대 코드입니다.")

    # Check if username already exists
    existing = db.query(User).filter(User.username == register_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 사용중인 사용자명입니다.")

    # Create user
    new_user = User(
        username=register_data.username,
        password_hash=get_password_hash(register_data.password),
        role="user"
    )

    db.add(new_user)

    # Mark invitation as used
    invitation.used = True
    invitation.used_at = datetime.utcnow()

    db.commit()
    db.refresh(new_user)

    return {
        "message": "회원가입이 완료되었습니다.",
        "username": new_user.username
    }


@router.get("/", response_model=List[InvitationResponse])
async def get_invitations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get all invitations (admin only)"""
    invitations = db.query(Invitation).order_by(Invitation.created_at.desc()).all()
    return invitations


@router.delete("/{invitation_id}")
async def delete_invitation(
    invitation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete invitation (admin only)"""
    invitation = db.query(Invitation).filter(Invitation.id == invitation_id).first()

    if not invitation:
        raise HTTPException(status_code=404, detail="초대장을 찾을 수 없습니다.")

    db.delete(invitation)
    db.commit()

    return {"message": "초대장이 삭제되었습니다."}
