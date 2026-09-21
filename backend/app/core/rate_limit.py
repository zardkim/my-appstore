"""요청 속도 제한 (in-memory).

로그인·가입·공유링크처럼 **인증 없이 외부에서 두드릴 수 있는** 엔드포인트만
보호한다. 나머지는 JWT 로 막혀 있으므로 대상이 아니다.

## 왜 라이브러리를 쓰지 않았나

이 앱은 uvicorn 단일 워커로 돈다(`CMD uvicorn app.main:app`). 프로세스가
하나뿐이라 in-memory 카운터로 충분하고, slowapi 같은 의존성을 추가하면
버전 고정과 API 변화를 계속 따라가야 한다.

**워커를 여러 개로 늘리거나 백엔드를 수평 확장하면 이 구현은 무력해진다**
(워커마다 카운터가 따로 생긴다). 그때는 Redis 기반으로 바꿔야 한다.
이 앱은 이미 Redis 를 쓰고 있으므로 옮기는 것 자체는 어렵지 않다.

## 동작

고정 윈도우(fixed window) 방식이다. 윈도우 경계에서 최대 2배까지 통과할 수
있지만, 무차별 대입을 늦추는 목적에는 충분하고 구현이 단순하다.
"""
import time
import threading
from collections import defaultdict
from typing import Dict, List, Tuple

from fastapi import HTTPException, Request, status


class RateLimiter:
    """키(보통 IP)별 고정 윈도우 카운터."""

    def __init__(self, max_requests: int, window_seconds: int, name: str = ""):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.name = name
        self._hits: Dict[str, List[float]] = defaultdict(list)
        self._lock = threading.Lock()

    def check(self, key: str, now: float = None) -> Tuple[bool, int]:
        """(허용 여부, 재시도까지 남은 초) 를 돌려준다.

        허용되면 호출 기록을 남긴다.
        """
        now = time.time() if now is None else now
        cutoff = now - self.window_seconds

        with self._lock:
            hits = [t for t in self._hits[key] if t > cutoff]

            if len(hits) >= self.max_requests:
                self._hits[key] = hits
                retry_after = int(hits[0] + self.window_seconds - now) + 1
                return False, max(retry_after, 1)

            hits.append(now)
            self._hits[key] = hits

            # 오래된 키가 무한정 쌓이지 않도록 가끔 정리한다
            if len(self._hits) > 10_000:
                self._prune(cutoff)

            return True, 0

    def _prune(self, cutoff: float) -> None:
        """호출자가 락을 잡은 상태에서만 부른다."""
        for key in [k for k, v in self._hits.items() if not any(t > cutoff for t in v)]:
            del self._hits[key]

    def reset(self, key: str = None) -> None:
        with self._lock:
            if key is None:
                self._hits.clear()
            else:
                self._hits.pop(key, None)


def get_client_key(request: Request) -> str:
    """제한 기준 키. 역방향 프록시 뒤에 있으므로 X-Forwarded-For 를 먼저 본다."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    return request.client.host if request.client else "unknown"


# ── 엔드포인트별 제한 ────────────────────────────────────────────────
# 로그인은 무차별 대입 대상이므로 가장 빡빡하게 잡는다.
login_limiter = RateLimiter(max_requests=10, window_seconds=60, name="login")
# 가입/최초 설정은 자동 생성 방지 목적이라 더 길게 본다.
signup_limiter = RateLimiter(max_requests=5, window_seconds=300, name="signup")
# 공유링크는 토큰/비밀번호 추측 시도를 늦춘다.
share_limiter = RateLimiter(max_requests=30, window_seconds=60, name="share")


def _make_dependency(limiter: RateLimiter):
    async def dependency(request: Request) -> None:
        allowed, retry_after = limiter.check(get_client_key(request))
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="요청이 너무 많습니다. 잠시 후 다시 시도해주세요.",
                headers={"Retry-After": str(retry_after)},
            )
    return dependency


rate_limit_login = _make_dependency(login_limiter)
rate_limit_signup = _make_dependency(signup_limiter)
rate_limit_share = _make_dependency(share_limiter)
