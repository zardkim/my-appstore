"""
캐쉬 관리 API (Admin only)
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.dependencies import get_current_admin_user
from app.core.redis_cache import redis_cache

router = APIRouter()


class CacheStatsResponse(BaseModel):
    """캐쉬 통계 응답"""
    enabled: bool
    redis_url: str
    total_keys: int
    memory_used: Optional[str] = None
    uptime_seconds: Optional[int] = None


class ClearCacheRequest(BaseModel):
    """캐쉬 삭제 요청"""
    pattern: Optional[str] = "*"  # 삭제할 키 패턴


@router.get("/stats", response_model=CacheStatsResponse)
async def get_cache_stats(
    current_user = Depends(get_current_admin_user)
):
    """
    캐쉬 통계 조회 (Admin only)

    Returns:
        캐쉬 상태 및 통계 정보
    """
    if not redis_cache.enabled:
        return {
            "enabled": False,
            "redis_url": "N/A",
            "total_keys": 0,
            "memory_used": None,
            "uptime_seconds": None
        }

    try:
        # Redis 정보 조회
        info = redis_cache.client.info()
        total_keys = redis_cache.client.dbsize()

        return {
            "enabled": True,
            "redis_url": str(redis_cache.client.connection_pool.connection_kwargs.get('host', 'N/A')),
            "total_keys": total_keys,
            "memory_used": info.get('used_memory_human', 'N/A'),
            "uptime_seconds": info.get('uptime_in_seconds', 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"캐쉬 통계 조회 실패: {str(e)}")


@router.post("/clear")
async def clear_cache(
    request: ClearCacheRequest,
    current_user = Depends(get_current_admin_user)
):
    """
    캐쉬 삭제 (Admin only)

    Args:
        request: 삭제할 키 패턴 (기본값: "*" - 전체 삭제)

    Returns:
        삭제된 키 개수
    """
    if not redis_cache.enabled:
        return {
            "success": False,
            "message": "Redis 캐쉬가 비활성화되어 있습니다.",
            "deleted_count": 0
        }

    try:
        if request.pattern == "*":
            # 전체 캐쉬 삭제
            redis_cache.clear_all()
            return {
                "success": True,
                "message": "모든 캐쉬가 삭제되었습니다.",
                "pattern": "*"
            }
        else:
            # 패턴에 맞는 캐쉬만 삭제
            deleted_count = redis_cache.delete_pattern(request.pattern)
            return {
                "success": True,
                "message": f"{deleted_count}개의 캐쉬 항목이 삭제되었습니다.",
                "pattern": request.pattern,
                "deleted_count": deleted_count
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"캐쉬 삭제 실패: {str(e)}")


@router.get("/keys")
async def list_cache_keys(
    pattern: str = "*",
    limit: int = 100,
    current_user = Depends(get_current_admin_user)
):
    """
    캐쉬 키 목록 조회 (Admin only)

    Args:
        pattern: 검색할 키 패턴 (기본값: "*")
        limit: 최대 반환 개수 (기본값: 100)

    Returns:
        캐쉬 키 목록
    """
    if not redis_cache.enabled:
        return {
            "enabled": False,
            "keys": []
        }

    try:
        keys = redis_cache.client.keys(pattern)

        # 제한된 개수만 반환
        limited_keys = keys[:limit] if len(keys) > limit else keys

        return {
            "enabled": True,
            "total_keys": len(keys),
            "returned_keys": len(limited_keys),
            "keys": limited_keys
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"캐쉬 키 조회 실패: {str(e)}")
