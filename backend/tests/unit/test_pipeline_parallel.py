"""Phase 4 파이프라인 병렬화 + Pre-creation 검증 테스트"""

import pytest

from app.agent.creation_executor import CreationExecutor
from app.notion.rate_limiter import RateLimiter


class TestRateLimiter:
    @pytest.mark.asyncio
    async def test_acquire_within_limit(self):
        limiter = RateLimiter(max_per_second=3)
        for _ in range(3):
            await limiter.acquire()

    @pytest.mark.asyncio
    async def test_gather_with_limit(self):
        limiter = RateLimiter(max_per_second=5)
        results = []

        async def task(i: int) -> int:
            results.append(i)
            return i

        tasks = [lambda i=i: task(i) for i in range(5)]
        out = await limiter.gather_with_limit(tasks)
        assert len(out) == 5
        assert set(out) == {0, 1, 2, 3, 4}

    @pytest.mark.asyncio
    async def test_gather_handles_exceptions(self):
        limiter = RateLimiter(max_per_second=3)

        async def ok_task() -> str:
            return "ok"

        async def fail_task() -> str:
            raise ValueError("fail")

        results = await limiter.gather_with_limit([ok_task, fail_task, ok_task])
        assert results[0] == "ok"
        assert isinstance(results[1], ValueError)
        assert results[2] == "ok"

    @pytest.mark.asyncio
    async def test_call_with_retry_success(self):
        limiter = RateLimiter(max_per_second=3)
        call_count = 0

        async def flaky() -> str:
            nonlocal call_count
            call_count += 1
            return "ok"

        result = await limiter.call_with_retry(flaky, max_retries=3)
        assert result == "ok"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_call_with_retry_rate_limit(self):
        limiter = RateLimiter(max_per_second=3)
        call_count = 0

        async def rate_limited() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("429 Too Many Requests")
            return "ok"

        result = await limiter.call_with_retry(rate_limited, max_retries=3)
        assert result == "ok"
        assert call_count == 3


class TestBlueprintIntegrity:
    def test_valid_blueprint_passes(self):
        blueprint = {
            "main_page": {"title": "Test"},
            "blocks": [
                {"type": "callout", "text": "Hi"},
                {"type": "database_ref", "db_index": 0},
            ],
            "databases": [{"title": "DB1", "properties": {"이름": "title"}}],
            "sub_pages": [],
        }
        issues = CreationExecutor.validate_blueprint_integrity(blueprint)
        assert issues == []

    def test_missing_title(self):
        blueprint = {
            "main_page": {"title": ""},
            "blocks": [{"type": "database_ref", "db_index": 0}],
            "databases": [{"title": "DB1", "properties": {"이름": "title"}}],
            "sub_pages": [],
        }
        issues = CreationExecutor.validate_blueprint_integrity(blueprint)
        assert any("main_page.title" in i for i in issues)

    def test_db_index_out_of_range(self):
        blueprint = {
            "main_page": {"title": "Test"},
            "blocks": [{"type": "database_ref", "db_index": 5}],
            "databases": [{"title": "DB1", "properties": {"이름": "title"}}],
            "sub_pages": [],
        }
        issues = CreationExecutor.validate_blueprint_integrity(blueprint)
        assert any("db_index=5" in i for i in issues)

    def test_linked_view_out_of_range(self):
        blueprint = {
            "main_page": {"title": "Test"},
            "blocks": [{"type": "linked_view", "db_index": 3}],
            "databases": [{"title": "DB1", "properties": {"이름": "title"}}],
            "sub_pages": [],
        }
        issues = CreationExecutor.validate_blueprint_integrity(blueprint)
        assert any("linked_view" in i for i in issues)

    def test_self_referencing_relation(self):
        blueprint = {
            "main_page": {"title": "Test"},
            "blocks": [],
            "databases": [
                {
                    "title": "DB1",
                    "properties": {
                        "이름": "title",
                        "자기참조": {"type": "relation", "target_db_index": 0},
                    },
                },
            ],
            "sub_pages": [],
        }
        issues = CreationExecutor.validate_blueprint_integrity(blueprint)
        assert any("자기참조" in i for i in issues)

    def test_relation_target_out_of_range(self):
        blueprint = {
            "main_page": {"title": "Test"},
            "blocks": [],
            "databases": [
                {
                    "title": "DB1",
                    "properties": {
                        "이름": "title",
                        "연결": {"type": "relation", "target_db_index": 5},
                    },
                },
            ],
            "sub_pages": [],
        }
        issues = CreationExecutor.validate_blueprint_integrity(blueprint)
        assert any("범위 밖" in i for i in issues)

    def test_rollup_missing_relation_property(self):
        blueprint = {
            "main_page": {"title": "Test"},
            "blocks": [],
            "databases": [
                {
                    "title": "DB1",
                    "properties": {
                        "이름": "title",
                        "합계": {"type": "rollup", "relation_property": "없는속성"},
                    },
                },
            ],
            "sub_pages": [],
        }
        issues = CreationExecutor.validate_blueprint_integrity(blueprint)
        assert any("없는속성" in i for i in issues)

    def test_db_parent_not_in_sub_pages(self):
        blueprint = {
            "main_page": {"title": "Test"},
            "blocks": [],
            "databases": [
                {"title": "DB1", "properties": {"이름": "title"}, "db_parent": "없는페이지"},
            ],
            "sub_pages": [{"title": "다른페이지"}],
        }
        issues = CreationExecutor.validate_blueprint_integrity(blueprint)
        assert any("없는페이지" in i for i in issues)

    def test_missing_title_property(self):
        blueprint = {
            "main_page": {"title": "Test"},
            "blocks": [],
            "databases": [
                {"title": "DB1", "properties": {"이름": "rich_text", "상태": "status"}},
            ],
            "sub_pages": [],
        }
        issues = CreationExecutor.validate_blueprint_integrity(blueprint)
        assert any("title 타입" in i for i in issues)


class TestAutoFixBlueprint:
    def test_fixes_db_index_out_of_range(self):
        blueprint = {
            "blocks": [{"type": "database_ref", "db_index": 5}],
            "databases": [{"title": "DB1", "properties": {"이름": "title"}}],
        }
        fixed = CreationExecutor._auto_fix_blueprint(blueprint, ["db_index out of range"])
        assert fixed["blocks"][0]["db_index"] == 0

    def test_removes_invalid_relation(self):
        blueprint = {
            "blocks": [],
            "databases": [
                {
                    "title": "DB1",
                    "properties": {
                        "이름": "title",
                        "잘못된연결": {"type": "relation", "target_db_index": 5},
                    },
                },
            ],
        }
        fixed = CreationExecutor._auto_fix_blueprint(blueprint, ["relation out of range"])
        props = fixed["databases"][0]["properties"]
        assert "잘못된연결" not in props
        assert "이름" in props

    def test_removes_self_referencing_relation(self):
        blueprint = {
            "blocks": [],
            "databases": [
                {
                    "title": "DB1",
                    "properties": {
                        "이름": "title",
                        "자기참조": {"type": "relation", "target_db_index": 0},
                    },
                },
            ],
        }
        fixed = CreationExecutor._auto_fix_blueprint(blueprint, ["self-reference"])
        assert "자기참조" not in fixed["databases"][0]["properties"]

    def test_removes_orphan_rollup(self):
        blueprint = {
            "blocks": [],
            "databases": [
                {
                    "title": "DB1",
                    "properties": {
                        "이름": "title",
                        "합계": {"type": "rollup", "relation_property": "없는속성"},
                    },
                },
            ],
        }
        fixed = CreationExecutor._auto_fix_blueprint(blueprint, ["rollup orphan"])
        assert "합계" not in fixed["databases"][0]["properties"]
