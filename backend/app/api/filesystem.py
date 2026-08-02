from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
import os
from pathlib import Path
from pydantic import BaseModel

from app.dependencies import get_current_admin_user
from app.models.user import User
from app.config import settings
from app.api.config import load_config

router = APIRouter()


def _get_allowed_roots() -> List[Path]:
    """
    브라우징이 허용된 루트 경로 목록
    SCAN_BASE_PATH뿐 아니라 config.json에 이미 등록된 스캔 폴더도 포함해,
    배포 환경마다 SCAN_BASE_PATH와 실제 등록된 폴더가 다를 수 있는 경우에도
    기존에 설정된 폴더를 계속 탐색할 수 있도록 함
    """
    roots = [Path(settings.SCAN_BASE_PATH).resolve()]
    try:
        config = load_config()
        for folder in config.get('folders', {}).get('scanFolders', []):
            try:
                roots.append(Path(folder).resolve())
            except Exception:
                continue
    except Exception:
        pass
    return roots


def _ensure_within_scan_base(candidate: Path) -> Path:
    """
    후보 경로가 허용된 루트(SCAN_BASE_PATH 또는 등록된 스캔 폴더) 하위인지 검증
    (경로 탐색 방지) 허용 범위를 벗어나면 403을 발생시킴
    """
    resolved = candidate.resolve()
    allowed_roots = _get_allowed_roots()
    for root in allowed_roots:
        if resolved == root or root in resolved.parents:
            return resolved

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"허용된 경로({', '.join(str(r) for r in allowed_roots)}) 밖에는 접근할 수 없습니다"
    )


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
    path: str = Query(default=None, description="탐색할 경로"),
    current_user: User = Depends(get_current_admin_user)
):
    """
    파일시스템 폴더 탐색 (관리자 전용)

    - path가 없으면 기본적으로 SCAN_BASE_PATH 폴더부터 시작
    - SCAN_BASE_PATH 하위 경로만 탐색 가능 (경로 탐색 방지)
    - 디렉토리 목록을 반환
    """
    try:
        scan_base = Path(settings.SCAN_BASE_PATH)

        # 경로 정규화
        browse_path = Path(path).resolve() if path else scan_base.resolve()

        # 경로가 존재하지 않으면 기본 경로 사용
        if not browse_path.exists():
            browse_path = scan_base.resolve()

        # 디렉토리가 아니면 부모 디렉토리 사용
        if not browse_path.is_dir():
            browse_path = browse_path.parent

        # SCAN_BASE_PATH 하위인지 검증 (경로 탐색 방지)
        browse_path = _ensure_within_scan_base(browse_path)

        # 읽기 권한 확인
        if not os.access(browse_path, os.R_OK):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="폴더에 접근할 수 없습니다"
            )

        # 부모 경로 계산 (SCAN_BASE_PATH 루트에서는 상위로 나가지 않음)
        parent_path = None
        if browse_path != scan_base.resolve() and browse_path != browse_path.parent:
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
        dir_path = Path(path).resolve()

        # SCAN_BASE_PATH 하위인지 검증 (경로 탐색 방지)
        _ensure_within_scan_base(dir_path)

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
