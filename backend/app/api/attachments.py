from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from pathlib import Path
from pydantic import BaseModel

from app.database import get_db
from app.models.attachment import Attachment
from app.models.version import Version
from app.models.filename_violation import FilenameViolation
from app.models.user import User
from app.schemas.attachment import Attachment as AttachmentSchema, AttachmentUpdate
from app.dependencies import get_current_user, get_current_admin_user
from app.config import settings

VALID_CLASSIFICATIONS = {"patch", "language_pack", "manual", "update"}


class ReclassifyVersionRequest(BaseModel):
    classification: str  # patch | language_pack | manual | update
    note: Optional[str] = None


router = APIRouter(prefix="/api/attachments", tags=["attachments"])


@router.post("/upload", response_model=AttachmentSchema)
async def upload_attachment(
    product_id: int = Form(...),
    file: UploadFile = File(...),
    note: Optional[str] = Form(None),
    type: str = Form("patch"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    패치/크랙 파일 업로드
    """
    # 제품 존재 여부 확인
    from app.models.product import Product
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # 파일 저장 경로 생성
    patches_dir = Path(settings.PATCHES_DIR)
    product_dir = patches_dir / str(product_id)
    product_dir.mkdir(parents=True, exist_ok=True)

    # 파일 저장
    file_path = product_dir / file.filename

    # 파일이 이미 존재하는 경우 고유한 이름 생성
    counter = 1
    original_filename = file.filename
    while file_path.exists():
        name, ext = os.path.splitext(original_filename)
        file_path = product_dir / f"{name}_{counter}{ext}"
        counter += 1

    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # 파일 크기 확인
    file_size = file_path.stat().st_size

    # DB에 저장
    attachment = Attachment(
        product_id=product_id,
        file_path=str(file_path),
        file_name=file_path.name,
        file_size=file_size,
        note=note,
        type=type
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)

    return attachment


@router.get("/product/{product_id}", response_model=List[AttachmentSchema])
def get_product_attachments(
    product_id: int,
    type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    특정 제품의 패치 파일 목록 조회
    """
    query = db.query(Attachment).filter(Attachment.product_id == product_id)

    if type:
        query = query.filter(Attachment.type == type)

    attachments = query.order_by(Attachment.created_at.desc()).all()
    return attachments


@router.get("/download/{attachment_id}")
async def download_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    패치 파일 다운로드
    """
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")

    file_path = Path(attachment.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        path=str(file_path),
        filename=attachment.file_name,
        media_type="application/octet-stream"
    )


@router.patch("/{attachment_id}", response_model=AttachmentSchema)
def update_attachment(
    attachment_id: int,
    update_data: AttachmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    패치 파일 정보 수정 (노트만 수정 가능)
    """
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")

    if update_data.note is not None:
        attachment.note = update_data.note

    db.commit()
    db.refresh(attachment)
    return attachment


@router.delete("/{attachment_id}")
def delete_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # 관리자만 삭제 가능
):
    """
    패치 파일 삭제
    """
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")

    # 파일 삭제
    file_path = Path(attachment.file_path)
    if file_path.exists():
        try:
            file_path.unlink()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

    # DB에서 삭제
    db.delete(attachment)
    db.commit()

    return {"message": "Attachment deleted successfully"}


@router.post("/from-version/{version_id}", response_model=AttachmentSchema)
def reclassify_version_as_attachment(
    version_id: int,
    request: ReclassifyVersionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    버전(Version)을 첨부파일(Attachment)로 분류 변환

    버전 탭의 파일을 패치/언어팩/메뉴얼/업데이트로 재분류할 때 사용한다.
    - Version 레코드를 Attachment 레코드로 변환 (물리 파일은 그대로 유지)
    - 관련 스캔 항목(FilenameViolation)이 있으면 등록 완료로 표시
    """
    if request.classification not in VALID_CLASSIFICATIONS:
        raise HTTPException(
            status_code=400,
            detail=f"유효하지 않은 분류입니다. 허용값: {', '.join(VALID_CLASSIFICATIONS)}"
        )

    version = db.query(Version).filter(Version.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="버전을 찾을 수 없습니다.")

    product_id = version.product_id

    # 같은 경로의 첨부파일이 이미 있는지 확인
    existing = db.query(Attachment).filter(
        Attachment.product_id == product_id,
        Attachment.file_path == version.file_path,
    ).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail="이 파일은 이미 해당 제품의 첨부파일로 등록되어 있습니다."
        )

    # Attachment 생성 (물리 파일은 그대로, DB 레코드만 변환)
    attachment = Attachment(
        product_id=product_id,
        file_path=version.file_path,
        file_name=version.file_name,
        file_size=version.file_size or 0,
        note=request.note or "",
        type=request.classification,
    )
    db.add(attachment)

    # 연관된 FilenameViolation 스캔 항목 등록 완료 처리
    scan_item = db.query(FilenameViolation).filter(
        FilenameViolation.folder_path == str(Path(version.file_path).parent),
        FilenameViolation.file_name == version.file_name,
    ).first()
    if scan_item:
        scan_item.is_resolved = True
        scan_item.product_id = product_id
        scan_item.classification = request.classification
        scan_item.violation_details = f"{request.classification} 등록 완료 (버전에서 변환)"

    # Version 레코드 삭제
    db.delete(version)
    db.commit()
    db.refresh(attachment)

    return attachment
