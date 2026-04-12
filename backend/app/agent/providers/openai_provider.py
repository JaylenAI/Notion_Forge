"""OpenAI Provider"""

import logging
from typing import Any

from app.agent.providers.base import BaseProvider

logger = logging.getLogger("notionforge.providers.openai")


class OpenAIProvider(BaseProvider):
    name = "openai"

    def __init__(self, api_key: str = "", model: str = ""):
        self.api_key = api_key
        self.default_model = model or "gpt-4o-mini"

    async def call(self, system_prompt: str, user_message: str, model: str = "") -> dict[str, Any] | None:
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": model or self.default_model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_message},
                        ],
                        "temperature": 0.3,
                        "max_tokens": 4096,
                    },
                    timeout=30.0,
                )
                return self.extract_json(resp.json()["choices"][0]["message"]["content"] or "")
        except Exception as e:
            logger.warning(f"[OpenAI 에러] {e}")
            return None
