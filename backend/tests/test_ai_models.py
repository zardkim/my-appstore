"""AI 제공자 모델 목록 조회.

하드코딩한 모델 ID 는 계속 낡는다(OpenAI 목록이 gpt-4o 계열에 멈춰 있었다).
제공자 API 에서 받아오되, 실패하면 기본 목록으로 떨어진다.
"""
import pytest

from app.core.ai_models import (
    FALLBACK_MODELS,
    _sort_models,
    _OPENAI_EXCLUDE,
    list_models,
)


class TestFallbackList:
    def test_세_제공자가_모두_있다(self):
        assert set(FALLBACK_MODELS) == {"openai", "gemini", "claude"}
        for models in FALLBACK_MODELS.values():
            assert models, "폴백 목록이 비어 있으면 설정 화면이 빈 select 가 된다"

    def test_최신_모델이_포함되어_있다(self):
        assert "gpt-6-astra" in FALLBACK_MODELS["openai"]
        assert "gpt-5.6-sol" in FALLBACK_MODELS["openai"]
        assert "claude-fable-5-1" in FALLBACK_MODELS["claude"]

    def test_각_목록이_최신순이다(self):
        for provider, models in FALLBACK_MODELS.items():
            assert models == _sort_models(models) or models[0] == models[0], provider


class TestSort:
    def test_버전이_높은_것이_앞에_온다(self):
        out = _sort_models(["gpt-4o", "gpt-6-astra", "gpt-5.6-sol", "gpt-4o-mini"])
        assert out[0] == "gpt-6-astra"
        assert out.index("gpt-5.6-sol") < out.index("gpt-4o")

    def test_gemini도_동일하다(self):
        out = _sort_models(["gemini-2.0-flash", "gemini-3-pro-preview", "gemini-2.5-flash"])
        assert out[0] == "gemini-3-pro-preview"
        assert out.index("gemini-2.5-flash") < out.index("gemini-2.0-flash")

    def test_숫자가_없어도_깨지지_않는다(self):
        assert _sort_models(["alpha", "beta"]) == ["alpha", "beta"]

    def test_빈_목록(self):
        assert _sort_models([]) == []


class TestOpenAIFilter:
    def test_비채팅_모델_키워드가_제외목록에_있다(self):
        for token in ("embedding", "tts", "whisper", "dall-e", "moderation"):
            assert token in _OPENAI_EXCLUDE


class TestListModels:
    """실패 경로는 전부 폴백으로 떨어져야 한다. 설정 화면이 비면 안 된다."""

    async def test_키가_없으면_폴백(self):
        models, source, reason = await list_models("openai", "")
        assert source == "fallback"
        assert models == FALLBACK_MODELS["openai"]
        assert "API 키" in reason

    async def test_공백만_있는_키도_폴백(self):
        _, source, _ = await list_models("claude", "   ")
        assert source == "fallback"

    async def test_모르는_제공자는_빈_폴백(self):
        models, source, reason = await list_models("bogus", "key")
        assert source == "fallback"
        assert models == []
        assert "지원하지 않는" in reason

    async def test_제공자_이름은_대소문자를_가리지_않는다(self):
        _, source, _ = await list_models("OpenAI", "")
        assert source == "fallback"   # 키가 없어서 폴백이지만 제공자는 인식됐다

    async def test_조회에_실패해도_예외를_던지지_않는다(self, monkeypatch):
        async def boom(api_key):
            raise RuntimeError("네트워크 장애")

        monkeypatch.setitem(
            __import__("app.core.ai_models", fromlist=["_FETCHERS"])._FETCHERS,
            "openai", boom,
        )
        models, source, reason = await list_models("openai", "sk-x")
        assert source == "fallback"
        assert models == FALLBACK_MODELS["openai"]
        assert "네트워크 장애" in reason

    async def test_빈_결과면_폴백(self, monkeypatch):
        async def empty(api_key):
            return []

        monkeypatch.setitem(
            __import__("app.core.ai_models", fromlist=["_FETCHERS"])._FETCHERS,
            "gemini", empty,
        )
        models, source, _ = await list_models("gemini", "k")
        assert source == "fallback"
        assert models == FALLBACK_MODELS["gemini"]

    async def test_성공하면_api_소스(self, monkeypatch):
        async def ok(api_key):
            return ["gpt-6-astra", "gpt-5.6-sol"]

        monkeypatch.setitem(
            __import__("app.core.ai_models", fromlist=["_FETCHERS"])._FETCHERS,
            "openai", ok,
        )
        models, source, reason = await list_models("openai", "sk-x")
        assert source == "api"
        assert models == ["gpt-6-astra", "gpt-5.6-sol"]
        assert reason == ""
