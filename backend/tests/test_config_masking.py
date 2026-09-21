"""설정 API 의 민감정보 마스킹.

v1.4.65 회귀: 관리자 API 응답(GET /api/config/)에 AI API 키가 평문으로
노출되던 버그. 이후 SENSITIVE_FIELDS 는 관리자에게도 항상 마스킹한다.
"""
from app.api.config import mask_sensitive_fields, SENSITIVE_FIELDS


class TestSensitiveFields:
    def test_등록되어야_할_키들(self):
        for key in ("openaiApiKey", "geminiApiKey", "claudeApiKey",
                    "smtpPassword", "discordWebhookUrl"):
            assert key in SENSITIVE_FIELDS


class TestMasking:
    def test_값이_있으면_별표로_바꾼다(self):
        out = mask_sensitive_fields({"openaiApiKey": "sk-realkey"})
        assert out["openaiApiKey"] == "***"

    def test_빈_값은_빈_값으로_둔다(self):
        # 프론트가 "설정됨" 배지를 truthy 로 판단하므로 빈 값은 빈 값이어야 한다
        assert mask_sensitive_fields({"openaiApiKey": ""})["openaiApiKey"] == ""

    def test_민감하지_않은_값은_건드리지_않는다(self):
        out = mask_sensitive_fields({"language": "ko", "postsPerPage": 20})
        assert out["language"] == "ko"
        assert out["postsPerPage"] == 20

    def test_중첩_구조도_마스킹한다(self):
        out = mask_sensitive_fields({
            "metadata": {"openaiApiKey": "sk-x", "aiModel": "gpt-4o-mini"},
            "general": {"discordWebhookUrl": "https://discord.com/api/webhooks/1/s"},
        })
        assert out["metadata"]["openaiApiKey"] == "***"
        assert out["metadata"]["aiModel"] == "gpt-4o-mini"
        assert out["general"]["discordWebhookUrl"] == "***"

    def test_리스트_안의_dict_도_마스킹한다(self):
        out = mask_sensitive_fields([{"smtpPassword": "p"}, {"ok": 1}])
        assert out[0]["smtpPassword"] == "***"
        assert out[1]["ok"] == 1

    def test_원본_평문이_결과에_남지_않는다(self):
        import json
        secret = "sk-DO-NOT-LEAK"
        out = mask_sensitive_fields({"metadata": {"openaiApiKey": secret}})
        assert secret not in json.dumps(out)
