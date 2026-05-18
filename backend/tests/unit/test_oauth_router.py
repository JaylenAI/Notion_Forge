"""OAuth Router 테스트: 인증 시작/콜백/상태 확인 엔드포인트"""

import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.middleware import RateLimitMiddleware
from app.main import app
from app.routers.oauth import STATE_TTL, _exchange_codes, _pending_states


def _reset_rate_limiter():
    """앱의 RateLimitMiddleware 내부 상태 초기화"""
    for middleware in app.user_middleware:
        if middleware.cls is RateLimitMiddleware:
            break
    # ASGI 미들웨어 스택에서 직접 접근
    current = app.middleware_stack
    while current:
        if isinstance(current, RateLimitMiddleware):
            current._requests.clear()
            break
        current = getattr(current, "app", None)


@pytest.fixture
async def client():
    _reset_rate_limiter()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=False) as c:
        yield c


@pytest.fixture(autouse=True)
def clear_states():
    """각 테스트 전후로 state/exchange 저장소 초기화"""
    _pending_states.clear()
    _exchange_codes.clear()
    yield
    _pending_states.clear()
    _exchange_codes.clear()


class TestAuthorizeEndpoint:
    """GET /api/oauth/authorize"""

    async def test_authorize_missing_client_id_returns_error(self, client):
        """client_id 미설정 시 에러 메시지 반환"""
        with patch("app.routers.oauth.settings") as mock_settings:
            mock_settings.notion_oauth_client_id = ""
            mock_settings.notion_oauth_redirect_uri = "http://localhost:9500/api/oauth/callback"

            resp = await client.get("/api/oauth/authorize")

        assert resp.status_code == 200
        data = resp.json()
        assert "error" in data
        assert "NOTION_OAUTH_CLIENT_ID" in data["error"]

    async def test_authorize_generates_state_in_redirect(self, client):
        """client_id 설정 시 state 파라미터 포함 리다이렉트"""
        with patch("app.routers.oauth.settings") as mock_settings:
            mock_settings.notion_oauth_client_id = "test-client-id"
            mock_settings.notion_oauth_redirect_uri = "http://localhost:9500/api/oauth/callback"

            resp = await client.get("/api/oauth/authorize")

        assert resp.status_code == 307
        location = resp.headers["location"]
        assert "api.notion.com" in location
        assert "state=" in location
        assert "client_id=test-client-id" in location
        assert "response_type=code" in location
        # state가 _pending_states에 저장되었는지 확인
        assert len(_pending_states) == 1

    async def test_authorize_includes_redirect_uri(self, client):
        """리다이렉트 URL에 redirect_uri 파라미터 포함"""
        with patch("app.routers.oauth.settings") as mock_settings:
            mock_settings.notion_oauth_client_id = "my-client"
            mock_settings.notion_oauth_redirect_uri = "http://example.com/callback"

            resp = await client.get("/api/oauth/authorize")

        location = resp.headers["location"]
        assert "redirect_uri=http" in location

    async def test_authorize_cleans_expired_states(self, client):
        """만료된 state가 정리됨"""
        _pending_states["old-state-1"] = time.time() - STATE_TTL - 10
        _pending_states["old-state-2"] = time.time() - STATE_TTL - 100

        with patch("app.routers.oauth.settings") as mock_settings:
            mock_settings.notion_oauth_client_id = "test-client"
            mock_settings.notion_oauth_redirect_uri = "http://localhost:9500/api/oauth/callback"

            await client.get("/api/oauth/authorize")

        # 만료된 state 제거, 새 state 1개만 남음
        assert "old-state-1" not in _pending_states
        assert "old-state-2" not in _pending_states
        assert len(_pending_states) == 1


class TestCallbackEndpoint:
    """GET /api/oauth/callback"""

    async def test_callback_without_state_returns_403(self, client):
        """state 없는 콜백은 403"""
        resp = await client.get("/api/oauth/callback?code=auth-code-123")
        assert resp.status_code == 403
        data = resp.json()
        assert "CSRF" in data["detail"]

    async def test_callback_with_invalid_state_returns_403(self, client):
        """존재하지 않는 state는 403"""
        resp = await client.get("/api/oauth/callback?code=auth-code-123&state=nonexistent-state")
        assert resp.status_code == 403
        data = resp.json()
        assert "CSRF" in data["detail"]

    async def test_callback_with_expired_state_returns_403(self, client):
        """만료된 state는 403 (CSRF 또는 만료)"""
        expired_state = "expired-state-token"
        _pending_states[expired_state] = time.time() - STATE_TTL - 1

        resp = await client.get(f"/api/oauth/callback?code=auth-code&state={expired_state}")
        assert resp.status_code == 403
        data = resp.json()
        assert "CSRF" in data["detail"] or "만료" in data["detail"]

    async def test_callback_without_code_returns_400(self, client):
        """code 없는 콜백은 400"""
        valid_state = "valid-state-token"
        _pending_states[valid_state] = time.time()

        resp = await client.get(f"/api/oauth/callback?state={valid_state}")
        assert resp.status_code == 400
        data = resp.json()
        assert "없습니다" in data["detail"]

    async def test_callback_with_error_param_redirects(self, client):
        """error 파라미터 있으면 프론트엔드로 리다이렉트"""
        with patch("app.routers.oauth.settings") as mock_settings:
            mock_settings.frontend_url = "http://localhost:9501"

            resp = await client.get("/api/oauth/callback?error=access_denied")

        assert resp.status_code == 307
        location = resp.headers["location"]
        assert "oauth_error=access_denied" in location

    async def test_callback_success_token_exchange(self, client):
        """정상 콜백: state 검증 + 토큰 교환 + 일회용 코드로 리다이렉트"""
        valid_state = "valid-state-for-exchange"
        _pending_states[valid_state] = time.time()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "ntn_real_access_token_xyz",
            "workspace_name": "My Workspace",
            "workspace_id": "ws-123",
        }

        with patch("app.routers.oauth.settings") as mock_settings:
            mock_settings.notion_oauth_client_id = "client-id"
            mock_settings.notion_oauth_client_secret = "client-secret"
            mock_settings.notion_oauth_redirect_uri = "http://localhost:9500/api/oauth/callback"
            mock_settings.frontend_url = "http://localhost:9501"

            with patch("httpx.AsyncClient") as mock_http_cls:
                mock_http_instance = AsyncMock()
                mock_http_instance.post = AsyncMock(return_value=mock_response)
                mock_http_instance.__aenter__ = AsyncMock(return_value=mock_http_instance)
                mock_http_instance.__aexit__ = AsyncMock(return_value=None)
                mock_http_cls.return_value = mock_http_instance

                resp = await client.get(f"/api/oauth/callback?code=authorization-code-abc&state={valid_state}")

        assert resp.status_code == 307
        location = resp.headers["location"]
        assert "oauth_callback=true" in location
        assert "code=" in location
        assert "oauth_token" not in location
        assert valid_state not in _pending_states
        assert len(_exchange_codes) == 1

    async def test_callback_token_exchange_failure_returns_502(self, client):
        """토큰 교환 실패 시 502"""
        valid_state = "state-for-failure"
        _pending_states[valid_state] = time.time()

        mock_response = MagicMock()
        mock_response.status_code = 401

        with patch("app.routers.oauth.settings") as mock_settings:
            mock_settings.notion_oauth_client_id = "client-id"
            mock_settings.notion_oauth_client_secret = "client-secret"
            mock_settings.notion_oauth_redirect_uri = "http://localhost:9500/api/oauth/callback"
            mock_settings.frontend_url = "http://localhost:9501"

            with patch("httpx.AsyncClient") as mock_http_cls:
                mock_http_instance = AsyncMock()
                mock_http_instance.post = AsyncMock(return_value=mock_response)
                mock_http_instance.__aenter__ = AsyncMock(return_value=mock_http_instance)
                mock_http_instance.__aexit__ = AsyncMock(return_value=None)
                mock_http_cls.return_value = mock_http_instance

                resp = await client.get(f"/api/oauth/callback?code=bad-code&state={valid_state}")

        assert resp.status_code == 502
        data = resp.json()
        assert "토큰 교환" in data["detail"]

    async def test_callback_missing_client_secret_returns_500(self, client):
        """client_secret 미설정 시 500"""
        valid_state = "state-no-secret"
        _pending_states[valid_state] = time.time()

        with patch("app.routers.oauth.settings") as mock_settings:
            mock_settings.notion_oauth_client_id = ""
            mock_settings.notion_oauth_client_secret = ""
            mock_settings.frontend_url = "http://localhost:9501"

            resp = await client.get(f"/api/oauth/callback?code=some-code&state={valid_state}")

        assert resp.status_code == 500
        data = resp.json()
        assert "클라이언트 설정" in data["detail"]

    async def test_callback_state_consumed_once(self, client):
        """state는 한 번만 사용 가능 (재사용 방지)"""
        valid_state = "one-time-state"
        _pending_states[valid_state] = time.time()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "token",
            "workspace_name": "ws",
            "workspace_id": "id",
        }

        with patch("app.routers.oauth.settings") as mock_settings:
            mock_settings.notion_oauth_client_id = "cid"
            mock_settings.notion_oauth_client_secret = "csecret"
            mock_settings.notion_oauth_redirect_uri = "http://localhost:9500/api/oauth/callback"
            mock_settings.frontend_url = "http://localhost:9501"

            with patch("httpx.AsyncClient") as mock_http_cls:
                mock_http_instance = AsyncMock()
                mock_http_instance.post = AsyncMock(return_value=mock_response)
                mock_http_instance.__aenter__ = AsyncMock(return_value=mock_http_instance)
                mock_http_instance.__aexit__ = AsyncMock(return_value=None)
                mock_http_cls.return_value = mock_http_instance

                # 첫 번째 사용: 성공
                resp1 = await client.get(f"/api/oauth/callback?code=code1&state={valid_state}")
                assert resp1.status_code == 307

                # 두 번째 사용: 실패 (state 이미 소비됨)
                resp2 = await client.get(f"/api/oauth/callback?code=code2&state={valid_state}")
                assert resp2.status_code == 403


class TestExchangeEndpoint:
    """POST /api/oauth/exchange"""

    async def test_exchange_valid_code(self, client):
        """유효한 교환 코드로 토큰 수신"""
        _exchange_codes["valid-code"] = {
            "access_token": "ntn_token_abc",
            "workspace_name": "Test WS",
            "workspace_id": "ws-001",
            "created": time.time(),
        }

        resp = await client.post("/api/oauth/exchange", params={"code": "valid-code"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["oauth_token"] == "ntn_token_abc"
        assert data["workspace_name"] == "Test WS"
        assert "valid-code" not in _exchange_codes

    async def test_exchange_invalid_code(self, client):
        """존재하지 않는 코드는 400"""
        resp = await client.post("/api/oauth/exchange", params={"code": "nonexistent"})
        assert resp.status_code == 400

    async def test_exchange_expired_code(self, client):
        """만료된 교환 코드는 410"""
        _exchange_codes["expired-code"] = {
            "access_token": "ntn_old",
            "workspace_name": "WS",
            "workspace_id": "id",
            "created": time.time() - 120,
        }

        resp = await client.post("/api/oauth/exchange", params={"code": "expired-code"})
        assert resp.status_code == 410

    async def test_exchange_code_consumed_once(self, client):
        """교환 코드는 1회만 사용 가능"""
        _exchange_codes["one-time"] = {
            "access_token": "ntn_once",
            "workspace_name": "WS",
            "workspace_id": "id",
            "created": time.time(),
        }

        resp1 = await client.post("/api/oauth/exchange", params={"code": "one-time"})
        assert resp1.status_code == 200

        resp2 = await client.post("/api/oauth/exchange", params={"code": "one-time"})
        assert resp2.status_code == 400


class TestStatusEndpoint:
    """GET /api/oauth/status"""

    async def test_status_configured(self, client):
        """OAuth 설정 완료 상태"""
        with patch("app.routers.oauth.settings") as mock_settings:
            mock_settings.notion_oauth_client_id = "configured-client-id"
            mock_settings.notion_oauth_redirect_uri = "http://localhost:9500/api/oauth/callback"
            mock_settings.frontend_url = "http://localhost:9501"

            resp = await client.get("/api/oauth/status")

        assert resp.status_code == 200
        data = resp.json()
        assert data["oauth_configured"] is True
        assert data["redirect_uri"] == "http://localhost:9500/api/oauth/callback"
        assert data["frontend_url"] == "http://localhost:9501"

    async def test_status_not_configured(self, client):
        """OAuth 미설정 상태"""
        with patch("app.routers.oauth.settings") as mock_settings:
            mock_settings.notion_oauth_client_id = ""
            mock_settings.notion_oauth_redirect_uri = "http://localhost:9500/api/oauth/callback"
            mock_settings.frontend_url = "http://localhost:9501"

            resp = await client.get("/api/oauth/status")

        assert resp.status_code == 200
        data = resp.json()
        assert data["oauth_configured"] is False

    async def test_status_returns_correct_urls(self, client):
        """설정된 URL이 정확히 반환"""
        with patch("app.routers.oauth.settings") as mock_settings:
            mock_settings.notion_oauth_client_id = "id"
            mock_settings.notion_oauth_redirect_uri = "https://prod.example.com/callback"
            mock_settings.frontend_url = "https://app.example.com"

            resp = await client.get("/api/oauth/status")

        data = resp.json()
        assert data["redirect_uri"] == "https://prod.example.com/callback"
        assert data["frontend_url"] == "https://app.example.com"


class TestStateTTL:
    """STATE_TTL 관련 동작 테스트"""

    def test_state_ttl_is_300_seconds(self):
        """TTL이 5분(300초)으로 설정"""
        assert STATE_TTL == 300

    async def test_state_just_before_expiry_is_valid(self, client):
        """TTL 직전의 state는 유효"""
        almost_expired_state = "almost-expired"
        _pending_states[almost_expired_state] = time.time() - STATE_TTL + 5  # 5초 남음

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "token",
            "workspace_name": "ws",
            "workspace_id": "id",
        }

        with patch("app.routers.oauth.settings") as mock_settings:
            mock_settings.notion_oauth_client_id = "cid"
            mock_settings.notion_oauth_client_secret = "csecret"
            mock_settings.notion_oauth_redirect_uri = "http://localhost:9500/api/oauth/callback"
            mock_settings.frontend_url = "http://localhost:9501"

            with patch("httpx.AsyncClient") as mock_http_cls:
                mock_http_instance = AsyncMock()
                mock_http_instance.post = AsyncMock(return_value=mock_response)
                mock_http_instance.__aenter__ = AsyncMock(return_value=mock_http_instance)
                mock_http_instance.__aexit__ = AsyncMock(return_value=None)
                mock_http_cls.return_value = mock_http_instance

                resp = await client.get(f"/api/oauth/callback?code=code&state={almost_expired_state}")

        assert resp.status_code == 307
