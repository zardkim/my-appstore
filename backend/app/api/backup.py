from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import json
import io
import os
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from app.database import get_db
from app.models.product import Product
from app.models.version import Version
from app.models.setting import Setting
from app.dependencies import get_current_admin_user
from app.config import settings

router = APIRouter()

# 백업에 포함할 데이터 폴더 목록 (라이브러리, DB, Redis, 로그 제외)
BACKUP_DATA_SUBDIRS = ["icons", "videos", "attachments", "screenshots", "eximage", "patches", "config"]
BACKUP_DATA_FILES = ["config.json", "scan_exclusions.txt"]

# 민감 설정 키 (백업 제외)
SENSITIVE_KEYS = {"ai_api_key", "openai_api_key", "gemini_api_key"}


def _dt_to_str(val):
    if val is None:
        return None
    if hasattr(val, 'isoformat'):
        return val.isoformat()
    return str(val)


def _build_db_snapshot(db: Session) -> dict:
    """DB 데이터를 dict로 직렬화"""
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

    settings_rows = db.query(Setting).all()
    settings_data = [
        {"key": s.key, "value": s.value, "description": s.description}
        for s in settings_rows
        if s.key not in SENSITIVE_KEYS
    ]

    return {
        "backup_version": "2.0",
        "backup_date": datetime.now(timezone.utc).isoformat(),
        "products_count": len(products_data),
        "settings_count": len(settings_data),
        "products": products_data,
        "settings": settings_data,
    }


@router.get("/export")
async def export_backup(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user)
):
    """
    전체 데이터 백업 ZIP (관리자 전용)
    - backup.json: products 메타데이터 + settings
    - data/: icons, videos, attachments, screenshots, eximage, patches, config
    """
    db_snapshot = _build_db_snapshot(db)
    data_root = Path(settings.CONFIG_DATA_DIR)

    # ZIP 파일을 메모리에 생성
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode='w', compression=zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
        # 1. backup.json 추가
        zf.writestr("backup.json", json.dumps(db_snapshot, ensure_ascii=False, indent=2))

        # 2. 개별 파일 추가
        for fname in BACKUP_DATA_FILES:
            fpath = data_root / fname
            if fpath.exists():
                zf.write(fpath, f"data/{fname}")

        # 3. 서브 디렉토리 추가
        for subdir in BACKUP_DATA_SUBDIRS:
            subdir_path = data_root / subdir
            if not subdir_path.exists():
                continue
            for file_path in subdir_path.rglob("*"):
                if file_path.is_file():
                    arcname = "data/" + str(file_path.relative_to(data_root))
                    zf.write(file_path, arcname)

    buf.seek(0)
    filename = f"myappstore_backup_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.zip"

    return StreamingResponse(
        buf,
        media_type="application/zip",
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
    - ZIP (v2.0): DB + 데이터 파일 복원
    - JSON (v1.0): DB만 복원 (하위 호환)
    """
    raw = await file.read()
    restored_files = 0

    if file.filename.endswith(".zip"):
        # ZIP 처리
        try:
            zf = zipfile.ZipFile(io.BytesIO(raw))
        except zipfile.BadZipFile:
            raise HTTPException(status_code=400, detail="유효하지 않은 ZIP 파일입니다.")

        try:
            backup_json = zf.read("backup.json").decode("utf-8")
            backup = json.loads(backup_json)
        except (KeyError, json.JSONDecodeError):
            raise HTTPException(status_code=400, detail="ZIP 내 backup.json을 읽을 수 없습니다.")

        if backup.get("backup_version") not in ("1.0", "2.0"):
            raise HTTPException(status_code=400, detail="지원하지 않는 백업 파일 형식입니다.")

        # 데이터 파일 복원
        data_root = Path(settings.CONFIG_DATA_DIR)
        for name in zf.namelist():
            if name.startswith("data/") and not name.endswith("/"):
                rel = name[len("data/"):]
                dest = data_root / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(zf.read(name))
                restored_files += 1

    elif file.filename.endswith(".json"):
        try:
            backup = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="유효하지 않은 JSON 파일입니다.")

        if backup.get("backup_version") not in ("1.0", "2.0"):
            raise HTTPException(status_code=400, detail="지원하지 않는 백업 파일 형식입니다.")
    else:
        raise HTTPException(status_code=400, detail="ZIP 또는 JSON 파일만 업로드 가능합니다.")

    restored_settings = 0
    restored_products = 0
    skipped_products = 0

    # Settings 복원
    for s in backup.get("settings", []):
        if s["key"] in SENSITIVE_KEYS:
            continue
        existing = db.query(Setting).filter(Setting.key == s["key"]).first()
        if existing:
            existing.value = s["value"]
        else:
            db.add(Setting(key=s["key"], value=s["value"], description=s.get("description")))
        restored_settings += 1

    # Products 복원
    for p in backup.get("products", []):
        existing = db.query(Product).filter(Product.folder_path == p["folder_path"]).first()
        if not existing:
            skipped_products += 1
            continue
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

    parts = []
    if restored_settings:
        parts.append(f"설정 {restored_settings}개")
    if restored_products:
        parts.append(f"제품 메타데이터 {restored_products}개")
    if restored_files:
        parts.append(f"데이터 파일 {restored_files}개")
    summary = ", ".join(parts) + " 복원 완료."
    if skipped_products:
        summary += f" (폴더 없음으로 스킵: {skipped_products}개)"

    return {
        "success": True,
        "restored_settings": restored_settings,
        "restored_products": restored_products,
        "restored_files": restored_files,
        "skipped_products": skipped_products,
        "message": summary
    }
