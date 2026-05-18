"""Notion Operations 테스트 — block_ops, page_ops, view_ops httpx 호출 경로 검증

실제 API 호출 대신 httpx.AsyncClient를 모킹하여 데이터 변환 로직과 에러 처리 검증.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.notion.client import NotionClient


@pytest.fixture
def real_client():
    """mock_mode=False인 NotionClient (httpx 클라이언트 모킹)"""
    with patch("app.notion.client.settings") as mock_settings:
        mock_settings.notion_api_key = "ntn_test_token_123456"
        mock_settings.notion_parent_page_id = "parent-page-id-123"

        with patch("notion_client.AsyncClient") as mock_notion_sdk:
            mock_notion_sdk.return_value = MagicMock()
            with patch("httpx.AsyncClient"):
                client = NotionClient(token="ntn_test_token_123456", parent_page_id="parent-page-id-123")

    # httpx 클라이언트 모킹
    client._http_client = AsyncMock()
    client._http_client_legacy = AsyncMock()
    client.rate_limiter = AsyncMock()
    client.rate_limiter.acquire = AsyncMock()
    client.rate_limiter.call_with_retry = AsyncMock()
    client.mock_mode = False
    return client


def _mock_response(status_code: int = 200, json_data: dict | None = None, text: str = ""):
    """httpx.Response 모킹 헬퍼"""
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data or {}
    resp.text = text or str(json_data or {})
    return resp


# =========================================================
# BlockOpsMixin Tests
# =========================================================


class TestBlockOpsReal:
    """block_ops.py 실제 API 경로 테스트"""

    async def test_add_blocks_success(self, real_client):
        """블록 추가 성공"""
        blocks = [{"type": "paragraph", "paragraph": {"rich_text": []}}]
        mock_resp = _mock_response(200, {"results": [{"id": "block-1", "type": "paragraph"}]})
        real_client._http_client.patch = AsyncMock(return_value=mock_resp)

        result = await real_client.add_blocks("page-123", blocks)

        assert len(result) == 1
        assert result[0]["id"] == "block-1"
        real_client._http_client.patch.assert_called_once()

    async def test_add_blocks_with_after_block_id(self, real_client):
        """after_block_id 지정 시 position 포함"""
        blocks = [{"type": "heading_1"}]
        mock_resp = _mock_response(200, {"results": [{"id": "block-2"}]})
        real_client._http_client.patch = AsyncMock(return_value=mock_resp)

        await real_client.add_blocks("page-123", blocks, after_block_id="prev-block")

        call_kwargs = real_client._http_client.patch.call_args
        body = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
        assert body["position"]["type"] == "after_block"
        assert body["position"]["after_block"]["id"] == "prev-block"

    async def test_add_blocks_chunking(self, real_client):
        """100개 이상 블록은 청크 분할"""
        blocks = [{"type": "paragraph"} for _ in range(150)]
        mock_resp1 = _mock_response(200, {"results": [{"id": f"b-{i}"} for i in range(100)]})
        mock_resp2 = _mock_response(200, {"results": [{"id": f"b-{i}"} for i in range(100, 150)]})
        real_client._http_client.patch = AsyncMock(side_effect=[mock_resp1, mock_resp2])

        result = await real_client.add_blocks("page-123", blocks)

        assert len(result) == 150
        assert real_client._http_client.patch.call_count == 2

    async def test_add_blocks_api_error_raises(self, real_client):
        """API 에러 시 RuntimeError 발생"""
        blocks = [{"type": "paragraph"}]
        mock_resp = _mock_response(400, text="Bad Request: invalid block type")
        real_client._http_client.patch = AsyncMock(return_value=mock_resp)

        with pytest.raises(RuntimeError, match="블록 추가"):
            await real_client.add_blocks("page-123", blocks)

    async def test_add_blocks_exception_raises(self, real_client):
        """네트워크 에러 시 RuntimeError"""
        blocks = [{"type": "paragraph"}]
        real_client._http_client.patch = AsyncMock(side_effect=ConnectionError("timeout"))

        with pytest.raises(RuntimeError, match="블록 추가 실패"):
            await real_client.add_blocks("page-123", blocks)

    async def test_get_block_success(self, real_client):
        """블록 조회 성공"""
        mock_resp = _mock_response(200, {"id": "block-1", "type": "heading_1", "has_children": False})
        real_client._http_client.get = AsyncMock(return_value=mock_resp)

        result = await real_client.get_block("block-1")

        assert result["id"] == "block-1"
        assert result["type"] == "heading_1"

    async def test_get_block_api_error_returns_fallback(self, real_client):
        """블록 조회 API 에러 시 기본 dict 반환"""
        mock_resp = _mock_response(404, text="Not found")
        real_client._http_client.get = AsyncMock(return_value=mock_resp)

        result = await real_client.get_block("block-404")

        assert result == {"id": "block-404"}

    async def test_get_block_exception_returns_fallback(self, real_client):
        """블록 조회 예외 시 기본 dict 반환"""
        real_client._http_client.get = AsyncMock(side_effect=Exception("network error"))

        result = await real_client.get_block("block-err")

        assert result == {"id": "block-err"}

    async def test_get_block_children_success(self, real_client):
        """하위 블록 목록 조회 성공"""
        mock_resp = _mock_response(
            200,
            {
                "results": [{"id": "child-1"}, {"id": "child-2"}],
                "has_more": False,
            },
        )
        real_client._http_client.get = AsyncMock(return_value=mock_resp)

        result = await real_client.get_block_children("parent-block")

        assert len(result) == 2
        assert result[0]["id"] == "child-1"

    async def test_get_block_children_pagination(self, real_client):
        """페이지네이션 처리"""
        resp1 = _mock_response(
            200,
            {
                "results": [{"id": "child-1"}],
                "has_more": True,
                "next_cursor": "cursor-abc",
            },
        )
        resp2 = _mock_response(
            200,
            {
                "results": [{"id": "child-2"}],
                "has_more": False,
            },
        )
        real_client._http_client.get = AsyncMock(side_effect=[resp1, resp2])

        result = await real_client.get_block_children("parent-block")

        assert len(result) == 2
        assert real_client._http_client.get.call_count == 2

    async def test_get_block_children_api_error_stops(self, real_client):
        """API 에러 시 빈 리스트 반환"""
        mock_resp = _mock_response(500, text="Internal error")
        real_client._http_client.get = AsyncMock(return_value=mock_resp)

        result = await real_client.get_block_children("parent-block")

        assert result == []

    async def test_get_block_children_exception_stops(self, real_client):
        """예외 발생 시 빈 리스트"""
        real_client._http_client.get = AsyncMock(side_effect=Exception("timeout"))

        result = await real_client.get_block_children("parent-block")

        assert result == []

    async def test_update_block_success(self, real_client):
        """블록 업데이트 성공"""
        mock_resp = _mock_response(200, {"id": "block-1", "type": "paragraph", "archived": False})
        real_client._http_client.patch = AsyncMock(return_value=mock_resp)

        result = await real_client.update_block("block-1", {"archived": False})

        assert result["id"] == "block-1"

    async def test_update_block_api_error_returns_fallback(self, real_client):
        """업데이트 API 에러 시 fallback 반환"""
        mock_resp = _mock_response(400, text="Invalid property")
        real_client._http_client.patch = AsyncMock(return_value=mock_resp)

        result = await real_client.update_block("block-1", {"invalid": True})

        assert result["id"] == "block-1"
        assert result["fallback"] is True

    async def test_update_block_exception_returns_fallback(self, real_client):
        """업데이트 예외 시 fallback"""
        real_client._http_client.patch = AsyncMock(side_effect=Exception("conn reset"))

        result = await real_client.update_block("block-1", {})

        assert result["fallback"] is True

    async def test_delete_block_success(self, real_client):
        """블록 삭제 성공"""
        mock_resp = _mock_response(200, {"id": "block-1", "archived": True})
        real_client._http_client.delete = AsyncMock(return_value=mock_resp)

        result = await real_client.delete_block("block-1")

        assert result is True

    async def test_delete_block_api_error(self, real_client):
        """블록 삭제 API 에러"""
        mock_resp = _mock_response(404, text="Not found")
        real_client._http_client.delete = AsyncMock(return_value=mock_resp)

        result = await real_client.delete_block("block-404")

        assert result is False

    async def test_delete_block_exception(self, real_client):
        """블록 삭제 예외"""
        real_client._http_client.delete = AsyncMock(side_effect=Exception("timeout"))

        result = await real_client.delete_block("block-err")

        assert result is False


# =========================================================
# PageOpsMixin Tests
# =========================================================


class TestPageOpsReal:
    """page_ops.py 실제 API 경로 테스트"""

    async def test_create_page_success(self, real_client):
        """페이지 생성 성공"""
        mock_resp = _mock_response(
            200,
            {
                "id": "new-page-id",
                "object": "page",
                "url": "https://notion.so/new-page",
            },
        )
        real_client._http_client_legacy.post = AsyncMock(return_value=mock_resp)

        result = await real_client.create_page(
            parent_id="parent-123",
            title="테스트 페이지",
            icon="📋",
            cover_url="https://images.unsplash.com/cover.jpg",
        )

        assert result["id"] == "new-page-id"
        assert result["object"] == "page"

    async def test_create_page_with_children(self, real_client):
        """children 포함 페이지 생성"""
        mock_resp = _mock_response(200, {"id": "page-with-children"})
        real_client._http_client_legacy.post = AsyncMock(return_value=mock_resp)

        children = [{"type": "paragraph", "paragraph": {"rich_text": []}}]
        result = await real_client.create_page(
            parent_id="parent-123",
            title="자식 포함",
            children=children,
        )

        call_kwargs = real_client._http_client_legacy.post.call_args
        body = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
        assert "children" in body
        assert result["id"] == "page-with-children"

    async def test_create_page_icon_fallback(self, real_client):
        """잘못된 아이콘 시 아이콘 없이 재시도"""
        error_resp = _mock_response(400, text="icon.emoji is not a valid emoji")
        success_resp = _mock_response(200, {"id": "page-no-icon"})
        real_client._http_client_legacy.post = AsyncMock(side_effect=[error_resp, success_resp])

        result = await real_client.create_page(
            parent_id="parent-123",
            title="아이콘 폴백",
            icon="INVALID_EMOJI",
        )

        assert result["id"] == "page-no-icon"
        assert real_client._http_client_legacy.post.call_count == 2

    async def test_create_page_icon_fallback_also_fails(self, real_client):
        """아이콘 폴백도 실패하면 RuntimeError"""
        error_resp1 = _mock_response(400, text="icon.emoji is not valid")
        error_resp2 = _mock_response(400, text="Other error after retry")
        real_client._http_client_legacy.post = AsyncMock(side_effect=[error_resp1, error_resp2])

        with pytest.raises(RuntimeError, match="생성 실패"):
            await real_client.create_page(
                parent_id="parent-123",
                title="실패 페이지",
                icon="BAD",
            )

    async def test_create_page_non_icon_error(self, real_client):
        """아이콘 관련이 아닌 에러는 바로 RuntimeError"""
        error_resp = _mock_response(403, text="Insufficient permissions for parent page")
        real_client._http_client_legacy.post = AsyncMock(return_value=error_resp)

        with pytest.raises(RuntimeError, match="생성 실패"):
            await real_client.create_page(
                parent_id="no-access",
                title="권한 없음",
            )

    async def test_create_page_network_exception(self, real_client):
        """네트워크 예외 시 RuntimeError"""
        real_client._http_client_legacy.post = AsyncMock(side_effect=ConnectionError("DNS resolution failed"))

        with pytest.raises(RuntimeError, match="생성 실패"):
            await real_client.create_page(parent_id="parent-123", title="네트워크 에러")

    async def test_get_page_success(self, real_client):
        """페이지 조회 성공"""
        mock_resp = _mock_response(200, {"id": "page-123", "object": "page", "properties": {}})
        real_client._http_client.get = AsyncMock(return_value=mock_resp)

        result = await real_client.get_page("page-123")

        assert result["id"] == "page-123"
        assert result["object"] == "page"

    async def test_get_page_api_error(self, real_client):
        """페이지 조회 API 에러"""
        mock_resp = _mock_response(404, text="Page not found")
        real_client._http_client.get = AsyncMock(return_value=mock_resp)

        result = await real_client.get_page("page-404")

        assert result == {"id": "page-404"}

    async def test_get_page_exception(self, real_client):
        """페이지 조회 예외"""
        real_client._http_client.get = AsyncMock(side_effect=Exception("timeout"))

        result = await real_client.get_page("page-err")

        assert result == {"id": "page-err"}

    async def test_update_page_success(self, real_client):
        """페이지 업데이트 성공"""
        mock_resp = _mock_response(200, {"id": "page-123", "properties": {"title": "updated"}})
        real_client._http_client.patch = AsyncMock(return_value=mock_resp)

        result = await real_client.update_page("page-123", properties={"title": "updated"})

        assert result["id"] == "page-123"

    async def test_update_page_api_error(self, real_client):
        """페이지 업데이트 API 에러"""
        mock_resp = _mock_response(400, text="Invalid property")
        real_client._http_client.patch = AsyncMock(return_value=mock_resp)

        result = await real_client.update_page("page-123", properties={})

        assert result["fallback"] is True

    async def test_update_page_exception(self, real_client):
        """페이지 업데이트 예외"""
        real_client._http_client.patch = AsyncMock(side_effect=Exception("conn refused"))

        result = await real_client.update_page("page-123", properties={})

        assert result["fallback"] is True

    async def test_delete_page_success(self, real_client):
        """페이지 삭제 성공"""
        mock_resp = _mock_response(200, {})
        real_client._http_client.delete = AsyncMock(return_value=mock_resp)

        result = await real_client.delete_page("page-123")

        assert result is True

    async def test_delete_page_api_error(self, real_client):
        """페이지 삭제 API 에러"""
        mock_resp = _mock_response(404, text="Not found")
        real_client._http_client.delete = AsyncMock(return_value=mock_resp)

        result = await real_client.delete_page("page-404")

        assert result is False

    async def test_delete_page_exception(self, real_client):
        """페이지 삭제 예외"""
        real_client._http_client.delete = AsyncMock(side_effect=Exception("timeout"))

        result = await real_client.delete_page("page-err")

        assert result is False

    async def test_move_page_success(self, real_client):
        """페이지 이동 성공 (POST /pages/:id/move)"""
        mock_resp = _mock_response(200, {"id": "page-123", "parent": {"page_id": "new-parent"}})
        real_client._http_client.post = AsyncMock(return_value=mock_resp)

        result = await real_client.move_page("page-123", "new-parent")

        assert result["parent"]["page_id"] == "new-parent"

    async def test_move_page_api_error(self, real_client):
        """페이지 이동 API 에러"""
        mock_resp = _mock_response(400, text="Cannot move page")
        real_client._http_client.post = AsyncMock(return_value=mock_resp)

        result = await real_client.move_page("page-123", "invalid-parent")

        assert result == {"id": "page-123"}

    async def test_archive_page_success(self, real_client):
        """페이지 아카이브 성공"""
        real_client.rate_limiter.call_with_retry = AsyncMock(return_value={"id": "page-123", "in_trash": True})

        result = await real_client.archive_page("page-123")

        assert result["in_trash"] is True

    async def test_restore_page_success(self, real_client):
        """페이지 복원 성공"""
        real_client.rate_limiter.call_with_retry = AsyncMock(return_value={"id": "page-123", "in_trash": False})

        result = await real_client.restore_page("page-123")

        assert result["in_trash"] is False

    async def test_lock_page_success(self, real_client):
        """페이지 잠금 성공"""
        mock_resp = _mock_response(200, {"id": "page-123", "is_locked": True})
        real_client._http_client.patch = AsyncMock(return_value=mock_resp)

        result = await real_client.lock_page("page-123", locked=True)

        assert result["is_locked"] is True

    async def test_lock_page_unlock(self, real_client):
        """페이지 잠금 해제"""
        mock_resp = _mock_response(200, {"id": "page-123", "is_locked": False})
        real_client._http_client.patch = AsyncMock(return_value=mock_resp)

        result = await real_client.lock_page("page-123", locked=False)

        assert result["is_locked"] is False

    async def test_create_page_markdown_success(self, real_client):
        """마크다운 페이지 생성 성공"""
        mock_resp = _mock_response(200, {"id": "md-page", "object": "page"})
        real_client._http_client.post = AsyncMock(return_value=mock_resp)

        result = await real_client.create_page_markdown("parent-1", "MD 페이지", "# Hello\n\nWorld")

        assert result["id"] == "md-page"

    async def test_create_page_markdown_api_error_returns_mock(self, real_client):
        """마크다운 페이지 API 에러 시 mock 반환"""
        mock_resp = _mock_response(400, text="Markdown API not supported")
        real_client._http_client.post = AsyncMock(return_value=mock_resp)

        result = await real_client.create_page_markdown("parent-1", "MD 실패", "# Fail")

        # mock_page 형태로 반환됨
        assert "id" in result
        assert result["object"] == "page"

    async def test_get_page_markdown_success(self, real_client):
        """마크다운 조회 성공"""
        mock_resp = _mock_response(200, {"markdown": "# Title\n\nContent"})
        real_client._http_client.get = AsyncMock(return_value=mock_resp)

        result = await real_client.get_page_markdown("page-123")

        assert result == "# Title\n\nContent"

    async def test_get_page_markdown_api_error(self, real_client):
        """마크다운 조회 API 에러 시 빈 문자열"""
        mock_resp = _mock_response(404, text="Not found")
        real_client._http_client.get = AsyncMock(return_value=mock_resp)

        result = await real_client.get_page_markdown("page-404")

        assert result == ""

    async def test_update_page_content_markdown_success(self, real_client):
        """마크다운 콘텐츠 교체 성공"""
        mock_resp = _mock_response(200, {"id": "page-123", "object": "page"})
        real_client._http_client.patch = AsyncMock(return_value=mock_resp)

        result = await real_client.update_page_content_markdown("page-123", "# New Content")

        assert result["id"] == "page-123"

    async def test_update_page_content_markdown_error(self, real_client):
        """마크다운 콘텐츠 교체 API 에러"""
        mock_resp = _mock_response(400, text="Replace content not supported")
        real_client._http_client.patch = AsyncMock(return_value=mock_resp)

        result = await real_client.update_page_content_markdown("page-123", "# Fail")

        assert result == {"id": "page-123"}


# =========================================================
# ViewOpsMixin Tests
# =========================================================


class TestViewOpsReal:
    """view_ops.py 실제 API 경로 테스트"""

    @pytest.fixture(autouse=True)
    def setup_get_data_source(self, real_client):
        """get_data_source_id를 모킹"""
        real_client.get_data_source_id = AsyncMock(return_value="data-source-123")

    async def test_create_view_success(self, real_client):
        """뷰 생성 성공"""
        mock_resp = _mock_response(200, {"id": "view-1", "type": "board", "name": "칸반 보드"})
        real_client._http_client.post = AsyncMock(return_value=mock_resp)

        result = await real_client.create_view(
            database_id="db-123",
            view_type="board",
            title="칸반 보드",
        )

        assert result["id"] == "view-1"
        assert result["type"] == "board"

    async def test_create_view_with_all_options(self, real_client):
        """모든 옵션 포함 뷰 생성"""
        mock_resp = _mock_response(200, {"id": "view-full", "type": "gallery"})
        real_client._http_client.post = AsyncMock(return_value=mock_resp)

        result = await real_client.create_view(
            database_id="db-123",
            view_type="gallery",
            title="갤러리 뷰",
            filters={"property": "상태", "status": {"equals": "완료"}},
            sorts=[{"property": "생성일", "direction": "descending"}],
            group_by={"property": "카테고리"},
            sub_group_by={"property": "우선순위"},
            quick_filters={"enabled": True},
            properties={"이름": {"visible": True}},
            position="first",
            configuration={"gallery_cover": "page_cover"},
        )

        assert result["id"] == "view-full"
        call_kwargs = real_client._http_client.post.call_args
        body = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
        assert body["type"] == "gallery"
        assert body["filter"] == {"property": "상태", "status": {"equals": "완료"}}
        assert body["sort"] == [{"property": "생성일", "direction": "descending"}]
        assert body["group_by"] == {"property": "카테고리"}

    async def test_create_view_api_error_with_configuration_fallback(self, real_client):
        """configuration 포함 시 에러 발생하면 configuration 제거 후 재시도"""
        error_resp = _mock_response(400, text="Invalid configuration")
        success_resp = _mock_response(200, {"id": "view-retry", "type": "board"})
        real_client._http_client.post = AsyncMock(side_effect=[error_resp, success_resp])

        result = await real_client.create_view(
            database_id="db-123",
            view_type="board",
            title="보드",
            configuration={"board_cover": "page_cover"},
        )

        assert result["id"] == "view-retry"
        assert real_client._http_client.post.call_count == 2

    async def test_create_view_api_error_fallback_also_fails(self, real_client):
        """재시도도 실패하면 fallback dict 반환"""
        error_resp = _mock_response(400, text="Error")
        real_client._http_client.post = AsyncMock(side_effect=[error_resp, error_resp])

        result = await real_client.create_view(
            database_id="db-123",
            view_type="calendar",
            title="캘린더",
            configuration={"calendar_by": "date"},
        )

        assert result["fallback"] is True
        assert result["type"] == "calendar"

    async def test_create_view_api_error_no_configuration(self, real_client):
        """configuration 없이 에러면 바로 fallback"""
        error_resp = _mock_response(500, text="Internal error")
        real_client._http_client.post = AsyncMock(return_value=error_resp)

        result = await real_client.create_view(
            database_id="db-123",
            view_type="list",
            title="리스트",
        )

        assert result["fallback"] is True
        assert real_client._http_client.post.call_count == 1

    async def test_create_view_exception(self, real_client):
        """뷰 생성 예외"""
        real_client._http_client.post = AsyncMock(side_effect=Exception("network error"))

        result = await real_client.create_view(
            database_id="db-123",
            view_type="table",
            title="테이블",
        )

        assert result["fallback"] is True

    async def test_update_view_success(self, real_client):
        """뷰 업데이트 성공"""
        mock_resp = _mock_response(200, {"id": "view-1", "name": "수정된 뷰"})
        real_client._http_client.patch = AsyncMock(return_value=mock_resp)

        result = await real_client.update_view("view-1", name="수정된 뷰")

        assert result["name"] == "수정된 뷰"

    async def test_update_view_filters_none_values(self, real_client):
        """None 값은 body에서 제외"""
        mock_resp = _mock_response(200, {"id": "view-1"})
        real_client._http_client.patch = AsyncMock(return_value=mock_resp)

        await real_client.update_view("view-1", name="test", filter=None, sort=None)

        call_kwargs = real_client._http_client.patch.call_args
        body = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
        assert "filter" not in body
        assert "sort" not in body
        assert body["name"] == "test"

    async def test_update_view_api_error(self, real_client):
        """뷰 업데이트 API 에러"""
        mock_resp = _mock_response(400, text="Invalid view")
        real_client._http_client.patch = AsyncMock(return_value=mock_resp)

        result = await real_client.update_view("view-1", name="fail")

        assert result["fallback"] is True

    async def test_update_view_exception(self, real_client):
        """뷰 업데이트 예외"""
        real_client._http_client.patch = AsyncMock(side_effect=Exception("timeout"))

        result = await real_client.update_view("view-1", name="err")

        assert result["fallback"] is True

    async def test_delete_view_success(self, real_client):
        """뷰 삭제 성공"""
        mock_resp = _mock_response(200, {})
        real_client._http_client.delete = AsyncMock(return_value=mock_resp)

        result = await real_client.delete_view("view-1")

        assert result is True

    async def test_delete_view_api_error(self, real_client):
        """뷰 삭제 API 에러"""
        mock_resp = _mock_response(404, text="View not found")
        real_client._http_client.delete = AsyncMock(return_value=mock_resp)

        result = await real_client.delete_view("view-404")

        assert result is False

    async def test_delete_view_exception(self, real_client):
        """뷰 삭제 예외"""
        real_client._http_client.delete = AsyncMock(side_effect=Exception("err"))

        result = await real_client.delete_view("view-err")

        assert result is False

    async def test_list_views_success(self, real_client):
        """뷰 목록 조회 성공"""
        mock_resp = _mock_response(
            200,
            {
                "results": [
                    {"id": "view-1", "type": "table"},
                    {"id": "view-2", "type": "board"},
                ]
            },
        )
        real_client._http_client.get = AsyncMock(return_value=mock_resp)

        result = await real_client.list_views("db-123")

        assert len(result) == 2
        assert result[0]["type"] == "table"

    async def test_list_views_api_error(self, real_client):
        """뷰 목록 조회 API 에러"""
        mock_resp = _mock_response(500, text="Internal error")
        real_client._http_client.get = AsyncMock(return_value=mock_resp)

        result = await real_client.list_views("db-123")

        assert result == []

    async def test_list_views_exception(self, real_client):
        """뷰 목록 조회 예외"""
        real_client._http_client.get = AsyncMock(side_effect=Exception("timeout"))

        result = await real_client.list_views("db-123")

        assert result == []

    async def test_get_view_success(self, real_client):
        """뷰 조회 성공"""
        mock_resp = _mock_response(200, {"id": "view-1", "type": "gallery", "name": "My Gallery"})
        real_client._http_client.get = AsyncMock(return_value=mock_resp)

        result = await real_client.get_view("view-1")

        assert result["type"] == "gallery"

    async def test_get_view_api_error(self, real_client):
        """뷰 조회 API 에러"""
        mock_resp = _mock_response(404, text="Not found")
        real_client._http_client.get = AsyncMock(return_value=mock_resp)

        result = await real_client.get_view("view-404")

        assert result == {"id": "view-404"}

    async def test_get_view_exception(self, real_client):
        """뷰 조회 예외"""
        real_client._http_client.get = AsyncMock(side_effect=Exception("err"))

        result = await real_client.get_view("view-err")

        assert result == {"id": "view-err"}

    async def test_create_linked_view_success(self, real_client):
        """링크드 뷰 생성 성공"""
        mock_resp = _mock_response(200, {"id": "linked-view-1", "type": "table"})
        real_client._http_client.post = AsyncMock(return_value=mock_resp)

        result = await real_client.create_linked_view(
            source_database_id="db-source",
            target_page_id="page-target",
            view_type="table",
            title="링크드 테이블",
        )

        assert result["id"] == "linked-view-1"

    async def test_create_linked_view_with_options(self, real_client):
        """링크드 뷰 옵션 포함 생성"""
        mock_resp = _mock_response(200, {"id": "linked-view-2", "type": "board"})
        real_client._http_client.post = AsyncMock(return_value=mock_resp)

        result = await real_client.create_linked_view(
            source_database_id="db-source",
            target_page_id="page-target",
            view_type="board",
            title="링크드 보드",
            filters={"property": "status"},
            sorts=[{"property": "date"}],
            group_by={"property": "status"},
            configuration={"board_cover": "page_cover"},
        )

        assert result["id"] == "linked-view-2"
        call_kwargs = real_client._http_client.post.call_args
        body = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
        assert body["create_database"]["parent"]["type"] == "page_id"
        assert body["filter"] == {"property": "status"}

    async def test_create_linked_view_api_error(self, real_client):
        """링크드 뷰 생성 API 에러"""
        mock_resp = _mock_response(400, text="Invalid linked view")
        real_client._http_client.post = AsyncMock(return_value=mock_resp)

        result = await real_client.create_linked_view(
            source_database_id="db-source",
            target_page_id="page-target",
        )

        assert result["fallback"] is True

    async def test_create_linked_view_exception(self, real_client):
        """링크드 뷰 생성 예외"""
        real_client._http_client.post = AsyncMock(side_effect=Exception("network err"))

        result = await real_client.create_linked_view(
            source_database_id="db-source",
            target_page_id="page-target",
        )

        assert result["fallback"] is True
