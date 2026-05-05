"""비동기 작업 라우터 테스트"""

import time
from unittest.mock import AsyncMock, MagicMock, patch

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


class TestRunGeneration:
    """_run_generation 내부 이벤트 처리 테스트"""

    async def test_complete_event_sets_result(self):
        from app.routers.tasks import _run_generation

        _task_store["gen-1"] = {
            "task_id": "gen-1",
            "status": "pending",
            "progress": [],
            "result": None,
            "error": None,
            "created_at": time.time(),
            "completed_at": None,
        }

        async def fake_events(*args, **kwargs):
            yield {"type": "progress", "step": "분석", "message": "시작"}
            yield {
                "type": "complete",
                "result": {
                    "main_url": "https://notion.so/abc",
                    "pages": [{"id": "p1"}],
                    "databases": [{"id": "d1"}],
                    "blocks": 10,
                },
            }

        with patch("app.routers.tasks.AgentOrchestrator") as mock_orch:
            mock_instance = AsyncMock()
            mock_instance.process = fake_events
            mock_orch.return_value = mock_instance

            await _run_generation("gen-1", "테스트", "token", "parent-id")

        task = _task_store["gen-1"]
        assert task["status"] == "completed"
        assert task["result"]["success"] is True
        assert task["result"]["notion_url"] == "https://notion.so/abc"
        assert len(task["progress"]) == 1

    async def test_error_event_sets_failed(self):
        from app.routers.tasks import _run_generation

        _task_store["gen-2"] = {
            "task_id": "gen-2",
            "status": "pending",
            "progress": [],
            "result": None,
            "error": None,
            "created_at": time.time(),
            "completed_at": None,
        }

        async def fake_events(*args, **kwargs):
            yield {"type": "error", "content": "API 키 만료"}

        with patch("app.routers.tasks.AgentOrchestrator") as mock_orch:
            mock_instance = AsyncMock()
            mock_instance.process = fake_events
            mock_orch.return_value = mock_instance

            await _run_generation("gen-2", "테스트", "token", "parent-id")

        task = _task_store["gen-2"]
        assert task["status"] == "failed"
        assert "API 키 만료" in task["error"]

    async def test_question_event_sets_failed(self):
        from app.routers.tasks import _run_generation

        _task_store["gen-3"] = {
            "task_id": "gen-3",
            "status": "pending",
            "progress": [],
            "result": None,
            "error": None,
            "created_at": time.time(),
            "completed_at": None,
        }

        async def fake_events(*args, **kwargs):
            yield {"type": "question", "content": "프로젝트 이름을 알려주세요"}

        with patch("app.routers.tasks.AgentOrchestrator") as mock_orch:
            mock_instance = AsyncMock()
            mock_instance.process = fake_events
            mock_orch.return_value = mock_instance

            await _run_generation("gen-3", "테스트", "token", "parent-id")

        task = _task_store["gen-3"]
        assert task["status"] == "failed"
        assert "추가 정보 필요" in task["error"]

    async def test_approval_request_auto_approved(self):
        from app.routers.tasks import _run_generation

        _task_store["gen-4"] = {
            "task_id": "gen-4",
            "status": "pending",
            "progress": [],
            "result": None,
            "error": None,
            "created_at": time.time(),
            "completed_at": None,
        }

        async def fake_events(*args, **kwargs):
            yield {"type": "approval_request"}
            yield {
                "type": "complete",
                "result": {"main_url": "url", "pages": [], "databases": [], "blocks": 0},
            }

        with patch("app.routers.tasks.AgentOrchestrator") as mock_orch:
            mock_instance = AsyncMock()
            mock_instance.process = fake_events
            mock_instance.approve_creation = MagicMock()
            mock_orch.return_value = mock_instance

            await _run_generation("gen-4", "테스트", "token", "parent-id")

        mock_instance.approve_creation.assert_called_once_with(approved=True)
        assert _task_store["gen-4"]["status"] == "completed"

    async def test_no_complete_event_fails(self):
        from app.routers.tasks import _run_generation

        _task_store["gen-5"] = {
            "task_id": "gen-5",
            "status": "pending",
            "progress": [],
            "result": None,
            "error": None,
            "created_at": time.time(),
            "completed_at": None,
        }

        async def fake_events(*args, **kwargs):
            yield {"type": "progress", "step": "분석", "message": "진행"}

        with patch("app.routers.tasks.AgentOrchestrator") as mock_orch:
            mock_instance = AsyncMock()
            mock_instance.process = fake_events
            mock_orch.return_value = mock_instance

            await _run_generation("gen-5", "테스트", "token", "parent-id")

        task = _task_store["gen-5"]
        assert task["status"] == "failed"
        assert "생성 완료 이벤트를 받지 못했습니다" in task["error"]

    async def test_exception_sets_failed(self):
        from app.routers.tasks import _run_generation

        _task_store["gen-6"] = {
            "task_id": "gen-6",
            "status": "pending",
            "progress": [],
            "result": None,
            "error": None,
            "created_at": time.time(),
            "completed_at": None,
        }

        with patch("app.routers.tasks.AgentOrchestrator") as mock_orch:
            mock_orch.side_effect = Exception("초기화 실패")

            await _run_generation("gen-6", "테스트", "token", "parent-id")

        task = _task_store["gen-6"]
        assert task["status"] == "failed"


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
