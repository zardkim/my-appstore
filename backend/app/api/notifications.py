"""
알림 설정 API (디스코드 웹훅)
"""
import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core import discord_notifier
from app.dependencies import get_current_admin_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()


class DiscordTestResponse(BaseModel):
    success: bool
    message: str


@router.post("/discord/test", response_model=DiscordTestResponse)
async def test_discord_webhook(
    current_user: User = Depends(get_current_admin_user)
):
    """
    디스코드 웹훅 테스트 메시지 전송 (관리자 전용).

    브라우저에는 마스킹된 값("***")만 내려가므로, 반드시 서버에 저장된
    웹훅 URL을 사용한다. 요청 본문으로 URL을 받지 않는다.
    """
    config = discord_notifier.get_discord_config()

    if not config.get("enabled"):
        return DiscordTestResponse(
            success=False,
            message="디스코드 알림이 꺼져 있습니다. 알림을 켜고 [적용]을 눌러 저장한 뒤 테스트해주세요."
        )

    result = await discord_notifier.send_test_message()
    return DiscordTestResponse(success=result["success"], message=result["message"])


@router.get("/discord/status")
async def get_discord_status(
    current_user: User = Depends(get_current_admin_user)
):
    """
    디스코드 알림 설정 상태 조회 (관리자 전용).

    웹훅 URL 자체는 반환하지 않고 설정 여부만 알려준다.
    """
    config = discord_notifier.get_discord_config()
    webhook_url = config.get("webhook_url", "")

    return {
        "enabled": config.get("enabled", False),
        "webhook_configured": bool(webhook_url),
        "webhook_valid": discord_notifier.is_valid_webhook_url(webhook_url),
        "notify_new_product": config.get("notify_new_product", True),
        "notify_new_version": config.get("notify_new_version", True),
    }
