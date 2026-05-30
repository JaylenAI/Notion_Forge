"""Notion Client 테스트: Mock 모드 + 실제 API 경로 (search, comments, emojis, init)"""

from unittest.mock import AsyncMock, MagicMock, patch

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


@pytest.fixture
def real_client():
    """mock_mode=False인 NotionClient (real API 경로 테스트용)"""
    with patch("app.notion.client.settings") as mock_settings:
        mock_settings.notion_api_key = "ntn_real_token_abc"
        mock_settings.notion_parent_page_id = "parent-id-real"
        with patch("notion_client.AsyncClient") as mock_sdk:
            mock_sdk.return_value = MagicMock()
            with patch("httpx.AsyncClient"):
                client = NotionClient(token="ntn_real_token_abc", parent_page_id="parent-id-real")

    client._http_client = AsyncMock()
    client._http_client_legacy = AsyncMock()
    client.rate_limiter = AsyncMock()
    client.rate_limiter.acquire = AsyncMock()
    client.rate_limiter.call_with_retry = AsyncMock()
    client._real_client = MagicMock()
    client.mock_mode = False
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

    async def test_list_views_mock(self, mock_client):
        result = await mock_client.list_views("db-123")
        assert result == []

    async def test_get_view_mock(self, mock_client):
        result = await mock_client.get_view("view-123")
        assert result["id"] == "view-123"

    async def test_delete_view_mock(self, mock_client):
        result = await mock_client.delete_view("view-123")
        assert result is True

    async def test_update_view_mock(self, mock_client):
        result = await mock_client.update_view("view-123", name="Updated")
        assert result["id"] == "view-123"


# =========================================================
# Real Mode Tests (non-mock paths)
# =========================================================


class TestInitBehavior:
    """NotionClient 초기화 동작 검증"""

    def test_mock_mode_when_no_token(self):
        """토큰 없으면 mock_mode=True"""
        with patch("app.notion.client.settings") as mock_settings:
            mock_settings.notion_api_key = ""
            mock_settings.notion_parent_page_id = ""
            client = NotionClient(token="", parent_page_id="")
        assert client.mock_mode is True

    def test_mock_mode_when_no_parent_page_id(self):
        """parent_page_id 없으면 mock_mode=True"""
        with patch("app.notion.client.settings") as mock_settings:
            mock_settings.notion_api_key = "ntn_token"
            mock_settings.notion_parent_page_id = ""
            client = NotionClient(token="ntn_token", parent_page_id="")
        assert client.mock_mode is True

    def test_real_mode_when_both_provided(self):
        """토큰과 parent_page_id 모두 있으면 mock_mode=False"""
        with patch("app.notion.client.settings") as mock_settings:
            mock_settings.notion_api_key = "ntn_real_token"
            mock_settings.notion_parent_page_id = "page-id-real"
            with patch("notion_client.AsyncClient"):
                with patch("httpx.AsyncClient"):
                    client = NotionClient(token="ntn_real_token", parent_page_id="page-id-real")
        assert client.mock_mode is False
        assert client._http_client is not None

    def test_settings_fallback(self):
        """인자 미제공 시 settings에서 가져옴"""
        with patch("app.notion.client.settings") as mock_settings:
            mock_settings.notion_api_key = "settings_token"
            mock_settings.notion_parent_page_id = "settings_page"
            with patch("notion_client.AsyncClient"):
                with patch("httpx.AsyncClient"):
                    client = NotionClient()
        assert client.token == "settings_token"
        assert client.parent_page_id == "settings_page"


class TestSearchRealMode:
    """search() 실제 API 경로 테스트"""

    async def test_search_with_query(self, real_client):
        """쿼리 포함 검색"""
        real_client.rate_limiter.call_with_retry = AsyncMock(
            return_value={"results": [{"id": "page-1", "object": "page"}]}
        )

        result = await real_client.search(query="프로젝트")

        assert result["results"][0]["id"] == "page-1"

    async def test_search_with_filter_type(self, real_client):
        """필터 타입 포함 검색"""
        real_client.rate_limiter.call_with_retry = AsyncMock(
            return_value={"results": [{"id": "db-1", "object": "database"}]}
        )

        result = await real_client.search(query="DB", filter_type="database")

        assert result["results"][0]["object"] == "database"

    async def test_search_empty_query(self, real_client):
        """빈 쿼리 검색"""
        real_client.rate_limiter.call_with_retry = AsyncMock(return_value={"results": []})

        result = await real_client.search()

        assert result == {"results": []}


class TestCommentsRealMode:
    """Comments API 실제 경로 테스트 (httpx 기반)"""

    async def test_add_comment_with_page_id(self, real_client):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "comment-1", "parent": {"page_id": "page-123"}}
        real_client._http_client.post = AsyncMock(return_value=mock_resp)

        with patch("app.notion.block_builder.rich_text", return_value=[{"text": {"content": "댓글"}}]):
            result = await real_client.add_comment(text="댓글 내용", page_id="page-123")

        assert result["id"] == "comment-1"

    async def test_add_comment_with_markdown(self, real_client):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "comment-md"}
        real_client._http_client.post = AsyncMock(return_value=mock_resp)

        result = await real_client.add_comment(markdown="**볼드** 댓글", page_id="page-123")

        assert result["id"] == "comment-md"
        call_args = real_client._http_client.post.call_args
        assert call_args.kwargs["json"]["markdown"] == "**볼드** 댓글"

    async def test_add_comment_with_block_id(self, real_client):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "comment-2"}
        real_client._http_client.post = AsyncMock(return_value=mock_resp)

        with patch("app.notion.block_builder.rich_text", return_value=[{"text": {"content": "블록 댓글"}}]):
            result = await real_client.add_comment(text="블록 댓글", block_id="block-123")

        assert result["id"] == "comment-2"

    async def test_add_comment_with_discussion_id(self, real_client):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "comment-3"}
        real_client._http_client.post = AsyncMock(return_value=mock_resp)

        with patch("app.notion.block_builder.rich_text", return_value=[{"text": {"content": "스레드"}}]):
            result = await real_client.add_comment(text="스레드 댓글", discussion_id="disc-123")

        assert result["id"] == "comment-3"

    async def test_update_comment(self, real_client):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "comment-1"}
        real_client._http_client.patch = AsyncMock(return_value=mock_resp)

        result = await real_client.update_comment("comment-1", markdown="수정된 내용")

        assert result["id"] == "comment-1"

    async def test_delete_comment(self, real_client):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        real_client._http_client.delete = AsyncMock(return_value=mock_resp)

        result = await real_client.delete_comment("comment-1")

        assert result is True

    async def test_get_comments(self, real_client):
        real_client.rate_limiter.call_with_retry = AsyncMock(return_value={"results": [{"id": "c1"}, {"id": "c2"}]})

        result = await real_client.get_comments("block-123")

        assert len(result) == 2


class TestCustomEmojisRealMode:
    """Custom Emoji API 실제 경로 테스트"""

    async def test_list_custom_emojis_success(self, real_client):
        """커스텀 이모지 목록 조회 성공"""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"results": [{"id": "emoji-1", "name": "fire"}]}
        real_client._http_client.get = AsyncMock(return_value=mock_resp)

        result = await real_client.list_custom_emojis()

        assert len(result) == 1
        assert result[0]["name"] == "fire"

    async def test_list_custom_emojis_api_error(self, real_client):
        """API 에러 시 빈 리스트"""
        mock_resp = MagicMock()
        mock_resp.status_code = 403
        real_client._http_client.get = AsyncMock(return_value=mock_resp)

        result = await real_client.list_custom_emojis()

        assert result == []

    async def test_list_custom_emojis_exception(self, real_client):
        """예외 시 빈 리스트"""
        real_client._http_client.get = AsyncMock(side_effect=Exception("network err"))

        result = await real_client.list_custom_emojis()

        assert result == []


class TestUsersRealMode:
    """Users API 실제 경로 테스트"""

    async def test_list_users_success(self, real_client):
        """사용자 목록 조회"""
        real_client.rate_limiter.call_with_retry = AsyncMock(
            return_value={"results": [{"id": "user-1", "name": "Test User"}]}
        )

        result = await real_client.list_users()

        assert len(result) == 1
        assert result[0]["id"] == "user-1"

    async def test_get_user_success(self, real_client):
        """사용자 조회"""
        real_client.rate_limiter.call_with_retry = AsyncMock(
            return_value={"id": "user-1", "name": "Test User", "type": "person"}
        )

        result = await real_client.get_user("user-1")

        assert result["type"] == "person"


class TestClientClose:
    """클라이언트 종료 테스트"""

    async def test_close_with_http_clients(self, real_client):
        """http 클라이언트 정리"""
        real_client._http_client = AsyncMock()
        real_client._http_client.aclose = AsyncMock()
        real_client._http_client_legacy = AsyncMock()
        real_client._http_client_legacy.aclose = AsyncMock()

        await real_client.close()

        real_client._http_client.aclose.assert_called_once()
        real_client._http_client_legacy.aclose.assert_called_once()

    async def test_close_without_http_client(self, mock_client):
        """mock_mode에서는 http_client가 없어도 안전하게 종료"""
        mock_client._http_client = None

        await mock_client.close()


class TestQueryPagination:
    async def test_query_database_paginates(self, real_client):
        from unittest.mock import AsyncMock, MagicMock

        client = real_client
        get_resp = MagicMock()
        get_resp.status_code = 200
        get_resp.json = MagicMock(return_value={"data_sources": [{"id": "ds1"}]})
        client._http_client.get = AsyncMock(return_value=get_resp)

        page1 = MagicMock()
        page1.status_code = 200
        page1.json = MagicMock(return_value={"results": [{"id": "1"}, {"id": "2"}], "has_more": True, "next_cursor": "c1"})
        page2 = MagicMock()
        page2.status_code = 200
        page2.json = MagicMock(return_value={"results": [{"id": "3"}], "has_more": False})
        client._http_client.post = AsyncMock(side_effect=[page1, page2])
        client.rate_limiter.acquire = AsyncMock()

        rows = await client.query_database("db1")
        assert [r["id"] for r in rows] == ["1", "2", "3"]
        assert client._http_client.post.call_count == 2

    async def test_query_database_single_page(self, real_client):
        from unittest.mock import AsyncMock, MagicMock

        client = real_client
        get_resp = MagicMock()
        get_resp.status_code = 200
        get_resp.json = MagicMock(return_value={"data_sources": [{"id": "ds1"}]})
        client._http_client.get = AsyncMock(return_value=get_resp)
        page = MagicMock()
        page.status_code = 200
        page.json = MagicMock(return_value={"results": [{"id": "1"}], "has_more": False})
        client._http_client.post = AsyncMock(return_value=page)
        client.rate_limiter.acquire = AsyncMock()

        rows = await client.query_database("db1")
        assert len(rows) == 1
        assert client._http_client.post.call_count == 1
