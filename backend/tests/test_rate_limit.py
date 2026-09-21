"""요청 속도 제한.

인증 없이 외부에서 두드릴 수 있는 엔드포인트(로그인/가입/공유링크)만 보호한다.
"""
import pytest

from app.core.rate_limit import RateLimiter, get_client_key


class FakeRequest:
    def __init__(self, headers=None, host="1.2.3.4"):
        self.headers = headers or {}
        self.client = type("C", (), {"host": host})() if host else None


class TestRateLimiter:
    def test_한도까지는_통과한다(self):
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        for _ in range(3):
            allowed, _ = limiter.check("ip1")
            assert allowed is True

    def test_한도를_넘으면_막는다(self):
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        for _ in range(3):
            limiter.check("ip1")
        allowed, retry_after = limiter.check("ip1")
        assert allowed is False
        assert retry_after >= 1

    def test_키가_다르면_따로_센다(self):
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        limiter.check("ip1"); limiter.check("ip1")
        assert limiter.check("ip1")[0] is False
        assert limiter.check("ip2")[0] is True   # 다른 IP 는 영향 없음

    def test_윈도우가_지나면_다시_통과한다(self):
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        now = 1000.0
        limiter.check("ip1", now=now)
        limiter.check("ip1", now=now)
        assert limiter.check("ip1", now=now + 1)[0] is False
        assert limiter.check("ip1", now=now + 61)[0] is True

    def test_reset(self):
        limiter = RateLimiter(max_requests=1, window_seconds=60)
        limiter.check("ip1")
        assert limiter.check("ip1")[0] is False
        limiter.reset("ip1")
        assert limiter.check("ip1")[0] is True

    def test_동시_호출에도_한도를_넘지_않는다(self):
        import threading
        limiter = RateLimiter(max_requests=50, window_seconds=60)
        results = []

        def worker():
            for _ in range(20):
                results.append(limiter.check("shared")[0])

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # 200회 시도 중 정확히 50회만 통과해야 한다 (락이 동작하는지)
        assert sum(results) == 50


class TestClientKey:
    def test_프록시_헤더를_우선한다(self):
        # 역방향 프록시 뒤에 있으므로 request.client.host 는 프록시 IP 다
        req = FakeRequest({"x-forwarded-for": "203.0.113.7, 10.0.0.1"}, host="10.0.0.1")
        assert get_client_key(req) == "203.0.113.7"

    def test_x_real_ip_도_본다(self):
        assert get_client_key(FakeRequest({"x-real-ip": "203.0.113.9"})) == "203.0.113.9"

    def test_헤더가_없으면_소켓_주소(self):
        assert get_client_key(FakeRequest(host="198.51.100.2")) == "198.51.100.2"

    def test_클라이언트_정보가_없어도_깨지지_않는다(self):
        assert get_client_key(FakeRequest(host=None)) == "unknown"
