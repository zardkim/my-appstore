"""
디스코드 웹훅 알림 전송

신규 앱 등록 / 기존 앱의 새 버전 추가를 디스코드 채널로 공지한다.
설정은 config.json의 general 섹션에 저장된다:
  - discordEnabled          : 알림 사용 여부
  - discordWebhookUrl       : 웹훅 URL (민감 정보, API 응답에서 마스킹됨)
  - discordNotifyNewProduct : 신규 앱 알림
  - discordNotifyNewVersion : 새 버전 알림

전송 실패가 스캔/매칭을 실패시키면 안 되므로 모든 예외는 로그만 남기고 삼킨다.
(activity_logger.log_activity와 동일한 자세)
"""
import asyncio
import ipaddress
import logging
from typing import List, Dict, Optional
from urllib.parse import urlparse

import httpx

logger = logging.getLogger(__name__)

# 웹훅으로 허용하는 호스트 (관리자 입력 URL로 서버가 요청을 보내므로 SSRF 방어)
ALLOWED_WEBHOOK_HOSTS = {
    "discord.com",
    "discordapp.com",
    "ptb.discord.com",
    "canary.discord.com",
}
WEBHOOK_PATH_PREFIX = "/api/webhooks/"

# 디스코드는 메시지당 embed 10개까지 허용
MAX_EMBEDS_PER_MESSAGE = 10
# 웹훅 rate limit(~5req/2s) 회피용 청크 간 딜레이
CHUNK_DELAY_SECONDS = 1.0
REQUEST_TIMEOUT = 10.0

COLOR_NEW_PRODUCT = 0x5865F2  # 디스코드 블러플 - 신규 앱
COLOR_NEW_VERSION = 0x57F287  # 그린 - 새 버전

# embed 필드 길이 제한 (디스코드 제한보다 넉넉히 아래로 자름)
MAX_TITLE_LEN = 240
MAX_DESC_LEN = 400


def is_valid_webhook_url(url: Optional[str]) -> bool:
    """디스코드 웹훅 URL 형식인지 검증"""
    if not url or not isinstance(url, str):
        return False
    try:
        parsed = urlparse(url.strip())
    except Exception:
        return False

    if parsed.scheme != "https":
        return False
    if (parsed.hostname or "").lower() not in ALLOWED_WEBHOOK_HOSTS:
        return False
    if not parsed.path.startswith(WEBHOOK_PATH_PREFIX):
        return False
    return True


def _truncate(text: Optional[str], limit: int) -> str:
    if not text:
        return ""
    text = str(text).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def _is_publicly_reachable(host: Optional[str]) -> bool:
    """
    디스코드 CDN이 바깥에서 가져갈 수 있는 호스트인지 대략 판정.

    localhost/사설 IP면 썸네일이 조용히 깨지므로 아예 붙이지 않는다.
    (도메인은 검증할 방법이 없으므로 통과시킨다)
    """
    if not host:
        return False
    host = host.lower()
    if host in ("localhost", "localhost.localdomain"):
        return False
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return True  # 도메인 - 공인망으로 가정
    return not (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved)


def _resolve_icon_url(icon_url: Optional[str], backend_url: str) -> Optional[str]:
    """
    embed 썸네일용 절대 URL 생성.

    디스코드 CDN이 공인망에서 직접 가져가므로, 외부에서 접근 가능한
    절대 URL을 만들 수 없으면 None을 반환해 썸네일을 생략한다.
    """
    if not icon_url:
        return None

    icon_url = icon_url.strip()

    # 이미 외부 절대 URL
    if icon_url.startswith("http://") or icon_url.startswith("https://"):
        host = urlparse(icon_url).hostname
        return icon_url if _is_publicly_reachable(host) else None

    # 로컬 캐시 경로(/static/icons/...) - backendUrl을 붙여야 함
    if icon_url.startswith("/") and backend_url:
        base = backend_url.strip().rstrip("/")
        if not _is_publicly_reachable(urlparse(base).hostname):
            return None
        return f"{base}{icon_url}"

    return None


def _build_embed(item: Dict, backend_url: str) -> Dict:
    """알림 항목 하나를 디스코드 embed로 변환 (제품 링크는 넣지 않는다)"""
    is_new_product = item.get("is_new_product", False)
    versions = item.get("versions") or []

    title = _truncate(item.get("title") or "(제목 없음)", MAX_TITLE_LEN)
    prefix = "🆕 새 앱 등록" if is_new_product else "⬆️ 새 버전 추가"

    embed: Dict = {
        "title": f"{prefix}: {title}",
        "color": COLOR_NEW_PRODUCT if is_new_product else COLOR_NEW_VERSION,
    }

    description = _truncate(item.get("description"), MAX_DESC_LEN)
    if description:
        embed["description"] = description

    fields = []
    if item.get("vendor"):
        fields.append({"name": "제조사", "value": _truncate(item["vendor"], 100), "inline": True})
    if item.get("category"):
        fields.append({"name": "카테고리", "value": _truncate(item["category"], 100), "inline": True})
    if versions:
        version_text = ", ".join(_truncate(v, 60) for v in versions[:5])
        if len(versions) > 5:
            version_text += f" 외 {len(versions) - 5}개"
        fields.append({"name": "버전", "value": _truncate(version_text, 300), "inline": False})
    if fields:
        embed["fields"] = fields

    thumbnail = _resolve_icon_url(item.get("icon_url"), backend_url)
    if thumbnail:
        embed["thumbnail"] = {"url": thumbnail}

    return embed


def get_discord_config() -> Dict:
    """config.json의 general 섹션에서 디스코드 설정 읽기.

    기존 설치의 config.json에는 이 키들이 없으므로 반드시 기본값과 함께 읽는다.
    """
    # 순환 import 방지를 위해 함수 내부에서 import
    from app.api.config import load_config

    try:
        general = load_config().get("general", {}) or {}
    except Exception as e:
        logger.warning(f"디스코드 설정 로드 실패: {e}")
        return {}

    return {
        "enabled": bool(general.get("discordEnabled", False)),
        "webhook_url": general.get("discordWebhookUrl", "") or "",
        "notify_new_product": bool(general.get("discordNotifyNewProduct", True)),
        "notify_new_version": bool(general.get("discordNotifyNewVersion", True)),
        "frontend_url": general.get("frontendUrl", "") or "",
        "backend_url": general.get("backendUrl", "") or "",
    }


async def _post_webhook(webhook_url: str, payload: Dict) -> bool:
    """웹훅 1회 전송. 성공 여부 반환."""
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        response = await client.post(webhook_url, json=payload)
        if response.status_code >= 400:
            logger.warning(
                f"디스코드 웹훅 전송 실패: HTTP {response.status_code} - {response.text[:200]}"
            )
            return False
    return True


async def send_new_items(items: List[Dict]) -> bool:
    """
    신규 등록/업데이트된 앱 목록을 디스코드로 전송.

    Args:
        items: [{id, title, description, vendor, category, icon_url,
                 is_new_product: bool, versions: [str, ...]}, ...]

    Returns:
        bool: 한 건이라도 전송했으면 True. 비활성/미설정/실패는 False.

    예외는 내부에서 모두 처리한다 - 호출자(스캔/매칭)는 절대 실패하면 안 된다.
    """
    try:
        if not items:
            return False

        config = get_discord_config()
        if not config.get("enabled"):
            return False

        webhook_url = config["webhook_url"]
        if not is_valid_webhook_url(webhook_url):
            logger.warning("디스코드 웹훅 URL이 설정되지 않았거나 형식이 올바르지 않습니다.")
            return False

        # 알림 종류별 필터링
        filtered = [
            item for item in items
            if (item.get("is_new_product") and config["notify_new_product"])
            or (not item.get("is_new_product") and config["notify_new_version"])
        ]
        if not filtered:
            return False

        embeds = [_build_embed(item, config["backend_url"]) for item in filtered]

        sent_any = False
        # 디스코드는 메시지당 embed 10개 제한 → 청크로 나눠 전송
        for i in range(0, len(embeds), MAX_EMBEDS_PER_MESSAGE):
            chunk = embeds[i:i + MAX_EMBEDS_PER_MESSAGE]
            payload = {"username": "MyApp Store", "embeds": chunk}

            try:
                if await _post_webhook(webhook_url, payload):
                    sent_any = True
            except Exception as e:
                logger.warning(f"디스코드 웹훅 전송 중 오류: {e}")

            # 마지막 청크가 아니면 rate limit 회피 딜레이
            if i + MAX_EMBEDS_PER_MESSAGE < len(embeds):
                await asyncio.sleep(CHUNK_DELAY_SECONDS)

        if sent_any:
            logger.info(f"디스코드 알림 전송 완료: {len(filtered)}건")
        return sent_any

    except Exception as e:
        logger.warning(f"디스코드 알림 전송 실패: {e}")
        return False


# 백그라운드 전송 태스크 강한 참조 유지 (GC로 중도 취소되는 것을 방지)
_background_tasks = set()


def send_new_items_background(items: List[Dict]) -> None:
    """
    send_new_items를 백그라운드 태스크로 실행한다.

    DB 커밋이 이미 끝난 시점이므로 전송을 기다릴 이유가 없다.
    await로 붙잡으면 청크가 많을 때(100개 = 10청크) 디스코드 응답 지연이
    그대로 스캔/매칭 API 응답 시간에 더해진다.
    """
    if not items:
        return
    try:
        task = asyncio.create_task(send_new_items(items))
        _background_tasks.add(task)
        task.add_done_callback(_background_tasks.discard)
    except RuntimeError:
        # 실행 중인 이벤트 루프가 없는 경우(동기 컨텍스트) - 알림만 포기
        logger.warning("실행 중인 이벤트 루프가 없어 디스코드 알림을 건너뜁니다.")


async def send_test_message() -> Dict:
    """
    설정 확인용 테스트 메시지 전송.

    브라우저는 마스킹된 값만 갖고 있으므로 반드시 서버에 저장된 웹훅을 사용한다.

    Returns:
        {"success": bool, "message": str}
    """
    config = get_discord_config()
    webhook_url = config.get("webhook_url", "")

    if not webhook_url:
        return {"success": False, "message": "웹훅 URL이 설정되지 않았습니다."}

    if not is_valid_webhook_url(webhook_url):
        return {
            "success": False,
            "message": "올바른 디스코드 웹훅 URL이 아닙니다. (https://discord.com/api/webhooks/... 형식)",
        }

    payload = {
        "username": "MyApp Store",
        "embeds": [{
            "title": "✅ 디스코드 알림 테스트",
            "description": "MyApp Store 알림이 정상적으로 연결되었습니다.",
            "color": COLOR_NEW_PRODUCT,
        }],
    }

    try:
        if await _post_webhook(webhook_url, payload):
            return {"success": True, "message": "테스트 메시지를 전송했습니다."}
        return {"success": False, "message": "디스코드가 요청을 거부했습니다. 웹훅 URL을 확인해주세요."}
    except httpx.TimeoutException:
        return {"success": False, "message": "디스코드 응답 시간이 초과되었습니다."}
    except Exception as e:
        logger.warning(f"디스코드 테스트 전송 실패: {e}")
        return {"success": False, "message": f"전송 실패: {e}"}
