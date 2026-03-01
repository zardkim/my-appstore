from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import Any
import json
import io
from datetime import datetime, timezone

from app.database import get_db
from app.models.product import Product
from app.models.version import Version
from app.models.setting import Setting
from app.dependencies import get_current_admin_user

router = APIRouter()


def _dt_to_str(val):
    """Convert datetime to ISO string for JSON serialization."""
    if val is None:
        return None
    if hasattr(val, 'isoformat'):
        return val.isoformat()
    return str(val)


@router.get("/export")
async def export_backup(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user)
):
    """
    전체 데이터 백업 (관리자 전용)
    - products 메타데이터 (파일 제외)
    - versions 메타데이터
    - settings
    """
    # Products
    products = db.query(Product).all()
    products_data = []
    for p in products:
        versions = db.query(Version).filter(Version.product_id == p.id).all()
        versions_data = [
            {
                "version_name": v.version_name,
                "file_name": v.file_name,
                "file_path": v.file_path,
                "file_size": v.file_size,
                "is_portable": v.is_portable,
                "release_date": _dt_to_str(v.release_date),
            }
            for v in versions
        ]
        products_data.append({
            "folder_path": p.folder_path,
            "title": p.title,
            "subtitle": p.subtitle,
            "description": p.description,
            "vendor": p.vendor,
            "icon_url": p.icon_url,
            "category": p.category,
            "is_portable": p.is_portable,
            "official_website": p.official_website,
            "license_type": p.license_type,
            "platform": p.platform,
            "detailed_description": p.detailed_description,
            "features": p.features,
            "system_requirements": p.system_requirements,
            "supported_formats": p.supported_formats,
            "installation_info": p.installation_info,
            "release_notes": p.release_notes,
            "release_date": p.release_date,
            "installation_guide": p.installation_guide,
            "patch_links": p.patch_links,
            "versions": versions_data,
        })

    # Settings
    settings_rows = db.query(Setting).all()
    # API 키 등 민감 정보는 제외
    sensitive_keys = {"ai_api_key", "openai_api_key", "gemini_api_key"}
    settings_data = [
        {"key": s.key, "value": s.value, "description": s.description}
        for s in settings_rows
        if s.key not in sensitive_keys
    ]

    backup = {
        "backup_version": "1.0",
        "backup_date": datetime.now(timezone.utc).isoformat(),
        "products_count": len(products_data),
        "settings_count": len(settings_data),
        "products": products_data,
        "settings": settings_data,
    }

    content = json.dumps(backup, ensure_ascii=False, indent=2)
    filename = f"myappstore_backup_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"

    return StreamingResponse(
        io.BytesIO(content.encode("utf-8")),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.post("/restore")
async def restore_backup(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user)
):
    """
    백업 파일에서 데이터 복원 (관리자 전용)

    복원 정책:
    - Settings: key 기준 upsert (민감 키 제외)
    - Products: folder_path 기준으로 기존 레코드 업데이트 (없으면 스킵)
    - Versions: 기존 레코드 건드리지 않음 (파일 경로 의존성 있음)
    """
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="JSON 파일만 업로드 가능합니다.")

    raw = await file.read()
    try:
        backup = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="유효하지 않은 JSON 파일입니다.")

    if backup.get("backup_version") != "1.0":
        raise HTTPException(status_code=400, detail="지원하지 않는 백업 파일 형식입니다.")

    restored_settings = 0
    restored_products = 0
    skipped_products = 0

    # Settings 복원
    sensitive_keys = {"ai_api_key", "openai_api_key", "gemini_api_key"}
    for s in backup.get("settings", []):
        if s["key"] in sensitive_keys:
            continue
        existing = db.query(Setting).filter(Setting.key == s["key"]).first()
        if existing:
            existing.value = s["value"]
        else:
            db.add(Setting(key=s["key"], value=s["value"], description=s.get("description")))
        restored_settings += 1

    # Products 복원 (folder_path 기준 메타데이터 업데이트)
    for p in backup.get("products", []):
        existing = db.query(Product).filter(Product.folder_path == p["folder_path"]).first()
        if not existing:
            skipped_products += 1
            continue

        # 메타데이터만 업데이트
        fields = [
            "title", "subtitle", "description", "vendor", "icon_url", "category",
            "is_portable", "official_website", "license_type", "platform",
            "detailed_description", "features", "system_requirements",
            "supported_formats", "installation_info", "release_notes",
            "release_date", "installation_guide", "patch_links",
        ]
        for field in fields:
            if field in p and p[field] is not None:
                setattr(existing, field, p[field])

        restored_products += 1

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"복원 중 오류 발생: {str(e)}")

    return {
        "success": True,
        "restored_settings": restored_settings,
        "restored_products": restored_products,
        "skipped_products": skipped_products,
        "message": f"설정 {restored_settings}개, 제품 메타데이터 {restored_products}개 복원 완료. (스킵: {skipped_products}개)"
    }
