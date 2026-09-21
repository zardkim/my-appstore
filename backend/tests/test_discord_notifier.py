"""디스코드 웹훅 알림 (v1.4.69 도입, v1.4.70 에서 링크 제거)."""
import pytest

from app.core import discord_notifier as d


class TestWebhookUrlValidation:
    """서버가 관리자 입력 URL 로 요청을 보내므로 호스트를 화이트리스트로 막는다."""

    @pytest.mark.parametrize("url", [
        "https://discord.com/api/webhooks/123/abc",
        "https://discordapp.com/api/webhooks/1/x",
        "https://canary.discord.com/api/webhooks/1/x",
    ])
    def test_허용(self, url):
        assert d.is_valid_webhook_url(url) is True

    @pytest.mark.parametrize("url", [
        "http://discord.com/api/webhooks/1/x",      # https 아님
        "https://evil.com/api/webhooks/1/x",        # 호스트 불일치
        "https://discord.com/api/oauth2/token",     # 웹훅 경로 아님
        "https://discord.com.evil.com/api/webhooks/1/x",
        "",
        None,
    ])
    def test_차단(self, url):
        assert d.is_valid_webhook_url(url) is False


class TestIconUrl:
    """썸네일은 디스코드 CDN 이 공인망에서 가져간다.

    로컬/사설 주소면 조용히 깨지므로 아예 붙이지 않는다.
    """

    def test_외부_절대주소는_그대로(self):
        assert d._resolve_icon_url("https://cdn.example.com/a.png", "") == "https://cdn.example.com/a.png"

    def test_로컬경로는_백엔드주소를_붙인다(self):
        assert d._resolve_icon_url("/static/icons/a.png", "https://store.example.com") == \
            "https://store.example.com/static/icons/a.png"

    @pytest.mark.parametrize("icon,backend", [
        ("/static/icons/a.png", "http://localhost:8110"),
        ("/static/icons/a.png", "http://192.168.0.5:8110"),
        ("http://127.0.0.1/a.png", ""),
        (None, "https://store.example.com"),
    ])
    def test_도달_불가하면_생략한다(self, icon, backend):
        assert d._resolve_icon_url(icon, backend) is None


class TestEmbed:
    def _item(self, **kw):
        base = {"id": 7, "title": "Photoshop 2024", "vendor": "Adobe",
                "category": "Graphics", "is_new_product": True, "versions": ["25.0"]}
        base.update(kw)
        return base

    def test_링크를_넣지_않는다(self):
        # v1.4.70: 사용자 요청으로 제품 링크 제거
        embed = d._build_embed(self._item(), "https://store.example.com")
        assert "url" not in embed

    def test_신규앱과_새버전의_제목이_다르다(self):
        new = d._build_embed(self._item(is_new_product=True), "")
        upd = d._build_embed(self._item(is_new_product=False), "")
        assert new["title"] != upd["title"]
        assert new["color"] != upd["color"]

    def test_버전이_많으면_잘라서_표시한다(self):
        embed = d._build_embed(self._item(versions=[f"{i}.0" for i in range(10)]), "")
        version_field = next(f for f in embed["fields"] if f["name"] == "버전")
        assert "외 5개" in version_field["value"]

    def test_긴_제목은_잘린다(self):
        embed = d._build_embed(self._item(title="X" * 500), "")
        assert len(embed["title"]) <= d.MAX_TITLE_LEN + 20

    def test_제목이_없어도_깨지지_않는다(self):
        embed = d._build_embed({"id": 1, "is_new_product": True}, "")
        assert embed["title"]


class TestSendGuards:
    async def test_비활성이면_보내지_않는다(self, monkeypatch):
        monkeypatch.setattr(d, "get_discord_config", lambda: {"enabled": False})
        assert await d.send_new_items([{"id": 1, "title": "x", "is_new_product": True}]) is False

    async def test_빈_목록이면_보내지_않는다(self):
        assert await d.send_new_items([]) is False

    async def test_웹훅이_잘못되면_보내지_않는다(self, monkeypatch):
        monkeypatch.setattr(d, "get_discord_config", lambda: {
            "enabled": True, "webhook_url": "https://evil.com/x",
            "notify_new_product": True, "notify_new_version": True,
            "frontend_url": "", "backend_url": ""})
        assert await d.send_new_items([{"id": 1, "title": "x", "is_new_product": True}]) is False

    async def test_알림_종류별로_걸러낸다(self, monkeypatch):
        sent = []

        async def fake_post(url, payload):
            sent.append(payload)
            return True

        monkeypatch.setattr(d, "_post_webhook", fake_post)
        monkeypatch.setattr(d, "CHUNK_DELAY_SECONDS", 0)
        monkeypatch.setattr(d, "get_discord_config", lambda: {
            "enabled": True, "webhook_url": "https://discord.com/api/webhooks/1/a",
            "notify_new_product": True, "notify_new_version": False,
            "frontend_url": "", "backend_url": ""})

        await d.send_new_items([
            {"id": 1, "title": "새앱", "is_new_product": True, "versions": []},
            {"id": 2, "title": "새버전", "is_new_product": False, "versions": ["2.0"]},
        ])
        titles = [e["title"] for p in sent for e in p["embeds"]]
        assert len(titles) == 1
        assert "새앱" in titles[0]

    async def test_embed_는_10개씩_나눠_보낸다(self, monkeypatch):
        sent = []

        async def fake_post(url, payload):
            sent.append(payload)
            return True

        monkeypatch.setattr(d, "_post_webhook", fake_post)
        monkeypatch.setattr(d, "CHUNK_DELAY_SECONDS", 0)
        monkeypatch.setattr(d, "get_discord_config", lambda: {
            "enabled": True, "webhook_url": "https://discord.com/api/webhooks/1/a",
            "notify_new_product": True, "notify_new_version": True,
            "frontend_url": "", "backend_url": ""})

        items = [{"id": i, "title": f"App{i}", "is_new_product": True, "versions": []}
                 for i in range(25)]
        await d.send_new_items(items)
        assert [len(p["embeds"]) for p in sent] == [10, 10, 5]

    async def test_전송이_터져도_예외를_밖으로_내지_않는다(self, monkeypatch):
        """스캔/매칭이 알림 때문에 실패하면 안 된다."""
        async def boom(url, payload):
            raise RuntimeError("네트워크 장애")

        monkeypatch.setattr(d, "_post_webhook", boom)
        monkeypatch.setattr(d, "CHUNK_DELAY_SECONDS", 0)
        monkeypatch.setattr(d, "get_discord_config", lambda: {
            "enabled": True, "webhook_url": "https://discord.com/api/webhooks/1/a",
            "notify_new_product": True, "notify_new_version": True,
            "frontend_url": "", "backend_url": ""})

        assert await d.send_new_items([{"id": 1, "title": "x", "is_new_product": True}]) is False
