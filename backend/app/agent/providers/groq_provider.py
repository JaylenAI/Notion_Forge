"""Groq AI Provider — JSON mode 지원"""

import logging
from typing import Any

from app.agent.providers.base import BaseProvider

logger = logging.getLogger("notionforge.providers.groq")


class GroqProvider(BaseProvider):
    name = "groq"
    supports_json_mode = True
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

            client = AsyncGroq(api_key=self.api_key or settings.groq_api_key)
            response = await client.chat.completions.create(
                model=model or self.default_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
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
