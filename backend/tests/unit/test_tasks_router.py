"""비동기 작업 라우터 테스트"""

import time
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.routers.tasks import _task_store


@pytest.fixture(autouse=True)
def clear_task_store():
    _task_store.clear()
    yield
    _task_store.clear()


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


class TestTaskSubmit:
    async def test_submit_returns_task_id(self, client):
        with patch("app.routers.tasks.AgentOrchestrator") as mock_orch:
            mock_instance = AsyncMock()
            mock_instance.process = AsyncMock(return_value=AsyncMock())
            mock_instance.process.return_value.__aiter__ = AsyncMock(return_value=iter([]))
            mock_orch.return_value = mock_instance

            resp = await client.post(
                "/api/tasks/submit",
                json={
                    "prompt": "테스트 템플릿",
                    "notion_token": "test-token-12345",
                    "parent_page_id": "abc12345-1234-1234-1234-123456789012",
                },
            )

        assert resp.status_code == 200
        data = resp.json()
        assert "task_id" in data
        assert data["status"] in ("pending", "running")

    async def test_submit_validates_input(self, client):
        resp = await client.post(
            "/api/tasks/submit",
            json={
                "prompt": "",
                "notion_token": "t",
                "parent_page_id": "invalid!",
            },
        )
        assert resp.status_code == 422

    async def test_concurrent_limit(self, client):
        for i in range(10):
            _task_store[f"task-{i}"] = {
                "task_id": f"task-{i}",
                "status": "running",
                "progress": [],
                "result": None,
                "error": None,
                "created_at": time.time(),
                "completed_at": None,
            }

        resp = await client.post(
            "/api/tasks/submit",
            json={
                "prompt": "또 다른 템플릿",
                "notion_token": "test-token-12345",
                "parent_page_id": "abc12345-1234-1234-1234-123456789012",
            },
        )
        assert resp.status_code == 429


class TestTaskStatus:
    async def test_get_existing_task(self, client):
        _task_store["test-123"] = {
            "task_id": "test-123",
            "status": "completed",
            "progress": [{"step": "done", "message": "완료", "timestamp": time.time()}],
            "result": {"success": True, "notion_url": "https://notion.so/abc"},
            "error": None,
            "created_at": time.time() - 10,
            "completed_at": time.time(),
        }

        resp = await client.get("/api/tasks/test-123")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "completed"
        assert data["result"]["success"] is True

    async def test_get_nonexistent_task(self, client):
        resp = await client.get("/api/tasks/nonexistent")
        assert resp.status_code == 404


class TestTaskCancel:
    async def test_delete_task(self, client):
        _task_store["del-123"] = {
            "task_id": "del-123",
            "status": "running",
            "progress": [],
            "result": None,
            "error": None,
            "created_at": time.time(),
            "completed_at": None,
        }

        resp = await client.delete("/api/tasks/del-123")
        assert resp.status_code == 200
        assert "del-123" not in _task_store

    async def test_delete_nonexistent(self, client):
        resp = await client.delete("/api/tasks/nope")
        assert resp.status_code == 404


class TestCleanup:
    def test_old_tasks_cleaned(self):
        from app.routers.tasks import _cleanup_old_tasks

        _task_store["old-task"] = {
            "task_id": "old-task",
            "status": "completed",
            "progress": [],
            "result": None,
            "error": None,
            "created_at": time.time() - 7200,
            "completed_at": time.time() - 7000,
        }
        _task_store["new-task"] = {
            "task_id": "new-task",
            "status": "running",
            "progress": [],
            "result": None,
            "error": None,
            "created_at": time.time(),
            "completed_at": None,
        }

        _cleanup_old_tasks()
        assert "old-task" not in _task_store
        assert "new-task" in _task_store
