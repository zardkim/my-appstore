"""
활동 로그 API (Admin only)
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.dependencies import get_current_admin_user
from app.models.activity_log import ActivityLog

router = APIRouter()

ACTION_LABELS = {
    "download": "다운로드",
    "scan": "스캔",
    "ai_search": "AI검색",
    "post_create": "게시글 등록",
    "post_update": "게시글 수정",
    "post_delete": "게시글 삭제",
    "product_create": "스토어 등록",
    "product_update": "스토어 수정",
    "product_delete": "스토어 삭제",
    "user_login": "로그인",
    "version_create": "버전 추가",
    "version_delete": "버전 삭제",
    "scan_item_register": "스캔 아이템 등록",
    "scan_item_delete": "스캔 아이템 삭제",
}


@router.get("/activity-logs")
async def get_activity_logs(
    action: Optional[str] = None,
    username: Optional[str] = None,
    resource_type: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    skip: int = 0,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user),
):
    """활동 로그 조회 (관리자 전용)"""
    query = db.query(ActivityLog).order_by(ActivityLog.created_at.desc())

    if action:
        query = query.filter(ActivityLog.action == action)
    if username:
        query = query.filter(ActivityLog.username.ilike(f"%{username}%"))
    if resource_type:
        query = query.filter(ActivityLog.resource_type == resource_type)
    if date_from:
        try:
            dt_from = datetime.fromisoformat(date_from)
            query = query.filter(ActivityLog.created_at >= dt_from)
        except ValueError:
            pass
    if date_to:
        try:
            dt_to = datetime.fromisoformat(date_to)
            query = query.filter(ActivityLog.created_at <= dt_to)
        except ValueError:
            pass

    total = query.count()
    logs = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "logs": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "username": log.username or "익명",
                "action": log.action,
                "action_label": ACTION_LABELS.get(log.action, log.action),
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "resource_name": log.resource_name,
                "ip_address": log.ip_address,
                "details": log.details,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ],
        "action_labels": ACTION_LABELS,
    }


@router.delete("/activity-logs")
async def clear_activity_logs(
    days_older_than: int = Query(30, description="N일 이상 된 로그 삭제"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user),
):
    """오래된 활동 로그 삭제 (관리자 전용)"""
    from datetime import timedelta
    cutoff = datetime.utcnow() - timedelta(days=days_older_than)
    deleted = db.query(ActivityLog).filter(ActivityLog.created_at < cutoff).delete()
    db.commit()
    return {"deleted": deleted, "message": f"{deleted}개의 로그가 삭제되었습니다."}
