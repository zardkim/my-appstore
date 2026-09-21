"""AI 제공자의 사용 가능 모델 목록 조회.

## 왜 API 에서 받아오나

예전에는 설정 화면에 모델 ID 를 하드코딩해 두었다. 그러면

- 제공자가 새 모델을 내놓아도 목록에 없어서 쓸 수 없고,
- 목록은 있는데 사용자 키로는 접근 권한이 없는 모델이 섞이고,
- 모델이 폐기(deprecate)되어도 목록에 남아 선택하면 실패한다.

실제로 OpenAI 목록이 gpt-4o 계열에 머물러 있었다. 그래서 각 제공자의
모델 목록 엔드포인트를 호출해 **그 키로 실제 쓸 수 있는 모델**을 보여준다.

호출이 실패하면(키 없음, 네트워크 장애, 권한 없음) 아래 FALLBACK_MODELS 로
떨어진다. 설정 화면이 비어버리지 않게 하기 위한 것이며, 폴백을 쓰고 있다는
사실을 응답의 source 필드로 알린다.
"""
import logging
import re
from typing import Dict, List, Tuple

import httpx

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 15.0

# 조회 실패 시에만 쓰는 목록. 최신 상태를 보장하지 않는다.
FALLBACK_MODELS: Dict[str, List[str]] = {
    "openai": [
        "gpt-6-astra",
        "gpt-5.6-sol",
        "gpt-4o",
        "gpt-4o-mini",
    ],
    "gemini": [
        "gemini-3-pro-preview",
        "gemini-3-flash-preview",
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash",
    ],
    "claude": [
        "claude-fable-5-1",
        "claude-opus-5",
        "claude-sonnet-5",
        "claude-haiku-4-5-20251001",
        "claude-opus-4-8",
        "claude-sonnet-4-6",
    ],
}

# OpenAI 는 채팅 외 모델(임베딩·음성·이미지 등)도 함께 반환하므로 걸러낸다.
_OPENAI_EXCLUDE = (
    "embedding", "tts", "whisper", "audio", "realtime", "moderation",
    "transcribe", "dall-e", "image", "search", "davinci", "babbage",
    "codex-mini", "computer-use",
)


def _sort_models(ids: List[str]) -> List[str]:
    """대략 최신순. 버전 숫자를 뽑아 내림차순으로 둔다.

    제공자가 정렬 순서를 보장하지 않으므로 여기서 정리한다. 완벽한 정렬은
    불가능하고(이름 규칙이 제공자마다 다르다) "최신이 위로 오는 편" 정도를
    노린다.
    """
    def key(model_id: str):
        nums = [int(n) for n in re.findall(r"\d+", model_id)[:3]]
        nums += [0] * (3 - len(nums))
        return (-nums[0], -nums[1], -nums[2], model_id)

    return sorted(ids, key=key)


async def _list_openai(api_key: str) -> List[str]:
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        r = await client.get(
            "https://api.openai.com/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
        )
        r.raise_for_status()
        data = r.json().get("data", [])

    ids = []
    for item in data:
        mid = item.get("id", "")
        if not (mid.startswith("gpt-") or re.match(r"^o\d", mid)):
            continue
        if any(token in mid for token in _OPENAI_EXCLUDE):
            continue
        ids.append(mid)
    return _sort_models(ids)


async def _list_gemini(api_key: str) -> List[str]:
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        r = await client.get(
            "https://generativelanguage.googleapis.com/v1beta/models",
            params={"key": api_key, "pageSize": 200},
        )
        r.raise_for_status()
        models = r.json().get("models", [])

    ids = []
    for item in models:
        # 텍스트 생성이 가능한 모델만 (임베딩 등 제외)
        if "generateContent" not in (item.get("supportedGenerationMethods") or []):
            continue
        name = item.get("name", "")
        ids.append(name.split("/", 1)[-1] if "/" in name else name)
    return _sort_models(ids)


async def _list_claude(api_key: str) -> List[str]:
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        r = await client.get(
            "https://api.anthropic.com/v1/models",
            headers={"x-api-key": api_key, "anthropic-version": "2023-06-01"},
            params={"limit": 100},
        )
        r.raise_for_status()
        data = r.json().get("data", [])

    # Anthropic 은 최신순으로 내려주므로 순서를 유지한다.
    return [item["id"] for item in data if item.get("id")]


_FETCHERS = {
    "openai": _list_openai,
    "gemini": _list_gemini,
    "claude": _list_claude,
}


async def list_models(provider: str, api_key: str) -> Tuple[List[str], str, str]:
    """(모델 목록, source, 사유) 를 돌려준다.

    source 는 "api" 또는 "fallback". 폴백이면 사유 문자열이 채워진다.
    """
    provider = (provider or "").lower().strip()
    fallback = FALLBACK_MODELS.get(provider, [])

    if provider not in _FETCHERS:
        return fallback, "fallback", f"지원하지 않는 제공자입니다: {provider}"

    if not api_key or not api_key.strip():
        return fallback, "fallback", "API 키가 설정되지 않아 기본 목록을 표시합니다."

    try:
        models = await _FETCHERS[provider](api_key.strip())
    except httpx.HTTPStatusError as e:
        code = e.response.status_code
        if code == 401:
            reason = "API 키가 유효하지 않습니다."
        elif code == 403:
            reason = "이 키로는 모델 목록을 조회할 권한이 없습니다."
        elif code == 429:
            reason = "요청이 너무 많습니다. 잠시 후 다시 시도해주세요."
        else:
            reason = f"모델 목록 조회 실패 (HTTP {code})"
        logger.warning(f"[{provider}] 모델 목록 조회 실패: HTTP {code}")
        return fallback, "fallback", reason
    except Exception as e:
        logger.warning(f"[{provider}] 모델 목록 조회 중 오류: {e}")
        return fallback, "fallback", f"모델 목록을 가져오지 못했습니다: {e}"

    if not models:
        return fallback, "fallback", "사용 가능한 모델이 없어 기본 목록을 표시합니다."

    return models, "api", ""
