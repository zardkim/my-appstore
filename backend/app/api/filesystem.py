from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
import os
from pathlib import Path
from pydantic import BaseModel

from app.dependencies import get_current_admin_user
from app.models.user import User

router = APIRouter()


class DirectoryItem(BaseModel):
    """디렉토리 아이템 정보"""
    name: str
    path: str
    is_dir: bool
    is_readable: bool
    size: Optional[int] = None


class BrowseResponse(BaseModel):
    """폴더 탐색 응답"""
    current_path: str
    parent_path: Optional[str] = None
    items: List[DirectoryItem]


@router.get("/browse", response_model=BrowseResponse)
async def browse_filesystem(
    path: str = Query(default="/library", description="탐색할 경로"),
    current_user: User = Depends(get_current_admin_user)
):
    """
    파일시스템 폴더 탐색 (관리자 전용)

    - path가 없으면 기본적으로 /library 폴더부터 시작
    - 디렉토리 목록을 반환
    """
    try:
        # 경로 정규화
        browse_path = Path(path).resolve()

        # 경로가 존재하지 않으면 기본 경로 사용
        if not browse_path.exists():
            browse_path = Path("/library")
            if not browse_path.exists():
                # /library도 없으면 홈 디렉토리 사용
                browse_path = Path.home()

        # 디렉토리가 아니면 부모 디렉토리 사용
        if not browse_path.is_dir():
            browse_path = browse_path.parent

        # 읽기 권한 확인
        if not os.access(browse_path, os.R_OK):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="폴더에 접근할 수 없습니다"
            )

        # 부모 경로 계산
        parent_path = None
        if browse_path != browse_path.parent:
            parent_path = str(browse_path.parent)

        # 디렉토리 내용 읽기
        items = []
        try:
            with os.scandir(browse_path) as entries:
                for entry in entries:
                    try:
                        # 숨김 파일은 표시하지 않음 (선택사항)
                        if entry.name.startswith('.'):
                            continue

                        is_dir = entry.is_dir(follow_symlinks=False)
                        is_readable = os.access(entry.path, os.R_OK)

                        # 디렉토리만 표시하거나 모든 파일을 표시할 수 있음
                        # 현재는 디렉토리만 표시
                        if not is_dir:
                            continue

                        size = None
                        if not is_dir:
                            try:
                                size = entry.stat(follow_symlinks=False).st_size
                            except:
                                pass

                        items.append(DirectoryItem(
                            name=entry.name,
                            path=entry.path,
                            is_dir=is_dir,
                            is_readable=is_readable,
                            size=size
                        ))
                    except (PermissionError, OSError):
                        # 접근할 수 없는 항목은 건너뜀
                        continue
        except PermissionError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="폴더 내용을 읽을 수 없습니다"
            )

        # 디렉토리를 이름순으로 정렬
        items.sort(key=lambda x: (not x.is_dir, x.name.lower()))

        return BrowseResponse(
            current_path=str(browse_path),
            parent_path=parent_path,
            items=items
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"폴더 탐색 중 오류 발생: {str(e)}"
        )


@router.post("/create-directory")
async def create_directory(
    path: str = Query(..., description="생성할 디렉토리 경로"),
    current_user: User = Depends(get_current_admin_user)
):
    """
    새 디렉토리 생성 (관리자 전용)
    """
    try:
        dir_path = Path(path)

        if dir_path.exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 존재하는 경로입니다"
            )

        # 부모 디렉토리가 존재하는지 확인
        if not dir_path.parent.exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="부모 디렉토리가 존재하지 않습니다"
            )

        # 디렉토리 생성
        dir_path.mkdir(parents=False, exist_ok=False)

        return {"message": "디렉토리가 생성되었습니다", "path": str(dir_path)}

    except HTTPException:
        raise
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="디렉토리를 생성할 권한이 없습니다"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"디렉토리 생성 중 오류 발생: {str(e)}"
        )
