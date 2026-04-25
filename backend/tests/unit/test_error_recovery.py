"""에러 복구 + 부분 결과 테스트: Notion API 재시도, 부분 결과 요약, 롤백 검증"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.agent.creation_executor import (
    CreationExecutor,
    _is_notion_retryable,
    _retry_notion,
)


class TestIsNotionRetryable:
    def test_rate_limit(self):
        assert _is_notion_retryable(Exception("rate_limit_exceeded")) is True

    def test_429(self):
        assert _is_notion_retryable(Exception("HTTP 429 Too Many Requests")) is True

    def test_502(self):
        assert _is_notion_retryable(Exception("502 Bad Gateway")) is True

    def test_503(self):
        assert _is_notion_retryable(Exception("503 Service Unavailable")) is True

    def test_504(self):
        assert _is_notion_retryable(Exception("504 Gateway Timeout")) is True

    def test_timeout(self):
        assert _is_notion_retryable(Exception("Connection timeout")) is True

    def test_connection_error(self):
        assert _is_notion_retryable(Exception("connection reset by peer")) is True

    def test_not_found(self):
        assert _is_notion_retryable(Exception("404 Not Found")) is False

    def test_unauthorized(self):
        assert _is_notion_retryable(Exception("401 Unauthorized")) is False

    def test_generic_error(self):
        assert _is_notion_retryable(Exception("unknown error")) is False


class TestRetryNotion:
    async def test_success_first_try(self):
        fn = AsyncMock(return_value={"id": "page-123"})
        result = await _retry_notion(fn)
        assert result["id"] == "page-123"
        assert fn.call_count == 1

    async def test_retry_on_rate_limit(self):
        fn = AsyncMock(side_effect=[Exception("429 rate limit"), {"id": "page-123"}])
        result = await _retry_notion(fn, max_retries=2)
        assert result["id"] == "page-123"
        assert fn.call_count == 2

    async def test_no_retry_on_permanent_error(self):
        fn = AsyncMock(side_effect=Exception("401 Unauthorized"))
        with pytest.raises(Exception, match="401"):
            await _retry_notion(fn, max_retries=2)
        assert fn.call_count == 1

    async def test_exhausts_retries(self):
        fn = AsyncMock(side_effect=Exception("503 Service Unavailable"))
        with pytest.raises(Exception, match="503"):
            await _retry_notion(fn, max_retries=1)
        assert fn.call_count == 2

    async def test_retry_with_timeout(self):
        fn = AsyncMock(side_effect=[Exception("Connection timeout"), {"ok": True}])
        result = await _retry_notion(fn, max_retries=1)
        assert result["ok"] is True


class TestSummarizePartialResult:
    def test_full_completion(self):
        bp = {
            "databases": [{"title": "DB1"}],
            "blocks": [{"type": "callout"}, {"type": "heading_1"}, {"type": "database_ref"}],
            "sub_pages": [{"title": "가이드"}],
        }
        result = {
            "pages": [{"id": "p1"}, {"id": "p2"}],
            "databases": [{"id": "db1"}],
            "blocks": 3,
        }
        summary = CreationExecutor.summarize_partial_result(bp, result)
        assert summary["completion_pct"] == 100.0
        assert summary["is_partial"] is False
        assert summary["databases"]["created"] == 1
        assert summary["blocks"]["created"] == 3
        assert summary["sub_pages"]["created"] == 1

    def test_partial_completion(self):
        bp = {
            "databases": [{"title": "DB1"}, {"title": "DB2"}],
            "blocks": [{"type": "callout"}, {"type": "heading_1"}, {"type": "database_ref"}, {"type": "database_ref"}],
            "sub_pages": [{"title": "A"}, {"title": "B"}],
        }
        result = {
            "pages": [{"id": "p1"}, {"id": "p2"}],
            "databases": [{"id": "db1"}],
            "blocks": 2,
        }
        summary = CreationExecutor.summarize_partial_result(bp, result)
        assert summary["is_partial"] is True
        assert summary["completion_pct"] < 100.0
        assert summary["databases"]["expected"] == 2
        assert summary["databases"]["created"] == 1

    def test_zero_expected(self):
        bp = {"databases": [], "blocks": [], "sub_pages": []}
        result = {"pages": [{"id": "p1"}], "databases": [], "blocks": 0}
        summary = CreationExecutor.summarize_partial_result(bp, result)
        assert summary["completion_pct"] == 0.0
        assert summary["is_partial"] is False

    def test_empty_result(self):
        bp = {
            "databases": [{"title": "DB"}],
            "blocks": [{"type": "callout"}],
            "sub_pages": [],
        }
        result = {"pages": [], "databases": [], "blocks": 0}
        summary = CreationExecutor.summarize_partial_result(bp, result)
        assert summary["completion_pct"] == 0.0
        assert summary["is_partial"] is False


class TestRollback:
    async def test_rollback_reverses_pages(self):
        mock_client = MagicMock()
        mock_client.archive_page = AsyncMock()
        executor = CreationExecutor(mock_client, MagicMock())

        result = {
            "pages": [
                {"id": "main-page", "title": "메인"},
                {"id": "sub-page-1", "title": "가이드"},
                {"id": "sub-page-2", "title": "FAQ"},
            ]
        }
        rolled = await executor.rollback(result)
        assert len(rolled) == 3
        assert mock_client.archive_page.call_count == 3
        calls = [c.args[0] for c in mock_client.archive_page.call_args_list]
        assert calls == ["sub-page-2", "sub-page-1", "main-page"]

    async def test_rollback_handles_archive_error(self):
        mock_client = MagicMock()
        mock_client.archive_page = AsyncMock(side_effect=[None, Exception("API error"), None])
        executor = CreationExecutor(mock_client, MagicMock())

        result = {
            "pages": [
                {"id": "p1", "title": "페이지1"},
                {"id": "p2", "title": "페이지2"},
                {"id": "p3", "title": "페이지3"},
            ]
        }
        rolled = await executor.rollback(result)
        assert len(rolled) == 2

    async def test_rollback_skips_empty_ids(self):
        mock_client = MagicMock()
        mock_client.archive_page = AsyncMock()
        executor = CreationExecutor(mock_client, MagicMock())

        result = {"pages": [{"title": "no-id"}, {"id": "real-id", "title": "있는페이지"}]}
        rolled = await executor.rollback(result)
        assert len(rolled) == 1
        assert mock_client.archive_page.call_count == 1


class TestValidateBlueprintIntegrity:
    def test_valid_blueprint(self):
        bp = {
            "main_page": {"title": "테스트"},
            "blocks": [{"type": "callout"}, {"type": "database_ref", "db_index": 0}],
            "databases": [{"properties": {"이름": "title"}}],
            "sub_pages": [],
        }
        issues = CreationExecutor.validate_blueprint_integrity(bp)
        assert len(issues) == 0

    def test_missing_main_title(self):
        bp = {"main_page": {}, "blocks": [], "databases": [], "sub_pages": []}
        issues = CreationExecutor.validate_blueprint_integrity(bp)
        assert any("title" in i for i in issues)

    def test_db_index_out_of_range(self):
        bp = {
            "main_page": {"title": "테스트"},
            "blocks": [{"type": "database_ref", "db_index": 5}],
            "databases": [{"properties": {"이름": "title"}}],
            "sub_pages": [],
        }
        issues = CreationExecutor.validate_blueprint_integrity(bp)
        assert any("범위 밖" in i for i in issues)

    def test_linked_view_out_of_range(self):
        bp = {
            "main_page": {"title": "테스트"},
            "blocks": [{"type": "linked_view", "db_index": 3}],
            "databases": [{"properties": {"이름": "title"}}],
            "sub_pages": [],
        }
        issues = CreationExecutor.validate_blueprint_integrity(bp)
        assert any("linked_view" in i for i in issues)

    def test_self_referencing_relation(self):
        bp = {
            "main_page": {"title": "테스트"},
            "blocks": [],
            "databases": [{"properties": {"이름": "title", "셀프": {"type": "relation", "target_db_index": 0}}}],
            "sub_pages": [],
        }
        issues = CreationExecutor.validate_blueprint_integrity(bp)
        assert any("자기참조" in i for i in issues)

    def test_relation_target_out_of_range(self):
        bp = {
            "main_page": {"title": "테스트"},
            "blocks": [],
            "databases": [{"properties": {"이름": "title", "연결": {"type": "relation", "target_db_index": 99}}}],
            "sub_pages": [],
        }
        issues = CreationExecutor.validate_blueprint_integrity(bp)
        assert any("범위 밖" in i for i in issues)

    def test_missing_title_property(self):
        bp = {
            "main_page": {"title": "테스트"},
            "blocks": [],
            "databases": [{"properties": {"상태": "status"}}],
            "sub_pages": [],
        }
        issues = CreationExecutor.validate_blueprint_integrity(bp)
        assert any("title 타입" in i for i in issues)

    def test_rollup_invalid_relation(self):
        bp = {
            "main_page": {"title": "테스트"},
            "blocks": [],
            "databases": [
                {"properties": {"이름": "title", "집계": {"type": "rollup", "relation_property": "없는속성"}}}
            ],
            "sub_pages": [],
        }
        issues = CreationExecutor.validate_blueprint_integrity(bp)
        assert any("rollup" in i for i in issues)

    def test_db_parent_not_in_sub_pages(self):
        bp = {
            "main_page": {"title": "테스트"},
            "blocks": [],
            "databases": [{"properties": {"이름": "title"}, "db_parent": "없는페이지"}],
            "sub_pages": [{"title": "가이드"}],
        }
        issues = CreationExecutor.validate_blueprint_integrity(bp)
        assert any("db_parent" in i for i in issues)

    def test_db_properties_alias(self):
        bp = {
            "main_page": {"title": "테스트"},
            "blocks": [],
            "databases": [{"db_properties": {"이름": "title"}}],
            "sub_pages": [],
        }
        issues = CreationExecutor.validate_blueprint_integrity(bp)
        assert len(issues) == 0


class TestAutoFixBlueprint:
    def test_fixes_db_index_out_of_range(self):
        bp = {
            "blocks": [{"type": "database_ref", "db_index": 5}],
            "databases": [{"properties": {"이름": "title"}}],
        }
        fixed = CreationExecutor._auto_fix_blueprint(bp, ["db_index 범위 밖"])
        assert fixed["blocks"][0]["db_index"] == 0

    def test_removes_invalid_relation(self):
        bp = {
            "blocks": [],
            "databases": [{"properties": {"이름": "title", "연결": {"type": "relation", "target_db_index": 99}}}],
        }
        fixed = CreationExecutor._auto_fix_blueprint(bp, ["relation 범위 밖"])
        assert "연결" not in fixed["databases"][0]["properties"]

    def test_removes_self_referencing_relation(self):
        bp = {
            "blocks": [],
            "databases": [{"properties": {"이름": "title", "셀프": {"type": "relation", "target_db_index": 0}}}],
        }
        fixed = CreationExecutor._auto_fix_blueprint(bp, ["자기참조"])
        assert "셀프" not in fixed["databases"][0]["properties"]

    def test_removes_invalid_rollup(self):
        bp = {
            "blocks": [],
            "databases": [{"properties": {"이름": "title", "집계": {"type": "rollup", "relation_property": "없는"}}}],
        }
        fixed = CreationExecutor._auto_fix_blueprint(bp, ["rollup"])
        assert "집계" not in fixed["databases"][0]["properties"]

    def test_fixes_linked_view_index(self):
        bp = {
            "blocks": [{"type": "linked_view", "db_index": 10}],
            "databases": [{"properties": {"이름": "title"}}],
        }
        fixed = CreationExecutor._auto_fix_blueprint(bp, ["linked_view 범위 밖"])
        assert fixed["blocks"][0]["db_index"] == 0

    def test_skips_non_dict_blocks(self):
        bp = {
            "blocks": ["not a dict"],
            "databases": [],
        }
        fixed = CreationExecutor._auto_fix_blueprint(bp, [])
        assert fixed["blocks"] == ["not a dict"]


class TestSubPageRefResolution:
    def test_resolves_exact_match(self):
        blocks = [{"type": "link_to_page", "sub_page_ref": "가이드"}]
        sub_page_map = {"가이드": "page-id-123"}
        CreationExecutor.resolve_sub_page_refs(blocks, sub_page_map)
        assert blocks[0]["page_id"] == "page-id-123"
        assert "sub_page_ref" not in blocks[0]

    def test_resolves_partial_match(self):
        blocks = [{"type": "link_to_page", "sub_page_ref": "가이드"}]
        sub_page_map = {"📖 가이드 페이지": "page-456"}
        CreationExecutor.resolve_sub_page_refs(blocks, sub_page_map)
        assert blocks[0]["page_id"] == "page-456"

    def test_no_match_leaves_unchanged(self):
        blocks = [{"type": "link_to_page", "sub_page_ref": "없는페이지"}]
        CreationExecutor.resolve_sub_page_refs(blocks, {"가이드": "p1"})
        assert "page_id" not in blocks[0]
        assert blocks[0]["sub_page_ref"] == "없는페이지"

    def test_resolves_in_children(self):
        blocks = [
            {
                "type": "toggle",
                "children": [{"type": "link_to_page", "sub_page_ref": "FAQ"}],
            }
        ]
        CreationExecutor.resolve_sub_page_refs(blocks, {"FAQ": "faq-id"})
        assert blocks[0]["children"][0]["page_id"] == "faq-id"

    def test_skips_non_dict_blocks(self):
        blocks = ["not a dict", {"type": "paragraph", "text": "ok"}]
        CreationExecutor.resolve_sub_page_refs(blocks, {"x": "y"})
