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
    # OpenAI 는 키가 없으면 이 목록이 보인다. 키를 넣으면 실제 사용 가능한
    # 전체 목록(gpt-4.x 포함)이 API 에서 내려온다.
    "openai": [
        "gpt-6-astra",
        "gpt-5.6-sol",
        "gpt-4.1",
        "gpt-4.1-mini",
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4",
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


# 텍스트 생성용이 아닌 모델. 이름에 이 조각이 들어가면 목록에서 뺀다.
# 제공자는 generateContent 를 지원한다고 표시하지만, 음성/이미지/음악 전용
# 모델이라 메타데이터 생성에는 쓸 수 없다.
_NON_TEXT_TOKENS = (
    "-tts", "tts-", "transcribe", "-image", "image-", "-audio", "audio-",
    "computer-use", "robotics", "lyria", "nano-banana", "veo-", "imagen",
    "embedding", "-live", "deep-research", "antigravity",
)


def _is_text_model(model_id: str) -> bool:
    mid = model_id.lower()
    return not any(token in mid for token in _NON_TEXT_TOKENS)


def _sort_models(ids: List[str], prefer_prefix: str = "") -> List[str]:
    """제공자의 주력 계열을 먼저, 그 안에서 버전이 높은 것을 먼저.

    제공자가 정렬 순서를 보장하지 않는다. 그냥 버전 숫자만으로 정렬하면
    날짜가 들어간 이름(deep-research-pro-preview-12-2025)이 위로 올라와
    정작 쓸 모델이 아래로 밀린다. 그래서 두 단계로 정렬한다.

      1) prefer_prefix 로 시작하는 것(gemini- / gpt-)을 먼저
      2) 그 안에서 버전 숫자 내림차순 (4자리 숫자는 연도로 보고 제외)
    """
    def key(model_id: str):
        family = 0 if (prefer_prefix and model_id.startswith(prefer_prefix)) else 1
        # 4자리 이상은 연도·날짜로 보고 버전에서 제외한다 (2025, 20251001 …)
        nums = [int(n) for n in re.findall(r"\d+", model_id) if len(n) < 4][:3]
        nums += [0] * (3 - len(nums))
        return (family, -nums[0], -nums[1], -nums[2], model_id)

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
        if not _is_text_model(mid):
            continue
        ids.append(mid)
    return _sort_models(ids, prefer_prefix="gpt-")


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
        mid = name.split("/", 1)[-1] if "/" in name else name
        # generateContent 를 지원한다고 표시돼도 음성/이미지/음악 전용 모델이
        # 섞여 온다. 메타데이터 생성에 쓸 수 없으므로 뺀다.
        if not _is_text_model(mid):
            continue
        ids.append(mid)
    return _sort_models(ids, prefer_prefix="gemini-")


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
    return [item["id"] for item in data if item.get("id") and _is_text_model(item["id"])]


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
