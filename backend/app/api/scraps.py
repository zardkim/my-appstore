from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.scrap import Scrap
from ..schemas import scrap as scrap_schema
from ..dependencies import get_current_user

router = APIRouter(tags=["scraps"])


@router.get("/", response_model=List[scrap_schema.Scrap])
async def get_my_scraps(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """현재 사용자의 스크랩 목록 조회"""
    scraps = db.query(Scrap).filter(
        Scrap.user_id == current_user.id
    ).order_by(Scrap.created_at.desc()).all()

    return scraps


@router.post("/{post_id}")
async def add_scrap(
    post_id: str,
    post_title: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """스크랩 추가"""
    # 이미 스크랩에 있는지 확인
    existing = db.query(Scrap).filter(
        Scrap.user_id == current_user.id,
        Scrap.post_id == post_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Already in scraps")

    # 스크랩 추가
    scrap = Scrap(
        user_id=current_user.id,
        post_id=post_id,
        post_title=post_title
    )
    db.add(scrap)
    db.commit()
    db.refresh(scrap)

    return {"message": "Added to scraps", "id": scrap.id}


@router.delete("/{post_id}")
async def remove_scrap(
    post_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """스크랩 제거"""
    scrap = db.query(Scrap).filter(
        Scrap.user_id == current_user.id,
        Scrap.post_id == post_id
    ).first()

    if not scrap:
        raise HTTPException(status_code=404, detail="Scrap not found")

    db.delete(scrap)
    db.commit()

    return {"message": "Removed from scraps"}


@router.get("/check/{post_id}")
async def check_scrap(
    post_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """특정 게시글이 스크랩에 있는지 확인"""
    scrap = db.query(Scrap).filter(
        Scrap.user_id == current_user.id,
        Scrap.post_id == post_id
    ).first()

    return {"is_scraped": scrap is not None}
