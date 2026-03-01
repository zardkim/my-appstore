import os
import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product_video import ProductVideo
from app.models.product import Product
from app.models.user import User
from app.schemas.product_video import ProductVideo as ProductVideoSchema, ProductVideoUpdate
from app.dependencies import get_current_user, get_current_admin_user
from app.config import settings

router = APIRouter(prefix="/api/product-videos", tags=["product-videos"])

ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.webm', '.ogg', '.mov', '.avi', '.mkv'}
ALLOWED_VIDEO_MIMES = {
    'video/mp4', 'video/webm', 'video/ogg',
    'video/quicktime', 'video/x-msvideo', 'video/x-matroska',
}
MIME_BY_EXT = {
    '.mp4': 'video/mp4',
    '.webm': 'video/webm',
    '.ogg': 'video/ogg',
    '.mov': 'video/quicktime',
    '.avi': 'video/x-msvideo',
    '.mkv': 'video/x-matroska',
}
MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500MB


def _get_video_dir(product_id: int) -> Path:
    video_dir = Path(settings.VIDEOS_DIR) / str(product_id)
    video_dir.mkdir(parents=True, exist_ok=True)
    return video_dir


def _unique_path(dest_dir: Path, filename: str) -> Path:
    dest = dest_dir / filename
    if not dest.exists():
        return dest
    stem, ext = os.path.splitext(filename)
    counter = 1
    while dest.exists():
        dest = dest_dir / f"{stem}_{counter}{ext}"
        counter += 1
    return dest


@router.get("/{product_id}", response_model=List[ProductVideoSchema])
def get_product_videos(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """제품의 설치안내 영상 목록 조회"""
    return (
        db.query(ProductVideo)
        .filter(ProductVideo.product_id == product_id)
        .order_by(ProductVideo.sort_order, ProductVideo.created_at)
        .all()
    )


@router.post("/upload/{product_id}", response_model=ProductVideoSchema)
async def upload_video(
    product_id: int,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """동영상 파일 직접 업로드"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="제품을 찾을 수 없습니다.")

    ext = Path(file.filename).suffix.lower() if file.filename else ''
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 파일 형식입니다. 지원 형식: {', '.join(ALLOWED_VIDEO_EXTENSIONS)}",
        )

    # 저장 디렉토리 준비
    video_dir = _get_video_dir(product_id)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    import random, string
    rand = ''.join(random.choices(string.hexdigits[:16], k=6))
    safe_name = Path(file.filename).name
    dest = _unique_path(video_dir, f"{timestamp}_{rand}_{safe_name}")

    # 파일 저장
    try:
        content = await file.read()
        if len(content) > MAX_VIDEO_SIZE:
            raise HTTPException(status_code=413, detail="파일 크기가 500MB를 초과합니다.")
        with open(dest, 'wb') as f:
            f.write(content)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 저장 실패: {e}")

    mime_type = MIME_BY_EXT.get(ext, 'video/mp4')
    video_title = title.strip() if title and title.strip() else Path(file.filename).stem

    video = ProductVideo(
        product_id=product_id,
        title=video_title,
        description=description,
        file_path=str(dest),
        file_name=dest.name,
        file_size=dest.stat().st_size,
        mime_type=mime_type,
        source='upload',
    )
    db.add(video)
    db.commit()
    db.refresh(video)
    return video


@router.patch("/{video_id}", response_model=ProductVideoSchema)
def update_video(
    video_id: int,
    data: ProductVideoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """영상 제목/설명/순서 수정"""
    video = db.query(ProductVideo).filter(ProductVideo.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="영상을 찾을 수 없습니다.")

    if data.title is not None:
        video.title = data.title
    if data.description is not None:
        video.description = data.description
    if data.sort_order is not None:
        video.sort_order = data.sort_order

    db.commit()
    db.refresh(video)
    return video


@router.delete("/{video_id}")
def delete_video(
    video_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """영상 삭제 (직접 업로드: 파일+DB / 스캔 등록: DB만)"""
    video = db.query(ProductVideo).filter(ProductVideo.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="영상을 찾을 수 없습니다.")

    if video.source == 'upload':
        file_path = Path(video.file_path)
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception:
                pass

    db.delete(video)
    db.commit()
    return {"message": "영상이 삭제되었습니다."}
