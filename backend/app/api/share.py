from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import logging

from app.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.version import Version
from app.models.share_link import ShareLink
from app.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

MAX_ACTIVE_LINKS_PER_USER = 20
MAX_EXPIRE_DAYS = 5
MAX_PASSWORD_FAILURES = 5


def _format_link(link: ShareLink, include_password: bool = False) -> dict:
    now = datetime.utcnow()
    is_expired = link.expires_at.replace(tzinfo=None) < now if link.expires_at else True
    result = {
        "id": link.id,
        "token": link.token,
        "product_id": link.product_id,
        "product_title": link.product.title if link.product else None,
        "product_icon": link.product.icon_url if link.product else None,
        "expires_at": link.expires_at.isoformat() if link.expires_at else None,
        "is_used": link.is_used,
        "is_expired": is_expired,
        "is_active": not link.is_used and not is_expired,
        "created_at": link.created_at.isoformat() if link.created_at else None,
        "note": link.note,
    }
    if include_password:
        result["password"] = link.password
    return result


@router.post("/create")
async def create_share_link(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """공유링크 생성"""
    body = await request.json()
    product_id = body.get("product_id")
    expires_days = int(body.get("expires_days", 1))
    note = body.get("note", "")

    if not product_id:
        raise HTTPException(status_code=400, detail="product_id가 필요합니다.")

    if expires_days < 1 or expires_days > MAX_EXPIRE_DAYS:
        raise HTTPException(status_code=400, detail=f"공유 기간은 1~{MAX_EXPIRE_DAYS}일 사이여야 합니다.")

    # 제품 존재 여부 확인
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="제품을 찾을 수 없습니다.")

    # 활성 링크 수 제한 확인
    now = datetime.utcnow()
    active_count = db.query(ShareLink).filter(
        ShareLink.created_by == current_user.id,
        ShareLink.is_used == False,
        ShareLink.expires_at > now
    ).count()

    if active_count >= MAX_ACTIVE_LINKS_PER_USER:
        raise HTTPException(
            status_code=400,
            detail=f"활성 공유링크는 최대 {MAX_ACTIVE_LINKS_PER_USER}개까지만 생성할 수 있습니다."
        )

    # 링크 생성
    token = ShareLink.generate_token()
    password = ShareLink.generate_password()
    expires_at = now + timedelta(days=expires_days)

    link = ShareLink(
        token=token,
        password=password,
        product_id=product_id,
        created_by=current_user.id,
        expires_at=expires_at,
        note=note[:200] if note else None,
    )

    db.add(link)
    db.commit()
    db.refresh(link)

    # 호스트 URL 구성 (역방향 프록시 헤더 우선 사용)
    x_forwarded_proto = request.headers.get("x-forwarded-proto", "")
    scheme = x_forwarded_proto.split(",")[0].strip() if x_forwarded_proto else request.url.scheme

    x_forwarded_host = request.headers.get("x-forwarded-host", "")
    host = (x_forwarded_host.split(",")[0].strip()
            if x_forwarded_host
            else request.headers.get("host") or request.url.netloc)

    share_url = f"{scheme}://{host}/share/{token}"

    logger.info(f"Share link created: token={token[:8]}... product_id={product_id} by user={current_user.username}")

    return {
        "id": link.id,
        "token": token,
        "password": password,
        "share_url": share_url,
        "expires_at": link.expires_at.isoformat(),
        "product_title": product.title,
        "note": link.note,
    }


@router.get("/my-links")
async def get_my_share_links(
    page: int = 1,
    limit: int = 20,
    status_filter: Optional[str] = None,  # "active" | "expired" | "used"
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """내 공유링크 목록 조회"""
    query = db.query(ShareLink).filter(ShareLink.created_by == current_user.id)
    now = datetime.utcnow()

    if status_filter == "used":
        query = query.filter(ShareLink.is_used == True)
    elif status_filter == "expired":
        query = query.filter(ShareLink.is_used == False, ShareLink.expires_at <= now)
    elif status_filter == "active":
        query = query.filter(ShareLink.is_used == False, ShareLink.expires_at > now)

    total = query.count()
    links = query.order_by(ShareLink.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    return {
        "links": [_format_link(link) for link in links],
        "total": total,
        "page": page,
        "limit": limit,
    }


@router.delete("/{link_id}")
async def delete_share_link(
    link_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """공유링크 삭제"""
    link = db.query(ShareLink).filter(ShareLink.id == link_id).first()

    if not link:
        raise HTTPException(status_code=404, detail="공유링크를 찾을 수 없습니다.")

    # 본인 링크 또는 관리자만 삭제 가능
    if link.created_by != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="삭제 권한이 없습니다.")

    db.delete(link)
    db.commit()

    return {"message": "공유링크가 삭제되었습니다."}


@router.get("/view/{token}")
async def view_share_page(token: str, db: Session = Depends(get_db)):
    """공유 페이지 정보 조회 (비인증)"""
    link = db.query(ShareLink).filter(ShareLink.token == token).first()

    if not link:
        raise HTTPException(status_code=404, detail="공유링크를 찾을 수 없습니다.")

    now = datetime.utcnow()
    is_expired = link.expires_at.replace(tzinfo=None) < now

    return {
        "product_title": link.product.title if link.product else None,
        "product_icon": link.product.icon_url if link.product else None,
        "product_description": link.product.description if link.product else None,
        "expires_at": link.expires_at.isoformat() if link.expires_at else None,
        "is_expired": is_expired,
        "is_used": link.is_used,
        "requires_password": True,
    }


@router.post("/access/{token}")
async def access_share_link(
    token: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """공유링크 비밀번호 인증 및 제품 정보 반환 (비인증, 1회성)"""
    body = await request.json()
    password = body.get("password", "")

    link = db.query(ShareLink).filter(ShareLink.token == token).first()

    if not link:
        raise HTTPException(status_code=404, detail="공유링크를 찾을 수 없습니다.")

    # 이미 사용됨
    if link.is_used:
        return {"success": False, "error": "already_used"}

    # 만료 확인
    now = datetime.utcnow()
    if link.expires_at.replace(tzinfo=None) < now:
        return {"success": False, "error": "expired"}

    # 비밀번호 실패 횟수 초과
    if link.password_fail_count >= MAX_PASSWORD_FAILURES:
        link.is_used = True  # 보안을 위해 만료 처리
        db.commit()
        return {"success": False, "error": "locked"}

    # 비밀번호 검증
    if link.password != password:
        link.password_fail_count += 1
        db.commit()
        remaining = MAX_PASSWORD_FAILURES - link.password_fail_count
        return {
            "success": False,
            "error": "invalid_password",
            "remaining_attempts": remaining,
        }

    # 인증 성공 - 1회성 처리
    client_ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown")
    link.is_used = True
    link.used_at = now
    link.used_by_ip = client_ip[:45] if client_ip else None
    db.commit()

    # 제품 상세 정보 반환
    product = link.product
    versions = db.query(Version).filter(Version.product_id == product.id).order_by(Version.release_date.desc()).all()

    version_list = []
    for v in versions:
        version_list.append({
            "id": v.id,
            "version_name": v.version_name,
            "file_name": v.file_name,
            "file_size": v.file_size,
            "release_date": v.release_date.isoformat() if v.release_date else None,
            "is_portable": v.is_portable,
        })

    logger.info(f"Share link accessed: token={token[:8]}... ip={client_ip}")

    return {
        "success": True,
        "product": {
            "id": product.id,
            "title": product.title,
            "subtitle": product.subtitle,
            "description": product.description,
            "vendor": product.vendor,
            "icon_url": product.icon_url,
            "category": product.category,
            "license_type": product.license_type,
            "platform": product.platform,
            "official_website": product.official_website,
        },
        "versions": version_list,
    }


@router.get("/admin/all")
async def admin_get_all_links(
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """전체 공유링크 목록 (관리자 전용)"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")

    total = db.query(ShareLink).count()
    links = db.query(ShareLink).order_by(ShareLink.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    result = []
    for link in links:
        item = _format_link(link)
        item["creator_username"] = link.creator.username if link.creator else None
        result.append(item)

    return {
        "links": result,
        "total": total,
        "page": page,
        "limit": limit,
    }
