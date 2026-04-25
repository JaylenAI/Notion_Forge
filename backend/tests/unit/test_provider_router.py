"""Provider Router 단위 테스트"""

import pytest

from app.agent.providers.base import BaseProvider
from app.agent.providers.router import ProviderRouter, create_provider, detect_provider_from_key


class TestDetectProviderFromKey:
    def test_empty_key(self):
        assert detect_provider_from_key("") == ""

    def test_claude_key(self):
        assert detect_provider_from_key("sk-ant-abc123") == "claude"

    def test_openai_key(self):
        assert detect_provider_from_key("sk-proj-abc123") == "openai"

    def test_openai_generic_key(self):
        assert detect_provider_from_key("sk-abc123def456") == "openai"

    def test_groq_key(self):
        assert detect_provider_from_key("gsk_abc123def456") == "groq"

    def test_gemini_key(self):
        assert detect_provider_from_key("AIzaSyAbc123def456ghi789jkl0123456") == "gemini"

    def test_short_ai_key_not_gemini(self):
        assert detect_provider_from_key("AIshort") == "openai"

    def test_unknown_key_defaults_openai(self):
        assert detect_provider_from_key("unknown-key-format") == "openai"

    def test_claude_before_openai(self):
        assert detect_provider_from_key("sk-ant-") == "claude"


class TestCreateProvider:
    def test_claude(self):
        provider = create_provider("claude", api_key="test")
        assert isinstance(provider, BaseProvider)
        assert provider.name == "claude"

    def test_gemini(self):
        provider = create_provider("gemini", api_key="test")
        assert provider.name == "gemini"

    def test_groq(self):
        provider = create_provider("groq", api_key="test")
        assert provider.name == "groq"

    def test_openai(self):
        provider = create_provider("openai", api_key="test")
        assert provider.name == "openai"

    def test_mock(self):
        provider = create_provider("mock")
        assert provider.name == "mock"

    def test_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown provider"):
            create_provider("nonexistent")

    def test_model_passthrough(self):
        provider = create_provider("groq", model="custom-model")
        assert provider.default_model == "custom-model"


class TestProviderRouter:
    def test_resolve_with_api_key(self):
        provider = ProviderRouter.resolve(api_key="sk-ant-test123")
        assert provider.name == "claude"

    def test_resolve_groq_key(self):
        provider = ProviderRouter.resolve(api_key="gsk_test123")
        assert provider.name == "groq"


class TestBaseProviderExtractJson:
    def test_json_block(self):
        text = '```json\n{"key": "value"}\n```'
        assert BaseProvider.extract_json(text) == {"key": "value"}

    def test_raw_json(self):
        text = '{"key": "value"}'
        assert BaseProvider.extract_json(text) == {"key": "value"}

    def test_json_in_text(self):
        text = 'Some text before {"key": "value"} and after'
        assert BaseProvider.extract_json(text) == {"key": "value"}

    def test_empty_text(self):
        assert BaseProvider.extract_json("") is None

    def test_no_json(self):
        assert BaseProvider.extract_json("no json here") is None

    def test_invalid_json(self):
        assert BaseProvider.extract_json("{invalid}") is None


class TestBaseProviderExtractBlueprintJson:
    def test_with_databases(self):
        text = '{"databases": [{"title": "DB"}]}'
        result = BaseProvider.extract_blueprint_json(text)
        assert result is not None
        assert "databases" in result

    def test_with_db_properties(self):
        text = '{"db_properties": {"name": "title"}}'
        result = BaseProvider.extract_blueprint_json(text)
        assert result is not None

    def test_without_required_fields(self):
        text = '{"title": "test"}'
        assert BaseProvider.extract_blueprint_json(text) is None


class TestGroqProviderMaxChars:
    def test_max_prompt_chars(self):
        provider = create_provider("groq")
        assert provider.get_max_prompt_chars() == 12000

    def test_base_provider_unlimited(self):
        provider = create_provider("claude")
        assert provider.get_max_prompt_chars() == 0


class TestMockProvider:
    @pytest.mark.asyncio
    async def test_returns_none(self):
        provider = create_provider("mock")
        result = await provider.call("system", "user")
        assert result is None
