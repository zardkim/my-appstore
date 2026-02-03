from fastapi import APIRouter, Depends, HTTPException, Response, Query
from sqlalchemy.orm import Session
from typing import Optional
import os
from pathlib import Path
import logging

from app.database import get_db
from app.models.version import Version
from app.models.user import User
from app.dependencies import get_current_user
from app.core.security import decode_access_token
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


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
    try:
        logger.info(f"Download request for version_id: {version_id}")

        # 버전 조회
        version = db.query(Version).filter(Version.id == version_id).first()
        if not version:
            logger.error(f"Version not found: {version_id}")
            raise HTTPException(status_code=404, detail="File not found")

        logger.info(f"Version found: {version.file_name}, path: {version.file_path}")

        # 파일 존재 확인
        file_path = Path(version.file_path)
        if not file_path.exists():
            logger.error(f"Physical file not found: {version.file_path}")
            raise HTTPException(status_code=404, detail="Physical file not found")

        # 파일 크기 확인
        file_size = file_path.stat().st_size
        logger.info(f"File size: {file_size} bytes")

        # Nginx X-Accel-Redirect 사용
        # SCAN_BASE_PATH를 사용하여 동적으로 경로 변환
        # 예: /library/folder/file.exe -> /protected/folder/file.exe
        scan_base_path = settings.SCAN_BASE_PATH
        internal_path = str(file_path).replace(scan_base_path, '/protected')

        logger.info(f"Internal path for X-Accel-Redirect: {internal_path}")

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

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


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
    try:
        from fastapi.responses import FileResponse

        logger.info(f"Direct download request for version_id: {version_id}")

        # 버전 조회
        version = db.query(Version).filter(Version.id == version_id).first()
        if not version:
            logger.error(f"Version not found: {version_id}")
            raise HTTPException(status_code=404, detail="File not found")

        logger.info(f"Version found: {version.file_name}, path: {version.file_path}")

        # 파일 존재 확인
        file_path = Path(version.file_path)
        if not file_path.exists():
            logger.error(f"Physical file not found: {version.file_path}")
            raise HTTPException(status_code=404, detail="Physical file not found")

        # 파일 응답
        return FileResponse(
            path=str(file_path),
            filename=version.file_name,
            media_type='application/octet-stream'
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Direct download error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")
