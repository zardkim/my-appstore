"""
Redis 기반 캐시 헬퍼
API 응답 및 통계 데이터 캐싱용
"""
import json
import hashlib
import logging
from typing import Optional, Any, Callable
from functools import wraps
import redis
from app.config import settings

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis 캐시 관리 클래스"""

    def __init__(self):
        """Redis 클라이언트 초기화"""
        try:
            self.client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # 연결 테스트
            self.client.ping()
            self.enabled = True
            logger.info(f"Connected to Redis: {settings.REDIS_URL}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}", exc_info=True)
            logger.warning("Cache will be disabled")
            self.client = None
            self.enabled = False

    def get(self, key: str) -> Optional[Any]:
        """
        캐시에서 값 가져오기

        Args:
            key: 캐시 키

        Returns:
            캐시된 값 또는 None
        """
        if not self.enabled:
            return None

        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Get error for key '{key}': {e}", exc_info=True)
            return None

    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """
        캐시에 값 저장

        Args:
            key: 캐시 키
            value: 저장할 값
            ttl: TTL (초), 기본 5분

        Returns:
            성공 여부
        """
        if not self.enabled:
            return False

        try:
            # Pydantic 모델 처리
            serialized = self._serialize_value(value)
            self.client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Set error for key '{key}': {e}", exc_info=True)
            return False

    def _serialize_value(self, value: Any) -> str:
        """
        값 직렬화 (Pydantic 모델 지원)
        """
        def convert_value(obj):
            # Pydantic v2 모델
            if hasattr(obj, 'model_dump'):
                return obj.model_dump(mode='json')
            # Pydantic v1 모델
            elif hasattr(obj, 'dict'):
                return obj.dict()
            # datetime 객체
            elif hasattr(obj, 'isoformat'):
                return obj.isoformat()
            # 일반 객체
            return str(obj)

        # dict나 list인 경우 재귀적으로 변환
        if isinstance(value, dict):
            return json.dumps({k: self._convert_for_json(v) for k, v in value.items()}, default=convert_value)
        elif isinstance(value, list):
            return json.dumps([self._convert_for_json(item) for item in value], default=convert_value)
        else:
            return json.dumps(value, default=convert_value)

    def _convert_for_json(self, obj):
        """
        JSON 직렬화를 위한 객체 변환
        """
        # Pydantic v2 모델
        if hasattr(obj, 'model_dump'):
            return obj.model_dump(mode='json')
        # Pydantic v1 모델
        elif hasattr(obj, 'dict'):
            return obj.dict()
        # datetime 객체
        elif hasattr(obj, 'isoformat'):
            return obj.isoformat()
        # dict
        elif isinstance(obj, dict):
            return {k: self._convert_for_json(v) for k, v in obj.items()}
        # list
        elif isinstance(obj, list):
            return [self._convert_for_json(item) for item in obj]
        # 기본값
        return obj

    def delete(self, key: str) -> bool:
        """
        캐시에서 값 삭제

        Args:
            key: 캐시 키

        Returns:
            성공 여부
        """
        if not self.enabled:
            return False

        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Delete error for key '{key}': {e}", exc_info=True)
            return False

    def delete_pattern(self, pattern: str) -> int:
        """
        패턴과 매칭되는 모든 키 삭제

        Args:
            pattern: 키 패턴 (예: "products:*")

        Returns:
            삭제된 키 개수
        """
        if not self.enabled:
            return 0

        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Delete pattern error for '{pattern}': {e}", exc_info=True)
            return 0

    def clear_all(self) -> bool:
        """
        모든 캐시 삭제 (주의: 전체 DB 플러시)

        Returns:
            성공 여부
        """
        if not self.enabled:
            return False

        try:
            self.client.flushdb()
            return True
        except Exception as e:
            logger.error(f"Clear all error: {e}", exc_info=True)
            return False

    def generate_key(self, prefix: str, **kwargs) -> str:
        """
        캐시 키 생성 (파라미터 기반 해싱)

        Args:
            prefix: 키 프리픽스
            **kwargs: 파라미터들

        Returns:
            생성된 캐시 키
        """
        # 파라미터를 정렬된 JSON으로 변환 후 해싱
        params_str = json.dumps(kwargs, sort_keys=True, default=str)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()
        return f"{prefix}:{params_hash}"


# 전역 캐시 인스턴스
redis_cache = RedisCache()


def cache_response(prefix: str = "api", ttl: int = 300):
    """
    API 응답 캐싱 데코레이터

    Args:
        prefix: 캐시 키 프리픽스
        ttl: TTL (초), 기본 5분

    Example:
        @cache_response(prefix="products_list", ttl=300)
        async def get_products(...):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 캐시 비활성화 시 원본 함수 실행
            if not redis_cache.enabled:
                return await func(*args, **kwargs)

            # kwargs에서 db 세션 제외 (직렬화 불가)
            cache_params = {
                k: v for k, v in kwargs.items()
                if k not in ('db', 'current_user') and not k.startswith('_')
            }

            # 캐시 키 생성
            cache_key = redis_cache.generate_key(prefix, **cache_params)

            # 캐시 조회
            try:
                cached_value = redis_cache.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache HIT: {cache_key}")
                    return cached_value
            except Exception as e:
                logger.error(f"Cache GET error {cache_key}: {e}", exc_info=True)
                # 캐시 읽기 실패 시 원본 함수 실행

            # 캐시 미스 - 원본 함수 실행
            logger.debug(f"Cache MISS: {cache_key}")
            result = await func(*args, **kwargs)

            # 결과 캐싱 (실패해도 원본 결과는 반환)
            try:
                redis_cache.set(cache_key, result, ttl)
            except Exception as e:
                logger.error(f"Cache SET error {cache_key}: {e}", exc_info=True)

            return result

        return wrapper
    return decorator


def invalidate_cache(patterns: list[str]):
    """
    캐시 무효화 헬퍼

    Args:
        patterns: 삭제할 캐시 키 패턴 리스트

    Example:
        invalidate_cache(["products:*", "stats:*"])
    """
    if not redis_cache.enabled:
        return

    for pattern in patterns:
        deleted = redis_cache.delete_pattern(pattern)
        logger.info(f"Cache INVALIDATE - Pattern '{pattern}': {deleted} keys deleted")
