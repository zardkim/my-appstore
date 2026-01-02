from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.dependencies import get_current_user
from app.models.comment import Comment
from app.models.post import Post
from app.models.user import User, UserRole
from app.schemas.comment import CommentCreate, CommentUpdate, CommentResponse

router = APIRouter()


@router.get("/{post_id}/comments", response_model=List[CommentResponse])
def get_comments(
    post_id: int,
    db: Session = Depends(get_db)
):
    """특정 게시글의 댓글 목록 조회"""
    # 게시글 존재 확인
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    # 댓글 조회
    comments = db.query(Comment).filter(Comment.post_id == post_id).order_by(Comment.created_at.asc()).all()

    result = []
    for comment in comments:
        comment_dict = {
            "id": comment.id,
            "post_id": comment.post_id,
            "author_id": comment.author_id,
            "author_username": comment.author.username if comment.author else "Unknown",
            "content": comment.content,
            "created_at": comment.created_at,
            "updated_at": comment.updated_at
        }
        result.append(CommentResponse(**comment_dict))

    return result


@router.post("/{post_id}/comments", response_model=CommentResponse)
def create_comment(
    post_id: int,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """댓글 작성"""
    # 게시글 존재 확인
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    # 댓글 생성
    new_comment = Comment(
        post_id=post_id,
        author_id=current_user.id,
        content=comment_data.content
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    comment_dict = {
        "id": new_comment.id,
        "post_id": new_comment.post_id,
        "author_id": new_comment.author_id,
        "author_username": current_user.username,
        "content": new_comment.content,
        "created_at": new_comment.created_at,
        "updated_at": new_comment.updated_at
    }

    return CommentResponse(**comment_dict)


@router.put("/comments/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """댓글 수정"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")

    # 작성자 또는 관리자만 수정 가능
    if comment.author_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="댓글을 수정할 권한이 없습니다.")

    # 업데이트
    comment.content = comment_data.content
    db.commit()
    db.refresh(comment)

    comment_dict = {
        "id": comment.id,
        "post_id": comment.post_id,
        "author_id": comment.author_id,
        "author_username": comment.author.username if comment.author else "Unknown",
        "content": comment.content,
        "created_at": comment.created_at,
        "updated_at": comment.updated_at
    }

    return CommentResponse(**comment_dict)


@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """댓글 삭제"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")

    # 작성자 또는 관리자만 삭제 가능
    if comment.author_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="댓글을 삭제할 권한이 없습니다.")

    db.delete(comment)
    db.commit()

    return {"message": "댓글이 삭제되었습니다."}
