"""DatabaseOpsMixin 실제 API 경로 테스트 (non-mock paths)"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.notion.client import NotionClient


@pytest.fixture
def real_client():
    """mock_mode=False인 NotionClient"""
    with patch("app.notion.client.settings") as mock_settings:
        mock_settings.notion_api_key = "ntn_real_token"
        mock_settings.notion_parent_page_id = "parent-page-id"
        with patch("notion_client.AsyncClient"):
            with patch("httpx.AsyncClient"):
                client = NotionClient(token="ntn_real_token", parent_page_id="parent-page-id")

    client._http_client = AsyncMock()
    client._http_client_legacy = AsyncMock()
    client.rate_limiter = AsyncMock()
    client.rate_limiter.acquire = AsyncMock()
    client.rate_limiter.call_with_retry = AsyncMock()
    client._real_client = MagicMock()
    client.mock_mode = False
    return client


class TestCreateDatabaseReal:
    async def test_create_success(self, real_client):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "db-new", "object": "database"}
        real_client._http_client_legacy.post = AsyncMock(return_value=mock_resp)

        result = await real_client.create_database(
            parent_id="parent-1",
            title="테스트 DB",
            properties={"이름": {"title": {}}},
        )

        assert result["id"] == "db-new"

    async def test_create_with_optional_fields(self, real_client):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "db-full"}
        real_client._http_client_legacy.post = AsyncMock(return_value=mock_resp)

        result = await real_client.create_database(
            parent_id="parent-1",
            title="풀 옵션 DB",
            properties={"이름": {"title": {}}},
            description="설명 텍스트",
            icon="📊",
            cover_url="https://img.com/cover.jpg",
        )

        assert result["id"] == "db-full"
        call_args = real_client._http_client_legacy.post.call_args
        json_data = call_args.kwargs["json"]
        assert json_data["icon"]["emoji"] == "📊"
        assert json_data["cover"]["external"]["url"] == "https://img.com/cover.jpg"
        assert json_data["description"][0]["text"]["content"] == "설명 텍스트"

    async def test_create_validation_error_fallback(self, real_client):
        error_resp = MagicMock()
        error_resp.status_code = 400
        error_resp.text = "validation_error: property format invalid"

        retry_resp = MagicMock()
        retry_resp.status_code = 200
        retry_resp.json.return_value = {"id": "db-fallback"}

        real_client._http_client_legacy.post = AsyncMock(side_effect=[error_resp, retry_resp])

        result = await real_client.create_database(
            parent_id="parent-1",
            title="폴백 DB",
            properties={"상태": {"select": {"options": []}}},
        )

        assert result["id"] == "db-fallback"

    async def test_create_non_validation_error_raises(self, real_client):
        error_resp = MagicMock()
        error_resp.status_code = 500
        error_resp.text = "internal server error"
        real_client._http_client_legacy.post = AsyncMock(return_value=error_resp)

        with pytest.raises(RuntimeError, match="DB 생성 API 에러"):
            await real_client.create_database(
                parent_id="parent-1",
                title="에러 DB",
                properties={"이름": {"title": {}}},
            )

    async def test_create_network_exception(self, real_client):
        real_client._http_client_legacy.post = AsyncMock(side_effect=Exception("connection timeout"))

        with pytest.raises(RuntimeError, match="생성 실패"):
            await real_client.create_database(
                parent_id="parent-1",
                title="타임아웃 DB",
                properties={"이름": {"title": {}}},
            )


class TestGetDatabaseReal:
    async def test_get_success(self, real_client):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "id": "db-1",
            "properties": {"이름": {"title": {}}},
            "data_sources": [{"id": "ds-1"}],
        }
        real_client._http_client.get = AsyncMock(return_value=mock_resp)

        result = await real_client.get_database("db-1")

        assert result["id"] == "db-1"
        assert result["data_sources"] == [{"id": "ds-1"}]

    async def test_get_error_returns_minimal(self, real_client):
        error_resp = MagicMock()
        error_resp.status_code = 404
        real_client._http_client.get = AsyncMock(return_value=error_resp)

        result = await real_client.get_database("db-missing")

        assert result == {"id": "db-missing", "properties": {}}

    async def test_get_exception_returns_minimal(self, real_client):
        real_client._http_client.get = AsyncMock(side_effect=Exception("timeout"))

        result = await real_client.get_database("db-1")

        assert result["id"] == "db-1"


class TestGetDataSourceId:
    async def test_with_data_sources(self, real_client):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "db-1", "data_sources": [{"id": "ds-custom"}]}
        real_client._http_client.get = AsyncMock(return_value=mock_resp)

        result = await real_client.get_data_source_id("db-1")

        assert result == "ds-custom"

    async def test_without_data_sources_fallback(self, real_client):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "db-1", "data_sources": []}
        real_client._http_client.get = AsyncMock(return_value=mock_resp)

        result = await real_client.get_data_source_id("db-1")

        assert result == "db-1"


class TestUpdateDatabaseReal:
    async def test_update(self, real_client):
        real_client.rate_limiter.call_with_retry = AsyncMock(
            return_value={"id": "db-1", "title": [{"text": {"content": "Updated"}}]}
        )

        result = await real_client.update_database("db-1", {"title": [{"text": {"content": "Updated"}}]})

        assert result["id"] == "db-1"


class TestLockDatabaseReal:
    async def test_lock(self, real_client):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"id": "db-1", "is_locked": True}
        real_client._http_client_legacy.patch = AsyncMock(return_value=mock_resp)

        result = await real_client.lock_database("db-1", locked=True)

        assert result["is_locked"] is True

    async def test_unlock(self, real_client):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"id": "db-1", "is_locked": False}
        real_client._http_client_legacy.patch = AsyncMock(return_value=mock_resp)

        result = await real_client.lock_database("db-1", locked=False)

        assert result["is_locked"] is False


class TestAddDatabaseItemReal:
    async def test_add_item_success(self, real_client):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "item-1", "object": "page"}
        real_client._http_client_legacy.post = AsyncMock(return_value=mock_resp)

        result = await real_client.add_database_item(
            database_id="db-1",
            properties={"이름": {"title": [{"text": {"content": "항목"}}]}},
            icon="📌",
        )

        assert result["id"] == "item-1"

    async def test_add_item_icon_fallback(self, real_client):
        error_resp = MagicMock()
        error_resp.status_code = 400
        error_resp.text = "icon.emoji is not a valid emoji"

        retry_resp = MagicMock()
        retry_resp.status_code = 200
        retry_resp.json.return_value = {"id": "item-noicon"}

        real_client._http_client_legacy.post = AsyncMock(side_effect=[error_resp, retry_resp])

        result = await real_client.add_database_item(
            database_id="db-1",
            properties={"이름": {"title": []}},
            icon="🫠",
        )

        assert result["id"] == "item-noicon"

    async def test_add_item_validation_status_fallback(self, real_client):
        error_resp = MagicMock()
        error_resp.status_code = 400
        error_resp.text = "validation_error: status property is not valid"

        retry_resp = MagicMock()
        retry_resp.status_code = 200
        retry_resp.json.return_value = {"id": "item-nostatus"}

        real_client._http_client_legacy.post = AsyncMock(side_effect=[error_resp, retry_resp])

        result = await real_client.add_database_item(
            database_id="db-1",
            properties={
                "이름": {"title": [{"text": {"content": "항목"}}]},
                "상태": {"status": {"name": "진행중"}},
            },
        )

        assert result["id"] == "item-nostatus"

    async def test_add_item_validation_select_fallback(self, real_client):
        error_resp = MagicMock()
        error_resp.status_code = 400
        error_resp.text = "validation_error: select option not found"

        retry_resp = MagicMock()
        retry_resp.status_code = 200
        retry_resp.json.return_value = {"id": "item-noselect"}

        real_client._http_client_legacy.post = AsyncMock(side_effect=[error_resp, retry_resp])

        result = await real_client.add_database_item(
            database_id="db-1",
            properties={
                "이름": {"title": [{"text": {"content": "항목"}}]},
                "분류": {"select": {"name": "옵션1"}},
            },
        )

        assert result["id"] == "item-noselect"

    async def test_add_item_validation_generic_fallback(self, real_client):
        error_resp = MagicMock()
        error_resp.status_code = 400
        error_resp.text = "validation_error: property format error"

        retry_resp = MagicMock()
        retry_resp.status_code = 200
        retry_resp.json.return_value = {"id": "item-titleonly"}

        real_client._http_client_legacy.post = AsyncMock(side_effect=[error_resp, retry_resp])

        result = await real_client.add_database_item(
            database_id="db-1",
            properties={
                "이름": {"title": [{"text": {"content": "항목"}}]},
                "숫자": {"number": 42},
            },
        )

        assert result["id"] == "item-titleonly"

    async def test_add_item_unknown_error_raises(self, real_client):
        error_resp = MagicMock()
        error_resp.status_code = 500
        error_resp.text = "internal server error"
        real_client._http_client_legacy.post = AsyncMock(return_value=error_resp)

        with pytest.raises(RuntimeError, match="DB 항목 추가 API 에러"):
            await real_client.add_database_item(
                database_id="db-1",
                properties={"이름": {"title": []}},
            )

    async def test_add_item_network_exception(self, real_client):
        real_client._http_client_legacy.post = AsyncMock(side_effect=Exception("timeout"))

        with pytest.raises(RuntimeError, match="DB 아이템 추가 실패"):
            await real_client.add_database_item(
                database_id="db-1",
                properties={"이름": {"title": []}},
            )


class TestQueryDatabaseReal:
    async def test_query_success(self, real_client):
        get_resp = MagicMock()
        get_resp.status_code = 200
        get_resp.json.return_value = {"id": "db-1", "data_sources": [{"id": "ds-1"}]}

        query_resp = MagicMock()
        query_resp.status_code = 200
        query_resp.json.return_value = {"results": [{"id": "p1"}, {"id": "p2"}]}

        real_client._http_client.get = AsyncMock(return_value=get_resp)
        real_client._http_client.post = AsyncMock(return_value=query_resp)

        result = await real_client.query_database("db-1")

        assert len(result) == 2

    async def test_query_with_filters_and_sorts(self, real_client):
        get_resp = MagicMock()
        get_resp.status_code = 200
        get_resp.json.return_value = {"id": "db-1", "data_sources": [{"id": "ds-1"}]}

        query_resp = MagicMock()
        query_resp.status_code = 200
        query_resp.json.return_value = {"results": [{"id": "p1"}]}

        real_client._http_client.get = AsyncMock(return_value=get_resp)
        real_client._http_client.post = AsyncMock(return_value=query_resp)

        result = await real_client.query_database(
            "db-1",
            filters={"property": "상태", "status": {"equals": "완료"}},
            sorts=[{"property": "날짜", "direction": "descending"}],
            page_size=50,
        )

        assert len(result) == 1
        call_args = real_client._http_client.post.call_args
        json_data = call_args.kwargs["json"]
        assert json_data["filter"]["property"] == "상태"
        assert json_data["sorts"][0]["direction"] == "descending"
        assert json_data["page_size"] == 50

    async def test_query_api_error_returns_empty(self, real_client):
        get_resp = MagicMock()
        get_resp.status_code = 200
        get_resp.json.return_value = {"id": "db-1", "data_sources": [{"id": "ds-1"}]}

        error_resp = MagicMock()
        error_resp.status_code = 400
        error_resp.text = "bad request"

        real_client._http_client.get = AsyncMock(return_value=get_resp)
        real_client._http_client.post = AsyncMock(return_value=error_resp)

        result = await real_client.query_database("db-1")

        assert result == []

    async def test_query_exception_returns_empty(self, real_client):
        get_resp = MagicMock()
        get_resp.status_code = 200
        get_resp.json.return_value = {"id": "db-1", "data_sources": [{"id": "ds-1"}]}

        real_client._http_client.get = AsyncMock(return_value=get_resp)
        real_client._http_client.post = AsyncMock(side_effect=Exception("network error"))

        result = await real_client.query_database("db-1")

        assert result == []

    async def test_query_page_size_capped_at_100(self, real_client):
        get_resp = MagicMock()
        get_resp.status_code = 200
        get_resp.json.return_value = {"id": "db-1", "data_sources": [{"id": "ds-1"}]}

        query_resp = MagicMock()
        query_resp.status_code = 200
        query_resp.json.return_value = {"results": []}

        real_client._http_client.get = AsyncMock(return_value=get_resp)
        real_client._http_client.post = AsyncMock(return_value=query_resp)

        await real_client.query_database("db-1", page_size=500)

        call_args = real_client._http_client.post.call_args
        json_data = call_args.kwargs["json"]
        assert json_data["page_size"] == 100
