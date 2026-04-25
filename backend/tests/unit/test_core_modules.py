"""Core 모듈 테스트: exceptions, dependencies, history, chat schema"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from app.core.exceptions import (
    BlueprintValidationError,
    ClaudeApiError,
    NotionAuthError,
    NotionPageNotFoundError,
    NotionRateLimitError,
    TemplateGenerationError,
)
from app.core.history import get_recent_history, save_generation_record
from app.schemas.chat import ChatMessage, ChatResponse


class TestExceptions:
    def test_notion_auth_error(self):
        err = NotionAuthError()
        assert err.status_code == 401
        assert "토큰" in err.detail

    def test_notion_page_not_found(self):
        err = NotionPageNotFoundError()
        assert err.status_code == 404

    def test_notion_rate_limit(self):
        err = NotionRateLimitError()
        assert err.status_code == 429

    def test_claude_api_error_default(self):
        err = ClaudeApiError()
        assert err.status_code == 500

    def test_claude_api_error_custom(self):
        err = ClaudeApiError("커스텀 에러")
        assert "커스텀" in err.detail

    def test_blueprint_validation_error(self):
        err = BlueprintValidationError()
        assert err.status_code == 422

    def test_template_generation_error(self):
        err = TemplateGenerationError("생성 실패")
        assert err.status_code == 500
        assert "생성 실패" in err.detail


class TestChatSchema:
    def test_chat_message(self):
        msg = ChatMessage(content="테스트")
        assert msg.content == "테스트"
        assert msg.notion_token is None

    def test_chat_message_with_token(self):
        msg = ChatMessage(content="테스트", notion_token="tk", parent_page_id="pid")
        assert msg.notion_token == "tk"

    def test_chat_response(self):
        resp = ChatResponse(type="ai_response", content="답변")
        assert resp.type == "ai_response"
        assert resp.metadata is None


class TestHistory:
    def test_save_generation_record(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("app.core.history.HISTORY_DIR", Path(tmpdir)):
                path = save_generation_record({"total_time": 1.0, "status": "success"})
                assert path is not None
                assert path.exists()
                with open(path) as f:
                    record = json.loads(f.readline())
                    assert record["metrics"]["status"] == "success"

    def test_save_with_blueprint(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("app.core.history.HISTORY_DIR", Path(tmpdir)):
                bp = {
                    "metadata": {"title": "테스트", "template_type": "dashboard"},
                    "blocks": [{"type": "callout"}],
                    "databases": [{"title": "DB1"}],
                    "sub_pages": [],
                }
                path = save_generation_record({"status": "success"}, blueprint=bp)
                assert path is not None
                with open(path) as f:
                    record = json.loads(f.readline())
                    assert record["blueprint_meta"]["title"] == "테스트"
                    assert record["blueprint_meta"]["blocks_count"] == 1

    def test_get_recent_history_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("app.core.history.HISTORY_DIR", Path(tmpdir)):
                result = get_recent_history()
                assert result == []

    def test_get_recent_history_nonexistent_dir(self):
        with patch("app.core.history.HISTORY_DIR", Path("/nonexistent/path")):
            result = get_recent_history()
            assert result == []


class TestDependencies:
    def test_get_notion_client(self):
        from app.core.dependencies import get_notion_client

        client = get_notion_client()
        assert client is not None
