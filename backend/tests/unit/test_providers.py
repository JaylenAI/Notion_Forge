"""LLM Provider 테스트 — OpenAI, Claude, Groq, Gemini"""

from unittest.mock import AsyncMock, MagicMock, patch

from app.agent.providers.claude_provider import ClaudeProvider
from app.agent.providers.gemini_provider import GeminiProvider
from app.agent.providers.groq_provider import GroqProvider
from app.agent.providers.openai_provider import OpenAIProvider


class TestOpenAIProvider:
    def test_init_defaults(self):
        p = OpenAIProvider()
        assert p.name == "openai"
        assert p.default_model == "gpt-4o-mini"

    def test_init_custom(self):
        p = OpenAIProvider(api_key="sk-test", model="gpt-4.1")
        assert p.api_key == "sk-test"
        assert p.default_model == "gpt-4.1"

    async def test_call_success(self):
        p = OpenAIProvider(api_key="sk-test")

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": '{"action": "create"}'}}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 50},
        }

        with patch("httpx.AsyncClient") as mock_http:
            mock_instance = AsyncMock()
            mock_instance.post = AsyncMock(return_value=mock_resp)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_http.return_value = mock_instance

            result = await p.call("system", "user msg")

        assert result == {"action": "create"}

    async def test_call_http_error(self):
        p = OpenAIProvider(api_key="sk-test")

        mock_resp = MagicMock()
        mock_resp.status_code = 429
        mock_resp.text = "rate limited"

        with patch("httpx.AsyncClient") as mock_http:
            mock_instance = AsyncMock()
            mock_instance.post = AsyncMock(return_value=mock_resp)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_http.return_value = mock_instance

            result = await p.call("system", "user msg")

        assert result is None

    async def test_call_exception(self):
        p = OpenAIProvider(api_key="sk-test")

        with patch("httpx.AsyncClient") as mock_http:
            mock_instance = AsyncMock()
            mock_instance.post = AsyncMock(side_effect=Exception("timeout"))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_http.return_value = mock_instance

            result = await p.call("system", "user msg")

        assert result is None

    async def test_call_with_tools_success(self):
        p = OpenAIProvider(api_key="sk-test")

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [
                {
                    "message": {
                        "tool_calls": [
                            {
                                "function": {
                                    "name": "create_database",
                                    "arguments": '{"title": "DB"}',
                                }
                            }
                        ]
                    }
                }
            ]
        }

        with patch("httpx.AsyncClient") as mock_http:
            mock_instance = AsyncMock()
            mock_instance.post = AsyncMock(return_value=mock_resp)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_http.return_value = mock_instance

            tools = [{"type": "function", "function": {"name": "create_database", "parameters": {}}}]
            result = await p.call_with_tools("system", "user", tools)

        assert result["tool_calls"][0]["name"] == "create_database"
        assert result["tool_calls"][0]["arguments"] == {"title": "DB"}

    async def test_call_with_tools_text_response(self):
        p = OpenAIProvider(api_key="sk-test")

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"choices": [{"message": {"content": '{"result": "ok"}', "tool_calls": None}}]}

        with patch("httpx.AsyncClient") as mock_http:
            mock_instance = AsyncMock()
            mock_instance.post = AsyncMock(return_value=mock_resp)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_http.return_value = mock_instance

            result = await p.call_with_tools("system", "user", [])

        assert result == {"result": "ok"}

    async def test_call_with_tools_error(self):
        p = OpenAIProvider(api_key="sk-test")

        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.text = "server error"

        with patch("httpx.AsyncClient") as mock_http:
            mock_instance = AsyncMock()
            mock_instance.post = AsyncMock(return_value=mock_resp)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_http.return_value = mock_instance

            result = await p.call_with_tools("system", "user", [])

        assert result is None


class TestClaudeProvider:
    def test_init_defaults(self):
        p = ClaudeProvider()
        assert p.name == "claude"
        assert p.default_model == "claude-sonnet-4-6"

    async def test_call_success(self):
        p = ClaudeProvider(api_key="sk-ant-test")

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='{"action": "plan"}')]
        mock_response.usage = MagicMock(input_tokens=80, output_tokens=40)

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        with patch("anthropic.AsyncAnthropic", return_value=mock_client):
            result = await p.call("system", "user msg")

        assert result == {"action": "plan"}

    async def test_call_import_error(self):
        p = ClaudeProvider(api_key="sk-ant-test")

        with patch.dict("sys.modules", {"anthropic": None}):
            with patch("builtins.__import__", side_effect=ImportError("no anthropic")):
                result = await p.call("system", "user msg")

        assert result is None

    async def test_call_exception(self):
        p = ClaudeProvider(api_key="sk-ant-test")

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(side_effect=Exception("API error"))

        with patch("anthropic.AsyncAnthropic", return_value=mock_client):
            result = await p.call("system", "user msg")

        assert result is None

    async def test_call_with_tools_tool_use(self):
        p = ClaudeProvider(api_key="sk-ant-test")

        tool_block = MagicMock()
        tool_block.type = "tool_use"
        tool_block.name = "add_blocks"
        tool_block.input = {"page_id": "p1", "blocks": []}

        mock_response = MagicMock()
        mock_response.content = [tool_block]
        mock_response.usage = MagicMock(input_tokens=100, output_tokens=60)

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        with patch("anthropic.AsyncAnthropic", return_value=mock_client):
            tools = [{"type": "function", "function": {"name": "add_blocks", "parameters": {}}}]
            result = await p.call_with_tools("system", "user", tools)

        assert result["tool_calls"][0]["name"] == "add_blocks"

    async def test_call_with_tools_text_response(self):
        p = ClaudeProvider(api_key="sk-ant-test")

        text_block = MagicMock()
        text_block.type = "text"
        text_block.text = '{"status": "done"}'

        mock_response = MagicMock()
        mock_response.content = [text_block]
        mock_response.usage = MagicMock(input_tokens=100, output_tokens=30)

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        with patch("anthropic.AsyncAnthropic", return_value=mock_client):
            result = await p.call_with_tools("system", "user", [])

        assert result == {"status": "done"}


class TestGroqProvider:
    def test_init_defaults(self):
        p = GroqProvider()
        assert p.name == "groq"
        assert p.default_model == "openai/gpt-oss-120b"

    def test_max_prompt_chars(self):
        p = GroqProvider()
        assert p.get_max_prompt_chars() == 12000

    async def test_call_success(self):
        p = GroqProvider(api_key="gsk-test")

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content='{"result": "ok"}'))]
        mock_response.usage = MagicMock(prompt_tokens=50, completion_tokens=30)

        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        with patch("groq.AsyncGroq", return_value=mock_client):
            result = await p.call("system", "user msg")

        assert result == {"result": "ok"}

    async def test_call_truncates_long_prompt(self):
        p = GroqProvider(api_key="gsk-test")

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content='{"ok": true}'))]
        mock_response.usage = None

        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        long_prompt = "x" * 15000
        with patch("groq.AsyncGroq", return_value=mock_client):
            result = await p.call(long_prompt, "user msg")

        assert result == {"ok": True}
        call_args = mock_client.chat.completions.create.call_args
        actual_system = call_args.kwargs["messages"][0]["content"]
        assert len(actual_system) == 12000

    async def test_call_exception(self):
        p = GroqProvider(api_key="gsk-test")

        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(side_effect=Exception("rate limit"))

        with patch("groq.AsyncGroq", return_value=mock_client):
            result = await p.call("system", "user msg")

        assert result is None

    async def test_call_injects_json_word_when_absent(self):
        """json_object 모드는 메시지에 'json'이 없으면 Groq가 400을 낸다 → user 메시지에 보장 (라이브 회귀)."""
        p = GroqProvider(api_key="gsk-test")
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content='{"ok": true}'))]
        mock_response.usage = None
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        # system/user 어디에도 'json'이 없는 프롬프트
        with patch("groq.AsyncGroq", return_value=mock_client):
            await p.call("템플릿을 설계하라", "회의록 만들어줘")
        msgs = mock_client.chat.completions.create.call_args.kwargs["messages"]
        combined = (msgs[0]["content"] + msgs[1]["content"]).lower()
        assert "json" in combined, "json_object 모드인데 메시지에 'json' 단어가 없음 (Groq 400 유발)"

    async def test_call_keeps_user_message_when_json_present(self):
        """이미 'json'이 있으면 user 메시지를 변형하지 않는다."""
        p = GroqProvider(api_key="gsk-test")
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content='{"ok": true}'))]
        mock_response.usage = None
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        with patch("groq.AsyncGroq", return_value=mock_client):
            await p.call("Output JSON only.", "회의록 만들어줘")
        msgs = mock_client.chat.completions.create.call_args.kwargs["messages"]
        assert msgs[1]["content"] == "회의록 만들어줘"  # 변형 없음

    async def test_call_with_tools_tool_calls(self):
        p = GroqProvider(api_key="gsk-test")

        tc = MagicMock()
        tc.function.name = "search"
        tc.function.arguments = '{"query": "test"}'

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(tool_calls=[tc], content=""))]

        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        with patch("groq.AsyncGroq", return_value=mock_client):
            tools = [{"type": "function", "function": {"name": "search", "parameters": {}}}]
            result = await p.call_with_tools("system", "user", tools)

        assert result["tool_calls"][0]["name"] == "search"

    async def test_call_with_tools_no_tool_calls(self):
        p = GroqProvider(api_key="gsk-test")

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(tool_calls=None, content='{"done": true}'))]

        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        with patch("groq.AsyncGroq", return_value=mock_client):
            result = await p.call_with_tools("system", "user", [])

        assert result == {"done": True}


class TestGeminiProvider:
    def test_init_defaults(self):
        p = GeminiProvider()
        assert p.name == "gemini"
        assert p.default_model == "gemini-2.5-flash"

    async def test_call_success(self):
        p = GeminiProvider(api_key="AIza-test")

        mock_response = MagicMock()
        mock_response.text = '{"plan": "create page"}'

        mock_aio_models = AsyncMock()
        mock_aio_models.generate_content = AsyncMock(return_value=mock_response)

        mock_client = MagicMock()
        mock_client.aio.models = mock_aio_models

        with patch("google.genai.Client", return_value=mock_client):
            result = await p.call("system", "user msg")

        assert result == {"plan": "create page"}

    async def test_call_empty_response(self):
        p = GeminiProvider(api_key="AIza-test")

        mock_response = MagicMock()
        mock_response.text = ""

        mock_aio_models = AsyncMock()
        mock_aio_models.generate_content = AsyncMock(return_value=mock_response)

        mock_client = MagicMock()
        mock_client.aio.models = mock_aio_models

        with patch("google.genai.Client", return_value=mock_client):
            result = await p.call("system", "user msg")

        assert result is None

    async def test_call_invalid_json(self):
        p = GeminiProvider(api_key="AIza-test")

        mock_response = MagicMock()
        mock_response.text = "not json at all"

        mock_aio_models = AsyncMock()
        mock_aio_models.generate_content = AsyncMock(return_value=mock_response)

        mock_client = MagicMock()
        mock_client.aio.models = mock_aio_models

        with patch("google.genai.Client", return_value=mock_client):
            result = await p.call("system", "user msg")

        assert result is None

    async def test_call_exception(self):
        p = GeminiProvider(api_key="AIza-test")

        mock_aio_models = AsyncMock()
        mock_aio_models.generate_content = AsyncMock(side_effect=Exception("quota exceeded"))

        mock_client = MagicMock()
        mock_client.aio.models = mock_aio_models

        with patch("google.genai.Client", return_value=mock_client):
            result = await p.call("system", "user msg")

        assert result is None

    async def test_call_with_tools_function_call(self):
        p = GeminiProvider(api_key="AIza-test")

        fc = MagicMock()
        fc.name = "create_page"
        fc.args = {"title": "새 페이지"}

        part = MagicMock()
        part.function_call = fc
        part.text = None

        candidate = MagicMock()
        candidate.content.parts = [part]

        mock_response = MagicMock()
        mock_response.candidates = [candidate]

        mock_aio_models = AsyncMock()
        mock_aio_models.generate_content = AsyncMock(return_value=mock_response)

        mock_client = MagicMock()
        mock_client.aio.models = mock_aio_models

        with patch("google.genai.Client", return_value=mock_client):
            tools = [{"type": "function", "function": {"name": "create_page", "parameters": {}}}]
            result = await p.call_with_tools("system", "user", tools)

        assert result["tool_calls"][0]["name"] == "create_page"
        assert result["tool_calls"][0]["arguments"] == {"title": "새 페이지"}

    async def test_call_with_tools_text_response(self):
        p = GeminiProvider(api_key="AIza-test")

        part = MagicMock()
        part.function_call = None
        part.text = '{"status": "complete"}'

        candidate = MagicMock()
        candidate.content.parts = [part]

        mock_response = MagicMock()
        mock_response.candidates = [candidate]

        mock_aio_models = AsyncMock()
        mock_aio_models.generate_content = AsyncMock(return_value=mock_response)

        mock_client = MagicMock()
        mock_client.aio.models = mock_aio_models

        with patch("google.genai.Client", return_value=mock_client):
            result = await p.call_with_tools("system", "user", [])

        assert result == {"status": "complete"}

    async def test_call_with_tools_exception(self):
        p = GeminiProvider(api_key="AIza-test")

        mock_aio_models = AsyncMock()
        mock_aio_models.generate_content = AsyncMock(side_effect=Exception("network"))

        mock_client = MagicMock()
        mock_client.aio.models = mock_aio_models

        with patch("google.genai.Client", return_value=mock_client):
            result = await p.call_with_tools("system", "user", [])

        assert result is None
