"""Workers + External Agents API mixin 유닛 테스트 (mock HTTP)"""

from unittest.mock import AsyncMock, MagicMock

import pytest


def _make_mock_client(mock_mode=False):
    from app.notion.workers import WorkerOpsMixin

    class FakeClient(WorkerOpsMixin):
        def __init__(self):
            self.mock_mode = mock_mode
            self.rate_limiter = MagicMock()
            self.rate_limiter.acquire = AsyncMock()
            self._http_client = MagicMock()
            self._mock_id_counter = 0

        def _mock_id(self):
            self._mock_id_counter += 1
            return f"mock-{self._mock_id_counter}"

    return FakeClient()


def _ok_response(data, status=200):
    resp = MagicMock()
    resp.status_code = status
    resp.json.return_value = data
    resp.text = ""
    return resp


def _error_response(status=400):
    resp = MagicMock()
    resp.status_code = status
    resp.text = "error"
    resp.json.return_value = {}
    return resp


class TestListWorkers:
    @pytest.mark.asyncio
    async def test_mock_mode(self):
        c = _make_mock_client(mock_mode=True)
        assert await c.list_workers() == []

    @pytest.mark.asyncio
    async def test_success(self):
        c = _make_mock_client()
        c._http_client.get = AsyncMock(return_value=_ok_response({"results": [{"id": "w1"}]}))
        result = await c.list_workers()
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_error(self):
        c = _make_mock_client()
        c._http_client.get = AsyncMock(return_value=_error_response())
        assert await c.list_workers() == []

    @pytest.mark.asyncio
    async def test_exception(self):
        c = _make_mock_client()
        c._http_client.get = AsyncMock(side_effect=Exception("net"))
        assert await c.list_workers() == []


class TestGetWorker:
    @pytest.mark.asyncio
    async def test_mock_mode(self):
        c = _make_mock_client(mock_mode=True)
        r = await c.get_worker("w1")
        assert r["id"] == "w1"

    @pytest.mark.asyncio
    async def test_success(self):
        c = _make_mock_client()
        c._http_client.get = AsyncMock(return_value=_ok_response({"id": "w1", "type": "sync"}))
        r = await c.get_worker("w1")
        assert r["type"] == "sync"

    @pytest.mark.asyncio
    async def test_error(self):
        c = _make_mock_client()
        c._http_client.get = AsyncMock(return_value=_error_response())
        r = await c.get_worker("w1")
        assert r == {"id": "w1"}

    @pytest.mark.asyncio
    async def test_exception(self):
        c = _make_mock_client()
        c._http_client.get = AsyncMock(side_effect=Exception("net"))
        r = await c.get_worker("w1")
        assert r == {"id": "w1"}


class TestDeployWorker:
    @pytest.mark.asyncio
    async def test_mock_mode(self):
        c = _make_mock_client(mock_mode=True)
        r = await c.deploy_worker("Sync", "sync", "code")
        assert r["status"] == "deploying"

    @pytest.mark.asyncio
    async def test_success(self):
        c = _make_mock_client()
        c._http_client.post = AsyncMock(return_value=_ok_response({"id": "w1", "status": "deploying"}))
        r = await c.deploy_worker("Sync", "sync", "code", database_id="db1", description="desc")
        assert r["status"] == "deploying"

    @pytest.mark.asyncio
    async def test_error(self):
        c = _make_mock_client()
        c._http_client.post = AsyncMock(return_value=_error_response())
        r = await c.deploy_worker("Sync", "sync", "code")
        assert r["fallback"] is True

    @pytest.mark.asyncio
    async def test_exception(self):
        c = _make_mock_client()
        c._http_client.post = AsyncMock(side_effect=Exception("net"))
        r = await c.deploy_worker("Sync", "sync", "code")
        assert r["fallback"] is True


class TestUpdateWorker:
    @pytest.mark.asyncio
    async def test_mock_mode(self):
        c = _make_mock_client(mock_mode=True)
        r = await c.update_worker("w1", title="New")
        assert r["title"] == "New"

    @pytest.mark.asyncio
    async def test_success(self):
        c = _make_mock_client()
        c._http_client.patch = AsyncMock(return_value=_ok_response({"id": "w1", "title": "New"}))
        r = await c.update_worker("w1", title="New")
        assert r["title"] == "New"

    @pytest.mark.asyncio
    async def test_error(self):
        c = _make_mock_client()
        c._http_client.patch = AsyncMock(return_value=_error_response())
        r = await c.update_worker("w1", title="x")
        assert r["fallback"] is True

    @pytest.mark.asyncio
    async def test_exception(self):
        c = _make_mock_client()
        c._http_client.patch = AsyncMock(side_effect=Exception("net"))
        r = await c.update_worker("w1", title="x")
        assert r["fallback"] is True


class TestDeleteWorker:
    @pytest.mark.asyncio
    async def test_mock_mode(self):
        c = _make_mock_client(mock_mode=True)
        assert await c.delete_worker("w1") is True

    @pytest.mark.asyncio
    async def test_success(self):
        c = _make_mock_client()
        c._http_client.delete = AsyncMock(return_value=_ok_response({}))
        assert await c.delete_worker("w1") is True

    @pytest.mark.asyncio
    async def test_error(self):
        c = _make_mock_client()
        c._http_client.delete = AsyncMock(return_value=_error_response())
        assert await c.delete_worker("w1") is False

    @pytest.mark.asyncio
    async def test_exception(self):
        c = _make_mock_client()
        c._http_client.delete = AsyncMock(side_effect=Exception("net"))
        assert await c.delete_worker("w1") is False


class TestGetWorkerLogs:
    @pytest.mark.asyncio
    async def test_mock_mode(self):
        c = _make_mock_client(mock_mode=True)
        assert await c.get_worker_logs("w1") == []

    @pytest.mark.asyncio
    async def test_success(self):
        c = _make_mock_client()
        c._http_client.get = AsyncMock(return_value=_ok_response({"results": [{"msg": "ok"}]}))
        r = await c.get_worker_logs("w1", limit=10)
        assert len(r) == 1

    @pytest.mark.asyncio
    async def test_error(self):
        c = _make_mock_client()
        c._http_client.get = AsyncMock(return_value=_error_response())
        assert await c.get_worker_logs("w1") == []

    @pytest.mark.asyncio
    async def test_exception(self):
        c = _make_mock_client()
        c._http_client.get = AsyncMock(side_effect=Exception("net"))
        assert await c.get_worker_logs("w1") == []


class TestRegisterExternalAgent:
    @pytest.mark.asyncio
    async def test_mock_mode(self):
        c = _make_mock_client(mock_mode=True)
        r = await c.register_external_agent("Bot", "설명", "지시")
        assert r["status"] == "registered"

    @pytest.mark.asyncio
    async def test_success(self):
        c = _make_mock_client()
        c._http_client.post = AsyncMock(return_value=_ok_response({"id": "a1", "name": "Bot"}))
        r = await c.register_external_agent("Bot", "설명", "지시", tools=[{"name": "t"}], avatar_url="http://img")
        assert r["name"] == "Bot"

    @pytest.mark.asyncio
    async def test_error(self):
        c = _make_mock_client()
        c._http_client.post = AsyncMock(return_value=_error_response())
        r = await c.register_external_agent("Bot", "설명", "지시")
        assert r["fallback"] is True

    @pytest.mark.asyncio
    async def test_exception(self):
        c = _make_mock_client()
        c._http_client.post = AsyncMock(side_effect=Exception("net"))
        r = await c.register_external_agent("Bot", "설명", "지시")
        assert r["fallback"] is True


class TestListExternalAgents:
    @pytest.mark.asyncio
    async def test_mock_mode(self):
        c = _make_mock_client(mock_mode=True)
        assert await c.list_external_agents() == []

    @pytest.mark.asyncio
    async def test_success(self):
        c = _make_mock_client()
        c._http_client.get = AsyncMock(return_value=_ok_response({"results": [{"id": "a1"}]}))
        assert len(await c.list_external_agents()) == 1

    @pytest.mark.asyncio
    async def test_error(self):
        c = _make_mock_client()
        c._http_client.get = AsyncMock(return_value=_error_response())
        assert await c.list_external_agents() == []

    @pytest.mark.asyncio
    async def test_exception(self):
        c = _make_mock_client()
        c._http_client.get = AsyncMock(side_effect=Exception("net"))
        assert await c.list_external_agents() == []


class TestUpdateExternalAgent:
    @pytest.mark.asyncio
    async def test_mock_mode(self):
        c = _make_mock_client(mock_mode=True)
        r = await c.update_external_agent("a1", name="New")
        assert r["name"] == "New"

    @pytest.mark.asyncio
    async def test_success(self):
        c = _make_mock_client()
        c._http_client.patch = AsyncMock(return_value=_ok_response({"id": "a1", "name": "New"}))
        r = await c.update_external_agent("a1", name="New")
        assert r["name"] == "New"

    @pytest.mark.asyncio
    async def test_error(self):
        c = _make_mock_client()
        c._http_client.patch = AsyncMock(return_value=_error_response())
        r = await c.update_external_agent("a1", name="x")
        assert r["fallback"] is True

    @pytest.mark.asyncio
    async def test_exception(self):
        c = _make_mock_client()
        c._http_client.patch = AsyncMock(side_effect=Exception("net"))
        r = await c.update_external_agent("a1", name="x")
        assert r["fallback"] is True


class TestDeleteExternalAgent:
    @pytest.mark.asyncio
    async def test_mock_mode(self):
        c = _make_mock_client(mock_mode=True)
        assert await c.delete_external_agent("a1") is True

    @pytest.mark.asyncio
    async def test_success(self):
        c = _make_mock_client()
        c._http_client.delete = AsyncMock(return_value=_ok_response({}))
        assert await c.delete_external_agent("a1") is True

    @pytest.mark.asyncio
    async def test_error(self):
        c = _make_mock_client()
        c._http_client.delete = AsyncMock(return_value=_error_response())
        assert await c.delete_external_agent("a1") is False

    @pytest.mark.asyncio
    async def test_exception(self):
        c = _make_mock_client()
        c._http_client.delete = AsyncMock(side_effect=Exception("net"))
        assert await c.delete_external_agent("a1") is False
