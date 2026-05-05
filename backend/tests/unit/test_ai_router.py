"""AI Router 테스트: provider 감지, copilot 상태, 모델 변경"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


class TestDetectProvider:
    """POST /api/templates/ai/detect-provider"""

    async def test_empty_key_returns_unknown(self, client):
        resp = await client.post("/api/templates/ai/detect-provider", json={"api_key": ""})
        assert resp.status_code == 200
        data = resp.json()
        assert data["provider"] == "unknown"

    async def test_invalid_key_returns_unknown(self, client):
        with patch("app.agent.providers.router.detect_provider_from_key", return_value=None):
            resp = await client.post("/api/templates/ai/detect-provider", json={"api_key": "invalid-key"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["provider"] == "unknown"

    async def test_openai_key_detected(self, client):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"data": [{"id": "gpt-4.1"}, {"id": "dall-e-3"}]}

        with patch("app.agent.providers.router.detect_provider_from_key", return_value="openai"):
            with patch("httpx.AsyncClient") as mock_http:
                mock_instance = AsyncMock()
                mock_instance.get = AsyncMock(return_value=mock_resp)
                mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
                mock_instance.__aexit__ = AsyncMock(return_value=None)
                mock_http.return_value = mock_instance

                resp = await client.post("/api/templates/ai/detect-provider", json={"api_key": "sk-test123"})

        assert resp.status_code == 200
        data = resp.json()
        assert data["provider"] == "openai"
        assert any(m["id"] == "gpt-4.1" for m in data["models"])

    async def test_groq_key_detected(self, client):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"data": [{"id": "llama-3.3-70b"}]}

        with patch("app.agent.providers.router.detect_provider_from_key", return_value="groq"):
            with patch("httpx.AsyncClient") as mock_http:
                mock_instance = AsyncMock()
                mock_instance.get = AsyncMock(return_value=mock_resp)
                mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
                mock_instance.__aexit__ = AsyncMock(return_value=None)
                mock_http.return_value = mock_instance

                resp = await client.post("/api/templates/ai/detect-provider", json={"api_key": "gsk_test123"})

        assert resp.status_code == 200
        data = resp.json()
        assert data["provider"] == "groq"

    async def test_anthropic_key_detected(self, client):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"data": [{"id": "claude-sonnet-4-6"}]}

        with patch("app.agent.providers.router.detect_provider_from_key", return_value="claude"):
            with patch("httpx.AsyncClient") as mock_http:
                mock_instance = AsyncMock()
                mock_instance.get = AsyncMock(return_value=mock_resp)
                mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
                mock_instance.__aexit__ = AsyncMock(return_value=None)
                mock_http.return_value = mock_instance

                resp = await client.post("/api/templates/ai/detect-provider", json={"api_key": "sk-ant-test"})

        assert resp.status_code == 200
        data = resp.json()
        assert data["provider"] == "anthropic"

    async def test_google_key_detected(self, client):
        mock_model = MagicMock()
        mock_model.name = "models/gemini-2.0-flash"
        mock_model.display_name = "Gemini 2.0 Flash"

        with patch("app.agent.providers.router.detect_provider_from_key", return_value="gemini"):
            with patch("google.genai.Client") as mock_genai:
                mock_client_instance = MagicMock()
                mock_client_instance.models.list.return_value = [mock_model]
                mock_genai.return_value = mock_client_instance

                resp = await client.post("/api/templates/ai/detect-provider", json={"api_key": "AIza-test"})

        assert resp.status_code == 200
        data = resp.json()
        assert data["provider"] == "google"
        assert len(data["models"]) == 1

    async def test_provider_api_error(self, client):
        with patch("app.agent.providers.router.detect_provider_from_key", return_value="openai"):
            with patch("httpx.AsyncClient") as mock_http:
                mock_instance = AsyncMock()
                mock_instance.get = AsyncMock(side_effect=Exception("Connection failed"))
                mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
                mock_instance.__aexit__ = AsyncMock(return_value=None)
                mock_http.return_value = mock_instance

                resp = await client.post("/api/templates/ai/detect-provider", json={"api_key": "sk-broken"})

        assert resp.status_code == 200
        data = resp.json()
        assert data["provider"] == "openai"
        assert "error" in data


class TestCopilotStatus:
    """GET /api/templates/ai/copilot-status"""

    async def test_copilot_available(self, client):
        resp = await client.get("/api/templates/ai/copilot-status")
        assert resp.status_code == 200
        data = resp.json()
        assert "available" in data


class TestSetCopilotModel:
    """POST /api/templates/ai/copilot-model"""

    async def test_set_valid_model(self, client):
        resp = await client.post("/api/templates/ai/copilot-model", json={"model": "gpt-4.1"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["model"] == "gpt-4.1"
        assert data["scope"] == "session"

    async def test_set_invalid_model(self, client):
        resp = await client.post("/api/templates/ai/copilot-model", json={"model": "invalid-model"})
        assert resp.status_code == 200
        data = resp.json()
        assert "error" in data

    async def test_set_all_allowed_models(self, client):
        allowed = ["gpt-4.1", "gpt-4.1-mini", "gpt-5-mini", "gpt-5.2", "claude-sonnet-4-5", "o3-mini", "o4-mini"]
        for model in allowed:
            resp = await client.post("/api/templates/ai/copilot-model", json={"model": model})
            data = resp.json()
            assert data["model"] == model


class TestGetCurrentModel:
    """GET /api/templates/ai/current-model"""

    async def test_get_current_model(self, client):
        resp = await client.get("/api/templates/ai/current-model")
        assert resp.status_code == 200
        data = resp.json()
        assert "default_model" in data
        assert "active" in data
