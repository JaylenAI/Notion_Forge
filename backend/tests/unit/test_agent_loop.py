"""AgentLoop 단위 테스트"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.agent.agent_loop import AgentLoop


@pytest.fixture
def mock_client():
    client = MagicMock()
    client.create_page = AsyncMock(return_value={"id": "page-1", "url": "https://notion.so/page-1"})
    client.create_database = AsyncMock(return_value={"id": "db-1"})
    client.add_blocks = AsyncMock(return_value=[{"id": "block-1"}])
    client.add_database_item = AsyncMock(return_value={"id": "item-1"})
    client.update_database = AsyncMock(return_value={"id": "db-1"})
    return client


class TestResolveRefs:
    def test_no_refs(self, mock_client):
        loop = AgentLoop(client=mock_client)
        args = {"parent_id": "abc", "title": "Test"}
        assert loop._resolve_refs(args) == {"parent_id": "abc", "title": "Test"}

    def test_step_ref_resolved(self, mock_client):
        loop = AgentLoop(client=mock_client)
        loop.step_results[1] = {"id": "page-123", "url": "https://notion.so/page-123"}
        args = {"parent_id": "$step1.id"}
        result = loop._resolve_refs(args)
        assert result["parent_id"] == "page-123"

    def test_step_ref_url_field(self, mock_client):
        loop = AgentLoop(client=mock_client)
        loop.step_results[2] = {"id": "db-1", "url": "https://notion.so/db-1"}
        args = {"link": "$step2.url"}
        result = loop._resolve_refs(args)
        assert result["link"] == "https://notion.so/db-1"

    def test_step_ref_default_to_id(self, mock_client):
        loop = AgentLoop(client=mock_client)
        loop.step_results[1] = {"id": "page-1"}
        args = {"ref": "$step1"}
        result = loop._resolve_refs(args)
        assert result["ref"] == "page-1"

    def test_step_ref_missing_step(self, mock_client):
        loop = AgentLoop(client=mock_client)
        args = {"parent_id": "$step5.id"}
        result = loop._resolve_refs(args)
        assert result["parent_id"] == "$step5.id"

    def test_mixed_refs_and_literals(self, mock_client):
        loop = AgentLoop(client=mock_client)
        loop.step_results[1] = {"id": "page-1"}
        args = {"parent_id": "$step1.id", "title": "My Page", "icon": "📝"}
        result = loop._resolve_refs(args)
        assert result == {"parent_id": "page-1", "title": "My Page", "icon": "📝"}


class TestAgentLoopRun:
    @pytest.mark.asyncio
    async def test_plan_failure_returns_error(self, mock_client):
        loop = AgentLoop(client=mock_client)
        with patch.object(loop, "_plan", return_value=None):
            result = await loop.run("test prompt", parent_page_id="parent-1")
        assert result["success"] is False
        assert "계획 수립 실패" in result["error"]

    @pytest.mark.asyncio
    async def test_successful_single_step(self, mock_client):
        loop = AgentLoop(client=mock_client)
        plan = {
            "plan": [
                {"step": 1, "tool": "apply_color_theme", "args": {"theme": "blue"}, "description": "테마 적용"},
            ],
            "reasoning": "단일 스텝 테스트",
        }
        with patch.object(loop, "_plan", return_value=plan):
            result = await loop.run("blue theme", parent_page_id="parent-1")
        assert result["success"] is True
        assert result["steps_completed"] == 1
        assert result["steps_total"] == 1

    @pytest.mark.asyncio
    async def test_multi_step_with_refs(self, mock_client):
        loop = AgentLoop(client=mock_client)
        plan = {
            "plan": [
                {"step": 1, "tool": "create_page", "args": {"parent_id": "parent-1", "title": "Main"}, "description": "메인 페이지"},
                {"step": 2, "tool": "apply_color_theme", "args": {"theme": "green"}, "description": "테마"},
            ],
            "reasoning": "2단계 테스트",
        }
        with patch.object(loop, "_plan", return_value=plan):
            result = await loop.run("green project", parent_page_id="parent-1")
        assert result["success"] is True
        assert result["steps_completed"] == 2
        assert result["page_id"] == "page-1"

    @pytest.mark.asyncio
    async def test_step_failure_triggers_reflect(self, mock_client):
        loop = AgentLoop(client=mock_client)
        plan = {
            "plan": [
                {"step": 1, "tool": "nonexistent_tool", "args": {}, "description": "없는 도구"},
            ],
            "reasoning": "실패 테스트",
        }
        reflection = {"action": "continue", "feedback": "skip"}
        with patch.object(loop, "_plan", return_value=plan), \
             patch.object(loop, "_reflect", return_value=reflection):
            result = await loop.run("fail test", parent_page_id="parent-1")
        assert result["steps_completed"] == 1

    @pytest.mark.asyncio
    async def test_retry_on_reflect(self, mock_client):
        loop = AgentLoop(client=mock_client)
        plan = {
            "plan": [
                {"step": 1, "tool": "apply_color_theme", "args": {"theme": "invalid"}, "description": "테마"},
            ],
            "reasoning": "retry 테스트",
        }
        original_execute = loop.registry.execute
        call_count = 0

        async def mock_execute(tool_name, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return {"error": "invalid theme"}
            return await original_execute(tool_name, **kwargs)

        reflection = {"action": "retry", "modified_args": {"theme": "blue"}}
        with patch.object(loop, "_plan", return_value=plan), \
             patch.object(loop, "_reflect", return_value=reflection), \
             patch.object(loop.registry, "execute", side_effect=mock_execute):
            result = await loop.run("retry test", parent_page_id="parent-1")
        assert call_count == 2


class TestAgentLoopPlan:
    @pytest.mark.asyncio
    async def test_plan_calls_provider(self, mock_client):
        loop = AgentLoop(client=mock_client)
        mock_plan = {"plan": [{"step": 1, "tool": "create_page", "args": {}}], "reasoning": "test"}
        loop.provider.call = AsyncMock(return_value=mock_plan)
        result = await loop._plan("test request", "parent-1")
        assert result == mock_plan
        loop.provider.call.assert_called_once()

    @pytest.mark.asyncio
    async def test_plan_includes_tool_descriptions(self, mock_client):
        loop = AgentLoop(client=mock_client)
        loop.provider.call = AsyncMock(return_value=None)
        await loop._plan("test", "parent-1")
        call_args = loop.provider.call.call_args
        system_prompt = call_args[0][0]
        assert "create_page" in system_prompt
        assert "create_database" in system_prompt


class TestAgentLoopReflect:
    @pytest.mark.asyncio
    async def test_reflect_returns_fallback_on_none(self, mock_client):
        loop = AgentLoop(client=mock_client)
        loop.provider.call = AsyncMock(return_value=None)
        result = await loop._reflect({"step": 1, "tool": "t"}, {"error": "fail"})
        assert result["action"] == "continue"

    @pytest.mark.asyncio
    async def test_reflect_passes_context(self, mock_client):
        loop = AgentLoop(client=mock_client)
        loop.provider.call = AsyncMock(return_value={"action": "done", "feedback": "ok"})
        result = await loop._reflect({"step": 1}, {"id": "x"})
        assert result["action"] == "done"
