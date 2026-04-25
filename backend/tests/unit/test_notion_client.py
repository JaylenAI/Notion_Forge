"""Notion Client Mock 모드 테스트: 실제 API 호출 없이 모든 메서드 경로 검증"""

from unittest.mock import patch

import pytest

from app.notion.client import NotionClient


@pytest.fixture
def mock_client():
    with patch("app.notion.client.settings") as mock_settings:
        mock_settings.notion_api_key = ""
        mock_settings.notion_parent_page_id = ""
        client = NotionClient(token="", parent_page_id="")
    assert client.mock_mode is True
    return client


class TestMockMode:
    def test_mock_mode_enabled(self, mock_client):
        assert mock_client.mock_mode is True

    async def test_search(self, mock_client):
        result = await mock_client.search(query="test")
        assert result == {"results": []}

    async def test_list_users(self, mock_client):
        result = await mock_client.list_users()
        assert result == []

    async def test_get_user(self, mock_client):
        result = await mock_client.get_user("user-id")
        assert result["id"] == "user-id"

    async def test_add_comment(self, mock_client):
        result = await mock_client.add_comment("테스트 코멘트", page_id="page-id")
        assert "id" in result

    async def test_get_comments(self, mock_client):
        result = await mock_client.get_comments("block-id")
        assert result == []

    async def test_list_custom_emojis(self, mock_client):
        result = await mock_client.list_custom_emojis()
        assert result == []


class TestMockHelpers:
    def test_mock_id_unique(self, mock_client):
        ids = {mock_client._mock_id() for _ in range(100)}
        assert len(ids) == 100

    def test_mock_page(self, mock_client):
        page = mock_client._mock_page("parent-1", "테스트 페이지", "📋", "https://img.com/cover.jpg")
        assert page["object"] == "page"
        assert "id" in page
        assert page["url"].startswith("https://notion.so/")
        assert page["icon"]["emoji"] == "📋"
        assert page["cover"]["external"]["url"] == "https://img.com/cover.jpg"

    def test_mock_page_no_icon_cover(self, mock_client):
        page = mock_client._mock_page("parent-1", "테스트", None, None)
        assert page["icon"] is None
        assert page["cover"] is None

    def test_mock_database(self, mock_client):
        db = mock_client._mock_database("parent-1", "테스트 DB", {"이름": {"title": {}}})
        assert db["object"] == "database"
        assert "id" in db
        assert db["properties"] == {"이름": {"title": {}}}

    def test_mock_blocks(self, mock_client):
        blocks = mock_client._mock_blocks(
            "page-1",
            [
                {"type": "paragraph"},
                {"type": "heading_1"},
            ],
        )
        assert len(blocks) == 2
        assert all("id" in b for b in blocks)

    def test_mock_db_item(self, mock_client):
        item = mock_client._mock_db_item("db-1", {"이름": {"title": []}}, "📌")
        assert item["object"] == "page"
        assert item["icon"]["emoji"] == "📌"


class TestPageOps:
    async def test_create_page_mock(self, mock_client):
        page = await mock_client.create_page(
            parent_id="parent-1",
            title="테스트 페이지",
            icon="📋",
        )
        assert "id" in page
        assert page["object"] == "page"

    async def test_get_page_mock(self, mock_client):
        page = await mock_client.get_page("page-123")
        assert "id" in page

    async def test_update_page_mock(self, mock_client):
        result = await mock_client.update_page("page-123", properties={})
        assert "id" in result

    async def test_archive_page_mock(self, mock_client):
        result = await mock_client.archive_page("page-123")
        assert result.get("in_trash") is True

    async def test_delete_page_mock(self, mock_client):
        result = await mock_client.delete_page("page-123")
        assert result is True

    async def test_move_page_mock(self, mock_client):
        result = await mock_client.move_page("page-123", "new-parent")
        assert result["parent"]["page_id"] == "new-parent"

    async def test_restore_page_mock(self, mock_client):
        result = await mock_client.restore_page("page-123")
        assert result.get("in_trash") is False

    async def test_lock_page_mock(self, mock_client):
        result = await mock_client.lock_page("page-123", locked=True)
        assert result["is_locked"] is True


class TestDatabaseOps:
    async def test_create_database_mock(self, mock_client):
        db = await mock_client.create_database(
            parent_id="parent-1",
            title="테스트 DB",
            properties={"이름": {"title": {}}},
        )
        assert "id" in db

    async def test_get_database_mock(self, mock_client):
        db = await mock_client.get_database("db-123")
        assert "id" in db

    async def test_query_database_mock(self, mock_client):
        result = await mock_client.query_database("db-123")
        assert isinstance(result, list)

    async def test_add_database_item_mock(self, mock_client):
        result = await mock_client.add_database_item(
            database_id="db-123",
            properties={},
        )
        assert "id" in result


class TestBlockOps:
    async def test_add_blocks_mock(self, mock_client):
        result = await mock_client.add_blocks(
            "page-123",
            [
                {"type": "paragraph", "paragraph": {"rich_text": []}},
            ],
        )
        assert isinstance(result, list)

    async def test_get_block_children_mock(self, mock_client):
        result = await mock_client.get_block_children("page-123")
        assert isinstance(result, list)

    async def test_get_block_mock(self, mock_client):
        result = await mock_client.get_block("block-123")
        assert result["id"] == "block-123"

    async def test_delete_block_mock(self, mock_client):
        result = await mock_client.delete_block("block-123")
        assert result is not None

    async def test_update_block_mock(self, mock_client):
        result = await mock_client.update_block("block-123", {})
        assert result is not None


class TestViewOps:
    async def test_create_view_mock(self, mock_client):
        result = await mock_client.create_view(
            database_id="db-123",
            view_type="board",
        )
        assert result is not None

    async def test_create_linked_view_mock(self, mock_client):
        result = await mock_client.create_linked_view(
            source_database_id="db-123",
            target_page_id="page-456",
        )
        assert result is not None
