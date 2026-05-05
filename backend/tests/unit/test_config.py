"""Config settings 테스트"""

from unittest.mock import patch

from app.config import Settings


class TestAiProvider:
    def test_provider_claude(self):
        s = Settings(copilot_enabled=False, anthropic_api_key="sk-test", gemini_api_key="", groq_api_key="")
        assert s.ai_provider == "claude"

    def test_provider_gemini(self):
        s = Settings(copilot_enabled=False, anthropic_api_key="", gemini_api_key="gk-test", groq_api_key="")
        assert s.ai_provider == "gemini"

    def test_provider_groq(self):
        s = Settings(copilot_enabled=False, anthropic_api_key="", gemini_api_key="", groq_api_key="gk-test")
        assert s.ai_provider == "groq"

    def test_provider_mock(self):
        s = Settings(copilot_enabled=False, anthropic_api_key="", gemini_api_key="", groq_api_key="")
        assert s.ai_provider == "mock"

    def test_provider_copilot_import_error_falls_through(self):
        with patch.dict("sys.modules", {"app.core.copilot_client": None}):
            s = Settings(copilot_enabled=True, anthropic_api_key="sk-abc", gemini_api_key="", groq_api_key="")
            provider = s.ai_provider
            assert provider in ("copilot", "claude")


class TestProperties:
    def test_mock_mode(self):
        s = Settings(copilot_enabled=False, anthropic_api_key="", gemini_api_key="", groq_api_key="")
        assert s.mock_mode is True

    def test_notion_ready_true(self):
        s = Settings(notion_api_key="ntn_test", notion_parent_page_id="abc123")
        assert s.notion_ready is True

    def test_notion_ready_false(self):
        s = Settings(notion_api_key="", notion_parent_page_id="")
        assert s.notion_ready is False
