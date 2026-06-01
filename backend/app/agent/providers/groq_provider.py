"""Groq AI Provider — JSON mode 지원"""

import logging
from typing import Any

from app.agent.providers.base import BaseProvider

logger = logging.getLogger("notionforge.providers.groq")


class GroqProvider(BaseProvider):
    name = "groq"
    supports_json_mode = True
    supports_function_calling = True
    MAX_PROMPT_CHARS = 12000

    def __init__(self, api_key: str = "", model: str = ""):
        self.api_key = api_key
        self.default_model = model or "openai/gpt-oss-120b"

    def get_max_prompt_chars(self) -> int:
        return self.MAX_PROMPT_CHARS

    async def call(self, system_prompt: str, user_message: str, model: str = "") -> dict[str, Any] | None:
        try:
            from groq import AsyncGroq

            from app.config import settings

            if len(system_prompt) > self.MAX_PROMPT_CHARS:
                system_prompt = system_prompt[: self.MAX_PROMPT_CHARS]

            # Groq의 json_object 모드는 메시지에 'json' 단어가 반드시 포함돼야 한다(없으면 400 BadRequest).
            # 프롬프트 truncation으로 'json'이 잘려나갈 수 있으므로 user 메시지에 보장한다.
            user_content = user_message
            if "json" not in (system_prompt + user_message).lower():
                user_content = f"{user_message}\n\n(Respond with a single valid JSON object.)"

            client = AsyncGroq(api_key=self.api_key or settings.groq_api_key)
            response = await client.chat.completions.create(
                model=model or self.default_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=4096,
            )
            text = response.choices[0].message.content or ""

            if response.usage:
                logger.info(f"[Groq] 토큰: {response.usage.prompt_tokens}→{response.usage.completion_tokens}")

            return self.extract_json(text)
        except ImportError:
            logger.warning("[Groq] groq 패키지 미설치")
            return None
        except Exception as e:
            logger.warning(f"[Groq 에러] {type(e).__name__}: {str(e)[:150]}")
            return None

    async def call_with_tools(
        self,
        system_prompt: str,
        user_message: str,
        tools: list[dict[str, Any]],
        model: str = "",
    ) -> dict[str, Any] | None:
        try:
            from groq import AsyncGroq

            from app.config import settings

            if len(system_prompt) > self.MAX_PROMPT_CHARS:
                system_prompt = system_prompt[: self.MAX_PROMPT_CHARS]

            client = AsyncGroq(api_key=self.api_key or settings.groq_api_key)
            kwargs: dict[str, Any] = {
                "model": model or self.default_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                "temperature": 0.3,
                "max_tokens": 4096,
            }
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            response = await client.chat.completions.create(**kwargs)
            message = response.choices[0].message

            if message.tool_calls:
                return {
                    "tool_calls": [
                        {
                            "name": tc.function.name,
                            "arguments": self.extract_json(tc.function.arguments) or {},
                        }
                        for tc in message.tool_calls
                    ]
                }

            text = message.content or ""
            return self.extract_json(text)
        except ImportError:
            logger.warning("[Groq] groq 패키지 미설치")
            return None
        except Exception as e:
            logger.warning(f"[Groq FC 에러] {type(e).__name__}: {str(e)[:150]}")
            return None
