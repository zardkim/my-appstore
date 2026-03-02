from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse, FileResponse
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
from app.models.post import Post
from app.models.comment import Comment
from app.models.user import User
from app.dependencies import get_current_admin_user
from app.config import settings

router = APIRouter()

# 백업에 포함할 data 서브디렉토리 (실제 소프트웨어 파일/library, PostgreSQL 바이너리/db, redis 제외)
BACKUP_DATA_SUBDIRS = ["icons", "videos", "attachments", "screenshots", "eximage", "patches", "config", "logs"]
BACKUP_DATA_FILES = ["config.json", "scan_exclusions.txt"]

# 민감 설정 키 (백업 제외)
SENSITIVE_KEYS = {"ai_api_key", "openai_api_key", "gemini_api_key"}

# 서버 백업 저장 디렉토리
BACKUP_DIR_NAME = "backup"


def get_backup_dir() -> Path:
    backup_dir = Path(settings.CONFIG_DATA_DIR) / BACKUP_DIR_NAME
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


def _safe_filename(name: str) -> str:
    """경로 탐색 공격 방지: 파일명만 허용"""
    return Path(name).name


def _dt_to_str(val):
    if val is None:
        return None
    if hasattr(val, 'isoformat'):
        return val.isoformat()
    return str(val)


def _build_db_snapshot(db: Session) -> dict:
    """모든 DB 데이터를 dict로 직렬화 (실제 소프트웨어 파일 경로만 참조, 파일 자체 제외)"""
    # Products + Versions
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
            "release_date": _dt_to_str(p.release_date),
            "installation_guide": p.installation_guide,
            "patch_links": p.patch_links,
            "versions": versions_data,
        })

    # Settings
    settings_rows = db.query(Setting).all()
    settings_data = [
        {"key": s.key, "value": s.value, "description": s.description}
        for s in settings_rows
        if s.key not in SENSITIVE_KEYS
    ]

    # Posts (팁&테크 게시글)
    posts = db.query(Post).all()
    posts_data = [
        {
            "id": p.id,
            "category": p.category,
            "title": p.title,
            "content": p.content,
            "tags": p.tags,
            "is_notice": p.is_notice,
            "author_id": p.author_id,
            "views": p.views,
            "images": p.images,
            "attachments": p.attachments,
            "created_at": _dt_to_str(p.created_at),
            "updated_at": _dt_to_str(p.updated_at),
        }
        for p in posts
    ]

    # Comments (댓글)
    comments = db.query(Comment).all()
    comments_data = [
        {
            "id": c.id,
            "post_id": c.post_id,
            "author_id": c.author_id,
            "content": c.content,
            "created_at": _dt_to_str(c.created_at),
            "updated_at": _dt_to_str(c.updated_at),
        }
        for c in comments
    ]

    # Users (비밀번호 해시 제외)
    users = db.query(User).all()
    users_data = [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": u.role.value if hasattr(u.role, 'value') else str(u.role),
            "is_active": u.is_active,
            "created_at": _dt_to_str(u.created_at),
        }
        for u in users
    ]

    return {
        "backup_version": "3.0",
        "backup_date": datetime.now(timezone.utc).isoformat(),
        "products_count": len(products_data),
        "settings_count": len(settings_data),
        "posts_count": len(posts_data),
        "comments_count": len(comments_data),
        "users_count": len(users_data),
        "products": products_data,
        "settings": settings_data,
        "posts": posts_data,
        "comments": comments_data,
        "users": users_data,
    }


def _build_zip_buffer(db_snapshot: dict) -> io.BytesIO:
    """DB 스냅샷 + 데이터 파일 → ZIP BytesIO"""
    data_root = Path(settings.CONFIG_DATA_DIR)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode='w', compression=zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
        zf.writestr("backup.json", json.dumps(db_snapshot, ensure_ascii=False, indent=2))

        for fname in BACKUP_DATA_FILES:
            fpath = data_root / fname
            if fpath.exists():
                zf.write(fpath, f"data/{fname}")

        for subdir in BACKUP_DATA_SUBDIRS:
            subdir_path = data_root / subdir
            if not subdir_path.exists():
                continue
            for file_path in subdir_path.rglob("*"):
                if file_path.is_file():
                    arcname = "data/" + str(file_path.relative_to(data_root))
                    zf.write(file_path, arcname)

    buf.seek(0)
    return buf


def _restore_from_bytes(raw: bytes, db: Session) -> dict:
    """ZIP 또는 JSON 바이트로부터 복원 수행, 결과 dict 반환"""
    restored_files = 0

    if raw[:2] == b'PK':  # ZIP magic bytes
        try:
            zf = zipfile.ZipFile(io.BytesIO(raw))
        except zipfile.BadZipFile:
            raise HTTPException(status_code=400, detail="유효하지 않은 ZIP 파일입니다.")

        try:
            backup_json = zf.read("backup.json").decode("utf-8")
            backup = json.loads(backup_json)
        except (KeyError, json.JSONDecodeError):
            raise HTTPException(status_code=400, detail="ZIP 내 backup.json을 읽을 수 없습니다.")

        if backup.get("backup_version") not in ("1.0", "2.0", "3.0"):
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
    else:
        try:
            backup = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise HTTPException(status_code=400, detail="유효하지 않은 백업 파일입니다.")

        if backup.get("backup_version") not in ("1.0", "2.0", "3.0"):
            raise HTTPException(status_code=400, detail="지원하지 않는 백업 파일 형식입니다.")

    restored_settings = 0
    restored_products = 0
    skipped_products = 0
    restored_posts = 0
    restored_comments = 0

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

    # Products 복원 (폴더 경로 일치 항목만)
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

    # Posts 복원 (ID 기반 upsert)
    for post_data in backup.get("posts", []):
        existing = db.query(Post).filter(Post.id == post_data["id"]).first()
        if existing:
            for field in ["category", "title", "content", "tags", "is_notice", "views", "images", "attachments"]:
                if field in post_data:
                    setattr(existing, field, post_data[field])
        else:
            db.add(Post(
                id=post_data["id"],
                category=post_data.get("category", "tip"),
                title=post_data.get("title", ""),
                content=post_data.get("content", ""),
                tags=post_data.get("tags"),
                is_notice=post_data.get("is_notice", False),
                author_id=post_data.get("author_id", 1),
                views=post_data.get("views", 0),
                images=post_data.get("images"),
                attachments=post_data.get("attachments"),
            ))
        restored_posts += 1

    # Comments 복원 (ID 기반 upsert)
    for c_data in backup.get("comments", []):
        existing = db.query(Comment).filter(Comment.id == c_data["id"]).first()
        if existing:
            if "content" in c_data:
                existing.content = c_data["content"]
        else:
            db.add(Comment(
                id=c_data["id"],
                post_id=c_data.get("post_id", 1),
                author_id=c_data.get("author_id", 1),
                content=c_data.get("content", ""),
            ))
        restored_comments += 1

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
    if restored_posts:
        parts.append(f"게시글 {restored_posts}개")
    if restored_comments:
        parts.append(f"댓글 {restored_comments}개")
    if restored_files:
        parts.append(f"데이터 파일 {restored_files}개")
    summary = ", ".join(parts) + " 복원 완료." if parts else "복원 완료."
    if skipped_products:
        summary += f" (폴더 없음으로 스킵: {skipped_products}개)"

    return {
        "success": True,
        "restored_settings": restored_settings,
        "restored_products": restored_products,
        "restored_posts": restored_posts,
        "restored_comments": restored_comments,
        "restored_files": restored_files,
        "skipped_products": skipped_products,
        "message": summary
    }


# ── API 엔드포인트 ──────────────────────────────────────────────────────────

@router.post("/create")
async def create_backup(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user)
):
    """백업 파일 생성하여 서버 backup 폴더에 저장 (관리자 전용)"""
    db_snapshot = _build_db_snapshot(db)
    filename = f"myappstore_backup_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.zip"
    backup_dir = get_backup_dir()
    backup_path = backup_dir / filename

    buf = _build_zip_buffer(db_snapshot)
    backup_path.write_bytes(buf.read())
    stat = backup_path.stat()

    return {
        "success": True,
        "filename": filename,
        "size": stat.st_size,
        "created_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        "message": f"백업 파일이 생성되었습니다: {filename}"
    }


@router.get("/list")
async def list_backups(
    current_user=Depends(get_current_admin_user)
):
    """서버 backup 폴더의 백업 파일 목록 조회 (관리자 전용)"""
    backup_dir = get_backup_dir()
    files = []
    for f in sorted(backup_dir.glob("*.zip"), key=lambda x: x.stat().st_mtime, reverse=True):
        stat = f.stat()
        files.append({
            "filename": f.name,
            "size": stat.st_size,
            "created_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        })
    return {"files": files, "count": len(files)}


@router.get("/download/{filename}")
async def download_backup_file(
    filename: str,
    current_user=Depends(get_current_admin_user)
):
    """서버에 저장된 특정 백업 파일 다운로드 (관리자 전용)"""
    safe_name = _safe_filename(filename)
    backup_path = get_backup_dir() / safe_name
    if not backup_path.exists() or not backup_path.is_file():
        raise HTTPException(status_code=404, detail="백업 파일을 찾을 수 없습니다.")

    def iterfile():
        with open(backup_path, "rb") as f:
            yield from f

    return StreamingResponse(
        iterfile(),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{safe_name}"'}
    )


@router.post("/restore-from-server/{filename}")
async def restore_from_server(
    filename: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user)
):
    """서버에 저장된 백업 파일로 복원 (관리자 전용)"""
    safe_name = _safe_filename(filename)
    backup_path = get_backup_dir() / safe_name
    if not backup_path.exists() or not backup_path.is_file():
        raise HTTPException(status_code=404, detail="백업 파일을 찾을 수 없습니다.")

    raw = backup_path.read_bytes()
    return _restore_from_bytes(raw, db)


@router.delete("/{filename}")
async def delete_backup_file(
    filename: str,
    current_user=Depends(get_current_admin_user)
):
    """서버 백업 파일 삭제 (관리자 전용)"""
    safe_name = _safe_filename(filename)
    backup_path = get_backup_dir() / safe_name
    if not backup_path.exists() or not backup_path.is_file():
        raise HTTPException(status_code=404, detail="백업 파일을 찾을 수 없습니다.")

    backup_path.unlink()
    return {"success": True, "message": f"백업 파일이 삭제되었습니다: {safe_name}"}


@router.post("/restore")
async def restore_backup(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user)
):
    """
    업로드한 백업 파일로 복원 (관리자 전용) - 파일 업로드 방식
    - ZIP (v2.0/3.0): DB + 데이터 파일 복원
    - JSON (v1.0): DB만 복원 (하위 호환)
    """
    if not (file.filename.endswith(".zip") or file.filename.endswith(".json")):
        raise HTTPException(status_code=400, detail="ZIP 또는 JSON 파일만 업로드 가능합니다.")

    raw = await file.read()
    return _restore_from_bytes(raw, db)


@router.get("/export")
async def export_backup(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user)
):
    """
    전체 데이터 백업 ZIP 직접 다운로드 (관리자 전용) - 하위 호환용
    """
    db_snapshot = _build_db_snapshot(db)
    buf = _build_zip_buffer(db_snapshot)
    filename = f"myappstore_backup_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.zip"

    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
