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
        assert data["version"] == "0.1.4"
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
