"""
스캔 목록 (Scan Items) 관리 API

파일 스캔 후 생성된 항목을 관리한다. 각 항목은 6가지 분류 중 하나로 자동 분류되며,
분류에 따라 제품 등록(AI 매칭) 또는 첨부파일(패치/언어팩/메뉴얼/업데이트) 또는 설치영상 등록 처리를 한다.

분류값: product | patch | language_pack | manual | update | installation_video
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime
import os
from pathlib import Path

from app.database import get_db
from app.models.filename_violation import FilenameViolation
from app.models.version import Version
from app.models.product import Product
from app.models.attachment import Attachment
from app.models.user import User
from app.dependencies import get_current_admin_user
from app.core.ai_metadata import AIMetadataGeneratorV2 as AIMetadataGenerator
from app.core.parser import FilenameParser
from app.core.classifier import classify_file
from app.api.config import load_config
from app.core.redis_cache import invalidate_cache
from app.core.auto_matcher import match_violations_to_products, find_similar_product
from app.core.activity_logger import log_activity

# ── 하위 호환: 기존 URL (/api/filename-violations) + 신규 URL (/api/scan-items)
router = APIRouter(tags=["Scan Items"])

VALID_CLASSIFICATIONS = {"product", "patch", "language_pack", "manual", "update", "installation_video"}


# ─────────────────────────────────────────────────────────────────
# Pydantic Schemas
# ─────────────────────────────────────────────────────────────────

class ScanItemResponse(BaseModel):
    id: int
    folder_path: str
    file_name: str
    violation_type: str
    violation_details: Optional[str] = None
    suggestion: Optional[str] = None
    created_at: Optional[datetime] = None
    is_resolved: bool
    classification: str
    classification_auto: bool
    product_id: Optional[int] = None
    version_id: Optional[int] = None

    class Config:
        from_attributes = True


# 하위 호환용 alias
FilenameViolationResponse = ScanItemResponse


class RenameFileRequest(BaseModel):
    new_filename: str


class ClassifyRequest(BaseModel):
    classification: str  # product | patch | language_pack | manual | update


class RegisterScanItemRequest(BaseModel):
    product_id: Optional[int] = None  # 제품 이외 분류일 때 필수
    note: Optional[str] = None


class BatchRenameRequest(BaseModel):
    violation_ids: List[int]


class BatchDeleteRequest(BaseModel):
    violation_ids: List[int]


class CreateProductWithMetadataRequest(BaseModel):
    metadata: Dict


# ─────────────────────────────────────────────────────────────────
# 목록 조회
# ─────────────────────────────────────────────────────────────────

@router.get("/api/scan-items/", response_model=List[ScanItemResponse])
@router.get("/api/filename-violations/", response_model=List[ScanItemResponse])
async def get_scan_items(
    classification: Optional[str] = Query(None, description="분류 필터: product|patch|language_pack|manual|update"),
    search: Optional[str] = Query(None, description="파일명 검색어"),
    resolved: bool = Query(False, description="등록 완료 항목 포함 여부"),
    page: int = Query(1, ge=1),
    size: int = Query(200, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """스캔 목록 조회 (관리자 전용)"""
    query = db.query(FilenameViolation).filter(
        FilenameViolation.is_resolved == resolved
    )

    if classification and classification in VALID_CLASSIFICATIONS:
        query = query.filter(FilenameViolation.classification == classification)

    if search:
        query = query.filter(
            FilenameViolation.file_name.ilike(f"%{search}%")
        )

    offset = (page - 1) * size
    items = query.order_by(FilenameViolation.created_at.desc()).offset(offset).limit(size).all()
    return items


# ─────────────────────────────────────────────────────────────────
# 통계
# ─────────────────────────────────────────────────────────────────

@router.get("/api/scan-items/stats")
@router.get("/api/filename-violations/stats")
async def get_scan_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """스캔 항목 통계 조회 (분류별)"""
    base = db.query(FilenameViolation).filter(FilenameViolation.is_resolved == False)
    total = base.count()

    by_classification = {}
    for cls in VALID_CLASSIFICATIONS:
        by_classification[cls] = base.filter(
            FilenameViolation.classification == cls
        ).count()

    return {
        "total": total,
        "by_classification": by_classification,
    }


# ─────────────────────────────────────────────────────────────────
# 분류 수동 변경
# ─────────────────────────────────────────────────────────────────

@router.patch("/api/scan-items/{scan_item_id}/classify")
@router.patch("/api/filename-violations/{scan_item_id}/classify")
async def classify_scan_item(
    scan_item_id: int,
    request: ClassifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """스캔 항목의 분류를 수동으로 변경한다."""
    if request.classification not in VALID_CLASSIFICATIONS:
        raise HTTPException(
            status_code=400,
            detail=f"유효하지 않은 분류입니다. 허용값: {', '.join(VALID_CLASSIFICATIONS)}"
        )

    item = db.query(FilenameViolation).filter(FilenameViolation.id == scan_item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="스캔 항목을 찾을 수 없습니다.")

    item.classification = request.classification
    item.classification_auto = False  # 수동 변경
    db.commit()

    return {"success": True, "id": scan_item_id, "classification": request.classification}


# ─────────────────────────────────────────────────────────────────
# 중복 제품 검사 (AI 검색 전 사전 검사)
# ─────────────────────────────────────────────────────────────────

@router.get("/api/scan-items/{scan_item_id}/find-similar")
@router.get("/api/filename-violations/{scan_item_id}/find-similar")
async def find_similar_products_for_scan_item(
    scan_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """AI 검색 전 중복 제품 검사 - 백엔드 매칭 로직과 동일한 방식으로 유사 제품 반환"""
    import os
    from app.core.parser import FilenameParser

    item = db.query(FilenameViolation).filter(FilenameViolation.id == scan_item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="스캔 항목을 찾을 수 없습니다.")

    similar_products = []
    folder_path = item.folder_path

    # 1단계: folder_path 정확한 매칭 (백엔드 1순위 검사와 동일)
    existing = db.query(Product).filter(Product.folder_path == folder_path).first()
    if existing:
        similar_products.append({
            "id": existing.id,
            "title": existing.title,
            "vendor": existing.vendor or "",
            "category": existing.category or "",
            "icon_url": existing.icon_url or "",
            "folder_path": existing.folder_path,
            "match_type": "exact_folder"
        })
    else:
        # 2단계: 폴더명 파싱 + 유사도 기반 검사 (백엔드 2순위 검사와 동일)
        parser = FilenameParser()
        folder_name = os.path.basename(folder_path)
        parsed_info = parser.parse(folder_name)
        software_name = parsed_info.get('software_name', folder_name)

        if parsed_info.get('year'):
            year = parsed_info['year']
            if year not in software_name:
                software_name = f"{software_name} {year}"

        similar = find_similar_product(db, software_name)
        if similar:
            similar_products.append({
                "id": similar.id,
                "title": similar.title,
                "vendor": similar.vendor or "",
                "category": similar.category or "",
                "icon_url": similar.icon_url or "",
                "folder_path": similar.folder_path,
                "match_type": "similar"
            })

    return {"similar_products": similar_products}


# ─────────────────────────────────────────────────────────────────
# 등록 (분류에 따라 제품 등록 or 첨부파일 등록)
# ─────────────────────────────────────────────────────────────────

@router.post("/api/scan-items/{scan_item_id}/register")
@router.post("/api/filename-violations/{scan_item_id}/register")
async def register_scan_item(
    scan_item_id: int,
    request: RegisterScanItemRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """분류에 따라 스캔 항목을 등록한다.

    - product       → AI 매칭 후 Product/Version 생성 (기존 create-product 로직)
    - 나머지 분류   → 지정된 제품의 Attachment로 등록 (product_id 필수)
    """
    item = db.query(FilenameViolation).filter(FilenameViolation.id == scan_item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="스캔 항목을 찾을 수 없습니다.")

    # 제품 분류: AI 매칭으로 Product 생성
    if item.classification == "product":
        result = await _register_as_product(item, db)
        if result.get("success") and result.get("product_id"):
            log_activity(db, action="product_create", resource_type="product",
                         resource_id=result["product_id"],
                         resource_name=result.get("product", {}).get("title") or item.file_name,
                         user_id=current_user.id, username=current_user.username)
        return result

    # 설치영상 분류: ProductVideo 생성
    if item.classification == "installation_video":
        if not request.product_id:
            raise HTTPException(
                status_code=400,
                detail="설치영상 등록 시 product_id가 필요합니다."
            )
        return await _register_as_video(item, request.product_id, request.note, db)

    # 그 외 분류: Attachment 생성
    if not request.product_id:
        raise HTTPException(
            status_code=400,
            detail="패치/언어팩/메뉴얼/업데이트 등록 시 product_id가 필요합니다."
        )

    return await _register_as_attachment(item, request.product_id, request.note, db)


async def _register_as_product(item: FilenameViolation, db: Session):
    """product 분류 항목을 AI 매칭으로 Product/Version으로 등록"""
    config = load_config()
    metadata_config = config.get('metadata', {})
    use_ai = metadata_config.get('scanMethod', 'manual') == 'ai'
    ai_provider = metadata_config.get('aiProvider', 'openai')
    ai_model = metadata_config.get('aiModel', 'gpt-4o-mini')

    if not use_ai:
        raise HTTPException(
            status_code=400,
            detail="AI 메타데이터 생성이 비활성화되어 있습니다. 설정 > 메타데이터 설정에서 스캔 방법을 'AI'로 변경해주세요."
        )

    if ai_provider == 'gemini':
        api_key = metadata_config.get('geminiApiKey', '')
    else:
        api_key = metadata_config.get('openaiApiKey', '') or metadata_config.get('apiKey', '')

    if not api_key or not api_key.strip():
        raise HTTPException(
            status_code=400,
            detail=f"{ai_provider.upper()} API 키가 설정되지 않았습니다. 설정 페이지에서 API 키를 입력해주세요."
        )

    try:
        # 같은 폴더의 미등록 product 항목을 함께 매칭
        same_folder = db.query(FilenameViolation).filter(
            FilenameViolation.folder_path == item.folder_path,
            FilenameViolation.is_resolved == False,
            FilenameViolation.classification == "product",
        ).all()

        results = await match_violations_to_products(
            db=db,
            violations=same_folder if same_folder else [item],
            ai_provider=ai_provider,
            ai_model=ai_model,
            api_key=api_key,
            skip_clarity_check=True,
            provided_metadata=None,
        )

        if results["matched"] > 0 and results["products"]:
            product_info = results["products"][0]
            is_duplicate = len(results.get("duplicates", [])) > 0
            duplicate_info = results["duplicates"][0] if is_duplicate else None
            matched_count = len(same_folder) if same_folder else 1

            return {
                "success": True,
                "message": "기존 제품에 버전이 추가되었습니다." if is_duplicate
                           else f"제품이 등록되었습니다. ({matched_count}개 파일 매칭)",
                "product_id": product_info["id"],
                "product": {
                    **product_info,
                    "is_duplicate": is_duplicate,
                    "duplicate_reason": duplicate_info["reason"] if duplicate_info else None,
                },
                "matched_files": matched_count,
            }

        if results.get("api_error"):
            err = results["api_error"]
            status = 429 if err.get("type") == "rate_limit" else \
                     402 if err.get("type") == "insufficient_quota" else 500
            raise HTTPException(status_code=status, detail=err.get("message", "API 오류"))

        raise HTTPException(
            status_code=500,
            detail=f"제품 등록 실패: {', '.join(results['errors']) if results['errors'] else 'Unknown error'}"
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"제품 등록 중 오류 발생: {str(e)}")


async def _register_as_video(
    item: FilenameViolation,
    product_id: int,
    note: Optional[str],
    db: Session,
):
    """installation_video 분류 항목을 ProductVideo로 등록 (data/videos/ 에 복사)"""
    import shutil
    from app.models.product_video import ProductVideo
    from app.config import settings

    MIME_BY_EXT = {
        '.mp4': 'video/mp4', '.webm': 'video/webm', '.ogg': 'video/ogg',
        '.mov': 'video/quicktime', '.avi': 'video/x-msvideo', '.mkv': 'video/x-matroska',
    }

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="제품을 찾을 수 없습니다.")

    src_path = Path(item.folder_path) / item.file_name
    if not src_path.exists():
        raise HTTPException(status_code=404, detail=f"파일을 찾을 수 없습니다: {src_path}")

    existing = db.query(ProductVideo).filter(
        ProductVideo.product_id == product_id,
        ProductVideo.file_name == item.file_name,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="이 파일은 이미 해당 제품의 설치영상으로 등록되어 있습니다.")

    # data/videos/{product_id}/ 에 복사
    dest_dir = Path(settings.VIDEOS_DIR) / str(product_id)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / item.file_name

    # 파일명 충돌 처리
    counter = 1
    while dest_path.exists():
        stem, ext = os.path.splitext(item.file_name)
        dest_path = dest_dir / f"{stem}_{counter}{ext}"
        counter += 1

    shutil.copy2(str(src_path), str(dest_path))

    ext = Path(item.file_name).suffix.lower()
    mime_type = MIME_BY_EXT.get(ext, 'video/mp4')
    title = note.strip() if note and note.strip() else Path(item.file_name).stem

    video = ProductVideo(
        product_id=product_id,
        title=title,
        file_path=str(dest_path),
        file_name=dest_path.name,
        file_size=dest_path.stat().st_size,
        mime_type=mime_type,
        source='scan',
    )
    db.add(video)

    item.is_resolved = True
    item.product_id = product_id
    item.violation_details = "설치영상 등록 완료"

    db.commit()
    db.refresh(video)

    return {
        "success": True,
        "message": "설치 안내 영상이 등록되었습니다.",
        "video_id": video.id,
        "product_id": product_id,
    }


async def _register_as_attachment(
    item: FilenameViolation,
    product_id: int,
    note: Optional[str],
    db: Session,
):
    """patch/language_pack/manual/update 분류 항목을 Attachment로 등록"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="제품을 찾을 수 없습니다.")

    file_full_path = os.path.join(item.folder_path, item.file_name)
    if not os.path.exists(file_full_path):
        raise HTTPException(
            status_code=404,
            detail=f"파일을 찾을 수 없습니다: {file_full_path}"
        )

    file_size = os.path.getsize(file_full_path)

    # 중복 첨부파일 확인 (같은 경로)
    existing = db.query(Attachment).filter(
        Attachment.product_id == product_id,
        Attachment.file_path == file_full_path,
    ).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail="이 파일은 이미 해당 제품에 등록되어 있습니다."
        )

    attachment = Attachment(
        product_id=product_id,
        file_path=file_full_path,
        file_name=item.file_name,
        file_size=file_size,
        note=note or "",
        type=item.classification,  # patch | language_pack | manual | update
    )
    db.add(attachment)

    # 스캔 항목을 등록 완료 처리
    item.is_resolved = True
    item.product_id = product_id
    item.violation_details = f"{item.classification} 등록 완료"

    db.commit()
    db.refresh(attachment)

    return {
        "success": True,
        "message": f"{item.classification} 등록이 완료되었습니다.",
        "attachment_id": attachment.id,
        "product_id": product_id,
    }


# ─────────────────────────────────────────────────────────────────
# 파일명 변경
# ─────────────────────────────────────────────────────────────────

@router.put("/api/scan-items/{scan_item_id}/rename")
@router.put("/api/filename-violations/{scan_item_id}/rename")
async def rename_scan_item(
    scan_item_id: int,
    request: RenameFileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """파일명 변경 (실제 파일 시스템 rename + DB 업데이트 + 분류 재계산)"""
    item = db.query(FilenameViolation).filter(FilenameViolation.id == scan_item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="스캔 항목을 찾을 수 없습니다.")

    old_path = os.path.join(item.folder_path, item.file_name)
    new_path = os.path.join(item.folder_path, request.new_filename)

    if not os.path.exists(old_path):
        raise HTTPException(status_code=404, detail=f"파일을 찾을 수 없습니다: {old_path}")
    if os.path.exists(new_path):
        raise HTTPException(status_code=409, detail=f"동일한 이름의 파일이 이미 존재합니다: {request.new_filename}")

    try:
        os.rename(old_path, new_path)

        # Version 레코드 업데이트 (이미 매칭된 경우)
        version = db.query(Version).filter(Version.file_path == old_path).first()
        if version:
            version.file_name = request.new_filename
            version.file_path = new_path

        # 파일명 변경 → 분류 재계산 (자동 분류 상태인 경우에만)
        folder_name = Path(item.folder_path).name
        new_classification = classify_file(request.new_filename, folder_name)

        old_name = item.file_name
        item.file_name = request.new_filename
        item.suggestion = request.new_filename
        item.violation_details = "파일명 변경됨 (AI 매칭 대기중)"
        # is_resolved는 변경하지 않음 - 여전히 등록 대기 상태

        # 자동 분류 상태이면 새 파일명 기준으로 분류 재계산
        if item.classification_auto:
            item.classification = new_classification

        db.commit()

        return {
            "success": True,
            "message": "파일명이 성공적으로 변경되었습니다.",
            "old_filename": old_name,
            "new_filename": request.new_filename,
            "classification": item.classification,
        }

    except PermissionError:
        db.rollback()
        raise HTTPException(status_code=403, detail="파일명을 변경할 권한이 없습니다.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"파일명 변경 중 오류가 발생했습니다: {str(e)}")


# ─────────────────────────────────────────────────────────────────
# 삭제
# ─────────────────────────────────────────────────────────────────

@router.delete("/api/scan-items/{scan_item_id}")
@router.delete("/api/filename-violations/{scan_item_id}")
async def delete_scan_item(
    scan_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """스캔 항목 삭제"""
    item = db.query(FilenameViolation).filter(FilenameViolation.id == scan_item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="스캔 항목을 찾을 수 없습니다.")

    db.delete(item)
    db.commit()
    return {"success": True, "message": "삭제되었습니다.", "id": scan_item_id}


@router.post("/api/scan-items/batch-delete")
@router.post("/api/filename-violations/batch-delete")
async def batch_delete_scan_items(
    request: BatchDeleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """선택한 스캔 항목 일괄 삭제"""
    deleted, failed, errors = 0, 0, []

    for item_id in request.violation_ids:
        try:
            item = db.query(FilenameViolation).filter(FilenameViolation.id == item_id).first()
            if not item:
                failed += 1
                errors.append(f"ID {item_id}: 항목을 찾을 수 없음")
                continue
            db.delete(item)
            deleted += 1
        except Exception as e:
            failed += 1
            errors.append(f"ID {item_id}: {str(e)}")
            db.rollback()

    if deleted > 0:
        db.commit()

    return {
        "message": f"삭제 완료: {deleted}개 성공, {failed}개 실패",
        "deleted_count": deleted,
        "failed_count": failed,
        "errors": errors or None,
    }


# ─────────────────────────────────────────────────────────────────
# 일괄 파일명 변경 (제안된 파일명으로)
# ─────────────────────────────────────────────────────────────────

@router.post("/api/scan-items/batch-rename")
@router.post("/api/filename-violations/batch-rename")
async def batch_rename_scan_items(
    request: BatchRenameRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """제안된 파일명으로 일괄 변경"""
    results = {"success": [], "failed": []}

    for item_id in request.violation_ids:
        item = db.query(FilenameViolation).filter(FilenameViolation.id == item_id).first()
        if not item:
            results["failed"].append({"id": item_id, "error": "항목을 찾을 수 없음"})
            continue

        if not item.suggestion:
            results["failed"].append({"id": item_id, "filename": item.file_name, "error": "제안된 파일명이 없습니다."})
            continue

        old_path = os.path.join(item.folder_path, item.file_name)
        new_path = os.path.join(item.folder_path, item.suggestion)

        if not os.path.exists(old_path):
            results["failed"].append({"id": item_id, "filename": item.file_name, "error": "파일을 찾을 수 없습니다."})
            continue

        if os.path.exists(new_path):
            results["failed"].append({"id": item_id, "filename": item.file_name, "error": "동일한 이름의 파일이 이미 존재합니다."})
            continue

        try:
            os.rename(old_path, new_path)

            version = db.query(Version).filter(Version.file_path == old_path).first()
            if version:
                version.file_name = item.suggestion
                version.file_path = new_path

            folder_name = Path(item.folder_path).name
            old_name = item.file_name
            item.file_name = item.suggestion
            item.violation_details = "파일명 변경됨 (AI 매칭 대기중)"

            if item.classification_auto:
                item.classification = classify_file(item.suggestion, folder_name)

            db.commit()
            results["success"].append({
                "id": item_id,
                "old_filename": old_name,
                "new_filename": item.suggestion,
                "classification": item.classification,
            })

        except Exception as e:
            db.rollback()
            results["failed"].append({"id": item_id, "filename": item.file_name, "error": str(e)})

    return {
        "message": f"성공: {len(results['success'])}개, 실패: {len(results['failed'])}개",
        "results": results,
    }


# ─────────────────────────────────────────────────────────────────
# AI 매칭으로 제품 생성 (하위 호환: 기존 ViolationAISearchDialog에서 사용)
# ─────────────────────────────────────────────────────────────────

@router.post("/api/scan-items/{scan_item_id}/create-product")
@router.post("/api/filename-violations/{scan_item_id}/create-product")
async def create_product_from_scan_item(
    scan_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """스캔 항목으로부터 AI 매칭으로 Product 생성 (하위 호환 엔드포인트)"""
    item = db.query(FilenameViolation).filter(FilenameViolation.id == scan_item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="스캔 항목을 찾을 수 없습니다.")

    return await _register_as_product(item, db)


@router.post("/api/scan-items/{scan_item_id}/create-product-with-metadata")
@router.post("/api/filename-violations/{scan_item_id}/create-product-with-metadata")
async def create_product_from_scan_item_with_metadata(
    scan_item_id: int,
    request: CreateProductWithMetadataRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """스캔 항목으로부터 사용자 제공 메타데이터로 Product 생성 (하위 호환 엔드포인트)"""
    item = db.query(FilenameViolation).filter(FilenameViolation.id == scan_item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="스캔 항목을 찾을 수 없습니다.")

    metadata = request.metadata
    config = load_config()
    metadata_config = config.get('metadata', {})
    ai_provider = metadata_config.get('aiProvider', 'gemini')
    ai_model = metadata_config.get('aiModel', 'gemini-2.5-flash')

    try:
        same_folder = db.query(FilenameViolation).filter(
            FilenameViolation.folder_path == item.folder_path,
            FilenameViolation.is_resolved == False,
            FilenameViolation.classification == "product",
        ).all()

        results = await match_violations_to_products(
            db=db,
            violations=same_folder if same_folder else [item],
            ai_provider=ai_provider,
            ai_model=ai_model,
            api_key="",
            skip_clarity_check=True,
            provided_metadata=metadata,
        )

        if results["matched"] > 0 and results["products"]:
            product_info = results["products"][0]
            is_duplicate = len(results.get("duplicates", [])) > 0
            duplicate_info = results["duplicates"][0] if is_duplicate else None

            return {
                "success": True,
                "message": "기존 제품에 버전이 추가되었습니다." if is_duplicate else "제품이 등록되었습니다.",
                "product_id": product_info["id"],
                "violation_id": scan_item_id,
                "product": {
                    **product_info,
                    "is_duplicate": is_duplicate,
                    "duplicate_reason": duplicate_info["reason"] if duplicate_info else None,
                },
            }

        raise HTTPException(
            status_code=500,
            detail=f"제품 등록 실패: {', '.join(results['errors']) if results['errors'] else 'Unknown error'}"
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"제품 등록 중 오류 발생: {str(e)}")
