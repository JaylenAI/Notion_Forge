"""Agent Tools 단위 테스트 — add_blocks, add_database_items, create_columns,
create_database, create_view, link_databases"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.agent.tools.add_blocks import AddBlocksTool, spec_to_block
from app.agent.tools.add_database_items import (
    AddDatabaseItemsTool,
    _blueprint_to_real_props,
    _build_item_props,
    _build_property_name_map,
    _format_value,
    _similarity,
)
from app.agent.tools.create_columns import CreateColumnsTool
from app.agent.tools.create_database import CreateDatabaseTool
from app.agent.tools.create_view import CreateViewTool
from app.agent.tools.link_databases import LinkDatabasesTool

# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def mock_client():
    client = MagicMock()
    client.add_blocks = AsyncMock(return_value=[{"id": "block-1"}, {"id": "block-2"}])
    client.add_database_item = AsyncMock(return_value={"id": "item-1"})
    client.create_database = AsyncMock(return_value={"id": "db-123", "url": "https://notion.so/db-123"})
    client.create_view = AsyncMock(return_value={"id": "view-1", "type": "board"})
    client.update_database = AsyncMock(return_value={"id": "db-123"})
    client.get_database = AsyncMock(
        return_value={
            "properties": {
                "Name": {"type": "title", "id": "title"},
                "Status": {"type": "status", "id": "abc1"},
                "Priority": {"type": "select", "id": "abc2"},
                "Due Date": {"type": "date", "id": "abc3"},
            }
        }
    )
    return client


# ============================================================
# AddBlocksTool Tests
# ============================================================


class TestAddBlocksTool:
    async def test_execute_basic_blocks(self, mock_client):
        tool = AddBlocksTool(mock_client)
        result = await tool.execute(
            page_id="page-1",
            blocks=[
                {"type": "paragraph", "text": "Hello"},
                {"type": "heading_1", "text": "Title"},
            ],
        )
        assert result["block_count"] == 2
        mock_client.add_blocks.assert_called_once()
        call_args = mock_client.add_blocks.call_args
        assert call_args[0][0] == "page-1"
        assert len(call_args[0][1]) == 2

    async def test_execute_skips_database_ref(self, mock_client):
        tool = AddBlocksTool(mock_client)
        result = await tool.execute(
            page_id="page-1",
            blocks=[
                {"type": "paragraph", "text": "Keep"},
                {"type": "database_ref", "db_index": 0},
                {"type": "divider"},
            ],
        )
        assert result["block_count"] == 2
        call_args = mock_client.add_blocks.call_args
        assert len(call_args[0][1]) == 2

    async def test_execute_empty_blocks(self, mock_client):
        mock_client.add_blocks = AsyncMock(return_value=[])
        tool = AddBlocksTool(mock_client)
        result = await tool.execute(page_id="page-1", blocks=[])
        assert result["block_count"] == 0

    def test_tool_spec(self, mock_client):
        tool = AddBlocksTool(mock_client)
        spec = tool.to_tool_spec()
        assert spec["function"]["name"] == "add_blocks"
        assert "page_id" in spec["function"]["parameters"]["properties"]
        assert "blocks" in spec["function"]["parameters"]["properties"]


# ============================================================
# spec_to_block Tests (data transformation logic)
# ============================================================


class TestSpecToBlock:
    def test_paragraph_basic(self):
        block = spec_to_block({"type": "paragraph", "text": "Hello world"})
        assert block["type"] == "paragraph"
        assert block["paragraph"]["rich_text"][0]["text"]["content"] == "Hello world"

    def test_paragraph_with_rich_text(self):
        block = spec_to_block(
            {
                "type": "paragraph",
                "rich_text": [
                    {"text": "Bold", "bold": True},
                    {"text": " normal"},
                ],
            }
        )
        assert block["type"] == "paragraph"
        rt = block["paragraph"]["rich_text"]
        assert len(rt) == 2
        assert rt[0]["annotations"]["bold"] is True

    def test_heading_1(self):
        block = spec_to_block({"type": "heading_1", "text": "Section"})
        assert block["type"] == "heading_1"

    def test_heading_2_with_color(self):
        block = spec_to_block({"type": "heading_2", "text": "Sub", "color": "blue"})
        assert block["type"] == "heading_2"

    def test_heading_3(self):
        block = spec_to_block({"type": "heading_3", "text": "Sub Sub"})
        assert block["type"] == "heading_3"

    def test_toggle_heading(self):
        block = spec_to_block(
            {
                "type": "toggle_heading",
                "text": "Toggle Title",
                "level": 2,
                "children": [{"type": "paragraph", "text": "Content"}],
            }
        )
        assert block["type"] == "heading_2"
        assert block["heading_2"].get("is_toggleable") is True

    def test_callout_basic(self):
        block = spec_to_block({"type": "callout", "text": "Note", "icon": "💡"})
        assert block["type"] == "callout"
        assert block["callout"]["icon"]["emoji"] == "💡"

    def test_callout_with_rich_text(self):
        block = spec_to_block(
            {
                "type": "callout",
                "rich_text": [{"text": "Important", "bold": True}],
                "icon": "🚨",
            }
        )
        assert block["type"] == "callout"
        assert block["callout"]["rich_text"][0]["annotations"]["bold"] is True

    def test_callout_with_children(self):
        block = spec_to_block(
            {
                "type": "callout",
                "text": "Parent",
                "icon": "📌",
                "children": [{"type": "paragraph", "text": "Child"}],
            }
        )
        assert block["type"] == "callout"
        assert "children" in block["callout"]

    def test_toggle_basic(self):
        block = spec_to_block({"type": "toggle", "text": "Click me"})
        assert block["type"] == "toggle"
        # toggle must always have children
        assert "children" in block["toggle"]

    def test_toggle_with_children_text(self):
        block = spec_to_block({"type": "toggle", "text": "FAQ", "children_text": "Answer here"})
        assert block["type"] == "toggle"

    def test_toggle_with_children_blocks(self):
        block = spec_to_block(
            {
                "type": "toggle",
                "text": "Section",
                "children": [{"type": "paragraph", "text": "Content"}],
            }
        )
        assert block["type"] == "toggle"

    def test_to_do(self):
        block = spec_to_block({"type": "to_do", "text": "Task", "checked": True})
        assert block["type"] == "to_do"
        assert block["to_do"]["checked"] is True

    def test_to_do_unchecked(self):
        block = spec_to_block({"type": "to_do", "text": "Task"})
        assert block["to_do"]["checked"] is False

    def test_divider(self):
        block = spec_to_block({"type": "divider"})
        assert block["type"] == "divider"

    def test_bulleted_list(self):
        block = spec_to_block({"type": "bulleted_list", "text": "Item 1"})
        assert block["type"] == "bulleted_list_item"

    def test_numbered_list(self):
        block = spec_to_block({"type": "numbered_list", "text": "Step 1"})
        assert block["type"] == "numbered_list_item"

    def test_quote(self):
        block = spec_to_block({"type": "quote", "text": "Wise words"})
        assert block["type"] == "quote"

    def test_table(self):
        block = spec_to_block({"type": "table", "rows": [["A", "B"], ["C", "D"]], "has_column_header": True})
        assert block["type"] == "table"

    def test_bookmark(self):
        block = spec_to_block({"type": "bookmark", "url": "https://notion.so"})
        assert block["type"] == "bookmark"

    def test_image(self):
        block = spec_to_block({"type": "image", "url": "https://img.com/pic.png"})
        assert block["type"] == "image"

    def test_video(self):
        block = spec_to_block({"type": "video", "url": "https://youtube.com/watch?v=x"})
        assert block["type"] == "video"

    def test_audio(self):
        block = spec_to_block({"type": "audio", "url": "https://audio.com/file.mp3"})
        assert block["type"] == "audio"

    def test_file(self):
        block = spec_to_block({"type": "file", "url": "https://files.com/doc.pdf", "name": "Doc"})
        assert block["type"] == "file"

    def test_pdf(self):
        block = spec_to_block({"type": "pdf", "url": "https://files.com/report.pdf"})
        assert block["type"] == "pdf"

    def test_code_block(self):
        block = spec_to_block({"type": "code", "code": "print('hello')", "language": "python"})
        assert block["type"] == "code"

    def test_embed(self):
        block = spec_to_block({"type": "embed", "url": "https://twitter.com/status/123"})
        assert block["type"] == "embed"

    def test_table_of_contents(self):
        block = spec_to_block({"type": "table_of_contents"})
        assert block["type"] == "table_of_contents"

    def test_breadcrumb(self):
        block = spec_to_block({"type": "breadcrumb"})
        assert block["type"] == "breadcrumb"

    def test_equation(self):
        block = spec_to_block({"type": "equation", "expression": "E=mc^2"})
        assert block["type"] == "equation"

    def test_synced_block_original(self):
        block = spec_to_block({"type": "synced_block", "children": [{"type": "paragraph", "text": "Synced"}]})
        assert block["type"] == "synced_block"
        assert block["synced_block"]["synced_from"] is None

    def test_synced_block_duplicate(self):
        block = spec_to_block({"type": "synced_block", "original_block_id": "block-abc"})
        assert block["type"] == "synced_block"
        assert block["synced_block"]["synced_from"]["block_id"] == "block-abc"

    def test_column_list(self):
        block = spec_to_block(
            {
                "type": "column_list",
                "columns": [
                    [{"type": "paragraph", "text": "Col 1"}],
                    [{"type": "paragraph", "text": "Col 2"}],
                ],
            }
        )
        assert block["type"] == "column_list"

    def test_column_list_with_dict_columns(self):
        block = spec_to_block(
            {
                "type": "column_list",
                "columns": [
                    {"blocks": [{"type": "paragraph", "text": "Col 1"}]},
                    {"blocks": [{"type": "paragraph", "text": "Col 2"}]},
                ],
            }
        )
        assert block["type"] == "column_list"

    def test_column_list_skips_database_ref(self):
        block = spec_to_block(
            {
                "type": "column_list",
                "columns": [
                    [{"type": "paragraph", "text": "Keep"}, {"type": "database_ref", "db_index": 0}],
                ],
            }
        )
        assert block["type"] == "column_list"

    def test_link_to_page(self):
        block = spec_to_block({"type": "link_to_page", "page_id": "page-abc"})
        assert block["type"] == "link_to_page"

    def test_unknown_type_fallback(self):
        block = spec_to_block({"type": "unknown_widget", "text": "fallback"})
        assert block["type"] == "paragraph"
        assert "fallback" in block["paragraph"]["rich_text"][0]["text"]["content"]

    def test_unknown_type_no_text(self):
        block = spec_to_block({"type": "nonexistent"})
        assert block["type"] == "paragraph"
        assert "[nonexistent]" in block["paragraph"]["rich_text"][0]["text"]["content"]


# ============================================================
# AddDatabaseItemsTool Tests
# ============================================================


class TestAddDatabaseItemsTool:
    async def test_execute_adds_items(self, mock_client):
        tool = AddDatabaseItemsTool(mock_client)
        result = await tool.execute(
            database_id="db-1",
            items=[
                {"Name": "Task 1", "Status": "진행 중"},
                {"Name": "Task 2", "Status": "완료"},
            ],
            db_properties={"Name": "title", "Status": "status"},
        )
        assert result["item_count"] == 2
        assert len(result["errors"]) == 0

    async def test_execute_handles_item_failure(self, mock_client):
        mock_client.add_database_item = AsyncMock(side_effect=Exception("API Error"))
        tool = AddDatabaseItemsTool(mock_client)
        result = await tool.execute(
            database_id="db-1",
            items=[{"Name": "Task 1"}],
            db_properties={"Name": "title"},
        )
        assert result["item_count"] == 0
        assert len(result["errors"]) == 1

    async def test_execute_fallback_when_db_unreachable(self, mock_client):
        mock_client.get_database = AsyncMock(side_effect=Exception("Not found"))
        tool = AddDatabaseItemsTool(mock_client)
        result = await tool.execute(
            database_id="db-1",
            items=[{"Title": "Item"}],
            db_properties={"Title": "title"},
        )
        # Falls back to blueprint props
        assert result["item_count"] == 1

    async def test_execute_empty_items(self, mock_client):
        tool = AddDatabaseItemsTool(mock_client)
        result = await tool.execute(
            database_id="db-1",
            items=[],
            db_properties={},
        )
        assert result["item_count"] == 0

    def test_tool_spec(self, mock_client):
        tool = AddDatabaseItemsTool(mock_client)
        spec = tool.to_tool_spec()
        assert spec["function"]["name"] == "add_database_items"
        required = spec["function"]["parameters"]["required"]
        assert "database_id" in required
        assert "items" in required
        # db_properties is optional
        assert "db_properties" not in required


# ============================================================
# Helper Functions Tests (add_database_items module)
# ============================================================


class TestBlueprintToRealProps:
    def test_title_string(self):
        result = _blueprint_to_real_props({"Name": "title"})
        assert result["Name"]["type"] == "title"

    def test_title_dict(self):
        result = _blueprint_to_real_props({"Name": {"type": "title"}})
        assert result["Name"]["type"] == "title"

    def test_string_type(self):
        result = _blueprint_to_real_props({"Status": "status", "Score": "number"})
        assert result["Status"]["type"] == "status"
        assert result["Score"]["type"] == "number"

    def test_dict_type(self):
        result = _blueprint_to_real_props({"Category": {"type": "select", "options": ["A", "B"]}})
        assert result["Category"]["type"] == "select"

    def test_unknown_type_fallback(self):
        result = _blueprint_to_real_props({"Weird": 123})
        assert result["Weird"]["type"] == "rich_text"


class TestBuildPropertyNameMap:
    def test_exact_match(self):
        bp = {"Name": "title", "Status": "status"}
        real = {"Name": {"type": "title", "id": "t"}, "Status": {"type": "status", "id": "s"}}
        result = _build_property_name_map(bp, real)
        assert result["Name"] == "Name"
        assert result["Status"] == "Status"

    def test_title_force_map(self):
        bp = {"Title": "title"}
        real = {"Name": {"type": "title", "id": "t"}}
        result = _build_property_name_map(bp, real)
        assert result["Title"] == "Name"

    def test_fuzzy_match(self):
        bp = {"Due Date": "date"}
        real = {"DueDate": {"type": "date", "id": "d"}}
        result = _build_property_name_map(bp, real)
        assert result["Due Date"] == "DueDate"

    def test_sequential_type_match(self):
        bp = {"Score": "number", "Amount": "number"}
        real = {
            "Value": {"type": "number", "id": "n1"},
            "Total": {"type": "number", "id": "n2"},
        }
        result = _build_property_name_map(bp, real)
        # Both should be mapped to some real prop
        assert len(result) == 2
        assert set(result.values()) == {"Value", "Total"}


class TestSimilarity:
    def test_identical(self):
        assert _similarity("hello", "hello") == 1.0

    def test_case_insensitive(self):
        assert _similarity("Hello", "hello") == 1.0

    def test_different(self):
        score = _similarity("abc", "xyz")
        assert score < 0.5

    def test_partial(self):
        score = _similarity("Due Date", "DueDate")
        assert score > 0.5


class TestFormatValue:
    def test_title(self):
        result = _format_value("title", "My Title")
        assert result == {"title": [{"text": {"content": "My Title"}}]}

    def test_rich_text(self):
        result = _format_value("rich_text", "Note")
        assert result == {"rich_text": [{"text": {"content": "Note"}}]}

    def test_select(self):
        result = _format_value("select", "High")
        assert result == {"select": {"name": "High"}}

    def test_multi_select_list(self):
        result = _format_value("multi_select", ["A", "B"])
        assert result == {"multi_select": [{"name": "A"}, {"name": "B"}]}

    def test_multi_select_string(self):
        result = _format_value("multi_select", "Tag")
        assert result == {"multi_select": [{"name": "Tag"}]}

    def test_status_english_mapping(self):
        result = _format_value("status", "in progress")
        assert result == {"status": {"name": "진행 중"}}

    def test_status_korean(self):
        result = _format_value("status", "완료")
        assert result == {"status": {"name": "완료"}}

    def test_status_korean_variation(self):
        result = _format_value("status", "진행중")
        assert result == {"status": {"name": "진행 중"}}

    def test_checkbox_bool(self):
        assert _format_value("checkbox", True) == {"checkbox": True}
        assert _format_value("checkbox", False) == {"checkbox": False}

    def test_checkbox_string(self):
        assert _format_value("checkbox", "true") == {"checkbox": True}
        assert _format_value("checkbox", "no") == {"checkbox": False}

    def test_number_int(self):
        assert _format_value("number", 42) == {"number": 42.0}

    def test_number_with_comma(self):
        assert _format_value("number", "1,000") == {"number": 1000.0}

    def test_number_with_currency(self):
        assert _format_value("number", "$50") == {"number": 50.0}
        assert _format_value("number", "1000원") == {"number": 1000.0}

    def test_number_invalid(self):
        assert _format_value("number", "abc") == {"number": None}

    def test_url(self):
        assert _format_value("url", "https://example.com") == {"url": "https://example.com"}

    def test_url_empty(self):
        assert _format_value("url", "") == {"url": None}

    def test_email(self):
        assert _format_value("email", "a@b.com") == {"email": "a@b.com"}

    def test_date(self):
        result = _format_value("date", "2024-01-15")
        assert result == {"date": {"start": "2024-01-15"}}

    def test_date_truncation(self):
        result = _format_value("date", "2024-01-15T10:00:00")
        assert result == {"date": {"start": "2024-01-15"}}

    def test_date_none(self):
        assert _format_value("date", "") == {"date": None}

    def test_people_string_name(self):
        # Non-user-id string falls back to rich_text
        result = _format_value("people", "John")
        assert "rich_text" in result

    def test_people_user_id(self):
        result = _format_value("people", "user_abc123")
        assert result == {"people": [{"id": "user_abc123"}]}

    def test_people_list(self):
        result = _format_value("people", ["u1", "u2"])
        assert result == {"people": [{"id": "u1"}, {"id": "u2"}]}

    def test_files_list(self):
        result = _format_value("files", ["https://f.com/a.pdf"])
        assert result["files"][0]["external"]["url"] == "https://f.com/a.pdf"

    def test_files_string(self):
        result = _format_value("files", "https://f.com/b.png")
        assert result["files"][0]["external"]["url"] == "https://f.com/b.png"

    def test_phone_number(self):
        assert _format_value("phone_number", "010-1234-5678") == {"phone_number": "010-1234-5678"}

    def test_relation_list(self):
        result = _format_value("relation", ["id1", "id2"])
        assert result == {"relation": [{"id": "id1"}, {"id": "id2"}]}

    def test_relation_string(self):
        result = _format_value("relation", "id1")
        assert result == {"relation": [{"id": "id1"}]}

    def test_unknown_type_fallback(self):
        result = _format_value("formula", "x + y")
        assert result == {"rich_text": [{"text": {"content": "x + y"}}]}


class TestBuildItemProps:
    def test_basic_mapping(self):
        item = {"Name": "Task 1", "Status": "진행 중"}
        bp_props = {"Name": "title", "Status": "status"}
        real_props = {
            "Name": {"type": "title", "id": "t"},
            "Status": {"type": "status", "id": "s"},
        }
        name_map = {"Name": "Name", "Status": "Status"}
        result = _build_item_props(item, bp_props, real_props, name_map)
        assert "Name" in result
        assert result["Name"]["title"][0]["text"]["content"] == "Task 1"

    def test_skips_icon_and_cover(self):
        item = {"Name": "Item", "icon": "📌", "cover_url": "https://img.com"}
        bp_props = {"Name": "title"}
        real_props = {"Name": {"type": "title", "id": "t"}}
        name_map = {"Name": "Name"}
        result = _build_item_props(item, bp_props, real_props, name_map)
        assert "icon" not in result
        assert "cover_url" not in result

    def test_fallback_title_injection(self):
        item = {"Priority": "High"}
        bp_props = {"Priority": "select"}
        real_props = {
            "Name": {"type": "title", "id": "t"},
            "Priority": {"type": "select", "id": "p"},
        }
        name_map = {"Priority": "Priority"}
        result = _build_item_props(item, bp_props, real_props, name_map)
        # Should inject title with first value
        assert "Name" in result


# ============================================================
# CreateColumnsTool Tests
# ============================================================


class TestCreateColumnsTool:
    async def test_execute_basic(self, mock_client):
        tool = CreateColumnsTool(mock_client)
        result = await tool.execute(
            page_id="page-1",
            columns=[
                {"blocks": [{"type": "paragraph", "text": "Col 1"}]},
                {"blocks": [{"type": "paragraph", "text": "Col 2"}]},
            ],
        )
        assert result["column_count"] == 2
        mock_client.add_blocks.assert_called_once()

    async def test_execute_skips_database_ref_in_columns(self, mock_client):
        tool = CreateColumnsTool(mock_client)
        result = await tool.execute(
            page_id="page-1",
            columns=[
                {"blocks": [{"type": "paragraph", "text": "Keep"}, {"type": "database_ref", "db_index": 0}]},
            ],
        )
        assert result["column_count"] == 1

    async def test_execute_empty_columns(self, mock_client):
        mock_client.add_blocks = AsyncMock(return_value=[{"id": "block-1"}])
        tool = CreateColumnsTool(mock_client)
        result = await tool.execute(page_id="page-1", columns=[])
        assert result["column_count"] == 0

    def test_tool_spec(self, mock_client):
        tool = CreateColumnsTool(mock_client)
        spec = tool.to_tool_spec()
        assert spec["function"]["name"] == "create_columns"


# ============================================================
# CreateDatabaseTool Tests
# ============================================================


class TestCreateDatabaseTool:
    async def test_execute_basic(self, mock_client):
        tool = CreateDatabaseTool(mock_client)
        result = await tool.execute(
            parent_id="page-1",
            title="Tasks DB",
            properties={"Name": "title", "Status": "status"},
        )
        assert result["id"] == "db-123"
        mock_client.create_database.assert_called_once()
        call_kwargs = mock_client.create_database.call_args[1]
        assert call_kwargs["parent_id"] == "page-1"
        assert call_kwargs["title"] == "Tasks DB"
        assert call_kwargs["is_inline"] is True

    async def test_execute_not_inline(self, mock_client):
        tool = CreateDatabaseTool(mock_client)
        await tool.execute(
            parent_id="page-1",
            title="DB",
            properties={"Name": "title"},
            is_inline=False,
        )
        call_kwargs = mock_client.create_database.call_args[1]
        assert call_kwargs["is_inline"] is False

    def test_tool_spec(self, mock_client):
        tool = CreateDatabaseTool(mock_client)
        spec = tool.to_tool_spec()
        assert spec["function"]["name"] == "create_database"
        required = spec["function"]["parameters"]["required"]
        assert "parent_id" in required
        assert "title" in required
        assert "properties" in required
        assert "is_inline" not in required


# ============================================================
# CreateViewTool Tests
# ============================================================


class TestCreateViewTool:
    async def test_execute_board_with_group_by(self, mock_client):
        tool = CreateViewTool(mock_client)
        result = await tool.execute(
            database_id="db-1",
            view_type="board",
            title="Board View",
            group_by="Status",
        )
        assert result["id"] == "view-1"
        call_kwargs = mock_client.create_view.call_args[1]
        assert call_kwargs["database_id"] == "db-1"
        assert call_kwargs["view_type"] == "board"
        assert call_kwargs["group_by"] == {"property": "Status", "type": "exact"}

    async def test_execute_calendar_without_group_by(self, mock_client):
        tool = CreateViewTool(mock_client)
        await tool.execute(
            database_id="db-1",
            view_type="calendar",
        )
        call_kwargs = mock_client.create_view.call_args[1]
        assert call_kwargs["group_by"] is None
        assert call_kwargs["title"] == ""

    async def test_execute_with_sorts(self, mock_client):
        tool = CreateViewTool(mock_client)
        sorts = [{"property": "Due Date", "direction": "ascending"}]
        await tool.execute(
            database_id="db-1",
            view_type="table",
            sorts=sorts,
        )
        call_kwargs = mock_client.create_view.call_args[1]
        assert call_kwargs["sorts"] == sorts

    def test_tool_spec(self, mock_client):
        tool = CreateViewTool(mock_client)
        spec = tool.to_tool_spec()
        assert spec["function"]["name"] == "create_view"
        required = spec["function"]["parameters"]["required"]
        assert "database_id" in required
        assert "view_type" in required
        assert "title" not in required


# ============================================================
# LinkDatabasesTool Tests
# ============================================================


class TestLinkDatabasesTool:
    async def test_execute_basic(self, mock_client):
        tool = LinkDatabasesTool(mock_client)
        result = await tool.execute(
            source_db_id="db-source",
            target_db_id="db-target",
        )
        assert result["success"] is True
        call_args = mock_client.update_database.call_args[0]
        assert call_args[0] == "db-source"
        updates = call_args[1]
        assert "관련 항목" in updates["properties"]
        relation = updates["properties"]["관련 항목"]["relation"]
        assert relation["database_id"] == "db-target"

    async def test_execute_custom_relation_name(self, mock_client):
        tool = LinkDatabasesTool(mock_client)
        await tool.execute(
            source_db_id="db-source",
            target_db_id="db-target",
            relation_name="프로젝트",
        )
        updates = mock_client.update_database.call_args[0][1]
        assert "프로젝트" in updates["properties"]

    def test_tool_spec(self, mock_client):
        tool = LinkDatabasesTool(mock_client)
        spec = tool.to_tool_spec()
        assert spec["function"]["name"] == "link_databases"
        required = spec["function"]["parameters"]["required"]
        assert "source_db_id" in required
        assert "target_db_id" in required
        assert "relation_name" not in required
