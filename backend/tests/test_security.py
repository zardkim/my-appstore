"""인증 기반 함수. 여기가 깨지면 로그인 전체가 깨진다."""
import pytest

from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
)


class TestPassword:
    def test_해시는_원문을_담지_않는다(self):
        h = get_password_hash("pw1234")
        assert "pw1234" not in h

    def test_같은_비밀번호도_매번_다른_해시(self):
        assert get_password_hash("pw1234") != get_password_hash("pw1234")

    def test_검증(self):
        h = get_password_hash("pw1234")
        assert verify_password("pw1234", h) is True
        assert verify_password("pw12345", h) is False
        assert verify_password("", h) is False


class TestToken:
    def test_발급한_토큰을_해석할_수_있다(self):
        payload = decode_access_token(create_access_token({"sub": "alice", "role": "admin"}))
        assert payload["sub"] == "alice"
        assert payload["role"] == "admin"
        assert "exp" in payload

    @pytest.mark.parametrize("bad", [
        "not.a.token",
        "",
        "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhbGljZSJ9.wrongsignature",
    ])
    def test_잘못된_토큰은_None(self, bad):
        assert decode_access_token(bad) is None

    def test_서명이_바뀌면_거부한다(self):
        token = create_access_token({"sub": "alice"})
        head, body, sig = token.split(".")
        tampered = f"{head}.{body}.{sig[:-2]}xx"
        assert decode_access_token(tampered) is None
