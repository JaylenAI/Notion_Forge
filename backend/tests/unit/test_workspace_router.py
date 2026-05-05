"""Workspace Router 테스트: 검색/코멘트/잠금/아카이브/메모리 엔드포인트"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.middleware import RateLimitMiddleware
from app.main import app

VALID_PAGE_ID = "abcdef12345678901234567890123456"
VALID_PAGE_ID_DASHES = "abcdef12-3456-7890-1234-567890123456"


def _reset_rate_limiter():
    """앱의 RateLimitMiddleware 내부 상태 초기화"""
    current = app.middleware_stack
    while current:
        if isinstance(current, RateLimitMiddleware):
            current._requests.clear()
            break
        current = getattr(current, "app", None)


@pytest.fixture
async def client():
    _reset_rate_limiter()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


class TestSearchEndpoint:
    """GET /api/templates/search"""

    async def test_search_returns_results(self, client):
        """검색 쿼리로 결과 반환"""
        mock_results = {
            "results": [
                {"id": "page-1", "title": "프로젝트 관리"},
                {"id": "page-2", "title": "프로젝트 대시보드"},
            ]
        }

        with patch("app.routers.workspace.NotionClient") as mock_cls:
            mock_instance = MagicMock()
            mock_instance.mock_mode = False
            mock_instance.search = AsyncMock(return_value=mock_results)
            mock_cls.return_value = mock_instance

            resp = await client.get("/api/templates/search?q=프로젝트")

        assert resp.status_code == 200
        data = resp.json()
        assert "results" in data
        assert len(data["results"]) == 2

    async def test_search_empty_query(self, client):
        """빈 쿼리도 정상 응답 (전체 검색)"""
        with patch("app.routers.workspace.NotionClient") as mock_cls:
            mock_instance = MagicMock()
            mock_instance.mock_mode = False
            mock_instance.search = AsyncMock(return_value={"results": []})
            mock_cls.return_value = mock_instance

            resp = await client.get("/api/templates/search?q=")

        assert resp.status_code == 200

    async def test_search_mock_mode(self, client):
        """mock_mode일 때 빈 결과 반환"""
        with patch("app.routers.workspace.NotionClient") as mock_cls:
            mock_instance = MagicMock()
            mock_instance.mock_mode = True
            mock_cls.return_value = mock_instance

            resp = await client.get("/api/templates/search?q=test")

        assert resp.status_code == 200
        data = resp.json()
        assert data["results"] == []


class TestCommentEndpoint:
    """POST /api/templates/{page_id}/comment"""

    async def test_add_comment_success(self, client):
        """정상 코멘트 추가"""
        with patch("app.routers.workspace.NotionClient") as mock_cls:
            mock_instance = MagicMock()
            mock_instance.add_comment = AsyncMock(return_value={"id": "comment-1"})
            mock_cls.return_value = mock_instance

            resp = await client.post(f"/api/templates/{VALID_PAGE_ID}/comment?text=좋은 템플릿입니다")

        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "comment-1"

    async def test_add_comment_empty_text_returns_400(self, client):
        """빈 텍스트는 400 반환"""
        resp = await client.post(f"/api/templates/{VALID_PAGE_ID}/comment?text=")
        assert resp.status_code == 400
        data = resp.json()
        assert "1~2000자" in data["detail"]

    async def test_add_comment_too_long_returns_400(self, client):
        """2000자 초과 텍스트는 400 반환"""
        long_text = "a" * 2001
        resp = await client.post(f"/api/templates/{VALID_PAGE_ID}/comment?text={long_text}")
        assert resp.status_code == 400
        data = resp.json()
        assert "1~2000자" in data["detail"]

    async def test_add_comment_exactly_2000_chars(self, client):
        """정확히 2000자는 허용"""
        text_2000 = "a" * 2000
        with patch("app.routers.workspace.NotionClient") as mock_cls:
            mock_instance = MagicMock()
            mock_instance.add_comment = AsyncMock(return_value={"id": "comment-ok"})
            mock_cls.return_value = mock_instance

            resp = await client.post(f"/api/templates/{VALID_PAGE_ID}/comment?text={text_2000}")

        assert resp.status_code == 200

    async def test_add_comment_invalid_page_id(self, client):
        """유효하지 않은 page_id는 400 반환"""
        resp = await client.post("/api/templates/invalid-id-format!/comment?text=hello")
        assert resp.status_code == 400
        data = resp.json()
        assert "페이지 ID" in data["detail"]

    async def test_add_comment_with_dashes_page_id(self, client):
        """하이픈 포함된 UUID 형식도 허용"""
        with patch("app.routers.workspace.NotionClient") as mock_cls:
            mock_instance = MagicMock()
            mock_instance.add_comment = AsyncMock(return_value={"id": "c-1"})
            mock_cls.return_value = mock_instance

            resp = await client.post(f"/api/templates/{VALID_PAGE_ID_DASHES}/comment?text=test")

        assert resp.status_code == 200


class TestLockEndpoint:
    """POST /api/templates/{page_id}/lock"""

    async def test_lock_page_success(self, client):
        """페이지 잠금 성공"""
        with patch("app.routers.workspace.NotionClient") as mock_cls:
            mock_instance = MagicMock()
            mock_instance.lock_page = AsyncMock(return_value={"locked": True})
            mock_cls.return_value = mock_instance

            resp = await client.post(f"/api/templates/{VALID_PAGE_ID}/lock?locked=true")

        assert resp.status_code == 200
        data = resp.json()
        assert data["locked"] is True

    async def test_unlock_page(self, client):
        """페이지 잠금 해제"""
        with patch("app.routers.workspace.NotionClient") as mock_cls:
            mock_instance = MagicMock()
            mock_instance.lock_page = AsyncMock(return_value={"locked": False})
            mock_cls.return_value = mock_instance

            resp = await client.post(f"/api/templates/{VALID_PAGE_ID}/lock?locked=false")

        assert resp.status_code == 200
        data = resp.json()
        assert data["locked"] is False

    async def test_lock_invalid_page_id(self, client):
        """유효하지 않은 page_id는 400"""
        resp = await client.post("/api/templates/INVALID_PAGE/lock?locked=true")
        assert resp.status_code == 400

    async def test_lock_default_is_true(self, client):
        """locked 파라미터 기본값은 True"""
        with patch("app.routers.workspace.NotionClient") as mock_cls:
            mock_instance = MagicMock()
            mock_instance.lock_page = AsyncMock(return_value={"locked": True})
            mock_cls.return_value = mock_instance

            resp = await client.post(f"/api/templates/{VALID_PAGE_ID}/lock")

        assert resp.status_code == 200


class TestArchiveEndpoint:
    """POST /api/templates/{page_id}/archive"""

    async def test_archive_page_success(self, client):
        """페이지 아카이브 성공"""
        with patch("app.routers.workspace.NotionClient") as mock_cls:
            mock_instance = MagicMock()
            mock_instance.archive_page = AsyncMock(return_value={"archived": True})
            mock_cls.return_value = mock_instance

            resp = await client.post(f"/api/templates/{VALID_PAGE_ID}/archive")

        assert resp.status_code == 200
        data = resp.json()
        assert data["archived"] is True

    async def test_archive_invalid_page_id(self, client):
        """유효하지 않은 page_id는 400"""
        resp = await client.post("/api/templates/not_valid!!!/archive")
        assert resp.status_code == 400


class TestPreferencesEndpoint:
    """메모리 선호도 GET/POST"""

    async def test_get_preferences(self, client):
        """선호도 조회"""
        mock_prefs = {"color_theme": "dark", "language": "ko"}

        with patch("app.agent.memory.memory") as mock_memory:
            mock_memory.get_all_preferences.return_value = mock_prefs

            resp = await client.get("/api/templates/memory/preferences")

        assert resp.status_code == 200
        data = resp.json()
        assert data["preferences"] == mock_prefs

    async def test_set_preference_success(self, client):
        """선호도 설정 성공"""
        with patch("app.agent.memory.memory") as mock_memory:
            mock_memory.save_preference = MagicMock()

            resp = await client.post("/api/templates/memory/preferences?key=theme&value=dark")

        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    async def test_set_preference_empty_key_returns_400(self, client):
        """빈 key는 400"""
        resp = await client.post("/api/templates/memory/preferences?key=&value=something")
        assert resp.status_code == 400
        data = resp.json()
        assert "1~50자" in data["detail"]

    async def test_set_preference_long_key_returns_400(self, client):
        """50자 초과 key는 400"""
        long_key = "k" * 51
        resp = await client.post(f"/api/templates/memory/preferences?key={long_key}&value=x")
        assert resp.status_code == 400

    async def test_set_preference_empty_value_allowed(self, client):
        """빈 value는 허용 (선호도 초기화 용도)"""
        with patch("app.agent.memory.memory") as mock_memory:
            mock_memory.save_preference = MagicMock()

            resp = await client.post("/api/templates/memory/preferences?key=theme&value=")

        assert resp.status_code == 200


class TestHistoryEndpoint:
    """GET /api/templates/history/recent"""

    async def test_get_recent_history(self, client):
        """최근 이력 조회"""
        mock_records = [
            {"prompt": "대시보드", "metrics": {"success": True}},
            {"prompt": "노트", "metrics": {"success": False}},
        ]

        with patch("app.core.history.get_recent_history", return_value=mock_records):
            resp = await client.get("/api/templates/history/recent")

        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 2
        assert len(data["records"]) == 2

    async def test_history_with_custom_params(self, client):
        """커스텀 days/limit 파라미터"""
        with patch("app.core.history.get_recent_history", return_value=[]) as mock_fn:
            resp = await client.get("/api/templates/history/recent?days=30&limit=10")

        assert resp.status_code == 200
        mock_fn.assert_called_once_with(days=30, limit=10)


class TestMemoryStatsEndpoint:
    """GET /api/templates/memory/stats"""

    async def test_get_memory_stats(self, client):
        """스킬 사용 통계 조회"""
        mock_stats = {"project": {"total": 10, "success": 8}, "dashboard": {"total": 5, "success": 5}}

        with patch("app.agent.memory.memory") as mock_memory:
            mock_memory.get_skill_stats.return_value = mock_stats

            resp = await client.get("/api/templates/memory/stats")

        assert resp.status_code == 200
        data = resp.json()
        assert data["stats"] == mock_stats


class TestPageIdValidation:
    """페이지 ID 형식 검증 유닛 테스트"""

    async def test_valid_32_hex(self, client):
        """32자리 hex는 유효"""
        with patch("app.routers.workspace.NotionClient") as mock_cls:
            mock_instance = MagicMock()
            mock_instance.archive_page = AsyncMock(return_value={"ok": True})
            mock_cls.return_value = mock_instance

            resp = await client.post(f"/api/templates/{VALID_PAGE_ID}/archive")
        assert resp.status_code == 200

    async def test_valid_uuid_with_dashes(self, client):
        """UUID 형식(하이픈 포함 36자)은 유효"""
        with patch("app.routers.workspace.NotionClient") as mock_cls:
            mock_instance = MagicMock()
            mock_instance.archive_page = AsyncMock(return_value={"ok": True})
            mock_cls.return_value = mock_instance

            resp = await client.post(f"/api/templates/{VALID_PAGE_ID_DASHES}/archive")
        assert resp.status_code == 200

    async def test_invalid_special_chars(self, client):
        """특수문자 포함 시 400"""
        resp = await client.post("/api/templates/abc!@#$%^&*()/archive")
        assert resp.status_code in (400, 404, 422)

    async def test_invalid_too_short(self, client):
        """너무 짧은 ID는 400"""
        resp = await client.post("/api/templates/abc123/archive")
        assert resp.status_code == 400

    async def test_invalid_uppercase(self, client):
        """대문자 hex는 400 (소문자만 허용)"""
        resp = await client.post("/api/templates/ABCDEF12345678901234567890123456/archive")
        assert resp.status_code == 400
