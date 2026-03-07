"""
활동 로그 기록 헬퍼
"""
import json
import logging
from typing import Optional, Any
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def log_activity(
    db: Session,
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[int] = None,
    resource_name: Optional[str] = None,
    user_id: Optional[int] = None,
    username: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[Any] = None,
):
    """
    활동 로그 기록

    Args:
        db: DB 세션
        action: 동작 (download, scan, ai_search, post_create, post_update, post_delete,
                       product_create, product_update, product_delete, user_login)
        resource_type: 리소스 유형 (product, post, scan_item, version)
        resource_id: 리소스 ID
        resource_name: 리소스 이름
        user_id: 사용자 ID
        username: 사용자명
        ip_address: IP 주소
        details: 추가 정보 (dict)
    """
    try:
        from app.models.activity_log import ActivityLog
        log = ActivityLog(
            user_id=user_id,
            username=username,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            ip_address=ip_address,
            details=json.dumps(details, ensure_ascii=False) if details else None,
        )
        db.add(log)
        db.commit()
    except Exception as e:
        logger.warning(f"Failed to log activity [{action}]: {e}")
        try:
            db.rollback()
        except Exception:
            pass


def get_client_ip(request) -> Optional[str]:
    """요청에서 클라이언트 IP 추출"""
    if request is None:
        return None
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if hasattr(request, 'client') and request.client:
        return request.client.host
    return None
