from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path
import os
import uuid
from datetime import datetime
from app.database import get_db
from app.dependencies import get_current_user, get_current_admin_user
from app.models.post import Post
from app.models.comment import Comment
from app.models.user import User, UserRole
from app.schemas.post import PostCreate, PostUpdate, PostResponse
from app.config import settings
import logging
logger = logging.getLogger(__name__)


router = APIRouter()


@router.get("/", response_model=List[PostResponse])
def get_posts(
    category: Optional[str] = None,
    is_notice: Optional[bool] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db)
):
    """게시글 목록 조회"""
    query = db.query(Post)

    # 필터링
    if category:
        query = query.filter(Post.category == category)
    if is_notice is not None:
        query = query.filter(Post.is_notice == is_notice)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Post.title.ilike(search_pattern)) | (Post.content.ilike(search_pattern))
        )

    # 정렬: 공지사항 먼저, 그 다음 최신순
    query = query.order_by(Post.is_notice.desc(), Post.created_at.desc())

    posts = query.offset(skip).limit(limit).all()

    # Response 변환
    result = []
    for post in posts:
        # 댓글 수 계산
        comments_count = db.query(Comment).filter(Comment.post_id == post.id).count()

        post_dict = {
            "id": post.id,
            "category": post.category,
            "title": post.title,
            "content": post.content,
            "tags": post.tags,
            "is_notice": post.is_notice,
            "author_id": post.author_id,
            "author_username": post.author.username if post.author else "Unknown",
            "views": post.views,
            "images": post.images,
            "attachments": post.attachments,
            "comments_count": comments_count,
            "created_at": post.created_at,
            "updated_at": post.updated_at
        }
        result.append(PostResponse(**post_dict))

    return result


@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """게시글 상세 조회"""
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    # 조회수 증가
    post.views += 1
    db.commit()

    # 댓글 수 계산
    comments_count = db.query(Comment).filter(Comment.post_id == post.id).count()

    post_dict = {
        "id": post.id,
        "category": post.category,
        "title": post.title,
        "content": post.content,
        "tags": post.tags,
        "is_notice": post.is_notice,
        "author_id": post.author_id,
        "author_username": post.author.username if post.author else "Unknown",
        "views": post.views,
        "images": post.images,
        "attachments": post.attachments,
        "comments_count": comments_count,
        "created_at": post.created_at,
        "updated_at": post.updated_at
    }

    return PostResponse(**post_dict)


@router.post("/", response_model=PostResponse)
def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """게시글 작성"""
    # 공지사항은 관리자만 작성 가능
    logger.debug(f"Create Post] User: {current_user.username}, Role: {current_user.role}, is_notice: {post_data.is_notice}")
    if post_data.is_notice and current_user.role != UserRole.admin:
        logger.debug(f"Create Post] Permission denied - User role: {current_user.role}")
        raise HTTPException(status_code=403, detail="공지사항은 관리자만 작성할 수 있습니다.")

    new_post = Post(
        category=post_data.category,
        title=post_data.title,
        content=post_data.content,
        tags=post_data.tags,
        is_notice=post_data.is_notice,
        images=post_data.images,
        attachments=post_data.attachments,
        author_id=current_user.id
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    post_dict = {
        "id": new_post.id,
        "category": new_post.category,
        "title": new_post.title,
        "content": new_post.content,
        "tags": new_post.tags,
        "is_notice": new_post.is_notice,
        "author_id": new_post.author_id,
        "author_username": current_user.username,
        "views": new_post.views,
        "images": new_post.images,
        "attachments": new_post.attachments,
        "comments_count": 0,
        "created_at": new_post.created_at,
        "updated_at": new_post.updated_at
    }

    return PostResponse(**post_dict)


@router.put("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    post_data: PostUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """게시글 수정"""
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    # 작성자 또는 관리자만 수정 가능
    if post.author_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="게시글을 수정할 권한이 없습니다.")

    # 업데이트
    update_data = post_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(post, key, value)

    db.commit()
    db.refresh(post)

    post_dict = {
        "id": post.id,
        "category": post.category,
        "title": post.title,
        "content": post.content,
        "tags": post.tags,
        "is_notice": post.is_notice,
        "author_id": post.author_id,
        "author_username": post.author.username if post.author else "Unknown",
        "views": post.views,
        "images": post.images,
        "attachments": post.attachments,
        "comments_count": 0,
        "created_at": post.created_at,
        "updated_at": post.updated_at
    }

    return PostResponse(**post_dict)


@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """게시글 삭제"""
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    # 작성자 또는 관리자만 삭제 가능
    if post.author_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="게시글을 삭제할 권한이 없습니다.")

    # 연관된 이미지 파일 삭제
    if post.images:
        eximage_dir = Path(settings.EXIMAGE_DIR)
        for image_path in post.images:
            try:
                # image_path는 "/static/eximage/filename.ext" 형식
                filename = Path(image_path).name
                file_path = eximage_dir / filename
                if file_path.exists():
                    file_path.unlink()
                    logger.debug(f"Delete Post] Deleted image: {file_path}")
            except Exception as e:
                logger.debug(f"Delete Post] Failed to delete image {image_path}: {e}")
                # 이미지 삭제 실패해도 게시글 삭제는 계속 진행

    db.delete(post)
    db.commit()

    return {"message": "게시글이 삭제되었습니다."}


@router.post("/upload-attachment")
async def upload_attachment(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    첨부파일 업로드
    """
    # 첨부파일 저장 디렉토리
    ATTACHMENTS_DIR = Path("/home/nuricom/project/myappStore/data/attachments")
    ATTACHMENTS_DIR.mkdir(parents=True, exist_ok=True)

    # 파일 크기 제한 (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024

    # 파일 내용 읽기
    contents = await file.read()
    file_size = len(contents)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="파일 크기는 10MB를 초과할 수 없습니다.")

    # 파일명 생성 (UUID + 원본 파일명)
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4().hex}{file_extension}"
    file_path = ATTACHMENTS_DIR / unique_filename

    # 파일 저장
    try:
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 저장 실패: {str(e)}")

    # 응답 데이터
    return {
        "filename": unique_filename,
        "original_filename": file.filename,
        "size": file_size,
        "uploaded_at": datetime.utcnow().isoformat()
    }


@router.get("/download-attachment/{filename}")
async def download_attachment(
    filename: str
):
    """
    첨부파일 다운로드
    """
    ATTACHMENTS_DIR = Path("/home/nuricom/project/myappStore/data/attachments")
    file_path = ATTACHMENTS_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream"
    )
