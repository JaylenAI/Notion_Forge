"""ToolRegistry 단위 테스트"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.agent.tools.base import BaseTool
from app.agent.tools.registry import ToolRegistry


@pytest.fixture
def mock_client():
    client = MagicMock()
    client.create_page = AsyncMock(return_value={"id": "page-123", "url": "https://notion.so/page-123"})
    client.create_database = AsyncMock(return_value={"id": "db-456"})
    client.add_blocks = AsyncMock(return_value=[{"id": "block-1"}])
    client.add_database_item = AsyncMock(return_value={"id": "item-1"})
    client.update_database = AsyncMock(return_value={"id": "db-456"})
    return client


@pytest.fixture
def registry(mock_client):
    return ToolRegistry(mock_client)


class TestToolRegistryInit:
    def test_registers_all_tools(self, registry):
        names = registry.list_names()
        assert len(names) == 11

    def test_expected_tools_present(self, registry):
        expected = [
            "create_page",
            "create_database",
            "add_blocks",
            "add_database_items",
            "create_columns",
            "link_databases",
            "create_view",
            "create_worker",
            "register_external_agent",
            "apply_color_theme",
            "generate_cover",
        ]
        for name in expected:
            assert registry.get(name) is not None, f"{name} not registered"

    def test_get_unknown_returns_none(self, registry):
        assert registry.get("nonexistent") is None


class TestToolSpecs:
    def test_specs_count(self, registry):
        specs = registry.get_tool_specs()
        assert len(specs) == 11

    def test_spec_structure(self, registry):
        specs = registry.get_tool_specs()
        for spec in specs:
            assert spec["type"] == "function"
            func = spec["function"]
            assert "name" in func
            assert "description" in func
            assert func["parameters"]["type"] == "object"
            assert "properties" in func["parameters"]

    def test_required_fields_exclude_optional(self, registry):
        spec = next(s for s in registry.get_tool_specs() if s["function"]["name"] == "create_page")
        required = spec["function"]["parameters"]["required"]
        assert "parent_id" in required
        assert "title" in required
        assert "icon" not in required
        assert "cover_url" not in required

    def test_descriptions_string(self, registry):
        desc = registry.get_tool_descriptions()
        assert "create_page" in desc
        assert "create_database" in desc
        assert isinstance(desc, str)


class TestToolExecution:
    @pytest.mark.asyncio
    async def test_execute_apply_color_theme(self, registry):
        result = await registry.execute("apply_color_theme", theme="blue")
        assert result["theme"] == "blue"
        assert "background" in result

    @pytest.mark.asyncio
    async def test_execute_generate_cover(self, registry):
        result = await registry.execute("generate_cover", color="green")
        assert result["color"] == "green"
        assert "url" in result

    @pytest.mark.asyncio
    async def test_execute_generate_cover_default(self, registry):
        result = await registry.execute("generate_cover")
        assert result["color"] == "default"

    @pytest.mark.asyncio
    async def test_execute_unknown_tool(self, registry):
        result = await registry.execute("nonexistent_tool")
        assert "error" in result
        assert "Unknown tool" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_create_page(self, registry, mock_client):
        result = await registry.execute(
            "create_page",
            parent_id="parent-1",
            title="Test Page",
            icon="📝",
        )
        assert result["id"] == "page-123"
        mock_client.create_page.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_catches_exception(self, registry, mock_client):
        mock_client.create_page = AsyncMock(side_effect=RuntimeError("API 오류"))
        result = await registry.execute("create_page", parent_id="p", title="T")
        assert "error" in result
        assert "API 오류" in result["error"]


class TestBaseToolSpec:
    def test_to_tool_spec_format(self):
        class DummyTool(BaseTool):
            name = "dummy"
            description = "A test tool"
            parameters = {
                "required_field": {"type": "string", "description": "Required"},
                "optional_field": {"type": "string", "description": "Optional", "optional": True},
            }

            async def execute(self, **kwargs):
                return {}

        spec = DummyTool().to_tool_spec()
        assert spec["type"] == "function"
        assert spec["function"]["name"] == "dummy"
        required = spec["function"]["parameters"]["required"]
        assert "required_field" in required
        assert "optional_field" not in required
