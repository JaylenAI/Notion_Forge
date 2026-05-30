"""Health 엔드포인트 테스트"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


class TestHealthEndpoints:
    async def test_health(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["version"] == "0.1.6"
        assert "ai_provider" in data
        assert "today_stats" in data

    async def test_liveness(self, client):
        resp = await client.get("/health/live")
        assert resp.status_code == 200
        assert resp.json()["alive"] is True

    async def test_readiness(self, client):
        resp = await client.get("/health/ready")
        assert resp.status_code == 200
        data = resp.json()
        assert "ready" in data
        assert "checks" in data
        assert "notion_configured" in data["checks"]
        assert "ai_provider_configured" in data["checks"]

    async def test_metrics_summary(self, client):
        resp = await client.get("/api/metrics/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert data["period"] == "7d"
        assert "total_generations" in data
        assert "success_rate" in data
        # 관측성: 백분위 지연 + 토큰 (avg만이 아님)
        assert "p50_duration_ms" in data
        assert "p95_duration_ms" in data
        assert "total_tokens_used" in data


class TestPrometheusMetrics:
    async def test_metrics_endpoint(self, client):
        resp = await client.get("/metrics")
        assert resp.status_code == 200
        body = resp.text
        assert "notionforge_generations_total" in body
        assert "notionforge_generation_duration_ms_p95" in body
        assert "notionforge_tokens_total" in body
        assert "# TYPE" in body
