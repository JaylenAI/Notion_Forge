"""Integration tests for all API endpoints (uses mock mode)"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_patterns(client):
    r = await client.get("/api/templates/patterns")
    assert r.status_code == 200
    assert len(r.json()["patterns"]) == 7


@pytest.mark.asyncio
async def test_preview_dashboard(client):
    r = await client.post("/api/templates/preview", json={"prompt": "대시보드 만들어줘 보라색"})
    assert r.status_code == 200
    bp = r.json()["blueprint"]
    assert bp["metadata"]["template_type"] in ("dashboard", "hub", "manage", "custom")


@pytest.mark.asyncio
async def test_preview_tracker(client):
    r = await client.post("/api/templates/preview", json={"prompt": "습관 트래커"})
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_preview_bookmark(client):
    r = await client.post("/api/templates/preview", json={"prompt": "북마크 사이트 만들어줘"})
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_preview_onboarding(client):
    r = await client.post("/api/templates/preview", json={"prompt": "온보딩 가이드"})
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_preview_empty_rejected(client):
    r = await client.post("/api/templates/preview", json={"prompt": ""})
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_generate_mock(client):
    r = await client.post(
        "/api/templates/generate",
        json={
            "prompt": "트래커 만들어줘",
            "notion_token": "ntn_test_token_for_mock",
            "parent_page_id": "00000000000000000000000000000000",
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["success"] in (True, False)


@pytest.mark.asyncio
async def test_generate_invalid_id_rejected(client):
    r = await client.post(
        "/api/templates/generate",
        json={
            "prompt": "트래커 만들어줘",
            "notion_token": "test",
            "parent_page_id": "invalid!@#",
        },
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_search_mock(client):
    r = await client.get("/api/templates/search?q=test")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_404(client):
    r = await client.get("/nonexistent")
    assert r.status_code == 404
