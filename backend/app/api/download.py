from fastapi import APIRouter, Depends, HTTPException, Response, Query
from sqlalchemy.orm import Session
from typing import Optional
import os
from pathlib import Path

from app.database import get_db
from app.models.version import Version
from app.models.user import User
from app.dependencies import get_current_user
from app.core.security import decode_access_token

router = APIRouter()


async def get_user_from_token(
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db)
) -> User:
    """
    쿼리 파라미터에서 토큰을 읽어 사용자 인증
    다운로드 엔드포인트 전용 (window.open 사용 시 Authorization 헤더 전달 불가)
    """
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )

    # JWT 토큰 검증
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )

    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user


@router.get("/{version_id}")
async def download_file(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_from_token)
):
    """
    파일 다운로드 (Nginx X-Accel-Redirect 사용)

    Args:
        version_id: 버전 ID
        token: JWT 토큰 (쿼리 파라미터)

    Returns:
        X-Accel-Redirect 헤더로 Nginx가 파일을 전송
    """
    # 버전 조회
    version = db.query(Version).filter(Version.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="File not found")

    # 파일 존재 확인
    file_path = Path(version.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Physical file not found")

    # 파일 크기 확인
    file_size = file_path.stat().st_size

    # Nginx X-Accel-Redirect 사용
    # Nginx 설정에서 /protected/ 경로를 실제 파일 경로로 매핑 필요
    # 예: location /protected/ { internal; alias /mnt/software/; }

    # 내부 경로 생성
    # /mnt/software/folder/file.exe -> /protected/folder/file.exe
    internal_path = str(file_path).replace('/mnt/software', '/protected')

    # 파일명에서 특수문자 처리 (URL 인코딩)
    import urllib.parse
    safe_filename = urllib.parse.quote(version.file_name)

    return Response(
        status_code=200,
        headers={
            'X-Accel-Redirect': internal_path,
            'Content-Disposition': f'attachment; filename="{safe_filename}"',
            'Content-Type': 'application/octet-stream',
            'Content-Length': str(file_size)
        }
    )


@router.get("/direct/{version_id}")
async def download_file_direct(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_from_token)
):
    """
    직접 다운로드 (Nginx 없이 FastAPI로 스트리밍)
    개발 환경이나 작은 파일용

    Args:
        version_id: 버전 ID
        token: JWT 토큰 (쿼리 파라미터)
    """
    from fastapi.responses import FileResponse

    # 버전 조회
    version = db.query(Version).filter(Version.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="File not found")

    # 파일 존재 확인
    file_path = Path(version.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Physical file not found")

    # 파일 응답
    return FileResponse(
        path=str(file_path),
        filename=version.file_name,
        media_type='application/octet-stream'
    )
