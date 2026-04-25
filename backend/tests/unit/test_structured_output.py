"""Structured Output (Pydantic 검증) + Function Calling 테스트"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.agent.agent_loop import AgentLoop
from app.agent.providers.base import BaseProvider
from app.schemas.blueprint import AIContentSpec, validate_ai_content


class TestAIContentSpec:
    def test_valid_content(self):
        raw = {
            "title": "테스트",
            "icon": "🧪",
            "color": "blue",
            "blocks": [{"type": "callout", "text": "Hi"}],
            "databases": [{"title": "DB1", "db_properties": {"이름": "title"}}],
        }
        spec = AIContentSpec.model_validate(raw)
        assert spec.title == "테스트"
        assert len(spec.blocks) == 1
        assert len(spec.databases) == 1

    def test_extra_fields_allowed(self):
        raw = {
            "title": "테스트",
            "blocks": [],
            "databases": [],
            "custom_field": "allowed",
        }
        spec = AIContentSpec.model_validate(raw)
        assert spec.title == "테스트"

    def test_defaults(self):
        raw = {}
        spec = AIContentSpec.model_validate(raw)
        assert spec.title == ""
        assert spec.color == "blue"
        assert spec.blocks == []
        assert spec.databases == []


class TestValidateAIContent:
    def test_valid_content_passes(self):
        raw = {
            "title": "운동 기록",
            "blocks": [{"type": "callout", "text": "Hi"}],
            "databases": [{"title": "DB1", "db_properties": {"이름": "title"}, "sample_items": []}],
        }
        result, errors = validate_ai_content(raw)
        assert len(errors) == 0
        assert result["title"] == "운동 기록"

    def test_empty_blocks_error(self):
        raw = {
            "title": "테스트",
            "blocks": [],
            "databases": [{"title": "DB1", "db_properties": {"이름": "title"}}],
        }
        _, errors = validate_ai_content(raw)
        assert any("blocks" in e for e in errors)

    def test_empty_databases_error(self):
        raw = {
            "title": "테스트",
            "blocks": [{"type": "callout", "text": "Hi"}],
            "databases": [],
        }
        _, errors = validate_ai_content(raw)
        assert any("databases" in e for e in errors)

    def test_missing_title_property_error(self):
        raw = {
            "title": "테스트",
            "blocks": [{"type": "callout", "text": "Hi"}],
            "databases": [{"title": "DB1", "db_properties": {"이름": "rich_text"}}],
        }
        _, errors = validate_ai_content(raw)
        assert any("title 타입" in e for e in errors)

    def test_db_properties_normalization(self):
        raw = {
            "title": "테스트",
            "blocks": [{"type": "callout", "text": "Hi"}],
            "db_properties": {"이름": "title", "상태": "status"},
            "sample_items": [{"이름": "A"}, {"이름": "B"}, {"이름": "C"}],
        }
        result, errors = validate_ai_content(raw)
        assert len(errors) == 0
        assert len(result["databases"]) == 1
        assert result["databases"][0]["db_properties"]["이름"] == "title"

    def test_relation_properties_accepted(self):
        raw = {
            "title": "테스트",
            "blocks": [{"type": "callout", "text": "Hi"}],
            "databases": [
                {
                    "title": "DB1",
                    "db_properties": {
                        "이름": "title",
                        "연결": {"type": "relation", "target_db_index": 1},
                    },
                },
                {"title": "DB2", "db_properties": {"이름": "title"}},
            ],
        }
        result, errors = validate_ai_content(raw)
        assert len(errors) == 0


class TestBaseProviderFunctionCalling:
    def test_supports_function_calling_default_false(self):
        assert BaseProvider.supports_function_calling is False

    def test_call_with_tools_default_fallback(self):
        class TestProvider(BaseProvider):
            name = "test"

            async def call(self, system_prompt, user_message, model=""):
                return {"result": "ok"}

        provider = TestProvider()
        assert not provider.supports_function_calling


class TestAgentLoopFunctionCalling:
    @pytest.fixture
    def mock_client(self):
        client = MagicMock()
        client.create_page = AsyncMock(return_value={"id": "page-1", "url": "https://notion.so/page-1"})
        client.create_database = AsyncMock(return_value={"id": "db-1"})
        client.add_blocks = AsyncMock(return_value=[{"id": "block-1"}])
        client.add_database_item = AsyncMock(return_value={"id": "item-1"})
        client.update_database = AsyncMock(return_value={"id": "db-1"})
        return client

    @pytest.mark.asyncio
    async def test_function_calling_plan(self, mock_client):
        loop = AgentLoop(client=mock_client)
        fc_result = {
            "tool_calls": [
                {"name": "create_page", "arguments": {"parent_id": "p1", "title": "테스트"}},
                {"name": "apply_color_theme", "arguments": {"theme": "blue"}},
            ]
        }
        loop.provider.call_with_tools = AsyncMock(return_value=fc_result)
        loop.provider.supports_function_calling = True

        plan = await loop._plan("테스트 만들어줘", "parent-1")
        assert plan is not None
        assert len(plan["plan"]) == 2
        assert plan["plan"][0]["tool"] == "create_page"
        assert plan["plan"][1]["tool"] == "apply_color_theme"
        assert plan["reasoning"] == "Function Calling 기반 계획"

    @pytest.mark.asyncio
    async def test_streaming_run(self, mock_client):
        loop = AgentLoop(client=mock_client)
        plan = {
            "plan": [
                {"step": 1, "tool": "apply_color_theme", "args": {"theme": "blue"}, "description": "테마 적용"},
            ],
            "reasoning": "스트리밍 테스트",
        }

        from unittest.mock import patch

        events = []
        with patch.object(loop, "_plan", return_value=plan):
            async for event in loop.run_streaming("test", "parent-1"):
                events.append(event)

        event_types = [e["type"] for e in events]
        assert "progress" in event_types
        assert "result" in event_types
        result_event = next(e for e in events if e["type"] == "result")
        assert result_event["result"]["success"] is True

    @pytest.mark.asyncio
    async def test_fallback_to_prompt_when_no_fc(self, mock_client):
        loop = AgentLoop(client=mock_client)
        loop.provider.supports_function_calling = False
        plan_dict = {
            "plan": [{"step": 1, "tool": "apply_color_theme", "args": {"theme": "blue"}, "description": "테마"}],
            "reasoning": "프롬프트 기반",
        }
        loop.provider.call = AsyncMock(return_value=plan_dict)

        plan = await loop._plan("test", "parent-1")
        assert plan == plan_dict
        loop.provider.call.assert_called_once()
