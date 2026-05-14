"""Phase 3 Notion Workers 통합 테스트:
worker_builder, workers mixin, create_worker tool, register_agent tool"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.notion.worker_builder import (
    build_sync_worker,
    build_tool_worker,
    build_webhook_worker,
    build_worker_project,
)

# ============================================================
# worker_builder 테스트
# ============================================================


class TestBuildSyncWorker:
    def test_basic_sync(self):
        result = build_sync_worker("GitHub Issues Sync")
        assert result["type"] == "sync"
        assert result["name"] == "GitHub Issues Sync"
        assert "defineSyncWorker" in result["code"]
        assert "fetchExternalData" in result["code"]
        assert result["schedule"] == "*/15 * * * *"

    def test_with_properties(self):
        props = {"Name": "title", "Status": "select", "Priority": "number"}
        result = build_sync_worker("Jira Sync", properties=props)
        assert '"Name": { type: "title" }' in result["code"]
        assert '"Status": { type: "select" }' in result["code"]

    def test_custom_schedule(self):
        result = build_sync_worker("Daily Sync", schedule="0 9 * * *")
        assert '"0 9 * * *"' in result["code"]

    def test_config_has_package_json(self):
        result = build_sync_worker("Test Sync")
        cfg = result["config"]
        assert cfg["type"] == "module"
        assert "@notionhq/workers" in cfg["dependencies"]


class TestBuildToolWorker:
    def test_basic_tool(self):
        result = build_tool_worker("Search Tool", description="검색 도구")
        assert result["type"] == "tool"
        assert "defineToolWorker" in result["code"]
        assert "검색 도구" in result["code"]

    def test_with_parameters(self):
        params = {
            "query": {"type": "string", "description": "검색어"},
            "limit": {"type": "number", "description": "결과 수"},
        }
        result = build_tool_worker("Search", parameters=params)
        assert 'query: { type: "string"' in result["code"]
        assert 'limit: { type: "number"' in result["code"]

    def test_with_action_code(self):
        code = '    return { result: "custom" };'
        result = build_tool_worker("Custom", action_code=code)
        assert "custom" in result["code"]


class TestBuildWebhookWorker:
    def test_basic_webhook(self):
        result = build_webhook_worker("Auto Tagger")
        assert result["type"] == "webhook"
        assert "defineWebhookWorker" in result["code"]
        assert '"page.created"' in result["code"]

    def test_custom_event(self):
        result = build_webhook_worker("Update Hook", event_type="page.updated")
        assert '"page.updated"' in result["code"]

    def test_with_database_filter(self):
        result = build_webhook_worker(
            "DB Hook",
            database_id="db-abc-123",
        )
        assert 'database_id: "db-abc-123"' in result["code"]

    def test_with_action_code(self):
        code = '    console.log("custom handler");'
        result = build_webhook_worker("Custom Hook", action_code=code)
        assert "custom handler" in result["code"]


class TestBuildWorkerProject:
    def test_single_worker_project(self):
        worker = build_sync_worker("Test Sync")
        project = build_worker_project([worker])
        assert project["project_name"] == "notionforge-workers"
        assert "package.json" in project["files"]
        assert "tsconfig.json" in project["files"]
        assert "notion.config.ts" in project["files"]
        assert ".env.example" in project["files"]
        assert ".gitignore" in project["files"]
        assert any("test_sync.ts" in f for f in project["files"])

    def test_multi_worker_project(self):
        workers = [
            build_sync_worker("Data Sync"),
            build_tool_worker("Quick Search"),
            build_webhook_worker("Auto Tag"),
        ]
        project = build_worker_project(workers, project_name="my-workers")
        assert project["project_name"] == "my-workers"
        assert len(project["workers"]) == 3
        assert len(project["files"]) == 8

    def test_package_json_contents(self):
        worker = build_tool_worker("My Tool")
        project = build_worker_project([worker])
        pkg = project["files"]["package.json"]
        assert "@notionhq/workers" in pkg
        assert "ntn dev" in pkg
        assert "ntn deploy" in pkg

    def test_tsconfig_strict(self):
        worker = build_sync_worker("X")
        project = build_worker_project([worker])
        tsconfig = project["files"]["tsconfig.json"]
        assert '"strict": true' in tsconfig

    def test_notion_config_imports(self):
        worker = build_sync_worker("Data Sync")
        project = build_worker_project([worker])
        config = project["files"]["notion.config.ts"]
        assert "defineConfig" in config
        assert "Data_Sync" in config or "data_sync" in config


# ============================================================
# WorkerOpsMixin 테스트
# ============================================================


def _make_worker_mock_resp(data=None):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = data or {"id": "worker-123", "status": "active"}
    resp.text = ""
    return resp


def _make_worker_mock_client():
    from app.notion.workers import WorkerOpsMixin

    client = MagicMock()
    client.mock_mode = False
    client._mock_id = MagicMock(return_value="mock-worker-id")

    mock_resp = _make_worker_mock_resp()

    http = MagicMock()
    http.post = AsyncMock(return_value=mock_resp)
    http.get = AsyncMock(return_value=mock_resp)
    http.patch = AsyncMock(return_value=mock_resp)
    http.delete = AsyncMock(return_value=mock_resp)
    client._http_client = http

    rl = MagicMock()
    rl.acquire = AsyncMock()
    client.rate_limiter = rl

    client.list_workers = WorkerOpsMixin.list_workers.__get__(client, type(client))
    client.get_worker = WorkerOpsMixin.get_worker.__get__(client, type(client))
    client.deploy_worker = WorkerOpsMixin.deploy_worker.__get__(client, type(client))
    client.update_worker = WorkerOpsMixin.update_worker.__get__(client, type(client))
    client.delete_worker = WorkerOpsMixin.delete_worker.__get__(client, type(client))
    client.get_worker_logs = WorkerOpsMixin.get_worker_logs.__get__(client, type(client))
    client.register_external_agent = WorkerOpsMixin.register_external_agent.__get__(client, type(client))
    client.list_external_agents = WorkerOpsMixin.list_external_agents.__get__(client, type(client))
    client.update_external_agent = WorkerOpsMixin.update_external_agent.__get__(client, type(client))
    client.delete_external_agent = WorkerOpsMixin.delete_external_agent.__get__(client, type(client))

    return client


class TestWorkerOps:
    @pytest.mark.asyncio
    async def test_list_workers(self):
        client = _make_worker_mock_client()
        client._http_client.get.return_value = _make_worker_mock_resp({"results": [{"id": "w-1"}, {"id": "w-2"}]})
        result = await client.list_workers()
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_worker(self):
        client = _make_worker_mock_client()
        result = await client.get_worker("worker-123")
        assert result["id"] == "worker-123"

    @pytest.mark.asyncio
    async def test_deploy_worker(self):
        client = _make_worker_mock_client()
        client._http_client.post.return_value = _make_worker_mock_resp(
            {"id": "w-new", "title": "My Sync", "status": "deploying"}
        )
        result = await client.deploy_worker(
            title="My Sync",
            worker_type="sync",
            code="export default defineSyncWorker({...})",
        )
        assert result["status"] == "deploying"
        call_args = client._http_client.post.call_args
        body = call_args.kwargs["json"]
        assert body["type"] == "sync"

    @pytest.mark.asyncio
    async def test_deploy_worker_with_db(self):
        client = _make_worker_mock_client()
        await client.deploy_worker(
            title="DB Sync",
            worker_type="sync",
            code="...",
            database_id="db-abc",
            description="데이터 동기화",
        )
        body = client._http_client.post.call_args.kwargs["json"]
        assert body["database_id"] == "db-abc"
        assert body["description"] == "데이터 동기화"

    @pytest.mark.asyncio
    async def test_update_worker(self):
        client = _make_worker_mock_client()
        result = await client.update_worker("w-1", title="Updated")
        assert result["id"] == "worker-123"

    @pytest.mark.asyncio
    async def test_delete_worker(self):
        client = _make_worker_mock_client()
        result = await client.delete_worker("w-1")
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_worker_error(self):
        client = _make_worker_mock_client()
        error_resp = _make_worker_mock_resp()
        error_resp.status_code = 404
        client._http_client.delete.return_value = error_resp
        result = await client.delete_worker("w-bad")
        assert result is False

    @pytest.mark.asyncio
    async def test_get_worker_logs(self):
        client = _make_worker_mock_client()
        client._http_client.get.return_value = _make_worker_mock_resp(
            {"results": [{"level": "info", "message": "sync started"}]}
        )
        logs = await client.get_worker_logs("w-1", limit=10)
        assert len(logs) == 1

    @pytest.mark.asyncio
    async def test_mock_mode_deploy(self):
        client = _make_worker_mock_client()
        client.mock_mode = True
        result = await client.deploy_worker(title="Mock Worker", worker_type="tool", code="...")
        assert result["status"] == "deploying"


# ============================================================
# External Agents API 테스트
# ============================================================


class TestExternalAgentsOps:
    @pytest.mark.asyncio
    async def test_register_agent(self):
        client = _make_worker_mock_client()
        client._http_client.post.return_value = _make_worker_mock_resp(
            {"id": "agent-1", "name": "NotionForge", "status": "registered"}
        )
        result = await client.register_external_agent(
            name="NotionForge",
            description="AI 템플릿 에이전트",
            instructions="사용자 요청에 따라 Notion 템플릿을 생성합니다.",
        )
        assert result["name"] == "NotionForge"
        body = client._http_client.post.call_args.kwargs["json"]
        assert body["name"] == "NotionForge"
        assert body["instructions"].startswith("사용자")

    @pytest.mark.asyncio
    async def test_register_agent_with_tools(self):
        client = _make_worker_mock_client()
        tools = [{"name": "create_template", "description": "템플릿 생성"}]
        await client.register_external_agent(
            name="ForgeAgent",
            description="test",
            instructions="test instructions",
            tools=tools,
        )
        body = client._http_client.post.call_args.kwargs["json"]
        assert body["tools"] == tools

    @pytest.mark.asyncio
    async def test_register_agent_with_avatar(self):
        client = _make_worker_mock_client()
        await client.register_external_agent(
            name="AvatarAgent",
            description="test",
            instructions="test",
            avatar_url="https://example.com/avatar.png",
        )
        body = client._http_client.post.call_args.kwargs["json"]
        assert body["avatar"]["external"]["url"] == "https://example.com/avatar.png"

    @pytest.mark.asyncio
    async def test_list_agents(self):
        client = _make_worker_mock_client()
        client._http_client.get.return_value = _make_worker_mock_resp({"results": [{"id": "a-1"}, {"id": "a-2"}]})
        result = await client.list_external_agents()
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_update_agent(self):
        client = _make_worker_mock_client()
        result = await client.update_external_agent("a-1", name="Updated Agent")
        assert result["id"] == "worker-123"

    @pytest.mark.asyncio
    async def test_delete_agent(self):
        client = _make_worker_mock_client()
        result = await client.delete_external_agent("a-1")
        assert result is True

    @pytest.mark.asyncio
    async def test_mock_mode_register(self):
        client = _make_worker_mock_client()
        client.mock_mode = True
        result = await client.register_external_agent(name="MockAgent", description="test", instructions="test")
        assert result["status"] == "registered"


# ============================================================
# Agent Tool 테스트 (CreateWorkerTool, RegisterAgentTool)
# ============================================================


class TestCreateWorkerTool:
    @pytest.mark.asyncio
    async def test_sync_worker_scaffold(self):
        from app.agent.tools.create_worker import CreateWorkerTool

        mock_client = MagicMock()
        mock_client.deploy_worker = AsyncMock()
        tool = CreateWorkerTool(mock_client)

        result = await tool.execute(
            name="GitHub Sync",
            worker_type="sync",
            description="GitHub Issues 동기화",
            properties={"Name": "title", "Status": "select"},
        )
        assert result["worker_type"] == "sync"
        assert result["files_count"] > 0
        assert "project" in result
        mock_client.deploy_worker.assert_not_called()

    @pytest.mark.asyncio
    async def test_tool_worker_scaffold(self):
        from app.agent.tools.create_worker import CreateWorkerTool

        mock_client = MagicMock()
        tool = CreateWorkerTool(mock_client)

        result = await tool.execute(
            name="Quick Search",
            worker_type="tool",
            description="빠른 검색",
        )
        assert result["worker_type"] == "tool"

    @pytest.mark.asyncio
    async def test_webhook_worker_scaffold(self):
        from app.agent.tools.create_worker import CreateWorkerTool

        mock_client = MagicMock()
        tool = CreateWorkerTool(mock_client)

        result = await tool.execute(
            name="Auto Tag",
            worker_type="webhook",
            event_type="page.created",
            database_id="db-123",
        )
        assert result["worker_type"] == "webhook"

    @pytest.mark.asyncio
    async def test_deploy_flag(self):
        from app.agent.tools.create_worker import CreateWorkerTool

        mock_client = MagicMock()
        mock_client.deploy_worker = AsyncMock(return_value={"id": "w-deployed", "status": "deploying"})
        tool = CreateWorkerTool(mock_client)

        result = await tool.execute(
            name="Deploy Test",
            worker_type="tool",
            deploy=True,
        )
        assert "deploy" in result
        assert result["deploy"]["status"] == "deploying"
        mock_client.deploy_worker.assert_called_once()

    @pytest.mark.asyncio
    async def test_invalid_type(self):
        from app.agent.tools.create_worker import CreateWorkerTool

        mock_client = MagicMock()
        tool = CreateWorkerTool(mock_client)

        result = await tool.execute(name="Bad", worker_type="invalid")
        assert "error" in result

    def test_tool_spec(self):
        from app.agent.tools.create_worker import CreateWorkerTool

        mock_client = MagicMock()
        tool = CreateWorkerTool(mock_client)
        spec = tool.to_tool_spec()
        assert spec["function"]["name"] == "create_worker"
        assert "worker_type" in spec["function"]["parameters"]["properties"]


class TestRegisterAgentTool:
    @pytest.mark.asyncio
    async def test_register(self):
        from app.agent.tools.register_agent import RegisterAgentTool

        mock_client = MagicMock()
        mock_client.register_external_agent = AsyncMock(
            return_value={"id": "agent-new", "name": "NotionForge", "status": "registered"}
        )
        tool = RegisterAgentTool(mock_client)

        result = await tool.execute(
            name="NotionForge",
            description="AI 템플릿 자동 생성",
            instructions="사용자 요청에 따라 Notion 워크스페이스를 생성합니다.",
        )
        assert result["status"] == "registered"

    def test_tool_spec(self):
        from app.agent.tools.register_agent import RegisterAgentTool

        mock_client = MagicMock()
        tool = RegisterAgentTool(mock_client)
        spec = tool.to_tool_spec()
        assert spec["function"]["name"] == "register_external_agent"
        assert "instructions" in spec["function"]["parameters"]["properties"]


# ============================================================
# ToolRegistry 통합 테스트
# ============================================================


class TestToolRegistryIntegration:
    def test_new_tools_registered(self):
        from app.agent.tools.registry import ToolRegistry

        mock_client = MagicMock()
        mock_client.mock_mode = True
        registry = ToolRegistry(mock_client)
        names = registry.list_names()
        assert "create_worker" in names
        assert "register_external_agent" in names
        assert len(names) == 11
