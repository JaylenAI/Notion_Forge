"""Groq AI Provider"""

import logging
from typing import Any

from app.agent.providers.base import BaseProvider

logger = logging.getLogger("notionforge.providers.groq")


class GroqProvider(BaseProvider):
    name = "groq"
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
                system_prompt = system_prompt[:self.MAX_PROMPT_CHARS]

            client = AsyncGroq(api_key=self.api_key or settings.groq_api_key)
            response = await client.chat.completions.create(
                model=model or self.default_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.3,
                max_tokens=4096,
            )
            return self.extract_json(response.choices[0].message.content or "")
        except Exception as e:
            logger.warning(f"[Groq 에러] {e}")
            return None
