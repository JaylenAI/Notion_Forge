"""보안 미들웨어 테스트 — RateLimitMiddleware, RequestIdMiddleware, sanitize_error"""

import time

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.middleware import RateLimitMiddleware, sanitize_error
from app.main import app


@pytest.fixture
def async_client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://testserver")


class TestSanitizeError:
    """sanitize_error 함수 단위 테스트"""

    def test_include_details_returns_truncated(self):
        long_msg = "A" * 1000
        error = Exception(long_msg)
        result = sanitize_error(error, include_details=True)
        assert len(result) == 500
        assert result == long_msg[:500]

    def test_include_details_short_message(self):
        error = Exception("짧은 에러")
        result = sanitize_error(error, include_details=True)
        assert result == "짧은 에러"

    def test_sensitive_traceback_pattern(self):
        error = Exception("Traceback (most recent call last):\n  File ...")
        result = sanitize_error(error, include_details=False)
        assert result == "처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."

    def test_sensitive_file_pattern(self):
        error = Exception('File "/app/main.py", line 42, in func')
        result = sanitize_error(error, include_details=False)
        assert result == "처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."

    def test_sensitive_sqlalchemy_pattern(self):
        error = Exception("sqlalchemy.exc.OperationalError: could not connect")
        result = sanitize_error(error, include_details=False)
        assert result == "처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."

    def test_sensitive_psycopg_pattern(self):
        error = Exception("psycopg2.errors.UniqueViolation")
        result = sanitize_error(error, include_details=False)
        assert result == "처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."

    def test_sensitive_internal_server_pattern(self):
        error = Exception("Internal Server Error: database connection pool exhausted")
        result = sanitize_error(error, include_details=False)
        assert result == "처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."

    def test_sensitive_line_pattern(self):
        error = Exception("line 55 in module xyz")
        result = sanitize_error(error, include_details=False)
        assert result == "처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."

    def test_long_non_sensitive_error_truncated(self):
        long_msg = "네트워크 에러 " * 50
        error = Exception(long_msg)
        result = sanitize_error(error, include_details=False)
        assert len(result) == 200
        assert result == long_msg[:200]

    def test_short_non_sensitive_error_returned_as_is(self):
        msg = "요청 형식이 잘못되었습니다."
        error = Exception(msg)
        result = sanitize_error(error, include_details=False)
        assert result == msg

    def test_case_insensitive_pattern_matching(self):
        error = Exception("TRACEBACK information leaked")
        result = sanitize_error(error, include_details=False)
        assert result == "처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."

    def test_empty_error_message(self):
        error = Exception("")
        result = sanitize_error(error, include_details=False)
        assert result == ""


class TestRateLimitMiddleware:
    """RateLimitMiddleware 통합 테스트 — ASGI transport 사용"""

    async def test_requests_under_limit_pass(self, async_client):
        """요청 제한 미만이면 정상 통과"""
        response = await async_client.get("/health")
        assert response.status_code == 200

    async def test_health_endpoint_exempt(self, async_client):
        """/health 엔드포인트는 rate limit 면제"""
        for _ in range(100):
            response = await async_client.get("/health")
            assert response.status_code == 200

    async def test_docs_endpoint_exempt(self, async_client):
        """/docs 엔드포인트는 rate limit 면제"""
        response = await async_client.get("/docs")
        assert response.status_code == 200

    async def test_rate_limit_exceeded_returns_429(self, async_client):
        """요청 한도 초과 시 429 반환"""
        # 낮은 RPM으로 미들웨어를 직접 테스트
        from fastapi import FastAPI
        from fastapi.responses import PlainTextResponse

        test_app = FastAPI()

        @test_app.get("/test")
        async def test_endpoint():
            return PlainTextResponse("ok")

        test_app.add_middleware(RateLimitMiddleware, rpm=5)

        transport = ASGITransport(app=test_app)
        client = AsyncClient(transport=transport, base_url="http://testserver")

        # 5 요청은 통과해야 함
        for i in range(5):
            resp = await client.get("/test")
            assert resp.status_code == 200, f"Request {i + 1} failed with {resp.status_code}"

        # 6번째 요청은 429
        resp = await client.get("/test")
        assert resp.status_code == 429

        data = resp.json()
        assert "retry_after" in data
        assert "Retry-After" in resp.headers

        await client.aclose()

    async def test_retry_after_header_value(self, async_client):
        """Retry-After 헤더 값이 양수"""
        from fastapi import FastAPI
        from fastapi.responses import PlainTextResponse

        test_app = FastAPI()

        @test_app.get("/test")
        async def test_endpoint():
            return PlainTextResponse("ok")

        test_app.add_middleware(RateLimitMiddleware, rpm=2)

        transport = ASGITransport(app=test_app)
        client = AsyncClient(transport=transport, base_url="http://testserver")

        # 2 요청 통과
        await client.get("/test")
        await client.get("/test")

        # 3번째 요청 429
        resp = await client.get("/test")
        assert resp.status_code == 429
        retry_after = int(resp.headers["Retry-After"])
        assert retry_after >= 1

        await client.aclose()

    async def test_x_forwarded_for_ip_extraction(self, async_client):
        """X-Forwarded-For 헤더에서 IP 추출"""
        from fastapi import FastAPI
        from fastapi.responses import PlainTextResponse

        test_app = FastAPI()

        @test_app.get("/test")
        async def test_endpoint():
            return PlainTextResponse("ok")

        test_app.add_middleware(RateLimitMiddleware, rpm=3)

        transport = ASGITransport(app=test_app)
        client = AsyncClient(transport=transport, base_url="http://testserver")

        # 다른 IP로 요청하면 각각 별도 rate limit
        for _ in range(3):
            resp = await client.get("/test", headers={"X-Forwarded-For": "1.2.3.4"})
            assert resp.status_code == 200

        for _ in range(3):
            resp = await client.get("/test", headers={"X-Forwarded-For": "5.6.7.8"})
            assert resp.status_code == 200

        # 1.2.3.4는 이제 429
        resp = await client.get("/test", headers={"X-Forwarded-For": "1.2.3.4"})
        assert resp.status_code == 429

        await client.aclose()

    async def test_x_forwarded_for_multiple_ips(self, async_client):
        """X-Forwarded-For에 여러 IP가 있으면 첫 번째만 사용"""
        from fastapi import FastAPI
        from fastapi.responses import PlainTextResponse

        test_app = FastAPI()

        @test_app.get("/test")
        async def test_endpoint():
            return PlainTextResponse("ok")

        test_app.add_middleware(RateLimitMiddleware, rpm=2)

        transport = ASGITransport(app=test_app)
        client = AsyncClient(transport=transport, base_url="http://testserver")

        # 같은 첫 번째 IP: 같은 rate limit bucket
        await client.get("/test", headers={"X-Forwarded-For": "10.0.0.1, 192.168.1.1"})
        await client.get("/test", headers={"X-Forwarded-For": "10.0.0.1, 172.16.0.1"})

        resp = await client.get("/test", headers={"X-Forwarded-For": "10.0.0.1, 8.8.8.8"})
        assert resp.status_code == 429

        await client.aclose()


class TestRateLimitCleanup:
    """Rate limit 내부 cleanup 로직 테스트"""

    def test_cleanup_old_entries(self):
        """60초 이상 지난 엔트리가 정리되는지 확인"""
        from starlette.applications import Starlette

        dummy_app = Starlette()
        middleware = RateLimitMiddleware(dummy_app, rpm=60)

        now = time.time()
        old_time = now - 120  # 2분 전

        middleware._requests["old-ip"] = [old_time, old_time + 1, old_time + 2]
        middleware._requests["recent-ip"] = [now - 10, now - 5, now]
        middleware._last_cleanup = now - 61  # cleanup 트리거

        middleware._cleanup_old_entries()

        assert "old-ip" not in middleware._requests
        assert "recent-ip" in middleware._requests
        assert len(middleware._requests["recent-ip"]) == 3

    def test_cleanup_skipped_within_60s(self):
        """마지막 cleanup 후 60초 미만이면 스킵"""
        from starlette.applications import Starlette

        dummy_app = Starlette()
        middleware = RateLimitMiddleware(dummy_app, rpm=60)

        now = time.time()
        old_time = now - 120

        middleware._requests["old-ip"] = [old_time]
        middleware._last_cleanup = now - 30  # 30초 전 cleanup

        middleware._cleanup_old_entries()

        # cleanup 스킵되어 old-ip가 남아있어야 함
        assert "old-ip" in middleware._requests

    def test_is_exempt_health_paths(self):
        """면제 경로 확인"""
        from starlette.applications import Starlette

        dummy_app = Starlette()
        middleware = RateLimitMiddleware(dummy_app)

        assert middleware._is_exempt("/health") is True
        assert middleware._is_exempt("/health/ready") is True
        assert middleware._is_exempt("/health/live") is True
        assert middleware._is_exempt("/docs") is True
        assert middleware._is_exempt("/redoc") is True
        assert middleware._is_exempt("/openapi.json") is True
        assert middleware._is_exempt("/api/test") is False
        assert middleware._is_exempt("/") is False


class TestRequestIdMiddleware:
    """RequestIdMiddleware 통합 테스트"""

    async def test_response_includes_request_id(self, async_client):
        """응답에 X-Request-ID 헤더가 포함됨"""
        response = await async_client.get("/health")
        assert "X-Request-ID" in response.headers
        assert len(response.headers["X-Request-ID"]) > 0

    async def test_client_provided_request_id_preserved(self, async_client):
        """클라이언트가 제공한 X-Request-ID가 보존됨"""
        custom_id = "my-custom-req-123"
        response = await async_client.get("/health", headers={"X-Request-ID": custom_id})
        assert response.headers["X-Request-ID"] == custom_id

    async def test_generated_request_id_format(self, async_client):
        """자동 생성된 X-Request-ID는 12자 UUID 형식"""
        response = await async_client.get("/health")
        request_id = response.headers["X-Request-ID"]
        # uuid4()[:12] 형태
        assert len(request_id) == 12

    async def test_different_requests_get_different_ids(self, async_client):
        """서로 다른 요청은 서로 다른 ID를 받음"""
        resp1 = await async_client.get("/health")
        resp2 = await async_client.get("/health")
        id1 = resp1.headers["X-Request-ID"]
        id2 = resp2.headers["X-Request-ID"]
        assert id1 != id2
